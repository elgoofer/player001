# -*- coding: utf-8 -*-
"""
Punto de entrada principal para la aplicación Radio Anarkadia.

Este script inicializa la aplicación Qt (PySide6) y muestra la ventana principal.
"""

import sys
# Necesario para manejar la aplicación gráfica y sus eventos.
from PySide6.QtWidgets import QApplication

# Importaremos la ventana principal desde nuestro módulo de GUI.
# Asegúrate de que la estructura de directorios sea:
# Radio Anarkadia/
# ├── app/
# │   ├── gui/
# │   │   ├── __init__.py
# │   │   └── ventana_principal.py  <-- Debe existir
# │   └── __init__.py
# ├── radio_anarkadia.py            <-- Este archivo
# └── requirements.txt
try:
    from app.gui.ventana_principal import VentanaPrincipal
except ModuleNotFoundError:
    # Mensaje de error más detallado
    print("----------------------------------------------------")
    print("ERROR: No se pudo importar 'VentanaPrincipal'.")
    print("Verifica lo siguiente:")
    print("1. Que exista el archivo: app/gui/ventana_principal.py")
    print("2. Que existan los archivos: app/__init__.py y app/gui/__init__.py")
    print("3. Que estés ejecutando 'python radio_anarkadia.py' desde")
    print("   el directorio raíz 'Radio Anarkadia/'.")
    print("----------------------------------------------------")
    # Imprime la ruta de búsqueda de módulos de Python para depuración
    print("\nRutas de búsqueda de Python (sys.path):")
    for ruta in sys.path:
        print(f"- {ruta}")
    print("----------------------------------------------------")
    sys.exit(1) # Salir si no se puede importar lo esencial.
except ImportError as e:
    # Captura otros posibles errores de importación
    print(f"----------------------------------------------------")
    print(f"ERROR: Ocurrió un problema al importar:")
    print(f"{e}")
    print(f"Revisa las dependencias y la estructura del proyecto.")
    print(f"----------------------------------------------------")
    sys.exit(1)


def configurar_y_lanzar():
    """
    Prepara e inicia la aplicación gráfica principal.
    """
    aplicacion = QApplication(sys.argv)
    ventana_principal = VentanaPrincipal()
    ventana_principal.show()
    print("Radio Anarkadia iniciada. Esperando eventos...")
    sys.exit(aplicacion.exec())

if __name__ == "__main__":
    print("Lanzando Radio Anarkadia...")
    configurar_y_lanzar()
    # Esta línea solo se alcanzará si aplicacion.exec() termina.
    print("Radio Anarkadia ha finalizado.")