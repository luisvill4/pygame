"""Enemigos: registro, aparicion, separacion y el rango del embestidor."""
import math

import pytest

from juego.config import RANGO_EMBESTIDOR, DISTANCIA_APARICION, ENEMIGOS_POR_NIVEL, ENEMIGOS_POR_JEFE
from juego.enemigos import TIPOS_ENEMIGO, crear_enemigo
from tests.ayudas import jugar


def test_todos_los_tipos_de_config_existen():
    usados = set(ENEMIGOS_POR_NIVEL.values()) | set(ENEMIGOS_POR_JEFE)
    assert usados <= set(TIPOS_ENEMIGO)


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
    rebotador.x, rebotador.y, rebotador.vx, rebotador.vy = 755, 300, 3, 0
    partida.enemigos.append(rebotador)
    partida.nave.invulnerable_hasta = math.inf
    jugar(partida, 3)
    assert rebotador.vx < 0
