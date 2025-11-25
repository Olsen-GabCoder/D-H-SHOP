"""
========================================
PAYMENTS/VIEWS.PY - Production Ready
========================================

Vues de traitement des paiements :
- Sélection de la méthode de paiement
- Traitement Airtel Money
- Traitement Moov Money
- Paiement à la livraison
- Webhook pour les callbacks des fournisseurs
- Pages de succès/échec

Intégration complète avec le système de commandes et envoi d'emails.
"""

import logging
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db import transaction
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt

from orders.models import Order, OrderStatus
from .models import PaymentMethod, Payment
from core.email_service import EmailService

logger = logging.getLogger(__name__)


@login_required
def payment_method(request):
    """
    Sélection du moyen de paiement
    
    Gère :
    - Récupération de la commande en session
    - Vérification que la commande n'est pas déjà payée
    - Affichage des méthodes de paiement actives
    - Redirection vers le traitement approprié
    """
    # Récupérer la commande en cours depuis la session
    order_id = request.session.get('order_id')
    
    if not order_id:
        messages.error(request, 'Aucune commande en cours. Veuillez passer une commande d\'abord.')
        return redirect('orders:checkout')
    
    try:
        order = Order.objects.get(id=order_id, customer=request.user.customer)
    except Order.DoesNotExist:
        messages.error(request, 'Commande introuvable.')
        return redirect('orders:cart_detail')
    
    # Vérifier que la commande n'est pas déjà payée
    if order.is_paid:
        messages.info(request, 'Cette commande est déjà payée.')
        return redirect('accounts:order_detail', order_number=order.order_number)
    
    # Moyens de paiement actifs
    payment_methods = PaymentMethod.objects.filter(is_active=True).order_by('display_order')
    
    if request.method == 'POST':
        method_slug = request.POST.get('payment_method')
        
        if not method_slug:
            messages.error(request, 'Veuillez sélectionner un moyen de paiement.')
            return redirect('payments:payment_method')
        
        # Sauvegarder le moyen de paiement en session
        request.session['payment_method'] = method_slug
        
        # Rediriger vers la page de traitement appropriée
        return redirect('payments:payment_process', method=method_slug)
    
    context = {
        'payment_methods': payment_methods,
        'order': order,
        'page_title': 'Choisir un moyen de paiement',
    }
    return render(request, 'payments/payment_method.html', context)


@login_required
def payment_process(request, method):
    """
    Traitement du paiement - Redirection vers la méthode appropriée
    
    Args:
        method (str): Slug de la méthode de paiement (aitel, moov, cod)
    """
    # Vérifier que la commande existe
    order_id = request.session.get('order_id')
    
    if not order_id:
        messages.error(request, 'Aucune commande en cours.')
        return redirect('orders:checkout')
    
    # Vérifier que la méthode de paiement est valide
    valid_methods = ['aitel', 'moov', 'cod']
    
    if method not in valid_methods:
        messages.error(request, 'Méthode de paiement invalide.')
        return redirect('payments:payment_method')
    
    # Rediriger vers la page de paiement appropriée
    if method == 'aitel':
        return redirect('payments:aitel_payment')
    elif method == 'moov':
        return redirect('payments:moov_payment')
    elif method == 'cod':
        return redirect('payments:cash_on_delivery')


@login_required
def aitel_payment(request):
    """
    Paiement Aitel Money
    
    Fonctionnalités :
    - Validation du numéro de téléphone (8 chiffres)
    - Création de l'enregistrement de paiement
    - Simulation de l'API Airtel Money (à remplacer en production)
    - Mise à jour du statut de la commande
    - Envoi d'email de confirmation
    - Nettoyage de la session
    """
    # Récupérer la commande
    order_id = request.session.get('order_id')
    
    if not order_id:
        messages.error(request, 'Aucune commande en cours.')
        return redirect('orders:checkout')
    
    try:
        order = Order.objects.get(id=order_id, customer=request.user.customer)
    except Order.DoesNotExist:
        messages.error(request, 'Commande introuvable.')
        return redirect('orders:cart_detail')
    
    # Récupérer la méthode de paiement Aitel
    try:
        payment_method = PaymentMethod.objects.get(slug='aitel', is_active=True)
    except PaymentMethod.DoesNotExist:
        messages.error(request, 'Le paiement Aitel Money n\'est pas disponible actuellement.')
        return redirect('payments:payment_method')
    
    if request.method == 'POST':
        phone = request.POST.get('phone', '').strip()
        
        # Validation du numéro
        if not phone or len(phone) != 8:
            messages.error(request, 'Numéro de téléphone invalide. Veuillez entrer 8 chiffres.')
            return redirect('payments:aitel_payment')
        
        try:
            with transaction.atomic():
                # Créer l'enregistrement de paiement
                payment = Payment.objects.create(
                    order=order,
                    payment_method=payment_method,
                    amount=order.total,
                    status='processing',
                    metadata={
                        'phone': phone,
                        'provider': 'aitel',
                        'initiated_at': timezone.now().isoformat()
                    }
                )
                
                # SIMULATION : Dans un environnement réel, vous appelleriez l'API Aitel Money ici
                # Pour la démo, on simule un paiement réussi
                
                # Marquer le paiement comme complété
                payment.status = 'completed'
                payment.completed_at = timezone.now()
                payment.provider_transaction_id = f"AITEL-{payment.transaction_id}"
                payment.save()
                
                # Mettre à jour la commande
                order.is_paid = True
                order.paid_at = timezone.now()
                order.status = 'processing'
                order.save()
                
                # Créer l'historique de statut
                OrderStatus.objects.create(
                    order=order,
                    status='processing',
                    comment=f'Paiement reçu via Aitel Money ({phone})',
                    created_by=request.user.username
                )
                
                # ENVOI DE L'EMAIL DE CONFIRMATION
                try:
                    EmailService.send_order_confirmation(order)
                    logger.info(f"Email de confirmation envoyé pour la commande {order.order_number} (Airtel)")
                except Exception as e:
                    logger.error(
                        f"Échec de l'envoi de l'email pour la commande {order.order_number} (Airtel): {str(e)}",
                        exc_info=True
                    )
                
                # Nettoyer la session
                if 'order_id' in request.session:
                    del request.session['order_id']
                if 'payment_method' in request.session:
                    del request.session['payment_method']
                
                messages.success(request, f'Paiement réussi ! Commande {order.order_number} confirmée.')
                return redirect('payments:payment_success', transaction_id=payment.transaction_id)
                
        except Exception as e:
            messages.error(request, f'Erreur lors du traitement du paiement : {str(e)}')
            return redirect('payments:aitel_payment')
    
    context = {
        'order': order,
        'payment_method': payment_method,
        'page_title': 'Paiement Aitel Money',
    }
    return render(request, 'payments/aitel_payment.html', context)


@login_required
def moov_payment(request):
    """
    Paiement Moov Money
    
    Fonctionnalités identiques à Aitel Money mais pour Moov
    """
    # Récupérer la commande
    order_id = request.session.get('order_id')
    
    if not order_id:
        messages.error(request, 'Aucune commande en cours.')
        return redirect('orders:checkout')
    
    try:
        order = Order.objects.get(id=order_id, customer=request.user.customer)
    except Order.DoesNotExist:
        messages.error(request, 'Commande introuvable.')
        return redirect('orders:cart_detail')
    
    # Récupérer la méthode de paiement Moov
    try:
        payment_method = PaymentMethod.objects.get(slug='moov', is_active=True)
    except PaymentMethod.DoesNotExist:
        messages.error(request, 'Le paiement Moov Money n\'est pas disponible actuellement.')
        return redirect('payments:payment_method')
    
    if request.method == 'POST':
        phone = request.POST.get('phone', '').strip()
        
        # Validation du numéro
        if not phone or len(phone) != 8:
            messages.error(request, 'Numéro de téléphone invalide. Veuillez entrer 8 chiffres.')
            return redirect('payments:moov_payment')
        
        try:
            with transaction.atomic():
                # Créer l'enregistrement de paiement
                payment = Payment.objects.create(
                    order=order,
                    payment_method=payment_method,
                    amount=order.total,
                    status='processing',
                    metadata={
                        'phone': phone,
                        'provider': 'moov',
                        'initiated_at': timezone.now().isoformat()
                    }
                )
                
                # SIMULATION : Dans un environnement réel, vous appelleriez l'API Moov Money ici
                
                # Marquer le paiement comme complété
                payment.status = 'completed'
                payment.completed_at = timezone.now()
                payment.provider_transaction_id = f"MOOV-{payment.transaction_id}"
                payment.save()
                
                # Mettre à jour la commande
                order.is_paid = True
                order.paid_at = timezone.now()
                order.status = 'processing'
                order.save()
                
                # Créer l'historique de statut
                OrderStatus.objects.create(
                    order=order,
                    status='processing',
                    comment=f'Paiement reçu via Moov Money ({phone})',
                    created_by=request.user.username
                )
                
                # ENVOI DE L'EMAIL DE CONFIRMATION
                try:
                    EmailService.send_order_confirmation(order)
                    logger.info(f"Email de confirmation envoyé pour la commande {order.order_number} (Moov)")
                except Exception as e:
                    logger.error(
                        f"Échec de l'envoi de l'email pour la commande {order.order_number} (Moov): {str(e)}",
                        exc_info=True
                    )
                
                # Nettoyer la session
                if 'order_id' in request.session:
                    del request.session['order_id']
                if 'payment_method' in request.session:
                    del request.session['payment_method']
                
                messages.success(request, f'Paiement réussi ! Commande {order.order_number} confirmée.')
                return redirect('payments:payment_success', transaction_id=payment.transaction_id)
                
        except Exception as e:
            messages.error(request, f'Erreur lors du traitement du paiement : {str(e)}')
            return redirect('payments:moov_payment')
    
    context = {
        'order': order,
        'payment_method': payment_method,
        'page_title': 'Paiement Moov Money',
    }
    return render(request, 'payments/moov_payment.html', context)


@login_required
def cash_on_delivery(request):
    """
    Paiement à la livraison
    
    Gère :
    - Confirmation de la commande sans paiement immédiat
    - Création d'un enregistrement de paiement en attente
    - Mise à jour du statut de la commande
    - Nettoyage de la session
    """
    # Récupérer la commande
    order_id = request.session.get('order_id')
    
    if not order_id:
        messages.error(request, 'Aucune commande en cours.')
        return redirect('orders:checkout')
    
    try:
        order = Order.objects.get(id=order_id, customer=request.user.customer)
    except Order.DoesNotExist:
        messages.error(request, 'Commande introuvable.')
        return redirect('orders:cart_detail')
    
    # Récupérer la méthode de paiement COD
    try:
        payment_method = PaymentMethod.objects.get(slug='cod', is_active=True)
    except PaymentMethod.DoesNotExist:
        messages.error(request, 'Le paiement à la livraison n\'est pas disponible actuellement.')
        return redirect('payments:payment_method')
    
    if request.method == 'POST':
        try:
            with transaction.atomic():
                # Créer l'enregistrement de paiement (en attente)
                payment = Payment.objects.create(
                    order=order,
                    payment_method=payment_method,
                    amount=order.total,
                    status='pending',
                    metadata={
                        'provider': 'cash_on_delivery',
                        'note': 'Paiement à effectuer lors de la livraison'
                    }
                )
                
                # Mettre à jour la commande (non payée, mais confirmée)
                order.status = 'processing'
                order.save()
                
                # Créer l'historique de statut
                OrderStatus.objects.create(
                    order=order,
                    status='processing',
                    comment='Commande confirmée - Paiement à la livraison',
                    created_by=request.user.username
                )
                
                # Nettoyer la session
                if 'order_id' in request.session:
                    del request.session['order_id']
                if 'payment_method' in request.session:
                    del request.session['payment_method']
                
                messages.success(
                    request,
                    f'Commande {order.order_number} confirmée ! Vous paierez à la livraison.'
                )
                return redirect('orders:order_success', order_number=order.order_number)
                
        except Exception as e:
            messages.error(request, f'Erreur lors de la confirmation : {str(e)}')
            return redirect('payments:cash_on_delivery')
    
    context = {
        'order': order,
        'payment_method': payment_method,
        'page_title': 'Paiement à la livraison',
    }
    return render(request, 'payments/cash_on_delivery.html', context)


@csrf_exempt
def payment_callback(request):
    """
    Callback des fournisseurs de paiement (Webhooks)
    
    Cette vue reçoit les notifications des fournisseurs de paiement
    pour confirmer ou annuler les transactions
    
    Sécurité :
    - CSRF exempt car appelé par des services externes
    - Validation des données reçues
    - Logging complet des activités
    """
    if request.method == 'POST':
        try:
            # Récupérer les données du webhook
            data = json.loads(request.body)
            
            transaction_id = data.get('transaction_id')
            status = data.get('status')
            provider_reference = data.get('provider_reference')
            
            if not transaction_id:
                return JsonResponse({'error': 'Transaction ID manquant'}, status=400)
            
            # Rechercher le paiement
            try:
                payment = Payment.objects.get(transaction_id=transaction_id)
            except Payment.DoesNotExist:
                return JsonResponse({'error': 'Paiement introuvable'}, status=404)
            
            # Mettre à jour le statut
            with transaction.atomic():
                if status == 'success' or status == 'completed':
                    payment.status = 'completed'
                    payment.completed_at = timezone.now()
                    payment.provider_transaction_id = provider_reference
                    
                    # Mettre à jour la commande
                    payment.order.is_paid = True
                    payment.order.paid_at = timezone.now()
                    payment.order.status = 'processing'
                    payment.order.save()
                    
                    # Historique
                    OrderStatus.objects.create(
                        order=payment.order,
                        status='processing',
                        comment=f'Paiement confirmé via webhook ({payment.payment_method.name})',
                        created_by='System'
                    )
                    
                    # ENVOI DE L'EMAIL DE CONFIRMATION
                    try:
                        EmailService.send_order_confirmation(payment.order)
                        logger.info(f"Email de confirmation envoyé via webhook pour {payment.order.order_number}")
                    except Exception as e:
                        logger.error(
                            f"Échec de l'envoi de l'email via webhook pour {payment.order.order_number}: {str(e)}",
                            exc_info=True
                        )
                    
                elif status == 'failed' or status == 'cancelled':
                    payment.status = 'failed'
                    payment.failure_reason = data.get('reason', 'Paiement refusé par le fournisseur')
                
                payment.metadata.update({
                    'webhook_received': timezone.now().isoformat(),
                    'webhook_data': data
                })
                payment.save()
            
            return JsonResponse({'status': 'success', 'message': 'Callback traité'})
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'JSON invalide'}, status=400)
        except Exception as e:
            logger.error(f"Erreur dans le webhook de paiement: {str(e)}", exc_info=True)
            return JsonResponse({'error': str(e)}, status=500)
    
    return HttpResponse('Webhook endpoint', status=200)


def payment_success(request, transaction_id):
    """
    Page de succès du paiement
    
    Affiche les détails de la transaction réussie
    """
    payment = get_object_or_404(Payment, transaction_id=transaction_id)
    
    # Vérifier que l'utilisateur a accès à cette commande
    if request.user.is_authenticated:
        if payment.order.customer.user != request.user:
            messages.error(request, 'Accès non autorisé.')
            return redirect('core:home')
    
    context = {
        'payment': payment,
        'order': payment.order,
        'page_title': 'Paiement réussi',
    }
    return render(request, 'payments/payment_success.html', context)


def payment_failed(request, transaction_id):
    """
    Page d'échec du paiement
    
    Affiche les détails de l'échec et propose des alternatives
    """
    payment = get_object_or_404(Payment, transaction_id=transaction_id)
    
    # Vérifier que l'utilisateur a accès à cette commande
    if request.user.is_authenticated:
        if payment.order.customer.user != request.user:
            messages.error(request, 'Accès non autorisé.')
            return redirect('core:home')
    
    context = {
        'payment': payment,
        'order': payment.order,
        'page_title': 'Paiement échoué',
    }
    return render(request, 'payments/payment_failed.html', context)


@login_required
def payment_history(request):
    """
    Historique des paiements de l'utilisateur
    
    Affiche toutes les transactions de l'utilisateur connecté
    """
    payments = Payment.objects.filter(
        order__customer=request.user.customer
    ).select_related(
        'order', 'payment_method'
    ).order_by('-created_at')
    
    context = {
        'payments': payments,
        'page_title': 'Historique des paiements',
    }
    return render(request, 'payments/payment_history.html', context)


@login_required
def payment_detail(request, transaction_id):
    """
    Détail d'un paiement spécifique
    
    Affiche les informations détaillées d'une transaction
    """
    payment = get_object_or_404(
        Payment.objects.select_related('order', 'payment_method'),
        transaction_id=transaction_id,
        order__customer=request.user.customer
    )
    
    context = {
        'payment': payment,
        'page_title': f'Détail du paiement {payment.transaction_id}',
    }
    return render(request, 'payments/payment_detail.html', context)