# server_chat.py
import asyncio
import websockets
import json
from database import init_db, login_user

init_db()

clients = {}

async def handler(websocket):
    # Esperar credenciales como JSON: {"username": "...", "password": "..."}
    try:
        raw = await websocket.recv()
        creds = json.loads(raw)
        username = creds.get("username", "").strip()
        password = creds.get("password", "")
    except Exception:
        await websocket.send(json.dumps({"error": "Formato inválido. Enviá JSON con username y password."}))
        await websocket.close()
        return

    # Verificar credenciales
    success, message = login_user(username, password)
    if not success:
        await websocket.send(json.dumps({"error": message}))
        await websocket.close()
        return

    # Login OK
    await websocket.send(json.dumps({"ok": True, "message": f"Bienvenido, {username}!"}))
    clients[websocket] = username
    print(f"{username} se conectó. Total conectados: {len(clients)}")

    # Avisar a los demás
    await asyncio.gather(
        *[client.send(json.dumps({"system": f"*** {username} se unió al chat ***"}))
          for client in clients if client != websocket]
    )

    try:
        async for message in websocket:
            full = {"from": username, "message": message}
            print(f"{username}: {message}")

            # Broadcast a todos EXCEPTO el emisor
            await asyncio.gather(
                *[client.send(json.dumps(full))
                  for client in clients if client != websocket]
            )

    finally:
        if websocket in clients:
            print(f"{clients[websocket]} se desconectó.")
            del clients[websocket]

            await asyncio.gather(
                *[client.send(json.dumps({"system": f"*** {username} salió del chat ***"}))
                  for client in clients]
            )


async def main():
    async with websockets.serve(handler, "127.0.0.1", 5000):
        print("Servidor chat corriendo en ws://127.0.0.1:5000")
        print("API REST + Web en http://127.0.0.1:5001  (correr app.py por separado)")
        await asyncio.Future()

asyncio.run(main())