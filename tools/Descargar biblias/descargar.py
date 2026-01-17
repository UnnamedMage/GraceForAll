import requests
from bs4 import BeautifulSoup 
from almacenar import insert_into_table

def obtener_capitulo(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        print(f"Error al obtener la página: {response.status_code}")
        return None
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Encuentra el bloque de texto del capítulo
    capitulo = soup.find("div", class_="passage-text")
    
    if not capitulo:
        print("No se encontró el capítulo en la página.")
        return None
    
    # Eliminar referencias cruzadas
    for ref in capitulo.find_all("sup", class_="crossreference"):
        ref.decompose()
    
    for footnote in capitulo.find_all("sup", class_="footnote"):
        footnote.decompose()
    
    # Eliminar sección de referencias cruzadas ocultas
    crossrefs = capitulo.find("div", class_="crossrefs hidden")
    if crossrefs:
        crossrefs.decompose()
    
    for h3 in capitulo.find_all("h3"):
        h3.decompose()
    
    for h4 in capitulo.find_all("h4"):
        h4.decompose()
    
    footnotes = capitulo.find("div", class_="footnotes")
    if footnotes:
        footnotes.decompose()
    # Extraer y limpiar el texto
    texto = capitulo.get_text(separator='\n', strip=True)
    
    return texto

LIBROS_BIBLIA = [
    "Génesis", "Éxodo", "Levítico", "Números", "Deuteronomio", "Josué", "Jueces", "Rut", "1 Samuel", "2 Samuel",
    "1 Reyes", "2 Reyes", "1 Crónicas", "2 Crónicas", "Esdras", "Nehemías", "Ester", "Job", "Salmos", "Proverbios",
    "Eclesiastés", "Cantares", "Isaías", "Jeremías", "Lamentaciones", "Ezequiel", "Daniel", "Oseas", "Joel",
    "Amós", "Abdías", "Jonás", "Miqueas", "Nahúm", "Habacuc", "Sofonías", "Hageo", "Zacarías", "Malaquías",
    "Mateo", "Marcos", "Lucas", "Juan", "Hechos", "Romanos", "1 Corintios", "2 Corintios", "Gálatas",
    "Efesios", "Filipenses", "Colosenses", "1 Tesalonicenses", "2 Tesalonicenses", "1 Timoteo", "2 Timoteo",
    "Tito", "Filemón", "Hebreos", "Santiago", "1 Pedro", "2 Pedro", "1 Juan", "2 Juan", "3 Juan", "Judas",
    "Apocalipsis"
]


capitulos_biblia = [
    50, 40, 27, 36, 34, 24, 21, 4, 31, 24,
    22, 25, 29, 36, 10, 13, 10, 42, 150, 31,
    12, 8, 66, 52, 5, 48, 12, 14, 3, 9,
    1, 4, 7, 3, 3, 3, 2, 14, 4,
    28, 16, 24, 21, 28, 16, 16, 13, 6,
    6, 4, 4, 5, 3, 6, 4, 3, 1,
    13, 5, 5, 3, 5, 1, 1, 1,
    22
]
def descargar_biblias(version):

    for i in range(len(LIBROS_BIBLIA)):
        libro = LIBROS_BIBLIA[i]
        total_capitulos = capitulos_biblia[i]
        print(f"Procesando el libro: {libro}")
        for capitulo in range(1, total_capitulos + 1):
            url = f"https://www.biblegateway.com/passage/?search={libro}%20{capitulo}&version={version}"
            textos = obtener_capitulo(url)
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
                insert_into_table(version, lista_versiculos, lista_textos)
        print(f"Libro {libro} agregado correctamente")
        
        
if __name__ == "__main__":
    for version in ["PDT", "TLA", "LBLA", "NBV"]:
        descargar_biblias(version)
            
                    