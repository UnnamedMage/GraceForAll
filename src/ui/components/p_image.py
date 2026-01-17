from PySide6.QtWidgets import QGraphicsPixmapItem
from PySide6.QtCore import Qt, Signal, QObject
from PySide6.QtGui import QPixmap, QImageReader
from typing import Literal


class Signals(QObject):
    loaded = Signal()


class PImage(QGraphicsPixmapItem):
    def __init__(self, parent):
        QGraphicsPixmapItem.__init__(self)
        self.aspect_ratio = Qt.KeepAspectRatio
        self.image = None
        self.parent = parent
        self.signals = Signals()

    def set_aspect_ratio_mode(self, value: Literal["keep", "ignore", "expand"]):
        if value == "keep":
            self.aspect_ratio = Qt.KeepAspectRatio
        elif value == "ignore":
            self.aspect_ratio = Qt.IgnoreAspectRatio
        elif value == "expand":
            self.aspect_ratio = Qt.KeepAspectRatioByExpanding

    def set_source(self, source: str):
        reader = QImageReader(source)
        image = reader.read()
        self.image = QPixmap.fromImage(image)

        self._set_pixmap()
        self.signals.loaded.emit()

    def _set_pixmap(self):
        if not self.image or self.image.isNull():
            return

        if self.parent:
            pixmap = self.image.scaled(
                self.parent.width(),
                self.parent.height(),
                self.aspect_ratio,
                Qt.SmoothTransformation,
            )
            x = (self.parent.width() - pixmap.width()) // 2
            y = (self.parent.height() - pixmap.height()) // 2

            self.setPos(x, y)
            self.setPixmap(pixmap)

    def update(self):
        self._set_pixmap()

    def setVisible(self, visible):
        super().setVisible(visible)
