import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import tkinter.filedialog as fd
import random
import time
import os
import webbrowser
import logging

from helpers import format_time, calculate_total_duration
from tooltips import CreateToolTip
import playlist_manager as pm
from metadata import extract_metadata

logger = logging.getLogger(__name__)

class RadioGUI:
    def __init__(self, player, playlist):
        """
        Inicializa la interfaz.
        Se espera que 'playlist' tenga un atributo 'canciones' (lista de diccionarios)
        y que 'player' tenga métodos reproducir(), detener(), set_time(), get_time() y get_length().
        """
        self.ventana = ttk.Window(themename="flatly")
        self.player = player
        self.playlist = playlist

        # Configuración de la ventana (máx: 1360x768)
        screen_width = self.ventana.winfo_screenwidth()
        screen_height = self.ventana.winfo_screenheight()
        desired_width = min(int(screen_width * 2 / 3), 1360)
        desired_height = min(int(screen_height * 2 / 3), 768)
        self.ventana.geometry(f"{desired_width}x{desired_height}")
        self.ventana.title("Radio Anarkadia")

        # Fuentes:
        self.big_toolbar_font = ("Helvetica", 16, "bold")    # Para botones de toolbar y controles
        self.op_button_font = ("Helvetica", 16)              # Para botones de operación
        self.metadata_font = ("Helvetica", 12)               # Para metadata y listas
        self.default_listbox_font = ("Helvetica", 12)

        # Íconos (emoji) para la pestaña OPERACION:
        self.icon_wikipedia = "🅆"
        self.icon_letra = "🎵"
        self.icon_historia = "📜"
        self.icon_pregunta = "❓"

        # Estado:
        self.playback_started = False
        self.track_start_time = None
        self.current_metadata = {}
        self.drag_start_index = None

        # Etiqueta para la duración total (se mostrará en la parte superior de la pestaña OPERACION)
        self.duracion_total_label = ttk.Label(self.ventana, text="", font=("Helvetica", 12, "bold"))

        self.configurar_interfaz()
        self.update_progress()

    def configurar_interfaz(self):
        # Configuración del grid principal de la ventana
        self.ventana.columnconfigure(0, weight=1)
        self.ventana.columnconfigure(1, weight=1)
        self.ventana.columnconfigure(2, weight=1)
        self.ventana.rowconfigure(0, weight=1)

        # Secciones principales con estilo "card"
        self.frame_lista = ttk.Labelframe(self.ventana, text="LISTA", bootstyle="card", padding=10)
        self.frame_operacion = ttk.Labelframe(self.ventana, text="OPERACION", bootstyle="card", padding=10)
        self.frame_data = ttk.Labelframe(self.ventana, text="DATA", bootstyle="card", padding=10)

        self.frame_lista.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.frame_operacion.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.frame_data.grid(row=0, column=2, sticky="nsew", padx=10, pady=10)

        # Colocar la etiqueta de duración total en la pestaña OPERACION
        self.duracion_total_label.place(in_=self.frame_operacion, relx=0.5, y=5, anchor="n")
        self.duracion_total_label.lift()

        # Configurar la pestaña LISTA (4 filas)
        for i in range(4):
            self.frame_lista.rowconfigure(i, weight=1)
        self.frame_lista.columnconfigure(0, weight=1)

        # Row 0: Toolbar
        self.toolbar_frame = ttk.Frame(self.frame_lista, padding=5)
        self.toolbar_frame.grid(row=0, column=0, sticky="ew")
        # Botón para cargar un archivo; se utiliza lambda para invocar la función del módulo pm.
        self.btn_toolbar_cargar_archivo = ttk.Button(
            self.toolbar_frame,
            text="📄",
            command=lambda: pm.cargar_archivo(self.playlist, self.actualizar_lista),
            bootstyle="ghost pill"
        )
        self.btn_toolbar_cargar_archivo.pack(side="left", padx=2)
        CreateToolTip(self.btn_toolbar_cargar_archivo, "Cargar archivo")
        self.btn_toolbar_cargar_carpeta = ttk.Button(
            self.toolbar_frame,
            text="📂",
            command=lambda: pm.cargar_carpeta(self.playlist, self.actualizar_lista),
            bootstyle="ghost pill"
        )
        self.btn_toolbar_cargar_carpeta.pack(side="left", padx=2)
        CreateToolTip(self.btn_toolbar_cargar_carpeta, "Cargar carpeta")
        self.btn_toolbar_guardar_lista = ttk.Button(
            self.toolbar_frame,
            text="💾",
            command=lambda: pm.guardar_playlist(self.playlist),
            bootstyle="ghost pill"
        )
        self.btn_toolbar_guardar_lista.pack(side="left", padx=2)
        CreateToolTip(self.btn_toolbar_guardar_lista, "Guardar playlist")
        self.btn_toolbar_cargar_lista = ttk.Button(
            self.toolbar_frame,
            text="📋",
            command=lambda: pm.cargar_playlist(self.playlist, self.actualizar_lista),
            bootstyle="ghost pill"
        )
        self.btn_toolbar_cargar_lista.pack(side="left", padx=2)
        CreateToolTip(self.btn_toolbar_cargar_lista, "Cargar playlist")
        self.btn_toolbar_orden_aleatorio = ttk.Button(
            self.toolbar_frame,
            text="🔀",
            command=lambda: pm.orden_aleatorio(self.playlist, self.actualizar_lista),
            bootstyle="ghost pill"
        )
        self.btn_toolbar_orden_aleatorio.pack(side="left", padx=2)
        CreateToolTip(self.btn_toolbar_orden_aleatorio, "Orden aleatorio")
        self.btn_toolbar_eliminar = ttk.Button(
            self.toolbar_frame,
            text="❌",
            command=lambda: pm.eliminar_seleccionado(
                self.playlist,
                (self.playlist_box.curselection()[0] if self.playlist_box.curselection() else None),
                self.actualizar_lista
            ),
            bootstyle="ghost pill"
        )
        self.btn_toolbar_eliminar.pack(side="right", padx=2)
        CreateToolTip(self.btn_toolbar_eliminar, "Eliminar seleccionado")

        # Row 1: Listbox para mostrar la playlist
        self.lista_display_frame = ttk.Frame(self.frame_lista, padding=5)
        self.lista_display_frame.grid(row=1, column=0, sticky="nsew")
        self.playlist_box = tk.Listbox(self.lista_display_frame, font=self.default_listbox_font)
        self.playlist_box.pack(side="left", fill="both", expand=True)
        self.scrollbar = ttk.Scrollbar(self.lista_display_frame)
        self.scrollbar.pack(side="right", fill="y")
        self.playlist_box.config(yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.playlist_box.yview)
        self.playlist_box.bind("<ButtonPress-1>", self.on_start_drag)
        self.playlist_box.bind("<B1-Motion>", self.on_drag_motion)
        self.playlist_box.bind("<ButtonRelease-1>", self.on_drop)
        try:
            if self.ventana.tk.call('info', 'commands', 'tkdnd::drop_target_register'):
                self.ventana.tk.call('tkdnd::drop_target_register', self.playlist_box, '*')
                self.playlist_box.bind('<<Drop>>', self.on_file_drop)
        except Exception:
            logger.exception("Error al configurar drag and drop")

        # Row 2: Barra de progreso y label
        self.progress_frame = ttk.Frame(self.frame_lista, padding=5)
        self.progress_frame.grid(row=2, column=0, sticky="ew")
        self.progress_scale = ttk.Scale(self.progress_frame, from_=0, to=100, orient="horizontal", length=300)
        self.progress_scale.pack(fill="x", expand=True)
        self.progress_scale.bind("<ButtonRelease-1>", self.on_seek_release)
        self.progress_label = ttk.Label(self.progress_frame, text="00:00 / 00:00", font=self.metadata_font)
        self.progress_label.pack()

        # Row 3: Controles de reproducción
        self.controls_frame = ttk.Frame(self.frame_lista, padding=5)
        self.controls_frame.grid(row=3, column=0, sticky="ew")
        for i in range(3):
            self.controls_frame.columnconfigure(i, weight=1)
        self.btn_reproducir = ttk.Button(
            self.controls_frame,
            text="\u25B6",
            command=self.reproducir,
            bootstyle="success pill"
        )
        self.btn_reproducir.grid(row=0, column=0, padx=3)
        CreateToolTip(self.btn_reproducir, "Reproducir")
        self.btn_stop = ttk.Button(
            self.controls_frame,
            text="\u23F9",
            command=self.detener,
            bootstyle="danger pill"
        )
        self.btn_stop.grid(row=0, column=1, padx=3)
        CreateToolTip(self.btn_stop, "Detener")
        self.btn_siguiente = ttk.Button(
            self.controls_frame,
            text="\u23ED",
            command=self.siguiente,
            bootstyle="info pill"
        )
        self.btn_siguiente.grid(row=0, column=2, padx=3)
        CreateToolTip(self.btn_siguiente, "Siguiente canción")

        # Pestaña OPERACION
        self.op_meta_frame = ttk.Frame(self.frame_operacion, padding=5)
        self.op_meta_frame.pack(fill="both", expand=True)
        self.metadata_label = ttk.Label(self.op_meta_frame, text="Información del track", font=self.metadata_font, anchor="w")
        self.metadata_label.pack(fill="x")
        self.op_buttons_frame = ttk.Frame(self.op_meta_frame, padding=5)
        self.op_buttons_frame.pack(fill="x", pady=5)
        self.btn_wikipedia = ttk.Button(
            self.op_buttons_frame,
            command=self.abrir_wikipedia,
            text=self.icon_wikipedia,
            bootstyle="primary pill"
        )
        self.btn_wikipedia.pack(side="left", padx=5)
        CreateToolTip(self.btn_wikipedia, "Wikipedia")
        self.btn_letra = ttk.Button(
            self.op_buttons_frame,
            command=self.abrir_letra,
            text=self.icon_letra,
            bootstyle="warning pill"
        )
        self.btn_letra.pack(side="left", padx=5)
        CreateToolTip(self.btn_letra, "Letra de la canción")
        self.btn_historia = ttk.Button(
            self.op_buttons_frame,
            command=self.abrir_historia,
            text=self.icon_historia,
            bootstyle="secondary pill"
        )
        self.btn_historia.pack(side="left", padx=5)
        CreateToolTip(self.btn_historia, "Historia")
        self.btn_pregunta = ttk.Button(
            self.op_buttons_frame,
            command=self.abrir_pregunta,
            text=self.icon_pregunta,
            bootstyle="danger pill"
        )
        self.btn_pregunta.pack(side="left", padx=5)
        CreateToolTip(self.btn_pregunta, "Ayuda")

        # Pestaña DATA (opcional)
        self.label_data = ttk.Label(self.frame_data, text="(Opcional)", font=self.metadata_font)
        self.label_data.pack(pady=10)

    def actualizar_duracion_total(self):
        total = calculate_total_duration(self.playlist.canciones)
        self.duracion_total_label.config(text=f"Duración Total: {format_time(total)}")
        self.duracion_total_label.lift()

    def actualizar_lista(self):
        self.playlist_box.delete(0, tk.END)
        if not self.playlist.canciones:
            return
        current_index = self.playlist.actual_index
        rotated = self.playlist.canciones[current_index:] + self.playlist.canciones[:current_index]
        for idx, cancion in enumerate(rotated):
            titulo = cancion.get("titulo", "Sin título")
            display_text = f"► {titulo}" if idx == 0 else f"{idx+1}. {titulo}"
            self.playlist_box.insert(tk.END, display_text)
        self.actualizar_duracion_total()

    def actualizar_metadata(self):
        song = self.playlist.obtener_cancion_actual()
        if not song:
            self.metadata_label.config(text="Sin metadata")
            self.current_metadata = {}
            return
        ruta = song.get("ruta", "")
        self.current_metadata = extract_metadata(ruta)
        self.metadata_label.config(
            text=f"Título: {self.current_metadata.get('title')}\n"
                 f"Artista: {self.current_metadata.get('artist')}\n"
                 f"Álbum: {self.current_metadata.get('album')}"
        )

    def reproducir(self):
        if len(self.playlist.canciones) == 0:
            logger.warning("No hay canción para reproducir.")
            return
        self.playlist.actual_index = 0
        self.playback_started = True
        self.track_start_time = time.time()
        song = self.playlist.obtener_cancion_actual()
        self.player.reproducir(song)
        duration = song.get("duracion", self.player.get_length()) if song else self.player.get_length()
        if duration <= 0:
            duration = 100
        self.progress_scale.config(to=duration)
        self.progress_scale.set(0)
        self.actualizar_lista()
        self.actualizar_metadata()

    def detener(self):
        self.player.detener()
        self.playback_started = False

    def siguiente(self):
        if len(self.playlist.canciones) == 0:
            return
        self.playlist.canciones = self.playlist.canciones[1:] + self.playlist.canciones[:1]
        self.playlist.actual_index = 0
        self.track_start_time = time.time()
        song = self.playlist.obtener_cancion_actual()
        self.player.reproducir(song)
        duration = song.get("duracion", self.player.get_length()) if song else self.player.get_length()
        if duration <= 0:
            duration = 100
        self.progress_scale.config(to=duration)
        self.progress_scale.set(0)
        self.actualizar_lista()
        self.actualizar_metadata()

    def eliminar_seleccionado(self):
        selected = self.playlist_box.curselection()
        index = selected[0] if selected else None
        pm.eliminar_seleccionado(self.playlist, index, self.actualizar_lista)

    def on_start_drag(self, event):
        self.drag_start_index = self.playlist_box.nearest(event.y)

    def on_drag_motion(self, event):
        pass

    def on_drop(self, event):
        drop_index = self.playlist_box.nearest(event.y)
        if drop_index == 0 and len(self.playlist.canciones) > 0:
            drop_index = 1
        if drop_index is None or self.drag_start_index is None:
            return
        if drop_index != self.drag_start_index:
            songs = self.playlist.canciones
            item = songs.pop(self.drag_start_index)
            if drop_index == 0 and len(songs) > 0:
                drop_index = 1
            songs.insert(drop_index, item)
            self.playlist.canciones = songs
            self.actualizar_lista()

    def on_file_drop(self, event):
        files = self.parse_drop_files(event.data)
        for file in files:
            if file.lower().endswith((".mp3", ".wav", ".ogg")):
                title = os.path.splitext(os.path.basename(file))[0]
                if len(self.playlist.canciones) > 0:
                    self.playlist.canciones.insert(1, {"ruta": file, "titulo": title})
                else:
                    self.playlist.canciones.append({"ruta": file, "titulo": title})
        self.actualizar_lista()

    def parse_drop_files(self, data):
        files = []
        if data:
            parts = data.split()
            for part in parts:
                if part.startswith("{") and part.endswith("}"):
                    files.append(part[1:-1])
                else:
                    files.append(part)
        return files

    def on_seek_release(self, event):
        if not self.playback_started or self.track_start_time is None:
            return
        new_pos = float(self.progress_scale.get())
        try:
            self.player.set_time(new_pos)
            self.track_start_time = time.time() - new_pos
        except Exception as e:
            logger.error("Error al buscar nueva posición: %s", e)

    def update_progress(self):
        if self.playback_started:
            pos_sec = self.player.get_time()
            total = self.player.get_length()
            self.progress_scale.set(pos_sec)
            self.progress_label.config(text=f"{format_time(pos_sec)} / {format_time(total)}")
        self.ventana.after(500, self.update_progress)

    def check_music_end(self):
        if self.playback_started:
            current_time = self.player.get_time()
            total_duration = self.player.get_length()
            if total_duration > 0 and current_time >= (total_duration - 1):
                logger.info("Tema finalizado, pasando al siguiente.")
                self.siguiente()
        self.ventana.after(500, self.check_music_end)

    def abrir_wikipedia(self):
        if self.current_metadata.get("title"):
            query = self.current_metadata["title"]
            url = "https://en.wikipedia.org/wiki/" + query.replace(" ", "_")
            webbrowser.open(url)
        else:
            webbrowser.open("https://en.wikipedia.org")

    def abrir_letra(self):
        if self.current_metadata.get("title"):
            query = self.current_metadata["title"]
            url = "https://www.lyrics.com/serp.php?st=" + query.replace(" ", "+")
            webbrowser.open(url)
        else:
            webbrowser.open("https://www.lyrics.com")

    def abrir_historia(self):
        if self.current_metadata.get("title"):
            query = self.current_metadata["title"]
            url = "https://www.allmusic.com/search/all/" + query.replace(" ", "+")
            webbrowser.open(url)
        else:
            webbrowser.open("https://www.allmusic.com")

    def abrir_pregunta(self):
        webbrowser.open("https://www.google.com/search?q=help")

    def iniciar(self):
        self.check_music_end()
        self.update_progress()
        self.ventana.mainloop()
