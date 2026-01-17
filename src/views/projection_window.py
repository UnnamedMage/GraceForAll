from PySide6.QtWidgets import QMainWindow, QWidget
from components.ui_elements import SYprojection, SYgrid
from PySide6.QtCore import Qt
from PySide6.QtGui import QScreen

class VentanaProyeccion(QMainWindow):
    def __init__(self, parent, app,pantalla_secundaria=None, on_close_callback=None):
        super().__init__(parent)
        self.setWindowTitle("Proyeccion")
        if isinstance(pantalla_secundaria, QScreen):
            self.setGeometry(pantalla_secundaria.geometry())
        else:
            self.setGeometry(pantalla_secundaria)
        
        screens = app.screens()
        screen_actual = app.screenAt(self.pos())
        index_actual = screens.index(screen_actual)
        if len(screens) > 1:
            index_nueva = 1 if index_actual == 0 else 0
            nueva_geo = screens[index_nueva].geometry()
            self.move(nueva_geo.x(), nueva_geo.y())
        self.setWindowFlags(Qt.Window | Qt.WindowStaysOnTopHint)
        self.showFullScreen()
        self.on_close_callback = on_close_callback
        self.crear_instancias()
        self.almacenar_elementos()
        self.definir_posicion()
        self.ajustes_iniciales()
        
    def crear_instancias(self):
        self.sim_envivo_inst = SYprojection(self)
        
    def almacenar_elementos(self):
        self.ventana = QWidget(self)
        self.sim_envivo_ctn, self.sim_envivo = self.sim_envivo_inst.get_widgets()
        self.media_envivo, self.audio_envivo = self.sim_envivo_inst.get_other_widget()
    
    def definir_posicion(self):
        self.contenedor = SYgrid(1,1,[1],[1],[[self.sim_envivo_ctn,0,0]])
        self.ventana.setLayout(self.contenedor)
        self.setCentralWidget(self.ventana)
    
    def ajustes_iniciales(self):
        self.sim_envivo_inst.resize(self, True)
      
        
    
    def closeEvent(self, event):
        if self.on_close_callback:
            self.on_close_callback()
        event.accept()