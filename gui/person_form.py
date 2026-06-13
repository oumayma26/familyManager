from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QDateEdit, QComboBox, QTextEdit,
    QPushButton, QFormLayout, QMessageBox, QGroupBox, QCheckBox,
    QDialog, QFileDialog, QFrame
)
from PySide6.QtCore import Signal, Qt, QDate
from PySide6.QtGui import QPixmap
import os
import shutil
import sys


class PersonForm(QWidget):
    person_saved = Signal(int)
    add_relation_requested = Signal()

    def __init__(self, db_manager):
        super().__init__()
        self.db = db_manager
        self.current_person_id = None
        self.photo_path = None
        
        self.setup_ui()
    
    def get_photos_dir(self):
        """Retourne le chemin du dossier photos"""
        if getattr(sys, 'frozen', False):
            base_dir = os.path.dirname(sys.executable)
        else:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        photos_dir = os.path.join(base_dir, "photos")
        os.makedirs(photos_dir, exist_ok=True)
        return photos_dir
    
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
        
        # Layout horizontal : Formulaire + Photo
        main_layout = QHBoxLayout()
        
        # ===== FORMULAIRE =====
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

        # État civil
        self.marital_status = QComboBox()
        self.marital_status.addItems(["Célibataire", "Marié(e)"])
        form_layout.addRow("État civil:", self.marital_status)

        # Famille de martyr
        self.is_martyr_family = QCheckBox("👨‍👩‍👧‍👦 Membre de la famille d'un martyr")
        self.is_martyr_family.setStyleSheet("QCheckBox { color: #1976d2; }")
        form_layout.addRow("Statut:", self.is_martyr_family)
        
        # Notes
        self.notes = QTextEdit()
        self.notes.setPlaceholderText("Notes, anecdotes, informations complémentaires...")
        self.notes.setMaximumHeight(100)
        form_layout.addRow("Notes:", self.notes)
        
        main_layout.addWidget(form_group, stretch=2)
        
        # ===== PHOTO =====
        photo_group = QGroupBox("📷 Photo")
        photo_layout = QVBoxLayout(photo_group)
        
        # Cadre aperçu
        self.photo_frame = QFrame()
        self.photo_frame.setFixedSize(200, 250)
        self.photo_frame.setStyleSheet("""
            QFrame {
                border: 2px dashed #ccc;
                border-radius: 10px;
                background-color: #f5f5f5;
            }
        """)
        self.photo_frame.setLayout(QVBoxLayout())
        
        self.photo_label = QLabel("Aucune photo")
        self.photo_label.setAlignment(Qt.AlignCenter)
        self.photo_label.setStyleSheet("color: #999; font-size: 12px;")
        self.photo_frame.layout().addWidget(self.photo_label)
        
        photo_layout.addWidget(self.photo_frame, alignment=Qt.AlignCenter)
        
        # Boutons photo
        photo_buttons = QHBoxLayout()
        
        self.btn_browse_photo = QPushButton("📁 Parcourir")
        self.btn_browse_photo.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                padding: 8px;
                border-radius: 5px;
                font-size: 11px;
            }
            QPushButton:hover { background-color: #1976D2; }
        """)
        self.btn_browse_photo.clicked.connect(self.browse_photo)
        photo_buttons.addWidget(self.btn_browse_photo)
        
        self.btn_clear_photo = QPushButton("🗑️ Supprimer")
        self.btn_clear_photo.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                padding: 8px;
                border-radius: 5px;
                font-size: 11px;
            }
            QPushButton:hover { background-color: #da190b; }
        """)
        self.btn_clear_photo.clicked.connect(self.clear_photo)
        self.btn_clear_photo.setEnabled(False)
        photo_buttons.addWidget(self.btn_clear_photo)
        
        photo_layout.addLayout(photo_buttons)
        photo_layout.addStretch()
        
        main_layout.addWidget(photo_group, stretch=1)
        
        layout.addLayout(main_layout)
        
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
        self.btn_add_relation.setEnabled(False)
        buttons_layout.addWidget(self.btn_add_relation)

        
        
        buttons_layout.addWidget(self.btn_save)
        buttons_layout.addStretch()
        
        layout.addLayout(buttons_layout)
        layout.addStretch()
    
    def browse_photo(self):
        """Ouvre un dialogue pour sélectionner une photo"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Sélectionner une photo",
            "",
            "Images (*.png *.jpg *.jpeg *.bmp *.gif)"
        )
        
        if not file_path:
            return
        
        # Vérifier taille max 5 Mo
        size_mb = os.path.getsize(file_path) / (1024 * 1024)
        if size_mb > 5:
            QMessageBox.warning(self, "Fichier trop grand", 
                              f"La photo fait {size_mb:.1f} Mo (max 5 Mo)")
            return
        
        self.display_photo(file_path)
        self.photo_path = file_path
        self.btn_clear_photo.setEnabled(True)
    
    def display_photo(self, image_path):
        """Affiche une photo dans le cadre"""
        pixmap = QPixmap(image_path)
        if pixmap.isNull():
            QMessageBox.warning(self, "Erreur", "Impossible de charger l'image")
            return
        
        scaled = pixmap.scaled(
            180, 230,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        
        self.photo_label.setPixmap(scaled)
        self.photo_label.setText("")
        self.photo_frame.setStyleSheet("""
            QFrame {
                border: 2px solid #4CAF50;
                border-radius: 10px;
                background-color: white;
            }
        """)
    
    def clear_photo(self):
        """Supprime la photo actuelle"""
        self.photo_label.clear()
        self.photo_label.setText("Aucune photo")
        self.photo_label.setPixmap(QPixmap())
        self.photo_path = None
        self.btn_clear_photo.setEnabled(False)
        self.photo_frame.setStyleSheet("""
            QFrame {
                border: 2px dashed #ccc;
                border-radius: 10px;
                background-color: #f5f5f5;
            }
        """)
    
    def save_photo(self, person_id):
        """Sauvegarde la photo dans le dossier photos/"""
        if not self.photo_path:
            return None
        
        photos_dir = self.get_photos_dir()
        ext = os.path.splitext(self.photo_path)[1].lower() or ".jpg"
        new_name = f"person_{person_id}{ext}"
        dest_path = os.path.join(photos_dir, new_name)
        
        # Supprimer ancienne photo si existe
        for f in os.listdir(photos_dir):
            if f.startswith(f"person_{person_id}."):
                os.remove(os.path.join(photos_dir, f))
        
        shutil.copy2(self.photo_path, dest_path)
        return dest_path
    
    def delete_photo(self, person_id):
        """Supprime la photo d'une personne"""
        photos_dir = self.get_photos_dir()
        for f in os.listdir(photos_dir):
            if f.startswith(f"person_{person_id}."):
                try:
                    os.remove(os.path.join(photos_dir, f))
                except Exception as e:
                    print(f"Erreur suppression photo: {e}")
    
    def load_photo(self, person_id, photo_path):
        """Charge la photo d'une personne existante"""
        if not photo_path:
            return
        
        if os.path.exists(photo_path):
            self.display_photo(photo_path)
            self.photo_path = photo_path
            self.btn_clear_photo.setEnabled(True)
            return
        
        # Chercher dans le dossier photos
        photos_dir = self.get_photos_dir()
        for f in os.listdir(photos_dir):
            if f.startswith(f"person_{person_id}."):
                full_path = os.path.join(photos_dir, f)
                self.display_photo(full_path)
                self.photo_path = full_path
                self.btn_clear_photo.setEnabled(True)
                return
    
    def load_person(self, person):
        self.current_person_id = person['id']
        self.cin.setText(person['cin'] or "")
        self.first_name.setText(person['first_name'] or "")
        self.last_name.setText(person['last_name'] or "")
        self.btn_add_relation.setEnabled(True)

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

        # État civil
        marital_map = {'celibataire': 0, 'marie': 1}
        self.marital_status.setCurrentIndex(marital_map.get(person.get('marital_status', 'celibataire'), 0))
        
        self.is_martyr.setChecked(bool(person.get('is_martyr', 0)))
        self.is_martyr_family.setChecked(bool(person.get('is_martyr_family', 0)))
        self.notes.setPlainText(person['notes'] or "")
        
        # Charger la photo
        self.load_photo(person['id'], person.get('photo_path'))
    
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
        self.clear_photo()
        self.marital_status.setCurrentIndex(0)

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

        marital_map = {0: 'celibataire', 1: 'marie'}
        marital_status = marital_map[self.marital_status.currentIndex()]
        
        notes = self.notes.toPlainText().strip() or None
        
        try:
            if self.current_person_id:
                # Mise à jour
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
                    notes=notes,
                    marital_status=marital_status
                )
                
                # Gérer la photo
                if self.photo_path:
                    saved_path = self.save_photo(self.current_person_id)
                    self.db.update_person(self.current_person_id, photo_path=saved_path)
                elif not self.photo_label.pixmap():
                    self.delete_photo(self.current_person_id)
                    self.db.update_person(self.current_person_id, photo_path=None)
                
                person_id = self.current_person_id
                QMessageBox.information(self, "Succès", "Personne mise à jour !")
            else:
                # Création
                person_id = self.db.add_person(
                    cin=cin,
                    first_name=first,
                    last_name=last,
                    birth_date=birth_str,
                    death_date=death_str,
                    gender=gender,
                    is_martyr=is_martyr,
                    is_martyr_family=is_martyr_family,
                    marital_status=marital_status,
                    notes=notes,
                    photo_path=None
                )
                
                # Sauvegarder la photo
                if self.photo_path:
                    saved_path = self.save_photo(person_id)
                    self.db.update_person(person_id, photo_path=saved_path)
                
                self.current_person_id = person_id
                QMessageBox.information(self, "Succès", "Personne ajoutée !")
            
            self.person_saved.emit(person_id)
            
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Une erreur est survenue :\n{str(e)}")

    def request_add_relation(self):
        from gui.family_member_dialog import FamilyMemberDialog
        
        martyr_name = f"{self.first_name.text()} {self.last_name.text()}"
        
        dialog = FamilyMemberDialog(self.db, self.current_person_id, martyr_name, self)
        if dialog.exec() == QDialog.Accepted:
            self.add_relation_requested.emit()