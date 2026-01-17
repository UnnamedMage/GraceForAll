from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String
from sqlalchemy.orm import sessionmaker

def insert_into_table(table_name, lista1, lista2):
    """
    Verifica si existe la tabla en la base de datos SQLite, si no, la crea. Luego, inserta los datos.

    Parámetros:
        db_path (str): Ruta de la base de datos SQLite.
        table_name (str): Nombre de la tabla a verificar o crear.
        column1_name (str): Nombre de la primera columna.
        column2_name (str): Nombre de la segunda columna.
        lista1 (list): Lista de valores a insertar en la primera columna.
        lista2 (list): Lista de valores a insertar en la segunda columna.

    """
    # Verificar que ambas listas tengan el mismo número de elementos
    if len(lista1) != len(lista2):
        print("Las listas deben tener el mismo número de elementos.")
        return
    db_path = f"{table_name}.db"
    # Conectar a la base de datos
    engine = create_engine(f"sqlite:///{db_path}")
    metadata = MetaData()
    metadata.reflect(bind=engine)

    # Si la tabla no existe, crearla
    if table_name not in metadata.tables:
        print(f"La tabla '{table_name}' no existe. Creándola ahora...")

        table = Table(
            table_name, metadata,
            Column("id", Integer, primary_key=True, autoincrement=True),
            Column("Versiculos", String, nullable=False),
            Column("Textos", String, nullable=False)
        )

        metadata.create_all(engine)  # Crear la tabla en la base de datos
        print(f"Tabla '{table_name}' creada correctamente.")

    else:
        table = metadata.tables[table_name]  # Obtener referencia a la tabla existente

    # Crear sesión
    Session = sessionmaker(bind=engine)
    session = Session()

    # Insertar los datos en la tabla
    with session.begin():
        for val1, val2 in zip(lista1, lista2):
            session.execute(table.insert().values({"Versiculos": val1, "Textos": val2}))

    # Cerrar la sesión
    session.close()