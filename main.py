import sys
import os
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QStackedWidget
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from database.db_manager import initialize_database
from modules.ai_engine import ensure_model_exists
from modules.reminder_system import start_reminder_daemon
from gui.dashboard_page import DashboardPage
from gui.tasks_page import TasksPage
from gui.ai_insights_page import AIInsightsPage
from gui.analytics_page import AnalyticsPage
from gui.settings_page import SettingsPage

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TaskSenseAI")
        self.setMinimumSize(1000, 650)
        self.setStyleSheet("QMainWindow { background-color: #1e1e2e; }")
        self.init_ui()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Sidebar
        sidebar = QWidget()
        sidebar.setFixedWidth(210)
        sidebar.setStyleSheet("background-color: #181825;")
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(10, 20, 10, 20)
        sidebar_layout.setSpacing(6)

        # App title
        title = QLabel("TaskSense AI")
        title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        title.setStyleSheet("color: #cba6f7; padding: 10px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sidebar_layout.addWidget(title)

        subtitle = QLabel("Smart Task Manager")
        subtitle.setFont(QFont("Arial", 8))
        subtitle.setStyleSheet("color: #6c7086; padding-bottom: 20px;")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sidebar_layout.addWidget(subtitle)

        # Nav buttons
        self.nav_buttons = []
        nav_items = [
            ("🏠  Dashboard", 0),
            ("📋  Tasks", 1),
            ("🤖  AI Insights", 2),
            ("📊  Analytics", 3),
            ("⚙️  Settings", 4),
        ]

        for label, index in nav_items:
            btn = QPushButton(label)
            btn.setFixedHeight(42)
            btn.setFont(QFont("Arial", 10))
            btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    color: #cdd6f4;
                    border: none;
                    border-radius: 8px;
                    text-align: left;
                    padding-left: 15px;
                }
                QPushButton:hover {
                    background-color: #313244;
                    color: #cba6f7;
                }
            """)
            btn.clicked.connect(lambda checked, i=index: self.switch_page(i))
            sidebar_layout.addWidget(btn)
            self.nav_buttons.append(btn)

        sidebar_layout.addStretch()

        version = QLabel("v1.0.0")
        version.setStyleSheet("color: #45475a; font-size: 10px;")
        version.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sidebar_layout.addWidget(version)

        # Pages
        self.stack = QStackedWidget()
        self.stack.setStyleSheet("background-color: #1e1e2e;")

        self.dashboard_page = DashboardPage()
        self.tasks_page = TasksPage(refresh_callback=self.refresh_all)
        self.ai_insights_page = AIInsightsPage()
        self.analytics_page = AnalyticsPage()
        self.settings_page = SettingsPage()

        self.stack.addWidget(self.dashboard_page)
        self.stack.addWidget(self.tasks_page)
        self.stack.addWidget(self.ai_insights_page)
        self.stack.addWidget(self.analytics_page)
        self.stack.addWidget(self.settings_page)

        main_layout.addWidget(sidebar)
        main_layout.addWidget(self.stack)

        self.switch_page(0)

    def switch_page(self, index):
        self.stack.setCurrentIndex(index)
        if index == 0:
            self.dashboard_page.load_pending_tasks()
        if index == 1:
            self.tasks_page.load_tasks()
        if index == 2:
            self.ai_insights_page.load_insights()
        if index == 3:
            from gui.analytics_page import AnalyticsPage
            old_widget = self.stack.widget(3)
            self.analytics_page = AnalyticsPage()
            self.stack.removeWidget(old_widget)
            old_widget.deleteLater()
            self.stack.insertWidget(3, self.analytics_page)
            self.stack.setCurrentIndex(3)

        for i, btn in enumerate(self.nav_buttons):
            if i == index:
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #313244;
                        color: #cba6f7;
                        border: none;
                        border-radius: 8px;
                        text-align: left;
                        padding-left: 15px;
                        font-weight: bold;
                    }
                """)
            else:
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: transparent;
                        color: #cdd6f4;
                        border: none;
                        border-radius: 8px;
                        text-align: left;
                        padding-left: 15px;
                    }
                    QPushButton:hover {
                        background-color: #313244;
                        color: #cba6f7;
                    }
                """)

    def refresh_all(self):
        self.dashboard_page.refresh()


def main():
    initialize_database()
    ensure_model_exists()
    start_reminder_daemon()
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
