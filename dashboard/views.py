"""
Dashboard Views - Vues pour le tableau de bord administrateur
Prêt pour la production avec gestion d'erreurs complète
"""
from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Sum, Count, Q, F, Avg
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
import logging

# Import des modèles
from orders.models import Order, OrderItem
from shop.models import Product, Category
from accounts.models import Customer
from payments.models import Payment

logger = logging.getLogger(__name__)


@staff_member_required
def dashboard_view(request):
    """
    Vue principale du dashboard administrateur
    
    Affiche toutes les statistiques principales :
    - Statistiques de ventes et revenus
    - Statistiques produits
    - Statistiques clients
    - Graphiques temporels
    - Dernières commandes et alertes
    
    Prêt pour la production avec gestion complète des erreurs
    """
    try:
        # ========================================
        # DÉFINITION DES PÉRIODES D'ANALYSE
        # ========================================
        today = timezone.now()
        start_of_today = today.replace(hour=0, minute=0, second=0, microsecond=0)
        start_of_week = today - timedelta(days=today.weekday())
        start_of_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        start_of_year = today.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # ========================================
        # STATISTIQUES COMMANDES
        # ========================================
        
        # Comptage des commandes
        total_orders = Order.objects.count()
        orders_today = Order.objects.filter(created_at__gte=start_of_today).count()
        orders_week = Order.objects.filter(created_at__gte=start_of_week).count()
        orders_month = Order.objects.filter(created_at__gte=start_of_month).count()
        
        # Commandes en attente (nécessitent une action)
        pending_orders = Order.objects.filter(
            status__in=['pending', 'processing']
        ).count()
        
        # Répartition des commandes par statut
        orders_by_status = Order.objects.values('status').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # ========================================
        # STATISTIQUES FINANCIÈRES
        # ========================================
        
        # Chiffre d'affaires total (commandes payées uniquement)
        total_revenue = Order.objects.filter(
            is_paid=True
        ).aggregate(total=Sum('total'))['total'] or Decimal('0.00')
        
        # CA par période
        revenue_today = Order.objects.filter(
            is_paid=True,
            paid_at__gte=start_of_today
        ).aggregate(total=Sum('total'))['total'] or Decimal('0.00')
        
        revenue_week = Order.objects.filter(
            is_paid=True,
            paid_at__gte=start_of_week
        ).aggregate(total=Sum('total'))['total'] or Decimal('0.00')
        
        revenue_month = Order.objects.filter(
            is_paid=True,
            paid_at__gte=start_of_month
        ).aggregate(total=Sum('total'))['total'] or Decimal('0.00')
        
        revenue_year = Order.objects.filter(
            is_paid=True,
            paid_at__gte=start_of_year
        ).aggregate(total=Sum('total'))['total'] or Decimal('0.00')
        
        # Panier moyen
        avg_order_value = Decimal('0.00')
        paid_orders_count = Order.objects.filter(is_paid=True).count()
        if paid_orders_count > 0:
            avg_order_value = total_revenue / paid_orders_count
        
        # ========================================
        # STATISTIQUES PRODUITS
        # ========================================
        
        # Comptage des produits
        total_products = Product.objects.filter(is_active=True).count()
        
        # Produits en rupture de stock
        out_of_stock = Product.objects.filter(
            variants__stock__available_quantity=0,
            is_active=True
        ).distinct().count()
        
        # Produits avec stock faible (< 10)
        low_stock = Product.objects.filter(
            variants__stock__available_quantity__lt=10,
            variants__stock__available_quantity__gt=0,
            is_active=True
        ).distinct().count()
        
        # Top 5 produits les plus vendus
        top_products = Product.objects.filter(
            is_active=True
        ).order_by('-sales_count')[:5]
        
        # Total articles vendus
        total_items_sold = OrderItem.objects.filter(
            order__is_paid=True
        ).aggregate(total=Sum('quantity'))['total'] or 0
        
        # ========================================
        # STATISTIQUES CLIENTS
        # ========================================
        
        # Comptage des clients
        total_customers = Customer.objects.count()
        
        # Nouveaux clients du mois
        new_customers_month = Customer.objects.filter(
            created_at__gte=start_of_month
        ).count()
        
        # Clients ayant passé au moins une commande
        active_customers = Customer.objects.filter(
            orders__isnull=False
        ).distinct().count()
        
        # Clients VIP (3+ commandes)
        vip_customers = Customer.objects.annotate(
            order_count=Count('orders')
        ).filter(order_count__gte=3).count()
        
        # Top 5 clients par dépenses
        top_customers = Customer.objects.annotate(
            total_spent_calc=Sum(
                'orders__total',
                filter=Q(orders__is_paid=True)
            )
        ).filter(
            total_spent_calc__isnull=False
        ).order_by('-total_spent_calc')[:5]
        
        # ========================================
        # STATISTIQUES PAIEMENTS
        # ========================================
        
        # Comptage des paiements par statut
        successful_payments = Payment.objects.filter(status='completed').count()
        pending_payments = Payment.objects.filter(status='pending').count()
        failed_payments = Payment.objects.filter(status='failed').count()
        
        # Répartition par méthode de paiement
        payments_by_method = Payment.objects.filter(
            status='completed'
        ).values('payment_method__name').annotate(
            count=Count('id'),
            total=Sum('amount')
        ).order_by('-count')
        
        # ========================================
        # DONNÉES POUR GRAPHIQUES (30 derniers jours)
        # ========================================
        
        last_30_days = []
        revenue_chart_data = []
        orders_chart_data = []
        
        for i in range(29, -1, -1):
            date = today - timedelta(days=i)
            date_start = date.replace(hour=0, minute=0, second=0, microsecond=0)
            date_end = date_start + timedelta(days=1)
            
            # CA du jour
            daily_revenue = Order.objects.filter(
                is_paid=True,
                paid_at__gte=date_start,
                paid_at__lt=date_end
            ).aggregate(total=Sum('total'))['total'] or Decimal('0.00')
            
            # Commandes du jour
            daily_orders = Order.objects.filter(
                created_at__gte=date_start,
                created_at__lt=date_end
            ).count()
            
            # Formatage pour le graphique
            last_30_days.append(date.strftime('%d/%m'))
            revenue_chart_data.append(float(daily_revenue))
            orders_chart_data.append(daily_orders)
        
        # ========================================
        # DERNIÈRES COMMANDES
        # ========================================
        
        recent_orders = Order.objects.select_related(
            'customer__user',
            'shipping_zone',
            'shipping_rate'
        ).prefetch_related(
            'items'
        ).order_by('-created_at')[:10]
        
        # ========================================
        # ALERTES ET NOTIFICATIONS
        # ========================================
        
        alerts = []
        
        # Commandes en attente
        if pending_orders > 0:
            alerts.append({
                'type': 'warning',
                'icon': 'fas fa-clock',
                'message': f'{pending_orders} commande(s) en attente de traitement',
                'url': '/admin/orders/order/?status__in=pending,processing',
                'priority': 1
            })
        
        # Produits en rupture de stock
        if out_of_stock > 0:
            alerts.append({
                'type': 'danger',
                'icon': 'fas fa-box-open',
                'message': f'{out_of_stock} produit(s) en rupture de stock',
                'url': '/admin/shop/product/',
                'priority': 2
            })
        
        # Produits avec stock faible
        if low_stock > 0:
            alerts.append({
                'type': 'warning',
                'icon': 'fas fa-exclamation-triangle',
                'message': f'{low_stock} produit(s) avec stock faible (< 10)',
                'url': '/admin/shop/product/',
                'priority': 3
            })
        
        # Paiements en attente
        if pending_payments > 0:
            alerts.append({
                'type': 'info',
                'icon': 'fas fa-credit-card',
                'message': f'{pending_payments} paiement(s) en attente de confirmation',
                'url': '/admin/payments/payment/?status=pending',
                'priority': 4
            })
        
        # Nouveaux clients
        if new_customers_month > 0:
            alerts.append({
                'type': 'success',
                'icon': 'fas fa-user-plus',
                'message': f'{new_customers_month} nouveau(x) client(s) ce mois',
                'url': '/admin/accounts/customer/',
                'priority': 5
            })
        
        # Trier les alertes par priorité
        alerts.sort(key=lambda x: x['priority'])
        
        # ========================================
        # STATISTIQUES SUPPLÉMENTAIRES
        # ========================================
        
        # Taux de conversion (commandes payées / total commandes)
        conversion_rate = 0
        if total_orders > 0:
            paid_orders = Order.objects.filter(is_paid=True).count()
            conversion_rate = round((paid_orders / total_orders) * 100, 2)
        
        # Nombre de catégories actives
        total_categories = Category.objects.filter(is_active=True).count()
        
        # ========================================
        # CONTEXTE POUR LE TEMPLATE
        # ========================================
        
        context = {
            # Meta
            'title': 'Tableau de bord',
            'dashboard_active': True,
            
            # Périodes
            'today': today,
            'start_of_month': start_of_month,
            
            # Statistiques commandes
            'total_orders': total_orders,
            'orders_today': orders_today,
            'orders_week': orders_week,
            'orders_month': orders_month,
            'pending_orders': pending_orders,
            'orders_by_status': orders_by_status,
            
            # Statistiques financières
            'total_revenue': total_revenue,
            'revenue_today': revenue_today,
            'revenue_week': revenue_week,
            'revenue_month': revenue_month,
            'revenue_year': revenue_year,
            'avg_order_value': avg_order_value,
            'conversion_rate': conversion_rate,
            
            # Statistiques produits
            'total_products': total_products,
            'total_categories': total_categories,
            'out_of_stock': out_of_stock,
            'low_stock': low_stock,
            'top_products': top_products,
            'total_items_sold': total_items_sold,
            
            # Statistiques clients
            'total_customers': total_customers,
            'new_customers_month': new_customers_month,
            'active_customers': active_customers,
            'vip_customers': vip_customers,
            'top_customers': top_customers,
            
            # Statistiques paiements
            'successful_payments': successful_payments,
            'pending_payments': pending_payments,
            'failed_payments': failed_payments,
            'payments_by_method': payments_by_method,
            
            # Données graphiques
            'last_30_days': last_30_days,
            'revenue_chart_data': revenue_chart_data,
            'orders_chart_data': orders_chart_data,
            
            # Listes
            'recent_orders': recent_orders,
            'alerts': alerts,
        }
        
        logger.info(f'Dashboard chargé avec succès pour {request.user.username}')
        return render(request, 'admin/dashboard.html', context)
        
    except Exception as e:
        # Logging de l'erreur complète
        logger.error(
            f'Erreur critique dans dashboard_view pour {request.user.username}: {str(e)}',
            exc_info=True,
            extra={
                'user': request.user.username,
                'user_id': request.user.id,
                'ip_address': request.META.get('REMOTE_ADDR'),
            }
        )
        
        # Contexte minimal en cas d'erreur
        context = {
            'title': 'Tableau de bord',
            'error_message': (
                'Une erreur est survenue lors du chargement du tableau de bord. '
                'Nos équipes techniques ont été informées. Veuillez réessayer dans quelques instants.'
            ),
            'technical_error': str(e) if request.user.is_superuser else None,
        }
        
        return render(request, 'admin/dashboard.html', context)


@staff_member_required
def dashboard_export_data(request):
    """
    Vue pour exporter les données du dashboard (optionnel)
    Format : CSV, JSON ou Excel
    """
    try:
        from django.http import JsonResponse
        
        # Récupérer le format demandé
        export_format = request.GET.get('format', 'json')
        
        # Collecter les données à exporter
        data = {
            'total_orders': Order.objects.count(),
            'total_revenue': float(
                Order.objects.filter(is_paid=True).aggregate(
                    total=Sum('total')
                )['total'] or 0
            ),
            'total_customers': Customer.objects.count(),
            'total_products': Product.objects.filter(is_active=True).count(),
            'export_date': timezone.now().isoformat(),
        }
        
        if export_format == 'json':
            return JsonResponse(data)
        
        # Autres formats possibles (CSV, Excel) peuvent être ajoutés ici
        
        return JsonResponse({'error': 'Format non supporté'}, status=400)
        
    except Exception as e:
        logger.error(f'Erreur export dashboard: {str(e)}', exc_info=True)
        return JsonResponse({'error': str(e)}, status=500)