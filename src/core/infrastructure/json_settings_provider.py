from ..domain.settings_provider import SettingsProvider
import json
from src.common import get_platform_path
from typing import Any


class JSONSettingsProvider(SettingsProvider):
    def __init__(self):
        self._appdata_path = get_platform_path("appdata", "data")
        self.file_path = str(self._appdata_path / "settings.json")
        self._appdata_path.mkdir(parents=True, exist_ok=True)
        self.settings = {}
        self._load_settings()

    def _load_settings(self):
        try:
            with open(self.file_path, "r") as file:
                self.settings = json.load(file)
        except FileNotFoundError:
            self._save_settings()

    def _save_settings(self):
        with open(self.file_path, "w") as file:
            json.dump(self.settings, file, indent=4)

    def get_settings(self, key: str) -> Any:
        return self.settings.get(key)

    def set_settings(self, key: str, value: str) -> None:
        self.settings[key] = value
        self._save_settings()
