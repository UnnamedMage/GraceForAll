from .....Qtive.Component import ToolButton, Frame, ComboBox, Popup, Label, Spacer
from .....Qtive.Props import (
    height,
    width,
    orientation,
    aspect_ratio,
    text,
    font_size,
    attributes,
    items,
    image,
    index,
    on_click,
    deploy,
    id,
    spacing,
    margins,
    alignment,
)
from .....Qtive.Style import add_rule
from ....components import MediaSelector
from ....utils.constants import FAMILIES, FACTORS
from functools import partial
from ..viewmodel import SongEditorVM

ToolBarButton = partial(
    ToolButton,
    height("100%"),
    aspect_ratio("1-1"),
)

BoxLabel = partial(
    Label,
    height("35%"),
    font_size(5),
    attributes({"text_align": "center"}),
)

BoxFrame = partial(
    Frame,
    height("65%"),
    orientation("row"),
    alignment("center"),
)

add_rule("""
    QFrame #box_song {
    background-color: transparent;
    border-color: {{secondaryColor}};
    border-width: 0 2px 0 0;
    border-style: solid;
    }
""")

add_rule("""
    QFrame #toolbar{
      background-color: {{secondaryDarkColor}};
      border-color: {{secondaryColor}};
      border-width: 1px;
      border-style: solid;
      border-radius: {{2 | density()}}px;  
    }
""")


def Toolbar():
    vm = SongEditorVM()
    return Frame(
        height("5.6sh"),
        orientation("row"),
        id("toolbar"),
        Frame(
            id("box_song"),
            height("100%"),
            width("35%"),
            BoxFrame(
                Spacer(),
                ComboBox(
                    height("2.8sh"),
                    aspect_ratio("4-1"),
                    font_size(5),
                    on_click(vm.set_font),
                    index(vm.font.family_index),
                    items(FAMILIES),
                ),
                Spacer(),
                ComboBox(
                    height("2.8sh"),
                    aspect_ratio("2-1"),
                    font_size(5),
                    index(vm.font.factor_index),
                    items([str(f) for f in FACTORS]),
                    on_click(vm.set_factor),
                ),
                Spacer(),
                Frame(
                    height("2.8sh"),
                    aspect_ratio("2-1"),
                    orientation("row"),
                    ToolBarButton(
                        image("black.svg"),
                        on_click(lambda: vm.set_color("black")),
                        attributes(vm.color.black),
                    ),
                    ToolBarButton(
                        image("white.svg"),
                        on_click(lambda: vm.set_color("white")),
                        attributes(vm.color.white),
                    ),
                ),
                Spacer(),
                Frame(
                    height("2.8sh"),
                    aspect_ratio("2-1"),
                    orientation("row"),
                    ToolBarButton(
                        text("N"),
                        attributes(vm.style.bold),
                        font_size(6),
                        on_click(vm.set_bold),
                    ),
                    ToolBarButton(
                        text("C"),
                        attributes(vm.style.italic),
                        font_size(6),
                        on_click(vm.set_italic),
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
                    height("2.8sh"),
                    aspect_ratio("3-1"),
                    orientation("row"),
                    ToolBarButton(
                        image("left.svg"),
                        on_click(lambda: vm.set_h_align("left")),
                        attributes(vm.h_align.left),
                    ),
                    ToolBarButton(
                        image("center.svg"),
                        on_click(lambda: vm.set_h_align("hcenter")),
                        attributes(vm.h_align.hcenter),
                    ),
                    ToolBarButton(
                        image("right.svg"),
                        on_click(lambda: vm.set_h_align("right")),
                        attributes(vm.h_align.right),
                    ),
                ),
                Spacer(),
                Frame(
                    height("2.8sh"),
                    aspect_ratio("3-1"),
                    orientation("row"),
                    ToolBarButton(
                        image("bottom.svg"),
                        on_click(lambda: vm.set_v_align("bottom")),
                        attributes(vm.v_align.bottom),
                    ),
                    ToolBarButton(
                        image("vcenter.svg"),
                        on_click(lambda: vm.set_v_align("vcenter")),
                        attributes(vm.v_align.vcenter),
                    ),
                    ToolBarButton(
                        image("top.svg"),
                        on_click(lambda: vm.set_v_align("top")),
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
                    height("2.8sh"),
                    aspect_ratio("4-1"),
                    font_size(5),
                    on_click(vm.set_in),
                    index(vm.animation.in_index),
                    items(["Desvanecer", "Deslizar", "Zoom", "Rebotar"]),
                ),
                Spacer(),
                ComboBox(
                    height("2.8sh"),
                    aspect_ratio("4-1"),
                    font_size(5),
                    on_click(vm.set_out),
                    index(vm.animation.out_index),
                    items(["Desvanecer", "Deslizar", "Zoom"]),
                ),
                Spacer(),
            ),
            BoxLabel(
                text("Animación"),
            ),
        ),
        ToolButton(
            height("80%"),
            width("15%"),
            alignment("center"),
            on_click(vm.bg.menu.emit),
            text("Fondo"),
            font_size(5),
            Popup(
                height("500%"),
                width("250%"),
                spacing(5),
                margins(5, 5, 5, 5),
                deploy(vm.bg.menu),
                attributes({"direction": "left", "margin": 10}),
                MediaSelector(
                    items(vm.bg.items),
                    font_size(4),
                    attributes({"default": "Pred..."}),
                    on_click(vm.set_background),
                ),
                ToolButton(
                    height("15%"),
                    font_size(5),
                    text("Agregar Fondo"),
                    on_click(vm.add_new_bg),
                ),
            ),
        ),
    )
