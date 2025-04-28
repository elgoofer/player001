import vlc
import os
import logging

logger = logging.getLogger(__name__)

class AudioPlayer:
    def __init__(self):
        # Crea una instancia de VLC y un reproductor
        self.instance = vlc.Instance()
        self.player = self.instance.media_player_new()
        self.is_paused = False

    def reproducir(self, cancion):
        """
        Carga y reproduce la canción indicada.
        Se espera que 'cancion' sea un diccionario con la clave "ruta".
        """
        if not cancion:
            logger.warning("No hay canción para reproducir.")
            return
        ruta = cancion.get("ruta")
        if not ruta or not os.path.isfile(ruta):
            logger.error("El archivo no existe o la ruta es inválida: %s", ruta)
            return
        media = self.instance.media_new(ruta)
        self.player.set_media(media)
        self.player.play()
        self.is_paused = False

    def pausar(self):
        # Alterna entre pausar y reanudar
        self.player.pause()
        self.is_paused = not self.is_paused

    def detener(self):
        self.player.stop()
        self.is_paused = False

    def get_time(self):
        """
        Retorna el tiempo actual de reproducción en segundos.
        """
        ms = self.player.get_time()
        if ms < 0:
            return 0
        return ms / 1000.0

    def get_length(self):
        """
        Retorna la duración total del tema en segundos.
        """
        ms = self.player.get_length()
        if ms < 0:
            return 0
        return ms / 1000.0

    def set_time(self, seconds):
        """
        Fija la posición de reproducción (en segundos).
        """
        try:
            self.player.set_time(int(seconds * 1000))
        except Exception as e:
            logger.error("Error al establecer la posición: %s", e)

    def is_playing(self):
        """
        Retorna True si hay una reproducción en curso.
        """
        return self.player.is_playing() == 1
