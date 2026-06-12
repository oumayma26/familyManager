from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QFrame, QGridLayout, QProgressBar, QPushButton
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont


class StatsView(QWidget):
    def __init__(self, db_manager):
        super().__init__()
        self.db = db_manager
        self.setup_ui()
        self.load_stats()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        
        # Titre
        title = QLabel("📊 Tableau de bord")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Grille des statistiques
        grid = QGridLayout()
        grid.setSpacing(15)
        
        # Carte 1 : Martyrs
        self.card_martyrs = self.create_stat_card(
            "☪️ Martyrs", 
            "0", 
            "#d32f2f", 
            "#ffebee"
        )
        grid.addWidget(self.card_martyrs, 0, 0)
        
        # Carte 2 : Familles
        self.card_families = self.create_stat_card(
            "👨‍👩‍👧‍👦 Familles", 
            "0", 
            "#1976d2", 
            "#e3f2fd"
        )
        grid.addWidget(self.card_families, 0, 1)
        
        # Carte 3 : Total
        self.card_total = self.create_stat_card(
            "👥 Total personnes", 
            "0", 
            "#388e3c", 
            "#e8f5e9"
        )
        grid.addWidget(self.card_total, 0, 2)
        
        # Carte 4 : Martyrs sans famille
        self.card_orphans = self.create_stat_card(
            "⚠️ Martyrs sans famille", 
            "0", 
            "#f57c00", 
            "#fff3e0"
        )
        grid.addWidget(self.card_orphans, 1, 0)
        
        # Carte 5 : Sans CIN
        self.card_no_cin = self.create_stat_card(
            "📝 Sans CIN", 
            "0", 
            "#7b1fa2", 
            "#f3e5f5"
        )
        grid.addWidget(self.card_no_cin, 1, 1)
        
        # Carte 6 : Répartition genre
        self.card_gender = self.create_gender_card()
        grid.addWidget(self.card_gender, 1, 2)
        
        layout.addLayout(grid)
        
        # Bouton actualiser
        self.btn_refresh = QPushButton("🔄 Actualiser")
        self.btn_refresh.setStyleSheet("""
            QPushButton {
                background-color: #1976d2;
                color: white;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1565c0;
            }
        """)
        self.btn_refresh.clicked.connect(self.load_stats)
        layout.addWidget(self.btn_refresh, alignment=Qt.AlignCenter)
        
        layout.addStretch()
    
    def create_stat_card(self, title, value, color, bg_color):
        """Crée une carte de statistique"""
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {bg_color};
                border-radius: 10px;
                padding: 15px;
                border: 1px solid {color};
            }}
        """)
        
        layout = QVBoxLayout(card)
        
        label_title = QLabel(title)
        label_title.setStyleSheet(f"color: {color}; font-size: 12px; font-weight: bold;")
        layout.addWidget(label_title)
        
        label_value = QLabel(value)
        label_value.setStyleSheet(f"color: {color}; font-size: 32px; font-weight: bold;")
        label_value.setAlignment(Qt.AlignCenter)
        layout.addWidget(label_value)
        
        # Stocker la référence pour mise à jour
        card.value_label = label_value
        
        return card
    
    def create_gender_card(self):
        """Crée une carte spéciale pour la répartition genre"""
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: #fafafa;
                border-radius: 10px;
                padding: 15px;
                border: 1px solid #666;
            }
        """)
        
        layout = QVBoxLayout(card)
        
        title = QLabel("⚥ Répartition par genre")
        title.setStyleSheet("color: #666; font-size: 12px; font-weight: bold;")
        layout.addWidget(title)
        
        # Homme
        self.bar_male = QProgressBar()
        self.bar_male.setStyleSheet("""
            QProgressBar {
                border: 1px solid #ddd;
                border-radius: 5px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #2196F3;
            }
        """)
        self.bar_male.setFormat("Homme: %v%")
        layout.addWidget(self.bar_male)
        
        # Femme
        self.bar_female = QProgressBar()
        self.bar_female.setStyleSheet("""
            QProgressBar {
                border: 1px solid #ddd;
                border-radius: 5px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #E91E63;
            }
        """)
        self.bar_female.setFormat("Femme: %v%")
        layout.addWidget(self.bar_female)
        
      
        return card
    
    def load_stats(self):
        """Charge et affiche les statistiques"""
        stats = self.db.get_stats()
        
        # Mettre à jour les cartes
        self.card_martyrs.value_label.setText(str(stats['total_martyrs']))
        self.card_families.value_label.setText(str(stats['total_families']))
        self.card_total.value_label.setText(str(stats['total_persons']))
        self.card_orphans.value_label.setText(str(stats['martyrs_without_family']))
        self.card_no_cin.value_label.setText(str(stats['without_cin']))
        
        # Mettre à jour les barres de genre
        total = stats['total_persons']
        if total > 0:
            gender = stats['gender_distribution']
            male = gender.get('M', 0)
            female = gender.get('F', 0)
            
            self.bar_male.setValue(int(male / total * 100))
            self.bar_female.setValue(int(female / total * 100))
        else:
            self.bar_male.setValue(0)
            self.bar_female.setValue(0)