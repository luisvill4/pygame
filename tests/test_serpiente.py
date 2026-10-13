"""La Serpiente: el cuerpo que la sigue, la mordida, la cola que se corta y el enrosque."""
import math

import pytest

from juego.config import ANCHO, SERPIENTE_ESPACIO, SERPIENTE_CUELLO, MS_POR_FRAME
from juego.jefes import crear_jefe
from tests.ayudas import jugar, avanzar, empezar_partida


def llegar_a_la_serpiente(partida):
    partida.jefes_vencidos = 2
    jefe = crear_jefe("serpiente", partida)
    partida.jefe = jefe
    jefe.x, jefe.y = 300, 250
    jefe.al_terminar_de_entrar(partida)
    partida.nave.invulnerable_hasta = math.inf
    return jefe


def dash_contra(partida, x, y):
    partida.nave.x, partida.nave.y = x - 25, y - 25
    partida.nave.dash_hasta = partida.tiempo + 500


def test_tiene_un_segmento_por_corte_mas_el_cuello(partida):
    jefe = llegar_a_la_serpiente(partida)
    assert len(jefe.segmentos) == jefe.vida_max + SERPIENTE_CUELLO
    assert jefe.vida_barra() == (jefe.vida_max, jefe.vida_max)


def test_el_cuerpo_la_sigue_como_una_cuerda(partida):
    jefe = llegar_a_la_serpiente(partida)
    jugar(partida, 300)
    anterior = jefe.centro()
    for segmento in jefe.segmentos:
        assert math.hypot(segmento.x - anterior[0], segmento.y - anterior[1]) <= SERPIENTE_ESPACIO + 0.01
        anterior = (segmento.x, segmento.y)


def test_el_cuerpo_hace_dano(partida):
    jefe = llegar_a_la_serpiente(partida)
    partida.nave.invulnerable_hasta = 0
    segmento = jefe.segmentos[3]
    partida.nave.x, partida.nave.y = segmento.x - 25, segmento.y - 25
    partida._choques_jefe()
    assert partida.vidas == partida.vidas_max - 1


def test_la_mordida_queda_fija_en_el_ultimo_pulso(partida):
    jefe = llegar_a_la_serpiente(partida)
    jefe.cambiar_fase_pulsos("acechar", 2, partida.tiempo)
    while jefe.pulso < 1:
        jugar(partida)
    fija = jefe.mordida
    partida.nave.x = 20 if partida.nave.x > 400 else 700        # la nave se corre...
    while jefe.fase == "acechar":
        jugar(partida)
    assert jefe.mordida == fija                                  # ...y la mordida no la sigue
    assert jefe.fase == "morder"
    assert jefe.angulo == pytest.approx(fija, abs=1e-6)


def test_al_chocar_con_un_borde_queda_aturdida_y_la_cola_se_puede_cortar(partida):
    jefe = llegar_a_la_serpiente(partida)
    assert not jefe.puede_recibir_golpe()
    jefe.x, jefe.y = ANCHO - 200, 300
    jefe.angulo = jefe.mordida = 0              # hacia la derecha: se estrella enseguida
    jefe.recorrido = 0
    jefe.cambiar_fase("morder", 5000, partida.tiempo)
    jugar(partida, 30)
    assert jefe.fase == "aturdida"
    assert jefe.puede_recibir_golpe()
    largo = len(jefe.segmentos)
    dash_contra(partida, *jefe.centro_nucleo())
    partida._choques_jefe()
    assert len(jefe.segmentos) == largo - 1     # se corto el cascabel
    assert jefe.vida == jefe.vida_max - 1
    assert jefe.fase == "nadar"


def test_cada_corte_la_acelera(partida):
    jefe = llegar_a_la_serpiente(partida)
    antes, pulso_antes = jefe.factor(), jefe.ms_pulso
    jefe.vida -= 2
    jefe.empezar_a_nadar(partida)
    assert jefe.factor() > antes
    assert jefe.ms_pulso < pulso_antes


def test_desde_el_segundo_corte_tambien_se_enrosca(partida):
    jefe = llegar_a_la_serpiente(partida)
    ataques = set()
    for _ in range(4):
        jefe.elegir_ataque(partida)
        ataques.add(jefe.fase)
    assert ataques == {"acechar"}
    jefe.vida -= 2
    for _ in range(4):
        jefe.elegir_ataque(partida)
        ataques.add(jefe.fase)
    assert ataques == {"acechar", "enroscarse"}


def test_el_enrosque_se_cierra_alrededor_de_donde_estabas(partida):
    jefe = llegar_a_la_serpiente(partida)
    jefe.vida -= 2
    jefe.ultimo_ataque = "morder"
    jefe.elegir_ataque(partida)
    centro = jefe.centro_enrosque
    radios = []
    while jefe.fase == "enroscarse":
        jugar(partida)
        cabeza = jefe.centro()
        radios.append(math.hypot(cabeza[0] - centro[0], cabeza[1] - centro[1]))
    assert radios[-1] < radios[len(radios) // 3] < 260
    assert radios[-1] < 60                      # al final aprieta
    assert jefe.fase == "mareada"


def test_escupe_veneno_solo_desde_la_mitad(partida):
    jefe = llegar_a_la_serpiente(partida)
    jugar(partida, int(6 * jefe.ms_pulso / MS_POR_FRAME))
    assert not partida.balas
    jefe.vida = jefe.vida_max // 2
    jefe.empezar_a_nadar(partida)
    jugar(partida, int(5 * jefe.ms_pulso / MS_POR_FRAME))
    assert 1 <= len(partida.balas) <= 2


def test_una_pelea_entera_se_puede_ganar(partida):
    jefe = llegar_a_la_serpiente(partida)
    for _ in range(60 * 240):
        if partida.jefe is None:
            break
        if jefe.puede_recibir_golpe():
            dash_contra(partida, *jefe.centro_nucleo())
        jugar(partida)
        partida.nave.invulnerable_hasta = math.inf
    assert partida.jefe is None


def test_se_dibuja_en_todas_sus_fases(app):
    avanzar(app)
    partida = empezar_partida(app)
    jefe = llegar_a_la_serpiente(partida)
    jefe.centro_enrosque = (400, 300)
    for fase in ("nadar", "acechar", "morder", "enroscarse", "aturdida", "mareada", "morir"):
        jefe.cambiar_fase(fase, 5000, partida.tiempo)
        avanzar(app, 5)
    partida.activar("hielo", 3000)
    jefe.cambiar_fase("nadar", 5000, partida.tiempo)
    avanzar(app, 3)
