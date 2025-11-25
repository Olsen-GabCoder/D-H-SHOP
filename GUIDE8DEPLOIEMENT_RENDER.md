# 🚀 GUIDE COMPLET : DÉPLOYER D&H-SHOP SUR RENDER.COM (GRATUIT)

## 📋 PRÉREQUIS

- ✅ Compte GitHub (gratuit) : https://github.com/signup
- ✅ Compte Render (gratuit) : https://render.com/register
- ✅ Votre projet Django fonctionnel en local

---

## PHASE 1️⃣ : PRÉPARATION DU CODE (15 minutes)

### Étape 1.1 : Créer un compte GitHub

1. Aller sur https://github.com/signup
2. Créer un compte avec votre email
3. Vérifier votre email

### Étape 1.2 : Installer Git sur Windows

```powershell
# Télécharger Git : https://git-scm.com/download/win
# Installer avec les options par défaut
```

### Étape 1.3 : Configurer Git

```powershell
git config --global user.name "Votre Nom"
git config --global user.email "votre-email@example.com"
```

### Étape 1.4 : Créer le fichier .gitignore

Créez `.gitignore` à la racine du projet :

```
# Environnement Python
venv/
env/
*.pyc
__pycache__/

# Django
*.log
db.sqlite3
media/
staticfiles/

# Secrets
.env
*.env

# IDE
.vscode/
.idea/

# OS
.DS_Store
Thumbs.db
```

### Étape 1.5 : Créer les fichiers Render

**1. Créer `build.sh` à la racine :**
```bash
#!/usr/bin/env bash
set -o errexit

pip install --upgrade pip
pip install -r requirements.txt
python manage.py collectstatic --noinput --clear
python manage.py migrate --noinput
```

**2. Rendre exécutable (Git Bash) :**
```bash
chmod +x build.sh
```

**3. Créer `render.yaml` à la racine :**
(Copier le contenu de l'artifact `render_yaml_config`)

**4. Mettre à jour `requirements.txt` :**
(Copier le contenu de l'artifact `requirements_render`)

### Étape 1.6 : Modifier settings.py

1. Ajouter en haut (après les imports) :
```python
import dj_database_url
```

2. Remplacer la section DATABASES :
(Copier le contenu de l'artifact `settings_render_production`)

### Étape 1.7 : Créer le dépôt GitHub

```powershell
# Dans le dossier de votre projet
cd C:\mon_ecommerce

# Initialiser Git
git init

# Ajouter tous les fichiers
git add .

# Premier commit
git commit -m "Initial commit - D&H-Shop"

# Créer un dépôt sur GitHub (via l'interface web)
# Puis lier votre projet :
git remote add origin https://github.com/VOTRE-USERNAME/dh-shop.git
git branch -M main
git push -u origin main
```

---

## PHASE 2️⃣ : DÉPLOIEMENT SUR RENDER (20 minutes)

### Étape 2.1 : Créer un compte Render

1. Aller sur https://render.com/register
2. S'inscrire avec GitHub (recommandé)
3. Autoriser l'accès à vos dépôts

### Étape 2.2 : Créer la base de données MySQL

1. Dans le dashboard Render, cliquer **"New +"** → **"PostgreSQL"** (gratuit)
   - ⚠️ **ATTENTION** : Render ne propose pas MySQL gratuit
   - **Solution** : Utiliser PostgreSQL (aussi puissant que MySQL)

2. Configuration :
   - **Name** : `dh-shop-db`
   - **Database** : `ecommerce_db`
   - **User** : `ecommerce_user`
   - **Region** : Choisir le plus proche (Europe)
   - **Plan** : **Free** (0$/mois)

3. Cliquer **"Create Database"**

4. **Copier l'URL de connexion** (Internal Database URL)

### Étape 2.3 : Modifier le code pour PostgreSQL

**⚠️ IMPORTANT** : Render gratuit = PostgreSQL (pas MySQL)

**1. Modifier `requirements.txt` :**
```txt
# Remplacer mysqlclient par :
psycopg2-binary==2.9.9
```

**2. Le reste reste identique** (Django gère automatiquement PostgreSQL)

### Étape 2.4 : Créer le service Web

1. Cliquer **"New +"** → **"Web Service"**
2. Sélectionner votre dépôt GitHub `dh-shop`
3. Configuration :
   - **Name** : `dh-shop`
   - **Region** : Europe (ou le plus proche)
   - **Branch** : `main`
   - **Runtime** : `Python 3`
   - **Build Command** : `./build.sh`
   - **Start Command** : `gunicorn config.wsgi:application`
   - **Plan** : **Free** (0$/mois)

4. **Variables d'environnement** (cliquer "Advanced") :

```
DEBUG=False
SECRET_KEY=[Généré automatiquement par Render]
ALLOWED_HOSTS=.onrender.com
DATABASE_URL=[Copier depuis la base de données créée]

# Email (utiliser Gmail)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=votre-email@gmail.com
EMAIL_HOST_PASSWORD=votre-mot-de-passe-application
DEFAULT_FROM_EMAIL=D&H-Shop <noreply@dhshop.com>

# Boutique
SITE_NAME=D&H-Shop
SHOP_NAME=D&H-Shop
SHOP_EMAIL=contact@dhshop.com
SHOP_PHONE=+241 XX XX XX XX
SHOP_ADDRESS=Libreville, Gabon
```

5. Cliquer **"Create Web Service"**

### Étape 2.5 : Attendre le déploiement (5-10 minutes)

Render va :
- ✅ Cloner votre code
- ✅ Installer les dépendances
- ✅ Collecter les fichiers statiques
- ✅ Appliquer les migrations
- ✅ Démarrer l'application

---

## PHASE 3️⃣ : POST-DÉPLOIEMENT (10 minutes)

### Étape 3.1 : Créer un superutilisateur

1. Dans Render, aller sur votre service Web
2. Cliquer sur **"Shell"** (en haut à droite)
3. Exécuter :
```bash
python manage.py createsuperuser
```

### Étape 3.2 : Tester l'application

Votre site est accessible sur :
```
https://dh-shop.onrender.com
```

Tester :
- ✅ Page d'accueil
- ✅ Admin : `/admin/`
- ✅ Inscription/Connexion
- ✅ Boutique

### Étape 3.3 : Configurer UptimeRobot (Optionnel - Gratuit)

Pour éviter que l'app s'endorme :

1. Aller sur https://uptimerobot.com (gratuit)
2. Créer un compte
3. **Add New Monitor** :
   - Type : HTTP(s)
   - URL : `https://dh-shop.onrender.com`
   - Interval : 5 minutes

---

## 🔧 MISES À JOUR FUTURES

Pour déployer des modifications :

```powershell
git add .
git commit -m "Description des modifications"
git push origin main
```

Render redéploiera automatiquement ! ✅

---

## ⚠️ LIMITATIONS DU PLAN GRATUIT

- App s'endort après 15 min d'inactivité (réveil : 30s)
- PostgreSQL : 1 GB de stockage
- 750 heures/mois de compute time
- Pas de domaine personnalisé (seulement `.onrender.com`)

**Pour lever ces limites** : Plan payant à $7/mois

---

## 🆘 DÉPANNAGE

### Erreur : "Build failed"
→ Vérifier les logs dans Render
→ S'assurer que `build.sh` est exécutable

### Erreur : "Database connection failed"
→ Vérifier `DATABASE_URL` dans les variables d'environnement

### Erreur : "Static files not found"
→ Vérifier que `STATIC_ROOT` est défini
→ Relancer `python manage.py collectstatic`

---

## 📞 SUPPORT

- Documentation Render : https://render.com/docs
- Support Render : support@render.com
- Community : https://community.render.com