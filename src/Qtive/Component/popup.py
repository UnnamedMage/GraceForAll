from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QVBoxLayout,
    QSizePolicy,
    QSpacerItem,
    QToolButton,
    QPushButton,
    QMainWindow,
)
from PySide6.QtGui import Qt
from PySide6.QtCore import QRect, QPoint, QSize, Signal, QEvent
from .interfaces import Component, Container, Floating, Static
from ..Props.visual import Height, Width, AspectRatio, Margins, Spacing, Orientation
from ..Props.content import Attributes, Deploy
from .helpers import separate_size
from math import floor


class Popup(QFrame, Component, Floating, Container):
    def __init__(self, *args):
        self.orientation: str
        self.position = "bottom"
        self.direction = "down"
        self.margin = 0
        QFrame.__init__(self)
        Container.__init__(self)
        Floating.__init__(self)
        Component.__init__(self)
        self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.setWindowFlags(Qt.Popup | Qt.FramelessWindowHint)
        self.setObjectName("popup")
        self.hide()
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
                    Orientation,
                    Width,
                    Height,
                    AspectRatio,
                    Spacing,
                    Margins,
                    Attributes,
                    Deploy,
                ),
            ):
                self.props[arg.key] = arg.value
            elif isinstance(arg, (Static, QSpacerItem)):
                self.statics.append(arg)
            elif isinstance(arg, Floating):
                arg.anchor = self
                self.floatings.append(arg)

        if self.props.get("orientation", "column") == "column":
            layout = QVBoxLayout(self)
            self.orientation = "column"
            intern_align = Qt.AlignHCenter
        else:
            layout = QHBoxLayout(self)
            self.orientation = "row"
            intern_align = Qt.AlignVCenter

        layout.setSpacing(self.props.get("spacing", 0))

        margins = self.props.get("margins", (0, 0, 0, 0))
        layout.setContentsMargins(*margins)

        for static in self.statics:
            align = static.props.get("alignment", None)
            if not isinstance(static, QSpacerItem):
                static.setParent(self)
                layout.addWidget(static, 0, align) if align else layout.addWidget(
                    static, 0, intern_align
                )
            else:
                layout.addItem(static)

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
            case "margin":
                self.margin = value

    def _flex_margin_space(self, window):
        margins = self.props.get("margins", (0, 0, 0, 0))
        spacing = self.props.get("spacing", 0)
        if isinstance(window, QMainWindow):
            w, h = window.size().width(), window.size().height()
            fw = w / 1920
            fh = h / 1032
            n_margins = []
            for i, margin in enumerate(margins):
                if i in (0, 3):
                    n = round(margin * fw)
                else:
                    n = round(margin * fh)
                n_margins.append(n)

            layout = self.layout()
            layout.setContentsMargins(*n_margins)

            if self.orientation == "row":
                n_spacing = round(spacing * fw)
            else:
                n_spacing = round(spacing * fh)

            layout.setSpacing(n_spacing)

            return n_margins, n_spacing
        else:
            self.layout().setContentsMargins(*margins)
            return margins, spacing

    def resize_statics(self):
        window = self.context.get("window")
        parent_size = self.contentsRect().size()
        items = len(self.statics)
        nitems = items - 1 if items > 0 else 0

        (left, top, right, bottom), spacing = self._flex_margin_space(window)

        usable_width = parent_size.width() - (left + right)
        usable_height = parent_size.height() - (top + bottom)

        if self.orientation == "row":
            usable_width = usable_width - (spacing * nitems)
        else:
            usable_height = usable_height - (spacing * nitems)

        # Usar estos tamaños en lugar de parent_size
        base_width = max(usable_width, 0)
        base_height = max(usable_height, 0)

        window_size = window.size()
        screen_size = window.screen().geometry().size()

        heights = []
        widths = []

        def calc(prop, base):
            if not prop:
                return None
            val, rule = separate_size(prop)
            if rule == "%":
                return int(base * min(val, 100) / 100)
            elif rule == "vw":
                return int(window_size.width() * min(val, 100) / 100)
            elif rule == "vh":
                return int(window_size.height() * min(val, 100) / 100)
            elif rule == "sw":
                return int(screen_size.width() * min(val, 100) / 100)
            elif rule == "sh":
                return int(screen_size.height() * min(val, 100) / 100)
            elif rule == "px":
                return int(val)
            return None

        for static in self.statics:
            width_prop = static.props.get("width", None)
            height_prop = static.props.get("height", None)
            aspect_prop = static.props.get("aspectratio", None)

            # Sin width ni height => depende del layout
            if not width_prop and not height_prop:
                heights.append("none" if self.orientation == "column" else base_height)
                widths.append("none" if self.orientation == "row" else base_width)
                continue

            # Parsear tamaños relativos o absolutos
            new_w = calc(width_prop, base_width)
            new_h = calc(height_prop, base_height)

            # Aplicar aspect ratio (solo si hay base definida)
            if aspect_prop and (new_w or new_h):
                try:
                    w_ratio, h_ratio = map(float, aspect_prop.split("-"))
                    if new_w and not new_h:
                        new_h = int(new_w * (h_ratio / w_ratio))
                    elif new_h and not new_w:
                        new_w = int(new_h * (w_ratio / h_ratio))
                    elif new_w and new_h:
                        try_w = new_w
                        try_h = int(try_w * (h_ratio / w_ratio))
                        if try_h > new_h:
                            try_h = new_h
                            try_w = int(try_h * (w_ratio / h_ratio))
                        if try_w > new_w:
                            try_w = new_w
                            try_h = int(try_w * (h_ratio / w_ratio))
                        new_w, new_h = try_w, try_h

                except Exception:
                    pass

            # Guardar resultados
            if new_w and new_h:
                heights.append(new_h)
                widths.append(new_w)
            elif new_w:  # solo ancho
                heights.append("none" if self.orientation == "column" else base_height)
                widths.append(new_w)
            elif new_h:  # solo alto
                heights.append(new_h)
                widths.append("none" if self.orientation == "row" else base_width)

        # --- SEGUNDA PASADA: Calcular espacio sobrante ---
        used_space = 0
        sizeless_branches = []

        for i, static in enumerate(self.statics):
            value = heights[i] if self.orientation == "column" else widths[i]
            if value == "none":
                sizeless_branches.append(i)
            else:
                used_space += value

        total_space = base_height if self.orientation == "column" else base_width
        available_space = max(total_space - used_space, 0)

        # Dividir espacio restante
        num_sizeless = len(sizeless_branches)
        space_per_branch = floor(available_space / num_sizeless) if num_sizeless else 0
        remainder = available_space - (space_per_branch * num_sizeless)

        # --- TERCERA PASADA: Aplicar tamaños finales ---
        for i, static in enumerate(self.statics):
            final_height = heights[i]
            final_width = widths[i]

            # Si no tiene tamaño definido, asignar el calculado
            if i in sizeless_branches:
                extra = remainder if i == sizeless_branches[-1] else 0
                if self.orientation == "column":
                    final_height = space_per_branch + extra
                    final_width = base_width
                else:
                    final_width = space_per_branch + extra
                    final_height = base_height

            # Aplicar tamaño fijo
            if hasattr(static, "set_size"):
                static.set_size(QSize(int(final_width), int(final_height)))

    def deploy(self, pos: QPoint = None):
        if not pos:
            parent_rect: QRect = self.anchor.geometry()
            global_pos: QPoint = self.anchor.mapToGlobal(QPoint(0, 0))
        else:
            parent_rect: QRect = QRect(0, 0)
            global_pos: QPoint = self.anchor.mapToGlobal(pos)

        x, y = global_pos.x(), global_pos.y()
        hook_w, hook_h = parent_rect.width(), parent_rect.height()

        w = self.width()
        h = self.height()

        margin = self.margin

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

            new_y -= margin
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
            new_y += margin
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
            new_x -= margin
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
            new_x += margin
        self.move(new_x, new_y)
        self.show()

    def set_size(self):
        parent_size = self.anchor.size()
        window = self.context.get("window")
        window_size = window.size()
        screen_size = window.screen().geometry().size()

        def calc(prop, base):
            if not prop:
                return None
            val, rule = separate_size(prop)
            if rule == "%":
                return int(base * val / 100)
            elif rule == "vw":
                return int(window_size.width() * min(val, 100) / 100)
            elif rule == "vh":
                return int(window_size.height() * min(val, 100) / 100)
            elif rule == "sw":
                return int(screen_size.width() * min(val, 100) / 100)
            elif rule == "sh":
                return int(screen_size.height() * min(val, 100) / 100)
            elif rule == "px":
                return int(val)
            return None

        width_prop = self.props.get("width", None)
        height_prop = self.props.get("height", None)
        aspect_prop = self.props.get("aspectratio", None)

        if not width_prop and not height_prop:
            self.setFixedSize(parent_size)
            return

        new_w = calc(width_prop, parent_size.width())
        new_h = calc(height_prop, parent_size.height())

        # Aplicar aspect ratio (solo si hay base definida)
        if aspect_prop and (new_w or new_h):
            try:
                w_ratio, h_ratio = map(float, aspect_prop.split("-"))
                if new_w and not new_h:
                    new_h = int(new_w * (h_ratio / w_ratio))
                elif new_h and not new_w:
                    new_w = int(new_h * (w_ratio / h_ratio))
                elif new_w and new_h:
                    try_w = new_w
                    try_h = int(try_w * (h_ratio / w_ratio))
                    if try_h > new_h:
                        try_h = new_h
                        try_w = int(try_h * (w_ratio / h_ratio))
                    if try_w > new_w:
                        try_w = new_w
                        try_h = int(try_w * (h_ratio / w_ratio))
                    new_w, new_h = try_w, try_h

            except Exception:
                pass

        if new_w and new_h:
            self.setFixedSize(QSize(new_w, new_h))
        elif new_w:  # solo ancho
            self.setFixedSize(QSize(new_w, parent_size.height()))
        elif new_h:  # solo alto
            self.setFixedSize(QSize(parent_size.width(), new_h))

    def closeEvent(self, event):  # ← tu función
        super().closeEvent(event)
        if isinstance(self.anchor, (QToolButton, QPushButton)):
            self.anchor.setAttribute(Qt.WA_UnderMouse, False)
            self.anchor.unsetCursor()
            self.anchor.update()

    def propagate_after_resize(self):
        self.resize_statics()
        self.resize_floatings()
