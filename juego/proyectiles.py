"""
Balas (las dispara el jefe): siguen derecho y desaparecen al salir de la pantalla.
"""
import random

from juego.dibujo import parpadeo
from juego.config import ANCHO, ALTO, MAGENTA, ROJO, BLANCO, EMBESTIDA


class Bala:
    __slots__ = ("x", "y", "vx", "vy")

    def __init__(self, x, y, vx, vy):
        self.x, self.y, self.vx, self.vy = x, y, vx, vy

    def mover(self, efectos):
        # Devuelve False si salio de la pantalla (hay que borrarla)
        self.x += self.vx
        self.y += self.vy
        if self.x < -20 or self.x > ANCHO + 20 or self.y < -20 or self.y > ALTO + 20:
            return False
        if random.random() < 0.3:
            efectos.particula(self.x, self.y, 0, 0, EMBESTIDA, 8, 2)
        return True


def mover_balas(balas, efectos):
    for bala in balas[:]:
        if not bala.mover(efectos):
            balas.remove(bala)


def romper_balas(balas, efectos, paleta):
    # Todas las balas estallan (al recoger hielo o al vencer al jefe)
    for bala in balas:
        efectos.explosion(bala.x, bala.y, paleta, 4, 2, 2)
    balas.clear()


def dibujar_balas(pantalla, balas):
    # Balas pixeladas que cambian de color (en la cuadricula de 2 pixeles)
    if parpadeo(100):
        borde, centro = MAGENTA, BLANCO
    else:
        borde, centro = ROJO, (255, 150, 230)
    for bala in balas:
        bala_x = int(bala.x) // 2 * 2
        bala_y = int(bala.y) // 2 * 2
        pantalla.fill(borde, (bala_x - 5, bala_y - 3, 10, 6))
        pantalla.fill(borde, (bala_x - 3, bala_y - 5, 6, 10))
        pantalla.fill(centro, (bala_x - 2, bala_y - 2, 4, 4))
