from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QDateEdit, QComboBox, QTextEdit,
    QPushButton, QFormLayout, QMessageBox, QGroupBox, QCheckBox
)
from PySide6.QtCore import Signal, Qt, QDate


class PersonForm(QWidget):
    person_saved = Signal(int)
    add_relation_requested = Signal()

    def __init__(self, db_manager):
        super().__init__()
        self.db = db_manager
        self.current_person_id = None
        
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Titre
        title = QLabel("📝 Informations personnelles")
        title_font = title.font()
        title_font.setPointSize(12)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # Formulaire
        form_group = QGroupBox()
        form_layout = QFormLayout(form_group)
        form_layout.setSpacing(10)
        
        # CIN
        self.cin = QLineEdit()
        self.cin.setPlaceholderText("Ex: AB123456")
        form_layout.addRow("CIN:", self.cin)
        
        # Prénom
        self.first_name = QLineEdit()
        self.first_name.setPlaceholderText("Ex: Marie")
        form_layout.addRow("Prénom *:", self.first_name)
        
        # Nom
        self.last_name = QLineEdit()
        self.last_name.setPlaceholderText("Ex: Dupont")
        form_layout.addRow("Nom *:", self.last_name)
        
        # Date de naissance
        self.birth_date = QDateEdit()
        self.birth_date.setCalendarPopup(True)
        self.birth_date.setDisplayFormat("dd/MM/yyyy")
        self.birth_date.setSpecialValueText("Non renseignée")
        self.birth_date.setDate(QDate(1900, 1, 1))
        form_layout.addRow("Date de naissance:", self.birth_date)
        
        # Date de décès
        self.death_date = QDateEdit()
        self.death_date.setCalendarPopup(True)
        self.death_date.setDisplayFormat("dd/MM/yyyy")
        self.death_date.setSpecialValueText("En vie")
        self.death_date.setDate(QDate(1900, 1, 1))
        form_layout.addRow("Date de décès:", self.death_date)
        
        # Genre
        self.gender = QComboBox()
        self.gender.addItems(["Non renseigné", "Homme", "Femme"])
        self.gender.setCurrentIndex(0)
        form_layout.addRow("Genre:", self.gender)
        
        # Martyr
        self.is_martyr = QCheckBox("☪️ Martyr")
        self.is_martyr.setStyleSheet("QCheckBox { font-weight: bold; color: #d32f2f; font-size: 11pt; }")
        form_layout.addRow("Statut:", self.is_martyr)

        # Famille de martyr
        self.is_martyr_family = QCheckBox("👨‍👩‍👧‍👦 Membre de la famille d'un martyr")
        self.is_martyr_family.setStyleSheet("QCheckBox { color: #1976d2; }")
        form_layout.addRow("Statut:", self.is_martyr_family)
        
        # Notes
        self.notes = QTextEdit()
        self.notes.setPlaceholderText("Notes, anecdotes, informations complémentaires...")
        self.notes.setMaximumHeight(100)
        form_layout.addRow("Notes:", self.notes)
        
        layout.addWidget(form_group)
        
        # Boutons
        buttons_layout = QHBoxLayout()
        
        self.btn_save = QPushButton("💾 Enregistrer")
        self.btn_save.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        self.btn_save.clicked.connect(self.save_person)

        # Bouton ajouter relation
        self.btn_add_relation = QPushButton("🔗 Ajouter un membre de famille")
        self.btn_add_relation.setStyleSheet("""
            QPushButton {
                background-color: #FF9800;
                color: white;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #F57C00;
            }
            QPushButton:disabled {
                background-color: #ccc;
                color: #666;
            }
        """)
        self.btn_add_relation.clicked.connect(self.request_add_relation)
        self.btn_add_relation.setEnabled(False)  # Désactivé par défaut
        buttons_layout.addWidget(self.btn_add_relation)

        # Bouton gérer les pensions
        self.btn_pensions = QPushButton("💰 Gérer les pensions")
        self.btn_pensions.setStyleSheet("""
            QPushButton {
                background-color: #FF9800;
                color: white;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #F57C00;
            }
            QPushButton:disabled {
                background-color: #ccc;
                color: #666;
            }
        """)
        self.btn_pensions.clicked.connect(self.open_pensions)
        self.btn_pensions.setEnabled(False)
        buttons_layout.addWidget(self.btn_pensions)
        
        self.btn_clear = QPushButton("🔄 Nouveau")
        self.btn_clear.setStyleSheet("""
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
        self.btn_clear.clicked.connect(self.clear_form)
        
        buttons_layout.addWidget(self.btn_save)
        buttons_layout.addWidget(self.btn_clear)
        buttons_layout.addStretch()
        
        layout.addLayout(buttons_layout)
        layout.addStretch()
    
    def load_person(self, person):
        self.current_person_id = person['id']
        self.cin.setText(person['cin'] or "")
        self.first_name.setText(person['first_name'] or "")
        self.last_name.setText(person['last_name'] or "")
        self.btn_add_relation.setEnabled(True)
        self.btn_pensions.setEnabled(True)

        if person['birth_date']:
            date = QDate.fromString(person['birth_date'], "yyyy-MM-dd")
            self.birth_date.setDate(date)
        else:
            self.birth_date.setDate(QDate(1900, 1, 1))
        
        if person['death_date']:
            date = QDate.fromString(person['death_date'], "yyyy-MM-dd")
            self.death_date.setDate(date)
        else:
            self.death_date.setDate(QDate(1900, 1, 1))
        
        gender_map = {"": 0, "M": 1, "F": 2}
        self.gender.setCurrentIndex(gender_map.get(person['gender'], 0))
        
        self.is_martyr.setChecked(True)
        self.is_martyr_family.setChecked(bool(person.get('is_martyr_family', 0)))
        self.notes.setPlainText(person['notes'] or "")
    
    def clear_form(self):
        self.current_person_id = None
        self.cin.clear()
        self.first_name.clear()
        self.last_name.clear()
        self.birth_date.setDate(QDate(1900, 1, 1))
        self.death_date.setDate(QDate(1900, 1, 1))
        self.gender.setCurrentIndex(0)
        self.is_martyr.setChecked(True)
        self.is_martyr_family.setChecked(False)
        self.notes.clear()
        self.btn_add_relation.setEnabled(False)
        self.btn_pensions.setEnabled(False)

    
    def save_person(self):
        first = self.first_name.text().strip()
        last = self.last_name.text().strip()
        
        if not first or not last:
            QMessageBox.warning(self, "Champs requis", 
                              "Le prénom et le nom sont obligatoires !")
            return
        
        cin = self.cin.text().strip() or None
        
        gender_map = {0: None, 1: "M", 2: "F"}
        gender = gender_map[self.gender.currentIndex()]
        
        birth = self.birth_date.date()
        birth_str = birth.toString("yyyy-MM-dd") if birth.year() > 1900 else None
        
        death = self.death_date.date()
        death_str = death.toString("yyyy-MM-dd") if death.year() > 1900 else None
        
        is_martyr = 1 if self.is_martyr.isChecked() else 0
        is_martyr_family = 1 if self.is_martyr_family.isChecked() else 0
        
        notes = self.notes.toPlainText().strip() or None
        
        try:
            if self.current_person_id:
                self.db.update_person(
                    self.current_person_id,
                    cin=cin,
                    first_name=first,
                    last_name=last,
                    birth_date=birth_str,
                    death_date=death_str,
                    gender=gender,
                    is_martyr=is_martyr,
                    is_martyr_family=is_martyr_family,
                    notes=notes
                )
                person_id = self.current_person_id
                QMessageBox.information(self, "Succès", "Personne mise à jour !")
            else:
                person_id = self.db.add_person(
                    cin=cin,
                    first_name=first,
                    last_name=last,
                    birth_date=birth_str,
                    death_date=death_str,
                    gender=gender,
                    is_martyr=is_martyr,
                    notes=notes
                )
                self.current_person_id = person_id
                QMessageBox.information(self, "Succès", "Personne ajoutée !")
            
            self.person_saved.emit(person_id)
            
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Une erreur est survenue :\n{str(e)}")

    def request_add_relation(self):
        # Ouvrir le dialogue d'ajout de membre de famille
        from gui.family_member_dialog import FamilyMemberDialog
        
        # Récupérer le nom du martyr actuel
        martyr_name = f"{self.first_name.text()} {self.last_name.text()}"
        
        dialog = FamilyMemberDialog(self.db, self.current_person_id, martyr_name, self)
        if dialog.exec() == QDialog.Accepted:
            self.add_relation_requested.emit()

    def open_pensions(self):
        from gui.pension_dialog import PensionDialog
        
        martyr_name = f"{self.first_name.text()} {self.last_name.text()}"
        dialog = PensionDialog(self.db, self.current_person_id, martyr_name, self)
        dialog.exec()