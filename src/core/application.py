from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QPalette, QColor, QIcon
from core.helpers import aclarar, oscurecer, SYpathcreater
from core.constants import cargar_constantes

class SYApplication(QApplication):
    def __init__(self, args):
        super().__init__(args)

    def start(self):
        self.setWindowIcon(QIcon(SYpathcreater("icons","GraceForAll.ico", temporal=True)))
        self.apply_language()
        self.apply_theme()
        self.config_options()
    
    def apply_theme(self):
        from services.json_service import cargar_estilo_actual
        theme = {"dark_mode": ["#A0A0A0","#353535","#2a2a2a","#1E1E1E","#ff0000","#2a82da","#253158","#ffffff",
                               "#121212","#2b2b2b","#5c5c5c","#333333","#3C3C3C","#000000","#888888"],
            "dark_blue_mode": ["#c0cbe0","#1e1e2e","#181820","#151521","#ff4b4b","#4c8aff","#2e4b79","#ffffff",
                               "#0e0e17","#1a1a2a","#3c3f4a","#2c2c3c","#34344a","#000000","#6a6a8a"],
            "dark_warm_mode": ["#e0d7c6","#3a2f2f","#2b1f1f","#331818","#cc3333","#d8893c","#77594e","#ffffff",
                               "#1b1a17","#2a2220","#6c5e5e","#4a3f3f","#594a4a","#000000","#a38c8c"],
       "solarized_dark_mode": ["#93a1a1","#002b36","#073642","#001f27","#dc322f","#268bd2","#2aa198","#ffffff",
                               "#001418","#073642","#586e75","#003847","#005460","#000000","#657b83"],
            "green_dark_mode": ["#c7dec7","#1e2b1e","#162416","#0d1a0d","#ff4444","#4fcf4f","#356635","#ffffff",
                               "#101810","#1a291a","#3a4a3a","#2f3f2f","#3c4c3c","#000000","#7f997f"]}
        colores = theme[cargar_estilo_actual()]
        
        palette_modify = QPalette()
        
    
        palette_modify.setColor(QPalette.Window, QColor(colores[1]))
        palette_modify.setColor(QPalette.WindowText, QColor(colores[0]))
        palette_modify.setColor(QPalette.Base, QColor(colores[2]))
        palette_modify.setColor(QPalette.AlternateBase, QColor(colores[1]))
        palette_modify.setColor(QPalette.ToolTipBase, QColor(colores[0]))
        palette_modify.setColor(QPalette.ToolTipText, QColor(colores[0]))
        palette_modify.setColor(QPalette.Text, QColor(colores[0]))
        palette_modify.setColor(QPalette.Button, QColor(colores[8]))
        palette_modify.setColor(QPalette.ButtonText, QColor(colores[0]))
        palette_modify.setColor(QPalette.BrightText, QColor(colores[4]))
        palette_modify.setColor(QPalette.Link, QColor(colores[5]))
        palette_modify.setColor(QPalette.Highlight, QColor(colores[6]))
        palette_modify.setColor(QPalette.HighlightedText, QColor(colores[7]))
        
        theme =  f"""
            QWidget#base_principal{{
                background-color: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 {colores[8]}, stop:1 {aclarar(colores[8])}
                );
            }}
            QWidget#transparente_top{{
                background-color: transparent;
                border-top: 1px solid {colores[0]};
            }}
            QWidget#transparente_right{{
                background-color: transparent;
                border-right: 1px solid {colores[0]};
            }}
            QWidget#transparente_top_right{{
                background-color: transparent;
                border-top: 1px solid {colores[0]};
                border-right: 1px solid {colores[0]};
            }}
            QWidget#secundario_top {{
                background-color:{aclarar(colores[3])};
                border-top: 1px solid {colores[0]};
            }}
            QWidget#encabezado {{
                background-color: transparent;
            }}
            QToolButton#menu_principal {{
                background-color: transparent;
                color: transparent;
                border-radius: 1px;
            }}
            QToolButton#menu_principal:hover {{
                background-color: {colores[11]};
                border-left: 3px solid {colores[0]};
            }}
            QToolButton#menu_principal:pressed {{
                background-color: {colores[11]};
                border-left: 3px solid {colores[0]};
            }}
            QToolButton#menu_secundario {{
                background-color: transparent;
                color: {colores[0]};
                border-radius: 1px;
            }}
            QToolButton#menu_secundario:hover {{
                background-color: {colores[11]};
                border-left: 3px solid {colores[0]};
            }}
            QToolButton#menu_secundario:pressed {{
                background-color: {colores[11]};
                border-left: 3px solid {colores[0]};
            }}
            QWidget#complemento{{
                background-color: qlineargradient(
                    spread:pad, x1:0, y1:0, x2:1, y2:1,
                    stop:0 {aclarar(colores[2])}, stop:1 {colores[2]}
                );
            }}
            QLabel#encabezado {{
                background-color: transparent;
                color: {colores[0]};
            }}
            QLabel#encabezadosecundario {{
                background-color: transparent;
                color: {colores[0]};
            }}
            QToolButton#btnencabezado {{
                background-color: transparent;
                color: {colores[0]};
                border-radius: 5px;
            }}
            QToolButton#btnencabezado:hover {{
                background-color: {colores[11]};
            }}
            QToolButton#btnencabezado:pressed {{
                background-color: {colores[11]};
            }}
            QToolButton#btnsistema {{
                background-color: transparent;
                color: {colores[0]};
                border-bottom: 2px solid rgba(0, 0, 0, 0.2);
                border-right: 2px solid rgba(255, 255, 255, 0.02);
                border-top: 2px solid rgba(255, 255, 255, 0.05);
                border-left: 2px solid rgba(0, 0, 0, 0.3);
                border-radius: 5px;
            }}
            QToolButton#btnsistema:hover {{
                background-color: {colores[11]};
            }}
            QToolButton#btnsistema:pressed {{
                background-color: {colores[11]};
            }}
            QWidget#base_secundaria{{
                background-color: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 {colores[8]}, stop:1 {aclarar(colores[8])}
                );
                border-radius: 15px;
                border: 1px solid {colores[0]};
            }}
            QWidget#grid_conjunto {{
                background-color: qlineargradient(
                    spread:pad, x1:0, y1:0, x2:1, y2:1,
                    stop:0 {colores[1]}, stop:1 {aclarar(colores[1])}
                );
                border-radius: 5px;
            }}
            QWidget#Fondo {{
                background-color: qlineargradient(
                    spread:pad, x1:0, y1:0, x2:1, y2:1,
                    stop:0 {colores[8]}, stop:1 {aclarar(colores[8])}
                );
            }}
            QWidget#proyeccion{{
                background-color: qlineargradient(
                    spread:pad, x1:0, y1:0, x2:1, y2:1,
                    stop:0 {colores[3]}, stop:1 {aclarar(colores[3])}
                );
                border: 2px solid {colores[9]};
                border-radius: 15px;
            }}
            QLabel#simulacion {{
                background-color: {colores[13]};
                color: {colores[7]};
            }}
            QMessageBox {{
                background-color: {colores[8]}; 
                border: 2px solid {colores[14]};
            }}
            """
        
        self.setPalette(palette_modify)
        self.setStyle("Fusion")
        self.setStyleSheet(theme)

    def apply_language(self):
        from services.json_service import cargar_idioma
        idioma = cargar_idioma()
        cargar_constantes(self, idioma)
        
    def config_options(self):
        self.diccionario_temas = dict(zip(self.lista_temas, ["dark_mode","dark_blue_mode","dark_warm_mode","solarized_dark_mode","green_dark_mode"]))
        self.diccionario_resoluciones = dict(zip(self.lista_resoluciones, [2160,1440,1080]))
        self.diccionario_tamanos = dict(zip(self.lista_puntos_fuente, [4,5]))
        self.diccionario_idiomas = dict(zip(self.lista_idiomas, ["es","en"]))
