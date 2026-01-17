from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QMainWindow,
    QSizePolicy,
)
from PySide6.QtCore import Qt, QCoreApplication, QTimer
from PySide6.QtGui import QGuiApplication
from .interfaces import Component, Static, Floating
from ..Props.visual import Height, Width, AspectRatio, Orientation, Margins, Spacing
from .helpers import separate_size, Context
from .frame import Frame


class Dialog(QDialog, Component):
    def __init__(self, *args):
        self.base_args = []
        self.base_things = []
        self._parent = None
        self.main_geometry = None
        self.new_height, self.new_width = None, None
        QDialog.__init__(self)
        Component.__init__(self)
        self.context = Context()
        self.context.set("window", self)
        self.assign_props(args)

        self.setWindowFlags(
            Qt.Window
            | Qt.CustomizeWindowHint
            | Qt.WindowTitleHint
            | Qt.FramelessWindowHint
        )
        self.setModal(True)
        self.setAttribute(Qt.WA_TranslucentBackground)

        for screen in QGuiApplication.screens():
            screen.geometryChanged.connect(
                lambda: QTimer.singleShot(500, self.on_screen_changed)
            )

        QCoreApplication.instance().screenAdded.connect(
            lambda: QTimer.singleShot(500, self.on_screen_changed)
        )
        QCoreApplication.instance().screenRemoved.connect(
            lambda: QTimer.singleShot(500, self.on_screen_changed)
        )

    def assign_props(self, args):
        for arg in args:
            if isinstance(
                arg,
                (Height, Width, AspectRatio),
            ):
                self.props[arg.key] = arg.value
            elif isinstance(arg, (Orientation, Margins, Spacing)):
                self.base_args.append(arg)
            elif isinstance(arg, (Static, Floating)):
                self.base_things.append(arg)

        self.central = Frame(*self.base_args, *self.base_things)
        self.central.setObjectName("dialog")
        self.central.setParent(self)
        self.central.set_context(self.context)
        self.central.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.central, 0, Qt.AlignLeft | Qt.AlignTop)
        self.setLayout(layout)

    def setParent(self, parent: QMainWindow):
        self._parent = parent

    def calculate_size(self):
        screen = (
            self._parent.screen() if self._parent else QGuiApplication.primaryScreen()
        )

        self.main_geometry = screen.availableGeometry()
        avail = self.main_geometry.size()
        full = screen.geometry().size()
        main_width = self.main_geometry.width()
        main_height = self.main_geometry.height()

        width_prop = self.props.get("width")
        height_prop = self.props.get("height")
        aspect = self.props.get("aspectratio")

        if not width_prop and not height_prop:
            self.new_width = int(main_width * 0.5)
            self.new_height = int(main_height * 0.5)
            return

        def calc(prop, base):
            if not prop:
                return None
            val, rule = separate_size(prop)
            if rule == "%":
                return int(base * min(val, 100) / 100)
            elif rule in ("vw", "vh"):
                return int(
                    avail.width() * val / 100
                    if "w" in rule
                    else avail.height() * val / 100
                )
            elif rule in ("sw", "sh"):
                return int(
                    full.width() * val / 100
                    if "w" in rule
                    else full.height() * val / 100
                )
            else:
                return int(val)

        new_w = calc(width_prop, avail.width())
        new_h = calc(height_prop, avail.height())

        # --- Ajuste por aspect ratio ---
        if aspect and (new_w or new_h):
            try:
                w_ratio, h_ratio = map(float, aspect.split("-"))
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

        self.new_width, self.new_height = (new_w, new_h)

    def resize_modal(self):
        main_x = self.main_geometry.x()
        main_y = self.main_geometry.y()

        self.setFixedSize(self.new_width, self.new_height)
        self.central.setFixedSize(self.new_width, self.new_height)

        if self._parent:
            parent_geometry = self._parent.geometry()
            new_x = parent_geometry.x() + (parent_geometry.width() - self.width()) // 2
            new_y = (
                parent_geometry.y() + (parent_geometry.height() - self.height()) // 2
            )
        else:
            main_width = self.main_geometry.width()
            main_height = self.main_geometry.height()
            new_x = main_x + (main_width - self.width()) // 2
            new_y = main_y + (main_height - self.height()) // 2

        self.move(new_x, new_y)

    def on_screen_changed(self):
        self.calculate_size()
        self.resize_modal()

    def show(self):
        if self._parent:
            self._parent.cover.show()
        self.on_screen_changed()
        super().show()

    def exec_(self):
        if self._parent:
            self._parent.cover.show()
        self.on_screen_changed()
        super().exec_()

    def closeEvent(self, event):
        event.accept()
        if self._parent:
            self._parent.cover.hide()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            # Ignorar ESC
            return
        super().keyPressEvent(event)
