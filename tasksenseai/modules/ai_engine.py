# -*- coding: utf-8 -*-
import logging
import os
import pickle
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

from tasksenseai.database.db_manager import get_connection, set_setting, get_setting

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

        if random.random() < 0.05:
            risk = random.choice(['Low', 'Medium', 'High'])

        data.append([delay, ignored, completion, risk])

    df = pd.DataFrame(data, columns=['delay_minutes', 'ignored_reminders', 'completion_time_minutes', 'risk_label'])
    df.to_csv(DATA_PATH, index=False)
    logging.info(f"Synthetic data generated: {len(df)} rows")
    return df


def train_model():
    if not os.path.exists(DATA_PATH):
        df = generate_synthetic_data()
    else:
        df = pd.read_csv(DATA_PATH)

    X = df[['delay_minutes', 'ignored_reminders', 'completion_time_minutes']]
    y = df['risk_label']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

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
        logging.info(f"{name} accuracy: {acc:.2f}")
        if acc > best_accuracy:
            best_accuracy = acc
            best_model = model
            best_name = name

    logging.info(f"Best model: {best_name} with accuracy {best_accuracy:.2f}")

    with open(MODEL_PATH, 'wb') as f:
        pickle.dump(best_model, f)

    from datetime import datetime
    set_setting('model_trained_at', datetime.now().isoformat())
    set_setting('model_accuracy', f"{best_accuracy:.2f}")
    set_setting('model_samples', str(len(df)))
    set_setting('model_name', best_name)

    logging.info(f"Model saved to {MODEL_PATH}")
    return best_model, best_accuracy


def load_model():
    if not os.path.exists(MODEL_PATH):
        logging.info("No model found, training now...")
        model, _ = train_model()
        return model
    with open(MODEL_PATH, 'rb') as f:
        return pickle.load(f)


def predict_risk(delay_minutes, ignored_reminders, completion_time_minutes):
    try:
        model = load_model()
        features = pd.DataFrame(
            [[delay_minutes, ignored_reminders, completion_time_minutes]],
            columns=['delay_minutes', 'ignored_reminders', 'completion_time_minutes']
        )
        prediction = model.predict(features)[0]
        probabilities = model.predict_proba(features)[0]
        confidence = round(max(probabilities) * 100, 1)
        return prediction, confidence
    except Exception as e:
        logging.info(f"ML Model failed: {e}. Using deterministic fallback.")
        score = (delay_minutes * 2) + (ignored_reminders * 10)
        risk = 'Low'
        if score > 150: risk = 'High'
        elif score > 60: risk = 'Medium'
        return risk, 50.0


def save_prediction(task_id, risk_level):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT current_risk FROM tasks WHERE id = ?', (task_id,))
    row = cursor.fetchone()
    old_risk = row['current_risk'] if row else None

    if old_risk != risk_level:
        cursor.execute("UPDATE tasks SET current_risk = ? WHERE id = ?", (risk_level, task_id))
        cursor.execute('''
            INSERT INTO predictions (task_id, risk_level, predicted_at)
            VALUES (?, ?, datetime('now'))
        ''', (task_id, risk_level))
        conn.commit()
    conn.close()


def get_prediction_for_task(task_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT current_risk FROM tasks WHERE id = ?', (task_id,))
    row = cursor.fetchone()
    conn.close()
    if row and row['current_risk'] != 'N/A':
        return {'risk_level': row['current_risk']}
    return None


def ensure_model_exists():
    if not os.path.exists(MODEL_PATH):
        logging.info("Training initial AI model...")
        train_model()
