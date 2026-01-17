from ....Qtive.Component import (
    Dialog,
    Frame,
    LineEdit,
    Spacer,
    ToolButton,
    Message,
)
from ....Qtive.Props import (
    height,
    orientation,
    width,
    alignment,
    font_size,
    text,
    on_click,
    on_text_change,
    deploy,
    placeholder,
    margins,
    spacing,
    id,
)
from ...composite import ModalTitleBar
from .viewmodel import SaveManagerVM


def SaveManager():
    vm = SaveManagerVM()
    return Dialog(
        height("19.6%"),
        width("25%"),
        ModalTitleBar(vm.window.title, vm.close, 20),
        Message(deploy(vm.window.message)),
        Frame(
            spacing(5),
            margins(5, 5, 5, 5),
            Frame(
                Spacer("vertical"),
                LineEdit(
                    text(vm.window.name),
                    on_text_change(vm.change_name),
                    font_size(16),
                    height("2.8sh"),
                    width("90%"),
                    alignment("center"),
                    placeholder("Nombre del programa:"),
                ),
                Spacer("vertical"),
            ),
            Frame(
                height("5.6 sh"),
                orientation("row"),
                spacing(5),
                Spacer(),
                ToolButton(
                    text("Cancelar"),
                    height("100%"),
                    width("20%"),
                    font_size(16),
                    on_click(vm.close),
                    id("cancel"),
                ),
                ToolButton(
                    text("Guardar"),
                    height("100%"),
                    width("20%"),
                    font_size(16),
                    on_click(vm.save),
                ),
            ),
        ),
    )
