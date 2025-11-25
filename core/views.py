from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.views.generic import TemplateView
from shop.models import Product, Category
from marketing.models import Promotion


def home(request):
    """
    Page d'accueil du site
    """
    # Produits phares (featured)
    featured_products = Product.objects.filter(
        is_active=True,
        is_featured=True
    )[:8]
    
    # Nouveaux produits
    new_products = Product.objects.filter(
        is_active=True,
        is_new=True
    ).order_by('-created_at')[:8]
    
    # Produits les plus vendus
    bestsellers = Product.objects.filter(
        is_active=True
    ).order_by('-sales_count')[:8]
    
    # Catégories principales (sans parent)
    main_categories = Category.objects.filter(
        is_active=True,
        parent__isnull=True
    ).order_by('display_order')[:6]
    
    # Promotions actives
    active_promotions = Promotion.objects.filter(
        is_active=True
    ).order_by('-priority')[:3]
    
    context = {
        'featured_products': featured_products,
        'new_products': new_products,
        'bestsellers': bestsellers,
        'main_categories': main_categories,
        'active_promotions': active_promotions,
    }
    
    return render(request, 'core/home.html', context)


def about(request):
    """
    Page À propos
    """
    context = {
        'page_title': 'À propos de nous',
    }
    return render(request, 'core/about.html', context)


def contact(request):
    """
    Page Contact avec formulaire
    """
    if request.method == 'POST':
        # Récupération des données du formulaire
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        subject = request.POST.get('subject', '').strip()
        message = request.POST.get('message', '').strip()
        
        # Validation basique
        if not all([name, email, subject, message]):
            messages.error(request, 'Veuillez remplir tous les champs.')
            return render(request, 'core/contact.html', {
                'name': name,
                'email': email,
                'subject': subject,
                'message': message,
            })
        
        # Validation de l'email
        if '@' not in email:
            messages.error(request, 'Veuillez entrer une adresse email valide.')
            return render(request, 'core/contact.html', {
                'name': name,
                'email': email,
                'subject': subject,
                'message': message,
            })
        
        # Envoi de l'email (optionnel, nécessite configuration SMTP)
        try:
            full_message = f"""
            Nouveau message de contact
            
            De: {name}
            Email: {email}
            Sujet: {subject}
            
            Message:
            {message}
            """
            
            # Décommentez ces lignes si vous avez configuré l'envoi d'emails
            # send_mail(
            #     f'[Contact] {subject}',
            #     full_message,
            #     email,
            #     [settings.DEFAULT_FROM_EMAIL],
            #     fail_silently=False,
            # )
            
            messages.success(
                request,
                'Votre message a été envoyé avec succès ! Nous vous répondrons dans les plus brefs délais.'
            )
            return redirect('core:contact')
            
        except Exception as e:
            messages.warning(
                request,
                'Votre message a été reçu mais l\'envoi de l\'email de confirmation a échoué. '
                'Nous traiterons votre demande dans les plus brefs délais.'
            )
            return redirect('core:contact')
    
    context = {
        'page_title': 'Contactez-nous',
    }
    return render(request, 'core/contact.html', context)


def faq(request):
    """
    Page FAQ (Questions fréquemment posées)
    """
    # Liste des questions-réponses
    faqs = [
        {
            'category': 'Commandes',
            'questions': [
                {
                    'question': 'Comment passer une commande ?',
                    'answer': 'Pour passer une commande, ajoutez les produits souhaités à votre panier, '
                             'puis cliquez sur "Panier" et suivez les étapes de validation.'
                },
                {
                    'question': 'Puis-je modifier ma commande après validation ?',
                    'answer': 'Une fois votre commande validée, vous ne pouvez plus la modifier directement. '
                             'Contactez notre service client dans les plus brefs délais.'
                },
                {
                    'question': 'Comment annuler une commande ?',
                    'answer': 'Vous pouvez annuler une commande tant qu\'elle n\'a pas été expédiée. '
                             'Rendez-vous dans votre espace client ou contactez-nous.'
                },
            ]
        },
        {
            'category': 'Livraison',
            'questions': [
                {
                    'question': 'Quels sont les délais de livraison ?',
                    'answer': 'Les délais de livraison sont généralement de 2 à 5 jours ouvrables '
                             'selon votre localisation.'
                },
                {
                    'question': 'Quels sont les frais de livraison ?',
                    'answer': 'Les frais de livraison varient selon votre zone géographique. '
                             'Ils sont calculés automatiquement lors du processus de commande.'
                },
                {
                    'question': 'Puis-je suivre ma commande ?',
                    'answer': 'Oui, vous recevrez un numéro de suivi par email une fois votre commande expédiée. '
                             'Vous pouvez également suivre votre commande depuis votre espace client.'
                },
            ]
        },
        {
            'category': 'Paiement',
            'questions': [
                {
                    'question': 'Quels moyens de paiement acceptez-vous ?',
                    'answer': 'Nous acceptons Aitel Money, Moov Money et le paiement à la livraison (cash).'
                },
                {
                    'question': 'Le paiement en ligne est-il sécurisé ?',
                    'answer': 'Oui, toutes les transactions sont sécurisées et cryptées. '
                             'Nous ne conservons aucune information bancaire.'
                },
                {
                    'question': 'Que faire si mon paiement échoue ?',
                    'answer': 'Si votre paiement échoue, vérifiez vos informations et réessayez. '
                             'Si le problème persiste, contactez votre fournisseur de paiement ou notre service client.'
                },
            ]
        },
        {
            'category': 'Retours et Remboursements',
            'questions': [
                {
                    'question': 'Quelle est votre politique de retour ?',
                    'answer': 'Vous disposez de 14 jours pour retourner un produit non utilisé dans son emballage d\'origine.'
                },
                {
                    'question': 'Comment obtenir un remboursement ?',
                    'answer': 'Une fois votre retour reçu et vérifié, nous procédons au remboursement '
                             'dans un délai de 5 à 10 jours ouvrables.'
                },
                {
                    'question': 'Les frais de retour sont-ils à ma charge ?',
                    'answer': 'Les frais de retour sont à votre charge sauf si le produit est défectueux '
                             'ou si nous avons commis une erreur.'
                },
            ]
        },
        {
            'category': 'Compte Client',
            'questions': [
                {
                    'question': 'Comment créer un compte ?',
                    'answer': 'Cliquez sur "S\'inscrire" en haut de la page et remplissez le formulaire d\'inscription.'
                },
                {
                    'question': 'J\'ai oublié mon mot de passe, que faire ?',
                    'answer': 'Cliquez sur "Mot de passe oublié" sur la page de connexion. '
                             'Vous recevrez un email pour réinitialiser votre mot de passe.'
                },
                {
                    'question': 'Comment modifier mes informations personnelles ?',
                    'answer': 'Connectez-vous à votre compte et rendez-vous dans "Mon profil" '
                             'pour modifier vos informations.'
                },
            ]
        },
    ]
    
    context = {
        'page_title': 'Questions fréquentes',
        'faqs': faqs,
    }
    return render(request, 'core/faq.html', context)

# ========================================
# PAGES LÉGALES
# ========================================

class TermsAndConditionsView(TemplateView):
    """
    Page Conditions Générales d'Utilisation (CGU)
    """
    template_name = 'core/legal/terms.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Conditions Générales d\'Utilisation'
        context['last_updated'] = '16 Novembre 2025'
        return context


class PrivacyPolicyView(TemplateView):
    """
    Page Politique de Confidentialité
    """
    template_name = 'core/legal/privacy.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Politique de Confidentialité'
        context['last_updated'] = '16 Novembre 2025'
        return context


class ReturnPolicyView(TemplateView):
    """
    Page Politique de Retour et Remboursement
    """
    template_name = 'core/legal/return_policy.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Politique de Retour et Remboursement'
        context['last_updated'] = '16 Novembre 2025'
        return context
