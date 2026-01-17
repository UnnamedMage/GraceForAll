from PySide6.QtWidgets import (
    QFrame,
    QVBoxLayout,
    QSizePolicy,
    QListWidget,
    QListWidgetItem,
    QAbstractItemView,
)
from PySide6.QtGui import Qt, QFontMetrics
from PySide6.QtCore import QRect, QPoint, Signal, QEvent
from .interfaces import Component, Interactive, Floating
from ..Props.visual import FontSize
from ..Props.content import Attributes, Items, Deploy
from .helpers import create_font


class Menu(QFrame, Component, Floating, Interactive):
    def __init__(self, *args):
        self.position = "bottom"
        self.direction = "down"
        self.items = []
        self.callback = None
        self.larger_item = ""
        QFrame.__init__(self)
        Interactive.__init__(self)
        Floating.__init__(self)
        Component.__init__(self)
        self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.setWindowFlags(Qt.Popup | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.hide()
        self.list = QListWidget(self)
        self.list.setSelectionMode(QAbstractItemView.SingleSelection)
        self.list.itemClicked.connect(lambda i: self.on_click(i))
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.list)
        self.assign_props(args)
        self._first_polish_done = False
        self.installEventFilter(self)

    def eventFilter(self, obj, event):
        et = event.type()

        # Cuando Qt YA CALCULÓ tamaño + QSS + layout
        if et in (QEvent.Polish, QEvent.PolishRequest):
            if not self._first_polish_done and self.context:
                self._first_polish_done = True
            return False

        # Cuando Qt recalcula el layout del widget
        if et == QEvent.LayoutRequest:
            if self._first_polish_done and self.context:
                pass
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
                (Items, FontSize, Attributes, Deploy),
            ):
                self.props[arg.key] = arg.value

            elif isinstance(arg, Floating):
                arg.anchor = self
                self.floatings.append(arg)

        self.font_size = self.props.get("fontsize", 3)

        if items := self.props.get("items"):
            if isinstance(items, list):
                self.add_items(items)
            elif isinstance(items, Signal):
                items.connect(self.add_items)

        if deploy := self.props.get("deploy", None):
            deploy.connect(self.deploy)

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
            case "position":
                self.position = value
            case "direction":
                self.direction = value

    def add_items(self, items: list[str]):
        self.items = items
        self.list.clear()
        for label in items:
            self.larger_item = (
                label if len(label) > len(self.larger_item) else self.larger_item
            )
            QListWidgetItem(label, self.list)
        self.set_size_by_items()

    def on_click(self, item: QListWidgetItem):
        index = self.list.indexFromItem(item).row()
        self.close()
        if self.callback:
            self.callback(index)
            self.callback = None

    def set_size_by_items(self):
        if not self.context:
            return
        font = create_font(self, self.font_size)
        self.list.setFont(font)
        rows = len(self.items)
        if rows == 0:
            total_height = 0
        elif rows <= 6:
            total_height = sum(QFontMetrics(font).height() + 2 for i in range(rows))
        else:
            total_height = (QFontMetrics(font).height() + 2) * 6
        width = int(QFontMetrics(font).horizontalAdvance(self.larger_item) * 1.4)
        self.list.setFixedSize(width, total_height)
        self.setFixedSize(width, total_height)

    def deploy(self, data: dict):
        pos = data.get("pos")
        self.callback = data.get("callback")

        if not pos:
            parent_rect: QRect = self.anchor.geometry()
            global_pos: QPoint = self.anchor.mapToGlobal(QPoint(0, 0))
        else:
            parent_rect: QRect = QRect(
                0,
                0,
                0,
                0,
            )
            global_pos: QPoint = self.anchor.mapToGlobal(pos)

        x, y = global_pos.x(), global_pos.y()
        hook_w, hook_h = parent_rect.width(), parent_rect.height()

        w = self.width()
        h = self.height()

        # --- POSICIÓN (punto de enganche) ---
        if self.position == "top":
            match self.direction:
                case "down":
                    new_x, new_y = x + (hook_w - w) // 2, y
                case "up":
                    new_x, new_y = x + (hook_w - w) // 2, y - h
                case "left":
                    new_x, new_y = x + hook_w - w, y - hook_h
                case "right":
                    new_x, new_y = x, y - hook_h
        elif self.position == "bottom":
            match self.direction:
                case "down":
                    new_x, new_y = x + (hook_w - w) // 2, y + hook_h
                case "up":
                    new_x, new_y = x + (hook_w - w) // 2, y + hook_h - h
                case "left":
                    new_x, new_y = x + hook_w - w, y + hook_h
                case "right":
                    new_x, new_y = x, y + hook_h
        elif self.position == "left":
            match self.direction:
                case "down":
                    new_x, new_y = x - w, y
                case "up":
                    new_x, new_y = x - w, y + hook_h - h
                case "left":
                    new_x, new_y = x - w, y + (hook_h - h) // 2
                case "right":
                    new_x, new_y = x, y + (hook_h - h) // 2
        elif self.position == "right":
            match self.direction:
                case "down":
                    new_x, new_y = x + hook_w, y
                case "up":
                    new_x, new_y = x + hook_w, y + hook_h - h
                case "left":
                    new_x, new_y = x + hook_w - w, y + (hook_h - h) // 2
                case "right":
                    new_x, new_y = x + hook_w, y + (hook_h - h) // 2
        self.move(new_x, new_y)
        self.list.clearFocus()
        self.list.clearSelection()
        self.show()

    def set_size(self):
        self.set_size_by_items()

    def propagate_after_resize(self):
        self.resize_floatings()
