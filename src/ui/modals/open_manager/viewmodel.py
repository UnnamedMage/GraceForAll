from ....Qtive.Managers import BaseVM
from src.core.factory import Factory
from ...utils.i18n.messages import MESSAGES


class OpenManagerVM(BaseVM):
    def __init__(self, factory: Factory):
        super().__init__()
        self.selected_schedule = None
        self.schedule_list = []
        self.schedule_service = factory.get_schedule_service()
        self.register("schedules_list", {"items": list})
        self.register("btns", {"attr": dict})
        self.register("window", {"message": dict, "close": ()})
        self.register("app", {"send_to_show": dict, "send_to_eliminate": dict})
        self.refresh_list()

    def refresh_list(self):
        response = self.schedule_service.get_all()
        self.schedule_list = response["data"]
        if self.schedule_list != []:
            self.schedule_list.sort(key=lambda x: x["date"], reverse=True)

    def on_start(self):
        self.selected_schedule = None
        self.btns.attr.emit({"disabled": True})
        self.schedules_list.items.emit(
            [[schedule["name"], schedule["date"]] for schedule in self.schedule_list]
        )

    def message(self, title, code):
        self.window.message.emit({"title": title, "message": MESSAGES[code]})

    def schedule_selected(self, coord: tuple):
        index = coord[0]
        self.selected_schedule = self.schedule_list[index]
        self.btns.attr.emit({"disabled": False})

    def send_schedule(self):
        if not self.selected_schedule:
            return

        response = self.schedule_service.get({"id": self.selected_schedule["id"]})

        if not response["success"]:
            self.message("Error", response["code"])
            self.app.send_to_eliminate.emit({"data": {"id": response["data"]["id"]}})
            self.refresh_list()
            self.on_start()
            return

        self.app.send_to_show.emit(response["data"].copy())
        self.window.close.emit()

    def delete_schedule(self):
        if not self.selected_schedule:
            return

        ident = {"id": self.selected_schedule["id"]}
        response = self.schedule_service.delete(ident)

        if response["success"]:
            self.app.send_to_eliminate.emit({"data": ident})
            self.refresh_list()
            self.message("Tarea completada", response["code"])
        else:
            self.message("Error", response["code"])

        self.on_start()
