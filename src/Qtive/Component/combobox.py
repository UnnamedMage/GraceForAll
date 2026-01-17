from PySide6.QtWidgets import QComboBox
from PySide6.QtCore import Signal, QEvent
from ..Props.visual import Width, Height, AspectRatio, Alignment, FontSize
from ..Props.content import Attributes, Items, Index
from ..Props.events import OnClick
from .interfaces import Interactive, Component, Static, Floating
from .helpers import create_font


class ComboBox(QComboBox, Component, Static, Interactive):
    def __init__(self, *args):
        QComboBox.__init__(self)
        Component.__init__(self)
        Interactive.__init__(self)
        Static.__init__(self)
        self.items = []
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
                    Alignment,
                    Height,
                    Width,
                    AspectRatio,
                    FontSize,
                    Attributes,
                    Index,
                    Items,
                    OnClick,
                ),
            ):
                self.props[arg.key] = arg.value
            elif isinstance(arg, Floating):
                arg.anchor = self
                self.floatings.append(arg)

        self.font_size = self.props.get("fontsize", 10)

        if items := self.props.get("items"):
            if isinstance(items, list):
                self.add_items(items)
            elif isinstance(items, Signal):
                items.connect(self.add_items)

        if index := self.props.get("index"):
            if isinstance(index, int):
                self.set_current_index(index)
            elif isinstance(index, Signal):
                index.connect(self.set_current_index)

        if onclick := self.props.get("onclick"):
            self.currentIndexChanged.connect(onclick)

    def set_current_index(self, index):
        self.blockSignals(True)
        self.setCurrentIndex(index)
        self.blockSignals(False)

    def add_items(self, items: list):
        self.clear()
        self.items = items
        self.addItems(items)

    def set_size(self, size):
        self.setFixedSize(size)

    def apply_style(self):
        font = create_font(self, self.font_size)
        self.setFont(font)

    def propagate_after_resize(self):
        self.apply_style()
        self.resize_floatings()
