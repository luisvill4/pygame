"""
Los cuadros del PROLOGO (escenas/historia/prologo.py): lo que sabe todo el mundo antes de
empezar (HISTORIA.md, seccion 1). 'paso' es la pagina del narrador.
"""
import math

import pygame

from juego import dibujo, interfaz, nave
from juego.config import ROJO, AMARILLO, CIAN, VIOLETA, NARANJA, TEXTO_SUAVE, LINEA_APAGADA
from juego.historia.glifos import escribir
from juego.escenas.historia.cuadros.base import cuadro
from juego.escenas.historia.cuadros import kit
from juego.escenas.historia.cuadros.kit import g, rotulo, NUESTRA, MAREA


@cuadro("cielo")
def cielo(pantalla, zona, t, paso, datos):
    # Nuestra galaxia que gira despacio y, arriba a la derecha, un punto rojo que no estaba
    kit.estrellas(pantalla, zona, 1, 90)
    kit.galaxia(pantalla, zona.centerx - 60, zona.centery + 10, 150, t * 0.004, NUESTRA, 1)
    if t > 50:
        x, y = zona.right - 110, zona.top + 64
        pantalla.fill(ROJO, (x - 2, y - 2, 4, 4))
        dibujo.halo(pantalla, x, y, 12, ROJO)
        if t > 90:      # la mira del telescopio se cierra sobre el punto
            lado = max(16, 60 - (t - 90) // 2 * 2)
            interfaz.esquinas(pantalla, pygame.Rect(x - lado // 2, y - lado // 2, lado, lado), AMARILLO,
                              largo=6, grueso=2)


@cuadro("marea")
def marea(pantalla, zona, t, paso, datos):
    # La Marea (roja, sin forma) se acerca a la nuestra (la espiral azul)
    kit.estrellas(pantalla, zona, 2, 70)
    kit.galaxia(pantalla, zona.left + 190, zona.centery, 120, t * 0.003, NUESTRA, 1)
    x = zona.right - 130 - min(t, 400) * 0.15
    kit.nube(pantalla, x, zona.centery - 20, 50, MAREA, 3)
    rotulo(pantalla, "NOSOTROS", zona.left + 190, zona.bottom - 24, (110, 170, 255))
    rotulo(pantalla, "LA MAREA", x, zona.bottom - 24, ROJO)


@cuadro("orbitas")
def orbitas(pantalla, zona, t, paso, datos):
    # Una estrella con sus planetas; la Marea entra por la derecha y las orbitas se estiran
    kit.estrellas(pantalla, zona, 3, 60)
    tiron = min(1.0, t / 420)
    sol_x, sol_y = zona.centerx - 60, zona.centery
    kit.frente_de_la_marea(pantalla, zona, zona.right - g(40 + 100 * tiron), t)
    for i, (radio, velocidad) in enumerate(((50, 0.03), (90, 0.018), (130, 0.011))):
        estirar = 1 + tiron * 0.25 * (i + 1)                 # las de afuera se estiran mas
        centro_x = sol_x + tiron * 14 * (i + 1)
        for grado in range(0, 360, 6):
            angulo = math.radians(grado)
            pantalla.fill(LINEA_APAGADA, (g(centro_x + math.cos(angulo) * radio * estirar),
                                          g(sol_y + math.sin(angulo) * radio * 0.45), 2, 2))
        angulo = t * velocidad + i * 2
        x = centro_x + math.cos(angulo) * radio * estirar
        y = sol_y + math.sin(angulo) * radio * 0.45
        if i == 2 and tiron >= 1:           # el de afuera se suelta y se va hacia la Marea
            x += (t - 420) * 0.6
        pantalla.fill((140, 200, 255), (g(x) - 4, g(y) - 4, 8, 8))
    pantalla.fill(AMARILLO, (sol_x - 8, sol_y - 8, 16, 16))
    dibujo.halo(pantalla, sol_x, sol_y, 28, AMARILLO)
    if paso >= 1:
        rotulo(pantalla, "FALTAN 6 AÑOS", zona.left + 20, zona.top + 24, ROJO, alinear="izquierda")


@cuadro("compas", sonido="fragmento")       # (el compas de verdad, el que se oye en el juego)
def compas(pantalla, zona, t, paso, datos):
    # Un osciloscopio: el compas pasa de derecha a izquierda, con el ritmo de verdad
    caja = zona.inflate(-80, -100)
    kit.osciloscopio(pantalla, caja, t, escribir("ALBA"), VIOLETA)
    rotulo(pantalla, "EL COMPAS", caja.left, caja.top - 24, VIOLETA, alinear="izquierda")


@cuadro("errante")
def errante(pantalla, zona, t, paso, datos):
    # La Errante sale de la Umbral y se pierde a lo lejos
    kit.estrellas(pantalla, zona, 5, 80)
    dibujo.pixel_art(pantalla, kit.ESTACION, zona.left + 90, zona.centery + 40, AMARILLO, 8)
    recorrido = min(t, 300)
    x = zona.left + 150 + recorrido * 1.4
    y = zona.centery + 40 - recorrido * 0.35
    if recorrido < 300:
        pixel = 4 if recorrido < 150 else 2                 # (se achica: se aleja)
        largo_llama = 2 + round(math.sin(t / 4) + 1) * 2
        pantalla.fill(NARANJA, (g(x) - len(kit.ERRANTE[0]) * pixel // 2 - largo_llama * pixel // 2,
                                g(y) - pixel, largo_llama * pixel // 2, pixel * 2))
        kit.errante(pantalla, x, y, pixel)
    if paso >= 1:
        rotulo(pantalla, "LA ERRANTE", zona.right - 24, zona.top + 24, TEXTO_SUAVE, alinear="derecha")
        rotulo(pantalla, "SIN SEÑAL", zona.right - 24, zona.top + 52, ROJO, alinear="derecha")


@cuadro("relojes")
def relojes(pantalla, zona, t, paso, datos):
    # Dos relojes: el de la Alondra casi no se mueve; el de la Umbral vuela
    kit.estrellas(pantalla, zona, 6, 40)
    izquierda, derecha, y = zona.centerx - 150, zona.centerx + 150, zona.centery - 20
    kit.reloj(pantalla, izquierda, y, 70, t * 0.004, CIAN)
    kit.reloj(pantalla, derecha, y, 70, t * 0.25, AMARILLO)
    rotulo(pantalla, "LA ALONDRA", izquierda, y + 100, CIAN)
    rotulo(pantalla, "LA UMBRAL", derecha, y + 100, AMARILLO)
    horas = min(t // 160, 9)
    meses = min(t // 25, 99)
    rotulo(pantalla, cuantos(horas, "HORA", "HORAS"), izquierda, y + 128, TEXTO_SUAVE)
    rotulo(pantalla, cuantos(meses, "MES", "MESES"), derecha, y + 128, TEXTO_SUAVE)


@cuadro("alba")
def alba(pantalla, zona, t, paso, datos):
    # Ines y Alba, y la Alondra entre las dos
    kit.estrellas(pantalla, zona, 7, 60)
    for personaje, centro, nombre, lugar, color in (("ines", zona.left + 120, "INES CORIA", "LA UMBRAL", AMARILLO),
                                                    ("alba", zona.right - 120, "ALBA", "LA ALONDRA", CIAN)):
        kit.retrato(pantalla, personaje, centro - 48, zona.top + 72, 8, color)
        rotulo(pantalla, nombre, centro, zona.top + 200, color)
        rotulo(pantalla, lugar, centro, zona.top + 228, TEXTO_SUAVE)
    kit.alondra(pantalla, zona.centerx, zona.centery - 4 + kit.vaiven(t, 126, 2), t, escala=2,
                imagen=nave.armar(()))      # (la de fabrica: todavia no tiene nada)


def cuantos(numero, singular, plural):
    return "%d %s" % (numero, singular if numero == 1 else plural)
