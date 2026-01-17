from collections import UserDict
from copy import deepcopy


class DICT(UserDict):
    """
    Diccionario ampliado para manejar estado con:
    - acceso por atributos
    - update seguro y profundo
    - diff contra otro estado
    - listeners por clave
    - hooks before/after update
    """

    # -----------------------------------------------------
    #  Constructor
    # -----------------------------------------------------
    def __init__(self, initial=None):
        super().__init__(initial or {})
        self._listeners = {}  # key -> list(callback)
        self._before_hooks = []  # (key, old, new)
        self._after_hooks = []  # (key, old, new)

    # -----------------------------------------------------
    #  Acceso por atributos
    # -----------------------------------------------------
    def __getattr__(self, item):
        try:
            return self.data[item]
        except KeyError:
            raise AttributeError(item)

    def __setattr__(self, key, value):
        # Para atributos internos de la clase
        if key.startswith("_") or key in ("data",):
            return super().__setattr__(key, value)

        # Para claves del dict
        old = self.data.get(key)
        self._emit_before(key, old, value)
        self.data[key] = value
        self._emit_after(key, old, value)
        self._notify_listeners(key, old, value)

    # -----------------------------------------------------
    # Métodos de update
    # -----------------------------------------------------
    def update_safe(self, **kwargs):
        for k, v in kwargs.items():
            if k in self.data:
                self[k] = v

    def update_deep(self, **kwargs):
        for k, v in kwargs.items():
            if (
                k in self.data
                and isinstance(self.data[k], dict)
                and isinstance(v, dict)
            ):
                self._deep_merge(self.data[k], v)
            else:
                self[k] = v

    def _deep_merge(self, base, new):
        for k, v in new.items():
            if k in base and isinstance(base[k], dict) and isinstance(v, dict):
                self._deep_merge(base[k], v)
            else:
                base[k] = v

    # -----------------------------------------------------
    # Hooks internos
    # -----------------------------------------------------
    def on_before_update(self, callback):
        """callback(key, old_value, new_value)"""
        self._before_hooks.append(callback)

    def on_after_update(self, callback):
        """callback(key, old_value, new_value)"""
        self._after_hooks.append(callback)

    def _emit_before(self, key, old, new):
        for cb in self._before_hooks:
            cb(key, old, new)

    def _emit_after(self, key, old, new):
        for cb in self._after_hooks:
            cb(key, old, new)

    # -----------------------------------------------------
    # Sistema de listeners por clave
    # -----------------------------------------------------
    def on_change(self, key, callback):
        """
        callback(old_value, new_value)
        """
        self._listeners.setdefault(key, []).append(callback)

    def _notify_listeners(self, key, old, new):
        if key in self._listeners:
            for cb in self._listeners[key]:
                cb(old, new)

    # -----------------------------------------------------
    # Comparación de estados
    # -----------------------------------------------------
    def diff(self, other: dict):
        changed = {}
        for k, v in self.data.items():
            if k not in other or other[k] != v:
                changed[k] = v
        return changed

    # -----------------------------------------------------
    # Utilidades
    # -----------------------------------------------------
    def only(self, *keys):
        return DICT({k: self.data[k] for k in keys if k in self.data})

    def except_keys(self, *keys):
        return DICT({k: v for k, v in self.data.items() if k not in keys})

    def clone(self):
        return DICT(deepcopy(self.data))
