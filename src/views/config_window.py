from PySide6.QtWidgets import QDialog,QFileDialog, QMessageBox
from PySide6.QtCore import Qt, QTimer
from components.ui_elements import SYgrid, SYbuttonbox,SYlabel, SYstacked, SYcombobox, SYmessagebox
from core.models import SY
from core.helpers import SYwindowsize,SYanimationwindow, SYcreatelistinst
from services.db_service import import_bible_tables
from services.json_service import (cargar_estilo_actual, editar_estilo_actual, 
                                   cargar_tamano_actual, editar_tamano_actual,
                                   cargar_resolucion_actual, editar_resolucion_actual)

class VentanaConfiguraciones(QDialog):
    def __init__(self, parent = None, app = None, funcion_resize = None):
        super().__init__(parent)
        self.setWindowTitle("Configuraciones")
        self.setWindowFlags(Qt.Window | Qt.CustomizeWindowHint | Qt.WindowTitleHint | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        SYwindowsize(self, 3, 1.5)
        self.app = app
        self.funcion_resize = funcion_resize
        self.crear_instancias()
        self.almacenar_widgets()
        self.definir_posicion()
        self.conectar_eventos()
        self.ajustes_iniciales()

    def crear_instancias(self):
        self.diccionario_temas =              self.app.diccionario_temas
        self.diccionario_tamano =               self.app.diccionario_tamanos
        self.diccionario_resoluciones =         self.app.diccionario_resoluciones
        self.identificador_programa_inst =      SYlabel(self, "Configuraciones", nombre="encabezado",tamano=SY.SFONT_1)
        self.control_ventana_instE =             SYbuttonbox(self,1, SY.WIDGET, SY.H, ["close"],nombre="btnencabezado",tamano=SY.SFONT_3, forma=SY.SQUARE, icon=True,alineacion=Qt.AlignRight)
        self.control_config_instE =              SYbuttonbox(self,2, SY.WIDGET, SY.V, ["Estilo","Herramientas\ndel sistema"],nombre="menu_secundario",tamano=SY.SFONT_3,alineacion=Qt.AlignTop)
        
        self.identificador_tema_inst =          SYlabel(self, "Estilo de colores", tamano=SY.SFONT_1)
        self.seleccionador_tema_inst =          SYcombobox(self, list(self.diccionario_temas.keys()), tamano=SY.SFONT_2)
        self.control_tema_instE =                SYbuttonbox(self,1, SY.WIDGET, SY.H, ["Aplicar"],tamano=SY.SFONT_2, alineacion= Qt.AlignHCenter)
        
        self.identificador_tamano_inst =        SYlabel(self, "Tamaño de la fuente", tamano=SY.SFONT_1)
        self.seleccionador_tamano_inst =        SYcombobox(self, list(self.diccionario_tamano.keys()), tamano=SY.SFONT_2)
        self.control_tamano_instE =              SYbuttonbox(self,1, SY.WIDGET, SY.H, ["Aplicar"],tamano=SY.SFONT_2, alineacion= Qt.AlignHCenter)
        
        self.identificador_resolucion_inst =    SYlabel(self, "Resolucion de conversion", tamano=SY.SFONT_1)
        self.seleccionador_resolucion_inst =    SYcombobox(self, list(self.diccionario_resoluciones.keys()), tamano=SY.SFONT_2)
        self.control_resolucion_instE =          SYbuttonbox(self,1, SY.WIDGET, SY.H, ["Aplicar"],tamano=SY.SFONT_2, alineacion= Qt.AlignHCenter)
        
        self.identificador_biblia_inst =        SYlabel(self, "Agregar nueva Biblia", tamano=SY.SFONT_1)
        self.control_biblia_instE =              SYbuttonbox(self,1, SY.WIDGET, SY.H, ["Buscar"],tamano=SY.SFONT_2)

        self.instancia_normal =           SYcreatelistinst(self, "_inst")
        self.instancia_especial =         SYcreatelistinst(self, "_instE")
        
    def almacenar_widgets(self):
        self.identificador_programa =                           self.identificador_programa_inst.get_widget()
        self.control_ventana_ctn, self.control_ventana_btn =    self.control_ventana_instE.get_widgets()
        self.control_config_ctn, self.control_config_btn =      self.control_config_instE.get_widgets()
        self.identificador_tema =                               self.identificador_tema_inst.get_widget()
        self.seleccionador_tema =                               self.seleccionador_tema_inst.get_widget()
        self.control_tema_ctn, self.control_tema_btn =          self.control_tema_instE.get_widgets()
        self.identificador_tamano =                               self.identificador_tamano_inst.get_widget()
        self.seleccionador_tamano =                               self.seleccionador_tamano_inst.get_widget()
        self.control_tamano_ctn, self.control_tamano_btn =        self.control_tamano_instE.get_widgets()
        self.identificador_resolucion =                           self.identificador_resolucion_inst.get_widget()
        self.seleccionador_resolucion =                           self.seleccionador_resolucion_inst.get_widget()
        self.control_resolucion_ctn, self.control_resolucion_btn = self.control_resolucion_instE.get_widgets()
        self.identificador_biblia =                               self.identificador_biblia_inst.get_widget()
        self.control_biblia_ctn, self.control_biblia_btn =         self.control_biblia_instE.get_widgets()


    def definir_posicion(self):
        self.biblia =               SYgrid(1,1,[1],[1],[[self.control_biblia_ctn,0,0]], (5,5,5,5),5)
        self.resolucion =           SYgrid(1,2,[1],[0,1],[[self.seleccionador_resolucion,0,0, Qt.AlignHCenter],[self.control_resolucion_ctn,0,1]], (5,5,5,5),5)
        self.herramientas=          SYgrid(6,1,[1,1,2,1,2,15],[1], [[self.identificador_resolucion,1,0, Qt.AlignBottom|Qt.AlignLeft],[self.resolucion,2,0, None, "grid_conjunto"],
                                                                    [self.identificador_biblia,3,0, Qt.AlignBottom|Qt.AlignLeft],[self.biblia,4,0, None, "grid_conjunto"]],(10,10,10,10), 10)
        self.fondo_herramientas =   SYgrid(1,1,[1],[1],[[self.herramientas,0,0, None, "Fondo"]])
        
        self.tamano =               SYgrid(1,2,[1],[0,1],[[self.seleccionador_tamano,0,0, Qt.AlignHCenter],[self.control_tamano_ctn,0,1]], (5,5,5,5),5)
        self.tema =                 SYgrid(1,2,[1],[0,1],[[self.seleccionador_tema,0,0, Qt.AlignHCenter],[self.control_tema_ctn,0,1]], (5,5,5,5),5)
        self.estilo =               SYgrid(6,1,[1,1,2,1,2,15],[1],[[self.identificador_tema,1,0, Qt.AlignBottom|Qt.AlignLeft],[self.tema,2,0, None, "Fondo"],
                                                                  [self.identificador_tamano,3,0, Qt.AlignBottom|Qt.AlignLeft],[self.tamano,4,0, None, "Fondo"]],(10,10,10,10), 10)
        self.fondo_estilo =         SYgrid(1,1,[1],[1],[[self.estilo,0,0, None, "Fondo"]])
        self.espacio_funciones =    SYstacked(2, [[self.fondo_estilo,0], [self.fondo_herramientas,1]])
        self.fondo_config =         SYgrid(1,1,[1],[1],[[self.control_config_ctn,0,0]], (15,15,15,15))
        self.centro =               SYgrid(1,2,[1],[1,3],[[self.fondo_config,0,0, None,"Fondo"], [self.espacio_funciones,0,1]], (3,3,3,3), 3)
        self.encabezado =           SYgrid(1,3,[1],[1,8,1],[[self.identificador_programa,0,1, Qt.AlignHCenter],[self.control_ventana_ctn,0,2]])
        self.base =                 SYgrid(2, 1, [2,38], [1], [[self.encabezado,0,0,None, "encabezado"], [self.centro,1,0, None, "complemento"]],(10,3,10,10))
        self.ventana =              SYgrid(1,1,[1],[1],[[self.base,0,0,None, "base_secundaria"]])
        self.setLayout(self.ventana)

    def conectar_eventos(self):
        self.control_ventana_btn[0].clicked.connect(self.cerrar_ventana)
        self.control_config_btn[0].clicked.connect(lambda: self.espacio_funciones.setCurrentIndex(0))
        self.control_config_btn[1].clicked.connect(lambda: self.espacio_funciones.setCurrentIndex(1))
        self.control_tema_btn[0].clicked.connect(self.aplicar_tema)
        self.control_tamano_btn[0].clicked.connect(self.aplicar_tamano)
        self.control_resolucion_btn[0].clicked.connect(self.aplicar_resolucion)
        self.control_biblia_btn[0].clicked.connect(self.agregar_biblia)
        
    def ajustes_iniciales(self):
        estilo_actual = cargar_estilo_actual()
        if estilo_actual in self.diccionario_temas.values():
            estilo_actual_espanol = list(self.diccionario_temas.keys())[list(self.diccionario_temas.values()).index(estilo_actual)]
            self.seleccionador_tema.setCurrentText(estilo_actual_espanol)
        self.identificador_tema.setAlignment(Qt.AlignLeft)
        tamano_actual = cargar_tamano_actual()
        if tamano_actual in self.diccionario_tamano.values():
            tamano_actual_nombre = list(self.diccionario_tamano.keys())[list(self.diccionario_tamano.values()).index(tamano_actual)]
            self.seleccionador_tamano.setCurrentText(tamano_actual_nombre)
        self.identificador_tamano.setAlignment(Qt.AlignLeft)
        resolucion_actual = cargar_resolucion_actual()
        if resolucion_actual in self.diccionario_resoluciones.values():
            resolucion_actual_nombre = list(self.diccionario_resoluciones.keys())[list(self.diccionario_resoluciones.values()).index(resolucion_actual)]
            self.seleccionador_resolucion.setCurrentText(resolucion_actual_nombre)
        self.identificador_resolucion.setAlignment(Qt.AlignLeft)
        
        self.resize_widgets()
        SYanimationwindow(self)
            
    def aplicar_tema(self):
        estilo_actual_espanol = self.seleccionador_tema.currentText()
        
        if estilo_actual_espanol in self.diccionario_temas:
            estilo_actual = self.diccionario_temas[estilo_actual_espanol]
            editar_estilo_actual(estilo_actual)
            self.app.apply_theme()
            self.funcion_resize()

    def aplicar_tamano(self):
        tamano_actual_nombre = self.seleccionador_tamano.currentText()
        if tamano_actual_nombre in self.diccionario_tamano:
            tamano_actual = self.diccionario_tamano[tamano_actual_nombre]
            editar_tamano_actual(tamano_actual)
            self.funcion_resize()

    def aplicar_resolucion(self):
        resolucion_actual_nombre = self.seleccionador_resolucion.currentText()
        if resolucion_actual_nombre in self.diccionario_resoluciones:
            resolucion_actual = self.diccionario_resoluciones[resolucion_actual_nombre]
            editar_resolucion_actual(resolucion_actual)


    def agregar_biblia(self):
        ruta_biblia, _ = QFileDialog.getOpenFileName(self, "Seleccionar Biblia", "", "Archivos de Biblia (*.db)")
        if ruta_biblia:
            
            biblias_importadas = import_bible_tables(ruta_biblia)
            if biblias_importadas:
                msg = SYmessagebox(self, QMessageBox.Information,"Proceso completado",f"Biblia importada correctamente: {', '.join(biblias_importadas)}", QMessageBox.Ok)
                msg.exec()
            else:
                msg = SYmessagebox(self, QMessageBox.Warning, "Proceso Fallido", "No se importo ninguna biblia", QMessageBox.Ok)
                msg.exec()

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
            SYwindowsize(self, 3, 1.5)
            self.layout().invalidate()
            self.layout().activate()
            self.update()
            self.resize_widgets()
        QTimer.singleShot(500, restraso)
        