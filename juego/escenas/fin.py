"""Game Over: el puntaje cuenta desde cero, la tabla de records y ENTER para jugar otra vez."""
import random

import pygame

from juego import dibujo
from juego.dibujo import texto, CHICA, MEDIA, GRANDE, TITULO
from juego.config import (ROJO, AMARILLO, CIAN, BLANCO, GRIS, FUEGO, ORO, ESCARCHA, ENERGIA, CORAZON)
from juego.entrada import ACEPTAR
from juego.escenas.base import Escena


class Fin(Escena):
    def __init__(self, app, partida, fila_nueva):
        super().__init__(app)
        self.partida = partida
        self.fila_nueva = fila_nueva    # fila de la tabla que se acaba de agregar (-1 = ninguna)

    def contador(self):
        # El puntaje cuenta desde cero hasta el resultado en 1.5 segundos
        puntaje = self.partida.puntaje
        return min(puntaje, int(puntaje * self.tiempo_en_escena() / 1500))

    def actualizar(self, entrada):
        self.app.efectos.actualizar()
        # Nuevo record: fuegos artificiales cuando termina de contar
        if self.fila_nueva == 0 and self.contador() == self.partida.puntaje and random.random() < 0.05:
            paleta = random.choice([FUEGO, ORO, ESCARCHA, ENERGIA, CORAZON])
            self.app.efectos.explosion(random.randint(80, 720), random.randint(80, 560), paleta, 40, 6)
        # ENTER se ignora el primer momento (para no saltear esta pantalla sin querer)
        if entrada.pulso(ACEPTAR) and self.tiempo_en_escena() > 800:
            self.app.nueva_partida()

    def dibujar(self, pantalla):
        self.app.fondo.mover_y_dibujar(pantalla)
        self.app.efectos.dibujar(pantalla)      # fuegos artificiales detras de todo
        dibujo.texto_3d(pantalla, "GAME OVER", TITULO, ROJO, (110, 0, 30), 75)

        contador = self.contador()
        dibujo.marco(pantalla, pygame.Rect(220, 125, 360, 125), AMARILLO if self.fila_nueva == 0 else CIAN)
        texto(pantalla, "PUNTOS", CHICA, ROJO, 400, 155)
        texto(pantalla, dibujo.numero_arcade(contador), GRANDE, BLANCO, 400, 195)
        texto(pantalla, "MEJOR COMBO " + str(self.partida.mejor_combo), CHICA, GRIS, 400, 230)
        if self.fila_nueva == 0 and contador == self.partida.puntaje:
            texto(pantalla, "¡NUEVO RECORD!", MEDIA, dibujo.color_arcoiris(), 400, 288)

        dibujo.tabla_records(pantalla, self.app.records.filas, 330, self.fila_nueva)

        if dibujo.parpadeo():
            texto(pantalla, self.app.entrada.ayuda("PRESIONA ENTER", "PRESIONA A"), MEDIA, CIAN, 400, 545)
        dibujo.efecto_crt(pantalla)
