# -*- coding: utf-8 -*-
"""
Ventana Principal de Radio Anarkadia.
REFACTORIZADO: Emite señal 'cancion_terminada_auto' al finalizar track,
ManejadorAcciones se encarga de eliminar y reproducir siguiente.
"""

import sys
import os
import traceback
import pygame
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                               QMessageBox, QApplication, QListWidgetItem,
                               QLabel, QFrame, QGroupBox, QSizePolicy,
                               QSpacerItem, QPushButton)
from PySide6.QtGui import (QDragEnterEvent, QDropEvent, QCloseEvent, QFont,
                           QColor)
# Añadir Signal a las importaciones de QtCore
from PySide6.QtCore import Slot, QDir, QTimer, QUrl, Qt, Signal

# --- Importar Componentes GUI ---
try:
    from .componentes.lista_reproduccion_widget import ListaReproduccionWidget
    from .componentes.barra_botones_archivo import BarraBotonesArchivoWidget
    from .componentes.controles_reproduccion_widget import ControlesReproduccionWidget
    from .componentes.panel_derecho_widget import PanelDerechoWidget
except ImportError as e: print(f"Error GUI: {e}"); sys.exit(1)

# --- Importar Lógica ---
try:
    from app.logica.reproductor_audio import ReproductorAudio, ReproductorAudioError
    from app.logica.manejador_acciones import ManejadorAcciones, ESTADO_AIRE_100
except ImportError as e: print(f"Error Logic: {e}"); sys.exit(1)
except ModuleNotFoundError as e_mod: print(f"Error Mod Logic: {e_mod}"); sys.exit(1)

# --- Constantes ---
ANCHO_VENTANA_INICIAL = 1000; ALTO_VENTANA_INICIAL = 600
FACTOR_STRETCH_IZQUIERDA = 4; FACTOR_STRETCH_DERECHA = 6
INTERVALO_TIMER_MS = 150

class VentanaPrincipal(QMainWindow):
    """
    Ventana principal. Emite señal al terminar canción automáticamente.
    """
    # --- NUEVA SEÑAL ---
    # Emite la ruta de la canción que terminó automáticamente
    cancion_terminada_auto = Signal(str)
    # -------------------

    def __init__(self):
        super().__init__(); self.setWindowTitle("Radio Anarkadia"); self.resize(ANCHO_VENTANA_INICIAL, ALTO_VENTANA_INICIAL)
        self.lista_reproduccion_widget: ListaReproduccionWidget | None = None; self.barra_botones_widget: BarraBotonesArchivoWidget | None = None; self.controles_widget: ControlesReproduccionWidget | None = None; self.panel_derecho_widget: PanelDerechoWidget | None = None
        self.reproductor: ReproductorAudio | None = None; self.manejador_acciones: ManejadorAcciones | None = None
        self.timer_verificacion: QTimer | None = None; self.ultima_ruta_usada: str = QDir.homePath()
        self._inicializar_reproductor(); self._configurar_ui(); self._inicializar_manejador_acciones()
        if not self.manejador_acciones: print("ERROR CRÍTICO: ManejadorAcciones None.")
        self._conectar_senales(); self._configurar_timer()
        if self.controles_widget and self.manejador_acciones:
            self.controles_widget.actualizar_modo_visual(self.manejador_acciones.modo_reproduccion_actual)
            vol = 100 if self.manejador_acciones.estado_aire_actual == ESTADO_AIRE_100 else 20; self.controles_widget.actualizar_volumen_visual(vol)
        self.setAcceptDrops(True); self._actualizar_estado_controles(); self.actualizar_display_tiempo_total_lista(); self._slot_seleccion_cambiada()
        print("VentanaPrincipal inicializada (emite señal cancion_terminada_auto).")

    # --- Métodos de inicialización (sin cambios) ---
    def _inicializar_reproductor(self, volumen_inicial_float=1.0):
        try: self.reproductor = ReproductorAudio(volumen_inicial=volumen_inicial_float); print(f"Reproductor OK (Vol: {volumen_inicial_float*100:.0f}%).")
        except ReproductorAudioError as e: self._mostrar_error("Error Audio", f"No inicializar:\n{e}"); self.reproductor = None
        except Exception as e_gen: self._mostrar_error("Error Audio Inesperado", f"{e_gen}"); self.reproductor = None
    def _configurar_ui(self):
        widget_central = QWidget(self); self.setCentralWidget(widget_central); layout_principal_horizontal = QHBoxLayout(widget_central); layout_principal_horizontal.setContentsMargins(5, 5, 5, 5); layout_principal_horizontal.setSpacing(10)
        panel_izquierdo = QWidget(); layout_izquierdo_vertical = QVBoxLayout(panel_izquierdo); layout_izquierdo_vertical.setContentsMargins(0,0,0,0); layout_izquierdo_vertical.setSpacing(5)
        self.barra_botones_widget = BarraBotonesArchivoWidget(panel_izquierdo); self.lista_reproduccion_widget = ListaReproduccionWidget(panel_izquierdo); self.controles_widget = ControlesReproduccionWidget(panel_izquierdo)
        if not self.reproductor and self.controles_widget: self.controles_widget.setEnabled(False)
        layout_izquierdo_vertical.addWidget(self.barra_botones_widget); layout_izquierdo_vertical.addWidget(self.lista_reproduccion_widget, stretch=1); layout_izquierdo_vertical.addWidget(self.controles_widget)
        self.panel_derecho_widget = PanelDerechoWidget(self)
        layout_principal_horizontal.addWidget(panel_izquierdo, stretch=FACTOR_STRETCH_IZQUIERDA); layout_principal_horizontal.addWidget(self.panel_derecho_widget, stretch=FACTOR_STRETCH_DERECHA)
        print("UI configurada (40/60).")
    def _inicializar_manejador_acciones(self):
        if (self.lista_reproduccion_widget and self.controles_widget and self.panel_derecho_widget and self.reproductor):
            try: self.manejador_acciones = ManejadorAcciones( ventana=self, lista_widget=self.lista_reproduccion_widget, controles_widget=self.controles_widget, reproductor=self.reproductor )
            except Exception as e: print(f"ERROR: Falló ManejadorAcciones: {e}"); traceback.print_exc(); self._mostrar_error("Error", f"{e}"); self.manejador_acciones = None
        else:
            componentes = [("Lista", self.lista_reproduccion_widget),("Controles", self.controles_widget),("Panel Der.", self.panel_derecho_widget),("Reprod", self.reproductor)]; faltantes = [n for n, w in componentes if not w]
            msg = f"Error: Faltan: {', '.join(faltantes)}."; print(msg); self._mostrar_error("Error", msg); self.manejador_acciones = None

    # --- _conectar_senales MODIFICADO ---
    def _conectar_senales(self):
        """Conecta las señales."""
        if not self.manejador_acciones: print("WARN: No conectar (no manejador)."); return
        print("DEBUG: Conectando señales...");

        # --- Conexiones estándar (sin cambios) ---
        if self.barra_botones_widget: bw = self.barra_botones_widget; bw.anadir_archivo_presionado.connect(self.manejador_acciones.accion_anadir_archivo); bw.anadir_carpeta_presionado.connect(self.manejador_acciones.accion_anadir_carpeta); bw.quitar_seleccionado_presionado.connect(self.manejador_acciones.accion_quitar_seleccionado); bw.guardar_lista_presionado.connect(self.manejador_acciones.accion_guardar_lista); bw.cargar_lista_presionado.connect(self.manejador_acciones.accion_cargar_lista); bw.limpiar_lista_presionado.connect(self.manejador_acciones.accion_limpiar_lista); bw.reordenar_aleatorio_presionado.connect(self.manejador_acciones.accion_reordenar_lista_aleatorio)
        if self.lista_reproduccion_widget:
            lw = self.lista_reproduccion_widget; lw.archivos_soltados.connect(self.manejador_acciones.accion_manejar_archivos_soltados); lw.itemDoubleClicked.connect(self.manejador_acciones.accion_item_doble_clic); lw.itemSelectionChanged.connect(self._slot_seleccion_cambiada)
            modelo = lw.model()
            if modelo: print("DEBUG: Conectando señales modelo lista..."); modelo.rowsInserted.connect(self._slot_modelo_lista_cambiado); modelo.rowsRemoved.connect(self._slot_modelo_lista_cambiado); modelo.rowsMoved.connect(self._slot_modelo_lista_cambiado)
        if self.controles_widget: cw = self.controles_widget; cw.play_pause_presionado.connect(self.manejador_acciones.accion_play_pause); cw.stop_presionado.connect(self.manejador_acciones.accion_stop); cw.siguiente_presionado.connect(self.manejador_acciones.accion_siguiente); cw.posicion_cambiada_usuario.connect(self.manejador_acciones.accion_cambiar_posicion); cw.volumen_cambiado_usuario.connect(self.manejador_acciones.accion_cambiar_volumen); cw.cambiar_modo_presionado.connect(self.manejador_acciones.accion_cambiar_modo)
        if self.panel_derecho_widget: self.panel_derecho_widget.boton_aire_presionado.connect(self.manejador_acciones.accion_alternar_volumen_aire)

        # --- NUEVA CONEXIÓN ---
        # Conectar la señal de fin de canción de esta ventana al nuevo slot del manejador
        # Verificar que el slot exista en ManejadorAcciones antes de conectar
        if hasattr(self.manejador_acciones, '_slot_manejar_fin_automatico'):
            print("DEBUG: Conectando self.cancion_terminada_auto -> manejador._slot_manejar_fin_automatico")
            self.cancion_terminada_auto.connect(self.manejador_acciones._slot_manejar_fin_automatico)
        else:
            print("WARN: El slot '_slot_manejar_fin_automatico' no existe en ManejadorAcciones.")
        # ---------------------

        print("DEBUG: Fin conexión.")
    # --- FIN _conectar_senales ---

    def _configurar_timer(self):
        if self.reproductor: self.timer_verificacion = QTimer(self); self.timer_verificacion.timeout.connect(self._slot_actualizar_y_verificar); self.timer_verificacion.setInterval(INTERVALO_TIMER_MS); print(f"Timer OK ({INTERVALO_TIMER_MS} ms).")
        else: print("WARN: No Timer (no reproductor).")

    # --- Slots de UI (sin cambios) ---
    @Slot()
    def _slot_seleccion_cambiada(self):
        print("DEBUG: Slot: Selección cambiada.")
        lista = self.lista_reproduccion_widget;
        if not lista: return
        brush_vacio = self.palette().base(); default_font = lista.font(); indices_seleccionados = {lista.row(item) for item in lista.selectedItems()}
        for i in range(lista.count()):
            item = lista.item(i)
            if item and i not in indices_seleccionados:
                 if lista._indice_item_resaltado_actualmente != i: item.setFont(default_font)
                 item.setBackground(brush_vacio)
        if self.reproductor:
            ruta_seleccionada = lista.obtener_ruta_seleccionada()
            if ruta_seleccionada != self.reproductor.archivo_cargado and (self.reproductor.esta_reproduciendo() or self.reproductor.esta_pausado()):
                print("DEBUG: Selección diferente, reseteando tiempos."); self._resetear_tiempos_ui()
        self._actualizar_estado_controles()
    @Slot()
    def _slot_modelo_lista_cambiado(self):
        print("DEBUG: Slot: Modelo lista cambiado."); self.actualizar_display_tiempo_total_lista(); self._slot_seleccion_cambiada()

    # --- Slot del Timer MODIFICADO ---
    @Slot()
    def _slot_actualizar_y_verificar(self):
        """Timer: Actualiza progreso y EMITE SEÑAL al fin de canción."""
        if not self.reproductor: # Ya no necesita al manejador aquí
            if self.timer_verificacion and self.timer_verificacion.isActive(): self.timer_verificacion.stop()
            return

        if self.reproductor.esta_reproduciendo():
            self._actualizar_progreso_ui()

        try:
            if self.reproductor.verificar_fin_cancion():
                print("DEBUG: Fin de canción detectado por el timer.")
                ruta_terminada = self.reproductor.archivo_cargado # Guardar ruta

                # --- Emitir la señal en lugar de actuar ---
                if ruta_terminada:
                    print(f"DEBUG: Emitiendo señal cancion_terminada_auto con ruta: {ruta_terminada}")
                    self.cancion_terminada_auto.emit(ruta_terminada)
                else:
                    # Caso raro: terminó pero no había archivo cargado? Detener por si acaso.
                    print("WARN: Canción terminó pero no había ruta cargada? Deteniendo.")
                    if self.manejador_acciones: # Pedir al manejador que detenga
                        self.manejador_acciones.accion_stop()
                # --- FIN EMISIÓN SEÑAL ---

                # Ya NO se elimina ni se llama a siguiente/reproducir desde aquí

        except pygame.error as e_pygame: print(f"WARN timer: Pygame ({e_pygame})"); self.timer_verificacion.stop()
        except Exception as e: print(f"ERROR timer: {e}"); traceback.print_exc(); self.timer_verificacion.stop()
    # --- FIN Slot del Timer ---

    # --- Métodos restantes (sin cambios) ---
    def _actualizar_estado_controles(self):
        if not self.controles_widget or not self.lista_reproduccion_widget or not self.barra_botones_widget or not self.panel_derecho_widget: return
        rep_ok = bool(self.reproductor and self.reproductor._inicializado); esta_reproduciendo = rep_ok and self.reproductor.esta_reproduciendo(); esta_pausado = rep_ok and self.reproductor.esta_pausado(); duracion_valida = rep_ok and self.reproductor.duracion_ms > 0; hay_items = self.lista_reproduccion_widget.count() > 0; hay_sel = bool(self.lista_reproduccion_widget.selectedItems()); hay_multiples = self.lista_reproduccion_widget.count() > 1
        self.controles_widget.habilitar_controles( habilitar=(rep_ok and hay_items), habilitar_progreso=(rep_ok and (esta_reproduciendo or esta_pausado) and duracion_valida) )
        if rep_ok: self.controles_widget.actualizar_estado_play_pause(esta_reproduciendo); self.controles_widget.boton_stop.setEnabled(esta_reproduciendo or esta_pausado); self.controles_widget.boton_siguiente.setEnabled(hay_items)
        self.barra_botones_widget.habilitar_boton_quitar(hay_sel); self.barra_botones_widget.habilitar_boton_guardar(hay_items); self.barra_botones_widget.habilitar_boton_limpiar(hay_items); self.barra_botones_widget.habilitar_boton_reordenar(hay_multiples)
        self.panel_derecho_widget.habilitar_controles_internos(rep_ok)
        if self.timer_verificacion:
            if esta_reproduciendo and not self.timer_verificacion.isActive(): self.timer_verificacion.start()
            elif not esta_reproduciendo and self.timer_verificacion.isActive(): self.timer_verificacion.stop()
    def _actualizar_progreso_ui(self):
        if self.reproductor and self.controles_widget and self.reproductor.esta_reproduciendo():
            try: pos_ms = self.reproductor.obtener_posicion_ms(); self.controles_widget.actualizar_tiempo_actual(pos_ms)
            except Exception as e: print(f"Error actualizando progreso: {e}")
    def _resetear_tiempos_ui(self):
        if self.controles_widget: self.controles_widget.actualizar_tiempo_total(0); self.controles_widget.actualizar_tiempo_actual(0)
    @Slot()
    def actualizar_display_tiempo_total_lista(self):
        if not self.panel_derecho_widget: print("WARN TIEMPO_UI: panel_derecho_widget no existe."); return
        if self.manejador_acciones:
            try: tiempo_formateado = self.manejador_acciones.calcular_y_formatear_tiempo_total_lista(); self.panel_derecho_widget.actualizar_tiempo_total(tiempo_formateado)
            except Exception as e: print(f"ERROR TIEMPO_UI: {e}"); traceback.print_exc(); self.panel_derecho_widget.actualizar_tiempo_total("--:--:--")
        else: self.panel_derecho_widget.actualizar_tiempo_total("--:--:--")
    @Slot(str)
    def actualizar_boton_aire(self, nuevo_estado: str):
        if self.panel_derecho_widget: self.panel_derecho_widget.actualizar_boton_aire_ui(nuevo_estado)
        else: print("WARN: panel_derecho_widget no existe para AIRE.")
    def _mostrar_error(self, titulo: str, mensaje: str):
        print(f"ERROR GUI: {titulo} - {mensaje}")
        try: QMessageBox.critical(self, titulo, mensaje)
        except RuntimeError as e: print(f"WARN QMessageBox: {e}")
    def _mostrar_info(self, titulo: str, mensaje: str):
        print(f"INFO GUI: {titulo} - {mensaje}")
        try: QMessageBox.information(self, titulo, mensaje)
        except RuntimeError as e: print(f"WARN QMessageBox: {e}")
    def closeEvent(self, event: QCloseEvent):
        print("Evento closeEvent. Limpiando...");
        if self.timer_verificacion and self.timer_verificacion.isActive(): print("  Deteniendo timer..."); self.timer_verificacion.stop()
        if self.reproductor:
            print("  Limpiando reproductor...");
            try: self.reproductor.detener(); self.reproductor.limpiar()
            except Exception as e: print(f"  ERROR limpieza reproductor: {e}"); traceback.print_exc()
        print("Limpieza OK."); event.accept()
    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls(): event.acceptProposedAction()
        else: event.ignore()
    def dropEvent(self, event: QDropEvent):
        if self.lista_reproduccion_widget and self.lista_reproduccion_widget.geometry().contains(event.position().toPoint()): pass
        else: event.ignore()

# --- Fin del archivo app/gui/ventana_principal.py ---