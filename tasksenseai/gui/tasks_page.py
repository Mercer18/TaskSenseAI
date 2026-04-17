# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit,
    QTextEdit, QComboBox, QDateEdit, QTableWidget, QTableWidgetItem,
    QHeaderView, QMessageBox, QDialog, QFrame, QGraphicsDropShadowEffect, QScrollArea
)
from PyQt6.QtCore import Qt, QDateTime, QSize
from PyQt6.QtGui import QFont, QColor, QIcon, QPixmap

from tasksenseai.modules.task_manager import (
    add_task, get_all_tasks, update_task_status, delete_task, get_task_by_id, update_task
)
from tasksenseai.modules.ai_engine import get_prediction_for_task
from tasksenseai.modules.behavior_tracker import log_behavior


# ═══════════════════════════════════════════════════════════════
#  TASK DIALOG (Add / Edit)
# ═══════════════════════════════════════════════════════════════

class TaskDialog(QDialog):
    def __init__(self, parent=None, task=None):
        super().__init__(parent)
        self.task = task
        self.setWindowTitle("Edit Task" if task else "Add New Task")
        self.setMinimumWidth(480)
        self.setStyleSheet("""
            QDialog { background-color: #1e1e2e; }
            QLabel  { color: #cdd6f4; font-size: 12px; background: transparent; border: none; }
            QLineEdit, QTextEdit, QComboBox, QDateEdit {
                background-color: #181825; color: #cdd6f4; border: 1px solid #313244;
                border-radius: 8px; padding: 8px; font-size: 13px;
            }
            QLineEdit:focus, QTextEdit:focus, QComboBox:focus { border: 1px solid #cba6f7; }
        """)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(14)
        layout.setContentsMargins(24, 24, 24, 24)

        header_text = "Edit Task" if self.task else "Create New Task"
        header = QLabel(header_text)
        header.setFont(QFont("Segoe UI", 15, QFont.Weight.Bold))
        header.setStyleSheet("color: #cba6f7; margin-bottom: 6px;")
        layout.addWidget(header)

        layout.addWidget(QLabel("Task Title *"))
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("What do you need to do?")
        if self.task: self.title_input.setText(self.task['title'])
        layout.addWidget(self.title_input)

        layout.addWidget(QLabel("Description"))
        self.desc_input = QTextEdit()
        self.desc_input.setPlaceholderText("Additional details (optional)...")
        self.desc_input.setMaximumHeight(80)
        if self.task and self.task.get('description'): self.desc_input.setText(self.task['description'])
        layout.addWidget(self.desc_input)

        layout.addWidget(QLabel("Due Date & Time"))
        datetime_row = QHBoxLayout()
        datetime_row.setSpacing(12)

        self.due_date = QDateEdit()
        dt = QDateTime.currentDateTime()
        if self.task and self.task.get('due_date'):
            try:
                parsed_dt = QDateTime.fromString(self.task['due_date'], Qt.DateFormat.ISODate)
                if parsed_dt.isValid(): dt = parsed_dt
            except: pass
                
        self.due_date.setDate(dt.date())
        self.due_date.setDisplayFormat("MMMM d, yyyy")
        self.due_date.setCalendarPopup(True)
        
        self.due_time_btn = QPushButton()
        self.due_time_btn.setFixedHeight(36)
        self.due_time_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.due_time_btn.setStyleSheet("""
            QPushButton {
                background-color: #181825; color: #cdd6f4; border: 1px solid #313244;
                border-radius: 8px; padding: 0 16px; text-align: left; font-size: 13px; font-weight: bold;
            }
            QPushButton:hover, QPushButton:focus { border: 1px solid #cba6f7; }
        """)
        self.due_time_btn.clicked.connect(self.open_time_picker)
        
        self.selected_time = dt.time()
        self.due_time_btn.setText(self.selected_time.toString("HH:mm"))

        datetime_row.addWidget(self.due_date, 3)
        datetime_row.addWidget(self.due_time_btn, 2)
        layout.addLayout(datetime_row)

        row = QHBoxLayout()
        left = QVBoxLayout(); left.addWidget(QLabel("Priority"))
        self.priority = QComboBox(); self.priority.addItems(["Low", "Medium", "High"])
        self.priority.setCurrentText(self.task['priority'] if self.task else "Medium")
        left.addWidget(self.priority); row.addLayout(left)

        right = QVBoxLayout(); right.addWidget(QLabel("Status"))
        self.status = QComboBox(); self.status.addItems(["Pending", "In Progress", "Completed"])
        self.status.setCurrentText(self.task['status'] if self.task else "Pending")
        right.addWidget(self.status); row.addLayout(right)
        layout.addLayout(row)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(12)
        cancel = QPushButton("Cancel"); cancel.setFixedHeight(40)
        cancel.setStyleSheet("background-color: #313244; color: #cdd6f4; border-radius: 8px; border: none;")
        cancel.clicked.connect(self.reject)

        save = QPushButton("Save Task"); save.setFixedHeight(40)
        save.setStyleSheet("background: #cba6f7; color: #11111b; border-radius: 8px; border: none; font-weight: bold;")
        save.clicked.connect(self.save_task)

        btn_row.addWidget(cancel); btn_row.addWidget(save)
        layout.addLayout(btn_row)

    def open_time_picker(self):
        from tasksenseai.gui.custom_widgets import MaterialTimePicker
        picker = MaterialTimePicker(self, self.selected_time)
        if picker.exec() == QDialog.DialogCode.Accepted:
            self.selected_time = picker.get_time()
            self.due_time_btn.setText(self.selected_time.toString("HH:mm"))

    def save_task(self):
        title = self.title_input.text().strip()
        if not title: return
        due_date_str = self.due_date.date().toString("yyyy-MM-dd")
        due_time_str = self.selected_time.toString("HH:mm:00")
        combined_iso = f"{due_date_str}T{due_time_str}"
        self.result_data = {
            'title': title, 'description': self.desc_input.toPlainText().strip(),
            'due_date': combined_iso, 'priority': self.priority.currentText(), 'status': self.status.currentText()
        }
        self.accept()


# ═══════════════════════════════════════════════════════════════
#  TASK CARD WIDGET
# ═══════════════════════════════════════════════════════════════

class ModernTaskCard(QFrame):
    def __init__(self, task, on_complete, on_edit, on_delete):
        super().__init__()
        self.task = task
        self.on_complete = on_complete
        self.on_edit = on_edit
        self.on_delete = on_delete
        
        pred = get_prediction_for_task(task['id'])
        risk = pred['risk_level'] if pred else 'N/A'
        
        risk_colors = {'Low': '#a6e3a1', 'Medium': '#f9e2af', 'High': '#f38ba8', 'N/A': '#585b70'}
        self.setStyleSheet(f"""
            QFrame {{
                background-color: #1e1e2e;
                border-radius: 12px;
                border-left: 4px solid {risk_colors.get(risk, '#313244')};
            }}
            QLabel {{ background: transparent; border: none; }}
        """)
        self.setFixedHeight(85)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 0, 20, 0)
        
        # Title & Info
        info = QVBoxLayout()
        info.setSpacing(2)
        info.addStretch()
        
        title = QLabel(task['title'])
        title.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        title.setStyleSheet("color: #cdd6f4;")
        info.addWidget(title)
        
        meta = QHBoxLayout()
        meta.setSpacing(12)
        
        prio_clr = {'Low': '#a6e3a1', 'Medium': '#f9e2af', 'High': '#f38ba8'}.get(task['priority'], '#6c7086')
        prio = QLabel(f"● {task['priority']}")
        prio.setStyleSheet(f"color: {prio_clr}; font-size: 11px;")
        
        due_str = (task.get('due_date') or '').replace('T', ' ')[:16] or 'No date'
        due = QLabel(f"📅 {due_str}")
        due.setStyleSheet("color: #6c7086; font-size: 11px;")
        
        risk_lbl = QLabel(f"🤖 Risk: {risk}")
        risk_lbl.setStyleSheet(f"color: {risk_colors.get(risk, '#585b70')}; font-size: 11px; font-weight: bold;")
        
        meta.addWidget(prio); meta.addWidget(due); meta.addWidget(risk_lbl); meta.addStretch()
        info.addLayout(meta)
        info.addStretch()
        layout.addLayout(info, 1)
        
        # Actions
        actions = QHBoxLayout()
        actions.setSpacing(8)
        
        if task['status'] != 'Completed':
            done = QPushButton("✅")
            done.setFixedSize(36, 36)
            done.setToolTip("Complete")
            done.setCursor(Qt.CursorShape.PointingHandCursor)
            done.setStyleSheet("background: #2a3a2e; border-radius: 18px; border: none;")
            done.clicked.connect(lambda: on_complete(task['id']))
            actions.addWidget(done)
            
        edit = QPushButton("✏️")
        edit.setFixedSize(36, 36)
        edit.setToolTip("Edit")
        edit.setCursor(Qt.CursorShape.PointingHandCursor)
        edit.setStyleSheet("background: #2e2a1e; border-radius: 18px; border: none;")
        edit.clicked.connect(lambda: on_edit(task))
        actions.addWidget(edit)
        
        trash = QPushButton("🗑")
        trash.setFixedSize(36, 36)
        trash.setToolTip("Delete")
        trash.setCursor(Qt.CursorShape.PointingHandCursor)
        trash.setStyleSheet("background: #2e1a1e; border-radius: 18px; border: none;")
        trash.clicked.connect(lambda: on_delete(task['id']))
        actions.addWidget(trash)
        
        layout.addLayout(actions)


# ═══════════════════════════════════════════════════════════════
#  TASKS PAGE
# ═══════════════════════════════════════════════════════════════

class TasksPage(QWidget):
    def __init__(self, refresh_callback=None):
        super().__init__()
        self.refresh_callback = refresh_callback
        self.setStyleSheet("background-color: #11111b;")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 28, 30, 20)
        layout.setSpacing(16)

        header = QHBoxLayout()
        title = QLabel("Task Manager")
        title.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        title.setStyleSheet("color: #cdd6f4;")

        add_btn = QPushButton("+ New Task")
        add_btn.setFixedSize(140, 42)
        add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        add_btn.setStyleSheet("""
            QPushButton { background: #cba6f7; color: #11111b; border-radius: 10px; font-weight: bold; }
            QPushButton:hover { background: #d4b6ff; }
        """)
        add_btn.clicked.connect(self.open_add_task)

        header.addWidget(title); header.addStretch(); header.addWidget(add_btn)
        layout.addLayout(header)

        # Filters
        filter_bar = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Find a task...")
        self.search_input.setFixedHeight(38)
        self.search_input.textChanged.connect(self.load_tasks)
        filter_bar.addWidget(self.search_input, 3)

        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["All Focus", "Pending Only", "Completed"])
        self.filter_combo.setFixedHeight(38)
        self.filter_combo.currentTextChanged.connect(self.load_tasks)
        filter_bar.addWidget(self.filter_combo, 1)
        layout.addLayout(filter_bar)

        # Scoped Sections
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        self.scroll_content = QWidget()
        self.scroll_content.setStyleSheet("background: transparent;")
        self.list_layout = QVBoxLayout(self.scroll_content)
        self.list_layout.setSpacing(25)
        self.list_layout.setContentsMargins(0, 10, 10, 10)
        scroll.setWidget(self.scroll_content)
        layout.addWidget(scroll)

        self.load_tasks()

    def _add_section(self, title, tasks):
        if not tasks: return
        
        container = QVBoxLayout()
        header = QLabel(title)
        header.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        header.setStyleSheet("color: #6c7086; margin-bottom: 5px;")
        container.addWidget(header)
        
        for t in tasks:
            card = ModernTaskCard(t, self.mark_complete, self.edit_task, self.delete_task)
            container.addWidget(card)
        
        self.list_layout.addLayout(container)

    def load_tasks(self):
        # Clear current list
        while self.list_layout.count():
            item = self.list_layout.takeAt(0)
            if item.layout():
                # Correctly clear nested layouts
                while item.layout().count():
                    si = item.layout().takeAt(0)
                    if si.widget(): si.widget().deleteLater()
            elif item.widget():
                item.widget().deleteLater()

        all_tasks = get_all_tasks()
        search = self.search_input.text().strip().lower()
        filt = self.filter_combo.currentText()
        
        # Master Filter
        tasks = []
        for t in all_tasks:
            if search and search not in t['title'].lower(): continue
            if filt == "Pending Only" and t['status'] == 'Completed': continue
            if filt == "Completed" and t['status'] != 'Completed': continue
            tasks.append(t)

        # Partitioning
        today = datetime.now().date()
        backlog = []
        today_tasks = []
        upcoming = []
        completed = []
        
        for t in tasks:
            if t['status'] == 'Completed':
                completed.append(t)
                continue
            
            if not t.get('due_date'):
                today_tasks.append(t)
                continue
                
            try:
                due = datetime.fromisoformat(t['due_date']).date()
                if due < today:
                    backlog.append(t)
                elif due == today:
                    today_tasks.append(t)
                else:
                    upcoming.append(t)
            except:
                today_tasks.append(t)

        # Render sections
        self._add_section("🕒 From Yesterday (Backlog)", backlog)
        self._add_section("📅 Today's Focus", today_tasks)
        self._add_section("🚀 Upcoming", upcoming)
        self._add_section("✅ Recently Completed", completed[:10]) # Limiting completed for speed

        if not tasks:
            empty = QLabel("No tasks found. Time to relax! 🍹")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty.setStyleSheet("color: #585b70; font-size: 14px; margin-top: 50px;")
            self.list_layout.addWidget(empty)

        self.list_layout.addStretch()

    def open_add_task(self):
        dlg = TaskDialog(self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            d = dlg.result_data
            add_task(d['title'], d['description'], d['due_date'], d['priority'])
            self.load_tasks()
            if self.refresh_callback: self.refresh_callback()

    def edit_task(self, task):
        dlg = TaskDialog(self, task=task)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            d = dlg.result_data
            update_task(task['id'], d['title'], d['description'], d['due_date'], d['priority'], d['status'])
            self.load_tasks()
            if self.refresh_callback: self.refresh_callback()

    def delete_task(self, task_id):
        msg = QMessageBox(self)
        msg.setWindowTitle("Delete Task")
        msg.setText("Are you sure you want to delete this task?")
        msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if msg.exec() == int(QMessageBox.StandardButton.Yes):
            delete_task(task_id)
            self.load_tasks()
            if self.refresh_callback: self.refresh_callback()

    def mark_complete(self, task_id):
        task = get_task_by_id(task_id)
        if not task: return

        now = datetime.now()
        
        # 1. Calculate metrics for performance logging
        delay_min = 0
        if task.get('due_date'):
            try:
                due_dt = datetime.fromisoformat(task['due_date'])
                diff = (now - due_dt).total_seconds() / 60
                delay_min = int(max(0, diff))
            except: pass
            
        try:
            created_dt = datetime.fromisoformat(task['created_at'])
            complete_min = int((now - created_dt).total_seconds() / 60)
        except:
            complete_min = 0
        
        ignored = task.get('reminders_sent', 0)

        # 2. Log behavior for AI training
        log_behavior(task_id, delay_min, ignored, complete_min)

        # 3. Perform update
        update_task_status(task_id, 'Completed')
        self.load_tasks()
        if self.refresh_callback: self.refresh_callback()

        # 4. Show Feedback Message
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setWindowTitle("Task Completed! 🎉")
        
        if task.get('due_date'):
            try:
                due_dt = datetime.fromisoformat(task['due_date'])
                if now < due_dt:
                    saved = (due_dt - now).total_seconds() / 60
                    time_str = self._fmt_time(saved)
                    msg.setText(f"Great job! You finished '{task['title']}' {time_str} early! 🚀")
                else:
                    msg.setText(f"Success! Task '{task['title']}' is done. Better late than never! 💪")
            except:
                msg.setText(f"Success! Task '{task['title']}' has been moved to the Vault. ✅")
        else:
            msg.setText(f"Excellent! Task '{task['title']}' has been moved to the Vault. ✅")
            
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.exec()

    def _fmt_time(self, m):
        if m < 60: return f"{int(m)}m"
        if m < 1440: return f"{m/60:.1f}h"
        return f"{m/1440:.1f}d"
