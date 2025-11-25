from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


class PasswordResetRequestForm(forms.Form):
    """
    Formulaire de demande de réinitialisation de mot de passe.
    Vérifie que l'email existe dans la base de données.
    """
    email = forms.EmailField(
        label="Adresse email",
        max_length=254,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Entrez votre adresse email',
            'autofocus': True
        }),
        error_messages={
            'required': 'Veuillez entrer votre adresse email.',
            'invalid': 'Veuillez entrer une adresse email valide.'
        }
    )

    def clean_email(self):
        """
        Valide que l'email existe dans la base de données.
        """
        email = self.cleaned_data.get('email', '').strip().lower()
        
        # Vérifier que l'email existe
        if not User.objects.filter(email__iexact=email).exists():
            raise ValidationError(
                "Aucun compte n'est associé à cette adresse email. "
                "Veuillez vérifier l'adresse ou créer un nouveau compte."
            )
        
        return email

    def get_user(self):
        """
        Retourne l'utilisateur correspondant à l'email validé.
        """
        email = self.cleaned_data.get('email')
        if email:
            try:
                return User.objects.get(email__iexact=email)
            except User.DoesNotExist:
                return None
        return None


class SetPasswordForm(forms.Form):
    """
    Formulaire pour définir un nouveau mot de passe.
    Utilisé après validation du lien de réinitialisation.
    """
    new_password1 = forms.CharField(
        label="Nouveau mot de passe",
        strip=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Entrez votre nouveau mot de passe',
            'autocomplete': 'new-password'
        }),
        help_text="Minimum 8 caractères, au moins une lettre et un chiffre.",
        error_messages={
            'required': 'Veuillez entrer un nouveau mot de passe.'
        }
    )
    
    new_password2 = forms.CharField(
        label="Confirmation du mot de passe",
        strip=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirmez votre mot de passe',
            'autocomplete': 'new-password'
        }),
        error_messages={
            'required': 'Veuillez confirmer votre mot de passe.'
        }
    )

    def clean_new_password1(self):
        """
        Valide la robustesse du mot de passe.
        """
        password = self.cleaned_data.get('new_password1')
        
        # Validation de la longueur minimale
        if len(password) < 8:
            raise ValidationError(
                "Le mot de passe doit contenir au moins 8 caractères."
            )
        
        # Validation : au moins une lettre
        if not any(char.isalpha() for char in password):
            raise ValidationError(
                "Le mot de passe doit contenir au moins une lettre."
            )
        
        # Validation : au moins un chiffre
        if not any(char.isdigit() for char in password):
            raise ValidationError(
                "Le mot de passe doit contenir au moins un chiffre."
            )
        
        return password

    def clean(self):
        """
        Valide que les deux mots de passe correspondent.
        """
        cleaned_data = super().clean()
        password1 = cleaned_data.get('new_password1')
        password2 = cleaned_data.get('new_password2')

        if password1 and password2 and password1 != password2:
            raise ValidationError({
                'new_password2': "Les deux mots de passe ne correspondent pas."
            })

        return cleaned_data