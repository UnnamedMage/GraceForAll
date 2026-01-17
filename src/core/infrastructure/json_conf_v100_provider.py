from ..domain import ConfV100Provider
import json
from src.common import get_platform_path
from typing import Any


class JSONConfV100Provider(ConfV100Provider):
    def __init__(self):
        self._conf_path = get_platform_path("appdata", "config.json")

    def exist_data(self) -> bool:
        return self._conf_path.exists()

    def init_data(self):
        self.configs = {}
        with open(self._conf_path, "r") as file:
            self.configs = json.load(file)

    def get_config(self, key: str) -> Any:
        general = self.configs.get("general")
        if general:
            return general.get(key)
        return None
