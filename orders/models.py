"""
orders/models.py - Modèles des Commandes
=========================================

✅ FAILLE #4 CORRIGÉE : 
- Ajout du modèle OrderNumberSequence
- Suppression de la logique de génération dans Order.save()

✅ FAILLE #7 CORRIGÉE :
- Suppression de l'effet de bord dans OrderStatus.save()
- La mise à jour du statut de Order doit être explicite dans les vues/admin
"""

from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
from accounts.models import Customer, Address
from shop.models import Product, ProductVariant
import uuid


# ========================================
# NOUVEAU : SÉQUENCE DE NUMÉROS DE COMMANDE
# ========================================

class OrderNumberSequence(models.Model):
    """
    Compteur atomique pour la génération des numéros de commande.
    
    Ce modèle garantit l'unicité des numéros même en cas de
    requêtes simultanées grâce à SELECT FOR UPDATE.
    
    Un enregistrement par jour est créé automatiquement.
    """
    prefix = models.CharField(
        max_length=20,
        unique=True,
        db_index=True,
        help_text="Préfixe basé sur la date (ex: 20250119)",
        verbose_name="Préfixe"
    )
    last_number = models.IntegerField(
        default=0,
        help_text="Dernier numéro séquentiel utilisé pour ce préfixe",
        verbose_name="Dernier numéro"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Créé le"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Mis à jour le"
    )

    class Meta:
        verbose_name = "Séquence de numéro de commande"
        verbose_name_plural = "Séquences de numéros de commande"
        ordering = ['-prefix']
        indexes = [
            models.Index(fields=['prefix'], name='idx_prefix'),
        ]

    def __str__(self):
        return f"{self.prefix} - Dernier: {self.last_number}"


# ========================================
# MODÈLES DE LIVRAISON
# ========================================

class ShippingZone(models.Model):
    """
    Zones géographiques de livraison au Gabon
    """
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Nom de la zone"
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
    
    # Zones couvertes (villes/quartiers séparés par des virgules)
    covered_cities = models.TextField(
        help_text="Liste des villes/quartiers couverts (séparés par des virgules). Ex: Libreville, Owendo, Akanda",
        verbose_name="Villes couvertes"
    )
    
    # Configuration
    is_active = models.BooleanField(
        default=True,
        verbose_name="Zone active"
    )
    display_order = models.IntegerField(
        default=0,
        verbose_name="Ordre d'affichage"
    )
    
    # Délais de livraison (en jours ouvrables)
    standard_delivery_days_min = models.IntegerField(
        default=2,
        validators=[MinValueValidator(1)],
        verbose_name="Délai standard minimum (jours)"
    )
    standard_delivery_days_max = models.IntegerField(
        default=5,
        validators=[MinValueValidator(1)],
        verbose_name="Délai standard maximum (jours)"
    )
    express_delivery_days_min = models.IntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        verbose_name="Délai express minimum (jours)"
    )
    express_delivery_days_max = models.IntegerField(
        default=2,
        validators=[MinValueValidator(1)],
        verbose_name="Délai express maximum (jours)"
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
        verbose_name = "Zone de livraison"
        verbose_name_plural = "Zones de livraison"
        ordering = ['display_order', 'name']

    def __str__(self):
        return self.name

    def get_cities_list(self):
        """Retourne la liste des villes couvertes"""
        return [city.strip() for city in self.covered_cities.split(',') if city.strip()]

    def is_city_covered(self, city_name):
        """Vérifie si une ville est couverte par cette zone"""
        if not city_name:
            return False
        city_name_lower = city_name.lower().strip()
        cities = self.get_cities_list()
        return any(city.lower() == city_name_lower for city in cities)


class ShippingRate(models.Model):
    """
    Tarifs de livraison par zone et type
    """
    DELIVERY_TYPE_CHOICES = [
        ('standard', 'Livraison Standard'),
        ('express', 'Livraison Express'),
    ]

    zone = models.ForeignKey(
        ShippingZone,
        on_delete=models.CASCADE,
        related_name='rates',
        verbose_name="Zone de livraison"
    )
    delivery_type = models.CharField(
        max_length=20,
        choices=DELIVERY_TYPE_CHOICES,
        verbose_name="Type de livraison"
    )
    
    # Tarif
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Prix (FCFA)"
    )
    
    # Conditions (optionnel)
    min_order_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Montant minimum de commande pour bénéficier de ce tarif. 0 = aucune limite",
        verbose_name="Montant minimum de commande"
    )
    free_shipping_threshold = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        help_text="Montant à partir duquel la livraison devient gratuite. Laisser vide = jamais gratuit",
        verbose_name="Seuil livraison gratuite"
    )
    
    # Configuration
    is_active = models.BooleanField(
        default=True,
        verbose_name="Tarif actif"
    )
    
    # Dates
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Créé le"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Modifié le"
    )

    class Meta:
        verbose_name = "Tarif de livraison"
        verbose_name_plural = "Tarifs de livraison"
        unique_together = ['zone', 'delivery_type']
        ordering = ['zone__display_order', 'delivery_type']

    def __str__(self):
        return f"{self.zone.name} - {self.get_delivery_type_display()} - {self.price} FCFA"

    def calculate_shipping_cost(self, order_amount):
        """
        Calcule le coût de livraison en fonction du montant de la commande
        
        Args:
            order_amount (Decimal): Montant total de la commande
            
        Returns:
            Decimal: Coût de livraison (0 si gratuit)
        """
        # Vérifier si la commande atteint le seuil de livraison gratuite
        if self.free_shipping_threshold and order_amount >= self.free_shipping_threshold:
            return 0
        
        # Sinon, retourner le prix normal
        return self.price

    @property
    def is_free_shipping_available(self):
        """Vérifie si la livraison gratuite est disponible pour ce tarif"""
        return self.free_shipping_threshold is not None


# ========================================
# MODÈLE PRINCIPAL : ORDER
# ========================================

class Order(models.Model):
    """
    Commandes des clients
    
    ✅ FAILLE #4 CORRIGÉE :
    - order_number généré par generate_order_number() dans services.py
    - Plus de logique de génération dans save()
    """
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('processing', 'En traitement'),
        ('shipped', 'Expédié'),
        ('delivered', 'Livré'),
        ('cancelled', 'Annulé'),
        ('refunded', 'Remboursé'),
    ]

    # Identifiants
    order_number = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        verbose_name="Numéro de commande",
        help_text="Généré automatiquement par le service"
    )
    uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
        verbose_name="UUID"
    )
    
    # Client
    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name='orders',
        verbose_name="Client"
    )
    
    # Adresses (sauvegardées au moment de la commande)
    shipping_address = models.ForeignKey(
        Address,
        on_delete=models.SET_NULL,
        null=True,
        related_name='shipping_orders',
        verbose_name="Adresse de livraison"
    )
    billing_address = models.ForeignKey(
        Address,
        on_delete=models.SET_NULL,
        null=True,
        related_name='billing_orders',
        verbose_name="Adresse de facturation"
    )
    
    # Zone et tarif de livraison utilisés
    shipping_zone = models.ForeignKey(
        ShippingZone,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='orders',
        verbose_name="Zone de livraison"
    )
    shipping_rate = models.ForeignKey(
        ShippingRate,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='orders',
        verbose_name="Tarif de livraison"
    )
    delivery_type = models.CharField(
        max_length=20,
        choices=[('standard', 'Standard'), ('express', 'Express')],
        default='standard',
        verbose_name="Type de livraison"
    )
    
    # Informations de contact (sauvegardées au moment de la commande)
    customer_email = models.EmailField(verbose_name="Email client")
    customer_phone = models.CharField(max_length=17, verbose_name="Téléphone client")
    
    # Montants
    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name="Sous-total"
    )
    shipping_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name="Frais de livraison"
    )
    tax_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name="Montant des taxes"
    )
    discount_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name="Montant de la réduction"
    )
    total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name="Total"
    )
    
    # Coupon (si utilisé)
    coupon_code = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Code promo utilisé"
    )
    
    # Statut et suivi
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name="Statut"
    )
    tracking_number = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Numéro de suivi"
    )
    
    # Notes
    customer_notes = models.TextField(
        blank=True,
        verbose_name="Notes du client"
    )
    admin_notes = models.TextField(
        blank=True,
        verbose_name="Notes internes (admin)"
    )
    
    # Paiement
    is_paid = models.BooleanField(
        default=False,
        verbose_name="Payé"
    )
    paid_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Payé le"
    )
    
    # Dates
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Créée le"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Mise à jour le"
    )

    class Meta:
        verbose_name = "Commande"
        verbose_name_plural = "Commandes"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['order_number'], name='idx_order_number'),
            models.Index(fields=['customer', '-created_at'], name='idx_customer_date'),
            models.Index(fields=['status'], name='idx_status'),
        ]

    def __str__(self):
        return f"Commande {self.order_number} - {self.customer.full_name}"

    def calculate_total(self):
        """Calcule et met à jour le total de la commande"""
        self.subtotal = sum(item.subtotal for item in self.items.all())
        self.total = self.subtotal + self.shipping_cost + self.tax_amount - self.discount_amount
        self.save()

    @property
    def item_count(self):
        """Retourne le nombre total d'articles dans la commande"""
        return sum(item.quantity for item in self.items.all())

    @property
    def can_be_cancelled(self):
        """Vérifie si la commande peut être annulée"""
        return self.status in ['pending', 'processing']


class OrderItem(models.Model):
    """
    Articles dans une commande
    """
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name="Commande"
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Produit"
    )
    variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Variante"
    )
    
    # Informations figées au moment de la commande
    product_name = models.CharField(
        max_length=255,
        verbose_name="Nom du produit"
    )
    variant_details = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Détails de la variante"
    )
    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Prix unitaire"
    )
    quantity = models.IntegerField(
        validators=[MinValueValidator(1)],
        verbose_name="Quantité"
    )
    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Sous-total"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Ajouté le"
    )

    class Meta:
        verbose_name = "Article de commande"
        verbose_name_plural = "Articles de commande"

    def __str__(self):
        return f"{self.product_name} x{self.quantity}"

    def save(self, *args, **kwargs):
        """Calcule le sous-total avant la sauvegarde"""
        self.subtotal = self.unit_price * self.quantity
        super().save(*args, **kwargs)


class OrderStatus(models.Model):
    """
    Historique des changements de statut d'une commande
    
    ✅ FAILLE #7 CORRIGÉE :
    - save() ne modifie plus Order automatiquement
    - La mise à jour de Order.status doit être explicite dans le code appelant
    """
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('processing', 'En traitement'),
        ('shipped', 'Expédié'),
        ('delivered', 'Livré'),
        ('cancelled', 'Annulé'),
        ('refunded', 'Remboursé'),
    ]

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='status_history',
        verbose_name="Commande"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        verbose_name="Statut"
    )
    comment = models.TextField(
        blank=True,
        verbose_name="Commentaire"
    )
    created_by = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Créé par"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Créé le"
    )

    class Meta:
        verbose_name = "Historique de statut"
        verbose_name_plural = "Historiques de statuts"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.order.order_number} - {self.get_status_display()} - {self.created_at.strftime('%d/%m/%Y %H:%M')}"

    # ✅ FAILLE #7 CORRIGÉE : Méthode save() sans effet de bord
    # L'ancienne implémentation modifiait automatiquement Order.status
    # Maintenant, le code appelant doit explicitement mettre à jour Order