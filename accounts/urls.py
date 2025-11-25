from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # Authentification
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Dashboard client
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Profil
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    
    # Adresses
    path('addresses/', views.address_list, name='address_list'),
    path('addresses/add/', views.address_add, name='address_add'),
    path('addresses/<int:pk>/edit/', views.address_edit, name='address_edit'),
    path('addresses/<int:pk>/delete/', views.address_delete, name='address_delete'),
    
    # ✅ CORRECTION : Ajout de l'URL manquante pour définir l'adresse par défaut
    path('addresses/<int:address_id>/set-default/', views.address_set_default, name='address_set_default'),
    
    # Commandes
    path('orders/', views.order_list, name='order_list'),
    path('orders/<str:order_number>/', views.order_detail, name='order_detail'),
    
    # PDF - Factures et Bons de livraison
    path('orders/<str:order_number>/invoice/', views.order_invoice, name='order_invoice'),
    path('orders/<str:order_number>/packing-slip/', views.order_packing_slip, name='order_packing_slip'),
    
    # ============================================================
    # RÉINITIALISATION DU MOT DE PASSE (Vues personnalisées)
    # ============================================================
    path('password-reset/', views.password_reset_request, name='password_reset'),
    path('password-reset/done/', views.password_reset_done, name='password_reset_done'),
    path('password-reset/<uidb64>/<token>/', views.password_reset_confirm, name='password_reset_confirm'),
    path('password-reset/complete/', views.password_reset_complete, name='password_reset_complete'),
]