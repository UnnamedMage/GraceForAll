from PySide6.QtWidgets import QDialog, QApplication, QMessageBox
from PySide6.QtCore import Qt, QEvent, QPoint,QTimer
from components.ui_elements import (SYgrid, SYbuttonbox, SYlineedit, SYprojection, SYlabel,
                             SYcbfont, SYtextedit, SYbackgroundslist, SYmessagebox, QTextCursor)
from core.models import SY
from core.helpers import SYwindowsize, SYalignmap, SYanimationwindow, SYcreatelistinst
from services.db_service import Song, is_title_unique_song, add_song, edit_song, delete_song

class VentanaCancion(QDialog):
    def __init__(self, parent = None, cancion_editar = None):
        super().__init__(parent)
        self.setWindowTitle("Agregar Canción")
        self.setWindowFlags(Qt.Window | Qt.CustomizeWindowHint | Qt.WindowTitleHint | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        SYwindowsize(self, 1.5, 1.5)
        self.cancion_editar = cancion_editar
        self.crear_instancias()
        self.almacenar_widgets()
        self.definir_posicion()
        self.conectar_eventos()
        self.ajustes_iniciales()
    
    def crear_instancias(self):
        self.identificador_inst =   SYlabel(self, "", nombre="encabezado",tamano=SY.SFONT_1)
        self.control_ventana_instE = SYbuttonbox(self,1, SY.WIDGET, SY.H, ["close"],tamano=SY.SFONT_3,forma=SY.SQUARE,nombre="btnencabezado",icon=True)
        
        self.nombre_cancion_inst =  SYlineedit(self,"Nombre de la cancion...",tamano=SY.SFONT_2)
        
        self.selector_fuente_inst = SYcbfont(self,["Georgia", "Times New Roman", "Arial", "Verdana", "Impact", "Tahoma"],tamano=SY.SFONT_2)
        self.selector_tamano_inst = SYcbfont(self,["1.0", "1.5","2.0", "2.5", "3.0"],tamano=SY.SFONT_2)
        self.control_estilo_instE =  SYbuttonbox(self,2, SY.WIDGET, SY.H, ["C", "N"],tamano=SY.SFONT_2,forma=SY.SQUARE)
        self.control_alinh_instE =   SYbuttonbox(self,3, SY.WIDGET, SY.H, ["left","center","right"],tamano=SY.SFONT_2,forma=SY.SQUARE,icon=True)
        self.control_alinv_instE =   SYbuttonbox(self,3, SY.WIDGET, SY.H, ["top","vcenter","bottom"],tamano=SY.SFONT_2,forma=SY.SQUARE,icon=True)
        self.menu_fondos_inst =     SYbackgroundslist(self)
        self.control_fondo_instE =   SYbuttonbox(self,1,SY.WIDGET,SY.H, ["Fondo de pantalla"],tamano=SY.SFONT_2)
        
        self.editor_texto_inst =    SYtextedit(self,"Escriba la cancion aqui...",tamano=SY.SFONT_2)
        self.sim_prevista_instE =    SYprojection(self)
        
        self.control_cancion_instE = SYbuttonbox(self,2,SY.WIDGET, SY.H,["Guardar","Salir"],tamano=SY.SFONT_3,alineacion=Qt.AlignRight)
        
        self.control_borrar_instE =  SYbuttonbox(self, 1, SY.WIDGET, SY.H, ["Borrar"],tamano=SY.SFONT_3)
        
        self.instancia_especial = SYcreatelistinst(self, "_instE")
        self.instancia_normal = SYcreatelistinst(self, "_inst")
        
    def almacenar_widgets(self):
        self.identificador =                                                self.identificador_inst.get_widget()
        self.control_ventana_ctn, self.control_ventana_btn =                self.control_ventana_instE.get_widgets()
        
        self.nombre_cancion =                                               self.nombre_cancion_inst.get_widget()
        
        self.selector_fuente =                                              self.selector_fuente_inst.get_widget()
        self.selector_tamano =                                              self.selector_tamano_inst.get_widget()
        self.control_estilo_ctn, self.control_estilo_btn =                  self.control_estilo_instE.get_widgets()
        self.control_alinh_ctn, self.control_alinh_btn =                    self.control_alinh_instE.get_widgets()
        self.control_alinv_ctn, self.control_alinv_btn =                    self.control_alinv_instE.get_widgets()
        self.menu_fondo_cnt, self.menu_fondo_list, self.menu_fondo_btn =    self.menu_fondos_inst.get_widgets()
        self.control_fondo_cnt, self.control_fondo_btn =                    self.control_fondo_instE.get_widgets()
        
        self.editor_texto =                                                 self.editor_texto_inst.get_widget()
        self.sim_prevista_ctn, self.sim_prevista =                          self.sim_prevista_instE.get_widgets()
        self.control_borrar_ctn, self.control_borrar_btn =                  self.control_borrar_instE.get_widgets()
        self.control_cancion_ctn, self.control_cancion_btn =                self.control_cancion_instE.get_widgets()
        
    def definir_posicion(self):
        self.pie =          SYgrid(1,3,[1],[0,1,0], [[self.control_cancion_ctn, 0,2]])
        self.cuerpo =       SYgrid(1,2,[1],[1,2],[[self.editor_texto,0,0],[self.sim_prevista_ctn,0,1]], (0,0,0,0), 10)
        self.posicion =     SYgrid(1,4,[1],[3,8,8,8], [[self.control_estilo_ctn,0,0,Qt.AlignRight], [self.control_alinh_ctn,0,1,Qt.AlignHCenter],
                                                       [self.control_alinv_ctn,0,2,Qt.AlignHCenter], [self.control_fondo_cnt,0,3,Qt.AlignHCenter]])
        self.fuente =       SYgrid(1,2,[1],[1,2],[[self.selector_fuente,0,0,Qt.AlignVCenter],[self.selector_tamano,0,1,Qt.AlignVCenter]], (0,0,0,0), 10)
        self.barra =        SYgrid(2,2,[1,1],[1,3],[[self.nombre_cancion,0,0, Qt.AlignVCenter], [self.fuente, 1,0], [self.posicion,1,1]], (0,0,0,0), 10)
        self.encabezado =   SYgrid(1,3,[1],[1,32,1],[[self.identificador,0,1, Qt.AlignHCenter],[self.control_ventana_ctn,0,2]])
        self.centro =       SYgrid(3,1,[4,30,4],[1],[[self.barra, 0,0], [self.cuerpo, 1, 0], [self.pie, 2, 0]], (10,10,10,10), 10)
        self.borde =        SYgrid(1,1,[1],[1],[[self.centro,0,0, None, "Fondo"]], (3,3,3,3))
        self.base =         SYgrid(2,1,[2,38],[1],[[self.encabezado, 0,0,None, "encabezado"], [self.borde,1,0, None, "complemento"]], (10,3,10,10))
        self.ventana =      SYgrid(1,1,[1],[1],[[self.base,0,0,None, "base_secundaria"]])
        self.setLayout(self.ventana)
    
    def conectar_eventos(self):
        self.control_ventana_btn[0].clicked.connect(self.cerrar_ventana)
        
        self.selector_fuente.currentIndexChanged.connect(lambda index: (self.sim_prevista_instE.update_style(self.selector_fuente.itemText(index))))
        self.selector_fuente.currentIndexChanged.connect(lambda index: (self.selector_fuente_inst.update_style(self.selector_fuente.itemText(index))))
        self.selector_tamano.currentIndexChanged.connect(lambda: (self.sim_prevista_instE.update_style(float(self.selector_tamano.currentText()))))
        self.control_estilo_btn[0].clicked.connect(lambda: self.sim_prevista_instE.update_style("c"))
        self.control_estilo_btn[1].clicked.connect(lambda: self.sim_prevista_instE.update_style("n"))
        self.control_alinh_btn[0].clicked.connect(lambda: self.sim_prevista_instE.update_style(Qt.AlignLeft))
        self.control_alinh_btn[1].clicked.connect(lambda: self.sim_prevista_instE.update_style(Qt.AlignHCenter))
        self.control_alinh_btn[2].clicked.connect(lambda: self.sim_prevista_instE.update_style(Qt.AlignRight))
        self.control_alinv_btn[0].clicked.connect(lambda: self.sim_prevista_instE.update_style(Qt.AlignTop))
        self.control_alinv_btn[1].clicked.connect(lambda: self.sim_prevista_instE.update_style(Qt.AlignVCenter))
        self.control_alinv_btn[2].clicked.connect(lambda: self.sim_prevista_instE.update_style(Qt.AlignBottom))
        self.menu_fondo_btn.clicked.connect(lambda: self.menu_fondos_inst.add_background(self))
        self.menu_fondo_list.itemClicked.connect(lambda item: self.sim_prevista_instE.update_background(item, True))
        self.menu_fondo_list.itemClicked.connect(lambda: self.menu_fondo_cnt.close())
        self.control_fondo_btn[0].clicked.connect(lambda: self.menu_fondo_cnt.exec_(self.control_fondo_btn[0].mapToGlobal(QPoint(0, self.control_fondo_btn[0].height()))))
        
        #self.editor_texto.textChanged.connect(self.actualizar_sim)
        self.editor_texto.cursorPositionChanged.connect(self.actualizar_sim)
        
        self.control_borrar_btn[0].clicked.connect(self.borrar_cancion)
        
        self.control_cancion_btn[0].clicked.connect(self.guardar)
        self.control_cancion_btn[1].clicked.connect(self.cerrar_ventana)
        
    def ajustes_iniciales(self):
        self.editor_texto.installEventFilter(self)
        self.resize_widgets()
        SYanimationwindow(self)
        
        def selector_modo():
            if self.cancion_editar and self.sim_prevista_instE.original_size:
                self.pie.add_element([[self.control_borrar_ctn,0,0]])
                self.sim_prevista_instE.update_song(self.cancion_editar)
                self.nombre_cancion.setText(self.sim_prevista_instE.song.titulo)
                #self.editor_texto.textChanged.disconnect()
                self.editor_texto.cursorPositionChanged.disconnect()
                self.editor_texto.insertPlainText(self.sim_prevista_instE.song.letra)
                #self.editor_texto.textChanged.connect(self.actualizar_sim)
                self.editor_texto.cursorPositionChanged.connect(self.actualizar_sim)
                self.selector_fuente.setCurrentText(self.sim_prevista_instE.song.fuente)
                self.selector_tamano.setCurrentText(str(float(self.sim_prevista_instE.song.factor)))
                self.sim_prevista_instE.load_song()
                self.identificador.setText(f"Editar ({self.sim_prevista_instE.song.titulo})")
                self.editor_texto.moveCursor(QTextCursor.Start)
            elif self.cancion_editar:
                QTimer.singleShot(500, selector_modo)
            else:
                self.identificador.setText("Agregar nueva cancion")
                
        QTimer.singleShot(500, selector_modo)
                
        
        
            
            
        
   

    def cerrar_ventana(self):
        if self.editor_texto.toPlainText() == "":
            self.close()
        else:
            if self.cancion_editar:
                msg = SYmessagebox(self,QMessageBox.Warning, "No ha guardado ningun cambio", "¿Desea salir de todas formas?", QMessageBox.Yes | QMessageBox.No)
            else:
                msg = SYmessagebox(self,QMessageBox.Warning, "No guardo la cancion", "¿Desea salir de todas formas?", QMessageBox.Yes | QMessageBox.No)
            response = msg.exec_()
            if response == QMessageBox.Yes:
                self.close()
    def actualizar_sim(self):
        #self.editor_texto.textChanged.disconnect()
        self.editor_texto.cursorPositionChanged.disconnect()
        texto = self.editor_texto_inst.get_verse()
        self.sim_prevista_instE.set_text(texto, False,False)
        #self.editor_texto.textChanged.connect(self.actualizar_sim)
        self.editor_texto.cursorPositionChanged.connect(self.actualizar_sim)
    def evento_pegar(self):
        #self.editor_texto.textChanged.disconnect()
        self.editor_texto.cursorPositionChanged.disconnect()
        pasted_text = QApplication.clipboard().text()
        self.editor_texto.insertPlainText(pasted_text)
        #self.editor_texto.textChanged.connect(self.actualizar_sim)
        self.editor_texto.cursorPositionChanged.connect(self.actualizar_sim)
    def guardar(self):
        nuevo_titulo = self.nombre_cancion.text()
        nuevo_letra = self.editor_texto.toPlainText()
        nueva_fuente = self.selector_fuente.currentText()
        nuevo_factor = float(self.selector_tamano.currentText())
        nuevo_cursiva = self.sim_prevista.font().italic()
        nuevo_negrita = self.sim_prevista.font().bold()
        nuevo_alineacion_vertical = SYalignmap(self.sim_prevista_instE.alignment_v)
        nuevo_alineacion_horizontal = SYalignmap(self.sim_prevista_instE.alignment_h)
        nuevo_fondo_url = self.sim_prevista_instE.ruta_imagen
        
        if nuevo_titulo == "":
            msg = SYmessagebox(self,QMessageBox.Warning, "No ha sido nombrada", "Por favor, ingrese un nombre a la cancion para continuar", QMessageBox.Ok)
            msg.exec_()
        elif nuevo_letra == "":
            msg = SYmessagebox(self,QMessageBox.Warning, "No contiene letra", "Por favor, escriba la letra de la cancion para continuar", QMessageBox.Ok)
            msg.exec_()
        else:
            if self.cancion_editar is not None and self.cancion_editar == nuevo_titulo:
                edit_song(
                    old_title=self.cancion_editar,
                    letra=nuevo_letra,
                    fuente=nueva_fuente,
                    factor=nuevo_factor,
                    cursiva=nuevo_cursiva, 
                    negrita=nuevo_negrita,
                    alineacion_vertical=nuevo_alineacion_vertical,
                    alineacion_horizontal=nuevo_alineacion_horizontal,
                    fondo_url=nuevo_fondo_url)
                self.close()
            elif is_title_unique_song(nuevo_titulo):
                if self.cancion_editar:
                    edit_song(
                        old_title=self.cancion_editar,
                        titulo=nuevo_titulo,
                        letra=nuevo_letra,
                        fuente=nueva_fuente,
                        factor=nuevo_factor,
                        cursiva=nuevo_cursiva, 
                        negrita=nuevo_negrita,
                        alineacion_vertical=nuevo_alineacion_vertical,
                        alineacion_horizontal=nuevo_alineacion_horizontal,
                        fondo_url=nuevo_fondo_url)
                    self.close()
                else:
                    cancion = Song(
                        titulo=nuevo_titulo,
                        letra=nuevo_letra,
                        fuente=nueva_fuente,
                        factor=nuevo_factor,
                        cursiva=nuevo_cursiva, 
                        negrita=nuevo_negrita,
                        alineacion_vertical=nuevo_alineacion_vertical,
                        alineacion_horizontal=nuevo_alineacion_horizontal,
                        fondo_url=nuevo_fondo_url)
                    add_song(cancion)
                    self.close()
            else:
                msg = SYmessagebox(self,QMessageBox.Warning, "Ese nombre ya existe", "Por favor, ingrese un nombre diferente a la cancion para continuar", QMessageBox.Ok)
                msg.exec_()
    
    def borrar_cancion(self):
        msg = SYmessagebox(self,QMessageBox.Warning, "La cancion sera borrada", "¿Desea continuar?", QMessageBox.Yes | QMessageBox.No)
        response = msg.exec_()
        if response == QMessageBox.Yes:
            delete_song(self.cancion_editar)
            self.close()

    def eventFilter(self, obj, event):
        if obj == self.editor_texto:
            if event.type() == QEvent.KeyPress and event.key() == Qt.Key_V and event.modifiers() & Qt.ControlModifier:
                self.evento_pegar()
                return True
            elif event.type() == QEvent.Drop:
                self.evento_pegar()
                return True
        return super().eventFilter(obj, event)
    
    def colapsar_widgets(self):
        for instancia in self.instancia_especial:
            if hasattr(instancia, 'collapse'):
                instancia.collapse()
   
    def resize_widgets(self):
        for instancia in self.instancia_normal:
            if hasattr(instancia, 'resize'):
                instancia.resize(self)
                
        def restraso():
            for instancia in self.instancia_especial:
                if hasattr(instancia, 'resize'):
                    instancia.resize(self)
        QTimer.singleShot(1000, restraso)
        
    def update_window(self):
        self.colapsar_widgets()
        def restraso():
            SYwindowsize(self, 1.5, 1.5)
            self.layout().invalidate()
            self.layout().activate()
            self.update()
            self.resize_widgets()
        QTimer.singleShot(500, restraso)
            
        
        