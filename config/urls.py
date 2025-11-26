"""
URL configuration for config project.
"""
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from dashboard.admin import admin_site

urlpatterns = [
    path('admin/', admin_site.urls),
    path('', include('core.urls', namespace='core')),
    path('shop/', include('shop.urls', namespace='shop')),
    path('cart/', include('orders.urls', namespace='orders')),
    path('account/', include('accounts.urls', namespace='accounts')),
    path('payment/', include('payments.urls', namespace='payments')),
    path('marketing/', include('marketing.urls', namespace='marketing')),
]

# Servir les fichiers média en développement ET production
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Les fichiers statiques sont gérés par WhiteNoise, pas besoin de les ajouter ici