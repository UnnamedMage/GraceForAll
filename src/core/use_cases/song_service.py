from src.core.domain import SongRepository, Song
from .response import Response
from ..domain.exceptions import AppCodeError
from pydantic import ValidationError as PydanticValidationError


class SongService:
    def __init__(self, song_repo: SongRepository):
        self.song_repo = song_repo

    def get_all(self) -> dict:
        """
        Returns:
            List of [dict[Song]]
        """
        songs = self.song_repo.get_all()
        songs_list = [song.model_dump() for song in songs]
        songs_list.sort(key=lambda x: x["title"])
        return Response(success=True, code="song.all_getted", data=songs_list).to_dict()

    def get(self, reference: dict) -> dict:
        """
        Args:
            reference: {"id": str} o {"title": str}

        Returns:
            dict: {
                "id":str,
                "title": str,
                "lyrics": list,
                "slide_style": {
                    "font": str,
                    "factor: float,
                    "italic": bool,
                    "bold": bool,
                    "v_align": Literal["VCenter", "Top", "Bottom"],
                    "h_align": Literal["HCenter", "Right", "Left"],
                    "in_animation": str,
                    "out_animation": str,
                    "bg_path": str

                }
            }
        """
        try:
            song = self.song_repo.get(reference)
            song_dumped = song.model_dump()
            song_dumped.update({"type": "song"})
            return Response(
                success=True, code="song.getted", data=song_dumped
            ).to_dict()
        except AppCodeError as e:
            return Response(success=False, code=e.code, details=e.details).to_dict()

    def add(self, song_data: dict) -> dict:
        """
        Args:
            song_data: {
                "title": str,
                "lyrics": list,
                "slide_style": {
                    "font": str,
                    "factor: float,
                    "italic": bool,
                    "bold": bool,
                    "v_align": Literal["VCenter", "Top", "Bottom"],
                    "h_align": Literal["HCenter", "Right", "Left"],
                    "in_animation": str,
                    "out_animation": str,
                    "bg_path": str

                }
            }
        """
        try:
            song = Song.model_validate(song_data)
            self.song_repo.add(song)
            return Response(success=True, code="song.created").to_dict()
        except AppCodeError as e:
            return Response(success=False, code=e.code, details=e.details).to_dict()
        except PydanticValidationError:
            return Response(success=False, code="validation.invalid_format").to_dict()

    def update(self, song_data: dict) -> dict:
        """
        Args:
            song_data: {
                "id":str,
                "title": str,
                "lyrics": list,
                "slide_style": {
                    "font": str,
                    "factor: float,
                    "italic": bool,
                    "bold": bool,
                    "v_align": Literal["VCenter", "Top", "Bottom"],
                    "h_align": Literal["HCenter", "Right", "Left"],
                    "in_animation": str,
                    "out_animation": str,
                    "bg_path": str

                }
            }
        """
        try:
            song = Song.model_validate(song_data)
            self.song_repo.update(song)
            return Response(success=True, code="song.updated").to_dict()
        except AppCodeError as e:
            return Response(success=False, code=e.code, details=e.details).to_dict()
        except PydanticValidationError:
            return Response(success=False, code="validation.invalid_format").to_dict()

    def delete(self, reference: dict) -> dict:
        """
        Args:
            reference: {"id": str} o {"title": str}
        """
        try:
            self.song_repo.delete(reference)
            return Response(success=True, code="song.deleted").to_dict()
        except AppCodeError as e:
            return Response(success=False, code=e.code, details=e.details).to_dict()
