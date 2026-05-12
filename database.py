import sqlite3
import hashlib
import os

DB_NAME = "chat.db"

def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            salt TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()

def hash_password(password: str, salt: str = None):
    if salt is None:
        salt = os.urandom(16).hex()
    pw_hash = hashlib.sha256((salt + password).encode()).hexdigest()
    return pw_hash, salt

def register_user(username: str, password: str):
    """
    Registra un usuario nuevo.
    Retorna (True, "User created") o (False, "mensaje de error")
    """
    conn = get_db()
    cursor = conn.cursor()
    pw_hash, salt = hash_password(password)
    try:
        cursor.execute(
            "INSERT INTO users (username, password_hash, salt) VALUES (?, ?, ?)",
            (username, pw_hash, salt)
        )
        conn.commit()
        return True, "User created"
    except sqlite3.IntegrityError:
        return False, "User already exists"
    finally:
        conn.close()

def login_user(username: str, password: str):
    """
    Verifica credenciales.
    Retorna (True, "OK") o (False, "mensaje de error")
    """
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()

    if not user:
        return False, "Usuario no encontrado"

    pw_hash, _ = hash_password(password, user["salt"])
    if pw_hash != user["password_hash"]:
        return False, "Contraseña incorrecta"

    return True, "OK"