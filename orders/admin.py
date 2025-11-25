"""
Administration Django pour le module Orders
Inclut la gestion des commandes, articles, statuts, zones et tarifs de livraison
✅ OPTIMISÉ : Requêtes N+1 corrigées avec select_related et prefetch_related
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.db.models import Count, Sum, Prefetch, Q
from django.utils import timezone
from .models import (
    Order, 
    OrderItem, 
    OrderStatus, 
    ShippingZone, 
    ShippingRate
)
from core.email_service import EmailService
import logging

logger = logging.getLogger('core.email_service')


# ========================================
# ADMIN POUR SHIPPINGZONE
# ========================================

@admin.register(ShippingZone)
class ShippingZoneAdmin(admin.ModelAdmin):
    """
    Administration des zones de livraison
    """
    list_display = [
        'name',
        'cities_preview',
        'delivery_times_display',
        'rates_count',
        'orders_count',
        'is_active_display',
        'display_order'
    ]
    list_filter = [
        'is_active',
        'created_at',
        'updated_at'
    ]
    search_fields = [
        'name',
        'slug',
        'covered_cities',
        'description'
    ]
    prepopulated_fields = {
        'slug': ('name',)
    }
    readonly_fields = [
        'created_at',
        'updated_at',
        'orders_count_readonly',
        'total_revenue'
    ]
    ordering = ['display_order', 'name']
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('name', 'slug', 'description')
        }),
        ('Couverture géographique', {
            'fields': ('covered_cities',),
            'description': 'Séparez les villes/quartiers par des virgules. Ex: Libreville, Owendo, Akanda'
        }),
        ('Délais de livraison', {
            'fields': (
                ('standard_delivery_days_min', 'standard_delivery_days_max'),
                ('express_delivery_days_min', 'express_delivery_days_max')
            ),
            'description': 'Délais en jours ouvrables'
        }),
        ('Configuration', {
            'fields': ('is_active', 'display_order')
        }),
        ('Statistiques', {
            'fields': ('orders_count_readonly', 'total_revenue', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """
        ✅ OPTIMISATION N+1 : Précharge les rates actifs avec annotation
        """
        qs = super().get_queryset(request)
        # Annoter avec le nombre de tarifs actifs et total
        qs = qs.annotate(
            active_rates_count=Count('rates', filter=Q(rates__is_active=True)),
            total_rates_count=Count('rates')
        )
        return qs
    
    def cities_preview(self, obj):
        """Affiche un aperçu des villes couvertes"""
        cities = obj.get_cities_list()
        if not cities:
            return format_html('<span style="color: #999;">Aucune ville</span>')
        
        if len(cities) <= 3:
            cities_str = ', '.join(cities)
        else:
            cities_str = ', '.join(cities[:3]) + f' <span style="color: #666;">(+{len(cities)-3})</span>'
        
        return format_html(
            '<span style="font-size: 12px;">{}</span>',
            cities_str
        )
    cities_preview.short_description = "Villes couvertes"
    
    def delivery_times_display(self, obj):
        """Affiche les délais de livraison"""
        return format_html(
            '<div style="font-size: 11px;">'
            '<strong>Standard:</strong> {}-{} jours<br>'
            '<strong>Express:</strong> {}-{} jours'
            '</div>',
            obj.standard_delivery_days_min,
            obj.standard_delivery_days_max,
            obj.express_delivery_days_min,
            obj.express_delivery_days_max
        )
    delivery_times_display.short_description = "Délais"
    
    def rates_count(self, obj):
        """Affiche le nombre de tarifs associés (utilise les annotations)"""
        count = obj.active_rates_count
        total = obj.total_rates_count
        
        if count == 0:
            return format_html(
                '<span style="color: #d9534f; font-weight: bold;">⚠ Aucun tarif</span>'
            )
        
        return format_html(
            '<span style="color: #5cb85c; font-weight: bold;">{}</span> / {}',
            count,
            total
        )
    rates_count.short_description = "Tarifs actifs"
    
    def orders_count(self, obj):
        """Affiche le nombre de commandes utilisant cette zone"""
        count = obj.orders.count()
        return format_html('<strong>{}</strong>', count)
    orders_count.short_description = "Commandes"
    
    def orders_count_readonly(self, obj):
        """Version readonly pour le fieldset"""
        return self.orders_count(obj)
    orders_count_readonly.short_description = "Nombre de commandes"
    
    def total_revenue(self, obj):
        """Calcule le revenu total des commandes de cette zone"""
        total = obj.orders.aggregate(total=Sum('total'))['total'] or 0
        total_float = float(total)
        formatted_total = f'{total_float:,.0f}'
        return format_html('<strong>{} FCFA</strong>', formatted_total)
    total_revenue.short_description = "Revenu total"
    
    def is_active_display(self, obj):
        """Affiche le statut actif/inactif"""
        if obj.is_active:
            return format_html(
                '<span style="background-color: #5cb85c; color: white; padding: 3px 8px; '
                'border-radius: 3px; font-weight: bold;">✓ Active</span>'
            )
        else:
            return format_html(
                '<span style="background-color: #d9534f; color: white; padding: 3px 8px; '
                'border-radius: 3px; font-weight: bold;">✗ Inactive</span>'
            )
    is_active_display.short_description = "Statut"
    
    actions = [
        'activate_zones',
        'deactivate_zones',
        'duplicate_zone'
    ]
    
    def activate_zones(self, request, queryset):
        """Active les zones sélectionnées"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} zone(s) activée(s).')
    activate_zones.short_description = "Activer les zones sélectionnées"
    
    def deactivate_zones(self, request, queryset):
        """Désactive les zones sélectionnées"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} zone(s) désactivée(s).')
    deactivate_zones.short_description = "Désactiver les zones sélectionnées"
    
    def duplicate_zone(self, request, queryset):
        """Duplique les zones sélectionnées"""
        count = 0
        for zone in queryset:
            # Dupliquer la zone
            zone_copy = ShippingZone.objects.get(pk=zone.pk)
            zone_copy.pk = None
            zone_copy.name = f"{zone.name} (Copie)"
            zone_copy.slug = f"{zone.slug}-copy"
            zone_copy.is_active = False
            zone_copy.save()
            
            # Dupliquer les tarifs associés
            for rate in zone.rates.all():
                rate_copy = ShippingRate.objects.get(pk=rate.pk)
                rate_copy.pk = None
                rate_copy.zone = zone_copy
                rate_copy.save()
            
            count += 1
        
        self.message_user(request, f'{count} zone(s) dupliquée(s) avec leurs tarifs.')
    duplicate_zone.short_description = "Dupliquer les zones sélectionnées"


# ========================================
# ADMIN POUR SHIPPINGRATE
# ========================================

@admin.register(ShippingRate)
class ShippingRateAdmin(admin.ModelAdmin):
    """
    Administration des tarifs de livraison
    """
    list_display = [
        'zone_name',
        'delivery_type_display',
        'price_display',
        'free_shipping_display',
        'min_order_display',
        'orders_count',
        'is_active_display',
        'updated_at'
    ]
    list_filter = [
        'delivery_type',
        'is_active',
        'zone',
        'created_at',
        'updated_at'
    ]
    search_fields = [
        'zone__name',
        'zone__slug'
    ]
    readonly_fields = [
        'created_at',
        'updated_at',
        'orders_count_readonly',
        'total_revenue'
    ]
    ordering = ['zone__display_order', 'delivery_type']
    
    fieldsets = (
        ('Zone et Type', {
            'fields': ('zone', 'delivery_type')
        }),
        ('Tarification', {
            'fields': ('price',),
            'description': 'Prix de base de la livraison en FCFA'
        }),
        ('Conditions optionnelles', {
            'fields': ('min_order_amount', 'free_shipping_threshold'),
            'description': 'Laissez à 0 ou vide pour ne pas appliquer de conditions'
        }),
        ('Configuration', {
            'fields': ('is_active',)
        }),
        ('Statistiques', {
            'fields': ('orders_count_readonly', 'total_revenue', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """
        ✅ OPTIMISATION N+1 : Précharge la zone associée
        """
        qs = super().get_queryset(request)
        return qs.select_related('zone')
    
    def zone_name(self, obj):
        """Affiche le nom de la zone avec lien"""
        url = reverse('admin:orders_shippingzone_change', args=[obj.zone.pk])
        return format_html(
            '<a href="{}" style="text-decoration: none; font-weight: bold;">{}</a>',
            url,
            obj.zone.name
        )
    zone_name.short_description = "Zone"
    
    def delivery_type_display(self, obj):
        """Affiche le type de livraison avec icône"""
        icons = {
            'standard': '📦',
            'express': '⚡'
        }
        colors = {
            'standard': '#5bc0de',
            'express': '#f0ad4e'
        }
        
        icon = icons.get(obj.delivery_type, '📦')
        color = colors.get(obj.delivery_type, '#999')
        
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 10px; '
            'border-radius: 3px; font-weight: bold; font-size: 12px;">'
            '{} {}</span>',
            color,
            icon,
            obj.get_delivery_type_display()
        )
    delivery_type_display.short_description = "Type"
    
    def price_display(self, obj):
        """Affiche le prix formaté"""
        price = float(obj.price)
        formatted_price = f'{price:,.0f}'
        return format_html(
            '<strong style="font-size: 14px; color: #333;">{} FCFA</strong>',
            formatted_price
        )
    price_display.short_description = "Prix"
    
    def free_shipping_display(self, obj):
        """Affiche les informations de livraison gratuite"""
        if obj.is_free_shipping_available:
            threshold = float(obj.free_shipping_threshold)
            formatted_threshold = f'{threshold:,.0f}'
            return format_html(
                '<span style="color: #5cb85c; font-weight: bold;">✓</span> '
                'Gratuit dès <strong>{} FCFA</strong>',
                formatted_threshold
            )
        else:
            return format_html('<span style="color: #999;">Non disponible</span>')
    free_shipping_display.short_description = "Livraison gratuite"
    
    def min_order_display(self, obj):
        """Affiche le montant minimum de commande"""
        if obj.min_order_amount > 0:
            min_amount = float(obj.min_order_amount)
            formatted_amount = f'{min_amount:,.0f}'
            return format_html('{} FCFA', formatted_amount)
        else:
            return format_html('<span style="color: #999;">Aucun minimum</span>')
    min_order_display.short_description = "Minimum"
    
    def orders_count(self, obj):
        """Affiche le nombre de commandes utilisant ce tarif"""
        count = obj.orders.count()
        if count > 0:
            return format_html('<strong style="color: #5cb85c;">{}</strong>', count)
        return format_html('<span style="color: #999;">{}</span>', count)
    orders_count.short_description = "Commandes"
    
    def orders_count_readonly(self, obj):
        """Version readonly pour le fieldset"""
        return self.orders_count(obj)
    orders_count_readonly.short_description = "Nombre de commandes"
    
    def total_revenue(self, obj):
        """Calcule le revenu total des commandes avec ce tarif"""
        total = obj.orders.aggregate(total=Sum('shipping_cost'))['total'] or 0
        total_float = float(total)
        formatted_total = f'{total_float:,.0f}'
        return format_html('<strong>{} FCFA</strong>', formatted_total)
    total_revenue.short_description = "Revenu livraison"
    
    def is_active_display(self, obj):
        """Affiche le statut actif/inactif"""
        if obj.is_active:
            return format_html(
                '<span style="background-color: #5cb85c; color: white; padding: 3px 8px; '
                'border-radius: 3px; font-weight: bold; font-size: 11px;">✓ Actif</span>'
            )
        else:
            return format_html(
                '<span style="background-color: #d9534f; color: white; padding: 3px 8px; '
                'border-radius: 3px; font-weight: bold; font-size: 11px;">✗ Inactif</span>'
            )
    is_active_display.short_description = "Statut"
    
    actions = [
        'activate_rates',
        'deactivate_rates',
        'apply_discount_10',
        'apply_discount_20'
    ]
    
    def activate_rates(self, request, queryset):
        """Active les tarifs sélectionnés"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} tarif(s) activé(s).')
    activate_rates.short_description = "Activer les tarifs sélectionnés"
    
    def deactivate_rates(self, request, queryset):
        """Désactive les tarifs sélectionnés"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} tarif(s) désactivé(s).')
    deactivate_rates.short_description = "Désactiver les tarifs sélectionnés"
    
    def apply_discount_10(self, request, queryset):
        """Applique une réduction de 10% sur les tarifs sélectionnés"""
        from decimal import Decimal
        count = 0
        for rate in queryset:
            rate.price = rate.price * Decimal('0.90')
            rate.save()
            count += 1
        self.message_user(request, f'Réduction de 10% appliquée sur {count} tarif(s).')
    apply_discount_10.short_description = "Appliquer -10% sur les tarifs"
    
    def apply_discount_20(self, request, queryset):
        """Applique une réduction de 20% sur les tarifs sélectionnés"""
        from decimal import Decimal
        count = 0
        for rate in queryset:
            rate.price = rate.price * Decimal('0.80')
            rate.save()
            count += 1
        self.message_user(request, f'Réduction de 20% appliquée sur {count} tarif(s).')
    apply_discount_20.short_description = "Appliquer -20% sur les tarifs"


# ========================================
# INLINES POUR ORDER
# ========================================

class OrderItemInline(admin.TabularInline):
    """
    Gestion des articles d'une commande (inline)
    """
    model = OrderItem
    extra = 0
    fields = ['product_name', 'variant_details', 'quantity', 'unit_price', 'subtotal']
    readonly_fields = ['product_name', 'variant_details', 'unit_price', 'quantity', 'subtotal']
    can_delete = False
    
    def has_add_permission(self, request, obj=None):
        # Empêcher l'ajout d'articles après création de la commande
        return False


class OrderStatusInline(admin.TabularInline):
    """
    Historique des statuts d'une commande (inline)
    """
    model = OrderStatus
    extra = 1
    fields = ['status', 'comment', 'created_by', 'created_at']
    readonly_fields = ['created_at']
    
    def save_model(self, request, obj, form, change):
        """Ajoute automatiquement le nom de l'utilisateur et envoie l'email si nécessaire"""
        if not obj.created_by:
            obj.created_by = request.user.username
        
        # Vérifier si le statut change pour 'shipped'
        if obj.status == 'shipped':
            # Envoyer l'email d'expédition
            try:
                EmailService.send_order_shipped(obj.order)
                logger.info(f'Email d\'expédition envoyé pour la commande {obj.order.order_number}')
            except Exception as e:
                logger.error(f'Échec envoi email expédition pour {obj.order.order_number}: {str(e)}')
        
        super().save_model(request, obj, form, change)


# ========================================
# ADMIN POUR ORDER
# ========================================

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """
    Administration des commandes avec support complet des zones de livraison
    """
    list_display = [
        'order_number',
        'customer_info',
        'shipping_info_display',
        'total_display',
        'item_count_display',
        'status_display',
        'payment_status',
        'created_at'
    ]
    list_filter = [
        'status',
        'is_paid',
        'delivery_type',
        'shipping_zone',
        'created_at',
        'updated_at'
    ]
    search_fields = [
        'order_number',
        'customer__user__username',
        'customer__user__email',
        'customer__user__first_name',
        'customer__user__last_name',
        'customer_email',
        'customer_phone',
        'tracking_number'
    ]
    readonly_fields = [
        'order_number',
        'uuid',
        'customer',
        'created_at',
        'updated_at',
        'paid_at',
        'subtotal',
        'total',
        'calculated_shipping_cost'
    ]
    ordering = ['-created_at']
    
    inlines = [OrderItemInline, OrderStatusInline]
    
    fieldsets = (
        ('Informations de la commande', {
            'fields': ('order_number', 'uuid', 'customer', 'status', 'is_paid', 'paid_at')
        }),
        ('Adresses', {
            'fields': ('shipping_address', 'billing_address')
        }),
        ('Livraison', {
            'fields': (
                'shipping_zone',
                'shipping_rate',
                'delivery_type',
                'tracking_number',
                'calculated_shipping_cost'
            ),
            'description': 'Informations sur la zone et le tarif de livraison'
        }),
        ('Contact', {
            'fields': ('customer_email', 'customer_phone')
        }),
        ('Montants', {
            'fields': (
                'subtotal',
                'shipping_cost',
                'tax_amount',
                'discount_amount',
                'total',
                'coupon_code'
            )
        }),
        ('Notes', {
            'fields': ('customer_notes', 'admin_notes'),
            'classes': ('collapse',)
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """
        ✅ OPTIMISATION N+1 : Précharge toutes les relations nécessaires
        """
        qs = super().get_queryset(request)
        return qs.select_related(
            'customer',
            'customer__user',
            'shipping_zone',
            'shipping_rate',
            'shipping_address',
            'billing_address'
        ).prefetch_related(
            Prefetch('items', queryset=OrderItem.objects.select_related('product', 'variant'))
        )
    
    actions = [
        'mark_as_processing',
        'mark_as_shipped',
        'mark_as_delivered',
        'mark_as_paid',
        'cancel_orders',
        'send_shipping_email',
        'recalculate_shipping'
    ]
    
    def customer_info(self, obj):
        """Affiche les informations du client avec lien"""
        customer_url = reverse('admin:accounts_customer_change', args=[obj.customer.pk])
        return format_html(
            '<a href="{}" style="text-decoration: none;">'
            '<strong>{}</strong><br>'
            '<small style="color: #666;">{}</small><br>'
            '<small style="color: #666;">{}</small>'
            '</a>',
            customer_url,
            obj.customer.full_name,
            obj.customer_email,
            obj.customer_phone or '-'
        )
    customer_info.short_description = "Client"
    
    def shipping_info_display(self, obj):
        """Affiche les informations de livraison"""
        if obj.shipping_zone:
            delivery_icons = {
                'standard': '📦',
                'express': '⚡'
            }
            icon = delivery_icons.get(obj.delivery_type, '📦')
            
            shipping_cost = float(obj.shipping_cost)
            formatted_cost = f'{shipping_cost:,.0f}'
            
            return format_html(
                '<div style="font-size: 11px;">'
                '<strong>{}</strong><br>'
                '<span style="color: #666;">{} {}</span><br>'
                '<span style="color: #5cb85c; font-weight: bold;">{} FCFA</span>'
                '</div>',
                obj.shipping_zone.name,
                icon,
                obj.get_delivery_type_display(),
                formatted_cost
            )
        else:
            shipping_cost = float(obj.shipping_cost)
            formatted_cost = f'{shipping_cost:,.0f}'
            
            return format_html(
                '<span style="color: #999;">{}</span><br>'
                '<span style="color: #5cb85c; font-weight: bold;">{} FCFA</span>',
                obj.get_delivery_type_display(),
                formatted_cost
            )
    shipping_info_display.short_description = "Livraison"
    
    def calculated_shipping_cost(self, obj):
        """Affiche le coût de livraison calculé"""
        if obj.shipping_rate:
            calculated_cost = obj.shipping_rate.calculate_shipping_cost(obj.subtotal)
            if calculated_cost == 0:
                threshold = obj.shipping_rate.free_shipping_threshold or 0
                threshold_float = float(threshold)
                formatted_threshold = f'{threshold_float:,.0f}'
                return format_html(
                    '<span style="color: #5cb85c; font-weight: bold; font-size: 14px;">GRATUIT ✓</span><br>'
                    '<small style="color: #999;">Seuil atteint: {} FCFA</small>',
                    formatted_threshold
                )
            else:
                calculated_float = float(calculated_cost)
                formatted_calculated = f'{calculated_float:,.0f}'
                return format_html(
                    '<strong style="font-size: 14px;">{} FCFA</strong>',
                    formatted_calculated
                )
        return format_html('<span style="color: #999;">N/A</span>')
    calculated_shipping_cost.short_description = "Coût calculé"
    
    def total_display(self, obj):
        """Affiche le total avec formatage"""
        total = float(obj.total)
        formatted_total = f'{total:,.0f}'
        return format_html(
            '<strong style="font-size: 14px; color: #28a745;">{} FCFA</strong>',
            formatted_total
        )
    total_display.short_description = "Total"
    
    def item_count_display(self, obj):
        """Affiche le nombre d'articles"""
        count = obj.item_count
        return format_html('<strong>{}</strong> article(s)', count)
    item_count_display.short_description = "Articles"
    
    def status_display(self, obj):
        """Affiche le statut avec code couleur"""
        status_colors = {
            'pending': '#ffc107',
            'processing': '#17a2b8',
            'shipped': '#007bff',
            'delivered': '#28a745',
            'cancelled': '#dc3545',
            'refunded': '#6c757d',
        }
        
        status_icons = {
            'pending': '⏳',
            'processing': '⚙️',
            'shipped': '🚚',
            'delivered': '✓',
            'cancelled': '✗',
            'refunded': '↩',
        }
        
        color = status_colors.get(obj.status, '#6c757d')
        icon = status_icons.get(obj.status, '•')
        
        return format_html(
            '<span style="background-color: {}; color: white; padding: 5px 10px; '
            'border-radius: 3px; font-weight: bold; display: inline-block;">'
            '{} {}</span>',
            color,
            icon,
            obj.get_status_display()
        )
    status_display.short_description = "Statut"
    
    def payment_status(self, obj):
        """Affiche le statut de paiement"""
        if obj.is_paid:
            return format_html(
                '<span style="background-color: #28a745; color: white; padding: 5px 10px; '
                'border-radius: 3px; font-weight: bold;">✓ Payé</span>'
            )
        else:
            return format_html(
                '<span style="background-color: #dc3545; color: white; padding: 5px 10px; '
                'border-radius: 3px; font-weight: bold;">✗ Non payé</span>'
            )
    payment_status.short_description = "Paiement"
    
    # Actions admin
    
    def mark_as_processing(self, request, queryset):
        """
        Action pour marquer comme en traitement
        ✅ FAILLE #7 CORRIGÉE : Logique explicite de mise à jour du statut
        """
        count = 0
        for order in queryset:
            if order.status == 'pending':
                # 1. Mettre à jour le statut de la commande
                order.status = 'processing'
                order.save()
                
                # 2. Créer l'historique de statut (sans effet de bord)
                OrderStatus.objects.create(
                    order=order,
                    status='processing',
                    comment='Marqué en traitement depuis l\'admin',
                    created_by=request.user.username
                )
                count += 1
        
        self.message_user(request, f'{count} commande(s) marquée(s) en traitement.')
    mark_as_processing.short_description = "Marquer comme 'En traitement'"
    
    def mark_as_shipped(self, request, queryset):
        """
        Action pour marquer les commandes comme expédiées avec envoi d'email
        ✅ FAILLE #7 CORRIGÉE : Logique explicite de mise à jour du statut
        """
        count = 0
        for order in queryset:
            if order.status in ['pending', 'processing']:
                # 1. Mettre à jour le statut de la commande
                order.status = 'shipped'
                order.save()
                
                # 2. Créer l'historique de statut (sans effet de bord)
                OrderStatus.objects.create(
                    order=order,
                    status='shipped',
                    comment='Marqué comme expédié depuis l\'admin',
                    created_by=request.user.username
                )
                
                # 3. Envoyer l'email
                try:
                    EmailService.send_order_shipped(order)
                    logger.info(f'Email d\'expédition envoyé pour {order.order_number}')
                except Exception as e:
                    logger.error(f'Échec envoi email pour {order.order_number}: {str(e)}')
                
                count += 1
        
        self.message_user(
            request,
            f'{count} commande(s) marquée(s) comme expédiée(s) et emails envoyés.'
        )
    mark_as_shipped.short_description = "Marquer comme 'Expédié' (avec email)"
    
    def mark_as_delivered(self, request, queryset):
        """Action pour marquer les commandes comme livrées"""
        count = 0
        for order in queryset:
            if order.status == 'shipped':
                order.status = 'delivered'
                order.save()
                
                OrderStatus.objects.create(
                    order=order,
                    status='delivered',
                    comment='Marqué comme livré depuis l\'admin',
                    created_by=request.user.username
                )
                count += 1
        
        self.message_user(request, f'{count} commande(s) marquée(s) comme livrée(s).')
    mark_as_delivered.short_description = "Marquer comme 'Livré'"
    
    def mark_as_paid(self, request, queryset):
        """Action pour marquer comme payé"""
        updated = queryset.filter(is_paid=False).update(is_paid=True, paid_at=timezone.now())
        self.message_user(request, f'{updated} commande(s) marquée(s) comme payée(s).')
    mark_as_paid.short_description = "Marquer comme payé"
    
    def cancel_orders(self, request, queryset):
        """
        Action pour annuler des commandes
        ✅ FAILLE #7 CORRIGÉE : Logique explicite de mise à jour du statut
        """
        count = 0
        for order in queryset:
            if order.status in ['pending', 'processing']:
                # 1. Mettre à jour le statut de la commande
                order.status = 'cancelled'
                order.save()
                
                # 2. Créer l'historique de statut (sans effet de bord)
                OrderStatus.objects.create(
                    order=order,
                    status='cancelled',
                    comment='Commande annulée via action admin',
                    created_by=request.user.username
                )
                count += 1
        
        self.message_user(
            request, 
            f'{count} commande(s) annulée(s) (seules celles en attente ou en traitement).'
        )
    cancel_orders.short_description = "Annuler les commandes sélectionnées"
    
    def send_shipping_email(self, request, queryset):
        """Action pour renvoyer l'email d'expédition"""
        count = 0
        for order in queryset:
            try:
                EmailService.send_order_shipped(order)
                count += 1
                logger.info(f'Email d\'expédition renvoyé pour {order.order_number}')
            except Exception as e:
                logger.error(f'Échec envoi email pour {order.order_number}: {str(e)}')
        
        self.message_user(request, f'{count} email(s) d\'expédition envoyé(s).')
    send_shipping_email.short_description = "Renvoyer l'email d'expédition"
    
    def recalculate_shipping(self, request, queryset):
        """Recalcule les frais de livraison en fonction des tarifs actuels"""
        count = 0
        for order in queryset:
            if order.shipping_rate:
                old_cost = order.shipping_cost
                new_cost = order.shipping_rate.calculate_shipping_cost(order.subtotal)
                
                if old_cost != new_cost:
                    order.shipping_cost = new_cost
                    order.calculate_total()
                    count += 1
        
        if count > 0:
            self.message_user(request, f'Frais de livraison recalculés pour {count} commande(s).')
        else:
            self.message_user(request, 'Aucune modification nécessaire.', level='warning')
    recalculate_shipping.short_description = "Recalculer les frais de livraison"


# ========================================
# ADMIN POUR ORDERITEM
# ========================================

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    """
    Administration des articles de commande
    """
    list_display = [
        'order_link',
        'product_name',
        'variant_details',
        'quantity',
        'unit_price_display',
        'subtotal_display',
        'created_at'
    ]
    list_filter = ['created_at']
    search_fields = [
        'order__order_number',
        'product_name',
        'variant_details'
    ]
    readonly_fields = [
        'order',
        'product',
        'variant',
        'product_name',
        'variant_details',
        'unit_price',
        'quantity',
        'subtotal',
        'created_at'
    ]
    ordering = ['-created_at']
    
    fieldsets = (
        ('Commande', {
            'fields': ('order',)
        }),
        ('Produit', {
            'fields': ('product', 'variant', 'product_name', 'variant_details')
        }),
        ('Prix et Quantité', {
            'fields': ('unit_price', 'quantity', 'subtotal')
        }),
        ('Date', {
            'fields': ('created_at',)
        }),
    )
    
    def get_queryset(self, request):
        """
        ✅ OPTIMISATION N+1 : Précharge la commande associée
        """
        qs = super().get_queryset(request)
        return qs.select_related('order', 'product', 'variant')
    
    def order_link(self, obj):
        """Affiche un lien vers la commande"""
        url = reverse('admin:orders_order_change', args=[obj.order.pk])
        return format_html(
            '<a href="{}" style="text-decoration: none; font-weight: bold;">{}</a>',
            url,
            obj.order.order_number
        )
    order_link.short_description = "Commande"
    
    def unit_price_display(self, obj):
        """Affiche le prix unitaire formaté"""
        unit_price = float(obj.unit_price)
        formatted_price = f'{unit_price:,.0f}'
        return format_html('{} FCFA', formatted_price)
    unit_price_display.short_description = "Prix unitaire"
    
    def subtotal_display(self, obj):
        """Affiche le sous-total formaté"""
        subtotal = float(obj.subtotal)
        formatted_subtotal = f'{subtotal:,.0f}'
        return format_html('<strong>{} FCFA</strong>', formatted_subtotal)
    subtotal_display.short_description = "Sous-total"


# ========================================
# ADMIN POUR ORDERSTATUS
# ========================================

@admin.register(OrderStatus)
class OrderStatusAdmin(admin.ModelAdmin):
    """
    Administration de l'historique des statuts
    """
    list_display = [
        'order_link',
        'status_display',
        'comment_preview',
        'created_by',
        'created_at'
    ]
    list_filter = ['status', 'created_at']
    search_fields = [
        'order__order_number',
        'comment',
        'created_by'
    ]
    readonly_fields = ['order', 'created_at']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Commande', {
            'fields': ('order',)
        }),
        ('Statut', {
            'fields': ('status', 'comment')
        }),
        ('Informations', {
            'fields': ('created_by', 'created_at')
        }),
    )
    
    def get_queryset(self, request):
        """
        ✅ OPTIMISATION N+1 : Précharge la commande associée
        """
        qs = super().get_queryset(request)
        return qs.select_related('order')
    
    def order_link(self, obj):
        """Affiche un lien vers la commande"""
        url = reverse('admin:orders_order_change', args=[obj.order.pk])
        return format_html(
            '<a href="{}" style="text-decoration: none; font-weight: bold;">{}</a>',
            url,
            obj.order.order_number
        )
    order_link.short_description = "Commande"
    
    def status_display(self, obj):
        """Affiche le statut avec code couleur"""
        status_colors = {
            'pending': '#ffc107',
            'processing': '#17a2b8',
            'shipped': '#007bff',
            'delivered': '#28a745',
            'cancelled': '#dc3545',
            'refunded': '#6c757d',
        }
        
        color = status_colors.get(obj.status, '#6c757d')
        
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; '
            'border-radius: 3px; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_display.short_description = "Statut"
    
    def comment_preview(self, obj):
        """Affiche un aperçu du commentaire"""
        if obj.comment:
            preview = obj.comment[:50]
            if len(obj.comment) > 50:
                preview += '...'
            return preview
        return '-'
    comment_preview.short_description = "Commentaire"