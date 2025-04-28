import os
import random
import tkinter.filedialog as fd
import logging

logger = logging.getLogger(__name__)

def cargar_archivo(playlist, actualizar_callback):
    """
    Permite al usuario seleccionar un archivo de audio y agregarlo a la playlist.
    :param playlist: Objeto de la playlist donde se almacenan las canciones.
    :param actualizar_callback: Función para actualizar la interfaz después de agregar el archivo.
    """
    ruta = fd.askopenfilename(
        title="Selecciona un archivo de audio",
        filetypes=[("Archivos de audio", "*.mp3 *.wav *.ogg")]
    )
    if ruta:
        titulo = os.path.basename(ruta).split(".")[0]  # Extraer el nombre del archivo sin extensión.
        playlist.canciones.append({"ruta": ruta, "titulo": titulo, "duracion": 0})
        actualizar_callback()
    else:
        logger.warning("No se seleccionó ningún archivo.")

def cargar_carpeta(playlist, actualizar_callback):
    """
    Permite al usuario seleccionar una carpeta y agregar todos los archivos de audio a la playlist.
    :param playlist: Objeto de la playlist donde se almacenan las canciones.
    :param actualizar_callback: Función para actualizar la interfaz después de agregar los archivos.
    """
    carpeta = fd.askdirectory(title="Selecciona una carpeta de audio")
    if carpeta:
        for archivo in os.listdir(carpeta):
            if archivo.lower().endswith((".mp3", ".wav", ".ogg")):
                ruta = os.path.join(carpeta, archivo)
                titulo = os.path.splitext(archivo)[0]
                playlist.canciones.append({"ruta": ruta, "titulo": titulo, "duracion": 0})
        actualizar_callback()
    else:
        logger.warning("No se seleccionó ninguna carpeta.")

def guardar_playlist(playlist):
    """
    Permite al usuario guardar la playlist en un archivo de texto.
    :param playlist: Objeto de la playlist que se guardará.
    """
    ruta_guardado = fd.asksaveasfilename(
        title="Guardar playlist",
        defaultextension=".txt",
        filetypes=[("Archivo de texto", "*.txt")]
    )
    if ruta_guardado:
        try:
            with open(ruta_guardado, "w", encoding="utf-8") as archivo:
                for cancion in playlist.canciones:
                    archivo.write(f"{cancion['ruta']}|{cancion['titulo']}|{cancion.get('duracion', 0)}\n")
            logger.info("Playlist guardada en: %s", ruta_guardado)
        except Exception as e:
            logger.exception("Error al guardar la playlist: %s", e)
    else:
        logger.warning("No se especificó una ruta para guardar.")

def cargar_playlist(playlist, actualizar_callback):
    """
    Permite al usuario cargar una playlist desde un archivo de texto.
    :param playlist: Objeto de la playlist donde se cargarán las canciones.
    :param actualizar_callback: Función para actualizar la interfaz después de cargar la playlist.
    """
    ruta = fd.askopenfilename(
        title="Cargar playlist",
        filetypes=[("Archivo de texto", "*.txt")]
    )
    if ruta:
        try:
            with open(ruta, "r", encoding="utf-8") as archivo:
                for linea in archivo:
                    datos = linea.strip().split("|")
                    if len(datos) == 3:
                        ruta_cancion, titulo, duracion = datos
                        playlist.canciones.append({
                            "ruta": ruta_cancion,
                            "titulo": titulo,
                            "duracion": float(duracion)
                        })
            actualizar_callback()
        except Exception as e:
            logger.exception("Error al cargar la playlist: %s", e)
    else:
        logger.warning("No se seleccionó ningún archivo de playlist.")

def eliminar_seleccionado(playlist, seleccionado, actualizar_callback):
    """
    Elimina una canción seleccionada de la playlist.
    :param playlist: Objeto de la playlist.
    :param seleccionado: Índice de la canción seleccionada.
    :param actualizar_callback: Función para actualizar la interfaz después de eliminar la canción.
    """
    if seleccionado is not None:
        try:
            eliminado = playlist.canciones.pop(seleccionado)
            logger.info("Eliminado: %s", eliminado.get('titulo', 'Sin título'))
            actualizar_callback()
        except IndexError:
            logger.error("Índice fuera de rango, no se pudo eliminar.")
    else:
        logger.warning("No hay elemento seleccionado para eliminar.")

def orden_aleatorio(playlist, actualizar_callback):
    """
    Mezcla las canciones de la playlist en un orden aleatorio.
    :param playlist: Objeto de la playlist.
    :param actualizar_callback: Función para actualizar la interfaz después de mezclar la playlist.
    """
    if playlist.canciones:
        random.shuffle(playlist.canciones)
        actualizar_callback()
        logger.info("Lista mezclada en orden aleatorio.")
    else:
        logger.warning("No hay canciones en la playlist.")
