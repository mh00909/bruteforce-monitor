import keyboard
import time
import joblib
import numpy as np
from src.block_ip import block_ip

MODEL_FILE = "models/keystroke_model.pkl"

def capture_keystrokes():
    keystrokes = []
    print("⌨️  Naciśnij klawisze do analizy (ESC kończy).")

    def on_key(event):
        keystrokes.append((event.name, time.time()))

    keyboard.hook(on_key)
    keyboard.wait("esc")
    return keystrokes

def extract_features(keystrokes):
    intervals = [t2 - t1 for (_, t1), (_, t2) in zip(keystrokes[:-1], keystrokes[1:])]
    if len(intervals) < 2:
        print("❗ Za mało danych.")
        return None
    return [np.mean(intervals), np.std(intervals), max(intervals), min(intervals)]

def predict_with_blocking(ip=None):
    model = joblib.load(MODEL_FILE)
    keystrokes = capture_keystrokes()
    features = extract_features(keystrokes)
    if features:
        prediction = model.predict([features])[0]
        if prediction == 1:
            print("\n🚨 Wykryto bota!")
            if ip:
                block_ip(ip)
        else:
            print("\n✅ To prawdopodobnie człowiek.")

if __name__ == "__main__":
    target_ip = input("Podaj IP do ewentualnego zablokowania (Enter, aby pominąć): ").strip()
    predict_with_blocking(target_ip if target_ip else None)