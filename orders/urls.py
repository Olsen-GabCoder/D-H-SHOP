from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    # ========================================
    # PANIER (CART)
    # ========================================
    
    # Affichage du panier
    path('', views.cart_detail, name='cart_detail'),
    
    # Ajouter un produit au panier
    path('add/<int:variant_id>/', views.cart_add, name='cart_add'),
    
    # Mettre à jour la quantité d'un article
    path('update/<int:variant_id>/', views.cart_update, name='cart_update'),
    
    # Supprimer un article du panier
    path('remove/<int:variant_id>/', views.cart_remove, name='cart_remove'),
    
    # Vider complètement le panier
    path('clear/', views.cart_clear, name='cart_clear'),
    
    # ========================================
    # CHECKOUT (PROCESSUS DE COMMANDE)
    # ========================================
    
    # Page de checkout (formulaire livraison/paiement)
    path('checkout/', views.checkout, name='checkout'),
    
    # Confirmation et création de la commande
    path('checkout/confirm/', views.checkout_confirm, name='checkout_confirm'),
    
    # ========================================
    # CONFIRMATION DE COMMANDE
    # ========================================
    
    # Page de succès après commande
    path('order/<str:order_number>/success/', views.order_success, name='order_success'),

    # Téléchargement de facture
    path('invoice/<str:order_number>/download/', views.download_invoice, name='download_invoice'),

    # Prévisualisation (optionnel)
    path('invoice/<str:order_number>/preview/', views.preview_invoice, name='preview_invoice'),
]