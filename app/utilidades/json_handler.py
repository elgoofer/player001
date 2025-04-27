# -*- coding: utf-8 -*-
"""
Módulo con funciones de utilidad para leer y escribir archivos JSON.
"""

import json
import os
import typing # Para type hints

# Definir un tipo genérico para los datos que esperamos leer/escribir
# En nuestro caso, será principalmente list[str] para las rutas.
TipoDatosJson = typing.TypeVar('TipoDatosJson')

def guardar_json(ruta_archivo: str, datos: TipoDatosJson) -> bool:
    """
    Guarda los datos proporcionados en un archivo JSON.

    Sobrescribe el archivo si ya existe.

    Args:
        ruta_archivo (str): Ruta completa donde se guardará el archivo JSON.
        datos (TipoDatosJson): Los datos (ej. lista, diccionario) a guardar.

    Returns:
        bool: True si se guardó correctamente, False en caso de error.
    """
    try:
        # Asegurarse de que el directorio exista
        directorio = os.path.dirname(ruta_archivo)
        if directorio and not os.path.exists(directorio):
            os.makedirs(directorio) # Crear directorios intermedios si no existen

        # Escribir el archivo JSON con codificación UTF-8 y sangría para legibilidad
        with open(ruta_archivo, 'w', encoding='utf-8') as f:
            json.dump(datos, f, ensure_ascii=False, indent=4)
        print(f"Datos guardados exitosamente en: {ruta_archivo}")
        return True
    except IOError as e:
        print(f"Error de E/S al guardar JSON en '{ruta_archivo}': {e}")
    except TypeError as e:
        # Esto podría ocurrir si 'datos' no es serializable a JSON
        print(f"Error de tipo al serializar datos a JSON: {e}")
    except Exception as e:
        print(f"Error inesperado al guardar JSON en '{ruta_archivo}': {e}")
    return False

def cargar_json(ruta_archivo: str) -> TipoDatosJson | None:
    """
    Carga datos desde un archivo JSON.

    Args:
        ruta_archivo (str): Ruta completa del archivo JSON a leer.

    Returns:
        TipoDatosJson | None: Los datos cargados desde el archivo, o None
                              si el archivo no existe o hay un error al leer/parsear.
    """
    if not os.path.exists(ruta_archivo) or not os.path.isfile(ruta_archivo):
        print(f"Error: El archivo JSON no existe o no es un archivo: {ruta_archivo}")
        return None

    datos_cargados = None
    try:
        # Leer el archivo JSON con codificación UTF-8
        with open(ruta_archivo, 'r', encoding='utf-8') as f:
            datos_cargados = json.load(f)
        print(f"Datos cargados exitosamente desde: {ruta_archivo}")
        return datos_cargados
    except json.JSONDecodeError as e:
        print(f"Error al decodificar JSON desde '{ruta_archivo}': {e}")
    except IOError as e:
        print(f"Error de E/S al cargar JSON desde '{ruta_archivo}': {e}")
    except Exception as e:
        print(f"Error inesperado al cargar JSON desde '{ruta_archivo}': {e}")

    return None # Devolver None si ocurrió algún error