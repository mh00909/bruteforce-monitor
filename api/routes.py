from flask import Blueprint, jsonify, request, current_app, send_file
from functools import wraps
from datetime import datetime, timedelta
import jwt
import json
import os
import io
import csv
import subprocess
from src.monitor_logs import monitor_login_attempts
from src.block_ip import block_ip



api_blueprint = Blueprint("api", __name__)

LOG_FILE = "logs/auth_attempts.log"
HISTORY_FILE = "logs/block_history.json"


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')

        if not token:
            return jsonify({"error": "Token wymagany."}), 401

        try:
            token = token.replace("Bearer ", "")
            jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token wygasł."}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Nieprawidłowy token."}), 401

        return f(*args, **kwargs)
    return decorated


@api_blueprint.route("/failed_attempts", methods=["GET"])
@token_required
def get_failed_attempts():
    attempts = monitor_login_attempts()
    return jsonify({"failed_attempts": attempts}), 200



@api_blueprint.route("/blocked_ips", methods=["GET"])
@token_required
def get_blocked_ips():
    try:
        result = subprocess.run(
            ["sudo", "iptables", "-L", "INPUT", "-v", "-n"],
            capture_output=True, text=True, check=True
        )

        blocked_ips = []
        for line in result.stdout.split("\n"):
            if "DROP" in line:
                parts = line.split()
                if len(parts) >= 8:
                    ip = parts[7]
                    blocked_ips.append(ip)

        return jsonify({"blocked_ips": blocked_ips}), 200

    except subprocess.CalledProcessError as e:
        return jsonify({"error": "Błąd podczas odczytu iptables."}), 500




@api_blueprint.route("/block_ip", methods=["POST"])
@token_required
def post_block_ip():
    data = request.get_json()
    ip = data.get("ip")
    if not ip:
        return jsonify({"error": "Brak adresu IP"}), 400

    block_ip(ip)
    save_to_history(ip, "blocked")

    with open(LOG_FILE, "a") as file:
        file.write(f"✅ Zablokowano IP: {ip}\n")

    return jsonify({"message": f"IP {ip} zablokowane."}), 200


@api_blueprint.route("/unblock_ip", methods=["POST"])
@token_required
def unblock_ip():
    data = request.get_json()
    ip = data.get("ip")

    if not ip:
        return jsonify({"error": "Brak adresu IP"}), 400

    try:
        subprocess.run(["sudo", "iptables", "-D", "INPUT", "-s", ip, "-j", "DROP"], check=True)
        save_to_history(ip, "unblocked")

        with open(LOG_FILE, "a") as file:
            file.write(f"✅ Odblokowano IP: {ip}\n")

        return jsonify({"message": f"IP {ip} odblokowane."}), 200

    except subprocess.CalledProcessError:
        return jsonify({"error": f"Nie można odblokować IP {ip}."}), 500




@api_blueprint.route("/block_history", methods=["GET"])
@token_required
def get_block_history():
    if not os.path.exists(HISTORY_FILE):
        return jsonify({"history": []}), 200

    with open(HISTORY_FILE, "r") as file:
        history = [json.loads(line) for line in file.readlines()]

    history.sort(key=lambda x: x["timestamp"], reverse=True)

    return jsonify({"history": history}), 200


@api_blueprint.route("/export_history", methods=["GET"])
@token_required
def export_history():
    if not os.path.exists(HISTORY_FILE):
        return jsonify({"error": "Brak historii do eksportu."}), 404

    try:
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["Adres IP", "Akcja", "Data i godzina"])  # Nagłówki

        with open(HISTORY_FILE, "r") as infile:
            for line in infile:
                try:
                    entry = json.loads(line.strip())
                    writer.writerow([
                        entry.get("ip", "Brak danych"),
                        "Zablokowano" if entry.get("action") == "blocked" else "Odblokowano",
                        entry.get("timestamp", "Brak daty")
                    ])
                except json.JSONDecodeError as e:
                    print(f"⚠️ Błąd w linii historii: {e}")  # Wyświetla problematyczne linie

        output.seek(0)
        return send_file(
            io.BytesIO(output.getvalue().encode('utf-8')),
            mimetype='text/csv',
            as_attachment=True,
            download_name="block_history.csv"
        )

    except Exception as e:
        print(f"❌ Błąd eksportu: {e}")
        return jsonify({"error": f"Błąd podczas eksportu: {str(e)}"}), 500
    




@api_blueprint.route("/login", methods=["POST"])
@token_required
def login():
    auth = request.get_json()

    if not auth or not auth.get("username") or not auth.get("password"):
        return jsonify({"error": "Podaj login i hasło."}), 400

    username = auth.get("username")
    password = auth.get("password")

    users = {"admin": "adminpass", "user": "userpass"}

    if users.get(username) != password:
        return jsonify({"error": "Nieprawidłowe dane logowania."}), 401

    token = jwt.encode(
        {"user": username, "exp": datetime.utcnow() + timedelta(hours=2)},
        current_app.config['SECRET_KEY'],
        algorithm="HS256"
    )

    return jsonify({"token": token})





def save_to_history(ip, action):
    entry = {
        "ip": ip,
        "action": action,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    with open(HISTORY_FILE, "a") as file:
        file.write(json.dumps(entry) + "\n")
