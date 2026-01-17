from .....Qtive.Component import (
    Frame,
    ToolButton,
    Label,
    Stacked,
    TableView,
    Slider,
    Spacer,
)
from .....Qtive.Props import (
    height,
    width,
    alignment,
    items,
    aspect_ratio,
    image,
    attributes,
    source,
    text,
    on_click,
    on_double_click,
    on_enter_press,
    orientation,
    on_execution,
    on_update,
    index,
    id,
    spacing,
    margins,
)
from ....components import Projector
from ..viewmodel import MainViewModel


def Preview():
    vm = MainViewModel()
    pc = vm.pc
    return Frame(
        width("35%"),
        spacing(5),
        margins(5, 5, 5, 5),
        id("box"),
        ToolButton(
            alignment("right"),
            image("go.svg"),
            height("5%"),
            aspect_ratio("1-1"),
            on_click(lambda: vm.pc.send_to_live(None)),
        ),
        Label(height("5%"), text(pc.view.title)),
        Stacked(
            height("46%"),
            index(pc.view.mode),
            TableView(
                items(pc.view.lyrics),
                attributes({"stretch": [1], "selection_mode": "row", "wrap": True}),
                on_click(pc.change_text),
                on_double_click(vm.pc.send_to_live),
                on_enter_press(vm.pc.send_to_live),
            ),
            Frame(
                Spacer("vertical"),
                margins(5, 5, 5, 5),
                Label(
                    height("10%"),
                    text(pc.player.time),
                    attributes({"text_align": "right"}),
                ),
                Slider(
                    orientation("row"),
                    height("15%"),
                    attributes(pc.player.range),
                    index(pc.player.value),
                    on_update(lambda p: pc.set_attr_player("pos", p)),
                ),
                Frame(
                    orientation("row"),
                    height("15%"),
                    spacing(5),
                    ToolButton(
                        image(pc.btns.play),
                        height("100%"),
                        aspect_ratio("3-2"),
                        on_click(pc.change_play),
                    ),
                    ToolButton(
                        image("stop.svg"),
                        height("80%"),
                        aspect_ratio("3-2"),
                        on_click(pc.set_stop),
                    ),
                    Spacer(),
                    ToolButton(
                        image(pc.btns.mute),
                        height("80%"),
                        aspect_ratio("3-2"),
                        on_click(pc.change_mute),
                    ),
                    Slider(
                        height("100%"),
                        width("20%"),
                        orientation("row"),
                        on_update(lambda v: pc.set_attr_player("volumen", v)),
                        index(pc.player.volumen),
                        attributes({"range": (0, 100)}),
                    ),
                ),
                Spacer("vertical"),
                Frame(height("11%")),
            ),
        ),
        Frame(
            height("44%"),
            id("projector_frame"),
            Projector(
                height("90%"),
                width("90%"),
                alignment("center"),
                source(pc.projector.bg),
                attributes(pc.projector.attrs),
                text(pc.projector.text),
                on_update(lambda t: pc.set_attr_player("time", t)),
                on_execution(lambda d: pc.set_attr_player("duration", d)),
                index(pc.projector.pos),
            ),
        ),
    )
