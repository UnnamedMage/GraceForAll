import sys
import ctypes
import os

os.environ["QT_LOGGING_RULES"] = "*.debug=false;qt.qpa.*=false;qt.multimedia.*=false"
os.environ["QT_ENABLE_HARDWARE_ACCELERATION"] = "0"
os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "0"
os.environ["QT_SCALE_FACTOR"] = "1"
from abc import ABC, abstractmethod
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QSharedMemory, QEvent, QObject
from ..Style.theme_generator import set_app


class StyleWatcher(QObject):
    def eventFilter(self, obj, event):
        if event.type() == QEvent.StyleChange:
            if hasattr(obj, "apply_style") and obj.isVisible():
                obj.apply_style()
        return super().eventFilter(obj, event)


class BaseApp(ABC):
    def __init__(self, identify: str = "default_app"):
        self._disable_dpi_scaling()
        self._application = QApplication(sys.argv)
        watcher = StyleWatcher()
        self._application.installEventFilter(watcher)
        set_app(self._application)
        self._create_memory_block(identify)
        self._pre_init()
        self._build_app()
        self._start()

    def _disable_dpi_scaling(self):
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except ImportError:
            pass
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(0)
        except ImportError:
            pass

    def _create_memory_block(self, identify):
        shared_memory = QSharedMemory(identify)
        if shared_memory.attach():
            sys.exit(0)
        if not shared_memory.create(1):
            sys.exit(1)

    def _start(self):
        self._start_app()
        """sys.excepthook = error_manager"""
        sys.exit(self._application.exec())

    @abstractmethod
    def _pre_init(self):
        pass

    @abstractmethod
    def _build_app(self):
        pass

    @abstractmethod
    def _start_app(self):
        pass
