import json
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix
import joblib
import os
import pickle

DATA_FILE = "logs/training_data.json"
MODEL_FILE = "models/keystroke_model.pkl"

def load_data():
    X, y = [], []
    if not os.path.exists(DATA_FILE):
        print(f"❌ Plik {DATA_FILE} nie istnieje.")
        return X, y

    with open(DATA_FILE, "r") as file:
        for line in file:
            entry = json.loads(line)
            intervals = entry["intervals"]
            if len(intervals) < 2:
                continue  
            features = [
                np.mean(intervals), # Średni czas
                np.std(intervals), # Odchylenie standardowe
                max(intervals), # Maksymalny interwał
                min(intervals), # Minimalny interwał
            ]
            X.append(features)
            y.append(1 if entry["label"] == "bot" else 0)  # bot = 1, ludzie = 0

    return np.array(X), np.array(y)

def train_model():
    X, y = load_data()
    if len(X) == 0:
        print("❗ Brak danych do treningu.")
        return

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    print("\n📊 Wyniki modelu:")
    print(classification_report(y_test, y_pred))
    print(f"🎯 Dokładność: {accuracy_score(y_test, y_pred):.2f}")

    os.makedirs("models", exist_ok=True)
    joblib.dump(model, MODEL_FILE)
    print(f"✅ Model zapisany w: {MODEL_FILE}")


def evaluate_model():
    with open("logs/training_data.json", "r") as file:
        data = [json.loads(line) for line in file]

    X = [entry["keystrokes"] for entry in data]
    y = [1 if entry["label"] == "bot" else 0 for entry in data]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    with open("models/keystroke_model.pkl", "rb") as model_file:
        model = pickle.load(model_file)

    y_pred = model.predict(X_test)

    print("📊 Raport klasyfikacji:")
    print(classification_report(y_test, y_pred))
    print("📉 Macierz pomyłek:")
    print(confusion_matrix(y_test, y_pred))


if __name__ == "__main__":
    train_model()
