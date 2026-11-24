import os
import time

import requests
from fastapi import HTTPException

TOKEN_URL = "https://id.twitch.tv/oauth2/token"
API_URL = "https://api.twitch.tv/helix"

_token = {"valor": None, "expira": 0}
_cache = {}
DURACION_CACHE = 60


def _credenciales():
    client_id = os.getenv("TWITCH_CLIENT_ID")
    client_secret = os.getenv("TWITCH_CLIENT_SECRET")
    if not client_id or not client_secret:
        raise HTTPException(status_code=500, detail="Faltan las credenciales de Twitch en las variables de entorno")
    return client_id, client_secret


def obtener_token():
    if _token["valor"] and time.time() < _token["expira"]:
        return _token["valor"]

    client_id, client_secret = _credenciales()
    params = {"client_id": client_id, "client_secret": client_secret, "grant_type": "client_credentials"}
    try:
        r = requests.post(TOKEN_URL, params=params, timeout=10)
    except requests.RequestException:
        raise HTTPException(status_code=503, detail="No se pudo conectar con Twitch")
    if r.status_code != 200:
        raise HTTPException(status_code=502, detail="Twitch rechazó las credenciales")

    datos = r.json()
    _token["valor"] = datos["access_token"]
    _token["expira"] = time.time() + datos["expires_in"] - 60
    return _token["valor"]


def _get(ruta, params):
    clave = ruta + str(sorted(params.items()))
    if clave in _cache and time.time() - _cache[clave][0] < DURACION_CACHE:
        return _cache[clave][1]

    cabeceras = {
        "Client-Id": _credenciales()[0],
        "Authorization": "Bearer " + obtener_token(),
    }
    try:
        r = requests.get(API_URL + ruta, headers=cabeceras, params=params, timeout=10)
    except requests.RequestException:
        raise HTTPException(status_code=503, detail="No se pudo conectar con Twitch")
    if r.status_code == 401:
        _token["valor"] = None
    if r.status_code != 200:
        raise HTTPException(status_code=502, detail="Error al consultar Twitch")
    datos = r.json()["data"]
    _cache[clave] = (time.time(), datos)
    return datos


def buscar_canales(texto, limite=5):
    canales = []
    for c in _get("/search/channels", {"query": texto, "first": limite}):
        canales.append({
            "login": c["broadcaster_login"],
            "nombre": c["display_name"],
            "en_directo": c["is_live"],
            "juego": c["game_name"],
            "titulo": c["title"],
            "idioma": c["broadcaster_language"],
        })
    return canales


def info_streamer(login):
    usuarios = _get("/users", {"login": login})
    if not usuarios:
        return None
    u = usuarios[0]
    directos = _get("/streams", {"user_login": login})
    streamer = {
        "login": u["login"],
        "nombre": u["display_name"],
        "descripcion": u["description"],
        "tipo": u["broadcaster_type"],
        "imagen": u["profile_image_url"],
        "creado": u["created_at"],
        "url": "https://www.twitch.tv/" + u["login"],
        "directo": None,
    }
    if directos:
        d = directos[0]
        streamer["directo"] = {
            "titulo": d["title"],
            "juego": d["game_name"],
            "espectadores": d["viewer_count"],
            "inicio": d["started_at"],
        }
    return streamer


def buscar_juego(nombre):
    juegos = _get("/games", {"name": nombre})
    if not juegos:
        return None
    j = juegos[0]
    top = _get("/streams", {"game_id": j["id"], "first": 3})
    return {
        "id": j["id"],
        "nombre": j["name"],
        "caratula": j["box_art_url"].replace("{width}", "285").replace("{height}", "380"),
        "top_directos": [{"streamer": s["user_name"], "espectadores": s["viewer_count"]} for s in top],
    }
