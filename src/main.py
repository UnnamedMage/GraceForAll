import sys, ctypes, os
from PySide6.QtCore import QSharedMemory
from views.main_window import VentanaPrincipal
from views.loading_window import VentanaCarga
from core.helpers import SYerror
from core.application import SYApplication

def GraceForAll():
    #Deshabilitar escalado de DPI
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except:
        pass
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(0)
    except:
        pass
    
    #Deshabilitar aceleración de hardware y escalado de DPI
    os.environ["QT_ENABLE_HARDWARE_ACCELERATION"] = "0"
    os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "0"
    os.environ["QT_SCALE_FACTOR"] = "1"
    
    #Deshabilitar mensajes de error
    try:
        devnull = os.open(os.devnull, os.O_WRONLY)
        os.dup2(devnull, sys.stderr.fileno()) 
    except:
        pass
    
    #Crear aplicación
    aplicacion = SYApplication(sys.argv)
    
    #Crear bloqueo de memoria compartida
    shared_memory = QSharedMemory("mi_app_unica")
    if shared_memory.attach():
        print("Otra instancia ya está en ejecución. Saliendo...")
        sys.exit(0)
    if not shared_memory.create(1):  
        print("No se pudo crear el bloqueo.")
        sys.exit(1)
        
    #Crear ventana de carga
    splash = VentanaCarga()
    splash.show()
    
    #Iniciar aplicación
    aplicacion.start()
    ventana = VentanaPrincipal(aplicacion)
    ventana.show()
    
    #Cerrar ventana de carga
    splash.cerrar(ventana)
    
    #Configurar excepción
    sys.excepthook = SYerror
    
    #Ejecutar aplicación
    sys.exit(aplicacion.exec())
    
if __name__ == "__main__":
    GraceForAll()