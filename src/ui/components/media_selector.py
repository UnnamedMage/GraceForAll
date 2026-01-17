from PySide6.QtWidgets import QListWidget, QAbstractItemView, QListWidgetItem
from PySide6.QtCore import Qt, Signal, QRect, QSize, QEvent, QTimer
from PySide6.QtGui import QPixmap, QImage, QPainter, QIcon
from PySide6.QtSvg import QSvgRenderer
import os
import cv2
from ...Qtive.Component.interfaces import Interactive, Component, Static, Floating
from ...Qtive.Component.helpers import create_font
from ...Qtive.Props.visual import Width, Height, AspectRatio, Alignment, FontSize
from ...Qtive.Props.content import Attributes, Items
from ...Qtive.Props.events import OnClick, OnDoubleClick


def create_tumb(path, size):
    if path.lower().endswith((".png", ".jpg", ".jpeg", ".bmp", ".webp")):
        pixmap = QPixmap(path)
    elif path.lower().endswith((".mp4", ".avi", ".mkv", ".mov", ".wmv", ".gif")):
        try:
            cap = cv2.VideoCapture(path)
            ret, frame = cap.read()
            if ret:
                # Convertir frame de OpenCV a QPixmap
                height, width, channel = frame.shape
                bytes_per_line = 3 * width
                q_img = QImage(
                    frame.data, width, height, bytes_per_line, QImage.Format_RGB888
                ).rgbSwapped()
                pixmap = QPixmap.fromImage(q_img)
            cap.release()
        except Exception:
            icon_video_svg_path = "src/assets/video.svg"
            pixmap = QPixmap(size, size)
            pixmap.fill(Qt.black)
            painter = QPainter(pixmap)
            svg_renderer = QSvgRenderer(icon_video_svg_path)
            svg_renderer.render(painter, QRect(30, 30, 40, 40))
            painter.end()
    elif path == "default":
        pixmap = QPixmap(size, int(size * 0.56))
        pixmap.fill(Qt.black)
    else:
        return None

    pixmap = pixmap.scaled(size, size, Qt.KeepAspectRatio, Qt.SmoothTransformation)

    final_pixmap = QPixmap(size, size)
    final_pixmap.fill(Qt.transparent)

    painter = QPainter(final_pixmap)
    x = (size - pixmap.width()) // 2
    y = (size - pixmap.height()) // 2
    painter.drawPixmap(x, y, pixmap)
    painter.end()

    icon = QIcon(final_pixmap)
    return icon


class MediaSelector(QListWidget, Component, Static, Interactive):
    def __init__(self, *args):
        QListWidget.__init__(self)
        Component.__init__(self)
        Static.__init__(self)
        Interactive.__init__(self)
        self._paths = []
        self.default = None

        self._resize_timer = QTimer()
        self._resize_timer.setSingleShot(True)
        self._resize_timer.timeout.connect(self.refresh_list)

        self.setViewMode(QListWidget.IconMode)
        self.setDragEnabled(False)
        self.setAcceptDrops(False)
        self.setDragDropMode(QAbstractItemView.NoDragDrop)
        self.setDefaultDropAction(Qt.IgnoreAction)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)

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
                    Items,
                    OnClick,
                    OnDoubleClick,
                ),
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

        if onclick := self.props.get("onclick"):
            self.itemClicked.connect(
                lambda i: onclick(i.data(Qt.UserRole).replace("\\", "/"))
            )

        if ondclick := self.props.get("ondoubleclick"):
            self.itemDoubleClicked.connect(
                lambda i: ondclick(i.data(Qt.UserRole).replace("\\", "/"))
            )

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
            case "default":
                self.default = value

    def add_items(self, paths: list):
        self._paths = paths
        self.refresh_list()

    def refresh_list(self):
        if not self.context:
            return

        self.clear()

        icon_size = int((self.width() - 14) / 3.332)
        self.setIconSize(QSize(icon_size, icon_size))

        if self.default:
            icon = create_tumb("default", icon_size)
            item = QListWidgetItem(icon, self.default)
            item.setData(Qt.UserRole, "default")
            self.addItem(item)

        for path in self._paths:
            if not os.path.exists(path):
                continue
            name = os.path.basename(path)

            if len(name) > 12:
                name = name[:12] + "..."

            if icon := create_tumb(path, icon_size):
                item = QListWidgetItem(icon, name)
                item.setData(Qt.UserRole, path)
                self.addItem(item)

    def set_size(self, size):
        self.setFixedSize(size)

    def apply_style(self):
        self.setFont(create_font(self, self.font_size))

    def propagate_after_resize(self):
        self.apply_style()
        self._resize_timer.start(200)
        self.resize_floatings()
