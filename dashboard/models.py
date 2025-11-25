"""
Dashboard Models - Modèles pour le tableau de bord administrateur

Ce fichier contient des modèles optionnels pour étendre les fonctionnalités
du dashboard : logs d'actions admin, statistiques sauvegardées, rapports, etc.

Pour l'instant, le dashboard fonctionne sans modèles dédiés car il utilise
directement les modèles existants (Order, Product, Customer, Payment).
"""
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal


class DashboardSnapshot(models.Model):
    """
    Sauvegarde des statistiques du dashboard à un moment donné
    
    Permet de :
    - Comparer les performances dans le temps
    - Générer des rapports historiques
    - Analyser les tendances
    """
    
    # Date et heure du snapshot
    snapshot_date = models.DateTimeField(default=timezone.now, db_index=True)
    created_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True,
        related_name='dashboard_snapshots'
    )
    
    # Statistiques commandes
    total_orders = models.IntegerField(default=0)
    orders_today = models.IntegerField(default=0)
    orders_month = models.IntegerField(default=0)
    pending_orders = models.IntegerField(default=0)
    
    # Statistiques financières
    total_revenue = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=Decimal('0.00')
    )
    revenue_today = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=Decimal('0.00')
    )
    revenue_month = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=Decimal('0.00')
    )
    avg_order_value = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=Decimal('0.00')
    )
    
    # Statistiques produits
    total_products = models.IntegerField(default=0)
    out_of_stock = models.IntegerField(default=0)
    total_items_sold = models.IntegerField(default=0)
    
    # Statistiques clients
    total_customers = models.IntegerField(default=0)
    new_customers_month = models.IntegerField(default=0)
    active_customers = models.IntegerField(default=0)
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, help_text="Notes optionnelles sur ce snapshot")
    
    class Meta:
        verbose_name = "Snapshot Dashboard"
        verbose_name_plural = "Snapshots Dashboard"
        ordering = ['-snapshot_date']
        indexes = [
            models.Index(fields=['-snapshot_date']),
        ]
    
    def __str__(self):
        return f"Snapshot du {self.snapshot_date.strftime('%d/%m/%Y %H:%M')}"
    
    @classmethod
    def create_snapshot(cls, user=None):
        """
        Crée un snapshot des statistiques actuelles
        
        Usage:
            DashboardSnapshot.create_snapshot(user=request.user)
        """
        from orders.models import Order
        from shop.models import Product
        from accounts.models import Customer
        
        today = timezone.now()
        start_of_today = today.replace(hour=0, minute=0, second=0, microsecond=0)
        start_of_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        snapshot = cls.objects.create(
            created_by=user,
            snapshot_date=today,
            
            # Commandes
            total_orders=Order.objects.count(),
            orders_today=Order.objects.filter(created_at__gte=start_of_today).count(),
            orders_month=Order.objects.filter(created_at__gte=start_of_month).count(),
            pending_orders=Order.objects.filter(
                status__in=['pending', 'processing']
            ).count(),
            
            # Finances
            total_revenue=Order.objects.filter(
                is_paid=True
            ).aggregate(total=models.Sum('total'))['total'] or Decimal('0.00'),
            
            revenue_today=Order.objects.filter(
                is_paid=True,
                paid_at__gte=start_of_today
            ).aggregate(total=models.Sum('total'))['total'] or Decimal('0.00'),
            
            revenue_month=Order.objects.filter(
                is_paid=True,
                paid_at__gte=start_of_month
            ).aggregate(total=models.Sum('total'))['total'] or Decimal('0.00'),
            
            # Produits
            total_products=Product.objects.filter(is_active=True).count(),
            out_of_stock=Product.objects.filter(
                variants__stock__available_quantity=0
            ).distinct().count(),
            
            # Clients
            total_customers=Customer.objects.count(),
            new_customers_month=Customer.objects.filter(
                created_at__gte=start_of_month
            ).count(),
            active_customers=Customer.objects.filter(
                orders__isnull=False
            ).distinct().count(),
        )
        
        return snapshot


class AdminActivityLog(models.Model):
    """
    Journal des actions administratives importantes
    
    Trace les actions critiques effectuées dans le dashboard :
    - Modification de commandes
    - Gestion des stocks
    - Actions sur les clients
    - Changements de configuration
    """
    
    ACTION_TYPES = [
        ('order_edit', 'Modification de commande'),
        ('order_cancel', 'Annulation de commande'),
        ('order_refund', 'Remboursement'),
        ('stock_update', 'Mise à jour stock'),
        ('product_edit', 'Modification produit'),
        ('customer_edit', 'Modification client'),
        ('settings_change', 'Changement configuration'),
        ('export_data', 'Export de données'),
        ('other', 'Autre'),
    ]
    
    # Qui et quand
    user = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True,
        related_name='admin_activities'
    )
    action_date = models.DateTimeField(default=timezone.now, db_index=True)
    
    # Quelle action
    action_type = models.CharField(max_length=50, choices=ACTION_TYPES, db_index=True)
    action_description = models.TextField(
        help_text="Description détaillée de l'action effectuée"
    )
    
    # Sur quel objet
    object_type = models.CharField(
        max_length=50, 
        blank=True,
        help_text="Type d'objet concerné (Order, Product, etc.)"
    )
    object_id = models.IntegerField(
        null=True, 
        blank=True,
        help_text="ID de l'objet concerné"
    )
    
    # Contexte technique
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=255, blank=True)
    
    # Données avant/après (optionnel, pour traçabilité complète)
    data_before = models.JSONField(
        null=True, 
        blank=True,
        help_text="État de l'objet avant modification (JSON)"
    )
    data_after = models.JSONField(
        null=True, 
        blank=True,
        help_text="État de l'objet après modification (JSON)"
    )
    
    class Meta:
        verbose_name = "Log d'activité admin"
        verbose_name_plural = "Logs d'activité admin"
        ordering = ['-action_date']
        indexes = [
            models.Index(fields=['-action_date']),
            models.Index(fields=['user', '-action_date']),
            models.Index(fields=['action_type', '-action_date']),
        ]
    
    def __str__(self):
        return f"{self.get_action_type_display()} - {self.user} - {self.action_date.strftime('%d/%m/%Y %H:%M')}"
    
    @classmethod
    def log_action(cls, user, action_type, description, object_type=None, 
                   object_id=None, request=None, data_before=None, data_after=None):
        """
        Enregistre une action administrative
        
        Usage:
            AdminActivityLog.log_action(
                user=request.user,
                action_type='order_edit',
                description='Changement de statut de la commande #12345',
                object_type='Order',
                object_id=12345,
                request=request
            )
        """
        ip_address = None
        user_agent = None
        
        if request:
            ip_address = cls._get_client_ip(request)
            user_agent = request.META.get('HTTP_USER_AGENT', '')[:255]
        
        return cls.objects.create(
            user=user,
            action_type=action_type,
            action_description=description,
            object_type=object_type,
            object_id=object_id,
            ip_address=ip_address,
            user_agent=user_agent,
            data_before=data_before,
            data_after=data_after,
        )
    
    @staticmethod
    def _get_client_ip(request):
        """Récupère l'IP réelle du client"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class DashboardAlert(models.Model):
    """
    Alertes personnalisables du dashboard
    
    Permet de configurer des alertes personnalisées basées sur des seuils :
    - Stock minimum atteint
    - Nombre de commandes en attente
    - Baisse du CA
    - Etc.
    """
    
    ALERT_TYPES = [
        ('stock_low', 'Stock faible'),
        ('stock_out', 'Rupture de stock'),
        ('orders_pending', 'Commandes en attente'),
        ('revenue_drop', 'Baisse du CA'),
        ('customer_inactive', 'Clients inactifs'),
        ('payment_failed', 'Paiements échoués'),
        ('custom', 'Alerte personnalisée'),
    ]
    
    SEVERITY_LEVELS = [
        ('info', 'Information'),
        ('warning', 'Avertissement'),
        ('danger', 'Critique'),
    ]
    
    # Configuration de l'alerte
    alert_type = models.CharField(max_length=50, choices=ALERT_TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    severity = models.CharField(
        max_length=20, 
        choices=SEVERITY_LEVELS, 
        default='info'
    )
    
    # Seuils (optionnels selon le type)
    threshold_value = models.IntegerField(
        null=True, 
        blank=True,
        help_text="Valeur seuil qui déclenche l'alerte"
    )
    
    # État
    is_active = models.BooleanField(default=True)
    is_resolved = models.BooleanField(default=False)
    
    # Notifications
    notify_by_email = models.BooleanField(
        default=False,
        help_text="Envoyer une notification par email"
    )
    email_recipients = models.TextField(
        blank=True,
        help_text="Emails des destinataires (un par ligne)"
    )
    
    # Dates
    triggered_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    last_checked = models.DateTimeField(default=timezone.now)
    
    class Meta:
        verbose_name = "Alerte Dashboard"
        verbose_name_plural = "Alertes Dashboard"
        ordering = ['-triggered_at']
        indexes = [
            models.Index(fields=['is_active', 'is_resolved', '-triggered_at']),
        ]
    
    def __str__(self):
        return f"[{self.get_severity_display()}] {self.title}"
    
    def resolve(self):
        """Marque l'alerte comme résolue"""
        self.is_resolved = True
        self.resolved_at = timezone.now()
        self.save(update_fields=['is_resolved', 'resolved_at'])
    
    def check_condition(self):
        """
        Vérifie si la condition de l'alerte est toujours vraie
        À implémenter selon les besoins
        """
        self.last_checked = timezone.now()
        self.save(update_fields=['last_checked'])

