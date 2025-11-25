# 🚀 GUIDE DE DÉPLOIEMENT - D&H-SHOP

## 📌 ÉTAPES DE DÉPLOIEMENT

### 1️⃣ **Installation initiale (une seule fois)**

#### Sur Windows :
```powershell
# 1. Créer l'environnement virtuel
python -m venv venv

# 2. Activer l'environnement
venv\Scripts\activate

# 3. Copier et configurer .env
copy env.example .env
# Éditer .env avec vos valeurs

# 4. Installer les dépendances
pip install -r requirements.txt

# 5. Créer la base de données MySQL
mysql -u root -p
CREATE DATABASE ecommerce_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
EXIT;

# 6. Appliquer les migrations
python manage.py migrate

# 7. Créer un superutilisateur
python manage.py createsuperuser

# 8. Collecter les fichiers statiques
python manage.py collectstatic --noinput
```

#### Sur Linux/Mac :
```bash
# 1. Créer l'environnement virtuel
python3 -m venv venv

# 2. Activer l'environnement
source venv/bin/activate

# 3. Copier et configurer .env
cp env.example .env
# Éditer .env avec vos valeurs

# 4. Installer les dépendances
pip install -r requirements.txt

# 5. Créer la base de données MySQL
mysql -u root -p
CREATE DATABASE ecommerce_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
EXIT;

# 6. Appliquer les migrations
python manage.py migrate

# 7. Créer un superutilisateur
python manage.py createsuperuser

# 8. Collecter les fichiers statiques
python manage.py collectstatic --noinput

# 9. Rendre le script exécutable
chmod +x deploy_linux.sh
```

---

### 2️⃣ **Déploiement rapide (après installation)**

#### Sur Windows :
```powershell
# Exécuter le script de déploiement
deploy_windows.bat
```

#### Sur Linux/Mac :
```bash
# Exécuter le script de déploiement
./deploy_linux.sh
```

---

## 🔧 CONFIGURATION REQUISE DANS .env

### Variables obligatoires :
```env
# Django
SECRET_KEY=votre_cle_secrete_generee
DEBUG=False  # True en développement, False en production
ALLOWED_HOSTS=votre-domaine.com,www.votre-domaine.com

# Base de données
DB_NAME=ecommerce_db
DB_USER=root
DB_PASSWORD=votre_mot_de_passe_mysql
DB_HOST=localhost
DB_PORT=3306

# Email (Production)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=votre_email@gmail.com
EMAIL_HOST_PASSWORD=votre_mot_de_passe_application
DEFAULT_FROM_EMAIL=Votre Boutique <noreply@votreboutique.com>
```

---

## 🌐 DÉPLOIEMENT SUR UN VPS (Production)

### Option 1 : Nginx + Gunicorn (Linux)

#### 1. Installer les dépendances système :
```bash
sudo apt update
sudo apt install python3-pip python3-venv mysql-server nginx
```

#### 2. Configurer Nginx :
Créer `/etc/nginx/sites-available/dhshop` :
```nginx
server {
    listen 80;
    server_name votre-domaine.com www.votre-domaine.com;

    location /static/ {
        alias /home/votre-user/mon_ecommerce/staticfiles/;
    }

    location /media/ {
        alias /home/votre-user/mon_ecommerce/media/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

#### 3. Activer le site :
```bash
sudo ln -s /etc/nginx/sites-available/dhshop /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

#### 4. Créer un service systemd :
Créer `/etc/systemd/system/dhshop.service` :
```ini
[Unit]
Description=D&H-Shop Gunicorn daemon
After=network.target

[Service]
User=votre-user
Group=www-data
WorkingDirectory=/home/votre-user/mon_ecommerce
ExecStart=/home/votre-user/mon_ecommerce/venv/bin/gunicorn \
          --workers 4 \
          --bind 127.0.0.1:8000 \
          config.wsgi:application

[Install]
WantedBy=multi-user.target
```

#### 5. Démarrer le service :
```bash
sudo systemctl start dhshop
sudo systemctl enable dhshop
sudo systemctl status dhshop
```

---

### Option 2 : Serveur Windows (IIS + Waitress)

Waitress est déjà configuré dans votre script `deploy_windows.bat`.

Pour un déploiement permanent :
```powershell
# Installer NSSM (Non-Sucking Service Manager)
choco install nssm

# Créer un service Windows
nssm install DHShop "C:\mon_ecommerce\venv\Scripts\waitress-serve.exe" "--port=8000 config.wsgi:application"
nssm set DHShop AppDirectory "C:\mon_ecommerce"
nssm start DHShop
```

---

## 🔒 CHECKLIST DE SÉCURITÉ (Production)

- [ ] `DEBUG=False` dans `.env`
- [ ] `SECRET_KEY` unique et complexe
- [ ] `ALLOWED_HOSTS` configuré avec votre domaine
- [ ] HTTPS activé (certificat SSL/TLS)
- [ ] Fichiers sensibles dans `.gitignore` (`.env`, `db.sqlite3`, `logs/`)
- [ ] Base de données MySQL sécurisée (pas de `root` en production)
- [ ] Firewall configuré (ports 80, 443 ouverts uniquement)
- [ ] Sauvegardes automatiques de la base de données
- [ ] Monitoring activé (Sentry, Logrotate)

---

## 🐛 DÉPANNAGE

### Erreur : `No module named 'mysql'`
```bash
# Windows
pip install mysql-connector-python

# Linux
pip install mysqlclient
```

### Erreur : `WhiteNoise non installé`
```bash
pip install whitenoise
```

### Erreur : `SMTP Authentication failed`
- Vérifier que l'authentification à 2 facteurs est activée (Gmail)
- Générer un "Mot de passe d'application" depuis votre compte Google
- Utiliser ce mot de passe dans `EMAIL_HOST_PASSWORD`

### Erreur : `Static files not found`
```bash
python manage.py collectstatic --noinput
```

---

## 📞 SUPPORT

Pour toute question :
- 📧 Email: support@dhshop.com
- 📚 Documentation: https://docs.dhshop.com
- 🐛 Issues: https://github.com/votre-repo/issues