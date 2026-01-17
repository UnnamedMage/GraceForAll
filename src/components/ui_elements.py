from PySide6.QtWidgets import (QWidget, QGridLayout, QSizePolicy, QToolButton, QWidgetAction ,QMenuBar, QFileDialog, QHeaderView,
                               QListWidget , QMenu, QFrame, QStackedWidget, QHBoxLayout, QListWidgetItem, QSlider,
                               QVBoxLayout, QLabel, QTreeView, QLineEdit, QTextEdit, QComboBox, QCompleter, QMessageBox, QAbstractItemView)

from PySide6.QtGui import (QFont, QStandardItemModel, QStandardItem, QPixmap, QIcon, QTextCursor, QColor, 
                           QGuiApplication, QResizeEvent,QPainter,QAction, QPalette)
from PySide6.QtCore import Qt, QSize, QUrl, QSortFilterProxyModel,QRect
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtMultimediaWidgets import QVideoWidget
from components.ui_logic import SYfont, SYcolorselector, SYcreate_icon
from core.helpers import SYpathcreater, SYmediarecognize, SYalignmap, SYwindowextra
from core.models import SY, SYsignals, Versicle, Media
from services.json_service import cargar_carpeta_raiz, editar_carpeta_raiz, cargar_fondo_predeterminado, editar_fondo_predeterminado, cargar_resolucion_actual
from services.db_service import Song, get_song_by_title
from PIL import Image
import os, shutil

class CustomToolButton(QToolButton):
    def __init__(self, texto, form, parent=None, icon=None,orientacion=None, nombre=None):
        super().__init__(parent)
        self.resize_modify = True
        self.svg = None
        if nombre:
            self.setObjectName(nombre)
        
        self.setText(texto)
            
        if icon:
            self.svg = icon
            svg_path = SYpathcreater( "icons", f"{self.svg}.svg", temporal=True)
            text_color = self.palette().color(self.foregroundRole())
            hex_color = text_color.name(QColor.HexRgb)
            with open(svg_path, "r", encoding="utf-8") as file:
                self.svg_data = file.read()
            self.svg_data = self.svg_data.replace('fill="currentColor"', f'fill="{hex_color}"')
            self.svg_data = self.svg_data.replace('stroke="currentColor"', f'stroke="{hex_color}"')
        self.form = form
        self.orientacion = orientacion
        
        
    def resizeEvent(self, event):
        if self.resize_modify == True:
            match self.form:
                case SY.SQUARE:
                    match self.orientacion:
                        case SY.H:
                            size = self.parentWidget().height() if self.parentWidget() else event.size().height()
                        case SY.V:
                            size = self.parentWidget().width() if self.parentWidget() else event.size().width()
                    self.setFixedSize(QSize(size, size))
                
                case SY.DSQUARE:
                    match self.orientacion:
                        case SY.H:
                            size = self.parentWidget().height() if self.parentWidget() else event.size().height()
                        case SY.V:
                            size = self.parentWidget().width() if self.parentWidget() else event.size().width()
                    self.setFixedSize(QSize(size*2, size*2))
                  
                case SY.RECTANGLE:
                    match self.orientacion:
                        case SY.H:
                            size = self.parentWidget().height() if self.parentWidget() else event.size().height()
                        case SY.V:
                            size = self.parentWidget().width() if self.parentWidget() else event.size().width()
                    self.setFixedSize(QSize(size*2, size))
                  
                case SY.TEXT:
                    match self.orientacion:
                        case SY.H:
                            available_height = self.parentWidget().height() if self.parentWidget() else event.size().height()
                            self.setFixedHeight(available_height)
                        case SY.V:
                            available_width = self.parentWidget().width() if self.parentWidget() else event.size().width()
                            self.setFixedWidth(available_width)
            super().resizeEvent(event)
            if self.svg:
                size = int(min(self.width(), self.height()) * 0.8) 
                renderer = QSvgRenderer(self.svg_data.encode('utf-8'))
                pixmap = QPixmap(size, size)
                pixmap.fill(Qt.transparent)
                
                painter = QPainter(pixmap)
                renderer.render(painter)
                painter.end()
                
                self.setIcon(QIcon(pixmap))
                self.setIconSize(QSize(size, size))
        else:
            super().resizeEvent(event)
           
class CustomTreeView(QTreeView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.signals = SYsignals()
    
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            index = self.currentIndex()
            if index.isValid():
                self.signals.enter_pressed.emit(index)
        super().keyPressEvent(event)

class CustomLabel(QLabel):
    def __init__(self, parent=None, path_imagen=None, tipo="png"):
        super().__init__(parent)
        self.tipo = tipo
        if tipo == "svg":
            self.ruta_imagen = SYpathcreater("icons", f"{path_imagen}.svg", temporal=True)
            text_color = self.palette().color(QPalette.WindowText)
            hex_color = text_color.name(QColor.HexRgb)
            with open(self.ruta_imagen, "r", encoding="utf-8") as file:
                self.svg_data = file.read()
            self.svg_data = self.svg_data.replace('fill="currentColor"', f'fill="{hex_color}"')
            self.svg_data = self.svg_data.replace('stroke="currentColor"', f'stroke="{hex_color}"')
            
        else:
            self.ruta_imagen = SYpathcreater("icons", path_imagen, temporal=True)
        
    def set_imagen(self):
        if self.ruta_imagen:
            if self.tipo == "svg":
                size = int(min(self.width(), self.height()) * 0.8) 
                renderer = QSvgRenderer(self.svg_data.encode('utf-8'))
                pixmap = QPixmap(size, size)
                pixmap.fill(Qt.transparent)
                
                painter = QPainter(pixmap)
                renderer.render(painter)
                painter.end()
                
                self.setPixmap(pixmap)
            else:
                pixmap = QPixmap(self.ruta_imagen)
                size = min(self.width(), self.height())
                self.setPixmap(pixmap.scaled(size, size, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            
    def resizeEvent(self, event):
        available_width = self.parentWidget().width() if self.parentWidget() else event.size().width()
        available_height = self.parentWidget().height() if self.parentWidget() else event.size().height()
        size = min(available_height, available_width)
        self.setFixedSize(QSize(size, size))
        super().resizeEvent(event)
        self.set_imagen()

class SYgrid(QGridLayout):
    
    def __init__(self,filas, columnas, dim_filas, dim_columnas, elementos=None, margenes = (0,0,0,0), espacio = 0, widget="asdasd"):
        super().__init__()
        for i in range(filas):
            if i < len(dim_filas):
                self.setRowStretch(i, dim_filas[i])
                    
        for j in range(columnas):
            if j < len(dim_columnas):
                self.setColumnStretch(j, dim_columnas[j])
        
        if elementos:
            for elemento in elementos:
                if len(elemento) == 3:
                    element, row, column = elemento
                    align = None
                    name = None
                elif len(elemento) == 4:
                    element, row, column, align = elemento
                    name = None
                elif len(elemento) == 5:
                    element, row, column, align, name = elemento
                
                    
                if isinstance(element, QGridLayout):
                    
                    container = QWidget()
                    container.setLayout(element)
                    if name:
                        container.setObjectName(name)
                    self.addWidget(container, row, column)
                else:
                    
                    self.addWidget(element, row, column)
                    
                    if align:
                        self.setAlignment(element,align)
        
        ###PlaceHolder###
        if False== True: 
            for i in range(filas):
                for j in range(columnas):
                    if not self.itemAtPosition(i,j):
                        widget_vacio = QWidget()
                        widget_vacio.setStyleSheet(f"background-color: rgba({i*50%255}, {j*50%255}, 200, 0.3);" "border: 1px solid black;")
                        self.addWidget(widget_vacio, i, j)
                        
                                
        self.setSpacing(espacio)
        self.setContentsMargins(*margenes)
        
    def add_element(self, elementos):
        if elementos:
            for elemento in elementos:
                if len(elemento) == 3:
                    element, row, column = elemento
                    align = None
                elif len(elemento) == 4:
                    element, row, column, align = elemento
                    
                if isinstance(element, QGridLayout):
                    
                    container = QWidget()
                    container.setLayout(element)
                    self.addWidget(container, row, column)
                else:
                    
                    self.addWidget(element, row, column)
                    
                    if align:
                        self.setAlignment(element,align)
 
class SYstacked(QStackedWidget):
    def __init__(self,num_paginas, elementos=None):
        super().__init__()
        pages = []
        for _ in range(num_paginas):
            page = QWidget()
            page.setObjectName("Fondo")
            layout_page = QGridLayout()
            layout_page.setContentsMargins(0,0,0,0)
            page.setLayout(layout_page)
            pages.append(page)
            self.addWidget(page)
        
        if elementos:
        
            for elemento in elementos:
                if len(elemento) == 2:
                    element, place, = elemento
                    name = "Fondo"
                elif len(elemento) == 3:
                    element, place, name = elemento
                
                if isinstance(element, QGridLayout):
                    for i, page in enumerate(pages):
                        if i == place:
                            grid_container = QWidget()
                            grid_container.setObjectName(name)
                            grid_container.setLayout(element)
                            page.layout().addWidget(grid_container)
                else:
                    for i, page in enumerate(pages):
                        if i == place:
                            page.layout().addWidget(element)
        
        #PlaceHolder
        for i, page in enumerate(pages):
            if page.layout().count() == 0: 
                label_vacio = QLabel(f"Pagina {i} (Vacia)")
                label_vacio.setAlignment(Qt.AlignCenter)
                label_vacio.setStyleSheet("background-color: lightblue; color: black; font-size: 16px;")
                page.layout().addWidget(label_vacio)
    
class SYmessagebox(QMessageBox):
    def __init__(self, parent ,icono, texto, texto_informativo, botones):
        super().__init__()
        self.setWindowFlags(Qt.Window | Qt.CustomizeWindowHint | Qt.WindowTitleHint | Qt.FramelessWindowHint)
        self.setIcon(icono) 
        self.setText(texto)
        self.setInformativeText(texto_informativo)
        self.setStandardButtons(botones)
        font = SYfont(parent, SY.VFONT_2)
        self.setFont(font)
        self.setStyleSheet(f"""
            QMessageBox QPushButton {{
                background-color: palette(button);
                color: palette(button-text);
                font-family: {font.family()};
                font-size: {font.pointSize()}px;
            }}
        """)
        
        if botones & QMessageBox.Yes:
            yes_button = self.button(QMessageBox.Yes)
            yes_button.setText("Sí")

class SYlabel:
    def __init__(self, parent, texto, tamano = SY.VFONT_1, nombre=None, imagen=False, link=False, tipo="png"):
        self.tamano = tamano
        self.imagen = imagen
        if imagen:
            self.label = CustomLabel(parent, texto, tipo)
        else:
            self.label = QLabel(texto)
            if link:
                self.label.setText(f'<a href="{texto}" style="color: blue; text-decoration: underline;">{texto}</a>')
                self.label.setTextFormat(Qt.RichText)
                self.label.setTextInteractionFlags(Qt.TextBrowserInteraction)
                self.label.setOpenExternalLinks(True)
            
        font = SYfont(parent, tamano)
        if nombre:
            self.label.setObjectName(nombre)
            font.setBold(True)
        self.label.setFont(font)
    
    def get_widget(self):
        return self.label
    
    def resize(self, parent):
        font = SYfont(parent, self.tamano)
        self.label.setFont(font)
        if self.imagen:
            self.label.resize(self.label.width(), self.label.height()) 
        
class SYlineedit:
    def __init__(self, parent, texto="Aqui va un holder", tamano = SY.VFONT_2):
        self.tamano = tamano
        self.line = QLineEdit(parent)
        self.line.setPlaceholderText(texto)
        font = SYfont(parent,tamano)
        self.line.setFont(font)
        self.line.setContextMenuPolicy(Qt.NoContextMenu)
    
    def get_widget(self):
        return self.line
    
    def resize(self, parent):
        font = SYfont(parent, self.tamano)
        self.line.setFont(font)
    
    def set_completer(self, diccionario, parent):
        self.completer = QCompleter(diccionario, parent)
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.line.setCompleter(self.completer)
    
class SYtextedit:
    def __init__(self, parent, texto="Aqui va un holder", tamano=SY.VFONT_2):
        self.tamano = tamano
        self.text_box = QTextEdit(parent)
        self.text_box.setPlaceholderText(texto)
        font = SYfont(parent, tamano)
        self.text_box.setFont(font)
        self.text_box.setContextMenuPolicy(Qt.NoContextMenu)

        # === Agrega resaltado visual con QFrame ===
        self.highlight_frame = QFrame(self.text_box.viewport())
        self.highlight_frame.setStyleSheet("background-color: rgba(200, 200, 200, 60); border: none;")
        self.highlight_frame.hide()

    def get_widget(self):
        return self.text_box

    def resize(self, parent):
        font = SYfont(parent, self.tamano)
        self.text_box.setFont(font)
        self.highlight_frame.hide()

    def _update_highlight(self):
        cursor = self.text_box.textCursor()
        document = self.text_box.document()

        full_text = self.text_box.toPlainText()
        lines = full_text.splitlines()
        cursor_position = cursor.position()

        # Encontrar índice de línea actual
        char_count = 0
        current_line_index = 0
        for i, line in enumerate(lines):
            char_count += len(line) + 1
            if char_count > cursor_position:
                current_line_index = i
                break

        # Determinar inicio y fin del bloque (como antes)
        start = current_line_index
        while start > 0 and lines[start - 1].strip() != "":
            start -= 1

        end = current_line_index
        while end < len(lines) - 1 and lines[end + 1].strip() != "":
            end += 1

        if start > end:
            self.highlight_frame.hide()
            return

        # Obtener posición visual del bloque en viewport
        start_block = document.findBlockByNumber(start)
        end_block = document.findBlockByNumber(end)

        cursor_start = QTextCursor(start_block)
        cursor_end = QTextCursor(end_block)
        cursor_end.movePosition(QTextCursor.EndOfBlock)

        rect_start = self.text_box.cursorRect(cursor_start)
        rect_end = self.text_box.cursorRect(cursor_end)

        # Crear un QRect que encierre el bloque completo
        top = rect_start.top()
        height = rect_end.bottom() - rect_start.top()
        width = self.text_box.viewport().width()

        block_rect = QRect(0, top, width, height)
        self.highlight_frame.setGeometry(block_rect)
        self.highlight_frame.show()

    def get_verse(self):
        full_text = self.text_box.toPlainText()
        lines = full_text.splitlines()

        cursor = self.text_box.textCursor()
        cursor_position = cursor.position()

        if cursor.block().text().strip() == "":
            self.highlight_frame.hide()
            return ""

        char_count = 0
        current_line_index = 0
        for i, line in enumerate(lines):
            char_count += len(line) + 1
            if char_count > cursor_position:
                current_line_index = i
                break

        start = current_line_index
        while start > 0 and lines[start - 1].strip() != "":
            start -= 1

        end = current_line_index
        while end < len(lines) - 1 and lines[end + 1].strip() != "":
            end += 1
            
        texto_seleccionado = "\n".join(lines[start:end + 1]).strip()
        self._update_highlight()
        return texto_seleccionado
    
class SYcombobox:
    def __init__(self, parent, opciones, tamano = SY.VFONT_2):
        self.tamano = tamano
        self.combo = QComboBox()
        for opcion in opciones:
            self.combo.addItem(opcion)
        
        font = SYfont(parent, tamano)
        self.combo.setFont(font)
        
    def get_widget(self):
        return self.combo
    
    def resize(self, parent):
        font = SYfont(parent, self.tamano)
        self.combo.setFont(font)
    
class SYcbfont:
    def __init__(self, parent,opciones, tamano = SY.VFONT_2):
        self.tamano = tamano
        self.combo = QComboBox()
    
        for i, opcion in enumerate(opciones):
            fuente_opcion = QFont(opcion)
            self.combo.addItem(opcion)
            self.combo.setItemData(i, fuente_opcion, Qt.FontRole)
            
        font = SYfont(parent, tamano)
        self.combo.setFont(font)
        self.update_style(opciones[0])
    
    def get_widget(self):
        return self.combo

    def resize(self, parent):
        font = SYfont(parent, self.tamano)
        self.combo.setFont(font)
        self.update_style(self.combo.currentText())

    def update_style(self, estilo):
        
        if estilo in ["Georgia", "Times New Roman", "Arial", "Verdana", "Impact", "Tahoma"]:
            font = self.combo.font()
            font.setFamily(estilo)
            self.combo.setFont(font)
            
class SYtoolbar:
    def __init__(self,parent,botones, tipo, orientacion, textos=None, tamano = SY.VFONT_2, forma = SY.TEXT, nombre=None,icon = None,alineacion=None, al_texto=None):
        self.tipo = tipo
        self.icon = icon
        self.orientacion = orientacion
        self.tamano = tamano
        self._parpadeo_color = True
        if tipo == SY.FRAME:
            self.button_container = QFrame()
            if orientacion == SY.V:
                button_layout = QVBoxLayout()
            else:
                button_layout = QHBoxLayout()
            self.button_container.setLayout(button_layout)
            if alineacion:
                button_layout.setAlignment(alineacion)
            
            
        elif tipo == SY.WIDGET:
            self.button_container = QWidget(parent)
            if orientacion == SY.V:
                button_layout = QVBoxLayout()
            else:
                button_layout = QHBoxLayout()
            self.button_container.setLayout(button_layout)
            if alineacion:
                button_layout.setAlignment(alineacion)
            button_layout.setSpacing(0)
            button_layout.setContentsMargins(0,0,0,0)
        
        self.button_list = []
        self.labels = []
        for i in range(botones):
            if i < len(textos):
                
                button = CustomToolButton(textos[i],forma,self.button_container,None,orientacion,nombre)
                button.setFont(SYfont(parent, self.tamano))
                if al_texto:
                    label = SYlabel(parent, textos[i].strip(),self.tamano).get_widget()
                    layout = SYgrid(1,2,[1],[0,1], None, (5,0,0,0))
                    #label.setAlignment(Qt.AlignBottom)
                    if icon:
                        icono = SYlabel(parent,icon[i], imagen=True, tipo="svg").get_widget()
                        icono.setAlignment(Qt.AlignVCenter)
                        layout.add_element([[icono,0,0]])
                    layout.add_element([[label,0,1]])
                    
                    button.setLayout(layout)
                    self.labels.append(label)
                if orientacion == SY.V:
                    button_layout.addWidget(button,1)
                else:
                    button_layout.addWidget(button)
                self.button_list.append(button)    
        
        if orientacion == SY.V:
            lista_alturas = [btn.sizeHint().height() for btn in self.button_list]
            altura_max = max(lista_alturas)

            for btn in self.button_list:
                btn.setFixedHeight(altura_max)
        
        self.palette_original = self.button_list[0].palette()
        
    
    def get_widgets(self):
        return self.button_container, self.button_list

    def collapse(self):
        for button in self.button_list:
            button.resize_modify = False
            button.setFixedSize(10,10)
    
    def resize(self, parent):
        for button in self.button_list:
            # Restaurar tamaño expansible
            button.setMinimumSize(0, 0)
            button.setMaximumSize(16777215, 16777215)
            button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            button.resize_modify = True
            # Reaplicar fuente si es necesario
            if not self.icon:
                button.setFont(SYfont(parent, self.tamano))
            # Forzar resizeEvent manualmente con nuevo tamaño
            new_size = button.sizeHint()
            button.resize(new_size)
            button.resizeEvent(QResizeEvent(new_size, button.size()))
            
        if self.labels:
            for label in self.labels:
                label.setFont(SYfont(parent, self.tamano))

        # 3. Recalcular altura uniforme si orientación es vertical
        if self.orientacion == SY.V:
            lista_alturas = [btn.sizeHint().height() for btn in self.button_list]
            altura_max = max(lista_alturas)
            for btn in self.button_list:
                btn.setFixedHeight(altura_max)

        # 4. Restaurar paleta si es necesario
        self.palette_original = self.button_list[0].palette()

        # 5. Reactivar layout
        self.button_container.layout().invalidate()
        self.button_container.layout().activate()
        self.button_container.updateGeometry()
                
    def blink_botton(self, botton, condition):
        if condition is None:
            self.button_list[botton].setPalette(self.palette_original)
            self.button_list[botton].update()
            return

        color = self.palette_original.color(QPalette.Button) if self._parpadeo_color else self.palette_original.color(QPalette.Highlight)
        pal = self.button_list[botton].palette()
        pal.setColor(QPalette.Button, color)
        self.button_list[botton].setPalette(pal)
        self.button_list[botton].update()

        self._parpadeo_color = not self._parpadeo_color
        
    def switch_button(self, botton, condition):
        color = self.palette_original.color(QPalette.Button) if not condition else self.palette_original.color(QPalette.Highlight)
        pal = self.button_list[botton].palette()
        pal.setColor(QPalette.Button, color)
        self.button_list[botton].setPalette(pal)
        self.button_list[botton].update()

class SYbuttonbox:
    def __init__(self,parent,botones, tipo, orientacion, textos=None, tamano = SY.VFONT_2, forma = SY.TEXT, nombre=None,icon = False,alineacion=None, al_texto=None):
        self.tipo = tipo
        self.icon = icon
        self.orientacion = orientacion
        self.tamano = tamano
        self._parpadeo_color = True
        if tipo == SY.FRAME:
            self.button_container = QFrame()
            if orientacion == SY.V:
                button_layout = QVBoxLayout()
            else:
                button_layout = QHBoxLayout()
            self.button_container.setLayout(button_layout)
            if alineacion:
                button_layout.setAlignment(alineacion)
            
            
        elif tipo == SY.WIDGET:
            self.button_container = QWidget(parent)
            if orientacion == SY.V:
                button_layout = QVBoxLayout()
            else:
                button_layout = QHBoxLayout()
            self.button_container.setLayout(button_layout)
            if alineacion:
                button_layout.setAlignment(alineacion)
            button_layout.setSpacing(0)
            button_layout.setContentsMargins(0,0,0,0)
        
        self.button_list = []
        self.labels = []
        for i in range(botones):
            if i < len(textos):
                if icon == True:
                    button = CustomToolButton("",forma,self.button_container,textos[i],orientacion,nombre)
                else:
                    button = CustomToolButton(textos[i],forma,self.button_container,None,orientacion,nombre)
                    button.setFont(SYfont(parent, self.tamano))
                    if al_texto:
                        label = SYlabel(parent, textos[i].strip(),self.tamano).get_widget()
                        label.setAlignment(al_texto)
                        layout = QHBoxLayout()
                        layout.addWidget(label)
                        button.setLayout(layout)
                        self.labels.append(label)
                if orientacion == SY.V:
                    button_layout.addWidget(button,1)
                else:
                    button_layout.addWidget(button)
                self.button_list.append(button)    
        
        if orientacion == SY.V:
            lista_alturas = [btn.sizeHint().height() for btn in self.button_list]
            altura_max = max(lista_alturas)

            for btn in self.button_list:
                btn.setFixedHeight(altura_max)
        
        self.palette_original = self.button_list[0].palette()
        
    
    def get_widgets(self):
        return self.button_container, self.button_list

    def collapse(self):
        for button in self.button_list:
            button.resize_modify = False
            button.setFixedSize(10,10)
    
    def resize(self, parent):
        for button in self.button_list:
            # Restaurar tamaño expansible
            button.setMinimumSize(0, 0)
            button.setMaximumSize(16777215, 16777215)
            button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            button.resize_modify = True
            # Reaplicar fuente si es necesario
            if not self.icon:
                button.setFont(SYfont(parent, self.tamano))
            # Forzar resizeEvent manualmente con nuevo tamaño
            new_size = button.sizeHint()
            button.resize(new_size)
            button.resizeEvent(QResizeEvent(new_size, button.size()))
            
        if self.labels:
            for label in self.labels:
                label.setFont(SYfont(parent, self.tamano))

        # 3. Recalcular altura uniforme si orientación es vertical
        if self.orientacion == SY.V:
            lista_alturas = [btn.sizeHint().height() for btn in self.button_list]
            altura_max = max(lista_alturas)
            for btn in self.button_list:
                btn.setFixedHeight(altura_max)

        # 4. Restaurar paleta si es necesario
        self.palette_original = self.button_list[0].palette()

        # 5. Reactivar layout
        self.button_container.layout().invalidate()
        self.button_container.layout().activate()
        self.button_container.updateGeometry()
                
    def blink_botton(self, botton, condition):
        if condition is None:
            self.button_list[botton].setPalette(self.palette_original)
            self.button_list[botton].update()
            return

        color = self.palette_original.color(QPalette.Button) if self._parpadeo_color else self.palette_original.color(QPalette.Highlight)
        pal = self.button_list[botton].palette()
        pal.setColor(QPalette.Button, color)
        self.button_list[botton].setPalette(pal)
        self.button_list[botton].update()

        self._parpadeo_color = not self._parpadeo_color
        
    def switch_button(self, botton, condition):
        color = self.palette_original.color(QPalette.Button) if not condition else self.palette_original.color(QPalette.Highlight)
        pal = self.button_list[botton].palette()
        pal.setColor(QPalette.Button, color)
        self.button_list[botton].setPalette(pal)
        self.button_list[botton].update()
               
class SYmenu:
    def __init__(self, parent, nombre, acciones, tamano = SY.VFONT_1):
        self.menu = QMenu(nombre,parent)
        self.actions = []
        self.tamano = tamano
        for action_name in acciones:
            if isinstance(action_name,str):
                action = QAction(action_name,parent)
                self.menu.addAction(action)
                self.actions.append(action)
            elif isinstance(action_name,QMenu):
                self.menu.addMenu(action_name)
        
        font = SYfont(parent,tamano)
        self.menu.setFont(font)
    
    def get_widgets(self):
        return self.menu, self.actions
    
    def resize(self, parent):
        font = SYfont(parent,self.tamano)
        self.menu.setFont(font)
        
class SYmenubar:
    def __init__(self, parent, opciones, acciones, tamano = SY.SFONT_2):
        self.tamano = tamano
        self.menubar = QMenuBar(parent)
        self.list_menus = []
        self.list_actions_bymenu = []
        
        for i, menu_name in enumerate(opciones):
            menu_inst = SYmenu(parent,menu_name,acciones[i])
            self.list_menus.append(menu_inst)
            self.menubar.addMenu(menu_inst.menu)
            self.list_actions_bymenu.append(menu_inst.actions)
            
        #self.menubar.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        font = SYfont(parent,tamano)
        self.menubar.setFont(font)
    
    def get_widgets(self):
        return self.menubar, self.list_actions_bymenu
    
    def resize(self, parent):
        font = SYfont(parent,self.tamano)
        self.menubar.setFont(font)
        
        for menu in self.list_menus:
            menu.resize(parent)
    
class SYtreeview:
    def __init__(self, parent ,num_columnas, tamano = SY.VFONT_3):
        self.tamano = tamano
        self.treeview = CustomTreeView()
        font = SYfont(parent,tamano)
        self.treeview.setFont(font)
        self.treeview.setEditTriggers(QTreeView.NoEditTriggers)
        self.model = QStandardItemModel()
        self.model.setColumnCount(num_columnas)
        self.treeview.setModel(self.model)
        self.treeview.setSortingEnabled(False)
        self.treeview.setAlternatingRowColors(True)
        self.treeview.setIndentation(0)
        self.treeview.header().setVisible(False)
        self.treeview.setSelectionBehavior(QTreeView.SelectRows)
        self.treeview.expandAll()
        
    def get_widgets(self):
        return self.treeview, self.model
    
    def get_proxy_model(self, columna_clave = 0):
        self.model_proxy = QSortFilterProxyModel()
        self.model_proxy.setSourceModel(self.model)
        self.model_proxy.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.model_proxy.setFilterKeyColumn(columna_clave)
        self.treeview.setModel(self.model_proxy)
        return self.model_proxy
    
    def resize(self, parent):
        font = SYfont(parent,self.tamano)
        self.treeview.setFont(font)
    
    def add_elements(self, *elementos, strip = False, columna_fit = 0):
        self.model.clear()

        if len(elementos) > 1:
            for row_data in zip(*elementos):
                items = [QStandardItem(e.strip() if strip else e) for e in row_data]
                self.model.appendRow(items)
            self.treeview.header().setSectionResizeMode(columna_fit, QHeaderView.ResizeToContents)

        elif len(elementos) == 1:
            for elemento in elementos[0]:
                item = QStandardItem(elemento.strip() if strip else elemento)
                self.model.appendRow([item])
        
    def set_context_menu(self,menu):
        self.treeview.setContextMenuPolicy(Qt.CustomContextMenu)
        self.treeview.customContextMenuRequested.connect(menu)
    def get_list(self):
        elements = []
        for row in range(self.model.rowCount()):
            item = self.model.item(row)
            if item is not None:
                elements.append(item.text())
        return elements
     
class SYprojection:
    def __init__(self, parent):
        self.original_size = None
        self.ruta_imagen = None
        self.factor = 1
        self.alignment_h = Qt.AlignHCenter
        self.alignment_v = Qt.AlignVCenter
        self.font = "Georgia"
        self.cursiva = False
        self.negrita = False
        self.versicle = Versicle()
        self.song = Song()
        self.element = None
        
        
        self.container = QWidget()
        self.container.setObjectName("proyeccion")
        self.container.setContentsMargins(0,0,0,0)
        self.container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        
        self.imagen_widget = QLabel("")
        self.imagen_widget.setObjectName("simulacion")
        self.imagen_widget.setAlignment(self.alignment_h | self.alignment_v)
        self.imagen_widget.setContentsMargins(0,0,0,0)
        self.imagen_widget.setWordWrap(True)
        
        self.video_widget = QVideoWidget()
        self.audio_widget = QAudioOutput()
        self.media_player = QMediaPlayer()
        self.media_player.setVideoOutput(self.video_widget)
        self.media_player.setAudioOutput(self.audio_widget)
        
        self.layout= QVBoxLayout()
        self.layout.addWidget(self.imagen_widget,0, Qt.AlignCenter)
        
        self.layout.setContentsMargins(0,0,0,0)
        self.container.setLayout(self.layout)
        
        self.video_widget.hide()
        self.imagen_widget.show()
        
    def get_widgets(self):
        return self.container, self.imagen_widget
    
    def get_other_widget(self):
        self.media = Media()
        self.layout.addWidget(self.video_widget,0, Qt.AlignCenter)
        return self.media_player, self.audio_widget
    
    def collapse(self):
        self.imagen_widget.setFixedSize(10,10)
        self.video_widget.setFixedSize(10,10)
    
    def resize(self, parent, secundaria=False):
        if secundaria == False:
            container_width = int(self.container.width() *0.8)
            container_height = int(self.container.height() *0.9)
        else:
            pantalla_secundaria = SYwindowextra()
            container_height = pantalla_secundaria.height()
            container_width = pantalla_secundaria.width()
            
        screens = QGuiApplication.screens()
        if len(screens) > 1:
            pantalla_secundaria_ratio = SYwindowextra()
            screen_width = pantalla_secundaria_ratio.width()
            screen_height = pantalla_secundaria_ratio.height()
            aspect_ratio = screen_width / screen_height
        else:
            aspect_ratio = 16 / 9

        new_width = container_width
        new_height = int(new_width / aspect_ratio)
        
        if new_height > container_height:
            new_height = container_height
            new_width = int(new_height * aspect_ratio)

        if new_width > container_width:
            new_width = container_width
            new_height = int(new_width / aspect_ratio)
        
        self.imagen_widget.setFixedSize(new_width, new_height)
        self.video_widget.setFixedSize(new_width, new_height)

        self.original_size = round(new_height/40)
        font = SYfont(parent, self.original_size)
        self.imagen_widget.setFont(font)
        
        font_modify = self.imagen_widget.font()
        font_modify.setFamily(self.font)
        font_modify.setPointSize(int(self.original_size * self.factor))
        font_modify.setItalic(self.cursiva)
        font_modify.setBold(self.negrita)
        self.imagen_widget.setFont(font_modify)
        
        
        
    def update_versicle(self, object):
        if isinstance(object,list):
            self.versicle.versicle = object[0].sibling(object[0].row(), 0).data()
            self.versicle.text = object[0].sibling(object[0].row(), 1).data()
        else:
            self.versicle.versicle = object.versicle
            self.versicle.text = object.text
        self.element = SY.VERSICLE
    
    def update_song(self, object):
        attributes = ["titulo", "letra", "fuente" ,"factor", "cursiva", "negrita", "alineacion_vertical", "alineacion_horizontal", "fondo_url"]
        if isinstance(object, str):
            for attr, value in zip(attributes, get_song_by_title(object)):
                setattr(self.song, attr, value)
        else:
            for attr, value in zip(attributes, object.to_list()):
                setattr(self.song, attr, value)
        self.element = SY.SONG
        
    def update_media(self, object):
        if not isinstance(object, Media):
            self.media.item = object
            self.media.name = os.path.basename(self.media.item.data(Qt.UserRole))
        else:
            self.media.item = object.item
            self.media.name = object.name
        self.element = SY.MEDIA
        
    def play_media(self, item, mute):
        ruta_media = item.data(Qt.UserRole)
        ruta_media = ruta_media.replace("\\", "/")
        self.current_media = ruta_media

        if SYmediarecognize(self.current_media):
            self.imagen_widget.show()
            self.video_widget.hide()
            self.media_player.stop()
            
            pixmap = QPixmap(self.current_media)
            self.imagen_widget.setPixmap(pixmap.scaled(self.imagen_widget.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            self.imagen_widget.hide()
            self.video_widget.show()
        
            self.media_player.setSource(QUrl.fromLocalFile(self.current_media))
            self.audio_widget.setMuted(mute)
            
            
    def show_media(self, negro, fondo):
        if negro == True:
            self.imagen_widget.show()
            self.video_widget.hide()
        else:
            self.imagen_widget.hide()
            self.video_widget.show()
            
        if fondo == True:
            self.audio_widget.setMuted(True)
        else:
            self.audio_widget.setMuted(False)
    
    def update_style(self, estilo):
        
        if estilo in ["Georgia", "Times New Roman", "Arial", "Verdana", "Impact", "Tahoma"]:
            font = self.imagen_widget.font()
            font.setFamily(estilo)
            self.font = estilo
            self.imagen_widget.setFont(font)
            
        elif isinstance(estilo, float):
            self.factor = estilo
            font = self.imagen_widget.font()
            new_size = self.original_size * self.factor
            font.setPointSize(int(new_size))
            self.imagen_widget.setFont(font)
            
        elif estilo == "c":
            font = self.imagen_widget.font()
            font.setItalic(not font.italic())
            self.cursiva = font.italic()
            self.imagen_widget.setFont(font)
            
        elif estilo == "n":
            font = self.imagen_widget.font()
            font.setBold(not font.bold())
            self.negrita = font.bold()
            self.imagen_widget.setFont(font)
            
        elif isinstance(estilo, Qt.AlignmentFlag):
            if estilo in [Qt.AlignLeft, Qt.AlignHCenter,Qt.AlignRight]:
                self.alignment_h = estilo
            else:
                self.alignment_v = estilo
            self.imagen_widget.setAlignment(self.alignment_h | self.alignment_v)
    
    def update_background(self, item, edicion = False):
        if isinstance(item, str):
            self.ruta_imagen = item
        else:
            self.ruta_imagen = item.data(Qt.UserRole).replace("\\", "/")
              
        if self.ruta_imagen == "negro":
            estilo = """
                border-image: none;
                background-color: black;
                color: black;
            """
        else:
            if self.ruta_imagen == "None":
                ruta_exponer = cargar_fondo_predeterminado()
                if not os.path.exists(ruta_exponer):
                    editar_fondo_predeterminado("None")
            else:
                ruta_exponer = self.ruta_imagen
                
            if os.path.exists(ruta_exponer):
                text_color = SYcolorselector(ruta_exponer)
                estilo = f"""
                    border-image: url('{ruta_exponer}') 0 0 0 0 stretch stretch;
                    color: {text_color};
                """
            else:
                estilo = """
                    border-image: none;
                    color: white;
                """
        self.imagen_widget.setStyleSheet(estilo)
        if edicion == True:
            font_modify = self.imagen_widget.font()
            font_modify.setFamily(self.font)
            font_modify.setPointSize(int(self.original_size * self.factor))
            font_modify.setItalic(self.cursiva)
            font_modify.setBold(self.negrita)
            self.imagen_widget.setFont(font_modify)
        
    def load_song(self, estado=False):
        self.imagen_widget.show()
        self.video_widget.hide()
        self.media_player.stop()
            
        self.update_background(self.song.fondo_url) if estado == False else self.update_background("negro")
        
        self.update_style(SYalignmap(self.song.alineacion_vertical))
        self.update_style(SYalignmap(self.song.alineacion_horizontal))
        
        self.update_style(self.song.fuente)
        self.update_style(float(self.song.factor))
        
        if self.song.cursiva != self.imagen_widget.font().italic():
            self.update_style("c")
        if self.song.negrita != self.imagen_widget.font().bold():
            self.update_style("n")
            
        
    
    def load_versicle(self,biblia,negro=False, fondo=False):
        self.imagen_widget.show()
        self.video_widget.hide()
        self.media_player.stop()
        
        versiculo= f"{self.versicle.text}({biblia.split('_')[0]})\n{self.versicle.versicle}"
        
        longitud_versiculo = max(40, min(len(versiculo), 480))
        normalizado = (longitud_versiculo - 30) / (480 - 30)
        factor = 2.8 - (normalizado * 1)
        
        self.update_background("None") if negro == False else self.update_background("negro")
        
        self.update_style("Georgia")
        self.update_style(float(factor))
        self.update_style(Qt.AlignVCenter)
        self.update_style(Qt.AlignHCenter)
        if False != self.imagen_widget.font().italic():
            self.update_style("c")
        if False != self.imagen_widget.font().bold():
            self.update_style("n")
        
        self.set_text(versiculo,negro, fondo)   
        
    def load_media(self, mute = True, negro=False, fondo=False):
        if negro==True:
            self.play_media(self.media.item,mute) if fondo == False else self.play_media(self.media.item, True)
            self.imagen_widget.show()
            self.video_widget.hide()
            self.update_background("negro")
            self.imagen_widget.setText(".")
        else:
            self.update_background("negro")
            self.imagen_widget.setText(".")
            self.update_style(Qt.AlignVCenter)
            self.update_style(Qt.AlignHCenter)  
            self.play_media(self.media.item,mute) if fondo == False else self.play_media(self.media.item, True)
        
            
    def set_text(self, texto, negro, fondo):
        if negro==True or fondo == True:
            self.imagen_widget.setText(".")  if negro == True else self.imagen_widget.setText("") 
        else:
            self.imagen_widget.setText(texto)
            
    def sync_media(self, media_player_to_sync, state):
        if not SYmediarecognize(self.media.item):
            self.media_player.setPosition(media_player_to_sync.position())
            if state == QMediaPlayer.PlaybackState.PlayingState:
                self.media_player.play()
            elif state == QMediaPlayer.PlaybackState.PausedState:
                self.media_player.pause()
            elif state == QMediaPlayer.PlaybackState.StoppedState:
                self.media_player.stop()
      
class SYbackgroundslist:
    def __init__(self, parent, tamano = SY.VFONT_1):
        self.tamano = tamano
        self.menu = QMenu(parent)
        widget_list = QWidget()
        widget_layout = QVBoxLayout(widget_list)
        
        self.image_list = QListWidget()
        self.image_list.setViewMode(QListWidget.IconMode)
        self.image_list.setDragEnabled(False)
        self.image_list.setAcceptDrops(False)
        self.image_list.setDragDropMode(QAbstractItemView.NoDragDrop)
        self.image_list.setDefaultDropAction(Qt.IgnoreAction)
        self.image_list.setEditTriggers(QAbstractItemView.NoEditTriggers)
        
        height = parent.screen().geometry().height()
        self.icon_size = int(height/11)
        self.image_list.setIconSize(QSize(self.icon_size, self.icon_size))

        widget_layout.addWidget(self.image_list)
        
        self.button = QToolButton()
        self.fuente = SYfont(parent, self.tamano)
        self.button.setFont(self.fuente)
        self.button.setText("Agregar fondo")
        
        self.image_list.setFont(self.fuente)
        widget_layout.addWidget(self.button)
        
        widget_action = QWidgetAction(self.menu)
        widget_action.setDefaultWidget(widget_list)
        
        self.menu.addAction(widget_action)
        
        self.refresh_list()
        
    def get_widgets(self):
        return self.menu, self.image_list, self.button
    
    def resize(self, parent):
        height = parent.screen().geometry().height()
        icon_size = int(height/11)
        self.image_list.setIconSize(QSize(icon_size, icon_size))
        self.fuente = SYfont(parent, self.tamano)
        self.button.setFont(self.fuente)
        self.image_list.setFont(self.fuente)
    
    def refresh_list(self):
        self.image_list.clear()
        
        icon_negro = SYcreate_icon("None", self.icon_size)
        item_ninguno = QListWidgetItem(icon_negro, "Ninguno")
        item_ninguno.setData(Qt.UserRole, "None")
        self.image_list.addItem(item_ninguno)
        
        ruta = SYpathcreater("backgrounds")
        carpeta_fondos = os.path.abspath(ruta)
        extensiones_validas = [".png", ".jpg", ".jpeg", ".bmp"]
        max_length = 10
        for archivo in os.listdir(carpeta_fondos):
            nombre, extension = os.path.splitext(archivo)
            if len(nombre) > max_length:
                nombre_mostrado = nombre[:max_length] + "..."
            else:
                nombre_mostrado = nombre
                
            if any(archivo.lower().endswith(ext) for ext in extensiones_validas):
                ruta_completa = os.path.join(carpeta_fondos, archivo)
                icon = SYcreate_icon(ruta_completa, self.icon_size)
                item = QListWidgetItem(icon, nombre_mostrado)
                item.setData(Qt.UserRole, ruta_completa)
                self.image_list.addItem(item)
    
    def add_background(self, parent):
        ruta_imagen, _ = QFileDialog.getOpenFileName(parent, "Seleccionar Imagen", "", "Imágenes (*.png *.jpg *.jpeg *.bmp *.gif)")
        ruta = SYpathcreater("backgrounds")
        carpeta_fondos = os.path.abspath(ruta)
        if ruta_imagen:
            nombre_archivo = os.path.basename(ruta_imagen)
            destino = os.path.join(carpeta_fondos, nombre_archivo)

            if os.path.exists(destino):
                base, ext = os.path.splitext(nombre_archivo)
                i = 1
                while os.path.exists(os.path.join(carpeta_fondos, f"{base}_{i}{ext}")):
                    i += 1
                destino = os.path.join(carpeta_fondos, f"{base}_{i}{ext}")

            try:
                max_width = cargar_resolucion_actual()
                with Image.open(ruta_imagen) as img:
                    if img.width > max_width:
                        ratio = max_width / img.width
                        new_size = (max_width, int(img.height * ratio))
                        img = img.resize(new_size, Image.LANCZOS)
                        img.save(destino)
                    else:
                        shutil.copy(ruta_imagen, destino)
            except Exception as e:
                msg = SYmessagebox(parent,QMessageBox.Warning, "No se pudo guardar la imagen", "El reescalado o proceso de copiado fallo", QMessageBox.Ok)
                msg.exec_()
                
            self.refresh_list()
                  
class SYmedialist:
    def __init__(self, parent, tamano = SY.VFONT_1):
        
        self.tamano = tamano
       
        self.widget_list = QWidget()
        self.widget_list.setObjectName("Fondo")
        widget_layout = QVBoxLayout(self.widget_list)
        
        self.image_list = QListWidget()
        self.image_list.setViewMode(QListWidget.IconMode)
        self.image_list.setDragEnabled(False)
        self.image_list.setAcceptDrops(False)
        self.image_list.setDragDropMode(QAbstractItemView.NoDragDrop)
        self.image_list.setDefaultDropAction(Qt.IgnoreAction)
        self.image_list.setEditTriggers(QAbstractItemView.NoEditTriggers)
        
        height = parent.screen().geometry().height()
        self.icon_size = int(height/11)
        self.image_list.setIconSize(QSize(self.icon_size, self.icon_size))

        widget_layout.addWidget(self.image_list)
        
        self.button = QToolButton()
        self.fuente = SYfont(parent, self.tamano)
        self.button.setFont(self.fuente)
        self.button.setText("Carpeta raiz")
        
        self.image_list.setFont(self.fuente)
        
        widget_layout.addWidget(self.button)
        self.carpeta_raiz = cargar_carpeta_raiz()
        self.refresh_list()
        
        
    def get_widgets(self):
        return self.widget_list, self.image_list, self.button
    
    def resize(self, parent):
        height = parent.screen().geometry().height()
        icon_size = int(height/11)
        self.fuente = SYfont(parent, self.tamano)
        self.image_list.setIconSize(QSize(icon_size, icon_size))
        self.image_list.setFont(self.fuente)
        self.button.setFont(self.fuente)
    
    def refresh_list(self):
        self.image_list.clear()
        if self.carpeta_raiz == "None":
            return
        if os.path.exists(self.carpeta_raiz): 
            extensiones_imagenes = [".png", ".jpg", ".jpeg", ".bmp"]
            extensiones_videos = [".mp4", ".avi", ".mov", ".mkv"]
            max_length = 10
            
            for archivo in os.listdir(self.carpeta_raiz):
                ruta_completa = os.path.join(self.carpeta_raiz, archivo)
                archivo_lower = archivo.lower()
                
                if len(archivo) > max_length:
                    nombre_mostrado = archivo[:max_length] + "..."
                else:
                    nombre_mostrado = archivo
                icon = None
                
                if any(archivo_lower.endswith(ext) for ext in extensiones_imagenes):
                    # Procesamiento de imagenes (generar miniatura)
                    icon = SYcreate_icon(ruta_completa, self.icon_size)
                elif any(archivo_lower.endswith(ext) for ext in extensiones_videos):
                    # Procesamiento de videos (generar miniatura)
                    icon = SYcreate_icon(ruta_completa, self.icon_size, SY.VIDEO)
                if icon is not None:
                    item = QListWidgetItem(icon, nombre_mostrado)
                    item.setData(Qt.UserRole, ruta_completa)
                    self.image_list.addItem(item)
        else:
            editar_carpeta_raiz("None")
    
    def change_root_media(self):
        directorio_inicial = self.carpeta_raiz if os.path.exists(self.carpeta_raiz) else os.path.expanduser("~/Desktop")

        carpeta_seleccionada = QFileDialog.getExistingDirectory(None, "Seleccionar Carpeta", directorio_inicial)

        if carpeta_seleccionada:
            self.carpeta_raiz = carpeta_seleccionada
            editar_carpeta_raiz(self.carpeta_raiz)
            self.refresh_list()

class SYvideocontrol:
    def __init__(self, parent):
        self.control_inst =    SYbuttonbox(parent,3,SY.WIDGET,SY.H,["▶ Play","⏸ Pause","⏹ Stop"])
        self.control_ctn, self.control_btn = self.control_inst.get_widgets()
        
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(0, 100)
        self.time_label_inst = SYlabel(parent, "00:00 / 00:00")    
        self.time_label = self.time_label_inst.get_widget()
        
        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(50)
        self.volume_label_inst = SYlabel(parent, "Vol:")
        self.volume_label = self.volume_label_inst.get_widget()
        
        
        self.container = QWidget()
        layout = QVBoxLayout()
        control_layout = SYgrid(1,3, [1], [18,0,5], [[self.control_ctn,0,0], [self.volume_label, 0, 1, Qt.AlignVCenter], [self.volume_slider, 0,2]])
        time_layout = SYgrid(1,2,[1], [7,1], [[self.slider,0,0], [self.time_label, 0, 1]])
        
        layout.addLayout(time_layout)
        layout.addLayout(control_layout)
        
        self.container.setLayout(layout)
        
    def get_widgets(self):
        return self.container, self.control_btn, self.slider, self.volume_slider
    
    def resize(self, parent):
        self.control_inst.resize(parent)
        self.time_label_inst.resize(parent)
        self.volume_label_inst.resize(parent)
        
    def update_position(self, position, media_player):
        self.slider.setValue(position)
        self.update_time_label(media_player)
    
    def update_duration(self, duration, media_player):
        self.slider.setRange(0, duration)
        self.update_time_label(media_player)
        
    def update_time_label(self, media_player):
        position = media_player.position() // 1000
        duration = media_player.duration() // 1000
        self.time_label.setText(f"{position // 60:02}:{position % 60:02} / {duration // 60:02}:{duration % 60:02}")