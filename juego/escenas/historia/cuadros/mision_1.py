"""
Los cuadros de la MISION 1: LA SEÑAL (el Cinturon Exterior y el Ojo).

    antes:    umbral_muelle (la Alondra amarrada bajo la Umbral) → cinturon (las monedas entre
              las rocas; con el segundo renglon laten con el compas) → despegue
    despues:  ojo_vencido (la lente apagada, que mira mas alla, y el compas con una nota nueva)
              → rumbo_nebulosa → moneda_alba (F01) → bitacora (F02) → rastro_errante
"""
import math
import random

import pygame

from juego import dibujo, interfaz
from juego.config import BLANCO, ROJO, AMARILLO, CIAN, VIOLETA, TEXTO, TEXTO_SUAVE, GRIS
from juego.historia.glifos import escribir, sonando
from juego.escenas.historia.cuadros.base import cuadro, NOCHE
from juego.escenas.historia.cuadros import kit
from juego.escenas.historia.cuadros.kit import g, rotulo, mezclar

ROCA_CLARA, ROCA_OSCURA = (150, 140, 150), (50, 44, 60)


def roca(pantalla, x, y, radio, semilla, apagada=0.0):
    # Un asteroide: un planetita gris con manchas (sale del cache del kit)
    claro, oscuro = ROCA_CLARA, ROCA_OSCURA
    if apagada:
        claro, oscuro = mezclar(claro, NOCHE, apagada), mezclar(oscuro, NOCHE, apagada)
    kit.planeta(pantalla, x, y, radio, claro, oscuro, semilla=semilla)


@cuadro("umbral_muelle", "ESTACION UMBRAL")
def umbral_muelle(pantalla, zona, t, paso, datos):
    # La Umbral sobre su planeta, la Alondra amarrada abajo y, a lo lejos, el resplandor rojo
    kit.estrellas(pantalla, zona, 21, 120)
    kit.nube(pantalla, zona.right - 80, zona.top + 50, 36, [mezclar(c, NOCHE, 0.45) for c in kit.MAREA], 22, 180)
    rotulo(pantalla, "LA MAREA", zona.right - 24, zona.top + 96, mezclar(ROJO, NOCHE, 0.2), alinear="derecha")
    kit.planeta(pantalla, zona.left + 200, zona.bottom + 250, 320, (60, 120, 200), (14, 26, 70), luz=(0.7, -1),
                semilla=7, tierra=(70, 150, 90))
    cx, cy = zona.centerx + 90, zona.centery - 18 + kit.vaiven(t, 360, 2)
    caja = kit.estacion(pantalla, cx, cy, t, pixel=5)
    # el brazo del muelle y la Alondra colgada de el
    pantalla.fill((90, 96, 130), (g(cx) - 2, caja.bottom, 4, 14))
    pantalla.fill(AMARILLO if kit.titila(t, 80) else (120, 100, 20), (g(cx) - 4, caja.bottom + 12, 8, 4))
    kit.alondra(pantalla, cx, caja.bottom + 42, t, escala=1, llama=0)
    if datos.get("quien") == "ines":
        kit.ondas(pantalla, cx, caja.top - 30, t, AMARILLO, hacia=-math.pi / 2, abertura=2.4, alcance=90)
    elif datos.get("quien") == "alba":
        kit.ondas(pantalla, cx, caja.bottom + 60, t, CIAN, hacia=math.pi / 2, abertura=1.6, alcance=40, periodo=40)


@cuadro("cinturon", "CINTURON EXTERIOR")
def cinturon(pantalla, zona, t, paso, datos):
    # Rocas a tres distancias (las cercanas pasan mas rapido) y monedas que flotan entre ellas.
    # Desde el segundo renglon, las monedas laten con el compas: cada pulso enciende la siguiente
    kit.estrellas(pantalla, zona, 23, 100, deriva=0.1, t=t)
    azar = random.Random(24)
    for capa, (cuantas, radios, rapidez, apagada) in enumerate(((9, (6, 10), 0.15, 0.6), (6, (12, 20), 0.35, 0.3),
                                                                (3, (26, 40), 0.7, 0.0))):
        for i in range(cuantas):
            x0 = azar.randint(0, zona.width + 200)
            y = zona.top + azar.randint(20, zona.height - 20)
            x = zona.left - 100 + (x0 - t * rapidez) % (zona.width + 200)
            roca(pantalla, x, y, azar.randint(*radios), capa * 10 + i % 4, apagada)
        if capa == 1:       # las monedas van entre las rocas de atras y las de adelante
            _monedas_del_cinturon(pantalla, zona, t, paso)


def _monedas_del_cinturon(pantalla, zona, t, paso):
    lugares = [(0.18, 0.62), (0.32, 0.30), (0.47, 0.68), (0.60, 0.40), (0.74, 0.70), (0.86, 0.34)]
    pulsos = 0
    if paso >= 1:
        pulsos = sum(1 for momento in range(0, t, 6) if sonando(escribir("ALBA"), 6, momento)
                     and not sonando(escribir("ALBA"), 6, momento - 6))
    for i, (fx, fy) in enumerate(lugares):
        x = zona.left + zona.width * fx
        y = zona.top + zona.height * fy + kit.vaiven(t + i * 30, 150, 4)
        if paso >= 1 and pulsos % len(lugares) == i and sonando(escribir("ALBA"), 6, t):
            dibujo.halo(pantalla, x, y, 30, VIOLETA)
            kit.ondas(pantalla, x, y, t, VIOLETA, abertura=math.tau, cuantas=1, periodo=24, alcance=24)
        kit.moneda(pantalla, x, y, t + i * 7, escala=2)


@cuadro("despegue")
def despegue(pantalla, zona, t, paso, datos):
    # La Alondra sale: la Umbral queda atras y las estrellas se estiran
    rapidez = 2 + kit.avance(t, 10, 120) * 10
    kit.estrellas(pantalla, zona, 25, 60)
    kit.estelas(pantalla, zona, 26, 50, t * rapidez / 6, rapidez=6)
    lejos = kit.avance(t, 0, 160)
    kit.estacion(pantalla, zona.left + 200 - lejos * 260, zona.centery - 40, t, pixel=4 if lejos < 0.4 else 2)
    x = zona.left + 260 + kit.avance(t, 0, 120) * 200
    kit.alondra(pantalla, x, zona.centery + kit.vaiven(t, 90, 2), t, escala=2, mira="derecha",
                llama=1 + kit.avance(t, 10, 60))


@cuadro("ojo_vencido", "CINTURON EXTERIOR")
def ojo_vencido(pantalla, zona, t, paso, datos):
    # El Ojo, cansado y apagado, se va a la deriva. Su lente sigue mirando a lo lejos (la brujula
    # del secreto F03); a la derecha, el compas con una nota nueva en amarillo
    kit.estrellas(pantalla, zona, 27, 90)
    x = zona.left + 190 + t * 0.05
    y = zona.centery + 10 + kit.vaiven(t, 300, 6)
    mirada = mezclar(CIAN, NOCHE, 0.6)
    kit.linea(pantalla, x + 40, y - 6, zona.right, y - 30, mirada, hueco=3, corrimiento=-t // 6)
    kit.jefe(pantalla, "ojo", x, y, "cansado", t, brillo=0.55, rapidez=40)
    caja = pygame.Rect(zona.right - 400, zona.top + 70, 340, 120)
    kit.osciloscopio(pantalla, caja, t, escribir("ALBA") + " .", VIOLETA, nuevo=len(escribir("ALBA").replace(" ", "")))
    rotulo(pantalla, "EL COMPAS", caja.left, caja.top - 18, VIOLETA, alinear="izquierda")
    if kit.titila(t, 60):
        rotulo(pantalla, "NOTA NUEVA", caja.right, caja.bottom + 22, AMARILLO, alinear="derecha")


@cuadro("bitacora", "RESTOS EN EL CINTURON")
def bitacora(pantalla, zona, t, paso, datos):
    # Un pedazo de la Errante a la deriva y, al lado, la bitacora que se lee en la pantallita
    kit.estrellas(pantalla, zona, 28, 80)
    x, y = zona.left + 220, zona.centery + 10 + kit.vaiven(t, 260, 4)
    _casco_roto(pantalla, x, y, t)
    pantalla_x = zona.left + 470
    caja = pygame.Rect(pantalla_x, zona.top + 50, 400, 180)
    pantalla.fill((6, 16, 24), caja)
    interfaz.esquinas(pantalla, caja, CIAN, largo=8, grueso=2)
    rotulo(pantalla, "BITACORA - ROCIO VEGA", caja.left + 16, caja.top + 22, CIAN, alinear="izquierda")
    rotulo(pantalla, "DIA 41", caja.left + 16, caja.top + 50, TEXTO_SUAVE, alinear="izquierda")
    escrito = max(0, t - 20) * 3
    for i, ancho in enumerate((330, 280, 350, 300, 160)):
        largo = min(ancho, escrito - i * 120)
        if largo > 0:
            pantalla.fill(mezclar(CIAN, NOCHE, 0.35), (caja.left + 16, caja.top + 74 + i * 18, g(largo), 6))
    if escrito > 600 and kit.titila(t, 50):
        pantalla.fill(CIAN, (caja.left + 16 + 160 + 6, caja.top + 74 + 4 * 18, 6, 6))


def _casco_roto(pantalla, x, y, t):
    # Un pedazo de casco con la franja roja de la Errante, el borde roto que todavia brilla y
    # los cables sueltos que se mecen
    kit.pintar(pantalla, kit.CASCO_ROTO, kit.PALETA_CASCO, x, y, 8)
    if kit.titila(t, 70):
        dibujo.halo(pantalla, x + 52, y - 10, 20, (255, 140, 0), 0.6)
    for i in range(3):
        largo = 20 + i * 8
        for paso in range(0, largo, 2):
            onda = math.sin(paso / 6 + t / 20 + i) * 3
            pantalla.fill((90, 80, 70) if i != 1 else ROJO, (g(x + 30 + i * 8 + onda), g(y + 36 + paso), 2, 2))
    rotulo(pantalla, "ERRANTE", x - 10, y - 54, GRIS)


@cuadro("rastro_errante", "HACE TRES AÑOS")
def rastro_errante(pantalla, zona, t, paso, datos):
    # El camino de la Errante: una estela vieja y punteada; al final, su fantasma. La Alondra lo sigue
    kit.estrellas(pantalla, zona, 29, 100)
    y_camino = lambda x: zona.centery + 30 - (x - zona.left) * 0.12 + math.sin((x - zona.left) / 90) * 14
    for x in range(zona.left + 40, zona.right - 140, 2):
        if (x // 2) % 6 < 2:
            pantalla.fill(mezclar(GRIS, NOCHE, 0.5), (x, g(y_camino(x)), 2, 2))
    fantasma_x = zona.right - 110
    kit.errante(pantalla, fantasma_x, y_camino(fantasma_x), 4, mezclar(GRIS, NOCHE, 0.45 if kit.titila(t, 120) else 0.6))
    rotulo(pantalla, "LA ERRANTE", fantasma_x, y_camino(fantasma_x) - 44, TEXTO_SUAVE)
    rapidez = 0.5 if paso < 2 else 1.4
    x = zona.left + 100 + min(t * rapidez, 380)
    kit.alondra(pantalla, x, y_camino(x), t, escala=2, mira="derecha", llama=0.6 if paso < 2 else 1.4)
