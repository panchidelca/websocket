from flask import Flask, request, jsonify, send_from_directory
from database import init_db, register_user, login_user
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from database import init_db, register_user, login_user
import os
import logging

# Silenciar logs de Flask y Werkzeug
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

app = Flask(__name__)
CORS(app)

init_db()

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

@app.route("/")
def index():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    runtime = os.path.join(base_dir, "index_runtime.html")
    if os.path.exists(runtime):
        return send_from_directory(base_dir, "index_runtime.html")
    return send_from_directory(base_dir, "index.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=False, port=5001)