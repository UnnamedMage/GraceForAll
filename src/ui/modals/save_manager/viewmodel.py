from ....Qtive.Managers import BaseVM
from src.core.factory import Factory
from ...utils.i18n.messages import MESSAGES


class SaveManagerVM(BaseVM):
    def __init__(self, factory: Factory):
        super().__init__()
        self.schedule_service = factory.get_schedule_service()
        self.register("app", {"saved_schedule": dict, "schedule_added": ()})
        self.register(
            "window",
            {"close": (), "show": (), "message": dict, "name": str, "title": str},
        )
        self.schedule = {}

    def request_receiver(self, request: dict):
        if request["action"] == "save":
            self._schedule_for_save(request["payload"])
        elif request["action"] == "save_as":
            self._schedule_for_save_as(request["payload"])

    def _schedule_for_save(self, schedule: dict):
        if schedule.get("items") == []:
            return

        if schedule.get("id") is None:
            self.schedule = schedule.copy()
            self.window.title.emit("Guardar")
            self.window.show.emit()
            return

        response = self.schedule_service.update(schedule.copy())
        if response["success"]:
            self.app.saved_schedule.emit(schedule.copy())

    def _schedule_for_save_as(self, schedule: dict):
        if schedule.get("items") == []:
            return
        if not schedule.get("id"):
            self._schedule_for_save(schedule)
            return
        self.schedule = schedule.copy()
        self.schedule.pop("name")
        self.schedule.pop("id")
        self.window.title.emit("Guardar como...")
        self.window.show.emit()

    def change_name(self, name: str):
        self.schedule["name"] = name

    def notification(self, title: str, code: str):
        self.window.message.emit({"title": title, "message": MESSAGES[code]})

    def save(self):
        response = self.schedule_service.add(self.schedule.copy())
        if response["success"]:
            self.notification("Tarea completada", response["code"])
            self.schedule.update(response["data"])
            self.app.saved_schedule.emit(self.schedule.copy())
            self.app.schedule_added.emit()
            self.close()
        else:
            self.notification("Error", response["code"])

    def close(self):
        self.schedule = {}
        self.window.name.emit("")
        self.window.close.emit()
