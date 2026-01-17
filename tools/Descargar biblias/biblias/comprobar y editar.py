import sqlite3

libros_biblia= {
    "Génesis": 1533,
    "Éxodo": 1213,
    "Levítico": 859,
    "Números": 1288,
    "Deuteronomio": 959,
    "Josué": 658,
    "Jueces": 618,
    "Rut": 85,
    "1 Samuel": 810,
    "2 Samuel": 695,
    "1 Reyes": 816,
    "2 Reyes": 719,
    "1 Crónicas": 942,
    "2 Crónicas": 822,
    "Esdras": 280,
    "Nehemías": 406,
    "Ester": 167,
    "Job": 1070,
    "Salmos": 2461,
    "Proverbios": 915,
    "Eclesiastés": 222,
    "Cantares": 117,
    "Isaías": 1292,
    "Jeremías": 1364,
    "Lamentaciones": 154,
    "Ezequiel": 1273,
    "Daniel": 357,
    "Oseas": 197,
    "Joel": 73,
    "Amós": 146,
    "Abdías": 21,
    "Jonás": 48,
    "Miqueas": 105,
    "Nahúm": 47,
    "Habacuc": 56,
    "Sofonías": 53,
    "Hageo": 38,
    "Zacarías": 211,
    "Malaquías": 55,
    "Mateo": 1071,
    "Marcos": 678,
    "Lucas": 1151,
    "Juan": 879,
    "Hechos": 1007,
    "Romanos": 433,
    "1 Corintios": 437,
    "2 Corintios": 257,
    "Gálatas": 149,
    "Efesios": 155,
    "Filipenses": 104,
    "Colosenses": 95,
    "1 Tesalonicenses": 89,
    "2 Tesalonicenses": 47,
    "1 Timoteo": 113,
    "2 Timoteo": 83,
    "Tito": 46,
    "Filemón": 25,
    "Hebreos": 303,
    "Santiago": 108,
    "1 Pedro": 105,
    "2 Pedro": 61,
    "1 Juan": 105,
    "2 Juan": 13,
    "3 Juan": 14,
    "Judas": 25,
    "Apocalipsis": 404
}

def verificar_versiculos():
    version = "RVR1960"
    conn = sqlite3.connect(f'scripts/Descargar biblias/biblias/{version}.db')
    cursor = conn.cursor()

    # Obtener la cantidad de versículos por libro
    cursor.execute(f"""
        SELECT SUBSTR(Versiculos, 1, INSTR(Versiculos, ' ') - 1) AS libro, COUNT(*) AS total
        FROM {version}
        GROUP BY libro
    """)
    resultados = cursor.fetchall()
    discrepancias = []

    for libro_db, total_db in resultados:
        if libro_db in libros_biblia:
            total_esperado = libros_biblia[libro_db]
            if total_db != total_esperado:
                discrepancias.append({
                    'libro': libro_db,
                    'versiculos_db': total_db,
                    'versiculos_esperados': total_esperado
                })
        else:
            discrepancias.append({
                'libro': libro_db,
                'versiculos_db': total_db,
                'versiculos_esperados': "❌ No encontrado en lista"
            })

    conn.close()

    if discrepancias:
        print("\nDiscrepancias encontradas en la base de datos RVA:")
        print("-" * 60)
        for d in discrepancias:
            print(f"📘 Libro: {d['libro']}")
            print(f"📊 Versículos en la base de datos: {d['versiculos_db']}")
            print(f"📌 Versículos esperados: {d['versiculos_esperados']}")
            print("-" * 60)
    else:
        print("\n✅ No se encontraron discrepancias en la base de datos RVA.")

def eliminar_versiculo(id_versiculo):
    version = "NVI"
    conn = sqlite3.connect(f'scripts/Descargar biblias/biblias/{version}.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute(f"DELETE FROM {version} WHERE id = ?", (id_versiculo,))
        conn.commit()
        if cursor.rowcount > 0:
            print(f"✅ Versículo con ID {id_versiculo} eliminado exitosamente")
        else:
            print(f"❌ No se encontró ningún versículo con el ID {id_versiculo}")
    except sqlite3.Error as e:
        print(f"❌ Error al eliminar el versículo: {e}")
    finally:
        conn.close()

def cambiar_nombre_tabla(version, idioma):
    conn = sqlite3.connect(f'scripts/Descargar biblias/biblias/{version}.db')
    cursor = conn.cursor()
    
    try:
        # Verificar si la tabla existe
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (version,))
        if not cursor.fetchone():
            print(f"❌ La tabla '{version}' no existe en la base de datos")
            return

        # Crear nombre nuevo válido
        nuevo_nombre = f"{version}_{idioma}"

        # Cambiar el nombre de la tabla
        cursor.execute(f"ALTER TABLE `{version}` RENAME TO `{nuevo_nombre}`")
        conn.commit()
        print(f"✅ Tabla renombrada exitosamente de '{version}' a '{nuevo_nombre}'")
    except sqlite3.Error as e:
        print(f"❌ Error al renombrar la tabla: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    # verificar_versiculos()  # Comentamos la función anterior
    # eliminar_versiculo(11079)  # Comentamos la función anterior
    # Ejemplo de uso:
    versiones= ["LBLA", "NVI", "NTV", "RVA", "RVA-2015"]
    for version in versiones:
        cambiar_nombre_tabla(version=version, idioma="es")