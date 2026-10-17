"""
App: crea todos los servicios del juego y corre el bucle principal.

Servicios (las escenas los usan con self.app.<servicio>):
    ventana, opciones, sonidos, records, progreso, entrada, fondo, efectos
    y pantalla (el lienzo de ANCHO x ALTO donde se dibuja todo)

Bucle con "paso fijo" (fixed timestep):
- La LOGICA avanza siempre en pasos de 1/60 s: el juego va a la misma velocidad
  a cualquier FPS, y todos los numeros de config.py siguen valiendo.
- Se DIBUJA a la frecuencia elegida en Opciones (30, 60, 90, 120, 144 o sin limite).
  En cada cuadro se corren los pasos de logica que "tocan" segun el tiempo real que
  paso (a 30 FPS, dos por cuadro; a 144, a veces ninguno) y se dibuja interpolado.
"""
import os

import pygame

from juego import nave, dibujo, recursos, accesibilidad
from juego.config import (CARPETA, ANCHO, ALTO, CENTRO_X, MS_POR_FRAME, ATRASO_MAXIMO, NOMBRE_CONFIG,
                          NOMBRE_RECORDS, NOMBRE_PROGRESO, SECTORES, AMARILLO, BLANCO)
from juego.reloj import LimitadorFPS
from juego.ventana import Ventana
from juego.guardado import Opciones, TablaRecords, Progreso
from juego.sonido import Sonidos
from juego.entrada import Entrada, SILENCIO, PANTALLA_COMPLETA
from juego.fondo import Fondo
from juego.efectos import Efectos
from juego.transicion import Transicion
from juego.partida import Partida
from juego.arcade.modo import ModoArcade
from juego.escenas.inicio import Inicio
from juego.escenas.presentacion import Presentacion
from juego.escenas.listo import Listo


class App:
    def __init__(self, carpeta_datos=CARPETA, usar_mandos=True, presentacion=True):
        # carpeta_datos: donde se guardan records.json y config.json (los tests usan otra)
        # Audio en estereo (para el paneo) y con un buffer chico: el sonido sale ~12 ms
        # despues del evento (con el de fabrica, mas grande, se nota el retraso)
        pygame.mixer.pre_init(44100, -16, 2, 512)
        pygame.init()
        pygame.display.set_caption("Caza Monedas")

        self.ventana = Ventana()
        self.opciones = Opciones(os.path.join(carpeta_datos, NOMBRE_CONFIG))
        accesibilidad.opciones = self.opciones     # los efectos leen de ahi el temblor, destellos y CRT
        self.sonidos = Sonidos()
        self.sonidos.reloj = lambda: self.ahora()      # (enfriamientos y ducking, con el reloj real)
        self.sonidos.aplicar_volumen(self.opciones)
        self.records = TablaRecords(os.path.join(carpeta_datos, NOMBRE_RECORDS))
        self.progreso = Progreso(os.path.join(carpeta_datos, NOMBRE_PROGRESO))
        nave.cambiar_color(self.progreso.color_nave())
        self.entrada = Entrada(usar_mandos)
        # La vibracion lee su intensidad de las opciones y usa el reloj real de la App
        self.entrada.haptica.opciones = self.opciones
        self.entrada.haptica.reloj = lambda: self.ahora()
        self.efectos = Efectos()
        self.pantalla = pygame.Surface((ANCHO, ALTO))     # lienzo donde se dibuja todo
        self.fondo = Fondo()
        self.abrir_ventana()
        self.limitador = LimitadorFPS()
        self.acumulado = 0              # ms reales que todavia no se convirtieron en pasos de logica
        self.fraccion = 1               # cuanto del paso actual ya paso (0 a 1): para interpolar
        self.ejecutando = True
        self.aviso = None               # (texto, hasta cuando): aviso chico de los atajos M y F11
        self.ventana_antes = None       # la resolucion en ventana antes de F11 (para volver)
        self.transicion = None          # el barrido de rombos al cambiar de pantalla (o None)
        # Al abrir: la advertencia, "HECHO CON PYGAME" y el titulo (el acorde del logo suena
        # ahi). Sin presentacion (los tests), directo al Inicio
        self.escena = Presentacion(self) if presentacion else Inicio(self)

    def abrir_ventana(self):
        # Abre la ventana con la resolucion guardada. Si ya no existe (un config.json viejo)
        # o no entra en el monitor, usa la primera
        nombres = self.ventana.nombres()
        if self.opciones.resolucion not in nombres:
            self.opciones.resolucion = nombres[0]
        self.ventana.aplicar(self.opciones.resolucion)

    def ahora(self):
        # Reloj real en milisegundos (los tests lo reemplazan para no tener que esperar)
        return pygame.time.get_ticks()

    def cambiar_escena(self, escena, transicion=True):
        # La escena nueva empieza ya; la transicion es solo dibujo (tapa la imagen vieja y
        # destapa la nueva). Sin transicion: lo que tiene que ser instantaneo (pausar,
        # seguir jugando, READY -> juego, la explosion)
        if transicion:
            self.transicion = Transicion(self.pantalla.copy(), self.ahora())
            self.sonidos.reproducir("ui_transicion")
        self.escena = escena

    def nueva_partida(self, dificultad=None, modo=None):
        # Deja todo como al principio y muestra "READY?" (sin dificultad: la ultima elegida).
        # 'modo': ModoArcade (por defecto) o ModoHistoria(numero de mision) (ver modos.py)
        dificultad = dificultad or self.opciones.dificultad
        modo = modo or ModoArcade()
        self.efectos.reiniciar()
        self.fondo.ir_a_sector(SECTORES[modo.primer_sector() - 1], instantaneo=True)     # donde empieza
        self.fondo.saltar_al_hiperespacio()                         # y llega volando
        partida = Partida(self.efectos, self.sonidos, self.entrada, self.records, self.opciones, dificultad,
                          self.progreso, modo=modo)
        self.sonidos.reproducir("ui_empezar")
        self.sonidos.reproducir("hiperespacio")         # (el fondo llega volando)
        self.cambiar_escena(Listo(self, partida))      # Listo pide la musica del juego (en el GO)

    # ---------- El bucle ----------

    def _leer_entrada(self):
        # Devuelve False si se cerro la ventana
        self.entrada.procesar(pygame.event.get())
        if self.entrada.cerrar:
            self.escena.al_cerrar()
            self.entrada.haptica.parar()
            self.ejecutando = False
            return False
        return True

    def _paso_de_logica(self):
        self._atajos()
        if self.escena.musica is not None:
            self.sonidos.tocar_musica(self.escena.musica)      # si ya suena, no hace nada
        if self.escena.ambiente is not None:
            self.sonidos.tocar_ambiente(self.escena.ambiente)  # (igual que la musica)
        if self.entrada.mando_desconectado:
            self.sonidos.reproducir("mando_fuera")
        elif self.entrada.mando_conectado and self.ahora() > 2000:     # (no los que ya estaban al abrir)
            self.sonidos.reproducir("mando_dentro")
        self.escena.actualizar(self.entrada)
        self.entrada.haptica.actualizar()       # los patrones de vibracion siguen con su paso
        self.sonidos.actualizar()               # la musica vuelve de a poco despues de un momento
        self.entrada.consumir()

    def _atajos(self):
        # Teclas que funcionan en cualquier pantalla
        opciones = self.opciones
        if self.entrada.pulso(SILENCIO):
            # M: calla todo o lo vuelve a encender (los volumenes de Opciones no se tocan)
            opciones.silencio = not opciones.silencio
            self.sonidos.aplicar_volumen(opciones)
            opciones.guardar()
            self.avisar("SONIDO: " + ("NO" if opciones.silencio else "SI"))
        if self.entrada.pulso(PANTALLA_COMPLETA):
            # F11: pantalla completa, o vuelve a la ventana de antes
            if opciones.resolucion == "COMPLETA":
                nombres = self.ventana.nombres()
                opciones.resolucion = self.ventana_antes if self.ventana_antes in nombres else nombres[0]
            else:
                self.ventana_antes = opciones.resolucion
                opciones.resolucion = "COMPLETA"
            self.ventana.aplicar(opciones.resolucion)
            opciones.guardar()
            self.avisar("PANTALLA: " + opciones.resolucion)

    def avisar(self, mensaje):
        self.aviso = (mensaje, self.ahora() + 1500)

    def _dibujar_aviso(self):
        # El aviso de los atajos, abajo al centro, encima de todo
        if self.aviso is None or self.ahora() > self.aviso[1]:
            return
        x = CENTRO_X
        ancho = recursos.fuente(dibujo.CHICA).size(self.aviso[0])[0] + 40
        dibujo.marco(self.pantalla, pygame.Rect(x - ancho // 2, 480, ancho, 40), AMARILLO)
        dibujo.texto(self.pantalla, self.aviso[0], dibujo.CHICA, BLANCO, x, 500)

    def _dibujar(self):
        self.escena.dibujar(self.pantalla)
        if self.transicion is not None and not self.transicion.dibujar(self.pantalla, self.ahora()):
            self.transicion = None
        self._dibujar_aviso()
        self.ventana.mostrar(self.pantalla)

    def paso(self):
        # Exactamente un paso de logica y un cuadro (lo usan los tests)
        if not self._leer_entrada():
            return
        self._paso_de_logica()
        self.fraccion = 1
        self._dibujar()

    def cuadro(self, ms_reales):
        # Un cuadro de la ventana, despues de que pasaron 'ms_reales' milisegundos:
        # corre los pasos de logica que tocan y dibuja interpolado
        self.acumulado += min(ms_reales, ATRASO_MAXIMO)    # si la ventana se trabo, no intenta alcanzar
        if not self._leer_entrada():
            return
        while self.acumulado >= MS_POR_FRAME:
            self._paso_de_logica()
            self.acumulado -= MS_POR_FRAME
        self.fraccion = self.acumulado / MS_POR_FRAME
        self._dibujar()

    def ejecutar(self):
        while self.ejecutando:
            # Espera lo necesario para no pasar los FPS elegidos (0 = sin limite)
            # y devuelve cuantos ms pasaron desde el cuadro anterior
            ms_reales = self.limitador.esperar(self.opciones.fps)
            self.cuadro(ms_reales)
        pygame.quit()
