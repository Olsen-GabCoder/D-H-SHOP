#!/usr/bin/env bash
set -o errexit

echo "🔧 Installation des dépendances..."
pip install --upgrade pip
pip install -r requirements.txt

echo "📁 Collecte des fichiers statiques..."
python manage.py collectstatic --noinput --clear

echo "🔄 Application des migrations..."
python manage.py migrate --noinput

echo "👤 Création du superutilisateur..."
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='Olsen').exists():
    User.objects.create_superuser('Olsen', 'olsenkampala@gmail.com', 'olsenk2000#2000')
    print('✅ Superutilisateur créé : Olsen / olsenk2000#2000')
else:
    print('✅ Superutilisateur existe déjà')
"

echo "✅ Build terminé avec succès !"