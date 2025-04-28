# playlist.py

import os
import glob
import logging

logger = logging.getLogger(__name__)

class PlaylistManager:
    def __init__(self, archivo_lista=None):
        """
        Inicializa el manejador de la lista de reproducción.
        :param archivo_lista: Ruta al archivo de texto con la lista. Cada línea debe tener:
                              titulo,duracion (en segundos),ruta_del_archivo
        """
        self.canciones = []    # Lista de canciones (cada canción es un diccionario)
        self.actual_index = 0  # Índice de la canción actual en reproducción
        if archivo_lista:
            self.cargar_lista(archivo_lista)

    def cargar_lista(self, archivo):
        """
        Carga las canciones desde un archivo de texto.
        Cada línea del archivo debe tener el siguiente formato:
        titulo,duracion,ruta
        """
        try:
            with open(archivo, 'r', encoding='utf-8') as f:
                for linea in f:
                    linea = linea.strip()
                    if not linea:
                        continue  # Ignoramos líneas vacías
                    datos = linea.split(',')
                    if len(datos) >= 3:
                        try:
                            # Se espera que la duración sea numérica (en segundos)
                            duracion = float(datos[1])
                        except ValueError:
                            logger.error("Duración inválida en la línea: %s", linea)
                            continue
                        cancion = {
                            'titulo': datos[0].strip(),
                            'duracion': duracion,
                            'ruta': datos[2].strip()
                        }
                        self.canciones.append(cancion)
                    else:
                        logger.warning("Línea ignorada (formato insuficiente): %s", linea)
        except Exception as e:
            logger.exception("Error al cargar la lista: %s", e)

    def agregar_archivo(self, ruta_archivo, duracion=0):
        """
        Agrega un archivo único a la playlist.
        :param ruta_archivo: Ruta del archivo de audio.
        :param duracion: Duración en segundos (opcional, se puede obtener con otras librerías).
        """
        if os.path.isfile(ruta_archivo):
            titulo = os.path.basename(ruta_archivo)
            cancion = {
                'titulo': titulo,
                'duracion': duracion,  # Se puede dejar en 0 o intentar obtenerla mediante otras librerías
                'ruta': ruta_archivo
            }
            self.canciones.append(cancion)
            logger.info("Agregado: %s", titulo)
        else:
            logger.error("El archivo %s no existe.", ruta_archivo)

    def agregar_archivos_desde_carpeta(self, carpeta, extensiones=None):
        """
        Agrega todos los archivos de audio de la carpeta especificada.
        :param carpeta: Ruta de la carpeta.
        :param extensiones: Lista de extensiones a considerar (por defecto: mp3, wav, ogg)
        """
        if extensiones is None:
            extensiones = ["*.mp3", "*.wav", "*.ogg"]
        if os.path.isdir(carpeta):
            for ext in extensiones:
                patron = os.path.join(carpeta, ext)
                for ruta_archivo in glob.glob(patron):
                    self.agregar_archivo(ruta_archivo)
        else:
            logger.error("El directorio %s no existe.", carpeta)

    def guardar_playlist(self, archivo_destino):
        """
        Guarda la playlist actual en un archivo de texto.
        Cada línea se guarda en el formato: titulo,duracion,ruta
        :param archivo_destino: Ruta del archivo donde guardar la playlist.
        """
        try:
            with open(archivo_destino, 'w', encoding='utf-8') as f:
                for cancion in self.canciones:
                    linea = f"{cancion['titulo']},{cancion['duracion']},{cancion['ruta']}\n"
                    f.write(linea)
            logger.info("Playlist guardada en %s", archivo_destino)
        except Exception as e:
            logger.exception("Error al guardar la playlist: %s", e)

    def obtener_cancion_actual(self):
        """
        Devuelve la canción actual para reproducir.
        """
        if self.canciones:
            return self.canciones[self.actual_index]
        return None

    def siguiente_cancion(self):
        """
        Avanza al siguiente tema en la lista, si existe.
        Retorna la nueva canción actual.
        """
        if self.canciones and self.actual_index < len(self.canciones) - 1:
            self.actual_index += 1
            return self.obtener_cancion_actual()
        logger.info("No hay más canciones en la lista.")
        return None

    def anterior_cancion(self):
        """
        Retrocede a la canción anterior en la lista, si es posible.
        Retorna la nueva canción actual.
        """
        if self.canciones and self.actual_index > 0:
            self.actual_index -= 1
            return self.obtener_cancion_actual()
        logger.info("Esta es la primera canción de la lista.")
        return None

    def duracion_total(self):
        """
        Calcula la duración total de la lista de reproducción sumando las duraciones de todas las canciones.
        :return: Duración total en segundos.
        """
        return sum(cancion['duracion'] for cancion in self.canciones)

    def agregar_cancion(self, cancion):
        """
        Agrega una canción a la playlist.
        Se espera que 'cancion' sea un diccionario con las claves 'titulo', 'duracion' y 'ruta'.
        """
        if isinstance(cancion, dict) and all(k in cancion for k in ('titulo', 'duracion', 'ruta')):
            self.canciones.append(cancion)
        else:
            logger.error("La canción no tiene el formato correcto.")

    def reset(self):
        """
        Reinicia el índice de la canción actual a 0.
        """
        self.actual_index = 0
