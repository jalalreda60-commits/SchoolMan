import os
import sys
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                                QLabel, QPushButton, QFrame, QStackedWidget,
                                QStatusBar, QSizePolicy, QScrollArea, QMessageBox)
from PySide6.QtCore import Qt, QSize, QTimer, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QPixmap, QFont, QIcon, QColor

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class SidebarButton(QPushButton):
    def __init__(self, icon, text, parent=None):
        super().__init__(parent)
        self.setObjectName("navBtn")
        self.setText(f"  {icon}  {text}")
        self.setCheckable(True)
        self.setFixedHeight(46)
        self.setFont(QFont("Segoe UI", 12))
        self.setCursor(Qt.PointingHandCursor)


class MainWindow(QMainWindow):
    def __init__(self, session, current_user):
        super().__init__()
        self.session = session
        self.current_user = current_user
        self.setWindowTitle(f"Le Schéma — Système de Gestion Scolaire")
        self.setMinimumSize(1200, 750)
        self.showMaximized()

        # Set window icon
        icon_path = os.path.join(BASE_DIR, 'assets', 'school_logo.ico')
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        self.pages = {}
        self.nav_buttons = []
        self.setup_ui()
        self.navigate_to(0)

    def setup_ui(self):
        from themes.dark_theme import DARK_THEME
        self.setStyleSheet(DARK_THEME)

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ── Sidebar ──────────────────────────────────────────
        self.sidebar = QFrame()
        self.sidebar.setObjectName("sidebar")
        self.sidebar.setFixedWidth(230)
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(10, 15, 10, 15)
        sidebar_layout.setSpacing(4)

        # Logo + school name
        logo_frame = QFrame()
        logo_layout = QVBoxLayout(logo_frame)
        logo_layout.setContentsMargins(5, 5, 5, 15)
        logo_layout.setSpacing(6)
        logo_label = QLabel()
        logo_path = os.path.join(BASE_DIR, 'assets', 'school_logo.png')
        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path).scaled(70, 70, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_label.setPixmap(pixmap)
        else:
            logo_label.setText("🎓")
            logo_label.setFont(QFont("Arial", 32))
        logo_label.setAlignment(Qt.AlignCenter)
        logo_layout.addWidget(logo_label)

        school_name_lbl = QLabel("Le Schéma")
        school_name_lbl.setStyleSheet("color: #FF6B00; font-size: 15px; font-weight: bold; background: transparent;")
        school_name_lbl.setAlignment(Qt.AlignCenter)
        logo_layout.addWidget(school_name_lbl)

        slogan_lbl = QLabel("Innover • Créer • Exceller")
        slogan_lbl.setStyleSheet("color: #505070; font-size: 9px; letter-spacing: 1px; background: transparent;")
        slogan_lbl.setAlignment(Qt.AlignCenter)
        logo_layout.addWidget(slogan_lbl)

        sidebar_layout.addWidget(logo_frame)

        # Divider
        div = QFrame()
        div.setFrameShape(QFrame.HLine)
        div.setStyleSheet("color: #2a2a4e; background: #2a2a4e; max-height: 1px; margin: 0 5px;")
        sidebar_layout.addWidget(div)
        sidebar_layout.addSpacing(8)

        # Navigation items
        nav_items = [
            ("📊", "Tableau de Bord"),
            ("🎓", "Élèves"),
            ("💳", "Paiements"),
            ("👥", "Employés"),
            ("📉", "Dépenses"),
            ("🚌", "Transport"),
            ("📅", "Emploi du Temps"),
            ("📊", "Rapports"),
            ("⚙", "Paramètres"),
        ]

        for i, (icon, text) in enumerate(nav_items):
            btn = SidebarButton(icon, text)
            btn.clicked.connect(lambda checked, idx=i: self.navigate_to(idx))
            sidebar_layout.addWidget(btn)
            self.nav_buttons.append(btn)

        sidebar_layout.addStretch()

        # Divider
        div2 = QFrame()
        div2.setFrameShape(QFrame.HLine)
        div2.setStyleSheet("color: #2a2a4e; background: #2a2a4e; max-height: 1px; margin: 0 5px;")
        sidebar_layout.addWidget(div2)

        # User info at bottom
        user_frame = QFrame()
        user_frame.setStyleSheet("background: #16213e; border-radius: 8px;")
        user_layout = QVBoxLayout(user_frame)
        user_layout.setContentsMargins(10, 8, 10, 8)
        user_layout.setSpacing(3)

        role_colors = {"Admin": "#FF6B00", "Comptable": "#27ae60", "Secrétaire": "#3498db"}
        role_color = role_colors.get(self.current_user.role, "#a0a0c0")

        user_name_lbl = QLabel(f"👤 {self.current_user.full_name or self.current_user.username}")
        user_name_lbl.setStyleSheet(f"color: {role_color}; font-size: 12px; font-weight: bold; background: transparent;")
        user_layout.addWidget(user_name_lbl)

        role_lbl = QLabel(f"   {self.current_user.role}")
        role_lbl.setStyleSheet("color: #606080; font-size: 10px; background: transparent;")
        user_layout.addWidget(role_lbl)

        logout_btn = QPushButton("🚪 Déconnexion")
        logout_btn.setStyleSheet("""
            QPushButton { background: transparent; color: #a0a0c0; border: none;
                         font-size: 11px; text-align: left; padding: 2px 0; }
            QPushButton:hover { color: #e74c3c; }
        """)
        logout_btn.clicked.connect(self.logout)
        user_layout.addWidget(logout_btn)
        sidebar_layout.addWidget(user_frame)

        main_layout.addWidget(self.sidebar)

        # ── Right area (topbar + content) ─────────────────────
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)

        # Top bar
        topbar = QFrame()
        topbar.setObjectName("topbar")
        topbar.setFixedHeight(55)
        topbar_layout = QHBoxLayout(topbar)
        topbar_layout.setContentsMargins(20, 0, 20, 0)
        topbar_layout.setSpacing(15)

        self.page_title_lbl = QLabel("Tableau de Bord")
        self.page_title_lbl.setStyleSheet("color: #e0e0e0; font-size: 16px; font-weight: bold;")
        topbar_layout.addWidget(self.page_title_lbl)
        topbar_layout.addStretch()

        # Quick actions in topbar
        from datetime import datetime
        self.clock_lbl = QLabel(datetime.now().strftime("%H:%M"))
        self.clock_lbl.setStyleSheet("color: #FF6B00; font-size: 18px; font-weight: bold;")
        topbar_layout.addWidget(self.clock_lbl)

        # Update clock every second
        self.clock_timer = QTimer()
        self.clock_timer.timeout.connect(self._update_clock)
        self.clock_timer.start(1000)

        topbar_layout.addWidget(QLabel("|"))

        date_lbl = QLabel(datetime.now().strftime("%d/%m/%Y"))
        date_lbl.setStyleSheet("color: #a0a0c0; font-size: 12px;")
        topbar_layout.addWidget(date_lbl)

        right_layout.addWidget(topbar)

        # Content area (stacked pages)
        self.stack = QStackedWidget()
        self.stack.setObjectName("contentArea")
        right_layout.addWidget(self.stack)

        main_layout.addWidget(right_widget)

        # Status bar
        status = self.statusBar()
        status.showMessage(f"✅ Connecté en tant que {self.current_user.username} ({self.current_user.role})  |  Base de données: school.db")

        # Initialize pages lazily
        self._init_pages()

    def _init_pages(self):
        """Initialize all page widgets and add them to the stack."""
        from ui.dashboard import DashboardWidget
        from ui.students import StudentsWidget
        from ui.payments import PaymentsWidget
        from ui.employees import EmployeesWidget
        from ui.expenses import ExpensesWidget
        from ui.transport_timetable import TransportWidget, TimetableWidget
        from ui.reports import ReportsWidget
        from ui.settings import SettingsWidget

        pages_classes = [
            ("Tableau de Bord", DashboardWidget),
            ("Gestion des Élèves", StudentsWidget),
            ("Gestion des Paiements", PaymentsWidget),
            ("Gestion des Employés", EmployeesWidget),
            ("Gestion des Dépenses", ExpensesWidget),
            ("Transport", TransportWidget),
            ("Emploi du Temps", TimetableWidget),
            ("Rapports & Exports", ReportsWidget),
            ("Paramètres", SettingsWidget),
        ]

        for i, (title, PageClass) in enumerate(pages_classes):
            try:
                widget = PageClass(self.session, self.current_user)
            except Exception as e:
                widget = QLabel(f"Erreur chargement: {e}")
                widget.setAlignment(Qt.AlignCenter)
                widget.setStyleSheet("color: #e74c3c; font-size: 14px;")
            self.stack.addWidget(widget)
            self.pages[i] = (title, widget)

    def navigate_to(self, index):
        # Update nav button states
        for i, btn in enumerate(self.nav_buttons):
            btn.setChecked(i == index)

        # Switch stack page
        self.stack.setCurrentIndex(index)

        # Update topbar title
        page_titles = [
            "📊 Tableau de Bord", "🎓 Gestion des Élèves", "💳 Gestion des Paiements",
            "👥 Gestion des Employés", "📉 Gestion des Dépenses", "🚌 Transport",
            "📅 Emploi du Temps", "📊 Rapports & Exports", "⚙ Paramètres"
        ]
        if index < len(page_titles):
            self.page_title_lbl.setText(page_titles[index])

        # Refresh page if it has a load method
        widget = self.stack.currentWidget()
        if hasattr(widget, 'load_data'):
            try:
                widget.load_data()
            except:
                pass

    def _update_clock(self):
        from datetime import datetime
        self.clock_lbl.setText(datetime.now().strftime("%H:%M"))

    def logout(self):
        reply = QMessageBox.question(self, "Déconnexion",
            "Voulez-vous vous déconnecter?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.close()
            # Re-show login
            from ui.login_window import LoginWindow
            self.login_win = LoginWindow(self.session)
            self.login_win.login_successful.connect(self._on_login)
            self.login_win.show()

    def _on_login(self, user):
        self.current_user = user
        self.show()
        self.navigate_to(0)
