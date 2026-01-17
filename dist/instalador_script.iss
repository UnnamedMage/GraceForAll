; --- CONFIGURACIÓN BÁSICA ---
[Setup]
AppName=GraceForAll
AppVersion=1.1
DefaultDirName={autopf}\GraceForAll
DefaultGroupName=GraceForAll
OutputDir=.
OutputBaseFilename=GraceForAll_1.1
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
Source: "build\GraceForAll.exe"; DestDir: "{autopf}\GraceForAll"; Flags: ignoreversion
Source: "assets\icons\GraceForAll.ico"; DestDir: "{autopf}\GraceForAll"; Flags: ignoreversion recursesubdirs

; Archivos de datos en AppData (NO se borrarán al desinstalar)
Source: "dist\default\backgrounds\*"; DestDir: "{localappdata}\GraceForAll\backgrounds"; Flags: onlyifdoesntexist uninsneveruninstall recursesubdirs
Source: "dist\default\databases\*"; DestDir: "{localappdata}\GraceForAll\databases"; Flags: onlyifdoesntexist uninsneveruninstall recursesubdirs

; --- CREAR ACCESO DIRECTO ---
[Icons]
Name: "{commondesktop}\GraceForAll"; Filename: "{autopf}\GraceForAll\GraceForAll.exe"; IconFilename: "{autopf}\GraceForAll\GraceForAll.ico"; WorkingDir: "{autopf}\GraceForAll"
Name: "{userprograms}\GraceForAll"; Filename: "{autopf}\GraceForAll\GraceForAll.exe"; WorkingDir: "{autopf}\GraceForAll"; IconFilename: "{autopf}\GraceForAll\GraceForAll.ico"