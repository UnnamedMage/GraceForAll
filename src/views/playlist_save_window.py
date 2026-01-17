from PySide6.QtWidgets import QDialog, QMessageBox,QGraphicsOpacityEffect
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QParallelAnimationGroup, QPoint, QTimer
from components.ui_elements import SYgrid, SYbuttonbox, SYlineedit, SYmessagebox, SYlabel
from core.models import SY
from core.helpers import SYwindowsize, SYanimationwindow, SYcreatelistinst
from services.db_service import is_title_playlist_unique, create_playlist
from datetime import datetime

class VentanaGuardarPlaylist(QDialog):
    def __init__(self, parent = None, lista_canciones=None):
        super().__init__(parent)
        self.setWindowTitle("Agregar playlist")
        self.setWindowFlags(Qt.Window | Qt.CustomizeWindowHint | Qt.WindowTitleHint | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        SYwindowsize(self, 3.5, 3.5)
        self.lista_canciones = lista_canciones
        self.crear_instancias()
        self.almacenar_widgets()
        self.definir_posicion()
        self.conectar_eventos()
        self.ajustes_iniciales()
        
    def crear_instancias(self):
        self.identificador_programa_inst =  SYlabel(self, "Guardar playlist", nombre="encabezado",tamano=SY.SFONT_1)
        self.control_ventana_instE = SYbuttonbox(self, 1, SY.WIDGET, SY.H, ["close"], nombre="btnencabezado", tamano=SY.SFONT_3, forma=SY.SQUARE, icon=True, alineacion=Qt.AlignRight)
        
        self.info_playlist_inst =           SYlabel(self, f"Fecha de creacion: {datetime.now().strftime("%d/%m/%Y")}\n\nNumero de canciones: {len(self.lista_canciones)}",SY.VFONT_2)
        
        self.nombre_playlist_inst =         SYlineedit(self,"Nombre de la playlist...", SY.VFONT_3)
        
        self.control_cancion_instE =          SYbuttonbox(self,2,SY.WIDGET, SY.H,["Guardar","Salir"])
    
        self.instancia_normal =           SYcreatelistinst(self, "_inst")
        self.instancia_especial =         SYcreatelistinst(self, "_instE")
    
    def almacenar_widgets(self):
        self.identificador_programa =                           self.identificador_programa_inst.get_widget()
        
        self.control_ventana_ctn, self.control_ventana_btn =    self.control_ventana_instE.get_widgets()
        
        self.info_playlist =                                    self.info_playlist_inst.get_widget()
        
        self.nombre_playlist =                                  self.nombre_playlist_inst.get_widget()
        
        self.control_cancion_ctn, self.control_cancion_btn =    self.control_cancion_instE.get_widgets()
        
    def definir_posicion(self):
        self.pie =          SYgrid(1,2,[1],[1,0], [[self.control_cancion_ctn, 0,1]])
        self.cuerpo =       SYgrid(2,1,[1],[1], [[self.info_playlist, 0,0]])
        self.encabezado =   SYgrid(1,3,[1],[9,130,9],[[self.identificador_programa,0,1, Qt.AlignHCenter],[self.control_ventana_ctn,0,2]])
        self.centro =       SYgrid(3,1,[30,15,20],[1],[[self.cuerpo,0,0],[self.nombre_playlist,1,0],[self.pie, 2, 0]],(10,10,10,10),10)
        self.borde =        SYgrid(1,1,[1],[1],[[self.centro,0,0, None, "Fondo"]], (3,3,3,3))
        self.base =         SYgrid(2,1,[10,65],[1],[[self.encabezado, 0,0,None, "encabezado"], [self.borde,1,0, None, "complemento"]],(10,3,10,10))
        self.ventana =      SYgrid(1,1,[1],[1],[[self.base,0,0,None,"base_secundaria"]])
        self.setLayout(self.ventana)
    
    def conectar_eventos(self):
        self.control_ventana_btn[0].clicked.connect(self.cerrar_ventana)
        self.control_cancion_btn[0].clicked.connect(self.guardar_playlist)
        self.control_cancion_btn[1].clicked.connect(self.cerrar_ventana)
    
    def ajustes_iniciales(self):
        self.nombre = None
        self.resize_widgets()
        SYanimationwindow(self)
        
        
    def cerrar_ventana(self):
        self.close()
    def guardar_playlist(self):
        nuevo_titulo = self.nombre_playlist.text()
        if nuevo_titulo == "":
                msg = SYmessagebox(self,QMessageBox.Warning, "No ha sido nombrada", "Por favor, ingrese un nombre a la playlist para continuar", QMessageBox.Ok)
                msg.exec_()
        else:
            if is_title_playlist_unique(nuevo_titulo):
                    create_playlist(nuevo_titulo, self.lista_canciones)
                    self.nombre = nuevo_titulo
                    self.close()
            else:
                msg = SYmessagebox(self,QMessageBox.Warning, "Ese nombre ya existe", "Por favor, ingrese un nombre diferente a la playlist para continuar", QMessageBox.Ok)
                msg.exec_()
    
    def colapsar_widgets(self):
        for instancia in self.instancia_especial:
            if hasattr(instancia, 'collapse'):
                instancia.collapse()
   
    def resize_widgets(self):
        for instancia in self.instancia_normal:
            if hasattr(instancia, 'resize'):
                instancia.resize(self)
                
        def restraso():
            for instancia in self.instancia_especial:
                if hasattr(instancia, 'resize'):
                    instancia.resize(self)
        QTimer.singleShot(1000, restraso)
        
    def update_window(self):
        self.colapsar_widgets()
        def restraso():
            SYwindowsize(self, 3.5, 4)
            self.layout().invalidate()
            self.layout().activate()
            self.update()
            self.resize_widgets()
        QTimer.singleShot(500, restraso)