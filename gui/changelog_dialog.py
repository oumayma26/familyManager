#!/usr/bin/env python3
"""
changelog_dialog.py — Dialogue "Nouveautés" style Timeline verticale

Chaque feature est affichée sur une ligne avec un point et un trait vertical.
Style épuré, moderne, facile à lire.
"""
import json
from pathlib import Path
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QFrame, QCheckBox, QWidget, QSizePolicy
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont


# ═══════════════════════════════════════════════════════════════════════════════
# CHARGEMENT DU CHANGELOG DEPUIS JSON
# ═══════════════════════════════════════════════════════════════════════════════

def _get_base_dir() -> Path:
    """Retourne le dossier racine (compatible PyInstaller)."""
    import sys
    if getattr(sys, 'frozen', False):
        return Path(sys.executable).parent
    return Path(__file__).parent


def load_changelog() -> dict:
    """Charge le changelog depuis changelog.json."""
    changelog_path = _get_base_dir() / "changelog.json"
    if not changelog_path.exists():
        return {}
    with open(changelog_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def get_latest_version() -> str:
    """Retourne la dernière version du changelog (semver)."""
    changelog = load_changelog()
    if not changelog:
        return "0.0.0"
    return max(changelog.keys(), key=lambda v: tuple(int(p) for p in v.split('.')))


def get_changelog_features(version: str = None) -> list[str]:
    """Retourne les features d'une version (dernière par défaut)."""
    changelog = load_changelog()
    if not changelog:
        return []
    if version is None:
        version = get_latest_version()
    return changelog.get(version, [])


# Constante pour rétrocompatibilité
CHANGELOG = load_changelog()


class ChangelogDialog(QDialog):
    """Dialogue affichant les nouveautés — Style Timeline verticale."""

    def __init__(self, version: str, features: list[str], parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Nouveautés — v{version}")
        self.setMinimumSize(500, 450)
        self.setMaximumSize(580, 600)
        self.setModal(True)

        self._setup_ui(version, features)
        self._apply_styles()

    def _setup_ui(self, version: str, features: list[str]):
        layout = QVBoxLayout(self)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        # ═══ HEADER ═══
        header = QFrame()
        header.setObjectName("changelogHeader")
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(28, 24, 28, 24)
        header_layout.setSpacing(6)

        title = QLabel(f"✨ Nouveautés")
        title.setObjectName("changelogTitle")
        title.setAlignment(Qt.AlignLeft)
        header_layout.addWidget(title)

        version_label = QLabel(f"Version {version}")
        version_label.setObjectName("changelogVersion")
        header_layout.addWidget(version_label)

        layout.addWidget(header)

        # ═══ SCROLL AREA (TIMELINE) ═══
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setObjectName("changelogScroll")

        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(28, 20, 28, 20)
        content_layout.setSpacing(0)

        for i, feature in enumerate(features):
            is_last = (i == len(features) - 1)
            item = self._create_timeline_item(feature, is_last)
            content_layout.addWidget(item)

        content_layout.addStretch()
        scroll.setWidget(content_widget)
        layout.addWidget(scroll, 1)

        # ═══ FOOTER ═══
        footer = QFrame()
        footer.setObjectName("changelogFooter")
        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(28, 16, 28, 16)
        footer_layout.setSpacing(12)

        self.dont_show_again = QCheckBox("Ne plus afficher au démarrage")
        self.dont_show_again.setObjectName("changelogCheckbox")
        footer_layout.addWidget(self.dont_show_again)
        footer_layout.addStretch()

        ok_btn = QPushButton("C'est parti !")
        ok_btn.setObjectName("changelogOkBtn")
        ok_btn.setMinimumWidth(120)
        ok_btn.setMinimumHeight(36)
        ok_btn.setCursor(Qt.PointingHandCursor)
        ok_btn.clicked.connect(self.accept)
        footer_layout.addWidget(ok_btn)

        layout.addWidget(footer)

    def _create_timeline_item(self, text: str, is_last: bool) -> QWidget:
        """Crée un item de timeline avec point + trait vertical + texte."""
        container = QWidget()
        container_layout = QHBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)
        container_layout.setAlignment(Qt.AlignTop)

        # ═══ COLONNE GAUCHE : Point + Trait ═══
        left_col = QWidget()
        left_col.setFixedWidth(28)
        left_layout = QVBoxLayout(left_col)
        left_layout.setContentsMargins(0, 8, 0, 0)
        left_layout.setSpacing(0)
        left_layout.setAlignment(Qt.AlignTop)

        # Point (cercle coloré)
        dot = QFrame()
        dot.setFixedSize(12, 12)
        dot.setObjectName("timelineDot")
        left_layout.addWidget(dot, alignment=Qt.AlignHCenter)

        # Trait vertical (sauf pour le dernier item)
        if not is_last:
            line = QFrame()
            line.setFixedWidth(2)
            line.setObjectName("timelineLine")
            line.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
            left_layout.addWidget(line, alignment=Qt.AlignHCenter)
        else:
            # Espace vide pour aligner le dernier item
            spacer = QWidget()
            spacer.setFixedWidth(2)
            spacer.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
            left_layout.addWidget(spacer, alignment=Qt.AlignHCenter)

        container_layout.addWidget(left_col)

        # ═══ COLONNE DROITE : Texte ═══
        right_col = QWidget()
        right_layout = QVBoxLayout(right_col)
        right_layout.setContentsMargins(8, 4, 0, 16 if not is_last else 4)
        right_layout.setSpacing(0)
        right_layout.setAlignment(Qt.AlignTop)

        label = QLabel(text)
        label.setWordWrap(True)
        label.setObjectName("timelineText")
        right_layout.addWidget(label)

        container_layout.addWidget(right_col, 1)

        return container

    def _apply_styles(self):
        """Stylesheet Timeline."""
        self.setStyleSheet("""
            /* ===== DIALOGUE ===== */
            QDialog {
                background-color: #ffffff;
                border-radius: 10px;
            }

            /* ===== HEADER ===== */
            QFrame#changelogHeader {
                background-color: #ffffff;
                border-bottom: 1px solid #f3f4f6;
            }

            QLabel#changelogTitle {
                color: #111827;
                font-size: 20pt;
                font-weight: 700;
            }

            QLabel#changelogVersion {
                color: #6b7280;
                font-size: 11pt;
                font-weight: 500;
            }

            /* ===== SCROLL ===== */
            QScrollArea#changelogScroll {
                background-color: #ffffff;
                border: none;
            }

            QScrollArea#changelogScroll QScrollBar:vertical {
                background-color: transparent;
                width: 6px;
                border-radius: 3px;
            }

            QScrollArea#changelogScroll QScrollBar::handle:vertical {
                background-color: #d1d5db;
                border-radius: 3px;
                min-height: 40px;
            }

            QScrollArea#changelogScroll QScrollBar::handle:vertical:hover {
                background-color: #9ca3af;
            }

            QScrollArea#changelogScroll QScrollBar::add-line:vertical,
            QScrollArea#changelogScroll QScrollBar::sub-line:vertical {
                height: 0px;
            }

            /* ===== TIMELINE ===== */
            QFrame#timelineDot {
                background-color: #4f46e5;
                border-radius: 6px;
                border: 2px solid #ffffff;
            }

            QFrame#timelineLine {
                background-color: #e5e7eb;
                min-height: 40px;
            }

            QLabel#timelineText {
                color: #374151;
                font-size: 10.5pt;
                line-height: 1.5;
                padding-bottom: 4px;
            }

            /* ===== FOOTER ===== */
            QFrame#changelogFooter {
                background-color: #f9fafb;
                border-top: 1px solid #f3f4f6;
                border-bottom-left-radius: 10px;
                border-bottom-right-radius: 10px;
            }

            QCheckBox#changelogCheckbox {
                color: #6b7280;
                font-size: 9.5pt;
            }

            QCheckBox#changelogCheckbox::indicator {
                width: 16px;
                height: 16px;
                border: 2px solid #d1d5db;
                border-radius: 4px;
                background-color: #ffffff;
            }

            QCheckBox#changelogCheckbox::indicator:checked {
                background-color: #4f46e5;
                border-color: #4f46e5;
            }

            /* ===== BOUTON OK ===== */
            QPushButton#changelogOkBtn {
                background-color: #4f46e5;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 20px;
                font-weight: 600;
                font-size: 10pt;
            }

            QPushButton#changelogOkBtn:hover {
                background-color: #4338ca;
            }

            QPushButton#changelogOkBtn:pressed {
                background-color: #3730a3;
            }
        """)