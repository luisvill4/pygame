"""Divisor y Enjambre: los enemigos que se destruyen con el dash."""
import math

import pytest

from juego.config import (COSTO_ENEMIGO, DIVISOR_PUNTOS, ENJAMBRE_CANTIDAD, ENJAMBRE_PUNTOS, ENJAMBRE_BONUS,
                          RECARGA_POR_DESTRUIR, REFUERZO_ESPERA, DIVISOR_NACIMIENTO, MS_POR_FRAME,
                          CARTEL_JEFE)
from juego.enemigos import TIPOS_ENEMIGO, crear_enemigo, crear_enemigos
from tests.ayudas import jugar


def poner_encima(partida, enemigo):
    # El enemigo activo, quieto y justo encima de la nave
    enemigo.aparece_en = 0
    enemigo.naciendo = False
    nave_x, nave_y = partida.nave.centro()
    enemigo.x, enemigo.y = nave_x - enemigo.tamano / 2, nave_y - enemigo.tamano / 2
    enemigo.vx = enemigo.vy = 0
    if enemigo not in partida.enemigos:
        partida.enemigos.append(enemigo)
    return enemigo


def con_dash(partida):
    partida.nave.dash_hasta = partida.tiempo + 500


def test_estan_registrados():
    for tipo in ["divisor", "divisor_mediano", "divisor_chico", "enjambre"]:
        assert TIPOS_ENEMIGO[tipo].destruible


def test_el_dash_parte_al_divisor_en_dos(partida):
    divisor = poner_encima(partida, crear_enemigo("divisor", partida))
    partida.nave.dash_listo = partida.tiempo + 1500
    recarga_antes = partida.nave.dash_listo
    con_dash(partida)
    jugar(partida)
    assert divisor not in partida.enemigos
    hijos = [e for e in partida.enemigos if e.tipo == "divisor_mediano"]
    assert len(hijos) == 2
    assert all(h.costo == 0 and h.naciendo for h in hijos)     # no cuestan y nacen parpadeando
    assert partida.puntaje == DIVISOR_PUNTOS["divisor"]
    assert partida.nave.dash_listo == pytest.approx(recarga_antes - RECARGA_POR_DESTRUIR)


def test_los_hijos_recien_nacidos_no_hacen_dano(partida):
    divisor = poner_encima(partida, crear_enemigo("divisor", partida))
    con_dash(partida)
    jugar(partida)
    partida.nave.dash_hasta = 0
    for hijo in partida.enemigos:
        poner_encima(partida, hijo).aparece_en = partida.tiempo + DIVISOR_NACIMIENTO
    jugar(partida)
    assert partida.vidas == 3
    assert divisor not in partida.enemigos


def test_mediano_en_chicos_y_chico_desaparece(partida):
    mediano = poner_encima(partida, crear_enemigo("divisor_mediano", partida))
    con_dash(partida)
    jugar(partida)
    chicos = [e for e in partida.enemigos if e.tipo == "divisor_chico"]
    assert len(chicos) == 2 and mediano not in partida.enemigos
    partida.enemigos.clear()
    chico = poner_encima(partida, crear_enemigo("divisor_chico", partida))
    con_dash(partida)
    jugar(partida)
    assert partida.enemigos == [] and chico not in partida.enemigos


def test_sin_dash_el_divisor_pega_y_no_se_parte(partida):
    divisor = poner_encima(partida, crear_enemigo("divisor", partida))
    jugar(partida)
    assert partida.vidas == 2
    assert divisor in partida.enemigos and len(partida.enemigos) == 1     # reaparecio lejos


def test_congelado_se_rompe_entero(partida):
    poner_encima(partida, crear_enemigo("divisor", partida))
    partida.activar("hielo", 5000)
    jugar(partida)
    assert partida.enemigos == []                   # sin hijos


def test_los_enemigos_normales_no_se_destruyen_con_el_dash(partida):
    perseguidor = poner_encima(partida, crear_enemigo("perseguidor", partida))
    con_dash(partida)
    jugar(partida)
    assert perseguidor in partida.enemigos and partida.vidas == 3   # lo atraviesa


def test_un_enjambre_son_varios_drones_que_cuestan_como_uno(partida):
    drones = crear_enemigos("enjambre", partida)
    assert len(drones) == ENJAMBRE_CANTIDAD
    assert len({id(d.bandada) for d in drones}) == 1
    assert sum(d.costo for d in drones) == pytest.approx(COSTO_ENEMIGO["enjambre"])
    partida.enemigos.extend(drones)
    assert partida.director.cantidad_actual() == pytest.approx(1)


def test_el_dron_explota_al_chocarte(partida):
    drones = crear_enemigos("enjambre", partida)
    partida.enemigos.extend(drones)
    dron = poner_encima(partida, drones[0])
    jugar(partida)
    assert partida.vidas == 2
    assert dron not in partida.enemigos and dron not in dron.bandada.drones


def test_destruir_el_enjambre_entero_con_dash_da_bonus(partida):
    drones = crear_enemigos("enjambre", partida)
    partida.enemigos.extend(drones)
    for dron in drones:
        poner_encima(partida, dron)
        con_dash(partida)
        partida.destruir_con_dash(dron)
    assert partida.enemigos == []
    assert partida.puntaje == ENJAMBRE_CANTIDAD * ENJAMBRE_PUNTOS + ENJAMBRE_BONUS


def test_sin_bonus_si_alguno_murio_de_otra_forma(partida):
    drones = crear_enemigos("enjambre", partida)
    partida.enemigos.extend(drones)
    partida.destruir_enemigo(drones[0], con_dash=False)
    for dron in drones[1:]:
        partida.destruir_con_dash(dron)
    assert partida.puntaje == (ENJAMBRE_CANTIDAD - 1) * ENJAMBRE_PUNTOS


def test_el_enjambre_vuela_en_formacion_y_se_lanza_en_picada(partida):
    partida.nave.invulnerable_hasta = math.inf
    drones = crear_enemigos("enjambre", partida)
    partida.enemigos.extend(drones)
    bandada = drones[0].bandada
    fases = set()
    for _ in range(600):
        jugar(partida)
        fases.add(bandada.fase)
    assert {"volar", "aviso", "picada"} <= fases
    # Los drones vuelan cerca del centro de su bandada (en formacion)
    for dron in bandada.drones:
        centro_x, centro_y = dron.centro()
        assert math.hypot(centro_x - bandada.x, centro_y - bandada.y) < 80


def test_si_destruis_enemigos_llegan_refuerzos(partida):
    partida.nivel = 6
    partida.director.completar_presupuesto()
    costo_lleno = partida.director.costo_actual()
    for enemigo in list(partida.enemigos):
        partida.quitar_enemigo(enemigo)
    partida.nave.invulnerable_hasta = math.inf
    jugar(partida, int(REFUERZO_ESPERA / MS_POR_FRAME) * 2 + 5)
    assert 0 < partida.director.costo_actual() <= costo_lleno


def test_cartel_al_presentar_un_enemigo_nuevo(partida):
    partida.nivel = 3
    partida.subir_nivel()                   # nivel 4: aparece el divisor
    assert partida.director.nuevo_tipo is TIPOS_ENEMIGO["divisor"]
    assert any(e.tipo == "divisor" for e in partida.enemigos)


def test_el_enjambre_vuelve_junto_despues_del_jefe(partida):
    drones = crear_enemigos("enjambre", partida)
    partida.enemigos.extend(drones)
    partida.iniciar_jefe()                  # se guardan durante la pelea
    partida.nave.invulnerable_hasta = math.inf
    partida.jefe_vencido()
    jugar(partida, int(CARTEL_JEFE / MS_POR_FRAME) + 2)
    assert all(d in partida.enemigos for d in drones)
    bandada = drones[0].bandada
    for dron in drones:
        centro_x, centro_y = dron.centro()
        assert math.hypot(centro_x - bandada.x, centro_y - bandada.y) < 80
