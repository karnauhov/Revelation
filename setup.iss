#define MyAppName "Revelation"
#define MyAppCompany "AI11"
#define MyAppFileName "revelation.exe"
#define MyAppVersion "1.0.9"
#define MyAppBuild "181"
#define CurrentYear GetDateTimeString('yyyy', '', '')
#define MyAppCopyright "Copyright © 2024-" + CurrentYear + " " + MyAppCompany + ". All rights reserved."

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "ukrainian"; MessagesFile: "compiler:Languages\Ukrainian.isl"
Name: "russian"; MessagesFile: "compiler:Languages\Russian.isl"

[Setup]
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppCompany}
AppPublisherURL=https://ai11.link
AppCopyright={#MyAppCopyright}
DefaultDirName={commonpf}\{#MyAppName}
DefaultGroupName={#MyAppName}
OutputDir=build\windows
OutputBaseFilename={#MyAppName}-windows-{#MyAppVersion}-{#MyAppBuild}
Compression=lzma
SolidCompression=yes
SetupIconFile=_art\app_icon.ico
UninstallDisplayIcon={app}\app_icon.ico
VersionInfoCompany={#MyAppCompany}
VersionInfoCopyright={#MyAppCopyright}
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
