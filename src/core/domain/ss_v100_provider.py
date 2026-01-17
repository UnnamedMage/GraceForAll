from abc import ABC, abstractmethod


class SSV100Provider(ABC):
    @abstractmethod
    def exist_db(self) -> bool:
        pass

    @abstractmethod
    def init_db(self) -> bool:
        pass

    @abstractmethod
    def get_all_songs(self) -> list[dict]:
        pass

    @abstractmethod
    def get_all_playlists(self) -> list[dict]:
        pass
