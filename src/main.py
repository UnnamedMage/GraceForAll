"""Archivo de arranque del programa"""

from src.common import PlatformPaths
from src.ui.app import App

PROJECT = "GraceForAll"

if __name__ == "__main__":
    instace = PlatformPaths(PROJECT)
    graceforall = App(PROJECT)
