from flask import Blueprint, jsonify, request
from src.monitor_logs import monitor_login_attempts
from src.block_ip import block_ip
import json
import os

api_blueprint = Blueprint("api", __name__)

LOG_FILE = "logs/auth_attempts.log"

@api_blueprint.route("/failed_attempts", methods=["GET"])
def get_failed_attempts():
    attempts = monitor_login_attempts()
    return jsonify({"failed_attempts": attempts}), 200

@api_blueprint.route("/blocked_ips", methods=["GET"])
def get_blocked_ips():
    if not os.path.exists(LOG_FILE):
        return jsonify({"blocked_ips": []}), 200

    blocked_ips = []
    with open(LOG_FILE, "r") as file:
        for line in file:
            if "Zablokowano IP" in line:
                ip = line.strip().split(":")[-1].strip()
                blocked_ips.append(ip)
    return jsonify({"blocked_ips": blocked_ips}), 200

@api_blueprint.route("/block_ip", methods=["POST"])
def post_block_ip():
    data = request.get_json()
    ip = data.get("ip")
    if not ip:
        return jsonify({"error": "Brak adresu IP"}), 400

    block_ip(ip)
    with open(LOG_FILE, "a") as file:
        file.write(f"✅ Zablokowano IP: {ip}\n")

    return jsonify({"message": f"IP {ip} zablokowane."}), 200
