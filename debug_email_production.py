"""
DIAGNOSTIC AVANCÉ SYSTÈME EMAIL - PRODUCTION
Exécutez: python debug_email_production.py
"""

import os
import sys
import django
from pathlib import Path

# Configuration Django
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.core.mail import send_mail, EmailMessage
from django.conf import settings
from django.template.loader import render_to_string
from orders.models import Order
from core.email_service import EmailService

def debug_production_flow():
    """Test du flux complet de production"""
    print("=" * 60)
    print("🔍 DIAGNOSTIC FLUX PRODUCTION")
    print("=" * 60)
    
    # 1. Vérification de la configuration effective
    print("\n1. CONFIGURATION EFFECTIVE:")
    print(f"   EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
    print(f"   DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")
    print(f"   DEFAULT_FROM_NAME: {getattr(settings, 'DEFAULT_FROM_NAME', 'NON DÉFINI')}")
    print(f"   EMAIL_HOST: {settings.EMAIL_HOST}")
    print(f"   EMAIL_PORT: {settings.EMAIL_PORT}")
    
    # 2. Test d'envoi direct Django
    print("\n2. TEST ENVOI DIRECT DJANGO:")
    try:
        send_mail(
            'Test Django Direct - D&H-SHOP',
            'Ceci est un test direct de Django.',
            settings.DEFAULT_FROM_EMAIL,
            ['olsenkampala@gmail.com'],
            fail_silently=False,
        )
        print("   ✅ Email Django envoyé avec succès")
    except Exception as e:
        print(f"   ❌ Erreur Django: {e}")
    
    # 3. Test avec EmailMessage
    print("\n3. TEST EMAILMESSAGE:")
    try:
        email = EmailMessage(
            'Test EmailMessage - D&H-SHOP',
            'Ceci est un test EmailMessage.',
            settings.DEFAULT_FROM_EMAIL,
            ['olsenkampala@gmail.com'],
        )
        email.send(fail_silently=False)
        print("   ✅ EmailMessage envoyé avec succès")
    except Exception as e:
        print(f"   ❌ Erreur EmailMessage: {e}")
    
    # 4. Test du service personnalisé
    print("\n4. TEST SERVICE PERSONNALISÉ:")
    try:
        # Récupérer une commande réelle
        last_order = Order.objects.last()
        if last_order:
            print(f"   📦 Commande test: {last_order.order_number}")
            result = EmailService.send_order_confirmation(last_order)
            print(f"   🔧 Résultat service: {result}")
        else:
            print("   ⚠️ Aucune commande trouvée")
    except Exception as e:
        print(f"   ❌ Erreur service: {e}")
        import traceback
        traceback.print_exc()
    
    # 5. Vérification du template dans le contexte réel
    print("\n5. VÉRIFICATION TEMPLATE RÉEL:")
    try:
        last_order = Order.objects.last()
        if last_order:
            context = {
                'order': last_order,
                'customer': last_order.customer,
                'items': last_order.items.all(),
                'shipping_address': last_order.shipping_address,
            }
            # Ajouter contexte boutique
            from core.email_service import EmailService
            context.update(EmailService._get_shop_context())
            
            content = render_to_string('emails/order_confirmation.html', context)
            print(f"   ✅ Template rendu: {len(content)} caractères")
        else:
            print("   ⚠️ Impossible de tester sans commande")
    except Exception as e:
        print(f"   ❌ Erreur template: {e}")

if __name__ == "__main__":
    debug_production_flow()