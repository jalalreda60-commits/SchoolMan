import os
import shutil
from datetime import datetime
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
                                QPushButton, QTableWidget, QTableWidgetItem, QDialog,
                                QFormLayout, QComboBox, QMessageBox, QFrame, QHeaderView,
                                QAbstractItemView, QDoubleSpinBox, QTabWidget, QGroupBox,
                                QTextEdit, QScrollArea, QFileDialog)
from PySide6.QtCore import Qt

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class SettingsWidget(QWidget):
    def __init__(self, session, current_user):
        super().__init__()
        self.session = session
        self.current_user = current_user
        self.setup_ui()
        self.load_settings()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(15)

        title = QLabel("⚙ Paramètres")
        title.setStyleSheet("color: #e0e0e0; font-size: 22px; font-weight: bold;")
        layout.addWidget(title)

        tabs = QTabWidget()
        layout.addWidget(tabs)

        # School tab
        school_tab = QWidget()
        school_layout = QVBoxLayout(school_tab)
        school_layout.setContentsMargins(20, 20, 20, 20)
        school_layout.setSpacing(12)

        school_group = QGroupBox("Informations de l'établissement")
        school_form = QFormLayout(school_group)
        school_form.setSpacing(10)
        school_form.setLabelAlignment(Qt.AlignRight)

        def lbl(text):
            l = QLabel(text)
            l.setStyleSheet("color: #a0a0c0; font-size: 12px;")
            return l
        def field(ph=""):
            f = QLineEdit()
            f.setPlaceholderText(ph)
            f.setFixedHeight(38)
            return f

        self.school_name = field("Nom de l'école")
        self.school_address = field("Adresse")
        self.school_phone = field("Téléphone")
        self.school_email = field("Email")
        self.currency = QComboBox()
        self.currency.setFixedHeight(38)
        self.currency.addItems(["MAD", "EUR", "USD", "XOF"])

        school_form.addRow(lbl("Nom de l'école:"), self.school_name)
        school_form.addRow(lbl("Adresse:"), self.school_address)
        school_form.addRow(lbl("Téléphone:"), self.school_phone)
        school_form.addRow(lbl("Email:"), self.school_email)
        school_form.addRow(lbl("Devise:"), self.currency)

        school_layout.addWidget(school_group)

        fees_group = QGroupBox("Frais par défaut")
        fees_form = QFormLayout(fees_group)
        fees_form.setSpacing(10)
        fees_form.setLabelAlignment(Qt.AlignRight)

        self.transport_fee = QDoubleSpinBox()
        self.transport_fee.setRange(0, 99999)
        self.transport_fee.setDecimals(2)
        self.transport_fee.setSuffix(" MAD")
        self.transport_fee.setFixedHeight(38)

        self.insurance_fee = QDoubleSpinBox()
        self.insurance_fee.setRange(0, 99999)
        self.insurance_fee.setDecimals(2)
        self.insurance_fee.setSuffix(" MAD")
        self.insurance_fee.setFixedHeight(38)

        fees_form.addRow(lbl("Frais transport:"), self.transport_fee)
        fees_form.addRow(lbl("Frais assurance:"), self.insurance_fee)

        school_layout.addWidget(fees_group)

        save_btn = QPushButton("💾 Enregistrer les paramètres")
        save_btn.setObjectName("primaryBtn")
        save_btn.setFixedWidth(250)
        save_btn.clicked.connect(self.save_settings)
        school_layout.addWidget(save_btn)
        school_layout.addStretch()

        tabs.addTab(school_tab, "🏫 École")

        # Backup tab
        backup_tab = QWidget()
        backup_layout = QVBoxLayout(backup_tab)
        backup_layout.setContentsMargins(20, 20, 20, 20)
        backup_layout.setSpacing(12)

        backup_group = QGroupBox("Sauvegarde de la base de données")
        bg_layout = QVBoxLayout(backup_group)
        bg_layout.setSpacing(10)

        info_lbl = QLabel(f"📁 Base de données: {os.path.join(BASE_DIR, 'school.db')}")
        info_lbl.setStyleSheet("color: #a0a0c0; font-size: 12px;")
        bg_layout.addWidget(info_lbl)

        backup_btn = QPushButton("💾 Créer une sauvegarde maintenant")
        backup_btn.setObjectName("primaryBtn")
        backup_btn.setFixedWidth(280)
        backup_btn.clicked.connect(self.create_backup)
        bg_layout.addWidget(backup_btn)

        restore_btn = QPushButton("📂 Restaurer une sauvegarde")
        restore_btn.setObjectName("secondaryBtn")
        restore_btn.setFixedWidth(280)
        restore_btn.clicked.connect(self.restore_backup)
        bg_layout.addWidget(restore_btn)

        self.backup_log = QTextEdit()
        self.backup_log.setReadOnly(True)
        self.backup_log.setMaximumHeight(200)
        self.backup_log.setPlaceholderText("Historique des sauvegardes...")
        bg_layout.addWidget(self.backup_log)
        self.load_backup_log()

        backup_layout.addWidget(backup_group)
        backup_layout.addStretch()

        tabs.addTab(backup_tab, "💾 Sauvegarde")

        # Users tab (admin only)
        if self.current_user.role == 'Admin':
            users_tab = QWidget()
            users_layout = QVBoxLayout(users_tab)
            users_layout.setContentsMargins(20, 20, 20, 20)
            users_layout.setSpacing(12)

            add_user_btn = QPushButton("➕ Nouvel Utilisateur")
            add_user_btn.setObjectName("primaryBtn")
            add_user_btn.setFixedWidth(200)
            add_user_btn.clicked.connect(self.add_user)
            users_layout.addWidget(add_user_btn)

            self.users_table = QTableWidget()
            self.users_table.setColumnCount(5)
            self.users_table.setHorizontalHeaderLabels(["Utilisateur", "Nom complet", "Rôle", "Statut", "Dernière connexion"])
            self.users_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            self.users_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
            self.users_table.verticalHeader().setVisible(False)
            self.users_table.setShowGrid(False)
            users_layout.addWidget(self.users_table)
            self.load_users()

            tabs.addTab(users_tab, "👤 Utilisateurs")

    def load_settings(self):
        from models.database import Setting
        def get(key, default=""):
            s = self.session.query(Setting).filter_by(key=key).first()
            return s.value if s else default

        self.school_name.setText(get('school_name', 'Le Schéma'))
        self.school_address.setText(get('school_address', ''))
        self.school_phone.setText(get('school_phone', ''))
        self.school_email.setText(get('school_email', ''))
        idx = self.currency.findText(get('currency', 'MAD'))
        if idx >= 0:
            self.currency.setCurrentIndex(idx)
        self.transport_fee.setValue(float(get('transport_fee', '300')))
        self.insurance_fee.setValue(float(get('insurance_fee', '200')))

    def save_settings(self):
        from models.database import Setting
        from datetime import datetime

        def set_val(key, value):
            s = self.session.query(Setting).filter_by(key=key).first()
            if s:
                s.value = value
                s.updated_at = datetime.now()
            else:
                self.session.add(Setting(key=key, value=value))

        set_val('school_name', self.school_name.text())
        set_val('school_address', self.school_address.text())
        set_val('school_phone', self.school_phone.text())
        set_val('school_email', self.school_email.text())
        set_val('currency', self.currency.currentText())
        set_val('transport_fee', str(self.transport_fee.value()))
        set_val('insurance_fee', str(self.insurance_fee.value()))
        self.session.commit()
        QMessageBox.information(self, "Succès", "✅ Paramètres enregistrés avec succès!")

    def create_backup(self):
        backups_dir = os.path.join(BASE_DIR, 'backups')
        os.makedirs(backups_dir, exist_ok=True)
        db_path = os.path.join(BASE_DIR, 'school.db')
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = os.path.join(backups_dir, f'school_backup_{timestamp}.db')
        try:
            shutil.copy2(db_path, backup_path)
            self.backup_log.append(f"✅ {datetime.now().strftime('%d/%m/%Y %H:%M')} - Sauvegarde créée: {os.path.basename(backup_path)}")
            QMessageBox.information(self, "Succès", f"✅ Sauvegarde créée:\n{backup_path}")
        except Exception as e:
            QMessageBox.warning(self, "Erreur", f"Erreur lors de la sauvegarde:\n{e}")

    def restore_backup(self):
        backups_dir = os.path.join(BASE_DIR, 'backups')
        file, _ = QFileDialog.getOpenFileName(self, "Sélectionner une sauvegarde", backups_dir, "Base de données (*.db)")
        if file:
            reply = QMessageBox.question(self, "Confirmer",
                "⚠ Cette action remplacera la base de données actuelle. Continuer?",
                QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                db_path = os.path.join(BASE_DIR, 'school.db')
                try:
                    shutil.copy2(file, db_path)
                    self.backup_log.append(f"🔄 {datetime.now().strftime('%d/%m/%Y %H:%M')} - Restauration depuis: {os.path.basename(file)}")
                    QMessageBox.information(self, "Succès", "✅ Base de données restaurée. Redémarrez l'application.")
                except Exception as e:
                    QMessageBox.warning(self, "Erreur", f"Erreur lors de la restauration:\n{e}")

    def load_backup_log(self):
        backups_dir = os.path.join(BASE_DIR, 'backups')
        if os.path.exists(backups_dir):
            files = sorted(os.listdir(backups_dir), reverse=True)
            for f in files[:10]:
                if f.endswith('.db'):
                    path = os.path.join(backups_dir, f)
                    size = os.path.getsize(path) / 1024
                    self.backup_log.append(f"📁 {f} ({size:.1f} KB)")

    def add_user(self):
        from hashlib import sha256
        from models.database import User

        dlg = QDialog(self)
        dlg.setWindowTitle("Nouvel Utilisateur")
        dlg.setMinimumSize(380, 300)
        layout = QVBoxLayout(dlg)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        form = QFormLayout()
        form.setSpacing(10)
        form.setLabelAlignment(Qt.AlignRight)

        def lbl(text):
            l = QLabel(text)
            l.setStyleSheet("color: #a0a0c0; font-size: 12px;")
            return l

        username_f = QLineEdit()
        username_f.setFixedHeight(38)
        fullname_f = QLineEdit()
        fullname_f.setFixedHeight(38)
        password_f = QLineEdit()
        password_f.setEchoMode(QLineEdit.Password)
        password_f.setFixedHeight(38)
        role_combo = QComboBox()
        role_combo.setFixedHeight(38)
        role_combo.addItems(["Admin", "Comptable", "Secrétaire"])

        form.addRow(lbl("Nom d'utilisateur:"), username_f)
        form.addRow(lbl("Nom complet:"), fullname_f)
        form.addRow(lbl("Mot de passe:"), password_f)
        form.addRow(lbl("Rôle:"), role_combo)
        layout.addLayout(form)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        cancel_btn = QPushButton("Annuler")
        cancel_btn.setObjectName("secondaryBtn")
        cancel_btn.clicked.connect(dlg.reject)
        save_btn = QPushButton("💾 Créer")
        save_btn.setObjectName("primaryBtn")
        layout.addLayout(btn_layout)
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(save_btn)

        def do_save():
            if not username_f.text().strip() or not password_f.text():
                QMessageBox.warning(dlg, "Erreur", "Identifiant et mot de passe requis.")
                return
            existing = self.session.query(User).filter_by(username=username_f.text().strip()).first()
            if existing:
                QMessageBox.warning(dlg, "Erreur", "Cet identifiant existe déjà.")
                return
            user = User(
                username=username_f.text().strip(),
                password=sha256(password_f.text().encode()).hexdigest(),
                full_name=fullname_f.text().strip(),
                role=role_combo.currentText()
            )
            self.session.add(user)
            self.session.commit()
            dlg.accept()
            self.load_users()
            QMessageBox.information(self, "Succès", "✅ Utilisateur créé!")

        save_btn.clicked.connect(do_save)
        dlg.exec()

    def load_users(self):
        if not hasattr(self, 'users_table'):
            return
        from models.database import User
        users = self.session.query(User).all()
        self.users_table.setRowCount(0)
        for u in users:
            row = self.users_table.rowCount()
            self.users_table.insertRow(row)
            items = [
                u.username, u.full_name or "—", u.role,
                "✅ Actif" if u.is_active else "❌ Inactif",
                u.last_login.strftime("%d/%m/%Y %H:%M") if u.last_login else "—"
            ]
            for col, text in enumerate(items):
                item = QTableWidgetItem(text)
                item.setTextAlignment(Qt.AlignCenter)
                self.users_table.setItem(row, col, item)
            self.users_table.setRowHeight(row, 38)
