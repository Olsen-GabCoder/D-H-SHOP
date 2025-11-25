/**
 * ========================================
 * ORDER-SUCCESS.JS - Page de Confirmation
 * ========================================
 */

(function() {
    'use strict';

    // ============================================
    // ANIMATION CONFETTI
    // ============================================
    
    /**
     * Crée et anime des confettis sur la page
     */
    function createConfetti() {
        const container = document.getElementById('confetti-container');
        if (!container) return;
        
        const colors = ['#f39c12', '#e74c3c', '#3498db', '#2ecc71', '#9b59b6', '#1abc9c'];
        const confettiCount = 50;
        
        for (let i = 0; i < confettiCount; i++) {
            setTimeout(() => {
                const confetti = document.createElement('div');
                confetti.className = 'confetti';
                confetti.style.left = Math.random() * 100 + '%';
                confetti.style.backgroundColor = colors[Math.floor(Math.random() * colors.length)];
                
                const duration = (Math.random() * 3 + 2) + 's';
                const delay = (Math.random() * 2) + 's';
                
                confetti.style.animationDuration = duration;
                confetti.style.animationDelay = delay;
                confetti.style.animation = `confetti-fall ${duration} linear`;
                
                container.appendChild(confetti);
                
                // Nettoyer après l'animation
                setTimeout(() => {
                    if (confetti.parentNode) {
                        confetti.parentNode.removeChild(confetti);
                    }
                }, 5000);
            }, i * 100);
        }
    }

    // ============================================
    // COPIER LE NUMÉRO DE COMMANDE
    // ============================================
    
    /**
     * Copie le numéro de commande dans le presse-papier
     */
    function initCopyOrderNumber() {
        const copyBtn = document.getElementById('copy-order-number');
        if (!copyBtn) return;
        
        copyBtn.addEventListener('click', function() {
            const orderNumber = document.getElementById('order-number');
            if (!orderNumber) return;
            
            const textToCopy = orderNumber.textContent.trim();
            
            // Méthode moderne avec Clipboard API
            if (navigator.clipboard && navigator.clipboard.writeText) {
                navigator.clipboard.writeText(textToCopy)
                    .then(() => showCopySuccess())
                    .catch(() => fallbackCopy(textToCopy));
            } else {
                fallbackCopy(textToCopy);
            }
        });
    }
    
    /**
     * Méthode de fallback pour copier le texte
     * @param {string} text - Texte à copier
     */
    function fallbackCopy(text) {
        const textArea = document.createElement('textarea');
        textArea.value = text;
        textArea.style.position = 'fixed';
        textArea.style.left = '-999999px';
        textArea.style.top = '-999999px';
        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();
        
        try {
            document.execCommand('copy');
            showCopySuccess();
        } catch (err) {
            console.error('Erreur de copie:', err);
            alert('Impossible de copier automatiquement. Numéro: ' + text);
        }
        
        document.body.removeChild(textArea);
    }
    
    /**
     * Affiche un feedback visuel après la copie
     */
    function showCopySuccess() {
        const btn = document.getElementById('copy-order-number');
        if (!btn) return;
        
        const originalHTML = btn.innerHTML;
        btn.innerHTML = '<i class="fas fa-check"></i>';
        btn.classList.remove('btn-outline-success');
        btn.classList.add('btn-success');
        
        // Utiliser showToast si disponible
        if (typeof showToast !== 'undefined') {
            showToast('Numéro de commande copié !', 'success');
        }
        
        // Restaurer l'état original après 2 secondes
        setTimeout(() => {
            btn.innerHTML = originalHTML;
            btn.classList.remove('btn-success');
            btn.classList.add('btn-outline-success');
        }, 2000);
    }

    // ============================================
    // TÉLÉCHARGER LA FACTURE
    // ============================================
    
    /**
     * Initialise le bouton de téléchargement de facture
     */
    function initDownloadInvoice() {
        const downloadBtn = document.getElementById('download-invoice');
        if (!downloadBtn) return;
        
        downloadBtn.addEventListener('click', function(e) {
            e.preventDefault();
            
            const originalHTML = this.innerHTML;
            this.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Téléchargement...';
            this.disabled = true;
            
            // Simuler le téléchargement (remplacer par un vrai appel AJAX)
            setTimeout(() => {
                if (typeof showToast !== 'undefined') {
                    showToast('Facture en cours de génération...', 'info');
                }
                
                // Restaurer le bouton
                setTimeout(() => {
                    this.innerHTML = originalHTML;
                    this.disabled = false;
                    
                    if (typeof showToast !== 'undefined') {
                        showToast('Facture téléchargée avec succès !', 'success');
                    }
                    
                    // TODO: Implémenter le téléchargement réel
                    // window.location.href = '/orders/invoice/' + orderNumber + '/download/';
                }, 1500);
            }, 2000);
        });
    }

    // ============================================
    // ANIMATION DES CARTES AU SCROLL
    // ============================================
    
    /**
     * Anime les cartes lorsqu'elles entrent dans le viewport
     */
    function initScrollAnimations() {
        const cards = document.querySelectorAll('.hover-effect');
        
        if (!('IntersectionObserver' in window)) {
            // Fallback: afficher toutes les cartes
            cards.forEach(card => {
                card.style.opacity = '1';
                card.style.transform = 'translateY(0)';
            });
            return;
        }
        
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };
        
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const target = entry.target;
                    
                    // État initial
                    target.style.opacity = '0';
                    target.style.transform = 'translateY(20px)';
                    target.style.transition = 'all 0.5s ease';
                    
                    // Animation d'entrée avec délai
                    setTimeout(() => {
                        target.style.opacity = '1';
                        target.style.transform = 'translateY(0)';
                    }, 100);
                    
                    // Ne plus observer cet élément
                    observer.unobserve(target);
                }
            });
        }, observerOptions);
        
        cards.forEach(card => observer.observe(card));
    }

    // ============================================
    // SMOOTH SCROLL POUR LES ANCRES
    // ============================================
    
    /**
     * Active le smooth scroll pour les liens d'ancre
     */
    function initSmoothScroll() {
        const links = document.querySelectorAll('a[href^="#"]');
        
        links.forEach(link => {
            link.addEventListener('click', function(e) {
                const href = this.getAttribute('href');
                if (href === '#' || href === '') return;
                
                const target = document.querySelector(href);
                if (target) {
                    e.preventDefault();
                    
                    // Scroll vers l'élément
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                    
                    // Ajouter l'hash à l'URL sans scroller
                    if (history.pushState) {
                        history.pushState(null, null, href);
                    }
                }
            });
        });
    }

    // ============================================
    // GESTION DE L'IMPRESSION
    // ============================================
    
    /**
     * Initialise les événements d'impression
     */
    function initPrintHandlers() {
        const beforePrint = () => {
            console.log('Impression en cours...');
            // Masquer les éléments non nécessaires
            document.querySelectorAll('.no-print').forEach(el => {
                el.style.display = 'none';
            });
        };
        
        const afterPrint = () => {
            console.log('Impression terminée');
            // Restaurer les éléments
            document.querySelectorAll('.no-print').forEach(el => {
                el.style.display = '';
            });
        };
        
        // Méthode moderne
        if (window.matchMedia) {
            const mediaQueryList = window.matchMedia('print');
            mediaQueryList.addListener(mql => {
                if (mql.matches) {
                    beforePrint();
                } else {
                    afterPrint();
                }
            });
        }
        
        // Méthode de fallback
        window.onbeforeprint = beforePrint;
        window.onafterprint = afterPrint;
    }

    // ============================================
    // SYSTÈME DE TOAST
    // ============================================
    
    /**
     * Crée une fonction toast si elle n'existe pas déjà
     */
    function initToastSystem() {
        if (typeof window.showToast !== 'undefined') {
            return; // Déjà défini
        }
        
        /**
         * Affiche un message toast
         * @param {string} message - Message à afficher
         * @param {string} type - Type (success, info, warning, danger)
         */
        window.showToast = function(message, type) {
            type = type || 'info';
            
            // Créer le HTML du toast
            const toastHTML = `
                <div class="toast align-items-center text-white bg-${type} border-0" role="alert" aria-live="assertive" aria-atomic="true">
                    <div class="d-flex">
                        <div class="toast-body">${message}</div>
                        <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
                    </div>
                </div>
            `;
            
            // Créer ou récupérer le conteneur
            let toastContainer = document.querySelector('.toast-container');
            if (!toastContainer) {
                toastContainer = document.createElement('div');
                toastContainer.className = 'toast-container position-fixed top-0 end-0 p-3';
                toastContainer.style.zIndex = '10000';
                document.body.appendChild(toastContainer);
            }
            
            // Ajouter le toast
            const tempDiv = document.createElement('div');
            tempDiv.innerHTML = toastHTML.trim();
            const toastElement = tempDiv.firstChild;
            toastContainer.appendChild(toastElement);
            
            // Initialiser avec Bootstrap Toast si disponible
            if (typeof bootstrap !== 'undefined' && bootstrap.Toast) {
                const bsToast = new bootstrap.Toast(toastElement, {
                    autohide: true,
                    delay: 5000
                });
                bsToast.show();
            } else {
                // Fallback: afficher manuellement
                toastElement.classList.add('show');
                setTimeout(() => {
                    toastElement.classList.remove('show');
                    setTimeout(() => {
                        if (toastElement.parentNode) {
                            toastElement.parentNode.removeChild(toastElement);
                        }
                    }, 300);
                }, 5000);
            }
        };
    }

    // ============================================
    // GESTION DE LA VISIBILITÉ
    // ============================================
    
    /**
     * Détecte les changements de visibilité de la page
     */
    function initVisibilityHandling() {
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                console.log('Page cachée - pause des animations');
            } else {
                console.log('Page visible - reprise des animations');
            }
        });
    }

    // ============================================
    // ACCORDÉON FAQ - ANALYTICS
    // ============================================
    
    /**
     * Suit l'ouverture des items FAQ
     */
    function initFAQTracking() {
        const accordionButtons = document.querySelectorAll('.accordion-button');
        
        accordionButtons.forEach(button => {
            button.addEventListener('click', function() {
                const question = this.textContent.trim();
                console.log('FAQ ouverte:', question);
                
                // TODO: Envoyer à Google Analytics
                // if (typeof gtag !== 'undefined') {
                //     gtag('event', 'faq_opened', {
                //         'event_category': 'engagement',
                //         'event_label': question
                //     });
                // }
            });
        });
    }

    // ============================================
    // VALIDATION DES LIENS
    // ============================================
    
    /**
     * Vérifie et valide les liens de la page
     */
    function validateLinks() {
        const links = document.querySelectorAll('a[href]');
        let brokenLinks = 0;
        
        links.forEach(link => {
            const href = link.getAttribute('href');
            
            // Vérifier les liens vides ou invalides
            if (!href || href === '#' || href === 'javascript:void(0)') {
                console.warn('Lien invalide ou vide:', link);
                brokenLinks++;
            }
        });
        
        if (brokenLinks > 0) {
            console.warn(`${brokenLinks} lien(s) invalide(s) détecté(s)`);
        }
    }

    // ============================================
    // INITIALISATION PRINCIPALE
    // ============================================
    
    /**
     * Fonction d'initialisation principale
     */
    function init() {
        console.log('🎉 Initialisation de la page de confirmation...');
        
        // Lancer les confettis après un court délai
        setTimeout(createConfetti, 500);
        
        // Initialiser tous les modules
        initCopyOrderNumber();
        initDownloadInvoice();
        initScrollAnimations();
        initSmoothScroll();
        initPrintHandlers();
        initToastSystem();
        initVisibilityHandling();
        initFAQTracking();
        
        // Validation en développement
        if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
            validateLinks();
        }
        
        console.log('✅ Page de confirmation chargée avec succès');
    }

    // Démarrer l'initialisation au chargement du DOM
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        // Le DOM est déjà chargé
        init();
    }

})();