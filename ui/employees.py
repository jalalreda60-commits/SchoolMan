import os
from datetime import datetime, date
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
                                QPushButton, QTableWidget, QTableWidgetItem, QDialog,
                                QFormLayout, QComboBox, QDateEdit, QTextEdit, QDoubleSpinBox,
                                QMessageBox, QFrame, QHeaderView, QAbstractItemView,
                                QSpinBox, QTabWidget, QCheckBox)
from PySide6.QtCore import Qt, QDate

MONTHS = ['Janvier','Février','Mars','Avril','Mai','Juin',
          'Juillet','Août','Septembre','Octobre','Novembre','Décembre']


class EmployeeDialog(QDialog):
    def __init__(self, session, employee=None, parent=None):
        super().__init__(parent)
        self.session = session
        self.employee = employee
        self.setWindowTitle("Modifier Employé" if employee else "Nouvel Employé")
        self.setMinimumSize(500, 500)
        self.setup_ui()
        if employee:
            self.populate(employee)

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        title = QLabel("👤 " + ("Modifier Employé" if self.employee else "Nouvel Employé"))
        title.setStyleSheet("color: #FF6B00; font-size: 18px; font-weight: bold;")
        layout.addWidget(title)

        form = QFormLayout()
        form.setSpacing(10)
        form.setLabelAlignment(Qt.AlignRight)

        def lbl(text):
            l = QLabel(text)
            l.setStyleSheet("color: #a0a0c0; font-size: 12px;")
            return l

        def field(ph=""):
            f = QLineEdit()
            f.setPlaceholderText(ph)
            f.setFixedHeight(38)
            return f

        self.first_name = field("Prénom")
        self.last_name = field("Nom")
        self.employee_type = QComboBox()
        self.employee_type.setFixedHeight(38)
        self.employee_type.addItems(["teacher", "staff", "driver"])
        self.subject = field("Matière enseignée")
        self.phone = field("+212 000 000 000")
        self.email = field("email@example.com")
        self.address = QTextEdit()
        self.address.setMaximumHeight(60)
        self.hire_date = QDateEdit()
        self.hire_date.setCalendarPopup(True)
        self.hire_date.setDate(QDate.currentDate())
        self.hire_date.setFixedHeight(38)
        self.base_salary = QDoubleSpinBox()
        self.base_salary.setRange(0, 99999)
        self.base_salary.setDecimals(2)
        self.base_salary.setSuffix(" MAD")
        self.base_salary.setFixedHeight(38)

        form.addRow(lbl("Prénom *:"), self.first_name)
        form.addRow(lbl("Nom *:"), self.last_name)
        form.addRow(lbl("Type:"), self.employee_type)
        form.addRow(lbl("Matière:"), self.subject)
        form.addRow(lbl("Téléphone:"), self.phone)
        form.addRow(lbl("Email:"), self.email)
        form.addRow(lbl("Adresse:"), self.address)
        form.addRow(lbl("Date embauche:"), self.hire_date)
        form.addRow(lbl("Salaire de base:"), self.base_salary)
        layout.addLayout(form)

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

    def populate(self, emp):
        self.first_name.setText(emp.first_name)
        self.last_name.setText(emp.last_name)
        idx = self.employee_type.findText(emp.employee_type)
        if idx >= 0:
            self.employee_type.setCurrentIndex(idx)
        self.subject.setText(emp.subject or "")
        self.phone.setText(emp.phone or "")
        self.email.setText(emp.email or "")
        self.address.setText(emp.address or "")
        if emp.hire_date:
            self.hire_date.setDate(QDate(emp.hire_date.year, emp.hire_date.month, emp.hire_date.day))
        self.base_salary.setValue(emp.base_salary or 0)

    def save(self):
        if not self.first_name.text().strip() or not self.last_name.text().strip():
            QMessageBox.warning(self, "Erreur", "Le prénom et le nom sont obligatoires.")
            return
        from models.database import Employee
        if self.employee:
            emp = self.employee
        else:
            emp = Employee()
            self.session.add(emp)
        emp.first_name = self.first_name.text().strip()
        emp.last_name = self.last_name.text().strip()
        emp.employee_type = self.employee_type.currentText()
        emp.subject = self.subject.text().strip()
        emp.phone = self.phone.text().strip()
        emp.email = self.email.text().strip()
        emp.address = self.address.toPlainText()
        hd = self.hire_date.date()
        emp.hire_date = date(hd.year(), hd.month(), hd.day())
        emp.base_salary = self.base_salary.value()
        self.session.commit()
        self.accept()


class SalaryDialog(QDialog):
    def __init__(self, session, employee, current_user, parent=None):
        super().__init__(parent)
        self.session = session
        self.employee = employee
        self.current_user = current_user
        self.setWindowTitle(f"Payer Salaire - {employee.first_name} {employee.last_name}")
        self.setMinimumSize(400, 350)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        title = QLabel(f"💰 Paiement Salaire\n{self.employee.first_name} {self.employee.last_name}")
        title.setStyleSheet("color: #FF6B00; font-size: 16px; font-weight: bold;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        form = QFormLayout()
        form.setSpacing(10)
        form.setLabelAlignment(Qt.AlignRight)

        def lbl(text):
            l = QLabel(text)
            l.setStyleSheet("color: #a0a0c0; font-size: 12px;")
            return l

        self.month_combo = QComboBox()
        self.month_combo.setFixedHeight(38)
        for m in MONTHS:
            self.month_combo.addItem(m)
        self.month_combo.setCurrentIndex(datetime.now().month - 1)

        self.year_spin = QSpinBox()
        self.year_spin.setRange(2020, 2050)
        self.year_spin.setValue(datetime.now().year)
        self.year_spin.setFixedHeight(38)

        month_row = QHBoxLayout()
        month_row.addWidget(self.month_combo)
        month_row.addWidget(self.year_spin)

        self.amount = QDoubleSpinBox()
        self.amount.setRange(0, 99999)
        self.amount.setDecimals(2)
        self.amount.setSuffix(" MAD")
        self.amount.setValue(self.employee.base_salary or 0)
        self.amount.setFixedHeight(38)

        self.bonus = QDoubleSpinBox()
        self.bonus.setRange(0, 99999)
        self.bonus.setDecimals(2)
        self.bonus.setSuffix(" MAD")
        self.bonus.setFixedHeight(38)

        self.notes = QTextEdit()
        self.notes.setMaximumHeight(70)

        form.addRow(lbl("Période:"), month_row)
        form.addRow(lbl("Salaire:"), self.amount)
        form.addRow(lbl("Bonus:"), self.bonus)
        form.addRow(lbl("Notes:"), self.notes)
        layout.addLayout(form)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        cancel_btn = QPushButton("Annuler")
        cancel_btn.setObjectName("secondaryBtn")
        cancel_btn.clicked.connect(self.reject)
        save_btn = QPushButton("💰 Payer")
        save_btn.setObjectName("primaryBtn")
        save_btn.clicked.connect(self.save)
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(save_btn)
        layout.addLayout(btn_layout)

    def save(self):
        from models.database import Salary
        salary = Salary(
            employee_id=self.employee.id,
            amount=self.amount.value(),
            bonus=self.bonus.value(),
            month=self.month_combo.currentIndex() + 1,
            year=self.year_spin.value(),
            paid_date=datetime.now(),
            is_paid=True,
            notes=self.notes.toPlainText()
        )
        self.session.add(salary)
        self.session.commit()
        QMessageBox.information(self, "Succès", f"✅ Salaire payé avec succès!")
        self.accept()


class EmployeesWidget(QWidget):
    def __init__(self, session, current_user):
        super().__init__()
        self.session = session
        self.current_user = current_user
        self.setup_ui()
        self.load_employees()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(12)

        header = QHBoxLayout()
        title = QLabel("👥 Gestion des Employés")
        title.setStyleSheet("color: #e0e0e0; font-size: 22px; font-weight: bold;")
        header.addWidget(title)
        header.addStretch()
        add_btn = QPushButton("➕ Nouvel Employé")
        add_btn.setObjectName("primaryBtn")
        add_btn.clicked.connect(self.add_employee)
        header.addWidget(add_btn)
        layout.addLayout(header)

        filter_frame = QFrame()
        filter_frame.setObjectName("card")
        filter_layout = QHBoxLayout(filter_frame)
        filter_layout.setContentsMargins(12, 8, 12, 8)
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Rechercher un employé...")
        self.search_input.setFixedHeight(36)
        self.search_input.textChanged.connect(self.load_employees)
        self.type_filter = QComboBox()
        self.type_filter.setFixedHeight(36)
        self.type_filter.setFixedWidth(130)
        self.type_filter.addItems(["Tous", "Enseignants", "Personnel", "Chauffeurs"])
        self.type_filter.currentIndexChanged.connect(self.load_employees)
        filter_layout.addWidget(self.search_input, 1)
        filter_layout.addWidget(QLabel("Type:"))
        filter_layout.addWidget(self.type_filter)
        layout.addWidget(filter_frame)

        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels(["Nom", "Prénom", "Type", "Matière", "Téléphone", "Salaire", "Embauche", "Actions"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(7, QHeaderView.ResizeToContents)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        layout.addWidget(self.table)

    def load_employees(self):
        from models.database import Employee
        search = self.search_input.text().lower()
        type_idx = self.type_filter.currentIndex()
        type_map = {1: 'teacher', 2: 'staff', 3: 'driver'}

        query = self.session.query(Employee).filter_by(is_active=True)
        if type_idx > 0:
            query = query.filter_by(employee_type=type_map[type_idx])
        employees = query.all()

        if search:
            employees = [e for e in employees if search in f"{e.first_name} {e.last_name}".lower()]

        type_labels = {'teacher': '👨‍🏫 Enseignant', 'staff': '👤 Personnel', 'driver': '🚌 Chauffeur'}
        self.table.setRowCount(0)
        for emp in employees:
            row = self.table.rowCount()
            self.table.insertRow(row)
            items = [
                emp.last_name, emp.first_name,
                type_labels.get(emp.employee_type, emp.employee_type),
                emp.subject or "—", emp.phone or "—",
                f"{emp.base_salary:,.0f} MAD",
                emp.hire_date.strftime("%d/%m/%Y") if emp.hire_date else "—"
            ]
            for col, text in enumerate(items):
                item = QTableWidgetItem(text)
                item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(row, col, item)

            actions = QWidget()
            act_layout = QHBoxLayout(actions)
            act_layout.setContentsMargins(4, 2, 4, 2)
            act_layout.setSpacing(4)

            edit_btn = QPushButton("✏")
            edit_btn.setFixedSize(30, 28)
            edit_btn.setStyleSheet("QPushButton{background:#2980b9;color:white;border-radius:4px;}")
            edit_btn.clicked.connect(lambda checked, eid=emp.id: self.edit_employee(eid))

            salary_btn = QPushButton("💰")
            salary_btn.setFixedSize(30, 28)
            salary_btn.setStyleSheet("QPushButton{background:#27ae60;color:white;border-radius:4px;}")
            salary_btn.clicked.connect(lambda checked, eid=emp.id: self.pay_salary(eid))

            del_btn = QPushButton("🗑")
            del_btn.setFixedSize(30, 28)
            del_btn.setStyleSheet("QPushButton{background:#c0392b;color:white;border-radius:4px;}")
            del_btn.clicked.connect(lambda checked, eid=emp.id: self.delete_employee(eid))

            act_layout.addWidget(edit_btn)
            act_layout.addWidget(salary_btn)
            act_layout.addWidget(del_btn)
            self.table.setCellWidget(row, 7, actions)
            self.table.setRowHeight(row, 42)

    def add_employee(self):
        dlg = EmployeeDialog(self.session, parent=self)
        if dlg.exec():
            self.load_employees()

    def edit_employee(self, emp_id):
        from models.database import Employee
        emp = self.session.query(Employee).get(emp_id)
        if emp:
            dlg = EmployeeDialog(self.session, employee=emp, parent=self)
            if dlg.exec():
                self.load_employees()

    def pay_salary(self, emp_id):
        from models.database import Employee
        emp = self.session.query(Employee).get(emp_id)
        if emp:
            dlg = SalaryDialog(self.session, emp, self.current_user, parent=self)
            dlg.exec()

    def delete_employee(self, emp_id):
        from models.database import Employee
        reply = QMessageBox.question(self, "Confirmer", "Désactiver cet employé?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            emp = self.session.query(Employee).get(emp_id)
            if emp:
                emp.is_active = False
                self.session.commit()
                self.load_employees()
