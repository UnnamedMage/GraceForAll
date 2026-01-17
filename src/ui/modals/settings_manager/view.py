from ....Qtive.Component import (
    Dialog,
    Frame,
    ComboBox,
    Spacer,
    ToolButton,
    Message,
    Label,
)
from ....Qtive.Props import (
    height,
    orientation,
    width,
    font_size,
    text,
    deploy,
    margins,
    spacing,
    id,
    attributes,
    items,
    on_click,
    index,
    image,
)
from ...composite import ModalTitleBar
from .viewmodel import SettingsManagerVM
from functools import partial

SectionButton = partial(ToolButton, height("5%"), id("sidebar"), font_size(4))


def SettingsManager():
    vm = SettingsManagerVM()
    return Dialog(
        height("60%"),
        width("35%"),
        ModalTitleBar("Configuracion", vm.window.close.emit, 5),
        Message(deploy(vm.view.message)),
        Frame(
            orientation("row"),
            Frame(
                width("25%"),
                spacing(5),
                margins(5, 5, 0, 5),
                Frame(height("10%")),
                SectionButton(
                    image("palette.svg"),
                    text("Apariencia"),
                    attributes(vm.btns_attrs.sect0),
                ),
                Spacer("vertical"),
            ),
            Frame(
                width("75%"),
                spacing(5),
                margins(5, 5, 5, 5),
                Label(height("10%"), text("Apariencia"), font_size(8)),
                Frame(
                    id("box"),
                    orientation("row"),
                    height("15%"),
                    margins(5, 5, 5, 5),
                    Frame(
                        height("90%"),
                        width("70%"),
                        Label(height("45%"), text("Elige tu modo"), font_size(6)),
                        Label(
                            id("sub_text"),
                            height("55%"),
                            text("Cambia entre colores oscuros o blancos"),
                            font_size(4),
                        ),
                    ),
                    Spacer(),
                    ComboBox(
                        height("50%"),
                        width("25%"),
                        items(["Claro", "Oscuro"]),
                        index(vm.theme.mode_index),
                        on_click(vm.change_mode),
                        font_size(4),
                    ),
                ),
                Frame(
                    id("box"),
                    orientation("row"),
                    height("15%"),
                    margins(5, 5, 5, 5),
                    Frame(
                        height("90%"),
                        width("70%"),
                        Label(height("45%"), text("Color de enfasis"), font_size(6)),
                        Label(
                            id("sub_text"),
                            height("55%"),
                            text(
                                "Seleccione el color que complementara al modo oscuro o blanco"
                            ),
                            attributes({"wrap": True}),
                            font_size(4),
                        ),
                    ),
                    Spacer(),
                    ComboBox(
                        height("50%"),
                        width("25%"),
                        font_size(4),
                        index(vm.theme.color_index),
                        on_click(vm.change_color),
                        items(
                            [
                                "Azul",
                                "Rojo",
                                "Morado",
                                "Cian",
                                "Amarillo",
                                "Rosa",
                                "Verde",
                            ]
                        ),
                    ),
                ),
                Spacer("vertical"),
            ),
        ),
    )
