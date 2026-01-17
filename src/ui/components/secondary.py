from PySide6.QtWidgets import QMainWindow
from PySide6.QtCore import Qt, QCoreApplication, QEvent
from ...Qtive.Component.interfaces import Component, Floating, Container, Static
from ...Qtive.Props.content import Deploy
from ...Qtive.Props.events import OnClose


class Secondary(QMainWindow, Component, Floating, Container):
    def __init__(self, *args):
        QMainWindow.__init__(self)
        Component.__init__(self)
        Floating.__init__(self)
        Container.__init__(self)
        self.callback = None
        self.setWindowTitle("Proyeccion")
        self.setWindowFlags(
            Qt.Window
            | Qt.WindowStaysOnTopHint
            | Qt.FramelessWindowHint
            | Qt.WindowTitleHint
        )
        self.assign_props(args)
        self._first_polish_done = False
        self.installEventFilter(self)

    def eventFilter(self, obj, event):
        et = event.type()

        # Cuando Qt YA CALCULÓ tamaño + QSS + layout
        if et in (QEvent.Polish, QEvent.PolishRequest):
            if not self._first_polish_done and self.context:
                self._first_polish_done = True
                self.propagate_after_resize()
            return False

        # Cuando Qt recalcula el layout del widget
        if et == QEvent.LayoutRequest:
            if self._first_polish_done and self.context:
                self.propagate_after_resize()
            return False

        return False

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self._first_polish_done and self.context:
            self.propagate_after_resize()

    def assign_props(self, args):
        u_static = None
        for arg in args:
            if isinstance(
                arg,
                (Deploy, OnClose),
            ):
                self.props[arg.key] = arg.value
            elif isinstance(arg, (Static)):
                u_static = arg
            elif isinstance(arg, Floating):
                arg.anchor = self
                self.floatings.append(arg)

        if u_static:
            self.statics.append(u_static)

        for static in self.statics:
            self.setCentralWidget(static)

        if deploy := self.props.get("deploy", None):
            deploy.connect(self.deploy)

        if onclose := self.props.get("onclose", None):
            self.callback = onclose

    def deploy(self, b: bool):
        if not b:
            self.close()
            if self.callback:
                self.callback(False)
            return
        screens = QCoreApplication.instance().screens()
        if len(screens) > 1:
            self.show()
            self.context.get("window").activateWindow()
            if self.callback:
                self.callback(True)
        else:
            if self.callback:
                self.callback(False)

    def set_context(self, cont):
        super().set_context(cont)
        window = self.context.get("window")
        window.on_close.connect(self.close)

    def resize_statics(self):
        for static in self.statics:
            static.set_size(self.size())

    def set_size(self):
        screens = QCoreApplication.instance().screens()
        if len(screens) > 1:
            secondary_screen = screens[1]
            self.setGeometry(secondary_screen.geometry())
        else:
            self.close()

    def closeEvent(self, event):
        if self.callback:
            self.callback(False)
        event.accept()

    def propagate_after_resize(self):
        self.resize_floatings()
        self.resize_statics()
