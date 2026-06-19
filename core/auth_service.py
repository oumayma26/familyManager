#!/usr/bin/env python3
"""
auth_service.py — Service d'authentification pour Family Manager

Gère :
- Hashage sécurisé (HMAC-SHA256 + salt + pepper)
- Création de compte
- Login / Logout
- Sessions persistantes
- Vérification des permissions

COMPATIBLE PYINSTALLER — pas d'imports circulaires avec database.py
"""

import os
import sys
import secrets
import hashlib
import hmac
import sqlite3
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import Optional, Tuple
from pathlib import Path


# ═══════════════════════════════════════════════════════════════════════════════
# UTILITAIRES DB — Copiés ici pour éviter les imports circulaires avec database.py
# ═══════════════════════════════════════════════════════════════════════════════

def _get_app_data_dir() -> Path:
    """Retourne le dossier de données de l'application (AppData/Local ou ~/.local/share)."""
    if sys.platform == 'win32':
        base_dir = Path(os.environ.get('LOCALAPPDATA', os.path.expanduser('~'))) / 'FamilyManager'
    else:
        base_dir = Path.home() / '.local' / 'share' / 'FamilyManager'
    base_dir.mkdir(parents=True, exist_ok=True)
    return base_dir


def _get_db_path() -> str:
    """Retourne le chemin absolu de la base de données (même que DatabaseManager)."""
    app_dir = _get_app_data_dir()
    db_dir = app_dir / "database"
    db_dir.mkdir(parents=True, exist_ok=True)
    return str(db_dir / "family_tree.db")


def _get_token_path() -> Path:
    """Retourne le chemin du fichier de session persistante."""
    return _get_app_data_dir() / "session.json"


# ═══════════════════════════════════════════════════════════════════════════════
# DATACLASSES & EXCEPTIONS
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class User:
    id: int
    username: str
    email: Optional[str]
    display_name: Optional[str]
    is_admin: bool
    is_active: bool
    created_at: str
    last_login: Optional[str]


class AuthError(Exception):
    """Exception d'authentification"""
    pass


# ═══════════════════════════════════════════════════════════════════════════════
# AUTH SERVICE
# ═══════════════════════════════════════════════════════════════════════════════

class AuthService:
    """Service d'authentification centralisé — Compatible PyInstaller"""

    # ⚠️ CHANGE CETTE VALEUR AVANT MISE EN PRODUCTION !
    PEPPER = "FamilyManager2024_SecretPepper_v1"
    SESSION_DAYS = 30
    MIN_PASSWORD_LENGTH = 6

    def __init__(self, db_path: str = None):
        """
        Initialise le service.
        Si db_path est None, utilise le même chemin que DatabaseManager.
        """
        self.db_path = db_path or _get_db_path()
        self._ensure_db()

    # ─── HASHAGE ─────────────────────────────────────────────────────────────

    def _hash_password(self, password: str, salt: Optional[bytes] = None) -> str:
        """
        Hash un mot de passe avec salt aléatoire + pepper secret.
        Format stocké : salt_hex:hash_hex
        """
        if salt is None:
            salt = os.urandom(32)  # 256 bits de salt

        key = hmac.new(
            self.PEPPER.encode(),
            salt + password.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()

        return f"{salt.hex()}:{key}"

    def _verify_password(self, password: str, stored_hash: str) -> bool:
        """Vérifie un mot de passe contre son hash stocké."""
        try:
            salt_hex, _ = stored_hash.split(":")
            salt = bytes.fromhex(salt_hex)
            return hmac.compare_digest(
                stored_hash,
                self._hash_password(password, salt)
            )
        except (ValueError, TypeError):
            return False

    # ─── CRUD UTILISATEURS ───────────────────────────────────────────────────

    def create_user(
        self,
        username: str,
        password: str,
        email: Optional[str] = None,
        display_name: Optional[str] = None,
        is_admin: bool = False
    ) -> User:
        """Crée un nouvel utilisateur."""
        if len(password) < self.MIN_PASSWORD_LENGTH:
            raise AuthError(f"Mot de passe trop court (min {self.MIN_PASSWORD_LENGTH} caractères)")

        if not username or not username.strip():
            raise AuthError("Nom d'utilisateur requis")

        username = username.strip().lower()
        password_hash = self._hash_password(password)

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    """INSERT INTO users (username, email, password_hash, display_name, is_admin)
                       VALUES (?, ?, ?, ?, ?)""",
                    (username, email, password_hash, display_name or username, int(is_admin))
                )
                user_id = cursor.lastrowid
                conn.commit()
                return self.get_user_by_id(user_id)

        except sqlite3.IntegrityError as e:
            err = str(e).lower()
            if "username" in err:
                raise AuthError(f"Le nom d'utilisateur '{username}' existe déjà")
            if "email" in err:
                raise AuthError("Cet email est déjà utilisé")
            raise AuthError("Erreur de création du compte")

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Récupère un utilisateur par ID."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
            return self._row_to_user(row) if row else None

    def get_user_by_username(self, username: str) -> Optional[User]:
        """Récupère un utilisateur par nom d'utilisateur."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute(
                "SELECT * FROM users WHERE username = ?",
                (username.lower().strip(),)
            ).fetchone()
            return self._row_to_user(row) if row else None

    def _row_to_user(self, row: sqlite3.Row) -> User:
        """Convertit une ligne SQL en objet User."""
        return User(
            id=row["id"],
            username=row["username"],
            email=row["email"],
            display_name=row["display_name"],
            is_admin=bool(row["is_admin"]),
            is_active=bool(row["is_active"]),
            created_at=row["created_at"],
            last_login=row["last_login"]
        )

    def update_password(self, user_id: int, old_password: str, new_password: str) -> bool:
        """Change le mot de passe d'un utilisateur."""
        if len(new_password) < self.MIN_PASSWORD_LENGTH:
            raise AuthError("Nouveau mot de passe trop court")

        user = self.get_user_by_id(user_id)
        if not user:
            raise AuthError("Utilisateur introuvable")

        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                "SELECT password_hash FROM users WHERE id = ?", (user_id,)
            ).fetchone()

            if not self._verify_password(old_password, row[0]):
                raise AuthError("Ancien mot de passe incorrect")

            new_hash = self._hash_password(new_password)
            conn.execute(
                "UPDATE users SET password_hash = ? WHERE id = ?",
                (new_hash, user_id)
            )
            conn.commit()
            return True

    def delete_user(self, user_id: int) -> bool:
        """Supprime un utilisateur (et ses sessions via CASCADE)."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
            conn.commit()
            return cursor.rowcount > 0

    def list_users(self) -> list[User]:
        """Liste tous les utilisateurs."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute("SELECT * FROM users ORDER BY created_at DESC").fetchall()
            return [self._row_to_user(r) for r in rows]

    # ─── SESSIONS ────────────────────────────────────────────────────────────

    def login(self, username: str, password: str) -> Tuple[User, str]:
        """
        Authentifie un utilisateur et crée une session.
        Retourne (User, token_session).
        """
        user = self.get_user_by_username(username)

        if not user:
            raise AuthError("Nom d'utilisateur ou mot de passe incorrect")

        if not user.is_active:
            raise AuthError("Ce compte est désactivé")

        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                "SELECT password_hash FROM users WHERE id = ?", (user.id,)
            ).fetchone()

            if not self._verify_password(password, row[0]):
                raise AuthError("Nom d'utilisateur ou mot de passe incorrect")

            # Mettre à jour last_login
            conn.execute(
                "UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?",
                (user.id,)
            )

            # Créer une session
            token = secrets.token_urlsafe(32)
            expires_at = datetime.now() + timedelta(days=self.SESSION_DAYS)

            conn.execute(
                """INSERT INTO sessions (user_id, token, expires_at)
                   VALUES (?, ?, ?)""",
                (user.id, token, expires_at.isoformat())
            )
            conn.commit()

            return user, token

    def validate_session(self, token: str) -> Optional[User]:
        """Valide un token de session et retourne l'utilisateur."""
        if not token:
            return None

        now = datetime.now().isoformat()

        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row

            # Nettoyer les sessions expirées
            conn.execute("DELETE FROM sessions WHERE expires_at < ?", (now,))

            row = conn.execute(
                """SELECT s.user_id FROM sessions s
                   WHERE s.token = ? AND s.expires_at > ?""",
                (token, now)
            ).fetchone()

            if not row:
                conn.commit()
                return None

            # Rafraîchir la session
            new_expires = datetime.now() + timedelta(days=self.SESSION_DAYS)
            conn.execute(
                "UPDATE sessions SET expires_at = ? WHERE token = ?",
                (new_expires.isoformat(), token)
            )
            conn.commit()

            return self.get_user_by_id(row["user_id"])

    def logout(self, token: str) -> bool:
        """Déconnecte une session spécifique."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("DELETE FROM sessions WHERE token = ?", (token,))
            conn.commit()
            return cursor.rowcount > 0

    def logout_all(self, user_id: int) -> int:
        """Déconnecte toutes les sessions d'un utilisateur."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "DELETE FROM sessions WHERE user_id = ?", (user_id,)
            )
            conn.commit()
            return cursor.rowcount

    # ─── UTILITAIRES ─────────────────────────────────────────────────────────

    def has_users(self) -> bool:
        """Vérifie si au moins un utilisateur existe (pour le premier setup)."""
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute("SELECT COUNT(*) FROM users").fetchone()
            return row[0] > 0

    def create_first_admin(self, username: str, password: str) -> User:
        """Crée le premier compte admin (setup initial uniquement)."""
        if self.has_users():
            raise AuthError("Un utilisateur existe déjà")

        return self.create_user(
            username=username,
            password=password,
            is_admin=True,
            display_name="Administrateur"
        )

    def generate_default_admin_hash(self, password: str = "admin123") -> str:
        """Génère le hash pour l'admin par défaut (à utiliser dans les migrations SQL)."""
        return self._hash_password(password)

    # ─── DB INITIALIZATION ───────────────────────────────────────────────────

    def _ensure_db(self):
        """
        S'assure que les tables auth existent.
        CRUCIAL : crée le dossier parent AVANT sqlite3.connect.
        """
        db_file = Path(self.db_path)
        db_file.parent.mkdir(parents=True, exist_ok=True)

        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE,
                    password_hash TEXT NOT NULL,
                    display_name TEXT,
                    is_admin INTEGER DEFAULT 0,
                    is_active INTEGER DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                    token TEXT UNIQUE NOT NULL,
                    expires_at TIMESTAMP NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_sessions_token ON sessions(token)
            """)
            conn.commit()