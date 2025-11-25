"""
Signaux pour l'application Core
================================

Gère l'invalidation automatique du cache des paramètres du site
lorsqu'ils sont modifiés dans l'interface d'administration.
"""

import logging
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache

logger = logging.getLogger(__name__)

# Clé de cache constante partagée entre tous les composants
SITE_SETTINGS_CACHE_KEY = 'site_settings'


@receiver(post_save, sender='core.SiteSettings')
def invalidate_site_settings_cache_on_save(sender, instance, **kwargs):
    """
    Invalide le cache des paramètres du site après une sauvegarde.
    
    Args:
        sender: Le modèle SiteSettings
        instance: L'instance sauvegardée
        **kwargs: Arguments supplémentaires du signal
    """
    try:
        cache.delete(SITE_SETTINGS_CACHE_KEY)
        logger.info(
            f"✅ Cache invalidé après sauvegarde de SiteSettings (ID: {instance.pk})"
        )
    except Exception as e:
        logger.error(
            f"❌ Erreur lors de l'invalidation du cache (sauvegarde): {e}"
        )


@receiver(post_delete, sender='core.SiteSettings')
def invalidate_site_settings_cache_on_delete(sender, instance, **kwargs):
    """
    Invalide le cache des paramètres du site après une suppression.
    
    Args:
        sender: Le modèle SiteSettings
        instance: L'instance supprimée
        **kwargs: Arguments supplémentaires du signal
    """
    try:
        cache.delete(SITE_SETTINGS_CACHE_KEY)
        logger.info(
            f"✅ Cache invalidé après suppression de SiteSettings (ID: {instance.pk})"
        )
    except Exception as e:
        logger.error(
            f"❌ Erreur lors de l'invalidation du cache (suppression): {e}"
        )