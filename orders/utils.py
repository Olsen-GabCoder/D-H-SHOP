"""
orders/utils.py - Utilitaires pour la génération de PDF
========================================================

Service de génération de factures PDF pour les commandes.
Utilise xhtml2pdf pour convertir des templates HTML en PDF.
"""

import logging
import os
from io import BytesIO
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.staticfiles import finders
from xhtml2pdf import pisa

# Configuration du logger
logger = logging.getLogger(__name__)


def link_callback(uri, rel):
    """
    Callback pour résoudre les chemins des ressources statiques (images, CSS).
    
    xhtml2pdf a besoin de cette fonction pour charger correctement
    les fichiers statiques (logos, CSS) dans le PDF.
    
    Args:
        uri (str): URI de la ressource
        rel (str): URI relative
    
    Returns:
        str: Chemin absolu vers la ressource
    
    Note:
        Cette fonction est utilisée automatiquement par xhtml2pdf
        lors de la génération du PDF.
    """
    # Utiliser Django staticfiles pour trouver les fichiers
    if uri.startswith(settings.MEDIA_URL):
        path = os.path.join(settings.MEDIA_ROOT, uri.replace(settings.MEDIA_URL, ""))
    elif uri.startswith(settings.STATIC_URL):
        path = os.path.join(settings.STATIC_ROOT, uri.replace(settings.STATIC_URL, ""))
        if not os.path.isfile(path):
            path = finders.find(uri.replace(settings.STATIC_URL, ""))
    else:
        path = finders.find(uri)
    
    # Vérifier que le fichier existe
    if not path or not os.path.isfile(path):
        logger.warning(f"Ressource introuvable pour le PDF : {uri}")
        return uri
    
    return path


def render_to_pdf(template_src, context_dict=None):
    """
    Génère un PDF à partir d'un template HTML.
    
    Cette fonction utilise xhtml2pdf pour convertir un template Django
    en document PDF. Elle gère automatiquement le rendu du template
    et la conversion en PDF.
    
    Args:
        template_src (str): Chemin vers le template HTML
        context_dict (dict): Contexte à passer au template
    
    Returns:
        HttpResponse: Réponse HTTP contenant le PDF (si succès)
        None: En cas d'erreur de génération
    
    Exemple:
        >>> context = {'order': order, 'company': settings.SHOP_NAME}
        >>> pdf = render_to_pdf('orders/invoice_pdf.html', context)
    """
    if context_dict is None:
        context_dict = {}
    
    try:
        # 1. Rendre le template HTML avec le contexte
        html = render_to_string(template_src, context_dict)
        
        # 2. Créer un buffer pour stocker le PDF
        result = BytesIO()
        
        # 3. Générer le PDF avec xhtml2pdf - AJOUT DU link_callback
        pdf = pisa.pisaDocument(
            BytesIO(html.encode("UTF-8")),
            result,
            encoding='UTF-8',
            link_callback=link_callback  # IMPORTANT: Ajout du callback
        )
        
        # 4. Vérifier les erreurs de génération
        if pdf.err:
            logger.error(f"Erreur lors de la génération du PDF : {pdf.err}")
            return None
        
        # 5. Créer la réponse HTTP avec le PDF
        response = HttpResponse(result.getvalue(), content_type='application/pdf')
        
        # 6. Définir le nom du fichier pour le téléchargement
        response['Content-Disposition'] = 'inline; filename="facture.pdf"'
        
        logger.info(f"PDF généré avec succès depuis le template {template_src}")
        return response
        
    except Exception as e:
        logger.exception(f"Erreur lors de la génération du PDF : {str(e)}")
        return None


def generate_invoice_pdf(order):
    """
    Génère une facture PDF pour une commande donnée.
    
    Fonction de haut niveau qui prépare le contexte complet
    pour une facture de commande et génère le PDF.
    
    Args:
        order (Order): Instance de la commande
    
    Returns:
        HttpResponse: Réponse HTTP contenant le PDF de la facture
        None: En cas d'erreur
    
    Exemple:
        >>> order = Order.objects.get(order_number='ORD-20250124-0001')
        >>> pdf_response = generate_invoice_pdf(order)
        >>> if pdf_response:
        >>>     return pdf_response
    """
    try:
        # Préparer le contexte pour le template
        context = {
            'order': order,
            'items': order.items.select_related('product', 'variant'),
            
            # Informations de la boutique (depuis settings)
            'shop_name': getattr(settings, 'SHOP_NAME', 'Mon Commerce'),
            'shop_email': getattr(settings, 'SHOP_EMAIL', 'contact@commerce.ga'),
            'shop_phone': getattr(settings, 'SHOP_PHONE', '+241 XX XX XX XX'),
            'shop_address': getattr(settings, 'SHOP_ADDRESS', 'Adresse du commerce'),
            'shop_website': getattr(settings, 'SHOP_WEBSITE', 'www.commerce.ga'),
            
            # Informations supplémentaires
            'page_title': f'Facture {order.order_number}',
        }
        
        # Générer le PDF
        pdf_response = render_to_pdf('orders/invoice_pdf.html', context)
        
        if pdf_response:
            # Définir le nom de fichier personnalisé
            filename = f'Facture_{order.order_number}.pdf'
            pdf_response['Content-Disposition'] = f'attachment; filename="{filename}"'
            
            logger.info(f"Facture PDF générée pour la commande {order.order_number}")
            return pdf_response
        else:
            logger.error(f"Échec de génération de la facture pour {order.order_number}")
            return None
            
    except Exception as e:
        logger.exception(
            f"Erreur lors de la génération de la facture pour {order.order_number} : {str(e)}"
        )
        return None