from ....Qtive.Component import Dialog, Label, Frame, Spacer
from ....Qtive.Props import (
    height,
    orientation,
    width,
    aspect_ratio,
    image,
    font_size,
    text,
    margins,
    spacing,
    id,
    attributes,
)
from ....Qtive.Style import add_rule
from ...composite import ModalTitleBar
from .viewmodel import AboutVM

add_rule("""
QLabel#title {
  border: none;
  background: transparent;
  color: {{primaryTextColor}};
  border-color:{{primaryTextColor}};
  border-width: 0 0 2px 0;
  border-style: solid;
}
    
""")


def About():
    vm = AboutVM()
    return Dialog(
        width("30%"),
        aspect_ratio("1-1"),
        ModalTitleBar("Acerca de...", vm.window.close.emit, 6),
        Frame(
            margins(20, 0, 20, 0),
            spacing(10),
            Label(
                height("5%"),
                text("Informacion acerca del programa"),
                font_size(5),
                id("title"),
            ),
            Frame(
                height("25%"),
                orientation("row"),
                margins(20, 0, 20, 0),
                spacing(20),
                Label(
                    height("100%"),
                    aspect_ratio("1-1"),
                    image("GraceForAll.png"),
                    font_size(5),
                ),
                Frame(
                    Spacer("vertical"),
                    Label(height("30%"), text("GraceForAll"), font_size(7)),
                    Label(height("20%"), text("Version 1.1.0"), font_size(4)),
                    Spacer("vertical"),
                ),
            ),
            Label(
                height("5%"),
                text("Las siguientes personas que han participado en este projecto:"),
                font_size(5),
            ),
            Frame(
                height("25%"),
                margins(20, 0, 20, 0),
                Label(
                    height("20%"),
                    text("● Izacar Alvarez Ortega(Desarrollador)"),
                    font_size(5),
                ),
                Spacer("vertical"),
            ),
            Label(
                id("title"), height("5%"), text("Informacion de contacto"), font_size(5)
            ),
            Frame(
                height("5%"),
                orientation("row"),
                Label(width("25%"), text("Correo:"), font_size(5)),
                Label(
                    width("75%"),
                    text("zerel.eclipse@gmail.com"),
                    font_size(5),
                    attributes({"text_mode": "email"}),
                ),
            ),
            Frame(
                height("5%"),
                orientation("row"),
                Label(width("25%"), text("Telefono:"), font_size(5)),
                Label(
                    width("75%"),
                    text("4426836838"),
                    font_size(5),
                    attributes({"text_mode": "phone"}),
                ),
            ),
            Label(
                text(
                    """Este software es un proyecto completamente gratuito,\ncreado para apoyar a iglesias y comunidades sin costo alguno.\nSu desarrollo y mantenimiento continúan gracias al apoyo\nde quienes desean contribuir voluntariamente.\n¡Gracias por ser parte de este proyecto!"""
                ),
                attributes({"wrap": True, "text_align": "center"}),
                font_size(4),
            ),
        ),
    )
