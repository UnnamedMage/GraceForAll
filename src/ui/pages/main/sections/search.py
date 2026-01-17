from .....Qtive.Component import (
    Spacer,
    Frame,
    ToolButton,
    Label,
    Stacked,
    LineEdit,
    TableView,
    Menu,
)
from .....Qtive.Props import (
    orientation,
    height,
    width,
    alignment,
    aspect_ratio,
    image,
    font_size,
    placeholder,
    text,
    on_click,
    index,
    items,
    attributes,
    deploy,
    on_text_change,
    filter,
    on_double_click,
    on_enter_press,
    on_right_click,
    id,
    spacing,
    margins,
)
from functools import partial
from ....components import MediaSelector
from ..viewmodel import MainViewModel
from .search_menu import SlideStyleMenu

ScheduleButton = partial(
    ToolButton,
    width("100%"),
    aspect_ratio("1-1"),
)

SectionsButton = partial(
    ToolButton,
    width("25%"),
)

ToolBarButton = partial(
    ToolButton,
    height("100%"),
    aspect_ratio("1-1"),
)


def Search():
    vm = MainViewModel()
    vr = vm.vr
    sr = vm.sr
    pc = vm.pc
    ssc = vm.ssc
    mr = vm.mr
    sc = vm.sc
    ss = vm.ss

    return Frame(
        width("30%"),
        id("box"),
        spacing(5),
        margins(5, 5, 5, 5),
        ToolButton(
            height("5%"),
            font_size(3.6),
            on_click(ssc.view.menu.emit),
            text("Cambiar estilo pred."),
            SlideStyleMenu(),
        ),
        Label(height("5%"), text(sc.schedule_list.name)),
        Frame(
            orientation("row"),
            spacing(5),
            height("40%"),
            TableView(
                items(sc.schedule_list.items),
                on_click(sc.select),
                index(sc.schedule_list.index),
                attributes({"stretch": [0, 1], "selection_mode": "row"}),
                on_double_click(pc.send_to_live),
            ),
            Frame(
                width("10%"),
                spacing(5),
                ScheduleButton(
                    image("upward.svg"),
                    on_click(sc.move_up),
                    attributes(sc.btns.up),
                ),
                ScheduleButton(
                    image("downward.svg"),
                    on_click(sc.move_down),
                    attributes(sc.btns.down),
                ),
                ScheduleButton(
                    image("remove.svg"),
                    on_click(sc.delete),
                    attributes(sc.btns.remove),
                ),
                Spacer("vertical"),
                ScheduleButton(
                    image("add.svg"),
                    on_click(sc.add),
                    attributes(sc.btns.add),
                ),
            ),
        ),
        Frame(
            orientation("row"),
            height("6%"),
            spacing(2),
            Spacer("horizontal"),
            SectionsButton(
                alignment("right"),
                text("Canciones"),
                attributes(ss.song.btn_attrs),
                on_click(lambda: ss.change_section(0)),
            ),
            SectionsButton(
                alignment("hcenter"),
                text("Versiculos"),
                attributes(ss.verse.btn_attrs),
                on_click(lambda: ss.change_section(1)),
            ),
            SectionsButton(
                alignment("left"),
                text("Media"),
                attributes(ss.media.btn_attrs),
                on_click(lambda: ss.change_section(2)),
            ),
            Spacer("horizontal"),
        ),
        Stacked(
            height("44%"),
            index(ss.section.index),
            Frame(
                spacing(5),
                LineEdit(
                    height("8%"),
                    placeholder("Busqueda por titulo"),
                    text(sr.search.text),
                    on_text_change(sr.song_list.filter.emit),
                ),
                TableView(
                    items(sr.song_list.items),
                    index(ss.song.index),
                    filter(sr.song_list.filter),
                    attributes({"stretch": [1], "selection_mode": "row"}),
                    on_click(sr.select_song),
                    on_double_click(vm.pc.send_to_live),
                    on_enter_press(vm.pc.send_to_live),
                    on_right_click(sr.menu_song),
                    Menu(
                        items(["Editar", "Eliminar"]),
                        deploy(sr.song_list.menu),
                        attributes({"direction": "right"}),
                    ),
                ),
            ),
            Frame(
                spacing(5),
                Frame(
                    height("8%"),
                    orientation("row"),
                    spacing(5),
                    LineEdit(
                        placeholder("Busqueda por cita"),
                        attributes(vr.search.attrs),
                        text(vr.search.text),
                        on_text_change(vr.looking_for_verse),
                    ),
                    ToolButton(
                        width("30%"),
                        text(vr.bible_selector.version),
                        on_click(vr.version_for_select),
                        Menu(
                            deploy(vr.bible_selector.menu),
                            items(vr.bible_selector.avalible_items),
                            attributes({"direction": "left"}),
                        ),
                    ),
                ),
                TableView(
                    items(vr.verses.items),
                    attributes({"stretch": [0, 1], "selection_mode": "row"}),
                    filter(vr.verses.filter),
                    index(ss.verse.index),
                    on_click(vr.select_verse),
                    on_double_click(vm.pc.send_to_live),
                    on_enter_press(vm.pc.send_to_live),
                ),
            ),
            Frame(
                spacing(5),
                MediaSelector(
                    items(mr.media.items),
                    font_size(2),
                    on_click(mr.media_selected),
                    on_double_click(pc.send_to_live),
                ),
                ToolButton(
                    height("10%"),
                    font_size(5),
                    text("Cambiar carpeta raiz"),
                    on_click(mr.change_media_folder),
                ),
            ),
        ),
    )
