import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
import sqlite3
import os
from datetime import datetime

def get_app_data_dir():
    app_data = os.environ.get('APPDATA')
    if not app_data:
        app_data = os.path.expanduser('~')
    
    tasksense_dir = os.path.join(app_data, 'TaskSenseAI')
    if not os.path.exists(tasksense_dir):
        os.makedirs(tasksense_dir)
    return tasksense_dir

DB_PATH = os.path.join(get_app_data_dir(), 'tasksense.db')

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def initialize_database():
    conn = get_connection()
    cursor = conn.cursor()

    # Tasks table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            due_date TEXT,
            priority TEXT DEFAULT 'Medium',
            status TEXT DEFAULT 'Pending',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            completed_at TEXT,
            reminders_sent INTEGER DEFAULT 0,
            current_risk TEXT DEFAULT 'N/A',
            is_deleted INTEGER DEFAULT 0
        )
    ''')

    # Ensure migrations on existing databases
    cursor.execute("PRAGMA table_info(tasks)")
    columns = [col['name'] for col in cursor.fetchall()]
    if 'current_risk' not in columns:
        cursor.execute("ALTER TABLE tasks ADD COLUMN current_risk TEXT DEFAULT 'N/A'")
    if 'is_deleted' not in columns:
        cursor.execute("ALTER TABLE tasks ADD COLUMN is_deleted INTEGER DEFAULT 0")
    if 'completed_at' not in columns:
        cursor.execute("ALTER TABLE tasks ADD COLUMN completed_at TEXT")
    if 'reminders_sent' not in columns:
        cursor.execute("ALTER TABLE tasks ADD COLUMN reminders_sent INTEGER DEFAULT 0")

    # Behavior logs table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS behavior_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id INTEGER,
            delay_minutes INTEGER DEFAULT 0,
            ignored_reminders INTEGER DEFAULT 0,
            completion_time_minutes INTEGER DEFAULT 0,
            logged_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (task_id) REFERENCES tasks(id)
        )
    ''')

    # Predictions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id INTEGER,
            risk_level TEXT,
            predicted_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (task_id) REFERENCES tasks(id)
        )
    ''')

    # Settings table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS app_settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    ''')
    
    # Initialize default settings
    cursor.execute("INSERT OR IGNORE INTO app_settings (key, value) VALUES ('check_interval', '5')")
    cursor.execute("INSERT OR IGNORE INTO app_settings (key, value) VALUES ('last_run_date', ?)", (datetime.now().date().isoformat(),))
    cursor.execute("INSERT OR IGNORE INTO app_settings (key, value) VALUES ('auto_start', '0')")

    conn.commit()
    conn.close()
    logging.info(f"Database initialized at {DB_PATH}")

def get_setting(key, default_value=None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM app_settings WHERE key = ?", (key,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return row['value']
    return default_value

def set_setting(key, value):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO app_settings (key, value) VALUES (?, ?)", (key, str(value)))
    conn.commit()
    conn.close()

if __name__ == "__main__":
    initialize_database()
