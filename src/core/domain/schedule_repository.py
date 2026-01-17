from abc import ABC, abstractmethod
from src.core.domain.entities import Schedule

class ScheduleRepository(ABC):
    @abstractmethod
    def get(self, reference:dict) -> Schedule:
        pass
    
    @abstractmethod
    def get_all(self, reference:dict = None) -> list[Schedule]:
        pass
    
    @abstractmethod
    def add(self, schedule:Schedule) -> None:
        pass
    
    @abstractmethod
    def update(self, schedule:Schedule) -> None:
        pass
    
    @abstractmethod
    def delete(self, reference:dict)->None:
        pass