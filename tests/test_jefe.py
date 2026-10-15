"""Jefe: aparicion, golpes, congelado, aviso del ataque y lo que pasa al vencerlo."""
import math

import pytest

from juego.config import JEFE_VIDA, CARTEL_JEFE, CARTEL_RANGO, MS_POR_FRAME, SECTORES
from juego.enemigos import crear_enemigo
from juego.jefes import TIPOS_JEFE
from tests.ayudas import jugar


def llegar_al_jefe(partida):
    partida.enemigos[:] = [crear_enemigo(t, partida) for t in
                           ["perseguidor", "rebotador", "embestidor", "perseguidor"]]
    partida.nivel = 4
    partida.director.asedio_cumplido = True     # (el asedio del tramo 4 retiene el nivel)
    partida.subir_nivel()       # nivel 5: aparece el jefe y los enemigos explotan
    return partida.jefe


def test_todos_los_jefes_de_los_sectores_existen():
    assert {sector["jefe"] for sector in SECTORES} <= set(TIPOS_JEFE)


def test_aparece_en_el_nivel_5_y_los_enemigos_explotan(partida):
    jefe = llegar_al_jefe(partida)
    assert jefe is not None
    assert jefe.vida == JEFE_VIDA
    assert partida.enemigos == []


def test_golpe_con_dash_en_el_nucleo(partida):
    jefe = llegar_al_jefe(partida)
    jefe.y = 70
    jefe.cambiar_fase("cansado", 2500, partida.tiempo)
    nucleo_x, nucleo_y = jefe.centro_nucleo()
    partida.nave.x, partida.nave.y = nucleo_x - 25, nucleo_y - 25
    partida.nave.dash_hasta = partida.tiempo + 500
    partida._choques_jefe()
    assert jefe.vida == JEFE_VIDA - 1
    assert partida.vidas == 3
    assert partida.nave.dash_hasta == 0         # la nave rebota


def test_congelado_no_avanza_su_fase(partida):
    jefe = llegar_al_jefe(partida)
    jefe.y = 70
    jefe.cambiar_fase("flotar", 2500, partida.tiempo)
    partida.activar("hielo", 5000)
    fin_de_fase = jefe.fase_hasta
    jugar(partida, 60)
    assert jefe.fase == "flotar"
    assert jefe.fase_hasta == pytest.approx(fin_de_fase + 60 * MS_POR_FRAME)


def test_el_aviso_muestra_justo_las_balas_que_salen(partida):
    jefe = llegar_al_jefe(partida)
    for ataque in ("abanico", "anillo"):
        partida.balas.clear()
        jefe.ataque = ataque
        direcciones, rapidez = jefe.direcciones_ataque(partida)
        jefe.disparar(partida)
        assert len(partida.balas) == len(direcciones)
        for bala, direccion in zip(partida.balas, direcciones):
            assert math.atan2(bala.vy, bala.vx) == pytest.approx(math.atan2(math.sin(direccion), math.cos(direccion)))


def test_al_vencerlo_empieza_el_sector_siguiente(partida):
    partida.nave.invulnerable_hasta = math.inf
    llegar_al_jefe(partida)
    partida.jefe_vencido()
    jugar(partida, int((CARTEL_JEFE + CARTEL_RANGO) / MS_POR_FRAME) + 2)
    assert partida.director.sector is SECTORES[1]
    assert partida.director.numero_tramo == 1 and partida.nivel == 6


def test_los_enemigos_no_vuelven_mientras_esta_el_cartel(partida):
    partida.nave.invulnerable_hasta = math.inf
    llegar_al_jefe(partida)
    partida.jefe_vencido()
    jugar(partida, int(CARTEL_JEFE / MS_POR_FRAME) - 5)
    assert partida.enemigos == []
