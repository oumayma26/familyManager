from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QComboBox, QDateEdit, QPushButton, QMessageBox,
    QFormLayout, QTableWidget, QTableWidgetItem, QHeaderView,
    QTabWidget, QLineEdit, QStackedWidget
)
from PySide6.QtCore import QDate, Qt
from PySide6.QtGui import QBrush, QColor


class PensionDialog(QDialog):
    def __init__(self, db_manager, martyr_id, martyr_name, parent=None):
        super().__init__(parent)
        self.db = db_manager
        self.martyr_id = martyr_id
        self.martyr_name = martyr_name
        
        self.setWindowTitle(f"💰 Gestion des pensions - {martyr_name}")
        self.setMinimumSize(700, 550)
        
        self.setup_ui()
        self.load_pensions()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Titre
        title = QLabel(f"💰 Pensions de la famille de {self.martyr_name}")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #1976d2;")
        layout.addWidget(title)
        
        # Info SMIG et montants
        smig = self.db.get_smig()
        pourcentages = self.db.get_all_pension_pourcentages()
        
        info = QLabel(f"""
        <b>SMIG actuel : {smig:,.0f} DT</b><br>
        Montants calculés automatiquement selon la loi tunisienne :
        • Conjoint(e) : {pourcentages.get('conjoint', 60)}% = <b>{smig * (pourcentages.get('conjoint', 60)/100):,.0f} DT</b>
        • Enfant : {pourcentages.get('enfant', 30)}% = <b>{smig * (pourcentages.get('enfant', 30)/100):,.0f} DT</b>
        • Parent : {pourcentages.get('parent', 40)}% = <b>{smig * (pourcentages.get('parent', 40)/100):,.0f} DT</b>
        • Orphelin : {pourcentages.get('orphelin', 50)}% = <b>{smig * (pourcentages.get('orphelin', 50)/100):,.0f} DT</b>
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
        
        self.combo_membre = QComboBox()
        self.combo_membre.setStyleSheet("""
            QComboBox {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 5px;
                background-color: white;
            }
        """)
        self.load_membres()
        form.addRow("Membre de la famille :", self.combo_membre)
        
        self.combo_type = QComboBox()
        self.combo_type.setStyleSheet("""
            QComboBox {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 5px;
                background-color: white;
            }
        """)
        self.combo_type.addItems([
            "Conjoint(e) - 60% du SMIG",
            "Enfant - 30% du SMIG",
            "Parent - 40% du SMIG",
            "Orphelin - 50% du SMIG"
        ])
        form.addRow("Type de pension :", self.combo_type)
        
        self.date_debut = QDateEdit()
        self.date_debut.setCalendarPopup(True)
        self.date_debut.setDate(QDate.currentDate())
        self.date_debut.setDisplayFormat("dd/MM/yyyy")
        self.date_debut.setStyleSheet("""
            QDateEdit {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 5px;
                background-color: white;
            }
        """)
        form.addRow("Date de début :", self.date_debut)
        
        layout.addLayout(form)
        
        # Bouton ajouter
        self.btn_add = QPushButton("➕ Ajouter la pension")
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
        self.btn_add.clicked.connect(self.add_pension)
        layout.addWidget(self.btn_add)
        
        # Séparateur
        separator = QLabel("─" * 50)
        separator.setAlignment(Qt.AlignCenter)
        separator.setStyleSheet("color: #ddd;")
        layout.addWidget(separator)
        
        # Titre tableau
        title_table = QLabel("📋 Pensions existantes")
        title_table.setStyleSheet("font-size: 13px; font-weight: bold; color: #666;")
        layout.addWidget(title_table)
        
        # Tableau des pensions - 7 colonnes (ajout de "Actions")
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "Membre", "Type", "% SMIG", "Montant (DT)", "Date début", "Statut", "Actions"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        # Colonne Actions en taille fixe
        self.table.horizontalHeader().setSectionResizeMode(6, QHeaderView.Fixed)
        self.table.setColumnWidth(6, 110)
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
        
        # Total
        self.label_total = QLabel("Total mensuel : 0 DT")
        self.label_total.setStyleSheet("""
            font-size: 18px; 
            font-weight: bold; 
            color: #d32f2f;
            background-color: #ffebee;
            padding: 15px;
            border-radius: 8px;
            border: 2px solid #d32f2f;
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
    
    def load_membres(self):
        """Charge les membres de la famille du martyr"""
        self.combo_membre.clear()
        members = self.db.get_family_members(self.martyr_id)
        
        for person in members:
            if person['id'] == self.martyr_id:
                continue
            
            name = f"{person['first_name']} {person['last_name']}"
            self.combo_membre.addItem(name, person['id'])
    
    def load_pensions(self):
        """Charge et affiche les pensions existantes"""
        pensions = self.db.get_pensions_by_martyr(self.martyr_id)
        pourcentages = self.db.get_all_pension_pourcentages()
        
        self.table.setRowCount(len(pensions))
        total = 0
        
        for i, p in enumerate(pensions):
            # Membre
            self.table.setItem(i, 0, QTableWidgetItem(
                f"{p['first_name']} {p['last_name']}"
            ))
            
            # Type
            self.table.setItem(i, 1, QTableWidgetItem(p['type_pension'].upper()))
            
            # % SMIG
            self.table.setItem(i, 2, QTableWidgetItem(
                f"{pourcentages.get(p['type_pension'], 0)}%"
            ))
            
            # Montant
            montant_item = QTableWidgetItem(f"{p['montant_mensuel']:,.2f}")
            montant_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.table.setItem(i, 3, montant_item)
            
            # Date début
            self.table.setItem(i, 4, QTableWidgetItem(p['date_debut'] or "-"))
            
            # Statut
            statut_item = QTableWidgetItem(p['statut'].upper())
            if p['statut'] == 'actif':
                statut_item.setBackground(QBrush(QColor("#c8e6c9")))
                statut_item.setForeground(QBrush(QColor("#2e7d32")))
                total += p['montant_mensuel']
            else:
                statut_item.setBackground(QBrush(QColor("#ffcdd2")))
                statut_item.setForeground(QBrush(QColor("#c62828")))
            self.table.setItem(i, 5, statut_item)
            
            # Bouton Paiements (colonne Actions)
            btn_paiements = QPushButton("💳 Paiements")
            btn_paiements.setStyleSheet("""
                QPushButton {
                    background-color: #2196F3;
                    color: white;
                    padding: 5px 8px;
                    border-radius: 3px;
                    font-size: 10px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #1976D2;
                }
            """)
            # Important : utiliser default args pour capturer les valeurs dans la closure
            btn_paiements.clicked.connect(
                lambda checked, pid=p['id'], 
                name=f"{p['first_name']} {p['last_name']}",
                montant=p['montant_mensuel']: 
                self.open_payments(pid, name, montant)
            )
            self.table.setCellWidget(i, 6, btn_paiements)
        
        self.label_total.setText(f"Total mensuel : {total:,.2f} DT")
    
    def open_payments(self, pension_id, membre_name, montant_mensuel):
        """Ouvre le dialogue des paiements pour une pension"""
        from gui.payment_dialog import PaymentDialog
        dialog = PaymentDialog(self.db, pension_id, membre_name, montant_mensuel, self)
        dialog.exec()
        # Rafraîchir au cas où le statut aurait changé
        self.load_pensions()
    
    def add_pension(self):
        membre_id = self.combo_membre.currentData()
        if not membre_id:
            QMessageBox.warning(self, "Erreur", "Aucun membre sélectionné !")
            return
        
        type_map = {0: 'conjoint', 1: 'enfant', 2: 'parent', 3: 'orphelin'}
        type_pension = type_map[self.combo_type.currentIndex()]
        
        date_debut = self.date_debut.date().toString("yyyy-MM-dd")
        
        try:
            self.db.add_pension(
                self.martyr_id,
                membre_id,
                type_pension,
                date_debut
            )
            QMessageBox.information(self, "Succès", "Pension ajoutée avec succès !")
            self.load_pensions()
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Impossible d'ajouter la pension :\n{str(e)}")