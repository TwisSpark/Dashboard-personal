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
            
            // Bloquear/desbloquear scroll del body
            if (sidebar.classList.contains('active')) {
                document.body.style.overflow = 'hidden';
            } else {
                document.body.style.overflow = '';
            }
        });
    }

    // Cerrar sidebar al hacer clic fuera
    document.addEventListener('click', function(e) {
        if (window.innerWidth <= 768) {
            if (!sidebar.contains(e.target) && !sidebarToggle.contains(e.target)) {
                sidebar.classList.remove('active');
                document.body.style.overflow = ''; // Desbloquear scroll
            }
        }
    });

    // ===== NAVEGACIÓN ENTRE SECCIONES =====
    menuLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            navegarSeccion(this);
        });
    });
    
    // También aplicar a botones con data-section
    document.querySelectorAll('[data-section]').forEach(btn => {
        if (!btn.classList.contains('sidebar-menu')) {
            btn.addEventListener('click', function(e) {
                e.preventDefault();
                navegarSeccion(this);
            });
        }
    });
    
    function navegarSeccion(element) {
        const targetSection = element.getAttribute('data-section');
        
        // Actualizar menú activo
        menuLinks.forEach(l => l.parentElement.classList.remove('active'));
        
        // Buscar el link del menú correspondiente y marcarlo activo
        menuLinks.forEach(l => {
            if (l.getAttribute('data-section') === targetSection) {
                l.parentElement.classList.add('active');
            }
        });
        
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
            document.body.style.overflow = ''; // Desbloquear scroll
        }
        
        // Scroll al inicio de la sección
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }

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
                        <div class="attack-date">
                            <svg viewBox="0 0 24 24" fill="currentColor">
                                <path d="M9 11H7v2h2v-2zm4 0h-2v2h2v-2zm4 0h-2v2h2v-2zm2-7h-1V2h-2v2H8V2H6v2H5c-1.11 0-1.99.9-1.99 2L3 20c0 1.1.89 2 2 2h14c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 16H5V9h14v11z"/>
                            </svg>
                            ${registro.fecha} - ${registro.hora}
                        </div>
                        <div class="attack-info">
                            <svg viewBox="0 0 24 24" fill="currentColor">
                                <path d="M11.99 2C6.47 2 2 6.48 2 12s4.47 10 9.99 10C17.52 22 22 17.52 22 12S17.52 2 11.99 2zM12 20c-4.42 0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8-3.58 8-8 8zm.5-13H11v6l5.25 3.15.75-1.23-4.5-2.67z"/>
                            </svg>
                            <span><strong>Duración:</strong> ${registro.duracion}</span>
                        </div>
                        ${registro.lugar ? `
                        <div class="attack-info">
                            <svg viewBox="0 0 24 24" fill="currentColor">
                                <path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z"/>
                            </svg>
                            <span><strong>Lugar:</strong> ${registro.lugar}</span>
                        </div>
                        ` : ''}
                        ${registro.acompanantes ? `
                        <div class="attack-info">
                            <svg viewBox="0 0 24 24" fill="currentColor">
                                <path d="M16 11c1.66 0 2.99-1.34 2.99-3S17.66 5 16 5c-1.66 0-3 1.34-3 3s1.34 3 3 3zm-8 0c1.66 0 2.99-1.34 2.99-3S9.66 5 8 5C6.34 5 5 6.34 5 8s1.34 3 3 3zm0 2c-2.33 0-7 1.17-7 3.5V19h14v-2.5c0-2.33-4.67-3.5-7-3.5zm8 0c-.29 0-.62.02-.97.05 1.16.84 1.97 1.97 1.97 3.45V19h6v-2.5c0-2.33-4.67-3.5-7-3.5z"/>
                            </svg>
                            <span><strong>Acompañantes:</strong> ${registro.acompanantes}</span>
                        </div>
                        ` : ''}
                        ${registro.sentimientos ? `
                        <div class="attack-info">
                            <svg viewBox="0 0 24 24" fill="currentColor">
                                <path d="M11.99 2C6.47 2 2 6.48 2 12s4.47 10 9.99 10C17.52 22 22 17.52 22 12S17.52 2 11.99 2zM12 20c-4.42 0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8-3.58 8-8 8zm3.5-9c.83 0 1.5-.67 1.5-1.5S16.33 8 15.5 8 14 8.67 14 9.5s.67 1.5 1.5 1.5zm-7 0c.83 0 1.5-.67 1.5-1.5S9.33 8 8.5 8 7 8.67 7 9.5 7.67 11 8.5 11zm3.5 6.5c2.33 0 4.31-1.46 5.11-3.5H6.89c.8 2.04 2.78 3.5 5.11 3.5z"/>
                            </svg>
                            <span><strong>Sentimientos:</strong> ${registro.sentimientos}</span>
                        </div>
                        ` : ''}
                        ${registro.notas ? `
                        <div class="attack-info">
                            <svg viewBox="0 0 24 24" fill="currentColor">
                                <path d="M14 2H6c-1.1 0-1.99.9-1.99 2L4 20c0 1.1.89 2 1.99 2H18c1.1 0 2-.9 2-2V8l-6-6zm2 16H8v-2h8v2zm0-4H8v-2h8v2zm-3-5V3.5L18.5 9H13z"/>
                            </svg>
                            <span><strong>Notas:</strong> ${registro.notas}</span>
                        </div>
                        ` : ''}
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