"""Archivo para funciones generales de todo el sistema"""

from pathlib import Path
import sys
from typing import Literal
from platformdirs import user_data_dir


def _find_project_root():
    current = Path(__file__).absolute()
    while current.parent != current:
        if (current / ".git").exists() or (current / "pyproject.toml").exists():
            return current
        current = current.parent
    return Path(__file__).parent  # Fallback


class PlatformPaths:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(
        self,
        app_name: str = "Unnamed",
        ext_approot_dev: list[str] = None,
        ext_appdata_dev: list[str] = None,
    ):
        if not hasattr(self, "_initialized"):
            self.app_name = app_name
            self.ext_approot = (
                ext_approot_dev if ext_approot_dev else ["seed_data", "app_root"]
            )
            self.ext_appdata = (
                ext_appdata_dev if ext_appdata_dev else ["seed_data", "app_data"]
            )
            self._initialized = True

    def get(self, *args, goto: Literal["intern", "approot", "appdata"]) -> Path:
        if getattr(sys, "frozen", False):  # Ejecutable empaquetado
            match goto:
                case "intern":
                    base_dir = sys._MEIPASS  # type: ignore
                case "approot":
                    base_dir = Path(sys.executable).parent
                case "appdata":
                    base_dir = Path(user_data_dir()) / self.app_name
        else:  # Desarrollo
            root = _find_project_root()
            match goto:
                case "intern":
                    base_dir = root
                case "approot":
                    base_dir = root.joinpath(*self.ext_approot)
                case "appdata":
                    base_dir = root.joinpath(*self.ext_appdata)
        base_dir.mkdir(parents=True, exist_ok=True)  # Asegura que el directorio exista
        if not args:
            return base_dir
        return base_dir.joinpath(*args)


def init_platform_path(
    app_name: str = "Unnamed",
    approot_dev: list[str] = None,
    appdata_dev: list[str] = None,
):
    """Inicializa el singleton (se llama en la configuración de la app)."""
    return PlatformPaths(app_name, approot_dev, appdata_dev)


def get_platform_path(goto: Literal["intern", "approot", "appdata"], *args):
    """Atajo global para pedir rutas."""
    instance = PlatformPaths()
    return instance.get(*args, goto=goto)
