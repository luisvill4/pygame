"""Ladron (roba la moneda y huye) y Escudero (escudo de frente que gira)."""
import math
import random

import pytest

from juego.config import (COMBO_TIEMPO, LADRON_BONUS, LADRON_PUNTOS, ESCUDERO_PUNTOS, ESCUDERO_GIRO,
                          DASH_PERFECTO_PUNTOS, ANCHO, ALTO, DIFICULTADES,
                          ENEMIGO_VELOCIDAD_MAX)
from juego.enemigos import TIPOS_ENEMIGO, crear_enemigo
from juego.rutas import RUTAS
from tests.ayudas import jugar


def poner(partida, enemigo, centro_x, centro_y):
    # El enemigo activo y quieto, con su centro en (centro_x, centro_y)
    enemigo.aparece_en = 0
    enemigo.naciendo = False
    enemigo.x, enemigo.y = centro_x - enemigo.tamano / 2, centro_y - enemigo.tamano / 2
    enemigo.vx = enemigo.vy = 0
    if enemigo not in partida.enemigos:
        partida.enemigos.append(enemigo)
    return enemigo


def poner_nave(partida, centro_x, centro_y):
    nave = partida.nave
    nave_x, nave_y = nave.centro()
    nave.x += centro_x - nave_x
    nave.y += centro_y - nave_y
    nave.vx = nave.vy = 0


def con_dash(partida):
    partida.nave.dash_hasta = partida.tiempo + 500


def ladron_con_la_moneda(partida, centro_x=500, centro_y=300):
    # Un ladron que ya atrapo la moneda y se queda quieto con ella (no huye). Mientras la
    # atrapa, la nave espera lejos (si no, la recogia ella)
    nave_x, nave_y = partida.nave.centro()
    poner_nave(partida, 60 if centro_x > ANCHO / 2 else ANCHO - 60, 60)
    ladron = poner(partida, crear_enemigo("ladron", partida), centro_x, centro_y)
    partida.moneda.x, partida.moneda.y = ladron.x + 10, ladron.y + 10
    jugar(partida)
    assert partida.moneda.robada_por is ladron
    poner_nave(partida, nave_x, nave_y)
    ladron.fase_hasta = math.inf
    return ladron


def con_combo(partida, combo=4):
    partida.combo = combo
    partida.ultima_moneda = partida.tiempo


# ---------- Ladron ----------

def test_el_ladron_va_hacia_la_moneda_y_la_roba(partida):
    poner_nave(partida, 100, 500)
    partida.moneda.x, partida.moneda.y = 600, 300
    ladron = poner(partida, crear_enemigo("ladron", partida), 450, 300)
    for _ in range(150):
        jugar(partida)
        if partida.moneda.robada_por is not None:
            break
    assert partida.moneda.robada_por is ladron
    assert ladron.fase == "atrapar"
    # Se la lleva encima de la cabeza
    jugar(partida)
    assert partida.moneda.centro()[0] == pytest.approx(ladron.centro()[0])
    assert partida.moneda.y < ladron.y


def test_el_ladron_no_lastima(partida):
    poner_nave(partida, 300, 300)
    ladron = poner(partida, crear_enemigo("ladron", partida), 300, 300)
    jugar(partida, 5)
    assert partida.vidas == partida.vidas_max
    assert ladron in partida.enemigos


def test_mientras_lleva_la_moneda_el_combo_espera(partida):
    ladron_con_la_moneda(partida)
    con_combo(partida)
    jugar(partida, int(COMBO_TIEMPO * 1.5 / (1000 / 60)))       # mucho mas que lo que dura el combo
    assert partida.combo == 4


def test_la_moneda_robada_no_se_agarra_y_el_iman_no_se_la_saca(partida):
    ladron = ladron_con_la_moneda(partida)
    partida.activar("iman", 5000)
    poner_nave(partida, *partida.moneda.centro())
    jugar(partida, 30)
    assert partida.estadisticas.monedas == 0
    assert partida.moneda.robada_por is ladron
    assert partida.moneda.centro()[0] == pytest.approx(ladron.centro()[0])


def test_alcanzarlo_con_el_dash_recupera_la_moneda_con_bonus(partida):
    ladron = ladron_con_la_moneda(partida)
    con_combo(partida)
    poner_nave(partida, *ladron.centro())
    con_dash(partida)
    jugar(partida)
    assert ladron not in partida.enemigos
    assert partida.moneda.robada_por is None
    assert partida.combo == 5                       # la moneda se cobra y el combo sigue
    assert partida.estadisticas.monedas == 1 and partida.estadisticas.recuperadas == 1
    assert partida.estadisticas.perfectos == 1      # es un dash perfecto
    moneda = partida.multiplicador_combo() + LADRON_BONUS
    perfecto = DASH_PERFECTO_PUNTOS * partida.multiplicador_combo()
    assert partida.puntaje == LADRON_PUNTOS + moneda + perfecto
    # La moneda aparece en otro lugar (no quedo donde estaba el ladron)
    assert math.hypot(partida.moneda.x - ladron.x, partida.moneda.y - ladron.y) > 30


def test_si_escapa_se_corta_el_combo_y_la_moneda_aparece_en_otro_lado(partida):
    poner_nave(partida, 800, 300)
    ladron = ladron_con_la_moneda(partida, 60, 300)
    con_combo(partida)
    ladron.fase_hasta = partida.tiempo          # que huya ya (al borde de la izquierda)
    for _ in range(120):
        jugar(partida)
        if ladron not in partida.enemigos:
            break
    assert ladron not in partida.enemigos
    assert partida.combo == 0
    assert partida.moneda.robada_por is None
    assert 0 <= partida.moneda.x <= ANCHO and 0 <= partida.moneda.y <= ALTO


def test_huye_al_borde_mas_cercano(partida):
    poner_nave(partida, 500, 300)
    ladron = ladron_con_la_moneda(partida, 900, 520)        # cerca de abajo
    ladron.fase_hasta = partida.tiempo
    jugar(partida, 20)
    assert ladron.huida == (0, 1)
    assert ladron.vy > 0


def test_si_sale_del_juego_por_otra_cosa_suelta_la_moneda_sin_castigo(partida):
    ladron = ladron_con_la_moneda(partida)
    con_combo(partida)
    ladron.retirarse(partida)           # (como al terminar su turno)
    assert partida.moneda.robada_por is None
    assert partida.combo == 4
    # Y si llega el jefe con la moneda robada, tambien la suelta
    otro = ladron_con_la_moneda(partida)
    partida.iniciar_jefe("ojo")
    assert partida.moneda.robada_por is None and otro not in partida.enemigos


def test_si_le_sacan_la_moneda_vuelve_a_buscarla_sin_cortar_el_combo(partida):
    ladron = ladron_con_la_moneda(partida)
    ladron.fase_hasta = partida.tiempo
    jugar(partida, 5)
    assert ladron.fase == "huir"
    con_combo(partida)
    partida.soltar_moneda()
    jugar(partida)
    assert ladron.fase == "buscar"
    ladron.x = -100                     # aunque ya estuviera saliendo de la pantalla
    jugar(partida)
    assert partida.combo == 4


def test_si_otro_ladron_ya_la_tiene_el_resto_deambula(partida):
    random.seed(2)                  # (deambular cambia de rumbo al azar)
    ladron_con_la_moneda(partida, 500, 300)
    otro = poner(partida, crear_enemigo("ladron", partida), 200, 300)
    jugar(partida, 60)
    assert otro.fase == "buscar"
    assert 0.1 < math.hypot(otro.vx, otro.vy) < 1   # pasea despacio, no va hacia la moneda


def test_huyendo_nunca_es_mas_rapido_que_la_nave(partida):
    # En PESADILLA y en el nivel 20 (lo mas rapido posible) igual se lo puede alcanzar
    partida.reglas = DIFICULTADES["PESADILLA"]
    partida.nivel = 20
    poner_nave(partida, 100, 300)
    ladron = ladron_con_la_moneda(partida, 700, 300)
    ladron.fase_hasta = partida.tiempo
    while ladron in partida.enemigos:
        jugar(partida)
        assert math.hypot(ladron.vx, ladron.vy) <= ENEMIGO_VELOCIDAD_MAX + 1e-9


# ---------- Escudero ----------

def escudero_mirando(partida, angulo, centro_x=330, centro_y=300):
    escudero = poner(partida, crear_enemigo("escudero", partida), centro_x, centro_y)
    escudero.angulo_escudo = angulo
    return escudero


def test_el_escudo_gira_despacio_hacia_la_nave(partida):
    poner_nave(partida, 60, 300)                        # lejos, a la izquierda del escudero
    escudero = escudero_mirando(partida, 0, 900)        # mirando a la derecha: le das la espalda
    jugar(partida)
    assert abs(escudero.angulo_escudo) == pytest.approx(math.radians(ESCUDERO_GIRO))
    jugar(partida, 130)
    assert abs(abs(escudero.angulo_escudo) - math.pi) < math.radians(5)     # termino mirandote


def test_el_dash_de_frente_rebota_sin_dano(partida):
    poner_nave(partida, 300, 300)
    escudero = escudero_mirando(partida, math.pi)       # mirando a la izquierda, hacia la nave
    con_dash(partida)
    jugar(partida)
    assert escudero in partida.enemigos
    assert partida.vidas == partida.vidas_max
    assert partida.estadisticas.perfectos == 0
    assert not partida.nave.en_dash(partida.tiempo)     # el dash se corto...
    assert partida.nave.vx < 0                          # ...y la nave rebota hacia atras
    jugar(partida, 10)
    assert partida.vidas == partida.vidas_max           # (y queda un rato invulnerable)


def test_el_dash_por_la_espalda_lo_rompe_y_es_perfecto(partida):
    poner_nave(partida, 300, 300)
    escudero = escudero_mirando(partida, 0)             # le da la espalda a la nave
    con_dash(partida)
    jugar(partida)
    assert escudero not in partida.enemigos
    assert partida.estadisticas.perfectos == 1
    assert partida.puntaje == ESCUDERO_PUNTOS + DASH_PERFECTO_PUNTOS


@pytest.mark.parametrize("angulo, bloquea", [(math.pi, True), (math.pi * 0.7, True), (math.pi / 2, False), (0, False)])
def test_el_escudo_cubre_solo_el_frente(partida, angulo, bloquea):
    escudero = escudero_mirando(partida, angulo)
    centro_x, centro_y = escudero.centro()
    assert escudero.bloquea_dash(centro_x - 50, centro_y) == bloquea         # un golpe desde la izquierda


def test_tocarlo_sin_dash_lastima(partida):
    poner_nave(partida, 330, 300)
    escudero_mirando(partida, 0)
    jugar(partida)
    assert partida.vidas == partida.vidas_max - 1


def test_las_ondas_de_frente_no_lo_rompen(partida):
    escudero = escudero_mirando(partida, math.pi)
    partida.onda_expansiva(300, 300, 100)               # desde la izquierda: contra el escudo
    assert escudero in partida.enemigos and escudero.aturdido(partida.tiempo)
    otro = escudero_mirando(partida, 0, 700, 300)
    partida.onda_expansiva(660, 300, 100)               # desde la izquierda: por la espalda
    assert otro not in partida.enemigos


# ---------- Los dos ----------

@pytest.mark.parametrize("tipo, sector", [("ladron", 3), ("escudero", 4)])
def test_aparecen_al_empezar_su_sector_con_su_ficha(partida, tipo, sector):
    # Es el primer escuadron del tramo 1 de su sector, y antes no aparece en ningun lado
    antes = {t for ruta in RUTAS[:sector - 1] for tramo in ruta for t, _, _ in tramo["escuadrones"]}
    assert tipo not in antes
    director = partida.director
    director.con_escuadrones = True
    director.vistos = {"perseguidor"}
    director.numero_sector = sector
    director.empezar_tramo()
    director.lanzar_escuadron()
    assert any(e.tipo == tipo for e in partida.enemigos)
    assert director.nuevo_tipo is TIPOS_ENEMIGO[tipo]


@pytest.mark.parametrize("tipo", ["ladron", "escudero"])
def test_se_dibujan_sin_sprite(partida, tipo, app):
    # Sin su sprite usan el dibujo de respaldo (y el escudo se dibuja encima)
    enemigo = poner(partida, crear_enemigo(tipo, partida), 300, 300)
    enemigo.dibujar(app.pantalla, partida)
    assert len(TIPOS_ENEMIGO[tipo].cuadros()) >= 1
