"""
Los cuadros COMUNES: los que no son de una mision.

    umbral_anio     el mensaje de Ines cada año: la Umbral y la Marea, mas cerca cuanto mas tarde
    rescate         la Alondra se rompio: Ines la remolca de vuelta
    plano           un plano nuevo: la Alondra en azul de plano, con la pieza que se suma
    despejado       un sistema libre despejado: las piezas suben a la Alondra
    puerta_menor    un atajo: un anillo que dobla el espacio
    eco             una transmision vieja que se recupera
    rumbo_*         el mapa de navegacion de un lugar al que sigue (las misiones lo usan al final)
    moneda_*        una moneda blanca con una firma grabada (ALBA, MATEO)

datos: "anios" (siempre), "modulo" y "nivel" (plano), "color" y "piezas" (despejado), "ritmo" (el glifo
del eco).
"""
import math
import random

import pygame

from juego import dibujo, interfaz, nave, recursos
from juego.config import (BLANCO, ROJO, AMARILLO, CIAN, VIOLETA, VERDE, HIELO, NARANJA, TEXTO, TEXTO_SUAVE,
                          LINEA_APAGADA, MAREA_ANIOS)
from juego.historia import modulos
from juego.historia.glifos import escribir
from juego.escenas.historia.cuadros.base import cuadro, NOCHE
from juego.escenas.historia.cuadros import kit
from juego.escenas.historia.cuadros.kit import g, rotulo, mezclar

PLANO = (8, 22, 52)             # el azul de los planos
TINTA = (120, 200, 255)         # las lineas del plano


def hablando(datos, quien):
    return datos.get("quien") == quien


@cuadro("umbral_anio", "ESTACION UMBRAL")
def umbral_anio(pantalla, zona, t, paso, datos):
    # La Umbral y el frente rojo que viene desde la izquierda: llega a la estacion en el año 6
    kit.estrellas(pantalla, zona, 11, 110)
    anios = min(datos.get("anios", 0), MAREA_ANIOS)
    estacion_x = zona.centerx + 160
    borde = zona.left + (estacion_x - 120 - zona.left) * anios / MAREA_ANIOS
    kit.frente_de_la_marea(pantalla, zona, borde, t, hacia="derecha")
    kit.planeta(pantalla, estacion_x - 40, zona.bottom + 150, 210, (70, 120, 170), (20, 34, 70), luz=(0.5, -1), semilla=4)
    caja = kit.estacion(pantalla, estacion_x, zona.centery - 20 + kit.vaiven(t, 300, 2), t, pixel=6)
    if hablando(datos, "ines"):
        kit.ondas(pantalla, caja.centerx, caja.top + 10, t, AMARILLO, hacia=-math.pi / 2, abertura=2.2, alcance=110)
    # Ines, en la ventana de la radio
    kit.retrato(pantalla, "ines", zona.left + 40, zona.bottom - 112, 8, AMARILLO)
    rotulo(pantalla, "AÑO %d" % int(datos.get("anios", 0)), zona.left + 88, zona.bottom - 128, AMARILLO)
    distancia = max(0, (estacion_x - 120 - borde) / (estacion_x - 120 - zona.left))
    if anios < MAREA_ANIOS:
        rotulo(pantalla, "LA MAREA", g(borde) + 40, zona.top + 54, ROJO, alinear="izquierda")
        kit.linea(pantalla, g(borde) + 8, zona.top + 70, caja.left - 8, zona.top + 70, mezclar(ROJO, NOCHE, 0.5),
                  hueco=2, hasta=distancia + 0.01)


@cuadro("rescate", "SEÑAL DE AUXILIO")
def rescate(pantalla, zona, t, paso, datos):
    # La Alondra a la deriva, echando chispas; un remolcador de la Umbral la engancha y se la lleva
    kit.estrellas(pantalla, zona, 12, 90)
    tira = kit.avance(t, 90, 120)
    nave_x = zona.centerx + 120 - tira * 160
    nave_y = zona.centery + 20 + kit.vaiven(t, 160, 4)
    remolque_x, remolque_y = nave_x - 230, zona.centery - 50 + kit.vaiven(t + 40, 160, 2)
    entra = kit.avance(t, 0, 70)
    remolque_x -= (1 - entra) * 300
    # el cable: punteado mientras viaja, firme cuando engancha
    if t > 60:
        kit.linea(pantalla, remolque_x + 20, remolque_y, nave_x - 30, nave_y - 10, AMARILLO,
                  hueco=0 if t > 90 else 3, hasta=kit.avance(t, 60, 30))
    dibujo.pixel_art(pantalla, ["..XXXX..", "XXXXXXXX", "XXooooXX", "XXXXXXXX", "..X..X.."], g(remolque_x),
                     g(remolque_y), (190, 196, 220), 4)
    pantalla.fill(AMARILLO, (g(remolque_x) - 6, g(remolque_y) - 2, 12, 4))
    kit.alondra(pantalla, nave_x, nave_y, t, escala=2, mira="derecha", llama=0)
    chispas = random.Random(t // 6)
    for _ in range(4 if t < 150 else 1):     # chispas de la avería (se calman cuando la remolcan)
        x = nave_x + chispas.randint(-30, 30)
        y = nave_y + chispas.randint(-24, 24)
        pantalla.fill(chispas.choice((NARANJA, AMARILLO, BLANCO)), (g(x), g(y), 2, 2))
    if hablando(datos, "ines"):
        kit.ondas(pantalla, remolque_x, remolque_y - 16, t, AMARILLO, hacia=-math.pi / 2, abertura=2.0, alcance=60)


@cuadro("plano", "EL HANGAR")
def plano(pantalla, zona, t, paso, datos):
    # El plano del modulo: la Alondra en lineas de plano y, encima, la pieza nueva que titila
    pantalla.fill(PLANO, zona)
    for x in range(zona.left, zona.right, 24):
        pantalla.fill(mezclar(PLANO, TINTA, 0.15), (x, zona.top, 2, zona.height))
    for y in range(zona.top, zona.bottom, 24):
        pantalla.fill(mezclar(PLANO, TINTA, 0.15), (zona.left, y, zona.width, 2))
    id_modulo = datos.get("modulo") or modulos.MODULOS[0].id
    modulo = modulos.POR_ID[id_modulo]
    nivel = max(1, min(datos.get("nivel", 1), max(modulo.piezas)))
    previas = [capa for antes in range(1, nivel) for capa in modulo.piezas[antes]]
    sin = nave.armar(previas)
    con = nave.armar(previas + list(modulo.piezas[nivel]))
    escala = 4
    centro_x, centro_y = zona.left + 250, zona.centery + 6
    base = pygame.transform.scale(recursos.tenir(sin, TINTA), (sin.get_width() * escala, sin.get_height() * escala))
    dibujo.pegar(pantalla, base, centro_x, centro_y, centrado=True)
    if kit.titila(t, 50):
        pieza = _diferencia(sin, con, AMARILLO)
        pieza = pygame.transform.scale(pieza, (pieza.get_width() * escala, pieza.get_height() * escala))
        dibujo.pegar(pantalla, pieza, centro_x, centro_y, centrado=True)
    caja = pygame.Rect(centro_x - 110, centro_y - 110, 220, 220)
    interfaz.esquinas(pantalla, caja, TINTA, largo=10, grueso=2)
    # las cotas, como en un plano de verdad
    kit.linea(pantalla, caja.left, caja.bottom + 10, caja.right, caja.bottom + 10, TINTA, hueco=2)
    rotulo(pantalla, "25 M", caja.centerx, caja.bottom + 10, TINTA)
    derecha = zona.left + 470
    rotulo(pantalla, "PLANO NUEVO", derecha, zona.top + 64, TEXTO_SUAVE, alinear="izquierda")
    kit.texto_grande(pantalla, modulo.nombre, AMARILLO, derecha, zona.top + 100, alinear="izquierda")
    rotulo(pantalla, "NIVEL %d" % nivel, derecha, zona.top + 136, TINTA, alinear="izquierda")
    for i, linea in enumerate(modulo.descripcion):
        rotulo(pantalla, linea, derecha, zona.top + 176 + i * 26, TEXTO, alinear="izquierda")
    abre = len(modulos.lo_que_abre(id_modulo, nivel))
    if abre:
        rotulo(pantalla, "ABRE %d %s" % (abre, "LUGAR" if abre == 1 else "LUGARES"), derecha, zona.top + 238,
               VERDE, alinear="izquierda")


def _diferencia(sin, con, color):
    # Los pixeles que cambian de una imagen a la otra, pintados de un color (la pieza nueva)
    pieza = pygame.Surface(con.get_size(), pygame.SRCALPHA)
    for y in range(0, con.get_height(), 2):
        for x in range(0, con.get_width(), 2):
            if con.get_at((x, y)) != sin.get_at((x, y)):
                pieza.fill(color, (x, y, 2, 2))
    return pieza


@cuadro("despejado", "SISTEMA DESPEJADO")
def despejado(pantalla, zona, t, paso, datos):
    # El planeta del sistema y las piezas que suben a la bodega de la Alondra
    color = datos.get("color", CIAN)
    kit.estrellas(pantalla, zona, 13, 100)
    planeta_x, planeta_y = zona.right - 200, zona.centery + 30
    kit.planeta(pantalla, planeta_x, planeta_y, 110, color, mezclar(color, NOCHE, 0.75), semilla=len(str(color)))
    nave_x, nave_y = zona.left + 220, zona.centery - 10 + kit.vaiven(t, 200, 2)
    kit.alondra(pantalla, nave_x, nave_y, t, escala=2, mira="derecha", llama=0.4)
    azar = random.Random(14)
    for i in range(14):
        sale = azar.randint(0, 160)
        dura = azar.randint(70, 110)
        edad = (t - sale) % (dura + 40)
        if t < sale or edad > dura:
            continue
        f = kit.avance(edad, 0, dura)
        x0, y0 = planeta_x - 80 + azar.randint(-20, 20), planeta_y + azar.randint(-80, 60)
        x = x0 + (nave_x + 30 - x0) * f
        y = y0 + (nave_y - y0) * f - math.sin(f * math.pi) * azar.randint(20, 60)
        pantalla.fill((180, 186, 210), (g(x) - 2, g(y) - 2, 6, 4))
        pantalla.fill(AMARILLO, (g(x), g(y), 2, 2))
    if datos.get("piezas"):
        rotulo(pantalla, "+%d PIEZAS" % datos["piezas"], nave_x, nave_y - 70, AMARILLO)


@cuadro("puerta_menor", "PUERTA MENOR")
def puerta_menor(pantalla, zona, t, paso, datos):
    # Un anillo violeta: adentro se ven otras estrellas (las del otro lado)
    kit.estrellas(pantalla, zona, 15, 100)
    cx, cy = zona.centerx + 120, zona.centery
    kit.disco(pantalla, cx, cy, 70, (14, 6, 30), ry=90)
    azar = random.Random(16)
    for _ in range(40):
        a, r = azar.uniform(0, math.tau), azar.random() ** 0.5
        x, y = cx + math.cos(a) * 64 * r, cy + math.sin(a) * 84 * r
        pantalla.fill(mezclar(VIOLETA, BLANCO, azar.random()), (g(x), g(y), 2, 2))
    for i in range(90):
        a = i * math.tau / 90 + t * 0.02
        wobble = math.sin(i * 3 + t / 10) * 3
        x = cx + math.cos(a) * (74 + wobble)
        y = cy + math.sin(a) * (96 + wobble)
        pantalla.fill(VIOLETA if i % 3 else BLANCO, (g(x), g(y), 4, 4))
    dibujo.halo(pantalla, cx, cy, 120, VIOLETA, 0.5)
    llega = kit.avance(t, 20, 160)
    kit.alondra(pantalla, zona.left + 150 + llega * 120, cy, t, escala=2, mira="derecha")


@cuadro("eco", "TRANSMISION RECUPERADA")
def eco(pantalla, zona, t, paso, datos):
    # Una transmision vieja: un osciloscopio con estatica y el compas debajo
    kit.estrellas(pantalla, zona, 17, 70)
    caja = pygame.Rect(zona.left + 120, zona.top + 60, zona.width - 240, zona.height - 110)
    kit.osciloscopio(pantalla, caja, t, datos.get("ritmo") or escribir("ALBA"), VIOLETA)
    azar = random.Random(t // 4)
    for _ in range(60):     # la estatica de una señal vieja
        x, y = azar.randint(caja.left, caja.right - 2), azar.randint(caja.top, caja.bottom - 2)
        gris = azar.choice((40, 70, 110))
        pantalla.fill((gris, gris, gris + 20), (g(x), g(y), 2, 2))
    if kit.titila(t, 60):
        pantalla.fill(ROJO, (caja.right - 30, caja.top + 14, 8, 8))
    rotulo(pantalla, "REC", caja.right - 64, caja.top + 18, ROJO)


# ---------- El mapa de navegacion hacia lo que sigue ----------

def _rumbo(desde, color_desde, hasta, color_hasta):
    def rumbo(pantalla, zona, t, paso, datos):
        # La pantalla de navegacion: los dos lugares, la ruta que se traza y la Alondra que la sigue
        kit.estrellas(pantalla, zona, 18, 70)
        for x in range(zona.left + 40, zona.right, 64):
            pantalla.fill((12, 18, 40), (x, zona.top, 2, zona.height))
        for y in range(zona.top + 32, zona.bottom, 64):
            pantalla.fill((12, 18, 40), (zona.left, y, zona.width, 2))
        x1, y1 = zona.left + 170, zona.centery + 40
        x2, y2 = zona.right - 190, zona.centery - 20
        kit.planeta(pantalla, x1, y1, 30, color_desde, mezclar(color_desde, NOCHE, 0.7), semilla=1)
        kit.planeta(pantalla, x2, y2, 52, color_hasta, mezclar(color_hasta, NOCHE, 0.75), semilla=2)
        dibujo.halo(pantalla, x2, y2, 80, color_hasta, 0.6)
        traza = kit.avance(t, 20, 140)
        kit.linea(pantalla, x1 + 40, y1 - 6, x2 - 64, y2 + 6, AMARILLO, hueco=3, hasta=traza, corrimiento=-t // 4)
        if traza > 0.05:
            f = traza * 0.8
            kit.alondra(pantalla, x1 + 40 + (x2 - 64 - x1 - 40) * f, y1 - 6 + (y2 - y1 + 12) * f - 2, t, escala=1,
                        mira="derecha")
        rotulo(pantalla, desde, x1, y1 + 56, color_desde)
        letras = max(0, (t - 120) // 3)
        if letras:
            rotulo(pantalla, hasta[:letras], x2, y2 + 80, color_hasta)
            interfaz.esquinas(pantalla, pygame.Rect(x2 - 64, y2 - 64, 128, 128), color_hasta, largo=8, grueso=2)
    return rumbo


cuadro("rumbo_nebulosa", "NAVEGACION")(_rumbo("CINTURON EXTERIOR", CIAN, "NEBULOSA CARMESI", ROJO))
cuadro("rumbo_esmeralda", "NAVEGACION")(_rumbo("NEBULOSA CARMESI", ROJO, "CAMPO ESMERALDA", VERDE))
cuadro("rumbo_ambar", "NAVEGACION")(_rumbo("CAMPO ESMERALDA", VERDE, "MAR DE AMBAR", AMARILLO))


# ---------- Las monedas firmadas ----------

def moneda_grande(pantalla, cx, cy, radio, t, palabra, color=(230, 232, 245)):
    # Una moneda grande hecha con codigo: el canto, la cara y el glifo grabado en el medio. Un
    # brillo pasa en diagonal, despacio (no destella)
    cx, cy, radio = g(cx), g(cy), g(radio)
    oscuro, medio = mezclar(color, NOCHE, 0.65), mezclar(color, NOCHE, 0.3)
    kit.disco(pantalla, cx + 6, cy + 4, radio, oscuro)        # el canto (se ve de costado)
    kit.disco(pantalla, cx, cy, radio, medio)
    kit.disco(pantalla, cx, cy, radio - 8, color)
    for grado in range(0, 360, 10):     # el borde granulado
        a = math.radians(grado)
        pantalla.fill(oscuro, (g(cx + math.cos(a) * (radio - 4)), g(cy + math.sin(a) * (radio - 4)), 2, 2))
    brillo = (t * 2) % (radio * 6) - radio * 2      # la franja de luz cruza y despues espera
    for y in range(cy - radio + 8, cy + radio - 8, 2):
        ancho = int(math.sqrt(max(0, (radio - 8) ** 2 - (y - cy) ** 2)))
        x = g(cx + brillo - (y - cy))
        if cx - ancho <= x <= cx + ancho - 6:
            pantalla.fill(BLANCO, (x, y, 6, 2))
    # el glifo grabado, en dos renglones (entero no entra en la cara)
    mitad = (len(palabra) + 1) // 2
    grabado = mezclar(color, (20, 20, 40), 0.75)
    kit.glifo(pantalla, escribir(palabra[:mitad]), cx, cy - 16, grabado)
    kit.glifo(pantalla, escribir(palabra[mitad:]), cx, cy + 16, grabado)


def _moneda_firmada(palabra, color):
    def moneda_firmada(pantalla, zona, t, paso, datos):
        # La moneda blanca, grande, con la firma grabada; al lado, el glifo se escribe de a una letra
        kit.estrellas(pantalla, zona, 19, 80)
        cx, cy = zona.left + 260, zona.centery + 6 + kit.vaiven(t, 240, 4)
        dibujo.halo(pantalla, cx, cy, 120, VIOLETA, 0.35)
        moneda_grande(pantalla, cx, cy, 96, t, palabra)
        glifo = escribir(palabra)
        encendidas = min(len(palabra), max(0, (t - 40) // 30))
        x = zona.left + 640
        kit.glifo(pantalla, glifo, x, zona.centery - 10, VIOLETA, encendidas)
        interfaz.esquinas(pantalla, pygame.Rect(x - 170, zona.centery - 50, 340, 80), mezclar(VIOLETA, NOCHE, 0.4),
                          largo=8, grueso=2)
        rotulo(pantalla, "GRABADO A MANO" if palabra == "MATEO" else "UNA FIRMA", x, zona.centery + 60, TEXTO_SUAVE)
    return moneda_firmada


cuadro("moneda_alba", "LA MONEDA BLANCA")(_moneda_firmada("ALBA", BLANCO))
cuadro("moneda_mateo", "LA OTRA FIRMA")(_moneda_firmada("MATEO", BLANCO))
