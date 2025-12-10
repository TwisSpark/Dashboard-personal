// ============================================================
// PERFIL.JS - Gestión de Avatar y Perfil
// ============================================================

document.addEventListener('DOMContentLoaded', function() {
    const avatarInput = document.getElementById('avatarInput');
    const avatarPreview = document.getElementById('avatarPreview');
    const deleteAvatar = document.getElementById('deleteAvatar');
    const avatarMessage = document.getElementById('avatarMessage');

    // ===== SUBIR AVATAR =====
    if (avatarInput) {
        avatarInput.addEventListener('change', async function(e) {
            const file = e.target.files[0];
            
            if (!file) return;
            
            // Validar tipo de archivo
            const allowedTypes = ['image/png', 'image/jpeg', 'image/jpg', 'image/gif', 'image/webp'];
            if (!allowedTypes.includes(file.type)) {
                mostrarMensaje('Formato no permitido. Usa: PNG, JPG, JPEG, GIF, WEBP', 'error');
                return;
            }
            
            // Validar tamaño (5MB máximo)
            if (file.size > 5 * 1024 * 1024) {
                mostrarMensaje('La imagen es muy grande. Máximo 5MB', 'error');
                return;
            }
            
            // Preview inmediato
            const reader = new FileReader();
            reader.onload = function(e) {
                if (avatarPreview.tagName === 'IMG') {
                    avatarPreview.src = e.target.result;
                } else {
                    // Reemplazar placeholder con imagen
                    const img = document.createElement('img');
                    img.src = e.target.result;
                    img.className = 'avatar-img';
                    img.id = 'avatarPreview';
                    avatarPreview.parentNode.replaceChild(img, avatarPreview);
                }
            };
            reader.readAsDataURL(file);
            
            // Subir al servidor
            const formData = new FormData();
            formData.append('avatar', file);
            
            try {
                const response = await fetch('/subir_avatar', {
                    method: 'POST',
                    body: formData
                });
                
                const data = await response.json();
                
                if (data.success) {
                    mostrarMensaje(data.message, 'success');
                    
                    // Recargar después de 1 segundo
                    setTimeout(() => {
                        location.reload();
                    }, 1000);
                } else {
                    mostrarMensaje(data.message, 'error');
                }
            } catch (error) {
                console.error('Error:', error);
                mostrarMensaje('Error al subir el avatar. Intenta nuevamente.', 'error');
            }
        });
    }

    // ===== ELIMINAR AVATAR =====
    if (deleteAvatar) {
        deleteAvatar.addEventListener('click', async function() {
            if (!confirm('¿Estás seguro de que quieres eliminar tu avatar?')) {
                return;
            }
            
            try {
                const response = await fetch('/eliminar_avatar', {
                    method: 'POST'
                });
                
                const data = await response.json();
                
                if (data.success) {
                    mostrarMensaje(data.message, 'success');
                    
                    // Recargar después de 1 segundo
                    setTimeout(() => {
                        location.reload();
                    }, 1000);
                } else {
                    mostrarMensaje(data.message, 'error');
                }
            } catch (error) {
                console.error('Error:', error);
                mostrarMensaje('Error al eliminar el avatar.', 'error');
            }
        });
    }

    // ===== MOSTRAR MENSAJES =====
    function mostrarMensaje(texto, tipo) {
        avatarMessage.textContent = texto;
        avatarMessage.className = `mensaje ${tipo} show`;
        
        // Auto-ocultar después de 5 segundos
        setTimeout(() => {
            avatarMessage.classList.remove('show');
        }, 5000);
    }

    // ===== VALIDACIÓN DE CONTRASEÑAS =====
    const forms = document.querySelectorAll('.perfil-form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const nuevaPassword = form.querySelector('[name="nueva_password"]');
            const confirmarPassword = form.querySelector('[name="confirmar_password"]');
            
            if (nuevaPassword && confirmarPassword) {
                if (nuevaPassword.value && nuevaPassword.value !== confirmarPassword.value) {
                    e.preventDefault();
                    mostrarMensaje('Las contraseñas nuevas no coinciden', 'error');
                    return false;
                }
            }
        });
    });
});