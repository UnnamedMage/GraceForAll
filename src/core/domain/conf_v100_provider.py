from abc import ABC, abstractmethod
from typing import Any


class ConfV100Provider(ABC):
    @abstractmethod
    def exist_data(self) -> bool:
        pass

    @abstractmethod
    def init_data(self):
        pass

    @abstractmethod
    def get_config(self, key: str) -> Any:
        pass
