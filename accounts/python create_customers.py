import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from accounts.models import Customer

# Créer les profils manquants
for user in User.objects.all():
    customer, created = Customer.objects.get_or_create(user=user)
    if created:
        print(f"✓ Profil créé pour {user.username}")
    else:
        print(f"- {user.username} a déjà un profil")

print("\nTerminé !")