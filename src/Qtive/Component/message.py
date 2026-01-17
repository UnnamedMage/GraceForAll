from PySide6.QtWidgets import (
    QDialog,
    QScrollArea,
    QTextBrowser,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QToolButton,
    QFrame,
)
from PySide6.QtCore import Qt, QCoreApplication, QTimer, Signal, QSize, QEvent
from PySide6.QtGui import QGuiApplication, QIcon
from .interfaces import Component, Floating, Interactive
from ..Props.content import Attributes, Deploy
from typing import Literal
from .helpers import create_font, image_or_svg_to_pixmap


class Message(QDialog, Component, Floating, Interactive):
    def __init__(self, *args):
        self.main_geometry = None
        self.new_height, self.new_width = None, None
        QDialog.__init__(self)
        Component.__init__(self)
        Interactive.__init__(self)
        Floating.__init__(self)
        self.assign_props(args)

        self._mode = "notification"

        # Widgets principales
        self.header = None
        self.close_btn = None
        self.title_lbl = None
        self.text_browser = None
        self.button_container = None
        self.btn_yes = None
        self.btn_no = None
        self.btn_ok = None

        self.build_ui()

        self.setWindowFlags(
            Qt.Window
            | Qt.CustomizeWindowHint
            | Qt.WindowTitleHint
            | Qt.FramelessWindowHint
        )
        self.setModal(True)

        for screen in QGuiApplication.screens():
            screen.geometryChanged.connect(
                lambda: QTimer.singleShot(500, self.set_size)
            )

        QCoreApplication.instance().screenAdded.connect(
            lambda: QTimer.singleShot(500, self.set_size)
        )
        QCoreApplication.instance().screenRemoved.connect(
            lambda: QTimer.singleShot(500, self.set_size)
        )
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

    def build_ui(self):
        self.base = QFrame()
        self.base.setObjectName("popup")
        main_layout = QVBoxLayout(self.base)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.base)
        self.setLayout(layout)

        # ---------------- HEADER ----------------
        self.header = QFrame()

        layout = QHBoxLayout(self.header)
        layout.setContentsMargins(5, 0, 5, 0)
        layout.setSpacing(0)

        self.title_lbl = QLabel("Título")

        layout.addWidget(self.title_lbl, 0, Qt.AlignLeft)

        self.close_btn = QToolButton()
        self.close_btn.setObjectName("cancel")
        self.close_btn.clicked.connect(lambda: self.done(3))

        layout.addStretch()
        layout.addWidget(self.close_btn)

        main_layout.addWidget(self.header)

        # ---------------- MESSAGE AREA ----------------
        self.body = QFrame()
        body_layout = QVBoxLayout(self.body)
        body_layout.setContentsMargins(0, 5, 5, 5)
        body_layout.setSpacing(5)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        message_container = QFrame()
        message_layout = QVBoxLayout(message_container)
        message_layout.setContentsMargins(0, 0, 0, 0)

        self.text_browser = QTextBrowser()
        self.text_browser.setOpenExternalLinks(True)
        message_layout.addWidget(self.text_browser)

        scroll.setWidget(message_container)
        body_layout.addWidget(scroll)

        # ---------------- BUTTONS ----------------
        self.button_container = QFrame()
        button_container_layout = QHBoxLayout(self.button_container)
        button_container_layout.addStretch()
        button_container_layout.setContentsMargins(0, 0, 0, 0)
        button_container_layout.setSpacing(5)

        # Confirmation mode buttons
        self.btn_yes = QToolButton()
        self.btn_yes.setText("Sí")
        self.btn_no = QToolButton()
        self.btn_no.setText("No")
        self.btn_no.setObjectName("cancel")
        self.btn_yes.clicked.connect(lambda: self.done(1))
        self.btn_no.clicked.connect(lambda: self.done(0))

        # Notification mode button
        self.btn_ok = QToolButton()
        self.btn_ok.setText("OK")
        self.btn_ok.clicked.connect(lambda: self.done(3))

        body_layout.addWidget(self.button_container)

        main_layout.addWidget(self.body)

        self.set_mode("notification")  # default

    def assign_props(self, args):
        for arg in args:
            if isinstance(
                arg,
                (Attributes, Deploy),
            ):
                self.props[arg.key] = arg.value
            elif isinstance(arg, Floating):
                arg.anchor = self
                self.floatings.append(arg)

        if deploy := self.props.get("deploy", None):
            if isinstance(deploy, Signal):
                deploy.connect(self.deploy)

    def deploy(self, data: dict):
        title = data.get("title", "Aviso")
        message = data.get("message", "")
        callback = data.get("callback")
        mode = data.get("mode", "notification")

        self.title_lbl.setText(title)
        self.text_browser.setText(message)
        self.set_mode(mode)

        self.move_to()

        value = self.exec_()

        if callback and value != 3:
            callback(bool(value))

    def set_mode(self, mode: Literal["confirmation", "notification"]):
        self._mode = mode
        button_container_layout = self.button_container.layout()
        # limpiar contenedor
        for i in reversed(range(button_container_layout.count())):
            w = button_container_layout.itemAt(i).widget()
            if w:
                w.setParent(None)

        button_container_layout.addStretch()

        if mode == "confirmation":
            button_container_layout.addWidget(self.btn_no)
            button_container_layout.addWidget(self.btn_yes)
        else:
            button_container_layout.addWidget(self.btn_ok)

    def calculate_size(self):
        window = self.context.get("window")
        screen = window.screen()

        self.main_geometry = screen.availableGeometry()
        main_width = self.main_geometry.width()
        main_height = self.main_geometry.height()

        self.new_width = int(main_width * 0.2)
        self.new_height = int(main_height * 0.2)

    def resize_modal(self):
        window = self.context.get("window")
        self.setFixedSize(self.new_width, self.new_height)
        self.base.setFixedSize(self.new_width, self.new_height)
        screen_size = window.screen().geometry().size()
        standard_height = int(screen_size.height() * 0.028)
        self.header.setFixedSize(self.new_width, standard_height + 2)
        self.close_btn.setFixedSize(standard_height * 2, standard_height)
        self.btn_no.setFixedSize(int(self.new_width * 0.25), standard_height)
        self.btn_ok.setFixedSize(int(self.new_width * 0.25), standard_height)
        self.btn_yes.setFixedSize(int(self.new_width * 0.25), standard_height)
        self.title_lbl.setFixedHeight(standard_height)
        self.move_to()

    def move_to(self):
        window = self.context.get("window")
        parent_geometry = window.geometry()
        new_x = parent_geometry.x() + (parent_geometry.width() - self.width()) // 2
        new_y = parent_geometry.y() + (parent_geometry.height() - self.height()) // 2

        self.move(new_x, new_y)

    def refresh_icon(self):
        if self.height() > 10 and self.width() > 10:
            pixmap = image_or_svg_to_pixmap(self.close_btn, "close.svg")
            if pixmap:
                self.close_btn.setIcon(QIcon(pixmap))
                self.close_btn.setIconSize(
                    QSize(self.close_btn.width() * 0.8, self.close_btn.height() * 0.8)
                )

    def set_size(self):
        self.calculate_size()
        self.resize_modal()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            # Mandar un código personalizado
            self.done(3)  # <-- cualquier valor que quieras
            return

        super().keyPressEvent(event)

    def apply_style(self):
        font = create_font(self)
        font.setPointSize(int(self.height() / 14))
        self.title_lbl.setFont(font)
        self.text_browser.setFont(font)
        self.btn_no.setFont(font)
        self.btn_ok.setFont(font)
        self.btn_yes.setFont(font)
        self.refresh_icon()

    def propagate_after_resize(self):
        self.apply_style()
        self.resize_floatings()
