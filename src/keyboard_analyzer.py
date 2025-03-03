import keyboard
import time
import json
from datetime import datetime
import requests
import numpy as np
from src.block_ip import block_ip

LOG_PATH = "logs/keyboard_activity.log"
API_URL = "http://localhost:5000/api/block_ip"
BOT_ACTIVITY_LOG = "logs/bot_activity.log"

TEST_IP = "192.168.60.100"

def get_jwt_token(username, password):
    response = requests.post("http://localhost:5000/api/login", json={"username": username, "password": password})
    return response.json().get("token") if response.status_code == 200 else None


def analyze_keystrokes(keystrokes, ip=None):
    times = keystrokes
    if len(times) < 2:
        print("📢 Zbyt mało danych do analizy.")
        return

    intervals = np.diff(times)
    avg_interval = np.mean(intervals)
    std_dev = np.std(intervals)

    print(f"\n📊 Analiza:")
    print(f"Średni czas między naciśnięciami: {avg_interval:.3f}s")
    print(f"Odchylenie standardowe: {std_dev:.3f}")

    if std_dev < 0.05:
        print("bot")
        return "bot"
    else:
        print("human")
        return "human"


def save_log(keystrokes):
    data = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "keystrokes": keystrokes
    }
    with open(LOG_PATH, "a") as file:
        file.write(json.dumps(data) + "\n")
    print(f"✅ Zapisano logi do {LOG_PATH}")

def save_bot_activity(ip):
    activity = {
        "ip": ip,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    with open(BOT_ACTIVITY_LOG, "a") as file:
        file.write(json.dumps(activity) + "\n")
    print(f"✅ Zapisano aktywność bota do {BOT_ACTIVITY_LOG}")



def simulate_bot_typing():
    print("Symulacja bota...")

    bot_keystrokes = [0.05, 0.04, 0.06, 0.05, 0.05, 0.06, 0.05]
    
    prediction = analyze_keystrokes(bot_keystrokes)
    print(f"🔍 Wykryto: {prediction} dla IP {TEST_IP}")

    if prediction == "bot":
        print(f"⚠️ Bot wykryty! Blokowanie IP {TEST_IP}...")
        block_ip_via_api(TEST_IP)
        save_bot_activity(TEST_IP)


def simulate_human_typing():
    print("Symulacja człowieka...")

    human_keystrokes = [0.2, 0.3, 0.15, 0.25, 0.4, 0.22, 0.35]

    prediction = analyze_keystrokes(human_keystrokes)
    print(f"🔍 Wykryto: {prediction} dla IP {TEST_IP}")



def block_ip_via_api(ip):
    token = get_jwt_token("admin", "adminpass")
    if not token:
        print("❌ Nie udało się pobrać tokenu.")
        return

    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    response = requests.post(API_URL, json={"ip": ip}, headers=headers)
    if response.status_code == 200:
        print(f"✅ Zablokowano IP przez API: {ip}")
    else:
        print(f"❌ Błąd blokowania IP ({ip}): {response.json().get('error')}")


if __name__ == "__main__":
    mode = input("Wybierz tryb: bot (b) / człowiek (h): ").strip().lower()
    
    if mode == "b":
        simulate_bot_typing()
    elif mode == "h":
        simulate_human_typing()
    else:
        print("⚠️ Nieznany tryb. Wybierz 'b' dla bota lub 'h' dla człowieka.")


