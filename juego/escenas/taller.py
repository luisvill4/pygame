"""
Taller: elegir UNA mejora entre tres cartas (ver mejoras.py).

Se abre desde Juego cuando el director deja ofertas (en el nivel MEJORA_PRIMER_NIVEL).
El juego queda quieto detras (pixelado y oscurecido). Las cartas (interfaz.carta) caen de a una;
IZQ/DER elige y ENTER la toma. Los primeros instantes no se aceptan teclas, asi no
se elige sin querer una carta que todavia no se leyo.
"""
import pygame

from juego import interfaz
from juego.dibujo import texto, CHICA, GRANDE
from juego.config import CENTRO_X, AMARILLO, CIAN, MAGENTA, TEXTO_SUAVE
from juego.entrada import ACEPTAR, IZQUIERDA, DERECHA
from juego.escenas.base import Escena

PASOS_SIN_ELEGIR = 30       # pasos (medio segundo) en que se ignoran las teclas
PASOS_ENTRE_CARTAS = 5      # cada carta cae este numero de pasos despues de la anterior
ANCHO_CARTA, ALTO_CARTA = 240, 316
SEPARACION = 36             # entre carta y carta
ARRIBA_CARTA = 182


class Taller(Escena):
    def __init__(self, app, escena_juego, captura):
        super().__init__(app)
        self.escena_juego = escena_juego
        self.partida = escena_juego.partida
        self.captura = captura
        self.fondo = interfaz.pixelado(captura, oscuridad=180)     # el juego quieto, de fondo
        self.ofertas = list(self.partida.director.ofertas)
        self.elegida = len(self.ofertas) // 2       # empieza en la del medio
        self.pasos = 0                              # pasos desde que se abrio (animacion)
        app.sonidos.reproducir("taller")

    def actualizar(self, entrada):
        self.pasos += 1
        # Cada carta que cae suena (una nota mas arriba cada una; la RARA brilla)
        for i, mejora in enumerate(self.ofertas):
            if self.pasos == i * PASOS_ENTRE_CARTAS + 1:
                self.app.sonidos.reproducir("carta_%d" % min(i + 1, 6))
                if mejora.peso < 1:
                    self.app.sonidos.reproducir_luego("carta_rara", 80)
        if self.pasos < PASOS_SIN_ELEGIR:
            return
        if entrada.pulso(IZQUIERDA):
            self.elegida = (self.elegida - 1) % len(self.ofertas)
            self.app.sonidos.reproducir("ui_mover")
        elif entrada.pulso(DERECHA):
            self.elegida = (self.elegida + 1) % len(self.ofertas)
            self.app.sonidos.reproducir("ui_mover")
        elif entrada.pulso(ACEPTAR):
            self.partida.elegir_mejora(self.ofertas[self.elegida].tipo)
            self.app.cambiar_escena(self.escena_juego)

    # ---------- Dibujo ----------

    def dibujar(self, pantalla):
        pantalla.blit(self.fondo, (0, 0))
        texto(pantalla, "TALLER", CHICA, CIAN, CENTRO_X, 34)
        interfaz.titulo(pantalla, "ELIGE UNA MEJORA", CENTRO_X, 78, AMARILLO, MAGENTA, alinear="centro",
                        tamano=GRANDE)
        texto(pantalla, "ES GRATIS Y DURA TODA LA PARTIDA", CHICA, TEXTO_SUAVE, CENTRO_X, 138)
        for i, mejora in enumerate(self.ofertas):
            self._dibujar_carta(pantalla, i, mejora)
        if self.pasos >= PASOS_SIN_ELEGIR:
            interfaz.ayudas(pantalla, self.app.entrada, [("cambiar", "ELEGIR"), ("aceptar", "TOMAR")])

    def _dibujar_carta(self, pantalla, i, mejora):
        # Cada carta cae desde arriba en saltos de 8 px; la elegida queda mas arriba y brilla
        pasos_carta = self.pasos - i * PASOS_ENTRE_CARTAS
        if pasos_carta < 0:
            return
        caida = max(0, 6 - pasos_carta) * 12
        elegida = i == self.elegida and self.pasos >= PASOS_SIN_ELEGIR
        centro_x = CENTRO_X + (i - (len(self.ofertas) - 1) / 2) * (ANCHO_CARTA + SEPARACION)
        arriba = ARRIBA_CARTA - caida - (14 if elegida else 0)
        carta = pygame.Rect(int(centro_x - ANCHO_CARTA // 2), arriba, ANCHO_CARTA, ALTO_CARTA)
        tienes = self.partida.mejora(mejora.tipo)
        pie = interfaz.carta(pantalla, carta, mejora.color, mejora.icono, mejora.nombre, mejora.descripcion,
                             elegida=elegida, rara=mejora.peso < 1, nivel=(tienes, mejora.maximo))
        if tienes == 0:
            etiqueta, color = "NUEVA", CIAN
        else:
            etiqueta, color = "NIVEL " + str(tienes + 1) + "/" + str(mejora.maximo), AMARILLO
        texto(pantalla, etiqueta, CHICA, color, pie.centerx, pie.centery)
