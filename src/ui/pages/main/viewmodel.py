from ....Qtive.Managers import BaseVM
from PySide6.QtWidgets import QFileDialog
from PySide6.QtCore import QPoint
from src.core.factory import Factory
from ....common import get_platform_path
from ...utils.i18n.messages import MESSAGES
from ...utils.constants import (
    BG_EXTENSIONS,
    SLIDE_STYLE,
    IN_ANIMATIONS,
    OUT_ANIMATIONS,
    FAMILIES,
    BG_IMAGE_EXTENSIONS,
    BG_VIDEO_EXTENSIONS,
)
import unicodedata
import os
import shutil
from copy import deepcopy
from typing import Optional


class MainViewModel(BaseVM):
    def __init__(self, factory: Factory):
        super().__init__()
        self.song_service = factory.get_song_service()
        self.verse_service = factory.get_verse_service()
        self.schedule_service = factory.get_schedule_service()
        self.settings_service = factory.get_settings_service()

        self.register(
            "app",
            {
                "song_editor": str,
                "open_manager": (),
                "save_manager": dict,
                "settings_manager": (),
                "about": (),
            },
        )
        self.register(
            "window", {"move": QPoint, "close": (), "restore": (), "minimize": ()}
        )
        self.register("view", {"message": dict})

        self.vr = VerseRepertory(self)
        self.sr = SongRepertory(self)
        self.pc = PreviewController(self)
        self.ssc = SlideStyleController(self)
        self.sc = ScheduleController(self)
        self.ss = SelectionSection()
        self.oc = OnliveController(self)
        self.mr = MediaRepertory(self)

        self.vr.request.verse_selected.connect(self.pc.run)
        self.sr.request.song_selected.connect(self.pc.run)
        self.mr.request.media_selected.connect(self.pc.run)
        self.sc.request.element_selected.connect(self.pc.run)
        self.sc.request.element_selected.connect(self.ss.clean_sections)
        self.vr.request.verse_selected.connect(self.sc.set_ext_element)
        self.sr.request.song_selected.connect(self.sc.set_ext_element)
        self.mr.request.media_selected.connect(self.sc.set_ext_element)
        self.pc.request.send_state.connect(self.oc.run)
        self.ssc.request.ss_changed.connect(self.pc.update_slide_style)
        self.ssc.request.ss_changed.connect(self.oc.update_slide_style)
        self.ssc.request.message.connect(self.view.message.emit)
        self.sr.request.song_deleted.connect(self.change_in_a_song)
        self.sr.request.song_for_edit.connect(self.app.song_editor.emit)
        self.sr.request.message.connect(self.view.message.emit)

    def pv_init(self):
        self.ss.refresh()
        self.vr.refresh()
        self.sr.refresh()
        self.mr.refresh()
        self.ssc.refresh()
        self.sc.refresh()
        self.oc.refresh()
        self.pc.refresh()

    def on_start(self):
        self.oc.altern_secondary()

    def _message(self, title="", text="", callback=None):
        message = {
            "title": title,
            "message": text,
        }
        if callback:
            message.update({"mode": "confirmation", "callback": callback})
        self.view.message.emit(message)

    def save_schedule(self, save_as=False):
        if self.sc.is_empty():
            self._message(
                "Aviso", "El programa no contiene elementos asi que no se puede guardar"
            )
            return

        schedule = self.sc.get_schedule()
        request = {"action": "save_as" if save_as else "save", "payload": schedule}
        self.app.save_manager.emit(request)

    def _os_callback(self, b: bool):
        self.save_schedule() if b else self.app.open_manager.emit()

    def open_schedule(self):
        if self.sc.is_edited():
            self._message(
                "Antes de continuar",
                "Desea guardar el programa actual?",
                self._os_callback,
            )
            return
        self.app.open_manager.emit()

    def _ns_callback(self, b: bool):
        self.save_schedule() if b else self.sc.refresh()

    def new_schedule(self):
        if self.sc.is_edited():
            self._message(
                "Antes de continuar",
                "Desea guardar el programa actual?",
                self._ns_callback,
            )
            return
        self.sc.refresh()

    def change_in_a_song(self, task: dict):
        self.sc.task_with_song(task)
        self.oc.task_with_song(task)
        self.pc.task_with_song(task)
        self.sr.refresh()


class OnliveController(BaseVM):
    def __init__(self, parent_vm: MainViewModel):
        super().__init__()
        self.parent_vm = parent_vm
        self.register(
            "view",
            {
                "title": str,
                "lyrics": list,
                "focus": (object, object),
                "mode": int,
                "secondary": bool,
            },
        )
        self.register(
            "projector",
            {
                "bg": str,
                "attrs": dict,
                "s_attrs": dict,
                "text": (str, bool),
                "pos": int,
            },
        )
        self.register("alert", {"text": str, "deploy": ()})
        self.register(
            "player", {"range": dict, "time": str, "value": int, "volumen": int}
        )
        self.register(
            "btns",
            {
                "play": str,
                "mute": str,
                "black_attrs": dict,
                "bg_attrs": dict,
                "secondary_attrs": dict,
            },
        )
        self.BASE_STATE = {
            "slide_style": SLIDE_STYLE.copy(),
            "element": {},
            "text": "",
            "index": None,
            "lyrics": [],
            "duration": 0,
            "pos": None,
            "time": 0,
            "p_mode": "play",
            "volumen": 50,
            "mute": False,
            "task": None,
            "black": False,
            "only_bg": False,
            "alert_text": "",
            "secondary": False,
        }
        self.state = self.BASE_STATE.copy()
        self.projector.attrs.connect(self._attrs_filter)

    def dispatch(self, action: dict):
        old_state = deepcopy(self.state)
        new_state = self.reducer(deepcopy(self.state), action)
        if new_state:
            self.state = new_state
            self.emit_changes(old_state)

    def reducer(self, state, action) -> dict | None:
        type_ = action["type"]
        payload: dict = action.get("payload")

        if type_ == "BLANK":
            state["task"] = "blank"
            return state

        if type_ == "SET_STATE":
            state.update(payload)
            state["task"] = None
            return state

        if type_ == "SECONDARY_SWITCH":
            state["task"] = "secondary_switch"
            return state

        if type_ == "PLAY_PAUSE":
            state["p_mode"] = (
                "play" if state["p_mode"] in ("pause", "stop") else "pause"
            )
            state["task"] = "play"
            return state

        if type_ == "STOP":
            if state["p_mode"] == "stop":
                return
            state["p_mode"] = "stop"
            state["time"] = 0
            state["task"] = "stop"
            return state

        if type_ == "MUTE":
            state["mute"] = not state["mute"]
            state["task"] = "mute"
            return state

        if type_ == "BLACK":
            state["black"] = not state["black"]
            if not state["black"]:
                state["p_mode"] = "play"
            state["task"] = "black"
            return state

        if type_ == "ONLY_BG":
            state["only_bg"] = not state["only_bg"]
            state["task"] = "only_bg"
            return state

        if type_ == "MUTE":
            state["mute"] = not state["mute"]
            state["task"] = "mute"
            return state

        if type_ == "SECONDARY":
            state["secondary"] = payload
            state["task"] = "secondary"
            return state

        if type_ == "SET_PLAYER_ATTRS":
            key, value = payload
            state[key] = value
            state["task"] = key
            return state

        if type_ == "UPDATE_SLIDE_STYLE":
            ss = state["slide_style"]
            ss.update(payload)
            state["task"] = "update"
            return state

        if type_ == "SET_TEXT":
            state["index"] = payload
            state["text"] = state["lyrics"][payload]
            state["task"] = "text"
            return state

        if type_ == "ANNOUNCE":
            state["task"] = "announce"
            return state

        if type_ == "SET_ALERT_TEXT":
            state["alert_text"] = payload
            state["task"] = "none"
            return state

    def _attrs_filter(self, d: dict):
        alt_d = d.copy()
        element_type = self.state["element"].get("type")
        if element_type in ("verse", "song"):
            alt_d["mute"] = True
        else:
            alt_d["mute"] = self.state["mute"]
            alt_d["volume"] = self.state["volumen"]
        self.projector.s_attrs.emit(alt_d)

    def _update_time_label(self):
        position = self.state["time"] // 1000
        duration = self.state["duration"] // 1000
        self.player.time.emit(
            f"{position // 60:02}:{position % 60:02} / {duration // 60:02}:{duration % 60:02}"
        )

    def _show_text(self, text: str):
        if self.state["black"] or self.state["only_bg"]:
            self.projector.text.emit("", True)
            return
        self.projector.text.emit(text, True)

    def _first_text(self):
        new_element = self.state["element"]
        element_type = new_element.get("type")
        title = "En vivo"
        text = ""
        if element_type == "song":
            title = f"En vivo-{new_element['title']}"
            idx = self.state["index"]
            text = self.state["lyrics"][idx]
            self.view.focus.emit(idx, 0)
        elif element_type == "media":
            title = f"En vivo-{os.path.basename(new_element['slide_style']['bg_path'])}"
            text = ""
        elif element_type == "verse":
            title = f"En vivo-{new_element['citation']}"
            text = f"{new_element['text']}\n{new_element['citation']}"
        self.view.title.emit(title)
        self._show_text(text)

    def _change_state(self):
        type_ = self.state["element"].get("type")
        if type_ == "media":
            self.projector.pos.emit(self.state["time"])
            attr = {
                "state": self.state["p_mode"],
                "initial_time": 0,
            }
            self.projector.attrs.emit(attr)
            self.btns.play.emit(
                "pause.svg" if self.state["p_mode"] == "play" else "play.svg"
            )
            self.player.volumen.emit(self.state["volumen"])
            self.btns.mute.emit("mute.svg" if self.state["mute"] else "on.svg")
        elif self.state["lyrics"] != []:
            self._show_text(self.state["lyrics"][self.state["index"]])
            self.view.focus.emit(self.state["index"], 0)

    def _change_bg(self, last_element, force: bool = False):
        if bg := self.state["element"]["slide_style"].get("bg_path"):
            new_bg = str(bg)
        else:
            new_bg = self.state["slide_style"]["bg_path"]

        if last_element != {}:
            last_bg = last_element["slide_style"].get("bg_path")
            if last_bg == new_bg and not force:
                return

        if not os.path.exists(new_bg):
            self.projector.bg.emit("")
            return

        element_type = self.state["element"]["type"]
        _, ext = os.path.splitext(new_bg)

        if ext.lower() in BG_IMAGE_EXTENSIONS:
            attr = {
                "aspect_ratio": "keep" if element_type == "media" else "expand",
            }
            self.projector.attrs.emit(attr)
            self.projector.bg.emit(new_bg)
            self.projector.bg.emit("") if self.state["black"] else None
            self.view.mode.emit(0)
        elif ext.lower() in BG_VIDEO_EXTENSIONS:
            attr = {
                "aspect_ratio": "keep" if element_type == "media" else "expand",
                "loop": False if element_type == "media" else True,
                "state": self.state["p_mode"] if not self.state["black"] else "pause",
                "initial_time": self.state["time"],
            }
            self.projector.bg.emit(new_bg)
            self.projector.attrs.emit(attr)
            self.projector.bg.emit("") if self.state["black"] else None

            self.btns.play.emit("pause.svg")
            self.view.mode.emit(1 if element_type == "media" else 0)

            self.btns.play.emit(
                "pause.svg"
                if self.state["p_mode"] == "play" and not self.state["black"]
                else "play.svg"
            )
            self.view.mode.emit(1 if element_type == "media" else 0)

            self.player.volumen.emit(
                self.state["volumen"]
            ) if element_type == "media" else None
            self.btns.mute.emit(
                "mute.svg" if self.state["mute"] else "on.svg"
            ) if element_type == "media" else None

    def emit_changes(self, old_state):
        if task := self.state.get("task"):
            if task == "time":
                self._update_time_label()
                self.player.value.emit(self.state["time"])
                if self.state["time"] == self.state["duration"]:
                    self.btns.play.emit("play.svg")
            elif task == "pos":
                self.projector.pos.emit(self.state["pos"])
                self.state["pos"] = None
            elif task == "duration":
                self._update_time_label()
                self.player.range.emit({"range": (0, self.state["duration"])})
            elif task == "mute":
                self.btns.mute.emit("mute.svg" if self.state["mute"] else "on.svg")
                self.projector.s_attrs.emit({"mute": self.state["mute"]})
            elif task == "play":
                self.btns.play.emit(
                    "play.svg" if self.state["p_mode"] == "pause" else "pause.svg"
                )
                self.projector.attrs.emit({"state": self.state["p_mode"]})
            elif task == "stop":
                self.btns.play.emit("play.svg")
                self.projector.attrs.emit(
                    {"state": self.state["p_mode"], "initial_time": self.state["time"]}
                )
            elif task == "volumen":
                self.projector.s_attrs.emit({"volume": self.state["volumen"]})
            elif task == "secondary_switch":
                self.view.secondary.emit(not self.state["secondary"])
            elif task == "text":
                self._show_text(self.state["text"])
                self.state["text"] = ""
            elif task == "announce":
                if self.state["alert_text"] == "":
                    self.state["task"] = None
                    return
                self.projector.text.emit(self.state["alert_text"], False)
                self.state["alert_text"] = ""
                self.alert.text.emit("")
            elif task == "black":
                if self.state["black"]:
                    self.projector.text.emit("", True)
                    self.projector.bg.emit("")
                    self.btns.play.emit("play.svg")
                    self.btns.black_attrs.emit({"checked": True})
                    self.state["task"] = None
                    return

                self.btns.black_attrs.emit({"checked": False})

                if self.state["element"] == {}:
                    self.state["task"] = None
                    return

                if bg := self.state["element"]["slide_style"].get("bg_path"):
                    new_bg = str(bg)
                else:
                    new_bg = self.state["slide_style"]["bg_path"]

                if not os.path.exists(new_bg):
                    self.projector.bg.emit("")
                else:
                    _, ext = os.path.splitext(new_bg)
                    self.projector.bg.emit("_show")
                    if ext.lower() in BG_VIDEO_EXTENSIONS:
                        self.btns.play.emit("pause.svg")
                        self.projector.attrs.emit({"state": self.state["p_mode"]})
                self._first_text()
            elif task == "only_bg":
                if self.state["only_bg"]:
                    self.projector.text.emit("", True)
                    self.btns.bg_attrs.emit({"checked": True})
                    self.state["task"] = None
                    return

                self.btns.bg_attrs.emit({"checked": False})

                if self.state["element"] == {}:
                    self.state["task"] = None
                    return

                self._first_text()
            elif task == "secondary":
                if self.state["secondary"]:
                    self.btns.secondary_attrs.emit({"checked": True})
                    self.state["task"] = None
                    return
                self.btns.secondary_attrs.emit({"checked": False})
            elif task == "blank":
                self.projector.text.emit("", True)
                self.projector.bg.emit("")
                self.view.mode.emit(0)
                self.view.title.emit("En vivo")
                self.view.lyrics.emit([])
                self.btns.mute.emit("mute.svg" if self.state["mute"] else "on.svg")
                self.player.volumen.emit(self.state["volumen"])
            elif task == "update":
                if self.state["element"] == {}:
                    self.state["task"] = None
                    return

                new_element = self.state["element"]

                style: dict = self.state["slide_style"] | new_element.get("slide_style")
                style.update({"immediate": True})
                if not new_element["slide_style"].get("bg_path"):
                    style["color"] = self.state["slide_style"]["color"]
                self.projector.attrs.emit({"slide_style": style})

                if new_element["slide_style"].get("bg_path") is None:
                    self._change_bg(old_state["element"], True)
            self.state["task"] = None
            return

        last_element = old_state["element"]
        new_element = self.state["element"]
        if last_element == new_element:
            self._change_state()
            return

        if not (last_element.get("type") == "verse" and new_element["type"] == "verse"):
            self.projector.text.emit("", True)

        self._change_bg(last_element)

        style: dict = self.state["slide_style"] | new_element.get("slide_style")
        style.update({"immediate": False})
        if not new_element["slide_style"].get("bg_path"):
            style["color"] = self.state["slide_style"]["color"]
        self.projector.attrs.emit({"slide_style": style})

        self.view.lyrics.emit([[lyric] for lyric in self.state["lyrics"]])

        self._first_text()

    def set_attr_player(self, key, value):
        self.dispatch({"type": "SET_PLAYER_ATTRS", "payload": (key, value)})

    def change_play(self):
        self.dispatch({"type": "PLAY_PAUSE"})

    def set_stop(self):
        self.dispatch({"type": "STOP"})

    def change_mute(self):
        self.dispatch({"type": "MUTE"})

    def change_text(self, coord):
        self.dispatch({"type": "SET_TEXT", "payload": coord[0]})

    def set_alert_text(self, text):
        self.dispatch({"type": "SET_ALERT_TEXT", "payload": text})

    def emit_announce(self, any):
        self.dispatch({"type": "ANNOUNCE"})

    def change_only_bg(self):
        self.dispatch({"type": "ONLY_BG"})

    def change_black(self):
        self.dispatch({"type": "BLACK"})

    def altern_secondary(self):
        self.dispatch({"type": "SECONDARY_SWITCH"})

    def set_secondary(self, b):
        self.dispatch({"type": "SECONDARY", "payload": b})

    def run(self, state: dict):
        self.dispatch({"type": "SET_STATE", "payload": state})

    def update_slide_style(self, update):
        self.dispatch({"type": "UPDATE_SLIDE_STYLE", "payload": update})

    def task_with_song(self, info: dict):
        if self.state["element"] == {}:
            return

        if self.state["element"].get("type") != "song":
            return

        if info["action"] == "added":
            return

        if info["data"]["id"] != self.state["element"]["id"]:
            return

        if info["action"] == "deleted":
            self.dispatch({"type": "BLANK"})
        elif info["action"] == "updated":
            self.dispatch({"type": "BLANK"})

    def refresh(self):
        self.dispatch({"type": "BLANK"})


class PreviewController(BaseVM):
    def __init__(self, parent_vm: MainViewModel):
        super().__init__()
        self.parent_vm = parent_vm
        self.register("request", {"send_state": dict})
        self.register(
            "view",
            {"title": str, "lyrics": list, "mode": int},
        )
        self.register("projector", {"bg": str, "attrs": dict, "text": str, "pos": int})
        self.register(
            "player", {"range": dict, "time": str, "value": int, "volumen": int}
        )
        self.register("btns", {"play": str, "mute": str})
        self.BASE_STATE = {
            "slide_style": SLIDE_STYLE.copy(),
            "element": {},
            "text": "",
            "index": None,
            "lyrics": [],
            "duration": 0,
            "pos": None,
            "time": 0,
            "p_mode": "play",
            "volumen": 50,
            "mute": False,
            "task": None,
        }
        self.state = self.BASE_STATE.copy()

    def dispatch(self, action: dict):
        old_state = deepcopy(self.state)
        new_state = self.reducer(deepcopy(self.state), action)
        if new_state:
            self.state = new_state
            self.emit_changes(old_state)

    def reducer(self, state, action) -> dict | None:
        type_ = action["type"]
        payload: dict = action.get("payload")

        if type_ == "BLANK":
            state["task"] = "blank"
            return state

        if type_ == "SET_ELEMENT":
            if state["element"] == payload:
                return None
            state["element"] = payload.copy()
            state["lyrics"] = payload.get("lyrics", [])
            state["index"] = 0 if state["lyrics"] != [] else None
            return state

        if type_ == "SEND_TO_ONLIVE":
            state["task"] = "send"
            return state

        if type_ == "PLAY_PAUSE":
            state["p_mode"] = (
                "play" if state["p_mode"] in ("pause", "stop") else "pause"
            )
            state["task"] = "play"
            return state

        if type_ == "STOP":
            if state["p_mode"] == "stop":
                return
            state["p_mode"] = "stop"
            state["task"] = "stop"
            return state

        if type_ == "MUTE":
            state["mute"] = not state["mute"]
            state["task"] = "mute"
            return state

        if type_ == "SET_PLAYER_ATTRS":
            key, value = payload
            state[key] = value
            state["task"] = key
            return state

        if type_ == "UPDATE_SLIDE_STYLE":
            ss = state["slide_style"]
            ss.update(payload)
            state["task"] = "update"
            return state

        if type_ == "SET_TEXT":
            state["index"] = payload
            state["text"] = state["lyrics"][payload]
            state["task"] = "text"
            return state

    def _update_time_label(self):
        position = self.state["time"] // 1000
        duration = self.state["duration"] // 1000
        self.player.time.emit(
            f"{position // 60:02}:{position % 60:02} / {duration // 60:02}:{duration % 60:02}"
        )

    def _change_bg(self, last_element, force: bool = False):
        if bg := self.state["element"]["slide_style"].get("bg_path"):
            new_bg = str(bg)
        else:
            new_bg = self.state["slide_style"]["bg_path"]

        if last_element != {}:
            last_bg = last_element["slide_style"].get("bg_path")
            if last_bg == new_bg and not force:
                return

        if not os.path.exists(new_bg):
            self.projector.bg.emit("")
            return

        element_type = self.state["element"]["type"]
        _, ext = os.path.splitext(new_bg)

        if ext.lower() in BG_IMAGE_EXTENSIONS:
            attr = {
                "aspect_ratio": "keep" if element_type == "media" else "expand",
            }
            self.projector.attrs.emit(attr)
            self.projector.bg.emit(new_bg)
            self.view.mode.emit(0)
        elif ext.lower() in BG_VIDEO_EXTENSIONS:
            attr = {
                "aspect_ratio": "keep" if element_type == "media" else "expand",
                "loop": False if element_type == "media" else True,
                "state": "play",
            }
            self.state["p_mode"] = "play"
            self.btns.play.emit("pause.svg")
            self.projector.bg.emit(new_bg)
            self.projector.attrs.emit(attr)
            self.view.mode.emit(1 if element_type == "media" else 0)

    def emit_changes(self, old_state):
        if task := self.state.get("task"):
            if task == "time":
                self._update_time_label()
                self.player.value.emit(self.state["time"])
                self.state["task"] = None
                if self.state["time"] == self.state["duration"]:
                    self.btns.play.emit("play.svg")
                return
            elif task == "pos":
                self.projector.pos.emit(self.state["pos"])
                self.state["pos"] = None
                self.state["task"] = None
                return
            elif task == "duration":
                self._update_time_label()
                self.player.range.emit({"range": (0, self.state["duration"])})
                self.state["task"] = None
                return
            elif task == "mute":
                self.btns.mute.emit("mute.svg" if self.state["mute"] else "on.svg")
                self.state["task"] = None
                return
            elif task == "play":
                self.btns.play.emit(
                    "play.svg" if self.state["p_mode"] == "pause" else "pause.svg"
                )
                self.projector.attrs.emit({"state": self.state["p_mode"]})
                self.state["task"] = None
                return
            elif task == "stop":
                self.btns.play.emit("play.svg")
                self.projector.attrs.emit({"state": self.state["p_mode"]})
                self.state["task"] = None
                return
            elif task == "send":
                self.request.send_state.emit(self.state.copy())
                self.state["task"] = None
                return
            elif task == "text":
                self.projector.text.emit(self.state["text"])
                self.state["text"] = ""
                self.state["task"] = None
            elif task == "blank":
                self.projector.text.emit("")
                self.projector.bg.emit("")
                self.view.mode.emit(0)
                self.view.title.emit("Prevista")
                self.view.lyrics.emit([])
                self.btns.mute.emit("mute.svg" if self.state["mute"] else "on.svg")
                self.player.volumen.emit(self.state["volumen"])
                self.state["task"] = None
                return
            elif task == "update":
                if self.state["element"] == {}:
                    self.state["task"] = None
                    return

                new_element = self.state["element"]

                style: dict = self.state["slide_style"] | new_element.get("slide_style")
                style.update({"immediate": True})
                if not new_element["slide_style"].get("bg_path"):
                    style["color"] = self.state["slide_style"]["color"]
                self.projector.attrs.emit({"slide_style": style})

                if new_element["slide_style"].get("bg_path") is None:
                    self._change_bg(old_state["element"], True)

                self.state["task"] = None
                return

        last_element = old_state["element"]
        new_element = self.state["element"]
        if last_element == new_element:
            return

        if not (last_element.get("type") == "verse" and new_element["type"] == "verse"):
            self.projector.text.emit("")

        self._change_bg(last_element)

        style: dict = self.state["slide_style"] | new_element.get("slide_style")
        style.update({"immediate": False})
        if not new_element["slide_style"].get("bg_path"):
            style["color"] = self.state["slide_style"]["color"]
        self.projector.attrs.emit({"slide_style": style})

        self.view.lyrics.emit([[lyric] for lyric in self.state["lyrics"]])

        element_type = new_element.get("type")
        if element_type == "song":
            self.view.title.emit(f"Prevista-{new_element['title']}")
            self.projector.text.emit(self.state["lyrics"][0])
        elif element_type == "media":
            self.view.title.emit(
                f"Prevista-{os.path.basename(new_element['slide_style']['bg_path'])}"
            )
            self.projector.text.emit("")
        elif element_type == "verse":
            self.view.title.emit(f"Prevista-{new_element['citation']}")
            text = f"{new_element['text']}\n{new_element['citation']}"
            self.projector.text.emit(text)

    def set_attr_player(self, key, value):
        self.dispatch({"type": "SET_PLAYER_ATTRS", "payload": (key, value)})

    def change_play(self):
        self.dispatch({"type": "PLAY_PAUSE"})

    def set_stop(self):
        self.dispatch({"type": "STOP"})

    def change_mute(self):
        self.dispatch({"type": "MUTE"})

    def change_text(self, coord):
        self.dispatch({"type": "SET_TEXT", "payload": coord[0]})

    def run(self, element: dict):
        self.dispatch({"type": "SET_ELEMENT", "payload": element})

    def send_to_live(self, coord):
        self.dispatch({"type": "SEND_TO_ONLIVE"})

    def update_slide_style(self, update):
        self.dispatch({"type": "UPDATE_SLIDE_STYLE", "payload": update})

    def task_with_song(self, info: dict):
        if self.state["element"] == {}:
            return

        if self.state["element"].get("type") != "song":
            return

        if info["action"] == "added":
            return

        if info["data"]["id"] != self.state["element"]["id"]:
            return

        if info["action"] == "deleted":
            self.dispatch({"type": "BLANK"})
        elif info["action"] == "updated":
            self.dispatch({"type": "SET_ELEMENT", "payload": info["data"]})

    def refresh(self):
        self.dispatch({"type": "BLANK"})


class SlideStyleController(BaseVM):
    def __init__(self, parent_vm: MainViewModel):
        super().__init__()
        self.settings_service = parent_vm.settings_service
        self.bg_folder = str(get_platform_path("appdata", "backgrounds"))
        self.register("request", {"ss_changed": dict, "message": dict})
        self.register("view", {"menu": ()})
        self.register("font", {"family_index": int, "factor_index": int})
        self.register("style", {"italic": dict, "bold": dict})
        self.register("color", {"black": dict, "white": dict})
        self.register("v_align", {"vcenter": dict, "top": dict, "bottom": dict})
        self.register("h_align", {"hcenter": dict, "left": dict, "right": dict})
        self.register("animation", {"in_index": int, "out_index": int})
        self.register("bg", {"items": list, "menu": ()})
        self.state = {
            "slide_style": SLIDE_STYLE.copy(),
            "change": None,
            "bg_list": [],
            "message": None,
        }

    def dispatch(self, action: dict):
        old_state = deepcopy(self.state)
        new_state = self.reducer(deepcopy(self.state), action)
        if new_state:
            self.state = new_state
            self.emit_changes(old_state)

    def _create_bg_list(self):
        pathes = []
        for file in os.listdir(self.bg_folder):
            full_path = os.path.join(self.bg_folder, file)
            if os.path.isfile(full_path):
                _, extension = os.path.splitext(file)
                if extension.lower() in BG_EXTENSIONS:
                    pathes.append(full_path)
        return pathes

    def reducer(self, state, action) -> dict | None:
        type_ = action["type"]
        payload: dict = action.get("payload")

        if type_ == "SET_SLIDE_STYLE":
            ss = state["slide_style"]
            ss.update(payload)
            state["change"] = payload
            return state

        if type_ == "SET_ATTRIBUTE":
            ss = state["slide_style"]
            items = payload.copy().items()
            for key, value in items:
                if key in ("italic", "bold"):
                    payload[key] = not ss[key]
                if ss[key] == value:
                    payload.pop(key)

            if payload == {}:
                return None

            ss.update(payload)
            state["change"] = payload
            return state

        if type_ == "REFRESH_BG_LIST":
            state["bg_list"] = self._create_bg_list()
            return state

        if type_ == "ADD_NEW_BG":
            media_path, _ = QFileDialog.getOpenFileName(
                None,
                "Seleccionar Multimedia",
                "",
                "Multimedia (*.png *.jpg *.jpeg *.bmp *.gif *.webp *.mp4 *.avi *.mkv *.mov *.wmv)",
            )
            folder = self.bg_folder
            if media_path:
                media_name = os.path.basename(media_path)
                destiny = os.path.join(folder, media_name)

                max_try = 4

                if os.path.exists(destiny):
                    base, ext = os.path.splitext(media_name)
                    i = 1
                    while os.path.exists(os.path.join(folder, f"{base}_{i}{ext}")):
                        i += 1
                        if i == max_try:
                            state["message"] = ("Error", "bg.transfer_failed")
                            return state
                    destiny = os.path.join(folder, f"{base}_{i}{ext}")

                try:
                    shutil.copy(media_path, destiny)
                except Exception:
                    state["message"] = ("Error", "bg.transfer_failed")
                    return state

                state["bg_list"] = self._create_bg_list()
                state["message"] = ("Tarea completada", "bg.transfer_completed")
                return state
            return None

    def _notification(self, title: str, code: str):
        self.request.message.emit(
            {
                "title": title,
                "message": MESSAGES[code],
            }
        )

    def _change_view(self, key, value):
        if key == "family":
            self.font.family_index.emit(FAMILIES.index(value))
        elif key == "italic":
            self.style.italic.emit({"checked": value})
        elif key == "bond":
            self.style.bold.emit({"checked": value})
        elif key == "color":
            self.color.black.emit({"checked": value == "black"})
            self.color.white.emit({"checked": value == "white"})
        elif key == "v_align":
            self.v_align.vcenter.emit({"checked": value == "vcenter"})
            self.v_align.top.emit({"checked": value == "top"})
            self.v_align.bottom.emit({"checked": value == "bottom"})
        elif key == "h_align":
            self.h_align.hcenter.emit({"checked": value == "hcenter"})
            self.h_align.left.emit({"checked": value == "left"})
            self.h_align.right.emit({"checked": value == "right"})
        elif key == "in_animation":
            self.animation.in_index.emit(IN_ANIMATIONS.index(value))
        elif key == "out_animation":
            self.animation.out_index.emit(OUT_ANIMATIONS.index(value))

    def emit_changes(self, old_state):
        old_list = old_state["bg_list"]
        new_list = self.state["bg_list"]

        if old_list != new_list:
            self.bg.items.emit(new_list)

        if message := self.state["message"]:
            self._notification(*message)
            self.state["message"] = None

        if not (change := self.state["change"]):
            return

        self.settings_service.set_defautl_slide_style(self.state["slide_style"])
        self.request.ss_changed.emit(change.copy())

        for key, value in change.items():
            self._change_view(key, value)

        self.state["change"] = None

    def set_attribute(self, key, value):
        self.dispatch({"type": "SET_ATTRIBUTE", "payload": {key: value}})

    def refresh_menu(self):
        self.dispatch({"type": "REFRESH_BG_LIST"})

    def add_bg(self):
        self.dispatch({"type": "ADD_NEW_BG"})

    def refresh(self):
        self.dispatch({"type": "REFRESH_BG_LIST"})
        response = self.settings_service.get_default_slide_style()

        ss = response["data"] if response["success"] else SLIDE_STYLE.copy()

        if not ss.get("bg_path", None):
            ss["bg_path"] = self.state["bg_list"][0]

        if not os.path.exists(ss["bg_path"]):
            ss["bg_path"] = self.state["bg_list"][0]

        self.dispatch({"type": "SET_SLIDE_STYLE", "payload": ss})


class ScheduleController(BaseVM):
    def __init__(self, parent_vm: MainViewModel):
        super().__init__()
        self.schedule_service = parent_vm.schedule_service
        self.register("request", {"element_selected": dict})
        self.register(
            "schedule_list", {"name": str, "items": list, "index": (object, object)}
        )
        self.register("btns", {"up": dict, "down": dict, "add": dict, "remove": dict})
        self.BASE_STATE = {
            "name": None,
            "items": [],
            "index": None,
            "ext": None,
            "edited": False,
        }
        self.state = self.BASE_STATE.copy()

    def dispatch(self, action: dict):
        old_state = deepcopy(self.state)
        new_state = self.reducer(deepcopy(self.state), action)
        if new_state:
            self.state = new_state
            self.emit_changes(action, old_state)

    def _is_edited(self, s: dict):
        response = self.schedule_service.verify_changes(s.copy())
        return response["success"]

    def reducer(self, state, action) -> dict | None:
        type_ = action["type"]
        payload = action.get("payload")

        if type_ == "SET_SCHEDULE":
            state["id"] = payload.get("id")
            state["items"] = payload.get("items", [])
            state["name"] = payload.get("name")
            state["index"] = None
            state["edited"] = False
            return state

        if type_ == "SET_EXT_ELEMENT":
            state["ext"] = payload
            state["index"] = None
            return state

        if type_ == "ADD_ELEMENT":
            ext = state["ext"]
            if not ext:
                return None
            items: list = state["items"]
            items.append(ext.copy())
            state["ext"] = None
            state["edited"] = self._is_edited(state)
            return state

        if type_ == "DELETE_ELEMENT":
            idx = state["index"]
            if idx is None:
                return None

            items = state["items"]
            if items == []:
                return None

            items = state["items"]
            items.pop(idx)
            state["index"] = 0 if items != [] else None
            state["edited"] = self._is_edited(state)
            return state

        if type_ == "MOVE_UP":
            idx = state["index"]
            if idx is None:
                return None

            if idx == 0:
                return None

            items = state["items"]
            items[idx - 1], items[idx] = items[idx], items[idx - 1]
            state["index"] = idx - 1
            state["edited"] = self._is_edited(state)
            return state

        if type_ == "MOVE_DOWN":
            idx = state["index"]
            if idx is None:
                return None

            items: list = state["items"]
            if idx == len(items) - 1:
                return None

            items[idx], items[idx + 1] = items[idx + 1], items[idx]
            state["index"] = idx + 1
            state["edited"] = self._is_edited(state)
            return state

        if type_ == "SELECT_ELEMENT":
            state["index"] = payload
            return state

        if type_ == "CHANGE_IN_SONG":
            items = state["items"]
            if items == []:
                return None

            if payload["action"] == "added":
                return None

            check = []
            for n, i in enumerate(items):
                if i["type"] in ("media", "verse"):
                    continue
                if i["id"] != payload["data"]["id"]:
                    continue
                check.append(n)

            if not check:
                return None

            for n in sorted(check, reverse=True):
                if payload["action"] == "deleted":
                    items.pop(n)
                elif payload["action"] == "updated":
                    items[n] = payload["data"].copy()

            return state

    def _formated_items(self):
        elements = []
        for item in self.state["items"]:
            element_type = item["type"]
            if element_type == "song":
                tag_type = "Cancion"
                tag_name = item["title"]
            elif element_type == "media":
                tag_type = "Media"
                tag_name = os.path.basename(item["slide_style"]["bg_path"])
            elif element_type == "verse":
                tag_type = "Versiculo"
                tag_name = item["citation"]
            element = [tag_type, tag_name]
            elements.append(element)
        return elements

    def _formated_name(self):
        if name := self.state.get("name"):
            text = f"Programa-{name}*" if self.state["edited"] else f"Programa-{name}"
        else:
            text = (
                "Programa-Aun sin guardar*" if self.state["items"] != [] else "Programa"
            )
        return text

    def emit_changes(self, action, old_state):
        type_ = action["type"]

        if self.state["index"] is None:
            attrs = {"disabled": True}
        else:
            attrs = {"disabled": False}

        self.btns.up.emit(attrs)
        self.btns.down.emit(attrs)
        self.btns.remove.emit(attrs)

        if type_ not in ("SELECT_ELEMENT", "SET_EXT_ELEMENT"):
            self.schedule_list.items.emit(self._formated_items())

        if self.state["ext"]:
            self.btns.add.emit({"disabled": False})
        else:
            self.btns.add.emit({"disabled": True})

        if (
            self.state["edited"] != old_state["edited"]
            or self.state["name"] != old_state["name"]
            or self.state["name"] is None
        ):
            self.schedule_list.name.emit(self._formated_name())

        if type_ == "MOVE_UP" or type_ == "MOVE_DOWN":
            self.schedule_list.index.emit(self.state["index"], 0)
        elif type_ == "SET_EXT_ELEMENT":
            self.schedule_list.index.emit(None, None)
        elif type_ == "DELETE_ELEMENT":
            if self.state["items"] != []:
                self.schedule_list.index.emit(0, 0)
        elif type_ == "SELECT_ELEMENT":
            self.request.element_selected.emit(self.state["items"][self.state["index"]])
        elif type_ == "ADD_ELEMENT":
            if self.state["index"]:
                self.schedule_list.index.emit(self.state["index"], 0)

    def move_up(self):
        self.dispatch({"type": "MOVE_UP"})

    def move_down(self):
        self.dispatch({"type": "MOVE_DOWN"})

    def delete(self):
        self.dispatch({"type": "DELETE_ELEMENT"})

    def add(self):
        self.dispatch({"type": "ADD_ELEMENT"})

    def select(self, coord):
        self.dispatch({"type": "SELECT_ELEMENT", "payload": coord[0]})

    def set_schedule(self, sdl):
        self.dispatch({"type": "SET_SCHEDULE", "payload": sdl})

    def set_ext_element(self, el):
        self.dispatch({"type": "SET_EXT_ELEMENT", "payload": el})

    def get_schedule(self):
        return self.state.copy()

    def task_with_song(self, info: dict):
        self.dispatch({"type": "CHANGE_IN_SONG", "payload": info})

    def change_in_schedule(self, info: dict):
        if not self.state.get("id"):
            return

        if self.state["id"] == info["data"]["id"]:
            new = self.BASE_STATE.copy()
            new.update({"ext": self.state["ext"]})
            self.set_schedule(new)

    def refresh(self):
        self.set_schedule(self.BASE_STATE.copy())

    def is_empty(self):
        return self.state["items"] == []

    def is_edited(self):
        return self.state["edited"]


class SelectionSection(BaseVM):
    def __init__(self):
        super().__init__()
        self.register("section", {"index": int})
        self.register("song", {"index": (object, object), "btn_attrs": dict})
        self.register("verse", {"index": (object, object), "btn_attrs": dict})
        self.register("media", {"btn_attrs": dict})
        self.state = {}

    def dispatch(self, action: dict):
        old_state = deepcopy(self.state)
        new_state = self.reducer(deepcopy(self.state), action)
        if new_state:
            self.state = new_state
            self.emit_changes(old_state)

    def reducer(self, state, action) -> dict | None:
        type_ = action["type"]
        payload = action.get("payload")

        if type_ == "CHANGE_SECTION":
            ss = state.get("selected_section")
            if ss == payload:
                return None
            sections = ["song", "verse", "media"]
            state["selected_section"] = payload
            for i, section in enumerate(sections):
                state[section] = True if i == payload else False
            return state

        if type_ == "CLEAR_SECTIONS":
            sections = ["song", "verse", "media"]
            for section in sections:
                state[section] = False
            return state

    def emit_changes(self, old_state):
        new_ss = self.state["selected_section"]
        old_ss = old_state.get("selected_section")
        self.section.index.emit(new_ss)

        sections = ["song", "verse", "media"]
        for i, sect in enumerate(sections):
            section = getattr(self, sect)
            if hasattr(section, "index") and not self.state[sect]:
                section.index.emit(None, None)

            if old_ss != new_ss:
                section.btn_attrs.emit({"checked": self.state["selected_section"] == i})

    def refresh(self):
        self.dispatch({"type": "CHANGE_SECTION", "payload": 0})

    def change_section(self, section: int):
        self.dispatch({"type": "CHANGE_SECTION", "payload": section})

    def clean_sections(self, *args):
        self.dispatch({"type": "CLEAR_SECTIONS"})


class SongRepertory(BaseVM):
    def __init__(self, parent_vm: MainViewModel):
        super().__init__()
        self.song_service = parent_vm.song_service
        self.register(
            "request",
            {
                "song_selected": dict,
                "song_for_edit": str,
                "message": dict,
                "song_deleted": dict,
            },
        )
        self.register("search", {"text": str})
        self.register("song_list", {"items": list, "filter": str, "menu": dict})
        self.songs = []

    def refresh(self):
        self.search.text.emit("")
        self.song_list.filter.emit("")
        response = self.song_service.get_all()
        self.songs = response["data"]
        self.song_list.items.emit([[song["title"]] for song in self.songs])

    def menu_song(self, data: dict):
        coord = data["coord"]
        song_selected = self.songs[coord[0]]

        def chose(index):
            if index == 0:
                self.request.song_for_edit.emit(song_selected["id"])
            elif index == 1:
                self.delete_song(song_selected)

        self.song_list.menu.emit({"callback": chose, "pos": data["pos"]})

    def delete_song(self, song):
        def chose(b: bool):
            if not b:
                return
            response = self.song_service.delete({"id": song["id"]})
            if response["success"]:
                self.request.message.emit(
                    {
                        "title": "Tarea completada",
                        "message": MESSAGES[response["code"]],
                    }
                )
                self.request.song_deleted.emit(
                    {"action": "deleted", "data": song.copy()}
                )

        self.request.message.emit(
            {
                "title": "Antes de continuar",
                "message": "Esta seguro de eliminar la cancion?",
                "mode": "confirmation",
                "callback": chose,
            }
        )

    def select_song(self, coord: tuple):
        index = coord[0]
        song = self.songs[index]
        song.update({"type": "song"})
        self.request.song_selected.emit(song.copy())


class VerseRepertory(BaseVM):
    def __init__(self, parent_vm: MainViewModel):
        super().__init__()
        self.verse_service = parent_vm.verse_service
        self.settings_service = parent_vm.settings_service
        self.register("request", {"verse_selected": dict})
        self.register("search", {"attrs": dict, "text": str})
        self.register(
            "bible_selector", {"avalible_items": list, "menu": dict, "version": str}
        )
        self.register("verses", {"items": list, "filter": str})
        self.bibles: list[dict] = []
        self.bible_selected: Optional[dict] = None
        self.book_names: list[str] = []
        self.norm_book_names: list[str] = []
        self.selected_book_verses: list[dict] = []
        self.selected_book_name = ""

    def _normalize_text(self, text: str):
        return (
            unicodedata.normalize("NFKD", text)
            .encode("ASCII", "ignore")
            .decode("utf-8")
            .lower()
        )

    def set_bible(self):
        self.book_names = self.verse_service.get_book_names_list(
            self.bible_selected["version"].rsplit("_", 1)[-1]
        )
        self.norm_book_names = [self._normalize_text(book) for book in self.book_names]
        self.search.attrs.emit({"completer": self.book_names})
        self.bible_selector.version.emit(self.bible_selected["version"])

    def update_verses(self):
        self.selected_book_verses = self.verse_service.get_book(
            dict(version=self.bible_selected["version"], name=self.selected_book_name)
        )
        self.verses.items.emit(
            [[verse["citation"], verse["text"]] for verse in self.selected_book_verses]
        )

    def set_book(self, name: str):
        if name not in self.book_names:
            return
        self.selected_book_name = name
        self.update_verses()

    def refresh(self):
        self.bibles = self.verse_service.get_all_bibles()

        if not self.bibles:
            return

        self.bibles.sort(key=lambda bible: bible["version"])

        response = self.settings_service.get_default_bible()
        if response["success"] and response["data"] in self.bibles:
            self.bible_selected = response["data"]
        else:
            self.bible_selected = self.bibles[0]
            self.settings_service.set_defautl_bible(self.bible_selected)

        self.set_bible()
        self.set_book(self.book_names[0])

    def looking_for_verse(self, text: str):
        norm_text = self._normalize_text(text)
        if norm_text in self.norm_book_names:
            book = self.book_names[self.norm_book_names.index(norm_text)]
            if book != self.selected_book_name:
                self.set_book(book)
            if text != book:
                self.search.text.emit(book)
                text = book
        self.verses.filter.emit(text)

    def version_for_select(self):
        avalible_bibles = [b for b in self.bibles if b != self.bible_selected]
        avalible_version = [b["version"] for b in avalible_bibles]

        def chose(index):
            self.bible_selected = avalible_bibles[index]
            self.set_bible()
            self.update_verses()

        self.bible_selector.avalible_items.emit(avalible_version)
        self.bible_selector.menu.emit({"callback": chose})

    def select_verse(self, coord: tuple):
        index = coord[0]
        verse = self.selected_book_verses[index]

        text_in_projection = f"{verse['text']}\n{verse['citation']}"
        length = max(40, min(len(text_in_projection), 480))
        normalized = (length - 30) / (480 - 30)
        factor = 5 - (normalized * 4)

        verse_formated = dict(
            type="verse",
            slide_style={"factor": factor},
        )
        verse_formated.update(verse)
        self.request.verse_selected.emit(verse_formated)


class MediaRepertory(BaseVM):
    def __init__(self, parent_vm: MainViewModel):
        super().__init__()
        self.settings_service = parent_vm.settings_service
        self.register("request", {"media_selected": dict})
        self.register("media", {"items": list})
        self.media_folder: Optional[str] = None

    def refresh(self):
        if not self.media_folder:
            response = self.settings_service.get_default_media_folder()
            if response["success"]:
                self.media_folder = response["data"]
        self.set_media()

    def change_media_folder(self):
        inital_dir = os.path.expanduser("~/Desktop")
        selected_folder = QFileDialog.getExistingDirectory(
            None, "Seleccionar Carpeta", inital_dir
        )
        if selected_folder:
            self.settings_service.set_defautl_media_folder(selected_folder)
            self.media_folder = selected_folder
            self.set_media()

    def set_media(self):
        if not self.media_folder:
            return

        if not os.path.exists(self.media_folder):
            return

        pathes = []

        for file in os.listdir(self.media_folder):
            full_path = os.path.join(self.media_folder, file)
            if os.path.isfile(full_path):
                _, extension = os.path.splitext(file)
                if extension.lower() in BG_EXTENSIONS:
                    pathes.append(full_path)

        self.media.items.emit(pathes)

    def media_selected(self, media: str):
        media_formated = dict(type="media", slide_style={"bg_path": media})
        self.request.media_selected.emit(media_formated)
