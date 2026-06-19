from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QFrame, QPushButton, QMessageBox, QTableWidget,
    QTableWidgetItem, QHeaderView, QAbstractItemView,
    QDialog
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QFont, QColor, QBrush


class PensionView(QWidget):
    def __init__(self, db_manager):
        super().__init__()
        self.db = db_manager
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(24)
        
        # Header
        header = QLabel("💰 Gestion des pensions")
        header.setObjectName("title")
        layout.addWidget(header)
        
        # ===== CARTE STATUT MOIS ACTUEL =====
        status_card = QFrame()
        status_card.setObjectName("card")
        status_layout = QVBoxLayout(status_card)
        status_layout.setContentsMargins(24, 24, 24, 24)
        status_layout.setSpacing(16)
        
        # Date actuelle
        current_date = QDate.currentDate()
        self.current_month = current_date.month()
        self.current_year = current_date.year()
        
        months_names = ["", "Janvier", "Février", "Mars", "Avril", "Mai", "Juin",
                       "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"]
        month_name = months_names[self.current_month]
        
        # Header avec mois et statut
        status_header = QHBoxLayout()
        
        month_title = QLabel(f"📅 {month_name} {self.current_year}")
        month_title_font = QFont()
        month_title_font.setPointSize(14)
        month_title_font.setBold(True)
        month_title.setFont(month_title_font)
        status_header.addWidget(month_title)
        status_header.addStretch()
        
        self.lbl_status = QLabel("⏳ Non payé")
        self.lbl_status.setStyleSheet("""
            background-color: #fef3c7;
            color: #d97706;
            padding: 8px 18px;
            border-radius: 20px;
            font-weight: 600;
            font-size: 10pt;
        """)
        status_header.addWidget(self.lbl_status)
        status_layout.addLayout(status_header)
        
        # Info SMIG
        self.lbl_smig = QLabel()
        self.lbl_smig.setObjectName("subtitle")
        status_layout.addWidget(self.lbl_smig)
        
        # Résumé
        self.lbl_summary = QLabel("Chargement...")
        self.lbl_summary.setStyleSheet("color: #475569; font-size: 11pt; padding: 8px 0;")
        status_layout.addWidget(self.lbl_summary)
        
        # Boutons d'action
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(12)
        
        self.btn_pay = QPushButton("💳 Payer les pensions")
        self.btn_pay.setObjectName("primary")
        self.btn_pay.setMinimumHeight(48)
        self.btn_pay.clicked.connect(self.pay_pensions)
        buttons_layout.addWidget(self.btn_pay)
        
        self.btn_cancel = QPushButton("❌ Annuler le paiement")
        self.btn_cancel.setObjectName("danger")
        self.btn_cancel.setMinimumHeight(48)
        self.btn_cancel.clicked.connect(self.cancel_pensions)
        buttons_layout.addWidget(self.btn_cancel)
        
        buttons_layout.addStretch()
        status_layout.addLayout(buttons_layout)
        
        layout.addWidget(status_card)
        
        # ===== TABLEAU RÉCAPITULATIF =====
        preview_card = QFrame()
        preview_card.setObjectName("card")
        preview_layout = QVBoxLayout(preview_card)
        preview_layout.setContentsMargins(20, 20, 20, 20)
        preview_layout.setSpacing(12)
        
        preview_title = QLabel("📋 Détail par martyr")
        preview_title_font = QFont()
        preview_title_font.setBold(True)
        preview_title_font.setPointSize(11)
        preview_title.setFont(preview_title_font)
        preview_title.setStyleSheet("color: #475569;")
        preview_layout.addWidget(preview_title)
        
        self.table_preview = QTableWidget()
        self.table_preview.setColumnCount(4)
        self.table_preview.setHorizontalHeaderLabels([
            "Martyr", "Bénéficiaires", "Montant total (DT)", "Statut"
        ])
        self.table_preview.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_preview.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table_preview.setMaximumHeight(300)
        preview_layout.addWidget(self.table_preview)
        
        layout.addWidget(preview_card)
        
        # Bouton historique
        history_layout = QHBoxLayout()
        history_layout.addStretch()
        
        self.btn_history = QPushButton("📋 Voir l'historique complet")
        self.btn_history.setObjectName("ghost")
        self.btn_history.setMinimumHeight(40)
        self.btn_history.clicked.connect(self.view_history)
        history_layout.addWidget(self.btn_history)
        history_layout.addStretch()
        
        layout.addLayout(history_layout)
        layout.addStretch()
    
    def load_pensions(self):
        """Charge l'état des pensions du mois actuel"""
        self.check_status()
        self.load_preview_table()
    
    def check_status(self):
        """Vérifie si les pensions du mois sont payées"""
        payments = self.db.get_pension_history(month=self.current_month, year=self.current_year)
        smig = self.db.get_smig()
        martyrs = self.db.get_martyrs()
        
        self.lbl_smig.setText(f"SMIG actuel : {smig} DT | Pension totale par martyr : {smig * 3} DT | {len(martyrs)} martyrs enregistrés")
        
        if payments:
            total_paid = sum(p['amount'] for p in payments)
            self.lbl_status.setText("✅ Payé")
            self.lbl_status.setStyleSheet("""
                background-color: #dcfce7;
                color: #16a34a;
                padding: 8px 18px;
                border-radius: 20px;
                font-weight: 600;
                font-size: 10pt;
            """)
            self.lbl_summary.setText(
                f"{len(payments)} paiements effectués pour un total de <b>{round(total_paid, 2)} DT</b>"
            )
            self.btn_pay.setEnabled(False)
            self.btn_pay.setText("✓ Déjà payé")
            self.btn_cancel.setEnabled(True)
        else:
            self.lbl_status.setText("⏳ Non payé")
            self.lbl_status.setStyleSheet("""
                background-color: #fef3c7;
                color: #d97706;
                padding: 8px 18px;
                border-radius: 20px;
                font-weight: 600;
                font-size: 10pt;
            """)
            
            # Calcul prévisionnel
            total_preview = 0
            count_benef = 0
            for martyr in martyrs:
                pensions = self.db.calculate_pensions(martyr['id'])
                total_preview += sum(p['amount'] for p in pensions)
                count_benef += len(pensions)
            
            self.lbl_summary.setText(
                f"Prévision : <b>{count_benef}</b> bénéficiaires, "
                f"montant estimé <b>{round(total_preview, 2)} DT</b>"
            )
            self.btn_pay.setEnabled(True)
            self.btn_pay.setText("💳 Payer les pensions")
            self.btn_cancel.setEnabled(False)
    
    def load_preview_table(self):
        """Charge le tableau de prévisualisation par martyr"""
        self.table_preview.setRowCount(0)
        
        martyrs = self.db.get_martyrs()
        row = 0
        
        for martyr in martyrs:
            pensions = self.db.calculate_pensions(martyr['id'])
            martyr_name = f"{martyr['first_name']} {martyr['last_name']}"
            
            self.table_preview.insertRow(row)
            
            # Nom du martyr
            name_item = QTableWidgetItem(martyr_name)
            self.table_preview.setItem(row, 0, name_item)
            
            # Nombre de bénéficiaires
            if pensions:
                benef_item = QTableWidgetItem(str(len(pensions)))
                self.table_preview.setItem(row, 1, benef_item)
                
                total = sum(p['amount'] for p in pensions)
                amount_item = QTableWidgetItem(str(round(total, 2)))
                self.table_preview.setItem(row, 2, amount_item)
                
                # Vérifier si déjà payé ce mois
                existing = self.db.get_pension_history(
                    martyr_id=martyr['id'],
                    month=self.current_month,
                    year=self.current_year
                )
                if existing:
                    status = QTableWidgetItem("✅ Payé")
                    status.setForeground(QBrush(QColor("#16a34a")))
                else:
                    status = QTableWidgetItem("⏳ En attente")
                    status.setForeground(QBrush(QColor("#d97706")))
                self.table_preview.setItem(row, 3, status)
            else:
                self.table_preview.setItem(row, 1, QTableWidgetItem("0"))
                self.table_preview.setItem(row, 2, QTableWidgetItem("0"))
                
                status = QTableWidgetItem("⚠️ Aucun bénéficiaire")
                status.setForeground(QBrush(QColor("#dc2626")))
                self.table_preview.setItem(row, 3, status)
            
            row += 1
    
    def pay_pensions(self):
        """Paie les pensions du mois actuel"""
        reply = QMessageBox.question(
            self, "Confirmer le paiement",
            f"Voulez-vous payer les pensions pour le mois actuel ?\n\n"
            f"Cette action est irréversible.",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            results = self.db.pay_pensions(self.current_month, self.current_year)
            
            paid = len(results['paid'])
            skipped = len(results['skipped'])
            
            if paid > 0:
                msg = f"✅ {paid} paiements effectués"
                if skipped > 0:
                    msg += f"\n⏭️ {skipped} déjà payés/ignorés"
                QMessageBox.information(self, "Succès", msg)
            elif skipped > 0:
                QMessageBox.information(self, "Information", f"Tous les paiements ({skipped}) étaient déjà effectués.")
            else:
                QMessageBox.information(self, "Information", "Aucun paiement à effectuer.")
            
            self.load_pensions()
    
    def cancel_pensions(self):
        """Annule tous les paiements du mois actuel"""
        payments = self.db.get_pension_history(month=self.current_month, year=self.current_year)
        count = len(payments)
        
        if count == 0:
            QMessageBox.information(self, "Information", "Aucun paiement à annuler pour ce mois.")
            return
        
        reply = QMessageBox.warning(
            self, "Confirmer l'annulation",
            f"Êtes-vous sûr de vouloir annuler les <b>{count}</b> paiements de ce mois ?\n\n"
            f"⚠️ Cette action est irréversible et supprimera définitivement les enregistrements.",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            result = self.db.cancel_pensions(self.current_month, self.current_year)
            
            QMessageBox.information(
                self, "Annulation effectuée",
                f"✅ {result['count']} paiements ont été annulés."
            )
            self.load_pensions()
    
    def view_history(self):
        """Ouvre le dialogue d'historique"""
        dialog = PensionHistoryDialog(self.db, self)
        dialog.exec()


class PensionHistoryDialog(QDialog):
    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db = db_manager
        
        self.setWindowTitle("Historique des pensions")
        self.setMinimumSize(1000, 700)
        
        self.setup_ui()
        self.load_history()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)
        
        # Header
        header = QLabel("📋 Historique des paiements")
        header.setObjectName("title")
        layout.addWidget(header)
        
        # Tableau
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "Date", "Martyr", "Bénéficiaire", "Type", "Montant (DT)", "Mois", "Année", "ID"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        layout.addWidget(self.table)
        
        # Total
        self.lbl_total = QLabel("Total payé : 0 DT")
        self.lbl_total.setStyleSheet("font-size: 14pt; font-weight: 700; color: #2563eb;")
        layout.addWidget(self.lbl_total)
        
        # Bouton fermer
        btn_close = QPushButton("Fermer")
        btn_close.setObjectName("ghost")
        btn_close.setMinimumHeight(44)
        btn_close.clicked.connect(self.reject)
        layout.addWidget(btn_close, alignment=Qt.AlignCenter)
    
    def load_history(self):
        self.table.setRowCount(0)
        
        payments = self.db.get_pension_history()
        
        months_names = ["", "Jan", "Fév", "Mar", "Avr", "Mai", "Juin",
                       "Juil", "Août", "Sep", "Oct", "Nov", "Déc"]
        
        total = 0.0
        for row, payment in enumerate(payments):
            self.table.insertRow(row)
            
            self.table.setItem(row, 0, QTableWidgetItem(payment.get('payment_date', '-')))
            self.table.setItem(row, 1, QTableWidgetItem(
                f"{payment.get('martyr_first', '')} {payment.get('martyr_last', '')}"
            ))
            self.table.setItem(row, 2, QTableWidgetItem(
                f"{payment.get('ben_first', '')} {payment.get('ben_last', '')}"
            ))
            self.table.setItem(row, 3, QTableWidgetItem(payment.get('beneficiary_type', '-')))
            self.table.setItem(row, 4, QTableWidgetItem(str(round(payment.get('amount', 0), 2))))
            
            month_num = payment.get('payment_month', 0)
            month_name = months_names[month_num] if 0 < month_num < 13 else "-"
            self.table.setItem(row, 5, QTableWidgetItem(month_name))
            self.table.setItem(row, 6, QTableWidgetItem(str(payment.get('payment_year', '-'))))
            self.table.setItem(row, 7, QTableWidgetItem(str(payment.get('id', '-'))))
            
            total += payment.get('amount', 0)
        
        self.lbl_total.setText(
            f"Total payé : {round(total, 2)} DT ({len(payments)} paiements)"
        )