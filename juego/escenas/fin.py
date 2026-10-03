"""Game Over: el puntaje cuenta desde cero, la tabla de records y ENTER para jugar otra vez."""
import random

import pygame

from juego import dibujo, lienzo
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
        self.mover_fondo()
        self.app.efectos.actualizar()
        # Nuevo record: fuegos artificiales cuando termina de contar
        if self.fila_nueva == 0 and self.contador() == self.partida.puntaje and random.random() < 0.05:
            paleta = random.choice([FUEGO, ORO, ESCARCHA, ENERGIA, CORAZON])
            self.app.efectos.explosion(random.randint(80, lienzo.ancho - 80), random.randint(80, 560), paleta, 40, 6)
        # ENTER se ignora el primer momento (para no saltear esta pantalla sin querer)
        if entrada.pulso(ACEPTAR) and self.tiempo_en_escena() > 800:
            self.app.nueva_partida()

    def dibujar(self, pantalla_completa):
        # Fondo y fuegos artificiales en todo el ancho; el resto en la zona central de 800x600
        self.dibujar_fondo(pantalla_completa)
        self.app.efectos.dibujar(pantalla_completa)     # fuegos artificiales detras de todo
        pantalla = dibujo.zona_central(pantalla_completa)
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
        dibujo.efecto_crt(pantalla_completa)
