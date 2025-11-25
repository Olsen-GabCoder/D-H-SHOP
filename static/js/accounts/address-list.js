/**
 * ========================================
 * ADDRESS-LIST.JS - Liste des Adresses
 * ========================================
 * Gestion du modal de suppression et interactions
 * avec la liste des adresses
 */

(function() {
    'use strict';

    // Variable pour stocker l'ID de l'adresse à supprimer
    let deleteAddressId = null;

    /**
     * Affiche le modal de confirmation de suppression
     * @param {string} addressId - ID de l'adresse à supprimer
     */
    window.confirmDelete = function(addressId) {
        deleteAddressId = addressId;
        const modal = document.getElementById('deleteModal');
        
        if (modal) {
            modal.classList.add('active');
            document.body.style.overflow = 'hidden';
        }
    };

    /**
     * Ferme le modal de confirmation
     */
    window.closeDeleteModal = function() {
        const modal = document.getElementById('deleteModal');
        
        if (modal) {
            modal.classList.remove('active');
            document.body.style.overflow = 'auto';
            deleteAddressId = null;
        }
    };

    /**
     * Soumet le formulaire de suppression
     */
    window.submitDelete = function() {
        if (deleteAddressId) {
            const form = document.getElementById(`delete-form-${deleteAddressId}`);
            
            if (form) {
                form.submit();
            }
        }
    };

    /**
     * Initialisation au chargement du DOM
     */
    document.addEventListener('DOMContentLoaded', function() {
        
        const modal = document.getElementById('deleteModal');
        
        // ============================================
        // GESTION DU MODAL
        // ============================================
        
        if (modal) {
            // Fermer le modal en cliquant à l'extérieur
            modal.addEventListener('click', function(e) {
                if (e.target === modal) {
                    window.closeDeleteModal();
                }
            });
        }
        
        // Fermer le modal avec la touche Échap
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape' && modal && modal.classList.contains('active')) {
                window.closeDeleteModal();
            }
        });
        
        // ============================================
        // ANIMATION DES CARTES D'ADRESSES
        // ============================================
        
        const addressCards = document.querySelectorAll('.address-card');
        
        addressCards.forEach((card, index) => {
            card.style.opacity = '0';
            card.style.transform = 'translateY(30px)';
            
            setTimeout(() => {
                card.style.transition = 'all 0.6s cubic-bezier(0.68, -0.55, 0.265, 1.55)';
                card.style.opacity = '1';
                card.style.transform = 'translateY(0)';
            }, 100 + (index * 100));
        });
        
        // ============================================
        // ANIMATION DES STATS
        // ============================================
        
        const statItems = document.querySelectorAll('.stat-item');
        
        statItems.forEach((item, index) => {
            item.style.opacity = '0';
            item.style.transform = 'scale(0.9)';
            
            setTimeout(() => {
                item.style.transition = 'all 0.5s cubic-bezier(0.68, -0.55, 0.265, 1.55)';
                item.style.opacity = '1';
                item.style.transform = 'scale(1)';
            }, 50 + (index * 100));
        });
        
        // ============================================
        // CONFIRMATION AVANT SOUMISSION DES FORMULAIRES
        // ============================================
        
        const setDefaultForms = document.querySelectorAll('form[action*="set_default"]');
        
        setDefaultForms.forEach(form => {
            form.addEventListener('submit', function(e) {
                // Ajouter une animation de chargement (optionnel)
                const button = this.querySelector('button[type="submit"]');
                if (button) {
                    button.disabled = true;
                    button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> <span>Chargement...</span>';
                }
            });
        });
        
        // ============================================
        // COPIER L'ADRESSE AU CLIC (Optionnel)
        // ============================================
        
        const addressDetails = document.querySelectorAll('.address-details');
        
        addressDetails.forEach(detail => {
            detail.style.cursor = 'pointer';
            detail.setAttribute('title', 'Cliquer pour copier l\'adresse');
            
            detail.addEventListener('click', function(e) {
                // Ne pas copier si on clique sur un bouton
                if (e.target.closest('.btn-action')) {
                    return;
                }
                
                // Extraire le texte de l'adresse
                const detailLines = this.querySelectorAll('.detail-line');
                const addressText = Array.from(detailLines)
                    .map(line => line.textContent.trim())
                    .join('\n');
                
                // Copier dans le presse-papier
                navigator.clipboard.writeText(addressText).then(() => {
                    showNotification('✓ Adresse copiée !', 'success');
                }).catch(err => {
                    console.error('Erreur lors de la copie:', err);
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
                z-index: 99999;
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
        `;
        document.head.appendChild(style);
        
        // ============================================
        // INITIALISATION AOS (Animation On Scroll)
        // ============================================
        
        if (typeof AOS !== 'undefined') {
            AOS.init({
                duration: 800,
                easing: 'ease-in-out',
                once: true,
                offset: 100
            });
        }
        
        // ============================================
        // LOGGING POUR LE DÉVELOPPEMENT
        // ============================================
        
        console.log('✅ Address List JS initialisé avec succès');
        console.log(`📍 ${addressCards.length} adresse(s) chargée(s)`);
        
    });
    
})();