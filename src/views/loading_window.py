from PySide6.QtWidgets import QSplashScreen
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt
from core.helpers import SYpathcreater, SYwindoworigen

class VentanaCarga(QSplashScreen):
    def __init__(self, mensaje="Cargando...", fondo=Qt.white):
        geometria_principal = SYwindoworigen()
        height = int(geometria_principal.height() * 0.5)
        width = int(geometria_principal.width() * 0.5)
        pixmap = QPixmap(SYpathcreater("icons", "loading_screen.png", temporal=True))
        pixmap_final = pixmap.scaled(width, height, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        super().__init__(pixmap_final, Qt.WindowStaysOnTopHint)
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setMessage(mensaje, fondo)

    def setMessage(self, texto, color=Qt.white):
        self.showMessage(
            texto,
            alignment=Qt.AlignBottom | Qt.AlignCenter,
            color=color
        )

    def cerrar(self, widget_principal):
        self.finish(widget_principal)