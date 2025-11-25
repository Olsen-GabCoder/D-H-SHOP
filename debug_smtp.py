"""
DIAGNOSTIC SMTP COMPLET
Exécutez: python debug_smtp.py
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
import smtplib
import logging

# Configurer le logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def test_smtp_connection():
    """Test de connexion SMTP directe"""
    print("=" * 60)
    print("🔍 DIAGNOSTIC SMTP COMPLET")
    print("=" * 60)
    
    print(f"📧 Backend: {settings.EMAIL_BACKEND}")
    print(f"📨 From: {settings.DEFAULT_FROM_EMAIL}")
    print(f"🔧 Host: {settings.EMAIL_HOST}:{settings.EMAIL_PORT}")
    print(f"🔐 TLS: {settings.EMAIL_USE_TLS}, SSL: {settings.EMAIL_USE_SSL}")
    print(f"👤 User: {settings.EMAIL_HOST_USER}")
    print(f"📱 Password: {'*' * len(settings.EMAIL_HOST_PASSWORD) if settings.EMAIL_HOST_PASSWORD else 'NON DÉFINI'}")
    
    # Test de connexion SMTP directe
    print("\n1. 🔗 TEST CONNEXION SMTP DIRECTE")
    try:
        server = smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT)
        server.ehlo()
        if settings.EMAIL_USE_TLS:
            server.starttls()
            server.ehlo()
        print("   ✅ Connexion SMTP établie")
        
        # Tentative de login
        print("2. 🔑 AUTHENTIFICATION SMTP")
        server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
        print("   ✅ Authentification SMTP réussie")
        
        server.quit()
        return True
        
    except Exception as e:
        print(f"   ❌ Erreur SMTP: {e}")
        return False

def test_django_email():
    """Test d'envoi d'email via Django"""
    print("\n3. 📨 TEST EMAIL DJANGO")
    try:
        result = send_mail(
            'Test SMTP Django - D&H-SHOP',
            'Ceci est un test SMTP via Django.',
            settings.DEFAULT_FROM_EMAIL,
            ['readdocuments64@gmail.com'],
            fail_silently=False,
        )
        print(f"   ✅ Résultat Django: {result} (1 = succès, 0 = échec)")
        return result == 1
    except Exception as e:
        print(f"   ❌ Erreur Django: {e}")
        return False

def test_email_message():
    """Test avec EmailMessage"""
    print("\n4. 📧 TEST EMAILMESSAGE")
    try:
        email = EmailMessage(
            'Test EmailMessage SMTP - D&H-SHOP',
            'Ceci est un test EmailMessage avec SMTP.',
            settings.DEFAULT_FROM_EMAIL,
            ['readdocuments64@gmail.com'],
        )
        result = email.send(fail_silently=False)
        print(f"   ✅ Résultat EmailMessage: {result} (1 = succès, 0 = échec)")
        return result == 1
    except Exception as e:
        print(f"   ❌ Erreur EmailMessage: {e}")
        return False

def check_gmail_app_password():
    """Vérification du mot de passe d'application Gmail"""
    print("\n5. 🔐 VÉRIFICATION MOT DE PASSE APPLICATION GMAIL")
    print("   📋 Conditions pour le mot de passe d'application Gmail:")
    print("   ✅ La vérification en 2 étapes doit être activée")
    print("   ✅ Le mot de passe d'application doit être généré pour 'Mail'")
    print("   ✅ Le mot de passe doit être correctement copié dans .env")
    print("   🔗 Pour générer: https://myaccount.google.com/apppasswords")

if __name__ == "__main__":
    # Tests
    smtp_ok = test_smtp_connection()
    django_ok = test_django_email() if smtp_ok else False
    emailmessage_ok = test_email_message() if smtp_ok else False
    
    # Recommendations
    print("\n" + "=" * 60)
    print("📋 RÉSUMÉ DU DIAGNOSTIC")
    print("=" * 60)
    
    if smtp_ok and django_ok and emailmessage_ok:
        print("✅ Tous les tests SMTP sont réussis!")
        print("📩 Les emails devraient maintenant être envoyés correctement.")
    else:
        print("❌ Des problèmes SMTP ont été détectés.")
        check_gmail_app_password()
        print("\n💡 Solutions possibles:")
        print("   🔄 Régénérez le mot de passe d'application Gmail")
        print("   📧 Vérifiez que l'email host user est correct")
        print("   🔒 Assurez-vous que la vérification 2FA est activée")
        print("   🌐 Vérifiez votre connexion Internet")