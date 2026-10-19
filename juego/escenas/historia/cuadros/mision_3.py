"""
Los cuadros de la MISION 3: LA DEVORADORA (el Campo Esmeralda).

    antes:    campo_esmeralda (un ladron se lleva una moneda) → niebla (la radio no pasa)
    despues:  radar (todos los ladrones salen hacia el Abismo) → carteros (F05) → clave (F06: cada
              ritmo es una letra) → amanecer (F06 + F01: la firma dice ALBA) → rumbo_ambar
"""
import math
import random

import pygame

from juego import dibujo
from juego.config import BLANCO, AMARILLO, VIOLETA, VERDE, HIELO, TEXTO, TEXTO_SUAVE, NARANJA
from juego.historia.glifos import escribir
from juego.escenas.historia.cuadros.base import cuadro, NOCHE
from juego.escenas.historia.cuadros import kit
from juego.escenas.historia.cuadros.kit import g, rotulo, mezclar
from juego.escenas.historia.cuadros.mision_2 import glifo_grande

ESPORAS = [(200, 255, 210), (90, 220, 140), (30, 120, 80), (12, 50, 36)]


@cuadro("campo_esmeralda", "CAMPO ESMERALDA")
def campo_esmeralda(pantalla, zona, t, paso, datos):
    # Las esporas, las monedas que flotan y un ladron que pasa, agarra una y se va con ella
    kit.estrellas(pantalla, zona, 51, 60)
    kit.nebulosa(pantalla, zona, 52, ESPORAS, t, puntos=1000, deriva=0.08)
    vuelta = t % 300
    robada = 2
    for i, (fx, fy) in enumerate(((0.2, 0.6), (0.38, 0.35), (0.55, 0.62), (0.72, 0.38), (0.86, 0.66))):
        x = zona.left + zona.width * fx
        y = zona.top + zona.height * fy + kit.vaiven(t + i * 40, 160, 4)
        if i == robada and vuelta > 120:
            continue
        kit.moneda(pantalla, x, y, t + i * 9, escala=2)
    # el ladron: entra desde arriba, baja a la moneda, la agarra y se va por la derecha
    destino_x = zona.left + zona.width * 0.55
    destino_y = zona.top + zona.height * 0.62
    if vuelta < 120:
        f = kit.avance(vuelta, 0, 120)
        x, y = destino_x - 200 + 200 * f, zona.top - 30 + (destino_y - 20 - zona.top + 30) * f
    else:
        f = kit.avance(vuelta, 120, 140)
        x, y = destino_x + (zona.right + 60 - destino_x) * f, destino_y - 20 - 60 * f
    kit.enemigo(pantalla, "ladron", x, y, t)
    if vuelta > 120:
        kit.moneda(pantalla, x, y - 30, t)


@cuadro("niebla", "CAMPO ESMERALDA")
def niebla(pantalla, zona, t, paso, datos):
    # La niebla de esporas tapa todo. La radio llega desde la izquierda y se corta donde empieza
    # la niebla: del otro lado solo hay estatica
    kit.estrellas(pantalla, zona, 53, 50)
    corte = zona.left + 300
    nave_x, nave_y = zona.right - 240, zona.centery + kit.vaiven(t, 160, 4)
    kit.alondra(pantalla, nave_x, nave_y, t, escala=2, mira="derecha", llama=0.5)
    color = AMARILLO if datos.get("quien") == "ines" else mezclar(AMARILLO, NOCHE, 0.4)
    kit.linea(pantalla, zona.left, zona.centery - 60, corte, zona.centery - 30, color, hueco=2, corrimiento=-t // 3)
    azar = random.Random(t // 4)
    for _ in range(40):         # la estatica del otro lado
        x = corte + azar.randint(0, nave_x - corte - 40)
        y = zona.centery - 30 + (x - corte) * 0.1 + azar.randint(-10, 10)
        pantalla.fill(mezclar(AMARILLO, NOCHE, 0.6), (g(x), g(y), 2, 2))
    kit.niebla(pantalla, zona, t, (60, 150, 100), densidad=0.6, semilla=54)
    kit.niebla(pantalla, zona, t + 400, (30, 90, 60), densidad=0.7, semilla=55)
    rotulo(pantalla, "SIN SEÑAL", corte + 90, zona.top + 54, (60, 150, 100))


@cuadro("radar", "RADAR DE LA UMBRAL")
def radar(pantalla, zona, t, paso, datos):
    # Un radar que barre: los puntos violetas (los ladrones) aparecen al pasar la linea y todos
    # van hacia el mismo borde, el del Abismo
    cx, cy, radio = zona.left + 300, zona.centery + 4, 116
    for r in (radio, radio * 2 // 3, radio // 3):
        for grado in range(0, 360, 3 if r == radio else 6):
            a = math.radians(grado)
            pantalla.fill((20, 70, 50), (g(cx + math.cos(a) * r), g(cy + math.sin(a) * r), 2, 2))
    pantalla.fill((20, 70, 50), (g(cx - radio), g(cy), radio * 2, 2))
    pantalla.fill((20, 70, 50), (g(cx), g(cy - radio), 2, radio * 2))
    barrido = t * 0.035
    for atras in range(0, 24, 3):           # la linea y su estela, que se apaga
        a = barrido - atras * 0.03
        color = mezclar(VERDE, NOCHE, atras / 26)
        kit.linea(pantalla, cx, cy, cx + math.cos(a) * radio, cy + math.sin(a) * radio, color)
    azar = random.Random(56)
    for i in range(9):
        a0, r0 = azar.uniform(0, math.tau), azar.uniform(0.3, 0.95) * radio
        x0, y0 = cx + math.cos(a0) * r0, cy + math.sin(a0) * r0
        avance_x = (t * 0.25 + i * 30) % (radio * 1.6)
        x, y = x0 + avance_x, y0 + (cy - y0) * avance_x / (radio * 2)
        if math.hypot(x - cx, y - cy) > radio:
            continue
        angulo = math.atan2(y - cy, x - cx)
        desde_barrido = (barrido - angulo) % math.tau
        if desde_barrido < 2.5:
            brillo = 1 - desde_barrido / 2.5
            pantalla.fill(mezclar(VIOLETA, NOCHE, 1 - brillo), (g(x) - 2, g(y) - 2, 6, 6))
    # a la derecha, hacia donde van: el Abismo
    flecha_x = zona.left + 520
    kit.linea(pantalla, cx + radio + 16, cy, flecha_x + 200, cy, mezclar(HIELO, NOCHE, 0.4), hueco=3, corrimiento=-t // 4)
    kit.agujero_negro(pantalla, zona.right - 130, cy, 22, t)
    rotulo(pantalla, "ABISMO AZUL", zona.right - 130, cy + 70, HIELO)


@cuadro("carteros", "EL CARTERO")
def carteros(pantalla, zona, t, paso, datos):
    # El ladron no huye: lleva la moneda con cuidado hacia el Abismo, como quien vuelve a casa
    kit.estrellas(pantalla, zona, 57, 90)
    casa_x = zona.right - 140
    kit.agujero_negro(pantalla, casa_x, zona.centery + 10, 20, t)
    kit.glifo(pantalla, escribir("CASA"), casa_x, zona.top + 60, VIOLETA)
    rotulo(pantalla, "CASA", casa_x, zona.top + 90, AMARILLO)
    x = zona.left + 120 + (t * 0.7) % (zona.width - 360)
    y = zona.centery + 20 + math.sin(t / 30) * 10
    kit.linea(pantalla, x + 50, y, casa_x - 50, zona.centery + 10, mezclar(VIOLETA, NOCHE, 0.6), hueco=3,
              corrimiento=-t // 4)
    kit.enemigo(pantalla, "ladron", x, y, t, escala=2)
    kit.moneda(pantalla, x, y - 52, t)


@cuadro("clave", "LA CLAVE DEL COMPAS")
def clave(pantalla, zona, t, paso, datos):
    # Cada ritmo es una letra: los glifos de ALBA, uno por columna, y debajo la letra que se
    # descifra cuando la linea de lectura pasa por encima
    kit.estrellas(pantalla, zona, 58, 50)
    palabra = "ALBA"
    lectura = (t * 1.6) % (zona.width + 200) - 100
    columnas = [zona.left + zona.width * (i + 1) / (len(palabra) + 1) for i in range(len(palabra))]
    for letra, x in zip(palabra, columnas):
        kit.glifo(pantalla, escribir(letra), x, zona.centery - 40, VIOLETA)
        leida = zona.left + lectura > x or t > zona.width / 1.6
        if leida:
            kit.texto_grande(pantalla, letra, AMARILLO, x, zona.centery + 30, escala=3)
        else:
            rotulo(pantalla, "?", x, zona.centery + 30, TEXTO_SUAVE)
    if t < zona.width / 1.6:
        pantalla.fill(mezclar(VIOLETA, NOCHE, 0.3), (g(zona.left + lectura), zona.top + 40, 2, zona.height - 80))
    if paso >= 1:
        rotulo(pantalla, "CORTO . LARGO -", zona.centerx, zona.bottom - 30, TEXTO_SUAVE)


@cuadro("amanecer", "ALBA")
def amanecer(pantalla, zona, t, paso, datos):
    # Un amanecer sobre el borde de un planeta: el cielo se tiñe de abajo hacia arriba. Arriba,
    # la firma de la moneda, traducida: ALBA (tambien quiere decir amanecer)
    sube = kit.avance(t, 0, 300) * (1 if paso < 2 else 1.4)
    horizonte = zona.bottom - 60
    for i, color in enumerate(((60, 20, 60), (140, 50, 60), (230, 120, 60), (255, 200, 120))):
        alto = g((140 - i * 32) * min(1.2, sube))
        if alto > 0:        # cada franja de color, con un borde tramado que la funde con la de arriba
            pantalla.fill(color, (zona.left, horizonte - alto + 6, zona.width, alto - 6))
            kit.tramado(pantalla, pygame.Rect(zona.left, horizonte - alto, zona.width, 6), color, fase=i)
    sol_y = horizonte + 30 - sube * 60
    kit.disco(pantalla, zona.centerx, sol_y, 40, (255, 230, 170))
    dibujo.halo(pantalla, zona.centerx, sol_y, 120, NARANJA)
    kit.disco(pantalla, zona.centerx, horizonte + 600, 760, (10, 16, 30), ry=600)
    pantalla.fill((255, 220, 160), (zona.left, horizonte, zona.width, 2))
    kit.estrellas(pantalla, pygame.Rect(zona.left, zona.top, zona.width, 80), 59, 40)
    glifo_grande(pantalla, "ALBA", zona.centerx, zona.top + 60, VIOLETA, traducidas=min(4, max(0, (t - 40) // 30)))
