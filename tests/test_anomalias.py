"""Anomalias: cuando llegan, cuanto duran, y que cada una avisa antes de atacar."""
import math
import random

import pygame
import pytest


from juego.anomalias import TIPOS_ANOMALIA, crear_anomalia
from juego.config import (ANCHO, ALTO, ANOMALIA_DURACION, ANOMALIA_ESPERA, RESPIRO_ANOMALIA, ASTEROIDES_AVISO,
                          ASTEROIDES_PUNTOS, ASTEROIDES_ESPERA, TORMENTA_AVISO, COMBO_TIEMPO, ORO_COMBO, ORO_MULTIPLICADOR,
                          MS_POR_FRAME, SECTORES, BLANCO, ANOMALIA_PROPIA)
from juego.proyectiles import Meteoro
from tests.ayudas import jugar, avanzar, empezar_partida


def poner(partida, tipo):
    # La anomalia ya en marcha (sin esperar a su nivel)
    partida.director.anomalia = crear_anomalia(tipo, partida)
    return partida.director.anomalia


def test_llega_en_el_tercer_nivel_del_sector(partida):
    director = partida.director
    director.con_anomalias = True
    partida.nivel = 2
    partida.subir_nivel()
    jugar(partida, int(ANOMALIA_ESPERA / MS_POR_FRAME) - 5)
    assert director.anomalia is None                # todavia no
    jugar(partida, 10)
    assert director.anomalia.tipo in TIPOS_ANOMALIA
    # Mientras dura (y un rato despues) no hay oleadas
    assert director.proxima_oleada >= director.anomalia.hasta + RESPIRO_ANOMALIA


def test_se_va_sola(partida):
    partida.nave.invulnerable_hasta = math.inf
    partida.director.empezar_anomalia()
    jugar(partida, int(ANOMALIA_DURACION / MS_POR_FRAME) + 2)
    assert partida.director.anomalia is None


def test_el_jefe_la_corta(partida):
    partida.director.empezar_anomalia()
    partida.iniciar_jefe()
    assert partida.director.anomalia is None


def test_la_del_sector_la_mitad_de_las_veces_y_todas_desde_el_principio(partida):
    # Antes cada sector traia siempre la suya: la fiebre del oro recien salia en el nivel 18
    random.seed(7)
    director = partida.director
    elegidas = [director.elegir_anomalia() for _ in range(2000)]
    propia = SECTORES[0]["anomalia"]
    assert abs(elegidas.count(propia) / len(elegidas) - ANOMALIA_PROPIA) < 0.05
    assert set(elegidas) == set(TIPOS_ANOMALIA)     # en el primer sector se pueden ver todas


def test_en_un_sector_sin_anomalia_propia_sale_una_al_azar(partida):
    director = partida.director
    director.sector = next(s for s in SECTORES if s["anomalia"] is None)
    director.empezar_anomalia()
    assert director.anomalia.tipo in TIPOS_ANOMALIA


def test_todos_los_sectores_usan_anomalias_que_existen():
    assert {s["anomalia"] for s in SECTORES} - {None} <= set(TIPOS_ANOMALIA)


def test_cada_asteroide_cae_por_una_columna_avisada(partida):
    partida.nave.invulnerable_hasta = math.inf
    lluvia = poner(partida, "asteroides")
    avisados = {}                                   # x -> cuando aparecio su columna
    caidos = 0
    duracion = 10000
    for _ in range(int(duracion / MS_POR_FRAME)):
        antes = list(partida.balas)
        jugar(partida)
        for x, _cae_en in lluvia.avisos:
            avisados.setdefault(x, partida.tiempo)
        for meteoro in [b for b in partida.balas if b not in antes]:
            caidos += 1
            assert meteoro.x in avisados
            assert partida.tiempo - avisados[meteoro.x] >= ASTEROIDES_AVISO - MS_POR_FRAME
    # El primero sale a los 1.5 s (cuando se va el cartel) y despues uno cada ASTEROIDES_ESPERA
    assert caidos >= int((duracion - 1500 - ASTEROIDES_AVISO) / ASTEROIDES_ESPERA)


def test_el_asteroide_lastima_y_el_dash_lo_rompe(partida):
    nave_x, nave_y = partida.nave.centro()
    partida.balas.append(Meteoro(nave_x, nave_y, 0, 1))
    jugar(partida)
    assert partida.vidas == partida.vidas_max - 1
    assert not partida.balas

    partida.nave.invulnerable_hasta = 0
    nave_x, nave_y = partida.nave.centro()
    partida.balas.append(Meteoro(nave_x, nave_y, 0, 1))
    partida.nave.dash_hasta = partida.tiempo + 500
    jugar(partida)
    assert not partida.balas
    assert partida.puntaje == ASTEROIDES_PUNTOS
    assert partida.vidas == partida.vidas_max - 1


def test_la_tormenta_avisa_antes_de_quemar(partida):
    tormenta = poner(partida, "tormenta")
    nave = partida.nave
    while tormenta.fase != "aviso":
        jugar(partida)
    empezo_aviso = partida.tiempo
    franja = tormenta.franja
    # Parada justo en el medio de la franja: mientras avisa, no pasa nada...
    while tormenta.fase == "aviso":
        nave.x, nave.y = franja.centerx - 25, franja.centery - 25
        nave.vx = nave.vy = 0
        jugar(partida)
        assert partida.vidas == partida.vidas_max
    assert partida.tiempo - empezo_aviso == pytest.approx(TORMENTA_AVISO, abs=MS_POR_FRAME)
    assert tormenta.franja is franja                # quema justo donde aviso
    # ...pero cuando quema, si
    nave.x, nave.y = franja.centerx - 25, franja.centery - 25
    jugar(partida)
    assert partida.vidas == partida.vidas_max - 1


def test_la_niebla_solo_deja_ver_cerca_de_la_nave(partida):
    niebla = poner(partida, "niebla")
    jugar(partida, int(2000 / MS_POR_FRAME))        # ya termino de cerrarse
    partida.nave.x, partida.nave.y = 100, 300
    pantalla = pygame.Surface((ANCHO, ALTO))
    pantalla.fill(BLANCO)
    niebla.dibujar(pantalla, partida)
    assert pantalla.get_at((125, 325))[:3] == BLANCO            # al lado de la nave se ve
    assert sum(pantalla.get_at((ANCHO - 60, 500))[:3]) < 200     # lejos, oscuro


def test_en_la_fiebre_del_oro_las_monedas_valen_doble_y_el_combo_dura_mas(partida):
    poner(partida, "oro")
    assert partida.tiempo_combo() == COMBO_TIEMPO * ORO_COMBO
    partida.moneda.x, partida.moneda.y = partida.nave.x + 15, partida.nave.y + 15
    jugar(partida)
    assert partida.puntaje == ORO_MULTIPLICADOR


@pytest.mark.parametrize("tipo", sorted(TIPOS_ANOMALIA))
def test_se_dibuja_entera(app, tipo):
    avanzar(app)
    partida = empezar_partida(app)
    partida.nave.invulnerable_hasta = math.inf
    partida.director.anomalia = crear_anomalia(tipo, partida)
    avanzar(app, int(6000 / MS_POR_FRAME))          # cartel, avisos, ataques...
