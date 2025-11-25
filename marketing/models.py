from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from accounts.models import Customer
from shop.models import Product, Category


class Coupon(models.Model):
    """
    Codes promo / bons de réduction
    """
    DISCOUNT_TYPE_CHOICES = [
        ('percentage', 'Pourcentage'),
        ('fixed', 'Montant fixe'),
    ]

    # Informations de base
    code = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Code promo"
    )
    description = models.TextField(
        blank=True,
        verbose_name="Description"
    )
    
    # Type et valeur de réduction
    discount_type = models.CharField(
        max_length=20,
        choices=DISCOUNT_TYPE_CHOICES,
        default='percentage',
        verbose_name="Type de réduction"
    )
    discount_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Valeur de la réduction"
    )
    max_discount_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        help_text="Montant maximum de réduction (pour les pourcentages)",
        verbose_name="Réduction maximum"
    )
    
    # Conditions d'utilisation
    minimum_purchase = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Montant minimum d'achat requis",
        verbose_name="Achat minimum"
    )
    
    # Limites d'utilisation
    usage_limit = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1)],
        help_text="Nombre maximum d'utilisations (vide = illimité)",
        verbose_name="Limite d'utilisation totale"
    )
    usage_limit_per_customer = models.IntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        help_text="Nombre d'utilisations par client",
        verbose_name="Limite par client"
    )
    times_used = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name="Nombre d'utilisations"
    )
    
    # Période de validité
    valid_from = models.DateTimeField(
        verbose_name="Valide à partir de"
    )
    valid_until = models.DateTimeField(
        verbose_name="Valide jusqu'à"
    )
    
    # Configuration
    is_active = models.BooleanField(
        default=True,
        verbose_name="Actif"
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
        verbose_name = "Coupon"
        verbose_name_plural = "Coupons"
        ordering = ['-created_at']

    def __str__(self):
        return self.code

    def calculate_discount(self, subtotal):
        """Calcule le montant de la réduction pour un sous-total donné"""
        if self.discount_type == 'percentage':
            discount = (subtotal * self.discount_value) / 100
            # Appliquer la limite maximale si définie
            if self.max_discount_amount:
                discount = min(discount, self.max_discount_amount)
            return discount
        else:  # fixed
            return min(self.discount_value, subtotal)

    def is_valid(self):
        """Vérifie si le coupon est valide"""
        now = timezone.now()
        
        # Vérifier si actif
        if not self.is_active:
            return False, "Ce coupon n'est plus actif"
        
        # Vérifier la période de validité
        if now < self.valid_from:
            return False, "Ce coupon n'est pas encore valide"
        
        if now > self.valid_until:
            return False, "Ce coupon a expiré"
        
        # Vérifier la limite d'utilisation
        if self.usage_limit and self.times_used >= self.usage_limit:
            return False, "Ce coupon a atteint sa limite d'utilisation"
        
        return True, "Coupon valide"

    def can_be_used_by_customer(self, customer):
        """Vérifie si le coupon peut être utilisé par ce client"""
        from orders.models import Order
        
        # Compter les utilisations par ce client
        usage_count = Order.objects.filter(
            customer=customer,
            coupon_code=self.code
        ).count()
        
        if usage_count >= self.usage_limit_per_customer:
            return False, f"Vous avez déjà utilisé ce coupon {self.usage_limit_per_customer} fois"
        
        return True, "Coupon disponible"


class CouponUsage(models.Model):
    """
    Suivi de l'utilisation des coupons
    """
    coupon = models.ForeignKey(
        Coupon,
        on_delete=models.CASCADE,
        related_name='usages',
        verbose_name="Coupon"
    )
    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name='coupon_usages',
        verbose_name="Client"
    )
    order = models.ForeignKey(
        'orders.Order',
        on_delete=models.CASCADE,
        related_name='coupon_usage',
        verbose_name="Commande"
    )
    discount_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Montant de la réduction"
    )
    used_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Utilisé le"
    )

    class Meta:
        verbose_name = "Utilisation de coupon"
        verbose_name_plural = "Utilisations de coupons"
        ordering = ['-used_at']

    def __str__(self):
        return f"{self.coupon.code} - {self.customer.full_name} - {self.used_at.strftime('%d/%m/%Y')}"


class Promotion(models.Model):
    """
    Promotions sur produits/catégories
    """
    DISCOUNT_TYPE_CHOICES = [
        ('percentage', 'Pourcentage'),
        ('fixed', 'Montant fixe'),
    ]
    
    PROMOTION_TYPE_CHOICES = [
        ('product', 'Produit spécifique'),
        ('category', 'Catégorie'),
        ('global', 'Globale (tout le site)'),
    ]

    # Informations de base
    name = models.CharField(
        max_length=200,
        verbose_name="Nom de la promotion"
    )
    description = models.TextField(
        blank=True,
        verbose_name="Description"
    )
    
    # Type de promotion
    promotion_type = models.CharField(
        max_length=20,
        choices=PROMOTION_TYPE_CHOICES,
        default='product',
        verbose_name="Type de promotion"
    )
    
    # Type et valeur de réduction
    discount_type = models.CharField(
        max_length=20,
        choices=DISCOUNT_TYPE_CHOICES,
        default='percentage',
        verbose_name="Type de réduction"
    )
    discount_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Valeur de la réduction"
    )
    
    # Cibles de la promotion
    products = models.ManyToManyField(
        Product,
        blank=True,
        related_name='promotions',
        verbose_name="Produits"
    )
    categories = models.ManyToManyField(
        Category,
        blank=True,
        related_name='promotions',
        verbose_name="Catégories"
    )
    
    # Période de validité
    valid_from = models.DateTimeField(
        verbose_name="Valide à partir de"
    )
    valid_until = models.DateTimeField(
        verbose_name="Valide jusqu'à"
    )
    
    # Configuration
    is_active = models.BooleanField(
        default=True,
        verbose_name="Active"
    )
    is_stackable = models.BooleanField(
        default=False,
        help_text="Peut être combinée avec d'autres promotions",
        verbose_name="Empilable"
    )
    priority = models.IntegerField(
        default=0,
        help_text="Priorité (plus élevé = appliqué en premier)",
        verbose_name="Priorité"
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
        verbose_name = "Promotion"
        verbose_name_plural = "Promotions"
        ordering = ['-priority', '-created_at']

    def __str__(self):
        return self.name

    def is_valid(self):
        """Vérifie si la promotion est valide"""
        now = timezone.now()
        
        if not self.is_active:
            return False
        
        if now < self.valid_from or now > self.valid_until:
            return False
        
        return True

    def calculate_discount(self, price):
        """Calcule le montant de la réduction pour un prix donné"""
        if self.discount_type == 'percentage':
            return (price * self.discount_value) / 100
        else:  # fixed
            return min(self.discount_value, price)

    def applies_to_product(self, product):
        """Vérifie si la promotion s'applique à un produit donné"""
        if self.promotion_type == 'global':
            return True
        
        if self.promotion_type == 'product':
            return self.products.filter(pk=product.pk).exists()
        
        if self.promotion_type == 'category':
            return self.categories.filter(pk=product.category.pk).exists()
        
        return False