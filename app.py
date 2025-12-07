from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import json, random, os

app = FastAPI(title="APY Aries API – TwisSpark")

# CORS abierto para pruebas
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Montar carpeta static
app.mount("/static", StaticFiles(directory="static"), name="static")

# Plantillas HTML
templates = Jinja2Templates(directory="templates")

# Función para cargar JSON y reemplazar {dinero}
def cargar_json(archivo: str):
    path = f"static/json/{archivo}.json"
    if not os.path.isfile(path):
        return {"error": f"Archivo {archivo}.json no encontrado"}
    
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    key = list(data.keys())[0]
    respuesta = random.choice(data[key])
    respuesta = respuesta.replace("{dinero}", str(random.randint(50, 500)))
    return {"respuesta": respuesta}

# Endpoint principal
@app.get("/", response_class=HTMLResponse)
async def inicio(request: Request):
    return templates.TemplateResponse("principal/inicio.html", {"request": request})

# Favicon
@app.get("/favicon.png")
async def favicon():
    if os.path.exists("favicon.png"):
        return FileResponse("favicon.png")
    raise HTTPException(status_code=404, detail="Favicon no encontrado")

# Endpoints de la API
@app.get("/work")
async def work():
    return cargar_json("work")

@app.get("/rob")
async def rob():
    return cargar_json("rob")

@app.get("/crime")
async def crime():
    return cargar_json("crime")

@app.get("/heal")
async def heal():
    return cargar_json("heal")

@app.get("/pay")
async def pay():
    return cargar_json("pay")

@app.get("/deliver")
async def deliver():
    return cargar_json("deliver")

# Endpoint dinámico
@app.get("/resp/{archivo}")
async def resp(archivo: str):
    archivo = archivo.lower()
    validos = ["work", "rob", "crime", "heal", "pay", "deliver"]
    if archivo not in validos:
        raise HTTPException(status_code=404, detail="Archivo JSON no válido")
    return cargar_json(archivo)

# Endpoint opcional para probar todos
@app.get("/all")
async def all_responses():
    resultados = {}
    for archivo in ["work", "rob", "crime", "heal", "pay", "deliver"]:
        resultados[archivo] = cargar_json(archivo)["respuesta"]
    return resultados