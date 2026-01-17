from PySide6.QtCore import Qt
from typing import Literal


class Width:
    def __init__(self, value: str):
        self.key = "width"
        self.value = value


def width(value: str) -> Width:
    """
    '%' for parent proportion or avalible geometry proportion,\n
    'vh' for view heigh proportion,\n
    'vw' for view width proportion\n
    'sh' for screen heigh proportion,\n
    'sw' for screen width proportion\n
    "px" for absolute pixels\n
        value: N%, Nvh, Nvw (e.g: 50%, 30vh, 10vw, 300px)
    """
    return Width(value)


class Height:
    def __init__(self, value: str):
        self.key = "height"
        self.value = value


def height(value: str) -> Height:
    """
    '%' for parent proportion or avalible geometry proportion,\n
    'vh' for view heigh proportion,\n
    'vw' for view width proportion\n
    'sh' for screen heigh proportion,\n
    'sw' for screen width proportion\n
    "px" for absolute pixels\n
        value: N%, Nvh, Nvw (e.g: 50%, 30vh, 10vw, 300px)
    """
    return Height(value)


class Orientation:
    def __init__(self, value: Literal["row", "column"]):
        self.key = "orientation"
        self.value = value


def orientation(value: Literal["row", "column"]) -> Orientation:
    if value not in ("row", "column"):
        value = "row"
    return Orientation(value)


class AspectRatio:
    def __init__(self, value: str):
        self.key = "aspectratio"
        self.value = value


def aspect_ratio(value: str):
    """
    Width proportion - Height proportion \n
    value: W-H (e.g: "16-9")

    """
    return AspectRatio(value)


class Margins:
    def __init__(self, value: list):
        self.key = "margins"
        self.value = value


def margins(left: int = 0, top: int = 0, right: int = 0, bottom: int = 0):
    return Margins([left, top, right, bottom])


class Spacing:
    def __init__(self, value: int):
        self.key = "spacing"
        self.value = value


def spacing(value: int = 0):
    return Spacing(value)


ALIGNMAP = {
    "top": Qt.AlignmentFlag.AlignTop,
    "bottom": Qt.AlignmentFlag.AlignBottom,
    "left": Qt.AlignmentFlag.AlignLeft,
    "right": Qt.AlignmentFlag.AlignRight,
    "vcenter": Qt.AlignmentFlag.AlignVCenter,
    "hcenter": Qt.AlignmentFlag.AlignHCenter,
    "center": Qt.AlignmentFlag.AlignCenter,
}


class Alignment:
    def __init__(self, value: Qt.AlignmentFlag):
        self.key = "alignment"
        self.value = value


def alignment(
    value: Literal["top", "bottom", "left", "right", "vcenter", "hcenter", "center"],
    value2: Literal["top", "bottom", "left", "right", "vcenter", "hcenter"] = None,
):
    final = (
        ALIGNMAP[value] | ALIGNMAP[value2]
        if value2 and value != value2
        else ALIGNMAP[value]
    )
    return Alignment(final)


class FontSize:
    def __init__(self, value: float):
        self.key = "fontsize"
        self.value = value


def font_size(value: float):
    return FontSize(value)


class Id:
    def __init__(self, value: str):
        self.key = "id"
        self.value = value


def id(value: str):
    return Id(value)
