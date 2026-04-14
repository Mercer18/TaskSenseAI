# -*- coding: utf-8 -*-
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

import matplotlib
matplotlib.use('QtAgg')
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from tasksenseai.modules.task_manager import get_all_tasks, get_task_stats
from tasksenseai.modules.behavior_tracker import get_average_behavior
from tasksenseai.modules.ai_engine import get_prediction_for_task


class AnalyticsPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color: #11111b;")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 28, 30, 20)
        layout.setSpacing(22)

        title = QLabel("📊  Analytics")
        title.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        title.setStyleSheet("color: #cdd6f4;")
        layout.addWidget(title)

        sub = QLabel("Your productivity insights and behavior patterns")
        sub.setStyleSheet("color: #6c7086; font-size: 12px;")
        layout.addWidget(sub)

        # ── Stats row ──
        stats = get_task_stats()
        avg = get_average_behavior()

        stats_row = QHBoxLayout()
        stats_row.setSpacing(14)

        avg_delay_display = f"{avg['avg_delay']:.0f}m"
        if avg['avg_delay'] >= 60:
            h = int(avg['avg_delay'] // 60)
            m = int(avg['avg_delay'] % 60)
            avg_delay_display = f"{h}h {m}m" if m else f"{h}h"

        for label, value, color in [
            ("Total Tasks",  stats['total'],       "#89b4fa"),
            ("Completed",    stats['completed'],   "#a6e3a1"),
            ("Avg Delay",    avg_delay_display,    "#f9e2af"),
            ("Avg Ignores",  avg['avg_ignored'],   "#f38ba8"),
        ]:
            card = QFrame()
            card.setStyleSheet(f"""
                QFrame {{
                    background-color: #1e1e2e;
                    border-radius: 14px;
                    border-left: 4px solid {color};
                }}
            """)
            cl = QVBoxLayout(card)
            cl.setContentsMargins(18, 14, 18, 14)
            v = QLabel(str(value))
            v.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
            v.setStyleSheet(f"color: {color}; border: none; background: transparent;")
            v.setAlignment(Qt.AlignmentFlag.AlignCenter)
            l = QLabel(label)
            l.setStyleSheet("color: #6c7086; font-size: 10px; border: none; background: transparent;")
            l.setAlignment(Qt.AlignmentFlag.AlignCenter)
            cl.addWidget(v)
            cl.addWidget(l)
            stats_row.addWidget(card)

        layout.addLayout(stats_row)

        # ── Charts ──
        charts = QHBoxLayout()
        charts.setSpacing(16)

        tasks = get_all_tasks()
        status_counts = {'Pending': 0, 'Completed': 0, 'In Progress': 0}
        risk_counts = {'Low': 0, 'Medium': 0, 'High': 0}

        for t in tasks:
            s = t.get('status', 'Pending')
            if s in status_counts:
                status_counts[s] += 1
            pred = get_prediction_for_task(t['id'])
            risk = pred['risk_level'] if pred else 'Low'
            if risk in risk_counts:
                risk_counts[risk] += 1

        BG = '#1e1e2e'

        # Pie chart
        pie_frame = QFrame()
        pie_frame.setStyleSheet(f"background-color: {BG}; border-radius: 14px; border: 1px solid #313244;")
        pl = QVBoxLayout(pie_frame)
        pl.setContentsMargins(12, 12, 12, 4)

        pt = QLabel("Task Status")
        pt.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        pt.setStyleSheet("color: #cdd6f4; background: transparent; border: none;")
        pt.setAlignment(Qt.AlignmentFlag.AlignCenter)
        pl.addWidget(pt)

        fig1 = Figure(figsize=(4, 3), facecolor=BG)
        ax1 = fig1.add_subplot(111)
        ax1.set_facecolor(BG)
        vals = [v for v in status_counts.values() if v > 0]
        lbls = [k for k, v in status_counts.items() if v > 0]
        clrs = {'Pending': '#f9e2af', 'Completed': '#a6e3a1', 'In Progress': '#89b4fa'}
        cs = [clrs.get(k, '#585b70') for k in lbls]

        if vals:
            wedges, texts, auts = ax1.pie(
                vals, labels=lbls, colors=cs, autopct='%1.0f%%',
                textprops={'color': '#cdd6f4', 'fontsize': 9},
                wedgeprops={'linewidth': 1, 'edgecolor': BG},
                startangle=90
            )
            for a in auts:
                a.set_color('#11111b')
                a.set_fontweight('bold')
        else:
            ax1.text(0.5, 0.5, 'No data', ha='center', va='center',
                     color='#585b70', transform=ax1.transAxes)

        c1 = FigureCanvas(fig1)
        c1.setStyleSheet(f"background-color: {BG};")
        pl.addWidget(c1)
        charts.addWidget(pie_frame)

        # Bar chart
        bar_frame = QFrame()
        bar_frame.setStyleSheet(f"background-color: {BG}; border-radius: 14px; border: 1px solid #313244;")
        bl = QVBoxLayout(bar_frame)
        bl.setContentsMargins(12, 12, 12, 4)

        bt = QLabel("Risk Distribution")
        bt.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        bt.setStyleSheet("color: #cdd6f4; background: transparent; border: none;")
        bt.setAlignment(Qt.AlignmentFlag.AlignCenter)
        bl.addWidget(bt)

        fig2 = Figure(figsize=(4, 3), facecolor=BG)
        ax2 = fig2.add_subplot(111)
        ax2.set_facecolor(BG)

        bar_clrs = ['#a6e3a1', '#f9e2af', '#f38ba8']
        bars = ax2.bar(risk_counts.keys(), risk_counts.values(), color=bar_clrs,
                       width=0.5, edgecolor=BG, linewidth=1)

        # Value labels on bars
        for bar in bars:
            h = bar.get_height()
            if h > 0:
                ax2.text(bar.get_x() + bar.get_width()/2, h + 0.2, str(int(h)),
                         ha='center', va='bottom', color='#cdd6f4', fontsize=10, fontweight='bold')

        ax2.tick_params(colors='#6c7086')
        ax2.spines['bottom'].set_color('#313244')
        ax2.spines['left'].set_color('#313244')
        ax2.spines['top'].set_visible(False)
        ax2.spines['right'].set_visible(False)
        for label in ax2.get_xticklabels() + ax2.get_yticklabels():
            label.set_color('#6c7086')
            label.set_fontsize(9)

        c2 = FigureCanvas(fig2)
        c2.setStyleSheet(f"background-color: {BG};")
        bl.addWidget(c2)
        charts.addWidget(bar_frame)

        layout.addLayout(charts)
