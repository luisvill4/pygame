"""
Proyectiles de los jefes. Todos viven en partida.balas y comparten la misma interfaz:

    mover(partida) -> False si hay que borrarlo (salio de la pantalla o estallo)
    dibujar(pantalla, parpadeo_encendido)
    radio          -> tamaño del circulo que hace daño

- Bala:  sigue derecho.
- Misil: lento, te persigue un rato girando de a poco y despues sigue derecho.
- Mina:  baja frenando, se queda quieta, avisa y estalla en un anillo de balas.

Como todos estan en la misma lista, el hielo los rompe, el dash los atraviesa y el
choque con la nave se revisa igual para todos (Partida._choques_jefe). Es polimorfismo:
cada clase resuelve "moverse" y "dibujarse" a su manera.
"""
import math
import random

from juego import lienzo
from juego.dibujo import parpadeo
from juego.config import (ALTO, MAGENTA, ROJO, BLANCO, AMARILLO, EMBESTIDA, FUEGO, RADIO_BALA,
                          FORTALEZA_MISIL_GUIADO, FORTALEZA_MINA_ESPERA, MS_POR_FRAME)


def fuera_de_pantalla(x, y):
    return x < -20 or x > lienzo.ancho + 20 or y < -20 or y > ALTO + 20


class Bala:
    __slots__ = ("x", "y", "vx", "vy")
    radio = RADIO_BALA

    def __init__(self, x, y, vx, vy):
        self.x, self.y, self.vx, self.vy = x, y, vx, vy

    def mover(self, partida):
        self.x += self.vx
        self.y += self.vy
        if fuera_de_pantalla(self.x, self.y):
            return False
        if random.random() < 0.3:
            partida.efectos.particula(self.x, self.y, 0, 0, EMBESTIDA, 8, 2)
        return True

    def dibujar(self, pantalla, encendido):
        # Bala pixelada que cambia de color (en la cuadricula de 2 pixeles)
        borde, centro = (MAGENTA, BLANCO) if encendido else (ROJO, (255, 150, 230))
        bala_x = int(self.x) // 2 * 2
        bala_y = int(self.y) // 2 * 2
        pantalla.fill(borde, (bala_x - 5, bala_y - 3, 10, 6))
        pantalla.fill(borde, (bala_x - 3, bala_y - 5, 6, 10))
        pantalla.fill(centro, (bala_x - 2, bala_y - 2, 4, 4))


class Misil(Bala):
    # Te sigue girando de a poco (asi se puede esquivar con una curva cerrada o el dash)
    __slots__ = ("guiado",)
    radio = 5
    giro = 0.045            # radianes por paso que puede corregir el rumbo

    def __init__(self, x, y, vx, vy):
        super().__init__(x, y, vx, vy)
        self.guiado = FORTALEZA_MISIL_GUIADO    # ms que le quedan siguiendote

    def mover(self, partida):
        if self.guiado > 0:
            self.guiado -= MS_POR_FRAME
            nave_x, nave_y = partida.nave.centro()
            rumbo = math.atan2(self.vy, self.vx)
            deseado = math.atan2(nave_y - self.y, nave_x - self.x)
            # La diferencia entre los dos angulos, llevada a -pi..pi (para girar por el lado corto)
            diferencia = (deseado - rumbo + math.pi) % (2 * math.pi) - math.pi
            rumbo += max(-self.giro, min(self.giro, diferencia))
            rapidez = math.hypot(self.vx, self.vy)
            self.vx, self.vy = math.cos(rumbo) * rapidez, math.sin(rumbo) * rapidez
        self.x += self.vx
        self.y += self.vy
        if fuera_de_pantalla(self.x, self.y):
            return False
        # Humo de fuego por detras
        partida.efectos.particula(self.x - self.vx * 3, self.y - self.vy * 3,
                                  -self.vx * 0.2, -self.vy * 0.2, FUEGO, 12, 2)
        return True

    def dibujar(self, pantalla, encendido):
        # Una cabeza amarilla con la punta hacia donde va
        misil_x = int(self.x) // 2 * 2
        misil_y = int(self.y) // 2 * 2
        pantalla.fill(ROJO, (misil_x - 5, misil_y - 5, 10, 10))
        pantalla.fill(AMARILLO if encendido else BLANCO, (misil_x - 3, misil_y - 3, 6, 6))
        rapidez = math.hypot(self.vx, self.vy) or 1
        punta_x = int(self.x + self.vx / rapidez * 6) // 2 * 2
        punta_y = int(self.y + self.vy / rapidez * 6) // 2 * 2
        pantalla.fill(BLANCO, (punta_x - 2, punta_y - 2, 4, 4))


class Mina(Bala):
    # Baja frenando hasta quedarse quieta; al rato estalla en un anillo de balas
    __slots__ = ("espera", "rapidez_balas")
    radio = 8
    cantidad_balas = 8

    def __init__(self, x, y, vx, vy, rapidez_balas):
        super().__init__(x, y, vx, vy)
        self.espera = FORTALEZA_MINA_ESPERA     # ms hasta estallar
        self.rapidez_balas = rapidez_balas

    def mover(self, partida):
        self.x += self.vx
        self.y += self.vy
        self.vx *= 0.95         # se va frenando
        self.vy *= 0.95
        self.espera -= MS_POR_FRAME
        if self.espera <= 0:
            self.estallar(partida)
            return False
        return not fuera_de_pantalla(self.x, self.y)

    def estallar(self, partida):
        giro = random.uniform(0, math.pi)
        for i in range(self.cantidad_balas):
            direccion = 2 * math.pi * i / self.cantidad_balas + giro
            partida.balas.append(Bala(self.x, self.y, math.cos(direccion) * self.rapidez_balas,
                                      math.sin(direccion) * self.rapidez_balas))
        partida.efectos.explosion(self.x, self.y, FUEGO, 16, 4, 3)
        partida.sonidos.reproducir("golpe")

    def dibujar(self, pantalla, encendido):
        # Un rombo con pinches; en el ultimo medio segundo parpadea rapido (aviso)
        mina_x = int(self.x) // 2 * 2
        mina_y = int(self.y) // 2 * 2
        por_estallar = self.espera < 500
        luz = BLANCO if (parpadeo(60) if por_estallar else encendido) else ROJO
        pantalla.fill(MAGENTA, (mina_x - 6, mina_y - 6, 12, 12))
        for pinche_x, pinche_y in ((-10, -2), (6, -2), (-2, -10), (-2, 6)):
            pantalla.fill(MAGENTA, (mina_x + pinche_x, mina_y + pinche_y, 4, 4))
        pantalla.fill(luz, (mina_x - 2, mina_y - 2, 4, 4))


def mover_balas(partida):
    # Se recorre una copia: las minas agregan balas nuevas a la lista al estallar
    for bala in partida.balas[:]:
        if not bala.mover(partida):
            partida.balas.remove(bala)


def romper_balas(balas, efectos, paleta):
    # Todas las balas estallan (al recoger hielo o al vencer al jefe)
    for bala in balas:
        efectos.explosion(bala.x, bala.y, paleta, 4, 2, 2)
    balas.clear()


def dibujar_balas(pantalla, balas):
    encendido = parpadeo(100)
    for bala in balas:
        bala.dibujar(pantalla, encendido)
