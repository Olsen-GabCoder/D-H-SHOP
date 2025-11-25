@echo off
REM ========================================
REM SCRIPT DE DÉPLOIEMENT - D&H-SHOP (Windows)
REM ========================================

echo.
echo ============================================
echo   DEPLOIEMENT DE D^&H-SHOP (Windows)
echo ============================================
echo.

REM ========================================
REM 1. VÉRIFICATION DE L'ENVIRONNEMENT VIRTUEL
REM ========================================
echo [1/8] Verification de l'environnement virtuel...
if not exist "venv\Scripts\activate.bat" (
    echo ❌ ERREUR: Environnement virtuel non trouve
    echo    Creez-le avec: python -m venv venv
    pause
    exit /b 1
)

call venv\Scripts\activate.bat
echo ✅ Environnement virtuel active

REM ========================================
REM 2. VÉRIFICATION DU FICHIER .env
REM ========================================
echo.
echo [2/8] Verification du fichier .env...
if not exist ".env" (
    echo ❌ ERREUR: Fichier .env manquant
    echo    Copiez env.example vers .env et configurez-le
    echo    Commande: copy env.example .env
    pause
    exit /b 1
)
echo ✅ Fichier .env trouve

REM ========================================
REM 3. INSTALLATION DES DÉPENDANCES
REM ========================================
echo.
echo [3/8] Installation des dependances...
pip install --upgrade pip
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ ERREUR: Installation des dependances echouee
    pause
    exit /b 1
)
echo ✅ Dependances installees

REM ========================================
REM 4. VÉRIFICATION DE LA CONFIGURATION
REM ========================================
echo.
echo [4/8] Verification de la configuration Django...
python manage.py check --deploy
if errorlevel 1 (
    echo ❌ ERREUR: Configuration invalide
    pause
    exit /b 1
)
echo ✅ Configuration valide

REM ========================================
REM 5. MIGRATIONS DE BASE DE DONNÉES
REM ========================================
echo.
echo [5/8] Application des migrations...
python manage.py migrate
if errorlevel 1 (
    echo ❌ ERREUR: Migrations echouees
    pause
    exit /b 1
)
echo ✅ Migrations appliquees

REM ========================================
REM 6. COLLECTE DES FICHIERS STATIQUES
REM ========================================
echo.
echo [6/8] Collecte des fichiers statiques...
python manage.py collectstatic --noinput --clear
if errorlevel 1 (
    echo ❌ ERREUR: Collecte des fichiers statiques echouee
    pause
    exit /b 1
)
echo ✅ Fichiers statiques collectes

REM ========================================
REM 7. CRÉATION D'UN SUPERUTILISATEUR (Optionnel)
REM ========================================
echo.
echo [7/8] Creation d'un superutilisateur (optionnel)...
set /p CREATE_SUPERUSER="Creer un superutilisateur maintenant ? (o/n): "
if /i "%CREATE_SUPERUSER%"=="o" (
    python manage.py createsuperuser
)

REM ========================================
REM 8. DÉMARRAGE DU SERVEUR
REM ========================================
echo.
echo [8/8] Demarrage du serveur...
echo.
echo ============================================
echo   SERVEUR PRET !
echo ============================================
echo.
echo   URL: http://127.0.0.1:8000
echo   Admin: http://127.0.0.1:8000/admin/
echo.
echo   Appuyez sur CTRL+C pour arreter le serveur
echo.
echo ============================================
echo.

REM Démarrage avec Waitress (production Windows)
waitress-serve --port=8000 --threads=4 config.wsgi:application

pause