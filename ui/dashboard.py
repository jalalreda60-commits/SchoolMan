import os
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                                QFrame, QGridLayout, QScrollArea, QPushButton, QSizePolicy)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QColor
from datetime import datetime, date


class StatCard(QFrame):
    def __init__(self, title, value, icon, color="#FF6B00", subtitle=""):
        super().__init__()
        self.setObjectName("card")
        self.setMinimumSize(180, 110)
        self.color = color
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 14, 18, 14)
        layout.setSpacing(4)

        top = QHBoxLayout()
        icon_lbl = QLabel(icon)
        icon_lbl.setStyleSheet(f"font-size: 26px; background: transparent; color: {color};")
        top.addWidget(icon_lbl)
        top.addStretch()
        layout.addLayout(top)

        val_lbl = QLabel(str(value))
        val_lbl.setObjectName("statValue")
        val_lbl.setStyleSheet(f"color: {color}; font-size: 26px; font-weight: bold; background: transparent;")
        layout.addWidget(val_lbl)
        self.val_lbl = val_lbl

        title_lbl = QLabel(title)
        title_lbl.setObjectName("statLabel")
        title_lbl.setStyleSheet("color: #a0a0c0; font-size: 11px; background: transparent;")
        layout.addWidget(title_lbl)

        if subtitle:
            sub_lbl = QLabel(subtitle)
            sub_lbl.setStyleSheet("color: #606080; font-size: 10px; background: transparent;")
            layout.addWidget(sub_lbl)

        self.setStyleSheet(f"""
            QFrame#card {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #1a1a2e, stop:1 #16213e);
                border: 1px solid #2a2a4e;
                border-left: 3px solid {color};
                border-radius: 12px;
            }}
            QFrame#card:hover {{
                border-left: 3px solid {color};
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #1e1e38, stop:1 #1a2540);
            }}
        """)

    def update_value(self, value):
        self.val_lbl.setText(str(value))


class MiniChart(QFrame):
    def __init__(self, title, data=None):
        super().__init__()
        self.setObjectName("card")
        self.title = title
        self.data = data or []
        self.setMinimumHeight(200)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 12, 15, 12)

        title_lbl = QLabel(title)
        title_lbl.setStyleSheet("color: #FF6B00; font-size: 13px; font-weight: bold; background: transparent;")
        layout.addWidget(title_lbl)

        self.chart_area = QLabel()
        self.chart_area.setStyleSheet("background: transparent;")
        self.chart_area.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.chart_area)

        self.setStyleSheet("""
            QFrame#card {
                background: #1a1a2e;
                border: 1px solid #2a2a4e;
                border-radius: 12px;
            }
        """)

    def set_data(self, data, labels=None):
        self.data = data
        self.labels = labels or []
        self.update_display()

    def update_display(self):
        if not self.data:
            self.chart_area.setText("Aucune donnée")
            return
        # Simple ASCII-like bar chart using HTML
        max_val = max(self.data) if self.data else 1
        if max_val == 0:
            max_val = 1
        bars = ""
        for i, val in enumerate(self.data):
            pct = int((val / max_val) * 80)
            label = self.labels[i] if self.labels and i < len(self.labels) else str(i+1)
            bars += f"""
            <div style='display:inline-block; text-align:center; margin:2px; vertical-align:bottom;'>
                <div style='background:linear-gradient(to top, #FF6B00, #FF8C00);
                           width:22px; height:{pct}px; border-radius:3px 3px 0 0; margin:0 auto;'></div>
                <div style='color:#606080; font-size:8px; margin-top:2px;'>{label}</div>
                <div style='color:#FF6B00; font-size:8px;'>{val}</div>
            </div>"""
        html = f"<div style='display:flex; align-items:flex-end; height:120px; padding:5px;'>{bars}</div>"
        self.chart_area.setText(html)
        self.chart_area.setTextFormat(Qt.RichText)


class NotificationWidget(QFrame):
    def __init__(self, message, level="warning"):
        super().__init__()
        colors = {"warning": "#FF6B00", "danger": "#e74c3c", "info": "#3498db", "success": "#27ae60"}
        color = colors.get(level, "#FF6B00")
        icons = {"warning": "⚠", "danger": "🔴", "info": "ℹ", "success": "✅"}
        icon = icons.get(level, "⚠")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        icon_lbl = QLabel(icon)
        icon_lbl.setStyleSheet(f"font-size: 16px; color: {color}; background: transparent;")
        layout.addWidget(icon_lbl)
        msg_lbl = QLabel(message)
        msg_lbl.setStyleSheet(f"color: #e0e0e0; font-size: 12px; background: transparent;")
        msg_lbl.setWordWrap(True)
        layout.addWidget(msg_lbl, 1)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: rgba({self._hex_to_rgb(color)}, 0.1);
                border-left: 3px solid {color};
                border-radius: 6px;
                margin: 2px 0;
            }}
        """)

    def _hex_to_rgb(self, hex_color):
        h = hex_color.lstrip('#')
        r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
        return f"{r},{g},{b}"


class DashboardWidget(QWidget):
    def __init__(self, session, current_user):
        super().__init__()
        self.session = session
        self.current_user = current_user
        self.setup_ui()
        self.load_data()
        # Auto-refresh every 30s
        self.timer = QTimer()
        self.timer.timeout.connect(self.load_data)
        self.timer.start(30000)

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(15)

        # Header
        header = QHBoxLayout()
        title = QLabel("📊 Tableau de Bord")
        title.setObjectName("pageTitle")
        title.setStyleSheet("color: #e0e0e0; font-size: 22px; font-weight: bold;")
        header.addWidget(title)
        header.addStretch()
        now = datetime.now()
        date_lbl = QLabel(now.strftime("%A %d %B %Y  |  %H:%M"))
        date_lbl.setStyleSheet("color: #606080; font-size: 12px;")
        header.addWidget(date_lbl)
        refresh_btn = QPushButton("⟳ Actualiser")
        refresh_btn.setObjectName("secondaryBtn")
        refresh_btn.setFixedWidth(110)
        refresh_btn.clicked.connect(self.load_data)
        header.addWidget(refresh_btn)
        layout.addLayout(header)

        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        content = QWidget()
        content.setStyleSheet("background: transparent;")
        self.content_layout = QVBoxLayout(content)
        self.content_layout.setSpacing(15)
        scroll.setWidget(content)
        layout.addWidget(scroll)

        # Stats grid
        self.stats_grid = QGridLayout()
        self.stats_grid.setSpacing(12)
        self.content_layout.addLayout(self.stats_grid)

        # Stat cards
        self.card_students = StatCard("Total Élèves", "0", "🎓", "#FF6B00")
        self.card_revenue_month = StatCard("Recettes du Mois", "0 MAD", "💰", "#27ae60")
        self.card_revenue_year = StatCard("Recettes Annuelles", "0 MAD", "📈", "#3498db")
        self.card_expenses = StatCard("Dépenses", "0 MAD", "📉", "#e74c3c")
        self.card_profit = StatCard("Bénéfice Net", "0 MAD", "💎", "#9b59b6")
        self.card_unpaid = StatCard("Élèves Impayés", "0", "⚠", "#e67e22")
        self.card_teachers = StatCard("Enseignants", "0", "👨‍🏫", "#1abc9c")
        self.card_employees = StatCard("Employés", "0", "👥", "#2980b9")
        self.card_transport = StatCard("Transport", "0", "🚌", "#8e44ad")

        cards = [self.card_students, self.card_revenue_month, self.card_revenue_year,
                 self.card_expenses, self.card_profit, self.card_unpaid,
                 self.card_teachers, self.card_employees, self.card_transport]

        for i, card in enumerate(cards):
            self.stats_grid.addWidget(card, i // 3, i % 3)

        # Charts row
        charts_layout = QHBoxLayout()
        charts_layout.setSpacing(12)
        self.revenue_chart = MiniChart("📊 Recettes Mensuelles (12 mois)")
        self.payment_chart = MiniChart("🎓 Élèves par Classe")
        charts_layout.addWidget(self.revenue_chart, 1)
        charts_layout.addWidget(self.payment_chart, 1)
        self.content_layout.addLayout(charts_layout)

        # Notifications
        notif_label = QLabel("🔔 Notifications & Alertes")
        notif_label.setStyleSheet("color: #FF6B00; font-size: 15px; font-weight: bold;")
        self.content_layout.addWidget(notif_label)
        self.notif_container = QVBoxLayout()
        self.content_layout.addLayout(self.notif_container)
        self.content_layout.addStretch()

    def clear_notifications(self):
        while self.notif_container.count():
            item = self.notif_container.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def load_data(self):
        from models.database import Student, Payment, Employee, Expense, Setting
        from sqlalchemy import func
        session = self.session
        now = datetime.now()

        try:
            # Students
            total_students = session.query(Student).filter_by(is_active=True).count()
            self.card_students.update_value(total_students)

            # Revenue this month
            month_rev = session.query(func.sum(Payment.amount)).filter(
                Payment.month == now.month, Payment.year == now.year).scalar() or 0
            self.card_revenue_month.update_value(f"{month_rev:,.0f} MAD")

            # Revenue this year
            year_rev = session.query(func.sum(Payment.amount)).filter(
                Payment.year == now.year).scalar() or 0
            self.card_revenue_year.update_value(f"{year_rev:,.0f} MAD")

            # Expenses this year
            year_exp = session.query(func.sum(Expense.expense_date)).scalar() or 0
            year_exp = session.query(func.sum(Expense.amount)).filter(
                func.strftime('%Y', Expense.expense_date) == str(now.year)).scalar() or 0
            self.card_expenses.update_value(f"{year_exp:,.0f} MAD")

            profit = year_rev - year_exp
            self.card_profit.update_value(f"{profit:,.0f} MAD")

            # Unpaid students (no payment this month)
            paid_ids = [p[0] for p in session.query(Payment.student_id).filter(
                Payment.month == now.month, Payment.year == now.year,
                Payment.payment_type == 'monthly').all()]
            unpaid = session.query(Student).filter(
                Student.is_active == True, ~Student.id.in_(paid_ids)).count()
            self.card_unpaid.update_value(unpaid)

            # Employees
            teachers = session.query(Employee).filter_by(employee_type='teacher', is_active=True).count()
            employees = session.query(Employee).filter_by(is_active=True).count()
            transport = session.query(Student).filter_by(has_transport=True, is_active=True).count()
            self.card_teachers.update_value(teachers)
            self.card_employees.update_value(employees)
            self.card_transport.update_value(transport)

            # Revenue chart (last 12 months)
            from models.database import Class
            months = []
            revenues = []
            month_labels = ['Jan','Fév','Mar','Avr','Mai','Jun','Jul','Aoû','Sep','Oct','Nov','Déc']
            for i in range(12):
                m = ((now.month - 1 - i) % 12) + 1
                y = now.year if m <= now.month else now.year - 1
                rev = session.query(func.sum(Payment.amount)).filter(
                    Payment.month == m, Payment.year == y).scalar() or 0
                months.insert(0, month_labels[m-1])
                revenues.insert(0, int(rev))
            self.revenue_chart.set_data(revenues, months)

            # Students by class
            classes = session.query(Class).all()
            class_names = []
            class_counts = []
            for cls in classes:
                cnt = session.query(Student).filter_by(class_id=cls.id, is_active=True).count()
                if cnt > 0:
                    class_names.append(cls.name)
                    class_counts.append(cnt)
            self.payment_chart.set_data(class_counts, class_names)

            # Notifications
            self.clear_notifications()
            if unpaid > 0:
                self.notif_container.addWidget(NotificationWidget(
                    f"{unpaid} élève(s) n'ont pas payé les frais de scolarité ce mois-ci.", "warning"))
            if profit < 0:
                self.notif_container.addWidget(NotificationWidget(
                    f"Attention: Déficit de {abs(profit):,.0f} MAD cette année.", "danger"))
            if total_students == 0:
                self.notif_container.addWidget(NotificationWidget(
                    "Aucun élève enregistré. Commencez par ajouter des élèves.", "info"))
            if unpaid == 0 and total_students > 0:
                self.notif_container.addWidget(NotificationWidget(
                    "Tous les élèves sont à jour dans leurs paiements ce mois.", "success"))

        except Exception as e:
            print(f"Dashboard load error: {e}")
