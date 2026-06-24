# core/feature_tracker.py
import json
from pathlib import Path
from .auth_service import _get_app_data_dir


class FeatureTracker:
    """Gère l'affichage des nouveautés après mise à jour"""
    
    _FILE = _get_app_data_dir() / "seen_versions.json"
    
    @classmethod
    def get_last_seen_version(cls) -> str:
        """Retourne la dernière version dont l'utilisateur a vu les nouveautés"""
        if not cls._FILE.exists():
            return "0.0.0"
        try:
            data = json.loads(cls._FILE.read_text(encoding='utf-8'))
            return data.get("last_seen_version", "0.0.0")
        except (json.JSONDecodeError, KeyError):
            return "0.0.0"
    
    @classmethod
    def mark_version_seen(cls, version: str):
        """Marque une version comme vue"""
        cls._FILE.parent.mkdir(parents=True, exist_ok=True)
        cls._FILE.write_text(json.dumps({"last_seen_version": version}), encoding='utf-8')
    
    @classmethod
    def should_show_changelog(cls, current_version: str) -> bool:
        """Détermine si les nouveautés doivent être affichées"""
        from packaging import version as pkg_version  # pip install packaging
        last_seen = cls.get_last_seen_version()
        return pkg_version.parse(current_version) > pkg_version.parse(last_seen)