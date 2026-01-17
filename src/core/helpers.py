from PySide6.QtWidgets import QGraphicsOpacityEffect
from PySide6.QtGui import QColor,QPalette
from PySide6.QtCore import Qt, QRect,  QPropertyAnimation, QEasingCurve, QParallelAnimationGroup, QPoint
import win32api # type: ignore
import os
import sys
from pathlib import Path
import traceback
from datetime import datetime

def SYcreatelistinst(parent, endswith):
    instacias = [getattr(parent, attr) for attr in dir(parent) if attr.endswith(endswith)]
    return instacias

def SYanimationwindow(parent, opacity_time = 2000, pos_time = 1500):
    # Animación de opacidad (fade-in)
    opacity_effect = QGraphicsOpacityEffect(parent)
    parent.setGraphicsEffect(opacity_effect)
    
    opacity_anim = QPropertyAnimation(opacity_effect, b"opacity")
    opacity_anim.setDuration(opacity_time)
    opacity_anim.setStartValue(0)
    opacity_anim.setEndValue(1)
    opacity_anim.setEasingCurve(QEasingCurve.InOutCubic)
    
    # Animación de movimiento (desplazamiento desde arriba)
    pos_anim = QPropertyAnimation(parent, b"pos")
    pos_anim.setDuration(pos_time)
    pos_anim.setStartValue(parent.pos() - QPoint(0, 50))
    pos_anim.setEndValue(parent.pos())
    pos_anim.setEasingCurve(QEasingCurve.OutBack)
    
    # Grupo de animaciones (ejecutar en paralelo)
    parent.animation_group = QParallelAnimationGroup()
    parent.animation_group.addAnimation(opacity_anim)
    parent.animation_group.addAnimation(pos_anim)
    parent.animation_group.start()
    
def SYwindowsize(parent, proporcion_x, proporcion_y):
    main_geometry = SYwindoworigen()
    main_width = main_geometry.width()
    main_height = main_geometry.height()
    main_x = main_geometry.x()
    main_y = main_geometry.y()
     
    new_width = int(main_width / proporcion_x)
    new_height = int(main_height / proporcion_y)
    parent.resize(new_width, new_height)
    new_x = main_x + (main_width - parent.width()) // 2
    new_y = main_y + (main_height - parent.height()) // 2
        
    parent.move(new_x, new_y)

def SYalignmap(alineacion):
    if isinstance(alineacion, str):
        mapa_alineacion = {
                "AlignLeft":Qt.AlignLeft,
                "AlignHCenter":Qt.AlignHCenter,
                "AlignRight":Qt.AlignRight,
                "AlignTop":Qt.AlignTop,
                "AlignVCenter":Qt.AlignVCenter,
                "AlignBottom":Qt.AlignBottom,
            }
    else:
        mapa_alineacion = {
                Qt.AlignLeft:"AlignLeft",
                Qt.AlignHCenter:"AlignHCenter",
                Qt.AlignRight:"AlignRight",
                Qt.AlignTop:"AlignTop",
                Qt.AlignVCenter:"AlignVCenter",
                Qt.AlignBottom:"AlignBottom",
            }
    return mapa_alineacion.get(alineacion, "")

def SYmediarecognize(item):
    if isinstance(item, str):
        ruta_media = item
    else:
        ruta_media = item.data(Qt.UserRole)
        ruta_media = ruta_media.replace("\\", "/")
    if ruta_media.lower().endswith(('.png', '.jpg', '.jpeg')):
        return True
    else:
        return False
    
def SYwindoworigen():
    monitor_info = win32api.GetMonitorInfo(win32api.MonitorFromPoint((0, 0)))
    work_area = monitor_info['Work']
    work_area_width = work_area[2] - work_area[0]
    work_area_height = work_area[3] - work_area[1]
    geometria_disponible = QRect(0,0,work_area_width,work_area_height)
    return geometria_disponible

def SYwindowextra(secundaria = False):
    monitores = win32api.EnumDisplayMonitors()
    
    if len(monitores) <= 1 and secundaria == True:
        return None
    
    monitor_info_salida = win32api.GetMonitorInfo(monitores[1][0]) 
    
    screen_area = monitor_info_salida['Monitor']  # Resolución total (incluye barra de tareas si es la primaria)
    screen_width = screen_area[2] - screen_area[0]
    screen_height = screen_area[3] - screen_area[1]
    
    geometria_disponible = QRect(0, 0, screen_width, screen_height)
    
    monitor_info = win32api.GetMonitorInfo(win32api.MonitorFromPoint((0, 0)))
    work_area = monitor_info['Monitor']
    work_area_width = work_area[2] - work_area[0]
    work_area_height = work_area[3] - work_area[1]
    geometria_principal = QRect(0,0,work_area_width,work_area_height)
    
    if geometria_disponible.height() == geometria_principal.height():
        monitor_info_salida2 = win32api.GetMonitorInfo(monitores[0][0])
        screen_area2 = monitor_info_salida2['Monitor']  # Resolución total (incluye barra de tareas si es la primaria)
        screen_width2 = screen_area2[2] - screen_area2[0]
        screen_height2 = screen_area2[3] - screen_area2[1]
        
        geometria_alternativa = QRect(0, 0, screen_width2, screen_height2)
        return geometria_alternativa
    else:    
        return geometria_disponible

def SYpathcreater(*args, temporal = False):
    if getattr(sys, 'frozen', False):
        if temporal == True:
            BASE_DIR = sys._MEIPASS
        else:
            BASE_DIR = Path.home() / 'AppData' / 'Local' / 'GraceForAll'
            
        path = os.path.join(BASE_DIR, *args)   
    else:
        path = os.path.join("assets",*args)
        
    return path

def aclarar(color, factor=1):
    c = QColor(color)
    return c.lighter(int(factor * 100)).name()

def oscurecer(color, factor=0.9):
    c = QColor(color)
    return c.darker(int(factor * 100)).name()

def SYerror(exctype, value, tb):
    fecha = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    if getattr(sys, 'frozen', False):
        base_path = os.path.dirname(sys.executable)
        archivo_error = os.path.join(base_path, f"GraceForALL_error_{fecha}.log")   
    else:
        archivo_error = f"GraceForALL_error_{fecha}.log"

    with open(archivo_error, "w", encoding="utf-8") as f:
        f.write("¡Ocurrió un error inesperado!\n\n")
        traceback.print_exception(exctype, value, tb, file=f)

    # También podrías notificar al usuario, cerrar recursos, etc.
    print(f"Error guardado en {archivo_error}")