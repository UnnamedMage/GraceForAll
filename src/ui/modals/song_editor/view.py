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
    source,
    text,
    attributes,
    on_click,
    on_text_change,
    deploy,
    id,
    spacing,
    placeholder,
    margins,
)
from ...components import Projector, LyricsEdit
from ...composite import ModalTitleBar
from .sections import Toolbar
from .viewmodel import SongEditorVM


def SongEditor():
    vm = SongEditorVM()
    return Dialog(
        ModalTitleBar("Editor de canciones", vm.close),
        Message(deploy(vm.window.message)),
        Frame(
            spacing(5),
            margins(5, 5, 5, 5),
            LineEdit(
                height("2.8sh"),
                width("40%"),
                font_size(5),
                on_text_change(vm.set_title),
                text(vm.inputs.title),
                placeholder("Titulo:"),
                alignment("left"),
            ),
            Toolbar(),
            Frame(
                orientation("row"),
                spacing(5),
                LyricsEdit(
                    width("40%"),
                    font_size(5),
                    text(vm.inputs.lyrics),
                    on_text_change(vm.set_lyrics),
                    on_click(vm.set_text),
                    placeholder("Escriba aqui los versos"),
                ),
                Frame(
                    id("projector_frame"),
                    Projector(
                        height("90%"),
                        width("90%"),
                        alignment("center"),
                        source(vm.projector.bg),
                        text(vm.projector.text),
                        attributes(vm.projector.attrs),
                    ),
                ),
            ),
            Frame(
                height("5.6 sh"),
                orientation("row"),
                ToolButton(
                    text("Eliminar"),
                    height("100%"),
                    width("10%"),
                    font_size(5),
                    attributes(vm.window.btn_delete),
                    on_click(vm.delete),
                ),
                Spacer(),
                Frame(
                    height("100%"),
                    width("20%"),
                    orientation("row"),
                    spacing(5),
                    ToolButton(
                        text("Cancelar"),
                        height("100%"),
                        width("50%"),
                        font_size(5),
                        on_click(vm.close),
                        id("cancel"),
                    ),
                    ToolButton(
                        text("Guardar"),
                        height("100%"),
                        width("50%"),
                        font_size(5),
                        on_click(vm.save),
                    ),
                ),
            ),
        ),
    )
