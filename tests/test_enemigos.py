"""Enemigos: registro, aparicion, separacion y el rango del embestidor."""
import math

import pytest

from juego.config import (ANCHO, RANGO_EMBESTIDOR, DISTANCIA_APARICION, COSTO_ENEMIGO, DESBLOQUEO_ENEMIGO, SECTORES,
                          DIFICULTADES, ENEMIGO_VELOCIDAD_MAX, NAVE_VELOCIDAD, ALTO, MS_CUADRO_REBOTE, MS_POR_FRAME,
                          ATURDIDO_ONDA)
from juego import recursos
from juego.enemigos import TIPOS_ENEMIGO, crear_enemigo
from juego.enemigos.rebotador import CHOQUE, PEGADO
from tests.ayudas import jugar


def test_todos_los_tipos_de_config_existen():
    usados = set(COSTO_ENEMIGO) | set(DESBLOQUEO_ENEMIGO) | {s["favorito"] for s in SECTORES}
    assert usados <= set(TIPOS_ENEMIGO)
    assert set(DESBLOQUEO_ENEMIGO) <= set(COSTO_ENEMIGO)


def test_enemigo_que_no_existe_avisa_claro(partida):
    with pytest.raises(ValueError, match="No existe el enemigo"):
        crear_enemigo("dragon", partida)


def test_aparecen_lejos_de_la_nave_y_con_aviso(partida):
    for _ in range(200):
        enemigo = crear_enemigo("perseguidor", partida)
        assert math.hypot(enemigo.x - partida.nave.x, enemigo.y - partida.nave.y) > DISTANCIA_APARICION
        assert not enemigo.activo(partida.tiempo)


def test_los_perseguidores_no_se_fusionan(partida):
    partida.enemigos[:] = [crear_enemigo("perseguidor", partida) for _ in range(3)]
    partida.enemigos.append(crear_enemigo("embestidor", partida))
    partida.nivel = 6
    minima = math.inf
    for frame in range(900):
        # La nave da vueltas en circulo
        t = frame / 60
        partida.nave.x = 375 + math.cos(t * 1.2) * 200
        partida.nave.y = 275 + math.sin(t * 1.2) * 180
        partida.nave.invulnerable_hasta = math.inf
        jugar(partida)
        if frame > 300:
            perseguidores = [e for e in partida.enemigos if e.tipo == "perseguidor"]
            for i, uno in enumerate(perseguidores):
                for otro in perseguidores[i + 1:]:
                    minima = min(minima, math.hypot(uno.x - otro.x, uno.y - otro.y))
    assert minima > 30


def poner_embestidor(partida, x, y):
    embestidor = crear_enemigo("embestidor", partida)
    embestidor.aparece_en = 0
    embestidor.fase_hasta = partida.tiempo + 2000
    embestidor.x, embestidor.y = x, y
    partida.enemigos.append(embestidor)
    return embestidor


def test_el_embestidor_no_sigue_si_estas_lejos(partida):
    partida.nave.x, partida.nave.y = 40, 280
    embestidor = poner_embestidor(partida, 700, 300)
    fases = set()
    for _ in range(480):
        jugar(partida)
        fases.add(embestidor.fase)
        assert embestidor.hacia_la_nave(partida)[2] > RANGO_EMBESTIDOR
    assert fases == {"acercarse"}


def test_el_embestidor_embiste_si_estas_cerca(partida):
    partida.nave.x, partida.nave.y = 375, 275
    partida.nave.invulnerable_hasta = math.inf
    embestidor = poner_embestidor(partida, 560, 280)
    fases = set()
    for _ in range(300):
        jugar(partida)
        fases.add(embestidor.fase)
    assert {"acercarse", "apuntar", "cargar"} <= fases


def test_el_rebotador_rebota_en_los_bordes(partida):
    rebotador = crear_enemigo("rebotador", partida)
    rebotador.aparece_en = 0
    rebotador.x, rebotador.y, rebotador.vx, rebotador.vy = ANCHO - 45, 300, 3, 0
    partida.enemigos.append(rebotador)
    partida.nave.invulnerable_hasta = math.inf
    jugar(partida, 3)
    assert rebotador.vx < 0


def _rebotador_en(partida, x, y, vx, vy):
    rebotador = crear_enemigo("rebotador", partida)
    rebotador.aparece_en = 0
    rebotador.x, rebotador.y, rebotador.vx, rebotador.vy = x, y, vx, vy
    partida.enemigos.append(rebotador)
    partida.nave.invulnerable_hasta = math.inf
    return rebotador


def test_el_rebotador_se_aplasta_contra_la_pared_y_vuelve_a_volar(partida):
    pared_x = ANCHO - 40
    rebotador = _rebotador_en(partida, pared_x - 2, 300, 3, 0)
    jugar(partida, 1)
    assert (rebotador.estado, rebotador.pared, rebotador.x) == ("choque", "derecha", pared_x)
    # Pegado a la pared durante los primeros PEGADO cuadros del choque
    while partida.tiempo - rebotador.inicio_choque < PEGADO * MS_CUADRO_REBOTE - 20:
        jugar(partida)
        assert rebotador.x == pared_x
    # Despues sale con la velocidad ya invertida...
    jugar(partida, 3)
    assert rebotador.x < pared_x and rebotador.estado == "choque"
    # ...y al terminar la animacion vuelve a volar
    jugar(partida, round(len(CHOQUE) * MS_CUADRO_REBOTE / MS_POR_FRAME))
    assert rebotador.estado == "volando"


def test_el_rebotador_reinicia_el_choque_si_toca_otra_pared(partida):
    # En una esquina: toca la derecha, sale y enseguida toca el piso
    rebotador = _rebotador_en(partida, ANCHO - 41, ALTO - 60, 3, 3)
    jugar(partida, 1)
    assert rebotador.pared == "derecha"
    primer_choque = rebotador.inicio_choque
    for _ in range(40):
        jugar(partida)
        if rebotador.pared == "abajo":
            break
    assert rebotador.pared == "abajo" and rebotador.estado == "choque"
    assert rebotador.inicio_choque > primer_choque


def test_la_hoja_del_rebotador_tiene_una_fila_por_pared():
    filas = TIPOS_ENEMIGO["rebotador"].cuadros_por_pared()
    assert sorted(filas) == ["abajo", "arriba", "derecha", "izquierda"]
    for cuadros in filas.values():
        assert len(cuadros) == 8 and all(c.get_size() == (40, 40) for c in cuadros)
    # La ficha del HUD y el congelado siguen usando cuadros de 40x40
    assert TIPOS_ENEMIGO["rebotador"].cuadros()[0].get_size() == (40, 40)


def test_el_rebotador_queda_pegado_justo_en_las_columnas_1_a_3():
    assert set(CHOQUE[:PEGADO]) == {1, 2, 3} and CHOQUE[PEGADO] == 4
    assert CHOQUE[-1] == 7


def test_el_vuelo_del_rebotador_sin_su_sprite_es_la_columna_0(monkeypatch):
    rebotador = TIPOS_ENEMIGO["rebotador"]
    # Con rebotador_vuelo.png: sus cuadros de 40x40
    for cuadro in rebotador.cuadros():
        assert cuadro.get_size() == (40, 40)
    # Sin el archivo: un solo cuadro, la columna 0 de la hoja (vuela quieto)
    monkeypatch.setattr(recursos, "hoja", lambda archivo, ancho: None)
    assert rebotador.cuadros() == [rebotador.cuadros_por_pared()["abajo"][0]]


def test_el_rebotador_aturdido_por_una_onda_vuelve_a_rebotar(partida):
    # Antes la onda lo dejaba con velocidad 0 y se quedaba quieto para siempre
    rebotador = _rebotador_en(partida, 400, 300, 3, 3)
    partida.onda_expansiva(380, 360, 200)     # abajo a la izquierda de su centro (420, 320)
    assert rebotador.aturdido(partida.tiempo)
    jugar(partida, round(ATURDIDO_ONDA / MS_POR_FRAME) + 1)
    antes_x, antes_y = rebotador.x, rebotador.y
    jugar(partida, 10)
    assert math.hypot(rebotador.x - antes_x, rebotador.y - antes_y) > 20
    # Sale lejos de la onda (hacia la derecha y arriba) con la rapidez que traia
    assert rebotador.vx > 0 and rebotador.vy < 0
    assert math.hypot(rebotador.vx, rebotador.vy) == pytest.approx(math.hypot(3, 3))


@pytest.mark.parametrize("tipo", ["perseguidor", "rebotador", "divisor_chico"])
def test_ninguno_te_persigue_mas_rapido_que_la_nave(partida, tipo):
    # En PESADILLA y en el nivel 20 (lo mas rapido posible) la nave igual puede escaparse
    partida.reglas = DIFICULTADES["PESADILLA"]
    partida.nivel = 20
    partida.nave.invulnerable_hasta = math.inf
    enemigo = crear_enemigo(tipo, partida)
    enemigo.aparece_en = 0
    partida.enemigos.append(enemigo)
    for paso in range(400):
        # La nave da vueltas, asi el enemigo la persigue en todas las direcciones
        jugar(partida, dx=math.cos(paso / 40), dy=math.sin(paso / 40))
        rapidez = math.hypot(enemigo.vx, enemigo.vy) * enemigo.paso(partida)
        assert rapidez <= ENEMIGO_VELOCIDAD_MAX + 1e-9
    assert ENEMIGO_VELOCIDAD_MAX < NAVE_VELOCIDAD


@pytest.mark.parametrize("dificultad", ["FACIL", "NORMAL", "DIFICIL"])
def test_en_las_dificultades_faciles_la_mira_del_embestidor_se_fija_antes(partida, dificultad):
    # El embestidor apunta hacia abajo y, justo antes de embestir, la nave se corre a un costado
    partida.reglas = DIFICULTADES[dificultad]
    partida.nave.invulnerable_hasta = math.inf
    partida.nave.x, partida.nave.y = 375, 380           # centro de la nave: (400, 405)
    embestidor = poner_embestidor(partida, 380, 180)    # centro: (400, 200), justo arriba
    embestidor.fase_hasta = partida.tiempo              # que apunte ya
    while embestidor.fase != "apuntar":
        jugar(partida)
    while partida.tiempo < embestidor.fase_hasta - 150:
        jugar(partida)
    partida.nave.x += 150
    while embestidor.fase == "apuntar":
        jugar(partida)
    if DIFICULTADES[dificultad]["apunte_fijo"] > 150:
        assert abs(embestidor.vx) < 0.5     # embiste hacia donde estabas: derecho hacia abajo
    else:
        assert embestidor.vx > 3            # te sigue hasta el ultimo momento
    assert embestidor.vy > 0
