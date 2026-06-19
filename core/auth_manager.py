#!/usr/bin/env python3
"""
auth_manager.py — Gestionnaire de session global

Singleton qui maintient l'état de connexion de l'application.
Persiste le token dans un fichier local pour le "Remember me".
"""

import json
from pathlib import Path
from typing import Optional
from dataclasses import asdict

from .auth_service import AuthService, User, AuthError


class AuthManager:
    """Singleton de gestion de session"""
    
    _instance = None
    _TOKEN_FILE = Path("database/session.json")
    
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
    
    # ========== PROPRIÉTÉS ==========
    
    @property
    def current_user(self) -> Optional[User]:
        return self._current_user
    
    @property
    def is_authenticated(self) -> bool:
        return self._current_user is not None
    
    @property
    def is_admin(self) -> bool:
        return self._current_user is not None and self._current_user.is_admin
    
    # ========== LOGIN / LOGOUT ==========
    
    def login(self, username: str, password: str, remember: bool = False) -> bool:
        """Authentifie et stocke la session"""
        try:
            user, token = self._service.login(username, password)
            self._current_user = user
            self._token = token
            
            if remember:
                self._save_token(token)
            
            return True
            
        except AuthError:
            return False
    
    def logout(self):
        """Déconnecte et nettoie"""
        if self._token:
            self._service.logout(self._token)
        
        self._current_user = None
        self._token = None
        self._clear_token()
    
    def auto_login(self) -> bool:
        """Tente une connexion automatique depuis le token sauvegardé"""
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
    
    # ========== PERSISTANCE TOKEN ==========
    
    def _save_token(self, token: str):
        """Sauvegarde le token localement"""
        self._TOKEN_FILE.parent.mkdir(parents=True, exist_ok=True)
        self._TOKEN_FILE.write_text(json.dumps({"token": token}), encoding='utf-8')
    
    def _load_token(self) -> Optional[str]:
        """Charge le token depuis le fichier"""
        if not self._TOKEN_FILE.exists():
            return None
        
        try:
            data = json.loads(self._TOKEN_FILE.read_text(encoding='utf-8'))
            return data.get("token")
        except (json.JSONDecodeError, KeyError):
            return None
    
    def _clear_token(self):
        """Supprime le token sauvegardé"""
        if self._TOKEN_FILE.exists():
            self._TOKEN_FILE.unlink()
    
    # ========== DELEGATION ==========
    
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