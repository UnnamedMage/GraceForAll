from src.core.domain import VerseRepository


class VerseService:
    def __init__(self, verse_repo: VerseRepository):
        self.verse_repo = verse_repo

    def get_all_bibles(self) -> list[dict]:
        """
        Returns:
            list of {"version": str}
        """
        return self.verse_repo.get_all_bibles()

    def get_book(self, reference: dict) -> list[dict]:
        """
        Args:
            reference: {"version":str, "name": str}

        Returns:
            list: [
                    {"version":str, "citation":str, "text":str}
                    ...
                ]
        """
        verses = self.verse_repo.get_book(reference)

        return [verse.model_dump() for verse in verses]

    def get(self, reference: dict) -> dict:
        """
        Args:
            reference: {"version":str,"citation": str}

        Returns:
            dict: {"version":str, "citation":str, "text":str}
        """
        verse = self.verse_repo.get(reference)
        return verse.model_dump()
    
    def import_bible(self, db_path):
        return self.verse_repo.import_bible_version(db_path)

    def get_book_names_list(self, language: str):
        books_by_language = {
            "es": [
                "Génesis",
                "Éxodo",
                "Levítico",
                "Números",
                "Deuteronomio",
                "Josué",
                "Jueces",
                "Rut",
                "1 Samuel",
                "2 Samuel",
                "1 Reyes",
                "2 Reyes",
                "1 Crónicas",
                "2 Crónicas",
                "Esdras",
                "Nehemías",
                "Ester",
                "Job",
                "Salmos",
                "Proverbios",
                "Eclesiastés",
                "Cantares",
                "Isaías",
                "Jeremías",
                "Lamentaciones",
                "Ezequiel",
                "Daniel",
                "Oseas",
                "Joel",
                "Amós",
                "Abdías",
                "Jonás",
                "Miqueas",
                "Nahúm",
                "Habacuc",
                "Sofonías",
                "Hageo",
                "Zacarías",
                "Malaquías",
                "Mateo",
                "Marcos",
                "Lucas",
                "Juan",
                "Hechos",
                "Romanos",
                "1 Corintios",
                "2 Corintios",
                "Gálatas",
                "Efesios",
                "Filipenses",
                "Colosenses",
                "1 Tesalonicenses",
                "2 Tesalonicenses",
                "1 Timoteo",
                "2 Timoteo",
                "Tito",
                "Filemón",
                "Hebreos",
                "Santiago",
                "1 Pedro",
                "2 Pedro",
                "1 Juan",
                "2 Juan",
                "3 Juan",
                "Judas",
                "Apocalipsis",
            ],
            "en": [
                "Genesis",
                "Exodus",
                "Leviticus",
                "Numbers",
                "Deuteronomy",
                "Joshua",
                "Judges",
                "Ruth",
                "1 Samuel",
                "2 Samuel",
                "1 Kings",
                "2 Kings",
                "1 Chronicles",
                "2 Chronicles",
                "Ezra",
                "Nehemiah",
                "Esther",
                "Job",
                "Psalms",
                "Proverbs",
                "Ecclesiastes",
                "Song of Solomon",
                "Isaiah",
                "Jeremiah",
                "Lamentations",
                "Ezekiel",
                "Daniel",
                "Hosea",
                "Joel",
                "Amos",
                "Obadiah",
                "Jonah",
                "Micah",
                "Nahum",
                "Habakkuk",
                "Soham",
                "Haggai",
                "Zechariah",
                "Malachi",
                "Matthew",
                "Mark",
                "Luke",
                "John",
                "Acts",
                "Romans",
                "1 Corinthians",
                "2 Corinthians",
                "Galatians",
                "Ephesians",
                "Philippians",
                "Colossians",
                "1 Thessalonians",
                "2 Thessalonians",
                "1 Timothy",
                "2 Timothy",
                "Titus",
                "Philemon",
                "Hebrews",
                "James",
                "1 Peter",
                "2 Peter",
                "1 John",
                "2 John",
                "3 John",
                "Jude",
                "Revelation",
            ],
        }
        return books_by_language.get(language, [])
