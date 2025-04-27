# -*- coding: utf-8 -*-
"""
Módulo con funciones de utilidad para el manejo de información de audio.
SIMPLIFICADO: Solo obtiene la duración de los archivos.
"""
import os
import typing # Mantenemos typing para type hints si es necesario

try:
    import mutagen
    # Ya no necesitamos las clases 'Easy...' específicas
except ImportError:
    print("ADVERTENCIA: La biblioteca 'mutagen' no está instalada.")
    print("             La obtención de duración no estará disponible.")
    print("             Ejecutá: pip install mutagen")
    mutagen = None

# Ya no se necesita el tipo MetadatosAudio

def obtener_duracion_ms(ruta_archivo: str) -> int:
    """
    Obtiene la duración en milisegundos de un archivo de audio usando mutagen.

    Args:
        ruta_archivo (str): La ruta completa al archivo de audio.

    Returns:
        int: La duración en milisegundos, o 0 si no se puede obtener
             (mutagen no disponible, archivo no existe, error de lectura, etc.).
    """
    # Chequeo inicial si mutagen está disponible y el archivo existe
    if not mutagen:
        # Ya se mostró advertencia al importar si mutagen no está
        return 0
    if not os.path.exists(ruta_archivo) or not os.path.isfile(ruta_archivo):
        # Evitar mensajes de error si el archivo simplemente no está
        # print(f"DEBUG Duración: Archivo no encontrado o no es archivo: '{os.path.basename(ruta_archivo)}'")
        return 0

    duracion_ms = 0
    nombre_base = os.path.basename(ruta_archivo) # Útil para logs de error
    # print(f"--- Intentando obtener duración para: {nombre_base}") # Log verboso opcional

    try:
        # Intentar abrir el archivo con mutagen
        info_audio = mutagen.File(ruta_archivo, easy=False) # easy=False por si acaso, aunque no debería afectar la duración

        # Verificar si se pudo abrir y si tiene información de duración
        if info_audio and hasattr(info_audio, 'info') and hasattr(info_audio.info, 'length'):
            duracion_segundos = info_audio.info.length
            # print(f"    Mutagen info.length: {duracion_segundos} (tipo: {type(duracion_segundos)})") # Verboso

            # Validar que la duración sea un número positivo
            if duracion_segundos and isinstance(duracion_segundos, (int, float)) and duracion_segundos > 0:
                duracion_ms = int(duracion_segundos * 1000)
                # print(f"    Duración calculada: {duracion_ms} ms") # Verboso
            # else:
                # print(f"    Duración inválida o cero desde mutagen para '{nombre_base}'.") # Verboso
        # else:
            # print(f"    Mutagen no encontró 'info.length' para '{nombre_base}'.") # Verboso

    except mutagen.MutagenError as e_mut:
        # Error específico de mutagen (ej. formato no soportado, archivo corrupto)
        print(f"    ADVERTENCIA: Error de Mutagen al leer duración de '{nombre_base}': {e_mut}")
    except Exception as e:
        # Otros errores inesperados durante la lectura
        print(f"    ERROR: Error inesperado al obtener duración de '{nombre_base}': {e}")

    # print(f"--- Duración final devuelta para {nombre_base}: {duracion_ms} ms") # Verboso
    return duracion_ms

# Eliminada la función obtener_metadatos_basicos

def formatear_tiempo_ms(milisegundos: int) -> str:
    """
    Formatea una duración en milisegundos al formato MM:SS.

    Args:
        milisegundos (int): La duración en milisegundos.

    Returns:
        str: La duración formateada como "MM:SS". Devuelve "00:00" si es 0 o negativo.
    """
    # Esta función no parece usarse directamente por los widgets principales,
    # pero la mantenemos por si es útil en otro lado o para futuras refactorizaciones.
    if milisegundos <= 0:
        return "00:00"
    # Calcular total de segundos redondeando (importante para precisión)
    total_segundos = round(milisegundos / 1000)
    minutos = total_segundos // 60
    segundos = total_segundos % 60
    # Formatear con ceros a la izquierda si es necesario
    return f"{minutos:02d}:{segundos:02d}"

# --- Fin del archivo app/utilidades/audio.py ---