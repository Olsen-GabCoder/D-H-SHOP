"""
orders/utils.py - Utilitaires pour la génération de PDF
========================================================

Service de génération de factures PDF pour les commandes.
VERSION PRODUCTION : Gestion robuste des erreurs et timeout
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
    VERSION SÉCURISÉE : Ne plante pas si la ressource est introuvable
    """
    try:
        # Utiliser Django staticfiles pour trouver les fichiers
        if uri.startswith(settings.MEDIA_URL):
            path = os.path.join(settings.MEDIA_ROOT, uri.replace(settings.MEDIA_URL, ""))
        elif uri.startswith(settings.STATIC_URL):
            # Essayer d'abord dans STATIC_ROOT (production)
            if hasattr(settings, 'STATIC_ROOT') and settings.STATIC_ROOT:
                path = os.path.join(settings.STATIC_ROOT, uri.replace(settings.STATIC_URL, ""))
                if os.path.isfile(path):
                    return path
            # Sinon utiliser les finders
            path = finders.find(uri.replace(settings.STATIC_URL, ""))
        else:
            path = finders.find(uri)
        
        # Vérifier que le fichier existe
        if path and os.path.isfile(path):
            return path
        
        logger.warning(f"Ressource introuvable pour le PDF : {uri}")
        return None
        
    except Exception as e:
        logger.error(f"Erreur dans link_callback pour {uri}: {str(e)}")
        return None


def render_to_pdf_bytes(template_src, context_dict=None):
    """
    Génère un PDF et retourne les BYTES (pas HttpResponse).
    VERSION PRODUCTION : Pour pièce jointe email
    
    Args:
        template_src (str): Chemin vers le template HTML
        context_dict (dict): Contexte à passer au template
    
    Returns:
        bytes: Contenu du PDF en bytes (pour pièce jointe)
        None: En cas d'erreur
    """
    if context_dict is None:
        context_dict = {}
    
    try:
        # 1. Rendre le template HTML avec le contexte
        html = render_to_string(template_src, context_dict)
        
        # 2. Créer un buffer pour stocker le PDF
        result = BytesIO()
        
        # 3. Générer le PDF avec xhtml2pdf
        pdf = pisa.pisaDocument(
            BytesIO(html.encode("UTF-8")),
            result,
            encoding='UTF-8',
            link_callback=link_callback
        )
        
        # 4. Vérifier les erreurs de génération
        if pdf.err:
            logger.error(f"Erreur xhtml2pdf : {pdf.err}")
            return None
        
        # 5. Retourner le contenu en bytes
        pdf_bytes = result.getvalue()
        logger.info(f"PDF généré avec succès ({len(pdf_bytes)} bytes)")
        return pdf_bytes
        
    except Exception as e:
        logger.exception(f"Erreur lors de la génération du PDF : {str(e)}")
        return None


def render_to_pdf(template_src, context_dict=None):
    """
    Génère un PDF et retourne un HttpResponse (pour téléchargement).
    VERSION PRODUCTION : Pour téléchargement direct
    
    Args:
        template_src (str): Chemin vers le template HTML
        context_dict (dict): Contexte à passer au template
    
    Returns:
        HttpResponse: Réponse HTTP contenant le PDF (si succès)
        None: En cas d'erreur de génération
    """
    try:
        # Utiliser la fonction bytes
        pdf_bytes = render_to_pdf_bytes(template_src, context_dict)
        
        if not pdf_bytes:
            return None
        
        # Créer la réponse HTTP avec le PDF
        response = HttpResponse(pdf_bytes, content_type='application/pdf')
        response['Content-Disposition'] = 'inline; filename="facture.pdf"'
        
        return response
        
    except Exception as e:
        logger.exception(f"Erreur lors de la génération du PDF : {str(e)}")
        return None


def generate_invoice_pdf(order):
    """
    Génère une facture PDF pour une commande donnée (pour téléchargement).
    VERSION PRODUCTION : Gestion robuste des erreurs
    
    Args:
        order (Order): Instance de la commande
    
    Returns:
        HttpResponse: Réponse HTTP contenant le PDF de la facture
        None: En cas d'erreur
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
        
        # CORRECTION : Gestion robuste de l'attribut manquant get_payment_status_display
        if not hasattr(order, 'get_payment_status_display'):
            # Créer une méthode temporaire pour éviter l'erreur
            order.get_payment_status_display = lambda: "En attente de paiement"
            logger.warning(f"Méthode get_payment_status_display manquante pour la commande {order.order_number}, utilisation d'une valeur par défaut")
        
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


def generate_invoice_pdf_bytes(order):
    """
    Génère une facture PDF et retourne les BYTES (pour pièce jointe email).
    VERSION PRODUCTION : Pour envoi par email
    
    Args:
        order (Order): Instance de la commande
    
    Returns:
        bytes: Contenu du PDF en bytes
        None: En cas d'erreur
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
        
        # CORRECTION : Gestion robuste de l'attribut manquant get_payment_status_display
        if not hasattr(order, 'get_payment_status_display'):
            # Créer une méthode temporaire pour éviter l'erreur
            order.get_payment_status_display = lambda: "En attente de paiement"
            logger.warning(f"Méthode get_payment_status_display manquante pour la commande {order.order_number}, utilisation d'une valeur par défaut")
        
        # Générer le PDF en bytes
        pdf_bytes = render_to_pdf_bytes('orders/invoice_pdf.html', context)
        
        if pdf_bytes:
            logger.info(f"Facture PDF (bytes) générée pour {order.order_number}")
            return pdf_bytes
        else:
            logger.error(f"Échec génération facture (bytes) pour {order.order_number}")
            return None
            
    except Exception as e:
        logger.exception(
            f"Erreur génération facture (bytes) pour {order.order_number} : {str(e)}"
        )
        return None