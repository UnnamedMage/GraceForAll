from core.helpers import SYpathcreater
from sqlalchemy import create_engine, Column, String, Integer, Boolean, REAL, ForeignKey, Table, MetaData, select, and_, or_, text
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from sqlalchemy.inspection import inspect
from sqlalchemy.schema import CreateTable
from datetime import datetime

db_path_song = SYpathcreater("databases","songs_and_playlists.db")
Base_song = declarative_base()

playlist_song_association = Table(
    "playlist_song",
    Base_song.metadata,
    Column("playlist_id", Integer, ForeignKey("playlists.id"), primary_key=True),
    Column("song_id", Integer, ForeignKey("songs.id"), primary_key=True),
    Column("order", Integer, primary_key=True),
)


class Song(Base_song):
    __tablename__ = "songs"
    id = Column(Integer, primary_key=True)
    titulo = Column(String, unique=True, nullable=False)
    letra = Column(String)
    fuente = Column(String)
    factor = Column(REAL, default=1)
    cursiva = Column(Boolean, default=False)
    negrita = Column(Boolean, default=False)
    alineacion_vertical = Column(String, default="Qt.AlignVCenter")
    alineacion_horizontal = Column(String, default="Qt.AlignHCenter")
    fondo_url = Column(String, default="None")
    
    def to_list(self):
        return [
            getattr(self, column.key) 
            for column in inspect(self).mapper.column_attrs
            if column.key not in ["id"]
            ]
    
class Playlist(Base_song):
    __tablename__ = "playlists"
    id = Column(Integer, primary_key=True)
    titulo = Column(String, unique=True, nullable=False)
    fecha_creacion = Column(String, default=datetime.now().strftime("%d/%m/%Y"))
    canciones = relationship("Song", secondary=playlist_song_association, backref="playlists")


engine_song = create_engine(f"sqlite:///{db_path_song}")    
Base_song.metadata.create_all(engine_song)
Session_song = sessionmaker(bind=engine_song)
session_song_var = Session_song()

def is_title_unique_song(titulo):
    return session_song_var.query(Song).filter(Song.titulo == titulo).first() is None

def add_song(new_song):
    session_song_var.add(new_song)
    session_song_var.commit()
    
def edit_song(old_title, **kwargs):
    song = session_song_var.query(Song).filter(Song.titulo == old_title).first()

    if "titulo" in kwargs:
        song.titulo = kwargs["titulo"]

    for key, value in kwargs.items():
        if hasattr(song, key):
            setattr(song, key, value)

    session_song_var.commit()
    
def delete_song(titulo):
    song = session_song_var.query(Song).filter(Song.titulo == titulo).first()

    if not song:
        return

    session_song_var.execute(
        playlist_song_association.delete().where(playlist_song_association.c.song_id == song.id)
    )
    
    session_song_var.delete(song)
    session_song_var.commit()
    
def get_all_song_titles():
    titles = session_song_var.query(Song.titulo).all()
    return [title[0] for title in titles]

def get_song_by_title(title):
    song_data = session_song_var.query(Song).filter(Song.titulo == title).first()

    if not song_data:
        return None

    return song_data.titulo,song_data.letra,song_data.fuente,song_data.factor,song_data.cursiva,song_data.negrita,song_data.alineacion_vertical,song_data.alineacion_horizontal,song_data.fondo_url

def is_title_playlist_unique(titulo):
    return session_song_var.query(Playlist).filter(Playlist.titulo == titulo).first() is None

def create_playlist(titulo, song_titles):
    new_playlist = Playlist(titulo=titulo)
    session_song_var.add(new_playlist)
    
    for order, song_title in enumerate(song_titles, start=1):
        song = session_song_var.query(Song).filter(Song.titulo == song_title).first()
        if song:
            session_song_var.execute(
                playlist_song_association.insert(),
                {"playlist_id": new_playlist.id, "song_id": song.id, "order": order}
            )
    
    session_song_var.commit()

def update_data_playlist(playlist_name, new_song_titles):
    playlist = session_song_var.query(Playlist).filter(Playlist.titulo == playlist_name).first()
    
    session_song_var.execute(
        playlist_song_association.delete().where(playlist_song_association.c.playlist_id == playlist.id)
    )

    
    for order, song_title in enumerate(new_song_titles, start=1):
        song = session_song_var.query(Song).filter(Song.titulo == song_title).first()
        if song:
            session_song_var.execute(
                playlist_song_association.insert(),
                {"playlist_id": playlist.id, "song_id": song.id, "order": order}
            )
   
    session_song_var.commit()

def get_all_playlist():
    playlists = session_song_var.query(Playlist.titulo, Playlist.fecha_creacion).order_by(Playlist.id.desc()).all()
    if not playlists:
        return None
    titles, dates = zip(*playlists)
    return [list(titles), list(dates)]

def delete_playlist(titulo):
    playlist = session_song_var.query(Playlist).filter(Playlist.titulo == titulo).first()
    if not playlist:
        return
    session_song_var.execute(
        playlist_song_association.delete().where(playlist_song_association.c.playlist_id == playlist.id)
    )
    session_song_var.delete(playlist)
    session_song_var.commit()
    
def get_songs_from_playlist(playlist_name):
    playlist = session_song_var.query(Playlist).filter(Playlist.titulo == playlist_name).first()

    songs = (
        session_song_var.query(Song.titulo)
        .join(playlist_song_association, Song.id == playlist_song_association.c.song_id)
        .filter(playlist_song_association.c.playlist_id == playlist.id)
        .order_by(playlist_song_association.c.order)
        .all()
    )

    return [song[0] for song in songs]


db_path_bible = SYpathcreater("databases","bibles.db")
engine_bible = create_engine(f"sqlite:///{db_path_bible}")
metadata_bible = MetaData()


def get_book_by_version(table_name,texto_parcial):
    # Crear una conexión a la base de datos
    
    
    # Cargar la tabla
    table = Table(table_name, metadata_bible, autoload_with=engine_bible)
    
    query = select(table.c["Versiculos"], table.c["Textos"]).where(
        table.c["Versiculos"].contains(texto_parcial)
    )
    
    
    # Ejecutar la consulta
    with engine_bible.connect() as connection:
        result = connection.execute(query).fetchall()
    
    # Separar los resultados en dos listas
    lista_columna_filtrada = [row[0] for row in result]
    lista_segunda_columna = [row[1] for row in result]
    
    return lista_columna_filtrada, lista_segunda_columna

def get_first_bible_version():
    with engine_bible.connect() as connection:
        result = connection.execute(text("SELECT name FROM sqlite_master WHERE type='table' LIMIT 1")).fetchone()
        return result[0] if result else "None"  
    
def get_all_bibles_versions():
    with engine_bible.connect() as connection:
        result = connection.execute(text("SELECT name FROM sqlite_master WHERE type='table'")).fetchall()
        return [row[0] for row in result] if result else "None"

def import_bible_tables(external_db_path):
    try:
        # Engines y metadatas
        external_engine = create_engine(f"sqlite:///{external_db_path}")
        external_metadata = MetaData()
        external_metadata.reflect(bind=external_engine)

        # Listar tablas externas
        table_names = external_metadata.tables.keys()

        imported_tables = []

        for table_name in table_names:
            # Verificar si ya existe en el destino
            with engine_bible.connect() as connection:
                exists = connection.execute(
                    text(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
                ).fetchone()

            if exists:
                continue  # ya existe, no importamos

            # Obtener tabla externa
            external_table = external_metadata.tables[table_name]

            # Re-crear la tabla en el engine destino
            create_stmt = CreateTable(external_table)
            with engine_bible.connect() as conn:
                conn.execute(create_stmt)

            # Copiar datos
            with external_engine.connect() as source_conn:
                result = source_conn.execute(select(external_table))
                columns = result.keys()
                rows = [dict(zip(columns, row)) for row in result.fetchall()]

            if rows:
                # Necesitamos construir una tabla con el mismo nombre en metadata destino
                destination_metadata = MetaData()
                destination_table = Table(
                    table_name,
                    destination_metadata,
                    autoload_with=engine_bible
                )

                with engine_bible.connect() as target_conn:
                    target_conn.execute(destination_table.insert(), rows)
                    target_conn.commit()

            imported_tables.append(table_name)

        return imported_tables

    except Exception as e:
        print(f"Error: {e}")
        return None  