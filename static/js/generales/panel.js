
// ============================================================
// PANEL.JS - Control del Dashboard
// ============================================================

document.addEventListener('DOMContentLoaded', function() {
    // Elementos del DOM
    const sidebarToggle = document.getElementById('sidebarToggle');
    const sidebar = document.getElementById('sidebar');
    const menuLinks = document.querySelectorAll('.sidebar-menu a');
    const sections = document.querySelectorAll('.content-section');
    const formRegistro = document.getElementById('formRegistro');
    const mensaje = document.getElementById('mensaje');

    // ===== TOGGLE SIDEBAR (Móvil) =====
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', function() {
            sidebar.classList.toggle('active');
        });
    }

    // Cerrar sidebar al hacer clic fuera
    document.addEventListener('click', function(e) {
        if (window.innerWidth <= 768) {
            if (!sidebar.contains(e.target) && !sidebarToggle.contains(e.target)) {
                sidebar.classList.remove('active');
            }
        }
    });

    // ===== NAVEGACIÓN ENTRE SECCIONES =====
    menuLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            const targetSection = this.getAttribute('data-section');
            
            // Actualizar menú activo
            menuLinks.forEach(l => l.parentElement.classList.remove('active'));
            this.parentElement.classList.add('active');
            
            // Mostrar sección
            sections.forEach(section => {
                section.classList.remove('active');
                if (section.id === targetSection) {
                    section.classList.add('active');
                }
            });

            // Cargar historial si es necesario
            if (targetSection === 'historial') {
                cargarHistorial();
            }
            
            // Cerrar sidebar en móvil
            if (window.innerWidth <= 768) {
                sidebar.classList.remove('active');
            }
        });
    });

    // ===== FORMULARIO DE REGISTRO =====
    if (formRegistro) {
        formRegistro.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            // Validar campos obligatorios
            const fecha = document.getElementById('fecha').value.trim();
            const hora = document.getElementById('hora').value.trim();
            const duracion = formRegistro.querySelector('[name="duracion"]').value.trim();
            
            if (!fecha || !hora || !duracion) {
                mostrarMensaje('Por favor completa los campos obligatorios', 'error');
                return;
            }
            
            // Enviar formulario
            const formData = new FormData(formRegistro);
            
            try {
                const response = await fetch('/registrar_ataque', {
                    method: 'POST',
                    body: formData
                });
                
                const data = await response.json();
                
                if (data.success) {
                    mostrarMensaje(data.message, 'success');
                    formRegistro.reset();
                    
                    // Establecer fecha y hora actual de nuevo
                    establecerFechaHora();
                    
                    // Recargar después de 1.5 segundos
                    setTimeout(() => {
                        location.reload();
                    }, 1500);
                } else {
                    mostrarMensaje(data.message, 'error');
                }
            } catch (error) {
                mostrarMensaje('Error de conexión. Intenta nuevamente.', 'error');
                console.error('Error:', error);
            }
        });
    }

    // ===== CARGAR HISTORIAL =====
    async function cargarHistorial() {
        const container = document.getElementById('historialContainer');
        container.innerHTML = '<p class="loading">Cargando historial...</p>';
        
        try {
            const response = await fetch('/obtener_registros');
            const registros = await response.json();
            
            if (registros.length === 0) {
                container.innerHTML = '<div class="empty-box"><p>No hay registros en el historial.</p></div>';
                return;
            }
            
            // Generar HTML
            let html = '';
            registros.forEach(registro => {
                html += `
                    <div class="attack-card">
                        <div class="attack-date">${registro.fecha} - ${registro.hora}</div>
                        <div class="attack-info"><strong>Duración:</strong> ${registro.duracion}</div>
                        ${registro.lugar ? `<div class="attack-info"><strong>Lugar:</strong> ${registro.lugar}</div>` : ''}
                        ${registro.acompanantes ? `<div class="attack-info"><strong>Acompañantes:</strong> ${registro.acompanantes}</div>` : ''}
                        ${registro.sentimientos ? `<div class="attack-info"><strong>Sentimientos:</strong> ${registro.sentimientos}</div>` : ''}
                    </div>
                `;
            });
            
            container.innerHTML = html;
        } catch (error) {
            container.innerHTML = '<div class="empty-box" style="color: var(--accent-red);"><p>Error al cargar el historial.</p></div>';
            console.error('Error:', error);
        }
    }

    // ===== MOSTRAR MENSAJES =====
    function mostrarMensaje(texto, tipo) {
        mensaje.textContent = texto;
        mensaje.className = `mensaje ${tipo} show`;
        
        // Auto-ocultar después de 5 segundos
        setTimeout(() => {
            mensaje.classList.remove('show');
        }, 5000);
    }

    // ===== ESTABLECER FECHA Y HORA ACTUAL =====
    function establecerFechaHora() {
        const fechaInput = document.getElementById('fecha');
        const horaInput = document.getElementById('hora');
        
        if (fechaInput) {
            const hoy = new Date().toISOString().split('T')[0];
            fechaInput.value = hoy;
            fechaInput.setAttribute('max', hoy);
        }

        if (horaInput) {
            const ahora = new Date();
            const horas = String(ahora.getHours()).padStart(2, '0');
            const minutos = String(ahora.getMinutes()).padStart(2, '0');
            horaInput.value = `${horas}:${minutos}`;
        }
    }

    // Establecer fecha y hora al cargar
    establecerFechaHora();
});