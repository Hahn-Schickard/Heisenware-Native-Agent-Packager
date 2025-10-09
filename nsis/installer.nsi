!include MUI2.nsh

!define COMPANY_NAME "Heisenware GmbH"
!define PROGRAM_NAME "{SYNOPSIS}"
!define APP_NAME "{NAME}"
!define BINARY "{HEISENWARE_AGENT_BINARY}"
!define MUI_LICENSEPAGE_TEXT_TOP "{SYNOPSIS} \
{DESCRIPTION}"

Name "${COMPANY_NAME} ${PROGRAM_NAME} Installer Wizard"
OutFile "..\${APP_NAME}_Installer.exe"
InstallDir "$ProgramFiles\${PROGRAM_NAME}"

RequestExecutionLevel admin

!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "LICENSE"
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_LANGUAGE "English"

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

Section "Directory"
!define MUI_PAGE_HEADER_TEXT "Select your install location"

SetOutPath "$INSTDIR" 
SectionEnd

Section "Install"
SetOutPath $INSTDIR
File /r "..\$APP_NAME"
AccessControl::GrantOnFile \
    "$INSTDIR\$APP_NAME\$BINARY" \
    "(BU)" \ 
    "GenericRead + GenericWrite + GenericExecute + Delete"
Pop $0
SetShellVarContext all
SimpleSC::InstallService "{NAME}Service" "{SYNOPSIS} {DESCRIPTION}" "16" "2" "$INSTDIR\$APP_NAME\$BINARY" "" "" ""
Pop $0
WriteUninstaller $INSTDIR\uninstaller.exe
SectionEnd

Section "Uninstall"
SetShellVarContext all
RmDir /r "$INSTDIR\$APP_NAME"
Delete $INSTDIR\uninstaller.exe
RmDir $INSTDIR
SectionEnd
