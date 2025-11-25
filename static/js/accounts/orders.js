/**
 * ========================================
 * ORDERS.JS - Page Mes Commandes
 * ========================================
 * Gestion de la liste des commandes avec :
 * - Filtrage par statut
 * - Recherche de commandes
 * - Modal de confirmation
 * - Copie du numéro de suivi
 * - Animations et notifications
 */

(function() {
    'use strict';

    document.addEventListener('DOMContentLoaded', function() {
        
        // ============================================
        // COMPTAGE DES COMMANDES PAR STATUT
        // ============================================
        function updateStatusCounts() {
            const orderCards = document.querySelectorAll('.order-card-modern');
            const counts = {
                pending: 0,
                processing: 0,
                shipped: 0,
                delivered: 0
            };
            
            orderCards.forEach(card => {
                const status = card.dataset.status;
                if (counts.hasOwnProperty(status)) {
                    counts[status]++;
                }
            });
            
            // Mettre à jour les compteurs
            Object.keys(counts).forEach(status => {
                const countElement = document.getElementById(`${status}-count`);
                if (countElement) {
                    countElement.textContent = counts[status];
                }
            });
        }
        
        updateStatusCounts();
        
        // ============================================
        // SYSTÈME DE FILTRAGE
        // ============================================
        const filterTabs = document.querySelectorAll('.filter-tab');
        const orderCards = document.querySelectorAll('.order-card-modern');
        
        filterTabs.forEach(tab => {
            tab.addEventListener('click', function() {
                const filter = this.dataset.filter;
                
                // Mettre à jour l'onglet actif
                filterTabs.forEach(t => t.classList.remove('active'));
                this.classList.add('active');
                
                // Filtrer les commandes avec animation
                orderCards.forEach((card, index) => {
                    if (filter === 'all' || card.dataset.status === filter) {
                        setTimeout(() => {
                            card.style.display = 'block';
                            card.style.opacity = '0';
                            card.style.transform = 'translateY(20px)';
                            
                            setTimeout(() => {
                                card.style.transition = 'all 0.4s ease';
                                card.style.opacity = '1';
                                card.style.transform = 'translateY(0)';
                            }, 50);
                        }, index * 50);
                    } else {
                        card.style.opacity = '0';
                        card.style.transform = 'translateY(-20px)';
                        setTimeout(() => {
                            card.style.display = 'none';
                        }, 300);
                    }
                });
            });
        });
        
        // ============================================
        // RECHERCHE DE COMMANDES
        // ============================================
        const searchInput = document.getElementById('order-search');
        const clearButton = document.getElementById('clear-search');
        
        if (searchInput) {
            searchInput.addEventListener('input', function() {
                const searchTerm = this.value.toLowerCase().trim();
                
                // Afficher/masquer le bouton clear
                if (searchTerm.length > 0) {
                    clearButton.style.display = 'block';
                } else {
                    clearButton.style.display = 'none';
                }
                
                // Rechercher dans les numéros de commande
                orderCards.forEach(card => {
                    const orderNumber = card.querySelector('.order-number span').textContent.toLowerCase();
                    
                    if (orderNumber.includes(searchTerm) || searchTerm === '') {
                        card.style.display = 'block';
                        card.style.opacity = '1';
                    } else {
                        card.style.display = 'none';
                    }
                });
            });
            
            // Bouton clear
            if (clearButton) {
                clearButton.addEventListener('click', function() {
                    searchInput.value = '';
                    this.style.display = 'none';
                    searchInput.focus();
                    
                    // Réafficher toutes les commandes
                    orderCards.forEach(card => {
                        card.style.display = 'block';
                        card.style.opacity = '1';
                    });
                });
            }
        }
        
        // ============================================
        // MODAL DE CONFIRMATION
        // ============================================
        window.cancelOrder = function(orderNumber) {
            // Créer la modal
            const modal = document.createElement('div');
            modal.className = 'modal-overlay';
            modal.innerHTML = `
                <div class="modal-content">
                    <div class="modal-icon">
                        <i class="fas fa-exclamation-triangle"></i>
                    </div>
                    <h3 class="modal-title">Annuler la commande ?</h3>
                    <p class="modal-text">
                        Êtes-vous sûr de vouloir annuler la commande <strong>${orderNumber}</strong> ? 
                        Cette action est irréversible.
                    </p>
                    <div class="modal-actions">
                        <button class="modal-btn cancel" onclick="closeModal()">
                            Non, garder
                        </button>
                        <button class="modal-btn confirm" onclick="confirmCancel('${orderNumber}')">
                            Oui, annuler
                        </button>
                    </div>
                </div>
            `;
            
            document.body.appendChild(modal);
            
            // Animation d'apparition
            setTimeout(() => {
                modal.classList.add('show');
            }, 10);
        };
        
        window.closeModal = function() {
            const modal = document.querySelector('.modal-overlay');
            if (modal) {
                modal.classList.remove('show');
                setTimeout(() => {
                    modal.remove();
                }, 300);
            }
        };
        
        window.confirmCancel = function(orderNumber) {
            // TODO: Implémenter l'appel AJAX pour annuler la commande
            console.log('Annulation de la commande:', orderNumber);
            
            // Fermer la modal
            closeModal();
            
            // Afficher une notification de succès
            showNotification('Commande annulée avec succès', 'success');
            
            // Mettre à jour le statut de la carte (simulation)
            const orderCard = document.querySelector(`[data-order="${orderNumber}"]`);
            if (orderCard) {
                const statusBadge = orderCard.querySelector('.order-status-badge');
                statusBadge.className = 'order-status-badge cancelled';
                statusBadge.innerHTML = `
                    <span class="status-dot"></span>
                    <span class="status-text">Annulée</span>
                `;
            }
        };
        
        // ============================================
        // SYSTÈME DE NOTIFICATIONS
        // ============================================
        window.showNotification = function(message, type = 'info') {
            const notification = document.createElement('div');
            notification.className = `notification notification-${type}`;
            notification.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                background: ${type === 'success' ? '#28a745' : type === 'error' ? '#dc3545' : '#17a2b8'};
                color: white;
                padding: 1rem 1.5rem;
                border-radius: 12px;
                box-shadow: 0 4px 20px rgba(0,0,0,0.3);
                z-index: 10000;
                display: flex;
                align-items: center;
                gap: 0.75rem;
                animation: slideInRight 0.3s ease;
            `;
            
            notification.innerHTML = `
                <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'times-circle' : 'info-circle'}"></i>
                <span>${message}</span>
            `;
            
            document.body.appendChild(notification);
            
            setTimeout(() => {
                notification.style.animation = 'slideOutRight 0.3s ease';
                setTimeout(() => notification.remove(), 300);
            }, 3000);
        };
        
        // ============================================
        // COPIER LE NUMÉRO DE SUIVI
        // ============================================
        const trackingNumbers = document.querySelectorAll('.tracking-number');
        trackingNumbers.forEach(element => {
            element.style.cursor = 'pointer';
            element.title = 'Cliquer pour copier';
            
            element.addEventListener('click', function() {
                const text = this.textContent.trim();
                navigator.clipboard.writeText(text).then(() => {
                    showNotification('Numéro de suivi copié !', 'success');
                    
                    // Effet visuel
                    this.style.color = 'var(--success-color)';
                    setTimeout(() => {
                        this.style.color = '';
                    }, 1000);
                });
            });
        });
        
        // ============================================
        // ANIMATION AU SCROLL
        // ============================================
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };
        
        const observer = new IntersectionObserver(function(entries) {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'translateY(0)';
                }
            });
        }, observerOptions);
        
        orderCards.forEach(card => {
            card.style.opacity = '0';
            card.style.transform = 'translateY(30px)';
            card.style.transition = 'all 0.6s ease';
            observer.observe(card);
        });
        
        // ============================================
        // FERMER LA MODAL EN CLIQUANT DEHORS
        // ============================================
        document.addEventListener('click', function(e) {
            if (e.target.classList.contains('modal-overlay')) {
                closeModal();
            }
        });
        
        // ============================================
        // RACCOURCIS CLAVIER
        // ============================================
        document.addEventListener('keydown', function(e) {
            // Escape pour fermer la modal
            if (e.key === 'Escape') {
                closeModal();
            }
            
            // Ctrl/Cmd + F pour focus sur la recherche
            if ((e.ctrlKey || e.metaKey) && e.key === 'f' && searchInput) {
                e.preventDefault();
                searchInput.focus();
            }
        });
        
        // ============================================
        // AUTO-REFRESH DES STATUTS (OPTIONNEL)
        // ============================================
        // Décommenter pour activer le refresh automatique toutes les 30 secondes
        /*
        setInterval(function() {
            // TODO: Implémenter l'appel AJAX pour récupérer les nouveaux statuts
            console.log('Vérification des mises à jour...');
        }, 30000);
        */
        
    });

})();