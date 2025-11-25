/* ========================================
   CHECKOUT.JS - Page de Validation
   ======================================== */

(function() {
    'use strict';
    
    // ============================================
    // VARIABLES GLOBALES
    // ============================================
    const loadingOverlay = document.getElementById('loadingOverlay');
    const checkoutForm = document.getElementById('checkout-form');
    const confirmOrderBtn = document.getElementById('confirm-order-btn');
    
    // ✅ CORRECTION : Lecture sécurisée des données
    // window.CHECKOUT_DATA est maintenant déjà un objet, plus besoin de JSON.parse
    const subtotalAmount = typeof window.CHECKOUT_DATA?.subtotal === 'number' 
        ? window.CHECKOUT_DATA.subtotal 
        : parseFloat(window.CHECKOUT_DATA?.subtotal || 0);
        
    const checkoutUrl = window.CHECKOUT_DATA?.checkoutUrl || '/orders/checkout/';
    const addressAddUrl = window.CHECKOUT_DATA?.addressAddUrl || '/accounts/address/add/';
    
    // ============================================
    // FONCTIONS UTILITAIRES
    // ============================================
    
    /**
     * Afficher l'overlay de chargement
     */
    function showLoading() {
        if (loadingOverlay) {
            loadingOverlay.classList.add('active');
        }
    }
    
    /**
     * Masquer l'overlay de chargement
     */
    function hideLoading() {
        if (loadingOverlay) {
            loadingOverlay.classList.remove('active');
        }
    }
    
    /**
     * Afficher une notification toast
     * @param {string} message - Message à afficher
     * @param {string} type - Type de notification (success, error, warning, info)
     */
    function showNotification(message, type = 'info') {
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
        
        const notification = document.createElement('div');
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
            <button onclick="this.parentElement.remove()" style="background: none; border: none; color: white; cursor: pointer;">
                <i class="fas fa-times"></i>
            </button>
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.style.animation = 'slideOutRight 0.3s ease';
            setTimeout(() => notification.remove(), 300);
        }, 5000);
    }
    
    // ============================================
    // SÉLECTION ADRESSE
    // ============================================
    
    /**
     * Initialiser la sélection des adresses
     */
    function initAddressSelection() {
        const addressRadios = document.querySelectorAll('.address-radio');
        
        addressRadios.forEach(radio => {
            radio.addEventListener('change', function() {
                // Retirer la sélection de toutes les cartes
                document.querySelectorAll('.address-card-modern').forEach(card => {
                    card.classList.remove('selected');
                });
                
                // Ajouter la sélection à la carte parente
                const parentCard = this.closest('.address-card-modern');
                if (parentCard) {
                    parentCard.classList.add('selected');
                    showNotification('Adresse de livraison mise à jour', 'info');
                }
            });
        });
    }
    
    // ============================================
    // SÉLECTION MODE DE LIVRAISON
    // ============================================
    
    /**
     * Mettre à jour les coûts de livraison et le total
     */
    function updateShippingCost() {
        const selectedRadio = document.querySelector('.shipping-rate-radio:checked');
        const shippingCostDisplay = document.getElementById('shipping-cost-display');
        const totalDisplay = document.getElementById('total-display');
        
        if (!selectedRadio) {
            if (shippingCostDisplay) {
                shippingCostDisplay.innerHTML = '<span class="free-tag">Gratuite</span>';
            }
            if (totalDisplay) {
                totalDisplay.textContent = subtotalAmount.toLocaleString('fr-FR') + ' FCFA';
            }
            return;
        }
        
        const shippingCost = parseFloat(selectedRadio.dataset.cost) || 0;
        const isFree = selectedRadio.dataset.isFree === 'true';
        
        // Mise à jour affichage livraison
        if (shippingCostDisplay) {
            if (isFree || shippingCost === 0) {
                shippingCostDisplay.innerHTML = '<span class="free-tag">Gratuite</span>';
            } else {
                shippingCostDisplay.textContent = shippingCost.toLocaleString('fr-FR') + ' FCFA';
            }
        }
        
        // Calcul réduction si applicable
        let discountAmount = 0;
        const discountDisplay = document.getElementById('discount-display');
        const discountRow = document.getElementById('discount-row');
        
        if (discountDisplay && discountRow && !discountRow.classList.contains('d-none')) {
            const discountText = discountDisplay.textContent.replace(/[^0-9]/g, '');
            discountAmount = parseFloat(discountText) || 0;
        }
        
        // Calcul total
        const newTotal = subtotalAmount + shippingCost - discountAmount;
        if (totalDisplay) {
            totalDisplay.textContent = newTotal.toLocaleString('fr-FR') + ' FCFA';
        }
    }
    
    /**
     * Initialiser la sélection des modes de livraison
     */
    function initShippingSelection() {
        const shippingRateRadios = document.querySelectorAll('.shipping-rate-radio');
        
        shippingRateRadios.forEach(radio => {
            radio.addEventListener('change', function() {
                // Retirer la sélection de toutes les cartes
                document.querySelectorAll('.shipping-option-card').forEach(card => {
                    card.classList.remove('selected');
                });
                
                // Ajouter la sélection à la carte parente
                const parentCard = this.closest('.shipping-option-card');
                if (parentCard) {
                    parentCard.classList.add('selected');
                }
                
                updateShippingCost();
                showNotification('Mode de livraison mis à jour', 'success');
            });
        });
        
        // Initialisation du coût
        updateShippingCost();
    }
    
    // ============================================
    // SÉLECTION MODE DE PAIEMENT
    // ============================================
    
    /**
     * Initialiser la sélection des modes de paiement
     */
    function initPaymentSelection() {
        const paymentRadios = document.querySelectorAll('.payment-radio');
        
        paymentRadios.forEach(radio => {
            radio.addEventListener('change', function() {
                // Retirer la sélection de toutes les cartes
                document.querySelectorAll('.payment-method-card-modern').forEach(card => {
                    card.classList.remove('selected');
                });
                
                // Ajouter la sélection à la carte parente
                const parentCard = this.closest('.payment-method-card-modern');
                if (parentCard) {
                    parentCard.classList.add('selected');
                    const paymentName = parentCard.querySelector('.payment-name').textContent;
                    showNotification(`Mode de paiement: ${paymentName}`, 'info');
                }
            });
        });
    }
    
    // ============================================
    // AJOUT NOUVELLE ADRESSE (AJAX)
    // ============================================
    
    /**
     * Initialiser le formulaire d'ajout d'adresse
     */
    function initAddAddressForm() {
        const saveAddressBtn = document.getElementById('save-address-btn');
        const addAddressForm = document.getElementById('add-address-form');
        
        if (!saveAddressBtn || !addAddressForm) return;
        
        saveAddressBtn.addEventListener('click', function() {
            // Validation du formulaire
            if (!addAddressForm.checkValidity()) {
                addAddressForm.reportValidity();
                return;
            }
            
            // Désactiver le bouton et afficher le loading
            const originalContent = this.innerHTML;
            this.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Enregistrement...';
            this.disabled = true;
            
            const formData = new FormData(addAddressForm);
            
            fetch(addressAddUrl, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => {
                if (response.ok) return response.json();
                throw new Error('Erreur serveur');
            })
            .then(data => {
                if (data.success) {
                    showNotification(data.message || 'Adresse enregistrée avec succès !', 'success');
                    
                    // Fermer le modal
                    const modalElement = document.getElementById('addAddressModal');
                    const modal = bootstrap.Modal.getInstance(modalElement);
                    if (modal) modal.hide();
                    
                    // Réinitialiser le formulaire
                    addAddressForm.reset();
                    
                    // Recharger la page après un court délai
                    setTimeout(() => {
                        window.location.href = checkoutUrl;
                    }, 1000);
                } else {
                    showNotification(data.message || 'Erreur lors de l\'enregistrement', 'error');
                    this.innerHTML = originalContent;
                    this.disabled = false;
                }
            })
            .catch(error => {
                console.error('Erreur:', error);
                showNotification('Erreur de connexion. Veuillez réessayer.', 'error');
                this.innerHTML = originalContent;
                this.disabled = false;
            });
        });
    }
    
    // ============================================
    // GESTION DES CODES PROMO
    // ============================================
    
    /**
     * Initialiser le système de codes promo
     */
    function initCouponSystem() {
        const couponForm = document.getElementById('coupon-form');
        const couponInput = document.getElementById('coupon-input');
        const couponMessage = document.getElementById('coupon-message');
        
        if (!couponForm) return;
        
        couponForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const code = couponInput.value.trim().toUpperCase();
            
            if (!code) {
                couponMessage.innerHTML = '<div class="alert alert-warning mt-3"><i class="fas fa-exclamation-triangle me-2"></i>Veuillez entrer un code promo</div>';
                return;
            }
            
            // Animation loading
            couponMessage.innerHTML = '<div class="alert alert-info mt-3"><span class="spinner-border spinner-border-sm me-2"></span>Vérification du code...</div>';
            
            // Simulation validation (à remplacer par vraie requête AJAX)
            setTimeout(() => {
                const validCodes = {
                    'BIENVENUE20': { type: 'percentage', value: 20, message: '20% de réduction appliquée !' },
                    'PROMO10': { type: 'percentage', value: 10, message: '10% de réduction appliquée !' },
                    'LIVRAISON-OFFERTE': { type: 'shipping', value: 0, message: 'Livraison gratuite appliquée !' }
                };
                
                if (validCodes[code]) {
                    const discount = validCodes[code];
                    
                    couponMessage.innerHTML = `<div class="alert alert-success mt-3"><i class="fas fa-check-circle me-2"></i>${discount.message}</div>`;
                    
                    const discountRow = document.getElementById('discount-row');
                    const discountDisplay = document.getElementById('discount-display');
                    const shippingCostDisplay = document.getElementById('shipping-cost-display');
                    
                    let discountValue = 0;
                    
                    if (discount.type === 'percentage') {
                        discountValue = subtotalAmount * (discount.value / 100);
                    } else if (discount.type === 'shipping') {
                        // Logique pour livraison gratuite
                        const shippingCostText = shippingCostDisplay.textContent.replace(/[^0-9]/g, '');
                        discountValue = parseFloat(shippingCostText) || 0;
                    }
                    
                    discountDisplay.textContent = '- ' + discountValue.toLocaleString('fr-FR') + ' FCFA';
                    discountRow.classList.remove('d-none');
                    
                    updateShippingCost();
                    showNotification('Code promo appliqué avec succès !', 'success');
                    
                    // Fermer le modal après succès
                    setTimeout(() => {
                        const modalElement = document.getElementById('couponModal');
                        const modal = bootstrap.Modal.getInstance(modalElement);
                        if (modal) modal.hide();
                        couponInput.value = '';
                    }, 2000);
                    
                } else {
                    couponMessage.innerHTML = '<div class="alert alert-danger mt-3"><i class="fas fa-times-circle me-2"></i>Code promo invalide ou expiré</div>';
                    showNotification('Code promo invalide', 'error');
                }
            }, 1000);
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
    // VALIDATION DU FORMULAIRE DE COMMANDE
    // ============================================
    
    /**
     * Initialiser la validation du formulaire
     */
    function initFormValidation() {
        if (!checkoutForm || !confirmOrderBtn) return;
        
        checkoutForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Vérification adresse sélectionnée
            const addressSelected = document.querySelector('input[name="address_id"]:checked');
            if (!addressSelected) {
                showNotification('Veuillez sélectionner une adresse de livraison', 'warning');
                const stepAddress = document.getElementById('step-address');
                if (stepAddress) {
                    stepAddress.scrollIntoView({ behavior: 'smooth', block: 'start' });
                }
                return;
            }
            
            // Vérification mode de livraison sélectionné
            const shippingRateSelected = document.querySelector('input[name="shipping_rate_id"]:checked');
            if (!shippingRateSelected) {
                showNotification('Veuillez sélectionner un mode de livraison', 'warning');
                const stepDelivery = document.getElementById('step-delivery');
                if (stepDelivery) {
                    stepDelivery.scrollIntoView({ behavior: 'smooth', block: 'start' });
                }
                return;
            }
            
            // Vérification acceptation des CGV
            const termsCheckbox = document.getElementById('accept-terms');
            if (!termsCheckbox || !termsCheckbox.checked) {
                showNotification('Veuillez accepter les conditions générales de vente', 'warning');
                if (termsCheckbox) {
                    termsCheckbox.focus();
                    const stepConfirm = document.getElementById('step-confirm');
                    if (stepConfirm) {
                        stepConfirm.scrollIntoView({ behavior: 'smooth', block: 'center' });
                    }
                }
                return;
            }
            
            // Animation du bouton
            confirmOrderBtn.classList.add('loading');
            confirmOrderBtn.disabled = true;
            
            showLoading();
            showNotification('Validation de votre commande en cours...', 'info');
            
            // Soumettre le formulaire après animation
            setTimeout(() => {
                checkoutForm.submit();
            }, 500);
        });
    }
    
    // ============================================
    // NAVIGATION ENTRE ÉTAPES
    // ============================================
    
    /**
     * Initialiser la navigation entre les étapes
     */
    function initStepNavigation() {
        const stepNumbers = document.querySelectorAll('.step-number-badge');
        const stepIds = ['step-address', 'step-delivery', 'step-payment', 'step-confirm'];
        
        stepNumbers.forEach((stepNumber, index) => {
            stepNumber.style.cursor = 'pointer';
            stepNumber.addEventListener('click', function() {
                if (stepIds[index]) {
                    const targetStep = document.getElementById(stepIds[index]);
                    if (targetStep) {
                        targetStep.scrollIntoView({ behavior: 'smooth', block: 'start' });
                    }
                }
            });
        });
    }
    
    // ============================================
    // VALIDATION EN TEMPS RÉEL
    // ============================================
    
    /**
     * Initialiser la validation en temps réel des champs
     */
    function initRealtimeValidation() {
        const requiredInputs = document.querySelectorAll('[required]');
        
        requiredInputs.forEach(input => {
            input.addEventListener('blur', function() {
                if (!this.value) {
                    this.classList.add('is-invalid');
                    this.classList.remove('is-valid');
                } else {
                    this.classList.remove('is-invalid');
                    this.classList.add('is-valid');
                }
            });
            
            input.addEventListener('input', function() {
                if (this.value) {
                    this.classList.remove('is-invalid');
                    this.classList.add('is-valid');
                }
            });
        });
    }
    
    // ============================================
    // ANIMATION AU SCROLL
    // ============================================
    
    /**
     * Initialiser les animations au scroll
     */
    function initScrollAnimations() {
        const steps = document.querySelectorAll('.checkout-step-modern');
        
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -100px 0px'
        };
        
        const stepObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.style.opacity = '0';
                    entry.target.style.transform = 'translateY(30px)';
                    
                    setTimeout(() => {
                        entry.target.style.transition = 'all 0.6s ease';
                        entry.target.style.opacity = '1';
                        entry.target.style.transform = 'translateY(0)';
                    }, 100);
                    
                    stepObserver.unobserve(entry.target);
                }
            });
        }, observerOptions);
        
        steps.forEach(step => {
            stepObserver.observe(step);
        });
    }
    
    // ============================================
    // GESTION DES MODALS
    // ============================================
    
    /**
     * Initialiser les gestionnaires de modals
     */
    function initModalHandlers() {
        // Modal d'ajout d'adresse
        const addAddressModal = document.getElementById('addAddressModal');
        if (addAddressModal) {
            addAddressModal.addEventListener('hidden.bs.modal', function () {
                const addAddressForm = document.getElementById('add-address-form');
                if (addAddressForm) {
                    addAddressForm.reset();
                    const inputs = addAddressForm.querySelectorAll('.is-valid, .is-invalid');
                    inputs.forEach(input => {
                        input.classList.remove('is-valid', 'is-invalid');
                    });
                }
                
                const saveAddressBtn = document.getElementById('save-address-btn');
                if (saveAddressBtn) {
                    saveAddressBtn.innerHTML = '<i class="fas fa-save"></i><span>Enregistrer l\'adresse</span>';
                    saveAddressBtn.disabled = false;
                }
            });
        }
        
        // Modal de coupon
        const couponModal = document.getElementById('couponModal');
        if (couponModal) {
            couponModal.addEventListener('hidden.bs.modal', function () {
                const couponMessage = document.getElementById('coupon-message');
                const couponInput = document.getElementById('coupon-input');
                if (couponMessage) couponMessage.innerHTML = '';
                if (couponInput) couponInput.value = '';
            });
        }
    }
    
    // ============================================
    // GESTION ERREURS RÉSEAU
    // ============================================
    
    /**
     * Initialiser la gestion des erreurs réseau
     */
    function initNetworkHandlers() {
        window.addEventListener('online', function() {
            showNotification('Connexion internet rétablie', 'success');
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
     * Améliorer l'accessibilité
     */
    function initAccessibility() {
        // Cartes d'adresses
        document.querySelectorAll('.address-card-modern').forEach(card => {
            card.setAttribute('tabindex', '0');
            card.setAttribute('role', 'radio');
        });
        
        // Cartes de livraison
        document.querySelectorAll('.shipping-option-card').forEach(card => {
            card.setAttribute('tabindex', '0');
            card.setAttribute('role', 'radio');
        });
        
        // Cartes de paiement
        document.querySelectorAll('.payment-method-card-modern').forEach(card => {
            card.setAttribute('tabindex', '0');
            card.setAttribute('role', 'radio');
        });
    }
    
    // ============================================
    // INITIALISATION
    // ============================================
    
    /**
     * Initialiser tous les modules
     */
    function init() {
        initAddressSelection();
        initShippingSelection();
        initPaymentSelection();
        initAddAddressForm();
        initCouponSystem();
        initFormValidation();
        initStepNavigation();
        initRealtimeValidation();
        initScrollAnimations();
        initModalHandlers();
        initNetworkHandlers();
        initAccessibility();
        
        console.log('✅ Checkout page JavaScript loaded');
        console.log('📊 Subtotal:', subtotalAmount.toLocaleString('fr-FR'), 'FCFA');
    }
    
    // Lancement au chargement du DOM
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
    
})();