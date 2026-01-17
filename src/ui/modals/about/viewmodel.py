from ....Qtive.Managers import BaseVM


class AboutVM(BaseVM):
    def __init__(self):
        super().__init__()
        self.register("window", {"close": ()})
