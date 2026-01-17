from PySide6.QtWidgets import QLineEdit, QCompleter
from PySide6.QtCore import Qt, Signal, QEvent
from PySide6.QtGui import QPainter, QFontMetrics, QPalette
from ..Props.visual import Width, Height, AspectRatio, Alignment, FontSize
from ..Props.content import Text, Attributes, PlaceHolder
from ..Props.events import OnTextChange, OnEnterPress
from .interfaces import Interactive, Component, Static, Floating
from .helpers import create_font


class LineEdit(QLineEdit, Component, Static, Interactive):
    enter_pressed = Signal(str)

    def __init__(self, *args):
        QLineEdit.__init__(self)
        Component.__init__(self)
        Static.__init__(self)
        Interactive.__init__(self)
        self._placeholder_text = ""
        self._completer = None
        self.setContextMenuPolicy(Qt.NoContextMenu)
        self.setClearButtonEnabled(True)
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
                    FontSize,
                    Text,
                    PlaceHolder,
                    Attributes,
                    OnTextChange,
                    OnEnterPress,
                ),
            ):
                self.props[arg.key] = arg.value
            elif isinstance(arg, Floating):
                arg.anchor = self
                self.floatings.append(arg)

        self.font_size = self.props.get("fontsize", 3)
        self._placeholder_text = self.props.get("placeholder", "")

        if ontextchange := self.props.get("ontextchange", None):
            self.textChanged.connect(ontextchange)

        if onenterpress := self.props.get("onenterpress"):
            self.enter_pressed.connect(onenterpress)

        if text := self.props.get("text", None):
            if isinstance(text, str):
                self.set_text(text)
            elif isinstance(text, Signal):
                text.connect(self.set_text)

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
            case "completer":
                self.set_completer(value)
            case "mode_password":
                self.setModePassword() if value else None

    def set_text(self, text: str):
        self.blockSignals(True)
        self.setText(text)
        self.blockSignals(False)

    def set_completer(self, dictionary: list):
        self._completer = QCompleter(dictionary, self)
        self._completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.setCompleter(self._completer)

    def setModePassword(self):
        self.setEchoMode(QLineEdit.Password)

    def paintEvent(self, event):
        super().paintEvent(event)
        if not self.text() and self._placeholder_text and self._first_polish_done:
            painter = QPainter(self)
            painter.setPen(self.palette().color(QPalette.ColorRole.Text))
            painter.setOpacity(0.5)
            fm = QFontMetrics(self.font())
            margin = self.textMargins().left() + 2
            baseline = (self.height() + fm.ascent() - fm.descent()) // 2
            painter.drawText(margin, baseline, self._placeholder_text)
            painter.end()

    def set_size(self, size):
        self.setFixedSize(size)

    def keyPressEvent(self, event):
        super().keyPressEvent(event)
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            text = self.text()
            self.enter_pressed.emit(text)

    def apply_style(self):
        font = create_font(self, self.font_size)
        self.setFont(font)
        if self._completer:
            popup = self._completer.popup()
            popup.setFont(font)
            self.setCompleter(self._completer)

    def propagate_after_resize(self):
        self.apply_style()
        self.resize_floatings()
