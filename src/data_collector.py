import keyboard
import time
import json
from datetime import datetime

def collect_data(label):
    keystrokes = []
    print(f"🚀 Rozpocznij pisanie ({label}). Naciśnij 'ESC', aby zakończyć.")

    def on_key(event):
        keystrokes.append((event.name, time.time()))

    keyboard.hook(on_key)
    keyboard.wait("esc")  

    intervals = [t2 - t1 for (_, t1), (_, t2) in zip(keystrokes[:-1], keystrokes[1:])]
    data = {"label": label, "intervals": intervals}

    with open("logs/training_data.json", "a") as file:
        file.write(json.dumps(data) + "\n")

    print(f"✅ Dane zapisane. Zebrano {len(intervals)} interwałów.\n")


def generate_bot_data(count=50, interval=0.1):
    """Generuje dane naciśnięć klawiszy dla bota z regularnymi odstępami."""
    keystrokes = []
    start_time = time.time()
    for i in range(count):
        keystrokes.append(("bot_key", start_time + i * interval))
    return keystrokes



def save_to_file(label, keystrokes):
    intervals = [t2 - t1 for (_, t1), (_, t2) in zip(keystrokes[:-1], keystrokes[1:])]
    data = {"label": label, "intervals": intervals}
    with open("logs/training_data.json", "a") as file:
        file.write(json.dumps(data) + "\n")
    print(f"✅ Zapisano {len(intervals)} interwałów dla etykiety '{label}'.")

if __name__ == "__main__":
    label = input("Podaj etykietę danych (bot/ludzie): ").strip().lower()

    if label == "bot":
        count = int(input("Ile naciśnięć zasymulować? (np. 50): "))
        interval = float(input("Podaj odstęp między naciśnięciami (np. 0.1): "))
        keystrokes = generate_bot_data(count, interval)
        save_to_file(label, keystrokes)
    else:
        print("🚀 Rozpocznij pisanie. Naciśnij 'ESC', aby zakończyć.")

        keystrokes = []
        def on_key(event):
            keystrokes.append((event.name, time.time()))

        keyboard.hook(on_key)
        keyboard.wait("esc")
        save_to_file(label, keystrokes)