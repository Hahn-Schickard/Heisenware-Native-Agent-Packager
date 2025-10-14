!include MUI2.nsh
!include LogicLib.nsh

!define PROGRAM_NAME "{NAME}"
!define PROGRAM_VERSION "{VERSION}"
!define UNINSTALL_REG_KEY "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PROGRAM_NAME}"

Name "{SYNOPSIS} Installer Wizard"
OutFile "..\{NAME}_Installer.exe"
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

Function SetRegistryKeys
    WriteRegStr HKLM "${UNINSTALL_REG_KEY}" "DisplayName" "{SYNOPSIS}"
    WriteRegStr HKLM "${UNINSTALL_REG_KEY}" "DisplayVersion" "${PROGRAM_VERSION}"
    WriteRegStr HKLM "${UNINSTALL_REG_KEY}" "InstallLocation" "$INSTDIR"
    WriteRegStr HKLM "${UNINSTALL_REG_KEY}" "UninstallString" "$INSTDIR\uninstall.exe"
FunctionEnd

!macro RemoveService un
  Function ${un}RemoveService
    SimpleSC::ExistsService "${PROGRAM_NAME}Service"
    Pop $0
    ${If} $0 == "0"
      SimpleSC::ServiceIsRunning "${PROGRAM_NAME}Service"
      Pop $0
      Pop $1
      ${If} $0 == "0"
        ${If} $1 == "1"
          ${If} ${Cmd} `MessageBox MB_OKCANCEL "${PROGRAM_NAME}Service is running. Stop and remove it?" IDOK`
            SimpleSC::StopService "${PROGRAM_NAME}Service" 1 60
            DetailPrint "${PROGRAM_NAME}Service stopped"
          ${Else}
            Abort
          ${EndIf}
        ${EndIf}
      ${EndIf}
      SimpleSC::RemoveService "${PROGRAM_NAME}Service"
      DetailPrint "${PROGRAM_NAME}Service removed"
    ${EndIf}
  FunctionEnd
!macroend

!insertmacro RemoveService "" 
!insertmacro RemoveService "un."

Function InstallService
  Call RemoveService
  SimpleSC::InstallService "${PROGRAM_NAME}Service" "{SYNOPSIS} {DESCRIPTION}" "16" "2" "$INSTDIR\{HEISENWARE_AGENT_BINARY}" "" "" ""
  Pop $0
  ${If} $0 != "0"
    Push $0
    SimpleSC::GetErrorMessage
    Pop $0
    ${If} ${Cmd} `MessageBox MB_OK "Failed to install ${PROGRAM_NAME}Service due to error $0" IDOK`
      Abort "Failed to install ${PROGRAM_NAME}Service due to error $0"
    ${EndIf}
  ${Else}
    DetailPrint "${PROGRAM_NAME}Service Installed"
  ${EndIf}
  SimpleSC::SetServiceFailure "${PROGRAM_NAME}Service" "0" "" "" "1" "60000" "2" "300000" "0" "0"
  Pop $0
  ${If} $0 != "0"
    Push $0
    SimpleSC::GetErrorMessage
    Pop $0
    ${If} ${Cmd} `MessageBox MB_OK "Failed to set restart policy for ${PROGRAM_NAME}Service due to error $0" IDOK`
      Abort "Failed to set restart policy for ${PROGRAM_NAME}Service due to error $0"
    ${EndIf}
  ${Else}
    DetailPrint "${PROGRAM_NAME}Service restart policy configured"
  ${EndIf}
  SimpleSC::StartService "${PROGRAM_NAME}Service" "" 60
  Pop $0
  ${If} $0 != "0"
    Push $0
    SimpleSC::GetErrorMessage
    Pop $0
    ${If} ${Cmd} `MessageBox MB_OK "Could not start ${PROGRAM_NAME}Service due to error $0" IDOK`
      Abort "Could not start ${PROGRAM_NAME}Service due to error $0"
    ${EndIf}
  ${Else}
    DetailPrint "${PROGRAM_NAME}Service started"
  ${EndIf}
FunctionEnd

!macro RemoveInstalled un
  Function ${un}RemoveInstalled
    Call ${un}RemoveService
    DeleteRegKey HKLM "${UNINSTALL_REG_KEY}"
    DetailPrint "Removed ${UNINSTALL_REG_KEY} WinRegKey"
    RmDir /r "$INSTDIR"
    Delete $INSTDIR\uninstaller.exe
    RmDir $INSTDIR
    DetailPrint "Removed $INSTDIR directory and it's content"
  FunctionEnd
!macroend

!insertmacro RemoveInstalled "" 
!insertmacro RemoveInstalled "un."

Function CleanInstall
  ${If} ${FileExists} "$INSTDIR\openssl"
    ${If} ${Cmd} `MessageBox MB_OKCANCEL "$INSTDIR\openssl already exists. Delete it?" IDOK`
      RMDir /r $INSTDIR\openssl
      DetailPrint "$INSTDIR\openssl folder deleted"
    ${Else}
      DetailPrint "Keeping old $INSTDIR\openssl folder"
    ${EndIf}
  ${EndIf}

  File /r openssl
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
