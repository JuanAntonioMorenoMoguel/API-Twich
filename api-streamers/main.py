from typing import List, Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel, EmailStr, Field

import almacen
import twitch

load_dotenv()

app = FastAPI(
    title="API de Usuarios y Streamers",
    description="API REST para gestionar usuarios, sus streamers y juegos favoritos, con datos de Twitch.",
    version="1.0",
)


class UsuarioEntrada(BaseModel):
    nombre: str = Field(..., min_length=2, max_length=50)
    email: EmailStr
    edad: Optional[int] = Field(None, ge=0, le=120)


class UsuarioActualizar(BaseModel):
    nombre: Optional[str] = Field(None, min_length=2, max_length=50)
    email: Optional[EmailStr] = None
    edad: Optional[int] = Field(None, ge=0, le=120)


class Preferencias(BaseModel):
    streamers: List[str] = []
    juegos: List[str] = []
    idiomas: List[str] = []


def con_enlaces(usuario):
    u = dict(usuario)
    base = "/usuarios/" + str(u["id"])
    u["enlaces"] = {
        "self": base,
        "preferencias": base + "/preferencias",
        "favoritos": base + "/favoritos",
        "actualizar": {"metodo": "PUT", "url": base},
        "eliminar": {"metodo": "DELETE", "url": base},
    }
    return u


@app.get("/")
def inicio():
    return {"mensaje": "API funcionando. Documentación en /docs"}


@app.get("/usuarios")
def listar_usuarios():
    return [con_enlaces(u) for u in almacen.listar()]


@app.get("/usuarios/{usuario_id}")
def obtener_usuario(usuario_id: int):
    usuario = almacen.obtener(usuario_id)
    if usuario is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return con_enlaces(usuario)


@app.post("/usuarios", status_code=201)
def crear_usuario(datos: UsuarioEntrada):
    if almacen.buscar_email(datos.email):
        raise HTTPException(status_code=400, detail="Ya existe un usuario con ese email")
    return con_enlaces(almacen.crear(datos.dict()))


@app.put("/usuarios/{usuario_id}")
def actualizar_usuario(usuario_id: int, datos: UsuarioActualizar):
    if almacen.obtener(usuario_id) is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    cambios = {k: v for k, v in datos.dict().items() if v is not None}
    if "email" in cambios:
        otro = almacen.buscar_email(cambios["email"])
        if otro and otro["id"] != usuario_id:
            raise HTTPException(status_code=400, detail="Ya existe un usuario con ese email")
    return con_enlaces(almacen.actualizar(usuario_id, cambios))


@app.delete("/usuarios/{usuario_id}")
def borrar_usuario(usuario_id: int):
    if not almacen.borrar(usuario_id):
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return {"mensaje": "Usuario eliminado"}


@app.get("/usuarios/{usuario_id}/preferencias")
def ver_preferencias(usuario_id: int):
    usuario = obtener_usuario(usuario_id)
    return usuario["preferencias"]


@app.put("/usuarios/{usuario_id}/preferencias")
def guardar_preferencias(usuario_id: int, prefs: Preferencias):
    obtener_usuario(usuario_id)
    usuario = almacen.actualizar(usuario_id, {"preferencias": prefs.dict()})
    return usuario["preferencias"]


@app.get("/twitch/buscar")
def buscar_en_twitch(response: Response, q: str, limite: int = 5):
    if limite < 1 or limite > 20:
        raise HTTPException(status_code=400, detail="El límite debe estar entre 1 y 20")
    response.headers["Cache-Control"] = "public, max-age=60"
    return twitch.buscar_canales(q, limite)


@app.get("/twitch/streamers/{login}")
def ver_streamer(login: str, response: Response):
    streamer = twitch.info_streamer(login)
    if streamer is None:
        raise HTTPException(status_code=404, detail="Streamer no encontrado en Twitch")
    response.headers["Cache-Control"] = "public, max-age=60"
    return streamer


@app.get("/twitch/juegos")
def ver_juego(nombre: str, response: Response):
    juego = twitch.buscar_juego(nombre)
    if juego is None:
        raise HTTPException(status_code=404, detail="Juego no encontrado en Twitch")
    response.headers["Cache-Control"] = "public, max-age=300"
    return juego


@app.get("/usuarios/{usuario_id}/favoritos")
def favoritos_de_usuario(usuario_id: int):
    usuario = obtener_usuario(usuario_id)
    prefs = usuario["preferencias"]
    resultado = {"streamers": [], "juegos": []}
    for login in prefs["streamers"]:
        streamer = twitch.info_streamer(login)
        if streamer:
            resultado["streamers"].append(streamer)
    for nombre in prefs["juegos"]:
        juego = twitch.buscar_juego(nombre)
        if juego:
            resultado["juegos"].append(juego)
    return resultado
