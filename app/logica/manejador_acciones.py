# -*- coding: utf-8 -*-
"""
Define la clase ManejadorAcciones.
REFACTORIZADO: Slot _slot_manejar_fin_automatico elimina ítem terminado.
CORREGIDO: Sintaxis e indentación revisada exhaustivamente.
"""

import typing
if typing.TYPE_CHECKING:
    from PySide6.QtWidgets import QListWidgetItem
    from app.gui.ventana_principal import VentanaPrincipal
    from app.gui.componentes.lista_reproduccion_widget import ListaReproduccionWidget
    from app.gui.componentes.controles_reproduccion_widget import ControlesReproduccionWidget
    from .reproductor_audio import ReproductorAudio

from PySide6.QtWidgets import QFileDialog, QMessageBox, QListWidgetItem, QApplication
from PySide6.QtCore import QDir, Qt, QTimer, Signal, QObject, Slot
from app.utilidades.archivos import buscar_archivos_audio_en_carpeta, obtener_directorio_padre
from app.utilidades.json_handler import guardar_json, cargar_json
from app.utilidades.audio import obtener_duracion_ms
import random
import os
import traceback

# Constantes
MODO_NORMAL = 0
MODO_REPETIR_TODO = 1
MODO_REPETIR_UNO = 2
MODO_ALEATORIO = 3
MODOS = [MODO_NORMAL, MODO_REPETIR_TODO, MODO_REPETIR_UNO, MODO_ALEATORIO]
FILTRO_PLAYLIST = "Listas Radio Anarkadia (*.rka);;Todos (*)"
EXTENSION_PLAYLIST_POR_DEFECTO = ".rka"
FORMATOS_AUDIO_FILTRO = "Audio (*.mp3 *.ogg *.wav *.flac);;Todos (*)"
ESTADO_AIRE_100 = "a_100"
ESTADO_AIRE_20 = "a_20"
VOLUMEN_AIRE_100 = 1.0
VOLUMEN_AIRE_20 = 0.2
DURACION_FADE_MS = 500
INTERVALO_FADE_MS = 25

def formatear_tiempo_hhmmss(milisegundos: int) -> str:
    if milisegundos < 0:
        return "--:--:--"
    total_segundos = milisegundos // 1000
    segundos = total_segundos % 60
    total_minutos = total_segundos // 60
    minutos = total_minutos % 60
    horas = total_minutos // 60
    return f"{horas:02d}:{minutos:02d}:{segundos:02d}"

class ManejadorAcciones(QObject):
    """Coordina acciones, maneja fin automático de canción."""

    def __init__(self, ventana: 'VentanaPrincipal', lista_widget: 'ListaReproduccionWidget', controles_widget: 'ControlesReproduccionWidget', reproductor: 'ReproductorAudio'):
        super().__init__()
        self.ventana = ventana
        self.lista_widget = lista_widget
        self.controles_widget = controles_widget
        self.reproductor = reproductor
        self.ultima_ruta_playlist = QDir.homePath()
        self.modo_reproduccion_actual = MODO_NORMAL
        self.estado_aire_actual = ESTADO_AIRE_100
        self.timer_volumen_aire = QTimer(self)
        self.timer_volumen_aire.setInterval(INTERVALO_FADE_MS)
        self.timer_volumen_aire.timeout.connect(self._actualizar_fade_volumen)
        self.volumen_objetivo_aire = VOLUMEN_AIRE_100
        self.volumen_actual_fade = VOLUMEN_AIRE_100
        self.paso_volumen_fade = 0.0
        print("ManejadorAcciones inicializado (con slot para fin automático).")

    def _reproducir_item_en_indice(self, indice: int) -> bool:
        print(f"\n--- DEBUG: Iniciando _reproducir_item_en_indice({indice}) ---")
        if not (self.lista_widget and self.reproductor):
            print("ERROR: Lista o reproductor no disponibles.")
            return False
        if not (0 <= indice < self.lista_widget.count()):
            print(f"ERROR: Índice {indice} fuera de rango.")
            return False

        item = self.lista_widget.item(indice)
        if not item:
            print(f"ERROR: No item en índice {indice}.")
            return False

        ruta = item.data(Qt.ItemDataRole.UserRole)
        if not ruta:
            print(f"ERROR: Ítem {indice} sin ruta.")
            return False

        nb = os.path.basename(ruta)
        print(f"Intentando: '{nb}'")

        if (self.reproductor.esta_reproduciendo() or self.reproductor.esta_pausado()) and self.reproductor.archivo_cargado != ruta:
            print("Deteniendo anterior.")
            self.accion_stop()

        self.lista_widget.setCurrentRow(indice)

        carga_ok = self._cargar_y_manejar_error(ruta)
        if not carga_ok:
            print(f"Fallo carga '{nb}'.")
            return False

        self.reproductor.volumen = self.volumen_objetivo_aire
        if self.controles_widget:
            self.controles_widget.actualizar_volumen_visual(int(self.volumen_objetivo_aire * 100))

        reprod_ok = self.reproductor.reproducir()
        if not reprod_ok:
            print(f"ERROR: Fallo reprod '{nb}'.")
            self._mostrar_error_ventana("Error", f"No iniciar:\n{nb}")
            return False

        print(f"Reproducción OK: '{nb}'.")
        print("Resaltando y moviendo...")
        self.lista_widget.resaltar_y_mover_item_actual(ruta)

        if self.controles_widget:
            if self.reproductor.duracion_ms > 0:
                print(f"Actualizando T.Total: {self.reproductor.duracion_ms}ms")
                self.controles_widget.actualizar_tiempo_total(self.reproductor.duracion_ms)
            else:
                self.controles_widget.actualizar_tiempo_total(0)
            print(f"Actualizando nombre: '{nb}'")
            self.controles_widget.actualizar_cancion_actual(nb)

        self._actualizar_estado_controles_ventana()
        print(f"--- Fin _reproducir_item_en_indice({indice}) ---")
        return True

    # --- Acciones de Archivo ---
    def accion_anadir_archivo(self):
        print("DEBUG: accion_anadir_archivo...")
        dir_ini = getattr(self.ventana, 'ultima_ruta_usada', QDir.homePath())
        dir_ini = dir_ini if QDir(dir_ini).exists() else QDir.homePath()
        if not self.ventana or not self.lista_widget:
            print("ERROR: Ventana o Lista no disponibles.")
            return
        try:
            rutas, _ = QFileDialog.getOpenFileNames(self.ventana, "Seleccionar Archivos de Audio", dir_ini, FORMATOS_AUDIO_FILTRO)
            if rutas:
                print(f"Añadiendo {len(rutas)} archivos...")
                for r in rutas:
                    self.lista_widget.agregar_archivo(r)
                try:
                    nuevo_dir = os.path.dirname(rutas[0])
                    if nuevo_dir and os.path.isdir(nuevo_dir) and hasattr(self.ventana, 'ultima_ruta_usada'):
                        print(f"DEBUG: Actualizando ultima_ruta_usada a: {nuevo_dir}")
                        self.ventana.ultima_ruta_usada = nuevo_dir
                except IndexError:
                    print("WARN: No se pudo obtener directorio de rutas[0].")
                except Exception as e_dir:
                    print(f"WARN: Error al obtener/actualizar directorio: {e_dir}")
            else:
                print("No rutas seleccionadas.")
        except Exception as e:
            print(f"ERROR inesperado en accion_anadir_archivo: {e}")
            traceback.print_exc()
            self._mostrar_error_ventana("Error al Añadir Archivos", f"Ocurrió un error:\n{e}")

    def accion_anadir_carpeta(self):
        print("DEBUG: accion_anadir_carpeta...")
        dir_ini = getattr(self.ventana, 'ultima_ruta_usada', QDir.homePath())
        dir_ini = dir_ini if QDir(dir_ini).exists() else QDir.homePath()
        if not self.ventana or not self.lista_widget:
            print("ERROR: Ventana o Lista no disponibles.")
            return
        try:
            ruta_c = QFileDialog.getExistingDirectory(self.ventana, "Seleccionar Carpeta con Audio", dir_ini, QFileDialog.Option.ShowDirsOnly | QFileDialog.Option.DontResolveSymlinks)
            if ruta_c:
                print(f"Carpeta seleccionada: {ruta_c}")
                if hasattr(self.ventana, 'ultima_ruta_usada'):
                    self.ventana.ultima_ruta_usada = ruta_c
                print("Buscando archivos de audio (recursivamente)...")
                archivos = buscar_archivos_audio_en_carpeta(ruta_c, recursivo=True)
                if archivos is None:
                    self._mostrar_error_ventana("Ruta Inválida", f"La ruta seleccionada no parece ser una carpeta válida:\n{ruta_c}")
                elif archivos:
                    print(f"Encontrados {len(archivos)}. Añadiendo...")
                    for r in archivos:
                         self.lista_widget.agregar_archivo(r)
                else:
                    self._mostrar_info_ventana("Carpeta Vacía", f"No se encontraron archivos de audio compatibles en:\n{ruta_c}")
            else:
                print("No se seleccionó carpeta.")
        except Exception as e:
            print(f"ERROR inesperado en accion_anadir_carpeta: {e}")
            traceback.print_exc()
            self._mostrar_error_ventana("Error al Añadir Carpeta", f"Ocurrió un error:\n{e}")

    # --- accion_quitar_seleccionado CORREGIDO ---
    def accion_quitar_seleccionado(self):
        """Quita el ítem seleccionado de la lista."""
        print("DEBUG: accion_quitar_seleccionado...")
        ruta_sel = None
        indice_sel = -1
        item_sel = None # Inicializar item_sel

        if self.lista_widget:
            item_sel = self.lista_widget.currentItem() # Obtener ítem seleccionado
            # --- CORRECCIÓN DE INDENTACIÓN Y LÓGICA ---
            if item_sel:
                ruta_sel = item_sel.data(Qt.ItemDataRole.UserRole) # Obtener ruta
                indice_sel = self.lista_widget.row(item_sel) # Obtener índice
            # --- FIN CORRECCIÓN ---

        if self.reproductor and self.reproductor.archivo_cargado == ruta_sel and ruta_sel is not None:
            print("Quitando activa, deteniendo...")
            self.accion_stop()

        if self.lista_widget and item_sel and indice_sel != -1: # Asegurar que item_sel exista
            nombre = os.path.basename(ruta_sel) if ruta_sel else f"Índice {indice_sel}"
            print(f"Quitando '{nombre}'")
            self.lista_widget.quitar_seleccionado() # Llama al método del widget
        elif not item_sel: # Usar item_sel para verificar si hubo selección
            print("No selección.")
        else: # Caso raro: item_sel existe pero indice_sel es -1
            print("ERROR: Índice inválido?")
    # --- FIN accion_quitar_seleccionado ---

    def accion_limpiar_lista(self):
        print("DEBUG: accion_limpiar_lista...")
        if not self.lista_widget or self.lista_widget.count() == 0:
            print("Lista vacía.")
            return
        resp = QMessageBox.question(self.ventana, "Confirmar", "¿Limpiar lista?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
        if resp == QMessageBox.StandardButton.Yes:
            print("Limpiando...")
            self.accion_stop()
            if self.lista_widget:
                self.lista_widget.clear()
        else:
            print("Cancelado.")

    def accion_manejar_archivos_soltados(self, rutas: list[str]):
        print(f"DEBUG: accion_manejar_archivos_soltados ({len(rutas)})...")
        if self.lista_widget:
            print(f"Añadiendo {len(rutas)}...")
            for r in rutas:
                self.lista_widget.agregar_archivo(r)
        else:
            print("ERROR: lista_widget None.")

    # --- Acciones de Reproducción ---
    def accion_play_pause(self):
        print("\n--- DEBUG: Iniciando accion_play_pause ---")
        if not self.reproductor:
            print("Salida - No reproductor.")
            return

        if self.reproductor.esta_pausado():
            print("Reanudando...")
            if self.reproductor.reproducir():
                print("OK.")
            else:
                print("ERROR: Fallo reanudar.")
                self._mostrar_error_ventana("Error", "No se pudo reanudar.")
            self._actualizar_estado_controles_ventana()
            return

        if self.reproductor.esta_reproduciendo():
            print("Pausando...")
            if self.reproductor.pausar():
                print("OK.")
            else:
                print("ERROR: Fallo pausar.")
            self._actualizar_estado_controles_ventana()
            return

        indice_a_reproducir = -1
        if self.lista_widget:
            idx_sel = self.lista_widget.currentRow()
            if 0 <= idx_sel < self.lista_widget.count():
                indice_a_reproducir = idx_sel
                print(f"Reproduciendo selección {idx_sel}.")
            elif self.lista_widget.count() > 0:
                indice_a_reproducir = 0
                print("Reproduciendo primer ítem.")
            else:
                print("Lista vacía.")
                self._mostrar_info_ventana("Lista Vacía", "Agregá canciones.")

        if indice_a_reproducir != -1:
            self._reproducir_item_en_indice(indice_a_reproducir)
        else:
            self._actualizar_estado_controles_ventana()
        print("--- Fin accion_play_pause ---")

    def accion_stop(self):
        print("DEBUG: accion_stop...")
        if not self.reproductor or (not self.reproductor.esta_reproduciendo() and not self.reproductor.esta_pausado()):
            print("Nada que detener.")
            return
        if self.timer_volumen_aire.isActive():
            print("Deteniendo fade.")
            self.timer_volumen_aire.stop()
        detenido_ok = self.reproductor.detener()
        if not detenido_ok:
            print("WARN: Error al detener.")
        QApplication.processEvents()
        if self.controles_widget:
            print("Limpiando UI.")
            self.controles_widget.actualizar_cancion_actual("")
            self._resetear_tiempos_ui_ventana()
        if self.lista_widget:
            print("Reseteando estilo lista.")
            self.lista_widget.resetear_estilo_item_actual()
        self._actualizar_estado_controles_ventana()
        print("Stop completado.")

    def accion_siguiente(self, forzado_por_usuario: bool = True):
        print(f"\n--- DEBUG: Iniciando accion_siguiente (Forzado={forzado_por_usuario}) ---")
        if not self.reproductor or not self.lista_widget or self.lista_widget.count() == 0:
            print("Precondiciones fallan.")
            self.accion_stop()
            return
        total = self.lista_widget.count()
        idx_ref = self.lista_widget._indice_item_resaltado_actualmente
        idx_ref = idx_ref if 0 <= idx_ref < total else -1
        print(f"Idx. Ref={idx_ref}, Total={total}, Modo={self.modo_reproduccion_actual}")
        idx_siguiente = -1
        if self.modo_reproduccion_actual == MODO_REPETIR_UNO and not forzado_por_usuario:
            if idx_ref != -1:
                idx_siguiente = idx_ref
                print("Modo Rep1: Misma canción.")
            else:
                print("Modo Rep1: Idx inválido.")
                self.accion_stop()
                return
        elif self.modo_reproduccion_actual == MODO_ALEATORIO:
            if total <= 1:
                idx_siguiente = 0 if total == 1 else -1
            else:
                cands = list(range(total))
                if idx_ref != -1:
                    cands.remove(idx_ref)
                idx_siguiente = random.choice(cands)
            print(f"Modo Aleat: Sgte={idx_siguiente}")
            if idx_siguiente == -1:
                print("Lista vacía?")
                self.accion_stop()
                return
        else: # Normal o Repetir Todo
            idx_siguiente_prov = idx_ref + 1
            if idx_siguiente_prov < total:
                idx_siguiente = idx_siguiente_prov
                print(f"Normal/RepTodo: Sgte={idx_siguiente}")
            else: # Fin de lista
                if self.modo_reproduccion_actual == MODO_REPETIR_TODO:
                    idx_siguiente = 0
                    print("RepTodo: Volviendo a 0")
                else:
                    print("Normal: Fin lista.")
                    self.accion_stop()
                    return
        print(f"Índice SIGUIENTE: {idx_siguiente}")
        if 0 <= idx_siguiente < total:
            self._reproducir_item_en_indice(idx_siguiente)
        else:
            print(f"ERROR Lógico: Índice inválido ({idx_siguiente}).")
            self.accion_stop()
        print("--- Fin accion_siguiente ---")

    def accion_item_doble_clic(self, item: 'QListWidgetItem'):
         print("\n--- DEBUG: accion_item_doble_clic ---")
         if not self.reproductor or not item or not self.lista_widget:
             print("Salida: Precondiciones.")
             return
         indice = self.lista_widget.row(item)
         print(f"Doble clic índice {indice}")
         if 0 <= indice < self.lista_widget.count():
             self._reproducir_item_en_indice(indice)
         else:
              print(f"ERROR: Índice inválido ({indice}).")
              self._actualizar_estado_controles_ventana()
         print("--- Fin accion_item_doble_clic ---")

    # --- Acciones de control y playlist ---
    def accion_cambiar_posicion(self, pos_ms: int):
        if self.reproductor and (self.reproductor.esta_reproduciendo() or self.reproductor.esta_pausado()):
            seg = pos_ms / 1000.0
            print(f"Cambiando a {seg:.2f}s...")
            if self.reproductor.establecer_posicion_segundos(seg):
                print("OK.")
                self._actualizar_progreso_ui_ventana()
                self._actualizar_estado_controles_ventana()
            else:
                print("Fallo.")
        else:
            print("No activo.")

    def accion_cambiar_volumen(self, val_porc: int):
        if self.reproductor:
            vol = val_porc / 100.0
            if self.timer_volumen_aire.isActive():
                print("Fade AIRE detenido.")
                self.timer_volumen_aire.stop()
                self.volumen_objetivo_aire = vol
                self.volumen_actual_fade = vol
                nuevo_estado = ESTADO_AIRE_100 if vol >= 0.6 else ESTADO_AIRE_20
                if self.estado_aire_actual != nuevo_estado:
                    self.estado_aire_actual = nuevo_estado
                    self._actualizar_boton_aire_ventana(nuevo_estado)
            self.reproductor.volumen = vol

    def accion_cambiar_modo(self):
        print("DEBUG: accion_cambiar_modo...")
        try:
            idx = MODOS.index(self.modo_reproduccion_actual)
        except ValueError:
            idx = -1
            print("WARN: Modo desconocido.")
        idx_sig = (idx + 1) % len(MODOS)
        self.modo_reproduccion_actual = MODOS[idx_sig]
        modos_str = ["Normal", "Rep Todo", "Rep Uno", "Aleatorio"]
        print(f"Cambiando a: {self.modo_reproduccion_actual} ({modos_str[idx_sig]})")
        if self.controles_widget:
            self.controles_widget.actualizar_modo_visual(self.modo_reproduccion_actual)

    def accion_alternar_volumen_aire(self):
        print("DEBUG: accion_alternar_volumen_aire...")
        if not self.reproductor:
            print("No reproductor.")
            return
        nuevo_estado = ESTADO_AIRE_20 if self.estado_aire_actual == ESTADO_AIRE_100 else ESTADO_AIRE_100
        self.volumen_objetivo_aire = VOLUMEN_AIRE_20 if nuevo_estado == ESTADO_AIRE_20 else VOLUMEN_AIRE_100
        print(f"Cambiando a: {nuevo_estado} (Vol: {self.volumen_objetivo_aire*100:.0f}%)")
        self.estado_aire_actual = nuevo_estado
        self._actualizar_boton_aire_ventana(nuevo_estado)
        if self.controles_widget:
            self.controles_widget.actualizar_volumen_visual(int(self.volumen_objetivo_aire * 100))
        if self.timer_volumen_aire.isActive():
            self.timer_volumen_aire.stop()
            print("Fade anterior detenido.")
        self.volumen_actual_fade = self.reproductor.volumen
        diff = self.volumen_objetivo_aire - self.volumen_actual_fade
        pasos = max(1, DURACION_FADE_MS // INTERVALO_FADE_MS)
        self.paso_volumen_fade = diff / pasos
        print(f"Iniciando fade: {self.volumen_actual_fade:.2f} -> {self.volumen_objetivo_aire:.2f}")
        if abs(diff) > 0.01:
            self.timer_volumen_aire.start()
        else:
            self.reproductor.volumen = self.volumen_objetivo_aire
            print("Ya en objetivo.")

    @Slot()
    def _actualizar_fade_volumen(self):
        if not self.reproductor:
            self.timer_volumen_aire.stop()
            return
        self.volumen_actual_fade += self.paso_volumen_fade
        alcanzado = (self.paso_volumen_fade >= 0 and self.volumen_actual_fade >= self.volumen_objetivo_aire) or \
                    (self.paso_volumen_fade < 0 and self.volumen_actual_fade <= self.volumen_objetivo_aire)
        vol_final = self.volumen_objetivo_aire if alcanzado else max(0.0, min(1.0, self.volumen_actual_fade))
        if alcanzado:
            self.timer_volumen_aire.stop()
        self.reproductor.volumen = vol_final

    def accion_guardar_lista(self):
        print("DEBUG: accion_guardar_lista...")
        if not self.lista_widget or self.lista_widget.count() == 0:
            self._mostrar_info_ventana("Guardar", "Lista vacía.")
            return
        dir_ini = self.ultima_ruta_playlist if QDir(self.ultima_ruta_playlist).exists() else QDir.homePath()
        ruta_f, _ = QFileDialog.getSaveFileName(self.ventana, "Guardar Lista", dir_ini, FILTRO_PLAYLIST)
        if ruta_f:
            if not ruta_f.lower().endswith(EXTENSION_PLAYLIST_POR_DEFECTO):
                ruta_f += EXTENSION_PLAYLIST_POR_DEFECTO
            print(f"Guardando en: {ruta_f}")
            rutas = self.lista_widget.obtener_todas_las_rutas()
            if guardar_json(ruta_f, rutas):
                self._mostrar_info_ventana("Guardado", f"Lista:\n{ruta_f}")
                padre = obtener_directorio_padre(ruta_f)
                if padre:
                    self.ultima_ruta_playlist = padre
            else:
                self._mostrar_error_ventana("Error Guardar", f"No guardar:\n{ruta_f}")
        else:
            print("Cancelado.")

    def accion_cargar_lista(self):
        print("DEBUG: accion_cargar_lista...")
        dir_ini = self.ultima_ruta_playlist if QDir(self.ultima_ruta_playlist).exists() else QDir.homePath()
        ruta_f, _ = QFileDialog.getOpenFileName(self.ventana, "Cargar Lista", dir_ini, FILTRO_PLAYLIST)
        if ruta_f:
            print(f"Archivo: {ruta_f}")
            reemplazar = True
            if self.lista_widget and self.lista_widget.count() > 0:
                resp = QMessageBox.question(self.ventana, "Confirmar", "¿Reemplazar lista?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel, QMessageBox.StandardButton.Yes)
                if resp == QMessageBox.StandardButton.Cancel:
                    print("Cancelado.")
                    return
                elif resp == QMessageBox.StandardButton.No:
                    print("Añadiendo.")
                    reemplazar = False
            if reemplazar:
                print("Reemplazando...")
                self.accion_stop()
                if self.lista_widget:
                    self.lista_widget.clear()
            datos = cargar_json(ruta_f)
            if isinstance(datos, list) and all(isinstance(r, str) for r in datos):
                print(f"Cargando {len(datos)} rutas...")
                n_err = 0
                for r in datos:
                    if os.path.exists(r) and os.path.isfile(r):
                        if self.lista_widget:
                            self.lista_widget.agregar_archivo(r)
                    else:
                        n_err += 1
                        print(f"WARN: No existe: {r}")
                msg = f"Lista cargada:\n{ruta_f}"
                if n_err > 0:
                    msg += f"\n({n_err} no encontrados)"
                self._mostrar_info_ventana("Cargado", msg)
                padre = obtener_directorio_padre(ruta_f)
                if padre:
                    self.ultima_ruta_playlist = padre
            elif datos is not None:
                print("Error formato.")
                self._mostrar_error_ventana("Error Formato", "No válido.")
            else:
                print("Error carga.")
                self._mostrar_error_ventana("Error Carga", f"No leer:\n{ruta_f}")
        else:
            print("No archivo.")

    def accion_reordenar_lista_aleatorio(self):
        print("DEBUG: accion_reordenar_lista_aleatorio...")
        if not self.lista_widget or self.lista_widget.count() <= 1:
            print("Pocos elementos.")
            return
        print("Reordenando...")
        ruta_resaltada_previa = None
        idx_resaltado = self.lista_widget._indice_item_resaltado_actualmente
        if idx_resaltado != -1:
            item_prev = self.lista_widget.item(idx_resaltado)
            if item_prev:
                ruta_resaltada_previa = item_prev.data(Qt.ItemDataRole.UserRole)
        idx_sel_prev = self.lista_widget.currentRow()
        signals_blocked = self.lista_widget.blockSignals(True)
        print(f"Señales block: {signals_blocked}")
        try:
            items_data = []
            print(f"Extrayendo {self.lista_widget.count()} ítems...")
            for i in range(self.lista_widget.count()):
                item_i = self.lista_widget.item(i)
                if item_i:
                    items_data.append({
                        "icono": item_i.icon(),
                        "texto": item_i.text(),
                        "data": item_i.data(Qt.ItemDataRole.UserRole)
                    })
            self.lista_widget.clear()
            print("Lista limpiada.")
            random.shuffle(items_data)
            print("Ítems barajados.")
            print("Reinsertando...")
            for d in items_data:
                item = QListWidgetItem(d["icono"], d["texto"])
                item.setData(Qt.ItemDataRole.UserRole, d["data"])
                if self.lista_widget._fuente_default:
                    item.setFont(self.lista_widget._fuente_default)
                self.lista_widget.addItem(item)
            print("Reinsertados.")
            if ruta_resaltada_previa:
                print(f"Buscando previa: {os.path.basename(ruta_resaltada_previa)}")
                nuevo_idx = -1
                for i in range(self.lista_widget.count()):
                    item = self.lista_widget.item(i)
                    if item and item.data(Qt.ItemDataRole.UserRole) == ruta_resaltada_previa:
                        nuevo_idx = i
                        break
                if nuevo_idx != -1:
                    print(f"Encontrada en {nuevo_idx}. Resaltando...")
                    self.lista_widget.resaltar_y_mover_item_actual(ruta_resaltada_previa)
                    self.lista_widget.setCurrentRow(0) # Asegurar selección en tope
                else:
                    print("WARN: No encontrada.")
                    self.lista_widget.resetear_estilo_item_actual()
                    if 0 <= idx_sel_prev < self.lista_widget.count():
                        self.lista_widget.setCurrentRow(idx_sel_prev)
            else:
                print("No había resaltado previo.")
                if 0 <= idx_sel_prev < self.lista_widget.count():
                    self.lista_widget.setCurrentRow(idx_sel_prev)
        except Exception as e:
            print(f"ERROR: {e}")
            traceback.print_exc()
        finally:
            self.lista_widget.blockSignals(signals_blocked)
            print(f"Señales unblock: {not signals_blocked}")
            print("Reordenamiento finalizado.")
            self._slot_seleccion_cambiada_ventana()

    def calcular_y_formatear_tiempo_total_lista(self) -> str:
        print("DEBUG TIEMPO: Calculando total...")
        if not self.lista_widget: return "00:00:00"
        t_ms = 0
        rutas = self.lista_widget.obtener_todas_las_rutas()
        if not rutas: return "00:00:00"
        print(f"Para {len(rutas)} rutas.")
        n_err_nf = 0
        n_err_dur = 0
        for r in rutas:
            d = obtener_duracion_ms(r)
            if d > 0:
                t_ms += d
            elif not os.path.exists(r):
                n_err_nf += 1
            else:
                n_err_dur += 1
        if n_err_nf: print(f"WARN: {n_err_nf} no encontrados.")
        if n_err_dur: print(f"WARN: Error duración {n_err_dur}.")
        fmt = formatear_tiempo_hhmmss(t_ms)
        print(f"Total: {t_ms} ms -> {fmt}")
        return fmt

    def _cargar_y_manejar_error(self, ruta_archivo: str) -> bool:
        nb = os.path.basename(ruta_archivo)
        print(f"DEBUG: _cargar_y_manejar_error('{nb}')...")
        if not self.reproductor: return False
        self._resetear_tiempos_ui_ventana()
        if self.controles_widget:
            self.controles_widget.actualizar_cancion_actual(f"Cargando: {nb}...")
        try:
            carga_ok = self.reproductor.cargar_archivo(ruta_archivo)
            print(f"Resultado carga: {carga_ok}")
            if not carga_ok:
                 self._mostrar_error_ventana("Error Carga", f"No cargar:\n{nb}")
                 if self.controles_widget: self.controles_widget.actualizar_cancion_actual("")
                 return False
            return True
        except Exception as e:
            print(f"ERROR carga '{nb}': {e}")
            traceback.print_exc()
            self._mostrar_error_ventana("Error Crítico Carga", f"{e}")
            if self.controles_widget: self.controles_widget.actualizar_cancion_actual("")
            return False

    # --- Slot para manejar fin automático ---
    @Slot(str)
    def _slot_manejar_fin_automatico(self, ruta_terminada: str):
        print(f"\n--- DEBUG: Slot _slot_manejar_fin_automatico recibido para: {os.path.basename(ruta_terminada)} ---")
        if not self.lista_widget:
            print("ERROR: lista_widget no disponible.")
            return
        item_eliminado_ok = False
        if self.lista_widget.count() > 0:
            item_a_eliminar = self.lista_widget.item(0)
            if item_a_eliminar and item_a_eliminar.data(Qt.ItemDataRole.UserRole) == ruta_terminada:
                print(f"DEBUG: Eliminando ítem terminado '{os.path.basename(ruta_terminada)}'...")
                signals_blocked = self.lista_widget.blockSignals(True)
                try:
                    item_obj_eliminado = self.lista_widget.takeItem(0)
                    if item_obj_eliminado:
                        print("DEBUG: Ítem eliminado. Procesando eventos...")
                        QApplication.processEvents()
                        print("DEBUG: Eventos procesados.")
                        item_eliminado_ok = True
                        if hasattr(self.lista_widget, '_indice_item_resaltado_actualmente') and self.lista_widget._indice_item_resaltado_actualmente == 0:
                            self.lista_widget._indice_item_resaltado_actualmente = -1
                    else:
                        print("WARN: takeItem(0) falló.")
                finally:
                    self.lista_widget.blockSignals(signals_blocked)
            else:
                print("WARN: Ítem en 0 no coincide con canción terminada. No se elimina.")
                if hasattr(self.lista_widget, 'resetear_estilo_item_actual'):
                    self.lista_widget.resetear_estilo_item_actual()
        else:
            print("DEBUG: Lista ya estaba vacía.")

        if self.lista_widget.count() > 0:
            print("DEBUG: Quedan ítems, reproduciendo nuevo índice 0...")
            self._reproducir_item_en_indice(0)
        else:
            print("DEBUG: Lista vacía. Deteniendo.")
            self.accion_stop()
        print("--- DEBUG: Fin _slot_manejar_fin_automatico ---")

    # --- Helpers ---
    def _mostrar_error_ventana(self, t: str, m: str):
        if self.ventana and hasattr(self.ventana, '_mostrar_error'): self.ventana._mostrar_error(t, m)
        else: print(f"ERROR (Ventana no disp.): {t} - {m}")
    def _mostrar_info_ventana(self, t: str, m: str):
        if self.ventana and hasattr(self.ventana, '_mostrar_info'): self.ventana._mostrar_info(t, m)
        else: print(f"INFO (Ventana no disp.): {t} - {m}")
    def _actualizar_estado_controles_ventana(self):
         if self.ventana and hasattr(self.ventana, '_actualizar_estado_controles'): self.ventana._actualizar_estado_controles()
    def _resetear_tiempos_ui_ventana(self):
        if self.ventana and hasattr(self.ventana, '_resetear_tiempos_ui'): self.ventana._resetear_tiempos_ui()
    def _slot_seleccion_cambiada_ventana(self):
         if self.ventana and hasattr(self.ventana, '_slot_seleccion_cambiada'): self.ventana._slot_seleccion_cambiada()
    def _actualizar_boton_aire_ventana(self, estado: str):
         if self.ventana and hasattr(self.ventana, 'actualizar_boton_aire'): self.ventana.actualizar_boton_aire(estado)

# --- Fin del archivo app/logica/manejador_acciones.py ---