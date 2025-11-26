"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
"""
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# ========================================
# Import du site admin personnalisé
# ========================================
from dashboard.admin import admin_site

urlpatterns = [
    # ========================================
    # INTERFACE D'ADMINISTRATION UNIQUE
    # ========================================
    
    # Admin personnalisé avec Dashboard (interface principale)
    # Accessible via /admin/
    path('admin/', admin_site.urls),
    
    # ========================================
    # APPLICATIONS PUBLIQUES
    # ========================================
    
    path('', include('core.urls', namespace='core')),
    path('shop/', include('shop.urls', namespace='shop')),
    path('cart/', include('orders.urls', namespace='orders')),
    path('account/', include('accounts.urls', namespace='accounts')),
    path('payment/', include('payments.urls', namespace='payments')),
    
    # ✅ NOUVEAU : API Marketing (codes promo)
    # Endpoints AJAX pour la gestion des coupons
    path('marketing/', include('marketing.urls', namespace='marketing')),
]

# ========================================
# SERVIR LES FICHIERS MÉDIA EN DÉVELOPPEMENT ET PRODUCTION
# ========================================
# ✅ CORRECTION : Servir les médias même en production pendant la transition vers Cloudinary
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Les fichiers statiques sont gérés par WhiteNoise automatiquement, pas besoin de les ajouter ici