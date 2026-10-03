"""Director de la progresion: presupuesto de enemigos, sectores y oleadas."""
import math
import random

from juego.config import (COSTO_ENEMIGO, DESBLOQUEO_ENEMIGO, ENEMIGOS_MAX, SECTORES, SECTOR_CADA_NIVELES,
                          OLEADA_DURACION, MS_POR_FRAME)
from tests.ayudas import jugar


def subir_hasta(partida, nivel):
    while partida.nivel < nivel:
        partida.subir_nivel()
        if partida.jefe is not None:        # sin pelear contra el jefe
            partida.jefe = None
            partida.enemigos.extend(partida.enemigos_guardados)
            partida.enemigos_guardados.clear()


def test_el_presupuesto_crece_con_el_nivel(partida):
    anterior = 0
    for nivel in range(1, 15):
        partida.nivel = nivel
        assert partida.director.presupuesto() >= anterior
        anterior = partida.director.presupuesto()


def test_nivel_1_es_un_solo_perseguidor(app):
    app.nueva_partida()
    partida = app.escena.partida
    assert [e.tipo for e in partida.enemigos] == ["perseguidor"]


def test_los_enemigos_respetan_el_presupuesto_y_el_desbloqueo(partida):
    random.seed(3)
    for _ in range(12):
        partida.subir_nivel()
        if partida.jefe is not None:
            partida.jefe = None
            partida.enemigos.extend(partida.enemigos_guardados)
            partida.enemigos_guardados.clear()
        director = partida.director
        fijos = [e for e in partida.enemigos if not e.de_oleada]
        assert director.cantidad_actual() <= ENEMIGOS_MAX + 1     # un enjambre cuenta como uno
        # No se pasa del presupuesto (salvo por el enemigo nuevo que se presenta)
        assert director.costo_actual() <= director.presupuesto() + max(COSTO_ENEMIGO.values())
        for enemigo in fijos:
            assert DESBLOQUEO_ENEMIGO[enemigo.tipo] <= partida.nivel


def test_el_enemigo_recien_desbloqueado_se_presenta(partida):
    subir_hasta(partida, 3)
    assert "embestidor" in [e.tipo for e in partida.enemigos]


def test_el_sector_cambia_cada_2_niveles_y_nunca_se_repite_seguido(partida):
    random.seed(1)
    sectores = [partida.director.sector]
    assert sectores[0] is SECTORES[0]           # siempre se empieza en el Cinturon
    for nivel in range(2, 20):
        subir_hasta(partida, nivel)
        cambia = (nivel - 1) % SECTOR_CADA_NIVELES == 0
        assert (partida.director.sector is not sectores[-1]) == cambia
        sectores.append(partida.director.sector)
    assert len({s["nombre"] for s in sectores}) >= 4        # se ven sectores distintos


def test_al_cambiar_de_sector_se_van_algunos_enemigos(partida):
    subir_hasta(partida, 8)                 # con varios enemigos
    antes = list(partida.enemigos)
    partida.director.cambiar_sector()
    assert len([e for e in antes if e not in partida.enemigos]) == int(len(antes) * 0.34)


def preparar_oleada(partida):
    partida.nivel = 4
    partida.nave.invulnerable_hasta = math.inf
    partida.director.proxima_oleada = partida.tiempo


def test_oleada_llega_se_va_y_da_premio(partida):
    preparar_oleada(partida)
    jugar(partida)
    director = partida.director
    assert director.en_oleada
    de_oleada = [e for e in partida.enemigos if e.de_oleada]
    assert de_oleada
    puntaje = partida.puntaje
    jugar(partida, int(OLEADA_DURACION / MS_POR_FRAME) + 2)
    assert not director.en_oleada
    assert not any(e.de_oleada for e in partida.enemigos)       # se fueron
    assert partida.puntaje > puntaje                            # premio
    assert partida.proximo_powerup <= partida.tiempo            # y un power-up enseguida


def test_oleada_sin_premio_si_perdiste_una_vida(partida):
    preparar_oleada(partida)
    jugar(partida)
    partida.nave.invulnerable_hasta = 0
    partida.danar_jugador(*partida.nave.centro())
    partida.nave.invulnerable_hasta = math.inf
    puntaje = partida.puntaje
    jugar(partida, int(OLEADA_DURACION / MS_POR_FRAME) + 2)
    assert partida.puntaje == puntaje


def test_el_jefe_corta_la_oleada(partida):
    preparar_oleada(partida)
    jugar(partida)
    partida.iniciar_jefe()
    assert not partida.director.en_oleada
    assert not any(e.de_oleada for e in partida.enemigos_guardados)     # no vuelven despues
