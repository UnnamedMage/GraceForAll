from src.core.domain import (
    SongRepository,
    ScheduleRepository,
    SSV100Provider,
    ConfV100Provider,
    SettingsProvider,
    Song,
    SlideStyle,
    Schedule,
)
from ..domain.exceptions import AppCodeError
from pydantic import ValidationError as PydanticValidationError

V100ALIGNMENT = {
    "AlignLeft": "left",
    "AlignHCenter": "hcenter",
    "AlignRight": "right",
    "AlignTop": "top",
    "AlignVCenter": "vcenter",
    "AlignBottom": "bottom",
}


class ImportService:
    def __init__(
        self,
        song_repo: SongRepository,
        schedule_repo: ScheduleRepository,
        ssv100_provider: SSV100Provider,
        settings_provider: SettingsProvider,
        conf_provider: ConfV100Provider,
    ):
        self.song_repo = song_repo
        self.schedule_repo = schedule_repo
        self.ssv100_provider = ssv100_provider
        self.settings_provider = settings_provider
        self.conf_provider = conf_provider

    def verify_ss(self):
        if not self.ssv100_provider.exist_db():
            return

        if self.settings_provider.get_settings("ss_v100"):
            return

        self.import_ss()

    def verify_conf(self):
        if not self.conf_provider.exist_data():
            return

        if self.settings_provider.get_settings("conf_v100"):
            return

        self.import_conf()

    def import_ss(self):
        self.ssv100_provider.init_db()
        v100_songs = self.ssv100_provider.get_all_songs()
        v100_playlists = self.ssv100_provider.get_all_playlists()

        song_dict = {}

        for song in v100_songs:
            if imported_song := self._create_song(song):
                song_dict[song["id"]] = imported_song

        for playlist in v100_playlists:
            self._create_schedule(playlist, song_dict)

        self.settings_provider.set_settings("ss_v100", True)

    def _create_song(self, song: dict) -> Song | None:
        try:
            new_song = Song(
                title=song["titulo"],
                lyrics=song["letra"].split("\n\n"),
                slide_style=SlideStyle(
                    family=song["fuente"],
                    factor=song["factor"],
                    italic=song["cursiva"],
                    bold=song["negrita"],
                    v_align=V100ALIGNMENT.get(song["alineacion_vertical"]),
                    h_align=V100ALIGNMENT.get(song["alineacion_horizontal"]),
                    bg_path=song["fondo_url"],
                ),
            )
            self.song_repo.add(new_song)
            return new_song
        except (AppCodeError, PydanticValidationError):
            try:
                new_song.title = new_song.title + "(importado)"
                self.song_repo.add(new_song)
                return new_song
            except (AppCodeError, PydanticValidationError):
                return None

    def _create_schedule(self, playlist: dict, song_dict: dict):
        elements = []

        for song_id in playlist["songs"]:
            if song := song_dict.get(song_id):
                elements.append({"type": "song", "id": song.id})

        try:
            new_schedule = Schedule(
                name=playlist["titulo"],
                items=elements,
            )
            self.schedule_repo.add(new_schedule)
        except (AppCodeError, PydanticValidationError):
            try:
                new_schedule.name = new_schedule.name + "(importado)"
                self.schedule_repo.add(new_schedule)
            except (AppCodeError, PydanticValidationError):
                return

    def import_conf(self):
        self.conf_provider.init_data()

        if bible := self.conf_provider.get_config("bible_default"):
            self.settings_provider.set_settings("bible", {"version": bible})

        if root_media := self.conf_provider.get_config("root_media"):
            self.settings_provider.set_settings("media_folder", root_media)

        if background := self.conf_provider.get_config("background_default"):
            self.settings_provider.set_settings("slide_style", {"bg_path": background})

        self.settings_provider.set_settings("conf_v100", True)
