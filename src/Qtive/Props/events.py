from typing import Callable


class OnClick:
    def __init__(self, value: Callable):
        self.key = "onclick"
        self.value = value


def on_click(value: Callable):
    return OnClick(value)


class OnDoubleClick:
    def __init__(self, value: Callable):
        self.key = "ondoubleclick"
        self.value = value


def on_double_click(value: Callable):
    return OnDoubleClick(value)


class OnEnterPress:
    def __init__(self, value: Callable):
        self.key = "onenterpress"
        self.value = value


def on_enter_press(value: Callable):
    return OnEnterPress(value)


class OnTextChange:
    def __init__(self, value: Callable):
        self.key = "ontextchange"
        self.value = value


def on_text_change(func: Callable):
    return OnTextChange(func)


class OnExecution:
    def __init__(self, value: Callable):
        self.key = "onexecution"
        self.value = value


def on_execution(func: Callable):
    return OnExecution(func)


class OnUpdate:
    def __init__(self, value: Callable):
        self.key = "onupdate"
        self.value = value


def on_update(value: Callable):
    return OnUpdate(value)


class OnRightClick:
    def __init__(self, value: Callable):
        self.key = "onrightclick"
        self.value = value


def on_right_click(value: Callable):
    return OnRightClick(value)


class OnClose:
    def __init__(self, value: Callable):
        self.key = "onclose"
        self.value = value


def on_close(value: Callable):
    return OnClose(value)
