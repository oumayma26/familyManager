from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QFrame, QGridLayout, QProgressBar, QPushButton,
    QDialog, QTableWidget, QTableWidgetItem, QHeaderView,
    QComboBox, QMessageBox, QSplitter, QAbstractItemView
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QFont, QColor, QBrush


class StatsView(QWidget):
    def __init__(self, db_manager):
        super().__init__()
        self.db = db_manager
        self.setup_ui()
        self.load_stats()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        
        # Titre
        title = QLabel("📊 Tableau de bord")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Grille des statistiques
        grid = QGridLayout()
        grid.setSpacing(15)
        
        # Carte 1 : Martyrs
        self.card_martyrs = self.create_stat_card(
            "☪️ Martyrs", 
            "0", 
            "#d32f2f", 
            "#ffebee"
        )
        grid.addWidget(self.card_martyrs, 0, 0)
        
        # Carte 2 : Familles
        self.card_families = self.create_stat_card(
            "👨‍👩‍👧‍👦 Familles", 
            "0", 
            "#1976d2", 
            "#e3f2fd"
        )
        grid.addWidget(self.card_families, 0, 1)
        
        # Carte 3 : Total
        self.card_total = self.create_stat_card(
            "👥 Total personnes", 
            "0", 
            "#388e3c", 
            "#e8f5e9"
        )
        grid.addWidget(self.card_total, 0, 2)
        
        # Carte 4 : Martyrs sans famille
        self.card_orphans = self.create_stat_card(
            "⚠️ Martyrs sans famille", 
            "0", 
            "#f57c00", 
            "#fff3e0"
        )
        grid.addWidget(self.card_orphans, 1, 0)
        
        # Carte 5 : Sans CIN
        self.card_no_cin = self.create_stat_card(
            "📝 Sans CIN", 
            "0", 
            "#7b1fa2", 
            "#f3e5f5"
        )
        grid.addWidget(self.card_no_cin, 1, 1)
        
        # Carte 6 : Répartition genre
        self.card_gender = self.create_gender_card()
        grid.addWidget(self.card_gender, 1, 2)
        
        layout.addLayout(grid)
        
        # ===== SECTION PENSIONS =====
        pension_frame = QFrame()
        pension_frame.setStyleSheet("""
            QFrame {
                background-color: #fff8e1;
                border: 2px solid #ff9800;
                border-radius: 10px;
                padding: 15px;
            }
        """)
        pension_layout = QVBoxLayout(pension_frame)
        
        pension_title = QLabel("💰 Gestion des Pensions")
        pension_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #e65100;")
        pension_layout.addWidget(pension_title)
        
        pension_info = QLabel("Formule: SMIG × 3 | Célibataire: Parents 100% (ou Frères/Sœurs) | Marié: Parents 20% + Conjoint 40% + Enfants 40%")
        pension_info.setStyleSheet("font-size: 11px; color: #666; padding: 5px;")
        pension_layout.addWidget(pension_info)
        
        # Boutons pensions
        pension_buttons = QHBoxLayout()
        
        self.btn_pay_pensions = QPushButton("💳 Payer les pensions du mois")
        self.btn_pay_pensions.setStyleSheet("""
            QPushButton {
                background-color: #ff9800;
                color: white;
                padding: 12px 20px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #f57c00;
            }
        """)
        self.btn_pay_pensions.clicked.connect(self.pay_pensions)
        pension_buttons.addWidget(self.btn_pay_pensions)
        
        self.btn_view_pensions = QPushButton("📋 Voir l'historique des paiements")
        self.btn_view_pensions.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                padding: 12px 20px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        self.btn_view_pensions.clicked.connect(self.view_pension_history)
        pension_buttons.addWidget(self.btn_view_pensions)
        
        pension_buttons.addStretch()
        pension_layout.addLayout(pension_buttons)
        
        layout.addWidget(pension_frame)
        
        # Bouton actualiser
        self.btn_refresh = QPushButton("🔄 Actualiser")
        self.btn_refresh.setStyleSheet("""
            QPushButton {
                background-color: #1976d2;
                color: white;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1565c0;
            }
        """)
        self.btn_refresh.clicked.connect(self.load_stats)
        layout.addWidget(self.btn_refresh, alignment=Qt.AlignCenter)
        
        layout.addStretch()
    
    def create_stat_card(self, title, value, color, bg_color):
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {bg_color};
                border-radius: 10px;
                padding: 15px;
                border: 1px solid {color};
            }}
        """)
        
        layout = QVBoxLayout(card)
        
        label_title = QLabel(title)
        label_title.setStyleSheet(f"color: {color}; font-size: 12px; font-weight: bold;")
        layout.addWidget(label_title)
        
        label_value = QLabel(value)
        label_value.setStyleSheet(f"color: {color}; font-size: 32px; font-weight: bold;")
        label_value.setAlignment(Qt.AlignCenter)
        layout.addWidget(label_value)
        
        card.value_label = label_value
        
        return card
    
    def create_gender_card(self):
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: #fafafa;
                border-radius: 10px;
                padding: 15px;
                border: 1px solid #666;
            }
        """)
        
        layout = QVBoxLayout(card)
        
        title = QLabel("⚥ Répartition par genre")
        title.setStyleSheet("color: #666; font-size: 12px; font-weight: bold;")
        layout.addWidget(title)
        
        self.bar_male = QProgressBar()
        self.bar_male.setStyleSheet("""
            QProgressBar {
                border: 1px solid #ddd;
                border-radius: 5px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #2196F3;
            }
        """)
        self.bar_male.setFormat("Homme: %v%")
        layout.addWidget(self.bar_male)
        
        self.bar_female = QProgressBar()
        self.bar_female.setStyleSheet("""
            QProgressBar {
                border: 1px solid #ddd;
                border-radius: 5px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #E91E63;
            }
        """)
        self.bar_female.setFormat("Femme: %v%")
        layout.addWidget(self.bar_female)
        
        return card
    
    def load_stats(self):
        stats = self.db.get_stats()
        
        self.card_martyrs.value_label.setText(str(stats['total_martyrs']))
        self.card_families.value_label.setText(str(stats['total_families']))
        self.card_total.value_label.setText(str(stats['total_persons']))
        self.card_orphans.value_label.setText(str(stats['martyrs_without_family']))
        self.card_no_cin.value_label.setText(str(stats['without_cin']))
        
        total = stats['total_persons']
        if total > 0:
            gender = stats['gender_distribution']
            male = gender.get('M', 0)
            female = gender.get('F', 0)
            
            self.bar_male.setValue(int(male / total * 100))
            self.bar_female.setValue(int(female / total * 100))
        else:
            self.bar_male.setValue(0)
            self.bar_female.setValue(0)
    
    def pay_pensions(self):
        dialog = PensionPaymentDialog(self.db, self)
        dialog.exec()
    
    def view_pension_history(self):
        dialog = PensionHistoryDialog(self.db, self)
        dialog.exec()


class PensionPaymentDialog(QDialog):
    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db = db_manager
        
        self.setWindowTitle("💳 Paiement des pensions")
        self.setMinimumSize(900, 600)
        
        self.setup_ui()
        self.load_preview()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        title = QLabel("💳 Paiement des pensions mensuelles")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #e65100;")
        layout.addWidget(title)
        
        smig = self.db.get_smig()
        info = QLabel("SMIG actuel: " + str(smig) + " DT | Pension totale par martyr: " + str(smig * 3) + " DT")
        info.setStyleSheet("background-color: #fff3e0; padding: 10px; border-radius: 5px; font-size: 12px;")
        layout.addWidget(info)
        
        date_layout = QHBoxLayout()
        
        self.combo_month = QComboBox()
        months = ["Janvier", "Février", "Mars", "Avril", "Mai", "Juin",
                  "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"]
        self.combo_month.addItems(months)
        self.combo_month.setCurrentIndex(QDate.currentDate().month() - 1)
        
        self.combo_year = QComboBox()
        current_year = QDate.currentDate().year()
        for year in range(current_year - 2, current_year + 2):
            self.combo_year.addItem(str(year))
        self.combo_year.setCurrentIndex(2)
        
        date_layout.addWidget(QLabel("Mois:"))
        date_layout.addWidget(self.combo_month)
        date_layout.addWidget(QLabel("Année:"))
        date_layout.addWidget(self.combo_year)
        date_layout.addStretch()
        
        layout.addLayout(date_layout)
        
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "Martyr", "Bénéficiaire", "Type", "Montant (DT)", "Pourcentage", "Mois", "Statut"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #ddd;
                border-radius: 5px;
            }
            QHeaderView::section {
                background-color: #ff9800;
                color: white;
                padding: 10px;
                font-weight: bold;
            }
        """)
        layout.addWidget(self.table)
        
        self.lbl_total = QLabel("Total à payer: 0 DT")
        self.lbl_total.setStyleSheet("font-size: 14px; font-weight: bold; color: #e65100;")
        layout.addWidget(self.lbl_total)
        
        buttons = QHBoxLayout()
        
        self.btn_preview = QPushButton("👁️ Prévisualiser")
        self.btn_preview.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #1976D2; }
        """)
        self.btn_preview.clicked.connect(self.load_preview)
        buttons.addWidget(self.btn_preview)
        
        self.btn_pay = QPushButton("💳 Payer maintenant")
        self.btn_pay.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #45a049; }
        """)
        self.btn_pay.clicked.connect(self.confirm_payment)
        buttons.addWidget(self.btn_pay)
        
        self.btn_cancel = QPushButton("❌ Annuler")
        self.btn_cancel.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #da190b; }
        """)
        self.btn_cancel.clicked.connect(self.reject)
        buttons.addWidget(self.btn_cancel)
        
        buttons.addStretch()
        layout.addLayout(buttons)
    
    def load_preview(self):
        self.table.setRowCount(0)
        
        martyrs = self.db.get_martyrs()
        total = 0
        row = 0
        
        for martyr in martyrs:
            pensions = self.db.calculate_pensions(martyr['id'])
            
            if not pensions:
                self.table.insertRow(row)
                self.table.setItem(row, 0, QTableWidgetItem(martyr['first_name'] + " " + martyr['last_name']))
                self.table.setItem(row, 1, QTableWidgetItem("-"))
                self.table.setItem(row, 2, QTableWidgetItem("-"))
                self.table.setItem(row, 3, QTableWidgetItem("0"))
                self.table.setItem(row, 4, QTableWidgetItem("-"))
                self.table.setItem(row, 5, QTableWidgetItem("-"))
                
                status = QTableWidgetItem("⚠️ Aucun bénéficiaire")
                status.setForeground(QBrush(QColor("#f44336")))
                self.table.setItem(row, 6, status)
                row += 1
                continue
            
            for pension in pensions:
                self.table.insertRow(row)
                self.table.setItem(row, 0, QTableWidgetItem(martyr['first_name'] + " " + martyr['last_name']))
                self.table.setItem(row, 1, QTableWidgetItem(pension['beneficiary_name']))
                self.table.setItem(row, 2, QTableWidgetItem(pension['beneficiary_type']))
                self.table.setItem(row, 3, QTableWidgetItem(str(round(pension['amount'], 2))))
                self.table.setItem(row, 4, QTableWidgetItem(str(pension['percentage']) + "%"))
                self.table.setItem(row, 5, QTableWidgetItem(self.combo_month.currentText() + " " + self.combo_year.currentText()))
                
                status = QTableWidgetItem("✅ Prêt à payer")
                status.setForeground(QBrush(QColor("#4caf50")))
                self.table.setItem(row, 6, status)
                
                total += pension['amount']
                row += 1
        
        self.lbl_total.setText("Total à payer: " + str(round(total, 2)) + " DT")
    
    def confirm_payment(self):
        month = self.combo_month.currentIndex() + 1
        year = int(self.combo_year.currentText())
        
        reply = QMessageBox.question(
            self, "Confirmer le paiement",
            "Voulez-vous payer les pensions pour " + self.combo_month.currentText() + " " + str(year) + " ?\n\n" +
            self.lbl_total.text(),
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            results = self.db.pay_pensions(month, year)
            
            paid = len(results['paid'])
            skipped = len(results['skipped'])
            errors = len(results['errors'])
            
            msg = "✅ Paiements effectués: " + str(paid) + "\n"
            msg += "⏭️ Déjà payés/skippés: " + str(skipped) + "\n"
            if errors > 0:
                msg += "❌ Erreurs: " + str(errors)
            
            QMessageBox.information(self, "Résultat du paiement", msg)
            self.load_preview()


class PensionHistoryDialog(QDialog):
    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db = db_manager
        
        self.setWindowTitle("📋 Historique des pensions")
        self.setMinimumSize(1000, 600)
        
        self.setup_ui()
        self.load_history()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        title = QLabel("📋 Historique des paiements de pensions")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #1976d2;")
        layout.addWidget(title)
        
        filters = QHBoxLayout()
        
        self.combo_month = QComboBox()
        self.combo_month.addItem("Tous les mois")
        months = ["Janvier", "Février", "Mars", "Avril", "Mai", "Juin",
                  "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"]
        self.combo_month.addItems(months)
        
        self.combo_year = QComboBox()
        self.combo_year.addItem("Toutes les années")
        current_year = QDate.currentDate().year()
        for year in range(current_year - 2, current_year + 2):
            self.combo_year.addItem(str(year))
        
        self.combo_month.currentIndexChanged.connect(self.load_history)
        self.combo_year.currentIndexChanged.connect(self.load_history)
        
        filters.addWidget(QLabel("Mois:"))
        filters.addWidget(self.combo_month)
        filters.addWidget(QLabel("Année:"))
        filters.addWidget(self.combo_year)
        filters.addStretch()
        
        layout.addLayout(filters)
        
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "Date", "Martyr", "Bénéficiaire", "Type", "Montant (DT)", "Mois", "Année", "ID Paiement"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #ddd;
                border-radius: 5px;
            }
            QHeaderView::section {
                background-color: #1976d2;
                color: white;
                padding: 10px;
                font-weight: bold;
            }
        """)
        layout.addWidget(self.table)
        
        self.lbl_total = QLabel("Total payé: 0 DT")
        self.lbl_total.setStyleSheet("font-size: 14px; font-weight: bold; color: #1976d2;")
        layout.addWidget(self.lbl_total)
        
        btn_close = QPushButton("❌ Fermer")
        btn_close.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #da190b; }
        """)
        btn_close.clicked.connect(self.reject)
        layout.addWidget(btn_close, alignment=Qt.AlignCenter)
    
    def load_history(self):
        self.table.setRowCount(0)
        
        month = self.combo_month.currentIndex()
        year = self.combo_year.currentText()
        
        month_filter = month if month > 0 else None
        year_filter = int(year) if year != "Toutes les années" else None
        
        payments = self.db.get_pension_history(month=month_filter, year=year_filter)
        
        total = 0
        for row, payment in enumerate(payments):
            self.table.insertRow(row)
            
            self.table.setItem(row, 0, QTableWidgetItem(payment.get('payment_date', '-')))
            self.table.setItem(row, 1, QTableWidgetItem(payment.get('martyr_first', '') + " " + payment.get('martyr_last', '')))
            self.table.setItem(row, 2, QTableWidgetItem(payment.get('ben_first', '') + " " + payment.get('ben_last', '')))
            self.table.setItem(row, 3, QTableWidgetItem(payment.get('beneficiary_type', '-')))
            self.table.setItem(row, 4, QTableWidgetItem(str(round(payment.get('amount', 0), 2))))
            
            months_names = ["", "Jan", "Fév", "Mar", "Avr", "Mai", "Juin",
                           "Juil", "Août", "Sep", "Oct", "Nov", "Déc"]
            month_name = months_names[payment.get('payment_month', 0)] if payment.get('payment_month', 0) < 13 else "-"
            self.table.setItem(row, 5, QTableWidgetItem(month_name))
            self.table.setItem(row, 6, QTableWidgetItem(str(payment.get('payment_year', '-'))))
            self.table.setItem(row, 7, QTableWidgetItem(str(payment.get('id', '-'))))
            
            total += payment.get('amount', 0)
        
        self.lbl_total.setText("Total payé: " + str(round(total, 2)) + " DT (" + str(len(payments)) + " paiements)")