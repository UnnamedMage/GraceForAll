; --- CONFIGURACIÓN BÁSICA ---
[Setup]
AppName=GraceForAll
AppVersion=1.0
DefaultDirName={autopf}\GraceForAll
DefaultGroupName=GraceForAll
OutputDir=.
OutputBaseFilename=GraceForAll_1.0
Compression=lzma2
SolidCompression=yes
PrivilegesRequired=admin
AllowNoIcons=yes
DisableDirPage=yes
UninstallFilesDir={autopf}\GraceForAll\Uninstall
UninstallDisplayIcon={autopf}\GraceForAll\GraceForAll.exe

; --- ARCHIVOS QUE SE INSTALARÁN ---
[Files]
; Archivos del programa (se borrarán al desinstalar)
Source: "dist\GraceForAll.exe"; DestDir: "{autopf}\GraceForAll"; Flags: ignoreversion
Source: "assets\design\GraceForAll.ico"; DestDir: "{autopf}\GraceForAll"; Flags: ignoreversion recursesubdirs

; Archivos de datos en AppData (NO se borrarán al desinstalar)
Source: "assets\backgrounds\*"; DestDir: "{localappdata}\GraceForAll\backgrounds"; Flags: onlyifdoesntexist uninsneveruninstall recursesubdirs
Source: "assets\databases\*"; DestDir: "{localappdata}\GraceForAll\databases"; Flags: onlyifdoesntexist uninsneveruninstall recursesubdirs
Source: "assets\config.json"; DestDir: "{localappdata}\GraceForAll"; Flags: onlyifdoesntexist uninsneveruninstall recursesubdirs

; --- CREAR ACCESO DIRECTO ---
[Icons]
Name: "{commondesktop}\GraceForAll"; Filename: "{autopf}\GraceForAll\GraceForAll.exe"; IconFilename: "{autopf}\GraceForAll\GraceForAll.ico"; WorkingDir: "{autopf}\GraceForAll"
Name: "{userprograms}\GraceForAll"; Filename: "{autopf}\GraceForAll\GraceForAll.exe"; WorkingDir: "{autopf}\GraceForAll"; IconFilename: "{autopf}\GraceForAll\GraceForAll.ico"