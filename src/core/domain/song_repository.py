from abc import ABC, abstractmethod
from src.core.domain.entities import Song

class SongRepository(ABC):
    @abstractmethod
    def add(self, song:Song) -> None:
        pass
    
    @abstractmethod
    def update(self, song:Song) -> None:
        pass
    
    @abstractmethod
    def get(self, reference:dict) -> Song:
        pass
    
    @abstractmethod
    def delete(self, reference:dict) ->None:
        pass
    
    @abstractmethod
    def get_all(self, reference:dict = None) -> list[Song]:
        pass
