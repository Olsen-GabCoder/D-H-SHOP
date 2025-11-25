"""
Context Processors pour l'application Core
===========================================

Rend les paramètres du site disponibles dans tous les templates
via la variable {{ site }}
"""

from django.core.cache import cache
from core.models import SiteSettings
from core.signals import SITE_SETTINGS_CACHE_KEY  # Import de la clé constante


def site_settings(request):
    """
    Rend les paramètres du site disponibles dans tous les templates
    via la variable {{ site }}
    
    Args:
        request: HttpRequest object
    
    Returns:
        dict: Dictionnaire contenant les paramètres du site
        
    Usage dans les templates:
        {{ site.site_name }}
        {{ site.contact_email }}
        {{ site.logo_url }}
    """
    # Tentative de récupération depuis le cache (10 minutes)
    # Utilisation de la clé constante partagée
    settings = cache.get(SITE_SETTINGS_CACHE_KEY)
    
    if settings is None:
        try:
            settings = SiteSettings.get_settings()
            # Mise en cache pour 10 minutes (600 secondes)
            if settings:
                cache.set(SITE_SETTINGS_CACHE_KEY, settings, 600)
        except Exception as e:
            # Log de l'erreur pour debugging
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Impossible de récupérer SiteSettings: {e}")
            
            # Fallback : objet vide avec attributs par défaut
            settings = type('obj', (object,), {
                'site_name': 'D&H-SHOP',
                'site_tagline': 'Gabon',
                'site_description': '',
                'contact_email': 'contact@dh-shop.com',
                'contact_phone': '+241 01 23 45 67',
                'contact_whatsapp': '',
                'address': 'Libreville',
                'city': 'Libreville',
                'country': 'Gabon',
                'business_hours': '',
                'facebook_url': '',
                'instagram_url': '',
                'twitter_url': '',
                'linkedin_url': '',
                'youtube_url': '',
                'tiktok_url': '',
                'logo_url': '/static/images/logo-default.jpeg',
                'favicon_url': '/static/images/favicon-default.ico',
                'meta_title': 'D&H-SHOP',
                'meta_description': '',
                'meta_keywords': '',
                'google_analytics_id': '',
                'facebook_pixel_id': '',
                'welcome_message': '',
                'maintenance_mode': False,
                'maintenance_message': '',
                'newsletter_enabled': True,
                'newsletter_description': 'Recevez nos offres exclusives',
                'legal_company_name': '',
                'legal_rccm': '',
                'legal_tax_id': '',
                'has_social_media': lambda: False,
                'get_social_media_links': lambda: {},
                'get_full_address': lambda: 'Libreville, Gabon',
                'get_business_hours_list': lambda: [],
            })()
    
    return {
        'site': settings
    }