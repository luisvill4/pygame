"""Desafios: cuando se proponen, como se cumplen o se fallan, y el premio."""
import math

from juego.config import (DESAFIO_ESPERA, DESAFIO_PUNTOS, DESAFIO_COMBO, DESAFIO_CAZADOR, COMBO_TIEMPO,
                          CARTEL_JEFE, CARTEL_RANGO, MS_POR_FRAME, JEFE_CADA_NIVELES)
from juego.desafios import TIPOS_DESAFIO
from juego.enemigos import crear_enemigo
from juego.powerups import TIPOS_POWERUP, Capsula
from tests.ayudas import jugar, avanzar, empezar_partida


def poner(partida, tipo):
    director = partida.director
    director.con_desafios = True
    director.desafio = TIPOS_DESAFIO[tipo]()
    return director.desafio


def recoger_moneda(partida):
    partida.moneda.x, partida.moneda.y = partida.nave.x + 15, partida.nave.y + 15
    jugar(partida)


def test_se_propone_en_el_nivel_2_y_al_llegar_a_cada_sector(partida):
    director = partida.director
    director.con_desafios = True
    partida.nave.invulnerable_hasta = math.inf
    partida.subir_nivel()                           # nivel 2
    jugar(partida, int(DESAFIO_ESPERA / MS_POR_FRAME) + 2)
    primero = director.desafio
    assert primero is not None and primero.en_curso()
    # Al vencer al jefe se cierra el sector; en el siguiente llega otro desafio (distinto)
    partida.nivel = JEFE_CADA_NIVELES - 1
    partida.subir_nivel()
    partida.jefe_vencido()
    assert director.desafio is None
    jugar(partida, int((CARTEL_JEFE + CARTEL_RANGO + DESAFIO_ESPERA) / MS_POR_FRAME) + 2)
    assert director.desafio is not None
    assert director.desafio.tipo != primero.tipo


def test_sin_dash_se_falla_al_usarlo(partida):
    desafio = poner(partida, "sin_dash")
    jugar(partida, dash=True)
    assert desafio.estado == "fallado"
    partida.iniciar_jefe()
    assert desafio.estado == "fallado"              # llegar al jefe ya no lo arregla
    assert partida.puntaje == 0


def test_llegar_al_jefe_cumple_los_de_aguantar_y_da_premio(partida):
    desafio = poner(partida, "sin_dash")
    jugar(partida, 30)
    partida.iniciar_jefe()
    assert desafio.estado == "cumplido"
    assert partida.puntaje == DESAFIO_PUNTOS * partida.director.numero_sector
    assert partida.director.bitacora.desafio_cumplido
    assert partida.proximo_powerup == partida.tiempo     # un power-up de regalo, enseguida


def test_intocable_se_falla_con_un_golpe_aunque_lo_pare_el_escudo(partida):
    desafio = poner(partida, "intocable")
    partida.activar("escudo", 10000)
    partida.danar_jugador(*partida.nave.centro())
    assert desafio.estado == "fallado"


def test_sin_ayuda_se_falla_al_agarrar_un_power_up(partida):
    desafio = poner(partida, "sin_ayuda")
    nave_x, nave_y = partida.nave.centro()
    partida.capsula = Capsula(TIPOS_POWERUP["escudo"], nave_x)
    partida.capsula.y = nave_y
    jugar(partida)
    assert desafio.estado == "fallado"


def test_sin_cortar_el_combo(partida):
    desafio = poner(partida, "combo")
    for _ in range(5):
        recoger_moneda(partida)
    assert desafio.progreso == 5
    jugar(partida, int(COMBO_TIEMPO / MS_POR_FRAME) + 5)     # se corta el combo...
    recoger_moneda(partida)
    assert desafio.progreso == 1                    # ...y vuelve a empezar
    for _ in range(DESAFIO_COMBO - 1):
        recoger_moneda(partida)
    assert desafio.estado == "cumplido"
    assert desafio.texto_progreso() == str(DESAFIO_COMBO) + "/" + str(DESAFIO_COMBO)


def test_cazador_solo_cuando_hay_enemigos_destruibles(partida):
    # Depende de los enemigos que trae el sector
    partida.director.tipos_del_sector = lambda: {"perseguidor", "rebotador"}
    assert not TIPOS_DESAFIO["cazador"].disponible(partida)
    partida.director.tipos_del_sector = lambda: {"perseguidor", "divisor"}
    assert TIPOS_DESAFIO["cazador"].disponible(partida)
    desafio = poner(partida, "cazador")
    for _ in range(DESAFIO_CAZADOR):
        chico = crear_enemigo("divisor_chico", partida)
        partida.enemigos.append(chico)
        partida.destruir_con_dash(chico)
    assert desafio.estado == "cumplido"


def test_los_de_lograr_se_fallan_si_llega_el_jefe_antes(partida):
    desafio = poner(partida, "combo")
    recoger_moneda(partida)
    partida.iniciar_jefe()
    assert desafio.estado == "fallado"


def test_se_dibuja_la_ficha_y_el_progreso(app):
    avanzar(app)
    partida = empezar_partida(app)
    partida.nave.invulnerable_hasta = math.inf
    director = partida.director
    for tipo in TIPOS_DESAFIO:
        director.desafio = TIPOS_DESAFIO[tipo]()
        director.tiempo_cartel_desafio = partida.tiempo
        avanzar(app, 30)
        director.desafio.estado = "cumplido"
        avanzar(app, 5)
        director.desafio.estado = "fallado"
        avanzar(app, 5)
