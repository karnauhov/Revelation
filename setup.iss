#define MyAppName "Revelation"
#define MyAppCompany "Oleh Karnaukhov"
#define MyAppFileName "revelation.exe"
#define MyAppVersion "1.0.1"
#define MyAppBuild "40"
#define CurrentYear GetDateTimeString('yyyy', '', '')

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "ukrainian"; MessagesFile: "compiler:Languages\Ukrainian.isl"
Name: "russian"; MessagesFile: "compiler:Languages\Russian.isl"

[Setup]
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher="Oleh Karnaukhov"
AppPublisherURL="https://g.dev/karnaukhov"
AppCopyright="Copyright © {#CurrentYear} {#MyAppCompany}. All rights reserved"
DefaultDirName={pf}\{#MyAppName}
DefaultGroupName={#MyAppName}
OutputDir=build\windows
OutputBaseFilename={#MyAppName}-windows-{#MyAppVersion}-{#MyAppBuild}
Compression=lzma
SolidCompression=yes
SetupIconFile=_art\app_icon.ico
UninstallDisplayIcon={app}\app_icon.ico
VersionInfoCompany="Oleh Karnaukhov"
VersionInfoDescription="Revelation Study app."
VersionInfoProductName="{#MyAppName}"
VersionInfoProductVersion="{#MyAppVersion}.{#MyAppBuild}"
DisableDirPage=no
ShowLanguageDialog=yes

[Files]
Source: "build\windows\x64\runner\Release\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "_art\app_icon.ico"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppFileName}"; IconFilename: "{app}\app_icon.ico"

[Run]
Filename: "{app}\{#MyAppFileName}"; Description: "{cm:LaunchProgram,Revelation}"; Flags: nowait postinstall skipifsilent