# -*- coding: utf-8 -*-
"""
Módulo con funciones de utilidad para el manejo de archivos y directorios.
"""

import os

# Formatos de audio aceptados por defecto.
# Podría leerse de una configuración en el futuro.
FORMATOS_AUDIO_POR_DEFECTO = ['.mp3', '.ogg', '.wav', '.flac']

def buscar_archivos_audio_en_carpeta(
    ruta_carpeta: str,
    formatos_aceptados: list[str] = None,
    recursivo: bool = True
) -> list[str]:
    """
    Busca archivos de audio con los formatos especificados en una carpeta.

    Args:
        ruta_carpeta (str): La ruta a la carpeta donde buscar.
        formatos_aceptados (list[str], optional): Lista de extensiones
            (ej. ['.mp3', '.flac']). Si es None, usa los formatos por defecto.
            Defaults to None.
        recursivo (bool, optional): Si es True, busca también en subcarpetas.
            Defaults to True.

    Returns:
        list[str]: Una lista ordenada de rutas completas a los archivos
                   de audio encontrados. Lista vacía si no se encuentran.
                   Devuelve None si la ruta_carpeta no es válida.
    """
    if not os.path.isdir(ruta_carpeta):
        print(f"Error: La ruta proporcionada no es un directorio válido: {ruta_carpeta}")
        return None # Indicar que la ruta no era válida

    archivos_encontrados = []
    formatos = formatos_aceptados if formatos_aceptados is not None else FORMATOS_AUDIO_POR_DEFECTO
    # Convertir a minúsculas para comparación insensible a mayúsculas
    formatos_lower = [f.lower() for f in formatos]

    if recursivo:
        # Búsqueda recursiva
        for raiz, _, nombres_archivos in os.walk(ruta_carpeta):
            for nombre in nombres_archivos:
                # Obtener extensión de forma segura
                _, ext = os.path.splitext(nombre)
                if ext.lower() in formatos_lower:
                    ruta_completa = os.path.join(raiz, nombre)
                    archivos_encontrados.append(ruta_completa)
    else:
        # Búsqueda solo en el directorio raíz especificado
        try:
            for nombre in os.listdir(ruta_carpeta):
                ruta_completa = os.path.join(ruta_carpeta, nombre)
                if os.path.isfile(ruta_completa):
                    _, ext = os.path.splitext(nombre)
                    if ext.lower() in formatos_lower:
                        archivos_encontrados.append(ruta_completa)
        except OSError as e:
            print(f"Error al listar directorio {ruta_carpeta}: {e}")
            return [] # Devolver lista vacía en caso de error de lectura

    return sorted(archivos_encontrados) # Devolver lista ordenada


def obtener_directorio_padre(ruta: str) -> str | None:
    """
    Obtiene la ruta del directorio padre de un archivo o carpeta.

    Args:
        ruta (str): Ruta del archivo o carpeta.

    Returns:
        str | None: Ruta del directorio padre, o None si no se puede determinar
                    (ej. si la ruta es la raíz '/').
    """
    try:
        # os.path.dirname devuelve el directorio padre
        directorio_padre = os.path.dirname(ruta)
        # En la raíz, dirname puede devolver la misma ruta o '', manejarlo
        if directorio_padre == ruta or not directorio_padre:
            # Podríamos devolver la misma ruta raíz si es '/' o 'C:\'
            # o None para indicar que no hay un "padre" en el sentido usual.
            # Devolver None parece más claro para el uso en diálogos.
            return None
        return directorio_padre
    except Exception as e:
        print(f"Error obteniendo directorio padre de '{ruta}': {e}")
        return None

# Podrían añadirse más funciones de utilidad de archivos aquí...