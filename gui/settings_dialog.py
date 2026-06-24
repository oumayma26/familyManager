from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QMessageBox, QFormLayout,
    QFrame, QGridLayout
)


class SettingsDialog(QDialog):
    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db = db_manager
        
        self.setWindowTitle("Paramètres")
        self.setMinimumWidth(500)
        self.setMinimumHeight(550)
        
        self.setup_ui()
        self.load_settings()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)
        
        # Header
        header = QLabel("⚙️ Paramètres")
        header.setObjectName("title")
        layout.addWidget(header)
        
        # ===== SECTION SMIG =====
        smig_card = QFrame()
        smig_card.setObjectName("card")
        smig_layout = QVBoxLayout(smig_card)
        smig_layout.setContentsMargins(20, 20, 20, 20)
        smig_layout.setSpacing(16)
        
        smig_title = QLabel("💰 Salaire Minimum Interprofessionnel Garanti")
        smig_title_font = smig_title.font()
        smig_title_font.setBold(True)
        smig_title_font.setPointSize(11)
        smig_title.setFont(smig_title_font)
        smig_title.setStyleSheet("color: #475569;")
        smig_layout.addWidget(smig_title)
        
        smig_form = QFormLayout()
        smig_form.setSpacing(12)
        
        self.smig_input = QLineEdit()
        self.smig_input.setPlaceholderText("Ex: 460")
        smig_form.addRow("SMIG actuel (DT)", self.smig_input)
        
        smig_layout.addLayout(smig_form)
        layout.addWidget(smig_card)
        
        # ===== SECTION PENSIONS =====
        pension_card = QFrame()
        pension_card.setObjectName("card")
        pension_layout = QVBoxLayout(pension_card)
        pension_layout.setContentsMargins(20, 20, 20, 20)
        pension_layout.setSpacing(16)
        
        pension_title = QLabel("📋 Pourcentages des pensions")
        pension_title_font = pension_title.font()
        pension_title_font.setBold(True)
        pension_title_font.setPointSize(11)
        pension_title.setFont(pension_title_font)
        pension_title.setStyleSheet("color: #475569;")
        pension_layout.addWidget(pension_title)
        
        pension_form = QFormLayout()
        pension_form.setSpacing(12)
        
        self.pourcentage_inputs = {}
        
        for type_pension, label, color in [
            ('conjoint', 'Conjoint(e)', '#818cf8'),
            ('enfant', 'Enfant', '#34d399'),
            ('parent', 'Parent', '#fbbf24'),
            ('orphelin', 'Orphelin', '#f472b6')
        ]:
            input_field = QLineEdit()
            input_field.setStyleSheet(f"""
                QLineEdit {{
                    border-left: 3px solid {color};
                    padding-left: 10px;
                }}
            """)
            pension_form.addRow(f"{label} (% du SMIG)", input_field)
            self.pourcentage_inputs[type_pension] = input_field
        
        pension_layout.addLayout(pension_form)
        
        # Info
        info = QLabel(
            "Les pensions sont calculées automatiquement :\n"
            "Montant = SMIG × Pourcentage / 100"
        )
        info.setStyleSheet("""
            background-color: #f8fafc;
            color: #64748b;
            padding: 12px 16px;
            border-radius: 8px;
            font-size: 10pt;
            border: 1px solid #e2e8f0;
        """)
        pension_layout.addWidget(info)
        
        layout.addWidget(pension_card)
        
        # ===== BOUTONS =====
        buttons = QHBoxLayout()
        buttons.setSpacing(12)
        buttons.addStretch()
        
        self.btn_cancel = QPushButton("Annuler")
        self.btn_cancel.setObjectName("ghost")
        self.btn_cancel.setMinimumHeight(40)
        self.btn_cancel.clicked.connect(self.reject)
        buttons.addWidget(self.btn_cancel)
        
        self.btn_save = QPushButton("💾 Enregistrer")
        self.btn_save.setObjectName("primary")
        self.btn_save.setMinimumHeight(44)
        self.btn_save.clicked.connect(self.save_settings)
        buttons.addWidget(self.btn_save)
        
        layout.addLayout(buttons)
        layout.addStretch()
    
    def load_settings(self):
        """Charge les paramètres actuels"""
        # SMIG
        smig = self.db.get_smig()
        self.smig_input.setText(str(smig))
        
        # Pourcentages
        pourcentages = self.db.get_all_pension_pourcentages()
        for type_pension, input_field in self.pourcentage_inputs.items():
            input_field.setText(str(pourcentages.get(type_pension, 0)))
    
    def save_settings(self):
        """Sauvegarde les paramètres"""
        try:
            # SMIG
            smig = float(self.smig_input.text().strip())
            if smig <= 0:
                raise ValueError("Le SMIG doit être positif")
            self.db.set_smig(smig)
            
            # Pourcentages
            for type_pension, input_field in self.pourcentage_inputs.items():
                pourcentage = int(input_field.text().strip())
                if pourcentage < 0 or pourcentage > 100:
                    raise ValueError(f"Le pourcentage doit être entre 0 et 100")
                self.db.set_pension_pourcentage(type_pension, pourcentage)
            
            QMessageBox.information(self, "Succès", "Paramètres mis à jour avec succès !")
            self.accept()
            
        except ValueError as e:
            QMessageBox.warning(self, "Erreur", f"Valeur invalide : {str(e)}")