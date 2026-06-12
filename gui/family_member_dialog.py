from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QDateEdit, QComboBox, QTextEdit,
    QPushButton, QFormLayout, QMessageBox, QCheckBox
)
from PySide6.QtCore import Qt, QDate


class FamilyMemberDialog(QDialog):
    def __init__(self, db_manager, martyr_id, martyr_name, parent=None):
        super().__init__(parent)
        self.db = db_manager
        self.martyr_id = martyr_id
        self.martyr_name = martyr_name
        
        self.setWindowTitle(f"🔗 Ajouter un membre de la famille de {martyr_name}")
        self.setMinimumWidth(450)
        
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Info martyr
        info = QLabel(f"Lié au martyr : <b>{self.martyr_name}</b>")
        info.setStyleSheet("color: #d32f2f; font-size: 11pt; padding: 10px; background-color: #ffebee; border-radius: 5px;")
        layout.addWidget(info)
        
        # Formulaire
        form = QFormLayout()
        
        # Type de relation
        self.rel_type = QComboBox()
        self.rel_type.addItems([
            "Enfant (fils/fille)",
            "Parent (père/mère)",
            "Conjoint(e)",
            "Frère/Sœur"
        ])
        form.addRow("Relation avec le martyr:", self.rel_type)
        
        # CIN
        self.cin = QLineEdit()
        self.cin.setPlaceholderText("Ex: AB123456")
        form.addRow("CIN:", self.cin)
        
        # Prénom
        self.first_name = QLineEdit()
        self.first_name.setPlaceholderText("Ex: Marie")
        form.addRow("Prénom *:", self.first_name)
        
        # Nom
        self.last_name = QLineEdit()
        self.last_name.setPlaceholderText("Ex: Dupont")
        form.addRow("Nom *:", self.last_name)
        
        # Date de naissance
        self.birth_date = QDateEdit()
        self.birth_date.setCalendarPopup(True)
        self.birth_date.setDisplayFormat("dd/MM/yyyy")
        self.birth_date.setSpecialValueText("Non renseignée")
        self.birth_date.setDate(QDate(1900, 1, 1))
        form.addRow("Date de naissance:", self.birth_date)
        
        # Genre
        self.gender = QComboBox()
        self.gender.addItems(["Non renseigné", "Homme", "Femme", "Autre"])
        form.addRow("Genre:", self.gender)
        
        # Notes
        self.notes = QTextEdit()
        self.notes.setPlaceholderText("Notes complémentaires...")
        self.notes.setMaximumHeight(80)
        form.addRow("Notes:", self.notes)
        
        layout.addLayout(form)
        
        # Boutons
        buttons = QHBoxLayout()
        
        self.btn_save = QPushButton("💾 Enregistrer")
        self.btn_save.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.btn_save.clicked.connect(self.save_family_member)
        
        self.btn_cancel = QPushButton("❌ Annuler")
        self.btn_cancel.clicked.connect(self.reject)
        
        buttons.addWidget(self.btn_save)
        buttons.addWidget(self.btn_cancel)
        layout.addLayout(buttons)
    
    def save_family_member(self):
        first = self.first_name.text().strip()
        last = self.last_name.text().strip()
        
        if not first or not last:
            QMessageBox.warning(self, "Champs requis", "Le prénom et le nom sont obligatoires !")
            return
        
        cin = self.cin.text().strip() or None
        
        gender_map = {0: None, 1: "M", 2: "F", 3: "O"}
        gender = gender_map[self.gender.currentIndex()]
        
        birth = self.birth_date.date()
        birth_str = birth.toString("yyyy-MM-dd") if birth.year() > 1900 else None
        
        notes = self.notes.toPlainText().strip() or None
        
        # Type de relation
        type_map = {0: "child", 1: "parent", 2: "spouse", 3: "sibling"}
        relation_type = type_map[self.rel_type.currentIndex()]
        
        try:
            # Créer la personne (famille de martyr)
            person_id = self.db.add_person(
                cin=cin,
                first_name=first,
                last_name=last,
                birth_date=birth_str,
                gender=gender,
                is_martyr=0,
                is_martyr_family=1,
                notes=notes
            )
            
            # Créer la relation avec le martyr
            self.db.add_relationship(self.martyr_id, person_id, relation_type)
            
            QMessageBox.information(self, "Succès", f"{first} {last} ajouté(e) comme membre de la famille !")
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Impossible d'ajouter :\n{str(e)}")