import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QFontDatabase, QIcon
from core.auth_manager import AuthManager
from gui.main_window import MainWindow
from gui.login_dialog import LoginDialog

def load_fonts():
    """Charge les polices système modernes selon l'OS"""
    font_db = QFontDatabase()
    
    # Priorité : Inter > SF Pro > Segoe UI > Arial
    families = QFontDatabase.families()
    
    preferred = None
    for font_name in ["Inter", "SF Pro Display", "Segoe UI", "Helvetica Neue", "Arial"]:
        if font_name in families:
            preferred = font_name
            break
    
    if not preferred:
        preferred = "Arial"
    
    return preferred


def setup_palette(app):
    """Configure une palette moderne neutre"""
    from PySide6.QtGui import QPalette, QColor
    
    palette = QPalette()
    
    # Couleurs de base
    slate_50 = QColor(248, 250, 252)
    slate_100 = QColor(241, 245, 249)
    slate_200 = QColor(226, 232, 240)
    slate_300 = QColor(203, 213, 225)
    slate_400 = QColor(148, 163, 184)
    slate_500 = QColor(100, 116, 139)
    slate_600 = QColor(71, 85, 105)
    slate_700 = QColor(51, 65, 85)
    slate_800 = QColor(30, 41, 59)
    slate_900 = QColor(15, 23, 42)
    
    indigo_500 = QColor(99, 102, 241)
    indigo_600 = QColor(79, 70, 229)
    
    # Application
    palette.setColor(QPalette.Window, slate_50)
    palette.setColor(QPalette.WindowText, slate_900)
    palette.setColor(QPalette.Base, QColor(255, 255, 255))
    palette.setColor(QPalette.AlternateBase, slate_100)
    palette.setColor(QPalette.ToolTipBase, slate_800)
    palette.setColor(QPalette.ToolTipText, QColor(255, 255, 255))
    palette.setColor(QPalette.Text, slate_800)
    palette.setColor(QPalette.Button, slate_100)
    palette.setColor(QPalette.ButtonText, slate_700)
    palette.setColor(QPalette.BrightText, QColor(255, 255, 255))
    palette.setColor(QPalette.Highlight, indigo_500)
    palette.setColor(QPalette.HighlightedText, QColor(255, 255, 255))
    palette.setColor(QPalette.Link, indigo_600)
    
    app.setPalette(palette)


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

     # Icône
    icon_path = Path("assets/icon/islam.ico")
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))
    
    # Police moderne
    font_family = load_fonts()
    font = QFont(font_family, 10)
    font.setStyleHint(QFont.SansSerif)
    app.setFont(font)
    
    # Palette
    setup_palette(app)
    
    # Stylesheet global moderne — "Linear-inspired"
    app.setStyleSheet("""
        /* ===== BASE ===== */
        QWidget {
            font-family: '%s';
            font-size: 10pt;
            color: #334155;
        }
        
        QMainWindow {
            background-color: #f8fafc;
        }
        
        /* ===== SIDEBAR / PANNEAUX ===== */
        QFrame#sidebar, QFrame#leftPanel {
            background-color: #ffffff;
            border-right: 1px solid #e2e8f0;
        }
        
        QFrame#card {
            background-color: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 12px;
        }
        
        /* ===== TYPOGRAPHIE ===== */
        QLabel#title {
            font-size: 18pt;
            font-weight: 700;
            color: #0f172a;
            letter-spacing: -0.5px;
        }
        
        QLabel#subtitle {
            font-size: 11pt;
            font-weight: 500;
            color: #64748b;
        }
        
        QLabel#statValue {
            font-size: 28pt;
            font-weight: 700;
            color: #0f172a;
            letter-spacing: -1px;
        }
        
        QLabel#statLabel {
            font-size: 9pt;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            color: #64748b;
        }
        
        /* ===== BOUTONS ===== */
        QPushButton {
            background-color: #f1f5f9;
            color: #475569;
            border: none;
            border-radius: 8px;
            padding: 8px 16px;
            font-weight: 600;
            font-size: 9.5pt;
        }
        
        QPushButton:hover {
            background-color: #e2e8f0;
        }
        
        QPushButton:pressed {
            background-color: #cbd5e1;
        }
        
        QPushButton:disabled {
            background-color: #f1f5f9;
            color: #94a3b8;
        }
        
        /* Bouton primaire */
        QPushButton#primary {
            background-color: #6366f1;
            color: white;
        }
        
        QPushButton#primary:hover {
            background-color: #4f46e5;
        }
        
        QPushButton#primary:pressed {
            background-color: #4338ca;
        }
        
        /* Bouton danger */
        QPushButton#danger {
            background-color: #fef2f2;
            color: #dc2626;
        }
        
        QPushButton#danger:hover {
            background-color: #fee2e2;
        }
        
        /* Bouton ghost */
        QPushButton#ghost {
            background-color: transparent;
            color: #64748b;
        }
        
        QPushButton#ghost:hover {
            background-color: #f1f5f9;
            color: #475569;
        }
        
        /* ===== INPUTS ===== */
        QLineEdit, QComboBox, QDateEdit, QTextEdit {
            background-color: #ffffff;
            border: 1.5px solid #e2e8f0;
            border-radius: 8px;
            padding: 8px 12px;
            font-size: 10pt;
            color: #334155;
        }
        
        QLineEdit:focus, QComboBox:focus, QDateEdit:focus, QTextEdit:focus {
            border-color: #6366f1;
        }
        
        QLineEdit::placeholder, QTextEdit::placeholder {
            color: #94a3b8;
        }
        
        QComboBox::drop-down {
            border: none;
            width: 24px;
        }
        
        QComboBox::down-arrow {
            image: none;
            border-left: 4px solid transparent;
            border-right: 4px solid transparent;
            border-top: 5px solid #94a3b8;
            margin-right: 8px;
        }
        
        QComboBox QAbstractItemView {
            background-color: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            selection-background-color: #e0e7ff;
            selection-color: #4338ca;
            padding: 4px;
        }
        
        /* ===== TABLEAUX ===== */
        QTableWidget {
            background-color: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 12px;
            gridline-color: #f1f5f9;
            outline: none;
        }
        
        QTableWidget::item {
            padding: 12px 8px;
            border-bottom: 1px solid #f1f5f9;
        }
        
        QTableWidget::item:selected {
            background-color: #e0e7ff;
            color: #4338ca;
        }
        
        QTableWidget::item:hover {
            background-color: #f8fafc;
        }
        
        QHeaderView::section {
            background-color: #f8fafc;
            color: #64748b;
            font-weight: 600;
            font-size: 9pt;
            padding: 12px 8px;
            border: none;
            border-bottom: 2px solid #e2e8f0;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        /* ===== GROUP BOX ===== */
        QGroupBox {
            background-color: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 12px;
            margin-top: 16px;
            padding: 20px;
            font-weight: 600;
            color: #334155;
        }
        
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 16px;
            padding: 0 8px;
            color: #475569;
            font-size: 10pt;
        }
        
        /* ===== TABS ===== */
        QPushButton#tab {
            background-color: transparent;
            color: #64748b;
            border: none;
            border-radius: 0;
            border-bottom: 2px solid transparent;
            padding: 12px 20px;
            font-weight: 600;
        }
        
        QPushButton#tab:checked, QPushButton#tab:checked:hover {
            color: #6366f1;
            border-bottom-color: #6366f1;
            background-color: transparent;
        }
        
        QPushButton#tab:hover {
            color: #475569;
            background-color: transparent;
        }
        
        /* ===== SCROLLBAR ===== */
        QScrollBar:vertical {
            background-color: transparent;
            width: 8px;
            border-radius: 4px;
        }
        
        QScrollBar::handle:vertical {
            background-color: #cbd5e1;
            border-radius: 4px;
            min-height: 32px;
        }
        
        QScrollBar::handle:vertical:hover {
            background-color: #94a3b8;
        }
        
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            height: 0px;
        }
        
        /* ===== TREE ===== */
        QTreeWidget {
            background-color: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 12px;
            outline: none;
        }
        
        QTreeWidget::item {
            padding: 10px;
            border-radius: 6px;
            margin: 2px 4px;
        }
        
        QTreeWidget::item:selected {
            background-color: #e0e7ff;
            color: #4338ca;
        }
        
        QTreeWidget::item:hover {
            background-color: #f8fafc;
        }
        
        /* ===== PROGRESS BAR ===== */
        QProgressBar {
            background-color: #f1f5f9;
            border-radius: 999px;
            height: 8px;
            text-align: center;
            font-size: 0px;
        }
        
        QProgressBar::chunk {
            background-color: #6366f1;
            border-radius: 999px;
        }
        
        /* ===== TOOLTIP ===== */
        QToolTip {
            background-color: #1e293b;
            color: #f8fafc;
            border: none;
            border-radius: 6px;
            padding: 6px 10px;
            font-size: 9pt;
        }
        
        /* ===== DIALOG ===== */
        QDialog {
            background-color: #f8fafc;
        }
        
        /* ===== SPLITTER ===== */
        QSplitter::handle {
            background-color: #e2e8f0;
        }
        
        QSplitter::handle:hover {
            background-color: #cbd5e1;
        }
        
        /* ===== CHECKBOX ===== */
        QCheckBox {
            spacing: 8px;
            font-size: 10pt;
        }
        
        QCheckBox::indicator {
            width: 18px;
            height: 18px;
            border: 2px solid #cbd5e1;
            border-radius: 4px;
            background-color: #ffffff;
        }
        
        QCheckBox::indicator:checked {
            background-color: #6366f1;
            border-color: #6366f1;
        }
        
        QCheckBox::indicator:hover {
            border-color: #94a3b8;
        }
    """ % font_family)




    # Icône
    icon_path = Path("assets/icon/islam.ico")
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))
    
    # Police, palette, stylesheet...
    # ... (ton code existant) ...
    
    # ========== AUTHENTIFICATION ==========
    auth = AuthManager()
    
    # Vérifier s'il y a des utilisateurs (premier démarrage)
    is_first = not auth.has_users()
    
    # Tenter auto-login
    auto_logged = auth.auto_login()
    
    if not auto_logged:
        # Montrer le dialogue de connexion
        login = LoginDialog(is_first_setup=is_first)
        
        if not login.exec():  # L'utilisateur a fermé sans se connecter
            sys.exit(0)
            
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()