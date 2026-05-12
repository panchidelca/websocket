# client_chat.py
import asyncio
import websockets
import json
import requests

API_URL = "http://127.0.0.1:5001"

def menu_auth():
    """Menú de registro/login en terminal. Retorna (username, password)."""
    while True:
        print("\n=== CHAT APP ===")
        print("1. Registrarse")
        print("2. Iniciar sesión")
        opcion = input("Elegí una opción: ").strip()

        username = input("Username: ").strip()
        password = input("Contraseña: ").strip()

        if opcion == "1":
            resp = requests.post(f"{API_URL}/register", json={"username": username, "password": password})
            data = resp.json()
            if resp.status_code == 201:
                print(f"✓ {data['message']}. Ahora podés iniciar sesión.")
            else:
                print(f"✗ Error: {data.get('error')}")

        elif opcion == "2":
            resp = requests.post(f"{API_URL}/login", json={"username": username, "password": password})
            data = resp.json()
            if resp.status_code == 200:
                print(f"✓ {data['message']}")
                return username, password
            else:
                print(f"✗ Error: {data.get('error')}")
        else:
            print("Opción inválida.")

async def chat(username, password):
    loop = asyncio.get_event_loop()

    async with websockets.connect("ws://127.0.0.1:5000") as websocket:
        # Enviar credenciales al servidor WS
        await websocket.send(json.dumps({"username": username, "password": password}))

        # Esperar respuesta de autenticación
        resp = json.loads(await websocket.recv())
        if "error" in resp:
            print(f"✗ {resp['error']}")
            return
        print(resp["message"])
        print("--- Escribí tu mensaje y presioná Enter. Ctrl+C para salir. ---\n")

        async def recibir():
            async for raw in websocket:
                msg = json.loads(raw)
                if "system" in msg:
                    print(f"\n{msg['system']}")
                elif "from" in msg:
                    print(f"\n{msg['from']}: {msg['message']}")

        async def enviar():
            while True:
                texto = await loop.run_in_executor(None, input)
                if texto.strip():
                    await websocket.send(texto)

        await asyncio.gather(recibir(), enviar())

def main():
    username, password = menu_auth()
    asyncio.run(chat(username, password))

if __name__ == "__main__":
    main()