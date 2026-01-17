from PySide6.QtCore import Signal


class Text:
    def __init__(self, value: str | Signal):
        self.key = "text"
        self.value = value


def text(value: str | Signal):
    return Text(value)


class Image:
    def __init__(self, value: str | Signal):
        self.key = "image"
        self.value = value


def image(value: str | Signal):
    """
    Only the file name is needed, the program will search for it in resource
    """
    return Image(value)


class PlaceHolder:
    def __init__(self, value: str):
        self.key = "placeholder"
        self.value = value


def placeholder(value: str):
    return PlaceHolder(value)


class Attributes:
    def __init__(self, value: dict | Signal):
        self.key = "attributes"
        self.value = value


def attributes(value: dict | Signal):
    return Attributes(value)


class Index:
    def __init__(self, value: int | Signal):
        self.key = "index"
        self.value = value


def index(value: int | Signal):
    return Index(value)


class Items:
    def __init__(self, value: list | Signal):
        self.key = "items"
        self.value = value


def items(value: list | Signal):
    return Items(value)


class Filter:
    def __init__(self, value: str | Signal):
        self.key = "filter"
        self.value = value


def filter(value: str | Signal):
    return Filter(value)


class Source:
    def __init__(self, value: str | Signal):
        self.key = "source"
        self.value = value


def source(value: str | Signal):
    return Source(value)


class Deploy:
    def __init__(self, value: Signal):
        self.key = "deploy"
        self.value = value


def deploy(value: Signal):
    return Deploy(value)
