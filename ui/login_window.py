import sys
import os
from hashlib import sha256
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                                QLineEdit, QPushButton, QCheckBox, QFrame, QMessageBox)
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QPoint, Signal
from PySide6.QtGui import QPixmap, QFont, QColor

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class LoginWindow(QWidget):
    login_successful = Signal(object)

    def __init__(self, session):
        super().__init__()
        self.session = session
        self.setWindowTitle("Le Schéma - Connexion")
        self.setFixedSize(460, 600)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self._drag_pos = None
        self.setup_ui()
        self.animate_in()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Card frame
        self.card = QFrame()
        self.card.setObjectName("loginCard")
        self.card.setStyleSheet("""
            QFrame#loginCard {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1a1a2e, stop:1 #16213e);
                border-radius: 20px;
                border: 1px solid #2a2a4e;
            }
        """)
        card_layout = QVBoxLayout(self.card)
        card_layout.setContentsMargins(40, 30, 40, 30)
        card_layout.setSpacing(15)

        # Close button
        close_btn = QPushButton("✕")
        close_btn.setFixedSize(30, 30)
        close_btn.setStyleSheet("""
            QPushButton { background: #c0392b; color: white; border-radius: 15px;
                         border: none; font-weight: bold; font-size: 12px; }
            QPushButton:hover { background: #e74c3c; }
        """)
        close_btn.clicked.connect(sys.exit)
        close_layout = QHBoxLayout()
        close_layout.addStretch()
        close_layout.addWidget(close_btn)
        card_layout.addLayout(close_layout)

        # Logo
        logo_label = QLabel()
        logo_path = os.path.join(BASE_DIR, 'assets', 'school_logo.png')
        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path).scaled(120, 120, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_label.setPixmap(pixmap)
        else:
            logo_label.setText("🎓")
            logo_label.setFont(QFont("Arial", 48))
        logo_label.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(logo_label)

        # School name
        school_label = QLabel("Le Schéma")
        school_label.setStyleSheet("color: #FF6B00; font-size: 24px; font-weight: bold;")
        school_label.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(school_label)

        slogan_label = QLabel("Innover • Créer • Exceller")
        slogan_label.setStyleSheet("color: #a0a0c0; font-size: 11px; letter-spacing: 2px;")
        slogan_label.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(slogan_label)

        # Divider
        div = QFrame()
        div.setFrameShape(QFrame.HLine)
        div.setStyleSheet("color: #2a2a4e;")
        card_layout.addWidget(div)

        # Title
        title = QLabel("CONNEXION")
        title.setStyleSheet("color: #e0e0e0; font-size: 14px; font-weight: bold; letter-spacing: 3px;")
        title.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(title)

        # Username
        user_label = QLabel("Nom d'utilisateur")
        user_label.setStyleSheet("color: #a0a0c0; font-size: 11px; margin-bottom: -8px;")
        card_layout.addWidget(user_label)
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Entrez votre identifiant")
        self.username_input.setText("admin")
        self.username_input.setFixedHeight(45)
        self.username_input.setStyleSheet("""
            QLineEdit {
                background-color: #0f0f23;
                color: #e0e0e0;
                border: 1px solid #3a3a6e;
                border-radius: 8px;
                padding: 0 15px;
                font-size: 14px;
            }
            QLineEdit:focus { border: 1px solid #FF6B00; }
        """)
        card_layout.addWidget(self.username_input)

        # Password
        pass_label = QLabel("Mot de passe")
        pass_label.setStyleSheet("color: #a0a0c0; font-size: 11px; margin-bottom: -8px;")
        card_layout.addWidget(pass_label)
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Entrez votre mot de passe")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setText("admin123")
        self.password_input.setFixedHeight(45)
        self.password_input.setStyleSheet("""
            QLineEdit {
                background-color: #0f0f23;
                color: #e0e0e0;
                border: 1px solid #3a3a6e;
                border-radius: 8px;
                padding: 0 15px;
                font-size: 14px;
            }
            QLineEdit:focus { border: 1px solid #FF6B00; }
        """)
        self.password_input.returnPressed.connect(self.do_login)
        card_layout.addWidget(self.password_input)

        # Remember me
        remember_layout = QHBoxLayout()
        self.remember_cb = QCheckBox("Se souvenir de moi")
        self.remember_cb.setStyleSheet("color: #a0a0c0; font-size: 11px;")
        remember_layout.addWidget(self.remember_cb)
        remember_layout.addStretch()
        card_layout.addLayout(remember_layout)

        # Error label
        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: #e74c3c; font-size: 11px;")
        self.error_label.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(self.error_label)

        # Login button
        self.login_btn = QPushButton("CONNEXION")
        self.login_btn.setFixedHeight(48)
        self.login_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #FF6B00, stop:1 #FF8C00);
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 15px;
                font-weight: bold;
                letter-spacing: 2px;
            }
            QPushButton:hover { background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #FF8C00, stop:1 #FFA500); }
            QPushButton:pressed { background: #e55a00; }
        """)
        self.login_btn.clicked.connect(self.do_login)
        card_layout.addWidget(self.login_btn)

        # Footer
        footer = QLabel("© 2026 Le Schéma • Système de Gestion Scolaire")
        footer.setStyleSheet("color: #404060; font-size: 9px;")
        footer.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(footer)

        main_layout.addWidget(self.card)

    def animate_in(self):
        self.setWindowOpacity(0)
        self.anim = QPropertyAnimation(self, b"windowOpacity")
        self.anim.setDuration(500)
        self.anim.setStartValue(0)
        self.anim.setEndValue(1)
        self.anim.setEasingCurve(QEasingCurve.OutCubic)
        self.anim.start()

    def do_login(self):
        from models.database import User
        username = self.username_input.text().strip()
        password = self.password_input.text()
        if not username or not password:
            self.error_label.setText("Veuillez remplir tous les champs")
            return
        hashed = sha256(password.encode()).hexdigest()
        user = self.session.query(User).filter_by(username=username, password=hashed, is_active=True).first()
        if user:
            from datetime import datetime
            user.last_login = datetime.now()
            self.session.commit()
            self.login_successful.emit(user)
            self.close()
        else:
            self.error_label.setText("Identifiant ou mot de passe incorrect")
            self.shake()

    def shake(self):
        x = self.x()
        y = self.y()
        for i in range(6):
            QTimer.singleShot(i * 50, lambda dx=((i%2)*2-1)*10: self.move(x + dx, y))
        QTimer.singleShot(300, lambda: self.move(x, y))

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, event):
        if self._drag_pos and event.buttons() == Qt.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_pos)

    def mouseReleaseEvent(self, event):
        self._drag_pos = None
