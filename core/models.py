from django.db import models
from django.core.validators import URLValidator, EmailValidator
from django.core.exceptions import ValidationError


class SiteSettings(models.Model):
    """
    Paramètres globaux du site e-commerce
    
    Ce modèle utilise le pattern Singleton pour garantir qu'une seule 
    instance existe dans la base de données.
    
    Accessible via: SiteSettings.get_settings()
    """
    
    # ========================================
    # INFORMATIONS GÉNÉRALES DU SITE
    # ========================================
    
    site_name = models.CharField(
        max_length=100,
        default='D&H-SHOP',
        verbose_name="Nom du site",
        help_text="Nom affiché dans le header et les emails"
    )
    
    site_tagline = models.CharField(
        max_length=200,
        default='Votre boutique e-commerce au Gabon',
        blank=True,
        verbose_name="Slogan/Tagline",
        help_text="Phrase d'accroche affichée sous le logo"
    )
    
    site_description = models.TextField(
        default='Boutique en ligne proposant des produits de qualité avec livraison rapide.',
        blank=True,
        verbose_name="Description du site",
        help_text="Description générale pour le footer et le SEO"
    )
    
    logo = models.ImageField(
        upload_to='site_settings/',
        blank=True,
        null=True,
        verbose_name="Logo du site",
        help_text="Logo affiché dans la navbar (recommandé: 200x60px, PNG avec fond transparent)"
    )
    
    favicon = models.ImageField(
        upload_to='site_settings/',
        blank=True,
        null=True,
        verbose_name="Favicon",
        help_text="Icône affichée dans l'onglet du navigateur (recommandé: 32x32px ou 64x64px, PNG/ICO)"
    )
    
    # ========================================
    # COORDONNÉES DE CONTACT
    # ========================================
    
    contact_email = models.EmailField(
        default='contact@dh-shop.tg',
        validators=[EmailValidator()],
        verbose_name="Email de contact",
        help_text="Email principal pour les demandes clients"
    )
    
    contact_phone = models.CharField(
        max_length=20,
        default='+228 XX XX XX XX',
        verbose_name="Téléphone de contact",
        help_text="Numéro principal affiché sur le site"
    )
    
    contact_whatsapp = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="WhatsApp",
        help_text="Numéro WhatsApp pour le support client (format international)"
    )
    
    # ========================================
    # ADRESSE PHYSIQUE
    # ========================================
    
    address_line1 = models.CharField(
        max_length=255,
        default='123 Rue du Commerce',
        verbose_name="Adresse ligne 1"
    )
    
    address_line2 = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Adresse ligne 2 (optionnel)"
    )
    
    city = models.CharField(
        max_length=100,
        default='Libreville',
        verbose_name="Ville"
    )
    
    country = models.CharField(
        max_length=100,
        default='Gabon',
        verbose_name="Pays"
    )
    
    postal_code = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="Code postal"
    )
    
    # ========================================
    # HORAIRES D'OUVERTURE
    # ========================================
    
    business_hours = models.TextField(
        default='Lun - Sam: 8h - 18h\nDimanche: Fermé',
        blank=True,
        verbose_name="Horaires d'ouverture",
        help_text="Format libre. Utilisez des retours à la ligne pour séparer les jours"
    )
    
    # ========================================
    # RÉSEAUX SOCIAUX
    # ========================================
    
    facebook_url = models.URLField(
        blank=True,
        validators=[URLValidator()],
        verbose_name="URL Facebook",
        help_text="Lien complet vers votre page Facebook"
    )
    
    instagram_url = models.URLField(
        blank=True,
        validators=[URLValidator()],
        verbose_name="URL Instagram",
        help_text="Lien complet vers votre profil Instagram"
    )
    
    twitter_url = models.URLField(
        blank=True,
        validators=[URLValidator()],
        verbose_name="URL Twitter/X",
        help_text="Lien complet vers votre profil Twitter/X"
    )
    
    linkedin_url = models.URLField(
        blank=True,
        validators=[URLValidator()],
        verbose_name="URL LinkedIn",
        help_text="Lien complet vers votre page LinkedIn"
    )
    
    youtube_url = models.URLField(
        blank=True,
        validators=[URLValidator()],
        verbose_name="URL YouTube",
        help_text="Lien complet vers votre chaîne YouTube"
    )
    
    tiktok_url = models.URLField(
        blank=True,
        validators=[URLValidator()],
        verbose_name="URL TikTok",
        help_text="Lien complet vers votre compte TikTok"
    )
    
    # ========================================
    # SEO (RÉFÉRENCEMENT)
    # ========================================
    
    meta_title = models.CharField(
        max_length=70,
        default='D&H-SHOP - E-Commerce au Gabon',
        verbose_name="Meta titre (SEO)",
        help_text="Titre affiché dans les résultats de recherche (max 70 caractères)"
    )
    
    meta_description = models.CharField(
        max_length=160,
        default='Boutique en ligne au Gabon proposant des produits de qualité avec livraison rapide à Libreville.',
        verbose_name="Meta description (SEO)",
        help_text="Description affichée dans les résultats de recherche (max 160 caractères)"
    )
    
    meta_keywords = models.CharField(
        max_length=255,
        default='ecommerce, gabon, boutique en ligne, livraison, shopping',
        blank=True,
        verbose_name="Meta mots-clés (SEO)",
        help_text="Mots-clés séparés par des virgules (optionnel, peu utilisé aujourd'hui)"
    )
    
    google_analytics_id = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="ID Google Analytics",
        help_text="Format: G-XXXXXXXXXX ou UA-XXXXXXXXX-X"
    )
    
    facebook_pixel_id = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="ID Facebook Pixel",
        help_text="ID du pixel Facebook pour le tracking"
    )
    
    # ========================================
    # MESSAGES PERSONNALISABLES
    # ========================================
    
    welcome_message = models.TextField(
        default='Bienvenue sur D&H-SHOP ! Profitez de nos offres exceptionnelles.',
        blank=True,
        verbose_name="Message de bienvenue",
        help_text="Affiché sur la page d'accueil ou en bannière"
    )
    
    maintenance_mode = models.BooleanField(
        default=False,
        verbose_name="Mode maintenance",
        help_text="Active le mode maintenance (site inaccessible sauf pour les admins)"
    )
    
    maintenance_message = models.TextField(
        default='Site en maintenance. Nous revenons bientôt !',
        blank=True,
        verbose_name="Message de maintenance",
        help_text="Message affiché quand le mode maintenance est actif"
    )
    
    # ========================================
    # PARAMÈTRES DE NEWSLETTER
    # ========================================
    
    newsletter_enabled = models.BooleanField(
        default=True,
        verbose_name="Newsletter active",
        help_text="Afficher le formulaire d'inscription à la newsletter"
    )
    
    newsletter_description = models.CharField(
        max_length=200,
        default='Recevez nos offres exclusives',
        blank=True,
        verbose_name="Description newsletter",
        help_text="Texte affiché sous le formulaire newsletter"
    )
    
    # ========================================
    # INFORMATIONS LÉGALES
    # ========================================
    
    company_legal_name = models.CharField(
        max_length=255,
        default='D&H-SHOP SARL',
        blank=True,
        verbose_name="Raison sociale",
        help_text="Nom légal de l'entreprise"
    )
    
    company_registration_number = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Numéro d'immatriculation",
        help_text="RCCM, SIRET ou équivalent"
    )
    
    vat_number = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Numéro TVA",
        help_text="Numéro de TVA intracommunautaire si applicable"
    )
    
    # ========================================
    # MÉTADONNÉES
    # ========================================
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Créé le"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Mis à jour le"
    )
    
    class Meta:
        verbose_name = "Paramètres du site"
        verbose_name_plural = "Paramètres du site"
    
    def __str__(self):
        return f"Paramètres du site - {self.site_name}"
    
    # ========================================
    # PATTERN SINGLETON
    # ========================================
    
    def save(self, *args, **kwargs):
        """
        Garantit qu'une seule instance existe (Singleton)
        """
        if not self.pk and SiteSettings.objects.exists():
            # Si on essaie de créer une nouvelle instance alors qu'une existe déjà
            raise ValidationError(
                "Une seule instance de SiteSettings peut exister. "
                "Veuillez modifier l'instance existante plutôt que d'en créer une nouvelle."
            )
        super().save(*args, **kwargs)
    
    @classmethod
    def get_settings(cls):
        """
        Récupère l'instance unique des paramètres du site.
        Crée une instance avec les valeurs par défaut si elle n'existe pas.
        
        Usage dans les vues:
            settings = SiteSettings.get_settings()
            site_name = settings.site_name
        """
        settings, created = cls.objects.get_or_create(pk=1)
        return settings
    
    @classmethod
    def load(cls):
        """
        Alias de get_settings() pour plus de lisibilité
        """
        return cls.get_settings()
    
    # ========================================
    # MÉTHODES UTILITAIRES
    # ========================================
    
    def get_full_address(self):
        """
        Retourne l'adresse complète formatée
        """
        parts = [
            self.address_line1,
            self.address_line2,
            self.city,
            self.postal_code,
            self.country
        ]
        return ", ".join(filter(None, parts))
    
    def has_social_media(self):
        """
        Vérifie si au moins un réseau social est configuré
        """
        return any([
            self.facebook_url,
            self.instagram_url,
            self.twitter_url,
            self.linkedin_url,
            self.youtube_url,
            self.tiktok_url
        ])
    
    def get_social_media_links(self):
        """
        Retourne un dictionnaire des réseaux sociaux configurés
        """
        social_media = {}
        
        if self.facebook_url:
            social_media['facebook'] = {
                'url': self.facebook_url,
                'icon': 'fab fa-facebook-f',
                'name': 'Facebook'
            }
        if self.instagram_url:
            social_media['instagram'] = {
                'url': self.instagram_url,
                'icon': 'fab fa-instagram',
                'name': 'Instagram'
            }
        if self.twitter_url:
            social_media['twitter'] = {
                'url': self.twitter_url,
                'icon': 'fab fa-twitter',
                'name': 'Twitter'
            }
        if self.linkedin_url:
            social_media['linkedin'] = {
                'url': self.linkedin_url,
                'icon': 'fab fa-linkedin-in',
                'name': 'LinkedIn'
            }
        if self.youtube_url:
            social_media['youtube'] = {
                'url': self.youtube_url,
                'icon': 'fab fa-youtube',
                'name': 'YouTube'
            }
        if self.tiktok_url:
            social_media['tiktok'] = {
                'url': self.tiktok_url,
                'icon': 'fab fa-tiktok',
                'name': 'TikTok'
            }
        
        return social_media
    
    def get_business_hours_list(self):
        """
        Retourne les horaires d'ouverture sous forme de liste
        """
        if not self.business_hours:
            return []
        return [line.strip() for line in self.business_hours.split('\n') if line.strip()]
    
    @property
    def logo_url(self):
        """
        Retourne l'URL du logo (safe pour les templates)
        """
        if self.logo:
            return self.logo.url
        return None
    
    @property
    def favicon_url(self):
        """
        Retourne l'URL du favicon (safe pour les templates)
        """
        if self.favicon:
            return self.favicon.url
        return None