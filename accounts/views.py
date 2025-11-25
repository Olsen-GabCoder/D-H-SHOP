from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db import transaction
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.urls import reverse

from .models import Customer, Address
from orders.models import Order
from core.email_service import EmailService
from .forms import PasswordResetRequestForm, SetPasswordForm
import logging

logger = logging.getLogger(__name__)


def register_view(request):
    """
    Inscription d'un nouvel utilisateur avec envoi email de bienvenue
    """
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')
    
    if request.method == 'POST':
        # Récupération des données
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        phone = request.POST.get('phone', '').strip()
        
        # Validation
        if not all([username, email, password1, password2, first_name, last_name, phone]):
            messages.error(request, 'Veuillez remplir tous les champs.')
            return render(request, 'accounts/register.html')
        
        if password1 != password2:
            messages.error(request, 'Les mots de passe ne correspondent pas.')
            return render(request, 'accounts/register.html')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Ce nom d\'utilisateur existe déjà.')
            return render(request, 'accounts/register.html')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Cet email est déjà utilisé.')
            return render(request, 'accounts/register.html')
        
        try:
            with transaction.atomic():
                # Création de l'utilisateur
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password1,
                    first_name=first_name,
                    last_name=last_name
                )
                
                # Le profil Customer est créé automatiquement par le signal
                # On met juste à jour le téléphone
                user.customer.phone = phone
                user.customer.save()
                
                # ========================================
                # ENVOI DE L'EMAIL DE BIENVENUE
                # ========================================
                try:
                    EmailService.send_welcome_email(user)
                    logger.info(f'Email de bienvenue envoyé à {user.email}')
                except Exception as e:
                    # Logger l'erreur mais ne pas bloquer l'inscription
                    logger.error(f'Échec envoi email bienvenue pour {user.email}: {str(e)}')
                
                # Connexion automatique
                login(request, user)
                
                messages.success(
                    request, 
                    f'Bienvenue {first_name} ! Votre compte a été créé avec succès. '
                    f'Un email de bienvenue vous a été envoyé.'
                )
                return redirect('accounts:dashboard')
                
        except Exception as e:
            logger.error(f'Erreur création compte pour {email}: {str(e)}')
            messages.error(request, f'Erreur lors de la création du compte : {str(e)}')
            return render(request, 'accounts/register.html')
    
    return render(request, 'accounts/register.html')


def login_view(request):
    """
    Connexion d'un utilisateur
    """
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        
        if not username or not password:
            messages.error(request, 'Veuillez remplir tous les champs.')
            return render(request, 'accounts/login.html')
        
        # Authentification
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            # Vérifier que le profil Customer existe
            if not hasattr(user, 'customer'):
                Customer.objects.create(user=user)
            
            login(request, user)
            messages.success(request, f'Bienvenue {user.get_full_name() or user.username} !')
            
            # Redirection vers la page demandée ou dashboard
            next_url = request.GET.get('next', 'accounts:dashboard')
            return redirect(next_url)
        else:
            messages.error(request, 'Nom d\'utilisateur ou mot de passe incorrect.')
            return render(request, 'accounts/login.html')
    
    return render(request, 'accounts/login.html')


@login_required
def logout_view(request):
    """
    Déconnexion de l'utilisateur
    """
    logout(request)
    messages.info(request, 'Vous avez été déconnecté avec succès.')
    return redirect('core:home')


@login_required
def dashboard(request):
    """
    Tableau de bord client
    """
    # Vérifier l'existence du profil Customer
    if not hasattr(request.user, 'customer'):
        Customer.objects.create(user=request.user)
    
    customer = request.user.customer
    
    # Statistiques
    recent_orders = Order.objects.filter(customer=customer).order_by('-created_at')[:5]
    total_orders = Order.objects.filter(customer=customer).count()
    pending_orders = Order.objects.filter(customer=customer, status='pending').count()
    
    # Adresses
    addresses = Address.objects.filter(customer=customer)
    
    context = {
        'customer': customer,
        'recent_orders': recent_orders,
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'addresses': addresses,
        'page_title': 'Mon tableau de bord',
    }
    return render(request, 'accounts/dashboard.html', context)


@login_required
def profile(request):
    """
    Affichage du profil client
    """
    if not hasattr(request.user, 'customer'):
        Customer.objects.create(user=request.user)
    
    customer = request.user.customer
    
    context = {
        'customer': customer,
        'page_title': 'Mon profil',
    }
    return render(request, 'accounts/profile.html', context)


@login_required
def profile_edit(request):
    """
    Modification du profil client
    """
    if not hasattr(request.user, 'customer'):
        Customer.objects.create(user=request.user)
    
    customer = request.user.customer
    
    if request.method == 'POST':
        # Mise à jour des données utilisateur
        request.user.first_name = request.POST.get('first_name', '').strip()
        request.user.last_name = request.POST.get('last_name', '').strip()
        request.user.email = request.POST.get('email', '').strip()
        
        # Mise à jour des données customer
        customer.phone = request.POST.get('phone', '').strip()
        
        # Photo de profil
        if 'profile_picture' in request.FILES:
            customer.profile_picture = request.FILES['profile_picture']
        
        # Préférences de notification
        customer.email_notifications = 'email_notifications' in request.POST
        customer.sms_notifications = 'sms_notifications' in request.POST
        customer.whatsapp_notifications = 'whatsapp_notifications' in request.POST
        
        try:
            request.user.save()
            customer.save()
            messages.success(request, 'Profil mis à jour avec succès !')
            return redirect('accounts:profile')
        except Exception as e:
            logger.error(f'Erreur mise à jour profil pour {request.user.username}: {str(e)}')
            messages.error(request, f'Erreur lors de la mise à jour : {str(e)}')
    
    context = {
        'customer': customer,
        'page_title': 'Modifier mon profil',
    }
    return render(request, 'accounts/profile_edit.html', context)


@login_required
def address_list(request):
    """
    Liste des adresses du client
    """
    if not hasattr(request.user, 'customer'):
        Customer.objects.create(user=request.user)
    
    addresses = Address.objects.filter(customer=request.user.customer).order_by('-is_default', '-created_at')
    
    context = {
        'addresses': addresses,
        'page_title': 'Mes adresses',
    }
    return render(request, 'accounts/address_list.html', context)


@login_required
def address_add(request):
    """
    Ajout d'une nouvelle adresse (avec redirection intelligente)
    """
    if not hasattr(request.user, 'customer'):
        Customer.objects.create(user=request.user)
    
    if request.method == 'POST':
        try:
            # Récupérer toutes les données du formulaire
            full_name = request.POST.get('full_name', '').strip()
            phone = request.POST.get('phone', '').strip()
            address_line1 = request.POST.get('address_line1', '').strip()
            address_line2 = request.POST.get('address_line2', '').strip()
            city = request.POST.get('city', '').strip()
            state = request.POST.get('state', '').strip()
            postal_code = request.POST.get('postal_code', '').strip()
            country = request.POST.get('country', 'Togo').strip()
            address_type = request.POST.get('address_type', 'shipping')
            is_default = 'is_default' in request.POST
            
            # Validation des champs obligatoires
            if not all([full_name, phone, address_line1, city]):
                messages.error(request, 'Veuillez remplir tous les champs obligatoires.')
                return render(request, 'accounts/address_form.html', {
                    'page_title': 'Ajouter une adresse',
                    'action': 'add',
                })
            
            # Créer l'adresse
            address = Address.objects.create(
                customer=request.user.customer,
                full_name=full_name,
                phone=phone,
                address_line1=address_line1,
                address_line2=address_line2,
                city=city,
                state=state,
                postal_code=postal_code,
                country=country,
                address_type=address_type,
                is_default=is_default
            )
            
            messages.success(request, 'Adresse ajoutée avec succès !')
            
            # Rediriger vers la page précédente (priorité : POST > GET > défaut)
            next_url = request.POST.get('next') or request.GET.get('next')
            
            if next_url:
                # Vérifier que l'URL de redirection est sûre (évite les redirections malveillantes)
                if url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
                    return redirect(next_url)
            
            # Par défaut, rediriger vers la liste des adresses
            return redirect('accounts:address_list')
            
        except Exception as e:
            logger.error(f'Erreur ajout adresse pour {request.user.username}: {str(e)}')
            messages.error(request, f'Erreur lors de l\'ajout : {str(e)}')
            return render(request, 'accounts/address_form.html', {
                'page_title': 'Ajouter une adresse',
                'action': 'add',
            })
    
    # GET : Afficher le formulaire vide
    context = {
        'page_title': 'Ajouter une adresse',
        'action': 'add',
    }
    return render(request, 'accounts/address_form.html', context)


@login_required
def address_edit(request, pk):
    """
    Modification d'une adresse
    """
    if not hasattr(request.user, 'customer'):
        Customer.objects.create(user=request.user)
    
    address = get_object_or_404(Address, pk=pk, customer=request.user.customer)
    
    if request.method == 'POST':
        try:
            address.full_name = request.POST.get('full_name', '').strip()
            address.phone = request.POST.get('phone', '').strip()
            address.address_line1 = request.POST.get('address_line1', '').strip()
            address.address_line2 = request.POST.get('address_line2', '').strip()
            address.city = request.POST.get('city', '').strip()
            address.state = request.POST.get('state', '').strip()
            address.postal_code = request.POST.get('postal_code', '').strip()
            address.country = request.POST.get('country', 'Togo')
            address.address_type = request.POST.get('address_type', 'shipping')
            address.is_default = 'is_default' in request.POST
            
            # Validation des champs obligatoires
            if not all([address.full_name, address.phone, address.address_line1, address.city]):
                messages.error(request, 'Veuillez remplir tous les champs obligatoires.')
                return render(request, 'accounts/address_form.html', {
                    'address': address,
                    'page_title': 'Modifier l\'adresse',
                    'action': 'edit',
                })
            
            address.save()
            
            messages.success(request, 'Adresse modifiée avec succès !')
            return redirect('accounts:address_list')
            
        except Exception as e:
            logger.error(f'Erreur modification adresse {pk} pour {request.user.username}: {str(e)}')
            messages.error(request, f'Erreur lors de la modification : {str(e)}')
    
    context = {
        'address': address,
        'page_title': 'Modifier l\'adresse',
        'action': 'edit',
    }
    return render(request, 'accounts/address_form.html', context)


@login_required
def address_delete(request, pk):
    """
    Suppression d'une adresse
    """
    if not hasattr(request.user, 'customer'):
        Customer.objects.create(user=request.user)
    
    address = get_object_or_404(Address, pk=pk, customer=request.user.customer)
    
    if request.method == 'POST':
        address_info = f"{address.full_name} - {address.city}"
        address.delete()
        messages.success(request, f'Adresse "{address_info}" supprimée avec succès !')
        return redirect('accounts:address_list')
    
    context = {
        'address': address,
        'page_title': 'Supprimer l\'adresse',
    }
    return render(request, 'accounts/address_confirm_delete.html', context)


@login_required
def address_set_default(request, address_id):
    """
    ✅ CORRECTION : Définir une adresse comme adresse par défaut
    """
    if not hasattr(request.user, 'customer'):
        Customer.objects.create(user=request.user)
    
    try:
        # Récupérer l'adresse appartenant à l'utilisateur
        address = get_object_or_404(Address, id=address_id, customer=request.user.customer)
        
        # Mettre à jour toutes les adresses de l'utilisateur
        Address.objects.filter(customer=request.user.customer).update(is_default=False)
        
        # Définir l'adresse sélectionnée comme par défaut
        address.is_default = True
        address.save()
        
        messages.success(request, f"L'adresse {address.full_name} a été définie comme adresse par défaut.")
        
    except Exception as e:
        logger.error(f'Erreur modification adresse par défaut {address_id} pour {request.user.username}: {str(e)}')
        messages.error(request, f"Erreur lors de la modification de l'adresse par défaut: {str(e)}")
    
    return redirect('accounts:address_list')


@login_required
def order_list(request):
    """
    Liste des commandes du client
    """
    if not hasattr(request.user, 'customer'):
        Customer.objects.create(user=request.user)
    
    orders = Order.objects.filter(customer=request.user.customer).order_by('-created_at')
    
    context = {
        'orders': orders,
        'page_title': 'Mes commandes',
    }
    return render(request, 'accounts/order_list.html', context)


@login_required
def order_detail(request, order_number):
    """
    Détail d'une commande
    """
    if not hasattr(request.user, 'customer'):
        Customer.objects.create(user=request.user)
    
    order = get_object_or_404(
        Order, 
        order_number=order_number, 
        customer=request.user.customer
    )
    
    context = {
        'order': order,
        'page_title': f'Commande {order.order_number}',
    }
    return render(request, 'accounts/order_detail.html', context)


@login_required
def order_invoice(request, order_number):
    """
    Génération de la facture PDF pour une commande
    """
    if not hasattr(request.user, 'customer'):
        Customer.objects.create(user=request.user)
    
    order = get_object_or_404(
        Order, 
        order_number=order_number, 
        customer=request.user.customer
    )
    
    try:
        # Générer le PDF
        from core.pdf_service import PDFService
        pdf_buffer = PDFService.generate_invoice_pdf(order)
        
        # Retourner le PDF
        response = HttpResponse(pdf_buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="facture_{order.order_number}.pdf"'
        
        logger.info(f'Facture PDF générée pour commande {order.order_number}')
        return response
        
    except Exception as e:
        logger.error(f'Erreur génération facture PDF pour {order.order_number}: {str(e)}')
        messages.error(request, 'Erreur lors de la génération de la facture. Veuillez réessayer.')
        return redirect('accounts:order_detail', order_number=order_number)


@login_required
def order_packing_slip(request, order_number):
    """
    Génération du bon de livraison PDF pour une commande
    """
    if not hasattr(request.user, 'customer'):
        Customer.objects.create(user=request.user)
    
    order = get_object_or_404(
        Order, 
        order_number=order_number, 
        customer=request.user.customer
    )
    
    try:
        # Générer le PDF
        from core.pdf_service import PDFService
        pdf_buffer = PDFService.generate_packing_slip_pdf(order)
        
        # Retourner le PDF
        response = HttpResponse(pdf_buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="bon_livraison_{order.order_number}.pdf"'
        
        logger.info(f'Bon de livraison PDF généré pour commande {order.order_number}')
        return response
        
    except Exception as e:
        logger.error(f'Erreur génération bon de livraison PDF pour {order.order_number}: {str(e)}')
        messages.error(request, 'Erreur lors de la génération du bon de livraison. Veuillez réessayer.')
        return redirect('accounts:order_detail', order_number=order_number)


# ============================================================================
# VUES DE RÉINITIALISATION DE MOT DE PASSE (à ajouter à la fin du fichier)
# ============================================================================

def password_reset_request(request):
    """
    Étape 1 : Demande de réinitialisation de mot de passe
    - Affiche le formulaire de saisie d'email
    - Génère et envoie le lien de réinitialisation par email
    """
    if request.user.is_authenticated:
        messages.info(request, 'Vous êtes déjà connecté.')
        return redirect('accounts:dashboard')
    
    if request.method == 'POST':
        form = PasswordResetRequestForm(request.POST)
        
        if form.is_valid():
            # Récupérer l'utilisateur validé
            user = form.get_user()
            
            if user:
                try:
                    # ========================================
                    # GÉNÉRATION DU TOKEN SÉCURISÉ
                    # ========================================
                    # 1. Générer le token de réinitialisation
                    token = default_token_generator.make_token(user)
                    
                    # 2. Encoder l'ID utilisateur en base64
                    uid = urlsafe_base64_encode(force_bytes(user.pk))
                    
                    # 3. Construire l'URL complète de réinitialisation
                    reset_path = reverse('accounts:password_reset_confirm', kwargs={
                        'uidb64': uid,
                        'token': token
                    })
                    reset_url = request.build_absolute_uri(reset_path)
                    
                    # ========================================
                    # ENVOI DE L'EMAIL
                    # ========================================
                    EmailService.send_password_reset(user, reset_url)
                    
                    logger.info(f'Email de réinitialisation envoyé à {user.email}')
                    
                    messages.success(
                        request,
                        'Un email contenant les instructions de réinitialisation '
                        'a été envoyé à votre adresse. Veuillez vérifier votre boîte de réception.'
                    )
                    return redirect('accounts:password_reset_done')
                    
                except Exception as e:
                    logger.error(f'Erreur envoi email réinitialisation pour {user.email}: {str(e)}')
                    messages.error(
                        request,
                        'Une erreur s\'est produite lors de l\'envoi de l\'email. '
                        'Veuillez réessayer ultérieurement.'
                    )
    else:
        form = PasswordResetRequestForm()
    
    context = {
        'form': form,
        'page_title': 'Mot de passe oublié',
    }
    return render(request, 'accounts/password_reset_request.html', context)


def password_reset_done(request):
    """
    Étape 2 : Confirmation d'envoi de l'email
    - Page intermédiaire après l'envoi du lien
    """
    context = {
        'page_title': 'Email envoyé',
    }
    return render(request, 'accounts/password_reset_done.html', context)


def password_reset_confirm(request, uidb64, token):
    """
    Étape 3 : Confirmation et changement du mot de passe
    - Valide le token et l'UID
    - Affiche le formulaire de nouveau mot de passe
    - Met à jour le mot de passe si valide
    """
    # ========================================
    # VALIDATION DU TOKEN ET DE L'UID
    # ========================================
    try:
        # 1. Décoder l'UID
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
        
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    
    # 2. Vérifier que l'utilisateur existe et que le token est valide
    if user is not None and default_token_generator.check_token(user, token):
        # Token valide : Afficher le formulaire de nouveau mot de passe
        
        if request.method == 'POST':
            form = SetPasswordForm(request.POST)
            
            if form.is_valid():
                # ========================================
                # MISE À JOUR DU MOT DE PASSE
                # ========================================
                new_password = form.cleaned_data['new_password1']
                
                try:
                    # Changer le mot de passe
                    user.set_password(new_password)
                    user.save()
                    
                    logger.info(f'Mot de passe réinitialisé avec succès pour {user.username}')
                    
                    messages.success(
                        request,
                        'Votre mot de passe a été modifié avec succès ! '
                        'Vous pouvez maintenant vous connecter avec votre nouveau mot de passe.'
                    )
                    return redirect('accounts:password_reset_complete')
                    
                except Exception as e:
                    logger.error(f'Erreur modification mot de passe pour {user.username}: {str(e)}')
                    messages.error(
                        request,
                        'Une erreur s\'est produite lors de la modification du mot de passe. '
                        'Veuillez réessayer.'
                    )
        else:
            form = SetPasswordForm()
        
        context = {
            'form': form,
            'validlink': True,
            'page_title': 'Nouveau mot de passe',
        }
        return render(request, 'accounts/password_reset_confirm.html', context)
    
    else:
        # ========================================
        # TOKEN INVALIDE OU EXPIRÉ
        # ========================================
        logger.warning(f'Tentative de réinitialisation avec token invalide : uidb64={uidb64}')
        
        context = {
            'validlink': False,
            'page_title': 'Lien invalide',
        }
        return render(request, 'accounts/password_reset_confirm.html', context)


def password_reset_complete(request):
    """
    Étape 4 : Confirmation finale
    - Page de succès après changement du mot de passe
    """
    context = {
        'page_title': 'Mot de passe modifié',
    }
    return render(request, 'accounts/password_reset_complete.html', context)


# ============================================================================
# FIN DES VUES DE RÉINITIALISATION
# ============================================================================