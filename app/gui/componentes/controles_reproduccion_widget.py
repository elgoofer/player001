# -*- coding: utf-8 -*-
""" Define ControlesReproduccionWidget. Robustece act tiempo actual. """

from PySide6.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QPushButton,
                               QSizePolicy, QSlider, QLabel, QStyle,
                               QSpacerItem)
from PySide6.QtCore import Signal, Slot, Qt

MODO_NORMAL=0; MODO_REPETIR_TODO=1; MODO_REPETIR_UNO=2; MODO_ALEATORIO=3
MODOS=[MODO_NORMAL, MODO_REPETIR_TODO, MODO_REPETIR_UNO, MODO_ALEATORIO]
DURACION_DESCONOCIDA_MS = 0

class ControlesReproduccionWidget(QWidget):
    """ Controles. Manejo robusto de actualización de tiempo. """
    play_pause_presionado=Signal(); stop_presionado=Signal(); siguiente_presionado=Signal()
    posicion_cambiada_usuario=Signal(int); volumen_cambiado_usuario=Signal(int)
    cambiar_modo_presionado=Signal()

    def __init__(self, parent=None):
        # ... (init sin cambios) ...
        super().__init__(parent)
        self._esta_en_play = False; self._usuario_arrastrando_slider_progreso = False; self._usuario_arrastrando_slider_volumen = False
        layout_principal=QVBoxLayout(self); layout_principal.setContentsMargins(0, 5, 0, 0); layout_principal.setSpacing(5)
        layout_progreso=QHBoxLayout(); layout_progreso.setContentsMargins(5, 0, 5, 0); self.etiqueta_tiempo_actual=QLabel("00:00"); self.etiqueta_tiempo_actual.setMinimumWidth(40); self.etiqueta_tiempo_actual.setAlignment(Qt.AlignmentFlag.AlignCenter); self.slider_progreso=QSlider(Qt.Orientation.Horizontal); self.slider_progreso.setRange(0, 1); self.slider_progreso.setEnabled(False); self.etiqueta_tiempo_total=QLabel("00:00"); self.etiqueta_tiempo_total.setMinimumWidth(40); self.etiqueta_tiempo_total.setAlignment(Qt.AlignmentFlag.AlignCenter); layout_progreso.addWidget(self.etiqueta_tiempo_actual); layout_progreso.addWidget(self.slider_progreso); layout_progreso.addWidget(self.etiqueta_tiempo_total);
        self.etiqueta_cancion_actual=QLabel("(Ninguna)"); self.etiqueta_cancion_actual.setAlignment(Qt.AlignmentFlag.AlignCenter); self.etiqueta_cancion_actual.setStyleSheet("color: gray; font-style: italic;")
        layout_controles_inferior=QHBoxLayout(); layout_controles_inferior.setContentsMargins(0, 0, 0, 0); estilo=self.style(); ico_play=estilo.standardIcon(QStyle.StandardPixmap.SP_MediaPlay); ico_pause=estilo.standardIcon(QStyle.StandardPixmap.SP_MediaPause); ico_stop=estilo.standardIcon(QStyle.StandardPixmap.SP_MediaStop); ico_next=estilo.standardIcon(QStyle.StandardPixmap.SP_MediaSkipForward); ico_vol=estilo.standardIcon(QStyle.StandardPixmap.SP_MediaVolume); self.boton_play_pause=QPushButton(); self.boton_play_pause.setIcon(ico_play); self.boton_play_pause.setToolTip("Play/Pause"); self.boton_stop=QPushButton(); self.boton_stop.setIcon(ico_stop); self.boton_stop.setToolTip("Stop"); self.boton_siguiente=QPushButton(); self.boton_siguiente.setIcon(ico_next); self.boton_siguiente.setToolTip("Siguiente"); self.boton_modo=QPushButton("Normal"); self.boton_modo.setToolTip("Modo: Normal"); self.etiqueta_icono_volumen=QLabel(); self.etiqueta_icono_volumen.setPixmap(ico_vol.pixmap(16, 16)); self.slider_volumen=QSlider(Qt.Orientation.Horizontal); self.slider_volumen.setRange(0, 100); self.slider_volumen.setValue(70); self.slider_volumen.setToolTip("Volumen"); self.slider_volumen.setFixedWidth(100); layout_controles_inferior.addStretch(1); layout_controles_inferior.addWidget(self.boton_play_pause); layout_controles_inferior.addWidget(self.boton_stop); layout_controles_inferior.addWidget(self.boton_siguiente); layout_controles_inferior.addWidget(self.boton_modo); layout_controles_inferior.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)); layout_controles_inferior.addWidget(self.etiqueta_icono_volumen); layout_controles_inferior.addWidget(self.slider_volumen); layout_controles_inferior.addStretch(1);
        layout_principal.addLayout(layout_progreso); layout_principal.addWidget(self.etiqueta_cancion_actual); layout_principal.addLayout(layout_controles_inferior);
        self.boton_play_pause.clicked.connect(self._on_play_pause); self.boton_stop.clicked.connect(self._on_stop); self.boton_siguiente.clicked.connect(self._on_siguiente); self.slider_progreso.sliderMoved.connect(self._on_slider_progreso_movido); self.slider_progreso.sliderReleased.connect(self._on_slider_progreso_liberado); self.slider_progreso.sliderPressed.connect(self._on_slider_progreso_presionado); self.slider_volumen.valueChanged.connect(self._on_slider_volumen_cambiado); self.boton_modo.clicked.connect(self._on_boton_modo_presionado)
        print("ControlesWidget inic.")

    # --- Slots Internos (sin cambios) ---
    @Slot()
    def _on_play_pause(self): self.play_pause_presionado.emit()
    @Slot()
    def _on_stop(self): self.stop_presionado.emit()
    @Slot()
    def _on_siguiente(self): self.siguiente_presionado.emit()
    @Slot(int)
    def _on_slider_progreso_movido(self, pos): self.actualizar_tiempo_actual(pos, True)
    @Slot()
    def _on_slider_progreso_liberado(self):
        if self._usuario_arrastrando_slider_progreso: self.posicion_cambiada_usuario.emit(self.slider_progreso.value()); self._usuario_arrastrando_slider_progreso = False
    @Slot()
    def _on_slider_progreso_presionado(self): self._usuario_arrastrando_slider_progreso = True
    @Slot(int)
    def _on_slider_volumen_cambiado(self, val): self.volumen_cambiado_usuario.emit(val)
    @Slot()
    def _on_boton_modo_presionado(self): self.cambiar_modo_presionado.emit()

    # --- Métodos Públicos ---
    @Slot(bool)
    def actualizar_estado_play_pause(self, esta_reproduciendo: bool):
        # ... (igual) ...
        estilo=self.style(); icono=estilo.standardIcon(QStyle.StandardPixmap.SP_MediaPause) if esta_reproduciendo else estilo.standardIcon(QStyle.StandardPixmap.SP_MediaPlay)
        self.boton_play_pause.setIcon(icono); self._esta_en_play = esta_reproduciendo

    @Slot(bool)
    def habilitar_controles(self, habilitar: bool, habilitar_progreso: bool = False):
        # ... (igual) ...
        self.boton_play_pause.setEnabled(habilitar); self.boton_stop.setEnabled(habilitar); self.boton_siguiente.setEnabled(habilitar); self.boton_modo.setEnabled(habilitar)
        dur_ok = self.slider_progreso.maximum() > DURACION_DESCONOCIDA_MS
        prog_hab = habilitar_progreso and dur_ok
        self.slider_progreso.setEnabled(prog_hab); self.etiqueta_tiempo_actual.setEnabled(prog_hab); self.etiqueta_tiempo_total.setEnabled(prog_hab); self.slider_volumen.setEnabled(True); self.etiqueta_cancion_actual.setEnabled(habilitar)

    @Slot(int)
    def actualizar_tiempo_total(self, duracion_ms: int):
        # ... (igual) ...
        if duracion_ms <= DURACION_DESCONOCIDA_MS: self.slider_progreso.setRange(0, 1); self.slider_progreso.setValue(0); self.slider_progreso.setEnabled(False); self.etiqueta_tiempo_total.setText("--:--")
        else: self.slider_progreso.setRange(0, duracion_ms); self.etiqueta_tiempo_total.setText(self._formatear_tiempo(duracion_ms))

    # --- actualizar_tiempo_actual REFINADO ---
    @Slot(int)
    def actualizar_tiempo_actual(self, pos_ms: int, forzar_etiqueta: bool = False):
        """ Actualiza slider y etiqueta. Evita poner valor >= máximo. """
        if pos_ms < 0: pos_ms = 0
        duracion_max = self.slider_progreso.maximum()

        if duracion_max > DURACION_DESCONOCIDA_MS:
            # Asegurarse que el valor a poner sea MENOR que el máximo
            # Si es igual o mayor, visualmente puede parecer que llegó al final.
            valor_a_poner = min(pos_ms, duracion_max)
            # Corrección adicional: si está muy cerca del final, no lo pongas
            # exactamente en el máximo para evitar el salto visual.
            if valor_a_poner >= duracion_max:
                 valor_a_poner = max(0, duracion_max - 1) # Un milisegundo menos

            if not self._usuario_arrastrando_slider_progreso:
                # Poner valor solo si es diferente al actual para evitar updates innecesarios
                if self.slider_progreso.value() != valor_a_poner:
                     self.slider_progreso.setValue(valor_a_poner)

            # Actualizar etiqueta
            if not self._usuario_arrastrando_slider_progreso or forzar_etiqueta:
                 # Usar pos_ms original para la etiqueta, para mostrar el tiempo real
                 self.etiqueta_tiempo_actual.setText(self._formatear_tiempo(pos_ms))
        else:
             # Duración desconocida
             self.etiqueta_tiempo_actual.setText("00:00")
             if not self._usuario_arrastrando_slider_progreso:
                 self.slider_progreso.setValue(0)
    # --- FIN actualizar_tiempo_actual ---

    @Slot(int)
    def actualizar_volumen_visual(self, val_porc: int):
        # ... (igual) ...
         val = max(0, min(100, val_porc));
         if self.slider_volumen.value() != val: self.slider_volumen.blockSignals(True); self.slider_volumen.setValue(val); self.slider_volumen.blockSignals(False)
    @Slot(int)
    def actualizar_modo_visual(self, modo: int):
        # ... (igual) ...
        t = "?"; tt = "?";
        if modo == MODO_NORMAL: t="Normal"; tt="Normal"
        elif modo == MODO_REPETIR_TODO: t="Rep Todo"; tt="Repetir Todo"
        elif modo == MODO_REPETIR_UNO: t="Rep Uno"; tt="Repetir Uno"
        elif modo == MODO_ALEATORIO: t="Aleatorio"; tt="Aleatorio"
        self.boton_modo.setText(t); self.boton_modo.setToolTip(f"Modo: {tt}")
    @Slot(str)
    def actualizar_cancion_actual(self, nombre: str):
        # ... (igual) ...
        if nombre: self.etiqueta_cancion_actual.setStyleSheet(""); self.etiqueta_cancion_actual.setText(nombre); self.etiqueta_cancion_actual.setToolTip(nombre)
        else: self.etiqueta_cancion_actual.setStyleSheet("color: gray; font-style: italic;"); self.etiqueta_cancion_actual.setText("(Ninguna)"); self.etiqueta_cancion_actual.setToolTip("")
    def _formatear_tiempo(self, ms: int) -> str:
        # ... (igual) ...
        if ms <= 0: return "00:00"
        ts = round(ms / 1000); m = ts // 60; s = ts % 60; return f"{m:02d}:{s:02d}"