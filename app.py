
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import json
import os
from datetime import datetime
from functools import wraps

app = Flask(__name__)
app.secret_key = 'tu_clave_secreta_super_segura_12345'

# Crear directorios necesarios
JSON_DIR = os.path.join('static', 'json', 'generales')
os.makedirs(JSON_DIR, exist_ok=True)

REGISTROS_FILE = os.path.join(JSON_DIR, 'registros.json')
USUARIOS_FILE = os.path.join(JSON_DIR, 'usuarios.json')

# Inicializar archivo JSON de registros
if not os.path.exists(REGISTROS_FILE):
    with open(REGISTROS_FILE, 'w', encoding='utf-8') as f:
        json.dump([], f)

# Credenciales iniciales
USUARIOS = {
    'admin': 'admin123',
    'usuario': 'password123'
}

# Inicializar archivo JSON de usuarios si no existe
if not os.path.exists(USUARIOS_FILE):
    with open(USUARIOS_FILE, 'w', encoding='utf-8') as f:
        json.dump(USUARIOS, f, indent=2)

# Decorador de protección
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Funciones de datos
def cargar_registros():
    try:
        with open(REGISTROS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return []

def guardar_registros(registros):
    with open(REGISTROS_FILE, 'w', encoding='utf-8') as f:
        json.dump(registros, f, indent=2, ensure_ascii=False)

def cargar_usuarios():
    try:
        with open(USUARIOS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {}

def guardar_usuarios(usuarios):
    with open(USUARIOS_FILE, 'w', encoding='utf-8') as f:
        json.dump(usuarios, f, indent=2)

# Rutas
@app.route('/')
def index():
    if 'usuario' in session:
        return redirect(url_for('panel'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    
    if request.method == 'POST':
        usuario = request.form.get('usuario', '').strip()
        password = request.form.get('password', '').strip()
        
        usuarios = cargar_usuarios()
        
        if not usuario or not password:
            error = 'Por favor completa todos los campos'
        elif usuario in usuarios and usuarios[usuario] == password:
            session['usuario'] = usuario
            return redirect(url_for('panel'))
        else:
            error = 'Usuario o contraseña incorrectos'
    
    return render_template('generales/login.html', error=error)

@app.route('/panel')
@login_required
def panel():
    registros = cargar_registros()
    total_ataques = len(registros)
    registros_recientes = sorted(registros, key=lambda x: x.get('timestamp', ''), reverse=True)[:5]
    
    return render_template('generales/panel.html', 
                         usuario=session['usuario'],
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
            'acompanantes': acompanantes
        }
        
        registros = cargar_registros()
        registros.append(nuevo_registro)
        guardar_registros(registros)
        
        return jsonify({'success': True, 'message': 'Ataque registrado exitosamente'})
    
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@app.route('/obtener_registros')
@login_required
def obtener_registros():
    registros = cargar_registros()
    registros_recientes = sorted(registros, key=lambda x: x.get('timestamp', ''), reverse=True)[:10]
    return jsonify(registros_recientes)

@app.route('/registrar_usuario', methods=['POST'])
@login_required
def registrar_usuario():
    nuevo_usuario = request.form.get('usuario', '').strip()
    nueva_password = request.form.get('password', '').strip()

    if not nuevo_usuario or not nueva_password:
        return jsonify({'success': False, 'message': 'Usuario y contraseña son obligatorios'}), 400

    usuarios = cargar_usuarios()
    
    if nuevo_usuario in usuarios:
        return jsonify({'success': False, 'message': 'El usuario ya existe'}), 400

    usuarios[nuevo_usuario] = nueva_password
    guardar_usuarios(usuarios)
    
    return jsonify({'success': True, 'message': 'Usuario registrado exitosamente'})

@app.route('/logout')
def logout():
    session.pop('usuario', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True, port=5000)