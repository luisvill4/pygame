"""
App: crea todos los servicios del juego y corre el bucle principal.

Servicios (las escenas los usan con self.app.<servicio>):
    ventana, opciones, sonidos, records, entrada, fondo, efectos
    (pantalla y fondo se vuelven a crear si cambia el formato: ver aplicar_formato)

Bucle con "paso fijo" (fixed timestep):
- La LOGICA avanza siempre en pasos de 1/60 s: el juego va a la misma velocidad
  a cualquier FPS, y todos los numeros de config.py siguen valiendo.
- Se DIBUJA a la frecuencia elegida en Opciones (30, 60, 90, 120, 144 o sin limite).
  En cada cuadro se corren los pasos de logica que "tocan" segun el tiempo real que
  paso (a 30 FPS, dos por cuadro; a 144, a veces ninguno) y se dibuja interpolado.
"""
import os

import pygame

from juego import lienzo
from juego.config import CARPETA, MS_POR_FRAME, ATRASO_MAXIMO, NOMBRE_CONFIG, NOMBRE_RECORDS, FONDO
from juego.reloj import LimitadorFPS
from juego.ventana import Ventana
from juego.guardado import Opciones, TablaRecords
from juego.sonido import Sonidos
from juego.entrada import Entrada
from juego.fondo import Fondo
from juego.efectos import Efectos
from juego.partida import Partida
from juego.escenas.inicio import Inicio
from juego.escenas.listo import Listo


class App:
    def __init__(self, carpeta_datos=CARPETA, usar_mandos=True):
        # carpeta_datos: donde se guardan records.json y config.json (los tests usan otra)
        pygame.init()
        pygame.display.set_caption("Caza Monedas")

        self.ventana = Ventana()
        self.opciones = Opciones(os.path.join(carpeta_datos, NOMBRE_CONFIG))
        self.sonidos = Sonidos()
        self.sonidos.aplicar_volumen(self.opciones)
        self.records = TablaRecords(os.path.join(carpeta_datos, NOMBRE_RECORDS))
        self.entrada = Entrada(usar_mandos)
        self.efectos = Efectos()
        self.aplicar_formato()          # crea el lienzo (pantalla), el fondo y abre la ventana
        self.limitador = LimitadorFPS()
        self.acumulado = 0              # ms reales que todavia no se convirtieron en pasos de logica
        self.fraccion = 1               # cuanto del paso actual ya paso (0 a 1): para interpolar
        self.ejecutando = True
        self.escena = Inicio(self)

    def aplicar_formato(self):
        # 4:3 o 16:9: cambia el ancho del lienzo, arma un fondo nuevo para ese ancho
        # y abre la ventana con una resolucion de ese formato
        lienzo.cambiar(self.opciones.formato)
        self.pantalla = pygame.Surface(lienzo.tamano())     # lienzo donde se dibuja todo
        self.fondo = Fondo()
        nombres = self.ventana.nombres()
        if self.opciones.resolucion not in nombres:
            # La pantalla completa existe en los dos formatos; si no, la primera ventana
            self.opciones.resolucion = nombres[0]
        self.ventana.aplicar(self.opciones.resolucion)

    def ahora(self):
        # Reloj real en milisegundos (los tests lo reemplazan para no tener que esperar)
        return pygame.time.get_ticks()

    def cambiar_escena(self, escena):
        self.escena = escena

    def nueva_partida(self, dificultad=None):
        # Deja todo como al principio y muestra "READY?" (sin dificultad: la ultima elegida)
        dificultad = dificultad or self.opciones.dificultad
        self.efectos.reiniciar()
        self.fondo.ir_a_sector(None, FONDO, instantaneo=True)      # vuelve a los colores del primer sector
        partida = Partida(self.efectos, self.sonidos, self.entrada, self.records, self.opciones, dificultad)
        self.sonidos.reproducir("seleccion")
        self.sonidos.empezar_musica()
        self.cambiar_escena(Listo(self, partida))

    # ---------- El bucle ----------

    def _leer_entrada(self):
        # Devuelve False si se cerro la ventana
        self.entrada.procesar(pygame.event.get())
        if self.entrada.cerrar:
            self.escena.al_cerrar()
            self.ejecutando = False
            return False
        return True

    def _paso_de_logica(self):
        self.escena.actualizar(self.entrada)
        self.entrada.consumir()

    def _dibujar(self):
        self.escena.dibujar(self.pantalla)
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
