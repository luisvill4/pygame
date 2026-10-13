"""
Abeja: las hijas de La Colmena (no aparecen solas: no tienen costo ni nivel de desbloqueo).

Sale disparada de una compuerta, da vueltas a tu alrededor y cada tanto se frena,
destella en blanco (el aviso) y te PICA en linea recta. El dash la destruye; si te
pica, se pierde (muere_al_chocar). Si rompes una compuerta, todas se enojan y pican ya.
Cuando la Colmena se enfurece, las llama a casa: vuelven volando sin hacer daño.

Sprite (opcional): abeja.png, 2 cuadros de 20x20 (las alas arriba y abajo).
"""
import math
import random

import pygame

from juego import dibujo, recursos
from juego.config import AMARILLO, BLANCO, ABEJA_VELOCIDAD, ABEJA_PICADA, ABEJA_PUNTOS
from juego.enemigos.base import Enemigo, registrar_enemigo

AVISO_PICADA = 400          # ms que destella antes de picar
DURACION_PICADA = 450
NEGRO_ABEJA = (40, 24, 0)


def abeja_respaldo(alas_arriba):
    # Cuerpo amarillo con rayas, alitas y aguijon (10x10 agrandado x2)
    imagen = pygame.Surface((10, 10), pygame.SRCALPHA)
    ala_y = 1 if alas_arriba else 3
    imagen.fill((200, 230, 255), (1, ala_y, 3, 2))
    imagen.fill((200, 230, 255), (6, ala_y, 3, 2))
    imagen.fill(AMARILLO, (2, 4, 6, 5))
    imagen.fill(NEGRO_ABEJA, (2, 5, 6, 1))
    imagen.fill(NEGRO_ABEJA, (2, 7, 6, 1))
    imagen.fill(NEGRO_ABEJA, (4, 9, 2, 1))       # aguijon
    imagen.fill(NEGRO_ABEJA, (3, 3, 4, 1))       # cabeza
    return pygame.transform.scale(imagen, (20, 20))


_blancas = []


@registrar_enemigo
class Abeja(Enemigo):
    tipo = "abeja"
    nombre = "ABEJA"
    color = AMARILLO
    tamano = 20
    radio = 7
    destruible = True
    muere_al_chocar = True
    puntos_dash = ABEJA_PUNTOS
    esbirro = True              # es de un jefe: se va cuando lo vencen

    @classmethod
    def cuadros_de_respaldo(cls):
        return [abeja_respaldo(True), abeja_respaldo(False)]

    def al_aparecer(self, partida):
        self.estado = "rondar"
        self.estado_hasta = 0
        self.orbita = random.uniform(0, 2 * math.pi)
        self.proxima_picada = partida.tiempo + random.randint(1200, 2400)

    def salir_de(self, partida, x, y, angulo):
        # Sale disparada de la compuerta (parpadea un instante sin hacer daño)
        self.nacer_en(partida, x, y, 250)
        self.vx, self.vy = math.cos(angulo) * 5, math.sin(angulo) * 5
        self.estado = "salir"
        self.estado_hasta = partida.tiempo + 500

    def volver_a_casa(self, x, y):
        self.estado = "volver"
        self.casa = (x, y)
        self.llego = False

    def hace_danio(self):
        return self.estado != "volver"

    def enojarse(self, partida):
        # ¡Le rompieron una compuerta a su madre!: pica ya
        if self.estado in ("rondar", "salir"):
            self.proxima_picada = partida.tiempo

    def mover(self, partida):
        ahora = partida.tiempo
        factor = partida.factor_velocidad()
        if self.estado == "salir":
            self.vx *= 0.94
            self.vy *= 0.94
            if ahora >= self.estado_hasta:
                self.estado = "rondar"
        elif self.estado == "rondar":
            # Da vueltas alrededor de la nave, a unos 130 px
            self.orbita += 0.03
            nave_x, nave_y = partida.nave.centro()
            centro_x, centro_y = self.centro()
            destino_x = nave_x + math.cos(self.orbita) * 130 - centro_x
            destino_y = nave_y + math.sin(self.orbita) * 130 - centro_y
            distancia = math.hypot(destino_x, destino_y) or 1
            rapidez = ABEJA_VELOCIDAD * factor
            self.vx += (destino_x / distancia * rapidez - self.vx) * 0.08
            self.vy += (destino_y / distancia * rapidez - self.vy) * 0.08
            if ahora >= self.proxima_picada:
                self.estado = "aviso"
                self.estado_hasta = ahora + AVISO_PICADA
        elif self.estado == "aviso":
            self.vx *= 0.85
            self.vy *= 0.85
            if ahora >= self.estado_hasta:
                dir_x, dir_y, distancia = self.hacia_la_nave(partida)
                distancia = distancia or 1
                self.vx = dir_x / distancia * ABEJA_PICADA * factor
                self.vy = dir_y / distancia * ABEJA_PICADA * factor
                self.estado = "picar"
                self.estado_hasta = ahora + DURACION_PICADA
        elif self.estado == "volver":
            casa_x, casa_y = self.casa
            centro_x, centro_y = self.centro()
            distancia = math.hypot(casa_x - centro_x, casa_y - centro_y) or 1
            self.vx = (casa_x - centro_x) / distancia * 6
            self.vy = (casa_y - centro_y) / distancia * 6
            self.llego = distancia < 20
        elif self.estado == "picar":
            if ahora >= self.estado_hasta:
                self.estado = "rondar"
                self.proxima_picada = ahora + random.randint(1200, 2400)

    def dibujar_cuerpo(self, pantalla, partida):
        if self.estado == "aviso" and dibujo.parpadeo(60):
            if not _blancas:
                _blancas.append(recursos.blanquear(self.cuadros()[0]))
            dibujo.pegar(pantalla, _blancas[0], self.x, self.y)
        else:
            self.dibujar_animado(pantalla)
        if self.estado == "aviso":
            centro_x, centro_y = self.centro()
            dibujo.texto(pantalla, "!", dibujo.CHICA, BLANCO, int(centro_x), int(self.y) - 10)
