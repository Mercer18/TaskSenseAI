# -*- coding: utf-8 -*-
from datetime import datetime

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit,
    QTextEdit, QComboBox, QDateTimeEdit, QTableWidget, QTableWidgetItem,
    QHeaderView, QMessageBox, QDialog, QFrame, QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt, QDateTime
from PyQt6.QtGui import QFont, QColor

from tasksenseai.modules.task_manager import (
    add_task, get_all_tasks, update_task_status, delete_task
)
from tasksenseai.modules.ai_engine import predict_risk, save_prediction, get_prediction_for_task
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
            QLabel  { color: #cdd6f4; font-size: 12px; }
        """)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(14)
        layout.setContentsMargins(24, 24, 24, 24)

        # Title
        header_text = "✏️  Edit Task" if self.task else "✨  Create New Task"
        header = QLabel(header_text)
        header.setFont(QFont("Segoe UI", 15, QFont.Weight.Bold))
        header.setStyleSheet("color: #cba6f7; margin-bottom: 6px;")
        layout.addWidget(header)

        # Task title
        layout.addWidget(QLabel("Task Title *"))
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("What do you need to do?")
        if self.task:
            self.title_input.setText(self.task['title'])
        layout.addWidget(self.title_input)

        # Description
        layout.addWidget(QLabel("Description"))
        self.desc_input = QTextEdit()
        self.desc_input.setPlaceholderText("Additional details (optional)...")
        self.desc_input.setMaximumHeight(80)
        if self.task and self.task.get('description'):
            self.desc_input.setText(self.task['description'])
        layout.addWidget(self.desc_input)

        # Due date
        layout.addWidget(QLabel("Due Date & Time"))
        self.due_date = QDateTimeEdit()
        if self.task and self.task.get('due_date'):
            try:
                dt = QDateTime.fromString(self.task['due_date'], Qt.DateFormat.ISODate)
                if not dt.isValid():
                    dt = QDateTime.fromString(self.task['due_date'], "yyyy-MM-dd HH:mm")
                self.due_date.setDateTime(dt if dt.isValid() else QDateTime.currentDateTime())
            except:
                self.due_date.setDateTime(QDateTime.currentDateTime())
        else:
            self.due_date.setDateTime(QDateTime.currentDateTime())
        self.due_date.setDisplayFormat("yyyy-MM-dd HH:mm")
        self.due_date.setCalendarPopup(True)
        layout.addWidget(self.due_date)

        # Priority + Status row
        row = QHBoxLayout()

        left = QVBoxLayout()
        left.addWidget(QLabel("Priority"))
        self.priority = QComboBox()
        self.priority.addItems(["Low", "Medium", "High"])
        self.priority.setCurrentText(self.task['priority'] if self.task else "Medium")
        left.addWidget(self.priority)
        row.addLayout(left)

        right = QVBoxLayout()
        right.addWidget(QLabel("Status"))
        self.status = QComboBox()
        self.status.addItems(["Pending", "In Progress", "Completed"])
        self.status.setCurrentText(self.task['status'] if self.task else "Pending")
        right.addWidget(self.status)
        row.addLayout(right)

        layout.addLayout(row)

        # Buttons
        btn_row = QHBoxLayout()
        btn_row.setSpacing(12)

        cancel = QPushButton("Cancel")
        cancel.setFixedHeight(40)
        cancel.setStyleSheet("""
            QPushButton { background-color: #313244; color: #cdd6f4; border: none;
                          border-radius: 8px; padding: 0 24px; font-size: 12px; }
            QPushButton:hover { background-color: #45475a; }
        """)
        cancel.clicked.connect(self.reject)

        save = QPushButton("💾  Save Task")
        save.setFixedHeight(40)
        save.setStyleSheet("""
            QPushButton { background-color: #cba6f7; color: #11111b; border: none;
                          border-radius: 8px; padding: 0 24px; font-size: 12px; font-weight: bold; }
            QPushButton:hover { background-color: #d4b6ff; }
        """)
        save.clicked.connect(self.save_task)

        btn_row.addWidget(cancel)
        btn_row.addWidget(save)
        layout.addLayout(btn_row)

    def save_task(self):
        title = self.title_input.text().strip()
        if not title:
            QMessageBox.warning(self, "Error", "Task title is required!")
            return
        self.result_data = {
            'title':       title,
            'description': self.desc_input.toPlainText().strip(),
            'due_date':    self.due_date.dateTime().toString("yyyy-MM-ddTHH:mm:00"),
            'priority':    self.priority.currentText(),
            'status':      self.status.currentText(),
        }
        self.accept()


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

        # ── Header ──
        header = QHBoxLayout()
        title = QLabel("📋  Task Manager")
        title.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        title.setStyleSheet("color: #cdd6f4;")

        add_btn = QPushButton("＋  New Task")
        add_btn.setFixedHeight(40)
        add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        add_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 #cba6f7, stop:1 #89b4fa);
                color: #11111b; border: none; border-radius: 10px;
                padding: 0 24px; font-size: 12px; font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 #d4b6ff, stop:1 #a0c4ff);
            }
        """)
        add_btn.clicked.connect(self.open_add_task)

        header.addWidget(title)
        header.addStretch()
        header.addWidget(add_btn)
        layout.addLayout(header)

        # ── Filter bar ──
        filter_bar = QHBoxLayout()
        filter_bar.setSpacing(12)

        search_icon = QLabel("🔍")
        search_icon.setStyleSheet("color: #585b70; font-size: 14px;")
        filter_bar.addWidget(search_icon)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search tasks...")
        self.search_input.setFixedHeight(36)
        self.search_input.textChanged.connect(self.load_tasks)
        filter_bar.addWidget(self.search_input, 3)

        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["All Tasks", "Pending", "In Progress", "Completed"])
        self.filter_combo.setFixedHeight(36)
        self.filter_combo.currentTextChanged.connect(self.load_tasks)
        filter_bar.addWidget(self.filter_combo, 1)

        layout.addLayout(filter_bar)

        # ── Task count ──
        self.count_label = QLabel("")
        self.count_label.setStyleSheet("color: #585b70; font-size: 11px;")
        layout.addWidget(self.count_label)

        # ── Table ──
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(
            ["ID", "Title", "Priority", "Due Date", "Status", "Risk", "Actions"]
        )
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSortingEnabled(True)
        self.table.setShowGrid(False)
        self.table.verticalHeader().setDefaultSectionSize(48)
        layout.addWidget(self.table)

        self.load_tasks()

    # ─── CRUD ─────────────────────────────────────────
    def open_add_task(self):
        dlg = TaskDialog(self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            d = dlg.result_data
            add_task(d['title'], d['description'], d['due_date'], d['priority'])
            self.load_tasks()
            if self.refresh_callback:
                self.refresh_callback()
            QMessageBox.information(self, "Success", "Task added successfully!")

    def edit_task(self, task):
        from tasksenseai.modules.task_manager import update_task
        dlg = TaskDialog(self, task=task)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            d = dlg.result_data
            update_task(task['id'], d['title'], d['description'],
                        d['due_date'], d['priority'], d['status'])
            self.load_tasks()
            if self.refresh_callback:
                self.refresh_callback()

    def delete_task(self, task_id):
        reply = QMessageBox.question(
            self, 'Delete Task', 'Are you sure you want to delete this task?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            delete_task(task_id)
            self.load_tasks()
            if self.refresh_callback:
                self.refresh_callback()

    # ─── Table loader ─────────────────────────────────
    def load_tasks(self):
        filt = self.filter_combo.currentText() if hasattr(self, 'filter_combo') else "All Tasks"
        search = self.search_input.text().strip().lower() if hasattr(self, 'search_input') else ""

        tasks = get_all_tasks()
        if filt != "All Tasks":
            tasks = [t for t in tasks if t['status'] == filt]
        if search:
            tasks = [t for t in tasks
                     if search in t['title'].lower()
                     or search in (t.get('description') or '').lower()]

        self.count_label.setText(f"Showing {len(tasks)} task{'s' if len(tasks) != 1 else ''}")

        self.table.setSortingEnabled(False)
        self.table.setRowCount(len(tasks))

        RISK_CLR = {'Low': '#a6e3a1', 'Medium': '#f9e2af', 'High': '#f38ba8'}
        PRIO_CLR = {'Low': '#a6e3a1', 'Medium': '#f9e2af', 'High': '#f38ba8'}
        STAT_CLR = {'Pending': '#f9e2af', 'Completed': '#a6e3a1', 'In Progress': '#89b4fa'}

        for row, task in enumerate(tasks):
            # ID
            id_item = QTableWidgetItem(str(task['id']))
            id_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 0, id_item)

            # Title
            self.table.setItem(row, 1, QTableWidgetItem(task['title']))

            # Priority  (with dot indicator)
            pri = task['priority']
            pri_item = QTableWidgetItem(f"● {pri}")
            pri_item.setForeground(QColor(PRIO_CLR.get(pri, '#cdd6f4')))
            self.table.setItem(row, 2, pri_item)

            # Due date
            due_str = task.get('due_date', '') or ''
            if due_str:
                due_str = due_str.replace("T", " ")[:16]
            self.table.setItem(row, 3, QTableWidgetItem(due_str or 'No date'))

            # Status  (with colour)
            stat = task['status']
            stat_item = QTableWidgetItem(stat)
            stat_item.setForeground(QColor(STAT_CLR.get(stat, '#cdd6f4')))
            self.table.setItem(row, 4, stat_item)

            # Risk
            pred = get_prediction_for_task(task['id'])
            risk = pred['risk_level'] if pred else 'N/A'
            risk_item = QTableWidgetItem(risk)
            risk_item.setForeground(QColor(RISK_CLR.get(risk, '#585b70')))
            self.table.setItem(row, 5, risk_item)

            # Action buttons
            aw = QWidget()
            aw.setStyleSheet("background: transparent;")
            al = QHBoxLayout(aw)
            al.setContentsMargins(6, 4, 6, 4)
            al.setSpacing(8)

            for icon, tip, style, handler in [
                ("✅", "Complete", "background:#2a3a2e; color:#a6e3a1;",
                 lambda _, tid=task['id']: self.mark_complete(tid)),
                ("✏️", "Edit",     "background:#2e2a1e; color:#f9e2af;",
                 lambda _, t=task: self.edit_task(t)),
                ("🗑", "Delete",   "background:#2e1a1e; color:#f38ba8;",
                 lambda _, tid=task['id']: self.delete_task(tid)),
            ]:
                btn = QPushButton(icon)
                btn.setFixedSize(38, 32)
                btn.setToolTip(tip)
                btn.setCursor(Qt.CursorShape.PointingHandCursor)
                btn.setStyleSheet(f"""
                    QPushButton {{ {style} border-radius: 8px; font-size: 14px; border: none; }}
                    QPushButton:hover {{ border: 1px solid #585b70; }}
                """)
                btn.clicked.connect(handler)
                al.addWidget(btn)

            self.table.setCellWidget(row, 6, aw)

            # Row highlight for overdue / soon
            if task.get('due_date') and stat != 'Completed':
                try:
                    due = datetime.fromisoformat(task['due_date'])
                    diff = (due - datetime.now()).total_seconds() / 60
                    bg = None
                    if diff < 0:
                        bg = QColor('#2e1a1a')
                    elif diff < 120:
                        bg = QColor('#2e281a')
                    if bg:
                        for c in range(6):
                            it = self.table.item(row, c)
                            if it:
                                it.setBackground(bg)
                except:
                    pass

        self.table.setSortingEnabled(True)
        self.table.resizeColumnsToContents()
        self.table.setColumnWidth(0, 50)
        self.table.setColumnWidth(1, 220)
        self.table.setColumnWidth(6, 160)

    # ─── Mark Complete (with personality) ─────────────
    def mark_complete(self, task_id):
        from tasksenseai.modules.task_manager import get_task_by_id

        task = get_task_by_id(task_id)
        delay = 0
        time_status = 'on_time'

        if task and task.get('due_date'):
            try:
                due = datetime.fromisoformat(task['due_date'])
                diff = (datetime.now() - due).total_seconds() / 60
                if diff > 5:
                    time_status = 'late'
                    delay = int(diff)
                elif diff < -30:
                    time_status = 'early'
            except:
                pass

        pred = get_prediction_for_task(task_id)
        risk = pred['risk_level'] if pred else 'Low'

        log_behavior(task_id, delay, 0, 30)
        update_task_status(task_id, 'Completed')

        messages = {
            ('High', 'early'):   "🤯 WAIT — You finished EARLY on a HIGH RISK task?!\nLEGENDARY move! Nobody saw this coming!",
            ('High', 'on_time'): "🔥 You actually did it ON TIME?!\nWe didn't see that coming — but WE LOVE IT!",
            ('High', 'late'):    "😮‍💨 FINALLY! Better late than never!\nThe procrastination monster lost today.",
            ('Medium', 'early'): "⚡ Ahead of schedule? That's growth!\nYou're leveling up, keep it going!",
            ('Medium', 'on_time'): "💪 Solid work! Right on schedule.\nConsistency is what separates winners from wishers.",
            ('Medium', 'late'):  "😤 Cutting it close, weren't you?\nYou got there though. Next time, less suspense!",
            ('Low', 'early'):    "🏆 Look at you being productive!\nYour future self just did a happy dance.",
            ('Low', 'on_time'):  "✅ Clean execution. Task done, no drama.\nThis is how it's supposed to go!",
            ('Low', 'late'):     "🙄 Really? Even a low-risk task got delayed?\nBut hey — you still finished it. Tomorrow we do better!",
        }

        msg = messages.get((risk, time_status),
                           "🎉 Task Complete!\nEvery completed task is a step forward!")

        QMessageBox.information(self, "Task Completed! 🎯", msg)
        self.load_tasks()
        if self.refresh_callback:
            self.refresh_callback()
