import keyboard
import time
import json
from datetime import datetime
import numpy as np
from src.block_ip import block_ip

LOG_PATH = "logs/keyboard_activity.log"

def on_key(event):
    keystrokes.append((event.name, time.time()))

def analyze_keystrokes(keystrokes, ip=None):
    times = [t for _, t in keystrokes]
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
        print("🚨 Podejrzenie bota.")
        if ip:
            block_ip(ip)
    else:
        print("✅ Prawdopodobnie człowiek.")

def save_log(keystrokes):
    data = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "keystrokes": keystrokes
    }
    with open(LOG_PATH, "a") as file:
        file.write(json.dumps(data) + "\n")
    print(f"✅ Zapisano logi do {LOG_PATH}")

if __name__ == "__main__":
    keystrokes = []
    print("⌨️  Monitoring klawiatury rozpoczęty. Naciśnij 'ESC', aby zakończyć.")
    keyboard.hook(on_key)
    keyboard.wait("esc")  
    analyze_keystrokes(keystrokes)
    save_log(keystrokes)
