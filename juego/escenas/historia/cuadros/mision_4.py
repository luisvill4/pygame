"""
Los cuadros de la MISION 4: LA COLMENA (el Mar de Ambar).

    antes:    panal (una pared de celdas con inscripciones: una biblioteca)
    despues:  mensaje_entero (SIGUE LAS MONEDAS y la firma; con la clave, traducida) → abismo (el
              compas sale de un agujero negro) → eco_mateo (F07) → poema (F08: dice YO)
"""
import math
import random

import pygame

from juego import dibujo, recursos
from juego.config import BLANCO, AMARILLO, VIOLETA, HIELO, TEXTO, TEXTO_SUAVE, GRIS, ROJO
from juego.historia.glifos import escribir
from juego.escenas.historia.cuadros.base import cuadro, NOCHE
from juego.escenas.historia.cuadros import kit
from juego.escenas.historia.cuadros.kit import g, rotulo, mezclar
from juego.escenas.historia.cuadros.mision_2 import glifo_grande

AMBAR, AMBAR_OSCURO, CERA = (255, 190, 60), (120, 70, 10), (60, 34, 6)
CELDA = ["...XXXXXX...",
         "..XooooooX..",
         ".XooooooooX.",
         "XooooooooooX",
         "XooooooooooX",
         ".XooooooooX.",
         "..XooooooX..",
         "...XXXXXX..."]


def celda(pantalla, x, y, pixel, borde, adentro):
    kit.pintar(pantalla, CELDA, {"X": borde, "o": adentro}, x, y, pixel)


_paredes = {}


def celdas_de_la_pared(zona):
    # Donde va cada celda y su inscripcion (rayitas y puntos): siempre las mismas
    azar = random.Random(61)
    ancho, alto = 12 * 4, 8 * 4
    lugares = []
    for fila in range(-1, zona.height // (alto - 8) + 2):
        for columna in range(-1, zona.width // ancho + 2):
            x = zona.left + columna * (ancho + 8) + (fila % 2) * (ancho // 2 + 4)
            y = zona.top + fila * (alto - 8)
            marcas = [azar.choice((2, 2, 6)) for _ in range(azar.randint(1, 3))]
            lugares.append((x, y, marcas))
    return lugares


def dibujar_celda(pantalla, x, y, marcas, encendida):
    celda(pantalla, x, y, 4, AMBAR if encendida else AMBAR_OSCURO,
          mezclar(AMBAR, CERA, 0.4) if encendida else (90, 54, 10))
    for m, largo in enumerate(marcas):
        pantalla.fill(BLANCO if encendida else CERA, (g(x) - 8 + m * 8, g(y) - 2, largo, 2))


@cuadro("panal", "MAR DE AMBAR")
def panal(pantalla, zona, t, paso, datos):
    # Una pared de celdas (una colmena del tamaño de un sistema solar). Cada celda tiene grabado un
    # pedacito de glifo; una luz recorre la pared como quien lee. Pasan abejas. (La pared quieta
    # se arma una vez y se guarda: son cientos de celdas)
    clave = tuple(zona)
    if clave not in _paredes:
        pared = pygame.Surface(zona.size)
        pared.fill(CERA)
        lugares = celdas_de_la_pared(zona)
        for x, y, marcas in lugares:
            dibujar_celda(pared, x - zona.left, y - zona.top, marcas, False)
        _paredes[clave] = (pared, lugares)
    pared, lugares = _paredes[clave]
    pantalla.blit(pared, zona.topleft)
    leyendo = (t // 4) % 60
    for i, (x, y, marcas) in enumerate(lugares):
        if i % 60 == leyendo:
            dibujar_celda(pantalla, x, y, marcas, True)
    for i in range(5):          # abejas en ochos
        a = t * 0.02 + i * 1.3
        x = zona.centerx + math.sin(a) * (220 + i * 40)
        y = zona.centery + math.sin(a * 2) * 60 + (i - 2) * 24
        kit.enemigo(pantalla, "abeja", x, y, t + i * 5, escala=2, rapidez=4)


@cuadro("mensaje_entero", "EL COMPAS, ENTERO")
def mensaje_entero(pantalla, zona, t, paso, datos):
    # Las tres palabras del compas en glifos. Con el tercer renglon ("SIGUE LAS MONEDAS") se
    # traducen; con el cuarto aparece la firma (traducida solo con la clave: F06)
    kit.estrellas(pantalla, zona, 62, 60)
    traducir = paso >= 2
    palabras = ["SIGUE", "LAS", "MONEDAS"]
    for i, palabra in enumerate(palabras):
        y = zona.top + 58 + i * 52
        color = VIOLETA if not traducir else mezclar(VIOLETA, BLANCO, 0.3)
        kit.glifo(pantalla, escribir(palabra), zona.left + 300, y, color)
        if traducir:
            letras = max(0, (t - 20) // 4 - i * 8)
            if letras:
                kit.texto_grande(pantalla, palabra[:letras], AMARILLO, zona.left + 560, y + 2, alinear="izquierda")
    if paso >= 3:
        y = zona.bottom - 40
        pantalla.fill(mezclar(VIOLETA, NOCHE, 0.6), (zona.left + 120, y - 24, zona.width - 240, 2))
        kit.glifo(pantalla, escribir("ALBA"), zona.left + 300, y, VIOLETA)
        firma = "ALBA" if "F06" in datos.get("encontrados", ()) else "????"
        kit.texto_grande(pantalla, firma, VIOLETA, zona.left + 560, y + 2, alinear="izquierda")


@cuadro("abismo", "ABISMO AZUL")
def abismo(pantalla, zona, t, paso, datos):
    # El compas no sale de la Marea: sale del borde de un agujero negro
    kit.estrellas(pantalla, zona, 63, 120)
    cx, cy = zona.centerx + 60, zona.centery + 10
    kit.agujero_negro(pantalla, cx, cy, 46, t)
    kit.ondas(pantalla, cx, cy - 50, t, VIOLETA, hacia=-math.pi / 2, abertura=math.tau, alcance=180, cuantas=3,
              periodo=90)
    rotulo(pantalla, "EL COMPAS SALE DE AQUI", cx, zona.bottom - 24, VIOLETA)


@cuadro("eco_mateo", "LA ULTIMA TRANSMISION")
def eco_mateo(pantalla, zona, t, paso, datos):
    # La voz de Mateo, de hace años: su retrato entre la estatica y lo que dice, escrito
    kit.estrellas(pantalla, zona, 64, 40)
    x, y = zona.left + 60, zona.top + 56
    kit.retrato(pantalla, "mateo", x, y, 12, GRIS)
    azar = random.Random(t // 5)
    for _ in range(70):         # la estatica encima del retrato
        px, py = x + azar.randrange(0, 144, 2), y + azar.randrange(0, 144, 2)
        gris = azar.choice((30, 60, 100, 160))
        pantalla.fill((gris, gris, gris), (px, py, 4, 2))
    frase = "...ES UNO SOLO... SE LLAMA ALBA..."
    letras = max(0, (t - 20) // 3)
    izquierda = zona.left + 260
    caja = pygame.Rect(izquierda, zona.top + 90, 600, 40)
    escrito = frase[:letras]
    dibujo.texto(pantalla, escrito, dibujo.CHICA, TEXTO, izquierda, caja.centery, alinear="izquierda",
                 contorno=kit.CONTORNO)
    if letras >= len(frase):       # el nombre, resaltado
        antes = frase.index("ALBA")
        x_alba = izquierda + recursos.fuente(dibujo.CHICA).size(frase[:antes])[0]
        dibujo.texto(pantalla, "ALBA", dibujo.CHICA, AMARILLO, x_alba, caja.centery, alinear="izquierda",
                     contorno=kit.CONTORNO)
    kit.osciloscopio(pantalla, pygame.Rect(izquierda, zona.top + 140, 600, 70), t, escribir("ALBA"), GRIS)
    rotulo(pantalla, "HACE AÑOS", izquierda, zona.top + 54, ROJO, alinear="izquierda")


@cuadro("poema", "LA CELDA")
def poema(pantalla, zona, t, paso, datos):
    # Una sola celda encendida en la pared oscura; adentro, una silueta con capucha. Dice YO
    pantalla.fill((30, 18, 4), zona)
    for fila in range(-1, 8):
        for columna in range(-1, 14):
            x = zona.left + columna * 76 + (fila % 2) * 38
            y = zona.top + fila * 40
            celda(pantalla, x, y, 6, (60, 36, 8), (40, 24, 4))
    cx, cy = zona.left + 300, zona.centery
    celda(pantalla, cx, cy, 16, AMBAR, mezclar(AMBAR, (40, 24, 4), 0.55))
    dibujo.halo(pantalla, cx, cy, 120, AMBAR, 0.5)
    silueta = kit.RETRATO_ULTIMO_SILUETA
    kit.pintar(pantalla, silueta, {"X": (60, 30, 10)}, cx, cy + 6, 6)
    if kit.titila(t, 120):
        pantalla.fill(AMBAR, (g(cx) - 16, g(cy) - 10, 6, 6))
        pantalla.fill(AMBAR, (g(cx) + 10, g(cy) - 10, 6, 6))
    kit.texto_grande(pantalla, "YO", AMBAR, zona.left + 640, zona.centery - 20, escala=4)
    kit.glifo(pantalla, escribir("OTRA"), zona.left + 640, zona.centery + 50, VIOLETA)
