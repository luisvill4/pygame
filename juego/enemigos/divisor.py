"""
Divisor: una masa verde y lenta que te sigue. El dash la parte en dos:

    divisor (grande, 48x48) -> 2 divisor_mediano (32x32) -> 2 divisor_chico (20x20) cada uno

Los chicos son los mas rapidos y los que mas puntos dan. Los hijos nacen donde se partio
su padre, salen disparados hacia los costados y parpadean un instante sin hacer daño.
Los hijos son parte del escuadron del padre (para el bonus hay que romperlos a todos).

Sprites (opcionales): divisor.png (96x48), divisor_mediano.png (64x32) y
divisor_chico.png (40x20), 2 cuadros cada uno. Si faltan, se dibuja un slime de respaldo.
"""
import math

import pygame

from juego.config import VERDE, DIVISOR_VELOCIDAD, DIVISOR_PUNTOS, DIVISOR_NACIMIENTO
from juego.enemigos.base import Enemigo, registrar_enemigo, TIPOS_ENEMIGO

VERDE_OSCURO = (0, 90, 40)
BRILLO = (200, 255, 210)


def slime(tamano, aplastado):
    # Slime de respaldo: se dibuja a la mitad de tamaño y se agranda x2 (pixeles gruesos, retro)
    base = tamano // 2
    imagen = pygame.Surface((base, base), pygame.SRCALPHA)
    ancho = base * (0.96 if aplastado else 0.84)
    alto = base * (0.68 if aplastado else 0.82)
    cuerpo = pygame.Rect(0, 0, round(ancho), round(alto))
    cuerpo.midbottom = (base // 2, base)
    pygame.draw.ellipse(imagen, VERDE_OSCURO, cuerpo)
    pygame.draw.ellipse(imagen, VERDE, cuerpo.inflate(-2, -2))
    ojo = max(1, base // 10)
    ojos_y = cuerpo.top + round(alto * 0.38)
    for ojo_x in (cuerpo.centerx - base // 6 - ojo // 2, cuerpo.centerx + base // 6 - ojo // 2):
        imagen.fill(VERDE_OSCURO, (ojo_x, ojos_y, ojo, ojo + 1))
    imagen.fill(BRILLO, (cuerpo.left + base // 6, cuerpo.top + 2, max(1, base // 8), 1))
    return pygame.transform.scale(imagen, (tamano, tamano))


class DivisorBase(Enemigo):
    color = VERDE
    destruible = True
    nombre = "DIVISOR"
    pista = "¡PARTILO CON EL DASH!"
    hijo = None                 # tipo en el que se parte (None = el mas chico)
    giro = 0.03                 # que tan rapido corrige el rumbo (los chicos son mas agiles)

    @classmethod
    def cuadros_de_respaldo(cls):
        return [slime(cls.tamano, False), slime(cls.tamano, True)]

    def mover(self, partida):
        dir_x, dir_y, distancia = self.hacia_la_nave(partida)
        rapidez = self.rapidez(partida, DIVISOR_VELOCIDAD[self.tipo])
        if distancia > 0:
            self.vx += (dir_x / distancia * rapidez - self.vx) * self.giro
            self.vy += (dir_y / distancia * rapidez - self.vy) * self.giro
        self.separarse(partida)

    def al_destruirse(self, partida, con_dash):
        # Con el dash se parte en dos; congelado se rompe entero
        if self.hijo is None or not con_dash:
            return
        centro_x, centro_y = self.centro()
        # Los hijos salen hacia los costados del dash (perpendicular a la nave)
        nave = partida.nave
        largo = math.hypot(nave.vx, nave.vy) or 1
        costado_x, costado_y = -nave.vy / largo, nave.vx / largo
        for signo in (-1, 1):
            hijo = TIPOS_ENEMIGO[self.hijo](partida)
            if self.escuadron is not None:
                self.escuadron.sumar(hijo)  # es parte del escuadron del padre
            hijo.nacer_en(partida, centro_x + costado_x * signo * 10, centro_y + costado_y * signo * 10,
                          DIVISOR_NACIMIENTO)
            hijo.vx, hijo.vy = costado_x * signo * 4, costado_y * signo * 4
            partida.enemigos.append(hijo)

    def actualizar(self, partida, congelado):
        # Mientras nace se sigue deslizando (asi se separa de donde estaba el padre)
        if self.naciendo and not congelado and not self.saliendo:
            self.x += self.vx
            self.y += self.vy
            self.vx *= 0.9
            self.vy *= 0.9
            self._bordes()
        super().actualizar(partida, congelado)


@registrar_enemigo
class Divisor(DivisorBase):
    tipo = "divisor"
    tamano = 48
    radio = 18
    hijo = "divisor_mediano"
    sonido_roto = "divisor_parte_1"
    puntos_dash = DIVISOR_PUNTOS["divisor"]


@registrar_enemigo
class DivisorMediano(DivisorBase):
    tipo = "divisor_mediano"
    tamano = 32
    radio = 12
    hijo = "divisor_chico"
    sonido_roto = "divisor_parte_2"
    giro = 0.05
    puntos_dash = DIVISOR_PUNTOS["divisor_mediano"]


@registrar_enemigo
class DivisorChico(DivisorBase):
    tipo = "divisor_chico"
    sonido_roto = "divisor_parte_3"
    tamano = 20
    radio = 7
    giro = 0.07
    puntos_dash = DIVISOR_PUNTOS["divisor_chico"]
