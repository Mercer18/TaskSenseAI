import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                              QFrame, QScrollArea, QProgressBar)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from database.db_manager import get_connection
from modules.ai_engine import predict_risk
from modules.task_manager import get_all_tasks
from modules.ai_engine import get_prediction_for_task

class RiskCard(QFrame):
    def __init__(self, task_title, risk, confidence=None):
        super().__init__()
        risk_colors = {'Low': '#a6e3a1', 'Medium': '#f9e2af', 'High': '#f38ba8'}
        risk_bg = {'Low': '#1e3a2f', 'Medium': '#3a2e1e', 'High': '#3a1e1e'}
        risk_emoji = {'Low': '🟢', 'Medium': '🟡', 'High': '🔴'}
        color = risk_colors.get(risk, '#6c7086')
        bg = risk_bg.get(risk, '#181825')

        self.setStyleSheet(f"""
            QFrame {{
                background-color: {bg};
                border-radius: 10px;
                border: 2px solid {color};
            }}
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 12, 15, 12)
        layout.setSpacing(10)

        left = QVBoxLayout()
        left.setSpacing(4)

        title = QLabel(task_title)
        title.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        title.setStyleSheet("color: #cdd6f4; border: none; background: transparent;")
        left.addWidget(title)

        risk_label = QLabel(f"{risk_emoji.get(risk, '⚪')}  Risk Level: {risk}")
        risk_label.setStyleSheet(f"color: {color}; font-size: 11px; border: none; background: transparent;")
        left.addWidget(risk_label)

        layout.addLayout(left)
        layout.addStretch()

        if confidence:
            conf_label = QLabel(f"Confidence: {confidence}%")
            conf_label.setStyleSheet("color: #6c7086; font-size: 10px; border: none; background: transparent;")
            layout.addWidget(conf_label)


class AIInsightsPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color: #1e1e2e;")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(20)

        # Header
        title = QLabel("🤖 AI Insights")
        title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        title.setStyleSheet("color: #cdd6f4;")
        layout.addWidget(title)

        subtitle = QLabel("Procrastination risk analysis powered by Machine Learning")
        subtitle.setStyleSheet("color: #6c7086; font-size: 12px;")
        layout.addWidget(subtitle)

        # Model info card
        model_card = QFrame()
        model_card.setStyleSheet("""
            QFrame {
                background-color: #181825;
                border-radius: 10px;
                border: 1px solid #313244;
            }
        """)
        model_layout = QHBoxLayout(model_card)
        model_layout.setContentsMargins(20, 15, 20, 15)

        model_info = [
            ("🧠 Model", "Random Forest Classifier"),
            ("🎯 Accuracy", "96%"),
            ("📊 Training Data", "1000 samples"),
            ("⚡ Features", "Delay, Ignores, Completion Time"),
        ]

        for label, value in model_info:
            info_widget = QVBoxLayout()
            l = QLabel(label)
            l.setStyleSheet("color: #6c7086; font-size: 10px;")
            v = QLabel(value)
            v.setFont(QFont("Arial", 10, QFont.Weight.Bold))
            v.setStyleSheet("color: #cba6f7;")
            info_widget.addWidget(l)
            info_widget.addWidget(v)
            model_layout.addLayout(info_widget)
            model_layout.addStretch()

        layout.addWidget(model_card)

        # Risk distribution
        dist_title = QLabel("📊 Risk Distribution")
        dist_title.setFont(QFont("Arial", 13, QFont.Weight.Bold))
        dist_title.setStyleSheet("color: #cdd6f4;")
        layout.addWidget(dist_title)

        self.dist_frame = QFrame()
        self.dist_frame.setStyleSheet("""
            QFrame {
                background-color: #181825;
                border-radius: 10px;
            }
        """)
        self.dist_layout = QVBoxLayout(self.dist_frame)
        self.dist_layout.setContentsMargins(20, 15, 20, 15)
        self.dist_layout.setSpacing(10)
        layout.addWidget(self.dist_frame)

        # Task predictions
        pred_title = QLabel("🎯 Task Risk Predictions")
        pred_title.setFont(QFont("Arial", 13, QFont.Weight.Bold))
        pred_title.setStyleSheet("color: #cdd6f4;")
        layout.addWidget(pred_title)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")

        scroll_content = QWidget()
        scroll_content.setStyleSheet("background-color: transparent;")
        self.predictions_layout = QVBoxLayout(scroll_content)
        self.predictions_layout.setSpacing(8)
        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)

        self.load_insights()

    def load_insights(self):
        tasks = get_all_tasks()

        # Risk distribution bars
        while self.dist_layout.count():
            item = self.dist_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        risk_counts = {'Low': 0, 'Medium': 0, 'High': 0}
        task_risks = []

        for task in tasks:
            pred = get_prediction_for_task(task['id'])
            risk = pred['risk_level'] if pred else 'Low'
            risk_counts[risk] += 1
            task_risks.append((task['title'], risk))

        total = len(tasks) or 1
        risk_colors = {'Low': '#a6e3a1', 'Medium': '#f9e2af', 'High': '#f38ba8'}

        for risk, count in risk_counts.items():
            row = QHBoxLayout()
            label = QLabel(f"{risk}")
            label.setFixedWidth(70)
            label.setStyleSheet(f"color: {risk_colors[risk]}; font-size: 11px; font-weight: bold;")

            bar = QProgressBar()
            bar.setMaximum(total)
            bar.setValue(count)
            bar.setFixedHeight(18)
            bar.setStyleSheet(f"""
                QProgressBar {{
                    background-color: #313244;
                    border-radius: 9px;
                    border: none;
                }}
                QProgressBar::chunk {{
                    background-color: {risk_colors[risk]};
                    border-radius: 9px;
                }}
            """)
            bar.setTextVisible(False)

            count_label = QLabel(f"{count} tasks")
            count_label.setFixedWidth(60)
            count_label.setStyleSheet("color: #6c7086; font-size: 10px;")

            row.addWidget(label)
            row.addWidget(bar)
            row.addWidget(count_label)

            row_widget = QWidget()
            row_widget.setLayout(row)
            self.dist_layout.addWidget(row_widget)

        # Clear predictions
        while self.predictions_layout.count():
            item = self.predictions_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not task_risks:
            empty = QLabel("No tasks yet. Add tasks to see AI predictions!")
            empty.setStyleSheet("color: #6c7086; font-size: 12px; padding: 20px;")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.predictions_layout.addWidget(empty)
        else:
            for title, risk in task_risks:
                card = RiskCard(title, risk)
                self.predictions_layout.addWidget(card)

        self.predictions_layout.addStretch()