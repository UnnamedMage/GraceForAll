from src.core.domain import (
    ScheduleRepository,
    Schedule,
    SongRepository,
    VerseRepository,
)
from .response import Response
from ..domain.exceptions import AppCodeError
from pydantic import ValidationError as PydanticValidationError


class ScheduleService:
    def __init__(
        self,
        schedule_repo: ScheduleRepository,
        song_repository: SongRepository,
        verse_repository: VerseRepository,
    ):
        self.schedule_repo = schedule_repo
        self.song_repo = song_repository
        self.verse_repo = verse_repository

    def get_all(self) -> dict:
        """
        Returns:
            List of [Schedules]
        """
        schedules = self.schedule_repo.get_all()
        schedule_list = [schedule.model_dump() for schedule in schedules]
        return Response(
            success=True, code="schedule.all_getted", data=schedule_list
        ).to_dict()

    def get(self, reference: dict) -> dict:
        """
        Args:
            reference: {"id": str} o {"name": str}

        Returns:
            dict: {
                "id":str,
                "name":str,
                "date":str,
                "items": [
                        {"song":{"id": str}} | {"media": {"path":str}} | {"verse":{"bible": dict, "citation": str}}
                        ...
                    ]
            }
        """
        try:
            schedule_data = self.schedule_repo.get(reference)
            schedule = schedule_data.model_dump()
            check = []
            items = []
            for n, item in enumerate(schedule["items"]):
                if item["type"] == "song":
                    if song := self._create_song(item["id"]):
                        song["type"] = "song"
                        items.append(song)
                        continue
                    check.append(n)
                elif item["type"] == "verse":
                    if verse := self._create_verse(item["version"], item["citation"]):
                        verse["type"] = "verse"
                        items.append(verse)
                        continue
                    check.append(n)
                elif item["type"] == "media":
                    media = {"type": "media", "slide_style": {"bg_path": item["path"]}}
                    items.append(media)
                    continue

            if check != []:
                for e in sorted(check, reverse=True):
                    schedule_data.items.pop(e)
                if schedule_data.items == []:
                    self.schedule_repo.delete(reference)
                    return Response(
                        success=False, code="schedule.invalid", data=schedule.copy()
                    ).to_dict()
                else:
                    self.schedule_repo.update(schedule_data)

            schedule["items"] = items

            return Response(
                success=True, code="schedule.getted", data=schedule
            ).to_dict()
        except AppCodeError as e:
            return Response(success=False, code=e.code, details=e.details).to_dict()

    def _create_song(self, id: str):
        song = None
        try:
            song = self.song_repo.get({"id": id})
            return song.model_dump()
        except AppCodeError:
            return song

    def _create_verse(self, version, citation):
        verse = None
        try:
            verse = self.verse_repo.get(
                {"version": version, "citation": citation}
            ).model_dump()
            text_in_projection = f"{verse['text']}\n{verse['citation']}"
            length = max(40, min(len(text_in_projection), 480))
            normalized = (length - 30) / (480 - 30)
            factor = 5 - (normalized * 4)
            verse_formated = dict(
                slide_style={"factor": factor},
            )
            verse_formated.update(verse)
            return verse_formated
        except AppCodeError:
            return verse

    def add(self, schedule_data: dict) -> dict:
        """
        Args:
            schedule_data: {
                "name":str,
                "date":str,
                "items": [
                        {"song":{"id": str}} | {"media": {"path":str}} | {"verse":{"bible": dict, "citation": str}}
                        ...
                    ]
            }
        """
        try:
            schedule_data["items"] = self._format_items(schedule_data["items"])
            schedule = Schedule.model_validate(schedule_data)
            self.schedule_repo.add(schedule)
            return Response(
                success=True,
                code="schedule.created",
                data={"id": schedule.id, "date": schedule.date},
            ).to_dict()
        except AppCodeError as e:
            return Response(success=False, code=e.code, details=e.details).to_dict()
        except PydanticValidationError:
            return Response(success=False, code="validation.invalid_format").to_dict()

    def _format_items(self, items: list):
        formated_items = []
        for item in items:
            if item["type"] == "song":
                formated = {"type": "song", "id": item["id"]}
            elif item["type"] == "media":
                formated = {"type": "media", "path": item["slide_style"]["bg_path"]}
            elif item["type"] == "verse":
                formated = {
                    "type": "verse",
                    "version": item["version"],
                    "citation": item["citation"],
                }
            formated_items.append(formated)
        return formated_items

    def update(self, schedule_data: dict) -> dict:
        """
        Args:
            schedule_data: {
                "id":str,
                "name":str,
                "date":str,
                "items": [song, media, verse]
            }
        """
        try:
            formated_items = []
            for item in schedule_data["items"]:
                if item["type"] == "song":
                    formated = {"type": "song", "id": item["id"]}
                elif item["type"] == "media":
                    formated = {"type": "media", "path": item["slide_style"]["bg_path"]}
                elif item["type"] == "verse":
                    formated = {
                        "type": "verse",
                        "version": item["version"],
                        "citation": item["citation"],
                    }
                formated_items.append(formated)
            schedule_data["items"] = formated_items
            schedule = Schedule.model_validate(schedule_data)
            self.schedule_repo.update(schedule)
            return Response(success=True, code="schedule.updated").to_dict()
        except AppCodeError as e:
            return Response(success=False, code=e.code, details=e.details).to_dict()
        except PydanticValidationError:
            return Response(success=False, code="validation.invalid_format").to_dict()

    def delete(self, reference: dict) -> dict:
        """
        Args:
            reference: {"id": str} o {"name": str}
        """
        try:
            self.schedule_repo.delete(reference)
            return Response(success=True, code="schedule.deleted").to_dict()
        except AppCodeError as e:
            return Response(success=False, code=e.code, details=e.details).to_dict()

    def verify_changes(self, schedule_for_revision: dict) -> dict:
        """
        Args:
            schedule_data: {
                "id":str,
                "name":str,
                "date":str,
                "items": [song, media, verse]
            }
        """
        try:
            if not schedule_for_revision.get("id"):
                if schedule_for_revision["items"] == []:
                    return Response(success=False, code="schedule.equal").to_dict()
                return Response(success=True, code="schedule.diferent").to_dict()

            schedule = self.schedule_repo.get(
                {"id": schedule_for_revision["id"]}
            ).model_dump()
            items_for_revision: list = schedule_for_revision["items"]
            items = schedule["items"]

            if len(items_for_revision) != len(items):
                return Response(success=True, code="schedule.diferent").to_dict()

            check = False
            items_for_revision = self._format_items(schedule_for_revision["items"])

            for n, item in enumerate(schedule["items"]):
                if check:
                    break

                ifr = items_for_revision[n]

                if ifr != item:
                    check = True

            if check:
                return Response(success=True, code="schedule.diferent").to_dict()
            else:
                return Response(success=False, code="schedule.equal").to_dict()
        except AppCodeError as e:
            return Response(success=False, code=e.code, details=e.details).to_dict()
