from PySide6.QtSvg import QSvgRenderer
from PySide6.QtGui import QFont, QColor, QPixmap, QPainter, QIcon, QImage
from PySide6.QtCore import Qt, QRect
import cv2
from core.models import SY
from core.helpers import SYpathcreater

def SYfont(parent, font_size):
    
    reference_height=1080
    min_size=6
    max_size=72
    
    base_size = font_size.value if not isinstance(font_size, int) else font_size
    
    screen = parent.screen()
    screen_height = screen.geometry().height()
    logical_dpi = screen.logicalDotsPerInch()
    
    scale_factor = (screen_height / reference_height) * (96 / logical_dpi)
    
    scaled_size = max(min(int(base_size * scale_factor), max_size), min_size)
    
    new_font = QFont("Segoe UI")
    new_font.setWeight(QFont.Bold)
    #new_font.setBold(True)
    new_font.setPointSize(scaled_size)
    return new_font


def SYcolorselector(ruta_imagen):
    pixmap = QPixmap(ruta_imagen)
    image = pixmap.toImage()
    image_width, image_height = image.width(), image.height()
    total_pixels = image_width * image_height
    min_samples = 1000
    step = max(1,int((total_pixels/ min_samples) ** 0.5))
    total_luminance = 0
    pixel_count = 0
    
    for x in range(0, image_width, step):
        for y in range(0, image_height, step):
            color = QColor(image.pixel(x,y))
            r,g,b = color.red(), color.green(), color.blue()
            
            luminance = 0.299 * r + 0.587 * g + 0.114 * b
            total_luminance += luminance
            pixel_count += 1
    
    image_luminance = total_luminance / pixel_count if pixel_count > 0 else 255
    text_color = "black" if image_luminance > 128 else "white"
    
    return text_color

def SYcreate_icon(ruta_imagen, tamano, tipo = SY.IMAGE):
    if tipo == SY.IMAGE:
        if ruta_imagen == "None":
            pixmap = QPixmap(tamano,int(tamano*0.56))
            pixmap.fill(Qt.black)
        else:
            pixmap = QPixmap(ruta_imagen)  
    else:
        try:
            cap = cv2.VideoCapture(ruta_imagen)
            ret, frame = cap.read()
            if ret:
                # Convertir frame de OpenCV a QPixmap
                height, width, channel = frame.shape
                bytes_per_line = 3 * width
                q_img = QImage(frame.data, width, height, bytes_per_line, QImage.Format_RGB888).rgbSwapped()
                pixmap = QPixmap.fromImage(q_img)
            cap.release()
        except Exception as e:
            icon_video_svg_path = SYpathcreater( "icons", "video.svg", temporal= True)
            pixmap = QPixmap(tamano, tamano)
            pixmap.fill(Qt.black)
            painter = QPainter(pixmap)
            svg_renderer = QSvgRenderer(icon_video_svg_path)
            svg_renderer.render(painter, QRect(30, 30, 40, 40))
            painter.end()
            
    pixmap = pixmap.scaled(tamano,tamano,Qt.KeepAspectRatio,Qt.SmoothTransformation)    
            
    final_pixmap = QPixmap(tamano,tamano)
    final_pixmap.fill(Qt.transparent)
    
    painter = QPainter(final_pixmap)
    x = (tamano - pixmap.width()) // 2
    y = (tamano - pixmap.height()) // 2
    painter.drawPixmap(x,y,pixmap)
    painter.end()
    
    icon = QIcon(final_pixmap)
    return icon
