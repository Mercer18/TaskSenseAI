# -*- coding: utf-8 -*-
import logging
import threading
import time
from datetime import datetime, timedelta
from tasksenseai.modules.task_manager import get_pending_tasks, increment_reminder_count
from tasksenseai.modules.ai_engine import predict_risk, save_prediction
from tasksenseai.modules.behavior_tracker import get_user_risk_features

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

try:
    from plyer import notification
    PLYER_AVAILABLE = True
except:
    PLYER_AVAILABLE = False

REMINDER_MESSAGES = {
    'Low': {
        'title': '📌 Task Reminder',
        'message': "You're on track, keep it up!\nDon't let it slip away! 💪"
    },
    'Medium': {
        'title': '🔔 Stay Focused!',
        'message': "Task due soon, time is ticking!\nGet on it before it's too late! ⏰"
    },
    'High': {
        'title': '🚨 Action Needed!',
        'message': "Critical Task Overdue! Complete it NOW!!\nSTOP PROCRASTINATING!!! ⚠️"
    }
}

def send_notification(risk_level, task_title):
    msg = REMINDER_MESSAGES.get(risk_level, REMINDER_MESSAGES['Medium'])

    if PLYER_AVAILABLE:
        try:
            notification.notify(
                title=f"{msg['title']}  —>  {task_title}  {msg['title'][0]}",
                message=msg['message'],
                app_name='TaskSenseAI',
                timeout=8
            )
        except Exception as e:
            logging.info(f"Notification error: {e}")
    else:
        logging.info(f"[{msg['title']}] {task_title} —> {msg['message']}")

# Track last reminder time per task
_last_reminded = {}

def check_and_remind():
    tasks = get_pending_tasks()
    now = datetime.now()

    for task in tasks:
        if not task.get('due_date'):
            continue
        try:
            due = datetime.fromisoformat(task['due_date'])
            time_diff = (due - now).total_seconds() / 60  # minutes until due (negative = overdue)

            # Pull REAL existing behavior — don't log fake entries
            features = get_user_risk_features(task['id'])

            # If no real behavior yet, use time-based defaults
            delay = max(0, int(-time_diff)) if time_diff < 0 else 0
            if all(f == 0 for f in features):
                features = [delay, 0, 0]

            risk, _ = predict_risk(*features)
            save_prediction(task['id'], risk)

            is_overdue = time_diff < 0

            # Determine per-task reminder interval (in minutes)
            if is_overdue:
                if risk == 'High':
                    interval = 1
                elif risk == 'Medium':
                    interval = 2
                else:
                    interval = 5
            else:
                # Widen the window: remind for tasks due within a few hours
                if risk == 'High' and time_diff <= 180:
                    interval = 2
                elif risk == 'Medium' and time_diff <= 120:
                    interval = 5
                elif risk == 'Low' and time_diff <= 60:
                    interval = 10
                elif time_diff <= 30:
                    # Any risk, if due within 30 minutes, remind
                    interval = 5
                else:
                    continue  # not close enough yet, skip

            task_id = task['id']
            last_time = _last_reminded.get(task_id)
            now_ts = datetime.now()

            if last_time is None or (now_ts - last_time).total_seconds() / 60 >= interval:
                send_notification(risk, task['title'])
                increment_reminder_count(task_id)
                _last_reminded[task_id] = now_ts
                logging.info(f"Reminder sent for '{task['title']}' — Risk: {risk} — Due in: {time_diff:.0f}min — Interval: {interval}min")

        except Exception as e:
            logging.warning(f"Reminder check error for task {task['id']}: {e}")


def start_reminder_daemon():
    def run():
        while True:
            try:
                check_and_remind()
            except Exception as e:
                logging.warning(f"Reminder daemon error: {e}")

            # The daemon ticks every 30 seconds so it can actually honour
            # the fine-grained per-task intervals (1-5 min).  The user-facing
            # "check_interval" setting is no longer used for the loop sleep;
            # it was causing a 5-minute gap that swallowed all reminders.
            time.sleep(30)

    thread = threading.Thread(target=run, daemon=True)
    thread.start()
    logging.info("Reminder daemon started (30s tick).")
