"""
Reliquias: las cosas escondidas del modo historia que guardan un fragmento del Archivo.

No llevan cartel ni brillan de mas: hay que darse cuenta de que estan (HISTORIA.md,
"Reglas para escribir un secreto"). Cada una guarda que fragmento esconde, tiene x/y (se
dibuja interpolada), sabe si la tocaste (tocada) y si ya se fue (termino). Las sueltan los
secretos (secretos.py) y el ModoHistoria (modo.py) las mueve y avisa cuando las encuentras.
Para una nueva: una clase con fragmento, x, y, caja(), tocada(), termino(), mover() y dibujar().

    MonedaGrabada   una moneda distinta: gira lento, tiene un glifo y se apaga si no la recoges
    Restos          los restos de una nave, apagados como el fondo: solo el dash los abre
    Baliza          una baliza de emergencia que titila un glifo a ritmo: tambien con el dash
"""
import math

import pygame

from juego import dibujo, recursos
from juego.config import ANCHO, MONEDA_GRABADA_DURA, RESTOS_VELOCIDAD, MS_CUADRO_MONEDA, BALIZA_VELOCIDAD, BALIZA_UNIDAD
from juego.moneda import imagen_moneda, TAMANO as TAMANO_MONEDA
from juego.historia.glifos import sonando


class MonedaGrabada:
    def __init__(self, fragmento, x, y, ahora):
        self.fragmento = fragmento
        self.x, self.y = x, y
        self.hasta = ahora + MONEDA_GRABADA_DURA

    def caja(self):
        return pygame.Rect(int(self.x), int(self.y), TAMANO_MONEDA, TAMANO_MONEDA)

    def tocada(self, partida):
        return partida.nave.caja_recoger().colliderect(self.caja())

    def termino(self, partida):
        return partida.tiempo >= self.hasta

    def mover(self, partida):
        # Flota apenas, como si respirara (no se escapa: se apaga)
        self.y += math.sin(partida.tiempo / 400) * 0.2

    def dibujar(self, pantalla, partida):
        # Blanca y lenta (las monedas comunes giran rapido y son doradas). Los ultimos 2 s parpadea
        restante = self.hasta - partida.tiempo
        if restante < 2000 and not dibujo.parpadeo(150):
            return
        cuadro = _moneda_palida()
        dibujo.pegar(pantalla, cuadro, self.x, self.y)
        # El glifo: un rombo pequeño y una raya, oscuros, en el medio de la moneda
        centro_x, centro_y = dibujo.en_grilla(self.x + 10), dibujo.en_grilla(self.y + 10)
        pantalla.fill((60, 60, 90), (centro_x - 4, centro_y - 2, 2, 4))
        pantalla.fill((60, 60, 90), (centro_x, centro_y - 2, 4, 2))


_palidas = []


def _moneda_palida():
    # La moneda en tonos de blanco frio (recursos.tenir) y girando cuatro veces mas lento
    if not _palidas:
        cuadros = recursos.hoja("moneda_giro.png", TAMANO_MONEDA) or [imagen_moneda()]
        _palidas.extend(recursos.tenir(cuadro, (200, 210, 255)) for cuadro in cuadros)
    return recursos.cuadro_animado(_palidas, MS_CUADRO_MONEDA * 4)


# Los restos: un casco partido de 40x14 pixeles de arte (cada uno de 2x2), en tonos del fondo
CASCO = [
    "......XXXXXXXXXX.........XXXX..........",
    "....XXooooooooooXX.....XXooooXX........",
    "...XoooooXXXXooooXX...XooooooooX.......",
    "..XoooooX....XooooX..XooooXXooooX......",
    ".XoooooX.vv...XoooXXXoooooX..XooX......",
    "XooooooX.vv....XoooooooooX....XoX..XX..",
    "XoooooooX......XooooooooX......X..XooX.",
    "XooooooooXXXXXXoooooooXX.........XoooX.",
    ".XoooooooooooooooooXXX...........XooX..",
    "..XXoooooooooooooXX...............XX...",
    "....XXXXooooooXXX......................",
    "........XXXXXX.........................",
]
CASCO = [renglon.ljust(40, ".") for renglon in CASCO]      # (todos del mismo largo)


class Restos:
    def __init__(self, fragmento):
        # Cruzan la pantalla despacio, de izquierda a derecha, por la mitad de arriba
        self.fragmento = fragmento
        self.x = -len(CASCO[0]) * 2
        self.y = 170
        self.abiertos = False

    def caja(self):
        return pygame.Rect(int(self.x), int(self.y), len(CASCO[0]) * 2, len(CASCO) * 2)

    def tocada(self, partida):
        # Solo el dash los abre (pasar por encima no hace nada: parecen parte del fondo)
        nave = partida.nave
        return nave.en_dash(partida.tiempo) and nave.caja_recoger().colliderect(self.caja())

    def termino(self, partida):
        return self.x > ANCHO

    def mover(self, partida):
        self.x += RESTOS_VELOCIDAD

    def dibujar(self, pantalla, partida):
        # Colores apagados (ningun canal arriba de ~110, como el fondo): no se nota que se puede tocar.
        # La luz de la cabina ('v') titila de vez en cuando: lo unico vivo que queda
        colores = {"X": (70, 74, 96), "o": (34, 36, 56),
                   "v": (110, 90, 40) if pygame.time.get_ticks() % 2600 < 160 else (40, 38, 50)}
        izquierda, arriba = dibujo.en_grilla(self.x), dibujo.en_grilla(self.y)
        for fila, renglon in enumerate(CASCO):
            for columna, letra in enumerate(renglon):
                if letra in colores:
                    pantalla.fill(colores[letra], (izquierda + columna * 2, arriba + fila * 2, 2, 2))


# La baliza: un cilindro con antena, de 9x12 pixeles de arte. 'L' es la luz que titila
BALIZA = [
    "....X....",
    "....X....",
    "...XLX...",
    "..XXXXX..",
    ".XoooooX.",
    ".XoXXXoX.",
    ".XoooooX.",
    ".XoXXXoX.",
    ".XoooooX.",
    "..XXXXX..",
    "...X.X...",
    "..X...X..",
]


class Baliza:
    def __init__(self, fragmento, glifo):
        # Cruza de derecha a izquierda por la mitad de abajo, mas despacio que los restos
        self.fragmento = fragmento
        self.glifo = glifo              # lo que titila (el mensaje, en el ritmo de El Ultimo)
        self.x = ANCHO
        self.y = 380

    def caja(self):
        # (un poco mas grande que el dibujo: es pequeña y hay que acertarle con el dash)
        return pygame.Rect(int(self.x) - 8, int(self.y) - 8, len(BALIZA[0]) * 2 + 16, len(BALIZA) * 2 + 16)

    def tocada(self, partida):
        nave = partida.nave
        return nave.en_dash(partida.tiempo) and nave.caja_recoger().colliderect(self.caja())

    def termino(self, partida):
        return self.x < -len(BALIZA[0]) * 2

    def mover(self, partida):
        self.x -= BALIZA_VELOCIDAD
        self.y += math.sin(partida.tiempo / 700) * 0.15

    def dibujar(self, pantalla, partida):
        # Apagada como el fondo; solo la luz titila el glifo (con el reloj real: es dibujo)
        encendida = sonando(self.glifo, BALIZA_UNIDAD, pygame.time.get_ticks())
        colores = {"X": (70, 74, 96), "o": (34, 36, 56), "L": (110, 90, 40) if encendida else (40, 38, 50)}
        izquierda, arriba = dibujo.en_grilla(self.x), dibujo.en_grilla(self.y)
        for fila, renglon in enumerate(BALIZA):
            for columna, letra in enumerate(renglon):
                if letra in colores:
                    pantalla.fill(colores[letra], (izquierda + columna * 2, arriba + fila * 2, 2, 2))
