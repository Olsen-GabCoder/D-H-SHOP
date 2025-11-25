/**
 * ========================================
 * DASHBOARD.JS - Tableau de Bord
 * ========================================
 * Gestion des animations, compteurs et interactions
 * du tableau de bord utilisateur
 */

(function() {
    'use strict';

    /**
     * Initialisation au chargement du DOM
     */
    document.addEventListener('DOMContentLoaded', function() {
        
        // ============================================
        // ANIMATION DES COMPTEURS
        // ============================================
        
        /**
         * Anime un compteur de 0 à la valeur cible
         * @param {HTMLElement} element - L'élément à animer
         * @param {number} target - La valeur cible
         * @param {number} duration - Durée de l'animation en ms
         */
        function animateCounter(element, target, duration = 2000) {
            const start = 0;
            const increment = target / (duration / 16);
            let current = start;
            
            const timer = setInterval(() => {
                current += increment;
                if (current >= target) {
                    current = target;
                    clearInterval(timer);
                }
                element.textContent = Math.floor(current);
            }, 16);
        }
        
        // Observer pour les statistiques
        const statValues = document.querySelectorAll('.stat-value');
        const observerOptions = {
            threshold: 0.5,
            rootMargin: '0px 0px -100px 0px'
        };
        
        const statsObserver = new IntersectionObserver(function(entries) {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const target = parseInt(entry.target.dataset.count) || 0;
                    if (target > 0) {
                        animateCounter(entry.target, target);
                    }
                    statsObserver.unobserve(entry.target);
                }
            });
        }, observerOptions);
        
        statValues.forEach(stat => {
            statsObserver.observe(stat);
        });
        
        // ============================================
        // ANIMATION DES STAT CARDS
        // ============================================
        const statCards = document.querySelectorAll('.stat-card');
        
        statCards.forEach((card, index) => {
            card.style.opacity = '0';
            card.style.transform = 'translateY(30px)';
            
            setTimeout(() => {
                card.style.transition = 'all 0.6s cubic-bezier(0.68, -0.55, 0.265, 1.55)';
                card.style.opacity = '1';
                card.style.transform = 'translateY(0)';
            }, 100 + (index * 100));
        });
        
        // ============================================
        // FERMER LA TIPS CARD
        // ============================================
        const tipsClose = document.querySelector('.tips-close');
        
        if (tipsClose) {
            tipsClose.addEventListener('click', function() {
                const tipsCard = this.closest('.tips-card');
                tipsCard.style.opacity = '0';
                tipsCard.style.transform = 'translateY(-20px)';
                
                setTimeout(() => {
                    tipsCard.remove();
                }, 300);
            });
        }
        
        // ============================================
        // ANIMATION DES ORDER ITEMS
        // ============================================
        const orderItems = document.querySelectorAll('.order-item');
        
        orderItems.forEach((item, index) => {
            item.style.opacity = '0';
            item.style.transform = 'translateX(-30px)';
            
            setTimeout(() => {
                item.style.transition = 'all 0.5s ease';
                item.style.opacity = '1';
                item.style.transform = 'translateX(0)';
            }, 200 + (index * 100));
        });
        
        // ============================================
        // ANIMATION DES ACTION CARDS
        // ============================================
        const actionCards = document.querySelectorAll('.action-card');
        
        actionCards.forEach((card, index) => {
            card.style.opacity = '0';
            card.style.transform = 'scale(0.9)';
            
            setTimeout(() => {
                card.style.transition = 'all 0.5s cubic-bezier(0.68, -0.55, 0.265, 1.55)';
                card.style.opacity = '1';
                card.style.transform = 'scale(1)';
            }, 300 + (index * 100));
        });
        
        // ============================================
        // HOVER EFFECT SUR LES NAV ITEMS
        // ============================================
        const navItems = document.querySelectorAll('.nav-item');
        
        navItems.forEach(item => {
            item.addEventListener('mouseenter', function() {
                if (!this.classList.contains('active')) {
                    const icon = this.querySelector('.nav-icon');
                    if (icon) {
                        icon.style.transform = 'scale(1.1) rotate(5deg)';
                    }
                }
            });
            
            item.addEventListener('mouseleave', function() {
                const icon = this.querySelector('.nav-icon');
                if (icon) {
                    icon.style.transform = 'scale(1) rotate(0deg)';
                }
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
                        const offset = 100;
                        const targetPosition = target.getBoundingClientRect().top + window.pageYOffset - offset;
                        window.scrollTo({
                            top: targetPosition,
                            behavior: 'smooth'
                        });
                    }
                }
            });
        });
        
        // ============================================
        // EFFET PARALLAX LÉGER SUR LE HERO
        // ============================================
        let ticking = false;
        
        window.addEventListener('scroll', function() {
            if (!ticking) {
                window.requestAnimationFrame(function() {
                    const scrolled = window.pageYOffset;
                    const hero = document.querySelector('.dashboard-hero');
                    
                    if (hero && scrolled < hero.offsetHeight) {
                        hero.style.transform = `translateY(${scrolled * 0.3}px)`;
                    }
                    
                    ticking = false;
                });
                
                ticking = true;
            }
        });
        
        // ============================================
        // COPIER LE NUMÉRO DE COMMANDE AU CLIC
        // ============================================
        const orderNumbers = document.querySelectorAll('.order-number');
        
        orderNumbers.forEach(orderNum => {
            orderNum.style.cursor = 'pointer';
            orderNum.setAttribute('title', 'Cliquer pour copier');
            
            orderNum.addEventListener('click', function(e) {
                e.preventDefault();
                const text = this.textContent.trim();
                
                // Copie dans le presse-papier
                navigator.clipboard.writeText(text).then(() => {
                    // Notification de succès
                    showNotification('✓ Numéro copié !', 'success');
                }).catch(err => {
                    console.error('Erreur lors de la copie:', err);
                    showNotification('Erreur lors de la copie', 'error');
                });
            });
        });
        
        // ============================================
        // SYSTÈME DE NOTIFICATIONS
        // ============================================
        
        /**
         * Affiche une notification toast
         * @param {string} message - Message à afficher
         * @param {string} type - Type de notification (success, error, info, warning)
         */
        function showNotification(message, type = 'info') {
            const notification = document.createElement('div');
            notification.textContent = message;
            notification.className = `toast-notification toast-${type}`;
            notification.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                padding: 15px 25px;
                background: ${getNotificationColor(type)};
                color: white;
                border-radius: 10px;
                box-shadow: 0 5px 20px rgba(0,0,0,0.2);
                z-index: 9999;
                font-weight: 600;
                animation: slideInRight 0.3s ease;
                transition: all 0.3s ease;
            `;
            
            document.body.appendChild(notification);
            
            setTimeout(() => {
                notification.style.opacity = '0';
                notification.style.transform = 'translateX(100%)';
                setTimeout(() => notification.remove(), 300);
            }, 2000);
        }
        
        /**
         * Retourne la couleur selon le type de notification
         * @param {string} type - Type de notification
         * @returns {string} - Code couleur
         */
        function getNotificationColor(type) {
            const colors = {
                success: '#28a745',
                error: '#dc3545',
                info: '#17a2b8',
                warning: '#ffc107'
            };
            return colors[type] || colors.info;
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
            
            @keyframes fadeInUp {
                from {
                    opacity: 0;
                    transform: translateY(30px);
                }
                to {
                    opacity: 1;
                    transform: translateY(0);
                }
            }
        `;
        document.head.appendChild(style);
        
        // ============================================
        // DÉTECTION DE LA VISIBILITÉ DE L'ONGLET
        // ============================================
        document.addEventListener('visibilitychange', function() {
            if (!document.hidden) {
                // L'utilisateur revient sur l'onglet
                console.log('Utilisateur de retour - Refresh possible');
                // Vous pouvez déclencher un refresh des données ici
            }
        });
        
        // ============================================
        // GESTION DU FORMULAIRE DE DÉCONNEXION
        // ============================================
        const logoutForm = document.querySelector('form[action*="logout"]');
        
        if (logoutForm) {
            logoutForm.addEventListener('submit', function(e) {
                // Ajout d'une animation de sortie (optionnel)
                const navItem = this.closest('.nav-item');
                if (navItem) {
                    navItem.style.opacity = '0.5';
                }
            });
        }
        
        // ============================================
        // PRÉCHARGEMENT DES IMAGES (Optionnel)
        // ============================================
        function preloadImages() {
            const images = document.querySelectorAll('img[data-src]');
            images.forEach(img => {
                const src = img.getAttribute('data-src');
                if (src) {
                    img.src = src;
                    img.removeAttribute('data-src');
                }
            });
        }
        
        preloadImages();
        
        // ============================================
        // REFRESH AUTOMATIQUE DES STATS (Optionnel)
        // ============================================
        
        /**
         * Rafraîchit les statistiques du dashboard
         * À implémenter avec des appels AJAX vers le backend
         */
        function refreshStats() {
            // Exemple d'implémentation :
            /*
            fetch('/api/dashboard/stats')
                .then(response => response.json())
                .then(data => {
                    // Mettre à jour les valeurs
                    document.querySelector('[data-count]').dataset.count = data.totalOrders;
                    // Réanimer les compteurs
                })
                .catch(error => {
                    console.error('Erreur lors du refresh:', error);
                });
            */
            console.log('Refresh stats...');
        }
        
        // Décommenter pour activer le refresh automatique toutes les 60 secondes
        /*
        setInterval(() => {
            if (!document.hidden) {
                refreshStats();
            }
        }, 60000);
        */
        
        // ============================================
        // LOGGING POUR LE DÉVELOPPEMENT
        // ============================================
        console.log('✅ Dashboard JS initialisé avec succès');
        console.log(`📊 ${statCards.length} statistiques chargées`);
        console.log(`📦 ${orderItems.length} commandes affichées`);
        
    });
    
})();