#!/usr/bin/env python3
"""
Script de build pour Family Manager (Windows)
Génère : .exe autonome + installateur NSIS + update.json
Tout est automatisé, aucune commande manuelle requise.
"""

import os
import sys
import shutil
import subprocess
import importlib.util
import urllib.request
import zipfile
import json
import hashlib
from pathlib import Path
from datetime import datetime


# ==================== CONFIGURATION ====================

APP_NAME = "FamilyManager"
APP_VERSION = "1.2.0"  # ← Bump ici
APP_PUBLISHER = "FamilyManager Team"
MAIN_SCRIPT = "main.py"
ICON_PATH = "assets/icon/islam.ico"

# URL de base où seront hébergés les fichiers (à adapter)
UPDATE_BASE_URL = "https://ton-site.com/downloads"

NSIS_URL = "https://sourceforge.net/projects/nsis/files/NSIS%203/3.10/nsis-3.10.zip/download"
NSIS_LOCAL_ZIP = "nsis.zip"
NSIS_EXTRACT_DIR = "nsis_portable"


# ==================== UTILITAIRES ====================

def print_step(step_num, total, title):
    print(f"\n{'='*60}")
    print(f"  Étape {step_num}/{total} : {title}")
    print(f"{'='*60}")


def run_command(cmd, description, cwd=None, timeout=300):
    print(f"\n   ▶ {description}")
    cmd_str = ' '.join(str(c) for c in cmd)
    print(f"     {cmd_str[:100]}{'...' if len(cmd_str) > 100 else ''}")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd, timeout=timeout)
    except subprocess.TimeoutExpired:
        print(f"   ⏱️  Timeout après {timeout}s")
        return False, "Timeout"
    except Exception as e:
        print(f"   ❌ Exception : {e}")
        return False, str(e)
    
    if result.returncode != 0:
        print(f"   ❌ ERREUR (code {result.returncode})")
        if result.stderr and len(result.stderr) < 800:
            print(f"   {result.stderr[:500]}")
        return False, result.stderr
    
    print(f"   ✅ OK")
    return True, result.stdout


def ensure_module(module_name, pip_name=None):
    if pip_name is None:
        pip_name = module_name
    
    spec = importlib.util.find_spec(module_name)
    if spec is not None:
        return True
    
    print(f"   📦 Installation de {pip_name}...")
    success, _ = run_command([sys.executable, "-m", "pip", "install", pip_name, "--quiet"], f"pip install {pip_name}")
    return success


def find_nsis():
    paths = [
        r"C:\Program Files (x86)\NSIS\makensis.exe",
        r"C:\Program Files\NSIS\makensis.exe",
        Path(NSIS_EXTRACT_DIR) / "nsis-3.10" / "makensis.exe",
        Path(NSIS_EXTRACT_DIR) / "makensis.exe",
    ]
    
    for p in paths:
        if Path(p).exists():
            return str(p)
    
    found = shutil.which("makensis")
    if found:
        return found
    
    return None


def download_nsis_portable():
    print(f"\n   📥 Téléchargement de NSIS portable...")
    
    nsis_dir = Path(NSIS_EXTRACT_DIR)
    if nsis_dir.exists():
        exe_path = nsis_dir / "nsis-3.10" / "makensis.exe"
        if exe_path.exists():
            print(f"   ✅ NSIS portable déjà présent")
            return str(exe_path)
        exe_path = nsis_dir / "makensis.exe"
        if exe_path.exists():
            return str(exe_path)
    
    try:
        print(f"   ⬇️  Téléchargement depuis SourceForge...")
        urllib.request.urlretrieve(NSIS_URL, NSIS_LOCAL_ZIP)
        print(f"   ✅ Téléchargé : {NSIS_LOCAL_ZIP}")
        
        print(f"   📂 Extraction...")
        with zipfile.ZipFile(NSIS_LOCAL_ZIP, 'r') as z:
            z.extractall(NSIS_EXTRACT_DIR)
        
        Path(NSIS_LOCAL_ZIP).unlink(missing_ok=True)
        
        exe_path = nsis_dir / "nsis-3.10" / "makensis.exe"
        if exe_path.exists():
            print(f"   ✅ NSIS prêt : {exe_path}")
            return str(exe_path)
        
        return None
        
    except Exception as e:
        print(f"   ❌ Erreur : {e}")
        return None


def install_nsis():
    print(f"\n   🔧 NSIS non trouvé — tentative d'installation...")
    
    print(f"   📌 Méthode 1 : winget...")
    success, _ = run_command(["winget", "install", "NSIS.NSIS", "--silent", "--accept-package-agreements"], "winget install NSIS", timeout=60)
    if success:
        nsis = find_nsis()
        if nsis:
            return nsis
    
    print(f"   📌 Méthode 2 : Chocolatey...")
    success, _ = run_command(["powershell", "-Command", "choco install nsis -y"], "choco install NSIS", timeout=60)
    if success:
        nsis = find_nsis()
        if nsis:
            return nsis
    
    print(f"   📌 Méthode 3 : Téléchargement portable...")
    nsis = download_nsis_portable()
    if nsis:
        return nsis
    
    return None


# ==================== GÉNÉRATION UPDATE.JSON ====================

def compute_sha256(filepath: Path) -> str:
    """Calcule le SHA-256 d'un fichier"""
    h = hashlib.sha256()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            h.update(chunk)
    return h.hexdigest()


def generate_update_json(exe_path: Path, release_notes: str = "", mandatory: bool = False) -> Path:
    """
    Génère le fichier update.json pour l'auto-updater.
    Doit être uploadé sur le serveur avec le .exe
    """
    print(f"\n   📝 Génération de update.json...")
    
    if not exe_path.exists():
        print(f"   ❌ Exécutable non trouvé : {exe_path}")
        return None
    
    checksum = compute_sha256(exe_path)
    size = exe_path.stat().st_size
    
    update_data = {
        "version": APP_VERSION,
        "url": f"{UPDATE_BASE_URL}/{exe_path.name}",
        "checksum": checksum,
        "size_bytes": size,
        "release_notes": release_notes,
        "min_version": "1.0.0",
        "mandatory": mandatory,
        "published_at": datetime.now().isoformat()
    }
    
    output = Path("update.json")
    output.write_text(json.dumps(update_data, indent=2), encoding='utf-8')
    
    print(f"   ✅ {output.name} généré")
    print(f"   📦 Version : {APP_VERSION}")
    print(f"   🔐 SHA-256 : {checksum[:16]}...")
    print(f"   📊 Taille : {size / 1024 / 1024:.1f} Mo")
    
    return output


# ==================== ÉTAPES DE BUILD ====================

def clean_build():
    dirs = ["build", "dist", f"{APP_NAME}.spec", "installer"]
    for d in dirs:
        path = Path(d)
        if path.exists():
            if path.is_dir():
                shutil.rmtree(path)
            else:
                path.unlink()
            print(f"   🗑️  {d}")


def prepare_assets():
    Path("assets").mkdir(exist_ok=True)
    has_icon = Path(ICON_PATH).exists()
    if not has_icon:
        print(f"   ℹ️  Pas d'icône personnalisée (optionnel)")
    return has_icon


def build_executable():
    if not ensure_module("PyInstaller", "pyinstaller"):
        print("❌ PyInstaller indisponible")
        sys.exit(1)
    
    cmd = [sys.executable, "-m", "PyInstaller", "--name", APP_NAME, "--onefile", "--windowed", "--clean", "--noconfirm"]
    
    if Path(ICON_PATH).exists():
        cmd.extend(["--icon", ICON_PATH])
    
    cmd.extend([
        "--hidden-import", "PySide6.QtCore",
        "--hidden-import", "PySide6.QtGui",
        "--hidden-import", "PySide6.QtWidgets",
        "--hidden-import", "sqlite3",
        "--hidden-import", "database.migrations.runner",
        "--hidden-import", "core.auth_service",
        "--hidden-import", "core.auth_manager",
    ])
    
    cmd.append(MAIN_SCRIPT)
    
    success, _ = run_command(cmd, "Compilation PyInstaller", timeout=300)
    
    if not success:
        print("\n❌ Build échoué !")
        sys.exit(1)


def create_installer_script(has_icon):
    """Génère le script NSIS — icône optionnelle"""
    installer_dir = Path("installer")
    installer_dir.mkdir(exist_ok=True)
    
    exe_source = Path("dist") / f"{APP_NAME}.exe"
    exe_dest = installer_dir / f"{APP_NAME}.exe"
    
    if not exe_source.exists():
        print(f"❌ Exécutable non trouvé : {exe_source}")
        sys.exit(1)
    
    shutil.copy2(exe_source, exe_dest)
    
    icon_define = ""
    icon_shortcuts = ""
    
    if has_icon:
        icon_define = '''
!define MUI_ICON "icon.ico"
!define MUI_UNICON "icon.ico"
'''
        icon_shortcuts = f'''
    CreateShortcut "$SMPROGRAMS\\${{APP_NAME}}\\${{APP_NAME}}.lnk" "$INSTDIR\\${{APP_EXE}}" "" "$INSTDIR\\icon.ico" 0
    CreateShortcut "$DESKTOP\\${{APP_NAME}}.lnk" "$INSTDIR\\${{APP_EXE}}" "" "$INSTDIR\\icon.ico" 0
'''
        shutil.copy2(ICON_PATH, installer_dir / "icon.ico")
    else:
        icon_shortcuts = f'''
    CreateShortcut "$SMPROGRAMS\\${{APP_NAME}}\\${{APP_NAME}}.lnk" "$INSTDIR\\${{APP_EXE}}"
    CreateShortcut "$DESKTOP\\${{APP_NAME}}.lnk" "$INSTDIR\\${{APP_EXE}}"
'''
    
    nsi = installer_dir / "installer.nsi"
    nsi.write_text(f'''; Family Manager Installer
!define APP_NAME "{APP_NAME}"
!define APP_VERSION "{APP_VERSION}"
!define APP_PUBLISHER "{APP_PUBLISHER}"
!define APP_EXE "{APP_NAME}.exe"

SetCompressor lzma
!include "MUI2.nsh"
!include "LogicLib.nsh"

Name "${{APP_NAME}} ${{APP_VERSION}}"
OutFile "../{APP_NAME}_Setup_{APP_VERSION}.exe"
InstallDir "$PROGRAMFILES64\\${{APP_NAME}}"
RequestExecutionLevel admin
{icon_define}
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "license.txt"
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_WELCOME
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_UNPAGE_FINISH

!insertmacro MUI_LANGUAGE "French"

Section "Install"
    SetOutPath "$INSTDIR"
    File "${{APP_EXE}}"
    
    File "icon.ico"
    
    CreateDirectory "$INSTDIR\\photos"
    CreateDirectory "$INSTDIR\\database"
    
    CreateDirectory "$SMPROGRAMS\\${{APP_NAME}}"
{icon_shortcuts}
    CreateShortcut "$SMPROGRAMS\\${{APP_NAME}}\\Désinstaller.lnk" "$INSTDIR\\uninstall.exe"
    
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APP_NAME}}" "DisplayName" "${{APP_NAME}}"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APP_NAME}}" "UninstallString" "$INSTDIR\\uninstall.exe"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APP_NAME}}" "DisplayVersion" "${{APP_VERSION}}"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APP_NAME}}" "Publisher" "${{APP_PUBLISHER}}"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APP_NAME}}" "DisplayIcon" "$INSTDIR\\icon.ico"
    
    WriteUninstaller "$INSTDIR\\uninstall.exe"
SectionEnd

Section "Uninstall"
    Delete "$SMPROGRAMS\\${{APP_NAME}}\\${{APP_NAME}}.lnk"
    Delete "$SMPROGRAMS\\${{APP_NAME}}\\Désinstaller.lnk"
    RMDir "$SMPROGRAMS\\${{APP_NAME}}"
    Delete "$DESKTOP\\${{APP_NAME}}.lnk"
    
    Delete "$INSTDIR\\${{APP_EXE}}"
    Delete "$INSTDIR\\uninstall.exe"
    Delete "$INSTDIR\\icon.ico"
    
    MessageBox MB_YESNO "Supprimer les données (photos et base de données) ?" /SD IDNO IDYES delete_data IDNO skip_delete
    
    delete_data:
        RMDir /r "$INSTDIR\\photos"
        RMDir /r "$INSTDIR\\database"
        Goto continue_delete
    
    skip_delete:
        CreateDirectory "$DESKTOP\\{APP_NAME}_Sauvegarde"
        CopyFiles "$INSTDIR\\photos\\*.*" "$DESKTOP\\{APP_NAME}_Sauvegarde\\photos\\"
        CopyFiles "$INSTDIR\\database\\*.*" "$DESKTOP\\{APP_NAME}_Sauvegarde\\database\\"
        MessageBox MB_OK "Données sauvegardées sur le Bureau"
    
    continue_delete:
    RMDir "$INSTDIR"
    DeleteRegKey HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APP_NAME}}"
SectionEnd
''', encoding="utf-8")
    
    license_file = installer_dir / "license.txt"
    license_file.write_text(f"""Family Manager v{APP_VERSION}

Copyright (c) 2024 {APP_PUBLISHER}
Usage personnel gratuit.
""", encoding="utf-8")
    
    return nsi


def build_installer(has_icon):
    nsis_path = find_nsis()
    
    if not nsis_path:
        print(f"\n   🔧 NSIS non trouvé — tentative d'installation...")
        nsis_path = install_nsis()
    
    if not nsis_path:
        print(f"\n   ❌ NSIS indisponible. Installateur non généré.")
        print(f"   💡 Installez NSIS manuellement : https://nsis.sourceforge.io/Download")
        return False
    
    print(f"\n   ✅ NSIS : {nsis_path}")
    
    nsi_script = create_installer_script(has_icon)
    
    success, output = run_command([nsis_path, str(nsi_script)], "Compilation NSIS")
    
    if not success:
        print(f"\n   ❌ Détail de l'erreur NSIS :")
        print(f"   {output[-500:] if len(output) > 500 else output}")
        return False
    
    installer = Path(f"{APP_NAME}_Setup_{APP_VERSION}.exe")
    if installer.exists():
        size_mb = installer.stat().st_size / (1024 * 1024)
        print(f"   ✅ Installateur : {installer.name} ({size_mb:.1f} Mo)")
        return True
    
    return False


def show_summary():
    print(f"\n{'='*60}")
    print("  ✅ BUILD TERMINÉ !")
    print(f"{'='*60}")
    
    portable = Path("dist") / f"{APP_NAME}.exe"
    installer = Path(f"{APP_NAME}_Setup_{APP_VERSION}.exe")
    update_json = Path("update.json")
    
    print("\n📁 Fichiers générés :\n")
    
    if portable.exists():
        size = portable.stat().st_size / (1024 * 1024)
        print(f"   📌 PORTABLE")
        print(f"      {portable}")
        print(f"      {size:.1f} Mo")
    
    if installer.exists():
        size = installer.stat().st_size / (1024 * 1024)
        print(f"\n   📌 INSTALLATEUR (recommandé)")
        print(f"      {installer}")
        print(f"      {size:.1f} Mo")
    
    if update_json.exists():
        print(f"\n   📌 MISE À JOUR")
        print(f"      {update_json}")
        print(f"      À uploader sur : {UPDATE_BASE_URL}/")
    
    print(f"\n🚀 Pour distribuer :")
    if installer.exists():
        print(f"   → Uploadez '{installer.name}' et 'update.json' sur {UPDATE_BASE_URL}/")
    else:
        print(f"   → Zippez le dossier 'dist/' et distribuez")


# ==================== MAIN ====================

def main():
    print(f"{'='*60}")
    print(f"  Build {APP_NAME} v{APP_VERSION}")
    print(f"  Python : {sys.executable}")
    print(f"{'='*60}")
    
    if not Path(MAIN_SCRIPT).exists():
        print(f"\n❌ {MAIN_SCRIPT} introuvable !")
        sys.exit(1)
    
    print_step(1, 5, "Nettoyage")
    clean_build()
    
    print_step(2, 5, "Préparation des assets")
    has_icon = prepare_assets()
    
    print_step(3, 5, "Build de l'exécutable")
    build_executable()
    
    print_step(4, 5, "Création de l'installateur")
    build_installer(has_icon)
    
    print_step(5, 5, "Génération update.json")
    exe_path = Path("dist") / f"{APP_NAME}.exe"
    generate_update_json(
        exe_path=exe_path,
        release_notes=(
            "🔐 Nouveau : Système d'authentification\n"
            "- Login sécurisé avec sessions persistantes\n"
            "- Gestion des utilisateurs (admin)\n"
            "- Migration automatique de la base de données"
        ),
        mandatory=True  # ← Cette version est obligatoire (schéma incompatible)
    )
    
    print_step(5, 5, "Résumé")  # Réutilise 5 car c'est le dernier
    show_summary()


if __name__ == "__main__":
    main()