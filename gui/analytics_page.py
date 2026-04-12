import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
import matplotlib
matplotlib.use('QtAgg')
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from modules.task_manager import get_all_tasks, get_task_stats
from modules.behavior_tracker import get_average_behavior
from modules.ai_engine import get_prediction_for_task

class AnalyticsPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color: #1e1e2e;")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(20)

        title = QLabel("📊 Analytics")
        title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        title.setStyleSheet("color: #cdd6f4;")
        layout.addWidget(title)

        subtitle = QLabel("Your productivity insights and behavior patterns")
        subtitle.setStyleSheet("color: #6c7086; font-size: 12px;")
        layout.addWidget(subtitle)

        # Stats row
        stats = get_task_stats()
        avg = get_average_behavior()

        stats_row = QHBoxLayout()
        
        avg_delay_display = f"{avg['avg_delay']}m"
        if avg['avg_delay'] >= 60:
            hours = int(avg['avg_delay'] // 60)
            mins = int(avg['avg_delay'] % 60)
            avg_delay_display = f"{hours}h {mins}m" if mins > 0 else f"{hours}h"
        
        stats_data = [
            ("Total Tasks", stats['total'], "#89b4fa"),
            ("Completed", stats['completed'], "#a6e3a1"),
            ("Avg Delay", avg_delay_display, "#f9e2af"),
            ("Avg Ignores", avg['avg_ignored'], "#f38ba8"),
        ]

        for label, value, color in stats_data:
            card = QFrame()
            card.setStyleSheet(f"""
                QFrame {{
                    background-color: #181825;
                    border-radius: 10px;
                    border: 2px solid {color};
                }}
            """)
            card_layout = QVBoxLayout(card)
            card_layout.setContentsMargins(15, 12, 15, 12)
            v = QLabel(str(value))
            v.setFont(QFont("Arial", 20, QFont.Weight.Bold))
            v.setStyleSheet(f"color: {color}; border: none;")
            v.setAlignment(Qt.AlignmentFlag.AlignCenter)
            l = QLabel(label)
            l.setStyleSheet("color: #6c7086; font-size: 10px; border: none;")
            l.setAlignment(Qt.AlignmentFlag.AlignCenter)
            card_layout.addWidget(v)
            card_layout.addWidget(l)
            stats_row.addWidget(card)

        layout.addLayout(stats_row)

        # Charts row
        charts_row = QHBoxLayout()
        charts_row.setSpacing(15)

        # Task status pie chart
        tasks = get_all_tasks()
        status_counts = {'Pending': 0, 'Completed': 0, 'In Progress': 0}
        risk_counts = {'Low': 0, 'Medium': 0, 'High': 0}

        for task in tasks:
            status = task.get('status', 'Pending')
            if status in status_counts:
                status_counts[status] += 1
            pred = get_prediction_for_task(task['id'])
            risk = pred['risk_level'] if pred else 'Low'
            if risk in risk_counts:
                risk_counts[risk] += 1

        # Pie chart - Task Status
        pie_frame = QFrame()
        pie_frame.setStyleSheet("background-color: #181825; border-radius: 10px;")
        pie_layout = QVBoxLayout(pie_frame)

        pie_title = QLabel("Task Status")
        pie_title.setStyleSheet("color: #cdd6f4; font-weight: bold; font-size: 12px;")
        pie_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        pie_layout.addWidget(pie_title)

        fig1 = Figure(figsize=(4, 3), facecolor='#181825')
        ax1 = fig1.add_subplot(111)
        ax1.set_facecolor('#181825')

        values = [v for v in status_counts.values() if v > 0]
        labels = [k for k, v in status_counts.items() if v > 0]
        colors = ['#f9e2af', '#a6e3a1', '#89b4fa'][:len(values)]

        if values:
            wedges, texts, autotexts = ax1.pie(
                values, labels=labels, colors=colors,
                autopct='%1.1f%%',
                textprops={'color': '#cdd6f4', 'fontsize': 9}
            )
            for autotext in autotexts:
                autotext.set_color('#1e1e2e')
                autotext.set_fontweight('bold')
                autotext.set_fontsize(9)
        else:
            ax1.text(0.5, 0.5, 'No data yet', ha='center', va='center',
                    color='#6c7086', transform=ax1.transAxes)

        canvas1 = FigureCanvas(fig1)
        canvas1.setStyleSheet("background-color: #181825;")
        pie_layout.addWidget(canvas1)
        charts_row.addWidget(pie_frame)

        # Bar chart - Risk Distribution
        bar_frame = QFrame()
        bar_frame.setStyleSheet("background-color: #181825; border-radius: 10px;")
        bar_layout = QVBoxLayout(bar_frame)

        bar_title = QLabel("Risk Distribution")
        bar_title.setStyleSheet("color: #cdd6f4; font-weight: bold; font-size: 12px;")
        bar_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        bar_layout.addWidget(bar_title)

        fig2 = Figure(figsize=(4, 3), facecolor='#181825')
        ax2 = fig2.add_subplot(111)
        ax2.set_facecolor('#181825')

        bar_colors = ['#a6e3a1', '#f9e2af', '#f38ba8']
        bars = ax2.bar(risk_counts.keys(), risk_counts.values(), color=bar_colors)
        ax2.tick_params(colors='#cdd6f4')
        ax2.spines['bottom'].set_color('#45475a')
        ax2.spines['left'].set_color('#45475a')
        ax2.spines['top'].set_visible(False)
        ax2.spines['right'].set_visible(False)
        for label in ax2.get_xticklabels() + ax2.get_yticklabels():
            label.set_color('#cdd6f4')
            label.set_fontsize(9)

        canvas2 = FigureCanvas(fig2)
        canvas2.setStyleSheet("background-color: #181825;")
        bar_layout.addWidget(canvas2)
        charts_row.addWidget(bar_frame)

        layout.addLayout(charts_row)


