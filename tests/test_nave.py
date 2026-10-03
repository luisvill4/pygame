"""Nave: velocidad, dash con buffer y el aviso de dash listo."""
import pytest

from juego.config import NAVE_VELOCIDAD, DASH_FUERZA
from tests.ayudas import jugar


def test_llega_a_la_velocidad_maxima(partida):
    jugar(partida, 60, dx=1)
    assert partida.nave.vx == pytest.approx(NAVE_VELOCIDAD, abs=0.05)


def test_en_diagonal_no_va_mas_rapido(partida):
    partida.nave.x, partida.nave.y = 100, 100
    jugar(partida, 40, dx=1, dy=1)
    assert (partida.nave.vx ** 2 + partida.nave.vy ** 2) ** 0.5 == pytest.approx(NAVE_VELOCIDAD, abs=0.1)


def test_el_stick_mueve_en_cualquier_angulo(partida):
    partida.nave.x, partida.nave.y = 375, 275
    jugar(partida, 30, dx=0.5, dy=-0.3)
    assert round(partida.nave.angulo_objetivo) == 301


def test_dash(partida):
    jugar(partida, dx=1, dash=True)
    assert partida.nave.en_dash(partida.tiempo)
    assert partida.nave.vx == pytest.approx(DASH_FUERZA)


def test_buffer_del_dash(partida):
    nave = partida.nave
    nave.dash_listo = partida.tiempo + 100      # se apreta 100 ms antes de que este listo
    jugar(partida, dash=True)
    jugar(partida, 10)
    assert nave.dash_hasta > 0                  # salio igual al recargarse

    nave.dash_hasta = 0
    nave.dash_listo = partida.tiempo + 300      # 300 ms antes: ya es demasiado
    jugar(partida, dash=True)
    jugar(partida, 25)
    assert nave.dash_hasta == 0


def test_aviso_de_dash_listo_una_sola_vez(partida):
    # Se anotan los anillos que se crean: el del dash tiene 16 particulas y el aviso 12
    cantidades = []
    anillo_original = partida.efectos.anillo
    partida.efectos.anillo = lambda *datos: cantidades.append(datos[3]) or anillo_original(*datos)
    jugar(partida, dash=True)
    jugar(partida, 150)
    assert cantidades.count(16) == 1
    assert cantidades.count(12) == 1


def test_al_dar_la_vuelta_frena_enseguida(partida):
    # A toda velocidad hacia la derecha y de golpe a la izquierda: en 3 pasos ya va para el
    # otro lado (con la aceleracion normal tardaba 5 y se pasaba de largo)
    partida.nave.x = 100
    jugar(partida, 60, dx=1)
    jugar(partida, 3, dx=-1)
    assert partida.nave.vx < 0


def test_al_doblar_casi_no_patina(partida):
    # De costado se corrige con NAVE_FRENADO: lo que iba hacia la derecha se pierde rapido
    partida.nave.x, partida.nave.y = 100, 100
    jugar(partida, 60, dx=1)
    partida.nave.x = 300
    jugar(partida, 5, dy=1)
    assert abs(partida.nave.vx) < 1
    assert partida.nave.vy > 2
