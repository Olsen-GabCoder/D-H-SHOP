from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from orders.models import Order
import uuid


class PaymentMethod(models.Model):
    """
    Moyens de paiement disponibles
    """
    FEE_TYPE_CHOICES = [
        ('fixed', 'Montant fixe'),
        ('percentage', 'Pourcentage'),
    ]

    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Nom"
    )
    slug = models.SlugField(
        max_length=100,
        unique=True,
        verbose_name="Slug"
    )
    description = models.TextField(
        blank=True,
        verbose_name="Description"
    )
    instructions = models.TextField(
        blank=True,
        help_text="Instructions pour le client",
        verbose_name="Instructions"
    )
    
    # Logo/Icône
    logo = models.ImageField(
        upload_to='payment_methods/',
        blank=True,
        null=True,
        verbose_name="Logo"
    )
    
    # Frais supplémentaires (optionnel)
    has_fee = models.BooleanField(
        default=False,
        verbose_name="A des frais supplémentaires"
    )
    fee_type = models.CharField(
        max_length=20,
        choices=FEE_TYPE_CHOICES,
        default='fixed',
        verbose_name="Type de frais"
    )
    fee_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name="Montant des frais"
    )
    fee_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name="Pourcentage des frais"
    )
    
    # Configuration
    is_active = models.BooleanField(
        default=True,
        verbose_name="Actif"
    )
    requires_verification = models.BooleanField(
        default=False,
        help_text="Le paiement nécessite une vérification manuelle",
        verbose_name="Nécessite vérification"
    )
    display_order = models.IntegerField(
        default=0,
        verbose_name="Ordre d'affichage"
    )
    
    # Dates
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Créé le"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Mis à jour le"
    )

    class Meta:
        verbose_name = "Moyen de paiement"
        verbose_name_plural = "Moyens de paiement"
        ordering = ['display_order', 'name']

    def __str__(self):
        return self.name

    def calculate_fee(self, amount):
        """Calcule les frais pour un montant donné"""
        if not self.has_fee:
            return 0
        
        if self.fee_type == 'fixed':
            return self.fee_amount
        else:  # percentage
            return (amount * self.fee_percentage) / 100


class Payment(models.Model):
    """
    Enregistrements des paiements
    """
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('processing', 'En traitement'),
        ('completed', 'Complété'),
        ('failed', 'Échoué'),
        ('cancelled', 'Annulé'),
        ('refunded', 'Remboursé'),
    ]

    # Identifiants
    transaction_id = models.CharField(
        max_length=100,
        unique=True,
        editable=False,
        verbose_name="ID de transaction"
    )
    uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
        verbose_name="UUID"
    )
    
    # Relations
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='payments',
        verbose_name="Commande"
    )
    payment_method = models.ForeignKey(
        PaymentMethod,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Moyen de paiement"
    )
    
    # Montants
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Montant"
    )
    fee_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name="Frais de transaction"
    )
    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Montant total (avec frais)"
    )
    
    # Statut et suivi
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name="Statut"
    )
    
    # Références externes (pour Aitel Money, Moov Money, etc.)
    external_reference = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Référence externe"
    )
    provider_transaction_id = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="ID transaction fournisseur"
    )
    
    # Métadonnées (JSON pour informations supplémentaires)
    metadata = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Métadonnées"
    )
    
    # Messages et notes
    customer_message = models.TextField(
        blank=True,
        verbose_name="Message client"
    )
    admin_notes = models.TextField(
        blank=True,
        verbose_name="Notes admin"
    )
    failure_reason = models.TextField(
        blank=True,
        verbose_name="Raison de l'échec"
    )
    
    # Dates
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Créé le"
    )
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Complété le"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Mis à jour le"
    )

    class Meta:
        verbose_name = "Paiement"
        verbose_name_plural = "Paiements"
        ordering = ['-created_at']

    def __str__(self):
        return f"Paiement {self.transaction_id} - {self.order.order_number}"

    def save(self, *args, **kwargs):
        """Génère un ID de transaction unique si nécessaire"""
        if not self.transaction_id:
            # Format: PAY-UUID-TIMESTAMP
            import time
            timestamp = str(int(time.time()))
            self.transaction_id = f"PAY-{str(self.uuid)[:8].upper()}-{timestamp}"
        
        # Calcule le montant total avec les frais
        if self.payment_method and self.payment_method.has_fee:
            self.fee_amount = self.payment_method.calculate_fee(self.amount)
        
        self.total_amount = self.amount + self.fee_amount
        
        super().save(*args, **kwargs)

    @property
    def is_successful(self):
        """Vérifie si le paiement est réussi"""
        return self.status == 'completed'

    @property
    def is_pending(self):
        """Vérifie si le paiement est en attente"""
        return self.status in ['pending', 'processing']

    @property
    def can_be_refunded(self):
        """Vérifie si le paiement peut être remboursé"""
        return self.status == 'completed'