import os
from datetime import datetime, date
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
                                QPushButton, QTableWidget, QTableWidgetItem, QDialog,
                                QFormLayout, QComboBox, QDateEdit, QTextEdit, QCheckBox,
                                QFileDialog, QMessageBox, QFrame, QHeaderView, QSplitter,
                                QAbstractItemView, QSpinBox, QDoubleSpinBox, QScrollArea)
from PySide6.QtCore import Qt, QDate, QSortFilterProxyModel
from PySide6.QtGui import QPixmap, QFont, QIcon

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLASSES = ['PS','MS','GS','CP','CE1','CE2','CM1','CM2','6EME','1AC','2AC','3AC','TC','1BAC','2BAC']


class StudentDialog(QDialog):
    def __init__(self, session, student=None, parent=None):
        super().__init__(parent)
        self.session = session
        self.student = student
        self.photo_path = None
        self.setWindowTitle("Modifier Élève" if student else "Nouvel Élève")
        self.setMinimumSize(700, 650)
        self.setup_ui()
        if student:
            self.populate(student)

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        title = QLabel("👤 " + ("Modifier Élève" if self.student else "Nouvel Élève"))
        title.setStyleSheet("color: #FF6B00; font-size: 18px; font-weight: bold;")
        layout.addWidget(title)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; }")
        content = QWidget()
        form_layout = QFormLayout(content)
        form_layout.setSpacing(10)
        form_layout.setLabelAlignment(Qt.AlignRight)

        def lbl(text):
            l = QLabel(text)
            l.setStyleSheet("color: #a0a0c0; font-size: 12px;")
            return l

        def field(placeholder=""):
            f = QLineEdit()
            f.setPlaceholderText(placeholder)
            f.setFixedHeight(38)
            return f

        self.first_name = field("Prénom")
        self.last_name = field("Nom")
        self.gender = QComboBox()
        self.gender.addItems(["Masculin", "Féminin"])
        self.gender.setFixedHeight(38)
        self.birth_date = QDateEdit()
        self.birth_date.setCalendarPopup(True)
        self.birth_date.setDate(QDate(2015, 1, 1))
        self.birth_date.setFixedHeight(38)
        self.address = QTextEdit()
        self.address.setMaximumHeight(70)
        self.parent_name = field("Nom du parent")
        self.parent_phone = field("+212 000 000 000")
        self.emergency_phone = field("+212 000 000 000")
        self.class_combo = QComboBox()
        self.class_combo.setFixedHeight(38)
        self.class_combo.addItem("-- Sélectionner --", None)
        from models.database import Class
        classes = self.session.query(Class).all()
        for cls in classes:
            self.class_combo.addItem(cls.name, cls.id)
        self.class_combo.currentIndexChanged.connect(self.update_fee)

        self.monthly_fee = QDoubleSpinBox()
        self.monthly_fee.setRange(0, 99999)
        self.monthly_fee.setDecimals(2)
        self.monthly_fee.setSuffix(" MAD")
        self.monthly_fee.setFixedHeight(38)
        self.has_transport = QCheckBox("Oui")
        self.insurance_paid = QCheckBox("Assurance payée")
        self.notes = QTextEdit()
        self.notes.setMaximumHeight(70)

        # Photo
        photo_layout = QHBoxLayout()
        self.photo_label = QLabel()
        self.photo_label.setFixedSize(80, 80)
        self.photo_label.setStyleSheet("border: 2px dashed #3a3a6e; border-radius: 8px; background: #1e1e3a;")
        self.photo_label.setAlignment(Qt.AlignCenter)
        self.photo_label.setText("📷")
        photo_layout.addWidget(self.photo_label)
        photo_btn = QPushButton("Choisir Photo")
        photo_btn.setObjectName("secondaryBtn")
        photo_btn.clicked.connect(self.choose_photo)
        photo_layout.addWidget(photo_btn)
        photo_layout.addStretch()
        photo_frame = QFrame()
        photo_frame.setLayout(photo_layout)

        form_layout.addRow(lbl("Photo:"), photo_frame)
        form_layout.addRow(lbl("Prénom *:"), self.first_name)
        form_layout.addRow(lbl("Nom *:"), self.last_name)
        form_layout.addRow(lbl("Genre:"), self.gender)
        form_layout.addRow(lbl("Date naissance:"), self.birth_date)
        form_layout.addRow(lbl("Adresse:"), self.address)
        form_layout.addRow(lbl("Parent:"), self.parent_name)
        form_layout.addRow(lbl("Tél. Parent:"), self.parent_phone)
        form_layout.addRow(lbl("Tél. Urgence:"), self.emergency_phone)
        form_layout.addRow(lbl("Classe *:"), self.class_combo)
        form_layout.addRow(lbl("Frais Mensuel:"), self.monthly_fee)
        form_layout.addRow(lbl("Transport:"), self.has_transport)
        form_layout.addRow(lbl("Assurance:"), self.insurance_paid)
        form_layout.addRow(lbl("Notes:"), self.notes)

        scroll.setWidget(content)
        layout.addWidget(scroll)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        cancel_btn = QPushButton("Annuler")
        cancel_btn.setObjectName("secondaryBtn")
        cancel_btn.clicked.connect(self.reject)
        save_btn = QPushButton("💾 Enregistrer")
        save_btn.setObjectName("primaryBtn")
        save_btn.clicked.connect(self.save)
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(save_btn)
        layout.addLayout(btn_layout)

    def update_fee(self):
        from models.database import Class
        class_id = self.class_combo.currentData()
        if class_id:
            cls = self.session.query(Class).get(class_id)
            if cls:
                self.monthly_fee.setValue(cls.monthly_fee)

    def choose_photo(self):
        path, _ = QFileDialog.getOpenFileName(self, "Choisir Photo", "", "Images (*.png *.jpg *.jpeg)")
        if path:
            self.photo_path = path
            pixmap = QPixmap(path).scaled(80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.photo_label.setPixmap(pixmap)

    def populate(self, student):
        self.first_name.setText(student.first_name)
        self.last_name.setText(student.last_name)
        idx = self.gender.findText(student.gender or "Masculin")
        if idx >= 0:
            self.gender.setCurrentIndex(idx)
        if student.birth_date:
            self.birth_date.setDate(QDate(student.birth_date.year, student.birth_date.month, student.birth_date.day))
        self.address.setText(student.address or "")
        self.parent_name.setText(student.parent_name or "")
        self.parent_phone.setText(student.parent_phone or "")
        self.emergency_phone.setText(student.emergency_phone or "")
        for i in range(self.class_combo.count()):
            if self.class_combo.itemData(i) == student.class_id:
                self.class_combo.setCurrentIndex(i)
                break
        self.monthly_fee.setValue(student.monthly_fee or 0)
        self.has_transport.setChecked(student.has_transport)
        self.insurance_paid.setChecked(student.insurance_paid)
        self.notes.setText(student.notes or "")
        if student.photo:
            full_path = os.path.join(BASE_DIR, student.photo) if not os.path.isabs(student.photo) else student.photo
            if os.path.exists(full_path):
                pixmap = QPixmap(full_path).scaled(80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.photo_label.setPixmap(pixmap)

    def save(self):
        if not self.first_name.text().strip() or not self.last_name.text().strip():
            QMessageBox.warning(self, "Erreur", "Le prénom et le nom sont obligatoires.")
            return
        if self.class_combo.currentData() is None:
            QMessageBox.warning(self, "Erreur", "Veuillez sélectionner une classe.")
            return

        from models.database import Student, Setting
        import random, string

        if self.student:
            s = self.student
        else:
            s = Student()
            # Generate student code
            year = datetime.now().year
            counter = ''.join(random.choices(string.digits, k=4))
            s.student_code = f"STU-{year}-{counter}"
            self.session.add(s)

        s.first_name = self.first_name.text().strip()
        s.last_name = self.last_name.text().strip()
        s.gender = self.gender.currentText()
        bd = self.birth_date.date()
        s.birth_date = date(bd.year(), bd.month(), bd.day())
        s.address = self.address.toPlainText()
        s.parent_name = self.parent_name.text().strip()
        s.parent_phone = self.parent_phone.text().strip()
        s.emergency_phone = self.emergency_phone.text().strip()
        s.class_id = self.class_combo.currentData()
        s.monthly_fee = self.monthly_fee.value()
        s.has_transport = self.has_transport.isChecked()
        s.insurance_paid = self.insurance_paid.isChecked()
        s.notes = self.notes.toPlainText()

        if self.photo_path:
            import shutil
            photos_dir = os.path.join(BASE_DIR, 'assets', 'photos')
            os.makedirs(photos_dir, exist_ok=True)
            ext = os.path.splitext(self.photo_path)[1]
            dest = os.path.join(photos_dir, f"{s.student_code}{ext}")
            shutil.copy2(self.photo_path, dest)
            s.photo = os.path.join('assets', 'photos', f"{s.student_code}{ext}")

        self.session.commit()
        self.accept()


class StudentsWidget(QWidget):
    def __init__(self, session, current_user):
        super().__init__()
        self.session = session
        self.current_user = current_user
        self.setup_ui()
        self.load_students()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(12)

        # Header
        header = QHBoxLayout()
        title = QLabel("🎓 Gestion des Élèves")
        title.setStyleSheet("color: #e0e0e0; font-size: 22px; font-weight: bold;")
        header.addWidget(title)
        header.addStretch()
        add_btn = QPushButton("➕ Nouvel Élève")
        add_btn.setObjectName("primaryBtn")
        add_btn.clicked.connect(self.add_student)
        header.addWidget(add_btn)
        layout.addLayout(header)

        # Search/filter bar
        filter_frame = QFrame()
        filter_frame.setObjectName("card")
        filter_layout = QHBoxLayout(filter_frame)
        filter_layout.setContentsMargins(12, 8, 12, 8)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Rechercher par nom, code...")
        self.search_input.setFixedHeight(36)
        self.search_input.textChanged.connect(self.filter_students)

        self.class_filter = QComboBox()
        self.class_filter.setFixedHeight(36)
        self.class_filter.setFixedWidth(120)
        self.class_filter.addItem("Toutes les classes", None)
        for cls in CLASSES:
            self.class_filter.addItem(cls, cls)
        self.class_filter.currentIndexChanged.connect(self.filter_students)

        self.status_filter = QComboBox()
        self.status_filter.setFixedHeight(36)
        self.status_filter.setFixedWidth(130)
        self.status_filter.addItems(["Tous", "Actifs", "Inactifs"])
        self.status_filter.currentIndexChanged.connect(self.filter_students)

        filter_layout.addWidget(self.search_input, 1)
        filter_layout.addWidget(QLabel("Classe:"))
        filter_layout.addWidget(self.class_filter)
        filter_layout.addWidget(QLabel("Statut:"))
        filter_layout.addWidget(self.status_filter)
        layout.addWidget(filter_frame)

        # Count label
        self.count_label = QLabel("0 élève(s)")
        self.count_label.setStyleSheet("color: #a0a0c0; font-size: 12px;")
        layout.addWidget(self.count_label)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels(
            ["Code", "Prénom", "Nom", "Classe", "Parent", "Téléphone", "Transport", "Assurance", "Actions"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(8, QHeaderView.ResizeToContents)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        layout.addWidget(self.table)

    def load_students(self):
        from models.database import Student, Class
        self.all_students = self.session.query(Student).join(Class, isouter=True).all()
        self.display_students(self.all_students)

    def display_students(self, students):
        self.table.setRowCount(0)
        for s in students:
            row = self.table.rowCount()
            self.table.insertRow(row)

            items = [
                s.student_code or "",
                s.first_name,
                s.last_name,
                s.class_.name if s.class_ else "—",
                s.parent_name or "—",
                s.parent_phone or "—",
                "✅" if s.has_transport else "❌",
                "✅" if s.insurance_paid else "❌",
            ]
            for col, text in enumerate(items):
                item = QTableWidgetItem(text)
                item.setTextAlignment(Qt.AlignCenter)
                if col == 0:
                    item.setForeground(Qt.yellow if False else QFont())
                self.table.setItem(row, col, item)

            # Actions
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(4, 2, 4, 2)
            actions_layout.setSpacing(4)

            edit_btn = QPushButton("✏")
            edit_btn.setFixedSize(30, 28)
            edit_btn.setStyleSheet("QPushButton{background:#2980b9;color:white;border-radius:4px;} QPushButton:hover{background:#3498db;}")
            edit_btn.clicked.connect(lambda checked, sid=s.id: self.edit_student(sid))

            pay_btn = QPushButton("💳")
            pay_btn.setFixedSize(30, 28)
            pay_btn.setStyleSheet("QPushButton{background:#27ae60;color:white;border-radius:4px;} QPushButton:hover{background:#2ecc71;}")
            pay_btn.clicked.connect(lambda checked, sid=s.id: self.payment_dialog(sid))

            del_btn = QPushButton("🗑")
            del_btn.setFixedSize(30, 28)
            del_btn.setStyleSheet("QPushButton{background:#c0392b;color:white;border-radius:4px;} QPushButton:hover{background:#e74c3c;}")
            del_btn.clicked.connect(lambda checked, sid=s.id: self.delete_student(sid))

            actions_layout.addWidget(edit_btn)
            actions_layout.addWidget(pay_btn)
            actions_layout.addWidget(del_btn)
            self.table.setCellWidget(row, 8, actions_widget)
            self.table.setRowHeight(row, 42)

        self.count_label.setText(f"{len(students)} élève(s)")

    def filter_students(self):
        text = self.search_input.text().lower()
        class_filter = self.class_filter.currentData()
        status_idx = self.status_filter.currentIndex()

        filtered = []
        for s in self.all_students:
            if status_idx == 1 and not s.is_active:
                continue
            if status_idx == 2 and s.is_active:
                continue
            if class_filter and (not s.class_ or s.class_.name != class_filter):
                continue
            if text and text not in f"{s.first_name} {s.last_name} {s.student_code or ''}".lower():
                continue
            filtered.append(s)
        self.display_students(filtered)

    def add_student(self):
        dlg = StudentDialog(self.session, parent=self)
        if dlg.exec():
            self.load_students()

    def edit_student(self, student_id):
        from models.database import Student
        s = self.session.query(Student).get(student_id)
        if s:
            dlg = StudentDialog(self.session, student=s, parent=self)
            if dlg.exec():
                self.load_students()

    def delete_student(self, student_id):
        from models.database import Student
        reply = QMessageBox.question(self, "Confirmer", "Voulez-vous vraiment désactiver cet élève?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            s = self.session.query(Student).get(student_id)
            if s:
                s.is_active = False
                self.session.commit()
                self.load_students()

    def payment_dialog(self, student_id):
        from ui.payments import PaymentDialog
        from models.database import Student
        s = self.session.query(Student).get(student_id)
        if s:
            dlg = PaymentDialog(self.session, s, self.current_user, parent=self)
            dlg.exec()
            self.load_students()
