"""
La moneda: se recoge con la nave y reaparece en otro lugar.

Aparece fuera del HUD, a una distancia de la nave que se alcanza antes de que se
corte el combo, y lejos de los enemigos y del jefe.
"""
import math
import random

import pygame

from juego import recursos, lienzo
from juego.hud import posicion_libre
from juego.config import (AMARILLO, ORO, IMANTADO, MS_CUADRO_MONEDA,
                          MONEDA_DISTANCIA_MIN, MONEDA_DISTANCIA_MAX)

TAMANO = 20


def imagen_moneda():
    # La moneda girando: con la animacion si existe; si no, una elipse que se angosta
    cuadros = recursos.hoja("moneda_giro.png", TAMANO)
    if cuadros:
        return recursos.cuadro_animado(cuadros, MS_CUADRO_MONEDA)
    ancho = max(4, int(abs(math.cos(pygame.time.get_ticks() / 180)) * 10) * 2)
    imagen = pygame.Surface((TAMANO, TAMANO), pygame.SRCALPHA)
    pygame.draw.ellipse(imagen, AMARILLO, (10 - ancho // 2, 0, ancho, TAMANO))
    return imagen


class Moneda:
    def __init__(self):
        # Empieza en el centro de la pantalla; (x, y) es su esquina de arriba a la izquierda
        self.x, self.y = lienzo.centro_x(), 300

    def centro(self):
        return self.x + TAMANO / 2, self.y + TAMANO / 2

    def caja(self):
        return pygame.Rect(int(self.x), int(self.y), TAMANO, TAMANO)

    def mover_a_lugar_nuevo(self, partida):
        self.x, self.y = lugar_para_moneda(partida)

    def atraer(self, nave, efectos):
        # Iman: si esta cerca, vuela hacia la nave
        nave_x, nave_y = nave.centro()
        centro_x, centro_y = self.centro()
        hacia_x, hacia_y = nave_x - centro_x, nave_y - centro_y
        distancia = math.hypot(hacia_x, hacia_y)
        if 0 < distancia < 250:
            paso = min(distancia, 6)
            self.x += hacia_x / distancia * paso
            self.y += hacia_y / distancia * paso
            if random.random() < 0.3:
                efectos.particula(self.x + 10, self.y + 10, 0, 0, IMANTADO, 10, 2)

    def brillar(self, efectos):
        # Brillo ocasional
        if random.random() < 0.06:
            efectos.particula(self.x + random.randint(0, TAMANO), self.y + random.randint(0, TAMANO),
                              0, -0.3, ORO, 14, 2)

    def dibujar(self, pantalla):
        imagen = imagen_moneda()
        pantalla.blit(imagen, imagen.get_rect(center=(int(self.x) + 10, int(self.y) + 10)))


def lugar_para_moneda(partida):
    # Prueba lugares al azar hasta encontrar uno que cumpla todo
    nave_x, nave_y = partida.nave.centro()
    for _ in range(200):
        nueva_x, nueva_y = posicion_libre(TAMANO, TAMANO)
        centro_x, centro_y = nueva_x + 10, nueva_y + 10
        distancia = math.hypot(centro_x - nave_x, centro_y - nave_y)
        if distancia < MONEDA_DISTANCIA_MIN or distancia > MONEDA_DISTANCIA_MAX:
            continue
        if any(math.hypot(centro_x - e.centro()[0], centro_y - e.centro()[1]) < 60 for e in partida.enemigos):
            continue
        if partida.jefe is not None and any(caja.inflate(40, 40).colliderect((nueva_x, nueva_y, TAMANO, TAMANO))
                                            for caja in partida.jefe.cajas_danio()):
            continue
        return nueva_x, nueva_y
    return nueva_x, nueva_y     # muy raro: si no encontro un lugar ideal, usa el ultimo
