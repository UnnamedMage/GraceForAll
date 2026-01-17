from PySide6.QtCore import QSize


class Component:
    def __init__(self):
        self.context = None
        self.props = {}

    def assign_props(self, args: tuple):
        pass

    def propagate_after_resize(self):
        pass


class Static:
    def set_size(self, size: QSize):
        pass


class Floating:
    def __init__(self):
        self.anchor = None

    def set_size(self):
        pass


class Interactive:
    def __init__(self):
        self.context = None
        self.floatings: list[Floating] = []

    def set_context(self, cont):
        self.context = cont
        for floating in self.floatings:
            floating.set_context(self.context)

    def resize_floatings(self):
        for floating in self.floatings:
            floating.set_size()

    def apply_style(self):
        pass


class Container:
    def __init__(self):
        self.context = None
        self.statics: list[Static] = []
        self.floatings: list[Floating] = []

    def set_context(self, cont):
        self.context = cont
        for floating in self.floatings:
            floating.set_context(self.context)
        for static in self.statics:
            static.set_context(self.context)

    def resize_statics(self):
        pass

    def resize_floatings(self):
        for floating in self.floatings:
            floating.set_size()
