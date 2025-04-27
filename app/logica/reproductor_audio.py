# -*- coding: utf-8 -*-
"""
Módulo reproductor.
CORREGIDO: Lógica de verificar_fin_cancion más estricta.
"""

import pygame
import os
import time
try:
    from app.utilidades.audio import obtener_duracion_ms
except ImportError:
    print("ERROR: No importar 'obtener_duracion_ms'.")
    def obtener_duracion_ms(ruta_archivo: str) -> int: return 0

FIN_CANCION_EVENTO = pygame.USEREVENT + 1

class ReproductorAudioError(Exception): pass

class ReproductorAudio:
    def __init__(self, volumen_inicial=1.0): # Default a 1.0 por botón AIRE
        self._inicializado = False; self._reproduciendo = False; self._pausado = False
        self._archivo_cargado = None; self._duracion_ms = 0
        self._tiempo_inicio_segmento_ms = 0; self._posicion_inicio_segmento_ms = 0
        self._volumen = max(0.0, min(1.0, volumen_inicial))
        try:
            if not pygame.get_init(): pygame.mixer.pre_init(44100, -16, 2, 2048); pygame.init(); print("Pygame inicializado.")
            else: print("Pygame ya inicializado.")
            if not pygame.mixer.get_init(): pygame.mixer.init(); print("Mixer inicializado.")
            else: print("Mixer ya inicializado.")
            pygame.mixer.music.set_volume(self._volumen)
            pygame.mixer.music.set_endevent(FIN_CANCION_EVENTO)
            self._inicializado = True
            print(f"Reproductor inicializado OK. Volumen: {self._volumen:.2f}")
        except pygame.error as e: self._inicializado = False; raise ReproductorAudioError(f"Fallo Pygame/Mixer: {e}")
        except Exception as e_gen: self._inicializado = False; raise ReproductorAudioError(f"Error inesperado audio: {e_gen}")

    @property
    def archivo_cargado(self): return self._archivo_cargado
    @property
    def duracion_ms(self) -> int: return self._duracion_ms
    @property
    def volumen(self) -> float: return self._volumen
    @volumen.setter
    def volumen(self, valor: float):
        if not self._inicializado: return
        self._volumen = max(0.0, min(1.0, valor))
        try:
            if pygame.mixer.get_init(): pygame.mixer.music.set_volume(self._volumen)
        except pygame.error as e: print(f"Err set vol: {e}")

    def cargar_archivo(self, ruta_archivo: str):
        if not self._inicializado: print("ERROR Carga: No inicializado."); return False
        if not os.path.exists(ruta_archivo): print(f"Err Carga: No existe: {os.path.basename(ruta_archivo)}"); return False
        if not pygame.mixer.get_init(): print("ERROR Carga: Mixer no inicializado."); return False

        try:
            if pygame.mixer.music.get_busy() or self._pausado:
                print("Carga: Deteniendo/descargando música anterior...")
                pygame.mixer.music.stop()
                pygame.mixer.music.unload()
                self._resetear_estado_interno()
            elif self._archivo_cargado:
                 pygame.mixer.music.unload()
                 self._resetear_estado_interno()

            print(f"Carga: Intentando cargar '{os.path.basename(ruta_archivo)}'...")
            pygame.mixer.music.load(ruta_archivo)
            self._archivo_cargado = ruta_archivo
            print(f"Carga: Pygame cargó OK.")
            self._duracion_ms = obtener_duracion_ms(ruta_archivo)
            if self._duracion_ms == 0: print(f"WARN Carga: Duración 0 para '{os.path.basename(ruta_archivo)}'")
            else: print(f"Carga: Duración: {self._duracion_ms} ms")
            return True
        except pygame.error as e: print(f"Error Pygame al cargar: {e}"); self._resetear_estado_interno(); return False
        except Exception as e: print(f"Error Gral al cargar: {e}"); self._resetear_estado_interno(); return False

    def reproducir(self):
        if not self._inicializado or not self._archivo_cargado: print("ERROR Reprod: Precondiciones fallan."); return False
        if not pygame.mixer.get_init(): print("ERROR Reprod: Mixer no inicializado."); return False
        try:
            t_actual = pygame.time.get_ticks()
            if self._pausado: print("Reprod: Reanudando..."); pygame.mixer.music.unpause(); self._tiempo_inicio_segmento_ms = t_actual
            elif not pygame.mixer.music.get_busy(): print("Reprod: Iniciando..."); pygame.mixer.music.play(); self._tiempo_inicio_segmento_ms = t_actual; self._posicion_inicio_segmento_ms = 0
            else: print("Reprod: Ya estaba reproduciendo."); self._reproduciendo=True; self._pausado=False; return True # Ya sonaba
            self._reproduciendo=True; self._pausado=False; return True
        except pygame.error as e: print(f"Err reprod: {e}"); return False

    def pausar(self):
        if not self._inicializado or not self.esta_reproduciendo(): print("ERROR Pausa: Precondiciones fallan."); return False
        if not pygame.mixer.get_init(): print("ERROR Pausa: Mixer no inicializado."); return False
        try:
            self._posicion_inicio_segmento_ms = self.obtener_posicion_ms()
            pygame.mixer.music.pause(); self._pausado=True; self._reproduciendo=False
            print(f"Pausa OK en {self._posicion_inicio_segmento_ms/1000:.2f}s."); return True
        except pygame.error as e: print(f"Err pausa: {e}"); return False

    def detener(self):
        if not self._inicializado or not pygame.mixer.get_init(): print("WARN Detener: No inicializado o mixer quit."); return False
        if not pygame.mixer.music.get_busy() and not self._pausado: return True # Ya detenido
        try:
            print("Detener: Llamando stop()..."); pygame.mixer.music.stop(); # pygame.mixer.music.unload() # Descargar?
            self._resetear_estado_interno(); print("Detener: OK."); return True
        except pygame.error as e: print(f"Err pygame al detener: {e}"); return False
        except Exception as e_gen: print(f"Err Gral al detener: {e_gen}"); return False

    def obtener_posicion_ms(self) -> int:
        if not self._inicializado or not pygame.mixer.get_init(): return 0
        if self._pausado: return self._posicion_inicio_segmento_ms
        elif self.esta_reproduciendo():
             t_actual = pygame.time.get_ticks(); t_transcurrido = t_actual - self._tiempo_inicio_segmento_ms
             pos_calculada = self._posicion_inicio_segmento_ms + t_transcurrido
             try:
                 pos_pygame_ms = pygame.mixer.music.get_pos()
                 if pos_pygame_ms != -1: pos_calculada = self._posicion_inicio_segmento_ms + pos_pygame_ms
             except pygame.error: pass
             pos_calculada = max(0, pos_calculada)
             if self._duracion_ms > 0: return min(pos_calculada, self._duracion_ms)
             else: return pos_calculada
        else: return 0

    def establecer_posicion_segundos(self, segundos: float):
        if not self._inicializado or not self._archivo_cargado or not pygame.mixer.get_init(): return False
        segundos = max(0, segundos); nueva_pos_ms = int(segundos * 1000)
        if self._duracion_ms > 0 and nueva_pos_ms >= self._duracion_ms: nueva_pos_ms = max(0, self._duracion_ms - 500); segundos = nueva_pos_ms / 1000.0
        estaba_reproduciendo = self.esta_reproduciendo(); estaba_pausado = self.esta_pausado()
        try:
            pygame.mixer.music.stop(); pygame.mixer.music.play(start=segundos)
            t_actual = pygame.time.get_ticks(); self._tiempo_inicio_segmento_ms = t_actual; self._posicion_inicio_segmento_ms = nueva_pos_ms
            print(f"Seek OK a {segundos:.2f}s."); self._reproduciendo=True; self._pausado=False
            if estaba_pausado and not estaba_reproduciendo: print("Seek: Volviendo a pausar."); pygame.mixer.music.pause(); self._pausado = True; self._reproduciendo = False
            return True
        except pygame.error as e: print(f"Err pygame set pos: {e}"); self._resetear_estado_interno(); return False
        except Exception as e_gen: print(f"Err gral set pos: {e_gen}"); self._resetear_estado_interno(); return False

    def esta_reproduciendo(self) -> bool:
        try: return self._inicializado and pygame.mixer.get_init() and pygame.mixer.music.get_busy() and not self._pausado
        except pygame.error: return False

    def esta_pausado(self) -> bool:
        return self._inicializado and self._pausado

    # --- verificar_fin_cancion REVISADO ---
    def verificar_fin_cancion(self) -> bool:
        """ Verifica si se recibió el evento de fin de canción Y si la música ya no está ocupada. """
        if not self._inicializado: return False

        evento_fin_recibido = False
        try:
            # Solo procesar eventos si el sistema de eventos está activo
            if pygame.display.get_init(): # Usar display como proxy fiable
                 for ev in pygame.event.get():
                     if ev.type == FIN_CANCION_EVENTO:
                         print("DEBUG Reprod: Evento FIN_CANCION_EVENTO recibido.")
                         evento_fin_recibido = True
                         # Marcar estado interno inmediatamente al recibir el evento
                         self._reproduciendo = False
                         self._pausado = False
                         break # No necesitamos procesar más eventos
            # else: print("DEBUG Reprod: Sistema eventos Pygame no activo.") # Verboso

        except pygame.error as e:
             print(f"Error Pygame en verificar_fin_cancion (get): {e}")
             # Si falla aquí, es probable que se esté cerrando, no asumimos fin prematuro.
             return False # No podemos estar seguros, mejor no indicar fin.

        # Devolver True SOLO si recibimos el evento Y además get_busy() confirma que no suena
        # Esto evita falsos positivos si el evento llega un instante antes.
        if evento_fin_recibido:
             try:
                 musica_ocupada = pygame.mixer.music.get_busy()
                 print(f"DEBUG Reprod: Evento Fin Recibido. get_busy() = {musica_ocupada}")
                 if not musica_ocupada:
                      print("DEBUG Reprod: Confirmado fin de canción (Evento + !get_busy()).")
                      return True
                 else:
                      # Evento recibido pero aún ocupado, esperar al siguiente ciclo del timer
                      return False
             except pygame.error as e:
                 print(f"Error Pygame en verificar_fin_cancion (get_busy): {e}")
                 return False # Error al verificar estado, no confirmar fin.

        # Si no se recibió el evento, no es el fin
        return False
    # --- FIN verificar_fin_cancion ---

    def limpiar(self):
        if self._inicializado:
            print("Limpiando ReproductorAudio...");
            try:
                if pygame.mixer.get_init() and pygame.mixer.music.get_busy(): print("  Deteniendo música..."); pygame.mixer.music.stop(); pygame.mixer.music.unload()
                if pygame.mixer.get_init(): print("  Cerrando Mixer..."); pygame.mixer.quit()
                if pygame.get_init(): print("  Cerrando Pygame..."); pygame.quit()
                print("Audio liberado OK.")
            except Exception as e: print(f"ERROR limpieza reproductor: {e}"); import traceback; traceback.print_exc()
            finally: self._inicializado = False; self._resetear_estado_interno()
        else: print("Limpiar: Reproductor no inicializado.")

    def _resetear_estado_interno(self):
        self._reproduciendo=False; self._pausado=False
        self._tiempo_inicio_segmento_ms=0; self._posicion_inicio_segmento_ms=0
        # Resetear archivo y duración solo cuando se descarga/limpia, no en stop simple
        # self._archivo_cargado=None; self._duracion_ms=0