from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QDateEdit, QComboBox, QTextEdit,
    QPushButton, QFormLayout, QMessageBox, QCheckBox,
    QFileDialog, QFrame
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QPixmap
import os
import shutil
import sys


class FamilyMemberDialog(QDialog):
    def __init__(self, db_manager, martyr_id, martyr_name, parent=None):
        super().__init__(parent)
        self.db = db_manager
        self.martyr_id = martyr_id
        self.martyr_name = martyr_name
        self.photo_path = None
        
        self.setWindowTitle(f"🔗 Ajouter un membre de la famille de {martyr_name}")
        self.setMinimumWidth(700)
        
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
        
        # Info martyr
        info = QLabel(f"Lié au martyr : <b>{self.martyr_name}</b>")
        info.setStyleSheet("color: #d32f2f; font-size: 11pt; padding: 10px; background-color: #ffebee; border-radius: 5px;")
        layout.addWidget(info)
        
        # Layout horizontal : Formulaire + Photo
        main_layout = QHBoxLayout()
        
        # ===== FORMULAIRE =====
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
        
        # ===== Date de décès avec checkbox "En vie" =====
        death_layout = QHBoxLayout()
        
        # Checkbox "En vie" (coché par défaut = pas de date)
        self.is_alive = QCheckBox("En vie")
        self.is_alive.setChecked(True)
        self.is_alive.setStyleSheet("QCheckBox { color: #4CAF50; font-weight: bold; }")
        self.is_alive.stateChanged.connect(self.toggle_death_date)
        death_layout.addWidget(self.is_alive)
        
        # DateEdit caché par défaut
        self.death_date = QDateEdit()
        self.death_date.setCalendarPopup(True)
        self.death_date.setDisplayFormat("dd/MM/yyyy")
        self.death_date.setDate(QDate.currentDate())
        self.death_date.setVisible(False)
        death_layout.addWidget(self.death_date)
        
        form.addRow("Décès:", death_layout)
        
        # Genre
        self.gender = QComboBox()
        self.gender.addItems(["Non renseigné", "Homme", "Femme"])
        form.addRow("Genre:", self.gender)
        
        # État civil
        self.marital_status = QComboBox()
        self.marital_status.addItems(["Célibataire", "Marié(e)"])
        form.addRow("État civil:", self.marital_status)
        
        # Notes
        self.notes = QTextEdit()
        self.notes.setPlaceholderText("Notes complémentaires...")
        self.notes.setMaximumHeight(80)
        form.addRow("Notes:", self.notes)
        
        main_layout.addLayout(form, stretch=2)
        
        # ===== PHOTO =====
        photo_group = QFrame()
        photo_layout = QVBoxLayout(photo_group)
        
        # Cadre aperçu
        self.photo_frame = QFrame()
        self.photo_frame.setFixedSize(180, 220)
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
        self.photo_label.setStyleSheet("color: #999; font-size: 11px;")
        self.photo_frame.layout().addWidget(self.photo_label)
        
        photo_layout.addWidget(self.photo_frame, alignment=Qt.AlignCenter)
        
        # Boutons photo
        photo_buttons = QHBoxLayout()
        
        self.btn_browse_photo = QPushButton("📁")
        self.btn_browse_photo.setToolTip("Parcourir")
        self.btn_browse_photo.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                padding: 6px;
                border-radius: 5px;
                font-size: 11px;
            }
            QPushButton:hover { background-color: #1976D2; }
        """)
        self.btn_browse_photo.clicked.connect(self.browse_photo)
        photo_buttons.addWidget(self.btn_browse_photo)
        
        self.btn_clear_photo = QPushButton("🗑️")
        self.btn_clear_photo.setToolTip("Supprimer")
        self.btn_clear_photo.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                padding: 6px;
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
    
    def toggle_death_date(self, state):
        """Affiche/masque la date de décès selon checkbox"""
        self.death_date.setVisible(not self.is_alive.isChecked())
    
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
            160, 200,
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
        
        shutil.copy2(self.photo_path, dest_path)
        return dest_path
    
    def save_family_member(self):
        first = self.first_name.text().strip()
        last = self.last_name.text().strip()
        
        if not first or not last:
            QMessageBox.warning(self, "Erreur", "Le prénom et le nom sont obligatoires !")
            return
        
        cin = self.cin.text().strip() or None
        
        gender_map = {0: None, 1: "M", 2: "F", 3: "O"}
        gender = gender_map[self.gender.currentIndex()]
        
        birth = self.birth_date.date()
        birth_str = birth.toString("yyyy-MM-dd") if birth.year() > 1900 else None
        
        # Date de décès : null si "En vie" est coché
        if self.is_alive.isChecked():
            death_str = None
        else:
            death = self.death_date.date()
            death_str = death.toString("yyyy-MM-dd")
        
        notes = self.notes.toPlainText().strip() or None
        
        # État civil
        marital_map = {0: 'celibataire', 1: 'marie'}
        marital_status = marital_map[self.marital_status.currentIndex()]
        
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
                death_date=death_str,
                gender=gender,
                is_martyr=0,
                is_martyr_family=1,
                marital_status=marital_status,
                notes=notes,
                photo_path=None
            )
            
            # Sauvegarder la photo
            if self.photo_path:
                saved_path = self.save_photo(person_id)
                self.db.update_person(person_id, photo_path=saved_path)
            
            # Créer la relation avec le martyr
            self.db.add_relationship(self.martyr_id, person_id, relation_type)
            
            QMessageBox.information(self, "Succès", f"{first} {last} ajouté(e) comme membre de la famille !")
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Impossible d'ajouter :\n{str(e)}")