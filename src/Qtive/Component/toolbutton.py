from PySide6.QtWidgets import QToolButton, QStyleOptionToolButton, QStyle
from PySide6.QtGui import QPainter, QFontMetrics, QIcon, QFont
from PySide6.QtCore import QRect, Qt, Signal, QSize, QEvent
from ..Props.visual import (
    Width,
    Height,
    AspectRatio,
    Alignment,
    FontSize,
    Orientation,
    Id,
)
from ..Props.content import Image, Text, Attributes
from ..Props.events import OnClick
from .interfaces import Interactive, Component, Static, Floating
from .helpers import image_or_svg_to_pixmap, create_font


class ToolButton(QToolButton, Component, Static, Interactive):
    def __init__(self, *args):
        QToolButton.__init__(self)
        Component.__init__(self)
        Static.__init__(self)
        Interactive.__init__(self)
        self.contents: dict = {}
        self._icon: str = None
        self.icon_position = Qt.AlignRight
        self.bold = False
        self.italic = False
        self._locked = None
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
                    OnClick,
                    FontSize,
                    Attributes,
                    Orientation,
                    Id,
                ),
            ):
                self.props[arg.key] = arg.value

            elif isinstance(arg, (Text, Image)):
                self.contents[arg.key] = arg.value

            elif isinstance(arg, Floating):
                arg.anchor = self
                self.floatings.append(arg)

        if attrs := self.props.get("attributes", None):
            if isinstance(attrs, Signal):
                attrs.connect(self.set_attributes)
            elif isinstance(attrs, dict):
                self.set_attributes(attrs)

        if self.contents != {}:
            last = list(self.contents.items())[-1][0]
        else:
            last = "text"

        align = self.props.get("Orientation", "row")

        if align == "row" and last == "imagen":
            self.icon_position = Qt.AlignRight
        elif align == "row" and last == "text":
            self.icon_position = Qt.AlignLeft
        elif align == "column" and last == "imagen":
            self.icon_position = Qt.AlignBottom
        elif align == "column" and last == "text":
            self.icon_position = Qt.AlignTop

        for key, value in self.contents.items():
            if key == "text":
                if isinstance(value, str):
                    self.setText(value)
                elif isinstance(value, Signal):
                    value.connect(self.setText)
            elif key == "image":
                if isinstance(value, str):
                    self._icon = value
                elif isinstance(value, Signal):
                    value.connect(self.set_icon)

        self.font_size = self.props.get("fontsize", 3)

        if on_click := self.props.get("onclick", None):
            self.clicked.connect(lambda: on_click())

        if id := self.props.get("id", None):
            self.setObjectName(id)

    def set_attributes(self, properties: dict):
        for key, value in properties.items():
            self.setter(key, value)

    def setter(self, attr, value):
        match attr:
            case "bold":
                self.bold = value
            case "italic":
                self.italic = value
            case "disabled":
                self.setDisabled(value)
            case "visible":
                self.setVisible(value)
            case "checked":
                self.set_checked(value)

    def set_checked(self, value):
        self.setCheckable(value)
        self.setChecked(value)
        self._locked = value
        self.setAttribute(Qt.WA_UnderMouse, False)
        self.unsetCursor()
        self.update()

    def set_icon(self, icon: str):
        self._icon = icon
        self.refresh_icon()

    def refresh_icon(self):
        if self.height() > 10 and self.width() > 10:
            pixmap = image_or_svg_to_pixmap(self, self._icon)
            if pixmap:
                self.setIcon(QIcon(pixmap))

    def mousePressEvent(self, event):
        if not self._locked:
            super().mousePressEvent(event)
        else:
            self.clicked.emit()

    def paintEvent(self, event):
        painter = QPainter(self)
        option = QStyleOptionToolButton()
        self.initStyleOption(option)
        self.style().drawPrimitive(QStyle.PE_PanelButtonTool, option, painter, self)

        icon = self.icon()
        text = self.text()
        has_icon = not icon.isNull()
        has_text = bool(text)

        w, h = self.width(), self.height()
        margin_factor = 0.8  # margen de seguridad (20%)

        if has_icon and has_text:
            fm = QFontMetrics(self.font())
            text_height = fm.height()
            icon_size = icon.actualSize(QSize(w, h))

            if self.icon_position == Qt.AlignLeft:
                # Ícono primero (izquierda), texto en el espacio restante (derecha)
                icon_w = int(icon_size.width() * margin_factor)
                icon_h = int(icon_size.height() * margin_factor)
                aspect_ratio = (
                    icon_size.width() / icon_size.height() if icon_size.height() else 1
                )

                # ajustar manteniendo aspect ratio dentro del alto disponible
                if icon_w > h * aspect_ratio:
                    icon_w = int(h * aspect_ratio * margin_factor)
                    icon_h = int(h * margin_factor)
                else:
                    icon_h = int(icon_w / aspect_ratio)

                icon_x = int(5 + (h - icon_h) / 2)
                icon_y = int((h - icon_h) / 2)
                icon_rect = QRect(icon_x, icon_y, icon_h, icon_h)

                text_rect = QRect(
                    icon_rect.right() + 8, 0, w - icon_rect.right() - 10, h
                )

                # --- Dibujar ---
                icon.paint(painter, icon_rect, Qt.AlignCenter)
                painter.drawText(text_rect, Qt.AlignVCenter | Qt.AlignLeft, text)

            elif self.icon_position == Qt.AlignRight:
                # Ícono primero (derecha), texto en el espacio restante (izquierda)
                icon_w = int(icon_size.width() * margin_factor)
                icon_h = int(icon_size.height() * margin_factor)
                aspect_ratio = (
                    icon_size.width() / icon_size.height() if icon_size.height() else 1
                )

                if icon_w > h * aspect_ratio:
                    icon_w = int(h * aspect_ratio * margin_factor)
                    icon_h = int(h * margin_factor)
                else:
                    icon_h = int(icon_w / aspect_ratio)

                icon_x = w - icon_w - 5
                icon_y = int((h - icon_h) / 2)
                icon_rect = QRect(icon_x, icon_y, icon_w, icon_h)

                text_rect = QRect(5, 0, icon_rect.x() - 10, h)

                # --- Dibujar ---
                icon.paint(painter, icon_rect, Qt.AlignCenter)
                painter.drawText(text_rect, Qt.AlignVCenter | Qt.AlignRight, text)

            elif self.icon_position == Qt.AlignTop:
                # Texto primero (abajo), ícono arriba con margen extra
                w_margin = int(w * 0.1)
                h_margin = int(h * 0.1)

                text_rect = QRect(
                    0, h - text_height - h_margin, w, text_height + h_margin
                )
                icon_h = h - int(2 * h_margin) - text_height
                icon_rect = QRect(w_margin, h_margin, w - (2 * w_margin), icon_h)

                # --- Dibujar ---
                painter.drawText(text_rect, Qt.AlignHCenter | Qt.AlignTop, text)
                icon.paint(painter, icon_rect, Qt.AlignCenter)

            elif self.icon_position == Qt.AlignBottom:
                # Texto primero (arriba), ícono abajo con margen extra

                w_margin = int(w * 0.1)
                h_margin = int(h * 0.1)

                text_rect = QRect(0, 0, w, text_height + h_margin)
                icon_h = h - int(2 * h_margin) - text_height
                icon_rect = QRect(
                    w_margin, h_margin + text_height, w - (2 * w_margin), icon_h
                )

                # --- Dibujar --
                painter.drawText(text_rect, Qt.AlignHCenter | Qt.AlignBottom, text)
                icon.paint(painter, icon_rect, Qt.AlignCenter)

        elif has_icon:
            # solo ícono (centrado, con margen)
            icon_size = icon.actualSize(QSize(w, h))
            icon_w = int(icon_size.width() * margin_factor)
            icon_h = int(icon_size.height() * margin_factor)
            aspect_ratio = (
                icon_size.width() / icon_size.height() if icon_size.height() else 1
            )

            if icon_w > h * aspect_ratio:
                icon_w = int(h * aspect_ratio * margin_factor)
                icon_h = int(h * margin_factor)
            else:
                icon_h = int(icon_w / aspect_ratio)

            icon_x = (w - icon_w) // 2
            icon_y = (h - icon_h) // 2
            icon_rect = QRect(icon_x, icon_y, icon_w, icon_h)
            icon.paint(painter, icon_rect, Qt.AlignCenter)

        elif has_text:
            # solo texto
            text_rect = QRect(0, 0, w, h)
            painter.drawText(text_rect, Qt.AlignCenter, text)

        else:
            super().paintEvent(event)

    def set_size(self, size):
        self.setFixedSize(size)

    def apply_style(self):
        font = create_font(self, self.font_size)
        font.setWeight(QFont.Weight.ExtraBold if self.bold else QFont.Weight.Bold)
        font.setItalic(self.italic)
        self.setFont(font)
        self.refresh_icon()

    def propagate_after_resize(self):
        self.apply_style()
        self.resize_floatings()
