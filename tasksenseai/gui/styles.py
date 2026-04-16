# -*- coding: utf-8 -*-
"""
Global QSS stylesheet for TaskSenseAI — Catppuccin Mocha + glassmorphism
"""

import os
BASE_DIR = os.path.dirname(__file__).replace('\\', '/')

GLOBAL_STYLESHEET_RAW = """
/* ═══════════════════════════════════════════════════════════════
   BASE & WINDOW
   ═══════════════════════════════════════════════════════════════ */
QMainWindow, QWidget#CentralWidget {
    background-color: #11111b;
}

/* ═══════════════════════════════════════════════════════════════
   CUSTOM SCROLLBARS
   ═══════════════════════════════════════════════════════════════ */
QScrollBar:vertical {
    background: #11111b;
    width: 8px;
    border-radius: 4px;
    margin: 0;
}
QScrollBar::handle:vertical {
    background: #45475a;
    min-height: 30px;
    border-radius: 4px;
}
QScrollBar::handle:vertical:hover {
    background: #585b70;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0;
}
QScrollBar:horizontal {
    background: #11111b;
    height: 8px;
    border-radius: 4px;
}
QScrollBar::handle:horizontal {
    background: #45475a;
    min-width: 30px;
    border-radius: 4px;
}
QScrollBar::handle:horizontal:hover {
    background: #585b70;
}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0;
}

/* ═══════════════════════════════════════════════════════════════
   TOOLTIPS
   ═══════════════════════════════════════════════════════════════ */
QToolTip {
    background-color: #1e1e2e;
    color: #cdd6f4;
    border: 1px solid #585b70;
    border-radius: 6px;
    padding: 6px 10px;
    font-size: 11px;
}

/* ═══════════════════════════════════════════════════════════════
   MESSAGE BOX  —  ensure ALL buttons are clearly readable
   ═══════════════════════════════════════════════════════════════ */
QMessageBox {
    background-color: #1e1e2e;
    border: 1px solid #313244;
}
QMessageBox QLabel {
    color: #cdd6f4;
    font-size: 13px;
    padding: 4px;
}
QMessageBox QPushButton {
    background: #313244;
    color: #cdd6f4;
    border: 1px solid #585b70;
    border-radius: 6px;
    padding: 6px 24px;
    min-width: 70px;
    min-height: 24px;
    font-size: 13px;
    font-weight: bold;
}
QMessageBox QPushButton:hover {
    background: #cba6f7;
    color: #11111b;
    border: 1px solid #cba6f7;
}
QMessageBox QPushButton:focus {
    outline: none;
    border: 1px solid #cba6f7;
}

/* ═══════════════════════════════════════════════════════════════
   INPUTS
   ═══════════════════════════════════════════════════════════════ */
QLineEdit, QTextEdit, QSpinBox {
    background-color: #181825;
    color: #cdd6f4;
    border: 1px solid #313244;
    border-radius: 8px;
    padding: 8px 12px;
    font-size: 12px;
    selection-background-color: #585b70;
}
QLineEdit:focus, QTextEdit:focus, QSpinBox:focus {
    border: 1px solid #cba6f7;
}

QComboBox {
    background-color: #181825;
    color: #cdd6f4;
    border: 1px solid #313244;
    border-radius: 8px;
    padding: 8px 16px;
    font-size: 13px;
    font-weight: bold;
    selection-background-color: #313244;
    selection-color: #cdd6f4;
}
QComboBox:hover, QComboBox:focus {
    border: 1px solid #cba6f7;
}
QComboBox::drop-down {
    border: none;
    width: 32px;
}
QComboBox::down-arrow, QDateEdit::down-arrow, QTimeEdit::down-arrow {
    image: url("__ARROW_DOWN__");
    width: 16px;
    height: 16px;
}
QComboBox QAbstractItemView {
    background-color: #1e1e2e;
    border: 1px solid #45475a;
    outline: none;
    selection-background-color: #cba6f7;
    selection-color: #11111b;
}
QComboBox QAbstractItemView::item {
    font-size: 13px;
    font-weight: bold;
    padding: 8px 12px;
    color: #cdd6f4;
}
QComboBox QAbstractItemView::item:hover, QComboBox QAbstractItemView::item:selected {
    background-color: #cba6f7;
    color: #11111b;
}

QDateEdit, QTimeEdit {
    background-color: #181825;
    color: #cdd6f4;
    border: 1px solid #313244;
    border-radius: 8px;
    padding: 8px 12px;
    font-size: 13px;
    font-weight: bold;
    selection-background-color: #313244;
    selection-color: #cdd6f4;
}
QDateEdit:hover, QTimeEdit:hover, QDateEdit:focus, QTimeEdit:focus {
    border: 1px solid #cba6f7;
}
QDateEdit::drop-down, QTimeEdit::drop-down {
    border: none;
    width: 32px;
}

/* ═══════════════════════════════════════════════════════════════
   PREMIUM CALENDAR DESIGN
   ═══════════════════════════════════════════════════════════════ */
QCalendarWidget QWidget#qt_calendar_navigationbar {
    background-color: #313244;
    border-top-left-radius: 12px;
    border-top-right-radius: 12px;
    padding: 6px;
    border: 1px solid #45475a;
    border-bottom: none;
}
QCalendarWidget QToolButton {
    color: #cdd6f4;
    font-size: 15px;
    font-weight: bold;
    background-color: transparent;
    border: none;
    border-radius: 6px;
    padding: 4px 10px;
    margin: 2px;
}
QCalendarWidget QToolButton:hover {
    background-color: #45475a;
    color: #cba6f7;
}
QCalendarWidget QToolButton::menu-indicator {
    image: url("__ARROW_DOWN__");
    subcontrol-position: center right;
    width: 14px;
    height: 14px;
    margin-right: -4px;
}
QCalendarWidget QToolButton#qt_calendar_prevmonth {
    qproperty-icon: none;
    image: url("__ARROW_LEFT__");
    width: 20px;
    height: 20px;
}
QCalendarWidget QToolButton#qt_calendar_nextmonth {
    qproperty-icon: none;
    image: url("__ARROW_RIGHT__");
    width: 20px;
    height: 20px;
}
QCalendarWidget QMenu {
    background-color: #313244;
    color: #cdd6f4;
}
QCalendarWidget QSpinBox {
    background: #45475a;
    color: #cdd6f4;
    border: 1px solid #585b70;
    border-radius: 4px;
    margin: 0px 4px;
    selection-background-color: #cba6f7;
    selection-color: #11111b;
}
QCalendarWidget QSpinBox:hover, QCalendarWidget QSpinBox:focus {
    border: 2px solid #cba6f7;
}
QCalendarWidget QSpinBox::up-button, QCalendarWidget QSpinBox::down-button {
    subcontrol-origin: border;
    width: 16px;
    background: transparent;
    border: none;
}
QCalendarWidget QSpinBox::up-arrow {
    image: url("__ARROW_UP__");
    width: 12px;
    height: 12px;
}
QCalendarWidget QSpinBox::down-arrow {
    image: url("__ARROW_DOWN__");
    width: 12px;
    height: 12px;
}
QCalendarWidget QTableView {
    background-color: #313244;
    alternate-background-color: #313244;
    color: #cdd6f4;
    selection-background-color: #cba6f7;
    selection-color: #11111b;
    border: 1px solid #45475a;
    border-top: none;
    outline: none;
    gridline-color: transparent;
    border-bottom-left-radius: 12px;
    border-bottom-right-radius: 12px;
}
QCalendarWidget QTableView:enabled {
    color: #cdd6f4;
}
QCalendarWidget QTableView:disabled {
    color: #585b70;
}
QCalendarWidget QHeaderView::section {
    background-color: #313244;
    color: #a6adc8;
    border: none;
    padding: 8px 0px;
    font-size: 12px;
    font-weight: bold;
    border-left: 1px solid #45475a;
    border-right: 1px solid #45475a;
}

QDateTimeEdit {
    background-color: #181825;
    color: #cdd6f4;
    border: 1px solid #313244;
    border-radius: 8px;
    padding: 8px 12px;
    font-size: 12px;
}
QDateTimeEdit:focus {
    border: 1px solid #cba6f7;
}

/* ═══════════════════════════════════════════════════════════════
   PROGRESS BAR
   ═══════════════════════════════════════════════════════════════ */
QProgressBar {
    background-color: #181825;
    border-radius: 6px;
    border: none;
    text-align: center;
    color: #cdd6f4;
    font-size: 10px;
}

/* ═══════════════════════════════════════════════════════════════
   TABLE
   ═══════════════════════════════════════════════════════════════ */
QTableWidget {
    background-color: #181825;
    alternate-background-color: #1a1a2e;
    color: #cdd6f4;
    border: 1px solid #313244;
    border-radius: 10px;
    gridline-color: rgba(69, 71, 90, 0.4);
    font-size: 12px;
    selection-background-color: rgba(203, 166, 247, 0.15);
    selection-color: #cdd6f4;
}
QTableWidget::item {
    padding: 6px 10px;
    border-bottom: 1px solid rgba(69, 71, 90, 0.3);
}
QTableWidget::item:hover {
    background-color: rgba(203, 166, 247, 0.08);
}
QHeaderView::section {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #24273a, stop:1 #1e1e2e);
    color: #cba6f7;
    padding: 10px 8px;
    border: none;
    border-bottom: 2px solid #cba6f7;
    font-weight: bold;
    font-size: 11px;
}
QHeaderView::section:hover {
    background-color: #313244;
}

/* ═══════════════════════════════════════════════════════════════
   DIALOGS
   ═══════════════════════════════════════════════════════════════ */
QDialog {
    background-color: #1e1e2e;
}

/* ═══════════════════════════════════════════════════════════════
   SCROLL AREA (transparent)
   ═══════════════════════════════════════════════════════════════ */
QScrollArea {
    border: none;
    background-color: transparent;
}
"""

GLOBAL_STYLESHEET = GLOBAL_STYLESHEET_RAW.replace(
    "__ARROW_DOWN__", f"{BASE_DIR}/icons/arrow_down.xpm"
).replace(
    "__ARROW_UP__", f"{BASE_DIR}/icons/arrow_up.xpm"
).replace(
    "__ARROW_LEFT__", f"{BASE_DIR}/icons/arrow_left.xpm"
).replace(
    "__ARROW_RIGHT__", f"{BASE_DIR}/icons/arrow_right.xpm"
)
