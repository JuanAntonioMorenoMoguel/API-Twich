# API de Usuarios y Streamers

API REST hecha con FastAPI para gestionar usuarios y sus preferencias (streamers y juegos favoritos), con integración de la API de Twitch (Helix).

## Instalación

```
pip install -r requirements.txt
```

## Credenciales de Twitch

Registrar una aplicación en https://dev.twitch.tv/console/apps y crear un fichero `.env` en la carpeta del proyecto con su Client ID y Client Secret:

```
TWITCH_CLIENT_ID=tu_client_id
TWITCH_CLIENT_SECRET=tu_client_secret
```

## Ejecutar

```
uvicorn main:app --reload
```

La documentación interactiva (Swagger) queda en http://127.0.0.1:8000/docs

## Endpoints

| Método | Ruta | Descripción |
|---|---|---|
| GET | /usuarios | Lista los usuarios |
| GET | /usuarios/{id} | Devuelve un usuario |
| POST | /usuarios | Crea un usuario |
| PUT | /usuarios/{id} | Actualiza un usuario |
| DELETE | /usuarios/{id} | Elimina un usuario |
| GET | /usuarios/{id}/preferencias | Preferencias del usuario |
| PUT | /usuarios/{id}/preferencias | Guarda las preferencias |
| GET | /usuarios/{id}/favoritos | Datos de Twitch de sus streamers y juegos favoritos |
| GET | /twitch/buscar?q=... | Busca canales en Twitch |
| GET | /twitch/streamers/{login} | Información de un streamer y si está en directo |
| GET | /twitch/juegos?nombre=... | Información de un juego y sus directos más vistos |

## Postman

Importar `API_Streamers.postman_collection.json` en Postman, o ejecutarla desde la terminal con la API arrancada:

```
npx newman run API_Streamers.postman_collection.json
```
