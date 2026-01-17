from PySide6.QtWidgets import QSlider
from PySide6.QtCore import Qt, Signal, QEvent
from ...Qtive.Component.interfaces import Interactive, Component, Static, Floating
from ...Qtive.Props.visual import Width, Height, AspectRatio, Alignment, Orientation
from ...Qtive.Props.content import Attributes, Index
from ...Qtive.Props.events import OnUpdate
from types import FunctionType, LambdaType, MethodType


class Slider(QSlider, Component, Static, Interactive):
    def __init__(self, *args):
        QSlider.__init__(self)
        Component.__init__(self)
        Static.__init__(self)
        Interactive.__init__(self)
        self.setRange(0, 100)
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
                (
                    Width,
                    Height,
                    AspectRatio,
                    Alignment,
                    Orientation,
                    Attributes,
                    Index,
                    OnUpdate,
                ),
            ):
                self.props[arg.key] = arg.value

            elif isinstance(arg, Floating):
                arg.anchor = self
                self.floatings.append(arg)

        if self.props.get("orientation", "column") == "column":
            self.setOrientation(Qt.Orientation.Vertical)
        else:
            self.setOrientation(Qt.Orientation.Horizontal)

        if index := self.props.get("index", None):
            if isinstance(index, Signal):
                index.connect(self.setValue)

        if onupdate := self.props.get("onupdate", None):
            if isinstance(onupdate, (FunctionType, MethodType, LambdaType)):
                self.sliderMoved.connect(onupdate)

        if attrs := self.props.get("attributes", None):
            if isinstance(attrs, Signal):
                attrs.connect(self.set_attributes)
            elif isinstance(attrs, dict):
                self.set_attributes(attrs)

    def set_attributes(self, properties: dict):
        for key, value in properties.items():
            self.setter(key, value)

    def setter(self, attr, value):
        match attr:
            case "range":
                self.setRange(*value)

    def set_size(self, size):
        self.setFixedSize(size)

    def propagate_after_resize(self):
        self.resize_floatings()
