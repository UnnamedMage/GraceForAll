from sqlalchemy import create_engine, Table, MetaData, select, text
from sqlalchemy.orm import declarative_base
from sqlalchemy.schema import CreateTable
from src.core.domain import VerseRepository, Verse
from src.common import get_platform_path

Base_verse = declarative_base()


class SQLiteVerseRepository(VerseRepository):
    def __init__(self):
        self._db_path = get_platform_path("appdata", "databases", "verses.db")
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        self.engine = create_engine(f"sqlite:///{self._db_path}")
        self.table = lambda name: Table(name, MetaData(), autoload_with=self.engine)

    def import_bible_version(self, db_path):
        try:
            external_engine = create_engine(f"sqlite:///{db_path}")
            external_metadata = MetaData()
            external_metadata.reflect(bind=external_engine)

            table_names = external_metadata.tables.keys()

            imported_names: list[str] = []

            for table_name in table_names:
                with self.engine.connect() as connection:
                    exists = connection.execute(
                        text(
                            f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'"
                        )
                    ).fetchone()

                if exists:
                    continue

                external_table = external_metadata.tables[table_name]

                create_stmt = CreateTable(external_table)
                with self.engine.connect() as conn:
                    conn.execute(create_stmt)

                with external_engine.connect() as source_conn:
                    result = source_conn.execute(select(external_table))
                    columns = result.keys()
                    rows = [dict(zip(columns, row)) for row in result.fetchall()]

                if rows:
                    destination_metadata = MetaData()
                    destination_table = Table(
                        table_name, destination_metadata, autoload_with=self.engine
                    )

                    with self.engine.connect() as target_conn:
                        target_conn.execute(destination_table.insert(), rows)
                        target_conn.commit()

                imported_names.append(table_name)
            if len(imported_names) == 0:
                raise ValueError("No hay ninguna Biblia nueva que agregar")
            return [{"version": name} for name in imported_names]

        except Exception:
            raise ValueError("Error ocurrido durante la importacion")

    def get_book(self, reference):
        table = self.table(reference["version"])

        query = select(table.c["citations"], table.c["texts"]).where(
            table.c["citations"].contains(reference["name"])
        )

        with self.engine.connect() as connection:
            result = connection.execute(query).fetchall()

        return [
            Verse(version=reference["version"], citation=row[0], text=row[1])
            for row in result
        ]

    def get(self, reference):
        table = self.table(reference["version"])

        query = select(table.c["citations"], table.c["texts"]).where(
            table.c["citations"].contains(reference["citation"])
        )

        with self.engine.connect() as connection:
            row = connection.execute(query).fetchone()

        return Verse(version=reference["version"], citation=row[0], text=row[1])

    def get_all_bibles(self):
        with self.engine.connect() as connection:
            result = connection.execute(
                text("SELECT name FROM sqlite_master WHERE type='table'")
            ).fetchall()
            return [{"version": row[0]} for row in result]
