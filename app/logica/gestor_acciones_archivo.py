# -*- coding: utf-8 -*-
"""
Módulo que encapsula la lógica para las acciones relacionadas con
archivos y la lista de reproducción (añadir, quitar, guardar, cargar, etc.).
CORREGIDO: Indentación en accion_anadir_carpeta. Revisión manual completa.
"""

import typing
if typing.TYPE_CHECKING:
    from .manejador_acciones import ManejadorAcciones
    from ..gui.ventana_principal import VentanaPrincipal
    from ..gui.componentes.lista_reproduccion_widget import ListaReproduccionWidget

# Añadir QListWidgetItem a las importaciones
from PySide6.QtWidgets import QFileDialog, QMessageBox, QListWidgetItem
from PySide6.QtCore import QDir, Qt
from ..utilidades.archivos import buscar_archivos_audio_en_carpeta, obtener_directorio_padre
from ..utilidades.json_handler import guardar_json, cargar_json
import os
import random
import traceback

# Constantes específicas de este gestor
FILTRO_PLAYLIST = "Listas Radio Anarkadia (*.rka);;Todos (*)"
EXTENSION_PLAYLIST_POR_DEFECTO = ".rka"
FORMATOS_AUDIO_FILTRO = "Audio (*.mp3 *.ogg *.wav *.flac);;Todos (*)"

class GestorAccionesArchivo:
    """
    Gestiona las operaciones de archivo y lista (añadir, quitar, guardar, etc.).
    """
    def __init__(self,
                 ventana: 'VentanaPrincipal',
                 lista_widget: 'ListaReproduccionWidget',
                 manejador_principal: 'ManejadorAcciones'):
        self.ventana = ventana
        self.lista_widget = lista_widget
        self.manejador_principal = manejador_principal
        self.ultima_ruta_playlist: str = QDir.homePath()
        print("GestorAccionesArchivo inicializado.")

    # --- Métodos movidos y adaptados ---
    def anadir_archivo(self):
        print("DEBUG GestorArchivo: anadir_archivo...")
        dir_ini = getattr(self.ventana, 'ultima_ruta_usada', QDir.homePath())
        dir_ini = dir_ini if QDir(dir_ini).exists() else QDir.homePath()
        if not self.ventana or not self.lista_widget:
            print("ERROR GestorArchivo: Ventana/Lista no disp.")
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
                        print(f"DEBUG GestorArchivo: Actualizando ultima_ruta_usada a: {nuevo_dir}")
                        self.ventana.ultima_ruta_usada = nuevo_dir
                except IndexError:
                    print("WARN GestorArchivo: No dir de rutas[0].")
                except Exception as e_dir:
                    print(f"WARN GestorArchivo: Error dir: {e_dir}")
            else:
                print("GestorArchivo: No rutas seleccionadas.")
        except Exception as e:
            print(f"ERROR GestorArchivo.anadir_archivo: {e}")
            traceback.print_exc()
            self.manejador_principal._mostrar_error_ventana("Error Añadir Archivos", f"{e}")

    # --- accion_anadir_carpeta CORREGIDO ---
    def anadir_carpeta(self):
        """Abre diálogo para seleccionar carpeta y añade archivos recursivamente."""
        print("DEBUG GestorArchivo: anadir_carpeta...")
        dir_ini = getattr(self.ventana, 'ultima_ruta_usada', QDir.homePath())
        dir_ini = dir_ini if QDir(dir_ini).exists() else QDir.homePath()
        if not self.ventana or not self.lista_widget:
            print("ERROR GestorArchivo: Ventana/Lista no disp.")
            return
        try:
            ruta_c = QFileDialog.getExistingDirectory(self.ventana, "Seleccionar Carpeta con Audio", dir_ini, QFileDialog.Option.ShowDirsOnly | QFileDialog.Option.DontResolveSymlinks)
            if ruta_c:
                print(f"Carpeta: {ruta_c}")
                if hasattr(self.ventana, 'ultima_ruta_usada'):
                    self.ventana.ultima_ruta_usada = ruta_c
                print("Buscando archivos...")
                archivos = buscar_archivos_audio_en_carpeta(ruta_c, recursivo=True)
                if archivos is None:
                    self.manejador_principal._mostrar_error_ventana("Ruta Inválida", f"{ruta_c}")
                elif archivos:
                    print(f"{len(archivos)} encontrados. Añadiendo...")
                    # --- CORRECCIÓN DE INDENTACIÓN ---
                    for r in archivos:
                        self.lista_widget.agregar_archivo(r)
                    # --- FIN CORRECCIÓN ---
                else:
                    self.manejador_principal._mostrar_info_ventana("Carpeta Vacía", f"No audio en:\n{ruta_c}")
            else:
                print("GestorArchivo: No carpeta.")
        except Exception as e:
            print(f"ERROR GestorArchivo.anadir_carpeta: {e}")
            traceback.print_exc()
            self.manejador_principal._mostrar_error_ventana("Error Añadir Carpeta", f"{e}")
    # --- FIN accion_anadir_carpeta ---

    def quitar_seleccionado(self):
        print("DEBUG GestorArchivo: quitar_seleccionado...")
        ruta_sel = None
        indice_sel = -1
        item_sel = None
        if self.lista_widget:
            item_sel = self.lista_widget.currentItem()
            if item_sel:
                ruta_sel = item_sel.data(Qt.ItemDataRole.UserRole)
                indice_sel = self.lista_widget.row(item_sel)
        if self.manejador_principal.reproductor and self.manejador_principal.reproductor.archivo_cargado == ruta_sel and ruta_sel is not None:
            print("Quitando activa...")
            self.manejador_principal.accion_stop()
        if self.lista_widget and item_sel and indice_sel != -1:
            nombre = os.path.basename(ruta_sel) if ruta_sel else f"Índice {indice_sel}"
            print(f"Quitando '{nombre}'")
            self.lista_widget.quitar_seleccionado()
        elif not item_sel:
            print("GestorArchivo: No selección.")
        else:
            print("ERROR GestorArchivo: Índice inválido?")

    def limpiar_lista(self):
        print("DEBUG GestorArchivo: limpiar_lista...")
        if not self.lista_widget or self.lista_widget.count() == 0:
            print("GestorArchivo: Lista vacía.")
            return
        resp = QMessageBox.question(self.ventana, "Confirmar", "¿Limpiar lista?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
        if resp == QMessageBox.StandardButton.Yes:
            print("Limpiando...")
            self.manejador_principal.accion_stop()
            if self.lista_widget:
                self.lista_widget.clear()
        else:
            print("GestorArchivo: Limpieza cancelada.")

    def guardar_lista(self):
        print("DEBUG GestorArchivo: guardar_lista...")
        if not self.lista_widget or self.lista_widget.count() == 0:
            self.manejador_principal._mostrar_info_ventana("Guardar", "Lista vacía.")
            return
        dir_ini = self.ultima_ruta_playlist if QDir(self.ultima_ruta_playlist).exists() else QDir.homePath()
        ruta_f, _ = QFileDialog.getSaveFileName(self.ventana, "Guardar Lista", dir_ini, FILTRO_PLAYLIST)
        if ruta_f:
            if not ruta_f.lower().endswith(EXTENSION_PLAYLIST_POR_DEFECTO):
                ruta_f += EXTENSION_PLAYLIST_POR_DEFECTO
            print(f"Guardando en: {ruta_f}")
            rutas = self.lista_widget.obtener_todas_las_rutas()
            if guardar_json(ruta_f, rutas):
                self.manejador_principal._mostrar_info_ventana("Guardado", f"Lista:\n{ruta_f}")
                padre = obtener_directorio_padre(ruta_f)
                if padre:
                    self.ultima_ruta_playlist = padre
            else:
                self.manejador_principal._mostrar_error_ventana("Error Guardar", f"No guardar:\n{ruta_f}")
        else:
            print("GestorArchivo: Guardado cancelado.")

    def cargar_lista(self):
        print("DEBUG GestorArchivo: cargar_lista...")
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
                self.manejador_principal.accion_stop()
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
                self.manejador_principal._mostrar_info_ventana("Cargado", msg)
                padre = obtener_directorio_padre(ruta_f)
                if padre:
                    self.ultima_ruta_playlist = padre
            elif datos is not None:
                print("Error formato.")
                self.manejador_principal._mostrar_error_ventana("Error Formato", "No válido.")
            else:
                print("Error carga.")
                self.manejador_principal._mostrar_error_ventana("Error Carga", f"No leer:\n{ruta_f}")
        else:
            print("GestorArchivo: No archivo seleccionado.")

    def reordenar_lista_aleatorio(self):
        print("DEBUG GestorArchivo: reordenar_lista_aleatorio...")
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
                item = QListWidgetItem(d["icono"], d["texto"]) # Usa QListWidgetItem importado
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
            self.manejador_principal._mostrar_error_ventana("Error al Reordenar", f"{e}")
        finally:
            self.lista_widget.blockSignals(signals_blocked)
            print(f"Señales unblock: {not signals_blocked}")
            print("Reordenamiento finalizado.")
            self.manejador_principal._slot_seleccion_cambiada_ventana()

# --- Fin del archivo app/logica/gestor_acciones_archivo.py ---