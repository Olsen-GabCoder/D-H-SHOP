"""
SCRIPT DE DIAGNOSTIC EMAIL COMPLET - CORRIGÉ POUR CONFIG
Exécutez: python debug_email.py
"""

import os
import sys
import django
from pathlib import Path

# Configuration Django CORRECTE
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')  # CORRIGÉ : config.settings au lieu de mon_ecommerce.settings
django.setup()

from django.template.loader import render_to_string, get_template
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from orders.models import Order
from core.email_service import EmailService

def debug_template_system():
    """Diagnostic du système de templates"""
    print("=" * 60)
    print("DIAGNOSTIC SYSTÈME TEMPLATES")
    print("=" * 60)
    
    # 1. Vérification des paramètres TEMPLATES
    print("\n1. CONFIGURATION TEMPLATES:")
    for i, template_config in enumerate(settings.TEMPLATES):
        print(f"   Configuration {i+1}:")
        print(f"   - BACKEND: {template_config['BACKEND']}")
        print(f"   - DIRS: {template_config.get('DIRS', [])}")
        print(f"   - APP_DIRS: {template_config.get('APP_DIRS', False)}")
    
    # 2. Vérification des dossiers templates
    print("\n2. RECHERCHE DES TEMPLATES:")
    template_dirs = []
    for config in settings.TEMPLATES:
        template_dirs.extend(config.get('DIRS', []))
    
    for template_dir in template_dirs:
        template_dir_path = Path(template_dir)
        print(f"   📁 Dossier template: {template_dir_path}")
        emails_path = template_dir_path / 'emails'
        if emails_path.exists():
            print(f"   ✅ Dossier emails trouvé: {emails_path}")
            order_confirmation_path = emails_path / 'order_confirmation.html'
            if order_confirmation_path.exists():
                print(f"   ✅ Fichier order_confirmation.html trouvé: {order_confirmation_path}")
                print(f"   📏 Taille du fichier: {order_confirmation_path.stat().st_size} octets")
            else:
                print(f"   ❌ Fichier order_confirmation.html INTROUVABLE dans: {emails_path}")
                # Lister les fichiers existants
                existing_files = list(emails_path.glob('*.html'))
                if existing_files:
                    print(f"   📄 Fichiers existants dans emails/:")
                    for f in existing_files:
                        print(f"      - {f.name}")
                else:
                    print(f"   📁 Dossier emails vide")
        else:
            print(f"   ❌ Dossier emails INTROUVABLE dans: {template_dir_path}")

def debug_template_loading():
    """Test du chargement du template"""
    print("\n3. TEST CHARGEMENT TEMPLATE:")
    
    template_paths_to_test = [
        'emails/order_confirmation.html',
        'emails/order_confirmation',
        'orders/emails/order_confirmation.html'
    ]
    
    for template_path in template_paths_to_test:
        print(f"\n   Test de: '{template_path}'")
        try:
            template = get_template(template_path)
            print(f"   ✅ Template chargé avec succès")
            print(f"   📍 Chemin réel: {template.origin.name}")
            break  # Arrêter au premier succès
        except Exception as e:
            print(f"   ❌ Erreur: {e}")
    
    # Test avec render_to_string
    print(f"\n   Test render_to_string:")
    try:
        context = {
            'order': type('MockOrder', (), {'order_number': 'TEST-123'})(),
            'customer': type('MockCustomer', (), {'user': type('MockUser', (), {'get_full_name': lambda: 'Test User', 'username': 'testuser'})()})(),
            'items': [],
            'shipping_address': type('MockAddress', (), {'full_name': 'Test User', 'address_line1': 'Test', 'city': 'Test', 'phone': '00000000'})(),
            'shop_name': 'Test Shop',
            'shop_email': 'test@example.com',
            'shop_phone': '00000000',
            'shop_address': 'Test Address',
            'shop_website': 'http://test.com'
        }
        html_content = render_to_string('emails/order_confirmation.html', context)
        print(f"   ✅ render_to_string() réussi")
        print(f"   📏 Taille du contenu: {len(html_content)} caractères")
    except Exception as e:
        print(f"   ❌ Erreur render_to_string(): {e}")
        import traceback
        traceback.print_exc()

def debug_email_service():
    """Test du service email avec une commande réelle"""
    print("\n4. TEST SERVICE EMAIL:")
    
    # Récupérer la dernière commande pour tester
    try:
        last_order = Order.objects.last()
        if last_order:
            print(f"   📦 Commande de test: {last_order.order_number}")
            print(f"   👤 Client: {last_order.customer.user.email}")
            
            # Test d'envoi d'email
            try:
                print("   📧 Tentative d'envoi d'email...")
                result = EmailService.send_order_confirmation(last_order)
                print(f"   ✅ Résultat envoi email: {result}")
            except Exception as e:
                print(f"   ❌ Erreur lors de l'envoi: {e}")
                import traceback
                traceback.print_exc()
        else:
            print("   ⚠️ Aucune commande trouvée dans la base de données")
    except Exception as e:
        print(f"   ❌ Erreur accès base de données: {e}")

def debug_template_paths():
    """Scan complet de tous les dossiers templates"""
    print("\n5. SCAN COMPLET DES TEMPLATES:")
    
    # Scan de tous les dossiers d'applications
    for app in settings.INSTALLED_APPS:
        try:
            if '.' in app:
                continue  # Ignorer les modules imbriqués
            
            app_module = __import__(app)
            app_path = Path(app_module.__file__).parent
            templates_path = app_path / 'templates'
            
            if templates_path.exists():
                print(f"   📁 {app}: {templates_path}")
                emails_path = templates_path / 'emails'
                if emails_path.exists():
                    print(f"     📧 emails/ trouvé")
                    for file in emails_path.glob('*.html'):
                        print(f"       📄 {file.name}")
        except Exception as e:
            print(f"   ⚠️ Erreur scan {app}: {e}")

def debug_settings():
    """Vérification des paramètres email"""
    print("\n6. CONFIGURATION EMAIL:")
    email_settings = [
        'EMAIL_BACKEND',
        'EMAIL_HOST', 
        'EMAIL_PORT',
        'EMAIL_USE_TLS',
        'EMAIL_HOST_USER',
        'DEFAULT_FROM_EMAIL',
        'SHOP_NAME',
        'SHOP_EMAIL',
        'SHOP_PHONE'
    ]
    
    for setting in email_settings:
        value = getattr(settings, setting, 'NON DÉFINI')
        print(f"   {setting}: {value}")

def create_test_template():
    """Création d'un template de test si nécessaire"""
    print("\n7. CRÉATION TEMPLATE DE TEST:")
    
    # Chemin par défaut pour les templates
    default_template_dir = BASE_DIR / 'templates'
    test_template_path = default_template_dir / 'emails' / 'order_confirmation.html'
    
    if not test_template_path.exists():
        print(f"   Création du template manquant: {test_template_path}")
        test_template_path.parent.mkdir(parents=True, exist_ok=True)
        
        template_content = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Test Email</title>
</head>
<body>
    <h1>Test Réussi!</h1>
    <p>Commande: {{ order.order_number }}</p>
    <p>Client: {{ customer.user.get_full_name|default:customer.user.username }}</p>
    <p>Email: {{ order.customer_email }}</p>
</body>
</html>"""
        
        with open(test_template_path, 'w', encoding='utf-8') as f:
            f.write(template_content)
        print("   ✅ Template de test créé")
    else:
        print(f"   ✅ Template existe déjà: {test_template_path}")

def check_template_directories():
    """Vérification détaillée des dossiers templates"""
    print("\n8. VÉRIFICATION DÉTAILLÉE DES DOSSIERS:")
    
    # Vérifier le dossier templates principal
    templates_dir = BASE_DIR / 'templates'
    print(f"   Dossier templates principal: {templates_dir}")
    print(f"   Existe: {templates_dir.exists()}")
    
    if templates_dir.exists():
        emails_dir = templates_dir / 'emails'
        print(f"   Dossier emails: {emails_dir}")
        print(f"   Existe: {emails_dir.exists()}")
        
        if emails_dir.exists():
            files = list(emails_dir.glob('*.html'))
            print(f"   Fichiers HTML trouvés: {len(files)}")
            for file in files:
                print(f"     - {file.name}")

if __name__ == "__main__":
    print("🚀 DIAGNOSTIC COMPLET DU SYSTÈME EMAIL - CONFIG")
    print("=" * 60)
    
    debug_template_system()
    debug_template_loading()
    debug_template_paths()
    debug_settings()
    check_template_directories()
    create_test_template()
    debug_email_service()
    
    print("\n" + "=" * 60)
    print("📋 RÉSUMÉ DU DIAGNOSTIC")
    print("=" * 60)
    print("Si vous voyez des ❌, corrigez les problèmes indiqués.")
    print("Si tout est ✅, le système email devrait fonctionner.")