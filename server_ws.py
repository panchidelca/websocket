# server_ws.py
import asyncio
import websockets
import json
from database import init_db, login_user

init_db()

clients = {}

async def handler(websocket):
    try:
        raw = await websocket.recv()
        creds = json.loads(raw)
        username = creds.get("username", "").strip()
        password = creds.get("password", "")
    except Exception:
        await websocket.send(json.dumps({"error": "Formato inválido. Enviá JSON con username y password."}))
        await websocket.close()
        return

    success, message = login_user(username, password)
    if not success:
        await websocket.send(json.dumps({"error": message}))
        await websocket.close()
        return

    await websocket.send(json.dumps({"ok": True, "message": f"Bienvenido, {username}!"}))
    clients[websocket] = username
    print(f"{username} se conectó. Total conectados: {len(clients)}")

    await asyncio.gather(
        *[client.send(json.dumps({"system": f"*** {username} se unió al chat ***"}))
          for client in clients if client != websocket]
    )

    try:
        async for message in websocket:
            full = {"from": username, "message": message}
            print(f"{username}: {message}")
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


async def start_server(host="0.0.0.0", port=5000):
    """Llamado desde main.py en un hilo background."""
    async with websockets.serve(handler, host, port):
        print(f"Servidor WebSocket escuchando en ws://{host}:{port}")
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(start_server())