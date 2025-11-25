/**
 * ========================================
 * PROFILE_EDIT.JS - Page d'Édition du Profil
 * ========================================
 * Gestion du formulaire d'édition avec :
 * - Preview d'image
 * - Validation en temps réel
 * - Drag & drop
 * - Notifications
 */

(function() {
    'use strict';

    document.addEventListener('DOMContentLoaded', function() {
        
        // ============================================
        // PREVIEW IMAGE
        // ============================================
        const fileInput = document.getElementById('profilePictureInput');
        const profilePreview = document.getElementById('profilePreview');
        
        if (fileInput) {
            fileInput.addEventListener('change', function(e) {
                const file = e.target.files[0];
                
                if (file) {
                    // Vérifier la taille (2MB max)
                    if (file.size > 2 * 1024 * 1024) {
                        alert('La taille du fichier ne doit pas dépasser 2MB');
                        this.value = '';
                        return;
                    }
                    
                    // Vérifier le type
                    if (!file.type.match('image.*')) {
                        alert('Veuillez sélectionner une image valide (JPG, PNG, GIF)');
                        this.value = '';
                        return;
                    }
                    
                    // Prévisualisation
                    const reader = new FileReader();
                    reader.onload = function(e) {
                        profilePreview.innerHTML = `
                            <img src="${e.target.result}" alt="Preview" class="preview-image">
                            <div class="preview-overlay">
                                <i class="fas fa-camera"></i>
                                <p>Changer</p>
                            </div>
                        `;
                    };
                    reader.readAsDataURL(file);
                }
            });
        }
        
        // Click sur preview pour ouvrir le sélecteur
        if (profilePreview) {
            profilePreview.addEventListener('click', function() {
                fileInput.click();
            });
        }
        
        // ============================================
        // SUPPRIMER LA PHOTO
        // ============================================
        const removePhotoBtn = document.getElementById('removePhotoBtn');
        
        if (removePhotoBtn) {
            removePhotoBtn.addEventListener('click', function() {
                if (confirm('Êtes-vous sûr de vouloir supprimer votre photo de profil ?')) {
                    profilePreview.innerHTML = `
                        <div class="preview-placeholder">
                            <i class="fas fa-user"></i>
                        </div>
                        <div class="preview-overlay">
                            <i class="fas fa-camera"></i>
                            <p>Changer</p>
                        </div>
                    `;
                    fileInput.value = '';
                    
                    // Ajouter un champ caché pour signaler la suppression
                    const form = document.getElementById('editProfileForm');
                    let removeInput = form.querySelector('input[name="remove_photo"]');
                    if (!removeInput) {
                        removeInput = document.createElement('input');
                        removeInput.type = 'hidden';
                        removeInput.name = 'remove_photo';
                        removeInput.value = 'true';
                        form.appendChild(removeInput);
                    }
                }
            });
        }
        
        // ============================================
        // VALIDATION DES CHAMPS
        // ============================================
        function validateField(input) {
            const value = input.value.trim();
            const feedback = input.nextElementSibling;
            
            // Email
            if (input.type === 'email') {
                const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
                if (!emailRegex.test(value)) {
                    input.classList.add('is-invalid');
                    input.classList.remove('is-valid');
                    if (feedback) feedback.textContent = 'Email invalide';
                    return false;
                }
            }
            
            // Téléphone
            if (input.id === 'phone') {
                const phoneDigits = value.replace(/\D/g, '');
                if (phoneDigits.length < 8) {
                    input.classList.add('is-invalid');
                    input.classList.remove('is-valid');
                    if (feedback) feedback.textContent = 'Numéro invalide (min. 8 chiffres)';
                    return false;
                }
            }
            
            // Champs requis
            if (input.hasAttribute('required') && !value) {
                input.classList.add('is-invalid');
                input.classList.remove('is-valid');
                if (feedback) feedback.textContent = 'Ce champ est obligatoire';
                return false;
            }
            
            // Valide
            input.classList.remove('is-invalid');
            input.classList.add('is-valid');
            if (feedback) feedback.textContent = '✓ Valide';
            return true;
        }
        
        // Validation en temps réel
        document.querySelectorAll('.form-control-modern').forEach(input => {
            input.addEventListener('blur', function() {
                if (this.value) {
                    validateField(this);
                }
            });
            
            input.addEventListener('input', function() {
                if (this.classList.contains('is-invalid') || this.classList.contains('is-valid')) {
                    validateField(this);
                }
            });
        });
        
        // ============================================
        // FORMATAGE TÉLÉPHONE
        // ============================================
        const phoneInput = document.getElementById('phone');
        
        if (phoneInput) {
            phoneInput.addEventListener('input', function() {
                this.value = this.value.replace(/[^\d\s\+\-\(\)]/g, '');
            });
        }
        
        // ============================================
        // SOUMISSION DU FORMULAIRE
        // ============================================
        const editForm = document.getElementById('editProfileForm');
        const saveBtn = document.querySelector('.btn-save');
        
        if (editForm) {
            editForm.addEventListener('submit', function(e) {
                e.preventDefault();
                
                // Valider tous les champs
                let isValid = true;
                document.querySelectorAll('.form-control-modern[required]').forEach(input => {
                    if (!validateField(input)) {
                        isValid = false;
                    }
                });
                
                if (!isValid) {
                    showNotification('Veuillez corriger les erreurs dans le formulaire', 'error');
                    return;
                }
                
                // Animation du bouton
                saveBtn.classList.add('loading');
                saveBtn.disabled = true;
                
                // Soumettre le formulaire
                setTimeout(() => {
                    this.submit();
                }, 500);
            });
        }
        
        // ============================================
        // NOTIFICATIONS
        // ============================================
        function showNotification(message, type = 'info') {
            const messagesContainer = document.querySelector('.messages-container') || createMessagesContainer();
            
            const alert = document.createElement('div');
            alert.className = `alert-modern alert-${type}`;
            alert.innerHTML = `
                <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i>
                <span>${message}</span>
                <button type="button" class="alert-close" onclick="this.parentElement.remove()">
                    <i class="fas fa-times"></i>
                </button>
            `;
            
            messagesContainer.appendChild(alert);
            
            // Scroll vers le haut
            window.scrollTo({ top: 0, behavior: 'smooth' });
            
            // Auto-dismiss après 5 secondes
            setTimeout(() => {
                alert.style.opacity = '0';
                setTimeout(() => alert.remove(), 300);
            }, 5000);
        }
        
        function createMessagesContainer() {
            const container = document.createElement('div');
            container.className = 'messages-container';
            const form = document.querySelector('.edit-form');
            form.insertBefore(container, form.firstChild);
            return container;
        }
        
        // ============================================
        // ANIMATION DES TOGGLE SWITCHES
        // ============================================
        document.querySelectorAll('.toggle-switch input').forEach(toggle => {
            toggle.addEventListener('change', function() {
                const slider = this.nextElementSibling;
                slider.style.transform = 'scale(1.1)';
                setTimeout(() => {
                    slider.style.transform = 'scale(1)';
                }, 200);
            });
        });
        
        // ============================================
        // CONFIRMATION AVANT DE QUITTER
        // ============================================
        let formChanged = false;
        
        document.querySelectorAll('.form-control-modern, .toggle-switch input').forEach(input => {
            input.addEventListener('change', function() {
                formChanged = true;
            });
        });
        
        if (fileInput) {
            fileInput.addEventListener('change', function() {
                formChanged = true;
            });
        }
        
        window.addEventListener('beforeunload', function(e) {
            if (formChanged && !editForm.classList.contains('submitted')) {
                e.preventDefault();
                e.returnValue = '';
            }
        });
        
        if (editForm) {
            editForm.addEventListener('submit', function() {
                this.classList.add('submitted');
                formChanged = false;
            });
        }
        
        // ============================================
        // AUTO-DISMISS DES MESSAGES
        // ============================================
        setTimeout(() => {
            document.querySelectorAll('.alert-modern').forEach(alert => {
                alert.style.opacity = '0';
                setTimeout(() => alert.remove(), 300);
            });
        }, 5000);
        
        // ============================================
        // ANIMATION AU SCROLL
        // ============================================
        const formCards = document.querySelectorAll('.form-card');
        
        const observerOptions = {
            threshold: 0.1,
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
        
        formCards.forEach(card => {
            cardObserver.observe(card);
        });
        
        // ============================================
        // DRAG & DROP POUR LA PHOTO
        // ============================================
        if (profilePreview) {
            ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
                profilePreview.addEventListener(eventName, preventDefaults, false);
            });
            
            function preventDefaults(e) {
                e.preventDefault();
                e.stopPropagation();
            }
            
            ['dragenter', 'dragover'].forEach(eventName => {
                profilePreview.addEventListener(eventName, function() {
                    this.style.borderColor = 'var(--primary-color)';
                    this.style.borderWidth = '4px';
                }, false);
            });
            
            ['dragleave', 'drop'].forEach(eventName => {
                profilePreview.addEventListener(eventName, function() {
                    this.style.borderColor = 'var(--border-color)';
                    this.style.borderWidth = '4px';
                }, false);
            });
            
            profilePreview.addEventListener('drop', function(e) {
                const dt = e.dataTransfer;
                const files = dt.files;
                
                if (files.length > 0) {
                    fileInput.files = files;
                    const event = new Event('change', { bubbles: true });
                    fileInput.dispatchEvent(event);
                }
            }, false);
        }
        
        // ============================================
        // RACCOURCIS CLAVIER
        // ============================================
        document.addEventListener('keydown', function(e) {
            // Ctrl+S ou Cmd+S pour sauvegarder
            if ((e.ctrlKey || e.metaKey) && e.key === 's') {
                e.preventDefault();
                if (editForm) {
                    editForm.dispatchEvent(new Event('submit', { bubbles: true, cancelable: true }));
                }
            }
            
            // Escape pour annuler
            if (e.key === 'Escape') {
                const cancelBtn = document.querySelector('.btn-cancel');
                if (cancelBtn && confirm('Voulez-vous vraiment quitter sans enregistrer ?')) {
                    window.location.href = cancelBtn.href;
                }
            }
        });
    });
})();