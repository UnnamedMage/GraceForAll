import requests
from bs4 import BeautifulSoup
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String
from sqlalchemy.orm import sessionmaker


def get_chapter_by_url(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print(f"Error al obtener la página: {response.status_code}")
        return None

    soup = BeautifulSoup(response.text, "html.parser")

    # Encuentra el bloque de texto del capítulo
    chapter = soup.find("div", class_="passage-text")

    if not chapter:
        print("No se encontró el capítulo en la página.")
        return None

    # Eliminar referencias cruzadas
    for ref in chapter.find_all("sup", class_="crossreference"):
        ref.decompose()

    for footnote in chapter.find_all("sup", class_="footnote"):
        footnote.decompose()

    # Eliminar sección de referencias cruzadas ocultas
    crossrefs = chapter.find("div", class_="crossrefs hidden")
    if crossrefs:
        crossrefs.decompose()

    for h3 in chapter.find_all("h3"):
        h3.decompose()

    for h4 in chapter.find_all("h4"):
        h4.decompose()

    footnotes = chapter.find("div", class_="footnotes")
    if footnotes:
        footnotes.decompose()
    # Extraer y limpiar el texto
    chapter_text = chapter.get_text(separator="\n", strip=True)

    return chapter_text


def insert_into_table(version, citations_list, texts_list, in_one_db=False):
    """
    Verifica si existe la tabla en la base de datos SQLite, si no, la crea. Luego, inserta los datos.

    Parámetros:
        table_name (str): Nombre de la tabla a verificar o crear.
        citations_list (list): Lista de valores a insertar en la primera columna.
        texts_list (list): Lista de valores a insertar en la segunda columna.

    """
    # Verificar que ambas listas tengan el mismo número de elementos
    if len(citations_list) != len(texts_list):
        print("Las listas deben tener el mismo número de elementos.")
        return
    if in_one_db:
        db_path = "verses.db"
    else:
        db_path = f"{version}.db"
    # Conectar a la base de datos
    engine = create_engine(f"sqlite:///{db_path}")
    metadata = MetaData()
    metadata.reflect(bind=engine)

    # Si la tabla no existe, crearla
    if version not in metadata.tables:
        print(f"La tabla '{version}' no existe. Creándola ahora...")

        table = Table(
            version,
            metadata,
            Column("id", Integer, primary_key=True, autoincrement=True),
            Column("citations", String, nullable=False),
            Column("texts", String, nullable=False),
        )

        metadata.create_all(engine)  # Crear la tabla en la base de datos
        print(f"Tabla '{version}' creada correctamente.")

    else:
        table = metadata.tables[version]  # Obtener referencia a la tabla existente

    # Crear sesión
    Session = sessionmaker(bind=engine)
    session = Session()

    # Insertar los datos en la tabla
    with session.begin():
        for val1, val2 in zip(citations_list, texts_list):
            session.execute(table.insert().values({"citations": val1, "texts": val2}))

    # Cerrar la sesión
    session.close()


LIBROS_BIBLIA = [
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
]


capitulos_biblia = [
    50,
    40,
    27,
    36,
    34,
    24,
    21,
    4,
    31,
    24,
    22,
    25,
    29,
    36,
    10,
    13,
    10,
    42,
    150,
    31,
    12,
    8,
    66,
    52,
    5,
    48,
    12,
    14,
    3,
    9,
    1,
    4,
    7,
    3,
    3,
    3,
    2,
    14,
    4,
    28,
    16,
    24,
    21,
    28,
    16,
    16,
    13,
    6,
    6,
    4,
    4,
    5,
    3,
    6,
    4,
    3,
    1,
    13,
    5,
    5,
    3,
    5,
    1,
    1,
    1,
    22,
]


def descargar_biblias(version, juntos=False):
    for i in range(len(LIBROS_BIBLIA)):
        libro = LIBROS_BIBLIA[i]
        total_capitulos = capitulos_biblia[i]
        print(f"Procesando el libro: {libro}")
        for capitulo in range(1, total_capitulos + 1):
            url = f"https://www.biblegateway.com/passage/?search={libro}%20{capitulo}&version={version}"
            textos = get_chapter_by_url(url)
            if textos:
                datos = textos.split("\n")
                numero = 0
                versiculo = None
                texto = ""
                anterior = "tx"
                lista_versiculos = []
                lista_textos = []
                for i, dato in enumerate(datos):
                    if dato.isdigit():
                        if anterior == "tx":
                            if versiculo:
                                lista_versiculos.append(versiculo)
                                lista_textos.append(texto)
                            numero = numero + 1
                            versiculo = f"{libro} {capitulo}:{numero} "
                            texto = ""
                            anterior = "num"
                    else:
                        if texto == "":
                            texto = dato
                        else:
                            if len(dato) < 3:
                                texto = texto + f"{dato}"
                            else:
                                texto = texto + f" {dato}"
                        anterior = "tx"

                    if i + 1 == len(datos):
                        lista_versiculos.append(versiculo)
                        lista_textos.append(texto)
                insert_into_table(
                    f"{version}_es", lista_versiculos, lista_textos, juntos
                )
        print(f"Libro {libro} agregado correctamente")


if __name__ == "__main__":
    for version in [
        "RVA",
        "RVR1960",
        "LBLA",
        "JBS",
        "DHH",
        "NBLA",
        "NBV",
        "NTV",
        "NVI",
        "CST",
        "PDT",
        "BLP",
        "BLPH",
        "RVA-2015",
        "RVC",
        "RVR1977",
        "RVR1995",
        "TLA",
        "SRV-BGR",
    ]:
        descargar_biblias(version, True)
