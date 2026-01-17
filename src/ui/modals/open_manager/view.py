from ....Qtive.Component import Dialog, Frame, Spacer, ToolButton, TableView, Message
from ....Qtive.Props import (
    height,
    orientation,
    width,
    font_size,
    text,
    attributes,
    items,
    on_click,
    on_double_click,
    deploy,
    spacing,
    margins,
)
from ...composite import ModalTitleBar
from .viewmodel import OpenManagerVM


def OpenManager():
    vm = OpenManagerVM()
    return Dialog(
        height("50%"),
        width("30%"),
        ModalTitleBar("Abrir programa", vm.window.close.emit),
        Message(deploy(vm.window.message)),
        Frame(
            spacing(5),
            margins(5, 5, 5, 5),
            TableView(
                items(vm.schedules_list.items),
                attributes({"stretch": [1, 0], "selection_mode": "row"}),
                on_click(vm.schedule_selected),
                on_double_click(vm.send_schedule),
                font_size(6),
            ),
            Frame(
                height("5.6 sh"),
                orientation("row"),
                ToolButton(
                    text("Borrar"),
                    height("100%"),
                    width("16%"),
                    font_size(5),
                    on_click(vm.delete_schedule),
                    attributes(vm.btns.attr),
                ),
                Spacer(),
                Frame(
                    orientation("row"),
                    spacing(5),
                    width("32%"),
                    ToolButton(
                        text("Cancelar"),
                        height("100%"),
                        width("50%"),
                        font_size(5),
                        on_click(vm.window.close.emit),
                    ),
                    ToolButton(
                        text("Abrir"),
                        height("100%"),
                        width("50%"),
                        font_size(5),
                        on_click(vm.send_schedule),
                        attributes(vm.btns.attr),
                    ),
                ),
            ),
        ),
    )
