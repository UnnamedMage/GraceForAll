from pathlib import Path
import subprocess
import sys

# Ruta del archivo actual: tools/build_resources.py
TOOLS_DIR = Path(__file__).resolve().parent

# Subimos a la raíz del proyecto
PROJECT_ROOT = TOOLS_DIR.parent

# Entramos a src
SRC_DIR = PROJECT_ROOT / "src"

QRC_FILE = SRC_DIR / "resources.qrc"
OUTPUT_FILE = SRC_DIR / "resources_rc.py"

if not QRC_FILE.exists():
    print(f"❌ No se encontró {QRC_FILE}")
    sys.exit(1)

print("🔄 Compilando recursos Qt...")
subprocess.run(
    [
        "pyside6-rcc",
        str(QRC_FILE),
        "-o",
        str(OUTPUT_FILE),
    ],
    check=True,
)

print("✅ Recursos compilados correctamente")
