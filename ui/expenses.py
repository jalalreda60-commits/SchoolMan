from datetime import datetime, date
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
                                QPushButton, QTableWidget, QTableWidgetItem, QDialog,
                                QFormLayout, QComboBox, QDateEdit, QTextEdit, QDoubleSpinBox,
                                QMessageBox, QFrame, QHeaderView, QAbstractItemView, QSpinBox)
from PySide6.QtCore import Qt, QDate

CATEGORIES = ['Loyer', 'Électricité', 'Eau', 'Internet', 'Fournitures',
              'Maintenance', 'Transport', 'Alimentation', 'Événements', 'Autres']


class ExpenseDialog(QDialog):
    def __init__(self, session, expense=None, current_user=None, parent=None):
        super().__init__(parent)
        self.session = session
        self.expense = expense
        self.current_user = current_user
        self.setWindowTitle("Modifier Dépense" if expense else "Nouvelle Dépense")
        self.setMinimumSize(450, 380)
        self.setup_ui()
        if expense:
            self.populate(expense)

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        title = QLabel("📉 " + ("Modifier Dépense" if self.expense else "Nouvelle Dépense"))
        title.setStyleSheet("color: #FF6B00; font-size: 18px; font-weight: bold;")
        layout.addWidget(title)

        form = QFormLayout()
        form.setSpacing(10)
        form.setLabelAlignment(Qt.AlignRight)

        def lbl(text):
            l = QLabel(text)
            l.setStyleSheet("color: #a0a0c0; font-size: 12px;")
            return l

        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Titre de la dépense")
        self.title_input.setFixedHeight(38)

        self.category = QComboBox()
        self.category.setFixedHeight(38)
        self.category.addItems(CATEGORIES)

        self.expense_type = QComboBox()
        self.expense_type.setFixedHeight(38)
        self.expense_type.addItems(["fixed", "variable"])

        self.amount = QDoubleSpinBox()
        self.amount.setRange(0, 999999)
        self.amount.setDecimals(2)
        self.amount.setSuffix(" MAD")
        self.amount.setFixedHeight(38)

        self.expense_date = QDateEdit()
        self.expense_date.setCalendarPopup(True)
        self.expense_date.setDate(QDate.currentDate())
        self.expense_date.setFixedHeight(38)

        self.description = QTextEdit()
        self.description.setMaximumHeight(80)
        self.description.setPlaceholderText("Description...")

        form.addRow(lbl("Titre *:"), self.title_input)
        form.addRow(lbl("Catégorie:"), self.category)
        form.addRow(lbl("Type:"), self.expense_type)
        form.addRow(lbl("Montant *:"), self.amount)
        form.addRow(lbl("Date:"), self.expense_date)
        form.addRow(lbl("Description:"), self.description)
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

    def populate(self, exp):
        self.title_input.setText(exp.title)
        idx = self.category.findText(exp.category or "")
        if idx >= 0:
            self.category.setCurrentIndex(idx)
        idx2 = self.expense_type.findText(exp.expense_type or "")
        if idx2 >= 0:
            self.expense_type.setCurrentIndex(idx2)
        self.amount.setValue(exp.amount or 0)
        if exp.expense_date:
            d = exp.expense_date
            self.expense_date.setDate(QDate(d.year, d.month, d.day))
        self.description.setText(exp.description or "")

    def save(self):
        if not self.title_input.text().strip():
            QMessageBox.warning(self, "Erreur", "Le titre est obligatoire.")
            return
        from models.database import Expense
        if self.expense:
            exp = self.expense
        else:
            exp = Expense()
            self.session.add(exp)
        exp.title = self.title_input.text().strip()
        exp.category = self.category.currentText()
        exp.expense_type = self.expense_type.currentText()
        exp.amount = self.amount.value()
        d = self.expense_date.date()
        exp.expense_date = date(d.year(), d.month(), d.day())
        exp.description = self.description.toPlainText()
        if self.current_user:
            exp.created_by = self.current_user.id
        self.session.commit()
        self.accept()


class ExpensesWidget(QWidget):
    def __init__(self, session, current_user):
        super().__init__()
        self.session = session
        self.current_user = current_user
        self.setup_ui()
        self.load_expenses()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(12)

        header = QHBoxLayout()
        title = QLabel("📉 Gestion des Dépenses")
        title.setStyleSheet("color: #e0e0e0; font-size: 22px; font-weight: bold;")
        header.addWidget(title)
        header.addStretch()
        add_btn = QPushButton("➕ Nouvelle Dépense")
        add_btn.setObjectName("primaryBtn")
        add_btn.clicked.connect(self.add_expense)
        header.addWidget(add_btn)
        layout.addLayout(header)

        filter_frame = QFrame()
        filter_frame.setObjectName("card")
        filter_layout = QHBoxLayout(filter_frame)
        filter_layout.setContentsMargins(12, 8, 12, 8)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Rechercher...")
        self.search_input.setFixedHeight(36)
        self.search_input.textChanged.connect(self.load_expenses)

        self.year_filter = QSpinBox()
        self.year_filter.setRange(2020, 2050)
        self.year_filter.setValue(datetime.now().year)
        self.year_filter.setFixedHeight(36)
        self.year_filter.setFixedWidth(80)
        self.year_filter.valueChanged.connect(self.load_expenses)

        self.cat_filter = QComboBox()
        self.cat_filter.setFixedHeight(36)
        self.cat_filter.setFixedWidth(140)
        self.cat_filter.addItem("Toutes catégories")
        self.cat_filter.addItems(CATEGORIES)
        self.cat_filter.currentIndexChanged.connect(self.load_expenses)

        filter_layout.addWidget(self.search_input, 1)
        filter_layout.addWidget(QLabel("Année:"))
        filter_layout.addWidget(self.year_filter)
        filter_layout.addWidget(QLabel("Catégorie:"))
        filter_layout.addWidget(self.cat_filter)
        layout.addWidget(filter_frame)

        self.total_lbl = QLabel("Total: 0 MAD")
        self.total_lbl.setStyleSheet("""
            QLabel { background: #1a1a2e; border: 1px solid #2a2a4e; border-left: 3px solid #e74c3c;
                     border-radius: 8px; padding: 8px 15px; color: #e74c3c; font-weight: bold; }
        """)
        layout.addWidget(self.total_lbl)

        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["Titre", "Catégorie", "Type", "Montant", "Date", "Description", "Actions"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(6, QHeaderView.ResizeToContents)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        layout.addWidget(self.table)

    def load_expenses(self):
        from models.database import Expense
        from sqlalchemy import func
        search = self.search_input.text().lower()
        year = self.year_filter.value()
        cat = self.cat_filter.currentText()

        query = self.session.query(Expense).filter(
            func.strftime('%Y', Expense.expense_date) == str(year))
        if cat != "Toutes catégories":
            query = query.filter_by(category=cat)
        expenses = query.order_by(Expense.expense_date.desc()).all()

        if search:
            expenses = [e for e in expenses if search in e.title.lower()]

        self.table.setRowCount(0)
        total = 0
        for exp in expenses:
            row = self.table.rowCount()
            self.table.insertRow(row)
            items = [
                exp.title,
                exp.category or "—",
                "Fixe" if exp.expense_type == "fixed" else "Variable",
                f"{exp.amount:,.2f} MAD",
                exp.expense_date.strftime("%d/%m/%Y") if exp.expense_date else "—",
                (exp.description or "")[:50] + ("..." if len(exp.description or "") > 50 else "")
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
            edit_btn.clicked.connect(lambda checked, eid=exp.id: self.edit_expense(eid))
            del_btn = QPushButton("🗑")
            del_btn.setFixedSize(30, 28)
            del_btn.setStyleSheet("QPushButton{background:#c0392b;color:white;border-radius:4px;}")
            del_btn.clicked.connect(lambda checked, eid=exp.id: self.delete_expense(eid))
            act_layout.addWidget(edit_btn)
            act_layout.addWidget(del_btn)
            self.table.setCellWidget(row, 6, actions)
            self.table.setRowHeight(row, 40)
            total += exp.amount

        self.total_lbl.setText(f"Total: {total:,.2f} MAD")

    def add_expense(self):
        dlg = ExpenseDialog(self.session, current_user=self.current_user, parent=self)
        if dlg.exec():
            self.load_expenses()

    def edit_expense(self, exp_id):
        from models.database import Expense
        exp = self.session.query(Expense).get(exp_id)
        if exp:
            dlg = ExpenseDialog(self.session, expense=exp, current_user=self.current_user, parent=self)
            if dlg.exec():
                self.load_expenses()

    def delete_expense(self, exp_id):
        from models.database import Expense
        reply = QMessageBox.question(self, "Confirmer", "Supprimer cette dépense?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            exp = self.session.query(Expense).get(exp_id)
            if exp:
                self.session.delete(exp)
                self.session.commit()
                self.load_expenses()
