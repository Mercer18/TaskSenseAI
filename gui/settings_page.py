import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                              QFrame, QPushButton, QSpinBox, QMessageBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

class SettingsPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color: #1e1e2e;")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(20)

        title = QLabel("⚙️ Settings")
        title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        title.setStyleSheet("color: #cdd6f4;")
        layout.addWidget(title)

        subtitle = QLabel("Configure TaskSenseAI preferences")
        subtitle.setStyleSheet("color: #6c7086; font-size: 12px;")
        layout.addWidget(subtitle)

        # App info card
        info_card = QFrame()
        info_card.setStyleSheet("""
            QFrame {
                background-color: #181825;
                border-radius: 10px;
                border: 1px solid #313244;
            }
        """)
        info_layout = QVBoxLayout(info_card)
        info_layout.setContentsMargins(20, 15, 20, 15)
        info_layout.setSpacing(8)

        info_title = QLabel("📱 Application Info")
        info_title.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        info_title.setStyleSheet("color: #cba6f7;")
        info_layout.addWidget(info_title)

        for label, value in [
            ("App Name", "TaskSenseAI"),
            ("Version", "1.0.0"),
            ("AI Model", "Random Forest Classifier"),
            ("Database", "SQLite (Local)"),
            ("Developer", "SE Lab Project"),
        ]:
            row = QHBoxLayout()
            l = QLabel(label)
            l.setStyleSheet("color: #6c7086; font-size: 11px;")
            v = QLabel(value)
            v.setStyleSheet("color: #cdd6f4; font-size: 11px;")
            row.addWidget(l)
            row.addStretch()
            row.addWidget(v)
            row_widget = QWidget()
            row_widget.setLayout(row)
            info_layout.addWidget(row_widget)

        layout.addWidget(info_card)

        # Reminder settings
        reminder_card = QFrame()
        reminder_card.setStyleSheet("""
            QFrame {
                background-color: #181825;
                border-radius: 10px;
                border: 1px solid #313244;
            }
        """)
        reminder_layout = QVBoxLayout(reminder_card)
        reminder_layout.setContentsMargins(20, 15, 20, 15)
        reminder_layout.setSpacing(10)

        reminder_title = QLabel("🔔 Reminder Settings")
        reminder_title.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        reminder_title.setStyleSheet("color: #cba6f7;")
        reminder_layout.addWidget(reminder_title)

        interval_row = QHBoxLayout()
        interval_label = QLabel("Check interval (minutes):")
        interval_label.setStyleSheet("color: #cdd6f4; font-size: 11px;")
        self.interval_spin = QSpinBox()
        self.interval_spin.setRange(1, 60)
        self.interval_spin.setValue(5)
        self.interval_spin.setStyleSheet("""
            QSpinBox {
                background-color: #313244;
                color: #cdd6f4;
                border: 1px solid #45475a;
                border-radius: 6px;
                padding: 5px;
                font-size: 11px;
            }
        """)
        interval_row.addWidget(interval_label)
        interval_row.addStretch()
        interval_row.addWidget(self.interval_spin)
        interval_widget = QWidget()
        interval_widget.setLayout(interval_row)
        reminder_layout.addWidget(interval_widget)

        layout.addWidget(reminder_card)

        # Danger zone
        danger_card = QFrame()
        danger_card.setStyleSheet("""
            QFrame {
                background-color: #2a1a1a;
                border-radius: 10px;
                border: 1px solid #f38ba8;
            }
        """)
        danger_layout = QVBoxLayout(danger_card)
        danger_layout.setContentsMargins(20, 15, 20, 15)

        danger_title = QLabel("⚠️ Danger Zone")
        danger_title.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        danger_title.setStyleSheet("color: #f38ba8;")
        danger_layout.addWidget(danger_title)

        retrain_btn = QPushButton("🔄 Retrain AI Model")
        retrain_btn.setStyleSheet("""
            QPushButton {
                background-color: #313244;
                color: #cdd6f4;
                border: none;
                border-radius: 6px;
                padding: 10px;
                font-size: 11px;
            }
            QPushButton:hover { background-color: #45475a; }
        """)
        retrain_btn.clicked.connect(self.retrain_model)
        danger_layout.addWidget(retrain_btn)

        layout.addWidget(danger_card)
        layout.addStretch()

    def retrain_model(self):
        reply = QMessageBox.question(self, 'Retrain Model',
                                     'This will retrain the AI model. Continue?',
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            from modules.ai_engine import train_model
            model, acc = train_model()
            QMessageBox.information(self, 'Done', f'Model retrained! Accuracy: {acc:.2%}')