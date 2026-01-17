from PySide6.QtWidgets import QDialog, QMessageBox, QHeaderView, QGraphicsOpacityEffect
from PySide6.QtCore import Qt, QSortFilterProxyModel, QTimer,QPropertyAnimation, QEasingCurve, QParallelAnimationGroup, QPoint
from PySide6.QtGui import QStandardItem
from components.ui_elements import SYgrid, SYbuttonbox, SYlineedit, SYmessagebox, SYtreeview, SYlabel
from core.models import SY
from core.helpers import SYwindowsize, SYanimationwindow, SYcreatelistinst
from services.db_service import get_all_playlist, delete_playlist, get_songs_from_playlist

class VentanaAbrirPlaylist(QDialog):
    def __init__(self, parent = None):
        super().__init__(parent)
        self.setWindowTitle("Abrir playlist")
        self.setWindowFlags(Qt.Window | Qt.CustomizeWindowHint | Qt.WindowTitleHint | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        SYwindowsize(self, 3.5, 3)
        self.crear_instancias()
        self.almacenar_widgets()
        self.definir_posicion()
        self.conectar_eventos()
        self.ajustes_iniciales()

    def crear_instancias(self):
        self.identificador_programa_inst =  SYlabel(self, "Abrir playlist", nombre="encabezado",tamano=SY.SFONT_1)
        self.control_ventana_instE =         SYbuttonbox(self,1, SY.WIDGET, SY.H, ["close"],nombre="btnencabezado",tamano=SY.VFONT_3, icon=True)
        
        self.buscador_playlist_inst =       SYlineedit(self, "Busqueda por titulo...")
        self.tv_playlist_inst =             SYtreeview(self,2)
        
        self.control_playlist1_instE =       SYbuttonbox(self,1,SY.WIDGET, SY.H,["Eliminar"],alineacion=Qt.AlignLeft)
        self.control_playlist2_instE =       SYbuttonbox(self,2,SY.WIDGET, SY.H,["  Abrir  ","  Salir  "],alineacion=Qt.AlignRight)
    
        self.instancia_normal =           SYcreatelistinst(self, "_inst")
        self.instancia_especial =         SYcreatelistinst(self, "_instE")
    
    def almacenar_widgets(self):
        self.identificador_programa =                               self.identificador_programa_inst.get_widget()
        self.control_ventana_ctn, self.control_ventana_btn =        self.control_ventana_instE.get_widgets()
        
        self.buscador_playlist =                                    self.buscador_playlist_inst.get_widget()
        self.tv_playlist, self.model_playlist =                     self.tv_playlist_inst.get_widgets()
        
        self.control_playlist1_ctn, self.control_playlist1_btn =    self.control_playlist1_instE.get_widgets()
        self.control_playlist2_ctn, self.control_playlist2_btn =    self.control_playlist2_instE.get_widgets()
        
    def definir_posicion(self):
        self.botones =      SYgrid(1,3, [1], [0,1,0], [[self.control_playlist1_ctn,0,0], [self.control_playlist2_ctn,0,2]])
        self.encabezado =   SYgrid(1,3,[1],[10,137,10],[[self.identificador_programa,0,1, Qt.AlignHCenter],[self.control_ventana_ctn,0,2]])
        self.centro =       SYgrid(3,1,[10,63,20],[1],[[self.buscador_playlist, 0,0], [self.tv_playlist, 1,0], [self.botones, 2,0]],(10,10,10,10),10)
        self.borde =        SYgrid(1,1,[1],[1],[[self.centro,0,0, None, "Fondo"]], (3,3,3,3))
        self.base =         SYgrid(2, 1, [10,93], [1], [[self.encabezado,0,0,None, "encabezado"], [self.borde,1,0, None, "complemento"]],(10,3,10,10))
        self.ventana =      SYgrid(1,1,[1],[1],[[self.base,0,0,None, "base_secundaria"]])
        self.setLayout(self.ventana)
    
    def conectar_eventos(self):
        self.control_ventana_btn[0].clicked.connect(self.cerrar_ventana)
        
        self.buscador_playlist.textChanged.connect(lambda texto: self.filtrar_canciones(texto))
        
        
        self.tv_playlist.doubleClicked.connect(self.abrir_playlist)
        
        self.control_playlist1_btn[0].clicked.connect(self.borrar_playlist)
        self.control_playlist2_btn[0].clicked.connect(self.abrir_playlist)
        self.control_playlist2_btn[1].clicked.connect(self.cerrar_ventana)
         
    def ajustes_iniciales(self):
        self.nombre_playlist = None
        self.lista_canciones = None
        self.recargar_elementos()
        self.tv_playlist.header().setStretchLastSection(False)
        
        
        self.model_playlist_proxy = QSortFilterProxyModel()
        self.model_playlist_proxy.setSourceModel(self.model_playlist)
        self.model_playlist_proxy.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.model_playlist_proxy.setFilterKeyColumn(0)
        self.tv_playlist.setModel(self.model_playlist_proxy)
        
        self.resize_widgets()
        
        SYanimationwindow(self)
    
            
    def recargar_elementos(self):
        self.model_playlist.clear()
        datos = get_all_playlist()
        if datos == None:
            return
        lista1, lista2 = datos
        for dato1, dato2 in zip(lista1, lista2):
            item1 = QStandardItem(dato1)
            item2 = QStandardItem(dato2)
            self.model_playlist.appendRow([item1, item2])
        self.tv_playlist.header().setSectionResizeMode(0, QHeaderView.Stretch)
        self.tv_playlist.header().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        
    def cerrar_ventana(self):
        self.close()     
            
    def borrar_playlist(self):
        selected_indexes = self.tv_playlist.selectionModel().selectedIndexes()
        if selected_indexes:
            nombre_playlist = self.model_playlist.itemFromIndex(self.model_playlist_proxy.mapToSource(selected_indexes[0])).text()
            msg = SYmessagebox(self,QMessageBox.Warning, "A punto de borrar playlist", f"¿Desea borrar la playlist {nombre_playlist}?", QMessageBox.Yes | QMessageBox.No)
            response = msg.exec_()
            if response == QMessageBox.Yes:
                delete_playlist(nombre_playlist)
                self.recargar_elementos()
                self.tv_playlist.selectionModel().clearSelection()
            
    def abrir_playlist(self):
        selected_indexes = self.tv_playlist.selectionModel().selectedIndexes()
        if selected_indexes:
            self.nombre_playlist = self.model_playlist.itemFromIndex(self.model_playlist_proxy.mapToSource(selected_indexes[0])).text()
            self.lista_canciones = get_songs_from_playlist(self.nombre_playlist)
            self.close()
                
    def filtrar_canciones(self, text):
        self.model_playlist_proxy.setFilterRegularExpression(text)
    
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
        
   