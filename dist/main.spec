# -*- mode: python ; coding: utf-8 -*-

import os
import sys
from pathlib import Path

# Obtener la ruta base del proyecto de manera alternativa
# Usamos sys.argv[0] que contiene la ruta al script que se está ejecutando
if getattr(sys, 'frozen', False):
    # Si estamos en modo ejecutable
    project_path = Path(sys.executable).parent
else:
    # Si estamos en modo construcción
    project_path = Path(sys.argv[0]).resolve().parent.parent

# Configuración principal
a = Analysis(
    # Ruta al script principal (ajusta según tu estructura)
    [os.path.join(project_path, 'src', 'main.py')],
    
    # Agregar la ruta del proyecto para que PyInstaller encuentre los módulos
    pathex=[str(project_path), str(project_path / 'src')],
    
    binaries=[],
    
    # Datos a incluir (formato: (origen, destino_en_el_ejecutable))
    datas=[
        (str(project_path / 'src' / 'ui'), 'ui'),
        (str(project_path / 'src' / 'Qtive'), 'Qtive'),
        (str(project_path / 'src' / 'core'), 'core'),
        (str(project_path / 'src' / 'common'), 'common'),
        (str(project_path / 'assets'), 'assets')
    ],
    
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='GraceForAll',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(project_path / 'assets' / 'design' /'GraceForAll.ico'),
)