from PySide6.QtCore import QObject, Signal
from abc import abstractmethod
from ..Tools import DICT


class Node:
    def __init__(self, schema: dict):
        self.signals = []
        # Creamos una clase dinámica que hereda de QObject
        attrs = {}

        # Declaramos señales como atributos de CLASE
        for name, types in schema.items():
            if not isinstance(types, tuple):
                types = (types,) if types else ()
            attrs[name] = Signal(*types)
            self.signals.append(name)

        DynamicNode = type("DynamicNode", (QObject,), attrs)
        self.obj = DynamicNode()

    def __getattr__(self, item):
        return getattr(self.obj, item)


class SingletonMeta(type(QObject), type):
    _instances = {}
    _init_args = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            # Guardamos los argumentos usados la primera vez
            cls._init_args[cls] = (args, kwargs)
            cls._instances[cls] = super().__call__(*args, **kwargs)
        else:
            # Si ya existe, no volvemos a pedir argumentos
            # pero si los mandan de nuevo, los ignoramos
            pass
        return cls._instances[cls]


class BaseVM(QObject, metaclass=SingletonMeta):
    def __init__(self):
        super().__init__()
        self._state: DICT = DICT()

    def set_state(self, state: dict | DICT):
        """Actualiza el estado y notifica a quien esté escuchando."""
        if isinstance(state, dict):
            state = DICT(state)
        self._state = state

    def get_state(self):
        """Devuelve el estado actual (copia para evitar modificaciones externas)."""
        return self._state.clone()

    def update_state(self, **kwargs):
        self._state.update_safe(**kwargs)

    @abstractmethod
    def pv_init(self):
        """Se ejecuta cuando la vista ya esta creada pero no mostrada."""
        pass

    @abstractmethod
    def on_start(self):
        """Se ejecuta cuando la vista asociada se muestra o el flujo comienza."""
        pass

    @abstractmethod
    def on_stop(self):
        """Se ejecuta cuando la vista asociada se oculta o el flujo termina."""
        pass

    def register(self, name: str, schema: dict):
        node = Node(schema)
        setattr(self, name, node)
