from abc import ABC, abstractmethod
from typing import Any


class SettingsProvider(ABC):
    @abstractmethod
    def get_settings(self, key: str) -> Any:
        pass

    @abstractmethod
    def set_settings(self, key: str, value: str) -> None:
        pass
