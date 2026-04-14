# -*- coding: utf-8 -*-
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QScrollArea, QProgressBar
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor

from tasksenseai.database.db_manager import get_connection, get_setting
from tasksenseai.modules.ai_engine import predict_risk, get_prediction_for_task
from tasksenseai.modules.task_manager import get_all_tasks


class RiskCard(QFrame):
    def __init__(self, task_title, risk, confidence=None):
        super().__init__()
        clr = {'Low': '#a6e3a1', 'Medium': '#f9e2af', 'High': '#f38ba8'}
        bg  = {'Low': '#1a2e24', 'Medium': '#2e281a', 'High': '#2e1a1a'}
        dot = {'Low': '🟢', 'Medium': '🟡', 'High': '🔴'}

        c = clr.get(risk, '#585b70')
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {bg.get(risk, '#1e1e2e')};
                border-radius: 12px;
                border: 1px solid {c};
            }}
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(18, 14, 18, 14)
        layout.setSpacing(12)

        left = QVBoxLayout()
        left.setSpacing(3)

        t = QLabel(task_title)
        t.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        t.setStyleSheet("color: #cdd6f4; background: transparent; border: none;")
        left.addWidget(t)

        r = QLabel(f"{dot.get(risk, '⚪')}  Risk: {risk}")
        r.setStyleSheet(f"color: {c}; font-size: 11px; background: transparent; border: none;")
        left.addWidget(r)

        layout.addLayout(left)
        layout.addStretch()

        if confidence:
            cl = QLabel(f"{confidence}%")
            cl.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
            cl.setStyleSheet(f"color: {c}; background: transparent; border: none;")
            layout.addWidget(cl)


class AIInsightsPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color: #11111b;")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 28, 30, 20)
        layout.setSpacing(22)

        title = QLabel("🤖  AI Insights")
        title.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        title.setStyleSheet("color: #cdd6f4;")
        layout.addWidget(title)

        sub = QLabel("Procrastination risk analysis powered by Machine Learning")
        sub.setStyleSheet("color: #6c7086; font-size: 12px;")
        layout.addWidget(sub)

        # ── Model info card ──
        mc = QFrame()
        mc.setStyleSheet("""
            QFrame {
                background-color: #1e1e2e;
                border-radius: 14px;
                border: 1px solid #313244;
            }
        """)
        ml = QHBoxLayout(mc)
        ml.setContentsMargins(24, 18, 24, 18)
        ml.setSpacing(0)

        info = [
            ("🧠  Model",        "Random Forest"),
            ("🎯  Accuracy",     "96%"),
            ("📊  Training Data", "1000 samples"),
            ("⚡  Features",     "Delay · Ignores · Time"),
        ]
        self.info_labels = {}
        for label, val in info:
            col = QVBoxLayout()
            col.setSpacing(3)
            l = QLabel(label)
            l.setStyleSheet("color: #585b70; font-size: 10px; background: transparent; border: none;")
            v = QLabel(val)
            v.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
            v.setStyleSheet("color: #cba6f7; background: transparent; border: none;")
            self.info_labels[label] = v
            col.addWidget(l)
            col.addWidget(v)
            ml.addLayout(col)
            ml.addStretch()

        layout.addWidget(mc)

        # ── Risk distribution ──
        dt = QLabel("📊  Risk Distribution")
        dt.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        dt.setStyleSheet("color: #cdd6f4;")
        layout.addWidget(dt)

        self.dist_frame = QFrame()
        self.dist_frame.setStyleSheet("""
            QFrame { background-color: #1e1e2e; border-radius: 14px; border: 1px solid #313244; }
        """)
        self.dist_layout = QVBoxLayout(self.dist_frame)
        self.dist_layout.setContentsMargins(24, 18, 24, 18)
        self.dist_layout.setSpacing(12)
        layout.addWidget(self.dist_frame)

        # ── Task predictions ──
        pt = QLabel("🎯  Task Risk Predictions")
        pt.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        pt.setStyleSheet("color: #cdd6f4;")
        layout.addWidget(pt)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        sw = QWidget()
        sw.setStyleSheet("background: transparent;")
        self.pred_layout = QVBoxLayout(sw)
        self.pred_layout.setSpacing(8)
        scroll.setWidget(sw)
        layout.addWidget(scroll)

        self.load_insights()

    def load_insights(self):
        # Update model metrics
        name = get_setting('model_name', 'Random Forest')
        self.info_labels["🧠  Model"].setText(name)

        acc = get_setting('model_accuracy', 'N/A')
        try:
            self.info_labels["🎯  Accuracy"].setText(f"{float(acc)*100:.1f}%")
        except:
            self.info_labels["🎯  Accuracy"].setText("N/A")

        samples = get_setting('model_samples', '1000')
        self.info_labels["📊  Training Data"].setText(f"{samples} samples")

        tasks = get_all_tasks()

        # Risk distribution
        while self.dist_layout.count():
            item = self.dist_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        risk_counts = {'Low': 0, 'Medium': 0, 'High': 0}
        task_risks = []
        for t in tasks:
            pred = get_prediction_for_task(t['id'])
            risk = pred['risk_level'] if pred else 'Low'
            risk_counts[risk] += 1
            task_risks.append((t['title'], risk))

        total = len(tasks) or 1
        clrs = {'Low': '#a6e3a1', 'Medium': '#f9e2af', 'High': '#f38ba8'}

        for risk, count in risk_counts.items():
            row = QHBoxLayout()
            lbl = QLabel(f"● {risk}")
            lbl.setFixedWidth(80)
            lbl.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
            lbl.setStyleSheet(f"color: {clrs[risk]}; background: transparent; border: none;")

            bar = QProgressBar()
            bar.setMaximum(total)
            bar.setValue(count)
            bar.setFixedHeight(14)
            bar.setTextVisible(False)
            bar.setStyleSheet(f"""
                QProgressBar {{ background-color: #181825; border-radius: 7px; border: none; }}
                QProgressBar::chunk {{ background-color: {clrs[risk]}; border-radius: 7px; }}
            """)

            cnt = QLabel(f"{count}")
            cnt.setFixedWidth(30)
            cnt.setStyleSheet("color: #585b70; font-size: 11px; background: transparent; border: none;")
            cnt.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

            pct = QLabel(f"{int(count/total*100)}%")
            pct.setFixedWidth(36)
            pct.setStyleSheet(f"color: {clrs[risk]}; font-size: 10px; background: transparent; border: none;")

            row.addWidget(lbl)
            row.addWidget(bar, 1)
            row.addWidget(cnt)
            row.addWidget(pct)

            w = QWidget()
            w.setStyleSheet("background: transparent; border: none;")
            w.setLayout(row)
            self.dist_layout.addWidget(w)

        # Predictions list
        while self.pred_layout.count():
            item = self.pred_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not task_risks:
            empty = QLabel("No tasks yet. Add tasks to see AI predictions!")
            empty.setStyleSheet("color: #585b70; font-size: 12px; padding: 24px;")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.pred_layout.addWidget(empty)
        else:
            for title, risk in task_risks:
                self.pred_layout.addWidget(RiskCard(title, risk))

        self.pred_layout.addStretch()
