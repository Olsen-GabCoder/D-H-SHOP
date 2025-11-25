"""
Script de test pour vérifier le fonctionnement des services Email et PDF
À exécuter depuis le shell Django : python manage.py shell < test_services.py
"""

print("=" * 60)
print("TEST DES SERVICES EMAIL ET PDF")
print("=" * 60)

# Test 1 : Import des services
print("\n[1] Import des services...")
try:
    from core.email_service import EmailService
    from core.pdf_service import PDFService
    from django.contrib.auth.models import User
    from orders.models import Order
    print("✅ Services importés avec succès")
except Exception as e:
    print(f"❌ Erreur d'import : {str(e)}")
    exit(1)

# Test 2 : Vérifier la configuration email
print("\n[2] Vérification de la configuration email...")
try:
    from django.conf import settings
    print(f"   EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
    print(f"   EMAIL_HOST: {settings.EMAIL_HOST}")
    print(f"   EMAIL_PORT: {settings.EMAIL_PORT}")
    print(f"   DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")
    print("✅ Configuration email OK")
except Exception as e:
    print(f"❌ Erreur configuration : {str(e)}")

# Test 3 : Récupérer un utilisateur de test
print("\n[3] Récupération d'un utilisateur de test...")
try:
    user = User.objects.first()
    if user:
        print(f"✅ Utilisateur trouvé : {user.username} ({user.email})")
    else:
        print("⚠️  Aucun utilisateur trouvé dans la base de données")
        print("   Créez un utilisateur avec : python manage.py createsuperuser")
except Exception as e:
    print(f"❌ Erreur : {str(e)}")

# Test 4 : Test d'envoi d'email de bienvenue (dry-run)
print("\n[4] Test d'envoi d'email de bienvenue...")
if user and user.email:
    try:
        # Simuler l'envoi (ne sera pas envoyé si backend = console)
        print(f"   Tentative d'envoi à : {user.email}")
        EmailService.send_welcome_email(user)
        print("✅ Email de bienvenue envoyé (vérifier la console ou les logs)")
    except Exception as e:
        print(f"❌ Erreur envoi email : {str(e)}")
else:
    print("⚠️  Pas d'utilisateur avec email pour tester")

# Test 5 : Récupérer une commande de test
print("\n[5] Récupération d'une commande de test...")
try:
    order = Order.objects.first()
    if order:
        print(f"✅ Commande trouvée : {order.order_number}")
    else:
        print("⚠️  Aucune commande trouvée dans la base de données")
        print("   Créez une commande de test depuis l'interface")
except Exception as e:
    print(f"❌ Erreur : {str(e)}")

# Test 6 : Test de génération de facture PDF
print("\n[6] Test de génération de facture PDF...")
if order:
    try:
        pdf_buffer = PDFService.generate_invoice_pdf(order)
        
        # Sauvegarder le PDF de test
        test_filename = f"test_facture_{order.order_number}.pdf"
        with open(test_filename, 'wb') as f:
            f.write(pdf_buffer.read())
        
        print(f"✅ Facture PDF générée : {test_filename}")
        print(f"   Commande : {order.order_number}")
        print(f"   Total : {order.total} FCFA")
    except Exception as e:
        print(f"❌ Erreur génération PDF : {str(e)}")
        import traceback
        traceback.print_exc()
else:
    print("⚠️  Pas de commande pour tester la génération PDF")

# Test 7 : Test de génération de bon de livraison
print("\n[7] Test de génération de bon de livraison...")
if order:
    try:
        pdf_buffer = PDFService.generate_packing_slip_pdf(order)
        
        # Sauvegarder le PDF de test
        test_filename = f"test_bon_livraison_{order.order_number}.pdf"
        with open(test_filename, 'wb') as f:
            f.write(pdf_buffer.read())
        
        print(f"✅ Bon de livraison PDF généré : {test_filename}")
    except Exception as e:
        print(f"❌ Erreur génération bon de livraison : {str(e)}")
        import traceback
        traceback.print_exc()
else:
    print("⚠️  Pas de commande pour tester")

# Test 8 : Test d'envoi d'email de confirmation de commande
print("\n[8] Test d'envoi d'email de confirmation de commande...")
if order:
    try:
        EmailService.send_order_confirmation(order)
        print(f"✅ Email de confirmation envoyé pour commande {order.order_number}")
    except Exception as e:
        print(f"❌ Erreur envoi email : {str(e)}")
else:
    print("⚠️  Pas de commande pour tester")

# Résumé final
print("\n" + "=" * 60)
print("RÉSUMÉ DES TESTS")
print("=" * 60)
print("\n✅ Tests terminés !")
print("\nSi vous utilisez EMAIL_BACKEND = 'console', les emails sont")
print("affichés dans la console au lieu d'être envoyés.")
print("\nPour activer l'envoi réel, configurez votre fichier .env avec")
print("vos identifiants SMTP et utilisez EMAIL_BACKEND = 'smtp'.")
print("\n" + "=" * 60)