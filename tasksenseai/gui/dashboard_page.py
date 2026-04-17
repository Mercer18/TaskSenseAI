# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QScrollArea,
    QGraphicsDropShadowEffect, QProgressBar
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QColor

from tasksenseai.modules.task_manager import get_task_stats, get_pending_tasks, get_all_tasks
from tasksenseai.modules.ai_engine import get_prediction_for_task


class GlowCard(QFrame):
    """Stat card with gradient left border and subtle glow."""

    def __init__(self, title, value, color, emoji):
        super().__init__()
        self.color = color
        self.setFixedHeight(110)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: #1e1e2e;
                border-radius: 14px;
                border-left: 4px solid {color};
            }}
        """)

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(24)
        shadow.setColor(QColor(color))
        shadow.setOffset(0, 0)
        self.setGraphicsEffect(shadow)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(6)

        top = QHBoxLayout()
        top.setSpacing(10)

        emoji_label = QLabel(emoji)
        emoji_label.setFont(QFont("Segoe UI Emoji", 20))
        emoji_label.setFixedWidth(36)
        emoji_label.setStyleSheet("background: transparent; border: none;")

        self.value_label = QLabel(str(value))
        self.value_label.setFont(QFont("Segoe UI", 26, QFont.Weight.Bold))
        self.value_label.setStyleSheet(f"color: {color}; background: transparent; border: none;")

        top.addWidget(emoji_label)
        top.addWidget(self.value_label)
        top.addStretch()
        layout.addLayout(top)

        title_label = QLabel(title)
        title_label.setStyleSheet("color: #6c7086; font-size: 11px; background: transparent; border: none;")
        layout.addWidget(title_label)

    def update_value(self, v):
        self.value_label.setText(str(v))


class DashboardPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color: #11111b;")
        self.init_ui()
        self.timer = QTimer()
        self.timer.timeout.connect(self.refresh)
        self.timer.start(15000)

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 28, 30, 20)
        layout.setSpacing(22)

        # ── Header ──
        title = QLabel("Dashboard")
        title.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        title.setStyleSheet("color: #cdd6f4;")
        layout.addWidget(title)

        greeting = self._build_greeting()
        layout.addWidget(greeting)

        # ── Stat cards ──
        stats = get_task_stats()
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(16)

        cards_data = [
            ("Total Tasks",    stats['total'],     "#89b4fa", "📋"),
            ("Pending",        stats['pending'],   "#f9e2af", "⏳"),
            ("Completed",      stats['completed'], "#a6e3a1", "✅"),
            ("Completion Rate", self._rate(stats),  "#cba6f7", "📈"),
        ]

        self.stat_cards = []
        for t, v, c, e in cards_data:
            card = GlowCard(t, v, c, e)
            self.stat_cards.append(card)
            cards_layout.addWidget(card)

        layout.addLayout(cards_layout)

        # ── Streak + Today ──
        mid_row = QHBoxLayout()
        mid_row.setSpacing(16)

        # Streak card (with glow like stat cards)
        streak_frame = QFrame()
        streak_frame.setStyleSheet("""
            QFrame {
                background-color: #1e1e2e;
                border-radius: 14px;
                border-left: 4px solid #fab387;
            }
        """)
        streak_glow = QGraphicsDropShadowEffect(streak_frame)
        streak_glow.setBlurRadius(24)
        streak_glow.setColor(QColor("#fab387"))
        streak_glow.setOffset(0, 0)
        streak_frame.setGraphicsEffect(streak_glow)
        streak_frame.setFixedHeight(90)
        sl = QHBoxLayout(streak_frame)
        sl.setContentsMargins(24, 16, 24, 16)

        streak_days = self._calc_streak()
        fire = QLabel("🔥")
        fire.setFont(QFont("Segoe UI Emoji", 28))
        fire.setStyleSheet("background: transparent; border: none;")

        streak_right = QVBoxLayout()
        self.streak_val = QLabel(f"{streak_days}")
        self.streak_val.setFont(QFont("Segoe UI", 28, QFont.Weight.Bold))
        self.streak_val.setStyleSheet("color: #fab387; background: transparent; border: none;")
        streak_sub = QLabel("day streak" if streak_days == 1 else "day streak")
        streak_sub.setStyleSheet("color: #6c7086; font-size: 11px; background: transparent; border: none;")
        streak_right.addWidget(self.streak_val)
        streak_right.addWidget(streak_sub)

        sl.addWidget(fire)
        sl.addSpacing(12)
        sl.addLayout(streak_right)
        sl.addStretch()

        mid_row.addWidget(streak_frame, 1)

        # Today's progress
        today_frame = QFrame()
        today_frame.setStyleSheet("""
            QFrame {
                background-color: #1e1e2e;
                border-radius: 14px;
                border-left: 4px solid #89b4fa;
            }
        """)
        today_glow = QGraphicsDropShadowEffect(today_frame)
        today_glow.setBlurRadius(24)
        today_glow.setColor(QColor("#89b4fa"))
        today_glow.setOffset(0, 0)
        today_frame.setGraphicsEffect(today_glow)
        today_frame.setFixedHeight(90)
        tl = QVBoxLayout(today_frame)
        tl.setContentsMargins(24, 14, 24, 14)

        today_done, today_total = self._today_progress()
        today_head = QHBoxLayout()
        today_label = QLabel("📅 Today's Progress")
        today_label.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        today_label.setStyleSheet("color: #cdd6f4; background: transparent; border: none;")
        self.today_count = QLabel(f"{today_done}/{today_total}")
        self.today_count.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        self.today_count.setStyleSheet("color: #a6e3a1; background: transparent; border: none;")
        today_head.addWidget(today_label)
        today_head.addStretch()
        today_head.addWidget(self.today_count)
        tl.addLayout(today_head)

        self.today_bar = QProgressBar()
        self.today_bar.setFixedHeight(12)
        self.today_bar.setMaximum(max(today_total, 1))
        self.today_bar.setValue(today_done)
        self.today_bar.setTextVisible(False)
        self.today_bar.setStyleSheet("""
            QProgressBar { background-color: #313244; border-radius: 6px; }
            QProgressBar::chunk { background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                stop:0 #a6e3a1, stop:1 #89b4fa); border-radius: 6px; }
        """)
        tl.addWidget(self.today_bar)

        mid_row.addWidget(today_frame, 2)
        layout.addLayout(mid_row)

        # ── Pending tasks list ──
        pending_title = QLabel("⚡ Upcoming Tasks")
        pending_title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        pending_title.setStyleSheet("color: #cdd6f4;")
        layout.addWidget(pending_title)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_content.setStyleSheet("background: transparent;")
        self.tasks_layout = QVBoxLayout(scroll_content)
        self.tasks_layout.setSpacing(8)
        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)

        self.load_pending_tasks()

    # ─── Helpers ──────────────────────────────────────
    @staticmethod
    def _rate(stats):
        if stats['total'] == 0:
            return "0%"
        return f"{int(stats['completed']/stats['total']*100)}%"

    def _build_greeting(self):
        tasks = get_all_tasks()
        today = datetime.now().date()
        backlog_count = 0
        for t in tasks:
            if t['status'] != 'Completed':
                if t.get('due_date'):
                    try:
                        due = datetime.fromisoformat(t['due_date']).date()
                        if due < today:
                            backlog_count += 1
                    except:
                        pass
        
        hour = datetime.now().hour
        if backlog_count > 0:
            if hour >= 21 or hour < 5:
                text = f"Still got {backlog_count} task{'s' if backlog_count > 1 else ''} from earlier. Want to clear them before bed? 🌙"
            else:
                text = f"Don't forget — you have {backlog_count} backlog task{'s' if backlog_count > 1 else ''} to clear! ⚒️"
        else:
            if hour < 12:
                text = "Good morning! Ready for a fresh start? What's on your mind? ☀️"
            elif hour < 17:
                text = "Good afternoon! Momentum is key. What's next on the list? 🚀"
            elif hour < 21:
                text = "Good evening! Wrapping things up? Anything else for today? 🌙"
            else:
                text = "Late night productivity? You're a machine! Planning for tomorrow? 🌌"

        lbl = QLabel(text)
        lbl.setStyleSheet("color: #6c7086; font-size: 13px; font-weight: 500;")
        return lbl

    def _calc_streak(self):
        """Calculate consecutive days with at least one task completed.
        Holds the streak if yesterday was completed but today hasn't been yet.
        """
        tasks = get_all_tasks()
        completed_dates = set()
        for t in tasks:
            if t.get('completed_at') and t.get('status') == 'Completed':
                try:
                    dt = datetime.fromisoformat(t['completed_at'])
                    completed_dates.add(dt.date())
                except:
                    pass

        streak = 0
        today = datetime.now().date()
        
        # If today hasn't been completed, we check if we have a streak ending yesterday.
        # This prevents the streak from dropping to 0 every morning.
        curr_day = today
        if curr_day not in completed_dates:
            yesterday = today - timedelta(days=1)
            if yesterday in completed_dates:
                curr_day = yesterday
            else:
                return 0 # No completion today OR yesterday -> Streak reset

        # Count backwards
        while curr_day in completed_dates:
            streak += 1
            curr_day -= timedelta(days=1)
            
        return streak

    def _today_progress(self):
        tasks = get_all_tasks()
        today = datetime.now().date()
        today_total = 0
        today_done = 0
        for t in tasks:
            try:
                created = datetime.fromisoformat(t['created_at']).date()
            except:
                continue
            # Count tasks created today OR due today
            due_today = False
            if t.get('due_date'):
                try:
                    due_today = datetime.fromisoformat(t['due_date']).date() == today
                except:
                    pass

            if created == today or due_today:
                today_total += 1
                if t.get('status') == 'Completed':
                    today_done += 1

        return today_done, today_total

    # ─── Pending tasks ────────────────────────────────
    def load_pending_tasks(self):
        while self.tasks_layout.count():
            item = self.tasks_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        tasks = get_pending_tasks()
        risk_colors = {'Low': '#a6e3a1', 'Medium': '#f9e2af', 'High': '#f38ba8', 'N/A': '#585b70'}

        if not tasks:
            empty = QLabel("No pending tasks! You're all caught up.")
            empty.setStyleSheet("color: #a6e3a1; font-size: 13px; padding: 24px;")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.tasks_layout.addWidget(empty)
            return

        for task in tasks[:10]:
            pred = get_prediction_for_task(task['id'])
            risk = pred['risk_level'] if pred else 'N/A'

            card = QFrame()
            card.setStyleSheet(f"""
                QFrame {{
                    background-color: #1e1e2e;
                    border-radius: 10px;
                    border-left: 3px solid {risk_colors.get(risk, '#313244')};
                    border-top: 1px solid #313244;
                    border-right: 1px solid #313244;
                    border-bottom: 1px solid #313244;
                }}
            """)
            cl = QHBoxLayout(card)
            cl.setContentsMargins(18, 12, 18, 12)

            title = QLabel(task['title'])
            title.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
            title.setStyleSheet("color: #cdd6f4; background: transparent; border: none;")

            due_str = task.get('due_date', '')
            if due_str:
                due_str = due_str.replace("T", " ")[:16]
            due = QLabel(f"Due: {due_str or 'No date'}")
            due.setStyleSheet("color: #6c7086; font-size: 10px; background: transparent; border: none;")

            risk_lbl = QLabel(f"● {risk}")
            risk_lbl.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
            risk_lbl.setStyleSheet(f"color: {risk_colors.get(risk, '#585b70')}; background: transparent; border: none;")

            cl.addWidget(title)
            cl.addStretch()
            cl.addWidget(due)
            cl.addSpacing(12)
            cl.addWidget(risk_lbl)

            self.tasks_layout.addWidget(card)

        self.tasks_layout.addStretch()

    # ─── Refresh ──────────────────────────────────────
    def refresh(self):
        stats = get_task_stats()
        vals = [stats['total'], stats['pending'], stats['completed'], self._rate(stats)]
        if hasattr(self, 'stat_cards'):
            for i, v in enumerate(vals):
                self.stat_cards[i].update_value(v)

        streak = self._calc_streak()
        if hasattr(self, 'streak_val'):
            self.streak_val.setText(str(streak))

        td, tt = self._today_progress()
        if hasattr(self, 'today_count'):
            self.today_count.setText(f"{td}/{tt}")
            self.today_bar.setMaximum(max(tt, 1))
            self.today_bar.setValue(td)

        self.load_pending_tasks()
