#!/bin/bash
# ========================================
# SCRIPT DE DÉPLOIEMENT - D&H-SHOP (Linux/Mac)
# ========================================

set -e  # Arrêter en cas d'erreur

echo ""
echo "============================================"
echo "  DÉPLOIEMENT DE D&H-SHOP (Linux/Mac)"
echo "============================================"
echo ""

# ========================================
# 1. VÉRIFICATION DE L'ENVIRONNEMENT VIRTUEL
# ========================================
echo "[1/8] Vérification de l'environnement virtuel..."
if [ ! -d "venv" ]; then
    echo "❌ ERREUR: Environnement virtuel non trouvé"
    echo "   Créez-le avec: python3 -m venv venv"
    exit 1
fi

source venv/bin/activate
echo "✅ Environnement virtuel activé"

# ========================================
# 2. VÉRIFICATION DU FICHIER .env
# ========================================
echo ""
echo "[2/8] Vérification du fichier .env..."
if [ ! -f ".env" ]; then
    echo "❌ ERREUR: Fichier .env manquant"
    echo "   Copiez env.example vers .env et configurez-le"
    echo "   Commande: cp env.example .env"
    exit 1
fi
echo "✅ Fichier .env trouvé"

# ========================================
# 3. INSTALLATION DES DÉPENDANCES
# ========================================
echo ""
echo "[3/8] Installation des dépendances..."
pip install --upgrade pip
pip install -r requirements.txt
echo "✅ Dépendances installées"

# ========================================
# 4. VÉRIFICATION DE LA CONFIGURATION
# ========================================
echo ""
echo "[4/8] Vérification de la configuration Django..."
python manage.py check --deploy
echo "✅ Configuration valide"

# ========================================
# 5. MIGRATIONS DE BASE DE DONNÉES
# ========================================
echo ""
echo "[5/8] Application des migrations..."
python manage.py migrate
echo "✅ Migrations appliquées"

# ========================================
# 6. COLLECTE DES FICHIERS STATIQUES
# ========================================
echo ""
echo "[6/8] Collecte des fichiers statiques..."
python manage.py collectstatic --noinput --clear
echo "✅ Fichiers statiques collectés"

# ========================================
# 7. CRÉATION D'UN SUPERUTILISATEUR (Optionnel)
# ========================================
echo ""
echo "[7/8] Création d'un superutilisateur (optionnel)..."
read -p "Créer un superutilisateur maintenant ? (o/n): " CREATE_SUPERUSER
if [ "$CREATE_SUPERUSER" = "o" ] || [ "$CREATE_SUPERUSER" = "O" ]; then
    python manage.py createsuperuser
fi

# ========================================
# 8. DÉMARRAGE DU SERVEUR
# ========================================
echo ""
echo "[8/8] Démarrage du serveur..."
echo ""
echo "============================================"
echo "  SERVEUR PRÊT !"
echo "============================================"
echo ""
echo "  URL: http://127.0.0.1:8000"
echo "  Admin: http://127.0.0.1:8000/admin/"
echo ""
echo "  Appuyez sur CTRL+C pour arrêter le serveur"
echo ""
echo "============================================"
echo ""

# Démarrage avec Gunicorn (production Linux)
gunicorn config.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 4 \
    --threads 2 \
    --timeout 120 \
    --access-logfile logs/gunicorn_access.log \
    --error-logfile logs/gunicorn_error.log