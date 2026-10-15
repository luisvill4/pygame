"""
MAPA ESTELAR: el centro del modo historia. Los cinco sectores como planetas unidos por la
ruta; lo recorrido brilla en el color de cada sector y lo que falta esta apagado.

IZQ/DER elige una mision; ACEPTAR despega (dialogo de antes -> READY -> la mision). Se
puede jugar la primera, las cumplidas (para buscar lo que falta del Archivo) y la que
sigue a una cumplida (Mision.disponible). OPCIONES abre el Archivo; VOLVER, el inicio.
Los planetas salen de las misiones registradas (historia/misiones/): una mision nueva
aparece sola (con su lugar en PLANETAS).
Lo que pasa al terminar una mision esta en escenas/historia/pasajes.py.
"""
import math

import pygame

from juego import dibujo, interfaz, nave
from juego.dibujo import texto, CHICA, MEDIA, GRANDE
from juego.config import (ANCHO, FONDO, SECTORES, ROJO, TEXTO, TEXTO_SUAVE, TEXTO_APAGADO, LINEA_APAGADA, VERDE,
                          CIAN, AMARILLO)
from juego.entrada import ACEPTAR, VOLVER, IZQUIERDA, DERECHA, OPCIONES
from juego.escenas.base import Escena
from juego.escenas.historia.dialogo import Dialogo
from juego.escenas.historia.archivo import Archivo
from juego.historia.mision import misiones_en_orden
from juego.historia.modo import ModoHistoria
from juego.sonido import SILENCIO

PLANETAS = [(150, 300), (340, 200), (540, 280), (750, 190), (940, 290)]     # centro de cada mision
RADIO_PLANETA = 26
INFORME = pygame.Rect(48, 392, ANCHO - 96, 148)
TILDE = [".......", "......X", ".....XX", "X...XX.", "XX.XX..", ".XXX...", "..X...."]


class Mapa(Escena):
    musica = "menu"
    ambiente = SILENCIO

    def __init__(self, app, elegida=None):
        super().__init__(app)
        self.misiones = misiones_en_orden()
        self.elegida = elegida or self._la_que_sigue()
        self.cursor = interfaz.Cursor(self.elegida - 1, rapidez=0.25)

    def _la_que_sigue(self):
        # La primera mision sin cumplir (si estan todas, la ultima)
        for mision in self.misiones:
            if mision.numero not in self.app.progreso.misiones:
                return mision.numero
        return len(self.misiones)

    def mision(self, numero):
        return self.misiones[numero - 1]

    def disponible(self, numero):
        return self.mision(numero).disponible(self.app.progreso)

    def actualizar(self, entrada):
        self.mover_fondo()
        self.cursor.avanzar()
        if entrada.pulso(IZQUIERDA) or entrada.pulso(DERECHA):
            paso = -1 if entrada.pulso(IZQUIERDA) else 1
            self.elegida = max(1, min(len(self.misiones), self.elegida + paso))
            self.cursor.ir_a(self.elegida - 1)
            self.app.sonidos.reproducir("ui_mover")
        elif entrada.pulso(ACEPTAR):
            if self.disponible(self.elegida):
                self.app.sonidos.reproducir("ui_aceptar")
                self._despegar()
            else:
                self.app.sonidos.reproducir("dash_vacio")      # "todavia no"
        elif entrada.pulso(OPCIONES):
            self.app.sonidos.reproducir("ui_aceptar")
            self.app.cambiar_escena(Archivo(self.app, volver_a=self))
        elif entrada.pulso(VOLVER):
            from juego.escenas.inicio import Inicio        # (Inicio abre el Mapa: se importa aca)
            self.app.sonidos.reproducir("ui_volver")
            self.app.cambiar_escena(Inicio(self.app))

    def _despegar(self):
        # El dialogo de antes, en el bioma de la mision, y despues READY -> la mision
        mision = self.mision(self.elegida)
        sector = SECTORES[mision.sector - 1]
        app = self.app
        app.fondo.ir_a_sector(sector, instantaneo=True)
        app.cambiar_escena(Dialogo(app, mision.antes, lambda: app.nueva_partida(modo=ModoHistoria(mision.numero)),
                                   "MISION %d" % mision.numero, mision.titulo, sector["color"]))

    # ---------- Dibujo ----------

    def dibujar(self, pantalla):
        self.dibujar_fondo(pantalla)
        interfaz.titulo(pantalla, "MAPA ESTELAR", 48, 60, CIAN, interfaz.mezclar(CIAN, FONDO, 0.6), tamano=GRANDE)
        # La amenaza, siempre a la vista
        if dibujo.parpadeo(900):
            texto(pantalla, "LA MAREA LLEGA EN 6 AÑOS", CHICA, ROJO, ANCHO - 48, 60, alinear="derecha")
        self._dibujar_ruta(pantalla)
        for mision in self.misiones:
            self._dibujar_planeta(pantalla, mision.numero)
        self._dibujar_nave(pantalla)
        self._dibujar_informe(pantalla)
        interfaz.ayudas(pantalla, self.app.entrada,
                        [("cambiar", "ELEGIR"), ("opciones", "ARCHIVO"), ("volver", "VOLVER"),
                         ("aceptar", "DESPEGAR")])

    def _dibujar_ruta(self, pantalla):
        # Puntitos entre un planeta y el siguiente: del color del sector si ya se puede ir
        for i in range(len(PLANETAS) - 1):
            (x1, y1), (x2, y2) = PLANETAS[i], PLANETAS[i + 1]
            color = SECTORES[self.mision(i + 2).sector - 1]["color"] if self.disponible(i + 2) else LINEA_APAGADA
            largo = math.hypot(x2 - x1, y2 - y1)
            pasos = int((largo - 2 * RADIO_PLANETA - 16) // 14)
            for paso in range(pasos + 1):
                avance = (RADIO_PLANETA + 8 + paso * 14) / largo
                x = dibujo.en_grilla(x1 + (x2 - x1) * avance)
                y = dibujo.en_grilla(y1 + (y2 - y1) * avance)
                pantalla.fill(color, (x - 2, y - 2, 4, 4))

    def _dibujar_planeta(self, pantalla, numero):
        centro_x, centro_y = PLANETAS[numero - 1]
        sector = SECTORES[self.mision(numero).sector - 1]
        cumplida = numero in self.app.progreso.misiones
        if self.disponible(numero):
            color, sombra = sector["color"], interfaz.mezclar(sector["color"], FONDO, 0.55)
        else:
            color, sombra = TEXTO_APAGADO, LINEA_APAGADA
        _circulo(pantalla, centro_x, centro_y, RADIO_PLANETA, sombra)
        _circulo(pantalla, centro_x - 4, centro_y - 4, RADIO_PLANETA - 8, color)
        if numero == self.elegida and dibujo.parpadeo(300):
            _anillo(pantalla, centro_x, centro_y, RADIO_PLANETA + 10, color)
        texto(pantalla, str(numero), CHICA, TEXTO if self.disponible(numero) else TEXTO_APAGADO, centro_x,
              centro_y + RADIO_PLANETA + 22)
        if cumplida:
            dibujo.pixel_art(pantalla, TILDE, centro_x + RADIO_PLANETA, centro_y - RADIO_PLANETA, VERDE, 4)
        elif not self.disponible(numero):
            texto(pantalla, "?", MEDIA, TEXTO_APAGADO, centro_x - 2, centro_y - 2)

    def _dibujar_nave(self, pantalla):
        # La Alondra flota arriba del planeta elegido y se desliza al cambiar
        indice = self.cursor.valor
        base = int(indice)
        siguiente = min(base + 1, len(PLANETAS) - 1)
        mezcla = indice - base
        x = PLANETAS[base][0] + (PLANETAS[siguiente][0] - PLANETAS[base][0]) * mezcla
        y = PLANETAS[base][1] + (PLANETAS[siguiente][1] - PLANETAS[base][1]) * mezcla
        flota = round(math.sin(pygame.time.get_ticks() / 300) * 2) * 2
        dibujo.pegar(pantalla, nave.imagen("nave"), x, y - RADIO_PLANETA - 44 + flota, centrado=True)

    def _dibujar_informe(self, pantalla):
        numero = self.elegida
        mision = self.mision(numero)
        sector = SECTORES[mision.sector - 1]
        color = sector["color"] if self.disponible(numero) else TEXTO_APAGADO
        adentro = interfaz.panel(pantalla, INFORME, color, "MISION %d" % numero)
        texto(pantalla, mision.titulo if self.disponible(numero) else "? ? ?", MEDIA, color, adentro.left,
              adentro.top + 10, alinear="izquierda")
        texto(pantalla, sector["nombre"], CHICA, TEXTO_SUAVE, adentro.left, adentro.top + 46, alinear="izquierda")
        if numero in self.app.progreso.misiones:
            estado, color_estado = "CUMPLIDA", VERDE
        elif self.disponible(numero):
            estado, color_estado = "NUEVA", AMARILLO
        else:
            estado, color_estado = "CUMPLI LA MISION %d" % (numero - 1), TEXTO_APAGADO
        texto(pantalla, estado, CHICA, color_estado, adentro.right, adentro.top + 10, alinear="derecha")
        # Cuantos fragmentos del Archivo hay en esta mision (no dice donde)
        propios = mision.fragmentos_visibles()
        hallados = len([fragmento for fragmento in propios if fragmento.id in self.app.progreso.fragmentos])
        texto(pantalla, "ARCHIVO %d/%d" % (hallados, len(propios)), CHICA, TEXTO_SUAVE, adentro.right,
              adentro.top + 46, alinear="derecha")


def _circulo(pantalla, centro_x, centro_y, radio, color):
    # Un circulo lleno en la grilla de 2 px (de a renglones)
    for dy in range(-radio, radio + 1, 2):
        mitad = dibujo.en_grilla(math.sqrt(max(0, radio * radio - dy * dy)))
        pantalla.fill(color, (dibujo.en_grilla(centro_x) - mitad, dibujo.en_grilla(centro_y + dy), 2 * mitad, 2))


def _anillo(pantalla, centro_x, centro_y, radio, color):
    # Un anillo de cuadraditos (el planeta elegido)
    for i in range(24):
        angulo = 2 * math.pi * i / 24
        x = dibujo.en_grilla(centro_x + math.cos(angulo) * radio)
        y = dibujo.en_grilla(centro_y + math.sin(angulo) * radio)
        pantalla.fill(color, (x - 2, y - 2, 4, 4))
