from .....Qtive.Component import (
    Spacer,
    Frame,
    ToolButton,
    Label,
    Popup,
    ComboBox,
)
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
    index,
    items,
    attributes,
    deploy,
    id,
    spacing,
    margins,
)
from ....utils.constants import FAMILIES, IN_ANIMATIONS, OUT_ANIMATIONS
from functools import partial
from ....components import MediaSelector
from ..viewmodel import MainViewModel

ToolBarButton = partial(
    ToolButton,
    height("100%"),
    aspect_ratio("1-1"),
)

BoxLabel = partial(
    Label,
    height("35%"),
    font_size(3),
    attributes({"text_align": "center"}),
)

BoxFrame = partial(
    Frame,
    id("test"),
    height("50%"),
    orientation("row"),
    alignment("center"),
)


def SlideStyleMenu():
    vm = MainViewModel().ssc
    return Popup(
        height("9.84vh"),
        width("70vw"),
        orientation("row"),
        margins(5, 5, 5, 5),
        deploy(vm.view.menu),
        attributes({"direction": "right"}),
        orientation("row"),
        Frame(
            id("box_song"),
            height("100%"),
            width("35%"),
            BoxFrame(
                Spacer(),
                ComboBox(
                    height("100%"),
                    aspect_ratio("5-1"),
                    font_size(3.6),
                    on_click(lambda i: vm.set_attribute("family", FAMILIES[i])),
                    index(vm.font.family_index),
                    items(FAMILIES),
                ),
                Spacer(),
                Frame(
                    height("100%"),
                    aspect_ratio("2-1"),
                    orientation("row"),
                    ToolBarButton(
                        image("black.svg"),
                        on_click(lambda: vm.set_attribute("color", "black")),
                        attributes(vm.color.black),
                    ),
                    ToolBarButton(
                        image("white.svg"),
                        on_click(lambda: vm.set_attribute("color", "white")),
                        attributes(vm.color.white),
                    ),
                ),
                Spacer(),
                Frame(
                    height("100%"),
                    aspect_ratio("2-1"),
                    orientation("row"),
                    ToolBarButton(
                        text("N"),
                        attributes(vm.style.bold),
                        font_size(3.6),
                        on_click(lambda: vm.set_attribute("bold", None)),
                    ),
                    ToolBarButton(
                        text("C"),
                        attributes(vm.style.italic),
                        font_size(3.6),
                        on_click(lambda: vm.set_attribute("italic", None)),
                    ),
                ),
                Spacer(),
            ),
            BoxLabel(
                text("Fuente"),
            ),
        ),
        Frame(
            id("box_song"),
            height("100%"),
            width("21%"),
            BoxFrame(
                Spacer(),
                Frame(
                    height("100%"),
                    aspect_ratio("3-1"),
                    orientation("row"),
                    ToolBarButton(
                        image("left.svg"),
                        on_click(lambda: vm.set_attribute("h_align", "left")),
                        attributes(vm.h_align.left),
                    ),
                    ToolBarButton(
                        image("center.svg"),
                        on_click(lambda: vm.set_attribute("h_align", "hcenter")),
                        attributes(vm.h_align.hcenter),
                    ),
                    ToolBarButton(
                        image("right.svg"),
                        on_click(lambda: vm.set_attribute("h_align", "right")),
                        attributes(vm.h_align.right),
                    ),
                ),
                Spacer(),
                Frame(
                    height("100%"),
                    aspect_ratio("3-1"),
                    orientation("row"),
                    ToolBarButton(
                        image("bottom.svg"),
                        on_click(lambda: vm.set_attribute("v_align", "bottom")),
                        attributes(vm.v_align.bottom),
                    ),
                    ToolBarButton(
                        image("vcenter.svg"),
                        on_click(lambda: vm.set_attribute("v_align", "vcenter")),
                        attributes(vm.v_align.vcenter),
                    ),
                    ToolBarButton(
                        image("top.svg"),
                        on_click(lambda: vm.set_attribute("v_align", "top")),
                        attributes(vm.v_align.top),
                    ),
                ),
                Spacer(),
            ),
            BoxLabel(
                text("Alineación"),
            ),
        ),
        Frame(
            id("box_song"),
            height("100%"),
            width("28%"),
            BoxFrame(
                Spacer(),
                ComboBox(
                    height("100%"),
                    aspect_ratio("4-1"),
                    font_size(3.6),
                    on_click(
                        lambda i: vm.set_attribute("in_animation", IN_ANIMATIONS[i])
                    ),
                    index(vm.animation.in_index),
                    items(["Desvanecer", "Deslizar", "Zoom", "Rebotar"]),
                ),
                Spacer(),
                ComboBox(
                    height("100%"),
                    aspect_ratio("4-1"),
                    font_size(3.6),
                    on_click(
                        lambda i: vm.set_attribute("out_animation", OUT_ANIMATIONS[i])
                    ),
                    index(vm.animation.out_index),
                    items(["Desvanecer", "Deslizar", "Zoom"]),
                ),
                Spacer(),
            ),
            BoxLabel(
                text("Animación"),
            ),
        ),
        Frame(
            ToolButton(
                height("70%"),
                width("90%"),
                alignment("center"),
                on_click(vm.bg.menu.emit),
                text("Fondo"),
                font_size(3.6),
                Popup(
                    height("500%"),
                    width("250%"),
                    spacing(5),
                    margins(5, 5, 5, 5),
                    deploy(vm.bg.menu),
                    attributes({"direction": "left", "margin": 10}),
                    MediaSelector(
                        items(vm.bg.items),
                        font_size(3),
                        on_click(lambda s: vm.set_attribute("bg_path", s)),
                    ),
                    ToolButton(
                        height("15%"),
                        font_size(3.6),
                        text("Agregar Fondo"),
                        on_click(vm.add_bg),
                    ),
                ),
            ),
        ),
    )
