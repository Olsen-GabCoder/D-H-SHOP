"""
orders/services.py - Couche de Service des Commandes
====================================================

✅ FAILLE #4 CORRIGÉE :
- Ajout de generate_order_number() avec SELECT FOR UPDATE
- Intégration dans create_order_from_cart()

✅ INTÉGRATION MARKETING :
- Support des codes promo dans create_order_from_cart()
- Validation et application des coupons
- Enregistrement de l'utilisation des coupons
"""

from decimal import Decimal
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import logging

from django.db import transaction
from django.db.models import F
from django.utils import timezone

from shop.models import ProductVariant
from accounts.models import Address, Customer
from .models import (
    Order, 
    OrderItem, 
    OrderStatus, 
    ShippingRate, 
    OrderNumberSequence
)

# ✅ NOUVEAUX IMPORTS MARKETING
from marketing.services import validate_coupon, record_coupon_usage

# Configuration du logger
logger = logging.getLogger(__name__)


# ============================================
# CLASSES DE DONNÉES (DATA TRANSFER OBJECTS)
# ============================================

@dataclass
class CartItemData:
    """Représentation d'un article du panier avec ses données validées"""
    variant: ProductVariant
    quantity: int
    unit_price: Decimal
    subtotal: Decimal
    product_name: str
    variant_details: str


@dataclass
class OrderCalculation:
    """Résultat des calculs de commande"""
    subtotal: Decimal
    shipping_cost: Decimal
    tax_amount: Decimal
    discount_amount: Decimal
    total: Decimal
    items: List[CartItemData]


@dataclass
class OrderCreationResult:
    """Résultat de la création d'une commande"""
    success: bool
    order: Optional[Order] = None
    error_message: Optional[str] = None
    validation_errors: Optional[List[str]] = None


# ============================================
# EXCEPTIONS MÉTIER
# ============================================

class OrderServiceException(Exception):
    """Exception de base pour les erreurs de service de commande"""
    pass


class InvalidCartException(OrderServiceException):
    """Le panier est invalide ou vide"""
    pass


class StockValidationException(OrderServiceException):
    """Erreur de validation du stock"""
    def __init__(self, errors: List[str]):
        self.errors = errors
        super().__init__(f"Erreurs de stock: {', '.join(errors)}")


class InvalidAddressException(OrderServiceException):
    """Adresse de livraison invalide"""
    pass


class InvalidShippingRateException(OrderServiceException):
    """Tarif de livraison invalide"""
    pass


class ShippingZoneMismatchException(OrderServiceException):
    """La zone de livraison ne couvre pas la ville"""
    pass


class OrderNumberGenerationException(OrderServiceException):
    """Erreur lors de la génération du numéro de commande"""
    pass


# ============================================
# ✅ GÉNÉRATION ATOMIQUE DU NUMÉRO
# ============================================

@transaction.atomic
def generate_order_number() -> str:
    """
    Génère un numéro de commande unique de manière thread-safe.
    
    Utilise SELECT FOR UPDATE pour verrouiller la ligne de séquence,
    garantissant qu'aucune autre transaction ne peut lire/modifier
    le même compteur simultanément.
    
    Format: ORD-YYYYMMDD-NNNN
    Exemple: ORD-20250119-0042
    
    Returns:
        str: Numéro de commande unique
        
    Raises:
        OrderNumberGenerationException: En cas d'erreur de génération
        
    Note:
        Cette fonction DOIT être appelée dans une transaction atomique.
        Le décorateur @transaction.atomic garantit que le verrou est
        maintenu jusqu'à la fin de la transaction.
    """
    try:
        # Générer le préfixe basé sur la date du jour
        today_prefix = timezone.now().strftime('%Y%m%d')
        
        # Récupérer ou créer la séquence pour aujourd'hui
        # SELECT FOR UPDATE verrouille la ligne jusqu'à la fin de la transaction
        sequence, created = OrderNumberSequence.objects.select_for_update().get_or_create(
            prefix=today_prefix,
            defaults={'last_number': 0}
        )
        
        # Incrémenter le compteur de manière atomique
        sequence.last_number = F('last_number') + 1
        sequence.save(update_fields=['last_number'])
        
        # Rafraîchir pour obtenir la valeur réelle
        sequence.refresh_from_db()
        
        # Générer le numéro de commande final
        order_number = f'ORD-{today_prefix}-{sequence.last_number:04d}'
        
        return order_number
        
    except Exception as e:
        raise OrderNumberGenerationException(
            f"Impossible de générer un numéro de commande: {str(e)}"
        )


# ============================================
# SERVICES DE VALIDATION
# ============================================

def validate_cart_items(
    cart: Dict[str, int]
) -> Tuple[List[CartItemData], List[str]]:
    """
    Valide les articles du panier et retourne les données structurées
    
    Args:
        cart: Dictionnaire {variant_id: quantity}
    
    Returns:
        Tuple[List[CartItemData], List[str]]: 
            - Liste des articles validés
            - Liste des erreurs de validation
    
    Raises:
        InvalidCartException: Si le panier est vide
    """
    if not cart:
        raise InvalidCartException("Le panier est vide")
    
    validated_items = []
    errors = []
    
    for variant_id, quantity in cart.items():
        try:
            variant = ProductVariant.objects.select_related(
                'product', 
                'product__category', 
                'stock'
            ).get(id=variant_id, is_active=True)
            
            # Vérification du stock disponible
            if not variant.stock.is_in_stock:
                errors.append(f'{variant.product.name} est en rupture de stock')
                continue
            
            if variant.stock.available_quantity < quantity:
                errors.append(
                    f'{variant.product.name} : stock insuffisant '
                    f'(disponible : {variant.stock.available_quantity})'
                )
                continue
            
            # Créer l'objet CartItemData validé
            item_total = variant.final_price * quantity
            
            validated_items.append(CartItemData(
                variant=variant,
                quantity=quantity,
                unit_price=variant.final_price,
                subtotal=item_total,
                product_name=variant.product.name,
                variant_details=f"{variant.size or ''} {variant.color or ''}".strip()
            ))
            
        except ProductVariant.DoesNotExist:
            errors.append(f'Variante {variant_id} introuvable ou inactive')
            continue
    
    if errors:
        raise StockValidationException(errors)
    
    if not validated_items:
        raise InvalidCartException("Aucun article valide dans le panier")
    
    return validated_items, errors


def validate_shipping_address(
    address_id: Optional[str],
    customer: Customer
) -> Address:
    """
    Valide et récupère l'adresse de livraison
    
    Args:
        address_id: ID de l'adresse
        customer: Client propriétaire
    
    Returns:
        Address: Adresse validée
    
    Raises:
        InvalidAddressException: Si l'adresse est invalide
    """
    if not address_id:
        raise InvalidAddressException("Aucune adresse de livraison sélectionnée")
    
    try:
        return Address.objects.get(
            id=address_id,
            customer=customer
        )
    except Address.DoesNotExist:
        raise InvalidAddressException(
            f"Adresse {address_id} introuvable ou n'appartient pas au client"
        )


def validate_shipping_rate(
    rate_id: Optional[str],
    shipping_address: Address
) -> ShippingRate:
    """
    Valide le tarif de livraison et sa zone
    
    Args:
        rate_id: ID du tarif de livraison
        shipping_address: Adresse de livraison
    
    Returns:
        ShippingRate: Tarif validé
    
    Raises:
        InvalidShippingRateException: Si le tarif est invalide
        ShippingZoneMismatchException: Si la zone ne couvre pas la ville
    """
    if not rate_id:
        raise InvalidShippingRateException("Aucun mode de livraison sélectionné")
    
    try:
        shipping_rate = ShippingRate.objects.select_related('zone').get(
            id=rate_id,
            is_active=True,
            zone__is_active=True
        )
    except ShippingRate.DoesNotExist:
        raise InvalidShippingRateException(
            f"Tarif de livraison {rate_id} introuvable ou inactif"
        )
    
    # Vérifier que la zone couvre bien la ville
    if not shipping_rate.zone.is_city_covered(shipping_address.city):
        raise ShippingZoneMismatchException(
            f"La zone {shipping_rate.zone.name} ne couvre pas {shipping_address.city}"
        )
    
    return shipping_rate


# ============================================
# SERVICES DE CALCUL
# ============================================

def calculate_order_totals(
    cart_items: List[CartItemData],
    shipping_rate: ShippingRate,
    discount_amount: Decimal = Decimal('0'),
    tax_amount: Decimal = Decimal('0')
) -> OrderCalculation:
    """
    Calcule tous les totaux de la commande
    
    Args:
        cart_items: Liste des articles validés
        shipping_rate: Tarif de livraison
        discount_amount: Montant de réduction (optionnel)
        tax_amount: Montant de taxe (optionnel)
    
    Returns:
        OrderCalculation: Tous les calculs de la commande
    """
    # Calcul du sous-total
    subtotal = sum(item.subtotal for item in cart_items)
    
    # Calcul des frais de livraison (peut être gratuit selon le montant)
    shipping_cost = shipping_rate.calculate_shipping_cost(subtotal)
    
    # Total final
    total = subtotal + shipping_cost + tax_amount - discount_amount
    
    return OrderCalculation(
        subtotal=subtotal,
        shipping_cost=shipping_cost,
        tax_amount=tax_amount,
        discount_amount=discount_amount,
        total=total,
        items=cart_items
    )


# ============================================
# SERVICE PRINCIPAL DE CRÉATION DE COMMANDE
# ============================================

def create_order_from_cart(
    customer: Customer,
    cart: Dict[str, int],
    address_id: str,
    shipping_rate_id: str,
    payment_method: str = 'cod',
    delivery_notes: str = '',
    customer_email: Optional[str] = None,
    customer_phone: Optional[str] = None,
    coupon_code: Optional[str] = None,  # ✅ NOUVEAU PARAMÈTRE
    tax_amount: Decimal = Decimal('0')
) -> OrderCreationResult:
    """
    Service principal de création de commande
    
    ✅ FAILLE #4 CORRIGÉE :
    - Utilise generate_order_number() pour un numéro unique thread-safe
    - Toute la création se fait dans une transaction atomique
    
    ✅ INTÉGRATION MARKETING :
    - Support des codes promo via le paramètre coupon_code
    - Validation et application des coupons
    - Enregistrement de l'utilisation
    
    Cette fonction encapsule toute la logique métier de création d'une commande :
    - Validation des articles du panier
    - Validation de l'adresse de livraison
    - Validation du tarif de livraison
    - Validation et application du code promo (si fourni)
    - Calcul des totaux
    - Génération du numéro de commande (ATOMIQUE)
    - Création atomique de la commande
    - Réservation du stock
    - Mise à jour des statistiques
    - Enregistrement de l'utilisation du coupon
    
    Args:
        customer: Client effectuant la commande
        cart: Panier sous forme {variant_id: quantity}
        address_id: ID de l'adresse de livraison
        shipping_rate_id: ID du tarif de livraison
        payment_method: Méthode de paiement ('cod', 'airtel', 'moov')
        delivery_notes: Instructions de livraison (optionnel)
        customer_email: Email du client (optionnel)
        customer_phone: Téléphone du client (optionnel)
        coupon_code: Code promo à appliquer (optionnel)
        tax_amount: Montant de taxe (optionnel)
    
    Returns:
        OrderCreationResult: Résultat de la création (succès ou erreur)
    """
    # Variables pour le coupon
    applied_coupon = None
    discount_amount = Decimal('0')
    
    try:
        # ============================================
        # PHASE 1 : VALIDATION
        # ============================================
        
        # 1.1 - Valider les articles du panier
        try:
            cart_items, _ = validate_cart_items(cart)
        except StockValidationException as e:
            return OrderCreationResult(
                success=False,
                error_message="Problèmes de stock détectés",
                validation_errors=e.errors
            )
        except InvalidCartException as e:
            return OrderCreationResult(
                success=False,
                error_message=str(e)
            )
        
        # 1.2 - Valider l'adresse de livraison
        try:
            shipping_address = validate_shipping_address(address_id, customer)
        except InvalidAddressException as e:
            return OrderCreationResult(
                success=False,
                error_message=str(e)
            )
        
        # 1.3 - Valider le tarif de livraison
        try:
            shipping_rate = validate_shipping_rate(shipping_rate_id, shipping_address)
        except (InvalidShippingRateException, ShippingZoneMismatchException) as e:
            return OrderCreationResult(
                success=False,
                error_message=str(e)
            )
        
        # ============================================
        # PHASE 2 : VALIDATION DU CODE PROMO
        # ============================================
        
        # ✅ 2.1 - Valider et appliquer le code promo si fourni
        if coupon_code:
            # Calculer le sous-total pour la validation du coupon
            cart_subtotal = sum(item.subtotal for item in cart_items)
            
            # Valider le coupon
            coupon_valid, coupon_message, coupon_discount, coupon_obj = validate_coupon(
                code=coupon_code,
                customer=customer,
                cart_total=cart_subtotal
            )
            
            if coupon_valid:
                # Coupon valide : appliquer la réduction
                applied_coupon = coupon_obj
                discount_amount = coupon_discount
                logger.info(
                    f"Coupon '{coupon_code}' appliqué pour le client {customer.id} : "
                    f"réduction de {discount_amount} FCFA"
                )
            else:
                # Coupon invalide : logger l'erreur mais continuer la commande
                logger.warning(
                    f"Tentative d'utilisation d'un coupon invalide '{coupon_code}' "
                    f"par le client {customer.id} : {coupon_message}"
                )
                # On ignore silencieusement le coupon invalide
                # pour ne pas bloquer la commande
        
        # ============================================
        # PHASE 3 : CALCULS
        # ============================================
        
        calculation = calculate_order_totals(
            cart_items=cart_items,
            shipping_rate=shipping_rate,
            discount_amount=discount_amount,  # ✅ Utilise la réduction du coupon
            tax_amount=tax_amount
        )
        
        # ============================================
        # PHASE 4 : CRÉATION ATOMIQUE
        # ============================================
        
        with transaction.atomic():
            # 4.1 - Générer le numéro de commande de manière atomique
            try:
                order_number = generate_order_number()
            except OrderNumberGenerationException as e:
                return OrderCreationResult(
                    success=False,
                    error_message=str(e)
                )
            
            # 4.2 - Créer la commande avec le numéro généré
            order = Order.objects.create(
                order_number=order_number,
                customer=customer,
                shipping_address=shipping_address,
                billing_address=shipping_address,
                shipping_zone=shipping_rate.zone,
                shipping_rate=shipping_rate,
                delivery_type=shipping_rate.delivery_type,
                customer_email=customer_email or customer.user.email,
                customer_phone=customer_phone or customer.phone or shipping_address.phone,
                subtotal=calculation.subtotal,
                shipping_cost=calculation.shipping_cost,
                tax_amount=calculation.tax_amount,
                discount_amount=calculation.discount_amount,
                total=calculation.total,
                customer_notes=delivery_notes,
                coupon_code=applied_coupon.code if applied_coupon else '',  # ✅ Enregistrer le code
                status='pending'
            )
            
            # 4.3 - Créer les articles de commande
            for item_data in calculation.items:
                OrderItem.objects.create(
                    order=order,
                    product=item_data.variant.product,
                    variant=item_data.variant,
                    product_name=item_data.product_name,
                    variant_details=item_data.variant_details,
                    unit_price=item_data.unit_price,
                    quantity=item_data.quantity,
                    subtotal=item_data.subtotal
                )
                
                # 4.4 - Réserver le stock
                item_data.variant.stock.reserved_quantity = F('reserved_quantity') + item_data.quantity
                item_data.variant.stock.save(update_fields=['reserved_quantity'])
                
                # 4.5 - Mettre à jour les statistiques du produit
                item_data.variant.product.sales_count = F('sales_count') + item_data.quantity
                item_data.variant.product.save(update_fields=['sales_count'])
            
            # ✅ 4.6 - Enregistrer l'utilisation du coupon si appliqué
            if applied_coupon:
                try:
                    record_coupon_usage(order=order, coupon=applied_coupon)
                    logger.info(
                        f"Utilisation du coupon '{applied_coupon.code}' enregistrée "
                        f"pour la commande {order.order_number}"
                    )
                except Exception as e:
                    # En cas d'erreur, logger mais ne pas bloquer la commande
                    logger.error(
                        f"Erreur lors de l'enregistrement de l'utilisation du coupon "
                        f"'{applied_coupon.code}' : {str(e)}"
                    )
            
            # 4.7 - Créer l'historique de statut
            status_comment = (
                f'Commande créée - '
                f'Livraison {shipping_rate.get_delivery_type_display()} '
                f'vers {shipping_rate.zone.name}'
            )
            if applied_coupon:
                status_comment += f' - Code promo "{applied_coupon.code}" appliqué'
            
            OrderStatus.objects.create(
                order=order,
                status='pending',
                comment=status_comment,
                created_by=customer.user.username
            )
            
            # 4.8 - Mettre à jour les statistiques du client
            customer.total_orders = F('total_orders') + 1
            customer.total_spent = F('total_spent') + calculation.total
            customer.save(update_fields=['total_orders', 'total_spent'])
        
        # ============================================
        # PHASE 5 : SUCCÈS
        # ============================================
        
        return OrderCreationResult(
            success=True,
            order=order
        )
        
    except Exception as e:
        # Capturer toute erreur inattendue
        logger.exception(f"Erreur lors de la création de la commande: {str(e)}")
        return OrderCreationResult(
            success=False,
            error_message=f"Erreur lors de la création de la commande: {str(e)}"
        )


# ============================================
# SERVICES AUXILIAIRES
# ============================================

def prepare_cart_items_for_display(cart: Dict[str, int]) -> List[Dict]:
    """
    Prépare les articles du panier pour l'affichage (vue checkout)
    """
    cart_items = []
    
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
        except ProductVariant.DoesNotExist:
            continue
    
    return cart_items


def calculate_cart_subtotal(cart: Dict[str, int]) -> Decimal:
    """Calcule le sous-total du panier"""
    subtotal = Decimal('0')
    
    for variant_id, quantity in cart.items():
        try:
            variant = ProductVariant.objects.get(id=variant_id, is_active=True)
            if variant.stock.is_in_stock:
                subtotal += variant.final_price * quantity
        except ProductVariant.DoesNotExist:
            continue
    
    return subtotal


def clean_cart_from_unavailable_items(cart: Dict[str, int]) -> Dict[str, int]:
    """Nettoie le panier des produits qui ne sont plus disponibles"""
    cleaned_cart = {}
    
    for variant_id, quantity in cart.items():
        try:
            variant = ProductVariant.objects.select_related('stock').get(
                id=variant_id,
                is_active=True
            )
            if variant.stock.is_in_stock:
                cleaned_cart[variant_id] = quantity
        except ProductVariant.DoesNotExist:
            continue
    
    return cleaned_cart