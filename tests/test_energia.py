"""La barra de energia: que la llena y como se sube de nivel."""
import math

import pygame

from juego import hud
from juego.config import (ANCHO, ALTO, ENERGIA_MONEDA, ENERGIA_COMBO, ENERGIA_PERFECTO, ENERGIA_ENEMIGO,
                          ENERGIA_DESAFIO, ENERGIA_INICIAL, ENERGIA_POR_NIVEL, ENERGIA_MAXIMA, JEFE_CADA_NIVELES)
from juego.desafios import TIPOS_DESAFIO
from juego.enemigos import crear_enemigo
from tests.ayudas import jugar


def recoger_moneda(partida):
    partida.moneda.x, partida.moneda.y = partida.nave.x + 15, partida.nave.y + 15
    jugar(partida)


def test_una_moneda_da_energia_y_con_combo_mas(partida):
    recoger_moneda(partida)
    assert partida.energia == ENERGIA_MONEDA
    partida.energia = 0
    partida.combo = 8                   # con la de ahora, 9 seguidas: x4
    partida.ultima_moneda = partida.tiempo
    recoger_moneda(partida)
    assert partida.energia == ENERGIA_MONEDA + ENERGIA_COMBO * 3


def test_el_dash_perfecto_y_destruir_enemigos_dan_energia(partida):
    partida._dash_perfecto(0, 0)
    assert partida.energia == ENERGIA_PERFECTO
    enemigo = crear_enemigo("divisor_chico", partida)
    partida.enemigos.append(enemigo)
    partida.destruir_con_dash(enemigo)
    assert partida.energia == ENERGIA_PERFECTO + ENERGIA_ENEMIGO


def test_cumplir_un_desafio_da_energia(partida):
    director = partida.director
    director.desafio = TIPOS_DESAFIO["interceptor"]()
    for _ in range(director.desafio.meta):
        director.al_interceptar()
    assert director.desafio.estado == "cumplido"
    assert partida.energia == ENERGIA_DESAFIO


def test_con_la_barra_llena_se_sube_y_sobra_el_resto(partida):
    partida.energia = partida.energia_necesaria() - 0.5
    partida.ganar_energia(1.5)
    assert partida.nivel == 2
    assert partida.energia == 1


def test_nunca_se_saltean_dos_niveles(partida):
    partida.ganar_energia(1000)
    assert partida.nivel == 2
    assert partida.energia < partida.energia_necesaria()


def test_cada_nivel_pide_un_poco_mas_con_tope(partida):
    assert partida.energia_necesaria() == ENERGIA_INICIAL
    partida.nivel = 3
    assert partida.energia_necesaria() == ENERGIA_INICIAL + 2 * ENERGIA_POR_NIVEL
    partida.nivel = 99
    assert partida.energia_necesaria() == ENERGIA_MAXIMA


def test_con_el_jefe_no_se_gana_y_su_nivel_vacia_la_barra(partida):
    partida.nave.invulnerable_hasta = math.inf
    partida.nivel = JEFE_CADA_NIVELES - 1
    partida.energia = partida.energia_necesaria() - 0.5
    partida.ganar_energia(3)                # sube al nivel del jefe
    assert partida.jefe is not None
    assert partida.energia == 0
    partida.ganar_energia(5)
    assert partida.energia == 0             # durante la pelea no se gana


def test_la_barra_se_dibuja(partida):
    pantalla = pygame.Surface((ANCHO, ALTO))
    partida.energia = partida.energia_necesaria() / 2
    hud.dibujar(pantalla, partida)
    # Algun bloque amarillo dentro de la barra (abajo a la derecha)
    barra = pygame.Rect(ANCHO - 148, 576, 128, 12)
    colores = {tuple(pantalla.get_at((x, barra.centery)))[:3] for x in range(barra.left, barra.right)}
    assert any(color[0] > 200 and color[1] > 150 and color[2] < 100 for color in colores)
