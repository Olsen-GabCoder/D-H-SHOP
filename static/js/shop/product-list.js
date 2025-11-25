/* ===================================
   PRODUCT LIST - JAVASCRIPT MODERNE
   Version: 2.0.0 - AJAX Integration
   =================================== */

(function() {
    'use strict';
    
    // ===================================
    // VARIABLES GLOBALES
    // ===================================
    
    let currentFilters = {
        categories: [],
        minPrice: 0,
        maxPrice: 1000000,
        inStock: true,
        onSale: false,
        newArrivals: false,
        rating: null,
        sortBy: 'newest',
        view: 'grid'
    };
    
    let allProducts = [];
    let filteredProducts = [];
    let currentPage = 1;
    const productsPerPage = 12;
    
    // ===================================
    // INITIALISATION
    // ===================================
    
    document.addEventListener('DOMContentLoaded', function() {
        console.log('🚀 Product List JS initialisé - Version AJAX');
        
        // Initialiser tous les composants
        initViewToggle();
        initPriceFilter();
        initCheckboxFilters();
        initRadioFilters();
        initSortControls();
        initResetFilters();
        initProductCards();
        initNotifications();
        loadProductsData();
        restoreUserPreferences();
        
        console.log('✅ Tous les composants initialisés');
    });
    
    // ===================================
    // GESTION DE LA VUE (GRILLE/LISTE)
    // ===================================
    
    function initViewToggle() {
        const viewButtons = document.querySelectorAll('.view-toggle-btn');
        const productsContainer = document.getElementById('products-container');
        
        if (!viewButtons.length || !productsContainer) return;
        
        viewButtons.forEach(button => {
            button.addEventListener('click', function() {
                const view = this.getAttribute('data-view');
                
                // Mettre à jour les boutons
                viewButtons.forEach(btn => btn.classList.remove('active'));
                this.classList.add('active');
                
                // Mettre à jour la grille
                if (view === 'list') {
                    productsContainer.classList.add('view-list');
                    productsContainer.classList.remove('view-grid');
                } else {
                    productsContainer.classList.add('view-grid');
                    productsContainer.classList.remove('view-list');
                }
                
                // Sauvegarder la préférence
                currentFilters.view = view;
                saveUserPreferences();
                
                // Animation
                animateViewChange(productsContainer);
                
                console.log(`📊 Vue changée: ${view}`);
            });
        });
    }
    
    function animateViewChange(container) {
        container.style.opacity = '0';
        container.style.transform = 'scale(0.98)';
        
        setTimeout(() => {
            container.style.transition = 'all 0.3s ease';
            container.style.opacity = '1';
            container.style.transform = 'scale(1)';
        }, 50);
    }
    
    // ===================================
    // FILTRE DE PRIX
    // ===================================
    
    function initPriceFilter() {
        const priceSlider = document.getElementById('price-range');
        const priceDisplay = document.getElementById('price-value');
        const minPriceInput = document.getElementById('min-price');
        const maxPriceInput = document.getElementById('max-price');
        const applyBtn = document.getElementById('apply-price-filter');
        
        if (!priceSlider) return;
        
        // Synchroniser le slider avec l'affichage
        priceSlider.addEventListener('input', function() {
            const value = parseInt(this.value);
            updatePriceDisplay(0, value);
            maxPriceInput.value = value;
        });
        
        // Synchroniser les inputs
        minPriceInput.addEventListener('input', function() {
            const value = parseInt(this.value) || 0;
            currentFilters.minPrice = value;
            updatePriceDisplay(value, currentFilters.maxPrice);
        });
        
        maxPriceInput.addEventListener('input', function() {
            const value = parseInt(this.value) || currentFilters.maxPrice;
            currentFilters.maxPrice = value;
            priceSlider.value = value;
            updatePriceDisplay(currentFilters.minPrice, value);
        });
        
        // Appliquer le filtre
        applyBtn.addEventListener('click', function() {
            currentFilters.minPrice = parseInt(minPriceInput.value) || 0;
            currentFilters.maxPrice = parseInt(maxPriceInput.value) || 1000000;
            
            // Animation du bouton
            this.style.transform = 'scale(0.95)';
            setTimeout(() => {
                this.style.transform = 'scale(1)';
            }, 150);
            
            applyFilters();
            updateActiveFilters();
            
            console.log(`💰 Filtre prix: ${currentFilters.minPrice} - ${currentFilters.maxPrice}`);
        });
        
        // Mise à jour du gradient du slider
        updateSliderGradient(priceSlider);
        priceSlider.addEventListener('input', function() {
            updateSliderGradient(this);
        });
    }
    
    function updatePriceDisplay(min, max) {
        const display = document.getElementById('price-value');
        if (display) {
            display.textContent = `${formatNumber(min)} - ${formatNumber(max)}`;
        }
    }
    
    function updateSliderGradient(slider) {
        const value = parseInt(slider.value);
        const max = parseInt(slider.max);
        const percentage = (value / max) * 100;
        
        slider.style.background = `linear-gradient(to right, #e74c3c 0%, #e74c3c ${percentage}%, #e0e0e0 ${percentage}%, #e0e0e0 100%)`;
    }
    
    // ===================================
    // FILTRES CHECKBOX
    // ===================================
    
    function initCheckboxFilters() {
        const inStockCheckbox = document.getElementById('in-stock');
        const onSaleCheckbox = document.getElementById('on-sale');
        const newArrivalsCheckbox = document.getElementById('new-arrivals');
        
        if (inStockCheckbox) {
            inStockCheckbox.addEventListener('change', function() {
                currentFilters.inStock = this.checked;
                applyFilters();
                updateActiveFilters();
                animateCheckbox(this);
            });
        }
        
        if (onSaleCheckbox) {
            onSaleCheckbox.addEventListener('change', function() {
                currentFilters.onSale = this.checked;
                applyFilters();
                updateActiveFilters();
                animateCheckbox(this);
            });
        }
        
        if (newArrivalsCheckbox) {
            newArrivalsCheckbox.addEventListener('change', function() {
                currentFilters.newArrivals = this.checked;
                applyFilters();
                updateActiveFilters();
                animateCheckbox(this);
            });
        }
    }
    
    function animateCheckbox(checkbox) {
        const parent = checkbox.closest('.filter-checkbox');
        if (parent) {
            parent.style.transform = 'scale(1.05)';
            setTimeout(() => {
                parent.style.transform = 'scale(1)';
            }, 200);
        }
    }
    
    // ===================================
    // FILTRES RADIO (NOTATION)
    // ===================================
    
    function initRadioFilters() {
        const ratingRadios = document.querySelectorAll('input[name="rating"]');
        
        ratingRadios.forEach(radio => {
            radio.addEventListener('change', function() {
                if (this.checked) {
                    const ratingValue = this.id.replace('rating-', '');
                    currentFilters.rating = parseInt(ratingValue);
                    applyFilters();
                    updateActiveFilters();
                    
                    console.log(`⭐ Filtre notation: ${ratingValue}+`);
                }
            });
        });
    }
    
    // ===================================
    // CONTRÔLES DE TRI
    // ===================================
    
    function initSortControls() {
        const sortSelect = document.getElementById('sort-by');
        
        if (!sortSelect) return;
        
        sortSelect.addEventListener('change', function() {
            currentFilters.sortBy = this.value;
            sortProducts();
            displayProducts();
            
            // Animation du select
            this.style.transform = 'scale(1.02)';
            setTimeout(() => {
                this.style.transform = 'scale(1)';
            }, 200);
            
            console.log(`🔄 Tri: ${this.value}`);
        });
    }
    
    function sortProducts() {
        const sortBy = currentFilters.sortBy;
        
        filteredProducts.sort((a, b) => {
            switch (sortBy) {
                case 'price-asc':
                    return getProductPrice(a) - getProductPrice(b);
                
                case 'price-desc':
                    return getProductPrice(b) - getProductPrice(a);
                
                case 'name-asc':
                    return getProductName(a).localeCompare(getProductName(b));
                
                case 'name-desc':
                    return getProductName(b).localeCompare(getProductName(a));
                
                case 'popular':
                    return getProductPopularity(b) - getProductPopularity(a);
                
                case 'newest':
                default:
                    return 0; // Garder l'ordre initial
            }
        });
    }
    
    // ===================================
    // RÉINITIALISATION DES FILTRES
    // ===================================
    
    function initResetFilters() {
        const resetBtn = document.getElementById('reset-filters');
        
        if (!resetBtn) return;
        
        resetBtn.addEventListener('click', function() {
            // Animation du bouton
            this.style.transform = 'rotate(360deg) scale(0.9)';
            
            setTimeout(() => {
                this.style.transform = 'rotate(0deg) scale(1)';
                
                // Réinitialiser tous les filtres
                resetAllFilters();
                
                // Réappliquer
                applyFilters();
                updateActiveFilters();
                
                showNotification('Filtres réinitialisés', 'success');
                
                console.log('🔄 Filtres réinitialisés');
            }, 300);
        });
    }
    
    function resetAllFilters() {
        // Réinitialiser les valeurs
        currentFilters = {
            categories: [],
            minPrice: 0,
            maxPrice: 1000000,
            inStock: true,
            onSale: false,
            newArrivals: false,
            rating: null,
            sortBy: 'newest',
            view: currentFilters.view // Garder la vue actuelle
        };
        
        // Réinitialiser les inputs
        const minPriceInput = document.getElementById('min-price');
        const maxPriceInput = document.getElementById('max-price');
        const priceSlider = document.getElementById('price-range');
        
        if (minPriceInput) minPriceInput.value = 0;
        if (maxPriceInput) maxPriceInput.value = 1000000;
        if (priceSlider) {
            priceSlider.value = 1000000;
            updateSliderGradient(priceSlider);
        }
        
        updatePriceDisplay(0, 1000000);
        
        // Réinitialiser les checkboxes
        const inStockCheckbox = document.getElementById('in-stock');
        const onSaleCheckbox = document.getElementById('on-sale');
        const newArrivalsCheckbox = document.getElementById('new-arrivals');
        
        if (inStockCheckbox) inStockCheckbox.checked = true;
        if (onSaleCheckbox) onSaleCheckbox.checked = false;
        if (newArrivalsCheckbox) newArrivalsCheckbox.checked = false;
        
        // Décocher les radios
        const ratingRadios = document.querySelectorAll('input[name="rating"]');
        ratingRadios.forEach(radio => radio.checked = false);
        
        // Réinitialiser le tri
        const sortSelect = document.getElementById('sort-by');
        if (sortSelect) sortSelect.value = 'newest';
    }
    
    // ===================================
    // CHARGEMENT DES DONNÉES PRODUITS
    // ===================================
    
    function loadProductsData() {
        const productsContainer = document.getElementById('products-container');
        if (!productsContainer) return;
        
        const productItems = productsContainer.querySelectorAll('.product-item-wrapper');
        
        allProducts = Array.from(productItems).map(item => {
            return {
                element: item,
                price: parseFloat(item.getAttribute('data-price')) || 0,
                category: item.getAttribute('data-category') || '',
                name: item.getAttribute('data-name') || '',
                inStock: !item.querySelector('.stock-out'),
                onSale: item.querySelector('.badge-sale') !== null,
                isNew: item.querySelector('.badge-new') !== null,
                rating: 4 // Par défaut
            };
        });
        
        filteredProducts = [...allProducts];
        
        console.log(`📦 ${allProducts.length} produits chargés`);
    }
    
    // ===================================
    // APPLICATION DES FILTRES
    // ===================================
    
    function applyFilters() {
        filteredProducts = allProducts.filter(product => {
            // Filtre prix
            if (product.price < currentFilters.minPrice || product.price > currentFilters.maxPrice) {
                return false;
            }
            
            // Filtre en stock
            if (currentFilters.inStock && !product.inStock) {
                return false;
            }
            
            // Filtre en promotion
            if (currentFilters.onSale && !product.onSale) {
                return false;
            }
            
            // Filtre nouveautés
            if (currentFilters.newArrivals && !product.isNew) {
                return false;
            }
            
            // Filtre notation
            if (currentFilters.rating && product.rating < currentFilters.rating) {
                return false;
            }
            
            return true;
        });
        
        sortProducts();
        displayProducts();
        updateProductCount();
        
        console.log(`🔍 ${filteredProducts.length} produits après filtrage`);
    }
    
    // ===================================
    // AFFICHAGE DES PRODUITS
    // ===================================
    
    function displayProducts() {
        const productsContainer = document.getElementById('products-container');
        if (!productsContainer) return;
        
        // Cacher tous les produits
        allProducts.forEach(product => {
            product.element.style.display = 'none';
            product.element.style.opacity = '0';
        });
        
        // Afficher les produits filtrés avec animation
        filteredProducts.forEach((product, index) => {
            product.element.style.display = 'block';
            
            setTimeout(() => {
                product.element.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
                product.element.style.opacity = '1';
                product.element.style.transform = 'translateY(0)';
            }, index * 50); // Animation échelonnée
        });
        
        // Afficher message si aucun produit
        if (filteredProducts.length === 0) {
            showNoProductsMessage(productsContainer);
        } else {
            hideNoProductsMessage(productsContainer);
        }
    }
    
    function showNoProductsMessage(container) {
        let noProductsDiv = container.querySelector('.no-products-container');
        
        if (!noProductsDiv) {
            noProductsDiv = document.createElement('div');
            noProductsDiv.className = 'no-products-container';
            noProductsDiv.innerHTML = `
                <div class="no-products-card">
                    <div class="no-products-icon">
                        <i class="fas fa-box-open"></i>
                    </div>
                    <h3 class="no-products-title">Aucun produit trouvé</h3>
                    <p class="no-products-text">
                        Désolé, nous n'avons trouvé aucun produit correspondant à vos critères.
                    </p>
                    <button class="btn-reset-search" onclick="document.getElementById('reset-filters').click()">
                        <i class="fas fa-redo"></i>
                        Réinitialiser les filtres
                    </button>
                </div>
            `;
            container.appendChild(noProductsDiv);
        }
        
        noProductsDiv.style.display = 'block';
    }
    
    function hideNoProductsMessage(container) {
        const noProductsDiv = container.querySelector('.no-products-container');
        if (noProductsDiv) {
            noProductsDiv.style.display = 'none';
        }
    }
    
    function updateProductCount() {
        const countElement = document.getElementById('product-count');
        if (countElement) {
            countElement.textContent = filteredProducts.length;
            
            // Animation du compteur
            countElement.style.transform = 'scale(1.2)';
            countElement.style.color = '#e74c3c';
            
            setTimeout(() => {
                countElement.style.transform = 'scale(1)';
                countElement.style.color = '';
            }, 300);
        }
    }
    
    // ===================================
    // FILTRES ACTIFS
    // ===================================
    
    function updateActiveFilters() {
        const container = document.getElementById('active-filters');
        if (!container) return;
        
        container.innerHTML = '';
        
        // Filtre prix
        if (currentFilters.minPrice > 0 || currentFilters.maxPrice < 1000000) {
            addFilterTag(container, 'Prix', `${formatNumber(currentFilters.minPrice)} - ${formatNumber(currentFilters.maxPrice)} FCFA`, 'price');
        }
        
        // Filtre en promotion
        if (currentFilters.onSale) {
            addFilterTag(container, 'En promotion', null, 'onSale');
        }
        
        // Filtre nouveautés
        if (currentFilters.newArrivals) {
            addFilterTag(container, 'Nouveautés', null, 'newArrivals');
        }
        
        // Filtre notation
        if (currentFilters.rating) {
            addFilterTag(container, 'Note', `${currentFilters.rating}+ étoiles`, 'rating');
        }
    }
    
    function addFilterTag(container, label, value, filterType) {
        const tag = document.createElement('div');
        tag.className = 'filter-tag';
        tag.innerHTML = `
            <i class="fas fa-filter"></i>
            <span>${label}${value ? ': ' + value : ''}</span>
            <button class="filter-tag-remove" data-filter="${filterType}">
                <i class="fas fa-times"></i>
            </button>
        `;
        
        container.appendChild(tag);
        
        // Gestionnaire de suppression
        const removeBtn = tag.querySelector('.filter-tag-remove');
        removeBtn.addEventListener('click', function() {
            removeFilter(filterType);
            tag.style.animation = 'slideOut 0.3s ease';
            setTimeout(() => tag.remove(), 300);
        });
    }
    
    function removeFilter(filterType) {
        switch (filterType) {
            case 'price':
                currentFilters.minPrice = 0;
                currentFilters.maxPrice = 1000000;
                document.getElementById('min-price').value = 0;
                document.getElementById('max-price').value = 1000000;
                document.getElementById('price-range').value = 1000000;
                updatePriceDisplay(0, 1000000);
                updateSliderGradient(document.getElementById('price-range'));
                break;
            
            case 'onSale':
                currentFilters.onSale = false;
                document.getElementById('on-sale').checked = false;
                break;
            
            case 'newArrivals':
                currentFilters.newArrivals = false;
                document.getElementById('new-arrivals').checked = false;
                break;
            
            case 'rating':
                currentFilters.rating = null;
                document.querySelectorAll('input[name="rating"]').forEach(radio => radio.checked = false);
                break;
        }
        
        applyFilters();
        updateActiveFilters();
    }
    
    // ===================================
    // AJOUT AU PANIER - VÉRITABLE AJAX
    // ===================================
    
    function initProductCards() {
        const addToCartButtons = document.querySelectorAll('.add-to-cart-btn');
        
        addToCartButtons.forEach(button => {
            button.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                
                const variantId = this.getAttribute('data-variant-id');
                
                if (!variantId || variantId === 'None') {
                    showNotification('Ce produit n\'est pas disponible', 'error');
                    return;
                }
                
                addToCart(variantId, this);
            });
        });
        
        console.log(`🛒 ${addToCartButtons.length} boutons panier initialisés`);
    }
    
    function addToCart(variantId, button) {
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
                
                console.log(`✅ Produit ${variantId} ajouté au panier`);
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
            const currentCount = parseInt(badge.textContent) || 0;
            const newCount = cartCount !== undefined ? cartCount : currentCount + 1;
            
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
    // SYSTÈME DE NOTIFICATIONS
    // ===================================
    
    function initNotifications() {
        // Le CSS pour les notifications est déjà injecté
        console.log('🔔 Système de notifications initialisé');
    }
    
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
    
    // ===================================
    // PRÉFÉRENCES UTILISATEUR
    // ===================================
    
    function saveUserPreferences() {
        const preferences = {
            view: currentFilters.view,
            sortBy: currentFilters.sortBy
        };
        
        try {
            localStorage.setItem('productListPreferences', JSON.stringify(preferences));
            console.log('💾 Préférences sauvegardées');
        } catch (e) {
            console.warn('Impossible de sauvegarder les préférences:', e);
        }
    }
    
    function restoreUserPreferences() {
        try {
            const saved = localStorage.getItem('productListPreferences');
            if (saved) {
                const preferences = JSON.parse(saved);
                
                // Restaurer la vue
                if (preferences.view) {
                    currentFilters.view = preferences.view;
                    const viewButton = document.querySelector(`[data-view="${preferences.view}"]`);
                    if (viewButton) viewButton.click();
                }
                
                // Restaurer le tri
                if (preferences.sortBy) {
                    currentFilters.sortBy = preferences.sortBy;
                    const sortSelect = document.getElementById('sort-by');
                    if (sortSelect) sortSelect.value = preferences.sortBy;
                }
                
                console.log('📂 Préférences restaurées');
            }
        } catch (e) {
            console.warn('Impossible de restaurer les préférences:', e);
        }
    }
    
    // ===================================
    // FONCTIONS UTILITAIRES
    // ===================================
    
    function getProductPrice(product) {
        return product.price;
    }
    
    function getProductName(product) {
        return product.name.toLowerCase();
    }
    
    function getProductPopularity(product) {
        // Calculer la popularité basée sur plusieurs critères
        let score = 0;
        if (product.onSale) score += 50;
        if (product.isNew) score += 30;
        if (product.rating) score += product.rating * 10;
        return score;
    }
    
    function formatNumber(num) {
        return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ' ');
    }
    
    // ===================================
    // INJECTION DU CSS POUR LES NOTIFICATIONS
    // ===================================
    
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
            
            @keyframes slideOut {
                from {
                    transform: translateX(0);
                    opacity: 1;
                }
                to {
                    transform: translateX(400px);
                    opacity: 0;
                }
            }
            
            .product-item-wrapper {
                transition: opacity 0.5s ease, transform 0.5s ease;
            }
            
            .btn-success {
                background-color: #27ae60 !important;
                border-color: #27ae60 !important;
            }
        `;
        document.head.appendChild(style);
    }
    
    // ===================================
    // EXPORT GLOBAL
    // ===================================
    
    window.ProductList = {
        applyFilters,
        resetAllFilters,
        updateProductCount,
        addToCart,
        showNotification
    };
    
    // Injecter les styles au chargement
    injectNotificationStyles();
    
    console.log('🎉 Product List JS AJAX complètement chargé et fonctionnel');
    
})();