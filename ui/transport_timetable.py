from datetime import datetime, date
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
                                QPushButton, QTableWidget, QTableWidgetItem, QDialog,
                                QFormLayout, QComboBox, QMessageBox, QFrame, QHeaderView,
                                QAbstractItemView, QDoubleSpinBox, QSpinBox, QTabWidget,
                                QCheckBox, QTextEdit)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QColor


class TransportWidget(QWidget):
    def __init__(self, session, current_user):
        super().__init__()
        self.session = session
        self.current_user = current_user
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(12)

        title = QLabel("🚌 Gestion du Transport")
        title.setStyleSheet("color: #e0e0e0; font-size: 22px; font-weight: bold;")
        layout.addWidget(title)

        tabs = QTabWidget()
        layout.addWidget(tabs)

        # Students with transport
        students_tab = QWidget()
        s_layout = QVBoxLayout(students_tab)
        s_layout.setContentsMargins(15, 15, 15, 15)
        s_layout.setSpacing(10)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Rechercher un élève...")
        self.search_input.setFixedHeight(36)
        self.search_input.textChanged.connect(self.load_data)
        s_layout.addWidget(self.search_input)

        self.students_table = QTableWidget()
        self.students_table.setColumnCount(6)
        self.students_table.setHorizontalHeaderLabels(["Code", "Nom", "Prénom", "Classe", "Transport", "Parent"])
        self.students_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.students_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.students_table.verticalHeader().setVisible(False)
        self.students_table.setShowGrid(False)
        self.students_table.setAlternatingRowColors(True)
        s_layout.addWidget(self.students_table)

        tabs.addTab(students_tab, "👨‍🎓 Élèves Transport")

        # Buses tab
        buses_tab = QWidget()
        b_layout = QVBoxLayout(buses_tab)
        b_layout.setContentsMargins(15, 15, 15, 15)
        b_layout.setSpacing(10)

        add_bus_btn = QPushButton("➕ Nouveau Bus")
        add_bus_btn.setObjectName("primaryBtn")
        add_bus_btn.setFixedWidth(180)
        add_bus_btn.clicked.connect(self.add_bus)
        b_layout.addWidget(add_bus_btn)

        self.buses_table = QTableWidget()
        self.buses_table.setColumnCount(6)
        self.buses_table.setHorizontalHeaderLabels(["N° Bus", "Plaque", "Capacité", "Route", "Chauffeur", "Statut"])
        self.buses_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.buses_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.buses_table.verticalHeader().setVisible(False)
        self.buses_table.setShowGrid(False)
        self.buses_table.setAlternatingRowColors(True)
        b_layout.addWidget(self.buses_table)

        tabs.addTab(buses_tab, "🚌 Buses")

    def load_data(self):
        from models.database import Student, Bus, Employee
        search = self.search_input.text().lower()

        # Students with transport
        students = self.session.query(Student).filter_by(is_active=True).all()
        self.students_table.setRowCount(0)
        for s in students:
            if search and search not in f"{s.first_name} {s.last_name}".lower():
                continue
            row = self.students_table.rowCount()
            self.students_table.insertRow(row)
            items = [
                s.student_code or "", s.last_name, s.first_name,
                s.class_.name if s.class_ else "—",
                "✅ Oui" if s.has_transport else "❌ Non",
                s.parent_phone or "—"
            ]
            for col, text in enumerate(items):
                item = QTableWidgetItem(text)
                item.setTextAlignment(Qt.AlignCenter)
                if col == 4:
                    if s.has_transport:
                        item.setForeground(QColor("#27ae60"))
                    else:
                        item.setForeground(QColor("#e74c3c"))
                self.students_table.setItem(row, col, item)
            self.students_table.setRowHeight(row, 38)

        # Buses
        buses = self.session.query(Bus).all()
        self.buses_table.setRowCount(0)
        for b in buses:
            driver = self.session.query(Employee).get(b.driver_id) if b.driver_id else None
            row = self.buses_table.rowCount()
            self.buses_table.insertRow(row)
            items = [
                b.bus_number or "", b.plate or "", str(b.capacity or "—"),
                b.route or "—",
                f"{driver.first_name} {driver.last_name}" if driver else "—",
                "✅ Actif" if b.is_active else "❌ Inactif"
            ]
            for col, text in enumerate(items):
                item = QTableWidgetItem(text)
                item.setTextAlignment(Qt.AlignCenter)
                self.buses_table.setItem(row, col, item)
            self.buses_table.setRowHeight(row, 38)

    def add_bus(self):
        from models.database import Bus, Employee
        dlg = QDialog(self)
        dlg.setWindowTitle("Nouveau Bus")
        dlg.setMinimumSize(400, 350)
        layout = QVBoxLayout(dlg)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        form = QFormLayout()
        form.setSpacing(10)
        form.setLabelAlignment(Qt.AlignRight)

        def lbl(text):
            l = QLabel(text)
            l.setStyleSheet("color: #a0a0c0;")
            return l

        num_f = QLineEdit()
        num_f.setFixedHeight(38)
        plate_f = QLineEdit()
        plate_f.setFixedHeight(38)
        cap_f = QSpinBox()
        cap_f.setRange(1, 100)
        cap_f.setValue(30)
        cap_f.setFixedHeight(38)
        route_f = QLineEdit()
        route_f.setFixedHeight(38)
        fee_f = QDoubleSpinBox()
        fee_f.setRange(0, 9999)
        fee_f.setDecimals(2)
        fee_f.setSuffix(" MAD")
        fee_f.setFixedHeight(38)

        driver_combo = QComboBox()
        driver_combo.setFixedHeight(38)
        driver_combo.addItem("-- Aucun --", None)
        drivers = self.session.query(Employee).filter_by(employee_type='driver', is_active=True).all()
        for d in drivers:
            driver_combo.addItem(f"{d.first_name} {d.last_name}", d.id)

        form.addRow(lbl("N° Bus:"), num_f)
        form.addRow(lbl("Plaque:"), plate_f)
        form.addRow(lbl("Capacité:"), cap_f)
        form.addRow(lbl("Route:"), route_f)
        form.addRow(lbl("Frais mensuel:"), fee_f)
        form.addRow(lbl("Chauffeur:"), driver_combo)
        layout.addLayout(form)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        cancel_btn = QPushButton("Annuler")
        cancel_btn.setObjectName("secondaryBtn")
        cancel_btn.clicked.connect(dlg.reject)
        save_btn = QPushButton("💾 Enregistrer")
        save_btn.setObjectName("primaryBtn")
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(save_btn)
        layout.addLayout(btn_layout)

        def do_save():
            bus = Bus(
                bus_number=num_f.text().strip(),
                plate=plate_f.text().strip(),
                capacity=cap_f.value(),
                route=route_f.text().strip(),
                monthly_fee=fee_f.value(),
                driver_id=driver_combo.currentData()
            )
            self.session.add(bus)
            self.session.commit()
            dlg.accept()
            self.load_data()

        save_btn.clicked.connect(do_save)
        dlg.exec()


class TimetableWidget(QWidget):
    def __init__(self, session, current_user):
        super().__init__()
        self.session = session
        self.current_user = current_user
        self.setup_ui()
        self.load_timetable()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(12)

        header = QHBoxLayout()
        title = QLabel("📅 Emploi du Temps")
        title.setStyleSheet("color: #e0e0e0; font-size: 22px; font-weight: bold;")
        header.addWidget(title)
        header.addStretch()

        self.class_combo = QComboBox()
        self.class_combo.setFixedHeight(36)
        self.class_combo.setFixedWidth(130)
        self.class_combo.addItem("Toutes les classes", None)
        from models.database import Class
        classes = self.session.query(Class).all()
        for cls in classes:
            self.class_combo.addItem(cls.name, cls.id)
        self.class_combo.currentIndexChanged.connect(self.load_timetable)
        header.addWidget(QLabel("Classe:"))
        header.addWidget(self.class_combo)

        add_btn = QPushButton("➕ Ajouter Cours")
        add_btn.setObjectName("primaryBtn")
        add_btn.clicked.connect(self.add_schedule)
        header.addWidget(add_btn)
        layout.addLayout(header)

        # Weekly timetable grid
        days = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi']
        self.table = QTableWidget()
        self.table.setColumnCount(len(days))
        self.table.setHorizontalHeaderLabels(days)
        self.table.setRowCount(8)
        hours = ['08:00-09:00', '09:00-10:00', '10:00-11:00', '11:00-12:00',
                 '14:00-15:00', '15:00-16:00', '16:00-17:00', '17:00-18:00']
        self.table.setVerticalHeaderLabels(hours)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setShowGrid(True)
        layout.addWidget(self.table)

    def load_timetable(self):
        from models.database import Schedule, Employee, Class
        class_id = self.class_combo.currentData()
        query = self.session.query(Schedule)
        if class_id:
            query = query.filter_by(class_id=class_id)
        schedules = query.all()

        self.table.clearContents()
        hours_start = ['08:00', '09:00', '10:00', '11:00', '14:00', '15:00', '16:00', '17:00']
        for sched in schedules:
            if sched.day_of_week < 6 and sched.start_time in hours_start:
                row = hours_start.index(sched.start_time)
                col = sched.day_of_week
                emp = self.session.query(Employee).get(sched.employee_id) if sched.employee_id else None
                cls = self.session.query(Class).get(sched.class_id) if sched.class_id else None
                text = f"{sched.subject or ''}\n{emp.last_name if emp else ''}\n{cls.name if cls else ''}"
                item = QTableWidgetItem(text)
                item.setTextAlignment(Qt.AlignCenter)
                item.setBackground(QColor("#1a3a2e"))
                self.table.setItem(row, col, item)

    def add_schedule(self):
        from models.database import Schedule, Employee, Class
        dlg = QDialog(self)
        dlg.setWindowTitle("Ajouter un cours")
        dlg.setMinimumSize(380, 380)
        layout = QVBoxLayout(dlg)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        form = QFormLayout()
        form.setSpacing(10)
        form.setLabelAlignment(Qt.AlignRight)

        def lbl(text):
            l = QLabel(text)
            l.setStyleSheet("color: #a0a0c0;")
            return l

        class_combo = QComboBox()
        class_combo.setFixedHeight(38)
        classes = self.session.query(Class).all()
        for cls in classes:
            class_combo.addItem(cls.name, cls.id)

        emp_combo = QComboBox()
        emp_combo.setFixedHeight(38)
        emp_combo.addItem("-- Aucun --", None)
        teachers = self.session.query(Employee).filter_by(employee_type='teacher', is_active=True).all()
        for t in teachers:
            emp_combo.addItem(f"{t.first_name} {t.last_name}", t.id)

        subject_f = QLineEdit()
        subject_f.setFixedHeight(38)

        day_combo = QComboBox()
        day_combo.setFixedHeight(38)
        day_combo.addItems(['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi'])

        start_combo = QComboBox()
        start_combo.setFixedHeight(38)
        start_combo.addItems(['08:00', '09:00', '10:00', '11:00', '14:00', '15:00', '16:00', '17:00'])

        end_combo = QComboBox()
        end_combo.setFixedHeight(38)
        end_combo.addItems(['09:00', '10:00', '11:00', '12:00', '15:00', '16:00', '17:00', '18:00'])

        room_f = QLineEdit()
        room_f.setFixedHeight(38)

        form.addRow(lbl("Classe:"), class_combo)
        form.addRow(lbl("Enseignant:"), emp_combo)
        form.addRow(lbl("Matière:"), subject_f)
        form.addRow(lbl("Jour:"), day_combo)
        form.addRow(lbl("Début:"), start_combo)
        form.addRow(lbl("Fin:"), end_combo)
        form.addRow(lbl("Salle:"), room_f)
        layout.addLayout(form)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        cancel_btn = QPushButton("Annuler")
        cancel_btn.setObjectName("secondaryBtn")
        cancel_btn.clicked.connect(dlg.reject)
        save_btn = QPushButton("💾 Enregistrer")
        save_btn.setObjectName("primaryBtn")
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(save_btn)
        layout.addLayout(btn_layout)

        def do_save():
            sched = Schedule(
                class_id=class_combo.currentData(),
                employee_id=emp_combo.currentData(),
                subject=subject_f.text().strip(),
                day_of_week=day_combo.currentIndex(),
                start_time=start_combo.currentText(),
                end_time=end_combo.currentText(),
                room=room_f.text().strip()
            )
            self.session.add(sched)
            self.session.commit()
            dlg.accept()
            self.load_timetable()

        save_btn.clicked.connect(do_save)
        dlg.exec()
