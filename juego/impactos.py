"""
El impacto de los momentos clave (solo dibujo: la logica esta en la Partida).

- Cuadro de impacto (el golpe final al jefe, como en los juegos de pelea): el juego se
  congela, el mundo se oscurece y desde el golpe salen lineas radiales en el color del jefe,
  con un destello en el centro. Despues la Partida sigue en camara lenta.
- Herida: al perder una vida, una vineta roja en los bordes que se apaga.
- Ultima vida: la vineta queda, suave, y late con el corazon (el sonido "latido").

Con DESTELLOS REDUCIDOS no hay destello blanco de pantalla completa y la vineta no late.
Todo va en bloques de la grilla de pixeles de arte (PIXEL_ARTE), como el resto del juego.
"""
import math
import random

import pygame

from juego import dibujo, accesibilidad
from juego.config import (BLANCO, NEGRO_VELO, IMPACTO_PASOS, IMPACTO_DESTELLO, HERIDA_MS, LATIDO_MS,
                          VINETA_HERIDA, VINETA_ULTIMA_VIDA)

_vinetas = {}           # (tamaño, color) -> la vineta (se arma una vez)


def vineta(tamano, color):
    # Bordes de un color que se apagan hacia el centro, en escalones (sin degradado: retro)
    clave = (tamano, color)
    if clave not in _vinetas:
        ancho, alto = tamano
        capa = pygame.Surface(tamano, pygame.SRCALPHA)
        for i, alfa in enumerate((200, 150, 100, 60, 30)):
            borde = 24 * i
            pygame.draw.rect(capa, color + (alfa,), (borde, borde, ancho - 2 * borde, alto - 2 * borde), 24)
        _vinetas[clave] = capa
    return _vinetas[clave]


def _vineta_con(pantalla, color, fuerza):
    # La vineta con una fuerza de 0 a 1, en 5 escalones (como se apagan las particulas)
    escalon = min(5, math.ceil(fuerza * 5))
    if escalon <= 0:
        return
    capa = vineta(pantalla.get_size(), color)
    capa.set_alpha(escalon * 51)
    pantalla.blit(capa, (0, 0))


# ---------- El golpe final ----------

def nuevo_impacto(x, y, color):
    # Los rayos se sortean una vez (asi no "bailan" de un cuadro al otro)
    azar = random.Random(int(x) * 7919 + int(y))
    rayos = []
    for i in range(28):
        angulo = 2 * math.pi * i / 28 + azar.uniform(-0.06, 0.06)
        rayos.append((angulo, azar.randint(50, 110), azar.randint(180, 620), azar.choice((2, 4))))
    return {"x": x, "y": y, "color": color, "rayos": rayos}


def cuadro_de_impacto(pantalla, partida, impacto, pasos_que_quedan):
    # Dibuja el cuadro de impacto encima del mundo congelado. 'pasos_que_quedan' del hit-stop:
    # los primeros pasos, el destello; despues, el mundo oscuro con el jefe y la nave
    # iluminados encima (los protagonistas del momento) y los rayos que se recogen
    pasados = IMPACTO_PASOS - pasos_que_quedan
    reducidos = accesibilidad.destellos_reducidos()
    if pasados < IMPACTO_DESTELLO and not reducidos:
        dibujo.oscurecer(pantalla, BLANCO, 210 - pasados * 40)
        return
    dibujo.oscurecer(pantalla, NEGRO_VELO, 170)
    if partida.jefe is not None:
        partida.jefe.dibujar(pantalla, partida)
    partida.nave.dibujar(pantalla, partida.tiempo, 0)
    x, y, color = impacto["x"], impacto["y"], impacto["color"]
    encogido = max(0.2, pasos_que_quedan / IMPACTO_PASOS)        # los rayos se recogen hacia el final
    for angulo, desde, largo, grosor in impacto["rayos"]:
        dx, dy = math.cos(angulo), math.sin(angulo)
        for distancia in range(desde, desde + int(largo * encogido), 6):
            bloque_x = dibujo.en_grilla(x + dx * distancia)
            bloque_y = dibujo.en_grilla(y + dy * distancia)
            pantalla.fill(color if distancia > desde + 30 else BLANCO, (bloque_x, bloque_y, grosor, grosor))
    # El centro: un nucleo blanco que se achica
    radio = int(36 * encogido) // 2 * 2
    for bloque_y in range(-radio, radio + 1, 4):
        for bloque_x in range(-radio, radio + 1, 4):
            if bloque_x * bloque_x + bloque_y * bloque_y <= radio * radio:
                pantalla.fill(BLANCO, (dibujo.en_grilla(x + bloque_x), dibujo.en_grilla(y + bloque_y), 4, 4))


# ---------- Herida y ultima vida ----------

def peligro(pantalla, partida):
    # Encima del mundo y debajo del HUD: la herida reciente y, con una vida, el latido
    fuerza = fuerza_de_la_vineta(partida)
    if fuerza > 0:
        _vineta_con(pantalla, VINETA_HERIDA, fuerza)


def fuerza_de_la_vineta(partida):
    # 0 a 1: la herida reciente (se apaga en HERIDA_MS) o, con una vida, el latido
    desde_herida = partida.tiempo - partida.tiempo_herida
    fuerza = 0.0
    if 0 <= desde_herida < HERIDA_MS:
        fuerza = 1 - desde_herida / HERIDA_MS
    if partida.vidas == 1 and partida.vidas_max > 1 and not partida.termino:
        if accesibilidad.destellos_reducidos():
            latido = 0.5                                         # quieta
        else:
            fase = (partida.tiempo % LATIDO_MS) / LATIDO_MS
            latido = 0.35 + 0.65 * (1 - fase) ** 3               # golpe y se apaga, como un corazon
        fuerza = max(fuerza, latido * VINETA_ULTIMA_VIDA)
    return fuerza


def latiendo(partida):
    # ¿La vida que queda esta en el "golpe" del latido? (el HUD la pinta de rojo)
    if partida.vidas != 1 or partida.vidas_max == 1 or accesibilidad.destellos_reducidos():
        return False
    return partida.tiempo % LATIDO_MS < LATIDO_MS * 0.2
