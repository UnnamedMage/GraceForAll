from PySide6.QtWidgets import QDialog, QGraphicsOpacityEffect
from PySide6.QtCore import Qt,QTimer, QPropertyAnimation, QEasingCurve, QParallelAnimationGroup, QPoint
from components.ui_elements import SYgrid, SYbuttonbox, SYlabel
from core.models import SY
from core.helpers import SYwindowsize, SYanimationwindow, SYcreatelistinst

class VentanaAcercaDe(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Acerca de GraceForAll")
        self.setWindowFlags(Qt.Window | Qt.CustomizeWindowHint | Qt.WindowTitleHint | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        SYwindowsize(self, 3.5, 3)
        self.crear_instancias()
        self.almacenar_widgets()
        self.definir_posicion()
        self.conectar_eventos()
        self.ajustes_iniciales()

    def crear_instancias(self):
        self.identificador_programa_inst = SYlabel(self, "Acerca de...", nombre="encabezado", tamano=SY.SFONT_1)
        self.control_ventana_instE = SYbuttonbox(self, 1, SY.WIDGET, SY.H, ["close"], nombre="btnencabezado", tamano=SY.SFONT_3, forma=SY.SQUARE, icon=True, alineacion=Qt.AlignRight)
        
        self.logo_inst = SYlabel(self, "GraceForAll.png", imagen=True)
        
        # Información
        self.titulo_inst = SYlabel(self, "GraceForAll", tamano=SY.SFONT_3)
        self.version_inst = SYlabel(self, "Versión 1.0.0", tamano=SY.SFONT_2)
        self.informacion_inst = SYlabel(self, "Informacion del desarrollador", tamano=SY.SFONT_3)
        self.contacto_inst = SYlabel(self, "Izacar Alvarez:", tamano=SY.SFONT_2)
        self.datos_contacto_inst = SYlabel(self, "izacar.alvarez@gmail.com", tamano=SY.SFONT_2, link=True)
        self.donaciones_inst = SYlabel(self, "Donaciones: ", tamano=SY.SFONT_2)
        self.datos_donaciones_inst = SYlabel(self, "https://paypal.me/AppGraceForAll", tamano=SY.SFONT_2, link=True)

        self.instancia_especial = SYcreatelistinst(self, "_instE")
        self.instancia_normal = SYcreatelistinst(self, "_inst")
        
    def almacenar_widgets(self):
        self.identificador_programa =                           self.identificador_programa_inst.get_widget()
        self.control_ventana_ctn, self.control_ventana_btn =    self.control_ventana_instE.get_widgets()
        self.logo =                                             self.logo_inst.get_widget()
        self.titulo =                                           self.titulo_inst.get_widget()
        self.version =                                          self.version_inst.get_widget()
        self.informacion =                                      self.informacion_inst.get_widget()
        self.contacto =                                         self.contacto_inst.get_widget()
        self.datos_contacto =                                   self.datos_contacto_inst.get_widget()
        self.donaciones =                                       self.donaciones_inst.get_widget()
        self.datos_donaciones =                                 self.datos_donaciones_inst.get_widget()


    def definir_posicion(self):
        self.info_contacto = SYgrid(2,2,[1,1],[0,1],[[self.contacto,0,0],[self.datos_contacto,0,1],[self.donaciones,1,0],[self.datos_donaciones,1,1]], (0,0,0,0),20)
        self.info_programa = SYgrid(2,1,[1,1],[1],[[self.titulo,0,0, Qt.AlignBottom],[self.version,1,0, Qt.AlignTop]], (0,0,0,0),10)
        self.programa = SYgrid(1,2,[1],[1,3],[[self.logo,0,0],[self.info_programa,0,1]], (10,10,10,10),10)
        self.centro =       SYgrid(3,1,[8,2,8],[1],[[self.programa,0,0],[self.informacion,1,0], [self.info_contacto,2,0]],(10,10,10,10),10)
        self.encabezado =   SYgrid(1,3,[1],[10,137,10],[[self.identificador_programa,0,1, Qt.AlignHCenter],[self.control_ventana_ctn,0,2]])
        self.borde =        SYgrid(1,1,[1],[1],[[self.centro,0,0, None, "Fondo"]], (3,3,3,3))
        self.base =         SYgrid(2, 1, [10,93], [1], [[self.encabezado,0,0,None, "encabezado"], [self.borde,1,0, None, "complemento"]],(10,3,10,10))
        self.ventana =      SYgrid(1,1,[1],[1],[[self.base,0,0,None, "base_secundaria"]])
        self.setLayout(self.ventana)

    def conectar_eventos(self):
        self.control_ventana_btn[0].clicked.connect(self.cerrar_ventana)

    def ajustes_iniciales(self):
        self.resize_widgets()
        SYanimationwindow(self)
        
    def cerrar_ventana(self):
        self.close()
    
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
            SYwindowsize(self, 3.5, 3)
            self.layout().invalidate()
            self.layout().activate()
            self.update()
            self.resize_widgets()
        QTimer.singleShot(500, restraso)     