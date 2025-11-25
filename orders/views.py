"""
========================================
ORDERS/VIEWS.PY - Production Ready
========================================

Vues refactorisées suivant le pattern "Thin Views" :
- Gestion du contexte HTTP (request/response)
- Extraction des données de la requête
- Délégation de la logique métier aux services
- Présentation des résultats (render/redirect)
- Intégration complète des fonctionnalités marketing (coupons)
- Support email automatisé
- Génération de factures PDF

Toute la logique métier complexe est dans orders/services.py
"""

import logging
from decimal import Decimal
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.conf import settings

from shop.models import Product, ProductVariant
from accounts.models import Address
from .models import Order, ShippingZone

# Import de la couche de service
from .services import (
    create_order_from_cart,
    prepare_cart_items_for_display,
    calculate_cart_subtotal,
    clean_cart_from_unavailable_items,
    OrderCreationResult,
    StockValidationException,
)

# Import des services utilitaires
from .utils import generate_invoice_pdf
from core.email_service import EmailService

# Logger pour le suivi des erreurs
logger = logging.getLogger(__name__)


# ========================================
# VUES DU PANIER
# ========================================

def cart_detail(request):
    """
    Affichage du panier avec nettoyage automatique des produits obsolètes.
    
    Gère :
    - Affichage des articles du panier
    - Calcul du total
    - Nettoyage des variantes inactives ou inexistantes
    """
    # Récupérer le panier de la session
    cart = request.session.get('cart', {})
    
    cart_items = []
    total = 0
    
    for variant_id, quantity in cart.items():
        try:
            variant = ProductVariant.objects.select_related(
                'product', 
                'product__category', 
                'stock'
            ).get(id=variant_id, is_active=True)
            
            if variant.stock.is_in_stock:
                subtotal = variant.final_price * quantity
                cart_items.append({
                    'variant': variant,
                    'quantity': quantity,
                    'subtotal': subtotal,
                })
                total += subtotal
        except ProductVariant.DoesNotExist:
            # Retirer les variantes qui n'existent plus du panier
            pass
    
    # Nettoyer le panier des produits inexistants
    if len(cart_items) < len(cart):
        cleaned_cart = {}
        for item in cart_items:
            cleaned_cart[str(item['variant'].id)] = item['quantity']
        request.session['cart'] = cleaned_cart
        request.session.modified = True
    
    context = {
        'cart_items': cart_items,
        'total': total,
        'page_title': 'Mon panier',
    }
    return render(request, 'orders/cart_detail.html', context)


def cart_add(request, variant_id):
    """
    Ajouter un produit au panier (Compatible AJAX et Classique).
    
    Fonctionnalités :
    - Support AJAX avec réponse JSON
    - Validation du stock disponible
    - Vérification de la quantité maximale
    - Mise à jour du compteur de panier
    - Messages utilisateur appropriés
    
    Args:
        variant_id: ID de la variante de produit à ajouter
    """
    if request.method == 'POST':
        # Récupérer la quantité depuis le POST (avec valeur par défaut de 1)
        try:
            quantity = int(request.POST.get('quantity', 1))
        except (ValueError, TypeError):
            quantity = 1
        
        # Détection requête AJAX
        is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'
        
        # Validation de la quantité
        if quantity < 1:
            if is_ajax:
                return JsonResponse({'error': 'Quantité invalide.'}, status=400)
            messages.error(request, 'Quantité invalide.')
            return redirect('shop:product_list')
        
        try:
            variant = ProductVariant.objects.select_related(
                'product', 
                'stock'
            ).get(id=variant_id, is_active=True)
            
            # Vérifier le stock disponible
            if not variant.stock.is_in_stock:
                msg = f'{variant.product.name} est en rupture de stock.'
                if is_ajax:
                    return JsonResponse({'error': msg}, status=400)
                messages.error(request, msg)
                return redirect('shop:product_detail', slug=variant.product.slug)
            
            # Récupérer le panier actuel
            cart = request.session.get('cart', {})
            
            # Calculer la quantité totale demandée
            current_quantity = cart.get(str(variant_id), 0)
            total_quantity = current_quantity + quantity
            
            # Vérifier si la quantité totale ne dépasse pas le stock
            if total_quantity > variant.stock.available_quantity:
                msg = (
                    f'Stock insuffisant pour {variant.product.name}. '
                    f'Disponible : {variant.stock.available_quantity}, '
                    f'Déjà dans le panier : {current_quantity}'
                )
                if is_ajax:
                    return JsonResponse({'error': msg}, status=400)
                messages.error(request, msg)
                return redirect('shop:product_detail', slug=variant.product.slug)
            
            # Ajouter ou mettre à jour la quantité
            cart[str(variant_id)] = total_quantity
            request.session['cart'] = cart
            request.session.modified = True
            
            # Calculer le nombre total d'articles pour mettre à jour le badge
            total_items = sum(cart.values())
            
            # Message de succès
            if str(variant_id) in cart and current_quantity > 0:
                msg = f'Quantité de {variant.product.name} mise à jour dans le panier.'
            else:
                msg = f'{variant.product.name} ajouté au panier avec succès.'
            
            # Réponse JSON pour les requêtes AJAX
            if is_ajax:
                return JsonResponse({
                    'success': True,
                    'message': msg,
                    'cart_count': total_items,
                    'variant_id': variant_id,
                    'product_name': variant.product.name
                })
            
            # Réponse classique pour les requêtes normales
            messages.success(request, msg)
            
        except ProductVariant.DoesNotExist:
            if is_ajax:
                return JsonResponse({'error': 'Produit introuvable.'}, status=404)
            messages.error(request, 'Produit introuvable.')
            return redirect('shop:product_list')
        except ValueError:
            if is_ajax:
                return JsonResponse({'error': 'Quantité invalide.'}, status=400)
            messages.error(request, 'Quantité invalide.')
            return redirect('shop:product_list')
    
    return redirect('orders:cart_detail')


def cart_remove(request, variant_id):
    """
    Retirer un produit du panier.
    
    Gère :
    - Suppression de l'article du panier
    - Mise à jour de la session
    - Messages de confirmation
    """
    cart = request.session.get('cart', {})
    
    if str(variant_id) in cart:
        try:
            # Récupérer le nom du produit avant de le supprimer
            variant = ProductVariant.objects.select_related('product').get(id=variant_id)
            product_name = variant.product.name
            
            del cart[str(variant_id)]
            request.session['cart'] = cart
            request.session.modified = True
            
            messages.success(request, f'{product_name} retiré du panier.')
        except ProductVariant.DoesNotExist:
            # Supprimer quand même du panier
            del cart[str(variant_id)]
            request.session['cart'] = cart
            request.session.modified = True
            messages.success(request, 'Produit retiré du panier.')
    else:
        messages.error(request, 'Produit introuvable dans le panier.')
    
    return redirect('orders:cart_detail')


def cart_update(request, variant_id):
    """
    Mettre à jour la quantité d'un produit dans le panier.
    
    Gère :
    - Modification de la quantité
    - Validation du stock disponible
    - Suppression si quantité = 0
    """
    if request.method == 'POST':
        try:
            quantity = int(request.POST.get('quantity', 1))
        except (ValueError, TypeError):
            messages.error(request, 'Quantité invalide.')
            return redirect('orders:cart_detail')
        
        cart = request.session.get('cart', {})
        
        if str(variant_id) in cart:
            if quantity > 0:
                # Vérifier le stock disponible
                try:
                    variant = ProductVariant.objects.select_related(
                        'product', 
                        'stock'
                    ).get(id=variant_id, is_active=True)
                    
                    if variant.stock.available_quantity >= quantity:
                        cart[str(variant_id)] = quantity
                        request.session['cart'] = cart
                        request.session.modified = True
                        messages.success(request, 'Quantité mise à jour avec succès.')
                    else:
                        messages.error(
                            request, 
                            f'Stock insuffisant. Disponible : {variant.stock.available_quantity}'
                        )
                except ProductVariant.DoesNotExist:
                    messages.error(request, 'Produit introuvable.')
            else:
                # Si quantité = 0, supprimer l'article
                del cart[str(variant_id)]
                request.session['cart'] = cart
                request.session.modified = True
                messages.success(request, 'Produit retiré du panier.')
        else:
            messages.error(request, 'Produit introuvable dans le panier.')
    
    return redirect('orders:cart_detail')


@require_http_methods(["POST"])
def cart_clear(request):
    """
    Vider complètement le panier.
    
    Supprime tous les articles du panier de la session.
    """
    if 'cart' in request.session:
        del request.session['cart']
        request.session.modified = True
    messages.success(request, 'Votre panier a été vidé.')
    return redirect('orders:cart_detail')


# ========================================
# VUES DE COMMANDE
# ========================================

@login_required
def checkout(request):
    """
    Page de validation de commande avec système de zones dynamiques.
    
    Fonctionnalités :
    - Préparation des articles du panier via le service
    - Calcul du sous-total
    - Détection automatique de la zone de livraison
    - Affichage des options de livraison (standard/express)
    - Calcul dynamique des frais de livraison
    """
    # Vérifier que l'utilisateur a un profil Customer
    if not hasattr(request.user, 'customer'):
        from accounts.models import Customer
        Customer.objects.create(user=request.user)
    
    # Récupérer le panier
    cart = request.session.get('cart', {})
    
    if not cart:
        messages.warning(request, 'Votre panier est vide.')
        return redirect('shop:product_list')
    
    # Utiliser le service pour préparer les items du panier
    cart_items = prepare_cart_items_for_display(cart)
    
    if not cart_items:
        messages.warning(request, 'Votre panier est vide.')
        return redirect('shop:product_list')
    
    # Calculer le sous-total avec le service
    subtotal = calculate_cart_subtotal(cart)
    
    # Adresses du client
    addresses = Address.objects.filter(
        customer=request.user.customer
    ).order_by('-is_default', '-created_at')
    
    # ========================================
    # Système de zones dynamiques
    # ========================================
    
    shipping_zones = ShippingZone.objects.filter(
        is_active=True
    ).prefetch_related('rates').order_by('display_order')
    
    shipping_options = []
    detected_zone = None
    
    # Détection automatique de la zone
    if addresses.exists():
        default_address = addresses.first()
        city = default_address.city
        
        for zone in shipping_zones:
            if zone.is_city_covered(city):
                detected_zone = zone
                break
    
    # Préparer les options de livraison avec tarifs
    for zone in shipping_zones:
        zone_info = {
            'zone': zone,
            'rates': {
                'standard': None,
                'express': None
            }
        }
        
        for rate in zone.rates.filter(is_active=True):
            calculated_cost = rate.calculate_shipping_cost(subtotal)
            
            zone_info['rates'][rate.delivery_type] = {
                'rate': rate,
                'cost': calculated_cost,
                'is_free': calculated_cost == 0,
                'delivery_days': {
                    'min': zone.express_delivery_days_min if rate.delivery_type == 'express' else zone.standard_delivery_days_min,
                    'max': zone.express_delivery_days_max if rate.delivery_type == 'express' else zone.standard_delivery_days_max
                }
            }
        
        shipping_options.append(zone_info)
    
    # Calcul du total par défaut
    default_shipping_cost = 0
    if detected_zone:
        standard_rate = detected_zone.rates.filter(
            delivery_type='standard',
            is_active=True
        ).first()
        if standard_rate:
            default_shipping_cost = standard_rate.calculate_shipping_cost(subtotal)
    
    total = subtotal + default_shipping_cost
    
    context = {
        'cart_items': cart_items,
        'subtotal': subtotal,
        'total': total,
        'addresses': addresses,
        'shipping_zones': shipping_zones,
        'shipping_options': shipping_options,
        'detected_zone': detected_zone,
        'default_shipping_cost': default_shipping_cost,
        'page_title': 'Validation de commande',
    }
    return render(request, 'orders/checkout.html', context)


@login_required
def checkout_confirm(request):
    """
    Confirmation et création de la commande avec intégration complète.
    
    Architecture "Thin View" :
    1. Extraction des données de la requête
    2. Délégation au service de création de commande
    3. Gestion du résultat (succès/erreur)
    4. Envoi de l'email de confirmation
    5. Nettoyage de la session
    6. Redirection appropriée
    
    Fonctionnalités intégrées :
    - Support des codes promo
    - Envoi d'email automatique (avec gestion d'erreur silencieuse)
    - Gestion multi-paiement (COD, Airtel, Moov)
    - Validation complète via le service
    """
    if request.method != 'POST':
        return redirect('orders:checkout')
    
    # ============================================
    # ÉTAPE 1 : VÉRIFICATION DU PROFIL CLIENT
    # ============================================
    
    if not hasattr(request.user, 'customer'):
        from accounts.models import Customer
        Customer.objects.create(user=request.user)
    
    # ============================================
    # ÉTAPE 2 : EXTRACTION DES DONNÉES
    # ============================================
    
    cart = request.session.get('cart', {})
    
    if not cart:
        messages.error(request, 'Votre panier est vide.')
        return redirect('shop:product_list')
    
    # Récupérer les données du formulaire
    address_id = request.POST.get('address_id')
    shipping_rate_id = request.POST.get('shipping_rate_id')
    delivery_notes = request.POST.get('delivery_notes', '').strip()
    payment_method = request.POST.get('payment_method', 'cod')
    
    # Récupérer le code promo depuis la session (si appliqué)
    coupon_code = request.session.get('coupon_code')
    coupon_discount = request.session.get('coupon_discount', 0)
    
    # ============================================
    # ÉTAPE 3 : APPEL DU SERVICE DE CRÉATION
    # ============================================
    
    result: OrderCreationResult = create_order_from_cart(
        customer=request.user.customer,
        cart=cart,
        address_id=address_id,
        shipping_rate_id=shipping_rate_id,
        payment_method=payment_method,
        delivery_notes=delivery_notes,
        customer_email=request.user.email,
        customer_phone=getattr(request.user.customer, 'phone', None),
        coupon_code=coupon_code,
        tax_amount=Decimal('0')  # TODO: Implémenter les taxes si nécessaire
    )
    
    # ============================================
    # ÉTAPE 4 : GESTION DU RÉSULTAT
    # ============================================
    
    if not result.success:
        # En cas d'erreur, afficher les messages appropriés
        if result.validation_errors:
            for error in result.validation_errors:
                messages.error(request, error)
        else:
            messages.error(request, result.error_message or 'Une erreur est survenue.')
        
        return redirect('orders:checkout')
    
    # ============================================
    # ÉTAPE 5 : SUCCÈS - GESTION DE LA SESSION
    # ============================================
    
    order = result.order
    
    # Sauvegarder l'ID de la commande en session pour le paiement
    request.session['order_id'] = order.id
    request.session['payment_method'] = payment_method
    
    # Nettoyer les données du coupon de la session
    # (Évite qu'il ne s'applique automatiquement à la prochaine commande)
    if 'coupon_code' in request.session:
        del request.session['coupon_code']
    if 'coupon_discount' in request.session:
        del request.session['coupon_discount']
    
    request.session.modified = True
    
    # Message de succès
    success_message = (
        f'Commande {order.order_number} créée avec succès ! '
        f'Livraison {order.shipping_rate.get_delivery_type_display()} '
        f'vers {order.shipping_zone.name}.'
    )
    
    # Ajouter une mention si un coupon a été appliqué
    if order.discount_amount > 0 and order.coupon_code:
        success_message += f' Code promo "{order.coupon_code}" appliqué (-{order.discount_amount} FCFA).'
    
    messages.success(request, success_message)
    
    # ============================================
    # ÉTAPE 6 : ENVOI DE L'EMAIL DE CONFIRMATION
    # ============================================
    
    # Envoi silencieux : en cas d'erreur, on log mais on ne bloque pas le processus
    try:
        EmailService.send_order_confirmation(order)
        messages.info(request, 'Un email de confirmation vous a été envoyé avec votre facture.')
    except Exception as e:
        # Log de l'erreur pour le suivi administratif
        logger.error(
            f"Échec de l'envoi de l'email de confirmation pour la commande {order.order_number}: {str(e)}",
            exc_info=True
        )
        # On n'affiche pas d'erreur à l'utilisateur pour ne pas l'inquiéter
        # La commande est créée avec succès, l'email n'est qu'un bonus
    
    # ============================================
    # ÉTAPE 7 : REDIRECTION SELON LE PAIEMENT
    # ============================================
    
    if payment_method in ['airtel', 'moov']:
        # Paiement mobile : rediriger vers la page de paiement
        return redirect('payments:payment_method')
    elif payment_method == 'cod':
        # Paiement à la livraison : vider le panier et aller à la confirmation
        if 'cart' in request.session:
            del request.session['cart']
            request.session.modified = True
        
        return redirect('orders:order_success', order_number=order.order_number)
    else:
        # Par défaut, aller vers la sélection du mode de paiement
        return redirect('payments:payment_method')


def order_success(request, order_number):
    """
    Page de confirmation de commande réussie.
    
    Fonctionnalités :
    - Affichage des détails de la commande
    - Vérification de propriété
    - Nettoyage de la session
    - Suggestions de produits similaires
    """
    # Récupérer la commande
    order = get_object_or_404(Order, order_number=order_number)
    
    # Vérifier que l'utilisateur est bien le propriétaire de la commande
    if request.user.is_authenticated:
        if not hasattr(request.user, 'customer'):
            from accounts.models import Customer
            Customer.objects.create(user=request.user)
        
        if order.customer != request.user.customer:
            messages.error(request, 'Vous n\'avez pas accès à cette commande.')
            return redirect('core:home')
    
    # Vider le panier si ce n'est pas déjà fait
    if 'cart' in request.session:
        del request.session['cart']
        request.session.modified = True
    
    # Nettoyer la session de l'ID de commande
    if 'order_id' in request.session:
        del request.session['order_id']
    if 'payment_method' in request.session:
        del request.session['payment_method']
    request.session.modified = True
    
    # Produits recommandés (même catégorie que les produits commandés)
    related_products = []
    if order.items.exists():
        first_item = order.items.first()
        if first_item and first_item.product:
            related_products = Product.objects.filter(
                category=first_item.product.category,
                is_active=True
            ).exclude(
                id__in=[item.product.id for item in order.items.all() if item.product]
            )[:4]
    
    context = {
        'order': order,
        'related_products': related_products,
        'page_title': 'Commande confirmée',
    }
    return render(request, 'orders/order_success.html', context)


# ========================================
# VUES DE FACTURATION
# ========================================

@login_required
def download_invoice(request, order_number):
    """
    Téléchargement sécurisé de la facture PDF d'une commande.
    
    Sécurité :
    - Authentification requise (@login_required)
    - Vérification de propriété de la commande
    - Gestion des erreurs avec messages appropriés
    
    Workflow :
    1. Vérification du profil Customer
    2. Récupération sécurisée de la commande
    3. Génération du PDF via le service
    4. Retour du fichier ou redirection en cas d'erreur
    
    Args:
        order_number (str): Numéro de commande (format: ORD-YYYYMMDD-NNNN)
    
    Returns:
        HttpResponse: PDF de la facture ou redirection
    """
    
    # ============================================
    # ÉTAPE 1 : VÉRIFICATION DU PROFIL CLIENT
    # ============================================
    
    if not hasattr(request.user, 'customer'):
        from accounts.models import Customer
        Customer.objects.create(user=request.user)
    
    # ============================================
    # ÉTAPE 2 : RÉCUPÉRATION SÉCURISÉE
    # ============================================
    
    try:
        # CRITICAL: Le filtre customer__user garantit la sécurité
        order = Order.objects.select_related(
            'customer',
            'customer__user',
            'shipping_address',
            'billing_address',
            'shipping_zone',
            'shipping_rate'
        ).prefetch_related(
            'items__product',
            'items__variant'
        ).get(
            order_number=order_number,
            customer__user=request.user  # Vérification de propriété
        )
        
    except Order.DoesNotExist:
        messages.error(
            request,
            "Commande introuvable ou vous n'avez pas accès à cette facture."
        )
        return redirect('accounts:order_list')
    
    # ============================================
    # ÉTAPE 3 : GÉNÉRATION DU PDF
    # ============================================
    
    pdf_response = generate_invoice_pdf(order)
    
    # ============================================
    # ÉTAPE 4 : GESTION DE LA RÉPONSE
    # ============================================
    
    if pdf_response:
        return pdf_response
    else:
        messages.error(
            request,
            "Une erreur est survenue lors de la génération de votre facture. "
            "Veuillez réessayer ou contacter le support."
        )
        return redirect('accounts:order_detail', order_number=order_number)


@login_required
def preview_invoice(request, order_number):
    """
    Prévisualisation HTML de la facture (avant téléchargement PDF).
    
    Utile pour :
    - Validation du design de la facture
    - Débogage
    - Aperçu rapide sans génération PDF
    
    Args:
        order_number (str): Numéro de commande
    
    Returns:
        HttpResponse: Rendu HTML de la facture
    """
    
    # Vérification du profil Customer
    if not hasattr(request.user, 'customer'):
        from accounts.models import Customer
        Customer.objects.create(user=request.user)
    
    # Récupération sécurisée de la commande
    try:
        order = Order.objects.select_related(
            'customer',
            'customer__user',
            'shipping_address',
            'billing_address',
            'shipping_zone',
            'shipping_rate'
        ).prefetch_related(
            'items__product',
            'items__variant'
        ).get(
            order_number=order_number,
            customer__user=request.user
        )
        
    except Order.DoesNotExist:
        messages.error(
            request,
            "Commande introuvable ou vous n'avez pas accès à cette facture."
        )
        return redirect('accounts:order_list')
    
    # Préparer le contexte (identique à celui du PDF)
    context = {
        'order': order,
        'items': order.items.select_related('product', 'variant'),
        'shop_name': settings.SHOP_NAME,
        'shop_email': settings.SHOP_EMAIL,
        'shop_phone': settings.SHOP_PHONE,
        'shop_address': settings.SHOP_ADDRESS,
        'shop_website': settings.SHOP_WEBSITE,
        'page_title': f'Facture {order.order_number}',
        'preview_mode': True,  # Indicateur pour le template
    }
    
    # Rendre le template HTML (sans conversion PDF)
    return render(request, 'orders/invoice_pdf.html', context)