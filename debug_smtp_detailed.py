"""
DIAGNOSTIC SMTP COMPLET - PROBLÈME D'AUTHENTIFICATION
Exécutez: python debug_smtp_detailed.py
"""

import os
import sys
import django
from pathlib import Path
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Configuration Django
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.conf import settings
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def debug_smtp_authentication():
    """Diagnostic complet de l'authentification SMTP"""
    print("=" * 70)
    print("🔍 DIAGNOSTIC SMTP COMPLET - AUTHENTIFICATION")
    print("=" * 70)
    
    # 1. Vérification des paramètres SMTP
    print("\n1. 🛠️ PARAMÈTRES SMTP CONFIGURÉS:")
    print(f"   📧 HOST: {settings.EMAIL_HOST}")
    print(f"   🔌 PORT: {settings.EMAIL_PORT}")
    print(f"   🔐 USE_TLS: {settings.EMAIL_USE_TLS}")
    print(f"   🔒 USE_SSL: {settings.EMAIL_USE_SSL}")
    print(f"   👤 USER: {settings.EMAIL_HOST_USER}")
    print(f"   📱 PASSWORD: {'*' * len(settings.EMAIL_HOST_PASSWORD) if settings.EMAIL_HOST_PASSWORD else 'NON DÉFINI'}")
    
    # 2. Test de connexion SMTP direct
    print("\n2. 🔗 TEST CONNEXION SMTP DIRECTE:")
    try:
        if settings.EMAIL_USE_SSL:
            server = smtplib.SMTP_SSL(settings.EMAIL_HOST, settings.EMAIL_PORT)
            print("   ✅ Connexion SSL établie")
        else:
            server = smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT)
            print("   ✅ Connexion TCP établie")
            
        # Afficher la bannière du serveur
        print(f"   📋 Bannière serveur: {server.ehlo()[1]}")
        
        # STARTTLS si nécessaire
        if settings.EMAIL_USE_TLS and not settings.EMAIL_USE_SSL:
            server.starttls()
            server.ehlo()
            print("   ✅ TLS démarré")
            
    except Exception as e:
        print(f"   ❌ Erreur connexion: {e}")
        return False
    
    # 3. Test d'authentification
    print("\n3. 🔑 TEST AUTHENTIFICATION:")
    try:
        server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
        print("   ✅ Authentification réussie")
    except smtplib.SMTPAuthenticationError as e:
        print(f"   ❌ ERREUR AUTHENTIFICATION: {e}")
        print("   💡 Causes possibles:")
        print("      - Mot de passe d'application incorrect")
        print("      - Vérification 2FA non activée")
        print("      - Accès aux apps moins sécurisées désactivé")
        print("      - Compte Gmail bloqué temporairement")
        return False
    except Exception as e:
        print(f"   ❌ Erreur authentification: {e}")
        return False
    
    # 4. Test d'envoi SMTP direct
    print("\n4. 📤 TEST ENVOI SMTP DIRECT:")
    try:
        # Créer le message
        msg = MIMEMultipart()
        msg['From'] = f"D&H-SHOP <{settings.EMAIL_HOST_USER}>"
        msg['To'] = "readdocuments64@gmail.com"
        msg['Subject'] = "Test SMTP Direct - D&H-SHOP"
        
        body = "Ceci est un test d'envoi SMTP direct depuis Python."
        msg.attach(MIMEText(body, 'plain'))
        
        # Envoyer
        server.send_message(msg)
        print("   ✅ Email envoyé avec succès via SMTP direct")
        
    except Exception as e:
        print(f"   ❌ Erreur envoi SMTP direct: {e}")
        return False
    finally:
        server.quit()
    
    return True

def debug_gmail_specific_issues():
    """Diagnostic des problèmes spécifiques à Gmail"""
    print("\n5. 🔍 DIAGNOSTIC SPÉCIFIQUE GMAIL:")
    
    print("   📋 Vérifications Gmail requises:")
    print("   1. ✅ Vérification 2 étapes ACTIVÉE")
    print("   2. ✅ Mot de passe d'application GÉNÉRÉ")
    print("   3. ✅ Accès aux apps moins sécurisées DÉSACTIVÉ")
    print("   4. ✅ Aucun blocage de sécurité sur le compte")
    
    print("\n   🔗 Liens importants:")
    print("   - Générer mot de passe app: https://myaccount.google.com/apppasswords")
    print("   - Vérification 2 étapes: https://myaccount.google.com/security")
    print("   - Activité du compte: https://myaccount.google.com/notifications")
    
    # Test avec différents ports
    print("\n6. 🔄 TEST PORTS ALTERNATIFS:")
    ports_to_test = [587, 465, 25]
    
    for port in ports_to_test:
        print(f"   🔧 Test port {port}:")
        try:
            if port == 465:
                server = smtplib.SMTP_SSL(settings.EMAIL_HOST, port, timeout=10)
            else:
                server = smtplib.SMTP(settings.EMAIL_HOST, port, timeout=10)
                if port == 587:
                    server.starttls()
            
            server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
            print(f"      ✅ Port {port} fonctionnel")
            server.quit()
        except Exception as e:
            print(f"      ❌ Port {port} échoué: {e}")

def debug_django_email_backend():
    """Test du backend email Django"""
    print("\n7. 🐍 TEST BACKEND DJANGO:")
    
    from django.core.mail import send_mail, get_connection
    
    try:
        # Test avec connexion explicite
        connection = get_connection()
        print(f"   📧 Backend: {connection.__class__.__name__}")
        
        # Test d'envoi simple
        result = send_mail(
            'Test Django SMTP - D&H-SHOP',
            'Ceci est un test du backend SMTP Django.',
            settings.DEFAULT_FROM_EMAIL,
            ['readdocuments64@gmail.com'],
            fail_silently=False,
        )
        print(f"   ✅ Résultat Django: {result} (1 = succès)")
        
    except Exception as e:
        print(f"   ❌ Erreur Django: {e}")
        import traceback
        traceback.print_exc()

def check_app_password_requirements():
    """Vérification des prérequis mot de passe d'application"""
    print("\n8. 🔐 VÉRIFICATION MOT DE PASSE APPLICATION:")
    
    print("   📋 PRÉREQUIS OBLIGATOIRES:")
    print("   1. Compte Google avec vérification 2 étapes ACTIVÉE")
    print("   2. Générer un mot de passe d'application pour 'Mail'")
    print("   3. Utiliser le mot de passe d'application, PAS le mot de passe principal")
    print("   4. Le mot de passe doit avoir 16 caractères sans espaces")
    
    print("\n   🚨 ERREURS COURANTES:")
    print("   - Utilisation du mot de passe Gmail principal ❌")
    print("   - Vérification 2 étapes désactivée ❌")
    print("   - Mot de passe d'application généré pour la mauvaise app ❌")
    print("   - Caractères mal copiés/collés ❌")

def test_simple_smtp():
    """Test SMTP le plus simple possible"""
    print("\n9. 🧪 TEST SMTP ULTRA-SIMPLE:")
    
    try:
        import smtplib
        from email.mime.text import MIMEText
        
        msg = MIMEText("Test ultra-simple SMTP")
        msg['Subject'] = 'Test SMTP Simple'
        msg['From'] = settings.EMAIL_HOST_USER
        msg['To'] = 'readdocuments64@gmail.com'
        
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
        server.sendmail(settings.EMAIL_HOST_USER, ['readdocuments64@gmail.com'], msg.as_string())
        server.quit()
        
        print("   ✅ Test SMTP simple réussi!")
        
    except Exception as e:
        print(f"   ❌ Test SMTP simple échoué: {e}")

if __name__ == "__main__":
    print("🚀 LANCEMENT DIAGNOSTIC SMTP COMPLET")
    print("=" * 70)
    
    # Lancer les diagnostics
    smtp_ok = debug_smtp_authentication()
    
    if not smtp_ok:
        debug_gmail_specific_issues()
        check_app_password_requirements()
        test_simple_smtp()
    
    debug_django_email_backend()
    
    print("\n" + "=" * 70)
    print("📋 RÉSUMÉ DU DIAGNOSTIC")
    print("=" * 70)
    
    if smtp_ok:
        print("✅ SMTP configuré correctement")
        print("💡 Le problème vient peut-être du code Django")
    else:
        print("❌ Problème d'authentification SMTP détecté")
        print("🔧 Solutions recommandées:")
        print("   1. Vérifiez la vérification 2 étapes Gmail")
        print("   2. Générez un NOUVEAU mot de passe d'application")
        print("   3. Copiez-collez exactement le mot de passe dans .env")
        print("   4. Testez avec le script simple ci-dessus")