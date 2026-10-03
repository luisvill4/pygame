"""Director de la progresion: presupuesto de enemigos, sectores y oleadas."""
import math
import random

from juego.config import (COSTO_ENEMIGO, DESBLOQUEO_ENEMIGO, ENEMIGOS_MAX, SECTORES, CARTEL_JEFE,
                          OLEADA_DURACION, MS_POR_FRAME, JEFE_CADA_NIVELES)
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


def test_cada_sector_termina_con_su_jefe_y_despues_viene_el_siguiente(partida):
    partida.nave.invulnerable_hasta = math.inf
    director = partida.director
    assert director.sector is SECTORES[0]       # siempre se empieza en el Cinturon
    for vuelta in range(len(SECTORES) + 1):
        sector = director.sector
        subir_hasta_el_jefe(partida)
        assert partida.jefe.tipo == sector["jefe"]
        assert director.sector is sector        # el sector no cambia durante la pelea
        partida.jefe_vencido()
        jugar(partida, int(CARTEL_JEFE / MS_POR_FRAME) + 2)
        siguiente = SECTORES[(vuelta + 1) % len(SECTORES)]
        assert director.sector is siguiente     # en orden, y despues del ultimo vuelve al primero
        assert director.numero_sector == vuelta + 2


def subir_hasta_el_jefe(partida):
    # Sube de nivel hasta que aparece el jefe (sin limpiar la pelea)
    partida.nivel = (partida.nivel // JEFE_CADA_NIVELES + 1) * JEFE_CADA_NIVELES - 1
    partida.subir_nivel()


def test_en_cada_sector_el_fondo_tiene_su_ambiente(app):
    fondo = app.fondo
    for sector in SECTORES:
        fondo.ir_a_sector(sector, instantaneo=True)
        for _ in range(400):
            fondo.mover()
        fondo.dibujar(app.pantalla)
        assert fondo.motas, sector["nombre"]


def test_al_cambiar_de_sector_se_van_algunos_enemigos(partida):
    subir_hasta(partida, 8)                 # con varios enemigos
    antes = list(partida.enemigos)
    grupos = {id(getattr(e, "bandada", e)) for e in antes}      # un enjambre se va entero
    partida.director.cambiar_sector()
    se_fueron = {id(getattr(e, "bandada", e)) for e in antes if e not in partida.enemigos}
    assert len(se_fueron) == int(len(grupos) * 0.34)


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
