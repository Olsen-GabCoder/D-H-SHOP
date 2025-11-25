/**
 * ========================================
 * ADDRESS-FORM.JS - Formulaire d'Adresse
 * ========================================
 * Gestion du formulaire wizard multi-étapes avec
 * validation avancée, animations et auto-complétion
 */

(function() {
    'use strict';

    // Configuration globale
    const CONFIG = {
        totalSteps: 3,
        gabonCities: ['Libreville', 'Port-Gentil', 'Franceville', 'Oyem', 'Moanda', 
                      'Mouila', 'Lambaréné', 'Tchibanga']
    };

    // État de l'application
    let currentStep = 1;
    let formModified = false;

    /**
     * Initialisation au chargement du DOM
     */
    document.addEventListener('DOMContentLoaded', function() {
        
        // Éléments du DOM
        const addressForm = document.getElementById('addressForm');
        const submitBtn = document.querySelector('.btn-submit');
        
        if (!addressForm) {
            console.error('❌ Formulaire d\'adresse introuvable');
            return;
        }

        // ============================================
        // NAVIGATION ENTRE LES ÉTAPES
        // ============================================
        
        initStepNavigation();
        
        // ============================================
        // VALIDATION EN TEMPS RÉEL
        // ============================================
        
        initRealTimeValidation();
        
        // ============================================
        // FORMATAGE AUTOMATIQUE
        // ============================================
        
        initPhoneFormatting();
        
        // ============================================
        // SOUMISSION DU FORMULAIRE
        // ============================================
        
        initFormSubmission(addressForm, submitBtn);
        
        // ============================================
        // ANIMATIONS ET INTERACTIONS
        // ============================================
        
        initFormAnimations();
        initTypeCardInteractions();
        
        // ============================================
        // AUTO-COMPLÉTION INTELLIGENTE
        // ============================================
        
        initAutoCompletion();
        
        // ============================================
        // GESTION DES ERREURS DJANGO
        // ============================================
        
        handleDjangoErrors();
        
        // ============================================
        // RACCOURCIS CLAVIER
        // ============================================
        
        initKeyboardShortcuts(addressForm);
        
        // ============================================
        // CONFIRMATION AVANT QUITTER
        // ============================================
        
        initUnsavedChangesWarning(addressForm);
        
        // ============================================
        // EFFET PARALLAX
        // ============================================
        
        initParallaxEffect();
        
        // ============================================
        // LOGGING POUR DEBUG
        // ============================================
        
        console.log('✅ Address Form initialized');
        console.log('📍 Current step:', currentStep);
        console.log('📝 Total steps:', CONFIG.totalSteps);
        
    });

    // ============================================
    // FONCTIONS DE NAVIGATION
    // ============================================
    
    /**
     * Initialise la navigation entre les étapes
     */
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
     * Affiche une étape spécifique du formulaire
     * @param {number} stepNumber - Numéro de l'étape
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
        
        // Scroll vers le haut avec animation fluide
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }
    
    /**
     * Met à jour les indicateurs visuels de progression
     * @param {number} stepNumber - Numéro de l'étape actuelle
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
    // FONCTIONS DE VALIDATION
    // ============================================
    
    /**
     * Valide tous les champs d'une étape
     * @param {number} stepNumber - Numéro de l'étape
     * @returns {boolean} - True si valide
     */
    function validateStep(stepNumber) {
        const stepElement = document.querySelector(`.form-step[data-step="${stepNumber}"]`);
        if (!stepElement) return false;
        
        const inputs = stepElement.querySelectorAll('input[required], select[required]');
        let isValid = true;
        
        inputs.forEach(input => {
            if (!validateField(input)) {
                isValid = false;
            }
        });
        
        return isValid;
    }
    
    /**
     * Valide un champ individuel
     * @param {HTMLElement} input - Champ à valider
     * @returns {boolean} - True si valide
     */
    function validateField(input) {
        const value = input.value.trim();
        const feedback = getFeedbackElement(input);
        
        // Validation de base : champ requis
        if (!value && input.hasAttribute('required')) {
            setFieldInvalid(input, feedback, 'Ce champ est obligatoire');
            return false;
        }
        
        // Validations spécifiques par champ
        const validationResult = validateSpecificField(input, value);
        
        if (!validationResult.isValid) {
            setFieldInvalid(input, feedback, validationResult.message);
            return false;
        }
        
        // Champ valide
        setFieldValid(input, feedback);
        return true;
    }
    
    /**
     * Validations spécifiques par type de champ
     * @param {HTMLElement} input - Champ à valider
     * @param {string} value - Valeur du champ
     * @returns {object} - Résultat de validation
     */
    function validateSpecificField(input, value) {
        switch (input.id) {
            case 'full_name':
                if (value.length < 3) {
                    return { isValid: false, message: 'Minimum 3 caractères' };
                }
                break;
                
            case 'phone':
                const phoneDigits = value.replace(/\D/g, '');
                if (phoneDigits.length < 8) {
                    return { isValid: false, message: 'Numéro invalide (min. 8 chiffres)' };
                }
                break;
                
            case 'address_line1':
                if (value.length < 5) {
                    return { isValid: false, message: 'Adresse trop courte (min. 5 caractères)' };
                }
                break;
                
            case 'city':
                if (value.length < 2) {
                    return { isValid: false, message: 'Ville invalide' };
                }
                break;
                
            case 'country':
                if (!value) {
                    return { isValid: false, message: 'Veuillez sélectionner un pays' };
                }
                break;
        }
        
        return { isValid: true };
    }
    
    /**
     * Récupère l'élément de feedback pour un champ
     * @param {HTMLElement} input - Champ de formulaire
     * @returns {HTMLElement|null} - Élément de feedback
     */
    function getFeedbackElement(input) {
        return input.parentElement.querySelector('.form-feedback') || 
               input.closest('.form-group-modern')?.querySelector('.form-feedback');
    }
    
    /**
     * Marque un champ comme invalide
     * @param {HTMLElement} input - Champ de formulaire
     * @param {HTMLElement} feedback - Élément de feedback
     * @param {string} message - Message d'erreur
     */
    function setFieldInvalid(input, feedback, message) {
        input.classList.add('is-invalid');
        input.classList.remove('is-valid');
        
        if (feedback) {
            feedback.textContent = message;
            feedback.style.display = 'block';
        }
    }
    
    /**
     * Marque un champ comme valide
     * @param {HTMLElement} input - Champ de formulaire
     * @param {HTMLElement} feedback - Élément de feedback
     */
    function setFieldValid(input, feedback) {
        input.classList.remove('is-invalid');
        input.classList.add('is-valid');
        
        if (feedback) {
            feedback.textContent = '✓ Valide';
            feedback.style.display = 'block';
        }
    }

    // ============================================
    // VALIDATION EN TEMPS RÉEL
    // ============================================
    
    /**
     * Initialise la validation en temps réel
     */
    function initRealTimeValidation() {
        document.querySelectorAll('input, select').forEach(input => {
            // Validation au blur
            input.addEventListener('blur', function() {
                if (this.value && this.hasAttribute('required')) {
                    validateField(this);
                }
            });
            
            // Re-validation pendant la saisie si déjà validé/invalidé
            input.addEventListener('input', function() {
                if (this.classList.contains('is-invalid') || this.classList.contains('is-valid')) {
                    validateField(this);
                }
            });
        });
    }

    // ============================================
    // FORMATAGE AUTOMATIQUE
    // ============================================
    
    /**
     * Initialise le formatage automatique du téléphone
     */
    function initPhoneFormatting() {
        const phoneInput = document.getElementById('phone');
        
        if (phoneInput) {
            phoneInput.addEventListener('input', function() {
                // Garder seulement les chiffres et les caractères autorisés
                this.value = this.value.replace(/[^\d\s\+\-\(\)]/g, '');
            });
        }
    }

    // ============================================
    // SOUMISSION DU FORMULAIRE
    // ============================================
    
    /**
     * Initialise la gestion de la soumission du formulaire
     * @param {HTMLFormElement} form - Formulaire
     * @param {HTMLElement} submitBtn - Bouton de soumission
     */
    function initFormSubmission(form, submitBtn) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Validation finale de toutes les étapes
            if (!validateAllSteps()) {
                return;
            }
            
            // Animation du bouton de soumission
            if (submitBtn) {
                submitBtn.classList.add('loading');
                submitBtn.disabled = true;
            }
            
            // Soumettre le formulaire après un délai pour l'animation
            setTimeout(() => {
                formModified = false;
                form.submit();
            }, 500);
        });
    }
    
    /**
     * Valide toutes les étapes du formulaire
     * @returns {boolean} - True si tout est valide
     */
    function validateAllSteps() {
        for (let step = 1; step <= CONFIG.totalSteps; step++) {
            if (!validateStep(step)) {
                showStep(step);
                showNotification('Veuillez remplir tous les champs obligatoires', 'error');
                return false;
            }
        }
        return true;
    }

    // ============================================
    // ANIMATIONS ET INTERACTIONS
    // ============================================
    
    /**
     * Initialise les animations des champs de formulaire
     */
    function initFormAnimations() {
        document.querySelectorAll('.form-control-modern').forEach(input => {
            input.addEventListener('focus', function() {
                this.parentElement.classList.add('focused');
            });
            
            input.addEventListener('blur', function() {
                this.parentElement.classList.remove('focused');
            });
        });
    }
    
    /**
     * Initialise les interactions avec les cartes de type d'adresse
     */
    function initTypeCardInteractions() {
        const typeCards = document.querySelectorAll('.type-card');
        
        typeCards.forEach(card => {
            card.addEventListener('click', function() {
                const radio = this.querySelector('input[type="radio"]');
                if (radio) {
                    radio.checked = true;
                    
                    // Animation de sélection
                    typeCards.forEach(c => c.style.transform = 'scale(1)');
                    this.style.transform = 'scale(1.02)';
                    
                    setTimeout(() => {
                        this.style.transform = 'scale(1)';
                    }, 200);
                }
            });
        });
    }

    // ============================================
    // AUTO-COMPLÉTION INTELLIGENTE
    // ============================================
    
    /**
     * Initialise l'auto-complétion pour les villes
     */
    function initAutoCompletion() {
        const cityInput = document.getElementById('city');
        const countrySelect = document.getElementById('country');
        
        if (!cityInput || !countrySelect) return;
        
        cityInput.addEventListener('input', function() {
            const value = this.value.toLowerCase();
            
            if (countrySelect.value === 'Gabon' && value.length >= 2) {
                const matches = CONFIG.gabonCities.filter(city => 
                    city.toLowerCase().startsWith(value)
                );
                
                if (matches.length > 0 && matches[0].toLowerCase() !== value) {
                    // Suggestion disponible
                    console.log('💡 Suggestion:', matches[0]);
                    // Ici, vous pouvez implémenter une liste déroulante de suggestions
                }
            }
        });
    }

    // ============================================
    // GESTION DES ERREURS DJANGO
    // ============================================
    
    /**
     * Gère l'affichage des erreurs Django
     */
    function handleDjangoErrors() {
        const djangoErrors = document.querySelectorAll('.errorlist');
        
        djangoErrors.forEach(errorList => {
            const field = errorList.previousElementSibling;
            
            if (field && field.classList.contains('form-control-modern')) {
                field.classList.add('is-invalid');
                
                const errors = Array.from(errorList.querySelectorAll('li'))
                    .map(li => li.textContent);
                
                const feedback = getFeedbackElement(field);
                
                if (feedback) {
                    feedback.textContent = errors.join(', ');
                    feedback.style.display = 'block';
                }
            }
        });
    }

    // ============================================
    // SYSTÈME DE NOTIFICATIONS
    // ============================================
    
    /**
     * Affiche une notification toast
     * @param {string} message - Message à afficher
     * @param {string} type - Type de notification (success, error, info, warning)
     */
    function showNotification(message, type = 'info') {
        const colors = {
            success: '#28a745',
            error: '#dc3545',
            info: '#17a2b8',
            warning: '#ffc107'
        };
        
        const icons = {
            success: 'check-circle',
            error: 'exclamation-circle',
            info: 'info-circle',
            warning: 'exclamation-triangle'
        };
        
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <i class="fas fa-${icons[type]}"></i>
                <span>${message}</span>
            </div>
        `;
        
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 16px 24px;
            background: ${colors[type]};
            color: white;
            border-radius: 12px;
            box-shadow: 0 8px 25px rgba(0,0,0,0.2);
            z-index: 10000;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 12px;
            animation: slideInRight 0.3s ease;
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.style.opacity = '0';
            notification.style.transform = 'translateX(100%)';
            notification.style.transition = 'all 0.3s ease';
            setTimeout(() => notification.remove(), 300);
        }, 5000);
    }

    // ============================================
    // RACCOURCIS CLAVIER
    // ============================================
    
    /**
     * Initialise les raccourcis clavier
     * @param {HTMLFormElement} form - Formulaire
     */
    function initKeyboardShortcuts(form) {
        document.addEventListener('keydown', function(e) {
            // Enter pour passer à l'étape suivante (sauf dans textarea)
            if (e.key === 'Enter' && currentStep < CONFIG.totalSteps && e.target.tagName !== 'TEXTAREA') {
                e.preventDefault();
                const nextBtn = document.querySelector(`.form-step[data-step="${currentStep}"] .btn-next`);
                if (nextBtn) {
                    nextBtn.click();
                }
            }
            
            // Ctrl+S pour sauvegarder
            if ((e.ctrlKey || e.metaKey) && e.key === 's') {
                e.preventDefault();
                if (currentStep === CONFIG.totalSteps) {
                    form.dispatchEvent(new Event('submit'));
                }
            }
        });
    }

    // ============================================
    // CONFIRMATION AVANT QUITTER
    // ============================================
    
    /**
     * Initialise l'avertissement de changements non sauvegardés
     * @param {HTMLFormElement} form - Formulaire
     */
    function initUnsavedChangesWarning(form) {
        form.addEventListener('input', function() {
            formModified = true;
        });
        
        window.addEventListener('beforeunload', function(e) {
            const submitBtn = document.querySelector('.btn-submit');
            if (formModified && submitBtn && !submitBtn.classList.contains('loading')) {
                e.preventDefault();
                e.returnValue = '';
            }
        });
        
        form.addEventListener('submit', function() {
            formModified = false;
        });
    }

    // ============================================
    // EFFET PARALLAX
    // ============================================
    
    /**
     * Initialise l'effet parallax sur le hero
     */
    function initParallaxEffect() {
        let ticking = false;
        
        window.addEventListener('scroll', function() {
            if (!ticking) {
                window.requestAnimationFrame(function() {
                    const scrolled = window.pageYOffset;
                    const hero = document.querySelector('.form-hero');
                    
                    if (hero && scrolled < hero.offsetHeight) {
                        hero.style.transform = `translateY(${scrolled * 0.3}px)`;
                    }
                    
                    ticking = false;
                });
                
                ticking = true;
            }
        });
    }

    // ============================================
    // ANIMATION CSS KEYFRAMES
    // ============================================
    
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slideInRight {
            from {
                opacity: 0;
                transform: translateX(100%);
            }
            to {
                opacity: 1;
                transform: translateX(0);
            }
        }
        
        .notification-content {
            display: flex;
            align-items: center;
            gap: 12px;
        }
        
        .notification-content i {
            font-size: 1.25rem;
        }
    `;
    document.head.appendChild(style);

})();