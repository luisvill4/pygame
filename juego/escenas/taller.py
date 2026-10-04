"""
Taller: elegir UNA mejora entre tres cartas (ver mejoras.py).

Se abre desde Juego cuando el director deja ofertas (nivel 3 y al cerrar cada sector).
El juego queda quieto detras (la ultima imagen, oscurecida). Las cartas caen de a una;
IZQ/DER elige y ENTER la toma. Los primeros instantes no se aceptan teclas, asi no
se elige sin querer una carta que todavia no se leyo.
"""
import pygame

from juego import dibujo
from juego.dibujo import texto, MINI, CHICA, GRANDE
from juego.config import FONDO, BLANCO, GRIS, AMARILLO, CIAN, MAGENTA
from juego.entrada import ACEPTAR, IZQUIERDA, DERECHA
from juego.escenas.base import Escena

PASOS_SIN_ELEGIR = 30       # pasos (medio segundo) en que se ignoran las teclas
PASOS_ENTRE_CARTAS = 5      # cada carta cae este numero de pasos despues de la anterior
ANCHO_CARTA, ALTO_CARTA = 220, 290
ARRIBA_CARTA = 172


class Taller(Escena):
    def __init__(self, app, escena_juego, captura):
        super().__init__(app)
        self.escena_juego = escena_juego
        self.partida = escena_juego.partida
        self.captura = captura
        self.ofertas = list(self.partida.director.ofertas)
        self.elegida = len(self.ofertas) // 2       # empieza en la del medio
        self.pasos = 0                              # pasos desde que se abrio (animacion)
        app.sonidos.reproducir("nuevo_record")

    def actualizar(self, entrada):
        self.pasos += 1
        if self.pasos < PASOS_SIN_ELEGIR:
            return
        if entrada.pulso(IZQUIERDA):
            self.elegida = (self.elegida - 1) % len(self.ofertas)
            self.app.sonidos.reproducir("seleccion")
        elif entrada.pulso(DERECHA):
            self.elegida = (self.elegida + 1) % len(self.ofertas)
            self.app.sonidos.reproducir("seleccion")
        elif entrada.pulso(ACEPTAR):
            self.partida.elegir_mejora(self.ofertas[self.elegida].tipo)
            self.app.cambiar_escena(self.escena_juego)

    # ---------- Dibujo ----------

    def dibujar(self, pantalla_completa):
        pantalla_completa.blit(self.captura, (0, 0))
        dibujo.oscurecer(pantalla_completa, FONDO, 190)
        pantalla = dibujo.zona_central(pantalla_completa)
        dibujo.texto_3d(pantalla, "ELIGE UNA MEJORA", GRANDE, AMARILLO, MAGENTA, 82, 4)
        texto(pantalla, "DURA TODA LA PARTIDA", CHICA, GRIS, 400, 134)

        for i, mejora in enumerate(self.ofertas):
            self._dibujar_carta(pantalla, i, mejora)

        if self.pasos >= PASOS_SIN_ELEGIR:
            ayuda = self.app.entrada.ayuda("IZQ/DER ELEGIR   ENTER TOMAR", "IZQ/DER ELEGIR   A TOMAR")
            texto(pantalla, ayuda, CHICA, GRIS, 400, 520)
        dibujo.efecto_crt(pantalla_completa)

    def _dibujar_carta(self, pantalla, i, mejora):
        # Cada carta cae desde arriba en saltos de 8 px; la elegida queda mas arriba y brilla
        pasos_carta = self.pasos - i * PASOS_ENTRE_CARTAS
        if pasos_carta < 0:
            return
        caida = max(0, 5 - pasos_carta) * 8
        elegida = i == self.elegida and self.pasos >= PASOS_SIN_ELEGIR
        centro_x = 400 + (i - (len(self.ofertas) - 1) / 2) * 240
        arriba = ARRIBA_CARTA - caida - (12 if elegida else 0)
        carta = pygame.Rect(int(centro_x - ANCHO_CARTA // 2), arriba, ANCHO_CARTA, ALTO_CARTA)

        if elegida:
            dibujo.marco(pantalla, carta, BLANCO if dibujo.parpadeo(300) else mejora.color)
        else:
            dibujo.marco(pantalla, carta, (60, 60, 90))
        # Icono grande, nombre, nivel y que hace
        color_icono = mejora.color if elegida else tuple(c * 2 // 3 for c in mejora.color)
        dibujo.pixel_art(pantalla, mejora.icono, carta.centerx, arriba + 62, color_icono, 7)
        texto(pantalla, mejora.nombre, CHICA, mejora.color if elegida else BLANCO, carta.centerx, arriba + 126)
        for fila, linea in enumerate(mejora.descripcion):
            texto(pantalla, linea, MINI, BLANCO if elegida else GRIS, carta.centerx, arriba + 162 + fila * 16)
        if mejora.peso < 1 and dibujo.parpadeo(250):
            texto(pantalla, "RARA", MINI, MAGENTA, carta.centerx, arriba + 18)      # sale menos seguido
        tenes = self.partida.mejora(mejora.tipo)
        if tenes == 0:
            etiqueta, color = "NUEVA", CIAN
        else:
            etiqueta, color = "NIVEL " + str(tenes + 1) + "/" + str(mejora.maximo), AMARILLO
        texto(pantalla, etiqueta, CHICA, color, carta.centerx, carta.bottom - 32)
