import json
import os

FICHERO = os.path.join(os.path.dirname(__file__), "datos.json")


def _cargar():
    if not os.path.exists(FICHERO):
        return {"siguiente_id": 1, "usuarios": []}
    with open(FICHERO, encoding="utf-8") as f:
        return json.load(f)


def _guardar(datos):
    with open(FICHERO, "w", encoding="utf-8") as f:
        json.dump(datos, f, indent=2, ensure_ascii=False)


def listar():
    return _cargar()["usuarios"]


def obtener(usuario_id):
    for u in listar():
        if u["id"] == usuario_id:
            return u
    return None


def buscar_email(email):
    for u in listar():
        if u["email"].lower() == email.lower():
            return u
    return None


def crear(usuario):
    datos = _cargar()
    usuario["id"] = datos["siguiente_id"]
    usuario["preferencias"] = {"streamers": [], "juegos": [], "idiomas": []}
    datos["siguiente_id"] += 1
    datos["usuarios"].append(usuario)
    _guardar(datos)
    return usuario


def actualizar(usuario_id, cambios):
    datos = _cargar()
    for u in datos["usuarios"]:
        if u["id"] == usuario_id:
            u.update(cambios)
            _guardar(datos)
            return u
    return None


def borrar(usuario_id):
    datos = _cargar()
    antes = len(datos["usuarios"])
    datos["usuarios"] = [u for u in datos["usuarios"] if u["id"] != usuario_id]
    _guardar(datos)
    return len(datos["usuarios"]) < antes
