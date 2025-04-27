# -*- coding: utf-8 -*-
"""
Define el widget BarraBotonesArchivoWidget.
AHORA: Usa íconos estándar de QStyle en lugar de texto para la mayoría de los botones,
con un tamaño fijo de 24px.
"""

from PySide6.QtWidgets import (QWidget, QHBoxLayout, QPushButton, QSpacerItem,
                               QSizePolicy, QStyle, QApplication) # Importar QStyle y QApplication
from PySide6.QtCore import Signal, Slot, QSize # Importar QSize

# Constante para el tamaño de los íconos
TAMANIO_ICONO_BOTON = 24

class BarraBotonesArchivoWidget(QWidget):
    """
    Widget con botones (mayormente íconos) para acciones de archivo y lista.
    """
    # Señales (sin cambios)
    anadir_archivo_presionado = Signal()
    anadir_carpeta_presionado = Signal()
    quitar_seleccionado_presionado = Signal()
    guardar_lista_presionado = Signal()
    cargar_lista_presionado = Signal()
    limpiar_lista_presionado = Signal()
    reordenar_aleatorio_presionado = Signal()


    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0) # Sin márgenes externos
        layout.setSpacing(5) # Espacio entre botones

        # Obtener el estilo actual de la aplicación para acceder a los íconos
        estilo = QApplication.style()
        tamanio_qsize = QSize(TAMANIO_ICONO_BOTON, TAMANIO_ICONO_BOTON)

        # --- Crear botones con íconos ---
        self.boton_anadir_archivo = QPushButton()
        icono_anadir_archivo = estilo.standardIcon(QStyle.StandardPixmap.SP_FileIcon)
        self.boton_anadir_archivo.setIcon(icono_anadir_archivo)
        self.boton_anadir_archivo.setIconSize(tamanio_qsize)
        self.boton_anadir_archivo.setToolTip("Añadir Archivo(s) de audio")
        self.boton_anadir_archivo.setFixedSize(tamanio_qsize.width()+10, tamanio_qsize.height()+10) # Ajustar tamaño botón

        self.boton_anadir_carpeta = QPushButton()
        icono_anadir_carpeta = estilo.standardIcon(QStyle.StandardPixmap.SP_DirIcon)
        self.boton_anadir_carpeta.setIcon(icono_anadir_carpeta)
        self.boton_anadir_carpeta.setIconSize(tamanio_qsize)
        self.boton_anadir_carpeta.setToolTip("Añadir Carpeta con archivos de audio")
        self.boton_anadir_carpeta.setFixedSize(tamanio_qsize.width()+10, tamanio_qsize.height()+10)

        # Botón Quitar Seleccionado (lo dejamos con texto por ahora, o icono SP_DialogDiscardButton?)
        self.boton_quitar_seleccionado = QPushButton("Quitar") # Texto corto
        # Alternativa con icono:
        # self.boton_quitar_seleccionado = QPushButton()
        # icono_quitar = estilo.standardIcon(QStyle.StandardPixmap.SP_DialogDiscardButton) # O SP_TrashIcon
        # self.boton_quitar_seleccionado.setIcon(icono_quitar)
        # self.boton_quitar_seleccionado.setIconSize(tamanio_qsize)
        # self.boton_quitar_seleccionado.setFixedSize(tamanio_qsize.width()+10, tamanio_qsize.height()+10)
        self.boton_quitar_seleccionado.setToolTip("Quitar ítem seleccionado de la lista")


        self.boton_cargar_lista = QPushButton()
        icono_cargar = estilo.standardIcon(QStyle.StandardPixmap.SP_ArrowDown) # Flecha abajo como "cargar"
        self.boton_cargar_lista.setIcon(icono_cargar)
        self.boton_cargar_lista.setIconSize(tamanio_qsize)
        self.boton_cargar_lista.setToolTip("Cargar Lista de Reproducción (*.rka)")
        self.boton_cargar_lista.setFixedSize(tamanio_qsize.width()+10, tamanio_qsize.height()+10)

        self.boton_guardar_lista = QPushButton()
        icono_guardar = estilo.standardIcon(QStyle.StandardPixmap.SP_DriveFDIcon) # Diskette
        self.boton_guardar_lista.setIcon(icono_guardar)
        self.boton_guardar_lista.setIconSize(tamanio_qsize)
        self.boton_guardar_lista.setToolTip("Guardar Lista de Reproducción actual (*.rka)")
        self.boton_guardar_lista.setFixedSize(tamanio_qsize.width()+10, tamanio_qsize.height()+10)

        self.boton_limpiar_lista = QPushButton()
        # Usamos SP_DialogCancelButton que suele ser una 'X' roja
        icono_limpiar = estilo.standardIcon(QStyle.StandardPixmap.SP_DialogCancelButton)
        # Alternativa: Papelera
        # icono_limpiar = estilo.standardIcon(QStyle.StandardPixmap.SP_TrashIcon)
        self.boton_limpiar_lista.setIcon(icono_limpiar)
        self.boton_limpiar_lista.setIconSize(tamanio_qsize)
        self.boton_limpiar_lista.setToolTip("Limpiar toda la Lista de Reproducción")
        self.boton_limpiar_lista.setFixedSize(tamanio_qsize.width()+10, tamanio_qsize.height()+10)

        # Botón Reordenar Aleatorio (usando caracter Unicode ∞)
        self.boton_reordenar_aleatorio = QPushButton("∞")
        # Aumentar un poco la fuente para que el símbolo sea visible
        fuente_infinito = self.font()
        fuente_infinito.setPointSize(fuente_infinito.pointSize() + 4) # Ajustar según sea necesario
        self.boton_reordenar_aleatorio.setFont(fuente_infinito)
        self.boton_reordenar_aleatorio.setToolTip("Reordenar la lista actual de forma aleatoria")
        # Darle un tamaño similar a los otros botones
        self.boton_reordenar_aleatorio.setFixedSize(tamanio_qsize.width()+10, tamanio_qsize.height()+10)

        # --- Añadir widgets al layout ---
        layout.addWidget(self.boton_anadir_archivo)
        layout.addWidget(self.boton_anadir_carpeta)
        # Espaciador flexible entre grupos de botones
        layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        layout.addWidget(self.boton_cargar_lista)
        layout.addWidget(self.boton_guardar_lista)
        layout.addWidget(self.boton_limpiar_lista)
        layout.addWidget(self.boton_reordenar_aleatorio)
        layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        layout.addWidget(self.boton_quitar_seleccionado)

        # --- Conectar señales (sin cambios en las conexiones) ---
        self.boton_anadir_archivo.clicked.connect(self._on_anadir_archivo)
        self.boton_anadir_carpeta.clicked.connect(self._on_anadir_carpeta)
        self.boton_quitar_seleccionado.clicked.connect(self._on_quitar_seleccionado)
        self.boton_guardar_lista.clicked.connect(self._on_guardar_lista)
        self.boton_cargar_lista.clicked.connect(self._on_cargar_lista)
        self.boton_limpiar_lista.clicked.connect(self._on_limpiar_lista)
        self.boton_reordenar_aleatorio.clicked.connect(self._on_reordenar_aleatorio)

        print("BarraBotonesArchivoWidget inicializado (con íconos).")

    # --- Slots internos que emiten señales (sin cambios) ---
    @Slot()
    def _on_anadir_archivo(self): print("DEBUG: Botón Añadir Archivo presionado..."); self.anadir_archivo_presionado.emit()
    @Slot()
    def _on_anadir_carpeta(self): print("DEBUG: Botón Añadir Carpeta presionado..."); self.anadir_carpeta_presionado.emit()
    @Slot()
    def _on_quitar_seleccionado(self): print("DEBUG: Botón Quitar presionado..."); self.quitar_seleccionado_presionado.emit()
    @Slot()
    def _on_guardar_lista(self): print("DEBUG: Botón Guardar Lista presionado."); self.guardar_lista_presionado.emit()
    @Slot()
    def _on_cargar_lista(self): print("DEBUG: Botón Cargar Lista presionado..."); self.cargar_lista_presionado.emit()
    @Slot()
    def _on_limpiar_lista(self): print("DEBUG: Botón Limpiar Lista presionado."); self.limpiar_lista_presionado.emit()
    @Slot()
    def _on_reordenar_aleatorio(self): print("DEBUG: Botón Reordenar Aleat. presionado."); self.reordenar_aleatorio_presionado.emit()

    # --- Métodos para habilitar/deshabilitar botones (sin cambios) ---
    @Slot(bool)
    def habilitar_boton_quitar(self, habilitar: bool): self.boton_quitar_seleccionado.setEnabled(habilitar)
    @Slot(bool)
    def habilitar_boton_guardar(self, habilitar: bool): self.boton_guardar_lista.setEnabled(habilitar)
    @Slot(bool)
    def habilitar_boton_limpiar(self, habilitar: bool): self.boton_limpiar_lista.setEnabled(habilitar)
    @Slot(bool)
    def habilitar_boton_reordenar(self, habilitar: bool): self.boton_reordenar_aleatorio.setEnabled(habilitar)

# --- Fin del archivo app/gui/componentes/barra_botones_archivo.py ---