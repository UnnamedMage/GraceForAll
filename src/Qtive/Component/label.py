from PySide6.QtWidgets import QLabel
from PySide6.QtCore import Signal, Qt, QEvent
from ..Props.visual import Width, Height, AspectRatio, Alignment, FontSize, Id
from ..Props.content import Image, Text, Attributes
from .interfaces import Interactive, Component, Static, Floating
from .helpers import image_or_svg_to_pixmap, create_font


class Label(QLabel, Component, Static, Interactive):
    def __init__(self, *args):
        QLabel.__init__(self)
        Component.__init__(self)
        Static.__init__(self)
        Interactive.__init__(self)
        self._image: str = None
        self.mode = None
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
                    Image,
                    FontSize,
                    Text,
                    Attributes,
                    Id,
                ),
            ):
                self.props[arg.key] = arg.value

            elif isinstance(arg, Floating):
                arg.anchor = self
                self.floatings.append(arg)

        if text := self.props.get("text", None):
            if isinstance(text, str):
                self.setText(text)
            elif isinstance(text, Signal):
                text.connect(self.setText)

        if image := self.props.get("image", None):
            if isinstance(image, str):
                self._image = image
            elif isinstance(image, Signal):
                image.connect(self.set_image)

        self.font_size = self.props.get("fontsize", 3)

        if attrs := self.props.get("attributes", None):
            if isinstance(attrs, Signal):
                attrs.connect(self.set_attributes)
            elif isinstance(attrs, dict):
                self.set_attributes(attrs)

        if id := self.props.get("id", None):
            self.setObjectName(id)

    def set_attributes(self, properties: dict):
        for key, value in properties.items():
            self.setter(key, value)

    def setter(self, attr, value):
        match attr:
            case "text_align":
                self.set_align(value)
            case "wrap":
                self.setWordWrap(value)
            case "text_mode":
                self.apply_text_mode(value)

    def apply_text_mode(self, mode):
        text = self.text()  # usar el texto ya asignado normalmente

        match mode:
            case "email":
                self.mode = mode
                self.setTextFormat(Qt.RichText)
                self.setOpenExternalLinks(True)
                flags = Qt.TextSelectableByMouse | Qt.LinksAccessibleByMouse
                self.setTextInteractionFlags(flags)
                if text:
                    self.setText(text)
            case "link":
                self.mode = mode
                self.setTextFormat(Qt.RichText)
                self.setOpenExternalLinks(True)
                flags = Qt.TextSelectableByMouse | Qt.LinksAccessibleByMouse
                self.setTextInteractionFlags(flags)
                if text:
                    self.setText(text)
            case "phone":
                self.mode = mode
                self.setTextFormat(Qt.RichText)
                self.setOpenExternalLinks(True)
                flags = Qt.TextSelectableByMouse | Qt.LinksAccessibleByMouse
                self.setTextInteractionFlags(flags)
                if text:
                    self.setText(text)
            case _:
                self.mode = None
                self.setTextFormat(Qt.PlainText)
                self.setTextInteractionFlags(Qt.NoTextInteraction)
                if text:
                    self.setText(text)

    def setText(self, arg__1):
        if not self.mode:
            return super().setText(arg__1)

        if self.mode == "email":
            html = f'<a href="mailto:{arg__1}">{arg__1}</a>'
            return super().setText(html)
        elif self.mode == "link":
            html = f'<a href="{arg__1}">{arg__1}</a>'
            return super().setText(html)
        elif self.mode == "phone":
            html = f'<a href="tel:{arg__1}">{arg__1}</a>'
            return super().setText(html)

    def set_align(self, align):
        if align == "left":
            h_align = Qt.AlignLeft
        elif align == "right":
            h_align = Qt.AlignRight
        else:  # "hcenter"
            h_align = Qt.AlignHCenter

        self.setAlignment(h_align | Qt.AlignVCenter)

    def set_image(self, image: str):
        self._image = image
        self.refresh_image()

    def refresh_image(self):
        if self.height() > 10 and self.width() > 10:
            pixmap = image_or_svg_to_pixmap(self, self._image)
            if pixmap:
                self.setPixmap(pixmap)

    def set_size(self, size):
        self.setFixedSize(size)

    def apply_style(self):
        self.setFont(create_font(self, self.font_size))
        self.refresh_image()

    def propagate_after_resize(self):
        self.apply_style()
        self.resize_floatings()
