from decimal import Decimal
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from accounts.models import Customer
from orders.services import calculate_cart_subtotal
from .services import validate_coupon


@require_POST
@login_required
def apply_coupon(request):
    """
    API AJAX pour valider et appliquer un code promo au panier.
    
    Cette vue :
    - Reçoit un code promo via POST
    - Valide le code avec le service validate_coupon
    - Stocke le résultat en session si valide
    - Retourne une réponse JSON
    
    Returns:
        JsonResponse: {
            success: bool,
            message: str,
            discount_amount: float (si succès),
            new_total: float (si succès)
        }
    """
    
    # 2. Récupérer les données
    code = request.POST.get('code', '').strip()
    
    # Récupérer le panier depuis la session
    cart = request.session.get('cart', {})
    
    # Vérifier que le panier n'est pas vide
    if not cart:
        return JsonResponse({
            'success': False,
            'message': 'Votre panier est vide. Ajoutez des produits avant d\'appliquer un code promo.'
        })
    
    # S'assurer que l'utilisateur a un profil Customer
    # Vérification/Création robuste
    if not hasattr(request.user, 'customer'):
        customer = Customer.objects.create(
            user=request.user,
            phone_number='',  # À compléter par l'utilisateur plus tard
            address='',
            city='',
            country='Tunisia'
        )
    else:
        customer = request.user.customer
    
    # 3. Calculer le montant du panier
    cart_total = calculate_cart_subtotal(cart)
    
    # 4. Appeler le service de validation
    success, message, discount_amount, coupon = validate_coupon(
        code=code,
        customer=customer,
        cart_total=cart_total
    )
    
    # 5. Gérer le succès
    if success:
        # Stocker le code promo et la réduction en session
        request.session['coupon_code'] = coupon.code
        request.session['coupon_discount'] = float(discount_amount)
        
        # Marquer la session comme modifiée
        request.session.modified = True
        
        # Calculer le nouveau total
        new_total = cart_total - discount_amount
        
        return JsonResponse({
            'success': True,
            'message': message,
            'discount_amount': float(discount_amount),
            'new_total': float(new_total)
        })
    
    # 6. Gérer l'échec
    else:
        # Nettoyer la session
        if 'coupon_code' in request.session:
            del request.session['coupon_code']
        if 'coupon_discount' in request.session:
            del request.session['coupon_discount']
        
        # Marquer la session comme modifiée
        request.session.modified = True
        
        return JsonResponse({
            'success': False,
            'message': message
        })


@require_POST
@login_required
def remove_coupon(request):
    """
    API AJAX pour retirer un code promo du panier.
    
    Returns:
        JsonResponse: {
            success: bool,
            message: str,
            new_total: float
        }
    """
    
    # Récupérer le panier depuis la session
    cart = request.session.get('cart', {})
    
    # Supprimer le coupon de la session
    if 'coupon_code' in request.session:
        del request.session['coupon_code']
    if 'coupon_discount' in request.session:
        del request.session['coupon_discount']
    
    # Marquer la session comme modifiée
    request.session.modified = True
    
    # Recalculer le total sans réduction
    cart_total = calculate_cart_subtotal(cart)
    
    return JsonResponse({
        'success': True,
        'message': 'Code promo retiré avec succès',
        'new_total': float(cart_total)
    })