"""
Template Tags pour les Paramètres du Site
==========================================

Permet d'accéder aux paramètres SiteSettings dans tous les templates
via le context processor (variable 'site' disponible globalement)

Usage dans les templates :
    {% load site_settings %}
    {{ site.site_name }}
    {{ site.contact_email }}
    {% render_social_links %}
"""

from django import template
from datetime import datetime

register = template.Library()


@register.inclusion_tag('components/social_links.html', takes_context=True)
def render_social_links(context):
    """
    Rendu des liens vers les réseaux sociaux configurés
    
    Utilise la variable 'site' déjà présente dans le contexte
    (fournie par le context processor)
    
    Usage dans les templates :
        {% load site_settings %}
        {% render_social_links %}
    
    Returns:
        Context avec la liste des réseaux sociaux actifs
    """
    # Récupération de 'site' depuis le contexte existant
    # (fourni par core.context_processors.site_settings)
    settings = context.get('site')
    
    if settings and hasattr(settings, 'get_social_media_links'):
        social_links = settings.get_social_media_links()
    else:
        social_links = {}
    
    return {'social_links': social_links}


@register.filter
def format_phone(phone_number):
    """
    Formate un numéro de téléphone pour l'affichage
    
    Usage :
        {{ site.contact_phone|format_phone }}
    
    Args:
        phone_number (str): Numéro brut
    
    Returns:
        str: Numéro formaté ou chaîne vide
    """
    if not phone_number:
        return ''
    
    # Retirer les espaces et caractères spéciaux
    clean = ''.join(filter(str.isdigit, str(phone_number)))
    
    # Exemple de formatage : +241 XX XX XX XX
    if len(clean) >= 9:
        return f"+{clean[:3]} {clean[3:5]} {clean[5:7]} {clean[7:9]} {clean[9:]}"
    
    return phone_number


@register.simple_tag
def site_year():
    """
    Retourne l'année en cours pour le copyright
    
    Usage :
        {% load site_settings %}
        © {% site_year %} Votre Société
    
    Returns:
        int: Année actuelle
    """
    return datetime.now().year