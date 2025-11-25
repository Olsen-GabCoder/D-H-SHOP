/* ===================================
   PRODUCT DETAIL - JAVASCRIPT MODERNE
   Version: 2.0.0 - AJAX Integration
   =================================== */

document.addEventListener('DOMContentLoaded', function() {
    'use strict';
    
    // ===================================
    // VARIABLES GLOBALES
    // ===================================
    const mainImage = document.getElementById('main-product-image');
    const thumbnails = document.querySelectorAll('.thumbnail-image');
    const currentImageIndex = document.getElementById('current-image-index');
    const variantBtns = document.querySelectorAll('.variant-btn-modern');
    const productPrice = document.getElementById('product-price');
    const quantityInput = document.getElementById('quantity');
    const stockIndicator = document.getElementById('stock-indicator');
    const addToCartBtn = document.querySelector('.btn-add-to-cart-modern');
    const addToCartForm = document.getElementById('add-to-cart-form');
    
    // ===================================
    // GALERIE D'IMAGES
    // ===================================
    
    thumbnails.forEach(thumbnail => {
        thumbnail.addEventListener('click', function() {
            // Update main image
            const newImageSrc = this.dataset.image;
            if (mainImage && newImageSrc) {
                mainImage.src = newImageSrc;
            }
            
            // Update active thumbnail
            thumbnails.forEach(t => t.classList.remove('active'));
            this.classList.add('active');
            
            // Update image counter
            if (currentImageIndex && this.dataset.index) {
                currentImageIndex.textContent = this.dataset.index;
            }
        });
    });
    
    // Navigation des vignettes
    const thumbnailsTrack = document.querySelector('.thumbnails-track');
    const prevBtn = document.querySelector('.thumbnail-prev');
    const nextBtn = document.querySelector('.thumbnail-next');
    
    if (thumbnailsTrack && prevBtn && nextBtn) {
        let currentPosition = 0;
        const thumbnailWidth = 96; // 80px + 16px gap
        
        prevBtn.addEventListener('click', () => {
            if (currentPosition > 0) {
                currentPosition--;
                updateThumbnailPosition();
            }
        });
        
        nextBtn.addEventListener('click', () => {
            const maxPosition = Math.max(0, thumbnails.length - 4);
            if (currentPosition < maxPosition) {
                currentPosition++;
                updateThumbnailPosition();
            }
        });
        
        function updateThumbnailPosition() {
            thumbnailsTrack.style.transform = `translateX(-${currentPosition * thumbnailWidth}px)`;
            prevBtn.disabled = currentPosition === 0;
            nextBtn.disabled = currentPosition >= Math.max(0, thumbnails.length - 4);
        }
        
        // Initial state
        updateThumbnailPosition();
    }
    
    // ===================================
    // VARIANTES - CORRECTION PRINCIPALE
    // ===================================
    
    variantBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            // Ne rien faire si le bouton est désactivé (rupture de stock)
            if (this.disabled || this.classList.contains('out-of-stock')) {
                return;
            }
            
            // Update active button
            variantBtns.forEach(b => {
                b.classList.remove('active');
                b.setAttribute('aria-checked', 'false');
            });
            this.classList.add('active');
            this.setAttribute('aria-checked', 'true');
            
            // ✅ CORRECTION : Récupérer le variant_id et mettre à jour l'URL du formulaire
            const newVariantId = this.dataset.variantId;
            
            if (addToCartForm && newVariantId) {
                // Mettre à jour l'action du formulaire avec le nouveau variant_id
                const baseUrl = addToCartForm.dataset.baseUrl;
                if (baseUrl) {
                    // Si data-base-url existe, l'utiliser pour construire l'URL
                    addToCartForm.action = baseUrl.replace('/0/', `/${newVariantId}/`);
                } else {
                    // ✅ CORRECTION : Utiliser le bon chemin /cart/add/ au lieu de /orders/add/
                    addToCartForm.action = `/cart/add/${newVariantId}/`;
                }
            }
            
            // ✅ Mettre à jour le prix affiché
            const newPrice = this.dataset.price;
            if (productPrice && newPrice) {
                productPrice.textContent = parseFloat(newPrice).toLocaleString('fr-FR', {
                    minimumFractionDigits: 0,
                    maximumFractionDigits: 0
                });
            }
            
            // ✅ Mettre à jour le stock disponible
            const newStock = parseInt(this.dataset.stock) || 0;
            
            // Mettre à jour l'attribut max du champ quantité
            if (quantityInput) {
                quantityInput.setAttribute('max', newStock);
                // Réinitialiser la quantité si elle dépasse le nouveau stock
                if (parseInt(quantityInput.value) > newStock) {
                    quantityInput.value = Math.max(1, newStock);
                }
            }
            
            // Mettre à jour l'indicateur de stock
            if (stockIndicator) {
                updateStockIndicator(newStock);
            }
            
            // Activer/désactiver le bouton d'ajout au panier selon le stock
            if (addToCartBtn) {
                addToCartBtn.disabled = newStock <= 0;
            }
        });
    });
    
    function updateStockIndicator(stock) {
        if (!stockIndicator) return;
        
        if (stock <= 0) {
            stockIndicator.innerHTML = `
                <span class="stock-status stock-out">
                    <i class="fas fa-times-circle"></i>
                    Rupture de stock
                </span>
            `;
        } else if (stock <= 5) {
            stockIndicator.innerHTML = `
                <span class="stock-status stock-low">
                    <i class="fas fa-exclamation-triangle"></i>
                    Plus que ${stock} en stock !
                </span>
            `;
        } else {
            stockIndicator.innerHTML = `
                <span class="stock-status stock-in">
                    <i class="fas fa-check-circle"></i>
                    En stock (${stock} disponible${stock > 1 ? 's' : ''})
                </span>
            `;
        }
    }
    
    // ===================================
    // CONTRÔLES DE QUANTITÉ
    // ===================================
    const decrementBtn = document.querySelector('.quantity-decrement');
    const incrementBtn = document.querySelector('.quantity-increment');
    
    if (decrementBtn && quantityInput) {
        decrementBtn.addEventListener('click', () => {
            const currentValue = parseInt(quantityInput.value) || 1;
            if (currentValue > 1) {
                quantityInput.value = currentValue - 1;
            }
        });
    }
    
    if (incrementBtn && quantityInput) {
        incrementBtn.addEventListener('click', () => {
            const currentValue = parseInt(quantityInput.value) || 1;
            const maxValue = parseInt(quantityInput.getAttribute('max')) || 99;
            if (currentValue < maxValue) {
                quantityInput.value = currentValue + 1;
            }
        });
    }
    
    if (quantityInput) {
        quantityInput.addEventListener('input', function() {
            let value = parseInt(this.value) || 1;
            const min = parseInt(this.getAttribute('min')) || 1;
            const max = parseInt(this.getAttribute('max')) || 99;
            
            if (value < min) value = min;
            if (value > max) value = max;
            
            this.value = value;
        });
        
        // Empêcher les valeurs non numériques
        quantityInput.addEventListener('keypress', function(e) {
            if (!/[0-9]/.test(e.key)) {
                e.preventDefault();
            }
        });
    }
    
    // ===================================
    // ONGLETS
    // ===================================
    const tabLinks = document.querySelectorAll('.tab-modern-link');
    const tabPanes = document.querySelectorAll('.tab-modern-pane');
    
    tabLinks.forEach(link => {
        link.addEventListener('click', function() {
            const targetTab = this.dataset.tab;
            
            // Update active tab
            tabLinks.forEach(l => {
                l.classList.remove('active');
                l.setAttribute('aria-selected', 'false');
            });
            this.classList.add('active');
            this.setAttribute('aria-selected', 'true');
            
            // Show corresponding pane
            tabPanes.forEach(pane => {
                pane.classList.remove('active');
            });
            
            const targetPane = document.getElementById(targetTab);
            if (targetPane) {
                targetPane.classList.add('active');
            }
            
            // Smooth scroll to tabs section
            const tabsSection = document.querySelector('.product-tabs-section');
            if (tabsSection) {
                tabsSection.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
    
    // ===================================
    // BOUTON WISHLIST
    // ===================================
    const wishlistBtn = document.querySelector('.btn-wishlist-modern');
    
    if (wishlistBtn) {
        wishlistBtn.addEventListener('click', function() {
            this.classList.toggle('active');
            
            const icon = this.querySelector('i');
            if (icon) {
                if (this.classList.contains('active')) {
                    icon.classList.remove('far');
                    icon.classList.add('fas');
                    showNotification('Ajouté aux favoris !', 'success');
                } else {
                    icon.classList.remove('fas');
                    icon.classList.add('far');
                    showNotification('Retiré des favoris', 'info');
                }
            }
        });
    }
    
    // ===================================
    // ZOOM IMAGE
    // ===================================
    const zoomBtn = document.querySelector('.image-zoom-btn');
    
    if (zoomBtn && mainImage) {
        zoomBtn.addEventListener('click', function() {
            openImageModal(mainImage.src);
        });
    }
    
    // Double-clic sur l'image principale pour zoomer
    if (mainImage) {
        mainImage.addEventListener('dblclick', function() {
            openImageModal(this.src);
        });
    }
    
    function openImageModal(imageUrl) {
        // Vérifier si un modal existe déjà
        const existingModal = document.querySelector('.image-modal-overlay');
        if (existingModal) {
            existingModal.remove();
        }
        
        const modal = document.createElement('div');
        modal.className = 'image-modal-overlay';
        modal.innerHTML = `
            <div class="image-modal-content">
                <button type="button" class="image-modal-close" aria-label="Fermer">&times;</button>
                <img src="${imageUrl}" alt="Zoom" class="image-modal-img">
            </div>
        `;
        
        document.body.appendChild(modal);
        document.body.style.overflow = 'hidden';
        
        // Fermer le modal
        modal.addEventListener('click', function(e) {
            if (e.target === modal || e.target.classList.contains('image-modal-close')) {
                closeImageModal(modal);
            }
        });
        
        // Focus pour l'accessibilité
        const closeBtn = modal.querySelector('.image-modal-close');
        if (closeBtn) {
            closeBtn.focus();
        }
    }
    
    function closeImageModal(modal) {
        if (modal) {
            modal.remove();
            document.body.style.overflow = '';
        }
    }
    
    // ===================================
    // PARTAGE SOCIAL
    // ===================================
    const shareButtons = document.querySelectorAll('.share-btn');
    
    shareButtons.forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            
            const url = window.location.href;
            const titleElement = document.querySelector('.product-title-detail');
            const title = titleElement ? titleElement.textContent.trim() : document.title;
            const shareType = this.dataset.share;
            
            let shareUrl = '';
            
            switch(shareType) {
                case 'facebook':
                    shareUrl = `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(url)}`;
                    break;
                case 'twitter':
                    shareUrl = `https://twitter.com/intent/tweet?url=${encodeURIComponent(url)}&text=${encodeURIComponent(title)}`;
                    break;
                case 'whatsapp':
                    shareUrl = `https://wa.me/?text=${encodeURIComponent(title + ' - ' + url)}`;
                    break;
                case 'pinterest':
                    const imageUrl = mainImage ? mainImage.src : '';
                    shareUrl = `https://pinterest.com/pin/create/button/?url=${encodeURIComponent(url)}&media=${encodeURIComponent(imageUrl)}&description=${encodeURIComponent(title)}`;
                    break;
                case 'copy':
                    copyToClipboard(url);
                    return;
            }
            
            if (shareUrl) {
                window.open(shareUrl, '_blank', 'width=600,height=400,scrollbars=yes');
            }
        });
    });
    
    function copyToClipboard(text) {
        if (navigator.clipboard && navigator.clipboard.writeText) {
            navigator.clipboard.writeText(text).then(() => {
                showNotification('Lien copié dans le presse-papiers !', 'success');
            }).catch(() => {
                fallbackCopyToClipboard(text);
            });
        } else {
            fallbackCopyToClipboard(text);
        }
    }
    
    function fallbackCopyToClipboard(text) {
        const textArea = document.createElement('textarea');
        textArea.value = text;
        textArea.style.position = 'fixed';
        textArea.style.left = '-9999px';
        document.body.appendChild(textArea);
        textArea.select();
        
        try {
            document.execCommand('copy');
            showNotification('Lien copié dans le presse-papiers !', 'success');
        } catch (err) {
            showNotification('Impossible de copier le lien', 'error');
        }
        
        document.body.removeChild(textArea);
    }
    
    // ===================================
    // FORMULAIRE D'AJOUT AU PANIER - VÉRITABLE AJAX
    // ===================================
    
    if (addToCartForm && addToCartBtn) {
        addToCartForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Vérifier que le bouton n'est pas désactivé
            if (addToCartBtn.disabled) {
                showNotification('Ce produit n\'est pas disponible', 'error');
                return;
            }
            
            // Sauvegarder le contenu original du bouton
            const originalHTML = addToCartBtn.innerHTML;
            const originalTransform = addToCartBtn.style.transform;
            
            // Animation du bouton - état de chargement
            addToCartBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Ajout en cours...';
            addToCartBtn.disabled = true;
            addToCartBtn.style.transform = 'scale(0.95)';
            
            // Préparer les données du formulaire
            const formData = new FormData(this);
            
            // Récupérer le token CSRF
            const csrfToken = getCSRFToken();
            if (csrfToken) {
                formData.append('csrfmiddlewaretoken', csrfToken);
            }
            
            // ✅ CORRECTION : URL corrigée (/cart/add/ au lieu de /orders/add/)
            const url = this.action;
            
            // Envoyer la requête AJAX
            fetch(url, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': csrfToken || ''
                }
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`Erreur HTTP: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                if (data.success) {
                    // ✅ SUCCÈS - Produit ajouté au panier
                    handleAddToCartSuccess(data, originalHTML);
                } else {
                    // ❌ ERREUR MÉTIER (stock, produit introuvable, etc.)
                    throw new Error(data.error || 'Erreur lors de l\'ajout au panier');
                }
            })
            .catch(error => {
                console.error('❌ Erreur AJAX:', error);
                handleAddToCartError(error, originalHTML, originalTransform);
            });
        });
    }
    
    function handleAddToCartSuccess(data, originalHTML) {
        if (!addToCartBtn) return;
        
        // État de succès
        addToCartBtn.innerHTML = '<i class="fas fa-check"></i> Ajouté !';
        addToCartBtn.classList.add('btn-success-state');
        addToCartBtn.style.transform = 'scale(1)';
        
        // Notification de succès
        showNotification(data.message || 'Produit ajouté au panier avec succès !', 'success');
        
        // Mettre à jour le badge du panier
        updateCartBadge(data.cart_count);
        
        // Remettre le bouton à son état initial après 2 secondes
        setTimeout(() => {
            addToCartBtn.innerHTML = originalHTML;
            addToCartBtn.classList.remove('btn-success-state');
            addToCartBtn.disabled = false;
        }, 2000);
    }
    
    function handleAddToCartError(error, originalHTML, originalTransform) {
        if (!addToCartBtn) return;
        
        // Réinitialiser le bouton
        addToCartBtn.innerHTML = originalHTML;
        addToCartBtn.disabled = false;
        addToCartBtn.style.transform = originalTransform;
        
        // Afficher message d'erreur
        const errorMessage = error.message || 'Impossible d\'ajouter le produit au panier';
        showNotification(errorMessage, 'error');
        
        console.error('Erreur ajout panier:', error);
    }
    
    function getCSRFToken() {
        // Récupérer le token CSRF depuis les cookies
        const name = 'csrftoken';
        let cookieValue = null;
        
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        
        return cookieValue;
    }
    
    function updateCartBadge(cartCount) {
        // Mettre à jour tous les badges panier dans la page
        const badges = document.querySelectorAll('.cart-badge, .badge, [data-cart-count]');
        
        badges.forEach(badge => {
            const newCount = cartCount !== undefined ? cartCount : (parseInt(badge.textContent) || 0) + 1;
            badge.textContent = newCount;
            
            // Animation du badge
            badge.style.transform = 'scale(1.3)';
            setTimeout(() => {
                badge.style.transform = 'scale(1)';
            }, 300);
        });
        
        // Émettre un événement personnalisé pour notifier d'autres composants
        const event = new CustomEvent('cartUpdated', { 
            detail: { count: cartCount } 
        });
        document.dispatchEvent(event);
    }
    
    // ===================================
    // SYSTÈME DE NOTIFICATIONS MODERNE
    // ===================================
    
    function showNotification(message, type = 'info') {
        // Créer la notification
        const notification = document.createElement('div');
        notification.className = `toast-notification toast-${type}`;
        notification.setAttribute('role', 'alert');
        notification.setAttribute('aria-live', 'assertive');
        
        const icons = {
            success: 'check-circle',
            error: 'exclamation-circle',
            warning: 'exclamation-triangle',
            info: 'info-circle'
        };
        
        notification.innerHTML = `
            <div class="toast-icon">
                <i class="fas fa-${icons[type] || 'info-circle'}"></i>
            </div>
            <div class="toast-content">
                <div class="toast-title">${getNotificationTitle(type)}</div>
                <div class="toast-message">${message}</div>
            </div>
            <button class="toast-close" aria-label="Fermer la notification">
                <i class="fas fa-times"></i>
            </button>
        `;
        
        // Ajouter au document
        document.body.appendChild(notification);
        
        // Animation d'entrée
        setTimeout(() => {
            notification.style.transform = 'translateX(0)';
            notification.style.opacity = '1';
        }, 10);
        
        // Fermeture automatique après 5 secondes
        const autoClose = setTimeout(() => {
            closeNotification(notification);
        }, 5000);
        
        // Fermeture manuelle
        const closeBtn = notification.querySelector('.toast-close');
        closeBtn.addEventListener('click', () => {
            clearTimeout(autoClose);
            closeNotification(notification);
        });
        
        // Fermeture au clic sur la notification
        notification.addEventListener('click', (e) => {
            if (e.target === notification) {
                clearTimeout(autoClose);
                closeNotification(notification);
            }
        });
    }
    
    function getNotificationTitle(type) {
        const titles = {
            success: 'Succès',
            error: 'Erreur',
            warning: 'Attention',
            info: 'Information'
        };
        return titles[type] || 'Notification';
    }
    
    function closeNotification(notification) {
        notification.style.transform = 'translateX(400px)';
        notification.style.opacity = '0';
        
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 300);
    }
    
    // Injecter les styles CSS pour les notifications
    function injectNotificationStyles() {
        const style = document.createElement('style');
        style.textContent = `
            .toast-notification {
                position: fixed;
                top: 100px;
                right: 20px;
                background: white;
                border-radius: 12px;
                padding: 1.25rem 1.5rem;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.16);
                display: flex;
                align-items: center;
                gap: 1rem;
                z-index: 9999;
                min-width: 320px;
                max-width: 400px;
                transform: translateX(400px);
                opacity: 0;
                transition: all 0.3s ease;
                border-left: 4px solid #e74c3c;
            }
            
            .toast-success {
                border-left-color: #27ae60;
            }
            
            .toast-error {
                border-left-color: #e74c3c;
            }
            
            .toast-warning {
                border-left-color: #f39c12;
            }
            
            .toast-info {
                border-left-color: #3498db;
            }
            
            .toast-icon {
                width: 40px;
                height: 40px;
                background: #e74c3c;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                color: white;
                font-size: 1.25rem;
                flex-shrink: 0;
            }
            
            .toast-success .toast-icon {
                background: #27ae60;
            }
            
            .toast-error .toast-icon {
                background: #e74c3c;
            }
            
            .toast-warning .toast-icon {
                background: #f39c12;
            }
            
            .toast-info .toast-icon {
                background: #3498db;
            }
            
            .toast-content {
                flex: 1;
            }
            
            .toast-title {
                font-weight: 700;
                color: #2c3e50;
                margin-bottom: 0.25rem;
                font-size: 0.95rem;
            }
            
            .toast-message {
                font-size: 0.9rem;
                color: #7f8c8d;
                line-height: 1.4;
            }
            
            .toast-close {
                background: none;
                border: none;
                color: #bdc3c7;
                font-size: 1.1rem;
                cursor: pointer;
                transition: all 0.3s ease;
                padding: 0.25rem;
                border-radius: 4px;
            }
            
            .toast-close:hover {
                color: #e74c3c;
                background: #f8f9fa;
            }
            
            .btn-success-state {
                background-color: #27ae60 !important;
                border-color: #27ae60 !important;
                color: white !important;
            }
        `;
        document.head.appendChild(style);
    }
    
    // Injecter les styles au chargement
    injectNotificationStyles();
    
    // ===================================
    // NAVIGATION AU CLAVIER
    // ===================================
    document.addEventListener('keydown', (e) => {
        // Left/Right arrows pour naviguer entre les images
        if (e.key === 'ArrowLeft' && prevBtn && !prevBtn.disabled) {
            prevBtn.click();
        } else if (e.key === 'ArrowRight' && nextBtn && !nextBtn.disabled) {
            nextBtn.click();
        }
        
        // Escape pour fermer les modales
        if (e.key === 'Escape') {
            const modal = document.querySelector('.image-modal-overlay');
            if (modal) {
                closeImageModal(modal);
            }
        }
    });
    
    // ===================================
    // LAZY LOADING DES IMAGES
    // ===================================
    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    if (img.dataset.src) {
                        img.src = img.dataset.src;
                        img.removeAttribute('data-src');
                    }
                    imageObserver.unobserve(img);
                }
            });
        }, {
            rootMargin: '50px 0px'
        });
        
        document.querySelectorAll('img[data-src]').forEach(img => {
            imageObserver.observe(img);
        });
    }
    
    // ===================================
    // SCROLL TO REVIEWS
    // ===================================
    const reviewLinks = document.querySelectorAll('a[href="#reviews-section"], .add-review-link');
    
    reviewLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            // Activer l'onglet reviews
            const reviewsTabBtn = document.querySelector('[data-tab="reviews"]');
            if (reviewsTabBtn) {
                reviewsTabBtn.click();
            }
        });
    });
    
    // ===================================
    // STICKY ADD TO CART (Mobile)
    // ===================================
    function initStickyBar() {
        if (window.innerWidth > 768) return;
        
        const productInfo = document.querySelector('.product-info-modern');
        if (!productInfo || !productPrice || !addToCartBtn) return;
        
        // Vérifier si la barre existe déjà
        let stickyBar = document.querySelector('.sticky-add-to-cart');
        
        if (!stickyBar) {
            stickyBar = document.createElement('div');
            stickyBar.className = 'sticky-add-to-cart';
            stickyBar.innerHTML = `
                <div class="sticky-bar-content">
                    <div class="sticky-price">
                        <span class="sticky-price-current">${productPrice.textContent}</span>
                        <span class="sticky-price-currency">FCFA</span>
                    </div>
                    <button type="button" class="btn-sticky-cart" ${addToCartBtn.disabled ? 'disabled' : ''}>
                        <i class="fas fa-shopping-cart"></i>
                        <span>Ajouter</span>
                    </button>
                </div>
            `;
            document.body.appendChild(stickyBar);
            
            const stickyBtn = stickyBar.querySelector('.btn-sticky-cart');
            if (stickyBtn) {
                stickyBtn.addEventListener('click', () => {
                    if (!addToCartBtn.disabled) {
                        // Scroll vers le formulaire et soumettre
                        addToCartForm.scrollIntoView({ behavior: 'smooth', block: 'center' });
                        setTimeout(() => {
                            addToCartBtn.click();
                        }, 500);
                    }
                });
            }
        }
        
        // Observer le scroll pour afficher/masquer la barre sticky
        let lastScrollY = window.scrollY;
        let ticking = false;
        
        window.addEventListener('scroll', () => {
            if (!ticking) {
                window.requestAnimationFrame(() => {
                    const infoRect = productInfo.getBoundingClientRect();
                    if (infoRect.bottom < 0) {
                        stickyBar.classList.add('visible');
                    } else {
                        stickyBar.classList.remove('visible');
                    }
                    lastScrollY = window.scrollY;
                    ticking = false;
                });
                ticking = true;
            }
        });
        
        // Mettre à jour le prix dans la barre sticky quand la variante change
        const observer = new MutationObserver(() => {
            const stickyPriceCurrent = stickyBar.querySelector('.sticky-price-current');
            if (stickyPriceCurrent && productPrice) {
                stickyPriceCurrent.textContent = productPrice.textContent;
            }
            
            const stickyBtn = stickyBar.querySelector('.btn-sticky-cart');
            if (stickyBtn && addToCartBtn) {
                stickyBtn.disabled = addToCartBtn.disabled;
            }
        });
        
        if (productPrice) {
            observer.observe(productPrice, { childList: true, characterData: true, subtree: true });
        }
    }
    
    // Initialiser la barre sticky
    initStickyBar();
    
    // Réinitialiser sur redimensionnement
    let resizeTimeout;
    window.addEventListener('resize', () => {
        clearTimeout(resizeTimeout);
        resizeTimeout = setTimeout(() => {
            const existingStickyBar = document.querySelector('.sticky-add-to-cart');
            if (window.innerWidth > 768 && existingStickyBar) {
                existingStickyBar.remove();
            } else if (window.innerWidth <= 768 && !existingStickyBar) {
                initStickyBar();
            }
        }, 250);
    });
    
    // ===================================
    // QUICK VIEW POUR PRODUITS SIMILAIRES
    // ===================================
    const quickViewBtns = document.querySelectorAll('.quick-view-btn');
    
    quickViewBtns.forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            const productSlug = this.dataset.productSlug;
            if (productSlug) {
                // Rediriger vers la page produit (à remplacer par un vrai quick view si implémenté)
                window.location.href = `/shop/product/${productSlug}/`;
            }
        });
    });
    
    // ===================================
    // BOUTONS AJOUTER AU PANIER (PRODUITS SIMILAIRES)
    // ===================================
    const addToCartQuickBtns = document.querySelectorAll('.add-to-cart-quick, .btn-product-cart');
    
    addToCartQuickBtns.forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            const variantId = this.dataset.variantId;
            if (variantId && variantId !== 'None') {
                // ✅ VÉRITABLE AJAX pour les produits similaires
                addToCartFromCard(variantId, this);
            } else {
                // Rediriger vers la page produit pour sélectionner la variante
                showNotification('Veuillez sélectionner une taille sur la page produit', 'info');
                
                // Trouver le lien vers le produit
                const productCard = this.closest('.product-card-modern');
                if (productCard) {
                    const productLink = productCard.querySelector('a[href*="/shop/product/"]');
                    if (productLink) {
                        setTimeout(() => {
                            window.location.href = productLink.href;
                        }, 1000);
                    }
                }
            }
        });
    });
    
    function addToCartFromCard(variantId, button) {
        // Sauvegarder le contenu original
        const originalContent = button.innerHTML;
        const originalTransform = button.style.transform;
        
        // Animation du bouton
        button.style.transform = 'scale(0.9)';
        button.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
        button.disabled = true;
        
        // ✅ CORRECTION : URL corrigée (/cart/add/ au lieu de /orders/add/)
        const url = `/cart/add/${variantId}/`;
        
        // Données du formulaire
        const formData = new FormData();
        formData.append('quantity', 1);
        formData.append('csrfmiddlewaretoken', getCSRFToken());
        
        // Envoi de la requête AJAX
        fetch(url, {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': getCSRFToken()
            }
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`Erreur HTTP: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                // Succès - Animation de confirmation
                button.style.transform = 'scale(1)';
                button.innerHTML = '<i class="fas fa-check"></i>';
                button.classList.add('btn-success');
                
                showNotification(data.message || 'Produit ajouté au panier', 'success');
                
                // Mettre à jour le badge du panier
                updateCartBadge(data.cart_count);
                
                // Réinitialiser le bouton après 2 secondes
                setTimeout(() => {
                    button.innerHTML = originalContent;
                    button.classList.remove('btn-success');
                    button.disabled = false;
                    button.style.transform = originalTransform;
                }, 2000);
            } else {
                // Erreur métier
                throw new Error(data.error || 'Erreur lors de l\'ajout au panier');
            }
        })
        .catch(error => {
            console.error('❌ Erreur AJAX:', error);
            
            // Réinitialiser le bouton
            button.innerHTML = originalContent;
            button.disabled = false;
            button.style.transform = originalTransform;
            
            // Afficher message d'erreur
            showNotification(
                error.message || 'Impossible d\'ajouter le produit au panier', 
                'error'
            );
        });
    }
    
    // ===================================
    // SCROLL TO TOP
    // ===================================
    const scrollToTopBtn = document.getElementById('scrollToTop');
    
    if (scrollToTopBtn) {
        window.addEventListener('scroll', () => {
            if (window.scrollY > 500) {
                scrollToTopBtn.classList.add('visible');
            } else {
                scrollToTopBtn.classList.remove('visible');
            }
        });
        
        scrollToTopBtn.addEventListener('click', () => {
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });
    }
    
    // ===================================
    // ÉCOUTEURS D'ÉVÉNEMENTS GLOBAUX
    // ===================================
    
    // Écouter les mises à jour du panier depuis d'autres composants
    document.addEventListener('cartUpdated', function(event) {
        console.log('🛒 Panier mis à jour:', event.detail);
    });
    
    // ===================================
    // INITIALISATION TERMINÉE
    // ===================================
    console.log('🎨 Product Detail Modern - AJAX Version Initialized successfully');
});