from PySide6.QtWidgets import (
    QTableView,
    QAbstractItemView,
    QHeaderView,
    QStyledItemDelegate,
    QStyleOptionViewItem,
)
from PySide6.QtGui import QStandardItemModel, QStandardItem, QFontMetrics
from PySide6.QtCore import (
    Qt,
    QSortFilterProxyModel,
    Signal,
    QSize,
    QObject,
    QModelIndex,
    QEvent,
)
from ..Props.visual import Width, Height, AspectRatio, Alignment, FontSize
from ..Props.content import Attributes, Filter, Items, Index
from ..Props.events import OnClick, OnDoubleClick, OnEnterPress, OnRightClick
from .interfaces import Interactive, Component, Static, Floating
from .helpers import create_font


class AutoWrapDelegate(QStyledItemDelegate):
    def sizeHint(self, option, index):
        text = index.data() or ""
        metrics = QFontMetrics(option.font)

        # Calcula el rectángulo que ocuparía el texto con saltos de línea
        rect = metrics.boundingRect(
            0,
            0,
            option.rect.width(),
            0,
            Qt.TextWordWrap,
            text,
        )
        # Devuelve el alto con un pequeño margen
        return QSize(rect.width(), int(rect.height() * 1.2))


class FitFontDelegate(QStyledItemDelegate):
    """Fila ajustada a la altura de la fuente (sin wrap)."""

    def sizeHint(self, option, index):
        og_size = super().sizeHint(option, index)
        metrics = QFontMetrics(option.font)
        height = int(metrics.height() * 1.5)
        return QSize(og_size.width(), height)


class TableView(QTableView, Component, Static, Interactive):
    """
    Allowed props:\n
        Width, Height, AspectRatio, Alignment,
        FontSize, Attributes, Filter, Items
    Atributes:
        "filter_key": int, "headers": list, "stretch": list[int],
        "selection_mode":"cell", "row", "multiple"
    """

    enter_pressed = Signal(QObject)
    on_click = Signal(QObject)

    def __init__(self, *args):
        QTableView.__init__(self)
        Component.__init__(self)
        Interactive.__init__(self)
        Static.__init__(self)

        self._current_index = None

        self.stretch_list: list = None
        self.headers: list = None
        self.horizontalHeader().setVisible(False)
        self.setEditTriggers(QTableView.NoEditTriggers)
        self._model = QStandardItemModel()
        self.model_proxy = QSortFilterProxyModel()
        self.model_proxy.setSourceModel(self._model)
        self.model_proxy.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.model_proxy.setFilterKeyColumn(0)
        self.setModel(self.model_proxy)
        self.setSortingEnabled(False)
        self.verticalHeader().setVisible(False)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setItemDelegate(FitFontDelegate(self))
        self.setSelectionMode(QTableView.SingleSelection)
        self.setSelectionBehavior(QTableView.SelectItems)
        self.on_click.connect(lambda i: setattr(self, "_current_index", i))
        self.assign_props(args)
        self._first_polish_done = False
        self.installEventFilter(self)

    def eventFilter(self, obj, event):
        et = event.type()

        # Cuando Qt YA CALCULÓ tamaño + QSS + layout
        if et in (QEvent.Polish, QEvent.PolishRequest):
            if not self._first_polish_done and self.context:
                self._first_polish_done = True
                self.propagate_after_resize()
            return False

        # Cuando Qt recalcula el layout del widget
        if et == QEvent.LayoutRequest:
            if self._first_polish_done and self.context:
                self.propagate_after_resize()
            return False

        return False

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self._first_polish_done and self.context:
            self.propagate_after_resize()

    def assign_props(self, args):
        for arg in args:
            if isinstance(
                arg,
                (
                    Alignment,
                    Height,
                    Width,
                    AspectRatio,
                    FontSize,
                    Attributes,
                    Filter,
                    Items,
                    OnClick,
                    OnDoubleClick,
                    OnEnterPress,
                    Index,
                    OnRightClick,
                ),
            ):
                self.props[arg.key] = arg.value
            elif isinstance(arg, Floating):
                arg.anchor = self
                self.floatings.append(arg)

        self.font_size = self.props.get("fontsize", 3)

        if items := self.props.get("items"):
            if isinstance(items, list):
                self.add_items(items)
            elif isinstance(items, Signal):
                items.connect(self.add_items)

        if filter := self.props.get("filter"):
            if isinstance(filter, str):
                self.filter(filter)
            elif isinstance(filter, Signal):
                filter.connect(self.filter)

        if attrs := self.props.get("attributes", None):
            if isinstance(attrs, Signal):
                attrs.connect(self.set_attributes)
            elif isinstance(attrs, dict):
                self.set_attributes(attrs)

        if onclick := self.props.get("onclick"):
            self.on_click.connect(lambda i: self.exec_func(onclick, i))

        if ondclick := self.props.get("ondoubleclick"):
            self.doubleClicked.connect(lambda i: self.exec_func(ondclick, i))

        if onenterpress := self.props.get("onenterpress"):
            self.enter_pressed.connect(lambda i: self.exec_func(onenterpress, i))

        if onrclick := self.props.get("onrightclick"):
            self.setContextMenuPolicy(Qt.CustomContextMenu)
            self.customContextMenuRequested.connect(
                lambda p: self.on_right_click(p, onrclick)
            )

        if index := self.props.get("index"):
            if isinstance(index, Signal):
                index.connect(self.set_focus)

    def set_attributes(self, properties: dict):
        for key, value in properties.items():
            self.setter(key, value)

    def setter(self, attr, value):
        match attr:
            case "filter_key":
                self.model_proxy.setFilterKeyColumn(value)
            case "headers":
                self.set_headers(value)
            case "selection_mode":
                self.set_selection_mode(value)
            case "stretch":
                self.stretch_list = value
            case "wrap":
                self.set_wrap(value)

    def set_wrap(self, wrap: bool):
        if wrap:
            self.setItemDelegate(AutoWrapDelegate(self))
        else:
            self.setItemDelegate(FitFontDelegate(self))

    def set_headers(self, headers: list):
        self.horizontalHeader().setVisible(True)
        self.headers = headers
        self.model.setHorizontalHeaderLabels(self.headers)

    def set_selection_mode(self, mode):
        if mode == "cell":
            self.setSelectionMode(QTableView.SingleSelection)
            self.setSelectionBehavior(QTableView.SelectItems)
        elif mode == "row":
            self.setSelectionMode(QTableView.SingleSelection)
            self.setSelectionBehavior(QTableView.SelectRows)
        elif mode == "multiple":
            self.setSelectionMode(QAbstractItemView.ContiguousSelection)
            self.setSelectionBehavior(QTableView.SelectRows)

    def exec_func(self, func, i):
        if isinstance(i, QModelIndex):
            index = self.model_proxy.mapToSource(i)
        else:
            indexes = i.indexes()
            if indexes == []:
                return
            else:
                index = self.model_proxy.mapToSource(indexes[0])
        func((index.row(), index.column()))

    def set_focus(self, row, column):
        self.blockSignals(True)
        self.selectionModel().blockSignals(True)

        if row is None or column is None or row < 0 or column < 0:
            self.clearSelection()
            self.clearFocus()
            self._current_index = None
            self.style().unpolish(self)
            self.style().polish(self)
            font = create_font(self, self.font_size)
            self.horizontalHeader().setFont(font)
            self.setFont(font)
            self.blockSignals(False)
            self.selectionModel().blockSignals(False)
            return

        source_model = self.model_proxy.sourceModel()
        source_qindex = source_model.index(row, column)
        proxy_qindex = self.model_proxy.mapFromSource(source_qindex)

        if proxy_qindex.isValid():
            self.setCurrentIndex(proxy_qindex)
            self.setFocus()

        self.blockSignals(False)
        self.selectionModel().blockSignals(False)

    def add_items(self, data_list: list[list]):
        self.blockSignals(True)
        self.selectionModel().blockSignals(True)
        self._model.clear()
        for data in data_list:
            row = [QStandardItem(str(cell)) for cell in data]
            self._model.appendRow(row)
        if self.headers:
            self._model.setHorizontalHeaderLabels(self.headers)
        if self.context:
            self.update_column_widths()
        self.blockSignals(False)
        self.selectionModel().blockSignals(False)

    def filter(self, text: str):
        self.blockSignals(True)
        self.selectionModel().blockSignals(True)
        self.model_proxy.setFilterFixedString(text)
        self.clearSelection()
        self.clearFocus()
        self._current_index = None
        self.blockSignals(False)
        self.selectionModel().blockSignals(False)

    def on_right_click(self, pos, func):
        index = self.indexAt(pos)

        if not index.isValid():
            return

        i = self.model_proxy.mapToSource(index)
        func({"pos": pos, "coord": (i.row(), i.column())})

    def update_column_widths(self):
        if not self.stretch_list:
            return

        header = self.horizontalHeader()

        # Asignar ResizeToContents a las columnas con factor 0
        fixed_width = 0
        for i, factor in enumerate(self.stretch_list):
            if factor == 0:
                header.setSectionResizeMode(i, QHeaderView.ResizeToContents)
                fixed_width += self.columnWidth(i)

        available_width = self.viewport().width() - fixed_width

        # Repartir espacio restante
        stretch_columns = [i for i, f in enumerate(self.stretch_list) if f > 0]
        total_factor = sum(f for f in self.stretch_list if f > 0)

        for i in stretch_columns:
            factor = self.stretch_list[i]
            header.setSectionResizeMode(i, QHeaderView.Fixed)
            width = int(available_width * (factor / total_factor))
            header.resizeSection(i, width)

        v_header = self.verticalHeader()

        # Ajustar altura de cada fila manualmente
        for row in range(v_header.count()):
            # Tomamos la primera columna como referencia
            index = self.model().index(row, 0)

            # Obtener el delegado real de esa celda
            delegate = self.itemDelegate(index)

            # Crear un option adecuado con el ancho de la fila
            option = QStyleOptionViewItem()
            option.initFrom(self)
            option.rect = self.visualRect(index)
            option.font = self.font()

            # Obtener sizeHint del delegate
            hint = delegate.sizeHint(option, index)

            # Aplicar la altura
            v_header.resizeSection(row, hint.height())

    def mousePressEvent(self, event):
        # IGNORAR CLIC DERECHO PARA SELECCIÓN
        if event.button() == Qt.RightButton:
            event.ignore()
            return
        super().mousePressEvent(event)
        # Emitir activación manual al hacer clic izquierdo
        index = self.indexAt(event.pos())
        if index.isValid():
            self.on_click.emit(index)

    def keyPressEvent(self, event):
        last_index = self._current_index
        super().keyPressEvent(event)
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            index = self.currentIndex()
            if index.isValid():
                self.enter_pressed.emit(index)

        if event.key() in (Qt.Key_Up, Qt.Key_Down, Qt.Key_Left, Qt.Key_Right):
            index = self.currentIndex()
            if index.isValid() and index != last_index:
                self.on_click.emit(index)

    def set_size(self, size):
        self.setFixedSize(size)

    def apply_style(self):
        font = create_font(self, self.font_size)
        self.horizontalHeader().setFont(font)
        self.setFont(font)

    def propagate_after_resize(self):
        self.apply_style()
        self.update_column_widths()
        self.resize_floatings()
