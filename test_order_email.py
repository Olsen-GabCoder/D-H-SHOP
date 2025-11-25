"""
Test d'envoi d'email de confirmation de commande avec le template réel
Exécutez après avoir vérifié que le template emails/order_confirmation.html existe
"""

import os
import sys
from pathlib import Path

# Configuration Django
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from orders.models import Order
from core.email_service import EmailService

def test_order_email():
    print("=" * 60)
    print("📦 TEST EMAIL DE COMMANDE RÉEL")
    print("=" * 60)
    
    # Récupérer la dernière commande
    last_order = Order.objects.last()
    if not last_order:
        print("❌ Aucune commande trouvée dans la base de données")
        print("💡 Créez d'abord une commande test")
        return
    
    print(f"📦 Commande: {last_order.order_number}")
    print(f"👤 Client: {last_order.customer.user.email}")
    
    # Test du template
    try:
        context = {
            'order': last_order,
            'customer': last_order.customer,
            'items': last_order.items.all(),
            'shipping_address': last_order.shipping_address,
        }
        html_content = render_to_string('emails/order_confirmation.html', context)
        print(f"✅ Template chargé: {len(html_content)} caractères")
    except Exception as e:
        print(f"❌ Erreur template: {e}")
        return
    
    # Test d'envoi via EmailService
    try:
        result = EmailService.send_order_confirmation(last_order)
        if result:
            print("✅ Email de commande envoyé avec succès !")
            print("📩 Vérifiez la boîte mail du client")
        else:
            print("❌ Échec de l'envoi de l'email de commande")
    except Exception as e:
        print(f"❌ Erreur lors de l'envoi: {e}")

if __name__ == "__main__":
    test_order_email()