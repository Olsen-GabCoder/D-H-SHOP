from decimal import Decimal
from django.db.models import F
from django.core.exceptions import ObjectDoesNotExist
from .models import Coupon, CouponUsage


def validate_coupon(code, customer, cart_total):
    """
    Valide un code promo et calcule la réduction applicable.
    
    Args:
        code (str): Le code promo à valider
        customer (Customer): L'objet client qui veut utiliser le coupon
        cart_total (Decimal): Le montant total du panier
    
    Returns:
        tuple: (success: bool, message: str, discount_amount: Decimal, coupon: Coupon|None)
    """
    
    # 1. Nettoyage : Vérifier si le code n'est pas vide
    if not code or not code.strip():
        return False, "Veuillez saisir un code promo", Decimal('0.00'), None
    
    code = code.strip()
    
    # 2. Recherche : Récupérer le coupon en base de données
    try:
        coupon = Coupon.objects.get(code__iexact=code, is_active=True)
    except ObjectDoesNotExist:
        return False, "Ce code promo n'existe pas ou n'est plus valide", Decimal('0.00'), None
    
    # 3. Validité globale : Vérifier la validité du coupon
    is_valid, validity_message = coupon.is_valid()
    if not is_valid:
        return False, validity_message, Decimal('0.00'), None
    
    # 4. Minimum d'achat : Vérifier le montant minimum requis
    if cart_total < coupon.minimum_purchase:
        return (
            False,
            f"Ce coupon nécessite un achat minimum de {coupon.minimum_purchase} FCFA. "
            f"Votre panier actuel : {cart_total} FCFA",
            Decimal('0.00'),
            None
        )
    
    # 5. Validité Client : Vérifier si le client peut utiliser ce coupon
    can_use, customer_message = coupon.can_be_used_by_customer(customer)
    if not can_use:
        return False, customer_message, Decimal('0.00'), None
    
    # 6. Calcul : Calculer le montant de la réduction
    discount_amount = coupon.calculate_discount(cart_total)
    
    # 7. Plafond de sécurité : S'assurer que la réduction ne dépasse pas le total
    discount_amount = min(discount_amount, cart_total)
    
    # Formatage du message de succès
    if coupon.discount_type == 'percentage':
        success_message = f"Code promo '{coupon.code}' appliqué : -{coupon.discount_value}% ({discount_amount} FCFA)"
    else:
        success_message = f"Code promo '{coupon.code}' appliqué : -{discount_amount} FCFA"
    
    return True, success_message, discount_amount, coupon


def record_coupon_usage(order, coupon):
    """
    Enregistre l'utilisation d'un coupon après validation d'une commande.
    
    Args:
        order (Order): L'objet commande validée
        coupon (Coupon): L'objet coupon utilisé
    
    Returns:
        CouponUsage: L'objet CouponUsage créé
    """
    
    # 1. Créer l'historique : Enregistrer l'utilisation du coupon
    coupon_usage = CouponUsage.objects.create(
        coupon=coupon,
        customer=order.customer,
        order=order,
        discount_amount=order.discount_amount
    )
    
    # 2. Incrémenter le compteur : Mettre à jour times_used de manière atomique
    # Utilisation de F() pour éviter les problèmes de concurrence
    Coupon.objects.filter(pk=coupon.pk).update(times_used=F('times_used') + 1)
    
    return coupon_usage