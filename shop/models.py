from django.db import models
from django.utils.text import slugify
from django.core.validators import MinValueValidator
from django.urls import reverse


class Category(models.Model):
    """
    Catégories de produits avec système hiérarchique (parent/enfant)
    """
    name = models.CharField(max_length=200, unique=True, verbose_name="Nom")
    slug = models.SlugField(max_length=200, unique=True, verbose_name="Slug")
    description = models.TextField(blank=True, verbose_name="Description")
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children',
        verbose_name="Catégorie parente"
    )
    image = models.ImageField(
        upload_to='categories/',
        blank=True,
        null=True,
        verbose_name="Image"
    )
    is_active = models.BooleanField(default=True, verbose_name="Active")
    display_order = models.IntegerField(default=0, verbose_name="Ordre d'affichage")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créée le")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Modifiée le")

    class Meta:
        verbose_name = "Catégorie"
        verbose_name_plural = "Catégories"
        ordering = ['display_order', 'name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('shop:category_detail', kwargs={'slug': self.slug})


class Product(models.Model):
    """
    Produits du catalogue
    """
    name = models.CharField(max_length=255, verbose_name="Nom du produit")
    slug = models.SlugField(max_length=255, unique=True, verbose_name="Slug")
    description = models.TextField(verbose_name="Description")
    short_description = models.CharField(
        max_length=500,
        blank=True,
        verbose_name="Description courte"
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='products',
        verbose_name="Catégorie"
    )
    
    # Prix
    base_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Prix de base"
    )
    sale_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        verbose_name="Prix en promotion"
    )
    
    # Images
    main_image = models.ImageField(
        upload_to='products/',
        verbose_name="Image principale"
    )
    
    # SEO
    meta_title = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Meta titre"
    )
    meta_description = models.CharField(
        max_length=300,
        blank=True,
        verbose_name="Meta description"
    )
    
    # Gestion
    is_active = models.BooleanField(default=True, verbose_name="Actif")
    is_featured = models.BooleanField(default=False, verbose_name="Produit phare")
    is_new = models.BooleanField(default=False, verbose_name="Nouveau produit")
    
    # Statistiques
    views_count = models.IntegerField(default=0, verbose_name="Nombre de vues")
    sales_count = models.IntegerField(default=0, verbose_name="Nombre de ventes")
    
    # Dates
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Modifié le")

    class Meta:
        verbose_name = "Produit"
        verbose_name_plural = "Produits"
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('shop:product_detail', kwargs={'slug': self.slug})

    @property
    def current_price(self):
        """Retourne le prix actuel (promo si disponible, sinon prix de base)"""
        return self.sale_price if self.sale_price else self.base_price

    @property
    def has_discount(self):
        """Vérifie si le produit est en promotion"""
        return self.sale_price is not None and self.sale_price < self.base_price

    @property
    def discount_percentage(self):
        """Calcule le pourcentage de réduction"""
        if self.has_discount:
            return int(((self.base_price - self.sale_price) / self.base_price) * 100)
        return 0


class ProductImage(models.Model):
    """
    Images supplémentaires pour un produit
    """
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name="Produit"
    )
    image = models.ImageField(upload_to='products/', verbose_name="Image")
    alt_text = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Texte alternatif"
    )
    display_order = models.IntegerField(default=0, verbose_name="Ordre d'affichage")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ajoutée le")

    class Meta:
        verbose_name = "Image produit"
        verbose_name_plural = "Images produits"
        ordering = ['display_order']

    def __str__(self):
        return f"Image {self.display_order} - {self.product.name}"


class ProductVariant(models.Model):
    """
    Variantes de produits (tailles, couleurs)
    """
    SIZE_CHOICES = [
        ('XS', 'XS'),
        ('S', 'S'),
        ('M', 'M'),
        ('L', 'L'),
        ('XL', 'XL'),
        ('XXL', 'XXL'),
        ('XXXL', 'XXXL'),
    ]

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='variants',
        verbose_name="Produit"
    )
    sku = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="SKU (code unique)"
    )
    size = models.CharField(
        max_length=10,
        choices=SIZE_CHOICES,
        blank=True,
        verbose_name="Taille"
    )
    color = models.CharField(max_length=50, blank=True, verbose_name="Couleur")
    color_code = models.CharField(
        max_length=7,
        blank=True,
        help_text="Code hexadécimal (ex: #FF5733)",
        verbose_name="Code couleur"
    )
    
    # Prix spécifique (si différent du produit principal)
    price_adjustment = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Ajustement de prix"
    )
    
    is_active = models.BooleanField(default=True, verbose_name="Active")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créée le")

    class Meta:
        verbose_name = "Variante"
        verbose_name_plural = "Variantes"
        unique_together = ['product', 'size', 'color']

    def __str__(self):
        parts = [self.product.name]
        if self.size:
            parts.append(f"Taille {self.size}")
        if self.color:
            parts.append(f"Couleur {self.color}")
        return " - ".join(parts)

    @property
    def final_price(self):
        """Prix final de la variante"""
        return self.product.current_price + self.price_adjustment


class Stock(models.Model):
    """
    Gestion des stocks par variante
    """
    variant = models.OneToOneField(
        ProductVariant,
        on_delete=models.CASCADE,
        related_name='stock',
        verbose_name="Variante"
    )
    quantity = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name="Quantité en stock"
    )
    reserved_quantity = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name="Quantité réservée"
    )
    low_stock_threshold = models.IntegerField(
        default=5,
        verbose_name="Seuil stock faible"
    )
    last_restocked = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Dernier réapprovisionnement"
    )
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Mis à jour le")

    class Meta:
        verbose_name = "Stock"
        verbose_name_plural = "Stocks"

    def __str__(self):
        return f"{self.variant} - Stock: {self.available_quantity}"

    @property
    def available_quantity(self):
        """Quantité disponible (stock - réservé)"""
        return max(0, self.quantity - self.reserved_quantity)

    @property
    def is_low_stock(self):
        """Vérifie si le stock est bas"""
        return self.available_quantity <= self.low_stock_threshold

    @property
    def is_in_stock(self):
        """Vérifie si le produit est en stock"""
        return self.available_quantity > 0