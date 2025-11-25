"""
Test final après activation SMTP
Exécutez: python test_email_smtp.py
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

# Configuration du logging en premier
from core.logging_config import setup_logging
setup_logging()

from django.core.mail import send_mail
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def test_smtp_email():
    """Test d'envoi SMTP réel"""
    print("=" * 60)
    print("🚀 TEST SMTP RÉEL")
    print("=" * 60)
    
    print(f"📧 Backend: {settings.EMAIL_BACKEND}")
    print(f"📨 From: {settings.DEFAULT_FROM_EMAIL}")
    print(f"🔧 Host: {settings.EMAIL_HOST}:{settings.EMAIL_PORT}")
    
    try:
        print("🔄 Envoi en cours...")
        result = send_mail(
            'Test SMTP Réel - D&H-SHOP',
            'Félicitations ! Votre configuration SMTP fonctionne correctement.',
            settings.DEFAULT_FROM_EMAIL,
            ['olsenkampala@gmail.com'],
            fail_silently=False,
        )
        print(f"✅ Résultat: {result} (1 = succès)")
        print("📩 Vérifiez votre boîte mail (y compris les spams)")
        
    except Exception as e:
        print(f"❌ Erreur SMTP: {e}")
        print("💡 Vérifiez:")
        print("   - Le mot de passe d'application Gmail")
        print("   - Que la vérification 2FA est activée")
        print("   - Les paramètres SMTP dans .env")

if __name__ == "__main__":
    test_smtp_email()