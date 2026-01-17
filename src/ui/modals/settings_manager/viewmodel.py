from ....Qtive.Managers import BaseVM
from ....Qtive.Style import set_theme
from src.core.factory import Factory
from ...utils.constants import COLORS, MODE


class SettingsManagerVM(BaseVM):
    def __init__(self, factory: Factory):
        super().__init__()
        self.settings_service = factory.get_settings_service()
        self.register("window", {"close": ()})
        self.register("view", {"message": dict})
        self.register("btns_attrs", {"sect0": dict})
        self.register("theme", {"mode_index": int, "color_index": int})
        self.set_state(
            {
                "section": None,
                "primary_color": None,
                "mode": None,
                "theme": None,
            }
        )

    def pv_init(self):
        response = self.settings_service.get_default_theme()
        if response["success"]:
            mode, pc = response["data"].split("_")
        else:
            mode, pc = "light", "blue"
            self.settings_service.set_defautl_theme("light_blue")
        self.theme.mode_index.emit(MODE.index(mode))
        self.theme.color_index.emit(COLORS.index(pc))
        self.update_state(mode=mode, primary_color=pc)
        self.dispatch({"type": "APPLY_THEME"})

    def on_start(self):
        self.dispatch({"type": "CHANGE_SECTION", "payload": 0})

    def dispatch(self, action: dict):
        old_state = self.get_state()
        new_state = self.reducer(action)
        if new_state:
            self.set_state(new_state)
            self.emit_changes(action, new_state, old_state)

    def reducer(self, action) -> dict | None:
        state = self.get_state()
        type_ = action["type"]
        payload: dict = action.get("payload")

        if type_ == "CHANGE_SECTION":
            if state.section == payload:
                return
            state.update_safe(section=payload)
            return state

        if type_ == "APPLY_THEME":
            new_theme = f"{state.mode}_{state.primary_color}"
            if state.theme == new_theme:
                return
            state.update_safe(theme=new_theme)
            return state

    def emit_changes(self, action, new_state, old_state):
        if action["type"] == "APPLY_THEME":
            theme = new_state.theme
            set_theme(theme)
            self.settings_service.set_defautl_theme(theme)
            return

        if old_state.section != new_state.section:
            for signal in self.btns_attrs.signals:
                if signal == f"sect{new_state.section}":
                    attrs = {"checked": True}
                else:
                    attrs = {"checked": False}
            getattr(self.btns_attrs, signal).emit(attrs)

    def change_mode(self, index):
        self.update_state(mode=MODE[index])
        self.dispatch({"type": "APPLY_THEME"})

    def change_color(self, index):
        self.update_state(primary_color=COLORS[index])
        self.dispatch({"type": "APPLY_THEME"})
