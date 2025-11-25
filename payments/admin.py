from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import PaymentMethod, Payment


@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    """
    Administration des moyens de paiement
    """
    list_display = [
        'name',
        'slug',
        'logo_preview',
        'fee_display',
        'is_active_display',
        'display_order',
        'payment_count'
    ]
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'slug', 'description']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['display_order', 'name']
    
    fieldsets = (
        ('Informations Générales', {
            'fields': ('name', 'slug', 'description')
        }),
        ('Configuration des Frais', {
            'fields': ('has_fee', 'fee_type', 'fee_amount', 'fee_percentage', 'instructions')
        }),
        ('Affichage', {
            'fields': ('logo', 'is_active', 'requires_verification', 'display_order')
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def logo_preview(self, obj):
        """Affiche une miniature du logo"""
        if obj.logo:
            return format_html(
                '<img src="{}" style="max-width: 50px; max-height: 50px; '
                'border-radius: 4px; object-fit: contain;" />',
                obj.logo.url
            )
        return format_html('<span style="color: #999;">-</span>')
    logo_preview.short_description = "Logo"
    
    def fee_display(self, obj):
        """Affiche les frais de manière formatée"""
        if not obj.has_fee:
            return format_html('<span style="color: #5cb85c;">Gratuit</span>')
        
        fees = []
        if obj.fee_type == 'percentage' and obj.fee_percentage > 0:
            fees.append(f"{obj.fee_percentage}%")
        if obj.fee_type == 'fixed' and obj.fee_amount > 0:
            fees.append(f"{obj.fee_amount} FCFA")
        
        if fees:
            return format_html(
                '<span style="color: #d9534f; font-weight: bold;">{}</span>',
                ' + '.join(fees)
            )
        return format_html('<span style="color: #999;">Non configuré</span>')
    fee_display.short_description = "Frais"
    
    def is_active_display(self, obj):
        """Affiche le statut actif/inactif"""
        if obj.is_active:
            return format_html(
                '<span style="background-color: #5cb85c; color: white; padding: 3px 8px; '
                'border-radius: 3px; font-weight: bold;">✓ Actif</span>'
            )
        else:
            return format_html(
                '<span style="background-color: #999; color: white; padding: 3px 8px; '
                'border-radius: 3px; font-weight: bold;">✗ Inactif</span>'
            )
    is_active_display.short_description = "Statut"
    
    def payment_count(self, obj):
        """Affiche le nombre de paiements avec cette méthode"""
        count = obj.payments.count()
        return format_html('<strong>{}</strong> paiement(s)', count)
    payment_count.short_description = "Utilisations"
    
    actions = ['activate_methods', 'deactivate_methods']
    
    def activate_methods(self, request, queryset):
        """Action pour activer des moyens de paiement"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} moyen(s) de paiement activé(s).')
    activate_methods.short_description = "Activer les moyens de paiement sélectionnés"
    
    def deactivate_methods(self, request, queryset):
        """Action pour désactiver des moyens de paiement"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} moyen(s) de paiement désactivé(s).')
    deactivate_methods.short_description = "Désactiver les moyens de paiement sélectionnés"


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    """
    Administration des paiements
    """
    list_display = [
        'transaction_id',
        'order_link',
        'payment_method',
        'amount_display',
        'fee_display',
        'status_display',
        'created_at'
    ]
    list_filter = [
        'status',
        'payment_method',
        'created_at',
        'updated_at'
    ]
    search_fields = [
        'transaction_id',
        'order__order_number',
        'external_reference',
        'provider_transaction_id'
    ]
    readonly_fields = [
        'transaction_id',
        'uuid',
        'created_at',
        'updated_at',
        'completed_at',
        'metadata_display'
    ]
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    
    fieldsets = (
        ('Identification', {
            'fields': ('transaction_id', 'uuid', 'order')
        }),
        ('Méthode de Paiement', {
            'fields': ('payment_method',)
        }),
        ('Montants', {
            'fields': ('amount', 'fee_amount', 'total_amount')
        }),
        ('Statut et Suivi', {
            'fields': ('status', 'external_reference', 'provider_transaction_id')
        }),
        ('Messages', {
            'fields': ('customer_message', 'admin_notes', 'failure_reason'),
            'classes': ('collapse',)
        }),
        ('Données Supplémentaires', {
            'fields': ('metadata_display',),
            'classes': ('collapse',)
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at', 'completed_at'),
            'classes': ('collapse',)
        }),
    )
    
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
    
    def amount_display(self, obj):
        """Affiche le montant formaté"""
        return format_html('<strong>{} FCFA</strong>', obj.amount)
    amount_display.short_description = "Montant"
    
    def fee_display(self, obj):
        """Affiche les frais formatés"""
        if obj.fee_amount > 0:
            return format_html(
                '<span style="color: #d9534f;">{} FCFA</span>',
                obj.fee_amount
            )
        return format_html('<span style="color: #999;">-</span>')
    fee_display.short_description = "Frais"
    
    def status_display(self, obj):
        """Affiche le statut avec code couleur"""
        status_colors = {
            'pending': '#f0ad4e',
            'processing': '#5bc0de',
            'completed': '#5cb85c',
            'failed': '#d9534f',
            'refunded': '#999',
            'cancelled': '#999',
        }
        
        status_icons = {
            'pending': '⏳',
            'processing': '⚙️',
            'completed': '✓',
            'failed': '✗',
            'refunded': '↩',
            'cancelled': '✗',
        }
        
        color = status_colors.get(obj.status, '#999')
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
    
    def metadata_display(self, obj):
        """Affiche les métadonnées de manière formatée"""
        if obj.metadata:
            import json
            formatted = json.dumps(obj.metadata, indent=2, ensure_ascii=False)
            return format_html('<pre style="background: #f5f5f5; padding: 10px;">{}</pre>', formatted)
        return '-'
    metadata_display.short_description = "Métadonnées"
    
    actions = [
        'mark_as_completed',
        'mark_as_failed',
        'mark_as_refunded'
    ]
    
    def mark_as_completed(self, request, queryset):
        """Action pour marquer comme complété"""
        from django.utils import timezone
        updated = 0
        for payment in queryset.filter(status__in=['pending', 'processing']):
            payment.status = 'completed'
            payment.completed_at = timezone.now()
            payment.save()
            
            # Marquer la commande comme payée
            payment.order.is_paid = True
            payment.order.paid_at = timezone.now()
            payment.order.save()
            
            updated += 1
        
        self.message_user(request, f'{updated} paiement(s) marqué(s) comme complété(s).')
    mark_as_completed.short_description = "Marquer comme 'Complété'"
    
    def mark_as_failed(self, request, queryset):
        """Action pour marquer comme échoué"""
        updated = queryset.filter(status__in=['pending', 'processing']).update(status='failed')
        self.message_user(request, f'{updated} paiement(s) marqué(s) comme échoué(s).')
    mark_as_failed.short_description = "Marquer comme 'Échoué'"
    
    def mark_as_refunded(self, request, queryset):
        """Action pour marquer comme remboursé"""
        updated = queryset.filter(status='completed').update(status='refunded')
        self.message_user(request, f'{updated} paiement(s) marqué(s) comme remboursé(s).')
    mark_as_refunded.short_description = "Marquer comme 'Remboursé'"
