from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    # Sélection du moyen de paiement
    path('method/', views.payment_method, name='payment_method'),
    
    # Traitement des paiements
    path('process/<str:method>/', views.payment_process, name='payment_process'),
    
    # Paiements mobiles (Aitel Money, Moov Money)
    path('mobile/aitel/', views.aitel_payment, name='aitel_payment'),
    path('mobile/moov/', views.moov_payment, name='moov_payment'),
    
    # Paiement à la livraison
    path('cod/', views.cash_on_delivery, name='cash_on_delivery'),
    
    # Confirmation et statut
    path('callback/', views.payment_callback, name='payment_callback'),
    path('success/<str:transaction_id>/', views.payment_success, name='payment_success'),
    path('failed/<str:transaction_id>/', views.payment_failed, name='payment_failed'),
]