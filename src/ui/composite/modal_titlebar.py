from ...Qtive.Component import Frame, ToolButton, Label
from ...Qtive.Props import (
    id,
    aspect_ratio,
    height,
    orientation,
    image,
    text,
    font_size,
    on_click,
    attributes,
)
from PySide6.QtCore import Signal
from typing import Callable


def ModalTitleBar(title: str | Signal, close_func: Callable, fontsize=6):
    return Frame(
        id("bar"),
        height("2.8sh"),
        orientation("row"),
        Frame(height("100%"), aspect_ratio("2-1")),
        Label(
            id("bar"),
            text(title),
            font_size(fontsize),
            attributes({"text_align": "center"}),
        ),
        ToolButton(
            image("close.svg"),
            height("100%"),
            aspect_ratio("2-1"),
            on_click(close_func),
        ),
    )
