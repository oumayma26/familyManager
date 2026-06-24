# database/__init__.py
import sqlite3
import os
import sys
from datetime import datetime
from pathlib import Path


def get_app_data_dir():
    """Retourne le dossier de données de l'application."""
    if sys.platform == 'win32':
        base_dir = Path(os.environ.get('LOCALAPPDATA', os.path.expanduser('~'))) / 'FamilyManager'
    else:
        base_dir = Path.home() / '.local' / 'share' / 'FamilyManager'
    
    base_dir.mkdir(parents=True, exist_ok=True)
    return base_dir


def get_db_path():
    """Retourne le chemin absolu de la base de données."""
    app_dir = get_app_data_dir()
    db_dir = app_dir / "database"
    db_dir.mkdir(parents=True, exist_ok=True)
    return str(db_dir / "family_tree.db")


def get_photos_dir():
    """Retourne le chemin du dossier photos."""
    app_dir = get_app_data_dir()
    photos_dir = app_dir / "photos"
    photos_dir.mkdir(parents=True, exist_ok=True)
    return str(photos_dir)