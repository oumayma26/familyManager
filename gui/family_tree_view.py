from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTreeWidget, 
    QTreeWidgetItem, QPushButton, QHBoxLayout, QComboBox,
    QTableWidget, QTableWidgetItem, QHeaderView, QStackedWidget,
    QAbstractItemView, QCheckBox, QMessageBox, QFrame
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QPixmap, QIcon, QPainter, QBrush, QColor, QFont

import os
import sys
from datetime import datetime


class FamilyTreeView(QWidget):
    def __init__(self, db_manager):
        super().__init__()
        self.db = db_manager
        self.current_person_id = None
        self.setup_ui()

    def get_photos_dir(self):
        """Retourne le chemin du dossier photos"""
        if getattr(sys, 'frozen', False):
            base_dir = os.path.dirname(sys.executable)
        else:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(base_dir, "photos")

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)

        # Header
        header = QLabel("🌳 Arbre généalogique")
        header.setObjectName("title")
        layout.addWidget(header)

        # Contrôles
        controls = QHBoxLayout()
        controls.setSpacing(12)

        controls.addWidget(QLabel("Centrer sur :"))

        self.combo_persons = QComboBox()
        self.combo_persons.setMinimumWidth(240)
        self.combo_persons.currentIndexChanged.connect(self.on_combo_changed)
        controls.addWidget(self.combo_persons)

        # Bouton toggle Arbre / Tableau
        self.btn_toggle = QPushButton("📊 Voir Tableau")
        self.btn_toggle.setObjectName("primary")
        self.btn_toggle.setMinimumHeight(36)
        self.btn_toggle.clicked.connect(self.toggle_view)
        controls.addWidget(self.btn_toggle)

        controls.addStretch()
        layout.addLayout(controls)

        # Stack pour switcher entre Arbre et Tableau
        self.stack = QStackedWidget()

        # ===== VUE ARBRE =====
        self.tree_widget = QWidget()
        tree_layout = QVBoxLayout(self.tree_widget)
        tree_layout.setContentsMargins(0, 0, 0, 0)

        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)
        self.tree.setIconSize(QSize(44, 44))
        self.tree.setStyleSheet("""
            QTreeWidget {
                border: 1px solid #e2e8f0;
                border-radius: 12px;
                padding: 8px;
                outline: none;
            }
            QTreeWidget::item {
                padding: 10px;
                min-height: 52px;
                border-radius: 8px;
                margin: 2px 4px;
            }
            QTreeWidget::item:selected {
                background-color: #e0e7ff;
                color: #4338ca;
            }
            QTreeWidget::item:hover {
                background-color: #f8fafc;
            }
        """)
        tree_layout.addWidget(self.tree)

        # ===== VUE TABLEAU =====
        self.table_widget = QWidget()
        table_layout = QVBoxLayout(self.table_widget)
        table_layout.setContentsMargins(0, 0, 0, 0)

        self.table = QTableWidget()
        self.table.setColumnCount(10)
        self.table.setHorizontalHeaderLabels([
            "Photo", "Nom", "CIN", "Relation", "Genre", "Naissance", "En vie", "Décès", "Statut", ""
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)
        self.table.horizontalHeader().setSectionResizeMode(9, QHeaderView.Fixed)
        self.table.setColumnWidth(0, 52)
        self.table.setColumnWidth(9, 44)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.cellClicked.connect(self.on_table_cell_clicked)
        table_layout.addWidget(self.table)

        # Ajouter au stack
        self.stack.addWidget(self.tree_widget)
        self.stack.addWidget(self.table_widget)

        layout.addWidget(self.stack)

        self.refresh_combo()

    def toggle_view(self):
        """Switch entre Arbre et Tableau"""
        if self.stack.currentIndex() == 0:
            self.stack.setCurrentIndex(1)
            self.btn_toggle.setText("🌳 Voir Arbre")
            self.load_table()
        else:
            self.stack.setCurrentIndex(0)
            self.btn_toggle.setText("📊 Voir Tableau")
            if self.current_person_id:
                self.load_tree(self.current_person_id)

    def refresh_combo(self):
        self.combo_persons.clear()
        persons = self.db.get_all_persons()

        for person in persons:
            name = f"{person['first_name']} {person['last_name']}"
            self.combo_persons.addItem(name, person['id'])

    def on_combo_changed(self, index):
        person_id = self.combo_persons.itemData(index)
        if person_id:
            self.load_tree(person_id)

    def create_default_avatar(self, gender, size=40):
        """Crée une icône avatar par défaut selon le genre"""
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.transparent)

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)

        if gender == "M":
            color = QColor("#818cf8")
        elif gender == "F":
            color = QColor("#f472b6")
        else:
            color = QColor("#94a3b8")

        painter.setBrush(QBrush(color))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(2, 2, size-4, size-4)

        painter.setPen(QColor("white"))
        font = painter.font()
        font.setPointSize(11)
        font.setBold(True)
        painter.setFont(font)

        initial = "?" if gender not in ["M", "F"] else ("H" if gender == "M" else "F")
        painter.drawText(pixmap.rect(), Qt.AlignCenter, initial)

        painter.end()
        return QIcon(pixmap)

    def get_person_icon(self, person, size=44):
        """Retourne l'icône d'une personne (photo ou avatar)"""
        photo_path = person.get('photo_path')
        person_id = person.get('id')

        if photo_path and os.path.exists(photo_path):
            pixmap = QPixmap(photo_path)
            if not pixmap.isNull():
                return QIcon(pixmap.scaled(size, size, Qt.KeepAspectRatio, Qt.SmoothTransformation))

        purchases_dir = self.get_photos_dir()
        if person_id and os.path.exists(purchases_dir):
            for f in os.listdir(purchases_dir):
                if f.startswith(f"person_{person_id}."):
                    full_path = os.path.join(purchases_dir, f)
                    pixmap = QPixmap(full_path)
                    if not pixmap.isNull():
                        return QIcon(pixmap.scaled(size, size, Qt.KeepAspectRatio, Qt.SmoothTransformation))

        return self.create_default_avatar(person.get('gender'), size)

    def load_tree(self, person_id):
        """Charge l'arbre généalogique avec photos"""
        self.current_person_id = person_id
        self.tree.clear()

        person = self.db.get_person(person_id)
        if not person:
            return

        root_text = f"{person['first_name']} {person['last_name']}"
        if person.get('is_martyr'):
            root_text += "  ☪️"

        root = QTreeWidgetItem(self.tree)
        root.setText(0, root_text)
        root.setIcon(0, self.get_person_icon(person, 44))
        root.setData(0, Qt.UserRole, person['id'])
        root.setSizeHint(0, QSize(0, 56))

        self._load_relations_recursive(root, person_id, set())
        self.tree.expandAll()

    def _load_relations_recursive(self, parent_item, person_id, visited):
        """Charge récursivement les relations avec photos"""
        if person_id in visited:
            return

        visited.add(person_id)
        relations = self.db.get_relationships(person_id)

        for rel in relations:
            if rel['person1_id'] == person_id:
                other_id = rel['person2_id']
            else:
                other_id = rel['person1_id']

            if other_id in visited:
                continue

            other = self.db.get_person(other_id)
            if not other:
                continue

            node = QTreeWidgetItem(parent_item)
            rel_type = rel['relation_type']
            type_labels = {
                'parent': '👨‍👩‍👧 Parent',
                'child': '👶 Enfant',
                'spouse': '💍 Conjoint(e)',
                'sibling': '👫 Frère/Sœur'
            }

            label = f"{other['first_name']} {other['last_name']}"
            if other.get('is_martyr_family'):
                label += "  👨‍👩‍👧‍👦"

            node.setText(0, f"{type_labels.get(rel_type, rel_type)} : {label}")
            node.setIcon(0, self.get_person_icon(other, 44))
            node.setData(0, Qt.UserRole, other_id)
            node.setSizeHint(0, QSize(0, 52))

            self._load_relations_recursive(node, other_id, visited.copy())

    def on_alive_toggled(self, person_id, checked):
        """Appelé quand on coche/décoche la case 'En vie'"""
        if checked:
            self.db.update_person(person_id, death_date=None)
        else:
            from datetime import date
            today = date.today().strftime("%Y-%m-%d")
            self.db.update_person(person_id, death_date=today)
        self.load_table()

    def on_table_cell_clicked(self, row, column):
        """Gère le clic sur une cellule du tableau"""
        if column == 9:
            item = self.table.item(row, 9)
            if item and item.text() == "✕":
                person_id = item.data(Qt.UserRole)
                person_name = self.table.item(row, 1).text()
                self.delete_family_member(person_id, person_name)

    def delete_family_member(self, person_id, person_name):
        """Supprime un membre de la famille"""
        reply = QMessageBox.question(
            self, "Confirmer la suppression",
            f"Êtes-vous sûr de vouloir supprimer {person_name} ?\n"
            "Cette personne sera supprimée définitivement.",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.db.delete_person(person_id)
            QMessageBox.information(self, "Succès", f"{person_name} a été supprimé(e) !")
            self.load_table()

    def load_table(self):
        """Charge le tableau avec photos"""
        if not self.current_person_id:
            return

        self.table.setRowCount(0)
        martyr = self.db.get_person(self.current_person_id)
        if not martyr:
            return

        family_members = self.db.get_family_members(self.current_person_id)
        relations = self.db.get_relationships(self.current_person_id)
        related_ids = set()
        for rel in relations:
            related_ids.add(rel['person1_id'])
            related_ids.add(rel['person2_id'])

        all_persons = {p['id']: p for p in family_members}
        for pid in related_ids:
            if pid not in all_persons:
                person = self.db.get_person(pid)
                if person:
                    all_persons[pid] = person

        row = 0
        for person in all_persons.values():
            self.table.insertRow(row)
            self.table.setRowHeight(row, 52)

            is_martyr = (person['id'] == martyr['id'])

            # === COLONNE 0 : PHOTO ===
            photo_item = QTableWidgetItem()
            photo_item.setIcon(self.get_person_icon(person, 36))
            photo_item.setTextAlignment(Qt.AlignCenter)
            if is_martyr:
                photo_item.setFlags(photo_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(row, 0, photo_item)

            # === COLONNE 1 : NOM ===
            name_item = QTableWidgetItem(f"{person['first_name']} {person['last_name']}")
            if person.get('is_martyr'):
                name_item.setText("☪️  " + name_item.text())
            elif person.get('is_martyr_family'):
                name_item.setText("👨‍👩‍👧‍👦  " + name_item.text())
            if is_martyr:
                name_item.setFlags(name_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(row, 1, name_item)

            # === COLONNE 2 : CIN ===
            cin_item = QTableWidgetItem(person.get('cin') or "—")
            cin_item.setForeground(QBrush(QColor("#94a3b8")))
            if is_martyr:
                cin_item.setFlags(cin_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(row, 2, cin_item)

            # === COLONNE 3 : RELATION ===
            relation_text = self.get_relation_text(person['id'], martyr['id'])
            relation_item = QTableWidgetItem(relation_text)
            if is_martyr:
                relation_item.setFlags(relation_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(row, 3, relation_item)

            # === COLONNE 4 : GENRE ===
            gender_map = {"M": "Homme", "F": "Femme", "O": "Autre", None: "—"}
            gender_item = QTableWidgetItem(gender_map.get(person.get('gender'), "—"))
            if is_martyr:
                gender_item.setFlags(gender_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(row, 4, gender_item)

            # === COLONNE 5 : DATE NAISSANCE ===
            birth_item = QTableWidgetItem(person.get('birth_date') or "—")
            birth_item.setForeground(QBrush(QColor("#94a3b8")))
            if is_martyr:
                birth_item.setFlags(birth_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(row, 5, birth_item)

            # === COLONNE 6 : EN VIE (checkbox) ===
            death_date_str = person.get('death_date')
            is_alive = not (death_date_str and death_date_str.strip())

            chk_alive = QCheckBox()
            chk_alive.setChecked(is_alive)
            chk_alive.setEnabled(not is_martyr)
            if is_martyr:
                chk_alive.setToolTip("Le martyr ne peut pas être modifié ici")

            chk_widget = QWidget()
            chk_layout = QHBoxLayout(chk_widget)
            chk_layout.addWidget(chk_alive)
            chk_layout.setAlignment(Qt.AlignCenter)
            chk_layout.setContentsMargins(0, 0, 0, 0)
            self.table.setCellWidget(row, 6, chk_widget)

            if not is_martyr:
                person_id_copy = person['id']
                chk_alive.toggled.connect(
                    lambda checked, pid=person_id_copy: 
                    self.on_alive_toggled(pid, checked)
                )

            # === COLONNE 7 : DATE DÉCÈS ===
            if death_date_str and death_date_str.strip():
                try:
                    date_obj = datetime.strptime(death_date_str, "%Y-%m-%d")
                    date_formatted = date_obj.strftime("%d/%m/%Y")
                except:
                    date_formatted = death_date_str

                death_item = QTableWidgetItem(date_formatted)
                death_item.setForeground(QBrush(QColor("#dc2626")))
            else:
                death_item = QTableWidgetItem("—")
                death_item.setForeground(QBrush(QColor("#16a34a")))

            font = death_item.font()
            font.setBold(True)
            death_item.setFont(font)
            death_item.setTextAlignment(Qt.AlignCenter)
            if is_martyr:
                death_item.setFlags(death_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(row, 7, death_item)

            # === COLONNE 8 : STATUT ===
            if person.get('is_martyr'):
                status = "☪️ Martyr"
            elif person.get('is_martyr_family'):
                status = "👨‍👩‍👧‍👦 Famille"
            else:
                status = "—"
            status_item = QTableWidgetItem(status)
            if is_martyr:
                status_item.setFlags(status_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(row, 8, status_item)

            # === COLONNE 9 : SUPPRIMER ===
            if not is_martyr:
                delete_item = QTableWidgetItem("✕")
                delete_item.setTextAlignment(Qt.AlignCenter)
                delete_item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
                delete_item.setForeground(QBrush(QColor("#dc2626")))
                font = delete_item.font()
                font.setPointSize(13)
                font.setBold(True)
                delete_item.setFont(font)
                delete_item.setData(Qt.UserRole, person['id'])
                delete_item.setToolTip("Supprimer ce membre")
                self.table.setItem(row, 9, delete_item)
            else:
                empty_item = QTableWidgetItem("—")
                empty_item.setTextAlignment(Qt.AlignCenter)
                empty_item.setFlags(Qt.ItemIsEnabled)
                empty_item.setForeground(QBrush(QColor("#cbd5e1")))
                self.table.setItem(row, 9, empty_item)

            row += 1

    def get_relation_text(self, person_id, martyr_id):
        """Trouve le type de relation entre une personne et le martyr"""
        if person_id == martyr_id:
            return "👤 Martyr (centré)"

        relations = self.db.get_relationships(martyr_id)
        for rel in relations:
            if rel['person1_id'] == person_id or rel['person2_id'] == person_id:
                rel_type = rel['relation_type']
                return {
                    'parent': '👤 Parent',
                    'child': '👶 Enfant',
                    'spouse': '💍 Conjoint(e)',
                    'sibling': '👫 Frère/Sœur'
                }.get(rel_type, rel_type)

        return "👨‍👩‍👧‍👦 Membre de famille"

    def refresh_tree(self):
        self.refresh_combo()
        if self.current_person_id:
            self.load_tree(self.current_person_id)