from flask import Flask, request, jsonify, send_from_directory
from database import init_db, register_user, login_user
import os

app = Flask(__name__)

init_db()

# --- API REST ---

@app.route("/register", methods=["POST"])
def register():
    data = request.json
    username = data.get("username", "").strip()
    password = data.get("password", "")

    if not username or not password:
        return jsonify({"error": "Username y contraseña requeridos"}), 400

    success, message = register_user(username, password)
    if not success:
        return jsonify({"error": message}), 409

    return jsonify({"message": message}), 201


@app.route("/login", methods=["POST"])
def login():
    data = request.json
    username = data.get("username", "").strip()
    password = data.get("password", "")

    if not username or not password:
        return jsonify({"error": "Username y contraseña requeridos"}), 400

    success, message = login_user(username, password)
    if not success:
        return jsonify({"error": message}), 401

    return jsonify({"message": "Login exitoso", "username": username}), 200


# --- Servir frontend web ---

@app.route("/")
def index():
    return send_from_directory(".", "index.html")


if __name__ == "__main__":
    app.run(debug=True, port=5001)