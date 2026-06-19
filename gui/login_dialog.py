from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QCheckBox, QMessageBox, QStackedWidget,
    QWidget, QFrame, QSizePolicy
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

from core.auth_manager import AuthManager


class LoginDialog(QDialog):
    """Dialogue modal de connexion"""

    login_success = Signal()  # Émis quand la connexion réussit

    def __init__(self, parent=None, is_first_setup: bool = False):
        super().__init__(parent)
        self.auth = AuthManager()
        self.is_first_setup = is_first_setup

        self.setWindowTitle("Family Manager — Connexion")
        self.setFixedSize(420, 520 if not is_first_setup else 560)

        # FIX : Garde le bouton X actif ET retire le ?
        self.setWindowFlags(
            Qt.Dialog | 
            Qt.WindowCloseButtonHint | 
            Qt.WindowTitleHint
        )

        self._setup_ui()
        self._apply_styles()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 30, 40, 30)
        layout.setSpacing(16)

        # Logo / Titre
        title = QLabel("👨‍👩‍👧‍👦 Family Manager")
        title.setObjectName("loginTitle")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        subtitle = QLabel("Gérez votre famille, simplement.")
        subtitle.setObjectName("loginSubtitle")
        subtitle.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtitle)

        layout.addSpacing(20)

        # Stack : Login / Register
        self.stack = QStackedWidget()

        # Page Login (toujours présente)
        self.login_page = self._create_login_page()
        self.stack.addWidget(self.login_page)

        # Page Register (créée mais affichée seulement si premier setup)
        self.register_page = self._create_register_page()
        self.stack.addWidget(self.register_page)

        if self.is_first_setup:
            self.stack.setCurrentIndex(1)  # Afficher inscription
            subtitle.setText("Créez votre compte administrateur")
        else:
            self.stack.setCurrentIndex(0)  # Afficher login

        layout.addWidget(self.stack)

        # Toggle link — AFFICHE SEULEMENT SI PREMIER SETUP
        if self.is_first_setup:
            self.toggle_btn = QPushButton("Déjà un compte ? Se connecter")
            self.toggle_btn.setObjectName("ghost")
            self.toggle_btn.setFlat(True)
            self.toggle_btn.clicked.connect(self._toggle_page)
            layout.addWidget(self.toggle_btn, alignment=Qt.AlignCenter)
        else:
            # Label discret au lieu du bouton toggle
            no_account = QLabel("Contactez l'administrateur pour créer un compte.")
            no_account.setObjectName("loginSubtitle")
            no_account.setAlignment(Qt.AlignCenter)
            layout.addWidget(no_account)

        # FIX : Bouton Annuler explicite
        self.btn_cancel = QPushButton("Annuler")
        self.btn_cancel.setObjectName("ghost")
        self.btn_cancel.clicked.connect(self.reject)  # ← Émet Rejected
        layout.addWidget(self.btn_cancel, alignment=Qt.AlignCenter)

    def _create_login_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        # Username
        self.login_user = QLineEdit()
        self.login_user.setPlaceholderText("Nom d'utilisateur")
        self.login_user.setObjectName("input")
        self.login_user.returnPressed.connect(self._do_login)
        layout.addWidget(self.login_user)

        # Password
        self.login_pass = QLineEdit()
        self.login_pass.setPlaceholderText("Mot de passe")
        self.login_pass.setEchoMode(QLineEdit.Password)
        self.login_pass.setObjectName("input")
        self.login_pass.returnPressed.connect(self._do_login)
        layout.addWidget(self.login_pass)

        # Login button
        btn = QPushButton("Se connecter")
        btn.setObjectName("primary")
        btn.clicked.connect(self._do_login)
        layout.addWidget(btn)

        layout.addStretch()
        return page

    def _create_register_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        # Username
        self.reg_user = QLineEdit()
        self.reg_user.setPlaceholderText("Nom d'utilisateur *")
        self.reg_user.setObjectName("input")
        layout.addWidget(self.reg_user)

        # Display name
        self.reg_display = QLineEdit()
        self.reg_display.setPlaceholderText("Nom affiché")
        self.reg_display.setObjectName("input")
        layout.addWidget(self.reg_display)

        # Email
        self.reg_email = QLineEdit()
        self.reg_email.setPlaceholderText("Email (optionnel)")
        self.reg_email.setObjectName("input")
        layout.addWidget(self.reg_email)

        # Password
        self.reg_pass = QLineEdit()
        self.reg_pass.setPlaceholderText("Mot de passe * (min. 6 caractères)")
        self.reg_pass.setEchoMode(QLineEdit.Password)
        self.reg_pass.setObjectName("input")
        layout.addWidget(self.reg_pass)

        # Confirm password
        self.reg_confirm = QLineEdit()
        self.reg_confirm.setPlaceholderText("Confirmer le mot de passe *")
        self.reg_confirm.setEchoMode(QLineEdit.Password)
        self.reg_confirm.setObjectName("input")
        layout.addWidget(self.reg_confirm)

        # Register button
        btn = QPushButton("Créer le compte")
        btn.setObjectName("primary")
        btn.clicked.connect(self._do_register)
        layout.addWidget(btn)

        layout.addStretch()
        return page

    def _toggle_page(self):
        current = self.stack.currentIndex()
        self.stack.setCurrentIndex(1 - current)

        # Mettre à jour le texte du bouton toggle
        if self.stack.currentIndex() == 0:
            self.toggle_btn.setText("Pas encore de compte ? S'inscrire")
        else:
            self.toggle_btn.setText("Déjà un compte ? Se connecter")

    def _do_login(self):
        """Tente la connexion avec les credentials saisis."""
        username = self.login_user.text().strip()
        password = self.login_pass.text()

        if not username or not password:
            QMessageBox.warning(self, "Champs requis", "Veuillez remplir tous les champs.")
            return

        # FIX : Appel à auth.login() manquant dans ton code
        if self.auth.login(username, password):
            self.login_success.emit()
            self.accept()
        else:
            QMessageBox.critical(
                self, "Échec de connexion",
                "Nom d'utilisateur ou mot de passe incorrect."
            )
            self.login_pass.clear()
            self.login_pass.setFocus()

    def _do_register(self):
        username = self.reg_user.text().strip()
        password = self.reg_pass.text()
        confirm = self.reg_confirm.text()
        email = self.reg_email.text().strip() or None
        display = self.reg_display.text().strip() or None

        if not username or not password:
            QMessageBox.warning(self, "Champs requis", "Nom d'utilisateur et mot de passe obligatoires.")
            return

        if password != confirm:
            QMessageBox.warning(self, "Erreur", "Les mots de passe ne correspondent pas.")
            self.reg_confirm.clear()
            return

        try:
            self.auth.create_user(
                username=username,
                password=password,
                email=email,
                display_name=display,
                is_admin=self.is_first_setup  # Premier compte = admin
            )

            # Auto-login après inscription
            self.auth.login(username, password)
            self.login_success.emit()
            self.accept()

        except Exception as e:
            QMessageBox.critical(self, "Erreur", str(e))

    def _apply_styles(self):
        self.setStyleSheet("""
            QDialog {
                background-color: #f8fafc;
            }

            QLabel#loginTitle {
                font-size: 22pt;
                font-weight: 700;
                color: #0f172a;
                letter-spacing: -0.5px;
            }

            QLabel#loginSubtitle {
                font-size: 10pt;
                color: #64748b;
                margin-bottom: 8px;
            }

            QLineEdit#input {
                background-color: #ffffff;
                border: 1.5px solid #e2e8f0;
                border-radius: 10px;
                padding: 12px 16px;
                font-size: 10.5pt;
                color: #334155;
                min-height: 20px;
            }

            QLineEdit#input:focus {
                border-color: #6366f1;
            }

            QLineEdit#input::placeholder {
                color: #94a3b8;
            }

            QPushButton#primary {
                background-color: #6366f1;
                color: white;
                border: none;
                border-radius: 10px;
                padding: 12px;
                font-weight: 600;
                font-size: 10.5pt;
                margin-top: 8px;
            }

            QPushButton#primary:hover {
                background-color: #4f46e5;
            }

            QPushButton#primary:pressed {
                background-color: #4338ca;
            }

            QPushButton#ghost {
                background-color: transparent;
                color: #6366f1;
                border: none;
                font-weight: 500;
                font-size: 9.5pt;
            }

            QPushButton#ghost:hover {
                color: #4f46e5;
                text-decoration: underline;
            }
        """)