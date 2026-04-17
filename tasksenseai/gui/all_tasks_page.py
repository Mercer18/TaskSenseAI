# -*- coding: utf-8 -*-
from datetime import datetime
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QComboBox, QTableWidget, QTableWidgetItem, QHeaderView, QFrame
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor

from tasksenseai.modules.task_manager import get_all_tasks
from tasksenseai.modules.ai_engine import get_prediction_for_task

class AllTasksPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color: #11111b;")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 28, 30, 20)
        layout.setSpacing(16)

        # Header
        header = QVBoxLayout()
        title = QLabel("Task Vault")
        title.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        title.setStyleSheet("color: #cdd6f4;")
        header.addWidget(title)

        sub = QLabel("Master Ledger — Full spreadsheet view of all task entries")
        sub.setStyleSheet("color: #6c7086; font-size: 12px;")
        header.addWidget(sub)
        layout.addLayout(header)

        # Divider
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet("color: #313244;")
        layout.addWidget(line)

        # Filter bar
        filter_bar = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search master list...")
        self.search_input.setFixedHeight(36)
        self.search_input.textChanged.connect(self.load_tasks)
        filter_bar.addWidget(self.search_input, 3)

        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["All Tasks", "Pending", "Completed"])
        self.filter_combo.setFixedHeight(36)
        self.filter_combo.currentTextChanged.connect(self.load_tasks)
        filter_bar.addWidget(self.filter_combo, 1)
        layout.addLayout(filter_bar)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "№", "Task Title", "Priority", "Due Date", "Status", "AI Risk", "Finished At", "Timing"
        ])
        
        # Styling for Excel-like density
        self.table.verticalHeader().setDefaultSectionSize(32) # Compact rows
        self.table.setShowGrid(True)
        self.table.setGridStyle(Qt.PenStyle.SolidLine)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch) # Title takes priority
        self.table.horizontalHeader().setMinimumSectionSize(50)
        
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #181825;
                color: #cdd6f4;
                gridline-color: #313244;
                border: 1px solid #313244;
                border-radius: 8px;
                font-size: 12px;
            }
            QTableWidget::item { padding: 5px; }
            QHeaderView::section {
                background-color: #1e1e2e;
                color: #cba6f7;
                padding: 8px;
                border: none;
                border-right: 1px solid #313244;
                border-bottom: 2px solid #313244;
                font-weight: bold;
            }
            QTableWidget::item:selected {
                background-color: #313244;
                color: #cba6f7;
            }
        """)
        
        layout.addWidget(self.table)
        
        self.count_lbl = QLabel("Total Entries: 0")
        self.count_lbl.setStyleSheet("color: #45475a; font-size: 11px;")
        layout.addWidget(self.count_lbl)

        self.load_tasks()

    def load_tasks(self):
        all_tasks = get_all_tasks()
        search = self.search_input.text().strip().lower()
        filt = self.filter_combo.currentText()

        # Filtering
        filtered = []
        for t in all_tasks:
            if search and search not in t['title'].lower(): continue
            if filt == "Pending" and t['status'] == 'Completed': continue
            if filt == "Completed" and t['status'] != 'Completed': continue
            filtered.append(t)

        # Hybrid Sorting: 
        # 1. Active tasks first, sorted by due date ASC (urgency)
        # 2. Completed tasks second, sorted by completed_at DESC (recency)
        active = [t for t in filtered if t['status'] != 'Completed']
        completed = [t for t in filtered if t['status'] == 'Completed']

        active.sort(key=lambda x: (x.get('due_date') or '9999-12-31', x['id']))
        completed.sort(key=lambda x: (x.get('completed_at') or '', x['id']), reverse=True)

        tasks = active + completed

        self.table.setRowCount(len(tasks))
        self.count_lbl.setText(f"Total Entries: {len(tasks)}")

        RISK_CLR = {'Low': '#a6e3a1', 'Medium': '#f9e2af', 'High': '#f38ba8'}
        STAT_CLR = {'Pending': '#f9e2af', 'Completed': '#a6e3a1', 'In Progress': '#89b4fa'}
        
        now = datetime.now()

        for row, t in enumerate(tasks):
            # Sequential No.
            id_item = QTableWidgetItem(str(row + 1))
            id_item.setToolTip(f"Internal ID: {t['id']}")
            id_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 0, id_item)

            # Title
            self.table.setItem(row, 1, QTableWidgetItem(t['title']))

            # Priority
            p_item = QTableWidgetItem(t['priority'])
            p_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 2, p_item)

            # Due Date
            due_str = t.get('due_date')
            due_disp = (due_str or '').replace('T', ' ')[:16] or '—'
            self.table.setItem(row, 3, QTableWidgetItem(due_disp))

            # Status
            s_item = QTableWidgetItem(t['status'])
            s_item.setForeground(QColor(STAT_CLR.get(t['status'], '#cdd6f4')))
            self.table.setItem(row, 4, s_item)

            # Risk
            pred = get_prediction_for_task(t['id'])
            risk = pred['risk_level'] if pred else 'N/A'
            r_item = QTableWidgetItem(risk)
            r_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            r_item.setForeground(QColor(RISK_CLR.get(risk, '#585b70')))
            self.table.setItem(row, 5, r_item)

            # Completed At
            fin_str = t.get('completed_at')
            fin_disp = (fin_str or '').replace('T', ' ')[:16] or '—'
            f_item = QTableWidgetItem(fin_disp)
            if not fin_str: f_item.setForeground(QColor('#45475a'))
            self.table.setItem(row, 6, f_item)

            # Timing / Performance Column
            timing_text = "—"
            timing_clr = "#45475a"

            if due_str:
                try:
                    due_dt = datetime.fromisoformat(due_str)
                    if t['status'] == 'Completed' and fin_str:
                        fin_dt = datetime.fromisoformat(fin_str)
                        diff = (fin_dt - due_dt).total_seconds() / 60
                        if diff <= 0:
                            timing_text = f"{self._fmt_m(abs(diff))} Early"
                            timing_clr = "#a6e3a1" # Green
                        else:
                            timing_text = f"{self._fmt_m(diff)} Late"
                            timing_clr = "#f38ba8" # Red
                    elif t['status'] != 'Completed':
                        diff = (due_dt - now).total_seconds() / 60
                        if diff < 0:
                            timing_text = f"Overdue {self._fmt_m(abs(diff))}"
                            timing_clr = "#f38ba8" # Red
                        else:
                            timing_text = f"{self._fmt_m(diff)} Left"
                            timing_clr = "#89b4fa" # Blue
                except: pass

            t_item = QTableWidgetItem(timing_text)
            t_item.setForeground(QColor(timing_clr))
            t_item.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
            self.table.setItem(row, 7, t_item)

    def _fmt_m(self, m):
        if m < 60: return f"{int(m)}m"
        if m < 1440: return f"{m/60:.1f}h"
        return f"{m/1440:.1f}d"
