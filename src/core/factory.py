from src.core.use_cases import (
    VerseService,
    ScheduleService,
    SongService,
    SettingsServices,
    ImportService,
)
from src.core.infrastructure import (
    SQLiteScheduleRepository,
    SQLiteSongRepository,
    SQLiteVerseRepository,
    JSONSettingsProvider,
    SQLiteSSV100Provider,
    JSONConfV100Provider,
)


class Factory:
    def __init__(self):
        song_repo = SQLiteSongRepository()
        verse_repo = SQLiteVerseRepository()
        schedule_repo = SQLiteScheduleRepository()
        self.verse_service = VerseService(verse_repo)
        self.song_service = SongService(song_repo)
        self.schedule_service = ScheduleService(schedule_repo, song_repo, verse_repo)
        settings_provider = JSONSettingsProvider()
        self.settings_service = SettingsServices(settings_provider)
        self.import_service = ImportService(
            song_repo,
            schedule_repo,
            SQLiteSSV100Provider(),
            settings_provider,
            JSONConfV100Provider(),
        )

    def get_verse_service(self):
        return self.verse_service

    def get_song_service(self):
        return self.song_service

    def get_schedule_service(self):
        return self.schedule_service

    def get_settings_service(self):
        return self.settings_service

    def get_import_service(self):
        return self.import_service
