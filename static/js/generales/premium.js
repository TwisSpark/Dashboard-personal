
// ============================================================
// PREMIUM.JS - Activación de Premium
// ============================================================

document.addEventListener('DOMContentLoaded', function() {
    const btnActivarPremium = document.getElementById('activarPremium');

    if (btnActivarPremium) {
        btnActivarPremium.addEventListener('click', async function() {
            // Confirmar antes de activar
            if (!confirm('¿Estás seguro de que quieres activar Sparkavia Premium?\n\nEn la versión demo, se activará instantáneamente.\nEn producción, serías redirigido a la pasarela de pago.')) {
                return;
            }

            // Cambiar estado del botón
            const textoOriginal = this.innerHTML;
            this.disabled = true;
            this.innerHTML = `
                <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor" style="animation: spin 1s linear infinite;">
                    <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
                </svg>
                Activando...
            `;

            try {
                const response = await fetch('/activar_premium', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    }
                });

                const data = await response.json();

                if (data.success) {
                    // Mostrar mensaje de éxito
                    this.innerHTML = `
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
                        </svg>
                        ¡Activado! 🎉
                    `;
                    this.style.background = 'linear-gradient(135deg, #00ff88, #00d4aa)';

                    // Mostrar confetti (opcional)
                    mostrarConfetti();

                    // Recargar página después de 2 segundos
                    setTimeout(() => {
                        location.reload();
                    }, 2000);
                } else {
                    throw new Error(data.message || 'Error al activar Premium');
                }
            } catch (error) {
                console.error('Error:', error);
                this.disabled = false;
                this.innerHTML = textoOriginal;
                alert('Error al activar Premium. Por favor, intenta nuevamente.');
            }
        });
    }

    // ===== ANIMACIÓN DE CONFETTI =====
    function mostrarConfetti() {
        // Simple confetti effect
        const colors = ['#ffd700', '#ffed4e', '#a875ff', '#8c52ff', '#00ff88'];
        const confettiCount = 50;

        for (let i = 0; i < confettiCount; i++) {
            setTimeout(() => {
                const confetti = document.createElement('div');
                confetti.style.position = 'fixed';
                confetti.style.width = '10px';
                confetti.style.height = '10px';
                confetti.style.backgroundColor = colors[Math.floor(Math.random() * colors.length)];
                confetti.style.left = Math.random() * window.innerWidth + 'px';
                confetti.style.top = '-10px';
                confetti.style.borderRadius = '50%';
                confetti.style.pointerEvents = 'none';
                confetti.style.zIndex = '10000';
                confetti.style.transition = 'all 3s ease-in-out';
                
                document.body.appendChild(confetti);
                
                setTimeout(() => {
                    confetti.style.top = window.innerHeight + 'px';
                    confetti.style.transform = `rotate(${Math.random() * 360}deg)`;
                    confetti.style.opacity = '0';
                }, 10);
                
                setTimeout(() => {
                    confetti.remove();
                }, 3000);
            }, i * 30);
        }
    }
});

// Agregar animación de spin al CSS inline
const style = document.createElement('style');
style.textContent = `
    @keyframes spin {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }
`;
document.head.appendChild(style);
