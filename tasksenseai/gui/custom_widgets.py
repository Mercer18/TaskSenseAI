# -*- coding: utf-8 -*-
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QWidget, QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt, QPoint, QRectF, pyqtSignal, QTime
from PyQt6.QtGui import QPainter, QColor, QFont, QPen, QPainterPath

import math

class AnalogClockPicker(QWidget):
    timeSelected = pyqtSignal(int, int) # hour, minute

    def __init__(self, is_am=True):
        super().__init__()
        self.setMinimumSize(220, 220)
        self.hour = 12
        self.minute = 0
        self.is_am = is_am
        self.selecting_hour = True # True = hour mode, False = minute mode

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        center = QPoint(int(self.width() / 2), int(self.height() / 2))
        radius = min(self.width(), self.height()) / 2 - 10

        # Draw background circle
        painter.setBrush(QColor("#1e1e2e"))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(center, int(radius), int(radius))

        # Font
        font = QFont("Segoe UI", 12, QFont.Weight.Bold)
        painter.setFont(font)
        
        # Calculate angle and position
        items = 12 if self.selecting_hour else 60
        step_val = 1 if self.selecting_hour else 5
        
        selected_val = self.hour if self.selecting_hour else self.minute
        if self.selecting_hour and selected_val == 0: selected_val = 12
        
        for i in range(1, items + 1):
            # Only draw numbers for every 1 hour, or every 5 minutes
            if not self.selecting_hour and i % 5 != 0 and i != 0:
                continue
                
            val_to_draw = i if self.selecting_hour else (i if i != 60 else 0)
            
            angle = math.radians(i * (360 / items) - 90)
            x = center.x() + (radius - 24) * math.cos(angle)
            y = center.y() + (radius - 24) * math.sin(angle)
            
            # Highlight selected
            if val_to_draw == selected_val:
                painter.setBrush(QColor("#cba6f7"))
                painter.drawEllipse(QPoint(int(x), int(y)), 16, 16)
                painter.setPen(QColor("#11111b"))
            else:
                painter.setPen(QColor("#cdd6f4"))
                
            text = str(val_to_draw)
            painter.drawText(QRectF(x - 16, y - 16, 32, 32), Qt.AlignmentFlag.AlignCenter, text)

        # Draw hand
        sel_angle = math.radians((selected_val if selected_val != 12 else (0 if self.selecting_hour else 60)) * (360 / items) - 90)
        hx = center.x() + (radius - 24) * math.cos(sel_angle)
        hy = center.y() + (radius - 24) * math.sin(sel_angle)

        painter.setPen(QPen(QColor("#cba6f7"), 2))
        painter.drawLine(center, QPoint(int(hx), int(hy)))
        painter.setBrush(QColor("#cba6f7"))
        painter.drawEllipse(center, 4, 4)

    def mousePressEvent(self, event):
        self._handle_mouse(event.position())

    def mouseMoveEvent(self, event):
        self._handle_mouse(event.position())

    def _handle_mouse(self, pos):
        center = QPoint(int(self.width() / 2), int(self.height() / 2))
        dx = pos.x() - center.x()
        dy = pos.y() - center.y()
        angle = math.degrees(math.atan2(dy, dx)) + 90
        if angle < 0: angle += 360

        if self.selecting_hour:
            h = int(round(angle / 30))
            if h == 0: h = 12
            self.hour = h
        else:
            m = int(round(angle / 6))
            if m == 60: m = 0
            self.minute = m
            
        self.update()
        self.timeSelected.emit(self.hour, self.minute)

class MaterialTimePicker(QDialog):
    def __init__(self, parent=None, initial_time=None):
        super().__init__(parent)
        self.setWindowTitle("Select Time")
        self.setFixedSize(300, 420)
        self.setStyleSheet("QDialog { background-color: #11111b; border-radius: 12px; }")
        
        self.time = initial_time if initial_time else QTime.currentTime()
        self.clock = AnalogClockPicker(is_am=(self.time.hour() < 12))
        
        h = self.time.hour() % 12
        if h == 0: h = 12
        self.clock.hour = h
        self.clock.minute = self.time.minute()
        
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        label = QLabel("SELECT TIME")
        label.setStyleSheet("color: #a6adc8; font-size: 11px; font-weight: bold; letter-spacing: 1px;")
        layout.addWidget(label)
        
        # Digital Display
        digi_layout = QHBoxLayout()
        digi_layout.setSpacing(8)
        
        self.hr_btn = QPushButton(f"{self.clock.hour:02d}")
        self.min_btn = QPushButton(f"{self.clock.minute:02d}")
        
        for btn in (self.hr_btn, self.min_btn):
            btn.setFixedSize(80, 80)
            btn.setFont(QFont("Segoe UI", 36))
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            
        self.colon = QLabel(":")
        self.colon.setStyleSheet("color: #cdd6f4; font-size: 36px; font-weight: bold;")
        
        # AM/PM Toggle
        am_pm_layout = QVBoxLayout()
        am_pm_layout.setSpacing(0)
        self.am_btn = QPushButton("AM")
        self.pm_btn = QPushButton("PM")
        
        for btn in (self.am_btn, self.pm_btn):
            btn.setFixedSize(40, 40)
            btn.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            am_pm_layout.addWidget(btn)
            
        self.am_btn.setStyleSheet("border-bottom-left-radius: 0; border-bottom-right-radius: 0; border: 1px solid #313244;")
        self.pm_btn.setStyleSheet("border-top-left-radius: 0; border-top-right-radius: 0; border: 1px solid #313244; border-top: none;")
        
        digi_layout.addStretch()
        digi_layout.addWidget(self.hr_btn)
        digi_layout.addWidget(self.colon)
        digi_layout.addWidget(self.min_btn)
        digi_layout.addLayout(am_pm_layout)
        digi_layout.addStretch()
        
        layout.addLayout(digi_layout)
        layout.addWidget(self.clock)
        
        # Buttons
        btn_layout = QHBoxLayout()
        cancel = QPushButton("CANCEL")
        ok = QPushButton("OK")
        
        for btn in (cancel, ok):
            btn.setFixedSize(80, 36)
            btn.setStyleSheet("color: #cba6f7; background: transparent; font-weight: bold; font-size: 13px; border: none;")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_layout.addWidget(btn)
            
        cancel.clicked.connect(self.reject)
        ok.clicked.connect(self.accept)
        layout.addLayout(btn_layout)
        
        # Connections
        self.hr_btn.clicked.connect(lambda: self.set_mode(True))
        self.min_btn.clicked.connect(lambda: self.set_mode(False))
        self.am_btn.clicked.connect(lambda: self.set_am_pm(True))
        self.pm_btn.clicked.connect(lambda: self.set_am_pm(False))
        self.clock.timeSelected.connect(self.update_display)
        
        self.set_mode(True)
        self.set_am_pm(self.clock.is_am)

    def set_mode(self, is_hour):
        self.clock.selecting_hour = is_hour
        self.clock.update()
        
        active_css = "background-color: rgba(203, 166, 247, 0.2); color: #cba6f7; border: none; border-radius: 8px;"
        inactive_css = "background-color: #1e1e2e; color: #cdd6f4; border: none; border-radius: 8px;"
        
        self.hr_btn.setStyleSheet(active_css if is_hour else inactive_css)
        self.min_btn.setStyleSheet(inactive_css if is_hour else active_css)

    def set_am_pm(self, is_am):
        self.clock.is_am = is_am
        active_css = "background-color: rgba(203, 166, 247, 0.2); color: #cba6f7;"
        inactive_css = "background-color: transparent; color: #a6adc8;"
        
        self.am_btn.setStyleSheet(self.am_btn.styleSheet().split("background-color")[0] + (active_css if is_am else inactive_css))
        self.pm_btn.setStyleSheet(self.pm_btn.styleSheet().split("background-color")[0] + (inactive_css if is_am else active_css))

    def update_display(self, h, m):
        self.hr_btn.setText(f"{h:02d}")
        self.min_btn.setText(f"{m:02d}")
        
    def get_time(self):
        h = self.clock.hour
        m = self.clock.minute
        if self.clock.is_am and h == 12: h = 0
        elif not self.clock.is_am and h < 12: h += 12
        return QTime(h, m)
