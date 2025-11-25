from django.contrib import admin
from .models import SiteSettings


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    """
    Interface admin pour les paramètres globaux du site
    
    Organisation en fieldsets pour une meilleure UX :
    - Informations générales (nom, logo, slogan)
    - Contact (email, téléphone, WhatsApp)
    - Adresse physique
    - Horaires d'ouverture
    - Réseaux sociaux
    - SEO & Analytics
    - Messages personnalisables
    - Newsletter
    - Informations légales
    """
    
    # ========================================
    # ORGANISATION DES CHAMPS EN SECTIONS
    # ========================================
    
    fieldsets = (
        ('📌 Informations Générales', {
            'fields': ('site_name', 'site_tagline', 'site_description', 'logo', 'favicon'),
            'description': 'Identité visuelle et description du site'
        }),
        
        ('📞 Contact', {
            'fields': ('contact_email', 'contact_phone', 'contact_whatsapp'),
            'description': 'Coordonnées de contact affichées sur le site'
        }),
        
        ('📍 Adresse Physique', {
            'fields': ('address_line1', 'address_line2', 'city', 'postal_code', 'country'),
            'description': 'Adresse complète de l\'entreprise'
        }),
        
        ('🕐 Horaires d\'Ouverture', {
            'fields': ('business_hours',),
            'description': 'Horaires d\'ouverture (format libre, une ligne par jour)',
            'classes': ('collapse',)  # Section repliée par défaut
        }),
        
        ('🌐 Réseaux Sociaux', {
            'fields': ('facebook_url', 'instagram_url', 'twitter_url', 'linkedin_url', 'youtube_url', 'tiktok_url'),
            'description': 'Liens vers les profils sur les réseaux sociaux',
            'classes': ('collapse',)
        }),
        
        ('🔍 SEO & Analytics', {
            'fields': ('meta_title', 'meta_description', 'meta_keywords', 'google_analytics_id', 'facebook_pixel_id'),
            'description': 'Paramètres pour le référencement et le tracking',
            'classes': ('collapse',)
        }),
        
        ('💬 Messages Personnalisables', {
            'fields': ('welcome_message', 'maintenance_mode', 'maintenance_message'),
            'description': 'Messages affichés sur le site et mode maintenance',
            'classes': ('collapse',)
        }),
        
        ('📧 Newsletter', {
            'fields': ('newsletter_enabled', 'newsletter_description'),
            'description': 'Configuration de la newsletter',
            'classes': ('collapse',)
        }),
        
        ('🏢 Informations Légales', {
            'fields': ('company_legal_name', 'company_registration_number', 'vat_number'),
            'description': 'Informations légales et fiscales de l\'entreprise',
            'classes': ('collapse',)
        }),
    )
    
    # ========================================
    # CONFIGURATION DE L'AFFICHAGE
    # ========================================
    
    # Liste des champs affichés dans la liste
    list_display = ['site_name', 'contact_email', 'contact_phone', 'maintenance_mode', 'updated_at']
    
    # Champs en lecture seule
    readonly_fields = ['created_at', 'updated_at']
    
    # Filtres dans la barre latérale
    list_filter = ['maintenance_mode', 'newsletter_enabled']
    
    # ========================================
    # RESTRICTIONS SINGLETON
    # ========================================
    
    def has_add_permission(self, request):
        """
        Empêche la création de plusieurs instances (Singleton)
        Autorise uniquement si aucune instance n'existe
        """
        return not SiteSettings.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        """
        Empêche la suppression des paramètres du site
        """
        return False
    
    # ========================================
    # PERSONNALISATION DE L'INTERFACE
    # ========================================
    
    def changelist_view(self, request, extra_context=None):
        """
        Redirige automatiquement vers le formulaire d'édition
        s'il existe une instance (UX optimisée pour singleton)
        """
        if SiteSettings.objects.exists():
            obj = SiteSettings.objects.first()
            from django.shortcuts import redirect
            from django.urls import reverse
            return redirect(reverse('admin:core_sitesettings_change', args=[obj.pk]))
        
        return super().changelist_view(request, extra_context)
    
    # ========================================
    # MÉTADONNÉES DE L'ADMIN
    # ========================================
    
    class Media:
        css = {
            'all': ('admin/css/custom_admin.css',)  # Si vous avez du CSS custom
        }