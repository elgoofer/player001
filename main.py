import logging
from gui import RadioGUI
from player import AudioPlayer
from playlist import PlaylistManager

# Configuración básica del logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def main():
    try:
        player = AudioPlayer()
        # Inicializamos el PlaylistManager sin pasar "playlist.txt"
        playlist = PlaylistManager()  
        app = RadioGUI(player, playlist)
        app.iniciar()  # Arranca la interfaz y la comprobación continua de fin de tema
    except Exception as e:
        logger.exception("Error al iniciar la aplicación")

if __name__ == '__main__':
    main()
