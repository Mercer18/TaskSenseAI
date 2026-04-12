import sqlite3
from datetime import datetime
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.db_manager import get_connection

def log_behavior(task_id, delay_minutes, ignored_reminders, completion_time_minutes):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO behavior_logs (task_id, delay_minutes, ignored_reminders, completion_time_minutes, logged_at)
        VALUES (?, ?, ?, ?, ?)
    ''', (task_id, delay_minutes, ignored_reminders, completion_time_minutes, datetime.now().isoformat()))
    conn.commit()
    conn.close()

def get_behavior_by_task(task_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM behavior_logs WHERE task_id = ?', (task_id,))
    logs = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return logs

def get_all_behavior():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM behavior_logs ORDER BY logged_at DESC')
    logs = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return logs

def get_average_behavior():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT 
            AVG(delay_minutes) as avg_delay,
            AVG(ignored_reminders) as avg_ignored,
            AVG(completion_time_minutes) as avg_completion
        FROM behavior_logs
    ''')
    row = cursor.fetchone()
    conn.close()
    return {
        'avg_delay': round(row['avg_delay'] or 0, 2),
        'avg_ignored': round(row['avg_ignored'] or 0, 2),
        'avg_completion': round(row['avg_completion'] or 0, 2)
    }

def get_user_risk_features(task_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT 
            COALESCE(AVG(delay_minutes), 0) as avg_delay,
            COALESCE(AVG(ignored_reminders), 0) as avg_ignored,
            COALESCE(AVG(completion_time_minutes), 0) as avg_completion
        FROM behavior_logs
        WHERE task_id = ?
    ''', (task_id,))
    row = cursor.fetchone()
    conn.close()
    return [row['avg_delay'], row['avg_ignored'], row['avg_completion']]