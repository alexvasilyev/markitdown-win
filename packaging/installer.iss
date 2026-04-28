; Inno Setup script for MarkItDown GUI
;
; Prerequisite: build the bundle first from the project root:
;     pyinstaller packaging/markitdown_gui.spec
; Then compile this script with Inno Setup 6 (iscc.exe packaging\installer.iss).

#define MyAppName     "MarkItDown GUI"
#define MyAppVersion  "0.1.0"
#define MyAppPublisher "Your Name"
#define MyAppExeName  "MarkItDownGUI.exe"

[Setup]
; Generate a fresh GUID with Inno Setup's Tools menu before publishing.
AppId={{8B5C0A4E-2E4B-4D1A-9C0F-MARKITDOWN0001}}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\MarkItDownGUI
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
OutputDir=..\dist\installer
OutputBaseFilename=MarkItDownGUI-Setup-{#MyAppVersion}
Compression=lzma
SolidCompression=yes
WizardStyle=modern
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop shortcut"; GroupDescription: "Additional icons:"; Flags: unchecked

[Files]
Source: "..\dist\MarkItDownGUI\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Launch {#MyAppName}"; Flags: nowait postinstall skipifsilent
