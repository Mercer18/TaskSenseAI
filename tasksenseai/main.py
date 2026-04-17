# -*- coding: utf-8 -*-
import sys
import os
from datetime import datetime

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QStackedWidget, QSystemTrayIcon, QMenu, QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QSize
from PyQt6.QtGui import QFont, QIcon, QColor, QPixmap, QPainter, QLinearGradient, QAction

from tasksenseai.database.db_manager import initialize_database, set_setting, get_setting
from tasksenseai.modules.ai_engine import ensure_model_exists
from tasksenseai.modules.task_manager import get_all_tasks
from tasksenseai.modules.reminder_system import start_reminder_daemon
from tasksenseai.gui.styles import GLOBAL_STYLESHEET
from tasksenseai.gui.dashboard_page import DashboardPage
from tasksenseai.gui.tasks_page import TasksPage
from tasksenseai.gui.all_tasks_page import AllTasksPage
from tasksenseai.gui.ai_insights_page import AIInsightsPage
from tasksenseai.gui.analytics_page import AnalyticsPage
from tasksenseai.gui.settings_page import SettingsPage


def _get_greeting():
    hour = datetime.now().hour
    if hour < 12:
        return "Good morning"
    elif hour < 17:
        return "Good afternoon"
    elif hour < 21:
        return "Good evening"
    return "Good night"


def _make_tray_icon():
    """Generate a simple purple circle icon for the system tray."""
    pix = QPixmap(64, 64)
    pix.fill(QColor(0, 0, 0, 0))
    painter = QPainter(pix)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    grad = QLinearGradient(0, 0, 64, 64)
    grad.setColorAt(0, QColor("#cba6f7"))
    grad.setColorAt(1, QColor("#89b4fa"))
    painter.setBrush(grad)
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawRoundedRect(4, 4, 56, 56, 16, 16)
    painter.setPen(QColor("#11111b"))
    painter.setFont(QFont("Arial", 26, QFont.Weight.Bold))
    painter.drawText(pix.rect(), Qt.AlignmentFlag.AlignCenter, "T")
    painter.end()
    return QIcon(pix)


class NavButton(QPushButton):
    """Custom sidebar nav button with animated active indicator."""

    ACTIVE_STYLE = """
        QPushButton {{
            background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                stop:0 rgba(203,166,247,0.18), stop:1 transparent);
            color: #cba6f7;
            border: none;
            border-left: 3px solid #cba6f7;
            border-radius: 0px;
            text-align: left;
            padding-left: 18px;
            font-weight: bold;
            font-size: {size}px;
        }}
    """
    INACTIVE_STYLE = """
        QPushButton {{
            background-color: transparent;
            color: #a6adc8;
            border: none;
            border-left: 3px solid transparent;
            border-radius: 0px;
            text-align: left;
            padding-left: 18px;
            font-size: {size}px;
        }}
        QPushButton:hover {{
            background: rgba(203,166,247,0.08);
            color: #cdd6f4;
        }}
    """

    def __init__(self, text, icon_char="", font_size=11):
        display = f"{icon_char}  {text}" if icon_char else text
        super().__init__(display)
        self._font_size = font_size
        self.setFixedHeight(44)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.set_active(False)

    def set_active(self, active):
        style = self.ACTIVE_STYLE if active else self.INACTIVE_STYLE
        self.setStyleSheet(style.format(size=self._font_size))


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TaskSenseAI")
        self.setMinimumSize(1080, 700)
        self.setObjectName("MainWindow")
        self.init_ui()
        self._setup_tray()

    def init_ui(self):
        central = QWidget()
        central.setObjectName("CentralWidget")
        self.setCentralWidget(central)
        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ─── Sidebar ───────────────────────────────────────────
        sidebar = QWidget()
        sidebar.setFixedWidth(230)
        sidebar.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
                    stop:0 #181825, stop:1 #11111b);
                border-right: 1px solid #313244;
            }
        """)
        sb = QVBoxLayout(sidebar)
        sb.setContentsMargins(0, 0, 0, 0)
        sb.setSpacing(0)

        # Logo area
        logo_area = QWidget()
        logo_area.setFixedHeight(100)
        logo_area.setStyleSheet("background: transparent; border: none;")
        la = QVBoxLayout(logo_area)
        la.setContentsMargins(20, 22, 20, 8)
        la.setSpacing(2)

        app_name = QLabel("TaskSenseAI")
        app_name.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        app_name.setStyleSheet("""
            color: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                stop:0 #cba6f7, stop:1 #89b4fa);
            background: transparent; border: none;
        """)
        # Qt QLabel doesn't support gradient text via QSS, so use solid
        app_name.setStyleSheet("color: #cba6f7; background: transparent; border: none;")
        la.addWidget(app_name)

        greeting = QLabel(f"{_get_greeting()} 👋")
        greeting.setFont(QFont("Segoe UI", 9))
        greeting.setStyleSheet("color: #6c7086; background: transparent; border: none;")
        la.addWidget(greeting)

        sb.addWidget(logo_area)

        # Divider
        div = QWidget()
        div.setFixedHeight(1)
        div.setStyleSheet("background-color: #313244;")
        sb.addWidget(div)
        sb.addSpacing(10)

        # Nav buttons
        self.nav_buttons = []
        nav_items = [
            ("Dashboard", "🏠", 0),
            ("Tasks",     "📋", 1),
            ("Task Vault", "📑", 2),
            ("AI Insights","🤖", 3),
            ("Analytics", "📊", 4),
            ("Settings",  "⚙️", 5),
        ]

        for label, icon, index in nav_items:
            btn = NavButton(label, icon)
            btn.clicked.connect(lambda checked, i=index: self.switch_page(i))
            sb.addWidget(btn)
            self.nav_buttons.append(btn)

        sb.addStretch()

        # Bottom info
        ver = QLabel("v2.0.0  ·  Catppuccin")
        ver.setStyleSheet("color: #45475a; font-size: 9px; background: transparent; border: none;")
        ver.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sb.addWidget(ver)
        sb.addSpacing(12)

        root.addWidget(sidebar)

        # ─── Page stack ─────────────────────────────────────────
        content_wrap = QWidget()
        content_wrap.setStyleSheet("background-color: #11111b; border: none;")
        cw_layout = QVBoxLayout(content_wrap)
        cw_layout.setContentsMargins(0, 0, 0, 0)

        self.stack = QStackedWidget()

        self.dashboard_page = DashboardPage()
        self.tasks_page = TasksPage(refresh_callback=self.refresh_all)
        self.all_tasks_page = AllTasksPage()
        self.ai_insights_page = AIInsightsPage()
        self.analytics_page = AnalyticsPage()
        self.settings_page = SettingsPage()

        self.stack.addWidget(self.dashboard_page)
        self.stack.addWidget(self.tasks_page)
        self.stack.addWidget(self.all_tasks_page)
        self.stack.addWidget(self.ai_insights_page)
        self.stack.addWidget(self.analytics_page)
        self.stack.addWidget(self.settings_page)

        cw_layout.addWidget(self.stack)
        root.addWidget(content_wrap)

        self.switch_page(0)

    # ─── System Tray ───────────────────────────────────────────
    def _setup_tray(self):
        self.tray_icon = QSystemTrayIcon(_make_tray_icon(), self)
        self.tray_icon.setToolTip("TaskSenseAI")

        tray_menu = QMenu()
        tray_menu.setStyleSheet("""
            QMenu { background-color: #1e1e2e; color: #cdd6f4; border: 1px solid #313244; border-radius: 8px; padding: 4px; }
            QMenu::item { padding: 6px 20px; border-radius: 4px; }
            QMenu::item:selected { background-color: #313244; }
        """)

        show_action = QAction("Show TaskSenseAI", self)
        show_action.triggered.connect(self._show_window)
        tray_menu.addAction(show_action)

        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(QApplication.quit)
        tray_menu.addAction(quit_action)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self._tray_activated)
        self.tray_icon.show()

    def _tray_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self._show_window()

    def _show_window(self):
        self.showNormal()
        self.activateWindow()

    def closeEvent(self, event):
        """Minimize to tray instead of quitting."""
        event.ignore()
        self.hide()
        
        # Determine personality message based on today's progress
        tasks = get_all_tasks()
        today = datetime.now().date()
        done_today = 0
        for t in tasks:
            if t.get('completed_at') and t.get('status') == 'Completed':
                try:
                    cd = datetime.fromisoformat(t['completed_at']).date()
                    if cd == today:
                        done_today += 1
                except: pass

        hour = datetime.now().hour
        if hour >= 21 or hour < 5:
            title = "Good night! 🌙"
            if done_today > 0:
                msg = f"Good work on the {done_today} task{'s' if done_today > 1 else ''} today! Rest up — see you tomorrow with more energy! 🌌"
            else:
                msg = "Rest up! Tomorrow is a new day to crush those tasks. See you then! 💤"
        elif hour < 12:
            title = "Stay focused! ☀️"
            msg = "TaskSenseAI is still tracking in the background. Keep that morning momentum! 🚀"
        else:
            title = "Background Mode 📋"
            msg = "I'm still here if you need me. TaskSenseAI is guarding your productivity! 🛡️"

        self.tray_icon.showMessage(
            title,
            msg,
            QSystemTrayIcon.MessageIcon.Information,
            3000
        )

    # ─── Page switching ────────────────────────────────────────
    def switch_page(self, index):
        self.stack.setCurrentIndex(index)

        if index == 0:
            self.dashboard_page.refresh()
        elif index == 1:
            self.tasks_page.load_tasks()
        elif index == 2:
            self.all_tasks_page.load_tasks()
        elif index == 3:
            self.ai_insights_page.load_insights()
        elif index == 4:
            from tasksenseai.gui.analytics_page import AnalyticsPage as AP
            old = self.stack.widget(4)
            self.analytics_page = AP()
            self.stack.removeWidget(old)
            old.deleteLater()
            self.stack.insertWidget(4, self.analytics_page)
            self.stack.setCurrentIndex(4)

        for i, btn in enumerate(self.nav_buttons):
            btn.set_active(i == index)

    def refresh_all(self):
        self.dashboard_page.refresh()
        self.all_tasks_page.load_tasks()


def main():
    initialize_database()
    ensure_model_exists()
    
    # Track day transitions
    set_setting('last_run_date', datetime.now().date().isoformat())

    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setStyleSheet(GLOBAL_STYLESHEET)

    start_reminder_daemon()

    window = MainWindow()
    
    # Optimized for user resolution (1920x1200) and adaptable to others
    if "--minimized" not in sys.argv:
        window.showMaximized()
    else:
        # Just ensure it exists in the background (tray is already setup in MainWindow.__init__)
        pass

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
