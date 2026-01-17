from abc import ABC, abstractmethod
from src.core.domain.entities import Verse

class VerseRepository(ABC):
    @abstractmethod
    def get(self,reference:dict) -> Verse:
        pass
    
    @abstractmethod
    def get_book(self,reference:dict) -> list[Verse]:
        pass
    
    @abstractmethod
    def get_all_bibles(self) -> list[dict]:
        pass
    
    @abstractmethod
    def import_bible_version(self,db_path:str) -> list[str]:
        pass
    
    