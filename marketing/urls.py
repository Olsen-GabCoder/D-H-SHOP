"""
marketing/urls.py - Configuration des URLs Marketing
====================================================

Endpoints API pour la gestion des codes promo via AJAX
"""

from django.urls import path
from . import views

app_name = 'marketing'

urlpatterns = [
    # ========================================
    # API AJAX - CODES PROMO
    # ========================================
    
    # Appliquer un code promo au panier
    # POST /marketing/api/apply/
    # Paramètres: code (string)
    # Retour: JSON {success, message, discount_amount, new_total}
    path('api/apply/', views.apply_coupon, name='api_apply_coupon'),
    
    # Retirer un code promo du panier
    # POST /marketing/api/remove/
    # Retour: JSON {success, message, new_total}
    path('api/remove/', views.remove_coupon, name='api_remove_coupon'),
]