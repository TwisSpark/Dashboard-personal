
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
import json
import random
import os
from pathlib import Path

app = FastAPI(title="APY Aries API - TwisSpark")

# Configuración CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Montar archivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")

# Configurar templates
templates = Jinja2Templates(directory="templates")

# Ruta base para JSON
JSON_DIR = Path("static/json")

def cargar_respuestas(archivo):
    """Carga respuestas desde un archivo JSON"""
    try:
        ruta = JSON_DIR / archivo
        with open(ruta, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Archivo {archivo} no encontrado")
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Error al procesar JSON")

def obtener_respuesta_aleatoria(clave, archivo):
    """Obtiene una respuesta aleatoria del JSON especificado SIN reemplazar placeholders"""
    data = cargar_respuestas(archivo)
    if clave not in data:
        raise HTTPException(status_code=404, detail=f"Clave '{clave}' no encontrada")

    respuestas = data[clave]
    respuesta = random.choice(respuestas)
    return respuesta  # Devuelve el texto con {dinero} y {user} sin reemplazar

@app.get("/", response_class=HTMLResponse)
async def inicio(request: Request):
    """Página principal del panel web"""
    return templates.TemplateResponse("principal/inicio.html", {"request": request})

@app.get("/favicon.png")
async def favicon():
    """Servir favicon"""
    return FileResponse("favicon.png")

@app.get("/work")
async def work():
    """Endpoint de trabajo - Devuelve respuesta con placeholders {dinero}"""
    respuesta = obtener_respuesta_aleatoria("work", "work.json")
    return {"comando": "work", "respuesta": respuesta}

@app.get("/rob")
async def rob():
    """Endpoint de robo - Devuelve respuesta con placeholders {dinero} y {user}"""
    respuesta = obtener_respuesta_aleatoria("rob", "rob.json")
    return {"comando": "rob", "respuesta": respuesta}

@app.get("/crime")
async def crime():
    """Endpoint de actividades delictivas - Devuelve respuesta con placeholders {dinero} y {user}"""
    respuesta = obtener_respuesta_aleatoria("crime", "crime.json")
    return {"comando": "crime", "respuesta": respuesta}

@app.get("/heal")
async def heal():
    """Endpoint de curación - Devuelve respuesta con placeholders {dinero} y {user}"""
    respuesta = obtener_respuesta_aleatoria("heal", "heal.json")
    return {"comando": "heal", "respuesta": respuesta}

@app.get("/pay")
async def pay():
    """Endpoint de transferencias - Devuelve respuesta con placeholders {dinero} y {user}"""
    respuesta = obtener_respuesta_aleatoria("pay", "pay.json")
    return {"comando": "pay", "respuesta": respuesta}

@app.get("/deliver")
async def deliver():
    """Endpoint de entregas - Devuelve respuesta con placeholders {dinero} y {user}"""
    respuesta = obtener_respuesta_aleatoria("deliver", "deliver.json")
    return {"comando": "deliver", "respuesta": respuesta}

@app.get("/me")
async def me():
    """Endpoint de información personal/random"""
    respuesta = obtener_respuesta_aleatoria("me", "me.json")
    return {"comando": "me", "respuesta": respuesta}

@app.get("/resp/{archivo}")
async def respuesta_dinamica(archivo: str):
    """Endpoint dinámico para cualquier archivo JSON - Devuelve respuestas con placeholders sin reemplazar"""
    if not archivo.endswith('.json'):
        archivo += '.json'

    data = cargar_respuestas(archivo)

    # Obtener la primera clave del JSON
    if not data:
        raise HTTPException(status_code=404, detail="JSON vacío")

    clave = list(data.keys())[0]
    respuesta = random.choice(data[clave])
    # No reemplazar placeholders, devolver el texto original

    return {"archivo": archivo, "clave": clave, "respuesta": respuesta}

@app.exception_handler(404)
async def not_found_handler(request: Request, exc: HTTPException):
    """Manejo de error 404"""
    return {"error": "Recurso no encontrado", "detalle": str(exc.detail)}

@app.exception_handler(500)
async def server_error_handler(request: Request, exc: Exception):
    """Manejo de error 500"""
    return {"error": "Error interno del servidor", "detalle": str(exc)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)