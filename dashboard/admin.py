from django.contrib import admin
from django.urls import path
from django.shortcuts import render
from django.db.models import Sum, Count, Q, F
from django.utils import timezone
from datetime import timedelta
from orders.models import Order, OrderItem
from shop.models import Product
from accounts.models import Customer
from payments.models import Payment
import logging

logger = logging.getLogger('dashboard')


class CustomAdminSite(admin.AdminSite):
    """
    Site d'administration personnalisé avec dashboard enrichi
    """
    site_header = 'Administration E-Commerce Gabon'
    site_title = 'Admin E-Commerce'
    index_title = 'Tableau de bord'
    
    def get_urls(self):
        """Ajouter l'URL du dashboard personnalisé"""
        urls = super().get_urls()
        custom_urls = [
            path('', self.admin_view(self.dashboard_view), name='index'),
        ]
        return custom_urls + urls
    
    def dashboard_view(self, request):
        """
        Vue principale du dashboard avec statistiques complètes
        """
        try:
            # ========================================
            # PÉRIODE D'ANALYSE
            # ========================================
            today = timezone.now()
            start_of_today = today.replace(hour=0, minute=0, second=0, microsecond=0)
            start_of_week = today - timedelta(days=today.weekday())
            start_of_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            start_of_year = today.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
            
            # ========================================
            # STATISTIQUES COMMANDES
            # ========================================
            
            # Total commandes
            total_orders = Order.objects.count()
            
            # Commandes du jour
            orders_today = Order.objects.filter(created_at__gte=start_of_today).count()
            
            # Commandes de la semaine
            orders_week = Order.objects.filter(created_at__gte=start_of_week).count()
            
            # Commandes du mois
            orders_month = Order.objects.filter(created_at__gte=start_of_month).count()
            
            # Commandes par statut
            orders_by_status = Order.objects.values('status').annotate(
                count=Count('id')
            ).order_by('-count')
            
            # Commandes en attente (nécessitent attention)
            pending_orders = Order.objects.filter(
                status__in=['pending', 'processing']
            ).count()
            
            # ========================================
            # STATISTIQUES FINANCIÈRES
            # ========================================
            
            # Chiffre d'affaires total (commandes payées uniquement)
            total_revenue = Order.objects.filter(
                is_paid=True
            ).aggregate(total=Sum('total'))['total'] or 0
            
            # CA du jour
            revenue_today = Order.objects.filter(
                is_paid=True,
                paid_at__gte=start_of_today
            ).aggregate(total=Sum('total'))['total'] or 0
            
            # CA de la semaine
            revenue_week = Order.objects.filter(
                is_paid=True,
                paid_at__gte=start_of_week
            ).aggregate(total=Sum('total'))['total'] or 0
            
            # CA du mois
            revenue_month = Order.objects.filter(
                is_paid=True,
                paid_at__gte=start_of_month
            ).aggregate(total=Sum('total'))['total'] or 0
            
            # CA de l'année
            revenue_year = Order.objects.filter(
                is_paid=True,
                paid_at__gte=start_of_year
            ).aggregate(total=Sum('total'))['total'] or 0
            
            # Valeur moyenne d'une commande
            avg_order_value = Order.objects.filter(
                is_paid=True
            ).aggregate(avg=Sum('total'))['avg'] or 0
            if total_orders > 0:
                avg_order_value = total_revenue / total_orders
            
            # ========================================
            # STATISTIQUES PRODUITS
            # ========================================
            
            # Total produits
            total_products = Product.objects.filter(is_active=True).count()
            
            # Produits en rupture de stock (quantité <= quantité réservée)
            # ✅ CORRECTION : Utilisation de F() au lieu de la propriété available_quantity
            out_of_stock = Product.objects.filter(
                variants__stock__quantity__lte=F('variants__stock__reserved_quantity')
            ).distinct().count()
            
            # Produits les plus vendus (top 5)
            top_products = Product.objects.filter(
                is_active=True
            ).order_by('-sales_count')[:5]
            
            # Articles vendus (quantité totale)
            total_items_sold = OrderItem.objects.filter(
                order__is_paid=True
            ).aggregate(total=Sum('quantity'))['total'] or 0
            
            # ========================================
            # STATISTIQUES CLIENTS
            # ========================================
            
            # Total clients
            total_customers = Customer.objects.count()
            
            # Nouveaux clients du mois
            new_customers_month = Customer.objects.filter(
                created_at__gte=start_of_month
            ).count()
            
            # Clients ayant commandé
            active_customers = Customer.objects.filter(
                orders__isnull=False
            ).distinct().count()
            
            # Clients VIP (plus de 3 commandes)
            vip_customers = Customer.objects.annotate(
                order_count=Count('orders')
            ).filter(order_count__gte=3).count()
            
            # Top 5 clients (par dépenses)
            top_customers = Customer.objects.annotate(
                total_spent_calc=Sum('orders__total', filter=Q(orders__is_paid=True))
            ).order_by('-total_spent_calc')[:5]
            
            # ========================================
            # STATISTIQUES PAIEMENTS
            # ========================================
            
            # Paiements réussis
            successful_payments = Payment.objects.filter(status='completed').count()
            
            # Paiements en attente
            pending_payments = Payment.objects.filter(status='pending').count()
            
            # Paiements échoués
            failed_payments = Payment.objects.filter(status='failed').count()
            
            # Répartition par méthode de paiement
            payments_by_method = Payment.objects.filter(
                status='completed'
            ).values('payment_method__name').annotate(
                count=Count('id'),
                total=Sum('amount')
            ).order_by('-count')
            
            # ========================================
            # DONNÉES POUR GRAPHIQUES
            # ========================================
            
            # CA des 30 derniers jours (pour graphique)
            last_30_days = []
            revenue_chart_data = []
            orders_chart_data = []
            
            for i in range(29, -1, -1):
                date = today - timedelta(days=i)
                date_start = date.replace(hour=0, minute=0, second=0, microsecond=0)
                date_end = date_start + timedelta(days=1)
                
                daily_revenue = Order.objects.filter(
                    is_paid=True,
                    paid_at__gte=date_start,
                    paid_at__lt=date_end
                ).aggregate(total=Sum('total'))['total'] or 0
                
                daily_orders = Order.objects.filter(
                    created_at__gte=date_start,
                    created_at__lt=date_end
                ).count()
                
                last_30_days.append(date.strftime('%d/%m'))
                revenue_chart_data.append(float(daily_revenue))
                orders_chart_data.append(daily_orders)
            
            # ========================================
            # DERNIÈRES COMMANDES
            # ========================================
            
            recent_orders = Order.objects.select_related(
                'customer__user',
                'shipping_zone'
            ).order_by('-created_at')[:10]
            
            # ========================================
            # ALERTES ET NOTIFICATIONS
            # ========================================
            
            alerts = []
            
            # Commandes en attente de traitement
            if pending_orders > 0:
                alerts.append({
                    'type': 'warning',
                    'icon': 'fas fa-clock',
                    'message': f'{pending_orders} commande(s) en attente de traitement',
                    'url': '/admin/orders/order/?status__in=pending,processing'
                })
            
            # Produits en rupture de stock
            if out_of_stock > 0:
                alerts.append({
                    'type': 'danger',
                    'icon': 'fas fa-box-open',
                    'message': f'{out_of_stock} produit(s) en rupture de stock',
                    'url': '/admin/shop/product/'
                })
            
            # Paiements en attente
            if pending_payments > 0:
                alerts.append({
                    'type': 'info',
                    'icon': 'fas fa-credit-card',
                    'message': f'{pending_payments} paiement(s) en attente de confirmation',
                    'url': '/admin/payments/payment/?status=pending'
                })
            
            # Nouveaux clients ce mois
            if new_customers_month > 0:
                alerts.append({
                    'type': 'success',
                    'icon': 'fas fa-user-plus',
                    'message': f'{new_customers_month} nouveau(x) client(s) ce mois',
                    'url': '/admin/accounts/customer/'
                })
            
            # ========================================
            # CONTEXTE POUR LE TEMPLATE
            # ========================================
            
            context = {
                **self.each_context(request),
                
                # Commandes
                'total_orders': total_orders,
                'orders_today': orders_today,
                'orders_week': orders_week,
                'orders_month': orders_month,
                'pending_orders': pending_orders,
                'orders_by_status': orders_by_status,
                
                # Finances
                'total_revenue': total_revenue,
                'revenue_today': revenue_today,
                'revenue_week': revenue_week,
                'revenue_month': revenue_month,
                'revenue_year': revenue_year,
                'avg_order_value': avg_order_value,
                
                # Produits
                'total_products': total_products,
                'out_of_stock': out_of_stock,
                'top_products': top_products,
                'total_items_sold': total_items_sold,
                
                # Clients
                'total_customers': total_customers,
                'new_customers_month': new_customers_month,
                'active_customers': active_customers,
                'vip_customers': vip_customers,
                'top_customers': top_customers,
                
                # Paiements
                'successful_payments': successful_payments,
                'pending_payments': pending_payments,
                'failed_payments': failed_payments,
                'payments_by_method': payments_by_method,
                
                # Graphiques
                'last_30_days': last_30_days,
                'revenue_chart_data': revenue_chart_data,
                'orders_chart_data': orders_chart_data,
                
                # Divers
                'recent_orders': recent_orders,
                'alerts': alerts,
                
                # Meta
                'title': 'Tableau de bord',
            }
            
            return render(request, 'admin/dashboard.html', context)
            
        except Exception as e:
            logger.error(f'Erreur dans dashboard_view: {str(e)}', exc_info=True)
            
            # Contexte minimal en cas d'erreur
            context = {
                **self.each_context(request),
                'error_message': 'Une erreur est survenue lors du chargement du tableau de bord.',
                'title': 'Tableau de bord',
            }
            return render(request, 'admin/dashboard.html', context)


# ========================================
# CRÉER L'INSTANCE DU SITE ADMIN PERSONNALISÉ
# ========================================

# Créer une instance du site admin personnalisé
admin_site = CustomAdminSite(name='admin')


# ========================================
# ENREGISTRER TOUS LES MODÈLES SUR LE CUSTOMADMINSITE
# ========================================

# Fonction helper pour enregistrer automatiquement les modèles
def register_all_models():
    """
    Enregistre automatiquement tous les modèles depuis les autres apps
    en réutilisant leurs ModelAdmin existants
    """
    from django.contrib import admin as default_admin
    from django.apps import apps
    
    # Liste des apps à inclure
    apps_to_include = ['core', 'shop', 'orders', 'accounts', 'payments', 'marketing']
    
    for app_label in apps_to_include:
        try:
            # Importer le module admin de l'app
            app_admin_module = __import__(f'{app_label}.admin', fromlist=[''])
            
            # Récupérer tous les modèles enregistrés dans l'admin par défaut
            app_config = apps.get_app_config(app_label)
            
            for model in app_config.get_models():
                # Vérifier si le modèle est enregistré dans l'admin par défaut
                if model in default_admin.site._registry:
                    # Récupérer la classe ModelAdmin correspondante
                    model_admin_class = default_admin.site._registry[model].__class__
                    
                    # Enregistrer sur notre CustomAdminSite
                    try:
                        admin_site.register(model, model_admin_class)
                        logger.info(f'Enregistre: {app_label}.{model.__name__}')  
                    except admin.sites.AlreadyRegistered:
                        logger.debug(f'Déjà enregistré: {app_label}.{model.__name__}')
                        pass
                        
        except ImportError as e:
            logger.warning(f'Impossible d\'importer {app_label}.admin: {e}')
            continue
        except Exception as e:
            logger.error(f'Erreur lors de l\'enregistrement de {app_label}: {e}')
            continue

# Appel de la fonction d'enregistrement automatique
register_all_models()

# Enregistrer aussi les modèles Django par défaut
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin, GroupAdmin

try:
    admin_site.register(User, UserAdmin)
    admin_site.register(Group, GroupAdmin)
except admin.sites.AlreadyRegistered:
    pass