from PySide6.QtWidgets import QMainWindow, QSizePolicy, QWidget
from PySide6.QtCore import Qt, QPoint, QCoreApplication, QTimer, Signal
from PySide6.QtGui import QGuiApplication
from .interfaces import Component, Floating, Static
from ..Props.visual import Height, Width, AspectRatio, Orientation, Margins, Spacing
from .helpers import separate_size, Context
from .frame import Frame


class Cover(QWidget):
    def __init__(self, parent):
        super().__init__(parent=parent)
        self.setWindowFlags(Qt.Tool | Qt.FramelessWindowHint)
        self.setObjectName("cover")
        self.setStyleSheet("QWidget#cover { background-color: grey; }")
        self.setWindowOpacity(0.2)
        self.hide()
        self._parent = parent

    def set_size(self):
        self.setGeometry(self._parent.geometry())


class Window(QMainWindow, Component):
    on_close = Signal()

    def __init__(self, *args):
        self.base_args = []
        self.base_things = []
        self._avalible_geometry = None
        self._contract_size = None
        self._fixed_mode = False
        self._is_full = True
        self.central = None
        QMainWindow.__init__(self)
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
        self.cover = Cover(self)

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

        self.on_screen_changed()

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
        self.central.setParent(self)
        self.central.set_context(self.context)
        self.central.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.setCentralWidget(self.central)

    def calculate_size(self):
        screen = QGuiApplication.primaryScreen()
        self._avalible_geometry = screen.availableGeometry()
        avail = self._avalible_geometry.size()
        full = screen.geometry().size()

        width_prop = self.props.get("width")
        height_prop = self.props.get("height")
        aspect = self.props.get("aspectratio")

        # --- Caso 1: No hay tamaño especificado → ventana adaptable ---
        if not width_prop and not height_prop:
            self._fixed_mode = False

            self._contract_size = (int(avail.width() * 0.5), int(avail.height() * 0.5))
            return

        # --- Caso 2: Alguno definido → modo fijo ---
        self._fixed_mode = True

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

        self._contract_size = (new_w, new_h)

    def toggle_size(self):
        if self._fixed_mode:
            return  # tamaño fijo → ignorar

        if self._is_full:
            self.contract_window()
        else:
            self.expand_window()

    def expand_window(self):
        screen = self._avalible_geometry
        self.setGeometry(screen)
        self._is_full = True
        self.central.setGeometry(screen)
        self.cover.set_size()

    def contract_window(self):
        screen = self._avalible_geometry
        w, h = self._contract_size
        self.resize(w, h)
        self.central.resize(w, h)
        self.cover.set_size()
        x, y = (
            screen.x() + (screen.width() - w) // 2,
            screen.y() + (screen.height() - h) // 2,
        )
        self.move(x, y)
        self.cover.move(x, y)
        self._is_full = False

    def move_window(self, new_pos: QPoint):
        if not self._is_full:
            screen_rect = self._avalible_geometry
            ventana_size = self.size()
            new_x = max(
                screen_rect.left(),
                min(new_pos.x(), screen_rect.right() - ventana_size.width()),
            )
            new_y = max(
                screen_rect.top(),
                min(new_pos.y(), screen_rect.bottom() - ventana_size.height()),
            )
            self.move(new_x, new_y)
            self.cover.move(new_x, new_y)

    def on_screen_changed(self):
        self.calculate_size()
        if self._fixed_mode:
            self.contract_window()
        elif self._is_full:
            self.expand_window()
        else:
            self.contract_window()

    def show(self):
        super().show()

    def closeEvent(self, event):
        self.on_close.emit()
        event.accept()
