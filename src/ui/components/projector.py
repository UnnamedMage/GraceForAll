from PySide6.QtWidgets import QGraphicsView, QGraphicsScene, QApplication
from PySide6.QtCore import Qt, Signal, QSize, QEvent
from ...Qtive.Component.interfaces import Interactive, Component, Static, Floating
from ...Qtive.Props.visual import Width, Height, AspectRatio, Alignment, Id
from ...Qtive.Props.content import Attributes, Source, Text, Index
from ...Qtive.Props.events import OnUpdate, OnExecution
from ...Qtive.Style import add_rule
from .p_video import PVideo
from .p_image import PImage
from .p_text import PText
from .p_marquee import PMarquee
from types import FunctionType, MethodType, LambdaType


add_rule("QGraphicsView#projector { background-color: {{secondaryColor}}; }")
add_rule("QGraphicsView#secondary { background-color: black; }")
add_rule(
    """QFrame#projector_frame { 
    background-color: {{secondaryDarkColor}};
    border-radius: {{2 | density()}}px;
    border: {{1 | density()}}px solid {{secondaryColor}};
    }
"""
)


class Projector(QGraphicsView, Component, Static, Interactive):
    def __init__(self, *args):
        QGraphicsView.__init__(self)
        Component.__init__(self)
        Static.__init__(self)
        Interactive.__init__(self)
        self.setObjectName("projector")
        self._scene = QGraphicsScene()
        self.setScene(self._scene)
        self.setFrameShape(QGraphicsView.NoFrame)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.func_pos = None
        self.func_dur = None
        self.text_postponed: str | None = None
        self.bg_onchange = False
        self.actual_media = None

        self.video = PVideo(self)
        self.video.setZValue(0)
        self._scene.addItem(self.video)

        self.image = PImage(self)
        self.video.setZValue(0)
        self._scene.addItem(self.image)

        self.text = PText(self)
        self.text.setZValue(1)
        self._scene.addItem(self.text)

        self.marquee = PMarquee(self)
        self.marquee.setZValue(2)
        self._scene.addItem(self.marquee)

        self.image.signals.loaded.connect(self.set_text_postponed)
        self.video.signals.loaded.connect(self.set_text_postponed)
        self.assign_props(args)
        self._first_polish_done = False
        self.installEventFilter(self)

    def eventFilter(self, obj, event):
        et = event.type()

        # Cuando Qt YA CALCULÓ tamaño + QSS + layout
        if et in (QEvent.Polish, QEvent.PolishRequest):
            if not self._first_polish_done and self.context:
                self._first_polish_done = True
                self.propagate_after_resize()
            return False

        # Cuando Qt recalcula el layout del widget
        if et == QEvent.LayoutRequest:
            if self._first_polish_done and self.context:
                self.propagate_after_resize()
            return False

        return False

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self._first_polish_done and self.context:
            self.propagate_after_resize()

    def assign_props(self, args):
        for arg in args:
            if isinstance(
                arg,
                (
                    Width,
                    Height,
                    AspectRatio,
                    Alignment,
                    Attributes,
                    Source,
                    OnUpdate,
                    OnExecution,
                    Text,
                    Index,
                    Id,
                ),
            ):
                self.props[arg.key] = arg.value

            elif isinstance(arg, Floating):
                arg.anchor = self
                self.floatings.append(arg)

        if text := self.props.get("text", None):
            if isinstance(text, Signal):
                text.connect(self.set_text)

        if source := self.props.get("source", None):
            if isinstance(source, str):
                self.set_source(source)
            else:
                source.connect(self.set_source)

        if attrs := self.props.get("attributes", None):
            if isinstance(attrs, Signal):
                attrs.connect(self.set_attributes)
            elif isinstance(attrs, dict):
                self.set_attributes(attrs)

        if index := self.props.get("index", None):
            if isinstance(index, Signal):
                index.connect(self.video.player.setPosition)

        if onupdate := self.props.get("onupdate", None):
            if isinstance(onupdate, (FunctionType, MethodType, LambdaType)):
                self.video.player.positionChanged.connect(onupdate)

        if onexecution := self.props.get("onexecution", None):
            if isinstance(onexecution, (FunctionType, MethodType, LambdaType)):
                self.video.player.durationChanged.connect(onexecution)

        if id := self.props.get("id"):
            self.setObjectName(id)

    def set_attributes(self, properties: dict):
        for key, value in properties.items():
            self.setter(key, value)

    def setter(self, attr, value):
        match attr:
            case "aspect_ratio":
                self.video.set_aspect_ratio_mode(value)
                self.image.set_aspect_ratio_mode(value)
            case "loop":
                self.video.set_loop(value)
            case "state":
                self.video.set_state(value)
            case "slide_style":
                self.text.set_attributes(value)
                if value.get("immediate"):
                    self.text._apply_style()
                    self.text._adjust_text()
            case "initial_time":
                self.video.set_initial_time(value)
            case "mute":
                self.video.audio_output.setMuted(value)
            case "volume":
                self.video.audio_output.setVolume(value / 100)

    def set_source(self, source: str):
        if source == "":
            self.video.setVisible(False)
            self.image.setVisible(False)
            return

        if source == "_show" and self.actual_media:
            self.actual_media.setVisible(True)

        if source.lower().endswith((".mp4", ".avi", ".mkv", ".mov", ".wmv", ".gif")):
            self.bg_onchange = True
            self.video.set_source(source)
            self.video.setVisible(True)
            self.actual_media = self.video
            self.image.setVisible(False)
        elif source.lower().endswith((".png", ".jpg", ".jpeg", ".bmp", ".webp")):
            self.bg_onchange = True
            self.image.set_source(source)
            self.actual_media = self.image
            self.video.setVisible(False)
            self.image.setVisible(True)

    def set_text(self, text: str, main: bool = True):
        if main:
            if self.bg_onchange:
                self.text_postponed = text
                return
            self.text.set_text_with_transition(text)
        else:
            self.marquee.set_text(text)

    def set_text_postponed(self):
        self.bg_onchange = False
        if self.text_postponed:
            self.text.set_text_with_transition(self.text_postponed)
            self.text_postponed = None

    def set_size(self, size: QSize):
        screens = QApplication.screens()
        geometry = screens[1].geometry() if len(screens) > 1 else screens[0].geometry()

        w_ratio, h_ratio = geometry.width(), geometry.height()
        new_w, new_h = size.width(), size.height()

        try_w = new_w
        try_h = int(try_w * (h_ratio / w_ratio))
        if try_h > new_h:
            try_h = new_h
            try_w = int(try_h * (w_ratio / h_ratio))
        if try_w > new_w:
            try_w = new_w
            try_h = int(try_w * (h_ratio / w_ratio))
        new_w, new_h = try_w, try_h

        self.setFixedSize(QSize(new_w, new_h))

    def wheelEvent(self, event):
        event.ignore()

    def propagate_after_resize(self):
        self.video.update()
        self.image.update()
        self.text.update()
        self.marquee.update()
        self.setSceneRect(self.rect())
        self.centerOn(0, 0)
        self.resize_floatings()
