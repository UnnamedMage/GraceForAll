from PySide6.QtWidgets import QTextEdit, QFrame, QApplication
from PySide6.QtCore import QRect, Qt, QTimer, Signal, QEvent
from PySide6.QtGui import QTextCursor, QPainter, QPalette
from ...Qtive.Props.visual import Width, Height, AspectRatio, Alignment, FontSize
from ...Qtive.Props.content import Attributes, PlaceHolder, Text
from ...Qtive.Props.events import OnClick, OnTextChange
from ...Qtive.Component.interfaces import Interactive, Component, Static, Floating
from ...Qtive.Component.helpers import create_font


class LyricsEdit(QTextEdit, Component, Static, Interactive):
    def __init__(self, *args):
        QTextEdit.__init__(self)
        Component.__init__(self)
        Interactive.__init__(self)
        Static.__init__(self)
        self.onclick_timer = None
        self.ontextchange_timer = None
        self.selected_paragraph = ""
        self._placeholder_text = ""
        self.setContextMenuPolicy(Qt.NoContextMenu)
        self.highlight_frame = QFrame(self.viewport())
        self.highlight_frame.setStyleSheet(
            "background-color: rgba(200, 200, 200, 60); border: none;"
        )
        self.highlight_frame.hide()
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
                    Attributes,
                    PlaceHolder,
                    OnClick,
                    OnTextChange,
                    Text,
                ),
            ):
                self.props[arg.key] = arg.value

            elif isinstance(arg, Floating):
                arg.anchor = self
                self.floatings.append(arg)

        self.font_size = self.props.get("fontsize", 3)

        if placeholder := self.props.get("placeholder"):
            self._placeholder_text = placeholder

        if onclick := self.props.get("onclick"):
            self.onclick_timer = QTimer(self)
            self.onclick_timer.setSingleShot(True)
            self.onclick_timer.timeout.connect(lambda: onclick(self.selected_paragraph))
            self.cursorPositionChanged.connect(lambda: self.get_paragraph())
            self.cursorPositionChanged.connect(lambda: self.onclick_timer.start(400))

        if ontextchange := self.props.get("ontextchange"):
            self.ontextchange_timer = QTimer(self)
            self.ontextchange_timer.setSingleShot(True)
            self.ontextchange_timer.timeout.connect(
                lambda: ontextchange(self.toPlainText())
            )
            self.textChanged.connect(lambda: self.ontextchange_timer.start(400))

        if text := self.props.get("text"):
            if isinstance(text, Signal):
                text.connect(self.setPlainText)
            elif isinstance(text, str):
                self.setPlainText(text)

    def paintEvent(self, event):
        super().paintEvent(event)

        if not self.toPlainText() and self._placeholder_text:
            painter = QPainter(self.viewport())
            painter.setFont(self.font())
            painter.setPen(self.palette().color(QPalette.ColorRole.Text))
            painter.setOpacity(0.5)

            margin = self.document().documentMargin()
            painter.drawText(
                margin,
                margin + self.fontMetrics().ascent(),
                self._placeholder_text,
            )
            painter.end()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_V and event.modifiers() & Qt.ControlModifier:
            self.paste()
            return True
        super().keyPressEvent(event)
        if event.key() == Qt.Key_Backspace:
            if not self.toPlainText():
                self.onclick_timer.start(1)

    def get_paragraph(self):
        self.blockSignals(True)

        full_text = self.toPlainText()
        lines = full_text.splitlines()

        cursor = self.textCursor()
        cursor_position = cursor.position()

        if cursor.block().text().strip() == "":
            self.highlight_frame.hide()
            self.blockSignals(False)
            self.selected_paragraph = ""
            return

        char_count = 0
        current_line_index = 0
        for i, line in enumerate(lines):
            char_count += len(line) + 1
            if char_count > cursor_position:
                current_line_index = i
                break

        start = current_line_index
        while start > 0 and lines[start - 1].strip() != "":
            start -= 1

        end = current_line_index
        while end < len(lines) - 1 and lines[end + 1].strip() != "":
            end += 1

        texto_seleccionado = "\n".join(lines[start : end + 1]).strip()
        self._update_highlight()
        self.blockSignals(False)
        self.selected_paragraph = texto_seleccionado
        return

    def _update_highlight(self):
        cursor = self.textCursor()
        document = self.document()

        full_text = self.toPlainText()
        lines = full_text.splitlines()
        cursor_position = cursor.position()

        # Encontrar índice de línea actual
        char_count = 0
        current_line_index = 0
        for i, line in enumerate(lines):
            char_count += len(line) + 1
            if char_count > cursor_position:
                current_line_index = i
                break

        # Determinar inicio y fin del bloque (como antes)
        start = current_line_index
        while start > 0 and lines[start - 1].strip() != "":
            start -= 1

        end = current_line_index
        while end < len(lines) - 1 and lines[end + 1].strip() != "":
            end += 1

        if start > end:
            self.highlight_frame.hide()
            return

        # Obtener posición visual del bloque en viewport
        start_block = document.findBlockByNumber(start)
        end_block = document.findBlockByNumber(end)

        cursor_start = QTextCursor(start_block)
        cursor_end = QTextCursor(end_block)
        cursor_end.movePosition(QTextCursor.EndOfBlock)

        rect_start = self.cursorRect(cursor_start)
        rect_end = self.cursorRect(cursor_end)

        # Crear un QRect que encierre el bloque completo
        top = rect_start.top()
        height = rect_end.bottom() - rect_start.top()
        width = self.viewport().width()

        block_rect = QRect(0, top, width, height)
        self.highlight_frame.setGeometry(block_rect)
        self.highlight_frame.show()

    def set_size(self, size):
        self.setFixedSize(size)

    def paste(self):
        self.blockSignals(True)
        pasted_text = QApplication.clipboard().text()
        self.insertPlainText(pasted_text)
        self.blockSignals(False)
        self.cursorPositionChanged.emit()
        self.textChanged.emit()

    def dropEvent(self, e):
        self.paste()
        return True

    def apply_style(self):
        font = create_font(self, self.font_size)
        self.setFont(font)

    def propagate_after_resize(self):
        self.apply_style()
        self.highlight_frame.hide()
        self.resize_floatings()
