DARK_THEME = """
QMainWindow, QDialog {
    background-color: #0f0f23;
    color: #e0e0e0;
}
QWidget {
    background-color: #0f0f23;
    color: #e0e0e0;
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 13px;
}
QFrame#sidebar {
    background-color: #1a1a2e;
    border-right: 1px solid #2a2a4e;
}
QFrame#topbar {
    background-color: #16213e;
    border-bottom: 1px solid #2a2a4e;
}
QFrame#card {
    background-color: #1a1a2e;
    border: 1px solid #2a2a4e;
    border-radius: 12px;
}
QFrame#contentArea {
    background-color: #0f0f23;
}
QPushButton#navBtn {
    background-color: transparent;
    color: #a0a0c0;
    border: none;
    border-radius: 8px;
    padding: 10px 15px;
    text-align: left;
    font-size: 13px;
}
QPushButton#navBtn:hover {
    background-color: #2a2a4e;
    color: #FF6B00;
}
QPushButton#navBtn:checked {
    background-color: rgba(255, 107, 0, 0.15);
    color: #FF6B00;
    border-left: 3px solid #FF6B00;
}
QPushButton#primaryBtn {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #FF6B00, stop:1 #FF8C00);
    color: white;
    border: none;
    border-radius: 8px;
    padding: 10px 20px;
    font-weight: bold;
    font-size: 13px;
}
QPushButton#primaryBtn:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #FF8C00, stop:1 #FFA500);
}
QPushButton#primaryBtn:pressed {
    background: #e55a00;
}
QPushButton#dangerBtn {
    background-color: #c0392b;
    color: white;
    border: none;
    border-radius: 8px;
    padding: 8px 16px;
    font-weight: bold;
}
QPushButton#dangerBtn:hover {
    background-color: #e74c3c;
}
QPushButton#successBtn {
    background-color: #27ae60;
    color: white;
    border: none;
    border-radius: 8px;
    padding: 8px 16px;
    font-weight: bold;
}
QPushButton#successBtn:hover {
    background-color: #2ecc71;
}
QPushButton#secondaryBtn {
    background-color: #2a2a4e;
    color: #e0e0e0;
    border: 1px solid #3a3a6e;
    border-radius: 8px;
    padding: 8px 16px;
}
QPushButton#secondaryBtn:hover {
    background-color: #3a3a6e;
}
QLineEdit, QComboBox, QDateEdit, QSpinBox, QDoubleSpinBox, QTextEdit {
    background-color: #1e1e3a;
    color: #e0e0e0;
    border: 1px solid #3a3a6e;
    border-radius: 6px;
    padding: 8px 10px;
    font-size: 13px;
}
QLineEdit:focus, QComboBox:focus, QDateEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QTextEdit:focus {
    border: 1px solid #FF6B00;
    background-color: #1e1e3a;
}
QComboBox::drop-down {
    border: none;
    width: 20px;
}
QComboBox::down-arrow {
    image: none;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 6px solid #FF6B00;
}
QComboBox QAbstractItemView {
    background-color: #1e1e3a;
    border: 1px solid #3a3a6e;
    selection-background-color: #FF6B00;
    color: #e0e0e0;
}
QTableWidget {
    background-color: #1a1a2e;
    alternate-background-color: #1e1e3a;
    color: #e0e0e0;
    gridline-color: #2a2a4e;
    border: 1px solid #2a2a4e;
    border-radius: 8px;
    selection-background-color: rgba(255, 107, 0, 0.2);
}
QTableWidget::item:selected {
    background-color: rgba(255, 107, 0, 0.3);
    color: white;
}
QHeaderView::section {
    background-color: #16213e;
    color: #FF6B00;
    padding: 10px 5px;
    border: none;
    border-bottom: 2px solid #FF6B00;
    font-weight: bold;
    font-size: 12px;
}
QScrollBar:vertical {
    background: #1a1a2e;
    width: 8px;
    border-radius: 4px;
}
QScrollBar::handle:vertical {
    background: #FF6B00;
    border-radius: 4px;
    min-height: 20px;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}
QLabel#pageTitle {
    color: #e0e0e0;
    font-size: 22px;
    font-weight: bold;
}
QLabel#statValue {
    color: #FF6B00;
    font-size: 28px;
    font-weight: bold;
}
QLabel#statLabel {
    color: #a0a0c0;
    font-size: 11px;
}
QLabel#sectionTitle {
    color: #FF6B00;
    font-size: 15px;
    font-weight: bold;
}
QTabWidget::pane {
    border: 1px solid #2a2a4e;
    border-radius: 8px;
    background-color: #1a1a2e;
}
QTabBar::tab {
    background-color: #1e1e3a;
    color: #a0a0c0;
    padding: 8px 20px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    margin-right: 2px;
}
QTabBar::tab:selected {
    background-color: #FF6B00;
    color: white;
}
QTabBar::tab:hover {
    background-color: #2a2a4e;
    color: #FF6B00;
}
QMessageBox {
    background-color: #1a1a2e;
    color: #e0e0e0;
}
QMessageBox QPushButton {
    background-color: #FF6B00;
    color: white;
    border-radius: 6px;
    padding: 6px 16px;
    min-width: 80px;
}
QCheckBox {
    color: #e0e0e0;
    spacing: 8px;
}
QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border: 2px solid #3a3a6e;
    border-radius: 4px;
    background-color: #1e1e3a;
}
QCheckBox::indicator:checked {
    background-color: #FF6B00;
    border-color: #FF6B00;
}
QGroupBox {
    border: 1px solid #2a2a4e;
    border-radius: 8px;
    margin-top: 12px;
    padding-top: 8px;
    color: #FF6B00;
    font-weight: bold;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 5px;
}
QSplitter::handle {
    background-color: #2a2a4e;
}
QStatusBar {
    background-color: #16213e;
    color: #a0a0c0;
    border-top: 1px solid #2a2a4e;
}
QProgressBar {
    border: 1px solid #2a2a4e;
    border-radius: 4px;
    background-color: #1e1e3a;
    text-align: center;
    color: white;
}
QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #FF6B00, stop:1 #FF8C00);
    border-radius: 3px;
}
"""
