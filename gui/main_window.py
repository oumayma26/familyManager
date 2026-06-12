from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QListWidget, QSplitter,
    QMessageBox, QFrame, QLineEdit, QComboBox,
    QStackedWidget, QDialog
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

from database.db_manager import DatabaseManager
from gui.person_form import PersonForm
from gui.family_tree_view import FamilyTreeView
from gui.stats_view import StatsView


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = DatabaseManager()
        self.current_person_id = None
        
        self.setWindowTitle("🌳 Family Manager")
        self.setMinimumSize(1200, 800)
        
        self.setup_ui()
        self.load_persons_list()
    
    def setup_ui(self):
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal horizontal
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # ===== PANNEAU GAUCHE : Liste des personnes =====
        left_panel = QFrame()
        left_panel.setFrameStyle(QFrame.StyledPanel)
        left_layout = QVBoxLayout(left_panel)
        
        # Titre
        title = QLabel("👥 Membres de la famille")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        left_layout.addWidget(title)
        
        # ===== ZONE DE RECHERCHE =====
        search_group = QFrame()
        search_group.setStyleSheet("background-color: #f5f5f5; border-radius: 8px; padding: 5px;")
        search_layout = QVBoxLayout(search_group)
        search_layout.setSpacing(8)
        
        # Barre de recherche
        search_bar_layout = QHBoxLayout()
        search_icon = QLabel("🔍")
        search_bar_layout.addWidget(search_icon)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Rechercher par nom, prénom ou CIN...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 5px;
                background-color: white;
            }
            QLineEdit:focus {
                border: 1px solid #2196F3;
            }
        """)
        self.search_input.textChanged.connect(self.on_search_changed)
        search_bar_layout.addWidget(self.search_input)
        
        search_layout.addLayout(search_bar_layout)
        
        # Filtres
        filters_layout = QHBoxLayout()
        
        # Filtre Type
        self.filter_type = QComboBox()
        self.filter_type.addItems(["☪️ Martyrs", "👨‍👩‍👧‍👦 Familles", "👥 Tous"])
        self.filter_type.setStyleSheet("""
            QComboBox {
                padding: 5px;
                border: 1px solid #ddd;
                border-radius: 3px;
                background-color: white;
            }
        """)
        self.filter_type.currentIndexChanged.connect(self.on_filter_changed)
        filters_layout.addWidget(QLabel("Type:"))
        filters_layout.addWidget(self.filter_type)
        
        # Filtre Genre
        self.filter_gender = QComboBox()
        self.filter_gender.addItems(["Tous", "Homme", "Femme"])
        self.filter_gender.setStyleSheet("""
            QComboBox {
                padding: 5px;
                border: 1px solid #ddd;
                border-radius: 3px;
                background-color: white;
            }
        """)
        self.filter_gender.currentIndexChanged.connect(self.on_filter_changed)
        filters_layout.addWidget(QLabel("Genre:"))
        filters_layout.addWidget(self.filter_gender)
        
        # Bouton réinitialiser
        self.btn_reset = QPushButton("🔄")
        self.btn_reset.setToolTip("Réinitialiser les filtres")
        self.btn_reset.setStyleSheet("""
            QPushButton {
                background-color: #757575;
                color: white;
                padding: 5px 10px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #616161;
            }
        """)
        self.btn_reset.clicked.connect(self.reset_filters)
        filters_layout.addWidget(self.btn_reset)
        
        filters_layout.addStretch()
        search_layout.addLayout(filters_layout)
        
        left_layout.addWidget(search_group)
        
        # Bouton ajouter
        self.btn_add = QPushButton("➕ Ajouter un martyr")
        self.btn_add.setStyleSheet("""
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
        self.btn_add.clicked.connect(self.show_add_form)
        left_layout.addWidget(self.btn_add)
        
        # Liste des personnes
        self.list_persons = QListWidget()
        self.list_persons.setStyleSheet("""
            QListWidget {
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 5px;
            }
            QListWidget::item {
                padding: 10px;
                border-bottom: 1px solid #eee;
            }
            QListWidget::item:selected {
                background-color: #e3f2fd;
                color: #1976d2;
            }
        """)
        self.list_persons.itemClicked.connect(self.on_person_selected)
        left_layout.addWidget(self.list_persons)
        
        # Bouton supprimer
        self.btn_delete = QPushButton("🗑️ Supprimer")
        self.btn_delete.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                padding: 8px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
        """)
        self.btn_delete.clicked.connect(self.delete_person)
        self.btn_delete.setEnabled(False)
        left_layout.addWidget(self.btn_delete)

        # Bouton paramètres
        self.btn_settings = QPushButton("⚙️ Paramètres")
        self.btn_settings.setStyleSheet("""
            QPushButton {
                background-color: #607d8b;
                color: white;
                padding: 8px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #546e7a;
            }
        """)
        self.btn_settings.clicked.connect(self.open_settings)
        left_layout.addWidget(self.btn_settings)
        
        # ===== PANNEAU CENTRAL : Details et Arbre =====
        right_panel = QFrame()
        right_layout = QVBoxLayout(right_panel)
        
        # Onglets via boutons
        tabs_layout = QHBoxLayout()
        self.btn_details = QPushButton("📝 Details")
        self.btn_tree = QPushButton("🌳 Arbre genealogique")
        self.btn_stats = QPushButton("📊 Stats")
        
        for btn in [self.btn_details, self.btn_tree, self.btn_stats]:
            btn.setCheckable(True)
            btn.setStyleSheet("""
                QPushButton {
                    padding: 10px 20px;
                    border: none;
                    background-color: #f5f5f5;
                    font-weight: bold;
                }
                QPushButton:checked {
                    background-color: #1976d2;
                    color: white;
                }
            """)
            tabs_layout.addWidget(btn)
        
        self.btn_details.setChecked(True)
        self.btn_details.clicked.connect(lambda: self.switch_tab("details"))
        self.btn_tree.clicked.connect(lambda: self.switch_tab("tree"))
        self.btn_stats.clicked.connect(lambda: self.switch_tab("stats"))
        
        right_layout.addLayout(tabs_layout)
        
        # ===== QStackedWidget pour switcher proprement =====
        self.stack = QStackedWidget()
        
        # 1. Formulaire de details
        self.person_form = PersonForm(self.db)
        self.person_form.person_saved.connect(self.on_person_saved)
        self.person_form.add_relation_requested.connect(self.on_family_member_added)
        self.stack.addWidget(self.person_form)
        
        # 2. Vue de l'arbre
        self.tree_view = FamilyTreeView(self.db)
        self.stack.addWidget(self.tree_view)
        
        # 3. Vue des statistiques
        self.stats_view = StatsView(self.db)
        self.stack.addWidget(self.stats_view)
        
        right_layout.addWidget(self.stack)
        
        # ===== ASSEMBLAGE =====
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([350, 850])
        
        main_layout.addWidget(splitter)
    
    def switch_tab(self, tab_name):
        self.btn_details.setChecked(tab_name == "details")
        self.btn_tree.setChecked(tab_name == "tree")
        self.btn_stats.setChecked(tab_name == "stats")
        
        if tab_name == "details":
            self.stack.setCurrentIndex(0)
        elif tab_name == "tree":
            self.stack.setCurrentIndex(1)
            if self.current_person_id:
                self.tree_view.current_person_id = self.current_person_id
                self.tree_view.load_tree(self.current_person_id)
        else:  # stats
            self.stack.setCurrentIndex(2)
            self.stats_view.load_stats()
    
    def load_persons_list(self):
        """Charge la liste avec les filtres par defaut (Martyrs)"""
        self.apply_filters()
    
    def on_person_selected(self, item):
        person_id = item.data(Qt.UserRole)
        self.current_person_id = person_id
        self.btn_delete.setEnabled(True)
        
        self.tree_view.current_person_id = person_id
        
        person = self.db.get_person(person_id)
        if person:
            self.person_form.load_person(person)
            if self.btn_tree.isChecked():
                self.tree_view.load_tree(person_id)
    
    def show_add_form(self):
        self.current_person_id = None
        self.btn_delete.setEnabled(False)
        self.person_form.clear_form()
        self.switch_tab("details")
        self.list_persons.clearSelection()
    
    def on_person_saved(self, person_id):
        self.load_persons_list()
        self.current_person_id = person_id
        self.btn_delete.setEnabled(True)
    
    def delete_person(self):
        if not self.current_person_id:
            return
        
        reply = QMessageBox.question(
            self, "Confirmer la suppression",
            "Es-tu sur de vouloir supprimer cette personne ?\n"
            "Toutes ses relations seront egalement supprimees.",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.db.delete_person(self.current_person_id)
            self.current_person_id = None
            self.btn_delete.setEnabled(False)
            self.person_form.clear_form()
            self.load_persons_list()
            QMessageBox.information(self, "Succes", "Personne supprimee !")

    def on_family_member_added(self):
        if self.btn_tree.isChecked():
            self.tree_view.load_tree(self.current_person_id)
        QMessageBox.information(self, "Succes", "Membre de la famille ajoute !")

    def on_search_changed(self, text):
        """Filtre la liste en temps reel selon la recherche"""
        self.apply_filters()
    
    def on_filter_changed(self):
        """Filtre la liste quand les filtres changent"""
        self.apply_filters()
    
    def apply_filters(self):
        """Applique tous les filtres (recherche + type + genre)"""
        search_text = self.search_input.text().strip().lower()
        
        type_filter = self.filter_type.currentIndex()
        
        gender_map = {0: None, 1: "M", 2: "F", 3: "O"}
        gender_filter = gender_map[self.filter_gender.currentIndex()]
        
        if type_filter == 0:
            persons = self.db.get_martyrs()
        elif type_filter == 1:
            persons = self.db.get_martyr_families()
        else:
            persons = self.db.get_all_persons()
        
        if search_text:
            persons = [p for p in persons if 
                      search_text in (p['first_name'] or '').lower() or
                      search_text in (p['last_name'] or '').lower() or
                      search_text in (p['cin'] or '').lower()]
        
        if gender_filter:
            persons = [p for p in persons if p.get('gender') == gender_filter]
        
        self.list_persons.clear()
        for person in persons:
            full_name = f"{person['first_name']} {person['last_name']}"
            
            if person.get('is_martyr'):
                full_name += " ☪️"
            elif person.get('is_martyr_family'):
                full_name += " 👨‍👩‍👧‍👦"
            elif person.get('cin'):
                full_name += f" [CIN: {person['cin']}]"
            elif person.get('birth_date'):
                full_name += f" ({person['birth_date'][:4]})"
            
            self.list_persons.addItem(full_name)
            self.list_persons.item(self.list_persons.count() - 1).setData(
                Qt.UserRole, person['id']
            )
    
    def reset_filters(self):
        """Reinitialise tous les filtres"""
        self.search_input.clear()
        self.filter_type.setCurrentIndex(0)
        self.filter_gender.setCurrentIndex(0)
        self.load_persons_list()

    def open_settings(self):
        from gui.settings_dialog import SettingsDialog
        dialog = SettingsDialog(self.db, self)
        if dialog.exec() == QDialog.Accepted:
            QMessageBox.information(self, "Succès", "Paramètres mis à jour !")