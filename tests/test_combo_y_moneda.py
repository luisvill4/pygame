"""Combo, multiplicador, niveles y lugar de la moneda."""
import math
import random

import pygame

from juego.config import COMBO_TIEMPO, MONEDA_DISTANCIA_MIN, MONEDA_DISTANCIA_MAX, MS_POR_FRAME
from juego.enemigos import crear_enemigo
from juego.hud import zonas_hud
from juego.moneda import lugar_para_moneda
from tests.ayudas import jugar


def recoger_moneda(partida):
    partida.moneda.x, partida.moneda.y = partida.nave.x + 15, partida.nave.y + 15
    jugar(partida)
    partida.moneda.x, partida.moneda.y = -500, -500


def test_el_combo_sube_hasta_x5(partida):
    for _ in range(12):
        recoger_moneda(partida)
    assert partida.combo == 12
    assert partida.multiplicador_combo() == 5
    recoger_moneda(partida)
    assert partida.multiplicador_combo() == 5       # no pasa de x5


def test_el_combo_se_corta_con_el_tiempo(partida):
    for _ in range(12):
        recoger_moneda(partida)
    jugar(partida, int(COMBO_TIEMPO / MS_POR_FRAME) + 5)
    assert partida.combo == 0
    recoger_moneda(partida)
    assert partida.combo == 1                       # (antes habia un bug que lo dejaba en x5)
    assert partida.multiplicador_combo() == 1


def test_el_combo_se_corta_con_un_golpe(partida):
    for _ in range(12):
        recoger_moneda(partida)
    partida.danar_jugador(*partida.nave.centro())
    assert partida.combo == 0
    recoger_moneda(partida)
    assert partida.multiplicador_combo() == 1


def test_puntos_dobles(partida):
    partida.activar("doble", 8000)
    recoger_moneda(partida)
    assert partida.puntaje == 2


def test_cada_10_monedas_sube_de_nivel(partida):
    for _ in range(10):
        recoger_moneda(partida)
    assert partida.nivel == 2
    assert [e.tipo for e in partida.enemigos] == ["rebotador"]


def test_lugar_de_la_moneda(partida):
    # Siempre a una distancia alcanzable, fuera del HUD y lejos de los enemigos
    random.seed(1)
    for _ in range(2000):
        partida.nave.x, partida.nave.y = random.randint(0, 750), random.randint(0, 550)
        partida.enemigos[:] = [crear_enemigo("rebotador", partida) for _ in range(4)]
        for enemigo in partida.enemigos:
            enemigo.x, enemigo.y = random.randint(0, 760), random.randint(70, 560)
        x, y = lugar_para_moneda(partida)
        nave_x, nave_y = partida.nave.centro()
        distancia = math.hypot(x + 10 - nave_x, y + 10 - nave_y)
        assert MONEDA_DISTANCIA_MIN <= distancia <= MONEDA_DISTANCIA_MAX
        assert pygame.Rect(x, y, 20, 20).collidelist(zonas_hud()) == -1
        for enemigo in partida.enemigos:
            enemigo_x, enemigo_y = enemigo.centro()
            assert math.hypot(x + 10 - enemigo_x, y + 10 - enemigo_y) >= 60
