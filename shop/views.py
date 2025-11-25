from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Product, Category


def product_list(request):
    """
    Liste de tous les produits
    """
    products = Product.objects.filter(is_active=True).order_by('-created_at')
    
    # Pagination
    paginator = Paginator(products, 12)  # 12 produits par page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Catégories pour le filtre
    categories = Category.objects.filter(is_active=True, parent__isnull=True)
    
    context = {
        'page_obj': page_obj,
        'categories': categories,
        'page_title': 'Tous les produits',
    }
    return render(request, 'shop/product_list.html', context)


def category_detail(request, slug):
    """
    Produits d'une catégorie spécifique
    """
    category = get_object_or_404(Category, slug=slug, is_active=True)
    
    # Produits de cette catégorie
    products = Product.objects.filter(
        category=category,
        is_active=True
    ).order_by('-created_at')
    
    # Pagination
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Sous-catégories
    subcategories = category.children.filter(is_active=True)
    
    context = {
        'category': category,
        'page_obj': page_obj,
        'subcategories': subcategories,
        'page_title': category.name,
    }
    return render(request, 'shop/category_detail.html', context)


def product_detail(request, slug):
    """
    Détail d'un produit
    """
    product = get_object_or_404(Product, slug=slug, is_active=True)
    
    # Incrémenter le compteur de vues
    product.views_count += 1
    product.save(update_fields=['views_count'])
    
    # Images supplémentaires
    additional_images = product.images.all().order_by('display_order')
    
    # Variantes disponibles
    variants = product.variants.filter(is_active=True).select_related('stock')
    
    # Produits similaires (même catégorie)
    related_products = Product.objects.filter(
        category=product.category,
        is_active=True
    ).exclude(id=product.id)[:4]
    
    context = {
        'product': product,
        'additional_images': additional_images,
        'variants': variants,
        'related_products': related_products,
        'page_title': product.name,
    }
    return render(request, 'shop/product_detail.html', context)


def product_search(request):
    """
    Recherche de produits
    """
    query = request.GET.get('q', '').strip()
    
    if query:
        # Recherche dans le nom et la description
        products = Product.objects.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query) |
            Q(short_description__icontains=query),
            is_active=True
        ).order_by('-created_at')
    else:
        products = Product.objects.none()
    
    # Pagination
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'query': query,
        'products_count': products.count(),
        'page_title': f'Recherche : {query}' if query else 'Recherche',
    }
    return render(request, 'shop/product_search.html', context)