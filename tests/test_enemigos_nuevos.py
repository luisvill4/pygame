"""Divisor y Enjambre: los enemigos que se destruyen con el dash."""
import math

import pytest

from juego.config import (DIVISOR_PUNTOS, ENJAMBRE_CANTIDAD, ENJAMBRE_PUNTOS, ENJAMBRE_BONUS,
                          RECARGA_POR_DESTRUIR, DIVISOR_NACIMIENTO, MS_POR_FRAME, CARTEL_JEFE, CARTEL_RANGO,
                          DASH_PERFECTO_PUNTOS, AVISO_ESCUADRON, ENTRADA_ESCUADRON)
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
    assert all(h.naciendo for h in hijos)                       # nacen parpadeando
    # Sus puntos y los del dash perfecto (romperlo con el dash lo es), y la recarga se adelanta
    assert partida.puntaje == DIVISOR_PUNTOS["divisor"] + DASH_PERFECTO_PUNTOS
    assert partida.estadisticas.perfectos == 1
    assert partida.nave.dash_listo <= recarga_antes - RECARGA_POR_DESTRUIR


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


def test_un_enjambre_son_varios_drones_con_una_bandada(partida):
    drones = crear_enemigos("enjambre", partida)
    assert len(drones) == ENJAMBRE_CANTIDAD
    assert len({id(d.bandada) for d in drones}) == 1


def test_el_enjambre_entra_volando_en_formacion(partida):
    # Un escuadron de un enjambre: los drones entran juntos y la bandada queda donde llegaron
    partida.director.con_escuadrones = True
    partida.nave.invulnerable_hasta = math.inf
    escuadron = partida.director.lanzar_escuadron(("enjambre", 1, "flanco"))
    assert len(escuadron.miembros) == ENJAMBRE_CANTIDAD
    jugar(partida, int((AVISO_ESCUADRON + ENTRADA_ESCUADRON) / MS_POR_FRAME) + 2)
    bandada = escuadron.miembros[0].bandada
    for dron in escuadron.miembros:
        assert dron.activo(partida.tiempo)
        centro_x, centro_y = dron.centro()
        assert math.hypot(centro_x - bandada.x, centro_y - bandada.y) < 80


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


def test_cartel_al_presentar_un_enemigo_nuevo(partida):
    # El divisor llega por primera vez en el tramo 2 del Cinturon
    partida.director.con_escuadrones = True
    partida.director.vistos = {"perseguidor"}
    partida.subir_nivel()
    partida.director.lanzar_escuadron()
    assert partida.director.nuevo_tipo is TIPOS_ENEMIGO["divisor"]
    assert any(e.tipo == "divisor" for e in partida.enemigos)


def test_dron_congelado_roto_justo_cuando_llega_el_jefe_no_vuelve(partida):
    # Bug viejo: un dron roto con el hielo justo cuando llegaba el jefe quedaba fuera de su
    # bandada y al volver despues del jefe el juego se caia. (Hoy es el objetivo cumplido)
    partida.nivel = 8
    partida.subir_nivel()                   # el tramo 4
    drones = crear_enemigos("enjambre", partida)
    partida.enemigos.extend(drones)
    partida.activar("hielo", 5000)
    roto = poner_encima(partida, drones[0])
    partida.director.cumplir_objetivo()
    jugar(partida)
    partida.iniciar_jefe()
    assert partida.jefe is not None
    assert partida.enemigos == []               # (los que quedaban explotaron)
    # Despues del jefe el sector nuevo empieza sin problema
    partida.desactivar("hielo")
    partida.nave.invulnerable_hasta = math.inf
    partida.jefe_vencido()
    partida.director.ofertas = []
    jugar(partida, int((CARTEL_JEFE + CARTEL_RANGO) / MS_POR_FRAME) + 30)
    assert roto not in partida.enemigos
    assert all(d in d.bandada.drones for d in partida.enemigos if d.tipo == "enjambre")
