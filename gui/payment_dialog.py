from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QComboBox, QLineEdit, QPushButton, QMessageBox,
    QFormLayout, QTableWidget, QTableWidgetItem, QHeaderView,
    QDateEdit
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QBrush, QColor

class PaymentDialog(QDialog):
    def __init__(self, db_manager, pension_id, membre_name, montant_mensuel, parent=None):
        super().__init__(parent)
        self.db = db_manager
        self.pension_id = pension_id
        self.montant_mensuel = montant_mensuel
        
        self.setWindowTitle(f"💳 Historique des paiements - {membre_name}")
        self.setMinimumSize(650, 550)
        
        self.setup_ui()
        self.load_payments()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Titre
        title = QLabel(f"💳 Paiements de la pension")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #1976d2;")
        layout.addWidget(title)
        
        # Info pension
        info = QLabel(f"""
        <b>Montant mensuel : {self.montant_mensuel:,.2f} DT</b><br>
        Complétez le formulaire ci-dessous pour enregistrer un nouveau paiement.
        """)
        info.setStyleSheet("""
            background-color: #e3f2fd; 
            padding: 15px; 
            border-radius: 8px;
            border: 1px solid #1976d2;
            font-size: 11px;
        """)
        info.setWordWrap(True)
        layout.addWidget(info)
        
        # Formulaire d'ajout
        form = QFormLayout()
        form.setSpacing(10)
        
        self.mois_annee = QLineEdit()
        self.mois_annee.setPlaceholderText("Ex: 01/2026")
        self.mois_annee.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 5px;
                background-color: white;
            }
        """)
        form.addRow("Mois/Année (MM/AAAA) :", self.mois_annee)
        
        self.montant_paye = QLineEdit()
        self.montant_paye.setPlaceholderText("Montant payé")
        self.montant_paye.setText(f"{self.montant_mensuel:.2f}")
        self.montant_paye.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 5px;
                background-color: white;
            }
        """)
        form.addRow("Montant payé (DT) :", self.montant_paye)
        
        self.mode_paiement = QComboBox()
        self.mode_paiement.addItems(["virement", "especes", "cheque"])
        self.mode_paiement.setStyleSheet("""
            QComboBox {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 5px;
                background-color: white;
            }
        """)
        form.addRow("Mode de paiement :", self.mode_paiement)
        
        self.date_paiement = QDateEdit()
        self.date_paiement.setCalendarPopup(True)
        self.date_paiement.setDate(QDate.currentDate())
        self.date_paiement.setDisplayFormat("dd/MM/yyyy")
        self.date_paiement.setStyleSheet("""
            QDateEdit {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 5px;
                background-color: white;
            }
        """)
        form.addRow("Date de paiement :", self.date_paiement)
        
        layout.addLayout(form)
        
        # Bouton ajouter
        self.btn_add = QPushButton("➕ Enregistrer le paiement")
        self.btn_add.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 12px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.btn_add.clicked.connect(self.add_payment)
        layout.addWidget(self.btn_add)
        
        # Séparateur
        separator = QLabel("─" * 50)
        separator.setAlignment(Qt.AlignCenter)
        separator.setStyleSheet("color: #ddd;")
        layout.addWidget(separator)
        
        # Titre tableau
        title_table = QLabel("📋 Historique des paiements")
        title_table.setStyleSheet("font-size: 13px; font-weight: bold; color: #666;")
        layout.addWidget(title_table)
        
        # Tableau historique
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Mois/Année", "Montant (DT)", "Mode", "Date paiement", "Statut", "Notes"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #ddd;
                border-radius: 5px;
                gridline-color: #eee;
            }
            QTableWidget::item {
                padding: 10px;
            }
            QHeaderView::section {
                background-color: #1976d2;
                color: white;
                padding: 10px;
                font-weight: bold;
            }
        """)
        self.table.setAlternatingRowColors(True)
        layout.addWidget(self.table)
        
        # Total payé
        self.label_total = QLabel("Total payé : 0 DT")
        self.label_total.setStyleSheet("""
            font-size: 14px; 
            font-weight: bold; 
            color: #2e7d32;
            background-color: #e8f5e9;
            padding: 10px;
            border-radius: 5px;
        """)
        self.label_total.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label_total)
        
        # Bouton fermer
        self.btn_close = QPushButton("❌ Fermer")
        self.btn_close.setStyleSheet("""
            QPushButton {
                background-color: #757575;
                color: white;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #616161;
            }
        """)
        self.btn_close.clicked.connect(self.accept)
        layout.addWidget(self.btn_close, alignment=Qt.AlignCenter)
    
    def load_payments(self):
        payments = self.db.get_paiements_by_pension(self.pension_id)
        self.table.setRowCount(len(payments))
        total_paye = 0
        
        for i, p in enumerate(payments):
            # Mois/Année
            self.table.setItem(i, 0, QTableWidgetItem(p['mois_annee']))
            
            # Montant
            montant_item = QTableWidgetItem(f"{p['montant_paye']:,.2f}")
            montant_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.table.setItem(i, 1, montant_item)
            total_paye += p['montant_paye']
            
            # Mode
            self.table.setItem(i, 2, QTableWidgetItem(p['mode_paiement'] or "-"))
            
            # Date paiement
            self.table.setItem(i, 3, QTableWidgetItem(p['date_paiement'] or "-"))
            
            # Statut avec couleur
            statut_item = QTableWidgetItem(p['statut'].upper())
            if p['statut'] == 'paye':
                statut_item.setBackground(QBrush(QColor("#c8e6c9")))
                statut_item.setForeground(QBrush(QColor("#2e7d32")))
            elif p['statut'] == 'retard':
                statut_item.setBackground(QBrush(QColor("#ffcdd2")))
                statut_item.setForeground(QBrush(QColor("#c62828")))
            else:
                statut_item.setBackground(QBrush(QColor("#fff9c4")))
                statut_item.setForeground(QBrush(QColor("#f57f17")))
            self.table.setItem(i, 4, statut_item)
            
            # Notes
            self.table.setItem(i, 5, QTableWidgetItem(p['notes'] or "-"))
        
        self.label_total.setText(f"Total payé : {total_paye:,.2f} DT")
    
    def add_payment(self):
        mois = self.mois_annee.text().strip()
        montant_text = self.montant_paye.text().strip()
        mode = self.mode_paiement.currentText()
        date_paiement = self.date_paiement.date().toString("yyyy-MM-dd")
        
        if not mois:
            QMessageBox.warning(self, "Erreur", "Le mois/année est obligatoire !")
            return
        
        if not montant_text:
            QMessageBox.warning(self, "Erreur", "Le montant est obligatoire !")
            return
        
        try:
            montant = float(montant_text)
        except ValueError:
            QMessageBox.warning(self, "Erreur", "Montant invalide !")
            return
        
        try:
            self.db.add_paiement(
                self.pension_id,
                mois,
                montant,
                date_paiement=date_paiement,
                mode_paiement=mode
            )
            QMessageBox.information(self, "Succès", "Paiement enregistré avec succès !")
            self.load_payments()
            self.mois_annee.clear()
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Impossible d'enregistrer le paiement :\n{str(e)}")