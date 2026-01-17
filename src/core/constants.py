def cargar_constantes(app, idioma):
    app.libros_biblia ={ 
        "es":[
        "Génesis", "Éxodo", "Levítico", "Números", "Deuteronomio", "Josué", "Jueces", "Rut", "1 Samuel", "2 Samuel",
        "1 Reyes", "2 Reyes", "1 Crónicas", "2 Crónicas", "Esdras", "Nehemías", "Ester", "Job", "Salmos", "Proverbios",
        "Eclesiastés", "Cantares", "Isaías", "Jeremías", "Lamentaciones", "Ezequiel", "Daniel", "Oseas", "Joel",
        "Amós", "Abdías", "Jonás", "Miqueas", "Nahúm", "Habacuc", "Sofonías", "Hageo", "Zacarías", "Malaquías",
        "Mateo", "Marcos", "Lucas", "Juan", "Hechos", "Romanos", "1 Corintios", "2 Corintios", "Gálatas",
        "Efesios", "Filipenses", "Colosenses", "1 Tesalonicenses", "2 Tesalonicenses", "1 Timoteo", "2 Timoteo",
        "Tito", "Filemón", "Hebreos", "Santiago", "1 Pedro", "2 Pedro", "1 Juan", "2 Juan", "3 Juan", "Judas",
        "Apocalipsis"
        ],
        "en":[
        "Genesis", "Exodus", "Leviticus", "Numbers", "Deuteronomy", "Joshua", "Judges", "Ruth", "1 Samuel", "2 Samuel",
        "1 Kings", "2 Kings", "1 Chronicles", "2 Chronicles", "Ezra", "Nehemiah", "Esther", "Job", "Psalms", "Proverbs",
        "Ecclesiastes", "Song of Solomon", "Isaiah", "Jeremiah", "Lamentations", "Ezekiel", "Daniel", "Hosea", "Joel",
        "Amos", "Obadiah", "Jonah", "Micah", "Nahum", "Habakkuk", "Soham", "Haggai", "Zechariah", "Malachi",
        "Matthew", "Mark", "Luke", "John", "Acts", "Romans", "1 Corinthians", "2 Corinthians", "Galatians",
        "Ephesians", "Philippians", "Colossians", "1 Thessalonians", "2 Thessalonians", "1 Timothy", "2 Timothy",
        "Titus", "Philemon", "Hebrews", "James", "1 Peter", "2 Peter", "1 John", "2 John", "3 John", "Jude",
        "Revelation"
        ]
        }

    app.libros_normalizados = {
        "es":{
        "genesis": "Génesis", "exodo": "Éxodo", "levitico": "Levítico", "numeros": "Números", "deuteronomio": "Deuteronomio",
        "josue": "Josué", "jueces": "Jueces", "rut": "Rut", "1 samuel": "1 Samuel", "2 samuel": "2 Samuel", "1 reyes": "1 Reyes",
        "2 reyes": "2 Reyes", "1 cronicas": "1 Crónicas", "2 cronicas": "2 Crónicas", "esdras": "Esdras", "nehemias": "Nehemías",
        "ester": "Ester", "job": "Job", "salmos": "Salmos", "proverbios": "Proverbios", "eclesiastes": "Eclesiastés",
        "cantares": "Cantares", "isaias": "Isaías", "jeremias": "Jeremías", "lamentaciones": "Lamentaciones", "ezequiel": "Ezequiel",
        "daniel": "Daniel", "oseas": "Oseas", "joel": "Joel", "amos": "Amós", "abdias": "Abdías", "jonas": "Jonás", "miqueas": "Miqueas",
        "nahum": "Nahúm", "habacuc": "Habacuc", "sofonias": "Sofonías", "hageo": "Hageo", "zacarias": "Zacarías", "malaquias": "Malaquías",
        "mateo": "Mateo", "marcos": "Marcos", "lucas": "Lucas", "juan": "Juan", "hechos": "Hechos", "romanos": "Romanos",
        "1 corintios": "1 Corintios", "2 corintios": "2 Corintios", "galatas": "Gálatas", "efesios": "Efesios", "filipenses": "Filipenses",
        "colosenses": "Colosenses", "1 tesalonicenses": "1 Tesalonicenses", "2 tesalonicenses": "2 Tesalonicenses", "1 timoteo": "1 Timoteo",
        "2 timoteo": "2 Timoteo", "tito": "Tito", "filemon": "Filemón", "hebreos": "Hebreos", "santiago": "Santiago", "1 pedro": "1 Pedro",
        "2 pedro": "2 Pedro", "1 juan": "1 Juan", "2 juan": "2 Juan", "3 juan": "3 Juan", "judas": "Judas", "apocalipsis": "Apocalipsis"
        }
    }
    match idioma:
        case "es":
            app.lista_puntos_fuente = ["Mediano", "Grande"]
            app.lista_resoluciones = ["2160p", "1440p", "1080p"]
            app.lista_temas = ["Modo oscuro", "Modo azul", "Modo calido", "Modo Solarized", "Modo verde"]
            app.lista_idiomas = ["Español", "Inglés"]

