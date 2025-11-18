Unicode True

!include MUI2.nsh
!include LogicLib.nsh

!define MUI_ICON "hw-logo.ico"
!define MUI_UNICON "hw-logo.ico"
!define MUI_WELCOMEFINISHPAGE_BITMAP "hw-banner.bmp"
!define MUI_UNWELCOMEFINISHPAGE_BITMAP "hw-banner.bmp"
!define PROGRAM_NAME "{NAME}"
!define PROGRAM_VERSION "{VERSION}"
!define UNINSTALL_REG_KEY "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PROGRAM_NAME}"
!define EXEC_TIMEOUT "10000" ; measured in ms

Name "{SYNOPSIS} Installer Wizard"
OutFile "..\{NAME}_installer.exe"
InstallDir "$ProgramFiles\${PROGRAM_NAME}"
InstallDirRegKey HKLM "${UNINSTALL_REG_KEY}" InstallLocation
RequestExecutionLevel admin

!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "LICENSE"
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_LANGUAGE "English"

Var PrevVersion

Page Directory DirectoryHeader
Page InstFiles InstallHeader

Function DirectoryHeader
  !insertmacro MUI_HEADER_TEXT "Installation location" \
    "Please select the location where the files should be installed"
FunctionEnd

Function InstallHeader
  !insertmacro MUI_HEADER_TEXT \
    "Installing files" \
    "Your files are currently being installed"
FunctionEnd

Function .onInit
    ReadRegStr $PrevVersion HKLM "${UNINSTALL_REG_KEY}" "DisplayVersion"
    ${IfNot} ${Errors}
        ${If} $PrevVersion == ""
            StrCpy $0 "It seems ${PROGRAM_NAME} is already installed. Do you want to re-install version ${PROGRAM_VERSION}?"
        ${ElseIf} $PrevVersion == ${PROGRAM_VERSION}
            StrCpy $0 "It seems ${PROGRAM_NAME} $PrevVersion is already installed. Do you want to re-install it?"
        ${Else}
            StrCpy $0 "It seems ${PROGRAM_NAME} is already installed at version $PrevVersion. Do you want to update to ${PROGRAM_VERSION}?"
        ${EndIf}
        ${If} ${Cmd} `MessageBox MB_YESNO|MB_ICONQUESTION "$0" /SD IDYES IDNO`
            Abort
        ${EndIf}
    ${EndIf}
FunctionEnd

Function isInRoot
  DetailPrint "Checking if installation path is inside disk root"
    ; get disk root path
  StrCpy $R0 $INSTDIR 3

  ; check if disk root matches INSTDIR
  StrCmp $R0 "$INSTDIR" 0 +2
    Abort "Installing in disk root is not allowed. Please create a new folder inside $R0"
FunctionEnd

!macro checkInstPath Path
  StrCmp $INSTDIR "${Path}" 0 +3
    MessageBox MB_OK "Installing in ${Path} is not allowed! Please create a new folder inside"
    Abort "Installing in ${Path} is not allowed!"
!macroend

Function isInBadPath
  DetailPrint "Checking if installation path is inside a blacklisted path"

  ; NSIS does not have arrays, and using StrTok is clumsy and unreliable
  !insertmacro checkInstPath "$SYSDIR"
  !insertmacro checkInstPath "$WINDIR"
  !insertmacro checkInstPath "$PROGRAMFILES"
  !insertmacro checkInstPath "$PROGRAMFILES64"
  !insertmacro checkInstPath "$DESKTOP"
  !insertmacro checkInstPath "$DOCUMENTS"
  !insertmacro checkInstPath "$MUSIC"
  !insertmacro checkInstPath "$PICTURES"
  !insertmacro checkInstPath "$VIDEOS"
  !insertmacro checkInstPath "$APPDATA"
  !insertmacro checkInstPath "$LOCALAPPDATA"
FunctionEnd

Function SetRegistryKeys
    WriteRegStr HKLM "${UNINSTALL_REG_KEY}" "DisplayName" "${PROGRAM_NAME}"
    WriteRegStr HKLM "${UNINSTALL_REG_KEY}" "DisplayVersion" "${PROGRAM_VERSION}"
    WriteRegStr HKLM "${UNINSTALL_REG_KEY}" "InstallLocation" "$INSTDIR"
    WriteRegStr HKLM "${UNINSTALL_REG_KEY}" "UninstallString" "$INSTDIR\uninstaller.exe"
FunctionEnd

!macro makeRemoveService un
  Function ${un}RemoveService
    DetailPrint "Stopping and removing ${PROGRAM_NAME}Service"
    ; Use nssm status to check service state
    ; 5 = SERVICE_NOT_FOUND
    nsExec::ExecToStack '/TIMEOUT=${EXEC_TIMEOUT}' \
      '"$INSTDIR\nssm.exe" status "${PROGRAM_NAME}Service"'
    Pop $0
    Pop $1

    ${If} $0 != 3 ; If service exists (is not "not found")
      DetailPrint '$1'
      ; Check if service is running (status == 0)
      ${If} $0 == 0
        ${If} ${Cmd} `MessageBox MB_OKCANCEL "${PROGRAM_NAME}Service is running. Stop and remove it?" IDOK`
          nsExec::ExecToStack '/TIMEOUT=${EXEC_TIMEOUT}' \
            '"$INSTDIR\nssm.exe" stop "${PROGRAM_NAME}Service"'
          Pop $0
          Pop $1
          DetailPrint "$1"
        ${Else}
          Abort "Keeping old files and aborting installation"
        ${EndIf}
      ${EndIf}

      ; Remove the service
      nsExec::ExecToStack '/TIMEOUT=${EXEC_TIMEOUT}' \
        '"$INSTDIR\nssm.exe" remove "${PROGRAM_NAME}Service" confirm'
      Pop $0
      Pop $1
      DetailPrint "$1"
    ${EndIf}
  FunctionEnd
!macroend

!insertmacro makeRemoveService ""
!insertmacro makeRemoveService "un."

!macro makeRemoveInstalled un
  Function ${un}RemoveInstalled
    Call ${un}RemoveService
    DeleteRegKey HKLM "${UNINSTALL_REG_KEY}"
    DetailPrint "Removed ${UNINSTALL_REG_KEY} WinRegKey"
    RmDir /r $INSTDIR\openssl
    DetailPrint "Removed $INSTDIR\openssl folder"
    Delete $INSTDIR\nssm.exe
    DetailPrint "Removed $INSTDIR\nssm.exe"
    Delete $INSTDIR\uninstaller.exe
    DetailPrint "Removed $INSTDIR\uninstaller.exe"
    SetOutPath "$TEMP"
    RmDir /r $INSTDIR
    DetailPrint "Removed $INSTDIR directory and it's content"
  FunctionEnd
!macroend

!insertmacro makeRemoveInstalled ""
!insertmacro makeRemoveInstalled "un."

!macro AbortOnError AbortMsg SuccessMsg
  Pop $0
  ${If} $0 == "1"
    Sleep 3000 ; initial start can take some time, so we check again
    nsExec::ExecToStack '/TIMEOUT=${EXEC_TIMEOUT}' \
      '"$INSTDIR\nssm.exe" status "${PROGRAM_NAME}Service"'
    Pop $0
    ${If} $0 != "0"
      Pop $1
      MessageBox MB_OK "${AbortMsg}$\r$\nExit code: $0$\r$\nError: $1"
      Call RemoveInstalled
      Abort "${AbortMsg}"
    ${EndIf}
  ${Else}
    DetailPrint "${SuccessMsg}"
  ${EndIf}
!macroend

Function InstallService
  Call RemoveService ; This will remove any old service
  ; Install the service using nssm
  nsExec::ExecToStack '/TIMEOUT=${EXEC_TIMEOUT}' \
    '"$INSTDIR\nssm.exe" install "${PROGRAM_NAME}Service" "$INSTDIR\{HEISENWARE_AGENT_BINARY}"'
  !insertmacro AbortOnError \
    "Failed to install ${PROGRAM_NAME}Service due to error" \
    "${PROGRAM_NAME}Service Installed"

  ; Set Service Description (the "Description" column in services.msc)
  nsExec::Exec '/TIMEOUT=${EXEC_TIMEOUT}' \
    '"$INSTDIR\nssm.exe" set "${PROGRAM_NAME}Service" Description "{DESCRIPTION}"'

  ; Set Service Work directory
  nsExec::Exec '/TIMEOUT=${EXEC_TIMEOUT}' \
    '"$INSTDIR\nssm.exe" set "${PROGRAM_NAME}Service" AppDirectory "$INSTDIR"'

  nsExec::Exec '/TIMEOUT=${EXEC_TIMEOUT}' \
    '"$INSTDIR\nssm.exe" set "${PROGRAM_NAME}Service" Start SERVICE_AUTO_START'
    
  nsExec::Exec '/TIMEOUT=${EXEC_TIMEOUT}' \
    '"$INSTDIR\nssm.exe" set "${PROGRAM_NAME}Service" Type SERVICE_WIN32_OWN_PROCESS'

  nsExec::Exec '/TIMEOUT=${EXEC_TIMEOUT}' \
    '"$INSTDIR\nssm.exe" set "${PROGRAM_NAME}Service" ObjectName LocalSystem'

  nsExec::Exec '/TIMEOUT=${EXEC_TIMEOUT}' \
    '"$INSTDIR\nssm.exe" set "${PROGRAM_NAME}Service" AppExit Default Restart'
  nsExec::Exec '/TIMEOUT=${EXEC_TIMEOUT}' \
    '"$INSTDIR\nssm.exe" set "${PROGRAM_NAME}Service" AppRestartDelay 10000'
  DetailPrint "${PROGRAM_NAME}Service restart policy configured"

  ; Set up StdOut and StdError logging
  nsExec::Exec '/TIMEOUT=${EXEC_TIMEOUT}' \
    '"$INSTDIR\nssm.exe" set "${PROGRAM_NAME}Service" AppStdout $INSTDIR\logs\service.log'
  nsExec::Exec '/TIMEOUT=${EXEC_TIMEOUT}' \
    '"$INSTDIR\nssm.exe" set "${PROGRAM_NAME}Service" AppStderr $INSTDIR\logs\service.log'
  ; Enable log file rotation 
  nsExec::Exec '/TIMEOUT=${EXEC_TIMEOUT}' \
    '"$INSTDIR\nssm.exe" set "${PROGRAM_NAME}Service" AppRotateFiles 1'
  ; Rotate log files while service is running
  nsExec::Exec '/TIMEOUT=${EXEC_TIMEOUT}' \
    '"$INSTDIR\nssm.exe" set "${PROGRAM_NAME}Service" AppRotateOnline 1'
  ; Rotate log files when log file is larger than 20 MB
  nsExec::Exec '/TIMEOUT=${EXEC_TIMEOUT}' \
    '"$INSTDIR\nssm.exe" set "${PROGRAM_NAME}Service" AppRotateBytes 20971520'
  DetailPrint "${PROGRAM_NAME}Service logging policy configured"

  ; Start the service
  nsExec::ExecToStack '/TIMEOUT=${EXEC_TIMEOUT}' \
    '"$INSTDIR\nssm.exe" start "${PROGRAM_NAME}Service"'
  !insertmacro AbortOnError \
    "Could not start ${PROGRAM_NAME}Service due to error" \
    "${PROGRAM_NAME}Service started"
FunctionEnd

Function CleanInstall
  Call isInRoot
  Call isInBadPath

  ${IfNot} ${FileExists} "$INSTDIR\logs"
    CreateDirectory "$INSTDIR\logs"
    DetailPrint "Created $INSTDIR\logs folder"
  ${EndIf}

  ${If} ${FileExists} "$INSTDIR\openssl"
    ${If} ${Cmd} `MessageBox MB_OKCANCEL "$INSTDIR\openssl already exists. Delete it?" IDOK`
      RMDir /r $INSTDIR\openssl
      DetailPrint "$INSTDIR\openssl folder deleted"
    ${Else}
      DetailPrint "Keeping old $INSTDIR\openssl folder"
    ${EndIf}
  ${EndIf}

  ${If} ${FileExists} "$INSTDIR\nssm.exe"
    Delete "$INSTDIR\nssm.exe"
    DetailPrint "Deleted original $INSTDIR\nssm.exe"
  ${EndIf}

  File /r openssl
  File nssm.exe
  File "{HEISENWARE_AGENT_BINARY}"
  SetShellVarContext all
  WriteUninstaller $INSTDIR\uninstaller.exe
  Call InstallService
  Call SetRegistryKeys
FunctionEnd

Function UpdateInstalled
  Call RemoveInstalled
  Call CleanInstall
FunctionEnd

Section "Directory"
!define MUI_PAGE_HEADER_TEXT "Select your install location"

SetOutPath "$INSTDIR"
SectionEnd

Section "Install"
  ${If} $PrevVersion == ""
    DetailPrint "Performing a fresh installation"
    Call CleanInstall
  ${Else}
    DetailPrint "Updating from version $PrevVersion to ${PROGRAM_VERSION}"
    Call UpdateInstalled
  ${EndIf}
SectionEnd

Section "Uninstall"
  Call un.RemoveInstalled
SectionEnd
