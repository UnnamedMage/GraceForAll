from PySide6.QtWidgets import QWidget, QMainWindow, QMessageBox
from PySide6.QtCore import Qt, QItemSelection, QPoint, QItemSelectionModel, QTimer
from PySide6.QtGui import QStandardItem, QKeySequence, QShortcut,QPainter, QColor

from components.ui_elements import (SYgrid, SYstacked, SYbuttonbox, SYlabel, SYtreeview,SYlineedit,SYtoolbar,
                                    SYprojection, SYmessagebox, SYmenu, SYmedialist, SYbackgroundslist, SYvideocontrol)
from core.models import SY, SYplaylist
from core.helpers import SYmediarecognize, SYwindoworigen, SYwindowextra, SYanimationwindow, SYcreatelistinst
from services.db_service import  (get_all_song_titles, is_title_playlist_unique, delete_song,
                                     update_data_playlist, get_book_by_version, get_all_bibles_versions)
from services.json_service import editar_fondo_predeterminado, editar_biblia_predeterminado, cargar_biblia_predeterminado
from views.song_window import VentanaCancion
from views.projection_window import VentanaProyeccion
from views.playlist_save_window import VentanaGuardarPlaylist
from views.playlist_open_window import VentanaAbrirPlaylist
from views.config_window import VentanaConfiguraciones
from views.about_window import VentanaAcercaDe
import unicodedata

class VentanaPrincipal(QMainWindow):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.setWindowTitle("GraceForAll")
        self.setWindowFlags(Qt.Window | Qt.CustomizeWindowHint | Qt.WindowTitleHint | Qt.FramelessWindowHint)
        self.geometria_disponible = SYwindoworigen()
        self.setGeometry(self.geometria_disponible)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.crear_instancias()
        self.almacenar_elementos()
        self.definir_posicion()
        self.conectar_eventos()
        self.definir_atajos()
        self.ajustes_iniciales()
        
     
    def crear_instancias(self):
        self.alt_menu_principal1_instE =      SYtoolbar(self,5,SY.WIDGET,SY.V,["\nNueva playlist","\nAbrir playlist...", "\nGuardar playlist",
                                                                               "\nGuardar como...", "\nNueva cancion"],icon=["new_playlist","open_playlist","save_playlist","save_as","new_song"],nombre="menu_principal",forma=SY.TEXT,alineacion=Qt.AlignTop, al_texto=Qt.AlignLeft|Qt.AlignVCenter)
        self.alt_menu_principal2_instE =      SYtoolbar(self,2,SY.WIDGET,SY.V,["\nConfiguracion", "\nAcerca de..."],icon=["settings","info"],nombre="menu_principal",forma=SY.TEXT,alineacion=Qt.AlignBottom, al_texto=Qt.AlignLeft|Qt.AlignVCenter)
        
        self.logo_inst =                     SYlabel(self, "GraceForAllnegative",imagen=True, tipo="svg")
        
        self.identificador_programa_inst =  SYlabel(self, "Grace For All", nombre="encabezado",tamano=SY.SFONT_3)
        self.control_ventana_instE =         SYbuttonbox(self,2,SY.WIDGET,SY.H, ["minimize", "close"],forma=SY.RECTANGLE,nombre="btnencabezado",icon=True, alineacion=Qt.AlignRight)
        
        self.control_fondo_instE =           SYbuttonbox(self,1,SY.WIDGET,SY.H, ["Fondo pred."], nombre="btnsistema",alineacion=Qt.AlignRight)
        self.menu_fondos_inst =             SYbackgroundslist(self)
        
        self.identidicador_playlist_inst =  SYlabel(self,"Playlist",tamano=SY.VFONT_2)
        self.tv_playlist_inst =             SYtreeview(self,1)
        self.playlist =                     SYplaylist()
        self.control_playlist1_instE =       SYbuttonbox(self,2,SY.WIDGET,SY.V,["upward","downward"],nombre="btnsistema",forma=SY.SQUARE,icon=True,alineacion=Qt.AlignTop)
        self.control_playlist2_instE =       SYbuttonbox(self,2,SY.WIDGET,SY.V,["add","remove"] ,nombre="btnsistema",forma=SY.SQUARE,icon=True, alineacion=Qt.AlignBottom)
        
        self.control_contenido_instE =       SYbuttonbox(self,3,SY.WIDGET,SY.H,["Canciones","Biblia","Media"],nombre="btnsistema")
        
        self.buscador_canciones_inst =      SYlineedit(self, "Busqueda por titulo...")
        self.tv_canciones_inst =            SYtreeview(self,1)
        
        self.seleccionador_biblia_instE =    SYbuttonbox(self,1,SY.WIDGET, SY.H, ["Seleccionar biblia"], tamano=SY.VFONT_0, alineacion=Qt.AlignLeft)
        self.buscador_versiculos_inst =     SYlineedit(self, "Busqueda versiculos...")
        self.tv_versiculos_inst =           SYtreeview(self,2,SY.VFONT_2)
        
        self.seleccionador_media_inst =     SYmedialist(self)
        
        
        self.control_prevista_instE =        SYbuttonbox(self, 1, SY.WIDGET, SY.H, ["go"], nombre="btnsistema",forma=SY.SQUARE,icon=True, alineacion=Qt.AlignRight)
        self.identidicador_prevista_inst =  SYlabel(self,"Prevista",tamano=SY.VFONT_2)
       
        self.tv_prevista_inst =             SYtreeview(self,1,SY.VFONT_2)
        self.control_media_prevista_inst =  SYvideocontrol(self)
        
        self.sim_prevista_instE =            SYprojection("")
        
        
        self.control_envivo1_instE =         SYbuttonbox(self, 2, SY.WIDGET, SY.H, ["Fondo", "Negro"],nombre="btnsistema",alineacion=Qt.AlignRight)
        self.control_envivo2_instE =         SYbuttonbox(self, 1, SY.WIDGET, SY.H, ["Mostrar"],nombre="btnsistema")
        
        self.identidicador_envivo_inst =    SYlabel(self,"En vivo",tamano=SY.VFONT_2)
        
        self.tv_envivo_inst =               SYtreeview(self,1,SY.VFONT_2)
        self.control_media_envivo_inst =    SYvideocontrol(self)
        
        self.sim_envivo_instE =              SYprojection("")
        
        self.instancia_especial =           SYcreatelistinst(self, "_instE")
        self.instancia_normal =           SYcreatelistinst(self, "_inst")
        
    def almacenar_elementos(self):
        self.ventana =                                                      QWidget(self)
        self.temporizador_sistema =                                         QTimer()
        
        self.alt_menu_principal1_ctn, self.alt_menu_principal1_btn =          self.alt_menu_principal1_instE.get_widgets()
        self.alt_menu_principal2_ctn, self.alt_menu_principal2_btn =          self.alt_menu_principal2_instE.get_widgets()
        
        self.logo =                                                         self.logo_inst.get_widget()
        
        self.identificador_programa =                                       self.identificador_programa_inst.get_widget()
        self.control_ventana_ctn, self.control_ventana_btn =                self.control_ventana_instE.get_widgets()
        
        
        self.control_fondo_cnt, self.control_fondo_btn =                    self.control_fondo_instE.get_widgets()
        self.menu_fondo_cnt, self.menu_fondo_list, self.menu_fondo_btn =    self.menu_fondos_inst.get_widgets()
        
        self.identidicador_playlist =                                       self.identidicador_playlist_inst.get_widget()
        self.tv_playlist, self.model_playlist =                             self.tv_playlist_inst.get_widgets()
        self.control_playlist_ctn1, self.control_playlist_btn1 =            self.control_playlist1_instE.get_widgets()
        self.control_playlist_ctn2, self.control_playlist_btn2 =            self.control_playlist2_instE.get_widgets()
        
        self.control_contenido_ctn, self.control_contenido_btn =            self.control_contenido_instE.get_widgets()
        
        self.buscador_canciones =                                           self.buscador_canciones_inst.get_widget()
        self.tv_canciones, self.model_canciones =                           self.tv_canciones_inst.get_widgets()
        self.model_canciones_proxy =                                        self.tv_canciones_inst.get_proxy_model()
        
        self.seleccionador_biblia_ctn, self.seleccionador_biblia_btn =      self.seleccionador_biblia_instE.get_widgets() 
        self.buscador_versiculos =                                          self.buscador_versiculos_inst.get_widget()
        self.tv_versiculos, self.model_versiculos =                         self.tv_versiculos_inst.get_widgets()
        self.model_versiculos_proxy =                                       self.tv_versiculos_inst.get_proxy_model()
        
        (self.seleccionador_media_ctn, self.seleccionador_media,
        self.seleccionador_media_btn) =                                     self.seleccionador_media_inst.get_widgets()
        
        
        self.control_prevista_ctn, self.control_prevista_btn =              self.control_prevista_instE.get_widgets()
        self.identidicador_prevista =                                       self.identidicador_prevista_inst.get_widget()
        
        self.tv_prevista, self.model_prevista =                             self.tv_prevista_inst.get_widgets()
        (self.control_media_envivo_ctn, self.control_media_envivo_btn,
        self.temporizador_media_envivo, self.volumen_media_envivo) =        self.control_media_envivo_inst.get_widgets()
        
        self.proyeccion_prevista, self.diapositiva_prevista =               self.sim_prevista_instE.get_widgets()
        self.reproductor_prevista, self.audio_prevista =                    self.sim_prevista_instE.get_other_widget()
        
        
        self.control_envivo1_ctn, self.control_envivo1_btn =                self.control_envivo1_instE.get_widgets()
        self.control_envivo2_ctn, self.control_envivo2_btn =                self.control_envivo2_instE.get_widgets()
        self.identidicador_envivo =                                         self.identidicador_envivo_inst.get_widget()
        
        self.tv_envivo, self.model_envivo =                                 self.tv_envivo_inst.get_widgets()
        (self.control_media_prevista_ctn, self.control_media_prevista_btn,
         self.temporizador_media_prevista, self.volumen_media_prevista) =   self.control_media_prevista_inst.get_widgets()
        
        self.proyeccion_envivo, self.diapositiva_envivo =                   self.sim_envivo_instE.get_widgets()
        self.reproductor_envivo, self.audio_envivo=                         self.sim_envivo_instE.get_other_widget()
        
    def definir_posicion(self):
        
        self.envivo_barra =             SYgrid(1, 3, [1], [1,0,0], [[self.control_envivo1_ctn, 0, 1], [self.control_envivo2_ctn, 0, 2]])
        
        self.control_media_envivo =     SYgrid(2,1,[16,4],[1],[[self.control_media_envivo_ctn,1,0]])
        
        self.envivo =                   SYstacked(2,[[self.tv_envivo,0], [self.control_media_envivo, 1]])
        
        self.top_seccion_envivo =       SYgrid(2,1, [1,1], [1],[[self.envivo_barra,0,0],[self.identidicador_envivo,1,0]])
        
        self.seccion_envivo =           SYgrid(3, 1, [6,28,26], [1],[[self.top_seccion_envivo,0,0],[self.envivo,1,0],
                                                                     [self.proyeccion_envivo,2,0]],(20,20,20,20), 20)
        
        
        self.prevista_barra =           SYgrid(1, 2, [1], [1,1], [[self.control_prevista_ctn, 0, 1]])
        
        self.control_media_prevista =   SYgrid(2,1,[16,4],[1],[[self.control_media_prevista_ctn,1,0]])
        
        self.prevista =                 SYstacked(2,[[self.tv_prevista,0], [self.control_media_prevista, 1]])
        
        self.top_seccion_prevista =     SYgrid(2,1,[1,1],[1],[[self.prevista_barra,0,0],[self.identidicador_prevista,1,0]])
        
        self.seccion_prevista =         SYgrid(4, 1, [6,28,26], [1],[[self.top_seccion_prevista,0,0],[self.prevista,1,0],
                                                                     [self.proyeccion_prevista,2,0]],(20,20,20,20), 20)
        
        
        self.barra_herramientas =       SYgrid(1, 2, [1], [1,0], [[self.control_fondo_cnt, 0,1]])
        
        self.playlist_barra =           SYgrid(2, 1, [1,1], [1],[[self.control_playlist_ctn1,0,0],[self.control_playlist_ctn2,1,0]])
        
        self.seccion_playlist =         SYgrid(1, 2, [1], [9,1],[[self.tv_playlist,0,0],[self.playlist_barra,0,1]])
        
        self.contenido_barra =          SYgrid(1, 3, [1], [1,0,1], [[self.control_contenido_ctn,0,1]])
        
        self.canciones_ctn =            SYgrid(2,1,[2,24],[1],[[self.buscador_canciones,0,0], [self.tv_canciones,1,0]],(0,0,0,0), 5)
        
        self.biblia_btn =               SYgrid(1, 2, [1], [0,1], [[self.seleccionador_biblia_ctn,0,0],[self.buscador_versiculos,0,1]])
        
        self.biblia =                   SYgrid(2,1,[2,24],[1],[[self.biblia_btn,0,0], [self.tv_versiculos,1,0]],(0,0,0,0), 5)
        
        self.contenido_ctn =            SYstacked(3,[[self.canciones_ctn,0],[self.biblia,1],[self.seleccionador_media_ctn,2]])
        
        self.control_ventana =          SYgrid(2, 1, [1,1], [1], [[self.control_ventana_ctn,0,0]])
        
        self.logo_nombre =             SYgrid(1, 2, [1], [0,1], [[self.logo,0,0],[self.identificador_programa,0,1, Qt.AlignVCenter]], (10,0,0,0))
        
        self.encabezado =               SYgrid(1, 2, [1], [12,74], [[self.logo_nombre,0,0, None, "transparente_right"],[self.control_ventana, 0, 1]])
        
        self.top_seccion_canciones =    SYgrid(2,1,[1,1],[1],[[self.barra_herramientas,0,0],[self.identidicador_playlist,1,0]])
        
        self.seccion_canciones =        SYgrid(4, 1, [6,24,4,26], [1],[[self.top_seccion_canciones,0,0],[self.seccion_playlist,1,0],
                                                                         [self.contenido_barra,2,0],[self.contenido_ctn,3,0]],(20,20,20,20), 20)
        self.cuerpo =               SYgrid(1,3,[1],[4,6,6],[[self.seccion_canciones,0,0],[self.seccion_prevista,0,1],[self.seccion_envivo,0,2]])
        
        self.menu =                   SYgrid(2,1,[1,1],[1], [[self.alt_menu_principal1_ctn,0,0],[self.alt_menu_principal2_ctn,1,0]],(5,0,0,0))
        self.entorno =                   SYgrid(1,2,[1],[12,74], [[self.menu,0,0,None, "transparente_top_right"],[self.cuerpo,0,1,None, "secundario_top"]])
        
        self.base =                  SYgrid(2, 1, [6,96], [1], [[self.encabezado,0,0,None, "encabezado"],[self.entorno,1,0]],(0,0,0,0),2)
        self.fondo =                     SYgrid(1,1,[1], [1], [[self.base,0,0,None, "base_principal"]])
        self.ventana.setLayout(self.fondo)
        self.setCentralWidget(self.ventana)
        
    def conectar_eventos(self):
        self.temporizador_sistema.timeout.connect(self.chequeo_timer)
        self.app.screenRemoved.connect(self.pantalla_removida)
        self.app.screenAdded.connect(self.pantalla_agregada)
        self.app.primaryScreenChanged.connect(self.cambio_pantalla)
        
        
        self.alt_menu_principal1_btn[0].clicked.connect(self.nueva_playlist)
        self.alt_menu_principal1_btn[1].clicked.connect(self.abrir_playlist)
        self.alt_menu_principal1_btn[2].clicked.connect(self.guardar_playlist)
        self.alt_menu_principal1_btn[3].clicked.connect(self.guardar_como_playlist)
        self.alt_menu_principal1_btn[4].clicked.connect(self.nueva_cancion)
        self.alt_menu_principal2_btn[0].clicked.connect(self.configuracion)
        self.alt_menu_principal2_btn[1].clicked.connect(self.acerca_de)
        
        self.control_ventana_btn[0].clicked.connect(self.minimizar_ventana)
        self.control_ventana_btn[1].clicked.connect(self.cerrar_ventana)
        
        self.control_fondo_btn[0].clicked.connect(lambda: self.menu_fondo_cnt.exec_(self.control_fondo_btn[0].mapToGlobal(
                                                  QPoint(self.control_fondo_btn[0].width() - self.menu_fondo_cnt.sizeHint().width(),self.control_fondo_btn[0].height()))))
        self.menu_fondo_btn.clicked.connect(lambda: self.menu_fondos_inst.add_background(self))
        self.menu_fondo_list.itemClicked.connect(lambda item: self.cambiar_fondo_predeterminado(item))
        self.menu_fondo_list.itemClicked.connect(lambda: self.menu_fondo_cnt.close())
        
        self.tv_playlist.clicked.connect(lambda index: self.cancion_prevista(index, "playlist"))
        self.tv_playlist.doubleClicked.connect(self.cancion_envivo)
        self.tv_playlist.signals.enter_pressed.connect(self.cancion_envivo)
        
        self.control_playlist_btn1[0].clicked.connect(self.mover_arriba)
        self.control_playlist_btn1[1].clicked.connect(self.mover_abajo)
        
        self.control_playlist_btn2[0].clicked.connect(self.agregar_cancion_playlist)
        self.control_playlist_btn2[1].clicked.connect(self.borrar_cancion_playlist)
    
        self.control_contenido_btn[0].clicked.connect(lambda: self.contenido_ctn.setCurrentIndex(0))
        self.control_contenido_btn[1].clicked.connect(lambda: self.contenido_ctn.setCurrentIndex(1))
        self.control_contenido_btn[2].clicked.connect(lambda: self.contenido_ctn.setCurrentIndex(2))
    
        self.buscador_canciones.textChanged.connect(lambda texto: self.filtrar_canciones(texto))
        self.tv_canciones.clicked.connect(lambda index: self.cancion_prevista(index, "canciones"))
        self.tv_canciones.doubleClicked.connect(self.cancion_envivo)
        self.tv_canciones.signals.enter_pressed.connect(self.cancion_envivo)
        
        self.seleccionador_biblia_btn[0].clicked.connect(self.mostrar_menu_biblia)
        self.buscador_versiculos.textChanged.connect(self.acciones_versiculos)
        
        self.tv_versiculos.clicked.connect(lambda index: self.versiculo_prevista(index))
        self.tv_versiculos.selectionModel().selectionChanged.connect(lambda index: self.versiculo_prevista(index))
        self.tv_versiculos.doubleClicked.connect(self.versiculo_envivo)
        self.tv_versiculos.signals.enter_pressed.connect(self.versiculo_envivo)
        
        self.seleccionador_media_btn.clicked.connect(self.seleccionador_media_inst.change_root_media)
        self.seleccionador_media.itemClicked.connect(lambda item: self.media_prevista_play(item))
        self.seleccionador_media.itemDoubleClicked.connect(self.media_envivo_play)
        
        
        self.control_prevista_btn[0].clicked.connect(self.a_envivo)
        
        self.tv_prevista.selectionModel().selectionChanged.connect(lambda index: self.letra_prevista(index))
        self.tv_prevista.doubleClicked.connect(lambda index: self.cancion_envivo_selecto(index))
        self.tv_prevista.signals.enter_pressed.connect(lambda index: self.cancion_envivo_selecto(index))
        
        self.volumen_media_prevista.valueChanged.connect(lambda volume: self.audio_prevista.setVolume(volume/100))
        self.temporizador_media_prevista.sliderMoved.connect(lambda position: self.reproductor_prevista.setPosition(position))
        self.reproductor_prevista.positionChanged.connect(lambda positon: self.control_media_prevista_inst.update_position(positon, self.reproductor_prevista))
        self.reproductor_prevista.durationChanged.connect(lambda duration: self.control_media_prevista_inst.update_duration(duration, self.reproductor_prevista))
        
        self.control_media_prevista_btn[0].clicked.connect(lambda: self.reproductor_prevista.play())
        self.control_media_prevista_btn[1].clicked.connect(lambda: self.reproductor_prevista.pause())
        self.control_media_prevista_btn[2].clicked.connect(lambda: self.reproductor_prevista.stop())
        
        
        self.control_envivo1_btn[0].clicked.connect(self.manejar_fondo)
        self.control_envivo1_btn[1].clicked.connect(self.manejar_negro)
        self.control_envivo2_btn[0].clicked.connect(self.abrir_proyeccion)
        
        self.tv_envivo.selectionModel().selectionChanged.connect(lambda index: self.letra_envivo(index))
        
        self.volumen_media_envivo.valueChanged.connect(lambda volume: self.manejar_volumen_envivo(volume/100))
        self.temporizador_media_envivo.sliderMoved.connect(lambda position: self.manejar_posicion_envivo(position))
        self.reproductor_envivo.positionChanged.connect(lambda positon: self.control_media_envivo_inst.update_position(positon, self.reproductor_envivo))
        self.reproductor_envivo.durationChanged.connect(lambda duration: self.control_media_envivo_inst.update_duration(duration, self.reproductor_envivo))
        
        self.control_media_envivo_btn[0].clicked.connect(lambda: self.media_play_envivo())
        self.control_media_envivo_btn[1].clicked.connect(lambda: self.media_pause_envivo())
        self.control_media_envivo_btn[2].clicked.connect(lambda: self.media_stop_envivo())
        
    def definir_atajos(self):
        shortcut_save = QShortcut(QKeySequence("Ctrl+C"), self)
        shortcut_save.activated.connect(self.nueva_cancion)
        
        shortcut_quit = QShortcut(QKeySequence("Ctrl+N"), self)
        shortcut_quit.activated.connect(self.nueva_playlist)
        
        shortcut_print = QShortcut(QKeySequence("Ctrl+Shift+G"), self)
        shortcut_print.activated.connect(self.guardar_como_playlist)
        
        shortcut_print = QShortcut(QKeySequence("Ctrl+G"), self)
        shortcut_print.activated.connect(self.guardar_playlist)
        
        shortcut_complex = QShortcut(QKeySequence("Ctrl+A"), self)
        shortcut_complex.activated.connect(self.abrir_playlist)   
        
    def ajustes_iniciales(self):
        self.biblia_selecionada = cargar_biblia_predeterminado()
        self.idioma_biblia = self.biblia_selecionada.rsplit("_", 1)[-1]
        self.libro_descargado = "Génesis"
        self.estado_negro = False
        self.estado_fondo = False
        self.ventana_proyeccion = None
        self.ventana_cancion = None
        self.ventana_playlist_agregar = None
        self.ventana_playlist = None
        self.ventana_configuracion = None
        self.ventana_acerca_de = None
        
        self.temporizador_sistema.start(1000)
        
        self.tv_canciones_inst.add_elements(sorted(get_all_song_titles(), key=lambda x: x.lower()))
        
        self.tv_canciones_inst.set_context_menu(self.mostrar_menu_canciones)
        
        self.actualizar_versiculos(self.libro_descargado)
        
        self.seleccionador_biblia_btn[0].setText(self.biblia_selecionada.split("_")[0])
        
        self.buscador_versiculos_inst.set_completer(self.app.libros_biblia[self.idioma_biblia], self)
        
        self.resize_widgets()
        
        SYanimationwindow(self)
        
    
    def chequeo_timer(self):
        self.control_envivo2_instE.blink_botton(0,self.ventana_proyeccion)
        geometria_nueva = SYwindoworigen()
        if self.geometria_disponible != geometria_nueva:
            self.actualizar_pantalla(geometria_nueva)
    
    def cambio_pantalla(self):
        screens = self.app.screens()
        screen_actual = self.app.screenAt(self.pos())
        if screen_actual is None:
            self.cambio_pantalla()
        index_actual = screens.index(screen_actual)
        if len(screens) > 1:
            index_nueva = 0 if index_actual == 0 else 1
            nueva_geo = screens[index_nueva].geometry()
            self.move(nueva_geo.x(), nueva_geo.y())
            self.actualizar_pantalla(SYwindoworigen())
    
    def actualizar_pantalla(self, geometria_nueva):
        self.geometria_disponible = geometria_nueva
        self.collapse_widgets()
        def restraso():
            self.setGeometry(self.geometria_disponible)
            self.layout().invalidate()
            self.layout().activate()
            self.update()
            self.resize_widgets()
            self.actualizar_ventanas()
        QTimer.singleShot(1000, restraso)
    
    def collapse_widgets(self):
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
            if self.ventana_proyeccion:
                self.ventana_proyeccion.close()
            self.abrir_proyeccion()         
        QTimer.singleShot(1000, restraso)
        
               
          
    def actualizar_ventanas(self):
        if self.ventana_cancion:
            self.ventana_cancion.update_window()
        if self.ventana_playlist:
            self.ventana_playlist.update_window()
        if self.ventana_playlist_agregar:
            self.ventana_playlist_agregar.update_window()
        if self.ventana_configuracion:
            self.ventana_configuracion.update_window()
        if self.ventana_acerca_de:
            self.ventana_acerca_de.update_window()
            
    def pantalla_agregada(self):
        self.sim_prevista_instE.resize(self)
        self.sim_envivo_instE.resize(self)
        self.abrir_proyeccion()
        
    def pantalla_removida(self):
        if self.ventana_proyeccion:
            self.ventana_proyeccion.close()
                
    def nueva_playlist(self):
        if self.playlist.state == True:
            msg = SYmessagebox(self,QMessageBox.Warning, "No guardo la playlist", "¿Desea continuar sin guardar la playlist?", QMessageBox.Yes | QMessageBox.No)
            if msg.exec_() == QMessageBox.No:
                if self.guardar_playlist() is False:
                    return 
        self.playlist.new()
        self.identidicador_playlist.setText(f"Playlist")
        self.model_playlist.clear()
    
    def abrir_playlist(self):
        if self.playlist.state == True:
            msg = SYmessagebox(self,QMessageBox.Warning, "No guardo la playlist", "¿Desea continuar sin guardar la playlist?", QMessageBox.Yes | QMessageBox.No)
            if msg.exec_() == QMessageBox.No:
                if self.guardar_playlist() is False:
                    return
        self.ventana_playlist = VentanaAbrirPlaylist(self)
        self.ventana_playlist.exec_()
        if self.ventana_playlist.nombre_playlist is not None:
            self.identidicador_playlist.setText(f"Playlist-{self.ventana_playlist.nombre_playlist}")
            self.playlist.open(self.ventana_playlist.nombre_playlist,self.ventana_playlist.lista_canciones)
            self.tv_playlist_inst.add_elements(self.ventana_playlist.lista_canciones)
            self.ventana_playlist = None
              
    
    def guardar_playlist(self):
        if self.playlist.state == False:
            msg = SYmessagebox(self,QMessageBox.Warning, "No hay cambios que guardar", "Por favor, realice algun cambio para continuar", QMessageBox.Ok)
            msg.exec_()
            return 
        self.playlist.compare(self.tv_playlist_inst.get_list())
        if self.playlist.temp_list == []:
            msg = SYmessagebox(self,QMessageBox.Warning, "No hay canciones en la playlist", "Por favor, agregue canciones a su playlist para poder guardar", QMessageBox.Ok)
            msg.exec_()
            return False
        else:
            if is_title_playlist_unique(self.playlist.base_name):
                self.ventana_playlist_agregar = VentanaGuardarPlaylist(self, self.playlist.temp_list)
                self.ventana_playlist_agregar.exec_()
                if self.ventana_playlist_agregar.nombre is not None:
                    self.identidicador_playlist.setText(f"Playlist-{self.ventana_playlist_agregar.nombre}")
                    self.playlist.save(self.ventana_playlist_agregar.nombre)
                    self.ventana_playlist_agregar = None
                    return True
                self.ventana_playlist_agregar = None
                return False
            else:
                update_data_playlist(self.playlist.base_name, self.playlist.temp_list)
                self.identidicador_playlist.setText(f"Playlist-{self.playlist.base_name}")
                self.playlist.save(self.playlist.base_name)
                return True
            
    def guardar_como_playlist(self):
        self.playlist.compare(self.tv_playlist_inst.get_list())
        if self.playlist.temp_list == []:
            msg = SYmessagebox(self,QMessageBox.Warning, "No hay canciones en la playlist", "Por favor, agregue canciones a su playlist para poder guardar", QMessageBox.Ok)
            msg.exec_()
        else:
            self.ventana_playlist_agregar = VentanaGuardarPlaylist(self, self.playlist.temp_list)
            self.ventana_playlist_agregar.exec_()
            if self.ventana_playlist_agregar.nombre is not None:
                self.identidicador_playlist.setText(f"Playlist-{self.ventana_playlist_agregar.nombre}")
                self.playlist.save(self.ventana_playlist_agregar.nombre)
            self.ventana_playlist_agregar = None
    
    def nueva_cancion(self, cancion = None):
        self.ventana_cancion = VentanaCancion(self, cancion)
        self.ventana_cancion.exec_()
        self.tv_canciones_inst.add_elements(sorted(get_all_song_titles(), key=lambda x: x.lower()))
        self.ventana_cancion = None
    
    def configuracion(self):
        index_actual = self.contenido_ctn.currentIndex()
        self.contenido_ctn.setCurrentIndex(1)
        self.contenido_ctn.setCurrentIndex(index_actual)
        self.ventana_configuracion = VentanaConfiguraciones(self, self.app, self.resize_widgets)
        self.ventana_configuracion.exec_()
        self.ventana_configuracion = None

    def acerca_de(self):
        self.ventana_acerca_de = VentanaAcercaDe(self)
        self.ventana_acerca_de.exec_()
        self.ventana_acerca_de = None
        
    def minimizar_ventana(self):
        self.showMinimized()    
        
    def cerrar_ventana(self):
        if self.playlist.state == True:
            msg = SYmessagebox(self,QMessageBox.Warning, "No guardo la playlist actual", "¿Desea salir sin guardar la playlist?", QMessageBox.Yes | QMessageBox.No)
            if msg.exec_() == QMessageBox.No:
                if self.guardar_playlist() == False:
                    return
            else:
                self.playlist.state = False
        if self.ventana_proyeccion is not None:
            self.ventana_proyeccion.close()
        self.close()
        
    def cambiar_fondo_predeterminado(self, item):
        ruta_completa = item.data(Qt.UserRole)
        editar_fondo_predeterminado(ruta_completa.replace("\\", "/"))
        if self.sim_prevista_instE.element == SY.VERSICLE:
            self.sim_prevista_instE.load_versicle(self.biblia_selecionada)
        elif self.sim_prevista_instE.song.fondo_url == "None" and self.sim_prevista_instE.element == SY.SONG:
            self.sim_prevista_instE.load_song()
        
        if self.sim_envivo_instE.element == SY.VERSICLE:
            self.sim_envivo_instE.load_versicle(self.biblia_selecionada, self.estado_negro, self.estado_fondo)
            if self.ventana_proyeccion:
                self.ventana_proyeccion.sim_envivo_inst.load_versicle(self.biblia_selecionada, self.estado_negro, self.estado_fondo)
        elif self.sim_envivo_instE.song.fondo_url == "None" and self.sim_envivo_instE.element == SY.SONG:
            self.sim_envivo_instE.load_song( self.estado_negro)
            if self.ventana_proyeccion:
                self.ventana_proyeccion.sim_envivo_inst.load_song( self.estado_negro)
        
    def cancion_prevista(self, dato, origen):
        self.prevista.setCurrentIndex(0)
        
        selection = QItemSelection(dato, dato)
        self.sim_prevista_instE.update_song(selection.indexes()[0].data())
        self.identidicador_prevista.setText(f"Prevista-{self.sim_prevista_instE.song.titulo}")
        self.tv_prevista_inst.add_elements(self.sim_prevista_instE.song.letra.split("\n\n"),strip=True)
        self.sim_prevista_instE.load_song()
        self.sim_prevista_instE.set_text(self.tv_prevista.model().data(self.tv_prevista.model().index(0,0,self.tv_prevista.rootIndex())), False,False)
        self.tv_playlist.selectionModel().clearSelection() if origen == "canciones" else self.tv_canciones.selectionModel().clearSelection()
            
    def cancion_envivo(self):
        self.envivo.setCurrentIndex(0)
        self.sim_envivo_instE.update_song(self.sim_prevista_instE.song)
        self.identidicador_envivo.setText(f"En vivo-{self.sim_envivo_instE.song.titulo}")
        self.tv_envivo_inst.add_elements(self.sim_envivo_instE.song.letra.split("\n\n"),strip=True)
        self.sim_envivo_instE.load_song(self.estado_negro)
        self.tv_envivo.setCurrentIndex(self.tv_envivo.model().index(0, 0))
        self.tv_envivo.setFocus()
        self.sim_envivo_instE.set_text(self.tv_envivo.model().data(self.tv_envivo.model().index(0,0,self.tv_envivo.rootIndex())),self.estado_negro, self.estado_fondo) 
        if self.ventana_proyeccion:
            self.ventana_proyeccion.sim_envivo_inst.update_song(self.sim_envivo_instE.song)
            self.ventana_proyeccion.sim_envivo_inst.load_song(self.estado_negro)
            self.ventana_proyeccion.sim_envivo_inst.set_text(self.tv_envivo.model().data(self.tv_envivo.model().index(0,0,self.tv_envivo.rootIndex())),self.estado_negro, self.estado_fondo)
            
    def mover_arriba(self):
        selected_indexes = self.tv_playlist.selectionModel().selectedIndexes()
        if selected_indexes:
            fila_actual = selected_indexes[0].row()

            if fila_actual > 0:
                index1 = self.model_playlist.index(fila_actual, 0)
                index2 = self.model_playlist.index(fila_actual - 1, 0)

                dato1 = self.model_playlist.data(index1)
                dato2 = self.model_playlist.data(index2)

                self.model_playlist.setData(index1, dato2)
                self.model_playlist.setData(index2, dato1)

                self.tv_playlist.selectionModel().setCurrentIndex(self.model_playlist.index(fila_actual - 1, 0),QItemSelectionModel.ClearAndSelect | QItemSelectionModel.Rows)
                self.playlist.compare(self.tv_playlist_inst.get_list())
                if self.playlist.state == True:
                    self.identidicador_playlist.setText(f"Playlist-{self.playlist.base_name}*")
                else:
                    self.identidicador_playlist.setText(f"Playlist-{self.playlist.base_name}") 
                    
    def mover_abajo(self):
        selected_indexes = self.tv_playlist.selectionModel().selectedIndexes()
        if selected_indexes:
            fila_actual = selected_indexes[0].row()
            total_filas = self.model_playlist.rowCount()

            if fila_actual < total_filas - 1:
                index1 = self.model_playlist.index(fila_actual, 0)
                index2 = self.model_playlist.index(fila_actual + 1, 0)

                dato1 = self.model_playlist.data(index1)
                dato2 = self.model_playlist.data(index2)

                self.model_playlist.setData(index1, dato2)
                self.model_playlist.setData(index2, dato1)

                self.tv_playlist.selectionModel().setCurrentIndex(self.model_playlist.index(fila_actual + 1, 0),QItemSelectionModel.ClearAndSelect | QItemSelectionModel.Rows)
                self.playlist.compare(self.tv_playlist_inst.get_list())
                if self.playlist.state == True:
                    self.identidicador_playlist.setText(f"Playlist-{self.playlist.base_name}*")
                else:
                    self.identidicador_playlist.setText(f"Playlist-{self.playlist.base_name}")
    
    def agregar_cancion_playlist(self, cancion = None):
        selected_indexes = self.tv_canciones.selectionModel().selectedIndexes()
        if selected_indexes or cancion:
            if cancion:
                self.model_playlist.appendRow(QStandardItem(cancion))
            else:
                self.model_playlist.appendRow(QStandardItem(self.model_canciones.itemFromIndex(self.model_canciones_proxy.mapToSource(selected_indexes[0])).text()))
            self.tv_canciones.selectionModel().clearSelection()
            self.playlist.compare(self.tv_playlist_inst.get_list())
            if self.playlist.state == True:
                self.identidicador_playlist.setText(f"Playlist-{self.playlist.base_name}*")
            else:
                self.identidicador_playlist.setText(f"Playlist-{self.playlist.base_name}")
                
    def borrar_cancion_playlist(self):
        selected_indexes = self.tv_playlist.selectionModel().selectedIndexes()
        if selected_indexes:
            self.model_playlist.removeRow(selected_indexes[0].row())
            self.tv_playlist.selectionModel().clearSelection()
            self.playlist.compare(self.tv_playlist_inst.get_list())
            if self.playlist.state == True:
                self.identidicador_playlist.setText(f"Playlist-{self.playlist.base_name}*")
            else:
                self.identidicador_playlist.setText(f"Playlist-{self.playlist.base_name}")
    
    def filtrar_canciones(self, text):
        self.model_canciones_proxy.setFilterRegularExpression(text)
    
    def selecionar_biblia(self, biblia):
        self.biblia_selecionada = biblia
        self.idioma_biblia = self.biblia_selecionada.rsplit("_", 1)[-1]
        editar_biblia_predeterminado(biblia)
        self.actualizar_versiculos(self.libro_descargado)
        self.buscador_versiculos_inst.set_completer(self.app.libros_biblia[self.idioma_biblia], self)
        self.seleccionador_biblia_btn[0].setText(self.biblia_selecionada.split("_")[0])
    
    def mostrar_menu_biblia(self):
        lista_biblias = get_all_bibles_versions()
        
        if lista_biblias == "None":
            return
        
        menu_biblias_inst = SYmenu(self, "Biblias", lista_biblias)
        menu_biblias, menu_biblias_act = menu_biblias_inst.get_widgets()
        
        for i, biblia in enumerate(lista_biblias):
            menu_biblias_act[i].triggered.connect(lambda _, b=biblia: self.selecionar_biblia(b))
        
        menu_biblias.exec_(self.seleccionador_biblia_btn[0].mapToGlobal(QPoint(0, self.seleccionador_biblia_btn[0].height())))
    
    def acciones_versiculos(self):
        texto_real = self.buscador_versiculos.text().strip()
        texto_normalizado = unicodedata.normalize("NFKD", texto_real).encode("ASCII", "ignore").decode("utf-8").lower()
        
        if texto_normalizado in self.app.libros_normalizados[self.idioma_biblia]:
            libro_real = self.app.libros_normalizados[self.idioma_biblia][texto_normalizado]
            if not self.libro_descargado == libro_real:
                self.libro_descargado = libro_real
                self.actualizar_versiculos(libro_real)
            if not texto_real == libro_real:
                self.buscador_versiculos.textChanged.disconnect(self.acciones_versiculos)
                self.model_versiculos_proxy.setFilterRegularExpression("")
                self.buscador_versiculos.clear()
                self.buscador_versiculos.setText(f"{libro_real} ")
                self.buscador_versiculos.textChanged.connect(self.acciones_versiculos)
            if self.libro_descargado == libro_real and texto_real == libro_real:
                self.model_versiculos_proxy.setFilterRegularExpression(texto_real)
        else:
            self.model_versiculos_proxy.setFilterRegularExpression(texto_real)  
    
    def versiculo_prevista(self, dato):
        self.prevista.setCurrentIndex(0)
        self.model_prevista.clear()
        if isinstance(dato, QItemSelection):
            seleccion=dato
        else:
            seleccion= QItemSelection(dato, dato)
            
        if not seleccion.indexes():
            return
        
        self.sim_prevista_instE.update_versicle(seleccion.indexes())
        self.identidicador_prevista.setText(f"Prevista-{self.sim_prevista_instE.versicle.versicle}")
        self.sim_prevista_instE.load_versicle(self.biblia_selecionada)
    
    def versiculo_envivo(self):
        self.envivo.setCurrentIndex(0)
        self.model_envivo.clear()
        self.sim_envivo_instE.update_versicle(self.sim_prevista_instE.versicle)
        self.identidicador_envivo.setText(f"En vivo-{self.sim_envivo_instE.versicle.versicle}")
        self.sim_envivo_instE.load_versicle(self.biblia_selecionada, self.estado_negro, self.estado_fondo)
        if self.ventana_proyeccion:
            self.ventana_proyeccion.sim_envivo_inst.update_versicle(self.sim_envivo_instE.versicle)
            self.ventana_proyeccion.sim_envivo_inst.load_versicle(self.biblia_selecionada, self.estado_negro, self.estado_fondo)
    
    def media_prevista_play(self, item):
        self.sim_prevista_instE.update_media(item)
        self.identidicador_prevista.setText(f"Prevista-{self.sim_prevista_instE.media.name}")
        if SYmediarecognize(self.sim_prevista_instE.media.item):
            self.model_prevista.clear()
            self.prevista.setCurrentIndex(0)
            self.sim_prevista_instE.load_media()
        else:
            self.prevista.setCurrentIndex(1)
            self.sim_prevista_instE.load_media()
            self.reproductor_prevista.play()
            
    def media_envivo_play(self):
        self.sim_envivo_instE.update_media(self.sim_prevista_instE.media)
        self.identidicador_envivo.setText(f"En vivo-{self.sim_envivo_instE.media.name}")
        self.reproductor_prevista.pause()
        tipo_media = SYmediarecognize(self.sim_envivo_instE.media.item)
        if tipo_media:
            self.model_envivo.clear()
            self.envivo.setCurrentIndex(0)
        else:
            self.envivo.setCurrentIndex(1)
        self.sim_envivo_instE.load_media(True,self.estado_negro, self.estado_fondo)
        if not tipo_media:
            self.reproductor_envivo.play()
        if self.ventana_proyeccion:
            self.ventana_proyeccion.sim_envivo_inst.update_media(self.sim_envivo_instE.media)
            self.ventana_proyeccion.sim_envivo_inst.load_media(False, self.estado_negro, self.estado_fondo)
            if not tipo_media:
                self.ventana_proyeccion.media_envivo.play()
    
    def a_envivo(self):
        if self.sim_prevista_instE.element == SY.SONG:
            selected_indexes = self.tv_prevista.selectionModel().selectedIndexes()
            if selected_indexes:
                fila_actual = selected_indexes[0]
                self.cancion_envivo_selecto(fila_actual)
            else:
                self.cancion_envivo()
        elif self.sim_prevista_instE.element == SY.VERSICLE:
            self.versiculo_envivo()
        elif self.sim_prevista_instE.element == SY.MEDIA:
            estado = self.reproductor_prevista.playbackState()
            self.media_envivo_play()
            self.sim_envivo_instE.sync_media(self.reproductor_prevista, estado)
            if self.ventana_proyeccion:
                self.ventana_proyeccion.sim_envivo_inst.sync_media(self.reproductor_prevista, estado)
                
    def letra_prevista(self, dato):
        if not dato.indexes():
            return
        self.sim_prevista_instE.set_text(dato.indexes()[0].data(), False,False)      
    
    def cancion_envivo_selecto(self, dato):
        selection = QItemSelection(dato, dato)
        self.sim_envivo_instE.update_song(self.sim_prevista_instE.song)
        self.identidicador_envivo.setText(f"En vivo-{self.sim_envivo_instE.song.titulo}")
        self.tv_envivo_inst.add_elements(self.sim_envivo_instE.song.letra.split("\n\n"),strip=True)
        self.sim_envivo_instE.load_song(self.estado_negro)
        self.tv_envivo.setCurrentIndex(self.tv_envivo.model().index(dato.row(), 0))
        self.tv_envivo.setFocus()
        self.sim_envivo_instE.set_text(selection.indexes()[0].data(),self.estado_negro, self.estado_fondo)
        if self.ventana_proyeccion:
            self.ventana_proyeccion.sim_envivo_inst.update_song(self.sim_envivo_instE.song)
            self.ventana_proyeccion.sim_envivo_inst.load_song(self.estado_negro)
            self.ventana_proyeccion.sim_envivo_inst.set_text(selection.indexes()[0].data(),self.estado_negro, self.estado_fondo)
    
    def manejar_fondo(self):
        self.estado_fondo = not self.estado_fondo
        self.control_envivo1_instE.switch_button(0, self.estado_fondo)
        if self.sim_envivo_instE.element == SY.SONG:
            self.sim_envivo_instE.load_song(self.estado_negro)
            selected_indexes = self.tv_envivo.selectionModel().selectedIndexes()
            self.sim_envivo_instE.set_text(self.tv_envivo.model().data(selected_indexes[0]), self.estado_negro, self.estado_fondo)
            if self.ventana_proyeccion:   
                self.ventana_proyeccion.sim_envivo_inst.load_song(self.estado_negro)
                self.ventana_proyeccion.sim_envivo_inst.set_text(self.diapositiva_envivo.text(), self.estado_negro, self.estado_fondo)
        elif self.sim_envivo_instE.element == SY.VERSICLE:
            self.sim_envivo_instE.load_versicle(self.biblia_selecionada, self.estado_negro, self.estado_fondo)
            if self.ventana_proyeccion:
                self.ventana_proyeccion.sim_envivo_inst.load_versicle(self.biblia_selecionada, self.estado_negro, self.estado_fondo)       
        elif self.sim_envivo_instE.element == SY.MEDIA:
            if SYmediarecognize(self.sim_envivo_instE.media.item):
                self.sim_envivo_instE.load_media(True,self.estado_negro,self.estado_fondo)
                if self.ventana_proyeccion:
                    self.ventana_proyeccion.sim_envivo_inst.load_media(False,self.estado_negro,self.estado_fondo)
            else:
                self.sim_envivo_instE.show_media(self.estado_negro, True)
                if self.ventana_proyeccion:
                    self.ventana_proyeccion.sim_envivo_inst.show_media(self.estado_negro,self.estado_fondo)
            
    def manejar_negro(self):
        self.estado_negro = not self.estado_negro
        self.control_envivo1_instE.switch_button(1, self.estado_negro)
        if self.sim_envivo_instE.element == SY.SONG:
            self.sim_envivo_instE.load_song(self.estado_negro)
            selected_indexes = self.tv_envivo.selectionModel().selectedIndexes()
            self.sim_envivo_instE.set_text(self.tv_envivo.model().data(selected_indexes[0]), self.estado_negro, self.estado_fondo)
            if self.ventana_proyeccion:   
                self.ventana_proyeccion.sim_envivo_inst.load_song(self.estado_negro)
                self.ventana_proyeccion.sim_envivo_inst.set_text(self.diapositiva_envivo.text(), self.estado_negro, self.estado_fondo)
        elif self.sim_envivo_instE.element == SY.VERSICLE:
            self.sim_envivo_instE.load_versicle(self.biblia_selecionada, self.estado_negro, self.estado_fondo)
            if self.ventana_proyeccion:
                self.ventana_proyeccion.sim_envivo_inst.load_versicle(self.biblia_selecionada, self.estado_negro, self.estado_fondo)       
        elif self.sim_envivo_instE.element == SY.MEDIA:
            if SYmediarecognize(self.sim_envivo_instE.media.item):
                self.sim_envivo_instE.load_media(True,self.estado_negro,self.estado_fondo)
                if self.ventana_proyeccion:
                    self.ventana_proyeccion.sim_envivo_inst.load_media(False,self.estado_negro,self.estado_fondo)
            else:
                self.sim_envivo_instE.show_media(self.estado_negro, True)
                if self.ventana_proyeccion:
                    self.ventana_proyeccion.sim_envivo_inst.show_media(self.estado_negro,self.estado_fondo)
    
    def reiniciar_proyeccion(self):
        self.ventana_proyeccion = None
        
    def abrir_proyeccion(self):
        if not self.ventana_proyeccion:
            pantallas = self.app.screens()
            pantalla_secundaria = None
            if len(pantallas) > 1:
                pantalla_secundaria = SYwindowextra(True)
            
            if pantalla_secundaria is not None:
                self.ventana_proyeccion = VentanaProyeccion(self, self.app, pantalla_secundaria, self.reiniciar_proyeccion)
                self.ventana_proyeccion.show()
                self.activateWindow()
                self.manejar_proyeccion()
        else:
            self.ventana_proyeccion.close()
                
    def manejar_proyeccion(self):
        if self.sim_envivo_instE.element == SY.SONG and self.ventana_proyeccion:
            self.ventana_proyeccion.sim_envivo_inst.update_song(self.sim_envivo_instE.song)
            self.ventana_proyeccion.sim_envivo_inst.load_song(self.estado_negro)
            self.ventana_proyeccion.sim_envivo_inst.set_text(self.diapositiva_envivo.text(),self.estado_negro, self.estado_fondo)
        elif self.sim_envivo_instE.element == SY.VERSICLE and self.ventana_proyeccion:
            self.ventana_proyeccion.sim_envivo_inst.update_versicle(self.sim_envivo_instE.versicle)
            self.ventana_proyeccion.sim_envivo_inst.load_versicle(self.biblia_selecionada, self.estado_negro, self.estado_fondo)
        elif self.sim_envivo_instE.element == SY.MEDIA and self.ventana_proyeccion:
            self.ventana_proyeccion.sim_envivo_inst.update_media(self.sim_envivo_instE.media)
            self.ventana_proyeccion.sim_envivo_inst.load_media(False, self.estado_negro, self.estado_fondo)
            def restraso():
                if not SYmediarecognize(self.sim_envivo_instE.media.item):
                    self.ventana_proyeccion.sim_envivo_inst.sync_media(self.reproductor_envivo, self.reproductor_envivo.playbackState())
            QTimer.singleShot(1000, restraso)
        

    def letra_envivo(self, dato):
        if not dato.indexes():
            return
        self.sim_envivo_instE.set_text(dato.indexes()[0].data(),self.estado_negro, self.estado_fondo)
        if self.ventana_proyeccion:
            self.ventana_proyeccion.sim_envivo_inst.set_text(dato.indexes()[0].data(),self.estado_negro, self.estado_fondo)
            
    def manejar_volumen_envivo(self, volumen):     
        self.audio_envivo.setVolume(volumen)
        if self.ventana_proyeccion:
            self.ventana_proyeccion.audio_envivo.setVolume(volumen)
            
    def manejar_posicion_envivo(self, posicion):
        self.reproductor_envivo.setPosition(posicion)
        if self.ventana_proyeccion:
            self.ventana_proyeccion.media_envivo.setPosition(posicion)        
    
    def media_play_envivo(self):
        self.reproductor_envivo.play()
        if self.ventana_proyeccion:
            self.ventana_proyeccion.media_envivo.play()
            
    def media_pause_envivo(self):
        self.reproductor_envivo.pause()
        if self.ventana_proyeccion:
            self.ventana_proyeccion.media_envivo.pause()
            
    def media_stop_envivo(self):
        self.reproductor_envivo.stop()
        if self.ventana_proyeccion:
            self.ventana_proyeccion.media_envivo.stop()
    
    def borrar_cancion(self, cancion):
        delete_song(cancion)
        self.tv_canciones_inst.add_elements(sorted(get_all_song_titles(), key=lambda x: x.lower()))
    
    def mostrar_menu_canciones(self, pos: QPoint):
        index = self.tv_canciones.indexAt(pos)
        if not index.isValid():
            return

        item = self.model_canciones.itemFromIndex(self.model_canciones_proxy.mapToSource(index))
        texto_fila = item.text()
        menu_canciones_inst = SYmenu(self, "canciones", ["Agregar", "Editar", "Borrar"])
        menu_canciones, menu_canciones_act = menu_canciones_inst.get_widgets()
        
        menu_canciones_act[0].triggered.connect(lambda: self.agregar_cancion_playlist(texto_fila))
        menu_canciones_act[1].triggered.connect(lambda: self.nueva_cancion(texto_fila))
        menu_canciones_act[2].triggered.connect(lambda: self.borrar_cancion(texto_fila))
        
        menu_canciones.exec_(self.tv_canciones.viewport().mapToGlobal(pos))
        
    
    def actualizar_versiculos(self, libro):
        if self.biblia_selecionada == "None":
            return
        versiculos, textos = get_book_by_version(self.biblia_selecionada, libro)
        self.tv_versiculos_inst.add_elements(versiculos, textos)
    
    def paintEvent(self, event):
        """Fondo con desenfoque visual (simulado con gradiente)."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        gradient = QColor(100, 100, 255, 50)
        painter.fillRect(self.rect(), gradient)
    
    def closeEvent(self, event):
        self.cerrar_ventana()
        event.accept()

            
            
            
        
        
            
            
            
            
            