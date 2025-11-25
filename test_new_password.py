"""
Test rapide du nouveau mot de passe SMTP
Exécutez après avoir mis à jour EMAIL_HOST_PASSWORD dans .env
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
import smtplib

def test_new_password():
    print("=" * 60)
    print("🔐 TEST NOUVEAU MOT DE PASSE SMTP")
    print("=" * 60)
    
    print(f"📧 Utilisateur: {settings.EMAIL_HOST_USER}")
    print(f"🔑 Mot de passe: {'*' * len(settings.EMAIL_HOST_PASSWORD)}")
    
    # Test SMTP direct
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
        print("✅ AUTHENTIFICATION RÉUSSIE !")
        server.quit()
        
        # Test envoi email
        send_mail(
            'Test Nouveau Mot de Passe - D&H-SHOP',
            'Félicitations ! Votre configuration SMTP fonctionne maintenant.',
            settings.DEFAULT_FROM_EMAIL,
            ['readdocuments64@gmail.com'],
            fail_silently=False,
        )
        print("✅ EMAIL ENVOYÉ AVEC SUCCÈS !")
        print("📩 Vérifiez votre boîte mail")
        
    except smtplib.SMTPAuthenticationError:
        print("❌ ERREUR AUTHENTIFICATION")
        print("💡 Le mot de passe est toujours incorrect")
        print("🔧 Vérifiez que:")
        print("   - La vérification 2 étapes est ACTIVÉE")
        print("   - Vous avez généré un mot de passe pour 'Mail'")
        print("   - Vous avez copié les 16 caractères SANS ESPACES")
        print("   - Vous avez redémarré le serveur après modification du .env")
    except Exception as e:
        print(f"❌ Autre erreur: {e}")

if __name__ == "__main__":
    test_new_password()