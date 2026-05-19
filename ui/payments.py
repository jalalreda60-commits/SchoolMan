import os
from datetime import datetime
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
                                QPushButton, QTableWidget, QTableWidgetItem, QDialog,
                                QFormLayout, QComboBox, QDoubleSpinBox, QTextEdit,
                                QMessageBox, QFrame, QHeaderView, QAbstractItemView,
                                QSpinBox, QCheckBox)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MONTHS = ['Janvier','Février','Mars','Avril','Mai','Juin',
          'Juillet','Août','Septembre','Octobre','Novembre','Décembre']


class PaymentDialog(QDialog):
    def __init__(self, session, student, current_user, parent=None):
        super().__init__(parent)
        self.session = session
        self.student = student
        self.current_user = current_user
        self.setWindowTitle(f"Paiement - {student.first_name} {student.last_name}")
        self.setMinimumSize(500, 480)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 20, 25, 20)
        layout.setSpacing(15)

        # Student info card
        info_frame = QFrame()
        info_frame.setObjectName("card")
        info_layout = QHBoxLayout(info_frame)
        info_layout.setContentsMargins(15, 10, 15, 10)

        name_lbl = QLabel(f"👤 {self.student.first_name} {self.student.last_name}")
        name_lbl.setStyleSheet("color: #FF6B00; font-size: 16px; font-weight: bold; background: transparent;")
        info_layout.addWidget(name_lbl)
        info_layout.addStretch()

        cls_lbl = QLabel(f"Classe: {self.student.class_.name if self.student.class_ else '—'}")
        cls_lbl.setStyleSheet("color: #a0a0c0; font-size: 12px; background: transparent;")
        info_layout.addWidget(cls_lbl)
        layout.addWidget(info_frame)

        # Payment form
        form = QFormLayout()
        form.setSpacing(12)
        form.setLabelAlignment(Qt.AlignRight)

        def lbl(text):
            l = QLabel(text)
            l.setStyleSheet("color: #a0a0c0; font-size: 12px;")
            return l

        # Payment type
        self.pay_type = QComboBox()
        self.pay_type.setFixedHeight(38)
        self.pay_type.addItems(["Mensualité", "Assurance", "Transport"])
        self.pay_type.currentIndexChanged.connect(self.update_amount)

        # Month/Year
        self.month_combo = QComboBox()
        self.month_combo.setFixedHeight(38)
        for m in MONTHS:
            self.month_combo.addItem(m)
        self.month_combo.setCurrentIndex(datetime.now().month - 1)

        self.year_spin = QSpinBox()
        self.year_spin.setRange(2020, 2050)
        self.year_spin.setValue(datetime.now().year)
        self.year_spin.setFixedHeight(38)

        month_year_layout = QHBoxLayout()
        month_year_layout.addWidget(self.month_combo)
        month_year_layout.addWidget(self.year_spin)

        # Amount
        self.amount_spin = QDoubleSpinBox()
        self.amount_spin.setRange(0, 99999)
        self.amount_spin.setDecimals(2)
        self.amount_spin.setSuffix(" MAD")
        self.amount_spin.setFixedHeight(38)

        # Notes
        self.notes_input = QTextEdit()
        self.notes_input.setMaximumHeight(70)
        self.notes_input.setPlaceholderText("Remarques...")

        # Print receipt
        self.print_receipt = QCheckBox("Générer et imprimer le reçu")
        self.print_receipt.setChecked(True)

        form.addRow(lbl("Type de paiement:"), self.pay_type)
        form.addRow(lbl("Période:"), month_year_layout)
        form.addRow(lbl("Montant:"), self.amount_spin)
        form.addRow(lbl("Notes:"), self.notes_input)
        form.addRow(lbl(""), self.print_receipt)

        layout.addLayout(form)

        # Previous payments for this student
        prev_lbl = QLabel("📋 Paiements récents")
        prev_lbl.setStyleSheet("color: #FF6B00; font-weight: bold;")
        layout.addWidget(prev_lbl)
        self.prev_table = QTableWidget()
        self.prev_table.setColumnCount(5)
        self.prev_table.setHorizontalHeaderLabels(["Type", "Mois", "Année", "Montant", "Date"])
        self.prev_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.prev_table.setMaximumHeight(130)
        self.prev_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.prev_table.verticalHeader().setVisible(False)
        self.prev_table.setShowGrid(False)
        self.load_prev_payments()
        layout.addWidget(self.prev_table)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        cancel_btn = QPushButton("Annuler")
        cancel_btn.setObjectName("secondaryBtn")
        cancel_btn.clicked.connect(self.reject)
        pay_btn = QPushButton("💳 Enregistrer le Paiement")
        pay_btn.setObjectName("primaryBtn")
        pay_btn.clicked.connect(self.save_payment)
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(pay_btn)
        layout.addLayout(btn_layout)

        self.update_amount()

    def update_amount(self):
        from models.database import Setting
        ptype = self.pay_type.currentIndex()
        if ptype == 0:  # Mensualité
            self.amount_spin.setValue(self.student.monthly_fee or 0)
        elif ptype == 1:  # Assurance
            setting = self.session.query(Setting).filter_by(key='insurance_fee').first()
            self.amount_spin.setValue(float(setting.value) if setting else 200)
        elif ptype == 2:  # Transport
            setting = self.session.query(Setting).filter_by(key='transport_fee').first()
            self.amount_spin.setValue(float(setting.value) if setting else 300)

    def load_prev_payments(self):
        from models.database import Payment
        payments = self.session.query(Payment).filter_by(
            student_id=self.student.id).order_by(Payment.payment_date.desc()).limit(5).all()
        self.prev_table.setRowCount(0)
        type_map = {'monthly': 'Mensualité', 'insurance': 'Assurance', 'transport': 'Transport'}
        for p in payments:
            row = self.prev_table.rowCount()
            self.prev_table.insertRow(row)
            items = [
                type_map.get(p.payment_type, p.payment_type),
                MONTHS[p.month - 1] if p.month and 1 <= p.month <= 12 else "—",
                str(p.year or ""),
                f"{p.amount:,.2f} MAD",
                p.payment_date.strftime("%d/%m/%Y") if p.payment_date else "—"
            ]
            for col, text in enumerate(items):
                item = QTableWidgetItem(text)
                item.setTextAlignment(Qt.AlignCenter)
                self.prev_table.setItem(row, col, item)
            self.prev_table.setRowHeight(row, 32)

    def save_payment(self):
        from models.database import Payment, Receipt, Setting
        import subprocess, sys

        type_map = {0: 'monthly', 1: 'insurance', 2: 'transport'}
        ptype = type_map[self.pay_type.currentIndex()]
        amount = self.amount_spin.value()
        month = self.month_combo.currentIndex() + 1
        year = self.year_spin.value()

        if amount <= 0:
            QMessageBox.warning(self, "Erreur", "Le montant doit être supérieur à 0.")
            return

        # Check duplicate monthly payment
        if ptype == 'monthly':
            existing = self.session.query(Payment).filter_by(
                student_id=self.student.id, payment_type='monthly',
                month=month, year=year).first()
            if existing:
                reply = QMessageBox.question(self, "Doublon",
                    f"Un paiement mensuel existe déjà pour {MONTHS[month-1]} {year}. Continuer?",
                    QMessageBox.Yes | QMessageBox.No)
                if reply == QMessageBox.No:
                    return

        # Get receipt counter
        setting = self.session.query(Setting).filter_by(key='receipt_counter').first()
        counter = int(setting.value) + 1 if setting else 1
        receipt_number = f"REC-{year}-{counter:06d}"
        if setting:
            setting.value = str(counter)
        else:
            self.session.add(Setting(key='receipt_counter', value=str(counter)))

        # Save payment
        payment = Payment(
            student_id=self.student.id,
            payment_type=ptype,
            amount=amount,
            month=month,
            year=year,
            receipt_number=receipt_number,
            notes=self.notes_input.toPlainText(),
            created_by=self.current_user.id
        )
        self.session.add(payment)
        self.session.flush()

        # Generate receipt
        if self.print_receipt.isChecked():
            school_settings = {}
            for key in ['school_name', 'school_address', 'school_phone', 'currency']:
                s = self.session.query(Setting).filter_by(key=key).first()
                school_settings[key] = s.value if s else ''

            from services.receipt_service import generate_receipt_pdf
            receipt_data = {
                'receipt_number': receipt_number,
                'student_name': f"{self.student.first_name} {self.student.last_name}",
                'student_code': self.student.student_code or '',
                'class_name': self.student.class_.name if self.student.class_ else '',
                'parent_name': self.student.parent_name or '',
                'payment_type': ptype,
                'amount': amount,
                'month': month,
                'year': year,
                'payment_date': datetime.now().strftime('%d/%m/%Y %H:%M'),
                'cashier': self.current_user.full_name or self.current_user.username,
                'school_name': school_settings.get('school_name', 'Le Schéma'),
                'school_address': school_settings.get('school_address', ''),
                'school_phone': school_settings.get('school_phone', ''),
                'currency': school_settings.get('currency', 'MAD'),
            }
            try:
                pdf_path = generate_receipt_pdf(receipt_data)
                receipt = Receipt(
                    receipt_number=receipt_number,
                    student_id=self.student.id,
                    payment_id=payment.id,
                    amount=amount,
                    payment_type=ptype,
                    pdf_path=pdf_path,
                    created_by=self.current_user.id
                )
                self.session.add(receipt)

                # Open PDF
                import platform
                if platform.system() == 'Windows':
                    os.startfile(pdf_path)
                elif platform.system() == 'Darwin':
                    subprocess.run(['open', pdf_path])
                else:
                    subprocess.run(['xdg-open', pdf_path])

                QMessageBox.information(self, "Succès",
                    f"✅ Paiement enregistré!\nReçu: {receipt_number}\nFichier PDF généré.")
            except Exception as e:
                QMessageBox.warning(self, "Avertissement",
                    f"Paiement enregistré mais erreur PDF:\n{e}")

        # Update student insurance status
        if ptype == 'insurance':
            self.student.insurance_paid = True

        self.session.commit()
        self.accept()


class PaymentsWidget(QWidget):
    def __init__(self, session, current_user):
        super().__init__()
        self.session = session
        self.current_user = current_user
        self.setup_ui()
        self.load_payments()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(12)

        header = QHBoxLayout()
        title = QLabel("💳 Gestion des Paiements")
        title.setStyleSheet("color: #e0e0e0; font-size: 22px; font-weight: bold;")
        header.addWidget(title)
        header.addStretch()
        layout.addLayout(header)

        # Filters
        filter_frame = QFrame()
        filter_frame.setObjectName("card")
        filter_layout = QHBoxLayout(filter_frame)
        filter_layout.setContentsMargins(12, 8, 12, 8)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Rechercher par élève, reçu...")
        self.search_input.setFixedHeight(36)
        self.search_input.textChanged.connect(self.load_payments)

        self.type_filter = QComboBox()
        self.type_filter.setFixedHeight(36)
        self.type_filter.setFixedWidth(140)
        self.type_filter.addItems(["Tous les types", "Mensualité", "Assurance", "Transport"])
        self.type_filter.currentIndexChanged.connect(self.load_payments)

        self.month_filter = QComboBox()
        self.month_filter.setFixedHeight(36)
        self.month_filter.setFixedWidth(120)
        self.month_filter.addItem("Tous les mois", 0)
        for i, m in enumerate(MONTHS, 1):
            self.month_filter.addItem(m, i)
        self.month_filter.setCurrentIndex(datetime.now().month)
        self.month_filter.currentIndexChanged.connect(self.load_payments)

        self.year_filter = QSpinBox()
        self.year_filter.setRange(2020, 2050)
        self.year_filter.setValue(datetime.now().year)
        self.year_filter.setFixedHeight(36)
        self.year_filter.setFixedWidth(80)
        self.year_filter.valueChanged.connect(self.load_payments)

        filter_layout.addWidget(self.search_input, 1)
        filter_layout.addWidget(QLabel("Type:"))
        filter_layout.addWidget(self.type_filter)
        filter_layout.addWidget(QLabel("Mois:"))
        filter_layout.addWidget(self.month_filter)
        filter_layout.addWidget(QLabel("Année:"))
        filter_layout.addWidget(self.year_filter)
        layout.addWidget(filter_frame)

        # Summary cards
        summary_layout = QHBoxLayout()
        self.total_lbl = QLabel("Total: 0 MAD")
        self.total_lbl.setStyleSheet("""
            QLabel { background: #1a1a2e; border: 1px solid #2a2a4e; border-left: 3px solid #27ae60;
                     border-radius: 8px; padding: 8px 15px; color: #27ae60; font-weight: bold; }
        """)
        self.count_lbl = QLabel("0 paiements")
        self.count_lbl.setStyleSheet("""
            QLabel { background: #1a1a2e; border: 1px solid #2a2a4e; border-left: 3px solid #FF6B00;
                     border-radius: 8px; padding: 8px 15px; color: #FF6B00; font-weight: bold; }
        """)
        summary_layout.addWidget(self.total_lbl)
        summary_layout.addWidget(self.count_lbl)
        summary_layout.addStretch()
        layout.addLayout(summary_layout)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels(["Reçu", "Élève", "Classe", "Type", "Mois", "Année", "Montant", "Date"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        self.table.doubleClicked.connect(self.open_receipt)
        layout.addWidget(self.table)

    def load_payments(self):
        from models.database import Payment, Student, Class
        from sqlalchemy import func

        query = self.session.query(Payment).join(Student, isouter=True)
        search = self.search_input.text().lower()
        type_idx = self.type_filter.currentIndex()
        month = self.month_filter.currentData()
        year = self.year_filter.value()

        type_map = {1: 'monthly', 2: 'insurance', 3: 'transport'}
        if type_idx > 0:
            query = query.filter(Payment.payment_type == type_map[type_idx])
        if month:
            query = query.filter(Payment.month == month)
        query = query.filter(Payment.year == year)

        payments = query.order_by(Payment.payment_date.desc()).all()

        if search:
            payments = [p for p in payments if search in f"{p.student.first_name} {p.student.last_name} {p.receipt_number or ''}".lower()]

        type_labels = {'monthly': 'Mensualité', 'insurance': 'Assurance', 'transport': 'Transport'}
        self.table.setRowCount(0)
        total = 0
        for p in payments:
            row = self.table.rowCount()
            self.table.insertRow(row)
            student = p.student
            items = [
                p.receipt_number or "—",
                f"{student.first_name} {student.last_name}" if student else "—",
                student.class_.name if student and student.class_ else "—",
                type_labels.get(p.payment_type, p.payment_type),
                MONTHS[p.month - 1] if p.month and 1 <= p.month <= 12 else "—",
                str(p.year or ""),
                f"{p.amount:,.2f} MAD",
                p.payment_date.strftime("%d/%m/%Y %H:%M") if p.payment_date else "—"
            ]
            for col, text in enumerate(items):
                item = QTableWidgetItem(text)
                item.setTextAlignment(Qt.AlignCenter)
                if col == 6:
                    item.setForeground(Qt.green if False else item.foreground())
                self.table.setItem(row, col, item)
            self.table.setRowHeight(row, 38)
            total += p.amount

        self.total_lbl.setText(f"Total: {total:,.2f} MAD")
        self.count_lbl.setText(f"{len(payments)} paiement(s)")

    def open_receipt(self):
        from models.database import Receipt
        row = self.table.currentRow()
        if row < 0:
            return
        receipt_num = self.table.item(row, 0).text()
        receipt = self.session.query(Receipt).filter_by(receipt_number=receipt_num).first()
        if receipt and receipt.pdf_path and os.path.exists(receipt.pdf_path):
            import subprocess, platform
            if platform.system() == 'Windows':
                os.startfile(receipt.pdf_path)
            elif platform.system() == 'Darwin':
                subprocess.run(['open', receipt.pdf_path])
            else:
                subprocess.run(['xdg-open', receipt.pdf_path])
        else:
            QMessageBox.information(self, "Info", "Aucun fichier PDF disponible pour ce paiement.")
