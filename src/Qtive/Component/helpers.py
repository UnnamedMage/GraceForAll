from PySide6.QtWidgets import QToolButton, QApplication
from PySide6.QtGui import QPainter, QPixmap, QColor, QPalette, QFont
from PySide6.QtCore import Qt, QSizeF, QObject, QPoint, QEvent, Signal
from PySide6.QtSvg import QSvgRenderer
from ...common import get_platform_path
import os


class Context:
    def __init__(self, **kwargs):
        self.data = kwargs

    def get(self, key, default=None):
        return self.data.get(key, default)

    def set(self, key, value):
        self.data[key] = value


def separate_size(size_prop: str):
    size_prop = size_prop.strip()
    value: float = 0
    rule: str = ""
    try:
        if size_prop.endswith("%"):
            value = float(size_prop[:-1])
            rule = "%"
        elif size_prop.endswith("vw"):
            value = float(size_prop[:-2])
            rule = "vw"
        elif size_prop.endswith("vh"):
            value = float(size_prop[:-2])
            rule = "vh"
        elif size_prop.endswith("sw"):
            value = float(size_prop[:-2])
            rule = "sw"
        elif size_prop.endswith("sh"):
            value = float(size_prop[:-2])
            rule = "sh"
        elif size_prop.endswith("px"):
            value = float(size_prop[:-2])
            rule = "px"
    except ValueError:
        pass

    if rule == "":
        raise ValueError("Invalid width or height")
    else:
        return value, rule


ASSETS = get_platform_path("intern", "assets", "icons")


def image_or_svg_to_pixmap(component, source: str) -> QPixmap | None:
    if not source:
        return None
    source = f"{ASSETS}\\{source}"
    if not os.path.exists(source):
        return None

    if source.endswith(".svg"):
        try:
            if isinstance(component, QToolButton):
                text_color = component.palette().color(QPalette.ButtonText)
            else:
                text_color = component.palette().color(QPalette.WindowText)
            hex_color = text_color.name(QColor.HexRgb)
            with open(source, "r", encoding="utf-8") as file:
                svg_data = file.read()
            svg_data = svg_data.replace('fill="currentColor"', f'fill="{hex_color}"')
            svg_data = svg_data.replace(
                'stroke="currentColor"', f'stroke="{hex_color}"'
            )
            data = svg_data
        except Exception:
            return None

        renderer = QSvgRenderer(bytearray(data, encoding="utf-8"))

        viewbox = renderer.viewBoxF()
        viewbox_size = viewbox.size()
        scaled_size = viewbox_size.scaled(
            QSizeF(component.width(), component.height()), Qt.KeepAspectRatio
        )

        out_pixmap = QPixmap(int(scaled_size.width()), int(scaled_size.height()))
        out_pixmap.fill(Qt.transparent)
        if scaled_size.width() > 10 or scaled_size.height() > 10:
            painter = QPainter(out_pixmap)
            renderer.render(painter)
            painter.end()
        return out_pixmap
    else:
        data = QPixmap(source)
        if data.isNull():
            return None

        out_pixmap = data.scaled(
            component.width(),
            component.height(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation,
        )
        return out_pixmap


def create_font(parent_widget, font_size: float = None) -> QFont:
    if not font_size:
        font = QFont("Segoe UI")
        font.setWeight(QFont.Bold)
        return font

    context: Context = parent_widget.context

    reference_height = 1080
    min_size = 6
    max_size = 72
    base_size = font_size * 5

    # Obtener pantalla asociada al widget o fallback
    window = context.get("window")
    if window is None:
        screen = QApplication.primaryScreen()
        window_height = 0
    else:
        screen = window.screen()
        window_height = window.height()

    if window_height <= 0:
        # Fallback si aún no está visible
        window_height = screen.size().height() if screen else reference_height

    logical_dpi = screen.logicalDotsPerInch() if screen else 96

    # Calcular escalado
    scale_factor = (window_height / reference_height) * (96 / logical_dpi)
    scaled_size = max(min(int(base_size * scale_factor), max_size), min_size)

    # Crear fuente
    font = QFont("Segoe UI")
    font.setWeight(QFont.Bold)
    font.setPointSize(scaled_size)

    return font


class DraggableHelper(QObject):
    position = Signal(QPoint)

    def __init__(self, frame):
        super().__init__(frame)
        self.frame = frame
        self.mouse_offset = None
        frame.installEventFilter(self)

    def eventFilter(self, obj, event):
        if obj is self.frame:
            if (
                event.type() == QEvent.MouseButtonPress
                and event.button() == Qt.LeftButton
            ):
                self.mouse_offset = (
                    event.globalPosition().toPoint() - self.frame.window().pos()
                )
                return True

            elif event.type() == QEvent.MouseMove and event.buttons() & Qt.LeftButton:
                if self.mouse_offset:
                    self.position.emit(
                        event.globalPosition().toPoint() - self.mouse_offset
                    )
                return True

            elif event.type() == QEvent.MouseButtonRelease:
                self.mouse_offset = None
                return True

        return super().eventFilter(obj, event)
