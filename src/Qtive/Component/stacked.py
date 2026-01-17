from PySide6.QtWidgets import QSizePolicy, QStackedWidget
from PySide6.QtCore import Signal, QEvent
from .frame import Frame
from ..Props.visual import Width, Height, AspectRatio, Alignment, Orientation
from ..Props.content import Index
from .interfaces import Component, Container, Static, Floating


class Stacked(QStackedWidget, Component, Static, Container):
    def __init__(self, *args):
        QStackedWidget.__init__(self)
        Component.__init__(self)
        Static.__init__(self)
        Container.__init__(self)
        self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
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
        for arg in args:
            if isinstance(
                arg,
                (Orientation, Width, Height, AspectRatio, Alignment, Index),
            ):
                self.props[arg.key] = arg.value
            elif isinstance(arg, Static):
                self.statics.append(arg)
            elif isinstance(arg, Floating):
                arg.anchor = self
                self.floatings.append(arg)

        for static in self.statics:
            self.addWidget(static)

        self.setCurrentIndex(0)

        if index := self.props.get("index", None):
            if isinstance(index, int):
                self.setCurrentIndex(index)
            elif isinstance(index, Signal):
                index.connect(self.setCurrentIndex)

    def resize_statics(self):
        parent_size = self.size()
        for static in self.statics:
            if hasattr(static, "set_size"):
                if not isinstance(static, Frame):
                    static.set_size(parent_size)
                else:
                    static.propagate_after_resize()

    def set_size(self, size):
        self.setFixedSize(size)

    def propagate_after_resize(self):
        self.resize_floatings()
        self.resize_statics()
