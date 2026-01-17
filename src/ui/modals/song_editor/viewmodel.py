from PySide6.QtWidgets import QFileDialog
from ....Qtive.Managers import BaseVM
from src.core.factory import Factory
from ....common import get_platform_path
from ...utils.i18n import MESSAGES
from ...utils.constants import (
    SONG,
    FAMILIES,
    FACTORS,
    IN_ANIMATIONS,
    OUT_ANIMATIONS,
    BG_EXTENSIONS,
    BG_IMAGE_EXTENSIONS,
    BG_VIDEO_EXTENSIONS,
)
import os
import shutil
from copy import deepcopy


class SongEditorVM(BaseVM):
    def __init__(self, factory: Factory):
        super().__init__()
        self.song_service = factory.get_song_service()
        self.settings_service = factory.get_settings_service()
        self.bg_folder = str(get_platform_path("appdata", "backgrounds"))
        self.register("app", {"task_with_song": dict, "task_with_bg": ()})
        self.register("window", {"message": dict, "btn_delete": dict, "close": ()})
        self.register("projector", {"bg": str, "attrs": dict, "text": str})
        self.register("inputs", {"title": str, "lyrics": str})
        self.register("font", {"family_index": int, "factor_index": int})
        self.register("style", {"italic": dict, "bold": dict})
        self.register("color", {"black": dict, "white": dict})
        self.register("v_align", {"vcenter": dict, "top": dict, "bottom": dict})
        self.register("h_align", {"hcenter": dict, "left": dict, "right": dict})
        self.register("animation", {"in_index": int, "out_index": int})
        self.register("bg", {"items": list, "menu": ()})
        self.style.italic.emit({"italic": True})
        self.style.bold.emit({"bold": True})
        self.song = deepcopy(SONG)
        self.test_text = ""
        self.default_bg = None
        self.bg_items = None

    def on_start(self):
        self.inputs.title.emit(self.song["title"])
        self.inputs.lyrics.emit(
            "\n\n".join(self.song["lyrics"]) if self.song["lyrics"] != [] else ""
        )

        self.font.family_index.emit(FAMILIES.index(self.song["slide_style"]["family"]))
        self.font.factor_index.emit(FACTORS.index(self.song["slide_style"]["factor"]))

        self.style.italic.emit({"checked": self.song["slide_style"]["italic"]})
        self.style.bold.emit({"checked": self.song["slide_style"]["bold"]})

        self.color.black.emit({"checked": self.song["slide_style"]["color"] == "black"})
        self.color.white.emit({"checked": self.song["slide_style"]["color"] == "white"})

        self.v_align.vcenter.emit(
            {"checked": self.song["slide_style"]["v_align"] == "vcenter"}
        )
        self.v_align.top.emit({"checked": self.song["slide_style"]["v_align"] == "top"})
        self.v_align.bottom.emit(
            {"checked": self.song["slide_style"]["v_align"] == "bottom"}
        )

        self.h_align.hcenter.emit(
            {"checked": self.song["slide_style"]["h_align"] == "hcenter"}
        )
        self.h_align.left.emit(
            {"checked": self.song["slide_style"]["h_align"] == "left"}
        )
        self.h_align.right.emit(
            {"checked": self.song["slide_style"]["h_align"] == "right"}
        )

        self.animation.in_index.emit(
            IN_ANIMATIONS.index(self.song["slide_style"]["in_animation"])
        )
        self.animation.out_index.emit(
            OUT_ANIMATIONS.index(self.song["slide_style"]["out_animation"])
        )

        self.window.btn_delete.emit({"visible": True if self.song.get("id") else False})

        if not self.bg_items:
            self.refresh_menu()

        response = self.settings_service.get_default_slide_style()
        if response["success"]:
            self.default_bg = response["data"]["bg_path"]

        if bg := self.song["slide_style"].get("bg_path"):
            self._change_bg(bg)
            return

        bg = self.default_bg

        if bg:
            self._change_bg(bg)

    def blank(self):
        self.song = deepcopy(SONG)
        self.projector.attrs.emit(self.song)
        self.test_text = ""
        self.projector.text.emit(self.test_text)

    def notification(self, title: str, code: str):
        self.window.message.emit(
            {
                "title": title,
                "message": MESSAGES[code],
            }
        )

    def send_task(self, action: str):
        self.app.task_with_song.emit(
            {
                "action": action,
                "data": self.song.copy(),
            }
        )

    def close(self):
        def chose(conf: bool):
            if conf:
                self.blank()
                self.window.close.emit()

        if self.song["lyrics"] != [] or self.song["title"] != "":
            self.window.message.emit(
                {
                    "title": "Antes de continuar",
                    "message": "Desea salir sin terminar la cancion?",
                    "mode": "confirmation",
                    "callback": chose,
                }
            )
        else:
            self.blank()
            self.window.close.emit()

    def save(self):
        if self.song.get("id"):
            response = self.song_service.update(self.song)
            action = "updated"
        else:
            response = self.song_service.add(self.song)
            action = "added"

        if not response["success"]:
            self.notification("Error", response["code"])
            return

        self.notification("Tarea completada", response["code"])
        self.send_task(action)
        self.blank()
        self.window.close.emit()

    def _delete_confirmed(self, b: bool):
        if not b:
            return
        response = self.song_service.delete({"id": self.song["id"]})
        if response["success"]:
            self.notification("Tarea completada", response["code"])
            self.send_task("deleted")
        self.blank()
        self.window.close.emit()

    def delete(self):
        if not self.song.get("id"):
            return

        self.window.message.emit(
            {
                "title": "Antes de continuar",
                "message": "Esta seguro de eliminar la cancion?",
                "mode": "confirmation",
                "callback": self._delete_confirmed,
            }
        )

    def set_song_id(self, id: str):
        response = self.song_service.get({"id": id})
        if response["success"]:
            self.song = response["data"]

    def update_preview(self):
        self.projector.attrs.emit(self.song)
        self.projector.text.emit(self.test_text)

    def set_title(self, text: str):
        self.song["title"] = text

    def set_text(self, text: str):
        self.test_text = text
        self.update_preview()

    def set_lyrics(self, plain_text: str):
        self.song["lyrics"] = plain_text.split("\n\n") if plain_text != "" else []

    def set_in(self, index):
        self.song["slide_style"]["in_animation"] = IN_ANIMATIONS[index]
        self.update_preview()

    def set_out(self, index):
        self.song["slide_style"]["out_animation"] = OUT_ANIMATIONS[index]
        self.update_preview()

    def set_factor(self, index):
        self.song["slide_style"]["factor"] = FACTORS[index]
        self.update_preview()

    def set_font(self, index):
        self.song["slide_style"]["family"] = FAMILIES[index]
        self.update_preview()

    def set_bold(self):
        self.song["slide_style"]["bold"] = not self.song["slide_style"]["bold"]
        self.update_preview()
        self.style.bold.emit({"checked": self.song["slide_style"]["bold"]})

    def set_italic(self):
        self.song["slide_style"]["italic"] = not self.song["slide_style"]["italic"]
        self.update_preview()
        self.style.italic.emit({"checked": self.song["slide_style"]["italic"]})

    def set_v_align(self, v_align: str):
        self.song["slide_style"]["v_align"] = v_align
        self.update_preview()
        self.v_align.vcenter.emit(
            {"checked": self.song["slide_style"]["v_align"] == "vcenter"}
        )
        self.v_align.top.emit({"checked": self.song["slide_style"]["v_align"] == "top"})
        self.v_align.bottom.emit(
            {"checked": self.song["slide_style"]["v_align"] == "bottom"}
        )

    def set_h_align(self, h_align: str):
        self.song["slide_style"]["h_align"] = h_align
        self.update_preview()
        self.h_align.hcenter.emit(
            {"checked": self.song["slide_style"]["h_align"] == "hcenter"}
        )
        self.h_align.left.emit(
            {"checked": self.song["slide_style"]["h_align"] == "left"}
        )
        self.h_align.right.emit(
            {"checked": self.song["slide_style"]["h_align"] == "right"}
        )

    def set_color(self, color: str):
        self.song["slide_style"]["color"] = color
        self.update_preview()
        self.color.black.emit({"checked": self.song["slide_style"]["color"] == "black"})
        self.color.white.emit({"checked": self.song["slide_style"]["color"] == "white"})

    def set_background(self, bg):
        if bg != "default":
            self.song["slide_style"]["bg_path"] = bg
        else:
            self.song["slide_style"]["bg_path"] = None
            bg = self.default_bg

        if bg:
            self._change_bg(bg)

    def refresh_menu(self):
        folder = self.bg_folder
        pathes = []

        for file in os.listdir(folder):
            full_path = os.path.join(folder, file)
            if os.path.isfile(full_path):
                _, extension = os.path.splitext(file)
                if extension.lower() in BG_EXTENSIONS:
                    pathes.append(full_path)

        self.bg_items = pathes
        self.bg.items.emit(pathes)

    def _change_bg(self, bg):
        _, ext = os.path.splitext(bg)
        if ext.lower() in BG_IMAGE_EXTENSIONS:
            self.projector.attrs.emit({"aspect_ratio": "expand"})
            self.projector.bg.emit(bg)
        elif ext.lower() in BG_VIDEO_EXTENSIONS:
            attr = {
                "aspect_ratio": "expand",
                "loop": True,
                "state": "play",
            }
            self.projector.bg.emit(bg)
            self.projector.attrs.emit(attr)

    def add_new_bg(self):
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

            if os.path.exists(destiny):
                base, ext = os.path.splitext(media_name)
                i = 1
                while os.path.exists(os.path.join(folder, f"{base}_{i}{ext}")):
                    i += 1
                destiny = os.path.join(folder, f"{base}_{i}{ext}")

            try:
                shutil.copy(media_path, destiny)
            except Exception:
                self.notification("Error", "bg.transfer_failed")
                return
            self.app.task_with_bg.emit()
            self.refresh_menu()
