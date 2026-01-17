from .....Qtive.Component import Spacer, Frame, ToolButton, Message
from .....Qtive.Props import (
    width,
    aspect_ratio,
    margins,
    image,
    font_size,
    text,
    on_click,
    deploy,
    id,
    spacing,
)
from .....Qtive.Style import add_rule
from functools import partial
from ..viewmodel import MainViewModel

SideBarButton = partial(
    ToolButton, width("100%"), aspect_ratio("5-1"), font_size(3.6), id("sidebar")
)

add_rule("""
    QToolButton#sidebar  {
    color: {{primaryTextColor}};
    background-color: {{secondaryLightColor}};
    border: none;
    }

    QToolButton#sidebar:checked,
    QToolButton#sidebar:pressed {
    border-color: {{primaryLightColor}};
    border-width: 0 0 0 5px;
    border-style: solid;
    }

    QToolButton#sidebar:hover {
    background-color: {{secondaryColor}};
    }         
""")


def SideBar():
    vm = MainViewModel()
    return Frame(
        width("14%"),
        spacing(5),
        margins(5, 0, 0, 0),
        SideBarButton(
            image("new_playlist.svg"),
            text("Nuevo Programa"),
            on_click(vm.new_schedule),
        ),
        SideBarButton(
            image("open_playlist.svg"),
            text("Abrir Programa..."),
            on_click(vm.open_schedule),
        ),
        SideBarButton(
            image("save_playlist.svg"),
            text("Guardar Programa"),
            on_click(lambda: vm.save_schedule()),
        ),
        SideBarButton(
            image("save_as.svg"),
            text("Guardar como..."),
            on_click(lambda: vm.save_schedule(True)),
        ),
        SideBarButton(
            image("new_song.svg"),
            text("Nueva cancion"),
            on_click(lambda: vm.app.song_editor.emit("")),
        ),
        Spacer("vertical"),
        SideBarButton(
            image("settings.svg"),
            text("Configuracion"),
            on_click(vm.app.settings_manager.emit),
        ),
        SideBarButton(
            image("info.svg"), text("Acerca de..."), on_click(vm.app.about.emit)
        ),
        Message(deploy(vm.view.message)),
    )
