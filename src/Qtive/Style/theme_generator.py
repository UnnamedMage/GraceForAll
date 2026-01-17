from jinja2 import Environment
from pathlib import Path
from .helpers import filter_opacity, filter_density, filter_darker, filter_lighter
from .themes import THEMES
from PySide6.QtWidgets import QApplication

CURRENT_DIR = Path(__file__).parent
TEMPLATE_PATH = CURRENT_DIR / "template.qss.j2"


class ThemeGenerator:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, "_initialized"):
            self.env = Environment()
            self.env.filters["opacity"] = filter_opacity
            self.env.filters["density"] = filter_density
            self.env.filters["lighter"] = filter_lighter
            self.env.filters["darker"] = filter_darker
            self.raw = ""
            self.themes = THEMES.copy()
            self.theme = None
            self.app = None
            self._initialized = True
            self._load_raw_qss()

    def _load_raw_qss(self):
        if not TEMPLATE_PATH.exists():
            return

        with open(TEMPLATE_PATH, "r") as f:
            self.raw = f.read()

    def set_app(self, app):
        self.app = app
        if self.theme:
            self._generate_qss()

    def set_theme(self, theme):
        if theme not in self.themes:
            return
        self.theme = theme
        self._generate_qss()

    def _generate_qss(self):
        if not self.raw or not self.app:
            return
        template = self.env.from_string(self.raw)
        theme = self.themes[self.theme]
        qss = template.render(**theme)

        self.app.setStyle("Fusion")
        self.app.setStyleSheet(qss)

    def add_raw_rule(self, rule):
        self.raw += rule


def set_app(app: QApplication):
    instance = ThemeGenerator()
    instance.set_app(app)


def add_rule(rule: str):
    instance = ThemeGenerator()
    instance.add_raw_rule(rule)


def set_theme(theme: str):
    instance = ThemeGenerator()
    instance.set_theme(theme)
