
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import json
import os
from datetime import datetime
from functools import wraps
import hashlib

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'tu_clave_secreta_super_segura_12345')

# Crear directorios necesarios
JSON_DIR = os.path.join('static', 'json', 'generales')
os.makedirs(JSON_DIR, exist_ok=True)

REGISTROS_FILE = os.path.join(JSON_DIR, 'registros.json')
ATAQUES_FILE = os.path.join(JSON_DIR, 'ataques.json')
USUARIOS_FILE = os.path.join(JSON_DIR, 'usuarios.json')

# Inicializar archivos JSON
for file_path in [REGISTROS_FILE, ATAQUES_FILE, USUARIOS_FILE]:
    if not os.path.exists(file_path):
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump([], f)

# Decorador de protección
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Funciones de datos
def cargar_json(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return []

def guardar_json(file_path, data):
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def verificar_usuario(usuario, password):
    usuarios = cargar_json(USUARIOS_FILE)
    password_hash = hash_password(password)
    for u in usuarios:
        if u['usuario'] == usuario and u['password'] == password_hash:
            return True
    return False

def usuario_existe(usuario):
    usuarios = cargar_json(USUARIOS_FILE)
    return any(u['usuario'] == usuario for u in usuarios)

def correo_existe(correo):
    usuarios = cargar_json(USUARIOS_FILE)
    return any(u['correo'] == correo for u in usuarios)

# Rutas
@app.route('/')
def index():
    if 'usuario' in session:
        return redirect(url_for('panel'))
    return render_template('generales/index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    
    if request.method == 'POST':
        usuario = request.form.get('usuario', '').strip()
        password = request.form.get('password', '').strip()
        
        if not usuario or not password:
            error = 'Por favor completa todos los campos'
        elif verificar_usuario(usuario, password):
            session['usuario'] = usuario
            return redirect(url_for('panel'))
        else:
            error = 'Usuario o contraseña incorrectos'
    
    return render_template('generales/login.html', error=error)

@app.route('/registro', methods=['GET', 'POST'])
def registro():
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
        elif usuario_existe(nombre):
            error = 'Este nombre de usuario ya está registrado'
        elif correo_existe(correo):
            error = 'Este correo ya está registrado'
        elif '@' not in correo or '.' not in correo:
            error = 'Por favor ingresa un correo válido'
        elif len(password) < 6:
            error = 'La contraseña debe tener al menos 6 caracteres'
        elif password != password2:
            error = 'Las contraseñas no coinciden'
        else:
            # Crear nuevo usuario
            usuarios = cargar_json(USUARIOS_FILE)
            nuevo_usuario = {
                'id': datetime.now().strftime('%Y%m%d%H%M%S%f'),
                'usuario': nombre,
                'correo': correo,
                'password': hash_password(password),
                'fecha_registro': datetime.now().isoformat()
            }
            usuarios.append(nuevo_usuario)
            guardar_json(USUARIOS_FILE, usuarios)
            
            success = 'Cuenta creada exitosamente. Ahora puedes iniciar sesión.'
    
    return render_template('generales/registro.html', error=error, success=success)

@app.route('/panel')
@login_required
def panel():
    usuario_actual = session['usuario']
    registros = cargar_json(REGISTROS_FILE)
    
    # Filtrar registros del usuario actual
    registros_usuario = [r for r in registros if r.get('usuario') == usuario_actual]
    total_ataques = len(registros_usuario)
    registros_recientes = sorted(registros_usuario, key=lambda x: x.get('timestamp', ''), reverse=True)[:5]
    
    return render_template('generales/panel.html', 
                         usuario=usuario_actual,
                         total_ataques=total_ataques,
                         registros_recientes=registros_recientes)

@app.route('/registrar_ataque', methods=['POST'])
@login_required
def registrar_ataque():
    try:
        fecha = request.form.get('fecha', '').strip()
        hora = request.form.get('hora', '').strip()
        duracion = request.form.get('duracion', '').strip()
        sentimientos = request.form.get('sentimientos', '').strip()
        lugar = request.form.get('lugar', '').strip()
        acompanantes = request.form.get('acompanantes', '').strip()
        notas = request.form.get('notas', '').strip()
        
        if not all([fecha, hora, duracion]):
            return jsonify({'success': False, 'message': 'Fecha, hora y duración son obligatorios'}), 400
        
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
            'notas': notas
        }
        
        registros = cargar_json(REGISTROS_FILE)
        registros.append(nuevo_registro)
        guardar_json(REGISTROS_FILE, registros)
        
        return jsonify({'success': True, 'message': 'Ataque registrado exitosamente'})
    
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@app.route('/obtener_registros')
@login_required
def obtener_registros():
    usuario_actual = session['usuario']
    registros = cargar_json(REGISTROS_FILE)
    registros_usuario = [r for r in registros if r.get('usuario') == usuario_actual]
    registros_recientes = sorted(registros_usuario, key=lambda x: x.get('timestamp', ''), reverse=True)[:10]
    return jsonify(registros_recientes)

@app.route('/logout')
def logout():
    session.pop('usuario', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)