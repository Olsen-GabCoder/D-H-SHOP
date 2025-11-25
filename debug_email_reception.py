"""
DIAGNOSTIC COMPLET SYSTÈME EMAIL - PROBLÈME DE RÉCEPTION
Exécutez: python debug_email_reception.py
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

from django.core.mail import EmailMessage, send_mail
from django.conf import settings
from django.template.loader import render_to_string
from orders.models import Order
from core.email_service import EmailService
import logging

# Configuration logging détaillé
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def debug_email_reception():
    """Diagnostic complet de la réception des emails"""
    print("=" * 70)
    print("🔍 DIAGNOSTIC COMPLET - PROBLÈME RÉCEPTION EMAIL")
    print("=" * 70)
    
    # 1. Vérification de la configuration effective
    print("\n1. 🛠️ CONFIGURATION EFFECTIVE:")
    print(f"   📧 EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
    print(f"   📨 DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")
    print(f"   🏷️ DEFAULT_FROM_NAME: {getattr(settings, 'DEFAULT_FROM_NAME', 'NON DÉFINI')}")
    print(f"   🔧 EMAIL_HOST: {settings.EMAIL_HOST}")
    print(f"   🔌 EMAIL_PORT: {settings.EMAIL_PORT}")
    print(f"   🔐 EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}")
    print(f"   👤 EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
    print(f"   📱 EMAIL_HOST_PASSWORD: {'*' * len(settings.EMAIL_HOST_PASSWORD) if settings.EMAIL_HOST_PASSWORD else 'NON DÉFINI'}")
    
    # 2. Test d'envoi direct SIMPLE
    print("\n2. 📤 TEST ENVOI DIRECT SIMPLE:")
    try:
        print("   🔄 Envoi en cours...")
        result = send_mail(
            'Test Simple - D&H-SHOP',
            'Ceci est un test simple de réception email.',
            settings.DEFAULT_FROM_EMAIL,
            ['olsenkampala@gmail.com'],
            fail_silently=False,
        )
        print(f"   ✅ Résultat Django send_mail: {result} (1 = succès, 0 = échec)")
    except Exception as e:
        print(f"   ❌ ERREUR send_mail: {e}")
        import traceback
        traceback.print_exc()
    
    # 3. Test avec EmailMessage COMPLET
    print("\n3. 📨 TEST EMAILMESSAGE COMPLET:")
    try:
        email = EmailMessage(
            'Test EmailMessage Complet - D&H-SHOP',
            'Ceci est un test EmailMessage avec contenu HTML.',
            settings.DEFAULT_FROM_EMAIL,
            ['olsenkampala@gmail.com'],
            reply_to=[settings.SHOP_EMAIL],
        )
        email.content_subtype = "html"
        email.body = """
        <!DOCTYPE html>
        <html>
        <body>
            <h1>Test de réception</h1>
            <p>Ceci est un test <strong>HTML</strong> complet.</p>
            <p>Si vous recevez cet email, le problème vient du template.</p>
        </body>
        </html>
        """
        result = email.send(fail_silently=False)
        print(f"   ✅ Résultat EmailMessage: {result} (1 = succès, 0 = échec)")
    except Exception as e:
        print(f"   ❌ ERREUR EmailMessage: {e}")
        import traceback
        traceback.print_exc()
    
    # 4. Test du service personnalisé avec une commande RÉELLE
    print("\n4. 🛒 TEST SERVICE PERSONNALISÉ (Commande réelle):")
    try:
        last_order = Order.objects.select_related(
            'customer', 'shipping_address'
        ).prefetch_related('items').last()
        
        if last_order:
            print(f"   📦 Commande trouvée: {last_order.order_number}")
            print(f"   👤 Client: {last_order.customer.user.email}")
            print(f"   📧 Email destination: {last_order.customer_email}")
            
            # Vérification du template
            print("\n   🔍 VÉRIFICATION TEMPLATE:")
            try:
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
                
                # Vérifier le contenu généré
                if "Confirmation de commande" in content:
                    print("   ✅ Contenu template semble correct")
                else:
                    print("   ⚠️ Contenu template anormal")
                    
            except Exception as template_error:
                print(f"   ❌ ERREUR Template: {template_error}")
            
            # Test d'envoi réel
            print("\n   🚀 TEST ENVOI RÉEL:")
            result = EmailService.send_order_confirmation(last_order)
            print(f"   📊 Résultat service: {result}")
            
        else:
            print("   ⚠️ Aucune commande trouvée dans la base")
            print("   💡 Créez une commande test d'abord")
            
    except Exception as e:
        print(f"   ❌ ERREUR service personnalisé: {e}")
        import traceback
        traceback.print_exc()
    
    # 5. Vérification du backend CONSOLE
    print("\n5. 🖥️ VÉRIFICATION BACKEND CONSOLE:")
    print("   📋 Les emails DEVRAIENT apparaître CI-DESSOUS dans la console Django")
    print("   🔍 Vérifiez la console où tourne 'python manage.py runserver'")
    print("   📝 Cherchez des lignes contenant 'Content-Type: text/plain' ou le sujet des emails")
    
    # 6. Test de configuration SMTP (si configuré)
    if settings.EMAIL_BACKEND != 'django.core.mail.backends.console.EmailBackend':
        print("\n6. 🔗 TEST CONFIGURATION SMTP:")
        try:
            import smtplib
            print(f"   🔄 Connexion à {settings.EMAIL_HOST}:{settings.EMAIL_PORT}")
            server = smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT)
            server.starttls() if settings.EMAIL_USE_TLS else None
            server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
            print("   ✅ Connexion SMTP réussie")
            server.quit()
        except Exception as e:
            print(f"   ❌ ERREUR SMTP: {e}")
    else:
        print("\n6. 🔗 TEST SMTP: (ignoré - mode console activé)")
    
    # 7. Vérification des logs email
    print("\n7. 📋 VÉRIFICATION LOGS EMAIL:")
    email_log_file = BASE_DIR / 'logs' / 'email.log'
    if email_log_file.exists():
        print(f"   📁 Fichier log trouvé: {email_log_file}")
        try:
            with open(email_log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()[-10:]  # 10 dernières lignes
            if lines:
                print("   📝 Dernières entrées log:")
                for line in lines:
                    print(f"      {line.strip()}")
            else:
                print("   ⚠️ Fichier log vide")
        except Exception as e:
            print(f"   ❌ Erreur lecture log: {e}")
    else:
        print("   ⚠️ Fichier log email introuvable")
    
    # 8. Recommandations
    print("\n8. 💡 RECOMMANDATIONS:")
    print("   ✅ Vérifiez la console Django (où runserver tourne)")
    print("   ✅ Les emails DOIVENT s'afficher dans cette console")
    print("   ✅ Si pas dans la console -> problème d'envoi")
    print("   ✅ Si dans la console mais pas en boîte -> problème backend")
    print("   🔄 Changez EMAIL_BACKEND pour SMTP en production")

def create_test_order():
    """Crée une commande test si nécessaire"""
    print("\n" + "=" * 70)
    print("🛠️ CRÉATION COMMANDE TEST (si nécessaire)")
    print("=" * 70)
    
    from orders.models import Order, OrderItem
    from accounts.models import Customer, Address
    from shop.models import Product, ProductVariant
    from django.contrib.auth.models import User
    from django.utils import timezone
    
    try:
        # Vérifier si une commande existe déjà
        if Order.objects.exists():
            print("✅ Des commandes existent déjà")
            return
        
        print("🔄 Création d'une commande test...")
        
        # Récupérer ou créer l'utilisateur
        user, created = User.objects.get_or_create(
            username='test_user',
            defaults={
                'email': 'olsenkampala@gmail.com',
                'first_name': 'Test',
                'last_name': 'User'
            }
        )
        if created:
            user.set_password('testpass123')
            user.save()
            print("👤 Utilisateur test créé")
        
        # Récupérer ou créer le customer
        customer, created = Customer.objects.get_or_create(user=user)
        if created:
            print("👤 Customer test créé")
        
        # Créer une adresse
        address, created = Address.objects.get_or_create(
            customer=customer,
            defaults={
                'full_name': 'Test User',
                'address_line1': '123 Test Street',
                'city': 'Libreville',
                'phone': '+228 12 34 56 78',
                'is_default': True
            }
        )
        if created:
            print("🏠 Adresse test créée")
        
        # Récupérer un produit existant ou en créer un
        product = Product.objects.first()
        if not product:
            print("⚠️ Aucun produit trouvé - création d'un produit test")
            # Créer un produit test minimal
            from shop.models import Category
            category = Category.objects.first()
            if not category:
                category = Category.objects.create(name='Test Category', slug='test-category')
            
            product = Product.objects.create(
                name='Produit Test',
                slug='produit-test',
                description='Description test',
                price=10000,
                category=category,
                is_active=True
            )
            print("📦 Produit test créé")
        
        # Créer une variante
        variant = ProductVariant.objects.filter(product=product).first()
        if not variant:
            variant = ProductVariant.objects.create(
                product=product,
                sku='TEST001',
                price=10000,
                is_active=True
            )
            print("📦 Variante test créée")
        
        # Créer la commande
        order = Order.objects.create(
            order_number='TEST-ORDER-001',
            customer=customer,
            shipping_address=address,
            billing_address=address,
            customer_email=user.email,
            customer_phone='+228 12 34 56 78',
            subtotal=10000,
            shipping_cost=2000,
            total=12000,
            status='pending'
        )
        print(f"📦 Commande test créée: {order.order_number}")
        
        # Créer un item de commande
        OrderItem.objects.create(
            order=order,
            product=product,
            variant=variant,
            product_name=product.name,
            unit_price=10000,
            quantity=1,
            subtotal=10000
        )
        print("🛍️ Article test ajouté à la commande")
        
        print("✅ Commande test créée avec succès!")
        
    except Exception as e:
        print(f"❌ Erreur création commande test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Créer une commande test si nécessaire
    create_test_order()
    
    # Lancer le diagnostic
    debug_email_reception()
    
    print("\n" + "=" * 70)
    print("📋 RÉSUMÉ DU DIAGNOSTIC")
    print("=" * 70)
    print("🔍 VÉRIFIEZ LA CONSOLE DJANGO (où runserver tourne)")
    print("📧 Les emails doivent s'afficher DANS CETTE CONSOLE")
    print("❌ Si rien dans la console -> Problème d'envoi")
    print("✅ Si dans la console -> Le système fonctionne (mode développement)")
    print("💡 En production, changez EMAIL_BACKEND pour SMTP")