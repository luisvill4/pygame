"""Dash: el dash perfecto (atravesar un peligro) y los dashes extra."""
import math

from juego.config import DASH_RECARGA, DASH_PERFECTO_RECARGA, DASH_PERFECTO_PUNTOS, MS_POR_FRAME
from juego.enemigos import crear_enemigo
from juego.proyectiles import Bala
from tests.ayudas import jugar


def enemigo_en(partida, tipo, x, y):
    enemigo = crear_enemigo(tipo, partida)
    enemigo.aparece_en = 0
    enemigo.x, enemigo.y = x, y
    partida.enemigos.append(enemigo)
    return enemigo


def test_atravesar_un_enemigo_con_el_dash_es_perfecto(partida):
    partida.nave.x, partida.nave.y = 100, 300
    enemigo_en(partida, "perseguidor", 160, 305)
    jugar(partida, dx=1, dash=True)
    jugar(partida, 6, dx=1)
    assert partida.estadisticas.perfectos == 1
    assert partida.vidas == partida.vidas_max
    assert partida.puntaje == DASH_PERFECTO_PUNTOS
    # Recarga casi enseguida (en vez de DASH_RECARGA)
    assert partida.nave.dash_listo - partida.tiempo <= DASH_PERFECTO_RECARGA
    assert DASH_PERFECTO_RECARGA < DASH_RECARGA


def test_una_sola_vez_por_dash(partida):
    partida.nave.x, partida.nave.y = 100, 300
    enemigo_en(partida, "perseguidor", 150, 305)
    enemigo_en(partida, "perseguidor", 200, 305)
    jugar(partida, dx=1, dash=True)
    jugar(partida, 10, dx=1)
    assert partida.estadisticas.perfectos == 1


def test_atravesar_una_bala_tambien(partida):
    partida.nave.x, partida.nave.y = 100, 300
    partida.balas.append(Bala(170, 325, 0, 0))
    jugar(partida, dx=1, dash=True)
    jugar(partida, 6, dx=1)
    assert partida.estadisticas.perfectos == 1
    assert partida.vidas == partida.vidas_max


def test_sin_dash_el_enemigo_pega(partida):
    partida.nave.x, partida.nave.y = 100, 300
    enemigo_en(partida, "perseguidor", 105, 305)
    jugar(partida)
    assert partida.estadisticas.perfectos == 0
    assert partida.vidas == partida.vidas_max - 1


def test_el_perfecto_mantiene_el_combo(partida):
    partida.combo = 4
    partida.ultima_moneda = partida.tiempo - 1900        # al combo le quedan 100 ms
    partida.nave.x, partida.nave.y = 100, 300
    enemigo_en(partida, "perseguidor", 160, 305)
    jugar(partida, dx=1, dash=True)
    jugar(partida, 12, dx=1)
    assert partida.combo == 4


def test_los_dashes_extra_salen_seguidos_y_se_recargan_juntos(partida):
    nave = partida.nave
    nave.dash_extra_max = 1
    jugar(partida, dx=1, dash=True)
    primero = nave.dash_hasta
    jugar(partida, int(nave.duracion_dash / MS_POR_FRAME) + 1)
    jugar(partida, dx=1, dash=True)
    assert nave.dash_hasta > primero                    # el extra salio sin esperar la recarga
    segundo = nave.dash_hasta
    jugar(partida, int(nave.duracion_dash / MS_POR_FRAME) + 1)
    jugar(partida, dx=1, dash=True)
    assert nave.dash_hasta == segundo                   # ya no quedan: hay que esperar
    jugar(partida, int(DASH_RECARGA / MS_POR_FRAME))
    jugar(partida, dx=1, dash=True)
    assert nave.dash_hasta > segundo
    assert nave.dash_extra == 1                         # recargado junto con el dash


def test_el_dash_se_cuenta_en_las_estadisticas(partida):
    jugar(partida, dx=1, dash=True)
    jugar(partida, int(DASH_RECARGA / MS_POR_FRAME) + 2)
    jugar(partida, dx=-1, dash=True)
    assert partida.estadisticas.dashes == 2
    assert math.isfinite(partida.nave.dash_listo)


def test_perfectos_seguidos_forman_una_cadena(partida):
    from juego.config import CADENA_PERFECTOS
    partida._dash_perfecto(0, 0)
    partida.perfecto_en_este_dash = False
    partida.tiempo += CADENA_PERFECTOS - 100
    partida._dash_perfecto(0, 0)
    assert partida.cadena == 2
    assert partida.puntaje == DASH_PERFECTO_PUNTOS * 3          # 1 + 2
    partida.perfecto_en_este_dash = False
    partida.tiempo += CADENA_PERFECTOS + 100                  # muy tarde: empieza otra
    partida._dash_perfecto(0, 0)
    assert partida.cadena == 1
    assert partida.estadisticas.mejor_cadena == 2
