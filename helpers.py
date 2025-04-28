import logging

logger = logging.getLogger(__name__)

def format_time(seconds):
    """
    Convierte un tiempo en segundos a formato MM:SS o HH:MM:SS si es mayor a 1 hora.
    """
    try:
        seconds = int(seconds)
    except (TypeError, ValueError) as e:
        logger.error("Error al convertir los segundos (%s): %s", seconds, e)
        return "00:00"
        
    if seconds >= 3600:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        return f"{hours:02}:{minutes:02}:{secs:02}"
    else:
        minutes = seconds // 60
        secs = seconds % 60
        return f"{minutes:02}:{secs:02}"

def calculate_total_duration(playlist):
    """
    Calcula la duración total de una lista de reproducción.
    :param playlist: Lista de canciones, cada una representada como un diccionario con la clave 'duracion'.
    :return: Duración total en segundos.
    """
    total = 0
    for song in playlist:
        try:
            duration = float(song.get("duracion", 0))
        except (ValueError, TypeError) as e:
            logger.error("Error al convertir la duración de la canción %s: %s", song, e)
            duration = 0
        total += duration
    return total
