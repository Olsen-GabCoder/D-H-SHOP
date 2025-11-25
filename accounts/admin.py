from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.utils.html import format_html
from .models import Customer, Address


class AddressInline(admin.TabularInline):
    """
    Gestion des adresses d'un client (inline)
    """
    model = Address
    extra = 0
    fields = ['full_name', 'phone', 'city', 'address_type', 'is_default']
    readonly_fields = []
    
    def has_delete_permission(self, request, obj=None):
        return True


class CustomerInline(admin.StackedInline):
    """
    Profil Customer inline dans User
    """
    model = Customer
    can_delete = False
    verbose_name_plural = 'Profil Client'
    fields = [
        'phone', 
        'date_of_birth', 
        'profile_picture',
        'email_notifications',
        'sms_notifications',
        'whatsapp_notifications',
        'is_blocked',
        'block_reason'
    ]


class UserAdmin(BaseUserAdmin):
    """
    Extension de l'admin User pour inclure le profil Customer
    """
    inlines = [CustomerInline]
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_staff', 'customer_stats']
    
    def get_queryset(self, request):
        """
        ✅ OPTIMISATION N+1 : Précharge le profil customer
        """
        qs = super().get_queryset(request)
        return qs.select_related('customer')
    
    def customer_stats(self, obj):
        """Affiche les statistiques du client"""
        if hasattr(obj, 'customer'):
            customer = obj.customer
            return format_html(
                '<strong>{}</strong> commande(s)<br><strong>{} FCFA</strong> dépensés',
                customer.total_orders,
                customer.total_spent
            )
        return '-'
    customer_stats.short_description = "Statistiques"


# Désenregistrer l'admin User par défaut et enregistrer le nôtre
admin.site.unregister(User)
admin.site.register(User, UserAdmin)


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    """
    Administration des clients
    """
    list_display = [
        'full_name',
        'user_email',
        'phone',
        'total_orders',
        'total_spent_display',
        'account_status',
        'notification_preferences',
        'created_at'
    ]
    list_filter = [
        'is_blocked',
        'email_notifications',
        'sms_notifications',
        'whatsapp_notifications',
        'created_at'
    ]
    search_fields = [
        'user__username',
        'user__email',
        'user__first_name',
        'user__last_name',
        'phone'
    ]
    readonly_fields = ['created_at', 'updated_at', 'total_orders', 'total_spent']
    # ✅ CORRECTION : date_hierarchy commenté pour éviter l'erreur timezone MySQL
    # date_hierarchy = 'created_at'
    ordering = ['-created_at']
    
    inlines = [AddressInline]
    
    fieldsets = (
        ('Utilisateur', {
            'fields': ('user',)
        }),
        ('Informations personnelles', {
            'fields': ('phone', 'date_of_birth', 'profile_picture')
        }),
        ('Préférences de communication', {
            'fields': ('email_notifications', 'sms_notifications', 'whatsapp_notifications')
        }),
        ('Statistiques', {
            'fields': ('total_orders', 'total_spent'),
            'classes': ('collapse',)
        }),
        ('Gestion du compte', {
            'fields': ('is_blocked', 'block_reason')
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """
        ✅ OPTIMISATION N+1 : Précharge l'utilisateur lié
        """
        qs = super().get_queryset(request)
        return qs.select_related('user')
    
    def full_name(self, obj):
        """Affiche le nom complet du client"""
        return obj.full_name
    full_name.short_description = "Nom complet"
    
    def user_email(self, obj):
        """Affiche l'email du client"""
        return obj.email
    user_email.short_description = "Email"
    
    def total_spent_display(self, obj):
        """Affiche le montant total dépensé avec formatage"""
        return format_html('<strong>{} FCFA</strong>', obj.total_spent)
    total_spent_display.short_description = "Total dépensé"
    
    def account_status(self, obj):
        """Affiche le statut du compte avec code couleur"""
        if obj.is_blocked:
            return format_html(
                '<span style="background-color: #d9534f; color: white; padding: 3px 8px; border-radius: 3px;">🔒 Bloqué</span>'
            )
        else:
            return format_html(
                '<span style="background-color: #5cb85c; color: white; padding: 3px 8px; border-radius: 3px;">✓ Actif</span>'
            )
    account_status.short_description = "Statut"
    
    def notification_preferences(self, obj):
        """Affiche les préférences de notification"""
        prefs = []
        if obj.email_notifications:
            prefs.append('📧 Email')
        if obj.sms_notifications:
            prefs.append('📱 SMS')
        if obj.whatsapp_notifications:
            prefs.append('💬 WhatsApp')
        
        if prefs:
            return format_html('<br>'.join(prefs))
        return format_html('<span style="color: #999;">Aucune</span>')
    notification_preferences.short_description = "Notifications"
    
    actions = ['block_customers', 'unblock_customers']
    
    def block_customers(self, request, queryset):
        """Action pour bloquer plusieurs clients"""
        updated = queryset.update(is_blocked=True)
        self.message_user(request, f'{updated} client(s) bloqué(s).')
    block_customers.short_description = "Bloquer les clients sélectionnés"
    
    def unblock_customers(self, request, queryset):
        """Action pour débloquer plusieurs clients"""
        updated = queryset.update(is_blocked=False, block_reason='')
        self.message_user(request, f'{updated} client(s) débloqué(s).')
    unblock_customers.short_description = "Débloquer les clients sélectionnés"


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    """
    Administration des adresses
    """
    list_display = [
        'full_name',
        'customer',
        'phone',
        'city',
        'country',
        'address_type_display',
        'is_default',
        'created_at'
    ]
    list_filter = ['address_type', 'is_default', 'country', 'city', 'created_at']
    search_fields = [
        'full_name',
        'phone',
        'customer__user__username',
        'customer__user__email',
        'address_line1',
        'city',
        'postal_code'
    ]
    list_editable = ['is_default']
    # ✅ CORRECTION : date_hierarchy commenté pour éviter l'erreur timezone MySQL
    # date_hierarchy = 'created_at'
    ordering = ['-created_at']
    
    fieldsets = (
        ('Client', {
            'fields': ('customer',)
        }),
        ('Contact', {
            'fields': ('full_name', 'phone')
        }),
        ('Adresse', {
            'fields': ('address_line1', 'address_line2', 'city', 'state', 'postal_code', 'country')
        }),
        ('Configuration', {
            'fields': ('address_type', 'is_default')
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    def get_queryset(self, request):
        """
        ✅ OPTIMISATION N+1 : Précharge le customer et son user
        """
        qs = super().get_queryset(request)
        return qs.select_related('customer__user')
    
    def address_type_display(self, obj):
        """Affiche le type d'adresse avec icône"""
        if obj.address_type == 'shipping':
            return format_html('📦 Livraison')
        else:
            return format_html('💳 Facturation')
    address_type_display.short_description = "Type"