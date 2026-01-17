from sqlalchemy import (
    Column,
    String,
    create_engine,
    Boolean,
    REAL,
    Integer,
)
from sqlalchemy.orm import declarative_base, sessionmaker
from src.common import get_platform_path
from ..domain.ss_v100_provider import SSV100Provider

Base = declarative_base()


class SongV100(Base):
    __tablename__ = "songs"
    id = Column(Integer, primary_key=True)
    titulo = Column(String)
    letra = Column(String)
    fuente = Column(String)
    factor = Column(REAL)
    cursiva = Column(Boolean)
    negrita = Column(Boolean)
    alineacion_vertical = Column(String)
    alineacion_horizontal = Column(String)
    fondo_url = Column(String)

    def to_dict(self):
        return {
            "id": self.id,
            "titulo": self.titulo,
            "letra": self.letra,
            "fuente": self.fuente,
            "factor": self.factor,
            "cursiva": self.cursiva,
            "negrita": self.negrita,
            "alineacion_vertical": self.alineacion_vertical,
            "alineacion_horizontal": self.alineacion_horizontal,
            "fondo_url": self.fondo_url,
        }


class PlaylistV100(Base):
    __tablename__ = "playlists"
    id = Column(Integer, primary_key=True)
    titulo = Column(String, unique=True, nullable=False)
    fecha_creacion = Column(String)

    def to_dict(self):
        return {
            "id": self.id,
            "titulo": self.titulo,
            "fecha_creacion": self.fecha_creacion,
        }


class PlaylistSongV100(Base):
    __tablename__ = "playlist_song"
    playlist_id = Column(Integer, primary_key=True)
    song_id = Column(Integer, primary_key=True)
    order = Column(Integer)


class SQLiteSSV100Provider(SSV100Provider):
    def __init__(self):
        self._db_path = get_platform_path(
            "appdata", "databases", "songs_and_playlists.db"
        )

    def exist_db(self) -> bool:
        return self._db_path.exists()

    def init_db(self):
        engine = create_engine(f"sqlite:///{self._db_path}")
        Base.metadata.create_all(engine)
        self.Session = sessionmaker(bind=engine)

    def get_all_songs(self) -> list[dict]:
        with self.Session() as session:
            songs = session.query(SongV100).all()
            return [song.to_dict() for song in songs]

    def get_all_playlists(self) -> list[dict]:
        with self.Session() as session:
            playlists = session.query(PlaylistV100).all()

            playlists_with_songs = []
            for playlist in playlists:
                pls = (
                    session.query(PlaylistSongV100)
                    .filter_by(playlist_id=playlist.id)
                    .all()
                )

                song_ids = [ps.song_id for ps in pls]
                playlist_dict = playlist.to_dict()
                playlist_dict["songs"] = song_ids
                playlists_with_songs.append(playlist_dict)

            return playlists_with_songs
