"""
Service centralisé pour l'envoi d'emails transactionnels
Version production - Configuration robuste pour environnement de production
"""

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags
import logging

# Import du service PDF
from orders.utils import generate_invoice_pdf_bytes

logger = logging.getLogger('core.email_service')


class EmailService:
    """
    Service centralisé pour gérer l'envoi d'emails transactionnels
    Version production - Gestion robuste des erreurs et logs détaillés
    """
    
    @staticmethod
    def _get_from_email():
        """
        Retourne l'email de l'expéditeur correctement formaté
        CORRIGÉ : Utilise la configuration Django sans double formatage
        """
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@commerce.ga')
        from_name = getattr(settings, 'DEFAULT_FROM_NAME', 'Mon Commerce')
        
        # Si l'email contient déjà un format nom <email>, on le retourne tel quel
        if '<' in from_email and '>' in from_email:
            return from_email
        
        # Sinon, on formate correctement
        return f"{from_name} <{from_email}>"
    
    @staticmethod
    def _get_shop_context():
        """
        Retourne le contexte standard de la boutique pour les templates
        """
        return {
            'shop_name': getattr(settings, 'SHOP_NAME', 'D&H-SHOP'),
            'shop_email': getattr(settings, 'SHOP_EMAIL', 'contact@dh-shop.tg'),
            'shop_phone': getattr(settings, 'SHOP_PHONE', '+228 XX XX XX XX'),
            'shop_address': getattr(settings, 'SHOP_ADDRESS', 'Libreville, Gabon'),
            'shop_website': getattr(settings, 'SHOP_WEBSITE', 'http://localhost:8000'),
            'shop_logo_url': getattr(settings, 'SHOP_LOGO_URL', ''),
            'social_facebook': getattr(settings, 'SOCIAL_FACEBOOK', ''),
            'social_instagram': getattr(settings, 'SOCIAL_INSTAGRAM', ''),
            'social_twitter': getattr(settings, 'SOCIAL_TWITTER', ''),
        }
    
    @staticmethod
    def send_email(subject, template_name, context, recipient_list, fail_silently=False, attachment=None):
        """
        Méthode générique pour envoyer un email avec template HTML et texte
        VERSION CORRIGÉE : Gestion correcte du retour SMTP et logs détaillés
        """
        try:
            # Ajouter les informations de la boutique au contexte
            context.update(EmailService._get_shop_context())
            
            # Render HTML et texte
            html_content = render_to_string(f'emails/{template_name}.html', context)
            text_content = strip_tags(html_content)  # Version texte simple
            
            # Créer l'email avec l'expéditeur correctement formaté
            from_email = EmailService._get_from_email()
            
            email = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=from_email,
                to=recipient_list
            )
            email.attach_alternative(html_content, "text/html")
            
            # Gestion de la pièce jointe
            if attachment:
                # attachment doit être un tuple (filename, content, mimetype)
                email.attach(*attachment)
            
            # Logs détaillés pour le diagnostic
            logger.info("Tentative d'envoi email: %s à %s", subject, recipient_list)
            logger.info("From: %s, Template: %s", from_email, template_name)
            logger.info("Paramètres SMTP: HOST=%s, PORT=%s, USER=%s, TLS=%s, SSL=%s", 
                       settings.EMAIL_HOST, settings.EMAIL_PORT, settings.EMAIL_HOST_USER, 
                       settings.EMAIL_USE_TLS, settings.EMAIL_USE_SSL)
            
            # CORRECTION CRITIQUE : Vérifier le vrai résultat d'envoi
            result = email.send(fail_silently=fail_silently)
            
            # CORRECTION : Vérifier que l'email est bien envoyé (result == 1)
            if result == 1:
                logger.info("Email envoyé avec succès: %s à %s", subject, recipient_list)
                return True
            else:
                logger.error("Échec envoi email: %s à %s - Résultat SMTP: %s", subject, recipient_list, result)
                return False
            
        except Exception as e:
            logger.error("Erreur lors de l'envoi de l'email: %s", str(e), exc_info=True)
            if not fail_silently:
                raise
            return False
    
    @staticmethod
    def send_order_confirmation(order):
        """
        Envoie un email de confirmation de commande AVEC FACTURE PDF
        VERSION CORRIGÉE : Utilise generate_invoice_pdf_bytes() pour éviter le timeout
        """
        try:
            logger.info("Début envoi confirmation commande: %s", order.order_number)
            
            subject = f"Confirmation de commande #{order.order_number}"
            
            # Préparer le contexte avec les relations nécessaires
            context = {
                'order': order,
                'customer': order.customer,
                'items': order.items.all(),
                'shipping_address': order.shipping_address,
            }
            
            # Vérifier que le template existe
            try:
                template_content = render_to_string('emails/order_confirmation.html', context)
                logger.info("Template chargé, taille: %s caractères", len(template_content))
            except Exception as template_error:
                logger.error("Erreur chargement template: %s", template_error)
                # Continuer malgré l'erreur de template pour ne pas bloquer la commande
            
            # Génération PDF non-bloquante
            attachment = None
            try:
                # Utiliser la fonction bytes directement (pas de HttpResponse)
                pdf_bytes = generate_invoice_pdf_bytes(order)
                
                if pdf_bytes:
                    filename = f"Facture_{order.order_number}.pdf"
                    attachment = (filename, pdf_bytes, 'application/pdf')
                    logger.info("Facture PDF générée (bytes): %s (%d bytes)", filename, len(pdf_bytes))
                else:
                    logger.warning("Aucun contenu PDF généré pour la commande %s", order.order_number)
                    
            except Exception as pdf_error:
                logger.error("Erreur génération PDF: %s", pdf_error, exc_info=True)
                # Continuer sans PDF - ne pas bloquer l'envoi de l'email
            
            # Envoyer l'email (avec ou sans PDF)
            result = EmailService.send_email(
                subject=subject,
                template_name='order_confirmation',
                context=context,
                recipient_list=[order.customer_email],
                fail_silently=True,
                attachment=attachment
            )
            
            if result:
                logger.info("Email de confirmation envoyé avec succès pour %s", order.order_number)
            else:
                logger.error("Échec de l'envoi d'email pour %s", order.order_number)
            
            return result
            
        except Exception as e:
            logger.error("Erreur critique dans send_order_confirmation: %s", str(e), exc_info=True)
            return False
    
    @staticmethod
    def send_order_shipped(order):
        """
        Envoie un email de notification d'expédition
        
        Args:
            order: Instance du modèle Order
            
        Returns:
            bool: True si envoyé avec succès
        """
        subject = f"Votre commande #{order.order_number} a été expédiée"
        context = {
            'order': order,
            'customer': order.customer,
            'tracking_number': order.tracking_number,
        }
        
        return EmailService.send_email(
            subject=subject,
            template_name='order_shipped',
            context=context,
            recipient_list=[order.customer_email],
            fail_silently=True
        )
    
    @staticmethod
    def send_welcome_email(user):
        """
        Envoie un email de bienvenue après inscription
        
        Args:
            user: Instance du modèle User
            
        Returns:
            bool: True si envoyé avec succès
        """
        subject = f"Bienvenue sur {getattr(settings, 'SHOP_NAME', 'D&H-SHOP')} !"
        context = {
            'user': user,
            'customer': user.customer if hasattr(user, 'customer') else None,
        }
        
        return EmailService.send_email(
            subject=subject,
            template_name='welcome',
            context=context,
            recipient_list=[user.email],
            fail_silently=True
        )
    
    @staticmethod
    def send_password_reset(user, reset_url):
        """
        Envoie un email de réinitialisation de mot de passe
        
        Args:
            user: Instance du modèle User
            reset_url: URL de réinitialisation
            
        Returns:
            bool: True si envoyé avec succès
        """
        subject = "Réinitialisation de votre mot de passe"
        context = {
            'user': user,
            'reset_url': reset_url,
        }
        
        return EmailService.send_email(
            subject=subject,
            template_name='password_reset',
            context=context,
            recipient_list=[user.email],
            fail_silently=True
        )
    
    @staticmethod
    def send_order_cancelled(order):
        """
        Envoie un email de notification d'annulation
        
        Args:
            order: Instance du modèle Order
            
        Returns:
            bool: True si envoyé avec succès
        """
        subject = f"Commande #{order.order_number} annulée"
        context = {
            'order': order,
            'customer': order.customer,
        }
        
        return EmailService.send_email(
            subject=subject,
            template_name='order_cancelled',
            context=context,
            recipient_list=[order.customer_email],
            fail_silently=True
        )
    
    @staticmethod
    def send_payment_confirmation(order):
        """
        Envoie un email de confirmation de paiement
        
        Args:
            order: Instance du modèle Order
            
        Returns:
            bool: True si envoyé avec succès
        """
        subject = f"Paiement confirmé pour la commande #{order.order_number}"
        context = {
            'order': order,
            'customer': order.customer,
        }
        
        return EmailService.send_email(
            subject=subject,
            template_name='payment_confirmation',
            context=context,
            recipient_list=[order.customer_email],
            fail_silently=True
        )
    
    @staticmethod
    def send_contact_form(subject, message, from_email, recipient_list=None):
        """
        Envoie un email depuis le formulaire de contact
        
        Args:
            subject (str): Sujet du message
            message (str): Contenu du message
            from_email (str): Email de l'expéditeur
            recipient_list (list): Liste des destinataires (par défaut l'email de la boutique)
            
        Returns:
            bool: True si envoyé avec succès
        """
        if recipient_list is None:
            recipient_list = [getattr(settings, 'SHOP_EMAIL', 'contact@dh-shop.tg')]
            
        context = {
            'subject': subject,
            'message': message,
            'from_email': from_email,
        }
        
        return EmailService.send_email(
            subject=f"Formulaire de contact : {subject}",
            template_name='contact_form',
            context=context,
            recipient_list=recipient_list,
            fail_silently=True
        )