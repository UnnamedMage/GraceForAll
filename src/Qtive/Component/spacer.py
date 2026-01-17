from PySide6.QtWidgets import QSpacerItem, QSizePolicy
from .interfaces import Interactive, Component, Static
from typing import Literal

class Spacer(QSpacerItem, Component, Interactive, Static):
    def __init__(self,orientation:Literal["horizontal", "vertical"]= "horizontal"):
        Component.__init__(self)
        Static.__init__(self)
        Interactive.__init__(self)
        if orientation == "horizontal":
            w,h,ph,pv = 1,1,QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum
        else:
             w,h,ph,pv = 1,1, QSizePolicy.Policy.Minimum,QSizePolicy.Policy.Expanding
        super().__init__(w, h, ph, pv)