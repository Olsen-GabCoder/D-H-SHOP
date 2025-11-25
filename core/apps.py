"""
Configuration de l'application Core
====================================

Gère le chargement des signaux au démarrage de l'application.
"""

from django.apps import AppConfig


class CoreConfig(AppConfig):
    """Configuration de l'application Core."""
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'
    verbose_name = 'Configuration du site'
    
    def ready(self):
        """
        Méthode appelée au démarrage de Django.
        Charge les signaux pour l'invalidation du cache.
        """
        try:
            # Import des signaux pour activer les receivers
            import core.signals
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"❌ Erreur lors du chargement des signaux Core: {e}")