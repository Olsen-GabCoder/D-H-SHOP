from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.db.models.signals import post_save
from django.dispatch import receiver


class Customer(models.Model):
    """
    Profil client étendu (lié au User Django)
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='customer',
        verbose_name="Utilisateur"
    )
    
    # Informations personnelles
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Le numéro de téléphone doit être au format : '+999999999'. 9 à 15 chiffres."
    )
    phone = models.CharField(
        validators=[phone_regex],
        max_length=17,
        blank=True,
        verbose_name="Téléphone"
    )
    date_of_birth = models.DateField(
        null=True,
        blank=True,
        verbose_name="Date de naissance"
    )
    profile_picture = models.ImageField(
        upload_to='customers/profiles/',
        blank=True,
        null=True,
        verbose_name="Photo de profil"
    )
    
    # Préférences de communication
    email_notifications = models.BooleanField(
        default=True,
        verbose_name="Notifications par email"
    )
    sms_notifications = models.BooleanField(
        default=False,
        verbose_name="Notifications par SMS"
    )
    whatsapp_notifications = models.BooleanField(
        default=False,
        verbose_name="Notifications par WhatsApp"
    )
    
    # Statistiques
    total_orders = models.IntegerField(
        default=0,
        verbose_name="Nombre total de commandes"
    )
    total_spent = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Montant total dépensé"
    )
    
    # Gestion du compte
    is_blocked = models.BooleanField(
        default=False,
        verbose_name="Compte bloqué"
    )
    block_reason = models.TextField(
        blank=True,
        verbose_name="Raison du blocage"
    )
    
    # Dates
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Inscrit le"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Mis à jour le"
    )

    class Meta:
        verbose_name = "Client"
        verbose_name_plural = "Clients"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username}"

    @property
    def full_name(self):
        """Retourne le nom complet du client"""
        return self.user.get_full_name() or self.user.username

    @property
    def email(self):
        """Retourne l'email du client"""
        return self.user.email


@receiver(post_save, sender=User)
def create_customer_profile(sender, instance, created, **kwargs):
    """
    Signal : Crée automatiquement un profil Customer lors de la création d'un User
    """
    if created:
        Customer.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_customer_profile(sender, instance, **kwargs):
    """
    Signal : Sauvegarde le profil Customer lors de la sauvegarde du User
    """
    if hasattr(instance, 'customer'):
        instance.customer.save()


class Address(models.Model):
    """
    Adresses de livraison et facturation
    """
    ADDRESS_TYPE_CHOICES = [
        ('shipping', 'Livraison'),
        ('billing', 'Facturation'),
    ]

    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name='addresses',
        verbose_name="Client"
    )
    
    # Informations de contact
    full_name = models.CharField(
        max_length=200,
        verbose_name="Nom complet"
    )
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Le numéro de téléphone doit être au format : '+999999999'. 9 à 15 chiffres."
    )
    phone = models.CharField(
        validators=[phone_regex],
        max_length=17,
        verbose_name="Téléphone"
    )
    
    # Adresse complète
    address_line1 = models.CharField(
        max_length=255,
        verbose_name="Adresse ligne 1"
    )
    address_line2 = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Adresse ligne 2 (optionnel)"
    )
    city = models.CharField(
        max_length=100,
        verbose_name="Ville"
    )
    state = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Région/État"
    )
    postal_code = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="Code postal"
    )
    country = models.CharField(
        max_length=100,
        default='Togo',
        verbose_name="Pays"
    )
    
    # Type et statut
    address_type = models.CharField(
        max_length=10,
        choices=ADDRESS_TYPE_CHOICES,
        default='shipping',
        verbose_name="Type d'adresse"
    )
    is_default = models.BooleanField(
        default=False,
        verbose_name="Adresse par défaut"
    )
    
    # Dates
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Créée le"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Modifiée le"
    )

    class Meta:
        verbose_name = "Adresse"
        verbose_name_plural = "Adresses"
        ordering = ['-is_default', '-created_at']

    def __str__(self):
        return f"{self.full_name} - {self.city} ({self.get_address_type_display()})"

    def save(self, *args, **kwargs):
        """
        Si cette adresse est définie par défaut,
        retire le statut par défaut des autres adresses du même type
        """
        if self.is_default:
            Address.objects.filter(
                customer=self.customer,
                address_type=self.address_type,
                is_default=True
            ).exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)

    @property
    def full_address(self):
        """Retourne l'adresse complète formatée"""
        parts = [
            self.address_line1,
            self.address_line2,
            self.city,
            self.state,
            self.postal_code,
            self.country
        ]
        return ", ".join(filter(None, parts))