from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTableWidget, QSplitter,
    QMessageBox, QFrame, QLineEdit, QComboBox,
    QStackedWidget, QDialog, QTableWidgetItem, QHeaderView,
    QAbstractItemView
)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QFont, QIcon, QPixmap, QPainter, QBrush, QColor

import os

from database.db_manager import DatabaseManager
from gui.person_form import PersonForm
from gui.family_tree_view import FamilyTreeView
from gui.stats_view import StatsView
from gui.pension_view import PensionView  # NOUVEAU


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = DatabaseManager()
        self.current_person_id = None
        
        self.setWindowTitle("Family Manager")
        self.setMinimumSize(1400, 900)
        
        self.setup_ui()
        self.load_persons_list()
    
    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # ===== PANNEAU GAUCHE : Sidebar =====
        left_panel = QFrame()
        left_panel.setObjectName("sidebar")
        left_panel.setMinimumWidth(320)
        left_panel.setMaximumWidth(380)
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(20, 20, 20, 20)
        left_layout.setSpacing(16)
        
        # Logo / Titre
        header_layout = QHBoxLayout()
        logo = QLabel("🌳")
        logo_font = QFont()
        logo_font.setPointSize(24)
        logo.setFont(logo_font)
        header_layout.addWidget(logo)
        
        title = QLabel("Family Manager")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        header_layout.addWidget(title)
        header_layout.addStretch()
        left_layout.addLayout(header_layout)
        
        subtitle = QLabel("Gestion des familles de martyrs")
        subtitle.setObjectName("subtitle")
        left_layout.addWidget(subtitle)
        
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setStyleSheet("color: #e2e8f0; max-height: 1px;")
        left_layout.addWidget(separator)
        
        # ===== ZONE DE RECHERCHE =====
        search_container = QFrame()
        search_container.setObjectName("card")
        search_layout = QVBoxLayout(search_container)
        search_layout.setContentsMargins(16, 16, 16, 16)
        search_layout.setSpacing(12)
        
        search_bar_layout = QHBoxLayout()
        search_icon = QLabel("🔍")
        search_bar_layout.addWidget(search_icon)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Rechercher par nom, prénom ou CIN...")
        self.search_input.textChanged.connect(self.on_search_changed)
        search_bar_layout.addWidget(self.search_input)
        search_layout.addLayout(search_bar_layout)
        
        filters_layout = QHBoxLayout()
        filters_layout.setSpacing(8)
        
        self.filter_type = QComboBox()
        self.filter_type.addItems(["☪️ Martyrs", "👨‍👩‍👧‍👦 Familles", "👥 Tous"])
        self.filter_type.currentIndexChanged.connect(self.on_filter_changed)
        filters_layout.addWidget(self.filter_type)
        
        self.filter_gender = QComboBox()
        self.filter_gender.addItems(["Tous", "Homme", "Femme"])
        self.filter_gender.currentIndexChanged.connect(self.on_filter_changed)
        filters_layout.addWidget(self.filter_gender)
        
        self.btn_reset = QPushButton("↺")
        self.btn_reset.setObjectName("ghost")
        self.btn_reset.setToolTip("Réinitialiser les filtres")
        self.btn_reset.setFixedSize(32, 32)
        self.btn_reset.clicked.connect(self.reset_filters)
        filters_layout.addWidget(self.btn_reset)
        
        search_layout.addLayout(filters_layout)
        left_layout.addWidget(search_container)
        
        # Bouton ajouter
        self.btn_add = QPushButton("+ Ajouter un martyr")
        self.btn_add.setObjectName("primary")
        self.btn_add.setMinimumHeight(44)
        self.btn_add.clicked.connect(self.show_add_form)
        left_layout.addWidget(self.btn_add)
        
        # Label liste
        list_header = QLabel("Membres")
        list_header.setObjectName("statLabel")
        left_layout.addWidget(list_header)
        
        # Tableau des personnes
        self.list_persons = QTableWidget()
        self.list_persons.setColumnCount(3)
        self.list_persons.setHorizontalHeaderLabels(["", "Nom", ""])
        self.list_persons.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)
        self.list_persons.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.list_persons.horizontalHeader().setSectionResizeMode(2, QHeaderView.Fixed)
        self.list_persons.setColumnWidth(0, 44)
        self.list_persons.setColumnWidth(2, 36)
        self.list_persons.horizontalHeader().hide()
        self.list_persons.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.list_persons.setSelectionMode(QAbstractItemView.SingleSelection)
        self.list_persons.setIconSize(QSize(32, 32))
        self.list_persons.cellClicked.connect(self.on_person_selected_table)
        left_layout.addWidget(self.list_persons)
        
        # Bouton paramètres en bas
        self.btn_settings = QPushButton("⚙️ Paramètres")
        self.btn_settings.setObjectName("ghost")
        self.btn_settings.setMinimumHeight(40)
        self.btn_settings.clicked.connect(self.open_settings)
        left_layout.addWidget(self.btn_settings)
        
        # ===== PANNEAU DROIT : Contenu =====
        right_panel = QFrame()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(24, 20, 24, 20)
        right_layout.setSpacing(20)
        
        # Header avec onglets — 4 onglets maintenant
        header_container = QFrame()
        header_container.setObjectName("card")
        header_layout = QHBoxLayout(header_container)
        header_layout.setContentsMargins(4, 4, 4, 0)
        header_layout.setSpacing(0)
        
        self.btn_details = QPushButton("📝 Détails")
        self.btn_tree = QPushButton("🌳 Arbre")
        self.btn_stats = QPushButton("📊 Stats")
        self.btn_pensions = QPushButton("💰 Pensions")  # NOUVEAU ONGLET
        
        self.tab_buttons = [self.btn_details, self.btn_tree, self.btn_stats, self.btn_pensions]
        for btn in self.tab_buttons:
            btn.setObjectName("tab")
            btn.setCheckable(True)
            btn.setCursor(Qt.PointingHandCursor)
            header_layout.addWidget(btn)
        
        header_layout.addStretch()
        
        self.btn_details.setChecked(True)
        self.btn_details.clicked.connect(lambda: self.switch_tab("details"))
        self.btn_tree.clicked.connect(lambda: self.switch_tab("tree"))
        self.btn_stats.clicked.connect(lambda: self.switch_tab("stats"))
        self.btn_pensions.clicked.connect(lambda: self.switch_tab("pensions"))
        
        right_layout.addWidget(header_container)
        
        # ===== QStackedWidget — 4 vues =====
        self.stack = QStackedWidget()
        
        # 1. Formulaire de détails
        self.person_form = PersonForm(self.db)
        self.person_form.person_saved.connect(self.on_person_saved)
        self.person_form.add_relation_requested.connect(self.on_family_member_added)
        self.stack.addWidget(self.person_form)
        
        # 2. Vue de l'arbre
        self.tree_view = FamilyTreeView(self.db)
        self.stack.addWidget(self.tree_view)
        
        # 3. Vue des statistiques — SANS pensions
        self.stats_view = StatsView(self.db)
        self.stack.addWidget(self.stats_view)
        
        # 4. Vue des pensions — NOUVEAU
        self.pension_view = PensionView(self.db)
        self.stack.addWidget(self.pension_view)
        
        right_layout.addWidget(self.stack)
        
        # ===== ASSEMBLAGE AVEC SPLITTER =====
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([340, 1060])
        splitter.setHandleWidth(1)
        
        main_layout.addWidget(splitter)
    
    def switch_tab(self, tab_name):
        for btn in self.tab_buttons:
            btn.setChecked(False)
        
        if tab_name == "details":
            self.btn_details.setChecked(True)
            self.stack.setCurrentIndex(0)
        elif tab_name == "tree":
            self.btn_tree.setChecked(True)
            self.stack.setCurrentIndex(1)
            if self.current_person_id:
                self.tree_view.current_person_id = self.current_person_id
                self.tree_view.load_tree(self.current_person_id)
        elif tab_name == "stats":
            self.btn_stats.setChecked(True)
            self.stack.setCurrentIndex(2)
            self.stats_view.load_stats()
        else:  # pensions
            self.btn_pensions.setChecked(True)
            self.stack.setCurrentIndex(3)
            self.pension_view.load_pensions()
    
    def load_persons_list(self):
        self.apply_filters()
    
    def on_person_selected_table(self, row, column):
        if column == 2:
            person_id = self.list_persons.item(row, 1).data(Qt.UserRole)
            self.delete_person(person_id)
            return
        
        person_id = self.list_persons.item(row, 1).data(Qt.UserRole)
        self.select_person(person_id)
    
    def select_person(self, person_id):
        self.current_person_id = person_id
        self.tree_view.current_person_id = person_id
        
        person = self.db.get_person(person_id)
        if person:
            self.person_form.load_person(person)
            if self.btn_tree.isChecked():
                self.tree_view.load_tree(person_id)
    
    def show_add_form(self):
        self.current_person_id = None
        self.person_form.clear_form()
        self.switch_tab("details")
        self.list_persons.clearSelection()
    
    def on_person_saved(self, person_id):
        self.load_persons_list()
        self.current_person_id = person_id
    
    def delete_person(self, person_id=None):
        if person_id is None:
            person_id = self.current_person_id
        
        if not person_id:
            return
        
        reply = QMessageBox.question(
            self, "Confirmer la suppression",
            "Êtes-vous sûr de vouloir supprimer cette personne ?\n"
            "Toutes ses relations seront également supprimées.",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.db.delete_person(person_id)
            if person_id == self.current_person_id:
                self.current_person_id = None
                self.person_form.clear_form()
            self.load_persons_list()
            QMessageBox.information(self, "Succès", "Personne supprimée !")

    def on_family_member_added(self):
        if self.btn_tree.isChecked():
            self.tree_view.load_tree(self.current_person_id)
        QMessageBox.information(self, "Succès", "Membre de la famille ajouté !")

    def on_search_changed(self, text):
        self.apply_filters()
    
    def on_filter_changed(self):
        self.apply_filters()
    
    def create_default_avatar(self, gender):
        size = 32
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
        painter.drawEllipse(1, 1, size-2, size-2)
        
        painter.setPen(QColor("white"))
        font = painter.font()
        font.setPointSize(10)
        font.setBold(True)
        painter.setFont(font)
        
        initial = "?" if gender not in ["M", "F"] else ("H" if gender == "M" else "F")
        painter.drawText(pixmap.rect(), Qt.AlignCenter, initial)
        
        painter.end()
        return QIcon(pixmap)
    
    def apply_filters(self):
        search_text = self.search_input.text().strip().lower()
        type_filter = self.filter_type.currentIndex()
        
        gender_map = {0: None, 1: "M", 2: "F"}
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
        
        self.list_persons.setRowCount(0)
        for row, person in enumerate(persons):
            self.list_persons.insertRow(row)
            self.list_persons.setRowHeight(row, 52)
            
            full_name = f"{person['first_name']} {person['last_name']}"
            
            if person.get('is_martyr'):
                full_name += "  ☪️"
            elif person.get('is_martyr_family'):
                full_name += "  👨‍👩‍👧‍👦"
            
            photo_item = QTableWidgetItem()
            photo_path = person.get('photo_path')
            if photo_path and os.path.exists(photo_path):
                pixmap = QPixmap(photo_path)
                if not pixmap.isNull():
                    icon = QIcon(pixmap.scaled(32, 32, Qt.KeepAspectRatio, Qt.SmoothTransformation))
                    photo_item.setIcon(icon)
                else:
                    photo_item.setIcon(self.create_default_avatar(person.get('gender')))
            else:
                photo_item.setIcon(self.create_default_avatar(person.get('gender')))
            photo_item.setTextAlignment(Qt.AlignCenter)
            photo_item.setFlags(photo_item.flags() & ~Qt.ItemIsEditable)
            self.list_persons.setItem(row, 0, photo_item)
            
            name_item = QTableWidgetItem(full_name)
            name_item.setData(Qt.UserRole, person['id'])
            self.list_persons.setItem(row, 1, name_item)
            
            delete_item = QTableWidgetItem("✕")
            delete_item.setTextAlignment(Qt.AlignCenter)
            delete_item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            delete_item.setForeground(QBrush(QColor("#ef4444")))
            font = delete_item.font()
            font.setPointSize(12)
            font.setBold(True)
            delete_item.setFont(font)
            self.list_persons.setItem(row, 2, delete_item)
    
    def reset_filters(self):
        self.search_input.clear()
        self.filter_type.setCurrentIndex(0)
        self.filter_gender.setCurrentIndex(0)
        self.load_persons_list()

    def open_settings(self):
        from gui.settings_dialog import SettingsDialog
        dialog = SettingsDialog(self.db, self)
        if dialog.exec() == QDialog.Accepted:
            QMessageBox.information(self, "Succès", "Paramètres mis à jour !")