/**
 * ========================================
 * REGISTER.JS - Page d'Inscription
 * ========================================
 * Gestion du formulaire multi-étapes avec validation,
 * indicateur de force du mot de passe et animations
 */

(function() {
    'use strict';

    // Variables globales
    let currentStep = 1;
    const totalSteps = 3;
    let formSubmitted = false;

    // ============================================
    // INITIALISATION AU CHARGEMENT DU DOM
    // ============================================
    document.addEventListener('DOMContentLoaded', function() {
        initRegisterPage();
    });

    /**
     * Initialisation principale de la page d'inscription
     */
    function initRegisterPage() {
        initStepNavigation();
        initFormValidation();
        initPasswordStrength();
        initPasswordToggles();
        initPhoneFormatting();
        initFormSubmission();
        initInputAnimations();
        initKeyboardShortcuts();
        handleDjangoErrors();
        
        console.log('✅ Page d\'inscription initialisée');
    }

    // ============================================
    // NAVIGATION ENTRE LES ÉTAPES
    // ============================================
    function initStepNavigation() {
        // Boutons "Suivant"
        document.querySelectorAll('.btn-next').forEach(btn => {
            btn.addEventListener('click', function() {
                const nextStep = parseInt(this.dataset.next);
                if (validateStep(currentStep)) {
                    showStep(nextStep);
                }
            });
        });

        // Boutons "Précédent"
        document.querySelectorAll('.btn-prev').forEach(btn => {
            btn.addEventListener('click', function() {
                const prevStep = parseInt(this.dataset.prev);
                showStep(prevStep);
            });
        });
    }

    /**
     * Afficher une étape spécifique
     */
    function showStep(stepNumber) {
        // Cacher toutes les étapes
        document.querySelectorAll('.form-step').forEach(step => {
            step.classList.remove('active');
        });

        // Afficher l'étape demandée
        const targetStep = document.querySelector(`.form-step[data-step="${stepNumber}"]`);
        if (targetStep) {
            targetStep.classList.add('active');
        }

        // Mettre à jour les indicateurs de progression
        updateProgressIndicators(stepNumber);

        currentStep = stepNumber;

        // Scroll vers le haut en douceur
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }

    /**
     * Mettre à jour les indicateurs de progression
     */
    function updateProgressIndicators(stepNumber) {
        document.querySelectorAll('.progress-step').forEach(step => {
            const stepNum = parseInt(step.dataset.step);
            step.classList.remove('active', 'completed');

            if (stepNum < stepNumber) {
                step.classList.add('completed');
            } else if (stepNum === stepNumber) {
                step.classList.add('active');
            }
        });
    }

    // ============================================
    // VALIDATION DU FORMULAIRE
    // ============================================
    function initFormValidation() {
        // Validation en temps réel
        document.querySelectorAll('input').forEach(input => {
            input.addEventListener('blur', function() {
                if (this.value) {
                    validateField(this);
                }
            });

            input.addEventListener('input', function() {
                if (this.classList.contains('is-invalid') || this.classList.contains('is-valid')) {
                    validateField(this);
                }
            });
        });
    }

    /**
     * Valider tous les champs d'une étape
     */
    function validateStep(stepNumber) {
        const stepElement = document.querySelector(`.form-step[data-step="${stepNumber}"]`);
        if (!stepElement) return false;

        const inputs = stepElement.querySelectorAll('input[required]');
        let isValid = true;

        inputs.forEach(input => {
            if (!validateField(input)) {
                isValid = false;
            }
        });

        return isValid;
    }

    /**
     * Valider un champ individuel
     */
    function validateField(input) {
        const value = input.value.trim();
        const feedback = input.parentElement.querySelector('.form-feedback') || 
                        input.closest('.form-group-modern')?.querySelector('.form-feedback');

        // Validation de base : champ requis
        if (!value && input.hasAttribute('required')) {
            showFieldError(input, feedback, 'Ce champ est obligatoire');
            return false;
        }

        // Validations spécifiques par type de champ
        if (input.id === 'username') {
            return validateUsername(input, value, feedback);
        }

        if (input.type === 'email') {
            return validateEmail(input, value, feedback);
        }

        if (input.id === 'phone') {
            return validatePhone(input, value, feedback);
        }

        if (input.id === 'password2') {
            return validatePasswordConfirmation(input, value, feedback);
        }

        // Si validation réussie
        showFieldSuccess(input, feedback);
        return true;
    }

    /**
     * Validation du nom d'utilisateur
     */
    function validateUsername(input, value, feedback) {
        if (value.length < 3) {
            showFieldError(input, feedback, 'Minimum 3 caractères');
            return false;
        }
        if (!/^[a-zA-Z0-9_]+$/.test(value)) {
            showFieldError(input, feedback, 'Lettres, chiffres et underscore uniquement');
            return false;
        }
        showFieldSuccess(input, feedback);
        return true;
    }

    /**
     * Validation de l'email
     */
    function validateEmail(input, value, feedback) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(value)) {
            showFieldError(input, feedback, 'Email invalide');
            return false;
        }
        showFieldSuccess(input, feedback);
        return true;
    }

    /**
     * Validation du téléphone
     */
    function validatePhone(input, value, feedback) {
        const phoneDigits = value.replace(/\D/g, '');
        if (phoneDigits.length < 8) {
            showFieldError(input, feedback, 'Numéro invalide (min. 8 chiffres)');
            return false;
        }
        showFieldSuccess(input, feedback);
        return true;
    }

    /**
     * Validation de la confirmation du mot de passe
     */
    function validatePasswordConfirmation(input, value, feedback) {
        const password1 = document.getElementById('password1')?.value;
        if (value !== password1) {
            showFieldError(input, feedback, 'Les mots de passe ne correspondent pas');
            return false;
        }
        showFieldSuccess(input, feedback);
        return true;
    }

    /**
     * Afficher une erreur de champ
     */
    function showFieldError(input, feedback, message) {
        input.classList.add('is-invalid');
        input.classList.remove('is-valid');
        if (feedback) {
            feedback.textContent = message;
            feedback.style.display = 'block';
        }
    }

    /**
     * Afficher le succès de validation
     */
    function showFieldSuccess(input, feedback) {
        input.classList.remove('is-invalid');
        input.classList.add('is-valid');
        if (feedback) {
            feedback.textContent = '✓ Valide';
            feedback.style.display = 'block';
        }
    }

    // ============================================
    // INDICATEUR DE FORCE DU MOT DE PASSE
    // ============================================
    function initPasswordStrength() {
        const password1 = document.getElementById('password1');
        const strengthFill = document.querySelector('.strength-fill');
        const strengthText = document.querySelector('.strength-text');

        if (!password1 || !strengthFill || !strengthText) return;

        password1.addEventListener('input', function() {
            const password = this.value;
            const strength = calculatePasswordStrength(password);

            updatePasswordStrengthUI(strength, strengthFill, strengthText);
        });
    }

    /**
     * Calculer la force du mot de passe
     */
    function calculatePasswordStrength(password) {
        let strength = 0;

        // Critères de force
        if (password.length >= 8) strength++;
        if (password.match(/[a-z]/)) strength++;
        if (password.match(/[A-Z]/)) strength++;
        if (password.match(/[0-9]/)) strength++;
        if (password.match(/[^a-zA-Z0-9]/)) strength++;

        return strength;
    }

    /**
     * Mettre à jour l'interface de force du mot de passe
     */
    function updatePasswordStrengthUI(strength, strengthFill, strengthText) {
        // Réinitialiser les classes
        strengthFill.className = 'strength-fill';
        strengthText.className = 'strength-text';

        if (strength <= 2) {
            strengthFill.classList.add('weak');
            strengthText.classList.add('weak');
            strengthText.textContent = 'Mot de passe faible';
        } else if (strength <= 4) {
            strengthFill.classList.add('medium');
            strengthText.classList.add('medium');
            strengthText.textContent = 'Mot de passe moyen';
        } else {
            strengthFill.classList.add('strong');
            strengthText.classList.add('strong');
            strengthText.textContent = 'Mot de passe fort';
        }
    }

    // ============================================
    // TOGGLE AFFICHAGE MOT DE PASSE
    // ============================================
    function initPasswordToggles() {
        document.querySelectorAll('.password-toggle').forEach(toggle => {
            toggle.addEventListener('click', function() {
                const targetId = this.dataset.target;
                const input = document.getElementById(targetId);
                const icon = this.querySelector('i');

                if (!input) return;

                if (input.type === 'password') {
                    input.type = 'text';
                    icon.classList.remove('fa-eye');
                    icon.classList.add('fa-eye-slash');
                } else {
                    input.type = 'password';
                    icon.classList.remove('fa-eye-slash');
                    icon.classList.add('fa-eye');
                }
            });
        });
    }

    // ============================================
    // FORMATAGE DU TÉLÉPHONE
    // ============================================
    function initPhoneFormatting() {
        const phoneInput = document.getElementById('phone');

        if (phoneInput) {
            phoneInput.addEventListener('input', function() {
                // Autoriser seulement les chiffres, espaces, +, -, (, )
                this.value = this.value.replace(/[^\d\s\+\-\(\)]/g, '');
            });
        }
    }

    // ============================================
    // SOUMISSION DU FORMULAIRE
    // ============================================
    function initFormSubmission() {
        const registerForm = document.getElementById('registerForm');
        const submitBtn = document.querySelector('.btn-submit');

        if (!registerForm) return;

        registerForm.addEventListener('submit', function(e) {
            e.preventDefault();

            // Empêcher la soumission multiple
            if (formSubmitted) {
                return false;
            }

            // Validation finale de l'étape 3
            if (!validateStep(3)) {
                return;
            }

            // Vérifier l'acceptation des conditions
            const acceptTerms = document.getElementById('accept_terms');
            if (!acceptTerms || !acceptTerms.checked) {
                showNotification('Veuillez accepter les conditions générales', 'warning');
                acceptTerms?.focus();
                return;
            }

            // Vérifier la correspondance des mots de passe
            const password1 = document.getElementById('password1')?.value;
            const password2 = document.getElementById('password2')?.value;

            if (password1 !== password2) {
                showNotification('Les mots de passe ne correspondent pas', 'danger');
                return;
            }

            // Animation du bouton
            submitBtn.classList.add('loading');
            submitBtn.disabled = true;
            formSubmitted = true;

            // Soumettre le formulaire après un court délai
            setTimeout(() => {
                this.submit();
            }, 500);
        });
    }

    // ============================================
    // SYSTÈME DE NOTIFICATIONS
    // ============================================
    function showNotification(message, type = 'info') {
        let messagesContainer = document.querySelector('.messages-container');

        // Créer le conteneur si nécessaire
        if (!messagesContainer) {
            messagesContainer = document.createElement('div');
            messagesContainer.className = 'messages-container';
            const form = document.querySelector('.register-form');
            form.insertBefore(messagesContainer, form.firstChild);
        }

        const iconMap = {
            success: 'check-circle',
            danger: 'exclamation-circle',
            warning: 'exclamation-triangle',
            info: 'info-circle'
        };

        const alert = document.createElement('div');
        alert.className = `alert-modern alert-${type}`;
        alert.innerHTML = `
            <i class="fas fa-${iconMap[type] || iconMap.info}"></i>
            <span>${message}</span>
            <button type="button" class="alert-close" onclick="this.parentElement.remove()">
                <i class="fas fa-times"></i>
            </button>
        `;

        messagesContainer.appendChild(alert);

        // Auto-dismiss après 5 secondes
        setTimeout(() => {
            alert.style.opacity = '0';
            setTimeout(() => alert.remove(), 300);
        }, 5000);
    }

    // ============================================
    // ANIMATION DES INPUTS AU FOCUS
    // ============================================
    function initInputAnimations() {
        document.querySelectorAll('.form-control-modern').forEach(input => {
            input.addEventListener('focus', function() {
                this.parentElement.classList.add('focused');
            });

            input.addEventListener('blur', function() {
                this.parentElement.classList.remove('focused');
            });
        });
    }

    // ============================================
    // RACCOURCIS CLAVIER
    // ============================================
    function initKeyboardShortcuts() {
        document.addEventListener('keydown', function(e) {
            // Enter pour passer à l'étape suivante (sauf dans textarea)
            if (e.key === 'Enter' && currentStep < totalSteps && e.target.tagName !== 'TEXTAREA') {
                e.preventDefault();
                const nextBtn = document.querySelector(`.form-step[data-step="${currentStep}"] .btn-next`);
                if (nextBtn) {
                    nextBtn.click();
                }
            }
        });
    }

    // ============================================
    // GESTION DES ERREURS DJANGO
    // ============================================
    function handleDjangoErrors() {
        const djangoErrors = document.querySelectorAll('.errorlist');

        djangoErrors.forEach(errorList => {
            const field = errorList.previousElementSibling;
            
            if (field && field.classList.contains('form-control-modern')) {
                field.classList.add('is-invalid');

                // Convertir les erreurs Django en format moderne
                const errors = Array.from(errorList.querySelectorAll('li'))
                    .map(li => li.textContent);
                
                const feedback = field.parentElement.querySelector('.form-feedback') || 
                                field.closest('.form-group-modern')?.querySelector('.form-feedback');

                if (feedback) {
                    feedback.textContent = errors.join(', ');
                    feedback.style.display = 'block';
                }
            }
        });
    }

    // Exposer la fonction showNotification globalement si nécessaire
    window.showNotification = showNotification;

})();