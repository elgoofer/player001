import logging
from mutagen import File as MutagenFile

logger = logging.getLogger(__name__)

def extract_metadata(file_path):
    """
    Extrae la metadata de un archivo de audio.

    Parámetros:
        file_path (str): Ruta del archivo de audio.

    Retorna:
        dict: Un diccionario con las claves 'title', 'artist' y 'album'.
              Si alguna entrada no está disponible, se asigna "Desconocido".
    """
    try:
        metadata = MutagenFile(file_path, easy=True)
        if metadata:
            title = metadata.get("title", ["Desconocido"])[0]
            artist = metadata.get("artist", ["Desconocido"])[0]
            album = metadata.get("album", ["Desconocido"])[0]
            return {"title": title, "artist": artist, "album": album}
        else:
            logger.warning("No se encontró metadata para el archivo: %s", file_path)
            return {"title": "Desconocido", "artist": "Desconocido", "album": "Desconocido"}
    except Exception as e:
        logger.exception("Error al extraer metadata del archivo %s: %s", file_path, e)
        return {"title": "Desconocido", "artist": "Desconocido", "album": "Desconocido"}
