# -*- coding: utf-8 -*-
"""
Global QSS stylesheet for TaskSenseAI — Catppuccin Mocha + glassmorphism
"""

GLOBAL_STYLESHEET = """
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
    background-color: #313244;
    color: #cdd6f4;
    border: 1px solid #585b70;
    border-radius: 8px;
    padding: 8px 28px;
    min-width: 80px;
    min-height: 28px;
    font-size: 12px;
    font-weight: bold;
}
QMessageBox QPushButton:hover {
    background-color: #45475a;
    border: 1px solid #cba6f7;
    color: #cdd6f4;
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
    padding: 8px 12px;
    font-size: 12px;
}
QComboBox:hover, QComboBox:focus {
    border: 1px solid #585b70;
}
QComboBox::drop-down {
    border: none;
    width: 24px;
}
QComboBox QAbstractItemView {
    background-color: #1e1e2e;
    color: #cdd6f4;
    border: 1px solid #313244;
    border-radius: 6px;
    selection-background-color: #313244;
    padding: 4px;
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
