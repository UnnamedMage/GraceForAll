from enum import Enum
from PySide6.QtCore import Signal, QObject
from services.json_service import cargar_tamano_actual

tamano_actual = cargar_tamano_actual()
class SY(Enum):
    #datos_predeterminados
    VFONT_0 = 2
    VFONT_1 = 3
    VFONT_2 = 3.5
    VFONT_3 = 5
    
    @property
    def value(self):
        if self.name.startswith('VFONT_'):
            return int(tamano_actual * self._value_)
        return self._value_
    
    SFONT_1 = 12
    SFONT_2 = 14
    SFONT_3 = 20
    #Objetos
    WIDGET = "widget"
    FRAME = "frame"
    V = "vertical"
    H = "horizontal"
    TEXT = "texto"
    SQUARE = "cuadrado"
    DSQUARE = "cuadrado_doble"
    RECTANGLE = "rectangulo"
    VERSICLE = "versiculo"
    MEDIA = "media"
    SONG= "cancion"
    PREVIEW = "prevista"
    ONLIVE = "envivo"
    IMAGE = "imagen"
    VIDEO = "video"
    
    
class SYsignals(QObject):
    enter_pressed = Signal(object)

class Media():
    item = None
    name = ""
   
class Versicle():
    versicle = ""
    text = ""

class SYplaylist():
    def __init__(self):
        self.base_name = "Aun sin nombre"
        self.base_list = []
        self.temp_name = "Aun sin nombre"
        self.temp_list = []
        
        self.state = False
        
    def compare(self, songs_list):
        self.temp_list = songs_list
        if self.temp_list == self.base_list:
            self.state = False
        else:
            self.state = True
    def new(self):
        self.base_name ="Aun sin nombre"
        self.base_list = []
        self.temp_list = []
        self.state = False
    def open(self, name, list):
        self.base_name = name
        self.base_list = list
        self.state = False
    def save(self, name):
        self.base_name = name
        self.base_list = self.temp_list
        self.state = False

    
    
    
    
    