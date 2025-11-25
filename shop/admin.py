from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Product, ProductImage, ProductVariant, Stock


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """
    Administration des catégories
    """
    list_display = ['name', 'parent', 'display_order', 'is_active', 'product_count', 'created_at']
    list_filter = ['is_active', 'parent', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['display_order', 'is_active']
    ordering = ['display_order', 'name']
    
    fieldsets = (
        ('Informations principales', {
            'fields': ('name', 'slug', 'description', 'parent')
        }),
        ('Image', {
            'fields': ('image',)
        }),
        ('Configuration', {
            'fields': ('is_active', 'display_order')
        }),
    )
    
    def product_count(self, obj):
        """Affiche le nombre de produits dans cette catégorie"""
        count = obj.products.count()
        return format_html('<strong>{}</strong> produit(s)', count)
    product_count.short_description = "Nombre de produits"


class ProductImageInline(admin.TabularInline):
    """
    Gestion des images supplémentaires d'un produit (inline)
    """
    model = ProductImage
    extra = 1
    fields = ['image', 'alt_text', 'display_order']


class ProductVariantInline(admin.TabularInline):
    """
    Gestion des variantes d'un produit (inline)
    """
    model = ProductVariant
    extra = 1
    fields = ['sku', 'size', 'color', 'color_code', 'price_adjustment', 'is_active']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """
    Administration des produits
    """
    list_display = [
        'name', 
        'category', 
        'display_price', 
        'has_discount', 
        'is_active', 
        'is_featured', 
        'is_new',
        'stock_status',
        'views_count',
        'sales_count'
    ]
    list_filter = ['category', 'is_active', 'is_featured', 'is_new', 'created_at']
    search_fields = ['name', 'description', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['is_active', 'is_featured', 'is_new']
    ordering = ['-created_at']
    # ✅ CORRECTION : date_hierarchy commenté pour éviter l'erreur timezone MySQL
    # date_hierarchy = 'created_at'
    
    inlines = [ProductImageInline, ProductVariantInline]
    
    fieldsets = (
        ('Informations principales', {
            'fields': ('name', 'slug', 'category', 'description', 'short_description')
        }),
        ('Prix', {
            'fields': ('base_price', 'sale_price')
        }),
        ('Image principale', {
            'fields': ('main_image',)
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description'),
            'classes': ('collapse',)
        }),
        ('Configuration', {
            'fields': ('is_active', 'is_featured', 'is_new')
        }),
        ('Statistiques', {
            'fields': ('views_count', 'sales_count'),
            'classes': ('collapse',)
        }),
    )
    
    def display_price(self, obj):
        """Affiche le prix avec indication de promotion"""
        if obj.has_discount:
            return format_html(
                '<span style="text-decoration: line-through; color: #999;">{} FCFA</span><br>'
                '<strong style="color: #d9534f;">{} FCFA</strong>',
                obj.base_price,
                obj.sale_price
            )
        return format_html('<strong>{} FCFA</strong>', obj.base_price)
    display_price.short_description = "Prix"
    
    def has_discount(self, obj):
        """Affiche une icône si le produit est en promotion"""
        if obj.has_discount:
            return format_html(
                '<span style="color: #d9534f;">✓ {}%</span>',
                obj.discount_percentage
            )
        return format_html('<span style="color: #999;">-</span>')
    has_discount.short_description = "Promo"
    
    def stock_status(self, obj):
        """Affiche le statut du stock"""
        variants = obj.variants.all()
        if not variants:
            return format_html('<span style="color: #999;">Aucune variante</span>')
        
        total_stock = sum(
            v.stock.available_quantity 
            for v in variants 
            if hasattr(v, 'stock')
        )
        
        if total_stock == 0:
            color = '#d9534f'
            status = 'Rupture'
        elif total_stock < 10:
            color = '#f0ad4e'
            status = f'Stock faible ({total_stock})'
        else:
            color = '#5cb85c'
            status = f'En stock ({total_stock})'
        
        return format_html('<span style="color: {};">{}</span>', color, status)
    stock_status.short_description = "Stock"
    
    actions = ['activate_products', 'deactivate_products', 'mark_as_featured']
    
    def activate_products(self, request, queryset):
        """Action pour activer plusieurs produits"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} produit(s) activé(s).')
    activate_products.short_description = "Activer les produits sélectionnés"
    
    def deactivate_products(self, request, queryset):
        """Action pour désactiver plusieurs produits"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} produit(s) désactivé(s).')
    deactivate_products.short_description = "Désactiver les produits sélectionnés"
    
    def mark_as_featured(self, request, queryset):
        """Action pour marquer comme produits phares"""
        updated = queryset.update(is_featured=True)
        self.message_user(request, f'{updated} produit(s) marqué(s) comme phare(s).')
    mark_as_featured.short_description = "Marquer comme produits phares"


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    """
    Administration des variantes de produits
    """
    list_display = ['__str__', 'product', 'sku', 'size', 'color', 'price_adjustment', 'stock_info', 'is_active']
    list_filter = ['product__category', 'size', 'is_active']
    search_fields = ['sku', 'product__name', 'color']
    list_editable = ['is_active']
    
    fieldsets = (
        ('Produit', {
            'fields': ('product',)
        }),
        ('Variante', {
            'fields': ('sku', 'size', 'color', 'color_code')
        }),
        ('Prix', {
            'fields': ('price_adjustment',)
        }),
        ('Configuration', {
            'fields': ('is_active',)
        }),
    )
    
    def stock_info(self, obj):
        """Affiche les informations de stock"""
        if hasattr(obj, 'stock'):
            stock = obj.stock
            if stock.is_in_stock:
                if stock.is_low_stock:
                    return format_html(
                        '<span style="color: #f0ad4e;">⚠ {} en stock</span>',
                        stock.available_quantity
                    )
                return format_html(
                    '<span style="color: #5cb85c;">✓ {} en stock</span>',
                    stock.available_quantity
                )
            return format_html('<span style="color: #d9534f;">✗ Rupture</span>')
        return format_html('<span style="color: #999;">Non défini</span>')
    stock_info.short_description = "Stock"


@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    """
    Administration des stocks
    """
    list_display = [
        'variant',
        'quantity',
        'reserved_quantity',
        'available_display',
        'stock_status',
        'low_stock_threshold',
        'last_restocked',
        'updated_at'
    ]
    list_filter = ['last_restocked', 'updated_at']
    search_fields = ['variant__product__name', 'variant__sku']
    readonly_fields = ['updated_at']
    
    fieldsets = (
        ('Variante', {
            'fields': ('variant',)
        }),
        ('Quantités', {
            'fields': ('quantity', 'reserved_quantity', 'low_stock_threshold')
        }),
        ('Réapprovisionnement', {
            'fields': ('last_restocked',)
        }),
    )
    
    def available_display(self, obj):
        """Affiche la quantité disponible"""
        return format_html('<strong>{}</strong>', obj.available_quantity)
    available_display.short_description = "Disponible"
    
    def stock_status(self, obj):
        """Affiche le statut du stock avec code couleur"""
        if not obj.is_in_stock:
            return format_html(
                '<span style="background-color: #d9534f; color: white; padding: 3px 8px; border-radius: 3px;">Rupture</span>'
            )
        elif obj.is_low_stock:
            return format_html(
                '<span style="background-color: #f0ad4e; color: white; padding: 3px 8px; border-radius: 3px;">Stock faible</span>'
            )
        else:
            return format_html(
                '<span style="background-color: #5cb85c; color: white; padding: 3px 8px; border-radius: 3px;">En stock</span>'
            )
    stock_status.short_description = "Statut"