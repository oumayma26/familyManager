from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QMessageBox, QFormLayout
)


class SettingsDialog(QDialog):
    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db = db_manager
        
        self.setWindowTitle("⚙️ Paramètres de l'application")
        self.setMinimumWidth(450)
        
        self.setup_ui()
        self.load_settings()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Titre
        title = QLabel("⚙️ Paramètres")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #1976d2;")
        layout.addWidget(title)
        
        # Formulaire
        form = QFormLayout()
        form.setSpacing(10)
        
        # SMIG
        self.smig_input = QLineEdit()
        self.smig_input.setPlaceholderText("Ex: 460")
        self.smig_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 5px;
            }
        """)
        form.addRow("SMIG actuel (DT) :", self.smig_input)
        
        # Séparateur
        sep = QLabel("─" * 40)
        sep.setStyleSheet("color: #ddd; margin: 10px 0;")
        layout.addWidget(sep)
        
        # Pourcentages des pensions
        title_pensions = QLabel("📋 Pourcentages des pensions")
        title_pensions.setStyleSheet("font-size: 13px; font-weight: bold; color: #1976d2;")
        layout.addWidget(title_pensions)
        
        self.pourcentage_inputs = {}
        
        for type_pension, label in [
            ('conjoint', 'Conjoint(e)'),
            ('enfant', 'Enfant'),
            ('parent', 'Parent'),
            ('orphelin', 'Orphelin')
        ]:
            input_field = QLineEdit()
            input_field.setStyleSheet("""
                QLineEdit {
                    padding: 8px;
                    border: 1px solid #ddd;
                    border-radius: 5px;
                }
            """)
            form.addRow(f"{label} (% du SMIG) :", input_field)
            self.pourcentage_inputs[type_pension] = input_field
        
        layout.addLayout(form)
        
        # Info
        info = QLabel("""
        Les pensions sont calculées automatiquement :
        Montant = SMIG × Pourcentage / 100
        """)
        info.setStyleSheet("background-color: #e3f2fd; padding: 10px; border-radius: 5px; font-size: 11px;")
        layout.addWidget(info)
        
        # Boutons
        buttons = QHBoxLayout()
        
        self.btn_save = QPushButton("💾 Enregistrer")
        self.btn_save.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.btn_save.clicked.connect(self.save_settings)
        
        self.btn_cancel = QPushButton("❌ Annuler")
        self.btn_cancel.setStyleSheet("""
            QPushButton {
                background-color: #757575;
                color: white;
                padding: 10px 20px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #616161;
            }
        """)
        self.btn_cancel.clicked.connect(self.reject)
        
        buttons.addWidget(self.btn_save)
        buttons.addWidget(self.btn_cancel)
        layout.addLayout(buttons)
    
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