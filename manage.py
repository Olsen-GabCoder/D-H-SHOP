#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    
    # ========================================
    # CONFIGURATION UTF-8 POUR WINDOWS
    # ========================================
    # Fix pour l'encodage des emojis et caractères spéciaux sur Windows
    if sys.platform == "win32":
        try:
            import io
            # Forcer l'encodage UTF-8 pour stdout et stderr
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
            
            # Définir la variable d'environnement pour Python
            os.environ['PYTHONIOENCODING'] = 'utf-8'
            
            # Pour les consoles Windows (optionnel mais recommandé)
            if hasattr(sys.stdout, 'reconfigure'):
                sys.stdout.reconfigure(encoding='utf-8')
            if hasattr(sys.stderr, 'reconfigure'):
                sys.stderr.reconfigure(encoding='utf-8')
                
        except Exception as e:
            # Si la configuration UTF-8 échoue, continuer sans (mode dégradé)
            print(f"Avertissement: Impossible de configurer UTF-8: {e}")
    
    # ========================================
    # CONFIGURATION DJANGO
    # ========================================
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()