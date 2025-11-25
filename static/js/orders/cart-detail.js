/**
 * ========================================
 * CART-DETAIL.JS - Page Panier
 * ========================================
 */

(function() {
    'use strict';

    // ============================================
    // VARIABLES GLOBALES
    // ============================================
    const loadingOverlay = document.getElementById('loadingOverlay');
    const clearCartForm = document.getElementById('clear-cart-form');
    const saveForLaterBtn = document.getElementById('save-for-later-btn');
    const couponForm = document.getElementById('coupon-form');
    const couponInput = document.getElementById('coupon-code-input');
    const couponMessage = document.getElementById('coupon-message');

    // ============================================
    // FONCTIONS UTILITAIRES
    // ============================================
    
    /**
     * Affiche l'overlay de chargement
     */
    function showLoading() {
        if (loadingOverlay) {
            loadingOverlay.classList.add('active');
        }
    }

    /**
     * Masque l'overlay de chargement
     */
    function hideLoading() {
        if (loadingOverlay) {
            loadingOverlay.classList.remove('active');
        }
    }

    /**
     * Affiche une notification toast
     * @param {string} message - Message à afficher
     * @param {string} type - Type de notification (success, error, warning, info)
     */
    function showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        
        const colors = {
            success: '#28a745',
            error: '#dc3545',
            warning: '#ffc107',
            info: '#17a2b8'
        };
        
        const icons = {
            success: 'check-circle',
            error: 'times-circle',
            warning: 'exclamation-triangle',
            info: 'info-circle'
        };
        
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: ${colors[type]};
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
            <i class="fas fa-${icons[type]}" style="font-size: 1.25rem;"></i>
            <span style="flex: 1;">${message}</span>
            <button onclick="this.parentElement.remove()" style="background: none; border: none; color: white; cursor: pointer; font-size: 1.25rem;">
                <i class="fas fa-times"></i>
            </button>
        `;
        
        document.body.appendChild(notification);
        
        // Auto-dismiss après 5 secondes
        setTimeout(() => {
            notification.style.animation = 'slideOutRight 0.3s ease';
            setTimeout(() => notification.remove(), 300);
        }, 5000);
    }

    /**
     * Désactive tous les boutons et liens
     */
    function disableAllInteractions() {
        document.querySelectorAll('button, a.btn').forEach(element => {
            element.classList.add('disabled');
            if (element.tagName === 'BUTTON') {
                element.disabled = true;
            }
        });
    }

    // ============================================
    // GESTION DES QUANTITÉS
    // ============================================
    
    /**
     * Soumet le formulaire de mise à jour de quantité
     * @param {HTMLFormElement} form - Formulaire à soumettre
     */
    function submitQuantityUpdate(form) {
        showLoading();
        
        // Désactiver tous les boutons de quantité pendant la mise à jour
        document.querySelectorAll('.qty-btn').forEach(btn => {
            btn.disabled = true;
        });
        
        form.submit();
    }

    /**
     * Initialise les contrôles de quantité
     */
    function initQuantityControls() {
        document.querySelectorAll('.quantity-selector-modern').forEach(selector => {
            const decreaseBtn = selector.querySelector('.qty-btn.decrease');
            const increaseBtn = selector.querySelector('.qty-btn.increase');
            const input = selector.querySelector('.qty-input');
            const form = selector.closest('.quantity-form');
            
            if (!decreaseBtn || !increaseBtn || !input || !form) return;
            
            // Bouton diminuer
            decreaseBtn.addEventListener('click', function(e) {
                e.preventDefault();
                
                const currentValue = parseInt(input.value);
                
                if (currentValue > 1) {
                    input.value = currentValue - 1;
                    
                    // Mettre à jour l'état des boutons
                    if (currentValue - 1 === 1) {
                        decreaseBtn.disabled = true;
                    }
                    increaseBtn.disabled = false;
                    
                    // Soumettre la mise à jour
                    submitQuantityUpdate(form);
                }
            });
            
            // Bouton augmenter
            increaseBtn.addEventListener('click', function(e) {
                e.preventDefault();
                
                const currentValue = parseInt(input.value);
                const maxValue = parseInt(input.max);
                
                if (currentValue < maxValue) {
                    input.value = currentValue + 1;
                    
                    // Mettre à jour l'état des boutons
                    if (currentValue + 1 >= maxValue) {
                        increaseBtn.disabled = true;
                    }
                    decreaseBtn.disabled = false;
                    
                    // Soumettre la mise à jour
                    submitQuantityUpdate(form);
                } else {
                    showNotification(`Quantité maximale disponible : ${maxValue}`, 'warning');
                }
            });
        });
    }

    // ============================================
    // SUPPRESSION D'ARTICLE
    // ============================================
    
    /**
     * Initialise les formulaires de suppression d'article
     */
    function initRemoveForms() {
        document.querySelectorAll('.remove-form').forEach(form => {
            form.addEventListener('submit', function(e) {
                e.preventDefault();
                
                const cartItem = this.closest('.cart-item-modern');
                const productName = cartItem.querySelector('.item-name a')?.textContent.trim() || 'cet article';
                
                if (confirm(`Êtes-vous sûr de vouloir retirer "${productName}" de votre panier ?`)) {
                    showLoading();
                    
                    // Animation de sortie
                    cartItem.style.transition = 'all 0.5s ease';
                    cartItem.style.opacity = '0';
                    cartItem.style.transform = 'translateX(-100%)';
                    
                    // Attendre la fin de l'animation avant de soumettre
                    setTimeout(() => {
                        this.submit();
                    }, 500);
                }
            });
        });
    }

    // ============================================
    // VIDER LE PANIER
    // ============================================
    
    /**
     * Initialise le formulaire de vidage du panier
     */
    function initClearCartForm() {
        if (!clearCartForm) return;
        
        clearCartForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const itemCount = document.querySelectorAll('.cart-item-modern').length;
            
            if (itemCount === 0) {
                showNotification('Votre panier est déjà vide', 'info');
                return;
            }
            
            if (confirm(`Êtes-vous sûr de vouloir supprimer tous les articles (${itemCount}) de votre panier ?`)) {
                showLoading();
                
                // Animation en cascade pour tous les items
                const items = document.querySelectorAll('.cart-item-modern');
                items.forEach((item, index) => {
                    setTimeout(() => {
                        item.style.transition = 'all 0.3s ease';
                        item.style.opacity = '0';
                        item.style.transform = 'translateX(-100%)';
                    }, index * 50);
                });
                
                // Attendre que toutes les animations soient terminées
                setTimeout(() => {
                    this.submit();
                }, items.length * 50 + 300);
            }
        });
    }

    // ============================================
    // SAUVEGARDER POUR PLUS TARD
    // ============================================
    
    /**
     * Initialise le bouton "Sauvegarder pour plus tard"
     */
    function initSaveForLater() {
        if (!saveForLaterBtn) return;
        
        saveForLaterBtn.addEventListener('click', function() {
            showNotification('Fonctionnalité bientôt disponible ! Vos articles seront sauvegardés.', 'info');
        });
    }

    // ============================================
    // GESTION DES CODES PROMO
    // ============================================
    
    /**
     * Applique un code promo
     * @param {string} code - Code promo à appliquer
     */
    function applyCouponCode(code) {
        if (!code) {
            couponMessage.innerHTML = '<div class="alert alert-warning mt-3"><i class="fas fa-exclamation-triangle me-2"></i>Veuillez entrer un code promo</div>';
            return;
        }
        
        const submitBtn = couponForm.querySelector('.btn-apply-coupon');
        const originalContent = submitBtn.innerHTML;
        
        // Afficher l'état de chargement
        submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Vérification...';
        submitBtn.disabled = true;
        
        // Simuler une vérification (à remplacer par un appel AJAX réel)
        setTimeout(() => {
            const validCodes = {
                'BIENVENUE20': { 
                    type: 'percentage', 
                    value: 20, 
                    message: '20% de réduction appliquée !' 
                },
                'ETE2024': { 
                    type: 'percentage', 
                    value: 10, 
                    message: '10% de réduction appliquée !' 
                },
                'FRAIS-PORT': { 
                    type: 'fixed', 
                    value: 0, 
                    message: 'Livraison gratuite appliquée !' 
                }
            };
            
            if (validCodes[code]) {
                const discount = validCodes[code];
                
                // Afficher le message de succès
                couponMessage.innerHTML = `
                    <div class="alert alert-success mt-3">
                        <i class="fas fa-check-circle me-2"></i>${discount.message}
                    </div>
                `;
                
                // Mettre à jour l'affichage du total
                updateCartTotal(discount);
                
                showNotification('Code promo appliqué avec succès !', 'success');
                
                // Fermer le modal après 2 secondes
                setTimeout(() => {
                    const modalElement = document.getElementById('couponModal');
                    if (modalElement && typeof bootstrap !== 'undefined') {
                        const modal = bootstrap.Modal.getInstance(modalElement);
                        if (modal) modal.hide();
                    }
                    couponInput.value = '';
                }, 2000);
                
            } else {
                couponMessage.innerHTML = `
                    <div class="alert alert-danger mt-3">
                        <i class="fas fa-times-circle me-2"></i>Code promo invalide ou expiré
                    </div>
                `;
                showNotification('Code promo invalide', 'error');
            }
            
            // Restaurer le bouton
            submitBtn.innerHTML = originalContent;
            submitBtn.disabled = false;
            
        }, 1000);
    }

    /**
     * Met à jour l'affichage du total avec la réduction
     * @param {Object} discount - Objet contenant les informations de réduction
     */
    function updateCartTotal(discount) {
        const discountRow = document.getElementById('discount-row');
        const discountAmount = document.getElementById('discount-amount');
        const totalDisplay = document.getElementById('total-display');
        const subtotalDisplay = document.getElementById('subtotal-display');
        
        if (!discountRow || !discountAmount || !totalDisplay || !subtotalDisplay) return;
        
        // Extraire le montant actuel
        const currentTotal = parseFloat(subtotalDisplay.textContent.replace(/\D/g, ''));
        let discountValue = 0;
        
        // Calculer la réduction
        if (discount.type === 'percentage') {
            discountValue = currentTotal * (discount.value / 100);
        } else if (discount.type === 'fixed') {
            discountValue = discount.value;
        }
        
        // Afficher la réduction
        discountAmount.textContent = '- ' + discountValue.toLocaleString('fr-FR') + ' FCFA';
        discountRow.classList.remove('d-none');
        
        // Calculer et afficher le nouveau total
        const newTotal = currentTotal - discountValue;
        totalDisplay.textContent = newTotal.toLocaleString('fr-FR') + ' FCFA';
    }

    /**
     * Initialise le formulaire de code promo
     */
    function initCouponForm() {
        if (!couponForm) return;
        
        couponForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const code = couponInput.value.trim().toUpperCase();
            applyCouponCode(code);
        });
        
        // Application rapide des codes
        document.querySelectorAll('.btn-quick-apply').forEach(btn => {
            btn.addEventListener('click', function() {
                const code = this.dataset.code;
                if (couponInput) {
                    couponInput.value = code;
                    couponForm.dispatchEvent(new Event('submit'));
                }
            });
        });
    }

    // ============================================
    // ANIMATIONS AU SCROLL
    // ============================================
    
    /**
     * Initialise les animations au scroll pour les items du panier
     */
    function initScrollAnimations() {
        const cartItems = document.querySelectorAll('.cart-item-modern');
        
        if (cartItems.length === 0) return;
        
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };
        
        const itemObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const target = entry.target;
                    
                    // État initial
                    target.style.opacity = '0';
                    target.style.transform = 'translateY(20px)';
                    
                    // Animation d'entrée
                    setTimeout(() => {
                        target.style.transition = 'all 0.6s ease';
                        target.style.opacity = '1';
                        target.style.transform = 'translateY(0)';
                    }, 100);
                    
                    // Ne plus observer cet élément
                    itemObserver.unobserve(target);
                }
            });
        }, observerOptions);
        
        cartItems.forEach(item => {
            itemObserver.observe(item);
        });
    }

    // ============================================
    // GESTION DES FORMULAIRES
    // ============================================
    
    /**
     * Désactive les interactions lors de la soumission d'un formulaire
     */
    function initFormSubmissions() {
        document.querySelectorAll('form').forEach(form => {
            form.addEventListener('submit', function(e) {
                // Ne pas désactiver si c'est le formulaire de code promo
                if (this.id === 'coupon-form') return;
                
                disableAllInteractions();
            });
        });
    }

    // ============================================
    // GESTION RÉSEAU
    // ============================================
    
    /**
     * Initialise les gestionnaires d'événements réseau
     */
    function initNetworkHandlers() {
        window.addEventListener('online', function() {
            showNotification('Connexion rétablie', 'success');
        });
        
        window.addEventListener('offline', function() {
            showNotification('Connexion internet perdue', 'error');
            hideLoading();
        });
    }

    // ============================================
    // ACCESSIBILITÉ
    // ============================================
    
    /**
     * Améliore l'accessibilité des éléments interactifs
     */
    function enhanceAccessibility() {
        // Labels pour les boutons de quantité
        document.querySelectorAll('.qty-btn.decrease').forEach(btn => {
            btn.setAttribute('aria-label', 'Diminuer la quantité');
        });
        
        document.querySelectorAll('.qty-btn.increase').forEach(btn => {
            btn.setAttribute('aria-label', 'Augmenter la quantité');
        });
        
        // Labels pour les boutons de suppression
        document.querySelectorAll('.btn-remove-item').forEach(btn => {
            const cartItem = btn.closest('.cart-item-modern');
            const productName = cartItem?.querySelector('.item-name a')?.textContent.trim() || 'cet article';
            btn.setAttribute('aria-label', `Retirer ${productName} du panier`);
        });
    }

    // ============================================
    // INITIALISATION
    // ============================================
    
    /**
     * Fonction d'initialisation principale
     */
    function init() {
        console.log('🛒 Initialisation de la page panier...');
        
        // Initialiser tous les modules
        initQuantityControls();
        initRemoveForms();
        initClearCartForm();
        initSaveForLater();
        initCouponForm();
        initScrollAnimations();
        initFormSubmissions();
        initNetworkHandlers();
        enhanceAccessibility();
        
        // Statistiques
        const cartItemsCount = document.querySelectorAll('.cart-item-modern').length;
        console.log('✅ Page panier chargée');
        console.log(`📊 Total articles: ${cartItemsCount}`);
    }

    // Démarrer l'initialisation au chargement du DOM
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

})();