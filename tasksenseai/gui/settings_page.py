# -*- coding: utf-8 -*-
import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QPushButton, QSpinBox, QMessageBox, QScrollArea
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont


class RetrainThread(QThread):
    finished = pyqtSignal(object, float)
    error = pyqtSignal(str)

    def run(self):
        try:
            from tasksenseai.modules.ai_engine import train_model
            model, acc = train_model()
            self.finished.emit(model, acc)
        except Exception as e:
            self.error.emit(str(e))


class SettingsPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color: #11111b;")
        self.init_ui()

    def _make_card(self, title_text, title_color="#cba6f7", border_color="#313244"):
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: #1e1e2e;
                border-radius: 14px;
                border: 1px solid {border_color};
            }}
        """)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(24, 18, 24, 18)
        card_layout.setSpacing(10)

        t = QLabel(title_text)
        t.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        t.setStyleSheet(f"color: {title_color}; background: transparent; border: none;")
        card_layout.addWidget(t)

        return card, card_layout

    def _info_row(self, label_text, value_text, parent_layout):
        row = QHBoxLayout()
        l = QLabel(label_text)
        l.setStyleSheet("color: #6c7086; font-size: 11px; background: transparent; border: none;")
        v = QLabel(value_text)
        v.setStyleSheet("color: #cdd6f4; font-size: 11px; background: transparent; border: none;")
        v.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        row.addWidget(l)
        row.addStretch()
        row.addWidget(v)
        w = QWidget()
        w.setStyleSheet("background: transparent; border: none;")
        w.setLayout(row)
        parent_layout.addWidget(w)
        return v

    def init_ui(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll_widget.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(scroll_widget)
        layout.setContentsMargins(30, 28, 30, 20)
        layout.setSpacing(20)

        title = QLabel("⚙️  Settings")
        title.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        title.setStyleSheet("color: #cdd6f4;")
        layout.addWidget(title)

        sub = QLabel("Configure TaskSenseAI preferences")
        sub.setStyleSheet("color: #6c7086; font-size: 12px;")
        layout.addWidget(sub)

        # ── Application Info ──
        card, cl = self._make_card("📱  Application Info")

        from tasksenseai.database.db_manager import DB_PATH, get_setting
        model_name = get_setting('model_name', 'Random Forest')
        acc_raw = get_setting('model_accuracy', 'N/A')
        try:
            acc_display = f"{float(acc_raw)*100:.1f}%"
        except:
            acc_display = "N/A"

        self._info_row("App Name",      "TaskSenseAI",   cl)
        self._info_row("Version",       "2.0.0",         cl)
        self._info_row("AI Model",      model_name,      cl)
        self._info_row("Model Accuracy", acc_display,     cl)
        self._info_row("Database",       "SQLite (Local)", cl)
        self._info_row("DB Location",    DB_PATH,         cl)
        self._info_row("Developer",      "SE Lab Project", cl)

        layout.addWidget(card)

        # ── Notification Settings ──
        ncard, nl = self._make_card("🔔  Notification Settings")

        desc = QLabel("The reminder system checks for upcoming/overdue tasks every 30 seconds.\n"
                      "Per-task reminder frequency adapts automatically based on risk level & urgency.")
        desc.setWordWrap(True)
        desc.setStyleSheet("color: #6c7086; font-size: 11px; background: transparent; border: none;")
        nl.addWidget(desc)

        # Visual summary of intervals
        intervals_data = [
            ("🔴 High risk — overdue",    "every 1 min"),
            ("🟡 Medium risk — overdue",   "every 2 min"),
            ("🟢 Low risk — overdue",      "every 5 min"),
            ("🔴 High risk — due < 3h",    "every 2 min"),
            ("🟡 Medium risk — due < 2h",  "every 5 min"),
            ("🟢 Low risk — due < 1h",     "every 10 min"),
        ]
        for label, interval in intervals_data:
            self._info_row(label, interval, nl)

        layout.addWidget(ncard)

        # ── Danger Zone ──
        dcard, dl = self._make_card("⚠️  Danger Zone", "#f38ba8", "#f38ba8")

        self.retrain_btn = QPushButton("🔄  Retrain AI Model")
        self.retrain_btn.setFixedHeight(42)
        self.retrain_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.retrain_btn.setStyleSheet("""
            QPushButton {
                background-color: #313244; color: #cdd6f4; border: none;
                border-radius: 10px; padding: 0 20px; font-size: 12px;
            }
            QPushButton:hover { background-color: #45475a; }
            QPushButton:disabled { background-color: #1e1e2e; color: #45475a; }
        """)
        self.retrain_btn.clicked.connect(self.retrain_model)
        dl.addWidget(self.retrain_btn)

        layout.addWidget(dcard)
        layout.addStretch()

        scroll.setWidget(scroll_widget)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

    def retrain_model(self):
        reply = QMessageBox.question(
            self, 'Retrain Model', 'This will retrain the AI model. Continue?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.retrain_btn.setEnabled(False)
            self.retrain_btn.setText("🔄  Retraining… Please wait")
            self.thread = RetrainThread()
            self.thread.finished.connect(self._on_done)
            self.thread.error.connect(self._on_err)
            self.thread.start()

    def _on_done(self, model, acc):
        self.retrain_btn.setEnabled(True)
        self.retrain_btn.setText("🔄  Retrain AI Model")
        QMessageBox.information(self, 'Done', f'Model retrained! Accuracy: {acc:.2%}')

    def _on_err(self, err):
        self.retrain_btn.setEnabled(True)
        self.retrain_btn.setText("🔄  Retrain AI Model")
        QMessageBox.critical(self, 'Error', f'Failed to retrain model:\n{err}')
