# -*- coding: utf-8 -*-
"""
Módulo que encapsula la lógica para gestionar el volumen "AIRE"
y el efecto de fade entre 100% y 20%.
"""

import typing
if typing.TYPE_CHECKING:
    # Para type hints, evitando importación circular real
    from .reproductor_audio import ReproductorAudio
    from ..gui.ventana_principal import VentanaPrincipal
    from ..gui.componentes.controles_reproduccion_widget import ControlesReproduccionWidget
    from .manejador_acciones import ManejadorAcciones # Necesario para llamar a _actualizar_boton_aire_ventana

# Importar QTimer y QObject/Slot
from PySide6.QtCore import QObject, QTimer, Slot

# Constantes copiadas de ManejadorAcciones
ESTADO_AIRE_100 = "a_100"
ESTADO_AIRE_20 = "a_20"
VOLUMEN_AIRE_100 = 1.0
VOLUMEN_AIRE_20 = 0.2
DURACION_FADE_MS = 500     # Duración total del fade en milisegundos
INTERVALO_FADE_MS = 25     # Intervalo del timer para actualizar el fade

class GestorVolumenAire(QObject):
    """
    Gestiona el estado del volumen AIRE (100% o 20%) y aplica
    un fade suave entre los dos estados.
    """
    def __init__(self,
                 reproductor: 'ReproductorAudio',
                 manejador_acciones: 'ManejadorAcciones', # Necesario para actualizar botón y slider
                 parent: QObject | None = None):
        """
        Inicializa el gestor de volumen AIRE.

        Args:
            reproductor: La instancia del reproductor de audio.
            manejador_acciones: La instancia del manejador principal para callbacks.
            parent: El objeto padre Qt (opcional).
        """
        super().__init__(parent)
        self.reproductor = reproductor
        self.manejador_acciones = manejador_acciones # Guardar referencia

        # Estado interno
        self.estado_aire_actual: str = ESTADO_AIRE_100
        self.volumen_objetivo_aire: float = VOLUMEN_AIRE_100
        self.volumen_actual_fade: float = VOLUMEN_AIRE_100 # Asumir inicial en 100%
        self.paso_volumen_fade: float = 0.0

        # Timer para el fade
        self.timer_volumen_aire = QTimer(self)
        self.timer_volumen_aire.setInterval(INTERVALO_FADE_MS)
        self.timer_volumen_aire.timeout.connect(self._actualizar_fade_volumen)

        print("GestorVolumenAire inicializado.")

    @property
    def estado_actual(self) -> str:
        """Devuelve el estado AIRE actual ('a_100' o 'a_20')."""
        return self.estado_aire_actual

    # --- Métodos públicos ---

    @Slot()
    def alternar_volumen_aire(self):
        """
        Inicia el proceso para cambiar al otro estado AIRE (100% <-> 20%)
        con un efecto de fade.
        """
        print("DEBUG GestorAire: Iniciando alternar_volumen_aire...")
        if not self.reproductor:
            print("ERROR GestorAire: No hay reproductor.")
            return

        # Determinar el nuevo estado y volumen objetivo
        nuevo_estado = ESTADO_AIRE_20 if self.estado_aire_actual == ESTADO_AIRE_100 else ESTADO_AIRE_100
        self.volumen_objetivo_aire = VOLUMEN_AIRE_20 if nuevo_estado == ESTADO_AIRE_20 else VOLUMEN_AIRE_100

        print(f"DEBUG GestorAire: Cambiando estado a: {nuevo_estado} (Vol. obj: {self.volumen_objetivo_aire*100:.0f}%)")
        self.estado_aire_actual = nuevo_estado

        # Notificar al manejador principal para que actualice la UI (botón y slider)
        self.manejador_acciones._actualizar_boton_aire_ventana(self.estado_aire_actual)
        if self.manejador_acciones.controles_widget:
            self.manejador_acciones.controles_widget.actualizar_volumen_visual(int(self.volumen_objetivo_aire * 100))

        # Iniciar el fade
        if self.timer_volumen_aire.isActive():
            self.timer_volumen_aire.stop()
            print("DEBUG GestorAire: Fade anterior detenido.")

        # Calcular pasos para el fade
        self.volumen_actual_fade = self.reproductor.volumen # Empezar desde el volumen real actual
        volumen_diff = self.volumen_objetivo_aire - self.volumen_actual_fade
        # Evitar división por cero si el intervalo es 0 o negativo
        intervalo = max(1, INTERVALO_FADE_MS)
        num_pasos = max(1, DURACION_FADE_MS // intervalo)
        self.paso_volumen_fade = volumen_diff / num_pasos

        print(f"DEBUG GestorAire: Iniciando fade: {self.volumen_actual_fade:.2f} -> {self.volumen_objetivo_aire:.2f} en ~{num_pasos} pasos.")

        # Solo iniciar el timer si hay una diferencia apreciable
        if abs(volumen_diff) > 0.01:
            self.timer_volumen_aire.start()
        else:
            # Si ya está en el objetivo, asegurar valor exacto
            self.reproductor.volumen = self.volumen_objetivo_aire
            print("DEBUG GestorAire: Volumen ya en objetivo. No se inicia fade.")

    def detener_fade_si_activo(self):
        """Detiene el timer del fade si está corriendo."""
        if self.timer_volumen_aire.isActive():
            print("DEBUG GestorAire: Fade detenido externamente (ej. volumen manual).")
            self.timer_volumen_aire.stop()
            # Actualizar estado interno para reflejar el volumen actual
            self.volumen_actual_fade = self.reproductor.volumen
            self.volumen_objetivo_aire = self.reproductor.volumen
            # Determinar el estado AIRE correspondiente al volumen actual
            self.estado_aire_actual = ESTADO_AIRE_100 if self.volumen_actual_fade >= 0.6 else ESTADO_AIRE_20
            # Notificar al manejador para actualizar el botón
            self.manejador_acciones._actualizar_boton_aire_ventana(self.estado_aire_actual)


    # --- Slot interno para el Timer ---

    @Slot()
    def _actualizar_fade_volumen(self):
        """Actualiza el volumen un paso durante el fade."""
        if not self.reproductor:
            self.timer_volumen_aire.stop()
            return

        # Calcular nuevo volumen y verificar si se alcanzó el objetivo
        self.volumen_actual_fade += self.paso_volumen_fade
        alcanzado = False
        if self.paso_volumen_fade > 0: # Subiendo
            alcanzado = self.volumen_actual_fade >= self.volumen_objetivo_aire
        elif self.paso_volumen_fade < 0: # Bajando
            alcanzado = self.volumen_actual_fade <= self.volumen_objetivo_aire
        else: # Paso cero
            alcanzado = True

        # Clamp y aplicar volumen
        volumen_final_paso = self.volumen_objetivo_aire if alcanzado else max(0.0, min(1.0, self.volumen_actual_fade))
        self.reproductor.volumen = volumen_final_paso

        # Detener timer si se alcanzó
        if alcanzado:
            self.timer_volumen_aire.stop()
            # print("DEBUG GestorAire: Fade AIRE completado.") # Opcional: log menos verboso