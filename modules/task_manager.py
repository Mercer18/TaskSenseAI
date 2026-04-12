import sqlite3
from datetime import datetime
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.db_manager import get_connection

def add_task(title, description, due_date, priority):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO tasks (title, description, due_date, priority, status, created_at)
        VALUES (?, ?, ?, ?, 'Pending', ?)
    ''', (title, description, due_date, priority, datetime.now().isoformat()))
    conn.commit()
    task_id = cursor.lastrowid
    conn.close()
    return task_id

def get_all_tasks():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM tasks ORDER BY created_at DESC')
    tasks = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return tasks

def get_task_by_id(task_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM tasks WHERE id = ?', (task_id,))
    task = cursor.fetchone()
    conn.close()
    return dict(task) if task else None

def update_task_status(task_id, status):
    conn = get_connection()
    cursor = conn.cursor()
    completed_at = datetime.now().isoformat() if status == 'Completed' else None
    cursor.execute('''
        UPDATE tasks SET status = ?, completed_at = ? WHERE id = ?
    ''', (status, completed_at, task_id))
    conn.commit()
    conn.close()

def delete_task(task_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM behavior_logs WHERE task_id = ?', (task_id,))
    cursor.execute('DELETE FROM predictions WHERE task_id = ?', (task_id,))
    cursor.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
    conn.commit()
    conn.close()

def get_pending_tasks():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks WHERE status = 'Pending' ORDER BY due_date ASC")
    tasks = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return tasks

def get_task_stats():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as total FROM tasks")
    total = cursor.fetchone()['total']
    cursor.execute("SELECT COUNT(*) as completed FROM tasks WHERE status = 'Completed'")
    completed = cursor.fetchone()['completed']
    cursor.execute("SELECT COUNT(*) as pending FROM tasks WHERE status = 'Pending'")
    pending = cursor.fetchone()['pending']
    conn.close()
    return {'total': total, 'completed': completed, 'pending': pending}