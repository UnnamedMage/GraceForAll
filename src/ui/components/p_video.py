from PySide6.QtCore import Qt, QUrl, QSizeF, Signal, QObject
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtMultimediaWidgets import QGraphicsVideoItem
from typing import Literal


class Signals(QObject):
    loaded = Signal()


class PVideo(QGraphicsVideoItem):
    """
    props:  Level, Source, Attributes
    """

    def __init__(self, parent):
        QGraphicsVideoItem.__init__(self)
        self.setParent(parent)
        self.initial_time = None
        self.player = QMediaPlayer()
        self.player.setVideoOutput(self)
        self.audio_output = QAudioOutput()
        self.player.setAudioOutput(self.audio_output)
        self.player.mediaStatusChanged.connect(self.delay_initial)
        self.setVisible(False)
        self.signals = Signals()
        self.audio_output.setMuted(True)

    def set_aspect_ratio_mode(self, value: Literal["keep", "ignore", "expand"]):
        match value:
            case "keep":
                self.setAspectRatioMode(Qt.KeepAspectRatio)
            case "ignore":
                self.setAspectRatioMode(Qt.IgnoreAspectRatio)
            case "expand":
                self.setAspectRatioMode(Qt.KeepAspectRatioByExpanding)

    def set_source(self, source: str):
        self.player.setSource(QUrl.fromLocalFile(source))

    def set_loop(self, loop: bool):
        self.player.setLoops(QMediaPlayer.Infinite if loop else 1)

    def set_state(self, state: Literal["play", "pause", "stop"]):
        match state:
            case "play":
                self.player.play()
            case "pause":
                self.player.pause()
            case "stop":
                self.player.stop()

    def set_initial_time(self, time: int):
        self.initial_time = time

    def delay_initial(self, status):
        if status == QMediaPlayer.MediaStatus.BufferedMedia and self.initial_time:
            self.player.setPosition(self.initial_time)
        if status in (
            QMediaPlayer.MediaStatus.BufferedMedia,
            QMediaPlayer.MediaStatus.LoadedMedia,
        ):
            self.signals.loaded.emit()

    def update(self):
        size = QSizeF(self.parent().size())
        self.setSize(size)
        self.setPos(0, 0)

    def setVisible(self, visible):
        if not visible:
            self.player.pause()
        super().setVisible(visible)
