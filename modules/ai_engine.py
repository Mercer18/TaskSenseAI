import os
import sys
import pickle
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.db_manager import get_connection

MODEL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'models', 'procrastination_model.pkl')
DATA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'synthetic_data.csv')

def generate_synthetic_data():
    import random
    random.seed(42)
    np.random.seed(42)

    data = []
    for _ in range(1000):
        delay = random.randint(0, 300)
        ignored = random.randint(0, 10)
        completion = random.randint(5, 500)

        if delay > 150 or ignored >= 5:
            risk = 'High'
        elif delay > 60 or ignored >= 2:
            risk = 'Medium'
        else:
            risk = 'Low'

        # Add some noise
        if random.random() < 0.05:
            risk = random.choice(['Low', 'Medium', 'High'])

        data.append([delay, ignored, completion, risk])

    df = pd.DataFrame(data, columns=['delay_minutes', 'ignored_reminders', 'completion_time_minutes', 'risk_label'])
    df.to_csv(DATA_PATH, index=False)
    print(f"Synthetic data generated: {len(df)} rows")
    return df

def train_model():
    if not os.path.exists(DATA_PATH):
        df = generate_synthetic_data()
    else:
        df = pd.read_csv(DATA_PATH)

    X = df[['delay_minutes', 'ignored_reminders', 'completion_time_minutes']]
    y = df['risk_label']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Train multiple models and pick best
    models = {
        'RandomForest': RandomForestClassifier(n_estimators=100, random_state=42),
        'DecisionTree': DecisionTreeClassifier(random_state=42),
        'LogisticRegression': LogisticRegression(random_state=42, max_iter=1000)
    }

    best_model = None
    best_accuracy = 0
    best_name = ''

    for name, model in models.items():
        model.fit(X_train, y_train)
        preds = model.predict(X_test)
        acc = accuracy_score(y_test, preds)
        print(f"{name} accuracy: {acc:.2f}")
        if acc > best_accuracy:
            best_accuracy = acc
            best_model = model
            best_name = name

    print(f"Best model: {best_name} with accuracy {best_accuracy:.2f}")

    with open(MODEL_PATH, 'wb') as f:
        pickle.dump(best_model, f)

    print(f"Model saved to {MODEL_PATH}")
    return best_model, best_accuracy

def load_model():
    if not os.path.exists(MODEL_PATH):
        print("No model found, training now...")
        model, _ = train_model()
        return model
    with open(MODEL_PATH, 'rb') as f:
        return pickle.load(f)

def predict_risk(delay_minutes, ignored_reminders, completion_time_minutes):
    model = load_model()
    features = np.array([[delay_minutes, ignored_reminders, completion_time_minutes]])
    prediction = model.predict(features)[0]
    probabilities = model.predict_proba(features)[0]
    confidence = round(max(probabilities) * 100, 1)
    return prediction, confidence

def save_prediction(task_id, risk_level):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO predictions (task_id, risk_level, predicted_at)
        VALUES (?, ?, datetime('now'))
    ''', (task_id, risk_level))
    conn.commit()
    conn.close()

def get_prediction_for_task(task_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM predictions WHERE task_id = ?
        ORDER BY predicted_at DESC LIMIT 1
    ''', (task_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def ensure_model_exists():
    if not os.path.exists(MODEL_PATH):
        print("Training initial AI model...")
        train_model()