import threading
import asyncio
import socket
import time
import os
import sys
import webbrowser
from PIL import Image, ImageDraw
import pystray

LOCAL_IP   = None
FLASK_PORT = 5001
WS_PORT    = 5000

# ── Resolver IP local ─────────────────────────────────────────────────────────
def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

# ── Inyectar IP en index.html ─────────────────────────────────────────────────
def patch_index(ip):
    base_dir = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    path = os.path.join(base_dir, "index.html")
    with open(path, "r", encoding="utf-8") as f:
        html = f.read()
    html = html.replace("__API_URL__", f"http://{ip}:{FLASK_PORT}")
    html = html.replace("__WS_URL__",  f"ws://{ip}:{WS_PORT}")
    out_path = os.path.join(base_dir, "index_runtime.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)

# ── Flask ─────────────────────────────────────────────────────────────────────
def run_flask():
    from app import app
    app.run(host="0.0.0.0", port=FLASK_PORT, debug=False, use_reloader=False)

# ── WebSocket ─────────────────────────────────────────────────────────────────
def run_ws():
    import server_ws
    asyncio.run(server_ws.start_server())

# ── Esperar a que Flask esté listo ────────────────────────────────────────────
def wait_for_flask(timeout=10):
    import urllib.request
    url = f"http://127.0.0.1:{FLASK_PORT}/"
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            urllib.request.urlopen(url, timeout=1)
            return True
        except Exception:
            time.sleep(0.1)
    return False

# ── Ícono del tray ────────────────────────────────────────────────────────────
def create_icon_image():
    img = Image.new("RGB", (64, 64), color=(15, 15, 25))
    draw = ImageDraw.Draw(img)
    # Burbuja de chat simple
    draw.ellipse([8, 8, 56, 48], fill=(0, 255, 136))
    draw.polygon([(12, 44), (8, 58), (24, 48)], fill=(0, 255, 136))
    return img

def abrir_chat(icon, item):
    webbrowser.open(f"http://{LOCAL_IP}:{FLASK_PORT}")

def cerrar(icon, item):
    icon.stop()
    os.kill(os.getpid(), 9)

def run_tray():
    menu = pystray.Menu(
        pystray.MenuItem(f"Abrir chat ({LOCAL_IP}:{FLASK_PORT})", abrir_chat, default=True),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("Cerrar servidor", cerrar),
    )
    icon = pystray.Icon("Chat App", create_icon_image(), "Chat App", menu)
    icon.run()

# ── Main ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    LOCAL_IP = get_local_ip()
    patch_index(LOCAL_IP)

    threading.Thread(target=run_flask, daemon=True).start()
    threading.Thread(target=run_ws,    daemon=True).start()

    print("Iniciando servidores...")
    if not wait_for_flask():
        print("ERROR: Flask no arrancó a tiempo.")
        sys.exit(1)

    print(f"Servidores corriendo:")
    print(f"  Web  → http://{LOCAL_IP}:{FLASK_PORT}")
    print(f"  Chat → ws://{LOCAL_IP}:{WS_PORT}")
    print(f"Ícono en la bandeja del sistema. Click derecho para opciones.")

    run_tray()  # bloquea acá — la app vive mientras el tray esté activo