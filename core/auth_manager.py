#!/usr/bin/env python3
"""
auth_manager.py — Gestionnaire de session global (Singleton)

Maintient l'état de connexion de l'application.

COMPATIBLE PYINSTALLER — pas d'imports circulaires
"""

import json
import os
import sys
from pathlib import Path
from typing import Optional

from .auth_service import AuthService, User, AuthError, _get_app_data_dir, _get_token_path


class AuthManager:
    """Singleton de gestion de session — Compatible PyInstaller"""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self._service = AuthService()
        self._current_user: Optional[User] = None
        self._token: Optional[str] = None
        self._initialized = True

    # ─── PROPRIÉTÉS ──────────────────────────────────────────────────────────

    @property
    def current_user(self) -> Optional[User]:
        return self._current_user

    @property
    def is_authenticated(self) -> bool:
        return self._current_user is not None

    @property
    def is_admin(self) -> bool:
        return self._current_user is not None and self._current_user.is_admin

    # ─── LOGIN / LOGOUT ──────────────────────────────────────────────────────

    def login(self, username: str, password: str) -> bool:
        """Authentifie et stocke la session."""
        try:
            user, token = self._service.login(username, password)
            self._current_user = user
            self._token = token

            return True

        except AuthError:
            return False

    def logout(self):
        """Déconnecte et nettoie tout."""
        if self._token:
            self._service.logout(self._token)

        self._current_user = None
        self._token = None
        self._clear_token()

    def auto_login(self) -> bool:
        """Tente une connexion automatique depuis le token sauvegardé."""
        token = self._load_token()

        if not token:
            return False

        user = self._service.validate_session(token)

        if user:
            self._current_user = user
            self._token = token
            return True

        # Token invalide ou expiré
        self._clear_token()
        return False

    # ─── PERSISTANCE TOKEN (dans AppData, pas dans ./database/) ──────────────

    def _save_token(self, token: str):
        """Sauvegarde le token dans AppData/Local/FamilyManager/session.json"""
        token_file = _get_token_path()
        token_file.parent.mkdir(parents=True, exist_ok=True)
        token_file.write_text(json.dumps({"token": token}), encoding='utf-8')

    def _load_token(self) -> Optional[str]:
        """Charge le token depuis AppData."""
        token_file = _get_token_path()
        if not token_file.exists():
            return None

        try:
            data = json.loads(token_file.read_text(encoding='utf-8'))
            return data.get("token")
        except (json.JSONDecodeError, KeyError):
            return None

    def _clear_token(self):
        """Supprime le token sauvegardé."""
        token_file = _get_token_path()
        if token_file.exists():
            token_file.unlink()

    # ─── DÉLÉGATION VERS AuthService ───────────────────────────────────────

    def create_user(self, *args, **kwargs):
        return self._service.create_user(*args, **kwargs)

    def update_password(self, *args, **kwargs):
        return self._service.update_password(*args, **kwargs)

    def list_users(self):
        return self._service.list_users()

    def delete_user(self, user_id: int):
        return self._service.delete_user(user_id)

    def has_users(self):
        return self._service.has_users()

    def create_first_admin(self, *args, **kwargs):
        return self._service.create_first_admin(*args, **kwargs)