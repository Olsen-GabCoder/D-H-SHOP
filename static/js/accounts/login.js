/**
 * ========================================
 * LOGIN.JS - Page de Connexion
 * ========================================
 * Gestion de la validation, interactions et animations
 * de la page de connexion
 */

(function() {
    'use strict';

    // ============================================
    // INITIALISATION AU CHARGEMENT DU DOM
    // ============================================
    document.addEventListener('DOMContentLoaded', function() {
        initLoginPage();
    });

    /**
     * Initialisation principale de la page de connexion
     */
    function initLoginPage() {
        // Récupération des éléments
        const elements = getElements();
        
        // Initialisation des fonctionnalités
        initPasswordToggle(elements);
        initFormValidation(elements);
        initFormSubmission(elements);
        initSocialButtons();
        initInputAnimations();
        initKeyboardShortcuts(elements);
        initAlertAutoDismiss();
        initAutoFocus(elements);
        initRememberMe(elements);
        initAnimatedShapes();
        initCapsLockDetection(elements);
        
        console.log('✅ Page de connexion initialisée');
    }

    /**
     * Récupération de tous les éléments DOM nécessaires
     */
    function getElements() {
        return {
            loginForm: document.getElementById('login-form'),
            loginBtn: document.getElementById('login-btn'),
            usernameInput: document.getElementById('username'),
            passwordInput: document.getElementById('password'),
            togglePassword: document.getElementById('toggle-password'),
            rememberCheckbox: document.getElementById('remember-me')
        };
    }

    // ============================================
    // TOGGLE MOT DE PASSE
    // ============================================
    function initPasswordToggle(elements) {
        const { togglePassword, passwordInput } = elements;
        
        if (!togglePassword || !passwordInput) return;
        
        togglePassword.addEventListener('click', function() {
            const icon = this.querySelector('i');
            
            if (passwordInput.type === 'password') {
                passwordInput.type = 'text';
                icon.classList.remove('fa-eye');
                icon.classList.add('fa-eye-slash');
            } else {
                passwordInput.type = 'password';
                icon.classList.remove('fa-eye-slash');
                icon.classList.add('fa-eye');
            }
        });
    }

    // ============================================
    // VALIDATION DU FORMULAIRE
    // ============================================
    function initFormValidation(elements) {
        const { usernameInput, passwordInput } = elements;
        
        if (usernameInput) {
            usernameInput.addEventListener('blur', validateUsername);
            usernameInput.addEventListener('input', function() {
                if (this.classList.contains('error')) {
                    validateUsername();
                }
            });
        }
        
        if (passwordInput) {
            passwordInput.addEventListener('blur', validatePassword);
            passwordInput.addEventListener('input', function() {
                if (this.classList.contains('error')) {
                    validatePassword();
                }
            });
        }
    }

    /**
     * Validation du nom d'utilisateur
     */
    function validateUsername() {
        const usernameInput = document.getElementById('username');
        const value = usernameInput.value.trim();
        const errorDiv = document.getElementById('username-error');
        
        if (!value) {
            showFieldError(usernameInput, errorDiv, 'Le nom d\'utilisateur est requis');
            return false;
        } else if (value.length < 3) {
            showFieldError(usernameInput, errorDiv, 'Le nom d\'utilisateur doit contenir au moins 3 caractères');
            return false;
        } else {
            hideFieldError(usernameInput, errorDiv);
            return true;
        }
    }

    /**
     * Validation du mot de passe
     */
    function validatePassword() {
        const passwordInput = document.getElementById('password');
        const value = passwordInput.value;
        const errorDiv = document.getElementById('password-error');
        
        if (!value) {
            showFieldError(passwordInput, errorDiv, 'Le mot de passe est requis');
            return false;
        } else if (value.length < 6) {
            showFieldError(passwordInput, errorDiv, 'Le mot de passe doit contenir au moins 6 caractères');
            return false;
        } else {
            hideFieldError(passwordInput, errorDiv);
            return true;
        }
    }

    /**
     * Afficher une erreur de champ
     */
    function showFieldError(input, errorDiv, message) {
        input.classList.add('error');
        errorDiv.textContent = message;
        errorDiv.classList.add('show');
    }

    /**
     * Masquer une erreur de champ
     */
    function hideFieldError(input, errorDiv) {
        input.classList.remove('error');
        errorDiv.classList.remove('show');
    }

    // ============================================
    // SOUMISSION DU FORMULAIRE
    // ============================================
    function initFormSubmission(elements) {
        const { loginForm, loginBtn } = elements;
        
        if (!loginForm) return;
        
        loginForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Validation complète
            const isUsernameValid = validateUsername();
            const isPasswordValid = validatePassword();
            
            if (!isUsernameValid || !isPasswordValid) {
                showNotification('Veuillez corriger les erreurs dans le formulaire', 'error');
                return;
            }
            
            // Animation du bouton
            const btnText = loginBtn.querySelector('.btn-text');
            const btnLoading = loginBtn.querySelector('.btn-loading');
            
            btnText.style.display = 'none';
            btnLoading.style.display = 'flex';
            loginBtn.disabled = true;
            
            // Tracking analytics (optionnel)
            trackEvent('login_attempt', 'form_submission');
            
            // Soumettre le formulaire
            this.submit();
        });
    }

    // ============================================
    // CONNEXION SOCIALE
    // ============================================
    function initSocialButtons() {
        const socialButtons = document.querySelectorAll('.social-btn');
        
        socialButtons.forEach(btn => {
            btn.addEventListener('click', function() {
                const platform = this.classList.contains('google') ? 'Google' : 'Facebook';
                showNotification(`Connexion via ${platform} - Fonctionnalité à venir`, 'info');
                
                // Tracking analytics
                const platformLower = platform.toLowerCase();
                trackEvent('social_login_click', platformLower);
            });
        });
    }

    // ============================================
    // SYSTÈME DE NOTIFICATIONS
    // ============================================
    window.showNotification = function(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = 'toast-notification';
        
        const icons = {
            success: 'check-circle',
            error: 'times-circle',
            warning: 'exclamation-triangle',
            info: 'info-circle'
        };
        
        const colors = {
            success: '#28a745',
            error: '#dc3545',
            warning: '#ffc107',
            info: '#17a2b8'
        };
        
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: ${colors[type] || colors.info};
            color: white;
            padding: 1rem 1.5rem;
            border-radius: 12px;
            box-shadow: 0 8px 30px rgba(0,0,0,0.3);
            z-index: 10000;
            display: flex;
            align-items: center;
            gap: 0.75rem;
            animation: slideInRight 0.3s ease;
            max-width: 400px;
        `;
        
        notification.innerHTML = `
            <i class="fas fa-${icons[type] || icons.info}" style="font-size: 1.25rem;"></i>
            <span style="flex: 1;">${message}</span>
            <button onclick="this.parentElement.remove()" style="background: none; border: none; color: white; cursor: pointer; padding: 0; margin-left: 10px;">
                <i class="fas fa-times"></i>
            </button>
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.style.animation = 'slideOutRight 0.3s ease';
            setTimeout(() => notification.remove(), 300);
        }, 5000);
    };

    // ============================================
    // ANIMATION DES INPUTS
    // ============================================
    function initInputAnimations() {
        const inputs = document.querySelectorAll('.form-input-modern');
        
        inputs.forEach(input => {
            input.addEventListener('focus', function() {
                this.parentElement.style.transform = 'scale(1.01)';
            });
            
            input.addEventListener('blur', function() {
                this.parentElement.style.transform = 'scale(1)';
            });
        });
    }

    // ============================================
    // RACCOURCIS CLAVIER
    // ============================================
    function initKeyboardShortcuts(elements) {
        const { usernameInput, passwordInput, loginForm } = elements;
        
        document.addEventListener('keydown', function(e) {
            // Enter pour soumettre
            if (e.key === 'Enter' && !e.shiftKey) {
                if (document.activeElement === usernameInput || 
                    document.activeElement === passwordInput) {
                    e.preventDefault();
                    loginForm.dispatchEvent(new Event('submit'));
                }
            }
        });
    }

    // ============================================
    // AUTO-DISMISS DES ALERTES
    // ============================================
    function initAlertAutoDismiss() {
        const alerts = document.querySelectorAll('.alert-modern');
        
        alerts.forEach(alert => {
            setTimeout(() => {
                alert.style.animation = 'slideOutUp 0.3s ease';
                setTimeout(() => alert.remove(), 300);
            }, 8000);
        });
    }

    // ============================================
    // FOCUS AUTOMATIQUE
    // ============================================
    function initAutoFocus(elements) {
        const { usernameInput } = elements;
        
        if (usernameInput && !usernameInput.value) {
            setTimeout(() => {
                usernameInput.focus();
            }, 500);
        }
    }

    // ============================================
    // REMEMBER ME PERSISTANCE
    // ============================================
    function initRememberMe(elements) {
        const { rememberCheckbox, usernameInput } = elements;
        
        if (!rememberCheckbox || !usernameInput) return;
        
        // Charger la préférence
        const savedUsername = localStorage.getItem('remembered_username');
        if (savedUsername) {
            usernameInput.value = savedUsername;
            rememberCheckbox.checked = true;
        }
        
        // Sauvegarder au changement
        rememberCheckbox.addEventListener('change', function() {
            if (this.checked) {
                localStorage.setItem('remembered_username', usernameInput.value);
            } else {
                localStorage.removeItem('remembered_username');
            }
        });
        
        // Mettre à jour si l'utilisateur change le username
        usernameInput.addEventListener('input', function() {
            if (rememberCheckbox.checked) {
                localStorage.setItem('remembered_username', this.value);
            }
        });
    }

    // ============================================
    // ANIMATION DES FORMES
    // ============================================
    function initAnimatedShapes() {
        const shapes = document.querySelectorAll('.shape');
        
        shapes.forEach((shape, index) => {
            shape.style.animationDelay = `${-index * 7}s`;
        });
    }

    // ============================================
    // DÉTECTION DE CAPS LOCK
    // ============================================
    function initCapsLockDetection(elements) {
        const { passwordInput } = elements;
        
        if (!passwordInput) return;
        
        passwordInput.addEventListener('keyup', function(e) {
            const isCapsLock = e.getModifierState && e.getModifierState('CapsLock');
            const errorDiv = document.getElementById('password-error');
            
            if (isCapsLock) {
                const warningColor = getComputedStyle(document.documentElement)
                    .getPropertyValue('--warning-color')
                    .trim();

                errorDiv.textContent = '⚠️ Attention : La touche Caps Lock est activée';
                errorDiv.style.color = warningColor;
                errorDiv.classList.add('show');
            } else if (!this.classList.contains('error')) {
                errorDiv.classList.remove('show');
            }
        });
    }

    // ============================================
    // ANALYTICS (OPTIONNEL)
    // ============================================
    function trackEvent(action, label) {
        if (typeof gtag !== 'undefined') {
            gtag('event', action, {
                'event_category': 'Authentication',
                'event_label': label
            });
        }
        
        // Log pour debug
        console.log('📊 Analytics:', action, label);
    }

    // ============================================
    // DÉTECTION DE LA LANGUE DU NAVIGATEUR
    // ============================================
    const browserLang = navigator.language || navigator.userLanguage;
    console.log('🌐 Langue du navigateur:', browserLang);

})();