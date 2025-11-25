/**
 * ========================================
 * PROFILE.JS - Page de Profil
 * ========================================
 * Gestion des animations, interactions et effets
 * visuels de la page de profil utilisateur
 */

(function() {
    'use strict';

    // ============================================
    // INITIALISATION AU CHARGEMENT DU DOM
    // ============================================
    document.addEventListener('DOMContentLoaded', function() {
        initProfilePage();
    });

    /**
     * Initialisation principale de la page de profil
     */
    function initProfilePage() {
        initStatBarsAnimation();
        initCardsAnimation();
        initInfoItemsHover();
        initQuickStatsAnimation();
        initCounterAnimation();
        initSmoothScroll();
        initParallaxEffect();
        initNotificationToggles();
        initEmailCopy();
        
        console.log('✅ Page de profil initialisée');
    }

    // ============================================
    // ANIMATION DES BARRES DE STATISTIQUES
    // ============================================
    function initStatBarsAnimation() {
        const statBars = document.querySelectorAll('.stat-bar-fill');

        const observerOptions = {
            threshold: 0.5,
            rootMargin: '0px 0px -100px 0px'
        };

        const statsObserver = new IntersectionObserver(function(entries) {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const bar = entry.target;
                    const width = bar.style.width;
                    bar.style.width = '0';

                    setTimeout(() => {
                        bar.style.width = width;
                    }, 100);

                    statsObserver.unobserve(entry.target);
                }
            });
        }, observerOptions);

        statBars.forEach(bar => {
            statsObserver.observe(bar);
        });
    }

    // ============================================
    // ANIMATION DES CARTES AU SCROLL
    // ============================================
    function initCardsAnimation() {
        const profileCards = document.querySelectorAll('.profile-card');

        const observerOptions = {
            threshold: 0.5,
            rootMargin: '0px 0px -100px 0px'
        };

        const cardObserver = new IntersectionObserver(function(entries) {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.style.opacity = '0';
                    entry.target.style.transform = 'translateY(30px)';

                    setTimeout(() => {
                        entry.target.style.transition = 'all 0.6s ease';
                        entry.target.style.opacity = '1';
                        entry.target.style.transform = 'translateY(0)';
                    }, 100);

                    cardObserver.unobserve(entry.target);
                }
            });
        }, observerOptions);

        profileCards.forEach(card => {
            cardObserver.observe(card);
        });
    }

    // ============================================
    // EFFET HOVER SUR LES INFO ITEMS
    // ============================================
    function initInfoItemsHover() {
        const infoItems = document.querySelectorAll('.info-item');

        infoItems.forEach(item => {
            item.addEventListener('mouseenter', function() {
                const icon = this.querySelector('.info-icon');
                if (icon) {
                    icon.style.transition = 'all 0.3s ease';
                    icon.style.transform = 'scale(1.1) rotate(5deg)';
                }
            });

            item.addEventListener('mouseleave', function() {
                const icon = this.querySelector('.info-icon');
                if (icon) {
                    icon.style.transform = 'scale(1) rotate(0deg)';
                }
            });
        });
    }

    // ============================================
    // ANIMATION DES STATISTIQUES RAPIDES
    // ============================================
    function initQuickStatsAnimation() {
        const quickStats = document.querySelectorAll('.quick-stat-item');

        quickStats.forEach((stat, index) => {
            stat.style.opacity = '0';
            stat.style.transform = 'translateY(20px)';

            setTimeout(() => {
                stat.style.transition = 'all 0.6s cubic-bezier(0.68, -0.55, 0.265, 1.55)';
                stat.style.opacity = '1';
                stat.style.transform = 'translateY(0)';
            }, 200 + (index * 100));
        });
    }

    // ============================================
    // COMPTEUR ANIMÉ POUR LES STATISTIQUES
    // ============================================
    function initCounterAnimation() {
        const observerOptions = {
            threshold: 0.5,
            rootMargin: '0px 0px -100px 0px'
        };

        const statValues = document.querySelectorAll('.stat-detailed-value');

        const counterObserver = new IntersectionObserver(function(entries) {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const value = parseInt(entry.target.textContent.replace(/\D/g, ''));
                    if (!isNaN(value) && value > 0) {
                        animateCounter(entry.target, value);
                    }
                    counterObserver.unobserve(entry.target);
                }
            });
        }, observerOptions);

        statValues.forEach(value => {
            counterObserver.observe(value);
        });
    }

    /**
     * Animer un compteur de 0 à une valeur cible
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

    // ============================================
    // SMOOTH SCROLL POUR LES LIENS
    // ============================================
    function initSmoothScroll() {
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
    }

    // ============================================
    // EFFET PARALLAX LÉGER SUR LE HERO
    // ============================================
    function initParallaxEffect() {
        let ticking = false;

        window.addEventListener('scroll', function() {
            if (!ticking) {
                window.requestAnimationFrame(function() {
                    const scrolled = window.pageYOffset;
                    const hero = document.querySelector('.profile-hero');

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
    // TOGGLE NOTIFICATIONS
    // ============================================
    function initNotificationToggles() {
        const notificationToggles = document.querySelectorAll('.status-badge');

        notificationToggles.forEach(toggle => {
            toggle.addEventListener('click', function(e) {
                e.preventDefault();

                // Toggle le statut
                if (this.classList.contains('status-active')) {
                    this.classList.remove('status-active');
                    this.classList.add('status-inactive');
                    this.textContent = 'Désactivé';
                    showNotification('Notification désactivée', 'info');
                } else {
                    this.classList.remove('status-inactive');
                    this.classList.add('status-active');
                    this.textContent = 'Activé';
                    showNotification('Notification activée', 'success');
                }

                // Ici, vous pouvez ajouter un appel AJAX pour sauvegarder la préférence
                // saveNotificationPreference(notificationType, isActive);
            });
        });
    }

    // ============================================
    // COPIER EMAIL AU CLIC
    // ============================================
    function initEmailCopy() {
        const emailElement = document.querySelector('.profile-email');

        if (emailElement) {
            emailElement.style.cursor = 'pointer';
            emailElement.setAttribute('title', 'Cliquer pour copier');

            emailElement.addEventListener('click', function() {
                const email = this.textContent.trim();

                navigator.clipboard.writeText(email).then(() => {
                    showNotification('Email copié dans le presse-papiers !', 'success');
                }).catch(err => {
                    console.error('Erreur lors de la copie:', err);
                    showNotification('Impossible de copier l\'email', 'error');
                });
            });
        }
    }

    // ============================================
    // SYSTÈME DE NOTIFICATIONS
    // ============================================
    function showNotification(message, type = 'info') {
        const iconMap = {
            success: 'check-circle',
            error: 'times-circle',
            warning: 'exclamation-triangle',
            info: 'info-circle'
        };

        const colorMap = {
            success: getComputedStyle(document.documentElement).getPropertyValue('--success-color').trim(),
            error: '#dc3545',
            warning: getComputedStyle(document.documentElement).getPropertyValue('--warning-color').trim(),
            info: getComputedStyle(document.documentElement).getPropertyValue('--info-color').trim()
        };

        const notification = document.createElement('div');
        notification.className = 'profile-notification';
        notification.innerHTML = `
            <i class="fas fa-${iconMap[type] || iconMap.info}"></i>
            <span>${message}</span>
        `;

        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 15px 25px;
            background: ${colorMap[type] || colorMap.info};
            color: white;
            border-radius: 10px;
            box-shadow: 0 5px 20px rgba(0,0,0,0.2);
            z-index: 9999;
            animation: slideIn 0.3s ease;
            display: flex;
            align-items: center;
            gap: 12px;
            font-weight: 600;
        `;

        document.body.appendChild(notification);

        setTimeout(() => {
            notification.style.opacity = '0';
            notification.style.transform = 'translateX(100%)';
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }

    // ============================================
    // SAUVEGARDE DE PRÉFÉRENCES (AJAX)
    // ============================================
    function saveNotificationPreference(type, isActive) {
        // Exemple d'appel AJAX pour sauvegarder les préférences
        // Vous pouvez implémenter cela avec fetch() ou axios

        /*
        fetch('/api/profile/notifications/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                notification_type: type,
                is_active: isActive
            })
        })
        .then(response => response.json())
        .then(data => {
            console.log('Préférence sauvegardée:', data);
        })
        .catch(error => {
            console.error('Erreur:', error);
            showNotification('Erreur lors de la sauvegarde', 'error');
        });
        */

        console.log('Sauvegarde de la préférence:', type, isActive);
    }

    /**
     * Récupérer un cookie par son nom (pour CSRF token)
     */
    function getCookie(name) {
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

    // ============================================
    // ANIMATION DE L'AVATAR AU HOVER
    // ============================================
    const avatar = document.querySelector('.profile-avatar, .profile-avatar-placeholder');
    if (avatar) {
        avatar.addEventListener('mouseenter', function() {
            this.style.transform = 'scale(1.05) rotate(2deg)';
        });

        avatar.addEventListener('mouseleave', function() {
            this.style.transform = 'scale(1) rotate(0deg)';
        });
    }

    // ============================================
    // ANIMATION DES ACTIONS RAPIDES
    // ============================================
    const quickActionBtns = document.querySelectorAll('.quick-action-btn');
    quickActionBtns.forEach((btn, index) => {
        btn.style.opacity = '0';
        btn.style.transform = 'scale(0.8)';

        setTimeout(() => {
            btn.style.transition = 'all 0.4s cubic-bezier(0.68, -0.55, 0.265, 1.55)';
            btn.style.opacity = '1';
            btn.style.transform = 'scale(1)';
        }, 300 + (index * 100));
    });

    // ============================================
    // DÉTECTION DE L'INACTIVITÉ
    // ============================================
    let inactivityTimer;
    const inactivityDelay = 300000; // 5 minutes

    function resetInactivityTimer() {
        clearTimeout(inactivityTimer);
        inactivityTimer = setTimeout(() => {
            console.log('Utilisateur inactif depuis 5 minutes');
            // Vous pouvez ajouter une action ici (ex: avertissement de déconnexion)
        }, inactivityDelay);
    }

    // Événements qui réinitialisent le timer
    ['mousedown', 'mousemove', 'keypress', 'scroll', 'touchstart'].forEach(event => {
        document.addEventListener(event, resetInactivityTimer, true);
    });

    resetInactivityTimer();

})();