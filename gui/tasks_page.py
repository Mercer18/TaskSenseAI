import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                              QLabel, QLineEdit, QTextEdit, QComboBox,
                              QDateTimeEdit, QTableWidget, QTableWidgetItem,
                              QHeaderView, QMessageBox, QDialog, QFrame)
from PyQt6.QtCore import Qt, QDateTime
from PyQt6.QtGui import QFont, QColor
from modules.task_manager import add_task, get_all_tasks, update_task_status, delete_task
from modules.ai_engine import predict_risk, save_prediction
from modules.behavior_tracker import log_behavior

class AddTaskDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add New Task")
        self.setMinimumWidth(450)
        self.setStyleSheet("""
            QDialog {
                background-color: #1e1e2e;
            }
            QLabel {
                color: #cdd6f4;
                font-size: 12px;
            }
            QLineEdit, QTextEdit, QComboBox, QDateTimeEdit {
                background-color: #313244;
                color: #cdd6f4;
                border: 1px solid #45475a;
                border-radius: 6px;
                padding: 8px;
                font-size: 12px;
            }
            QLineEdit:focus, QTextEdit:focus {
                border: 1px solid #cba6f7;
            }
        """)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)

        title = QLabel("✨ Create New Task")
        title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        title.setStyleSheet("color: #cba6f7; margin-bottom: 10px;")
        layout.addWidget(title)

        # Title
        layout.addWidget(QLabel("Task Title *"))
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Enter task title...")
        layout.addWidget(self.title_input)

        # Description
        layout.addWidget(QLabel("Description"))
        self.desc_input = QTextEdit()
        self.desc_input.setPlaceholderText("Enter description (optional)...")
        self.desc_input.setMaximumHeight(80)
        layout.addWidget(self.desc_input)

        # Due Date
        layout.addWidget(QLabel("Due Date & Time"))
        self.due_date = QDateTimeEdit()
        self.due_date.setDateTime(QDateTime.currentDateTime())
        self.due_date.setDisplayFormat("yyyy-MM-dd HH:mm")
        self.due_date.setCalendarPopup(True)
        layout.addWidget(self.due_date)

        # Priority
        layout.addWidget(QLabel("Priority"))
        self.priority = QComboBox()
        self.priority.addItems(["Low", "Medium", "High"])
        self.priority.setCurrentText("Medium")
        layout.addWidget(self.priority)

        # Buttons
        btn_layout = QHBoxLayout()
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #45475a;
                color: #cdd6f4;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-size: 12px;
            }
            QPushButton:hover { background-color: #585b70; }
        """)
        cancel_btn.clicked.connect(self.reject)

        save_btn = QPushButton("✅ Save Task")
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #cba6f7;
                color: #1e1e2e;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #d0b4f7; }
        """)
        save_btn.clicked.connect(self.save_task)

        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(save_btn)
        layout.addLayout(btn_layout)

    def save_task(self):
        title = self.title_input.text().strip()
        if not title:
            QMessageBox.warning(self, "Error", "Task title is required!")
            return
        desc = self.desc_input.toPlainText().strip()
        due = self.due_date.dateTime().toString("yyyy-MM-dd HH:mm")
        priority = self.priority.currentText()
        self.result_data = {
            'title': title,
            'description': desc,
            'due_date': due,
            'priority': priority
        }
        self.accept()


class TasksPage(QWidget):
    def __init__(self, refresh_callback=None):
        super().__init__()
        self.refresh_callback = refresh_callback
        self.setStyleSheet("background-color: #1e1e2e;")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(15)

        # Header
        header = QHBoxLayout()
        title = QLabel("📋 Task Manager")
        title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        title.setStyleSheet("color: #cdd6f4;")

        add_btn = QPushButton("+ Add New Task")
        add_btn.setFixedHeight(38)
        add_btn.setStyleSheet("""
            QPushButton {
                background-color: #cba6f7;
                color: #1e1e2e;
                border: none;
                border-radius: 8px;
                padding: 0 20px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #d0b4f7; }
        """)
        add_btn.clicked.connect(self.open_add_task)

        header.addWidget(title)
        header.addStretch()
        header.addWidget(add_btn)
        layout.addLayout(header)

        # Filter bar
        filter_layout = QHBoxLayout()
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["All Tasks", "Pending", "Completed", "In Progress"])
        self.filter_combo.setStyleSheet("""
            QComboBox {
                background-color: #313244;
                color: #cdd6f4;
                border: 1px solid #45475a;
                border-radius: 6px;
                padding: 6px 12px;
                font-size: 12px;
            }
        """)
        self.filter_combo.currentTextChanged.connect(self.load_tasks)
        filter_layout.addWidget(QLabel("Filter:"))
        filter_layout.addWidget(self.filter_combo)
        filter_layout.addStretch()

        filter_label = QLabel("Filter:")
        filter_label.setStyleSheet("color: #cdd6f4;")
        layout.addLayout(filter_layout)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["ID", "Title", "Priority", "Due Date", "Status", "Risk", "Actions"])
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #181825;
                color: #cdd6f4;
                border: none;
                border-radius: 8px;
                gridline-color: #313244;
                font-size: 12px;
            }
            QTableWidget::item {
                padding: 8px;
            }
            QTableWidget::item:selected {
                background-color: #313244;
            }
            QHeaderView::section {
                background-color: #313244;
                color: #cba6f7;
                padding: 8px;
                border: none;
                font-weight: bold;
            }
        """)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        layout.addWidget(self.table)

        self.load_tasks()

    def open_add_task(self):
        dialog = AddTaskDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.result_data
            task_id = add_task(data['title'], data['description'], data['due_date'], data['priority'])
            risk, confidence = predict_risk(0, 0, 0)
            save_prediction(task_id, risk)
            self.load_tasks()
            if self.refresh_callback:
                self.refresh_callback()
            QMessageBox.information(self, "Success", f"Task added! Initial risk: {risk}")

    def load_tasks(self):
        filter_text = self.filter_combo.currentText() if hasattr(self, 'filter_combo') else "All Tasks"
        tasks = get_all_tasks()

        if filter_text != "All Tasks":
            tasks = [t for t in tasks if t['status'] == filter_text]

        self.table.setRowCount(len(tasks))

        risk_colors = {'Low': '#a6e3a1', 'Medium': '#f9e2af', 'High': '#f38ba8'}

        for row, task in enumerate(tasks):
            self.table.setItem(row, 0, QTableWidgetItem(str(row + 1)))
            self.table.setItem(row, 1, QTableWidgetItem(task['title']))

            priority_item = QTableWidgetItem(task['priority'])
            priority_colors = {'Low': '#a6e3a1', 'Medium': '#f9e2af', 'High': '#f38ba8'}
            priority_item.setForeground(QColor(priority_colors.get(task['priority'], '#cdd6f4')))
            self.table.setItem(row, 2, priority_item)

            self.table.setItem(row, 3, QTableWidgetItem(task['due_date'] or 'No date'))

            status_item = QTableWidgetItem(task['status'])
            status_colors = {'Pending': '#f9e2af', 'Completed': '#a6e3a1', 'In Progress': '#89b4fa'}
            status_item.setForeground(QColor(status_colors.get(task['status'], '#cdd6f4')))
            self.table.setItem(row, 4, status_item)

            # Risk column
            from modules.ai_engine import get_prediction_for_task
            pred = get_prediction_for_task(task['id'])
            risk = pred['risk_level'] if pred else 'N/A'
            risk_item = QTableWidgetItem(risk)
            risk_item.setForeground(QColor(risk_colors.get(risk, '#cdd6f4')))
            self.table.setItem(row, 5, risk_item)

            # Action buttons
            action_widget = QWidget()
            action_layout = QHBoxLayout(action_widget)
            action_layout.setContentsMargins(4, 2, 4, 2)
            action_layout.setSpacing(4)

            complete_btn = QPushButton("✅")
            complete_btn.setFixedSize(30, 26)
            complete_btn.setToolTip("Mark Complete")
            complete_btn.setStyleSheet("QPushButton { background-color: #a6e3a1; border-radius: 4px; } QPushButton:hover { background-color: #b9f0b4; }")
            complete_btn.clicked.connect(lambda _, tid=task['id']: self.mark_complete(tid))

            delete_btn = QPushButton("🗑")
            delete_btn.setFixedSize(30, 26)
            delete_btn.setToolTip("Delete Task")
            delete_btn.setStyleSheet("QPushButton { background-color: #f38ba8; border-radius: 4px; } QPushButton:hover { background-color: #f5a0b5; }")
            delete_btn.clicked.connect(lambda _, tid=task['id']: self.delete_task(tid))

            action_layout.addWidget(complete_btn)
            action_layout.addWidget(delete_btn)
            self.table.setCellWidget(row, 6, action_widget)

        self.table.resizeColumnsToContents()
        self.table.setColumnWidth(1, 200)

    def mark_complete(self, task_id):
        from datetime import datetime
        from modules.task_manager import get_task_by_id
        from modules.ai_engine import get_prediction_for_task
        import random

        task = get_task_by_id(task_id)
        delay = 0
        time_status = 'on_time'

        if task and task.get('due_date'):
            try:
                due = datetime.fromisoformat(task['due_date'])
                now = datetime.now()
                diff = (now - due).total_seconds() / 60
                if diff > 5:
                    time_status = 'late'
                    delay = int(diff)
                elif diff < -30:
                    time_status = 'early'
                    delay = 0
                else:
                    time_status = 'on_time'
                    delay = 0
            except:
                delay = 0

        # Get risk level
        pred = get_prediction_for_task(task_id)
        risk = pred['risk_level'] if pred else 'Low'

        log_behavior(task_id, delay, 0, 30)
        update_task_status(task_id, 'Completed')

        # Message matrix
        messages = {
            ('High', 'early'): (
                "🤯 WAIT— You finished EARLY?! On a HIGH RISK task?!\n"
                "Nobody saw this coming. You just rewrote your own story. LEGENDARY!"
            ),
            ('High', 'on_time'): (
                "🔥 YOOO you actually did it ON TIME?!\n"
                "We didn't see that coming — but WE LOVE IT. Keep proving us wrong!"
            ),
            ('High', 'late'): (
                "😮‍💨 FINALLY! Better late than never, but let's not make this a habit!\n"
                "The procrastination monster lost today. Don't feed it tomorrow."
            ),
            ('Medium', 'early'): (
                "⚡ Ahead of schedule on a medium risk task?\n"
                "That's not just good — that's growth. You're leveling up!"
            ),
            ('Medium', 'on_time'): (
                "💪 Solid work! Right on schedule.\n"
                "Consistency is what separates winners from wishers. Stay on it!"
            ),
            ('Medium', 'late'): (
                "😤 Cutting it close weren't you?\n"
                "You got there though. Next time let's not make it a thriller!"
            ),
            ('Low', 'early'): (
                "🏆 Look at you being all productive!\n"
                "Your future self just did a happy dance. Keep this energy!"
            ),
            ('Low', 'on_time'): (
                "✅ Clean execution. Task done, no drama.\n"
                "This is how it's supposed to go. Build on this!"
            ),
            ('Low', 'late'): (
                "🙄 Really? Even a low risk task got delayed?\n"
                "But hey — you still finished it. Tomorrow we do better, deal?"
            ),
        }

        msg = messages.get((risk, time_status), 
            "🎉 Task Complete!\nEvery completed task is a step forward. Keep going!")

        QMessageBox.information(self, "Task Completed! 🎯", msg)

        self.load_tasks()
        if self.refresh_callback:
            self.refresh_callback()

    def delete_task(self, task_id):
        reply = QMessageBox.question(self, 'Delete Task', 'Are you sure you want to delete this task?',
                                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            delete_task(task_id)
            self.load_tasks()
            if self.refresh_callback:
                self.refresh_callback()


