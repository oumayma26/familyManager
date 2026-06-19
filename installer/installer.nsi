; Family Manager Installer
!define APP_NAME "FamilyManager"
!define APP_VERSION "1.2.0"
!define APP_PUBLISHER "FamilyManager Team"
!define APP_EXE "FamilyManager.exe"

SetCompressor lzma
!include "MUI2.nsh"
!include "LogicLib.nsh"

Name "${APP_NAME} ${APP_VERSION}"
OutFile "../FamilyManager_Setup_1.2.0.exe"
InstallDir "$PROGRAMFILES64\${APP_NAME}"
RequestExecutionLevel admin

!define MUI_ICON "icon.ico"
!define MUI_UNICON "icon.ico"

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
    File "${APP_EXE}"
    
    File "icon.ico"
    
    CreateDirectory "$INSTDIR\photos"
    CreateDirectory "$INSTDIR\database"
    
    CreateDirectory "$SMPROGRAMS\${APP_NAME}"

    CreateShortcut "$SMPROGRAMS\${APP_NAME}\${APP_NAME}.lnk" "$INSTDIR\${APP_EXE}" "" "$INSTDIR\icon.ico" 0
    CreateShortcut "$DESKTOP\${APP_NAME}.lnk" "$INSTDIR\${APP_EXE}" "" "$INSTDIR\icon.ico" 0

    CreateShortcut "$SMPROGRAMS\${APP_NAME}\Désinstaller.lnk" "$INSTDIR\uninstall.exe"
    
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "DisplayName" "${APP_NAME}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "UninstallString" "$INSTDIR\uninstall.exe"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "DisplayVersion" "${APP_VERSION}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "Publisher" "${APP_PUBLISHER}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "DisplayIcon" "$INSTDIR\icon.ico"
    
    WriteUninstaller "$INSTDIR\uninstall.exe"
SectionEnd

Section "Uninstall"
    Delete "$SMPROGRAMS\${APP_NAME}\${APP_NAME}.lnk"
    Delete "$SMPROGRAMS\${APP_NAME}\Désinstaller.lnk"
    RMDir "$SMPROGRAMS\${APP_NAME}"
    Delete "$DESKTOP\${APP_NAME}.lnk"
    
    Delete "$INSTDIR\${APP_EXE}"
    Delete "$INSTDIR\uninstall.exe"
    Delete "$INSTDIR\icon.ico"
    
    MessageBox MB_YESNO "Supprimer les données (photos et base de données) ?" /SD IDNO IDYES delete_data IDNO skip_delete
    
    delete_data:
        RMDir /r "$INSTDIR\photos"
        RMDir /r "$INSTDIR\database"
        Goto continue_delete
    
    skip_delete:
        CreateDirectory "$DESKTOP\FamilyManager_Sauvegarde"
        CopyFiles "$INSTDIR\photos\*.*" "$DESKTOP\FamilyManager_Sauvegarde\photos\"
        CopyFiles "$INSTDIR\database\*.*" "$DESKTOP\FamilyManager_Sauvegarde\database\"
        MessageBox MB_OK "Données sauvegardées sur le Bureau"
    
    continue_delete:
    RMDir "$INSTDIR"
    DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}"
SectionEnd
