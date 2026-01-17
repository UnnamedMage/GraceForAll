from PySide6.QtWidgets import QGraphicsProxyWidget, QLabel
from PySide6.QtGui import QFont
from PySide6.QtCore import (
    Qt,
    QPointF,
    QTimer,
    QEasingCurve,
    Signal,
    QPropertyAnimation,
    QObject,
    Property,
)
from enum import Enum


class AnimationState(Enum):
    STOPPED = 0
    RUNNING = 1
    PAUSED = 2


class AnimationDirection(Enum):
    IN = 0
    OUT = 1


# =============================================================================
# MÓDULO BASE
# =============================================================================


class BaseTransitionAnimation(QObject):
    """Clase base para animaciones de transición (entrada/salida)"""

    # Señal para notificar cuando la animación termina
    finished = Signal()

    def __init__(self, text_item):
        super().__init__()
        self.text_item = text_item
        self.animation = None
        self.timer = None
        self.state = AnimationState.STOPPED
        self.direction = AnimationDirection.IN
        self.original_opacity = 1.0
        self.original_pos = QPointF(0, 0)
        self.original_scale = 1.0
        self.original_rotation = 0.0

    def setup_animation(self):
        pass

    def start(self, direction=AnimationDirection.IN):
        self.direction = direction
        self.state = AnimationState.RUNNING
        self.save_original_state()
        self.prepare_animation()

        if self.animation:
            # CONECTAR SEÑAL DE FINALIZACIÓN
            self.animation.finished.connect(self._on_animation_finished)
            self.animation.start()

        if self.timer:
            self.timer.start()

    def stop(self):
        self.state = AnimationState.STOPPED
        if self.animation:
            self.animation.finished.disconnect()
            self.animation.stop()
        if self.timer:
            self.timer.stop()
        self.cleanup()

    def _on_animation_finished(self):
        """Maneja la finalización de la animación"""
        if self.animation:
            self.animation.finished.disconnect()
        self.finished.emit()
        self.state = AnimationState.STOPPED

    def save_original_state(self):
        self.original_opacity = self.text_item.opacity()
        self.original_pos = self.text_item.pos()
        self.original_scale = self.text_item.scale()
        self.original_rotation = self.text_item.rotation()

    def prepare_animation(self):
        pass

    def cleanup(self):
        if self.direction == AnimationDirection.OUT:
            self.text_item.setOpacity(self.original_opacity)
            self.text_item.setPos(self.original_pos)
            self.text_item.setScale(self.original_scale)
            self.text_item.setRotation(self.original_rotation)

    def get_duration(self):
        """Retorna la duración estimada de la animación en ms"""
        if self.animation:
            return self.animation.duration()
        elif self.timer:
            # Para animaciones basadas en timer, estimar duración
            return 2000  # 2 segundos por defecto
        return 1000  # 1 segundo por defecto


# =============================================================================
# ANIMACIONES DE ENTRADA (MISMAS PERO CON SEÑALES)
# =============================================================================


class FadeInAnimation(BaseTransitionAnimation):
    """Entrada con efecto de fundido"""

    def __init__(self, text_item):
        super().__init__(text_item)
        self.setup_animation()

    def setup_animation(self):
        self.animation = QPropertyAnimation(self.text_item, b"opacity")
        self.animation.setDuration(1000)
        self.animation.setStartValue(0.0)
        self.animation.setEndValue(1.0)
        self.animation.setEasingCurve(QEasingCurve.OutCubic)

    def prepare_animation(self):
        if self.direction == AnimationDirection.IN:
            self.text_item.setOpacity(0.0)
            self.text_item.setPos(self.text_item.pos_in_view)
            self.text_item.setScale(1.0)


class SlideInAnimation(BaseTransitionAnimation):
    """Entrada deslizante desde la izquierda"""

    def __init__(self, text_item):
        super().__init__(text_item)
        self.setup_animation()

    def setup_animation(self):
        self.animation = QPropertyAnimation(self.text_item, b"pos")
        self.animation.setDuration(800)
        self.animation.setEasingCurve(QEasingCurve.OutBack)

    def prepare_animation(self):
        if self.direction == AnimationDirection.IN:
            target_pos = self.text_item.pos_in_view
            start_pos = QPointF(
                target_pos.x() - self.text_item.parent().width(), target_pos.y()
            )
            self.animation.setStartValue(start_pos)
            self.animation.setEndValue(target_pos)
            self.text_item.setPos(start_pos)
            self.text_item.setOpacity(1.0)
            self.text_item.setScale(1.0)


class ZoomInAnimation(BaseTransitionAnimation):
    """Entrada con zoom desde pequeño"""

    def __init__(self, text_item):
        super().__init__(text_item)
        self.setup_animation()

    def setup_animation(self):
        self.animation = QPropertyAnimation(self.text_item, b"scale")
        self.animation.setDuration(700)
        self.animation.setStartValue(0.3)
        self.animation.setEndValue(1.0)
        self.animation.setEasingCurve(QEasingCurve.OutBack)

    def prepare_animation(self):
        if self.direction == AnimationDirection.IN:
            self.text_item.setScale(0.3)
            self.text_item.setOpacity(1.0)
            self.text_item.setPos(self.text_item.pos_in_view)


class BounceInAnimation(BaseTransitionAnimation):
    """Entrada con efecto de rebote"""

    def __init__(self, text_item):
        super().__init__(text_item)
        self.setup_animation()

    def setup_animation(self):
        self.animation = QPropertyAnimation(self.text_item, b"pos")
        self.animation.setDuration(1000)
        self.animation.setEasingCurve(QEasingCurve.OutBounce)

    def prepare_animation(self):
        if self.direction == AnimationDirection.IN:
            target_pos = self.text_item.pos_in_view
            start_pos = QPointF(target_pos.x(), target_pos.y() - 120)
            self.animation.setStartValue(start_pos)
            self.animation.setEndValue(target_pos)
            self.text_item.setPos(start_pos)
            self.text_item.setOpacity(1.0)
            self.text_item.setScale(1.0)


class SpinInAnimation(BaseTransitionAnimation):
    """Entrada giratoria"""

    def __init__(self, text_item):
        super().__init__(text_item)
        self._rotation = 0
        self.setup_animation()

    def get_rotation(self):
        return self._rotation

    def set_rotation(self, angle):
        self._rotation = angle
        self.text_item.setRotation(angle)

    rotation = Property(float, get_rotation, set_rotation)

    def setup_animation(self):
        self.animation = QPropertyAnimation(self, b"rotation")
        self.animation.setDuration(900)
        self.animation.setStartValue(-360)
        self.animation.setEndValue(0)
        self.animation.setEasingCurve(QEasingCurve.OutCubic)

    def prepare_animation(self):
        if self.direction == AnimationDirection.IN:
            self.text_item.setRotation(-360)
            self.text_item.setScale(1.0)
            self.text_item.setOpacity(1.0)
            self.text_item.setPos(self.text_item.pos_in_view)


class TypewriterInAnimation(BaseTransitionAnimation):
    """Entrada tipo máquina de escribir"""

    def __init__(self, text_item):
        super().__init__(text_item)
        self.original_text = ""
        self.current_text = ""
        self.char_index = 0
        self.setup_animation()

    def setup_animation(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.type_next_char)
        self.timer.setInterval(50)

    def prepare_animation(self):
        if self.direction == AnimationDirection.IN:
            self.original_text = self.text_item.toPlainText()
            self.current_text = ""
            self.char_index = 0
            self.text_item.setPlainText("")
            self.text_item.setScale(1.0)
            self.text_item.setOpacity(1.0)
            self.text_item.setPos(self.text_item.pos_in_view)

    def start(self, direction=AnimationDirection.IN):
        super().start(direction)
        if direction == AnimationDirection.IN:
            self.timer.start()

    def stop(self):
        self.timer.stop()
        super().stop()

    def type_next_char(self):
        if self.char_index < len(self.original_text):
            self.current_text += self.original_text[self.char_index]
            self.text_item.setPlainText(self.current_text)
            self.char_index += 1
        else:
            self._on_animation_finished()  # LLAMAR MANUALMENTE AL TERMINAR

    def get_duration(self):
        """Duración estimada basada en la longitud del texto"""
        char_count = len(self.original_text) if self.original_text else 0
        return char_count * 50 + 500  # 50ms por carácter + 500ms extra


# =============================================================================
# ANIMACIONES DE SALIDA (MISMAS PERO CON SEÑALES)
# =============================================================================


class FadeOutAnimation(BaseTransitionAnimation):
    """Salida con efecto de fundido"""

    def __init__(self, text_item):
        super().__init__(text_item)
        self.setup_animation()

    def setup_animation(self):
        self.animation = QPropertyAnimation(self.text_item, b"opacity")
        self.animation.setDuration(1000)
        self.animation.setStartValue(1.0)
        self.animation.setEndValue(0.0)
        self.animation.setEasingCurve(QEasingCurve.InCubic)

    def prepare_animation(self):
        if self.direction == AnimationDirection.OUT:
            self.text_item.setOpacity(1.0)


class SlideOutAnimation(BaseTransitionAnimation):
    """Salida deslizante hacia la derecha"""

    def __init__(self, text_item):
        super().__init__(text_item)
        self.setup_animation()

    def setup_animation(self):
        self.animation = QPropertyAnimation(self.text_item, b"pos")
        self.animation.setDuration(800)
        self.animation.setEasingCurve(QEasingCurve.InBack)

    def prepare_animation(self):
        if self.direction == AnimationDirection.OUT:
            start_pos = self.text_item.pos_in_view
            end_pos = QPointF(
                start_pos.x() + self.text_item.parent().width(), start_pos.y()
            )
            self.animation.setStartValue(start_pos)
            self.animation.setEndValue(end_pos)


class ZoomOutAnimation(BaseTransitionAnimation):
    """Salida con zoom hacia pequeño"""

    def __init__(self, text_item):
        super().__init__(text_item)
        self.setup_animation()

    def setup_animation(self):
        self.animation = QPropertyAnimation(self.text_item, b"scale")
        self.animation.setDuration(700)
        self.animation.setStartValue(1.0)
        self.animation.setEndValue(0.3)
        self.animation.setEasingCurve(QEasingCurve.InBack)

    def prepare_animation(self):
        if self.direction == AnimationDirection.OUT:
            self.text_item.setScale(1.0)


class SpinOutAnimation(BaseTransitionAnimation):
    """Salida giratoria"""

    def __init__(self, text_item):
        super().__init__(text_item)
        self._rotation = 0
        self.setup_animation()

    def get_rotation(self):
        return self._rotation

    def set_rotation(self, angle):
        self._rotation = angle
        self.text_item.setRotation(angle)

    rotation = Property(float, get_rotation, set_rotation)

    def setup_animation(self):
        self.animation = QPropertyAnimation(self, b"rotation")
        self.animation.setDuration(900)
        self.animation.setStartValue(0)
        self.animation.setEndValue(360)
        self.animation.setEasingCurve(QEasingCurve.InCubic)

    def prepare_animation(self):
        if self.direction == AnimationDirection.OUT:
            self.text_item.setRotation(0)


class ShrinkOutAnimation(BaseTransitionAnimation):
    """Salida con efecto de encogimiento"""

    def __init__(self, text_item):
        super().__init__(text_item)
        self.setup_animation()

    def setup_animation(self):
        self.animation = QPropertyAnimation(self.text_item, b"scale")
        self.animation.setDuration(500)
        self.animation.setStartValue(1.0)
        self.animation.setEndValue(0.0)
        self.animation.setEasingCurve(QEasingCurve.InQuad)


# =============================================================================
# CLASE PRINCIPAL CORREGIDA
# =============================================================================


class PText(QGraphicsProxyWidget):
    """
    props:  Level, Text, Attributes
    """

    def __init__(self, parent):
        QGraphicsProxyWidget.__init__(self)
        self.setParent(parent)
        self.text = QLabel()
        self.text.setWordWrap(True)
        self.text.setStyleSheet("background-color: transparent;")
        self.setWidget(self.text)
        self.font_factor = 1
        self.font_bold = False
        self.font_italic = False
        self.font_family = "Arial"
        self.text_color = "black"
        self.h_align = "hcenter"
        self.v_align = "vcenter"
        self.in_animation = "slide_in"
        self.out_animation = "fade_out"
        self.text_animation = ("slide_in", "fade_out")
        self.update_style_needs = True
        self.gradient = None
        self.pos_in_view = None
        # Variables de estado
        self.current_text = ""
        self.previous_text = ""
        self.is_transitioning = False

        # Diccionarios de animaciones
        self.in_animations = {}
        self.out_animations = {}

        # Inicializar módulos
        self._initialize_animation_modules()

    def set_attributes(self, properties: dict):
        for key, value in properties.items():
            self.setter(key, value)
        self.update_style_needs = True

    def setter(self, attr, value):
        if attr == "factor":
            self.font_factor = value
        elif attr == "bold":
            self.font_bold = value
        elif attr == "italic":
            self.font_italic = value
        elif attr == "family":
            self.font_family = value
        elif attr == "color":
            self.text_color = value
        elif attr == "h_align":
            self.h_align = value
        elif attr == "v_align":
            self.v_align = value
        elif attr == "in_animation":
            self.in_animation = value
        elif attr == "out_animation":
            self.out_animation = value

    def _font(self):
        parent = self.parent()
        window = parent.context.get("window")
        screen = window.screen()
        logical_dpi = screen.logicalDotsPerInch() if screen else 96
        reference_height = 1080
        base_size = 40 + (10 * self.font_factor)
        scale_factor = (parent.height() / reference_height) * (96 / logical_dpi)
        scaled_size = int(base_size * scale_factor)
        font = QFont(self.font_family)
        font.setPointSize(scaled_size)
        font.setBold(self.font_bold)
        font.setItalic(self.font_italic)
        return font

    def _apply_style(self):
        self.text.setFont(self._font())
        self.text.setStyleSheet(
            f"background-color: transparent; color: {self.text_color};"
        )
        self.update_style_needs = False

    def _adjust_text(self):
        if self.text.text() != "":
            if self.h_align == "left":
                h_align = Qt.AlignLeft
            elif self.h_align == "right":
                h_align = Qt.AlignRight
            else:  # "hcenter"
                h_align = Qt.AlignHCenter

            # Cálculo Y
            if self.v_align == "top":
                y_align = Qt.AlignTop
            elif self.v_align == "bottom":
                y_align = Qt.AlignBottom
            else:  # "vcenter"
                y_align = Qt.AlignVCenter

            self.text.setAlignment(h_align | y_align)
            self.set_pos_mod(0, 0)

    def update(self):
        # self.stop_all_animations() revisar esto tambien
        parente_size = self.parent().size()
        self.text.setFixedSize(parente_size)
        h, w = int(parente_size.height() * 0.03), int(parente_size.width() * 0.03)
        self.text.setContentsMargins(w, h, w, h)
        self.setPos(0, 0)
        self._apply_style()
        self._adjust_text()

    def set_pos_mod(self, x, y):
        self.pos_in_view = QPointF(x, y)

    def setPlainText(self, text):
        if self.update_style_needs:
            self._apply_style()
        self.text.setText(text)
        self._adjust_text()

    def _initialize_animation_modules(self):
        """Inicializa todos los módulos de animación"""

        # Animaciones de ENTRADA
        self.in_animations = {
            "fade": FadeInAnimation(self),
            "slide": SlideInAnimation(self),
            "zoom": ZoomInAnimation(self),
            "bounce": BounceInAnimation(self),
            "spin": SpinInAnimation(self),  # revisa despues
            "typewriter": TypewriterInAnimation(self),  # revisa despues
        }

        # Animaciones de SALIDA
        self.out_animations = {
            "fade": FadeOutAnimation(self),
            "slide": SlideOutAnimation(self),
            "zoom": ZoomOutAnimation(self),
            "spin": SpinOutAnimation(self),  # revisa despues
            "shrink": ShrinkOutAnimation(self),  # revisa despues
        }

    def set_text_with_transition(self, new_text):
        if new_text == "":
            self.current_text = new_text
            self.setPlainText(new_text)
            return

        # Si ya hay texto actual, iniciar secuencia de transición
        if self.current_text:
            self._start_transition_sequence(new_text)
        else:
            # Si no hay texto actual, establecer directamente y animar entrada
            self.current_text = new_text
            self.setPlainText(new_text)
            self._play_entrance_animation()

    def _start_transition_sequence(self, new_text):
        """Inicia la secuencia completa de transición de texto"""
        self.is_transitioning = True
        self.previous_text = self.current_text

        # Obtener animación de salida
        out_animation_name = self.out_animation
        if out_animation_name in self.out_animations:
            out_animation = self.out_animations[out_animation_name]

            # CONECTAR SEÑAL PARA SABER CUÁNDO TERMINA LA SALIDA
            out_animation.finished.connect(
                lambda: self._on_out_animation_finished(new_text)
            )

            # Iniciar animación de salida
            out_animation.start(AnimationDirection.OUT)
        else:
            # Si no hay animación de salida válida, cambiar texto inmediatamente
            self._change_text_during_transition(new_text)

    def _on_out_animation_finished(self, new_text):
        """Se ejecuta cuando termina la animación de salida"""
        # Cambiar el texto
        self._change_text_during_transition(new_text)

    def _change_text_during_transition(self, new_text):
        """Cambia el texto durante la transición"""
        self.current_text = new_text
        self.setPlainText(new_text)

        # Pequeño delay para que el texto se establezca antes de la entrada
        QTimer.singleShot(50, self._play_entrance_animation)

    def _play_entrance_animation(self):
        """Ejecuta la animación de entrada"""
        in_animation_name = self.in_animation
        if in_animation_name in self.in_animations:
            in_animation = self.in_animations[in_animation_name]

            # CONECTAR SEÑAL PARA SABER CUÁNDO TERMINA LA ENTRADA
            in_animation.finished.connect(self._on_in_animation_finished)

            # Iniciar animación de entrada
            in_animation.start(AnimationDirection.IN)
        else:
            # Si no hay animación de entrada válida, terminar transición
            self._end_transition()

    def _on_in_animation_finished(self):
        """Se ejecuta cuando termina la animación de entrada"""
        self._end_transition()

    def _end_transition(self):
        """Marca el fin de la transición"""
        self.is_transitioning = False

    def stop_all_animations(self):
        """Detiene todas las animaciones"""
        for animation in self.in_animations.values():
            animation.stop()
        for animation in self.out_animations.values():
            animation.stop()
        self.is_transitioning = False
