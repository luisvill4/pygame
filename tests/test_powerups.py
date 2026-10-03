"""Power-ups: registro, capsula que cae, efectos y los que duran hasta perder una vida."""
import pytest

from juego.config import (TURBO_VELOCIDAD, NAVE_VELOCIDAD, RECARGA_RAPIDA, DASH_RECARGA,
                          VELOCIDAD_POWERUP, MS_POR_FRAME)
from juego.powerups import TIPOS_POWERUP, Capsula
from juego.proyectiles import Bala
from tests.ayudas import jugar


def test_todos_los_powerups_estan_completos():
    assert list(TIPOS_POWERUP) == ["escudo", "hielo", "vida", "iman", "doble", "turbo", "recarga"]
    for powerup in TIPOS_POWERUP.values():
        assert powerup.nombre and powerup.descripcion and powerup.letra


def recoger(partida, tipo):
    partida.capsula = Capsula(TIPOS_POWERUP[tipo], partida.nave.x + 25)
    partida.capsula.y = partida.nave.y + 25
    jugar(partida)


def test_la_capsula_cae_derecho_y_se_va_por_abajo(partida):
    partida.nave.x, partida.nave.y = 0, 550
    partida.proximo_powerup = 0
    jugar(partida)
    capsula = partida.capsula
    capsula.x = 600                     # lejos de la nave, para que no la recoja
    x_inicial, y_inicial = capsula.x, capsula.y
    jugar(partida, 60)
    assert capsula.x == x_inicial
    assert capsula.y - y_inicial == pytest.approx(VELOCIDAD_POWERUP * 60)
    # Tarda unos 7 segundos en salir por abajo
    frames = 61
    while partida.capsula is capsula:
        jugar(partida)
        frames += 1
    assert 6.5 < frames * MS_POR_FRAME / 1000 < 7.5


@pytest.mark.parametrize("tipo", ["escudo", "hielo", "iman", "doble"])
def test_los_temporales_duran_lo_configurado(partida, tipo):
    recoger(partida, tipo)
    assert partida.activo(tipo)
    jugar(partida, int(TIPOS_POWERUP[tipo].duracion / MS_POR_FRAME) + 2)
    assert not partida.activo(tipo)


def test_vida_suma_una_y_solo_cae_si_falta(partida):
    assert not TIPOS_POWERUP["vida"].disponible(partida)
    partida.vidas = 2
    assert TIPOS_POWERUP["vida"].disponible(partida)
    recoger(partida, "vida")
    assert partida.vidas == 3 == partida.vidas_max


def test_turbo_y_recarga(partida):
    recoger(partida, "turbo")
    recoger(partida, "recarga")
    assert partida.vel_max() == TURBO_VELOCIDAD
    assert partida.recarga_dash() == RECARGA_RAPIDA
    jugar(partida, 60, dx=1)
    assert partida.nave.vx == pytest.approx(TURBO_VELOCIDAD, abs=0.05)
    # Mientras estan activos no vuelven a caer
    assert not TIPOS_POWERUP["turbo"].disponible(partida)


def test_el_escudo_aguanta_y_protege_a_turbo(partida):
    recoger(partida, "escudo")
    recoger(partida, "turbo")
    partida.danar_jugador(*partida.nave.centro())
    assert partida.vidas == 3
    assert not partida.activo("escudo")
    assert partida.activo("turbo")


def test_al_perder_una_vida_se_pierden_turbo_y_recarga(partida):
    recoger(partida, "turbo")
    recoger(partida, "recarga")
    partida.danar_jugador(*partida.nave.centro())
    assert partida.vidas == 2
    assert partida.vel_max() == NAVE_VELOCIDAD
    assert partida.recarga_dash() == DASH_RECARGA
    textos = [t.texto for t in partida.efectos.textos]
    assert "-TURBO" in textos and "-RECARGA" in textos


def test_el_hielo_rompe_las_balas(partida):
    partida.balas.append(Bala(400, 100, 0, 1))
    recoger(partida, "hielo")
    assert partida.balas == []
