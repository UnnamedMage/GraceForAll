from PySide6.QtWidgets import QLabel, QGraphicsProxyWidget
from PySide6.QtGui import QPainter, QFontMetrics
from PySide6.QtCore import QTimer
from ...Qtive.Component.helpers import create_font


class MarqueeLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.px = 0
        self.py = 0
        self.setWordWrap(True)
        self._speed = 2
        self.textLength = 0
        self.fontPointSize = 0
        self.n_loop = 0
        self._font = create_font(self)
        self.setStyleSheet("""
            background-color: transparent;
            color: white;
        """)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._tick)

    def setText(self, arg__1):
        super().setText(arg__1)

        if arg__1 != "":
            self.start(20)

    def start(self, interval=40):
        self.n_loop = 0
        self.updateCoordinates()
        self.setStyleSheet("""
            background-color: red;
            color: white;
        """)
        self.timer.start(interval)

    def stop(self):
        self.timer.stop()
        self.setStyleSheet("""
            background-color: transparent;
            color: white;
        """)
        self.setText("")

    def _tick(self):
        self.px -= self._speed
        if self.px <= -self.textLength:
            self.px = self.width()
            self.n_loop += 1
            if self.n_loop == 2:  # detener después de una vuelta
                self.stop()
        self.update()  # forzar repaint

    def updateCoordinates(self):
        self.fontPointSize = int(self.height() * 0.8)
        self.py = int(self.height() * 0.1)
        self.px = self.width()
        self._font.setPointSize(self.fontPointSize)
        self.textLength = QFontMetrics(self._font).horizontalAdvance(self.text())
        self._speed = self.px / 220

    def resizeEvent(self, event):
        self.updateCoordinates()
        super().resizeEvent(event)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.TextAntialiasing)
        painter.setFont(self._font)
        painter.drawText(self.px, self.py + self.fontPointSize, self.text())


class PMarquee(QGraphicsProxyWidget):
    def __init__(self, parent):
        QGraphicsProxyWidget.__init__(self)
        self.setParent(parent)
        self.marquee = MarqueeLabel()
        self.setWidget(self.marquee)

    def set_text(self, text: str):
        if text != "":
            self.marquee.setText(text)
        else:
            self.marquee.stop()

    def update(self):
        parente_size = self.parent().size()
        size_x, size_y = parente_size.width(), parente_size.height() // 10

        self.marquee.setFixedSize(size_x, size_y)
        self.setPos(0, (parente_size.height() - size_y))
