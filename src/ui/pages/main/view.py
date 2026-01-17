from ....Qtive.Component import Window, Frame
from ....Qtive.Props import orientation, spacing, margins
from .sections import TitleBar, SideBar, Search, Onlive, Preview


def MainView():
    return Window(
        TitleBar(),
        Frame(
            orientation("row"),
            SideBar(),
            Frame(
                spacing(5),
                margins(5, 5, 5, 5),
                orientation("row"),
                Search(),
                Preview(),
                Onlive(),
            ),
        ),
    )
