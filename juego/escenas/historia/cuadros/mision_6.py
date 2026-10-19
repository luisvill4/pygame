"""
Los cuadros de la MISION 6 (oculta): LOS RESTOS (al borde del Abismo).

    antes:    calculo (las tres bitacoras marcan un punto) → restos_lejos (la Errante, partida en tres)
    despues:  errante_partida (no hay nadie: falta la capsula) → caja_negra (F10: entraron a la
              puerta) → moneda_mateo (F13) → alba_sola (gracias)
"""
import math

import pygame

from juego import dibujo, interfaz
from juego.config import BLANCO, ROJO, AMARILLO, CIAN, HIELO, NARANJA, TEXTO, TEXTO_SUAVE, GRIS
from juego.escenas.historia.cuadros.base import cuadro, NOCHE
from juego.escenas.historia.cuadros import kit
from juego.escenas.historia.cuadros.kit import g, rotulo, mezclar

# Los tres pedazos de la Errante (la proa, el medio con el hueco de la capsula y los motores)
PROA = ["....PPPPP", "..PPPPvPPr", ".PnnnnnnPr", "PPPPPPPPrr", "..PPPPPr.."]
MEDIO = ["rPPPPPPPPr", "rPnnHHnnPr", "rPPPHHPPPr", ".rPPPPPPr."]
MOTORES = ["rPPPP...", "rrPPPPoo", "rPPPPPoo", "rrPPPP..", ".rPP...."]
PALETA = dict(kit.PALETA_CASCO, H=(10, 10, 20), o=(80, 60, 50))


def pedazos(pantalla, cx, cy, t, pixel, separados=1.0):
    # Los tres pedazos a la deriva, cada uno a su ritmo
    for i, (forma, dx, dy) in enumerate(((PROA, -120, -30), (MEDIO, 0, 10), (MOTORES, 120, -10))):
        x = cx + dx * separados + math.sin(t / 90 + i) * 4
        y = cy + dy * separados + math.sin(t / 70 + i * 2) * 4
        kit.pintar(pantalla, forma, PALETA, x, y, pixel)


@cuadro("calculo", "LOS CALCULOS DE INES")
def calculo(pantalla, zona, t, paso, datos):
    # Las tres bitacoras y, en el mapa, tres lineas que se cruzan en un punto: ahi se partio
    kit.estrellas(pantalla, zona, 101, 60)
    for i in range(3):
        x, y = zona.left + 90, zona.top + 60 + i * 64
        pantalla.fill((214, 204, 180), (x, y, 56, 44))
        for renglon in range(4):
            pantalla.fill((120, 110, 90), (x + 6, y + 8 + renglon * 8, 40 - (renglon % 2) * 12, 2))
        rotulo(pantalla, "%d/3" % (i + 1), x + 28, y + 56, TEXTO_SUAVE)
    mapa = pygame.Rect(zona.left + 260, zona.top + 40, zona.width - 320, zona.height - 80)
    for x in range(mapa.left, mapa.right, 40):
        pantalla.fill((12, 18, 40), (x, mapa.top, 2, mapa.height))
    for y in range(mapa.top, mapa.bottom, 40):
        pantalla.fill((12, 18, 40), (mapa.left, y, mapa.width, 2))
    interfaz.esquinas(pantalla, mapa, TEXTO_SUAVE, largo=8, grueso=2)
    punto = (mapa.right - 200, mapa.centery + 10)
    kit.agujero_negro(pantalla, mapa.right - 90, mapa.centery, 14, t)
    for i, (x0, y0) in enumerate(((mapa.left + 20, mapa.top + 20), (mapa.left + 40, mapa.bottom - 20),
                                  (mapa.centerx, mapa.top + 10))):
        kit.linea(pantalla, x0, y0, punto[0], punto[1], CIAN, hueco=2, hasta=kit.avance(t, i * 30, 120))
    if t > 160:
        interfaz.esquinas(pantalla, pygame.Rect(punto[0] - 14, punto[1] - 14, 28, 28), ROJO, largo=6, grueso=2)
        rotulo(pantalla, "AQUI", punto[0], punto[1] - 30, ROJO)


@cuadro("restos_lejos", "AL BORDE DEL ABISMO")
def restos_lejos(pantalla, zona, t, paso, datos):
    # La Errante, partida en tres, a la luz azul del Abismo
    kit.estrellas(pantalla, zona, 102, 90)
    kit.agujero_negro(pantalla, zona.right - 90, zona.centery + 50, 60, t)
    pedazos(pantalla, zona.left + 340, zona.centery - 10, t, 6, separados=1.3)


@cuadro("errante_partida", "LOS RESTOS")
def errante_partida(pantalla, zona, t, paso, datos):
    # De cerca: el hueco donde iba la capsula esta vacio (desde el tercer renglon, marcado)
    kit.estrellas(pantalla, zona, 103, 70)
    cx, cy = zona.centerx, zona.centery + 10
    pedazos(pantalla, cx, cy, t, 8, separados=1.8)
    if paso >= 2:
        hueco_x = cx + math.sin(t / 90 + 1) * 4
        hueco_y = cy + 10 * 1.8 + math.sin(t / 70 + 2) * 4 - 4
        if kit.titila(t, 80):
            interfaz.esquinas(pantalla, pygame.Rect(g(hueco_x) - 24, g(hueco_y) - 20, 48, 40), AMARILLO, largo=6,
                              grueso=2)
        rotulo(pantalla, "LA CAPSULA NO ESTA", cx, zona.bottom - 26, AMARILLO)


@cuadro("caja_negra", "LA CAJA NEGRA")
def caja_negra(pantalla, zona, t, paso, datos):
    # La caja negra suena; al lado, el camino de la capsula: baja hacia el borde y entra
    kit.estrellas(pantalla, zona, 104, 70)
    x, y = zona.left + 180, zona.centery
    pantalla.fill(NARANJA, (x - 50, y - 34, 100, 68))
    pantalla.fill((150, 70, 0), (x - 50, y + 26, 100, 8))
    pantalla.fill((30, 20, 10), (x - 40, y - 24, 80, 20))
    for i in range(0, 76, 4):           # la onda de la voz
        alto = 2 + int(abs(math.sin(i / 7 + t / 6)) * 8) // 2 * 2
        pantalla.fill(AMARILLO, (x - 38 + i, y - 14 - alto // 2, 2, alto))
    if kit.titila(t, 60):
        pantalla.fill(ROJO, (x + 36, y + 8, 6, 6))
    cx, cy = zona.right - 160, zona.centery + 20
    kit.agujero_negro(pantalla, cx, cy, 40, t)
    traza = kit.avance(t, 30, 200)
    kit.linea(pantalla, zona.left + 400, zona.top + 50, cx - 10, cy - 50, mezclar(HIELO, NOCHE, 0.3), hueco=3,
              hasta=traza)
    if traza > 0:
        px = zona.left + 400 + (cx - 10 - zona.left - 400) * traza
        py = zona.top + 50 + (cy - 50 - zona.top - 50) * traza
        kit.capsula(pantalla, px, py, 4, t=t)
    if traza >= 1:
        rotulo(pantalla, "NO ES UN FINAL", cx, zona.bottom - 24, HIELO)
