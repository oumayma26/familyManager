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
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(24)
        
        # Header
        header = QLabel("📊 Statistiques")
        header.setObjectName("title")
        layout.addWidget(header)
        
        # ===== GRILLE DES STATISTIQUES =====
        grid = QGridLayout()
        grid.setSpacing(16)
        
        self.card_martyrs = self.create_stat_card("☪️ Martyrs", "0", "#dc2626")
        grid.addWidget(self.card_martyrs, 0, 0)
        
        self.card_families = self.create_stat_card("👨‍👩‍👧‍👦 Familles", "0", "#2563eb")
        grid.addWidget(self.card_families, 0, 1)
        
        self.card_total = self.create_stat_card("👥 Total personnes", "0", "#16a34a")
        grid.addWidget(self.card_total, 0, 2)
        
        self.card_orphans = self.create_stat_card("⚠️ Martyrs sans famille", "0", "#ea580c")
        grid.addWidget(self.card_orphans, 1, 0)
        
        self.card_no_cin = self.create_stat_card("📝 Sans CIN", "0", "#7c3aed")
        grid.addWidget(self.card_no_cin, 1, 1)
        
        self.card_gender = self.create_gender_card()
        grid.addWidget(self.card_gender, 1, 2)
        
        layout.addLayout(grid)
        
        # Bouton actualiser
        refresh_layout = QHBoxLayout()
        refresh_layout.addStretch()
        
        self.btn_refresh = QPushButton("🔄 Actualiser")
        self.btn_refresh.setObjectName("ghost")
        self.btn_refresh.setMinimumHeight(40)
        self.btn_refresh.clicked.connect(self.load_stats)
        refresh_layout.addWidget(self.btn_refresh)
        refresh_layout.addStretch()
        
        layout.addLayout(refresh_layout)
        layout.addStretch()
    
    def create_stat_card(self, title, value, accent_color):
        card = QFrame()
        card.setObjectName("card")
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(8)
        
        indicator = QFrame()
        indicator.setFixedHeight(3)
        indicator.setStyleSheet(f"background-color: {accent_color}; border-radius: 2px;")
        layout.addWidget(indicator)
        
        label_title = QLabel(title)
        label_title.setObjectName("statLabel")
        layout.addWidget(label_title)
        
        label_value = QLabel(value)
        label_value.setObjectName("statValue")
        layout.addWidget(label_value)
        
        card.value_label = label_value
        return card
    
    def create_gender_card(self):
        card = QFrame()
        card.setObjectName("card")
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)
        
        indicator = QFrame()
        indicator.setFixedHeight(3)
        indicator.setStyleSheet("background-color: #64748b; border-radius: 2px;")
        layout.addWidget(indicator)
        
        title = QLabel("⚥ Répartition par genre")
        title.setObjectName("statLabel")
        layout.addWidget(title)
        
        male_container = QVBoxLayout()
        male_container.setSpacing(4)
        
        male_header = QHBoxLayout()
        male_label = QLabel("Hommes")
        male_label.setStyleSheet("color: #334155; font-weight: 500; font-size: 9pt;")
        male_header.addWidget(male_label)
        
        self.male_percent = QLabel("0%")
        self.male_percent.setStyleSheet("color: #6366f1; font-weight: 600; font-size: 9pt;")
        male_header.addWidget(self.male_percent)
        male_container.addLayout(male_header)
        
        self.bar_male = QProgressBar()
        self.bar_male.setTextVisible(False)
        self.bar_male.setFixedHeight(8)
        self.bar_male.setStyleSheet("""
            QProgressBar { background-color: #e0e7ff; border-radius: 4px; }
            QProgressBar::chunk { background-color: #6366f1; border-radius: 4px; }
        """)
        male_container.addWidget(self.bar_male)
        layout.addLayout(male_container)
        
        female_container = QVBoxLayout()
        female_container.setSpacing(4)
        
        female_header = QHBoxLayout()
        female_label = QLabel("Femmes")
        female_label.setStyleSheet("color: #334155; font-weight: 500; font-size: 9pt;")
        female_header.addWidget(female_label)
        
        self.female_percent = QLabel("0%")
        self.female_percent.setStyleSheet("color: #ec4899; font-weight: 600; font-size: 9pt;")
        female_header.addWidget(self.female_percent)
        female_container.addLayout(female_header)
        
        self.bar_female = QProgressBar()
        self.bar_female.setTextVisible(False)
        self.bar_female.setFixedHeight(8)
        self.bar_female.setStyleSheet("""
            QProgressBar { background-color: #fce7f3; border-radius: 4px; }
            QProgressBar::chunk { background-color: #ec4899; border-radius: 4px; }
        """)
        female_container.addWidget(self.bar_female)
        layout.addLayout(female_container)
        layout.addStretch()
        
        return card
    
    def load_stats(self):
        stats = self.db.get_stats()
        
        self.card_martyrs.value_label.setText(str(stats['total_martyrs']))
        self.card_families.value_label.setText(str(stats['total_families']))
        self.card_total.value_label.setText(str(stats['total_persons']))
        self.card_orphans.value_label.setText(str(stats['martyrs_without_family']))
        self.card_no_cin.value_label.setText(str(stats['without_cin']))
        
        total = stats['total_persons']
        if total > 0:
            gender = stats['gender_distribution']
            male = gender.get('M', 0)
            female = gender.get('F', 0)
            
            male_pct = int(male / total * 100)
            female_pct = int(female / total * 100)
            
            self.bar_male.setValue(male_pct)
            self.bar_female.setValue(female_pct)
            self.male_percent.setText(f"{male_pct}% ({male})")
            self.female_percent.setText(f"{female_pct}% ({female})")
        else:
            self.bar_male.setValue(0)
            self.bar_female.setValue(0)
            self.male_percent.setText("0%")
            self.female_percent.setText("0%")