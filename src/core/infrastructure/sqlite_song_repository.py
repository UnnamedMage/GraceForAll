import json
from sqlalchemy import JSON, Column, String, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from src.core.domain import Song, SongRepository
from src.common import get_platform_path
from ..domain.exceptions import AppCodeError

Base_song = declarative_base()


class SongModel(Base_song):
    __tablename__ = "songs"

    id = Column(String, primary_key=True, nullable=False)
    title = Column(String, nullable=False, unique=True)
    lyrics = Column(JSON, nullable=False)
    slide_style = Column(JSON, nullable=False)

    @staticmethod
    def from_entity(song: Song):
        return SongModel(
            id=song.id,
            title=song.title,
            lyrics=json.dumps(song.lyrics),
            slide_style=song.slide_style.model_dump_json(),
        )

    def to_entity(self):
        return Song.model_validate(
            {
                "id": self.id,
                "title": self.title,
                "lyrics": json.loads(self.lyrics),
                "slide_style": json.loads(self.slide_style),
            }
        )

    def update_from_entity(self, song: Song):
        self.title = song.title
        self.lyrics = json.dumps(song.lyrics)
        self.slide_style = song.slide_style.model_dump_json()


class SQLiteSongRepository(SongRepository):
    def __init__(self):
        self._db_path = get_platform_path("appdata", "databases", "songs.db")
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        engine = create_engine(f"sqlite:///{self._db_path}")
        Base_song.metadata.create_all(engine)
        self.Session = sessionmaker(bind=engine)

    def add(self, song: Song):
        with self.Session() as session:
            existing_by_name = (
                session.query(SongModel).filter(SongModel.title == song.title).first()
            )

            if existing_by_name:
                raise AppCodeError("song.duplicated")

            song_model = SongModel.from_entity(song)
            session.add(song_model)
            session.commit()

    def update(self, song: Song):
        with self.Session() as session:
            existing_by_name = (
                session.query(SongModel).filter(SongModel.title == song.title).first()
            )

            if existing_by_name:
                if not existing_by_name.id == song.id:
                    raise AppCodeError("song.duplicated")

            song_model = (
                session.query(SongModel).filter(SongModel.id == song.id).first()
            )
            if song_model:
                song_model.update_from_entity(song)
                session.commit()
                return
        raise AppCodeError("song.not_found")

    def get(self, reference: dict) -> Song:
        with self.Session() as session:
            query = session.query(SongModel)
            for key, value in reference.items():
                query = query.filter(getattr(SongModel, key) == value)
            song_model = query.first()
            if song_model:
                return song_model.to_entity()
        raise AppCodeError("song.not_found")

    def get_all(self, reference=None):
        with self.Session() as session:
            query = session.query(SongModel)
            if reference:
                for key, value in reference.items():
                    query = query.filter(getattr(SongModel, key) == value)
            song_models = query.all()
            return [model.to_entity() for model in song_models]

    def delete(self, reference):
        with self.Session() as session:
            query = session.query(SongModel)
            for key, value in reference.items():
                query = query.filter(getattr(SongModel, key) == value)
            song_model = query.first()
            if song_model:
                session.delete(song_model)
                session.commit()
                return
        raise AppCodeError("song.not_found")
