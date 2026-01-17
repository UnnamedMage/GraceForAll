import json
from core.helpers import SYpathcreater

config_path = SYpathcreater("config.json")

def cargar_configuracion():
    try:
        with open(config_path, "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        print("Error: No se pudo cargar el archivo config.json")
        return {}

def cargar_colores():
    config = cargar_configuracion()
    selected_stylesheet = config.get("general", {}).get("selected_stylesheet", "")
    lista_colores = config.get("colors", {}).get(selected_stylesheet, [])
    return lista_colores

def cargar_idioma():
    config = cargar_configuracion()
    idioma = config.get("general", {}).get("language", "")
    return idioma

def cargar_carpeta_raiz():
    config = cargar_configuracion()
    root_media = config.get("general", {}).get("root_media", "")
    return root_media

def editar_carpeta_raiz(new_root_media):

    with open(config_path, "r", encoding="utf-8") as file:
        data = json.load(file)

    data["general"]["root_media"] = new_root_media

    with open(config_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)
        
def cargar_fondo_predeterminado():
    config = cargar_configuracion()
    background_default = config.get("general", {}).get("background_default", "")
    return background_default

def editar_fondo_predeterminado(new_background):

    with open(config_path, "r", encoding="utf-8") as file:
        data = json.load(file)

    data["general"]["background_default"] = new_background

    with open(config_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)
        
def cargar_biblia_predeterminado():
    config = cargar_configuracion()
    bible_default = config.get("general", {}).get("bible_default", "")
    return bible_default

def editar_biblia_predeterminado(new_bible):

    with open(config_path, "r", encoding="utf-8") as file:
        data = json.load(file)

    data["general"]["bible_default"] = new_bible

    with open(config_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)

def cargar_estilo_actual():
    config = cargar_configuracion()
    estilo_actual = config.get("general", {}).get("selected_theme", "")
    return estilo_actual

def editar_estilo_actual(new_theme):

    with open(config_path, "r", encoding="utf-8") as file:
        data = json.load(file)

    data["general"]["selected_theme"] = new_theme

    with open(config_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)

def cargar_tamano_actual():
    config = cargar_configuracion()
    tamano_actual = config.get("general", {}).get("point_font", "")
    return tamano_actual

def editar_tamano_actual(new_point_font):

    with open(config_path, "r", encoding="utf-8") as file:
        data = json.load(file)

    data["general"]["point_font"] = new_point_font

    with open(config_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)

def cargar_resolucion_actual():
    config = cargar_configuracion()
    resolucion_actual = config.get("general", {}).get("resolution_max", "")
    return resolucion_actual

def editar_resolucion_actual(new_resolution_max):

    with open(config_path, "r", encoding="utf-8") as file:
        data = json.load(file)

    data["general"]["resolution_max"] = new_resolution_max

    with open(config_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)



