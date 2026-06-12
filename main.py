import sys
from PySide6.QtWidgets import QApplication
from gui.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    # Style global
    app.setStyleSheet("""
        QMainWindow {
            background-color: #fafafa;
        }
        QWidget {
            font-family: 'Segoe UI', Arial, sans-serif;
            font-size: 10pt;
        }
        QGroupBox {
            font-weight: bold;
            border: 1px solid #ddd;
            border-radius: 5px;
            margin-top: 10px;
            padding-top: 10px;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px;
        }
        QLineEdit, QComboBox, QTextEdit, QDateEdit {
            padding: 5px;
            border: 1px solid #ccc;
            border-radius: 3px;
        }
        QLineEdit:focus, QComboBox:focus, QTextEdit:focus {
            border: 1px solid #2196F3;
        }
    """)
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()