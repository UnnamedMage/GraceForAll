from .....Qtive.Component import Spacer, Frame, ToolButton, Label
from .....Qtive.Props import (
    orientation,
    height,
    width,
    alignment,
    aspect_ratio,
    image,
    font_size,
    text,
    on_click,
    on_update,
    id,
    attributes,
    spacing,
    margins,
)
from functools import partial
from ..viewmodel import MainViewModel

TitleBarButton = partial(
    ToolButton,
    alignment("right"),
    height("100%"),
    aspect_ratio("2-1"),
)


def TitleBar():
    vm = MainViewModel()
    return Frame(
        orientation("row"),
        height("6vh"),
        id("bar"),
        on_update(vm.window.move.emit),
        spacing(10),
        Frame(
            orientation("row"),
            width("14%"),
            margins(10, 2, 2, 2),
            spacing(2),
            Label(
                height("100%"),
                aspect_ratio("1-1"),
                image("GraceForAllnegative.svg"),
                id("bar"),
            ),
            Label(
                text("GraceForAll"),
                font_size(5),
                id("bar"),
                attributes({"text_align": "center"}),
            ),
        ),
        Frame(
            Frame(
                orientation("row"),
                height("2.8sh"),
                Spacer("horizontal"),
                TitleBarButton(
                    image("minimize.svg"), on_click(vm.window.minimize.emit)
                ),
                TitleBarButton(image("maximize.svg"), on_click(vm.window.restore.emit)),
                TitleBarButton(image("close.svg"), on_click(vm.window.close.emit)),
            ),
            Spacer("vertical"),
        ),
    )
