"""
HUD: el marcador que se dibuja encima del juego.

- Arriba: puntos y combo (izquierda), record (centro), vidas (derecha).
- Abajo: power-ups activos (izquierda), barra del jefe (centro), dash y nivel (derecha).
- Carteles: "NIVEL X" y "¡JEFE VENCIDO!".

ZONAS_HUD son los rectangulos que ocupa el HUD: ahi no aparecen monedas.
Si el HUD cambia de lugar o crece, hay que actualizarlas.
"""
import random

import pygame

from juego import dibujo, nave
from juego.dibujo import texto, CHICA, GRANDE
from juego.config import (ANCHO, ALTO, ROJO, BLANCO, AMARILLO, GRIS, CIAN, MAGENTA,
                          VIDAS_MAX, COMBO_TIEMPO, CARTEL_JEFE)
from juego.powerups import TIPOS_POWERUP

ZONAS_HUD = [
    pygame.Rect(0, 0, 800, 100),        # arriba: puntos, combo, record y vidas
    pygame.Rect(0, 530, 800, 70),       # abajo: dash, nivel y barra del jefe
    pygame.Rect(0, 430, 180, 170),      # abajo a la izquierda: power-ups activos
]


def posicion_libre(ancho, alto):
    # Esquina de arriba a la izquierda, al azar, de algo que no tape el HUD
    while True:
        nueva_x = random.randint(0, ANCHO - ancho)
        nueva_y = random.randint(0, ALTO - alto)
        if pygame.Rect(nueva_x, nueva_y, ancho, alto).collidelist(ZONAS_HUD) == -1:
            return nueva_x, nueva_y


def dibujar(pantalla, partida):
    _marcador(pantalla, partida)
    _activos(pantalla, partida)
    if partida.jefe is not None:
        _barra_jefe(pantalla, partida.jefe)
    # Carteles al subir de nivel y al vencer al jefe
    if partida.tiempo - partida.tiempo_cartel_nivel < 1500:
        dibujo.texto_3d(pantalla, "NIVEL " + str(partida.nivel), GRANDE, AMARILLO, MAGENTA, 250, 4)
    if partida.tiempo - partida.tiempo_cartel_jefe < CARTEL_JEFE:
        dibujo.texto_3d(pantalla, "¡JEFE VENCIDO!", GRANDE, dibujo.color_arcoiris(), MAGENTA, 300, 4)


def _marcador(pantalla, partida):
    ahora = partida.tiempo

    # Puntaje (izquierda): se pone amarillo un instante al recoger una moneda
    texto(pantalla, "PUNTOS", CHICA, ROJO, 20, 22, alinear="izquierda")
    color = AMARILLO if ahora - partida.tiempo_moneda < 200 else BLANCO
    texto(pantalla, dibujo.numero_arcade(partida.puntaje), CHICA, color, 20, 46, alinear="izquierda")

    # Combo (debajo del puntaje) con una barra del tiempo que le queda
    if partida.combo >= 2:
        multiplicador = partida.multiplicador_combo()
        if multiplicador > 1:
            texto(pantalla, "COMBO x" + str(multiplicador), CHICA, dibujo.color_arcoiris(), 20, 72, alinear="izquierda")
        else:
            texto(pantalla, "COMBO " + str(partida.combo), CHICA, GRIS, 20, 72, alinear="izquierda")
        restante = max(0, 1 - (ahora - partida.ultima_moneda) / COMBO_TIEMPO)
        pantalla.fill(AMARILLO, (20, 86, int(128 * restante), 4))

    # Record (centro): se actualiza en vivo si lo estas superando
    texto(pantalla, "RECORD", CHICA, ROJO, 400, 22)
    if partida.puntaje > partida.puntaje_maximo:
        texto(pantalla, dibujo.numero_arcade(partida.puntaje), CHICA, AMARILLO, 400, 46)
    else:
        texto(pantalla, dibujo.numero_arcade(partida.puntaje_maximo), CHICA, BLANCO, 400, 46)

    # Nivel y dash (abajo a la derecha)
    texto(pantalla, "NIVEL " + str(partida.nivel), CHICA, AMARILLO, 780, 575, alinear="derecha")
    if ahora >= partida.nave.dash_listo:
        texto(pantalla, "DASH", CHICA, CIAN, 780, 545, alinear="derecha")
    else:
        texto(pantalla, "DASH", CHICA, GRIS, 780, 545, alinear="derecha")
        # max(0, ...) por si RECARGA cambia a mitad de una recarga
        cargado = max(0, 1 - (partida.nave.dash_listo - ahora) / partida.recarga_dash())
        pantalla.fill(CIAN, (716, 557, int(64 * cargado), 3))

    # Vidas (derecha): parpadean despues de recibir un golpe
    texto(pantalla, "VIDAS", CHICA, ROJO, 780, 22, alinear="derecha")
    if ahora - partida.tiempo_golpe < 800 and dibujo.parpadeo(80):
        return
    for i in range(VIDAS_MAX):
        icono_x = 780 - VIDAS_MAX * 28 + 3 + i * 28
        icono = nave.imagen("icono") if i < partida.vidas else nave.imagen("icono_vacio")
        pantalla.blit(icono, (icono_x, 34))


def _activos(pantalla, partida):
    # Abajo a la izquierda: power-ups activos; los temporales con los segundos que les quedan
    fila_y = 575
    for powerup in TIPOS_POWERUP.values():
        if not partida.activo(powerup.tipo):
            continue
        if powerup.dura_hasta_perder_vida():
            mensaje = powerup.nombre
        else:
            segundos = int(partida.restante(powerup.tipo) // 1000) + 1
            mensaje = powerup.nombre + " " + str(segundos)
        texto(pantalla, mensaje, CHICA, powerup.color, 20, fila_y, alinear="izquierda")
        fila_y -= 26


def _barra_jefe(pantalla, jefe):
    # Abajo al centro: un bloque por cada golpe que le queda
    texto(pantalla, "JEFE", CHICA, ROJO, 318, 575, alinear="derecha")
    ancho_bloque = 200 // jefe.vida_max
    for i in range(jefe.vida_max):
        bloque = pygame.Rect(330 + i * ancho_bloque, 567, ancho_bloque - 4, 16)
        if i < jefe.vida:
            pantalla.fill(MAGENTA, bloque)
        else:
            pygame.draw.rect(pantalla, GRIS, bloque, 2)
