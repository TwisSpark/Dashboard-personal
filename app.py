
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import json
import os
from datetime import datetime
from functools import wraps
import hashlib
import base64
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Configuración de la aplicación
app.secret_key = os.environ.get('SECRET_KEY', 'tu_clave_secreta_super_segura_12345_cambiar_en_produccion')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Límite de 16MB para uploads
app.config['PERMANENT_SESSION_LIFETIME'] = 86400  # Sesión de 24 horas
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

# Crear directorios necesarios
JSON_DIR = os.path.join('static', 'json', 'generales')
AVATARS_DIR = os.path.join('static', 'avatars')
os.makedirs(JSON_DIR, exist_ok=True)
os.makedirs(AVATARS_DIR, exist_ok=True)

# Rutas de archivos JSON
REGISTROS_FILE = os.path.join(JSON_DIR, 'registros.json')
ATAQUES_FILE = os.path.join(JSON_DIR, 'ataques.json')
USUARIOS_FILE = os.path.join(JSON_DIR, 'usuarios.json')

# Inicializar archivos JSON si no existen
for file_path in [REGISTROS_FILE, ATAQUES_FILE, USUARIOS_FILE]:
    if not os.path.exists(file_path):
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump([], f)

# ===== DECORADORES =====
def login_required(f):
    """Decorador para proteger rutas que requieren autenticación"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# ===== FUNCIONES DE MANEJO DE DATOS =====
def cargar_json(file_path):
    """Carga datos desde un archivo JSON"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            if not content:
                return []
            return json.loads(content)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        print(f"Error: Archivo JSON corrupto: {file_path}")
        return []
    except Exception as e:
        print(f"Error al cargar {file_path}: {str(e)}")
        return []

def guardar_json(file_path, data):
    """Guarda datos en un archivo JSON"""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error al guardar {file_path}: {str(e)}")
        return False

# ===== FUNCIONES DE AUTENTICACIÓN =====
def hash_password(password):
    """Genera un hash SHA-256 de la contraseña"""
    return hashlib.sha256(password.encode()).hexdigest()

def verificar_usuario(usuario, password):
    """Verifica si el usuario y contraseña son correctos"""
    usuarios = cargar_json(USUARIOS_FILE)
    password_hash = hash_password(password)
    for u in usuarios:
        if u['usuario'] == usuario and u['password'] == password_hash:
            return True
    return False

def usuario_existe(usuario):
    """Verifica si un nombre de usuario ya existe"""
    usuarios = cargar_json(USUARIOS_FILE)
    return any(u['usuario'].lower() == usuario.lower() for u in usuarios)

def correo_existe(correo):
    """Verifica si un correo ya está registrado"""
    usuarios = cargar_json(USUARIOS_FILE)
    return any(u['correo'].lower() == correo.lower() for u in usuarios)

def obtener_info_usuario(usuario):
    """Obtiene información completa de un usuario"""
    usuarios = cargar_json(USUARIOS_FILE)
    for u in usuarios:
        if u['usuario'] == usuario:
            return u
    return None

def allowed_file(filename):
    """Verifica si el archivo tiene una extensión permitida"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def generar_nombre_avatar(usuario):
    """Genera un nombre único para el avatar"""
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    return f"{usuario}_{timestamp}"

# ===== RUTAS PRINCIPALES =====
@app.route('/')
def index():
    """Página de inicio - redirige según estado de sesión"""
    if 'usuario' in session:
        return redirect(url_for('panel'))
    return render_template('generales/index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Ruta de inicio de sesión"""
    # Si ya está logueado, redirigir al panel
    if 'usuario' in session:
        return redirect(url_for('panel'))
    
    error = None
    
    if request.method == 'POST':
        usuario = request.form.get('usuario', '').strip()
        password = request.form.get('password', '').strip()
        
        # Validaciones
        if not usuario or not password:
            error = 'Por favor completa todos los campos'
        elif len(usuario) < 3:
            error = 'El usuario debe tener al menos 3 caracteres'
        elif len(password) < 6:
            error = 'La contraseña debe tener al menos 6 caracteres'
        elif verificar_usuario(usuario, password):
            session['usuario'] = usuario
            session.permanent = True
            return redirect(url_for('panel'))
        else:
            error = 'Usuario o contraseña incorrectos'
    
    return render_template('generales/login.html', error=error)

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    """Ruta de registro de nuevos usuarios"""
    # Si ya está logueado, redirigir al panel
    if 'usuario' in session:
        return redirect(url_for('panel'))
    
    error = None
    success = None
    
    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        correo = request.form.get('correo', '').strip()
        password = request.form.get('password', '').strip()
        password2 = request.form.get('password2', '').strip()
        
        # Validaciones
        if not all([nombre, correo, password, password2]):
            error = 'Por favor completa todos los campos'
        elif len(nombre) < 3:
            error = 'El nombre de usuario debe tener al menos 3 caracteres'
        elif len(nombre) > 20:
            error = 'El nombre de usuario no puede tener más de 20 caracteres'
        elif not nombre.isalnum():
            error = 'El nombre de usuario solo puede contener letras y números'
        elif usuario_existe(nombre):
            error = 'Este nombre de usuario ya está registrado'
        elif correo_existe(correo):
            error = 'Este correo ya está registrado'
        elif '@' not in correo or '.' not in correo:
            error = 'Por favor ingresa un correo válido'
        elif len(password) < 6:
            error = 'La contraseña debe tener al menos 6 caracteres'
        elif len(password) > 100:
            error = 'La contraseña es demasiado larga'
        elif password != password2:
            error = 'Las contraseñas no coinciden'
        else:
            # Crear nuevo usuario
            usuarios = cargar_json(USUARIOS_FILE)
            nuevo_usuario = {
                'id': datetime.now().strftime('%Y%m%d%H%M%S%f'),
                'usuario': nombre,
                'correo': correo.lower(),
                'password': hash_password(password),
                'fecha_registro': datetime.now().isoformat(),
                'ultimo_acceso': None,
                'avatar': None,
                'premium': False,
                'fecha_premium': None
            }
            usuarios.append(nuevo_usuario)
            
            if guardar_json(USUARIOS_FILE, usuarios):
                success = 'Cuenta creada exitosamente. Ahora puedes iniciar sesión.'
            else:
                error = 'Error al crear la cuenta. Intenta nuevamente.'
    
    return render_template('generales/registro.html', error=error, success=success)

@app.route('/panel')
@login_required
def panel():
    """Panel principal del usuario"""
    usuario_actual = session['usuario']
    registros = cargar_json(REGISTROS_FILE)
    
    # Actualizar último acceso
    actualizar_ultimo_acceso(usuario_actual)
    
    # Obtener info del usuario
    info_usuario = obtener_info_usuario(usuario_actual)
    es_premium = info_usuario.get('premium', False) if info_usuario else False
    
    # Filtrar registros del usuario actual
    registros_usuario = [r for r in registros if r.get('usuario') == usuario_actual]
    total_ataques = len(registros_usuario)
    
    # Ordenar por timestamp y tomar solo los últimos 5 para la vista principal
    registros_recientes = sorted(
        registros_usuario, 
        key=lambda x: x.get('timestamp', ''), 
        reverse=True
    )[:5]
    
    return render_template('generales/panel.html', 
                         usuario=usuario_actual,
                         total_ataques=total_ataques,
                         registros_recientes=registros_recientes,
                         info_usuario=info_usuario,
                         es_premium=es_premium)

@app.route('/registrar_ataque', methods=['POST'])
@login_required
def registrar_ataque():
    """Registra un nuevo episodio epiléptico"""
    try:
        # Obtener datos del formulario
        fecha = request.form.get('fecha', '').strip()
        hora = request.form.get('hora', '').strip()
        duracion = request.form.get('duracion', '').strip()
        sentimientos = request.form.get('sentimientos', '').strip()
        lugar = request.form.get('lugar', '').strip()
        acompanantes = request.form.get('acompanantes', '').strip()
        notas = request.form.get('notas', '').strip()
        
        # Campos adicionales opcionales
        tipo_crisis = request.form.get('tipo_crisis', '').strip()
        severidad = request.form.get('severidad', '').strip()
        desencadenante = request.form.get('desencadenante', '').strip()
        actividad_previa = request.form.get('actividad_previa', '').strip()
        medicacion_tomada = request.form.get('medicacion_tomada', '').strip()
        aura = request.form.get('aura', '').strip()
        tiempo_recuperacion = request.form.get('tiempo_recuperacion', '').strip()
        
        # Validaciones
        if not all([fecha, hora, duracion]):
            return jsonify({
                'success': False, 
                'message': 'Fecha, hora y duración son obligatorios'
            }), 400
        
        # Validar formato de fecha
        try:
            datetime.strptime(fecha, '%Y-%m-%d')
        except ValueError:
            return jsonify({
                'success': False, 
                'message': 'Formato de fecha inválido'
            }), 400
        
        # Validar formato de hora
        try:
            datetime.strptime(hora, '%H:%M')
        except ValueError:
            return jsonify({
                'success': False, 
                'message': 'Formato de hora inválido'
            }), 400
        
        # Crear nuevo registro
        nuevo_registro = {
            'id': datetime.now().strftime('%Y%m%d%H%M%S%f'),
            'timestamp': datetime.now().isoformat(),
            'usuario': session['usuario'],
            'fecha': fecha,
            'hora': hora,
            'duracion': duracion,
            'sentimientos': sentimientos,
            'lugar': lugar,
            'acompanantes': acompanantes,
            'notas': notas,
            'tipo_crisis': tipo_crisis,
            'severidad': severidad,
            'desencadenante': desencadenante,
            'actividad_previa': actividad_previa,
            'medicacion_tomada': medicacion_tomada,
            'aura': aura,
            'tiempo_recuperacion': tiempo_recuperacion
        }
        
        # Guardar registro
        registros = cargar_json(REGISTROS_FILE)
        registros.append(nuevo_registro)
        
        if guardar_json(REGISTROS_FILE, registros):
            return jsonify({
                'success': True, 
                'message': 'Episodio registrado exitosamente'
            })
        else:
            return jsonify({
                'success': False, 
                'message': 'Error al guardar el registro'
            }), 500
    
    except Exception as e:
        print(f"Error en registrar_ataque: {str(e)}")
        return jsonify({
            'success': False, 
            'message': f'Error inesperado: {str(e)}'
        }), 500

@app.route('/obtener_registros')
@login_required
def obtener_registros():
    """Obtiene TODOS los registros del usuario para el historial completo"""
    try:
        usuario_actual = session['usuario']
        registros = cargar_json(REGISTROS_FILE)
        
        # Filtrar registros del usuario actual
        registros_usuario = [r for r in registros if r.get('usuario') == usuario_actual]
        
        # Ordenar por timestamp descendente (más reciente primero)
        registros_ordenados = sorted(
            registros_usuario, 
            key=lambda x: x.get('timestamp', ''), 
            reverse=True
        )
        
        return jsonify(registros_ordenados)
    
    except Exception as e:
        print(f"Error en obtener_registros: {str(e)}")
        return jsonify([]), 500

@app.route('/eliminar_registro/<registro_id>', methods=['POST'])
@login_required
def eliminar_registro(registro_id):
    """Elimina un registro específico (opcional)"""
    try:
        usuario_actual = session['usuario']
        registros = cargar_json(REGISTROS_FILE)
        
        # Buscar y eliminar el registro
        registro_encontrado = False
        nuevos_registros = []
        
        for registro in registros:
            if registro.get('id') == registro_id and registro.get('usuario') == usuario_actual:
                registro_encontrado = True
            else:
                nuevos_registros.append(registro)
        
        if not registro_encontrado:
            return jsonify({
                'success': False, 
                'message': 'Registro no encontrado'
            }), 404
        
        if guardar_json(REGISTROS_FILE, nuevos_registros):
            return jsonify({
                'success': True, 
                'message': 'Registro eliminado exitosamente'
            })
        else:
            return jsonify({
                'success': False, 
                'message': 'Error al eliminar el registro'
            }), 500
    
    except Exception as e:
        print(f"Error en eliminar_registro: {str(e)}")
        return jsonify({
            'success': False, 
            'message': 'Error inesperado'
        }), 500

@app.route('/estadisticas')
@login_required
def estadisticas():
    """Obtiene estadísticas del usuario (opcional - para futuras implementaciones)"""
    try:
        usuario_actual = session['usuario']
        registros = cargar_json(REGISTROS_FILE)
        
        # Filtrar registros del usuario
        registros_usuario = [r for r in registros if r.get('usuario') == usuario_actual]
        
        # Calcular estadísticas básicas
        total = len(registros_usuario)
        
        # Por mes (últimos 6 meses)
        from collections import defaultdict
        por_mes = defaultdict(int)
        
        for registro in registros_usuario:
            try:
                fecha = registro.get('fecha', '')
                mes = fecha[:7]  # YYYY-MM
                por_mes[mes] += 1
            except:
                continue
        
        stats = {
            'total': total,
            'por_mes': dict(por_mes)
        }
        
        return jsonify(stats)
    
    except Exception as e:
        print(f"Error en estadisticas: {str(e)}")
        return jsonify({'error': 'Error al obtener estadísticas'}), 500

@app.route('/logout')
def logout():
    """Cierra la sesión del usuario"""
    session.pop('usuario', None)
    return redirect(url_for('index'))

# ===== RUTAS DE PERFIL Y PREMIUM =====
@app.route('/perfil', methods=['GET', 'POST'])
@login_required
def perfil():
    """Página de edición de perfil"""
    usuario_actual = session['usuario']
    info_usuario = obtener_info_usuario(usuario_actual)
    error = None
    success = None
    
    if request.method == 'POST':
        # Obtener datos del formulario
        nuevo_nombre = request.form.get('nombre', '').strip()
        nuevo_correo = request.form.get('correo', '').strip()
        password_actual = request.form.get('password_actual', '').strip()
        nueva_password = request.form.get('nueva_password', '').strip()
        confirmar_password = request.form.get('confirmar_password', '').strip()
        
        usuarios = cargar_json(USUARIOS_FILE)
        
        # Validar cambio de nombre
        if nuevo_nombre and nuevo_nombre != usuario_actual:
            if len(nuevo_nombre) < 3:
                error = 'El nombre debe tener al menos 3 caracteres'
            elif len(nuevo_nombre) > 20:
                error = 'El nombre no puede tener más de 20 caracteres'
            elif not nuevo_nombre.isalnum():
                error = 'El nombre solo puede contener letras y números'
            elif usuario_existe(nuevo_nombre):
                error = 'Este nombre de usuario ya está en uso'
            else:
                # Actualizar nombre en todos los registros
                for u in usuarios:
                    if u['usuario'] == usuario_actual:
                        u['usuario'] = nuevo_nombre
                        session['usuario'] = nuevo_nombre
                        break
                
                registros = cargar_json(REGISTROS_FILE)
                for r in registros:
                    if r.get('usuario') == usuario_actual:
                        r['usuario'] = nuevo_nombre
                guardar_json(REGISTROS_FILE, registros)
                usuario_actual = nuevo_nombre
                success = 'Nombre de usuario actualizado correctamente'
        
        # Validar cambio de correo
        if nuevo_correo and nuevo_correo.lower() != info_usuario.get('correo', '').lower():
            if '@' not in nuevo_correo or '.' not in nuevo_correo:
                error = 'Por favor ingresa un correo válido'
            elif correo_existe(nuevo_correo) and nuevo_correo.lower() != info_usuario.get('correo', '').lower():
                error = 'Este correo ya está registrado'
            else:
                for u in usuarios:
                    if u['usuario'] == usuario_actual:
                        u['correo'] = nuevo_correo.lower()
                        break
                success = 'Correo actualizado correctamente'
        
        # Validar cambio de contraseña
        if nueva_password:
            if not password_actual:
                error = 'Debes ingresar tu contraseña actual'
            elif not verificar_usuario(usuario_actual, password_actual):
                error = 'La contraseña actual es incorrecta'
            elif len(nueva_password) < 6:
                error = 'La nueva contraseña debe tener al menos 6 caracteres'
            elif nueva_password != confirmar_password:
                error = 'Las contraseñas nuevas no coinciden'
            else:
                for u in usuarios:
                    if u['usuario'] == usuario_actual:
                        u['password'] = hash_password(nueva_password)
                        break
                success = 'Contraseña actualizada correctamente'
        
        if not error:
            guardar_json(USUARIOS_FILE, usuarios)
            info_usuario = obtener_info_usuario(usuario_actual)
    
    return render_template('generales/perfil.html', 
                         info_usuario=info_usuario, 
                         error=error, 
                         success=success)

@app.route('/subir_avatar', methods=['POST'])
@login_required
def subir_avatar():
    """Sube o actualiza el avatar del usuario"""
    try:
        usuario_actual = session['usuario']
        
        if 'avatar' not in request.files:
            return jsonify({'success': False, 'message': 'No se seleccionó ningún archivo'}), 400
        
        file = request.files['avatar']
        
        if file.filename == '':
            return jsonify({'success': False, 'message': 'No se seleccionó ningún archivo'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({
                'success': False, 
                'message': 'Formato no permitido. Usa: PNG, JPG, JPEG, GIF, WEBP'
            }), 400
        
        # Leer y convertir a base64
        file_data = file.read()
        if len(file_data) > 5 * 1024 * 1024:  # Máximo 5MB
            return jsonify({'success': False, 'message': 'La imagen es muy grande. Máximo 5MB'}), 400
        
        # Convertir a base64
        extension = file.filename.rsplit('.', 1)[1].lower()
        base64_data = base64.b64encode(file_data).decode('utf-8')
        avatar_data = f"data:image/{extension};base64,{base64_data}"
        
        # Actualizar en la base de datos
        usuarios = cargar_json(USUARIOS_FILE)
        for u in usuarios:
            if u['usuario'] == usuario_actual:
                u['avatar'] = avatar_data
                break
        
        if guardar_json(USUARIOS_FILE, usuarios):
            return jsonify({
                'success': True, 
                'message': 'Avatar actualizado correctamente',
                'avatar_url': avatar_data
            })
        else:
            return jsonify({'success': False, 'message': 'Error al guardar el avatar'}), 500
    
    except Exception as e:
        print(f"Error en subir_avatar: {str(e)}")
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@app.route('/eliminar_avatar', methods=['POST'])
@login_required
def eliminar_avatar():
    """Elimina el avatar del usuario"""
    try:
        usuario_actual = session['usuario']
        usuarios = cargar_json(USUARIOS_FILE)
        
        for u in usuarios:
            if u['usuario'] == usuario_actual:
                u['avatar'] = None
                break
        
        if guardar_json(USUARIOS_FILE, usuarios):
            return jsonify({'success': True, 'message': 'Avatar eliminado correctamente'})
        else:
            return jsonify({'success': False, 'message': 'Error al eliminar el avatar'}), 500
    
    except Exception as e:
        print(f"Error en eliminar_avatar: {str(e)}")
        return jsonify({'success': False, 'message': 'Error inesperado'}), 500

@app.route('/premium')
@login_required
def premium():
    """Página de información de Premium"""
    usuario_actual = session['usuario']
    info_usuario = obtener_info_usuario(usuario_actual)
    return render_template('generales/premium.html', info_usuario=info_usuario)

@app.route('/activar_premium', methods=['POST'])
@login_required
def activar_premium():
    """Activa cuenta premium (simulado - en producción integrar con Stripe/PayPal)"""
    try:
        usuario_actual = session['usuario']
        usuarios = cargar_json(USUARIOS_FILE)
        
        for u in usuarios:
            if u['usuario'] == usuario_actual:
                u['premium'] = True
                u['fecha_premium'] = datetime.now().isoformat()
                break
        
        if guardar_json(USUARIOS_FILE, usuarios):
            return jsonify({
                'success': True, 
                'message': '¡Bienvenido a Sparkavia Premium! 🎉'
            })
        else:
            return jsonify({'success': False, 'message': 'Error al activar Premium'}), 500
    
    except Exception as e:
        print(f"Error en activar_premium: {str(e)}")
        return jsonify({'success': False, 'message': 'Error inesperado'}), 500

# ===== FUNCIONES AUXILIARES =====
def actualizar_ultimo_acceso(usuario):
    """Actualiza la fecha de último acceso del usuario"""
    try:
        usuarios = cargar_json(USUARIOS_FILE)
        for u in usuarios:
            if u['usuario'] == usuario:
                u['ultimo_acceso'] = datetime.now().isoformat()
                break
        guardar_json(USUARIOS_FILE, usuarios)
    except Exception as e:
        print(f"Error al actualizar último acceso: {str(e)}")

# ===== MANEJADORES DE ERRORES =====
@app.errorhandler(404)
def page_not_found(e):
    """Página no encontrada"""
    return render_template('generales/404.html'), 404

@app.errorhandler(500)
def internal_error(e):
    """Error interno del servidor"""
    return render_template('generales/500.html'), 500

@app.errorhandler(413)
def request_entity_too_large(e):
    """Archivo muy grande"""
    return jsonify({
        'success': False, 
        'message': 'El archivo es demasiado grande. Máximo 16MB.'
    }), 413

# ===== PUNTO DE ENTRADA =====
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug_mode)