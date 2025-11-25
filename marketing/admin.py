from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from .models import Coupon, CouponUsage, Promotion


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    """
    Administration des coupons de réduction
    """
    list_display = [
        'code',
        'discount_display',
        'minimum_purchase_display',
        'usage_display',
        'validity_display',
        'status_display'
    ]
    list_filter = [
        'is_active',
        'discount_type',
        'valid_from',
        'valid_until',
        'created_at'
    ]
    search_fields = ['code', 'description']
    readonly_fields = ['times_used', 'created_at', 'updated_at']
    date_hierarchy = 'valid_from'
    ordering = ['-created_at']
    
    fieldsets = (
        ('Informations Générales', {
            'fields': ('code', 'description')
        }),
        ('Configuration de la Réduction', {
            'fields': (
                'discount_type',
                'discount_value',
                'max_discount_amount',
                'minimum_purchase'
            )
        }),
        ('Limites d\'Utilisation', {
            'fields': (
                'usage_limit',
                'usage_limit_per_customer',
                'times_used'
            )
        }),
        ('Période de Validité', {
            'fields': ('valid_from', 'valid_until')
        }),
        ('Configuration', {
            'fields': ('is_active',)
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def discount_display(self, obj):
        """Affiche la réduction de manière formatée"""
        if obj.discount_type == 'percentage':
            text = f"{obj.discount_value}%"
            if obj.max_discount_amount:
                text += f" (max {obj.max_discount_amount} FCFA)"
        else:
            text = f"{obj.discount_value} FCFA"
        
        return format_html(
            '<span style="color: #d9534f; font-weight: bold;">{}</span>',
            text
        )
    discount_display.short_description = "Réduction"
    
    def minimum_purchase_display(self, obj):
        """Affiche le montant minimum d'achat"""
        if obj.minimum_purchase > 0:
            return format_html(
                '<span style="color: #5bc0de;">{} FCFA</span>',
                obj.minimum_purchase
            )
        return format_html('<span style="color: #999;">Aucun</span>')
    minimum_purchase_display.short_description = "Achat minimum"
    
    def usage_display(self, obj):
        """Affiche les statistiques d'utilisation"""
        if obj.usage_limit:
            remaining = obj.usage_limit - obj.times_used
            percentage = (obj.times_used / obj.usage_limit) * 100
            
            if percentage >= 100:
                color = '#d9534f'
                status = 'Épuisé'
            elif percentage >= 80:
                color = '#f0ad4e'
                status = f'{remaining} restant(s)'
            else:
                color = '#5cb85c'
                status = f'{remaining} restant(s)'
            
            return format_html(
                '<span style="color: {};">{} / {}</span><br>'
                '<small style="color: {};">{}</small>',
                color,
                obj.times_used,
                obj.usage_limit,
                color,
                status
            )
        else:
            return format_html(
                '<span style="color: #5cb85c;">{} utilisations</span><br>'
                '<small style="color: #999;">Illimité</small>',
                obj.times_used
            )
    usage_display.short_description = "Utilisations"
    
    def validity_display(self, obj):
        """Affiche la période de validité"""
        now = timezone.now()
        
        if now < obj.valid_from:
            status = 'Pas encore valide'
            color = '#999'
        elif now > obj.valid_until:
            status = 'Expiré'
            color = '#d9534f'
        else:
            status = 'Valide'
            color = '#5cb85c'
        
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span><br>'
            '<small>Du {} au {}</small>',
            color,
            status,
            obj.valid_from.strftime('%d/%m/%Y'),
            obj.valid_until.strftime('%d/%m/%Y')
        )
    validity_display.short_description = "Validité"
    
    def status_display(self, obj):
        """Affiche le statut actif/inactif"""
        is_valid, message = obj.is_valid()
        
        if obj.is_active and is_valid:
            return format_html(
                '<span style="background-color: #5cb85c; color: white; padding: 5px 10px; '
                'border-radius: 3px; font-weight: bold;">✓ Actif</span>'
            )
        elif obj.is_active and not is_valid:
            return format_html(
                '<span style="background-color: #f0ad4e; color: white; padding: 5px 10px; '
                'border-radius: 3px; font-weight: bold;">⚠ {}</span>',
                message
            )
        else:
            return format_html(
                '<span style="background-color: #999; color: white; padding: 5px 10px; '
                'border-radius: 3px; font-weight: bold;">✗ Inactif</span>'
            )
    status_display.short_description = "Statut"
    
    actions = ['activate_coupons', 'deactivate_coupons']
    
    def activate_coupons(self, request, queryset):
        """Action pour activer des coupons"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} coupon(s) activé(s).')
    activate_coupons.short_description = "Activer les coupons sélectionnés"
    
    def deactivate_coupons(self, request, queryset):
        """Action pour désactiver des coupons"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} coupon(s) désactivé(s).')
    deactivate_coupons.short_description = "Désactiver les coupons sélectionnés"


@admin.register(CouponUsage)
class CouponUsageAdmin(admin.ModelAdmin):
    """
    Administration des utilisations de coupons
    """
    list_display = [
        'coupon',
        'customer_link',
        'order_link',
        'discount_amount_display',
        'used_at'
    ]
    list_filter = ['used_at', 'coupon']
    search_fields = [
        'coupon__code',
        'customer__user__username',
        'customer__user__email',
        'order__order_number'
    ]
    readonly_fields = ['coupon', 'customer', 'order', 'discount_amount', 'used_at']
    date_hierarchy = 'used_at'
    ordering = ['-used_at']
    
    def has_add_permission(self, request):
        """Empêche l'ajout manuel (créé automatiquement)"""
        return False
    
    def customer_link(self, obj):
        """Affiche un lien vers le client"""
        url = reverse('admin:accounts_customer_change', args=[obj.customer.pk])
        return format_html(
            '<a href="{}" style="text-decoration: none;">'
            '<strong>{}</strong><br>'
            '<small style="color: #666;">{}</small>'
            '</a>',
            url,
            obj.customer.full_name,
            obj.customer.user.email
        )
    customer_link.short_description = "Client"
    
    def order_link(self, obj):
        """Affiche un lien vers la commande"""
        url = reverse('admin:orders_order_change', args=[obj.order.pk])
        return format_html(
            '<a href="{}" style="text-decoration: none;">'
            '<strong>{}</strong><br>'
            '<small style="color: #666;">{} FCFA</small>'
            '</a>',
            url,
            obj.order.order_number,
            obj.order.total
        )
    order_link.short_description = "Commande"
    
    def discount_amount_display(self, obj):
        """Affiche le montant de réduction formaté"""
        return format_html(
            '<span style="color: #d9534f; font-weight: bold;">{} FCFA</span>',
            obj.discount_amount
        )
    discount_amount_display.short_description = "Réduction appliquée"


@admin.register(Promotion)
class PromotionAdmin(admin.ModelAdmin):
    """
    Administration des promotions
    """
    list_display = [
        'name',
        'promotion_type',
        'discount_display',
        'validity_display',
        'priority_display',
        'status_display'
    ]
    list_filter = [
        'is_active',
        'promotion_type',
        'discount_type',
        'is_stackable',
        'valid_from',
        'valid_until'
    ]
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']
    filter_horizontal = ['products', 'categories']
    date_hierarchy = 'valid_from'
    ordering = ['-priority', '-created_at']
    
    fieldsets = (
        ('Informations Générales', {
            'fields': ('name', 'description')
        }),
        ('Type de Promotion', {
            'fields': ('promotion_type',)
        }),
        ('Configuration de la Réduction', {
            'fields': ('discount_type', 'discount_value')
        }),
        ('Cibles de la Promotion', {
            'fields': ('products', 'categories'),
            'description': 'Sélectionnez les produits ou catégories concernés (uniquement pour les promotions de type "Produit" ou "Catégorie")'
        }),
        ('Période de Validité', {
            'fields': ('valid_from', 'valid_until')
        }),
        ('Configuration Avancée', {
            'fields': ('is_active', 'is_stackable', 'priority')
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def discount_display(self, obj):
        """Affiche la réduction de manière formatée"""
        if obj.discount_type == 'percentage':
            text = f"{obj.discount_value}%"
        else:
            text = f"{obj.discount_value} FCFA"
        
        return format_html(
            '<span style="color: #d9534f; font-weight: bold;">{}</span>',
            text
        )
    discount_display.short_description = "Réduction"
    
    def validity_display(self, obj):
        """Affiche la période de validité"""
        now = timezone.now()
        
        if now < obj.valid_from:
            status = 'Pas encore active'
            color = '#999'
        elif now > obj.valid_until:
            status = 'Expirée'
            color = '#d9534f'
        else:
            status = 'Active'
            color = '#5cb85c'
        
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span><br>'
            '<small>Du {} au {}</small>',
            color,
            status,
            obj.valid_from.strftime('%d/%m/%Y'),
            obj.valid_until.strftime('%d/%m/%Y')
        )
    validity_display.short_description = "Validité"
    
    def priority_display(self, obj):
        """Affiche la priorité"""
        if obj.priority >= 10:
            color = '#d9534f'
            label = 'Haute'
        elif obj.priority >= 5:
            color = '#f0ad4e'
            label = 'Moyenne'
        else:
            color = '#5cb85c'
            label = 'Basse'
        
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span><br>'
            '<small>Priorité: {}</small>',
            color,
            label,
            obj.priority
        )
    priority_display.short_description = "Priorité"
    
    def status_display(self, obj):
        """Affiche le statut actif/inactif"""
        is_valid = obj.is_valid()
        
        if obj.is_active and is_valid:
            icon = '✓'
            text = 'Active'
            color = '#5cb85c'
        elif obj.is_active and not is_valid:
            icon = '⚠'
            text = 'Configuration invalide'
            color = '#f0ad4e'
        else:
            icon = '✗'
            text = 'Inactive'
            color = '#999'
        
        stackable = '🔗 Empilable' if obj.is_stackable else ''
        
        return format_html(
            '<span style="background-color: {}; color: white; padding: 5px 10px; '
            'border-radius: 3px; font-weight: bold;">{} {}</span><br>'
            '<small style="color: #666;">{}</small>',
            color,
            icon,
            text,
            stackable
        )
    status_display.short_description = "Statut"
    
    actions = ['activate_promotions', 'deactivate_promotions']
    
    def activate_promotions(self, request, queryset):
        """Action pour activer des promotions"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} promotion(s) activée(s).')
    activate_promotions.short_description = "Activer les promotions sélectionnées"
    
    def deactivate_promotions(self, request, queryset):
        """Action pour désactiver des promotions"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} promotion(s) désactivée(s).')
    deactivate_promotions.short_description = "Désactiver les promotions sélectionnées"