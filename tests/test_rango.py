"""Rango del sector: las estrellas, la letra, el premio y el cierre del sector."""
import math

from juego.config import (RANGO_COMBO, RANGO_PUNTOS, RANGO_TIEMPO_JEFE, RANGO_SELLO, CARTEL_JEFE, CARTEL_RANGO,
                          MS_POR_FRAME, MONEDAS_POR_NIVEL)
from juego.enemigos import crear_enemigo
from juego.rango import Bitacora, calcular_rango
from tests.ayudas import jugar, avanzar, empezar_partida


def bitacora(golpes=0, combo=RANGO_COMBO, desafio=True, tiempo_jefe=10000):
    nueva = Bitacora()
    nueva.golpes, nueva.mejor_combo = golpes, combo
    nueva.desafio_cumplido, nueva.tiempo_jefe = desafio, tiempo_jefe
    return nueva


def test_perfecto_es_s():
    rango = calcular_rango(bitacora(), "ojo", 1)
    assert rango["letra"] == "S" and rango["estrellas"] == 5
    assert rango["puntos"] == RANGO_PUNTOS["S"]


def test_cada_cosa_resta_estrellas():
    assert calcular_rango(bitacora(golpes=1), "ojo", 1)["letra"] == "A"
    assert calcular_rango(bitacora(golpes=3), "ojo", 1)["letra"] == "B"
    assert calcular_rango(bitacora(golpes=3, combo=0, desafio=False), "ojo", 1)["letra"] == "C"
    lento = RANGO_TIEMPO_JEFE["ojo"] + 1000
    assert calcular_rango(bitacora(tiempo_jefe=lento), "ojo", 1)["letra"] == "A"


def test_en_la_segunda_vuelta_hay_mas_tiempo_para_el_jefe():
    un_poco_lento = RANGO_TIEMPO_JEFE["fortaleza"] * 1.1
    assert calcular_rango(bitacora(tiempo_jefe=un_poco_lento), "fortaleza", 1)["letra"] == "A"
    assert calcular_rango(bitacora(tiempo_jefe=un_poco_lento), "fortaleza", 2)["letra"] == "S"


def test_la_bitacora_anota_golpes_y_combo(partida):
    partida.activar("escudo", 10000)
    partida.danar_jugador(*partida.nave.centro())       # el escudo lo para, pero cuenta
    for _ in range(3):
        partida.moneda.x, partida.moneda.y = partida.nave.x + 15, partida.nave.y + 15
        jugar(partida)
    assert partida.director.bitacora.golpes == 1
    assert partida.director.bitacora.mejor_combo == 3


def test_al_vencer_al_jefe_sale_el_rango_y_despues_vuelven_los_enemigos(partida):
    partida.nave.invulnerable_hasta = math.inf
    director = partida.director
    partida.enemigos.append(crear_enemigo("perseguidor", partida))
    partida.iniciar_jefe()
    jugar(partida, 60)
    partida.jefe_vencido()
    rango = director.rango
    assert rango["sector"] == 1
    assert dict((fila[0], fila[1]) for fila in rango["filas"])["JEFE"] == "0:01"
    # Sin golpes (2), sin combo (0), sin desafio (0) y jefe rapido (1): B
    assert rango["letra"] == "B"
    puntos = partida.puntaje
    jugar(partida, int((CARTEL_JEFE + RANGO_SELLO) / MS_POR_FRAME) - 2)
    assert partida.puntaje == puntos                    # todavia no cayo la letra
    jugar(partida, 4)
    assert partida.puntaje == puntos + RANGO_PUNTOS["B"]
    # Los enemigos esperan a que se cierre el sector
    assert partida.enemigos == [] and director.cerrando_sector()
    jugar(partida, int((CARTEL_RANGO - RANGO_SELLO) / MS_POR_FRAME) + 2)
    assert not director.cerrando_sector()
    assert partida.enemigos


def test_mientras_se_cierra_el_sector_no_se_sube_de_nivel(partida):
    partida.nave.invulnerable_hasta = math.inf
    partida.iniciar_jefe()
    partida.jefe_vencido()
    partida.monedas_recogidas = MONEDAS_POR_NIVEL - 1
    nivel = partida.nivel
    partida.moneda.x, partida.moneda.y = partida.nave.x + 15, partida.nave.y + 15
    jugar(partida)
    assert partida.nivel == nivel


def test_se_dibuja_el_cartel(app):
    avanzar(app)
    partida = empezar_partida(app)
    partida.nave.invulnerable_hasta = math.inf
    partida.iniciar_jefe()
    partida.jefe_vencido()
    avanzar(app, int((CARTEL_JEFE + CARTEL_RANGO) / MS_POR_FRAME) + 10)
