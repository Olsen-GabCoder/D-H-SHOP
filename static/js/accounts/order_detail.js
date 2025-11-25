/**
 * ========================================
 * ORDER_DETAIL.JS - Détail d'une Commande
 * ========================================
 * Gestion de la page de détail avec :
 * - Modal d'annulation
 * - Copie du numéro de commande
 * - Notifications
 * - Mode impression
 * - Animations et interactions
 */

(function() {
    'use strict';

    document.addEventListener('DOMContentLoaded', function() {
        
        // ============================================
        // MODAL ANNULATION COMMANDE
        // ============================================
        window.cancelOrderModal = function() {
            const modal = document.createElement('div');
            modal.className = 'modal-overlay';
            modal.innerHTML = `
                <div class="modal-content">
                    <div class="modal-icon">
                        <i class="fas fa-exclamation-triangle"></i>
                    </div>
                    <h3 class="modal-title">Annuler cette commande ?</h3>
                    <p class="modal-text">
                        Cette action est irréversible. Pour annuler votre commande, 
                        veuillez contacter notre service client qui traitera votre demande dans les plus brefs délais.
                    </p>
                    <div class="modal-actions">
                        <button class="modal-btn cancel" onclick="closeModal()">
                            Retour
                        </button>
                        <button class="modal-btn confirm" onclick="contactSupport()">
                            Contacter le service client
                        </button>
                    </div>
                </div>
            `;
            
            document.body.appendChild(modal);
            
            setTimeout(() => {
                modal.classList.add('show');
            }, 10);
            
            // Fermer en cliquant dehors
            modal.addEventListener('click', function(e) {
                if (e.target === modal) {
                    closeModal();
                }
            });
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
        
        window.contactSupport = function() {
            // TODO: Rediriger vers la page de contact ou ouvrir le chat
            showNotification('Redirection vers le service client...', 'info');
            setTimeout(() => {
                window.location.href = '/contact/'; // Adapter l'URL selon votre config
            }, 1000);
        };
        
        // ============================================
        // COPIER NUMÉRO DE COMMANDE
        // ============================================
        const orderNumber = document.querySelector('.hero-title');
        if (orderNumber) {
            orderNumber.style.cursor = 'pointer';
            orderNumber.title = 'Cliquer pour copier le numéro';
            
            orderNumber.addEventListener('click', function() {
                const text = this.textContent.replace('Commande ', '').trim();
                
                if (navigator.clipboard && navigator.clipboard.writeText) {
                    navigator.clipboard.writeText(text).then(() => {
                        showNotification('Numéro de commande copié !', 'success');
                        
                        // Effet visuel
                        this.style.transform = 'scale(1.05)';
                        setTimeout(() => {
                            this.style.transform = 'scale(1)';
                        }, 200);
                    }).catch(err => {
                        console.error('Erreur lors de la copie:', err);
                        fallbackCopyText(text);
                    });
                } else {
                    fallbackCopyText(text);
                }
            });
        }
        
        // Fallback pour la copie (navigateurs plus anciens)
        function fallbackCopyText(text) {
            const textArea = document.createElement('textarea');
            textArea.value = text;
            textArea.style.position = 'fixed';
            textArea.style.left = '-999999px';
            document.body.appendChild(textArea);
            textArea.select();
            
            try {
                document.execCommand('copy');
                showNotification('Numéro de commande copié !', 'success');
            } catch (err) {
                showNotification('Impossible de copier', 'error');
            }
            
            document.body.removeChild(textArea);
        }
        
        // ============================================
        // SYSTÈME DE NOTIFICATIONS
        // ============================================
        window.showNotification = function(message, type = 'info') {
            const notification = document.createElement('div');
            notification.className = 'notification-toast';
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
                animation: slideIn 0.3s ease;
                max-width: 400px;
            `;
            
            notification.innerHTML = `
                <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'times-circle' : 'info-circle'}"></i>
                <span>${message}</span>
            `;
            
            document.body.appendChild(notification);
            
            setTimeout(() => {
                notification.style.animation = 'slideOut 0.3s ease';
                setTimeout(() => notification.remove(), 300);
            }, 3000);
        };
        
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
        
        document.querySelectorAll('.content-card, .status-card').forEach(card => {
            card.style.opacity = '0';
            card.style.transform = 'translateY(30px)';
            card.style.transition = 'all 0.6s ease';
            observer.observe(card);
        });
        
        // ============================================
        // RACCOURCIS CLAVIER
        // ============================================
        document.addEventListener('keydown', function(e) {
            // Escape pour fermer la modal
            if (e.key === 'Escape') {
                closeModal();
            }
            
            // Ctrl/Cmd + P pour imprimer
            if ((e.ctrlKey || e.metaKey) && e.key === 'p') {
                e.preventDefault();
                window.print();
            }
        });
        
        // ============================================
        // HIGHLIGHT DES ÉLÉMENTS IMPORTANTS
        // ============================================
        const importantElements = document.querySelectorAll('.total-value, .status-badge, .amount-value');
        importantElements.forEach(element => {
            element.style.transition = 'transform 0.2s ease';
            
            element.addEventListener('mouseenter', function() {
                this.style.transform = 'scale(1.05)';
            });
            
            element.addEventListener('mouseleave', function() {
                this.style.transform = 'scale(1)';
            });
        });
        
        // ============================================
        // SMOOTH SCROLL POUR LES ANCRES
        // ============================================
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function(e) {
                const href = this.getAttribute('href');
                if (href !== '#' && href.length > 1) {
                    e.preventDefault();
                    const target = document.querySelector(href);
                    if (target) {
                        target.scrollIntoView({
                            behavior: 'smooth',
                            block: 'start'
                        });
                    }
                }
            });
        });
        
        // ============================================
        // COPIE DU NUMÉRO DE SUIVI
        // ============================================
        const trackingNumbers = document.querySelectorAll('.tracking-number');
        trackingNumbers.forEach(element => {
            element.style.cursor = 'pointer';
            element.title = 'Cliquer pour copier le numéro de suivi';
            
            element.addEventListener('click', function() {
                const text = this.textContent.trim();
                
                if (navigator.clipboard && navigator.clipboard.writeText) {
                    navigator.clipboard.writeText(text).then(() => {
                        showNotification('Numéro de suivi copié !', 'success');
                        
                        // Effet visuel
                        const originalColor = this.style.color;
                        this.style.color = '#28a745';
                        setTimeout(() => {
                            this.style.color = originalColor;
                        }, 1000);
                    });
                }
            });
        });
        
        // ============================================
        // AVANT/APRÈS IMPRESSION
        // ============================================
        window.addEventListener('beforeprint', function() {
            console.log('Préparation de l\'impression...');
            // Vous pouvez ajouter du code ici pour préparer la page avant l'impression
        });
        
        window.addEventListener('afterprint', function() {
            console.log('Impression terminée');
        });
        
        // ============================================
        // ANIMATION DES STATUTS
        // ============================================
        const statusBadges = document.querySelectorAll('.status-badge');
        statusBadges.forEach(badge => {
            badge.style.transition = 'all 0.3s ease';
            
            badge.addEventListener('mouseenter', function() {
                this.style.transform = 'translateY(-2px)';
                this.style.boxShadow = '0 4px 12px rgba(0, 0, 0, 0.15)';
            });
            
            badge.addEventListener('mouseleave', function() {
                this.style.transform = 'translateY(0)';
                this.style.boxShadow = 'none';
            });
        });
        
        // ============================================
        // TOOLTIP POUR LES ACTIONS
        // ============================================
        const actionButtons = document.querySelectorAll('.btn-action');
        actionButtons.forEach(button => {
            button.addEventListener('mouseenter', function() {
                const tooltip = this.querySelector('span');
                if (tooltip) {
                    tooltip.style.transition = 'all 0.3s ease';
                }
            });
        });
        
        // ============================================
        // INTERACTIONS AVEC LES PRODUITS
        // ============================================
        const productItems = document.querySelectorAll('.product-item-modern');
        productItems.forEach(item => {
            item.addEventListener('click', function(e) {
                // Ne pas déclencher si on clique sur un lien ou bouton
                if (e.target.tagName !== 'A' && e.target.tagName !== 'BUTTON') {
                    // Vous pouvez ajouter une action ici, par exemple ouvrir le détail du produit
                    console.log('Produit cliqué');
                }
            });
        });
        
        // ============================================
        // VALIDATION AVANT ANNULATION
        // ============================================
        const cancelButtons = document.querySelectorAll('[onclick*="cancelOrderModal"]');
        cancelButtons.forEach(button => {
            button.addEventListener('click', function(e) {
                // L'action est gérée par la fonction cancelOrderModal()
                console.log('Demande d\'annulation initiée');
            });
        });
        
        // ============================================
        // AMÉLIORATION DE L'ACCESSIBILITÉ
        // ============================================
        
        // Ajouter des rôles ARIA si nécessaire
        const modals = document.querySelectorAll('.modal-overlay');
        modals.forEach(modal => {
            modal.setAttribute('role', 'dialog');
            modal.setAttribute('aria-modal', 'true');
        });
        
        // Focus trap dans la modal
        document.addEventListener('keydown', function(e) {
            const modal = document.querySelector('.modal-overlay.show');
            if (modal && e.key === 'Tab') {
                const focusableElements = modal.querySelectorAll(
                    'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
                );
                
                const firstElement = focusableElements[0];
                const lastElement = focusableElements[focusableElements.length - 1];
                
                if (e.shiftKey) {
                    if (document.activeElement === firstElement) {
                        e.preventDefault();
                        lastElement.focus();
                    }
                } else {
                    if (document.activeElement === lastElement) {
                        e.preventDefault();
                        firstElement.focus();
                    }
                }
            }
        });
        
        // ============================================
        // GESTION DE L'ÉTAT DE CHARGEMENT
        // ============================================
        window.addEventListener('load', function() {
            // Masquer l'indicateur de chargement si présent
            const loader = document.querySelector('.page-loader');
            if (loader) {
                loader.style.opacity = '0';
                setTimeout(() => {
                    loader.remove();
                }, 300);
            }
        });
        
        // ============================================
        // DÉTECTION DU MODE SOMBRE (OPTIONNEL)
        // ============================================
        if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
            console.log('Mode sombre détecté');
            // Vous pouvez ajouter des ajustements pour le mode sombre ici
        }
        
        // ============================================
        // SUIVI DES INTERACTIONS (ANALYTICS)
        // ============================================
        function trackEvent(eventName, eventData) {
            // TODO: Intégrer avec votre système d'analytics
            console.log('Event tracked:', eventName, eventData);
        }
        
        // Exemple d'utilisation
        document.querySelectorAll('.btn-action-full').forEach(button => {
            button.addEventListener('click', function() {
                trackEvent('button_click', {
                    button_type: this.className,
                    button_text: this.textContent.trim()
                });
            });
        });
        
    });

    // ============================================
    // ANIMATIONS CSS ADDITIONNELLES
    // ============================================
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slideIn {
            from {
                transform: translateX(400px);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
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
        
        @keyframes fadeIn {
            from {
                opacity: 0;
            }
            to {
                opacity: 1;
            }
        }
        
        @keyframes scaleIn {
            from {
                transform: scale(0.9);
                opacity: 0;
            }
            to {
                transform: scale(1);
                opacity: 1;
            }
        }
    `;
    document.head.appendChild(style);

})();