"""
Los personajes del modo historia: su nombre, su color y su retrato.

PERSONAJES es lo que se usa en los dialogos: (quien, texto), donde 'quien' es una clave de
aqui ("alba", "ines"...). Los retratos estan dibujados con codigo (pixel art de 12x12 con
varios colores) y se usan en la radio (chicos) y en los dialogos (grandes).

Cada retrato es una lista de renglones: cada letra es un pixel y su color sale de la
paleta del retrato ("." = transparente). Un personaje sin retrato (la Errante) es
estatica de radio. Para sumar un personaje: su nombre y color en PERSONAJES y, si tiene
cara, su dibujo en RETRATOS.

"ultimo" es EL ULTIMO: el que dejo las monedas (HISTORIA.md, "La verdad"). Aparece al final de
la mision 5, viejo y cansado. "voz" es el mismo, joven, en su primera bitacora (la Bitacora sin
fecha): el mismo dibujo sin arrugas y con los colores mas vivos. "cantores" (???) es el compas
cuando "habla" por la radio.
"""
import random

import pygame

from juego.config import CIAN, AMARILLO, GRIS, VIOLETA
from juego.dibujo import en_grilla

# Quien habla: nombre en la caja y color
PERSONAJES = {
    "alba": ("ALBA", CIAN),
    "ines": ("INES CORIA", AMARILLO),
    "errante": ("BITACORA DE LA ERRANTE", GRIS),
    "mateo": ("MATEO SAAVEDRA", GRIS),
    "cantores": ("???", VIOLETA),
    "ultimo": ("EL ULTIMO", VIOLETA),
    "voz": ("SIN FECHA", VIOLETA),
}

RETRATOS = {
    "alba": {       # el casco con el visor
        "dibujo": ["...XXXXXX...",
                   "..XXXXXXXX..",
                   ".XXooooooXX.",
                   ".XovvvvbvoX.",
                   ".XovvvvvvoX.",
                   ".XXooooooXX.",
                   "..XXXXXXXX..",
                   "...XooooX...",
                   "..XXXXXXXX..",
                   ".XXXXooXXXX.",
                   "XXXXXooXXXXX",
                   "XXXXXXXXXXXX"],
        "paleta": {"X": (0, 180, 210), "o": (0, 60, 90), "v": (20, 40, 110), "b": (230, 250, 255)},
    },
    "ines": {       # el pelo recogido, los anteojos y el guardapolvo
        "dibujo": ["....oooo....",
                   "...oooooo...",
                   "..oossssoo..",
                   "..osssssso..",
                   "..svvsvvss..",
                   "..ssssssss..",
                   "...ssmmss...",
                   "....ssss....",
                   "...XXXXXX...",
                   "..XXXyyXXX..",
                   ".XXXXyyXXXX.",
                   "XXXXXyyXXXXX"],
        "paleta": {"o": (110, 70, 20), "s": (240, 200, 160), "v": (255, 221, 0), "m": (150, 60, 60),
                   "X": (225, 225, 235), "y": (255, 221, 0)},
    },
    "mateo": {      # la gorra de capitan, la barba y el uniforme de la Errante (grabado: en gris)
        "dibujo": ["...XXXXXX...",
                   "..XXXXXXXX..",
                   ".vvvvvvvvvv.",
                   "..ssssssss..",
                   "..soossoos..",
                   "..ssssssss..",
                   "..bssmmssb..",
                   "..bbbbbbbb..",
                   "...bbbbbb...",
                   "..uuuyyuuu..",
                   ".uuuuyyuuuu.",
                   "uuuuuyyuuuuu"],
        "paleta": {"X": (60, 70, 100), "v": (30, 34, 50), "s": (200, 180, 160), "o": (40, 40, 50),
                   "m": (120, 70, 70), "b": (110, 90, 70), "u": (120, 126, 140), "y": (190, 190, 200)},
    },
    "cantores": {   # un glifo que late
        "dibujo": ["............",
                   ".....XX.....",
                   "....XooX....",
                   "...XoXXoX...",
                   "..XoX..XoX..",
                   ".XoX.XX.XoX.",
                   ".XoX.XX.XoX.",
                   "..XoX..XoX..",
                   "...XoXXoX...",
                   "....XooX....",
                   ".....XX.....",
                   "............"],
        "paleta": {"X": (190, 120, 255), "o": (70, 30, 120)},
    },
}
RETRATOS["ultimo"] = {      # la capucha, los ojos que brillan, las arrugas y los tentaculos de la barba
    "dibujo": ["....XXXX....",
               "..XXXXXXXX..",
               ".XXssssssXX.",
               ".XssssssssX.",
               ".XsEEssEEsX.",
               ".XssssssssX.",
               ".XswsswswsX.",
               ".XXsttttsXX.",
               "XXX.tttt.XXX",
               "XXXX.tt.XXXX",
               "XXXXX..XXXXX",
               "XXXXXXXXXXXX"],
    "paleta": {"X": (80, 44, 140), "s": (160, 150, 196), "E": (255, 236, 255), "w": (104, 94, 144),
               "t": (128, 110, 180)},
}
# La voz sin fecha: el mismo, millones de años antes (sin arrugas, la barba corta, colores vivos)
RETRATOS["voz"] = {
    "dibujo": [renglon.replace("w", "s") for renglon in RETRATOS["ultimo"]["dibujo"][:8]] +
              ["XXX......XXX", "XXXX....XXXX", "XXXXX..XXXXX", "XXXXXXXXXXXX"],
    "paleta": {"X": (150, 90, 230), "s": (205, 196, 240), "E": (255, 255, 255), "t": (175, 150, 230)},
}
FONDO_RETRATO = (8, 10, 26)


def dibujar_retrato(pantalla, personaje, izquierda, arriba, pixel):
    # El retrato con su recuadro, en la grilla de 2 px; 'pixel' es el lado de cada pixel (par)
    lado = 12 * pixel
    izquierda, arriba = en_grilla(izquierda), en_grilla(arriba)
    pantalla.fill(FONDO_RETRATO, (izquierda, arriba, lado, lado))
    if personaje not in RETRATOS:
        _estatica(pantalla, izquierda, arriba, pixel)
        return
    retrato = RETRATOS[personaje]
    for fila, renglon in enumerate(retrato["dibujo"]):
        for columna, letra in enumerate(renglon):
            color = retrato["paleta"].get(letra)
            if color is not None:
                pantalla.fill(color, (izquierda + columna * pixel, arriba + fila * pixel, pixel, pixel))


def _estatica(pantalla, izquierda, arriba, pixel):
    # Ruido de radio que cambia en cada cuadro (es solo dibujo: usa su propio azar)
    azar = random.Random(pygame.time.get_ticks() // 80)
    for fila in range(12):
        for columna in range(12):
            gris = azar.choice((20, 40, 70, 110, 150))
            pantalla.fill((gris, gris, gris + 10), (izquierda + columna * pixel, arriba + fila * pixel, pixel, pixel))
