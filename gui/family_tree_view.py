from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QGraphicsView, 
    QGraphicsScene, QGraphicsEllipseItem, QGraphicsTextItem,
    QGraphicsLineItem, QPushButton, QHBoxLayout, QComboBox,
    QTableWidget, QTableWidgetItem, QHeaderView, QStackedWidget
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPen, QBrush, QColor, QFont


class FamilyTreeView(QWidget):
    def __init__(self, db_manager):
        super().__init__()
        self.db = db_manager
        self.current_person_id = None
        
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Titre
        title = QLabel("🌳 Arbre généalogique / Tableau familial")
        title_font = title.font()
        title_font.setPointSize(12)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # Contrôles
        controls = QHBoxLayout()
        
        controls.addWidget(QLabel("Centrer sur:"))
        
        self.combo_persons = QComboBox()
        self.combo_persons.currentIndexChanged.connect(self.on_combo_changed)
        controls.addWidget(self.combo_persons)
        
        # Bouton toggle Arbre / Tableau
        self.btn_toggle = QPushButton("📊 Voir Tableau")
        self.btn_toggle.setStyleSheet("""
            QPushButton {
                background-color: #1976d2;
                color: white;
                padding: 8px 15px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1565c0;
            }
        """)
        self.btn_toggle.clicked.connect(self.toggle_view)
        controls.addWidget(self.btn_toggle)
        
        self.btn_refresh = QPushButton("🔄 Actualiser")
        self.btn_refresh.clicked.connect(self.refresh_tree)
        controls.addWidget(self.btn_refresh)
        
        controls.addStretch()
        layout.addLayout(controls)
        
        # Stack pour switcher entre Arbre et Tableau
        self.stack = QStackedWidget()
        
        # ===== VUE ARBRE =====
        self.tree_widget = QWidget()
        tree_layout = QVBoxLayout(self.tree_widget)
        
        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        self.view.setRenderHints(self.view.renderHints())
        self.view.setStyleSheet("background-color: #f5f5f5; border: 1px solid #ddd;")
        tree_layout.addWidget(self.view)
        
        # ===== VUE TABLEAU =====
        self.table_widget = QWidget()
        table_layout = QVBoxLayout(self.table_widget)
        
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Nom", "CIN", "Relation", "Genre", "Date naissance", "Statut"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
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
    
    def load_tree(self, person_id):
        self.current_person_id = person_id
        self.scene.clear()
        
        person = self.db.get_person(person_id)
        if not person:
            return
        
        # Dessiner la personne centrale
        self.draw_person_node(person, 400, 300, is_main=True)
        
        # Dessiner les relations
        self.draw_relations(person_id, 400, 300)
        
        self.view.setSceneRect(0, 0, 800, 600)
        self.view.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)
    
    def load_table(self):
        """Charge le tableau avec toute la famille du martyr"""
        if not self.current_person_id:
            return
        
        self.table.setRowCount(0)
        
        # Récupérer le martyr central
        martyr = self.db.get_person(self.current_person_id)
        if not martyr:
            return
        
        # Récupérer toute la famille (martyr + relations + membres de famille)
        family_members = self.db.get_family_members(self.current_person_id)
        
        # Ajouter aussi les relations du martyr
        relations = self.db.get_relationships(self.current_person_id)
        related_ids = set()
        for rel in relations:
            related_ids.add(rel['person1_id'])
            related_ids.add(rel['person2_id'])
        
        # Combiner tout le monde
        all_persons = {p['id']: p for p in family_members}
        for pid in related_ids:
            if pid not in all_persons:
                person = self.db.get_person(pid)
                if person:
                    all_persons[pid] = person
        
        # Remplir le tableau
        row = 0
        for person in all_persons.values():
            self.table.insertRow(row)
            
            # Nom
            name_item = QTableWidgetItem(f"{person['first_name']} {person['last_name']}")
            if person.get('is_martyr'):
                name_item.setText("☪️ " + name_item.text())
            elif person.get('is_martyr_family'):
                name_item.setText("👨‍👩‍👧‍👦 " + name_item.text())
            self.table.setItem(row, 0, name_item)
            
            # CIN
            self.table.setItem(row, 1, QTableWidgetItem(person.get('cin') or "-"))
            
            # Relation
            relation_text = self.get_relation_text(person['id'], martyr['id'])
            self.table.setItem(row, 2, QTableWidgetItem(relation_text))
            
            # Genre
            gender_map = {"M": "Homme", "F": "Femme", "O": "Autre", None: "-"}
            self.table.setItem(row, 3, QTableWidgetItem(gender_map.get(person.get('gender'), "-")))
            
            # Date naissance
            birth = person.get('birth_date') or "-"
            self.table.setItem(row, 4, QTableWidgetItem(birth))
            
            # Statut
            if person.get('is_martyr'):
                status = "☪️ Martyr"
            elif person.get('is_martyr_family'):
                status = "👨‍👩‍👧‍👦 Famille"
            else:
                status = "-"
            self.table.setItem(row, 5, QTableWidgetItem(status))
            
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
    
    def draw_person_node(self, person, x, y, is_main=False):
        radius = 40
        ellipse = QGraphicsEllipseItem(x - radius, y - radius, radius * 2, radius * 2)
        
        if is_main:
            ellipse.setBrush(QBrush(QColor("#1976d2")))
            ellipse.setPen(QPen(QColor("#0d47a1"), 3))
        else:
            color = QColor("#e3f2fd") if person.get('gender') == 'F' else QColor("#fff3e0")
            ellipse.setBrush(QBrush(color))
            ellipse.setPen(QPen(QColor("#666"), 2))
        
        self.scene.addItem(ellipse)
        
        name_text = f"{person['first_name']}\n{person['last_name']}"
        text = QGraphicsTextItem(name_text)
        text.setDefaultTextColor(Qt.white if is_main else Qt.black)
        
        font = QFont()
        font.setPointSize(8)
        font.setBold(True)
        text.setFont(font)
        
        text_rect = text.boundingRect()
        text.setPos(x - text_rect.width() / 2, y - text_rect.height() / 2)
        self.scene.addItem(text)
        
        return (x, y)
    
    def draw_relations(self, person_id, center_x, center_y):
        relations = self.db.get_relationships(person_id)
        
        relations_by_type = {
            'parent': [],
            'child': [],
            'spouse': [],
            'sibling': []
        }
        
        for rel in relations:
            if rel['person1_id'] == person_id:
                other_id = rel['person2_id']
            else:
                other_id = rel['person1_id']
            
            other = self.db.get_person(other_id)
            if not other:
                continue
            
            relations_by_type[rel['relation_type']].append({
                'person': other,
                'relation_type': rel['relation_type']
            })
        
        vertical_spacing = 150
        horizontal_spacing = 180
        
        # Parents (en haut)
        parents = relations_by_type['parent']
        if parents:
            start_x = center_x - ((len(parents) - 1) * horizontal_spacing) / 2
            for i, parent in enumerate(parents):
                x = start_x + i * horizontal_spacing
                y = center_y - vertical_spacing
                self.draw_connection(center_x, center_y, x, y, "PARENT")
                self.draw_person_node(parent['person'], x, y)
        
        # Conjoints (à droite)
        spouses = relations_by_type['spouse']
        if spouses:
            start_y = center_y - ((len(spouses) - 1) * horizontal_spacing) / 2
            for i, spouse in enumerate(spouses):
                x = center_x + vertical_spacing
                y = start_y + i * horizontal_spacing
                self.draw_connection(center_x, center_y, x, y, "CONJOINT")
                self.draw_person_node(spouse['person'], x, y)
        
        # Enfants (en bas)
        children = relations_by_type['child']
        if children:
            start_x = center_x - ((len(children) - 1) * horizontal_spacing) / 2
            for i, child in enumerate(children):
                x = start_x + i * horizontal_spacing
                y = center_y + vertical_spacing
                self.draw_connection(center_x, center_y, x, y, "ENFANT")
                self.draw_person_node(child['person'], x, y)
        
        # Frères/Sœurs (à gauche)
        siblings = relations_by_type['sibling']
        if siblings:
            start_y = center_y - ((len(siblings) - 1) * horizontal_spacing) / 2
            for i, sibling in enumerate(siblings):
                x = center_x - vertical_spacing
                y = start_y + i * horizontal_spacing
                self.draw_connection(center_x, center_y, x, y, "FRÈRE/SŒUR")
                self.draw_person_node(sibling['person'], x, y)
    
    def draw_connection(self, x1, y1, x2, y2, label_text):
        line = QGraphicsLineItem(x1, y1, x2, y2)
        line.setPen(QPen(QColor("#999"), 2, Qt.DashLine))
        self.scene.addItem(line)
        
        label = QGraphicsTextItem(label_text)
        label.setDefaultTextColor(QColor("#666"))
        mid_x = (x1 + x2) / 2
        mid_y = (y1 + y2) / 2
        label.setPos(mid_x, mid_y)
        self.scene.addItem(label)
    
    def refresh_tree(self):
        self.refresh_combo()
        if self.current_person_id:
            self.load_tree(self.current_person_id)