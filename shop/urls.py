from django.urls import path
from . import views

app_name = 'shop'

urlpatterns = [
    # Liste des produits
    path('', views.product_list, name='product_list'),
    
    # Catégories
    path('category/<slug:slug>/', views.category_detail, name='category_detail'),
    
    # Détail d'un produit
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),
    
    # Recherche
    path('search/', views.product_search, name='product_search'),
]
