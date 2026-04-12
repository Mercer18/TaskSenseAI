import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QScrollArea)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont
from modules.task_manager import get_task_stats, get_pending_tasks
from modules.ai_engine import get_prediction_for_task

class StatCard(QFrame):
    def __init__(self, title, value, color, emoji):
        super().__init__()
        self.setFixedHeight(100)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: #181825;
                border-radius: 12px;
                border-left: 4px solid {color};
            }}
        """)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(6)

        # Emoji + value on same line
        top_row = QHBoxLayout()
        top_row.setSpacing(10)

        emoji_label = QLabel(emoji)
        emoji_label.setFont(QFont("Segoe UI Emoji", 18))
        emoji_label.setFixedWidth(32)
        emoji_label.setStyleSheet("color: white; border: none; background: transparent;")

        value_label = QLabel(str(value))
        value_label.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        value_label.setStyleSheet(f"color: {color}; border: none; background: transparent;")

        top_row.addWidget(emoji_label)
        top_row.addWidget(value_label)
        top_row.addStretch()
        layout.addLayout(top_row)

        # Title below
        title_label = QLabel(title)
        title_label.setStyleSheet("color: #6c7086; font-size: 11px; border: none; background: transparent;")
        layout.addWidget(title_label)

class DashboardPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color: #1e1e2e;")
        self.init_ui()

        # Auto refresh every 30 seconds
        self.timer = QTimer()
        self.timer.timeout.connect(self.refresh)
        self.timer.start(15000)

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(20)

        # Header
        header = QHBoxLayout()
        title = QLabel("🏠 Dashboard")
        title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        title.setStyleSheet("color: #cdd6f4;")
        subtitle = QLabel("Welcome back! Here's your productivity overview.")
        subtitle.setStyleSheet("color: #6c7086; font-size: 12px;")
        header.addWidget(title)
        header.addStretch()
        layout.addLayout(header)
        layout.addWidget(subtitle)

        # Stats cards
        stats = get_task_stats()
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(15)

        cards_data = [
            ("Total Tasks", stats['total'], "#89b4fa", "📋"),
            ("Pending", stats['pending'], "#f9e2af", "⏳"),
            ("Completed", stats['completed'], "#a6e3a1", "✅"),
            ("Completion Rate",
             f"{int((stats['completed']/stats['total']*100) if stats['total'] > 0 else 0)}%",
             "#cba6f7", "📈"),
        ]

        for title_text, value, color, emoji in cards_data:
            card = StatCard(title_text, value, color, emoji)
            cards_layout.addWidget(card)

        layout.addLayout(cards_layout)

        # Pending tasks with risk
        pending_title = QLabel("⚡ Pending Tasks & Risk Levels")
        pending_title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        pending_title.setStyleSheet("color: #cdd6f4; margin-top: 10px;")
        layout.addWidget(pending_title)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")

        scroll_content = QWidget()
        scroll_content.setStyleSheet("background-color: transparent;")
        self.tasks_layout = QVBoxLayout(scroll_content)
        self.tasks_layout.setSpacing(8)
        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)

        self.load_pending_tasks()

    def load_pending_tasks(self):
        # Clear existing
        while self.tasks_layout.count():
            item = self.tasks_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        tasks = get_pending_tasks()
        risk_colors = {'Low': '#a6e3a1', 'Medium': '#f9e2af', 'High': '#f38ba8', 'N/A': '#6c7086'}
        risk_bg = {'Low': '#1e3a2f', 'Medium': '#3a2e1e', 'High': '#3a1e1e', 'N/A': '#24273a'}

        if not tasks:
            empty = QLabel("🎉 No pending tasks! You're all caught up.")
            empty.setStyleSheet("color: #a6e3a1; font-size: 13px; padding: 20px;")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.tasks_layout.addWidget(empty)
            return

        for task in tasks[:10]:
            pred = get_prediction_for_task(task['id'])
            risk = pred['risk_level'] if pred else 'N/A'

            card = QFrame()
            card.setStyleSheet(f"""
                QFrame {{
                    background-color: {risk_bg.get(risk, '#181825')};
                    border-radius: 8px;
                    border: 2px solid {risk_colors.get(risk, '#6c7086')};
                }}
            """)
            card_layout = QHBoxLayout(card)
            card_layout.setContentsMargins(15, 10, 15, 10)

            task_title = QLabel(task['title'])
            task_title.setStyleSheet("color: #cdd6f4; font-size: 12px; font-weight: bold; border: none; background: transparent;")

            due_label = QLabel(f"Due: {task['due_date'] or 'No date'}")
            due_label.setStyleSheet("color: #6c7086; font-size: 11px; border: none; background: transparent;")

            risk_label = QLabel(f"Risk: {risk}")
            risk_label.setStyleSheet(f"color: {risk_colors.get(risk, '#6c7086')}; font-size: 11px; font-weight: bold; border: none; background: transparent;")

            card_layout.addWidget(task_title)
            card_layout.addStretch()
            card_layout.addWidget(due_label)
            card_layout.addWidget(risk_label)

            self.tasks_layout.addWidget(card)

        self.tasks_layout.addStretch()

    def refresh(self):
        # Remove all widgets from existing layout
        layout = self.layout()
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                while item.layout().count():
                    nested = item.layout().takeAt(0)
                    if nested.widget():
                        nested.widget().deleteLater()
        
        # Rebuild stats cards
        stats = get_task_stats()
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(15)

        cards_data = [
            ("Total Tasks", stats['total'], "#89b4fa", "📋"),
            ("Pending", stats['pending'], "#f9e2af", "⏳"),
            ("Completed", stats['completed'], "#a6e3a1", "✅"),
            ("Completion Rate",
            f"{int((stats['completed']/stats['total']*100) if stats['total'] > 0 else 0)}%",
            "#cba6f7", "📈"),
        ]

        # Re-add header
        title = QLabel("🏠 Dashboard")
        title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        title.setStyleSheet("color: #cdd6f4;")
        layout.addWidget(title)

        subtitle = QLabel("Welcome back! Here's your productivity overview.")
        subtitle.setStyleSheet("color: #6c7086; font-size: 12px;")
        layout.addWidget(subtitle)

        for title_text, value, color, emoji in cards_data:
            card = StatCard(title_text, value, color, emoji)
            cards_layout.addWidget(card)
        layout.addLayout(cards_layout)

        # Re-add pending title
        pending_title = QLabel("⚡ Pending Tasks & Risk Levels")
        pending_title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        pending_title.setStyleSheet("color: #cdd6f4; margin-top: 10px;")
        layout.addWidget(pending_title)

        # Re-add scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
        scroll_content = QWidget()
        scroll_content.setStyleSheet("background-color: transparent;")
        self.tasks_layout = QVBoxLayout(scroll_content)
        self.tasks_layout.setSpacing(8)
        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)

        self.load_pending_tasks()