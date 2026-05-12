# Chat App

App de chat en tiempo real para red local. Corre un servidor con interfaz web — cualquier dispositivo en la misma red WiFi puede conectarse desde el navegador.

## Estructura de archivos

```
chat_app/
├── main.py           ← punto de entrada
├── app.py            ← servidor Flask (API REST + frontend)
├── server_ws.py      ← servidor WebSocket (chat en tiempo real)
├── database.py       ← base de datos SQLite
├── index.html        ← interfaz web
├── requirements.txt  ← dependencias
└── chat.db           ← se crea automáticamente
```

## Instalación

### 1. Crear entorno virtual

```bash
python -m venv venv --system-site-packages
```

> `--system-site-packages` es necesario en Linux para que el venv pueda
> ver paquetes del sistema como `python-gobject`.

### 2. Activar el entorno

```bash
# Linux / Mac
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 3. Instalar dependencias del sistema (Linux)

**Arch / Manjaro:**
```bash
sudo pacman -S python-pyqt6-webengine python-gobject webkit2gtk
```

**Ubuntu / Debian:**
```bash
sudo apt install python3-gi gir1.2-webkit2-4.0 gir1.2-gtk-3.0
```

### 4. Instalar dependencias Python

```bash
pip install -r requirements.txt
```

## Uso

```bash
python main.py
```

Al arrancar:
- Los servidores quedan corriendo en background
- Aparece un **ícono en la bandeja del sistema**
- La consola muestra la dirección para compartir

### Opciones del ícono (click derecho)
- **Abrir chat** → abre el navegador con el chat
- **Cerrar servidor** → apaga todo

### Conectarse desde otro dispositivo
La consola muestra algo como:
```
Web  → http://192.168.1.55:5001
```
Cualquier dispositivo en la misma red WiFi puede abrir esa URL en su navegador, sin instalar nada.

## Puertos utilizados

| Puerto | Uso |
|--------|-----|
| 5001   | API REST + frontend web (Flask) |
| 5000   | WebSocket chat en tiempo real |

Asegurate de que el firewall permita estos puertos si otros dispositivos no pueden conectarse:

```bash
# Arch con ufw
sudo ufw allow 5000
sudo ufw allow 5001
```

## Notas

- Si ya tenías un `chat.db` de una versión anterior (sin contraseña), borralo: `rm chat.db`
- El archivo `index_runtime.html` se genera automáticamente al arrancar, no lo edites