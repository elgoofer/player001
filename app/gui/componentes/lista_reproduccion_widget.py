# -*- coding: utf-8 -*-
"""
Define el widget ListaReproduccionWidget.
SIMPLIFICADO: Eliminado método mover_item_actual_al_final.
CORREGIDO: Sintaxis e indentación revisada manualmente en todo el archivo.
"""
import os
import traceback # Para imprimir errores más detallados si es necesario

from PySide6.QtWidgets import (QListWidget, QAbstractItemView, QListWidgetItem,
                               QStyle, QApplication)
from PySide6.QtGui import (QIcon, QDragEnterEvent, QDropEvent, QDragMoveEvent,
                           QPalette, QColor, QFont)
from PySide6.QtCore import Qt, Signal, Slot, QUrl, QMimeData

# Formatos de archivo soportados
FORMATOS_AUDIO_ACEPTADOS = ['.mp3', '.ogg', '.wav', '.flac']

# Ruta al ícono personalizado
DIRECTORIO_ACTUAL = os.path.dirname(os.path.abspath(__file__))
RUTA_ICONO_NOTA = os.path.abspath(os.path.join(
    DIRECTORIO_ACTUAL, "..", "..", "..", "recursos", "iconos", "nota_musical.png"
))

# Constante para el factor de tamaño de fuente del ítem activo
FACTOR_TAMANIO_FUENTE_ACTIVA = 1.5 # 150%

class ListaReproduccionWidget(QListWidget):
    """
    Widget de lista que muestra archivos de audio, maneja drag & drop,
    y resalta el ítem en reproducción (moviéndolo al tope).
    """
    archivos_soltados = Signal(list)
    _icono_musica_cargado = None
    _fuente_default = None
    _tamanio_fuente_default = 0
    _indice_item_resaltado_actualmente = -1

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setAcceptDrops(True)
        self.setDragEnabled(True)
        self.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        self.viewport().setAcceptDrops(True)

        # Configurar Paleta
        paleta_actual = self.palette()
        color_fondo_seleccion = QColor(0, 0, 0)
        color_texto_seleccion = QColor(255, 255, 0)
        paleta_actual.setColor(QPalette.Highlight, color_fondo_seleccion)
        paleta_actual.setColor(QPalette.HighlightedText, color_texto_seleccion)
        self.setPalette(paleta_actual)

        # Guardar fuente default
        if ListaReproduccionWidget._fuente_default is None:
            fuente_base = self.font() or QApplication.font()
            ListaReproduccionWidget._fuente_default = fuente_base
            ListaReproduccionWidget._tamanio_fuente_default = fuente_base.pointSizeF()
            # --- CORRECCIÓN DE INDENTACIÓN ---
            if ListaReproduccionWidget._tamanio_fuente_default <= 0:
                 ListaReproduccionWidget._tamanio_fuente_default = 10.0
                 print(f"WARN: Tamaño de fuente default <= 0, establecido a 10.0pt")
            # --- FIN CORRECCIÓN ---
            print(f"Fuente default guardada: Tamaño {ListaReproduccionWidget._tamanio_fuente_default}pt")

        # Carga de Ícono
        if ListaReproduccionWidget._icono_musica_cargado is None:
            icono_estilo_standard = None
            estilo_app = QApplication.style()
            if estilo_app:
                icono_estilo_standard = estilo_app.standardIcon(QStyle.StandardPixmap.SP_DriveCDIcon)
            if os.path.exists(RUTA_ICONO_NOTA):
                try:
                    ListaReproduccionWidget._icono_musica_cargado = QIcon(RUTA_ICONO_NOTA)
                    print(f"Ícono personalizado cargado: {RUTA_ICONO_NOTA}")
                except Exception as e:
                    print(f"Error ícono: {e}")
                    ListaReproduccionWidget._icono_musica_cargado = icono_estilo_standard
            else:
                print(f"Ícono no encontrado: {RUTA_ICONO_NOTA}")
                ListaReproduccionWidget._icono_musica_cargado = icono_estilo_standard
            if ListaReproduccionWidget._icono_musica_cargado is None:
                print("WARN: No se pudo cargar ícono.")

        self._indice_item_resaltado_actualmente = -1
        print("ListaReproduccionWidget inicializado (syntax revisada).")

    # --- Métodos de gestión de ítems ---
    @Slot(str)
    def agregar_archivo(self, ruta_archivo_completa: str):
        nombre_archivo = os.path.basename(ruta_archivo_completa)
        icono_para_item = ListaReproduccionWidget._icono_musica_cargado
        item = QListWidgetItem(icono_para_item, nombre_archivo)
        item.setData(Qt.ItemDataRole.UserRole, ruta_archivo_completa)
        if ListaReproduccionWidget._fuente_default:
            item.setFont(ListaReproduccionWidget._fuente_default)
        self.addItem(item)

    @Slot()
    def quitar_seleccionado(self) -> str | None:
        items = self.selectedItems()
        if items:
            item = items[0]
            ruta_quitada = item.data(Qt.ItemDataRole.UserRole)
            nombre_base = os.path.basename(ruta_quitada) if ruta_quitada else "?"
            indice = self.row(item)

            if indice == self._indice_item_resaltado_actualmente:
                self._indice_item_resaltado_actualmente = -1

            if indice != -1:
                self.takeItem(indice)
                print(f"Archivo quitado: {nombre_base}")
                # Ajustar índice resaltado si se quitó uno anterior
                if self._indice_item_resaltado_actualmente > indice:
                    self._indice_item_resaltado_actualmente -= 1
                return ruta_quitada # Correctamente indentado
            else:
                print("WARN: Ítem seleccionado no encontrado.")
                return None
        else:
            return None

    def obtener_ruta_seleccionada(self) -> str | None:
        items = self.selectedItems()
        if items:
             return items[0].data(Qt.ItemDataRole.UserRole)
        else:
             return None

    def obtener_todas_las_rutas(self) -> list[str]:
        rutas = []
        for i in range(self.count()):
            item = self.item(i)
            if item:
                 ruta = item.data(Qt.ItemDataRole.UserRole)
                 if ruta:
                     rutas.append(ruta)
        return rutas

    # --- Métodos de resaltado y movimiento ---
    def _resetear_estilos_todos(self):
        if not ListaReproduccionWidget._fuente_default: return
        fuente_def = ListaReproduccionWidget._fuente_default
        print("DEBUG ListWidget: Reseteando estilos todos...")
        for i in range(self.count()):
            item = self.item(i)
            if item:
                item.setFont(fuente_def)
        self._indice_item_resaltado_actualmente = -1
        print("DEBUG ListWidget: Reseteo estilos completo.")

    @Slot(str)
    def resaltar_y_mover_item_actual(self, ruta_archivo_actual: str):
        print(f"DEBUG ListWidget: Resaltar/Mover '{os.path.basename(ruta_archivo_actual)}'...")
        if not ruta_archivo_actual:
            self._resetear_estilos_todos()
            return

        item_encontrado = None
        indice_encontrado = -1
        for i in range(self.count()):
            item = self.item(i)
            if item:
                 ruta_item = item.data(Qt.ItemDataRole.UserRole)
                 if ruta_item == ruta_archivo_actual:
                    item_encontrado = item
                    indice_encontrado = i
                    break

        if not item_encontrado:
            print(f"WARN: No ítem para '{ruta_archivo_actual}'.")
            self._resetear_estilos_todos()
            return

        self.resetear_estilo_item_actual(forzar=False)

        item_movido = False
        if indice_encontrado > 0:
            print(f"Moviendo de {indice_encontrado} a 0.")
            item_a_mover = self.takeItem(indice_encontrado)
            if item_a_mover:
                self.insertItem(0, item_a_mover)
                item_encontrado = item_a_mover # Actualizar referencia
                indice_encontrado = 0
                item_movido = True
            else:
                print(f"WARN: takeItem({indice_encontrado}) falló.")

        if item_encontrado and ListaReproduccionWidget._fuente_default:
            fuente_activa = QFont(ListaReproduccionWidget._fuente_default)
            nuevo_tamanio = ListaReproduccionWidget._tamanio_fuente_default * FACTOR_TAMANIO_FUENTE_ACTIVA
            fuente_activa.setPointSizeF(nuevo_tamanio)
            fuente_activa.setBold(True)
            item_encontrado.setFont(fuente_activa)
            self._indice_item_resaltado_actualmente = indice_encontrado
            print(f"Estilo activo índice {indice_encontrado}")

        if ListaReproduccionWidget._fuente_default:
            fuente_def = ListaReproduccionWidget._fuente_default
            for i in range(1, self.count()):
                 item = self.item(i)
                 if item:
                     item.setFont(fuente_def)

        if item_movido or self.currentRow() != 0:
             self.setCurrentRow(0)
             self.scrollToItem(self.item(0), QAbstractItemView.ScrollHint.PositionAtTop)

    @Slot(bool)
    def resetear_estilo_item_actual(self, forzar: bool = True):
        if forzar:
            print("DEBUG ListWidget: Reseteando estilo activo...")
        if self._indice_item_resaltado_actualmente != -1:
            item = self.item(self._indice_item_resaltado_actualmente)
            if item and ListaReproduccionWidget._fuente_default:
                item.setFont(ListaReproduccionWidget._fuente_default)
                if forzar:
                    print(f"Estilo reseteado índice {self._indice_item_resaltado_actualmente}")
            elif forzar:
                print(f"WARN: No resetear índice {self._indice_item_resaltado_actualmente}")
            self._indice_item_resaltado_actualmente = -1
        elif forzar:
            print("DEBUG ListWidget: No había ítem activo.")

    # --- Método mover_item_actual_al_final ELIMINADO ---

    # --- Métodos de Drag & Drop (Revisados) ---
    def dragEnterEvent(self, event: QDragEnterEvent):
        mime_data = event.mimeData()
        if mime_data.hasUrls():
            urls_validas = any(url.isLocalFile() and self._es_formato_aceptado(url.toLocalFile()) for url in mime_data.urls())
            if urls_validas:
                event.acceptProposedAction()
            else:
                event.ignore()
        elif event.source() == self: # Permitir reordenamiento interno
            super().dragEnterEvent(event)
        else:
            event.ignore()

    def dragMoveEvent(self, event: QDragMoveEvent):
        mime_data = event.mimeData()
        if mime_data.hasUrls():
            urls_validas = any(url.isLocalFile() and self._es_formato_aceptado(url.toLocalFile()) for url in mime_data.urls())
            if urls_validas:
                event.acceptProposedAction()
            else:
                event.ignore()
        elif event.source() == self: # Permitir reordenamiento interno
            super().dragMoveEvent(event)
        else:
            event.ignore()

    def dropEvent(self, event: QDropEvent):
        idx_res = self._indice_item_resaltado_actualmente
        ruta_res = None
        if idx_res != -1:
            item_res = self.item(idx_res)
            if item_res:
                 ruta_res = item_res.data(Qt.ItemDataRole.UserRole)

        # Dejar que QListWidget maneje el drop si es interno
        if event.source() == self:
            super().dropEvent(event)
        # Si son URLs externas
        elif event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            rutas = [url.toLocalFile() for url in urls if url.isLocalFile() and os.path.isfile(url.toLocalFile()) and self._es_formato_aceptado(url.toLocalFile())]
            if rutas:
                self.archivos_soltados.emit(rutas)
                event.acceptProposedAction()
            else:
                event.ignore()
        else:
            event.ignore()

        # Re-aplicar resaltado después del drop
        if ruta_res:
            print("Re-aplicando resaltado post-Drop...")
            # Llamar a la función para encontrar y resaltar/mover de nuevo
            self.resaltar_y_mover_item_actual(ruta_res)

    def _es_formato_aceptado(self, ruta_archivo: str) -> bool:
        _ , extension = os.path.splitext(ruta_archivo)
        return bool(extension and extension.lower() in FORMATOS_AUDIO_ACEPTADOS)

# --- Fin del archivo app/gui/componentes/lista_reproduccion_widget.py ---