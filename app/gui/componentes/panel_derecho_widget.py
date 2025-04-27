# -*- coding: utf-8 -*-
"""
Define el widget PanelDerechoWidget que encapsula la interfaz
de la sección derecha de la ventana principal (Tiempo Total, Aire).
SIMPLIFICADO: Los paneles de información de canción ahora están desactivados.
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                               QGroupBox, QPushButton, QSizePolicy, QSpacerItem)
from PySide6.QtGui import QFont, QColor
from PySide6.QtCore import Qt, Signal, Slot

# Constantes para el botón AIRE (se mantienen)
ESTADO_AIRE_100 = "a_100"
ESTADO_AIRE_20 = "a_20"
COLOR_AIRE_100 = "background-color: green; color: white;"
COLOR_AIRE_20 = "background-color: red; color: white;"

class PanelDerechoWidget(QWidget):
    """
    Widget que contiene los elementos del panel derecho:
    Tiempo Total y Botón Aire. Los paneles de info están deshabilitados.
    """
    # Señal emitida cuando se presiona el botón AIRE interno (se mantiene)
    boton_aire_presionado = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        # Referencias internas a los widgets que necesitamos actualizar
        self.etiqueta_tiempo_total_lista: QLabel | None = None
        self.boton_aire: QPushButton | None = None
        # --- Referencias a etiquetas de info eliminadas ---
        # self.etiqueta_info_en_play: QLabel | None = None
        # self.etiqueta_info_siguiente: QLabel | None = None

        # --- Colores eliminados (ya no se usan) ---
        # self.color_fondo_en_play = "gray"
        # ...

        self._configurar_ui_interna()

        print("PanelDerechoWidget inicializado (simplificado, sin paneles de info).")

    def _configurar_ui_interna(self):
        """Crea y dispone los widgets internos del panel derecho."""
        layout_principal_derecho = QVBoxLayout(self) # Layout principal
        layout_principal_derecho.setContentsMargins(5, 5, 5, 5)
        layout_principal_derecho.setSpacing(8)

        # --- Layout Superior (TIEMPO_TOTAL | AIRE) ---
        layout_superior = QHBoxLayout()
        layout_superior.setSpacing(10)

        # Grupo TIEMPO_TOTAL (sin cambios)
        grupo_tiempo_total = QGroupBox("TIEMPO TOTAL")
        layout_grupo_tiempo = QVBoxLayout(grupo_tiempo_total)
        self.etiqueta_tiempo_total_lista = QLabel("--:--:--")
        font_tiempo = self.etiqueta_tiempo_total_lista.font()
        font_tiempo.setPointSize(14); font_tiempo.setBold(True)
        self.etiqueta_tiempo_total_lista.setFont(font_tiempo)
        self.etiqueta_tiempo_total_lista.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.etiqueta_tiempo_total_lista.setToolTip("Tiempo total estimado de la lista de reproducción")
        layout_grupo_tiempo.addWidget(self.etiqueta_tiempo_total_lista)
        layout_superior.addWidget(grupo_tiempo_total, stretch=1)

        # Grupo AIRE (sin cambios)
        grupo_aire = QGroupBox("AIRE")
        layout_grupo_aire = QHBoxLayout(grupo_aire)
        layout_grupo_aire.setContentsMargins(10, 5, 10, 5)
        self.boton_aire = QPushButton("AIRE")
        self.boton_aire.setMinimumHeight(40)
        self.boton_aire.setToolTip("Alternar volumen AIRE (100% / 20%)")
        # Establecer estado inicial y estilo
        self.boton_aire.setProperty("estado_aire", ESTADO_AIRE_100)
        self.boton_aire.setStyleSheet(COLOR_AIRE_100)
        font_aire = self.boton_aire.font(); font_aire.setBold(True)
        self.boton_aire.setFont(font_aire)
        # Conectar clic a slot interno que emite señal pública
        self.boton_aire.clicked.connect(self._on_boton_aire_clicked)
        # Centrar botón AIRE
        layout_grupo_aire.addStretch(1)
        layout_grupo_aire.addWidget(self.boton_aire)
        layout_grupo_aire.addStretch(1)
        layout_superior.addWidget(grupo_aire, stretch=1)

        layout_principal_derecho.addLayout(layout_superior)
        # ---------------------------------------------

        # --- Grupo INFO (AHORA DESACTIVADO o con Placeholder) ---
        grupo_info = QGroupBox("INFO")
        layout_info_vertical = QVBoxLayout(grupo_info)
        layout_info_vertical.setContentsMargins(5, 8, 5, 8); layout_info_vertical.setSpacing(6)

        # Placeholder indicando que la función está desactivada
        label_info_placeholder = QLabel("(Funcionalidad de información de canción desactivada)")
        label_info_placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label_info_placeholder.setStyleSheet("color: gray; font-style: italic;")
        label_info_placeholder.setWordWrap(True)
        layout_info_vertical.addWidget(label_info_placeholder, stretch=1) # Ocupa todo el espacio

        # --- Paneles EN PLAY y SIGUIENTE ELIMINADOS ---
        # grupo_en_play = QGroupBox("EN PLAY") ...
        # grupo_siguiente = QGroupBox("SIGUIENTE") ...
        # ---------------------------------------------

        layout_principal_derecho.addWidget(grupo_info, stretch=1) # El grupo INFO ahora solo tiene el placeholder
        # ----------------------------------------------

        # --- Placeholder inferior (sin cambios) ---
        # Podemos mantenerlo o quitarlo si el grupo INFO ahora ocupa todo
        area_resto_derecha = QWidget()
        # Hacer que este widget inferior ocupe cualquier espacio sobrante
        area_resto_derecha.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        # layout_resto = QVBoxLayout(area_resto_derecha) # No necesitamos layout si no hay contenido
        # label_resto_placeholder = QLabel("(Área inferior derecha)") ...
        # layout_resto.addWidget(label_resto_placeholder)
        layout_principal_derecho.addWidget(area_resto_derecha, stretch=1) # Estirar este espacio vacío
        # -----------------------------------------------

    # --- Slots Públicos para Actualizar la UI ---

    @Slot(str)
    def actualizar_tiempo_total(self, tiempo_formateado: str):
        """Actualiza la etiqueta de tiempo total."""
        if self.etiqueta_tiempo_total_lista:
            self.etiqueta_tiempo_total_lista.setText(tiempo_formateado)
        else:
            print("WARN (PanelDerecho): No se encontró etiqueta_tiempo_total_lista para actualizar.")

    @Slot(str)
    def actualizar_boton_aire_ui(self, nuevo_estado: str):
        """Actualiza el estilo y propiedad del botón AIRE."""
        if not self.boton_aire: return
        if nuevo_estado == ESTADO_AIRE_100:
            self.boton_aire.setStyleSheet(COLOR_AIRE_100)
            self.boton_aire.setProperty("estado_aire", ESTADO_AIRE_100)
        elif nuevo_estado == ESTADO_AIRE_20:
            self.boton_aire.setStyleSheet(COLOR_AIRE_20)
            self.boton_aire.setProperty("estado_aire", ESTADO_AIRE_20)
        else:
            print(f"WARN (PanelDerecho): Estado AIRE desconocido recibido: {nuevo_estado}")

    # --- Slot actualizar_paneles_info ELIMINADO ---
    # @Slot(dict)
    # def actualizar_paneles_info(self, info_encontrada: dict): ...

    # --- Slot Interno para Botón AIRE (sin cambios) ---
    @Slot()
    def _on_boton_aire_clicked(self):
        """Emite la señal pública cuando se hace clic en el botón AIRE."""
        print("DEBUG (PanelDerecho): Botón AIRE clickeado, emitiendo señal boton_aire_presionado.")
        self.boton_aire_presionado.emit()

    # --- Método para Habilitar/Deshabilitar Controles Internos (sin cambios) ---
    @Slot(bool)
    def habilitar_controles_internos(self, habilitar: bool):
        """Habilita o deshabilita los controles interactivos del panel (botón AIRE)."""
        if self.boton_aire:
            self.boton_aire.setEnabled(habilitar)

# --- Fin del archivo app/gui/componentes/panel_derecho_widget.py ---