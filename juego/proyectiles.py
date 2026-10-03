"""
Proyectiles de los jefes. Todos viven en partida.balas y comparten la misma interfaz:

    mover(partida) -> False si hay que borrarlo (salio de la pantalla o estallo)
    dibujar(pantalla, parpadeo_encendido)
    radio          -> tamaño del circulo que hace daño
    destruible     -> el dash lo destruye (y da 'puntos'); si no, el dash lo atraviesa

- Bala:     sigue derecho.
- Obus:     una bala grande y lenta (se ve venir de lejos).
- Misil:    te persigue un rato girando de a poco; el dash lo destruye.
- Mina:     viaja frenando, se queda quieta, avisa y estalla en una cruz de balas.
- Escombro: un trozo de metal que cae.
- Onda:     una onda de choque que corre a ras del piso.
- Veneno:   una gota verde y lenta que escupe la Serpiente.

Como todos estan en la misma lista, el hielo los rompe, el dash los atraviesa y el
choque con la nave se revisa igual para todos (Partida._choques_jefe). Es polimorfismo:
cada clase resuelve "moverse" y "dibujarse" a su manera.
"""
import math
import random

from juego import lienzo
from juego.dibujo import parpadeo
from juego.config import (ALTO, MAGENTA, ROJO, BLANCO, AMARILLO, EMBESTIDA, FUEGO, RADIO_BALA, MS_POR_FRAME)

GRIS_METAL = (90, 100, 150)
METAL_OSCURO = (44, 48, 86)


def fuera_de_pantalla(x, y, margen=20):
    return x < -margen or x > lienzo.ancho + margen or y < -margen or y > ALTO + margen


class Bala:
    __slots__ = ("x", "y", "vx", "vy")
    radio = RADIO_BALA
    destruible = False
    puntos = 0

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


class Obus(Bala):
    # Grande y lento: un "¡PUM!" que se ve venir
    __slots__ = ()
    radio = 8

    def mover(self, partida):
        self.x += self.vx
        self.y += self.vy
        if fuera_de_pantalla(self.x, self.y, 30):
            return False
        if random.random() < 0.5:
            partida.efectos.particula(self.x, self.y, -self.vx * 0.2, -self.vy * 0.2, FUEGO, 10, 4)
        return True

    def dibujar(self, pantalla, encendido):
        obus_x = int(self.x) // 2 * 2
        obus_y = int(self.y) // 2 * 2
        pantalla.fill(ROJO, (obus_x - 8, obus_y - 6, 16, 12))
        pantalla.fill(ROJO, (obus_x - 6, obus_y - 8, 12, 16))
        pantalla.fill((255, 140, 0) if encendido else AMARILLO, (obus_x - 4, obus_y - 4, 8, 8))
        pantalla.fill(BLANCO, (obus_x - 4, obus_y - 4, 4, 4))


class Misil(Bala):
    # Te sigue girando de a poco (se esquiva con una curva cerrada) y el dash lo destruye
    __slots__ = ("guiado", "giro")
    radio = 6
    destruible = True
    puntos = 5

    def __init__(self, x, y, vx, vy, guiado, giro=0.04):
        super().__init__(x, y, vx, vy)
        self.guiado = guiado        # ms que le quedan siguiendote
        self.giro = giro            # radianes por paso que puede corregir el rumbo

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
        pantalla.fill(ROJO, (misil_x - 6, misil_y - 6, 12, 12))
        pantalla.fill(AMARILLO if encendido else BLANCO, (misil_x - 4, misil_y - 4, 8, 8))
        rapidez = math.hypot(self.vx, self.vy) or 1
        punta_x = int(self.x + self.vx / rapidez * 8) // 2 * 2
        punta_y = int(self.y + self.vy / rapidez * 8) // 2 * 2
        pantalla.fill(BLANCO, (punta_x - 2, punta_y - 2, 4, 4))


class Mina(Bala):
    # Viaja frenando hasta quedarse quieta; al rato estalla en una cruz (+ o x) de balas
    __slots__ = ("espera", "rapidez_balas", "forma")
    radio = 8

    def __init__(self, x, y, vx, vy, rapidez_balas, espera, forma="+"):
        super().__init__(x, y, vx, vy)
        self.espera = espera                # ms hasta estallar
        self.rapidez_balas = rapidez_balas
        self.forma = forma

    def mover(self, partida):
        self.x += self.vx
        self.y += self.vy
        self.vx *= 0.95         # se va frenando: recorre 20 veces su velocidad inicial
        self.vy *= 0.95
        self.espera -= MS_POR_FRAME
        if self.espera <= 0:
            self.estallar(partida)
            return False
        return not fuera_de_pantalla(self.x, self.y)

    def estallar(self, partida):
        giro = 0 if self.forma == "+" else math.pi / 4
        for i in range(4):
            direccion = math.pi / 2 * i + giro
            partida.balas.append(Bala(self.x, self.y, math.cos(direccion) * self.rapidez_balas,
                                      math.sin(direccion) * self.rapidez_balas))
        partida.efectos.explosion(self.x, self.y, FUEGO, 16, 4, 3)
        partida.sonidos.reproducir("golpe")

    def dibujar(self, pantalla, encendido):
        # Un cuadrado con pinches en su forma; en el ultimo medio segundo parpadea rapido (aviso)
        mina_x = int(self.x) // 2 * 2
        mina_y = int(self.y) // 2 * 2
        por_estallar = self.espera < 500
        luz = BLANCO if (parpadeo(60) if por_estallar else encendido) else ROJO
        pantalla.fill(MAGENTA, (mina_x - 6, mina_y - 6, 12, 12))
        if self.forma == "+":
            pinches = ((-12, -2), (8, -2), (-2, -12), (-2, 8))
        else:
            pinches = ((-10, -10), (6, -10), (-10, 6), (6, 6))
        for pinche_x, pinche_y in pinches:
            pantalla.fill(MAGENTA, (mina_x + pinche_x, mina_y + pinche_y, 4, 4))
        pantalla.fill(luz, (mina_x - 2, mina_y - 2, 4, 4))


class Escombro(Bala):
    # Un trozo de metal que cae (las cortinas de la Fortaleza)
    __slots__ = ()
    radio = 9

    def mover(self, partida):
        self.x += self.vx
        self.y += self.vy
        return not fuera_de_pantalla(self.x, self.y, 30)

    def dibujar(self, pantalla, encendido):
        escombro_x = int(self.x) // 2 * 2
        escombro_y = int(self.y) // 2 * 2
        pantalla.fill(METAL_OSCURO, (escombro_x - 10, escombro_y - 8, 20, 16))
        pantalla.fill(GRIS_METAL, (escombro_x - 8, escombro_y - 8, 14, 10))
        pantalla.fill(ROJO if encendido else (255, 140, 0), (escombro_x - 10, escombro_y + 6, 20, 2))


class Onda(Bala):
    # Onda de choque a ras del piso (la Fortaleza al caer)
    __slots__ = ()
    radio = 10

    def mover(self, partida):
        self.x += self.vx
        if random.random() < 0.6:
            partida.efectos.particula(self.x, self.y + random.randint(-8, 8), -self.vx * 0.3, -1,
                                      FUEGO, 14, 4)
        return not fuera_de_pantalla(self.x, self.y, 30)

    def dibujar(self, pantalla, encendido):
        onda_x = int(self.x) // 2 * 2
        onda_y = int(self.y) // 2 * 2
        for alto, color in ((20, ROJO), (12, (255, 140, 0)), (6, AMARILLO if encendido else BLANCO)):
            pantalla.fill(color, (onda_x - 4, onda_y - alto // 2, 8, alto))


class Veneno(Bala):
    # Gota lenta que gotea mientras viaja
    __slots__ = ()
    radio = 7

    def mover(self, partida):
        self.x += self.vx
        self.y += self.vy
        if fuera_de_pantalla(self.x, self.y):
            return False
        if random.random() < 0.4:
            partida.efectos.particula(self.x, self.y, 0, 0.6, [(0, 60, 30), (60, 255, 120), (200, 255, 210)], 14, 2)
        return True

    def dibujar(self, pantalla, encendido):
        gota_x = int(self.x) // 2 * 2
        gota_y = int(self.y) // 2 * 2
        pantalla.fill((0, 90, 40), (gota_x - 8, gota_y - 6, 16, 12))
        pantalla.fill((0, 90, 40), (gota_x - 6, gota_y - 8, 12, 16))
        pantalla.fill((60, 255, 120), (gota_x - 6, gota_y - 4, 12, 8))
        pantalla.fill((60, 255, 120), (gota_x - 4, gota_y - 6, 8, 12))
        pantalla.fill(BLANCO if encendido else (200, 255, 210), (gota_x - 4, gota_y - 4, 4, 4))


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
