from PySide6.QtWidgets import QApplication


def filter_opacity(color: str, alpha: float):
    """
    Permite escribir:
        {{ color | opacity(0.3) }}
    y convierte #RRGGBB en rgba(r,g,b,a)
    """

    color = color.strip().lower()

    # --- FORMATO HEX #RGB ---
    if color.startswith("#") and len(color) == 4:
        r = int(color[1] * 2, 16)
        g = int(color[2] * 2, 16)
        b = int(color[3] * 2, 16)
        return f"rgba({r}, {g}, {b}, {alpha})"

    # --- FORMATO HEX #RRGGBB ---
    if color.startswith("#") and len(color) == 7:
        r = int(color[1:3], 16)
        g = int(color[3:5], 16)
        b = int(color[5:7], 16)
        return f"rgba({r}, {g}, {b}, {alpha})"

    # --- FORMATO rgb(r,g,b) ---
    if color.startswith("rgb("):
        parts = color[4:-1].split(",")
        r, g, b = [int(x.strip()) for x in parts]
        return f"rgba({r}, {g}, {b}, {alpha})"

    # --- FORMATO rgba(r,g,b,a) ---
    if color.startswith("rgba("):
        parts = color[5:-1].split(",")
        r, g, b, a_old = [x.strip() for x in parts]
        return f"rgba({r}, {g}, {b}, {alpha})"

    # fallback
    return color


def filter_density(px: int):
    screen = QApplication.primaryScreen()

    v_ratio = screen.geometry().height() / 1080
    h_ratio = screen.geometry().width() / 1920

    ratio = (v_ratio + h_ratio) / 2
    return int(px * ratio)


def _parse_color(color: str):
    """
    Convierte un color en formato HEX/RGB/RGBA a tupla (r, g, b, a)
    """
    color = color.strip().lower()

    # --- HEX #RGB ---
    if color.startswith("#") and len(color) == 4:
        r = int(color[1] * 2, 16)
        g = int(color[2] * 2, 16)
        b = int(color[3] * 2, 16)
        return r, g, b, 1.0

    # --- HEX #RRGGBB ---
    if color.startswith("#") and len(color) == 7:
        r = int(color[1:3], 16)
        g = int(color[3:5], 16)
        b = int(color[5:7], 16)
        return r, g, b, 1.0

    # --- rgb(...) ---
    if color.startswith("rgb("):
        parts = color[4:-1].split(",")
        r, g, b = [int(x.strip()) for x in parts]
        return r, g, b, 1.0

    # --- rgba(...) ---
    if color.startswith("rgba("):
        parts = color[5:-1].split(",")
        r, g, b = [int(x.strip()) for x in parts[:3]]
        a = float(parts[3])
        return r, g, b, a

    raise ValueError(f"Formato no soportado: {color}")


def _apply_factor(value: int, factor: float) -> int:
    """
    Aplica un factor multiplicador y mantiene el 0-255.
    """
    return max(0, min(255, int(value * factor)))


def filter_lighter(color: str, percent: int = 110):
    """
    {{ color | lighter(115) }}
    Aclara el color multiplicando por percent/100
    """
    r, g, b, a = _parse_color(color)
    factor = percent / 100.0
    r2 = _apply_factor(r, factor)
    g2 = _apply_factor(g, factor)
    b2 = _apply_factor(b, factor)

    if a == 1.0:
        return f"rgb({r2}, {g2}, {b2})"
    return f"rgba({r2}, {g2}, {b2}, {a})"


def filter_darker(color: str, percent: int = 110):
    """
    {{ color | darker(130) }}
    Oscurece el color multiplicando por percent/100 pero al revés.
    (Qt: darker(130) = más oscuro)
    """
    r, g, b, a = _parse_color(color)
    factor = 100 / percent  # Qt-style darker
    r2 = _apply_factor(r, factor)
    g2 = _apply_factor(g, factor)
    b2 = _apply_factor(b, factor)

    if a == 1.0:
        return f"rgb({r2}, {g2}, {b2})"
    return f"rgba({r2}, {g2}, {b2}, {a})"
