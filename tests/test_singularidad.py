"""La Singularidad: gravedad, el anillo que gira a ritmo, la nova y el nucleo."""
import math

import pytest

from juego.config import SINGULARIDAD_HUECOS, SINGULARIDAD_RADIO, MS_POR_FRAME
from juego.jefes import crear_jefe
from juego.jefes.singularidad import LUGARES
from tests.ayudas import jugar, avanzar, empezar_partida


def llegar_a_la_singularidad(partida):
    partida.jefes_vencidos = 4
    jefe = crear_jefe("singularidad", partida)
    partida.jefe = jefe
    jefe.escala = 1
    jefe.radio_anillo = SINGULARIDAD_RADIO
    jefe.ubicar_asteroides()
    jefe.al_terminar_de_entrar(partida)
    partida.nave.invulnerable_hasta = math.inf
    partida.nave.x, partida.nave.y = 40, 500
    return jefe


def jugar_hasta(partida, jefe, fase, maximo=60 * 30):
    for _ in range(maximo):
        if jefe.fase == fase:
            return
        jugar(partida)
    raise AssertionError("nunca llego a " + fase)


def test_el_anillo_tiene_paredes_y_huecos(partida):
    jefe = llegar_a_la_singularidad(partida)
    assert len(jefe.asteroides) == LUGARES - SINGULARIDAD_HUECOS
    # Entre dos asteroides vecinos no pasa la nave (su circulo de daño mide 22 px)
    a, b = jefe.asteroides[0], jefe.asteroides[1]
    separacion = math.hypot(a.x - b.x, a.y - b.y) - 30
    assert separacion < 22


def test_te_atrae_pero_el_dash_no_lo_siente(partida):
    jefe = llegar_a_la_singularidad(partida)
    nave = partida.nave
    nave.vx = nave.vy = 0
    jefe.atraer(partida, 0.2)
    centro_x, centro_y = jefe.centro()
    nave_x, nave_y = nave.centro()
    assert nave.vx * (centro_x - nave_x) > 0 and nave.vy * (centro_y - nave_y) > 0
    nave.vx = nave.vy = 0
    nave.dash_hasta = partida.tiempo + 500
    jefe.atraer(partida, 0.2)
    assert nave.vx == nave.vy == 0


def test_el_anillo_gira_de_a_un_lugar_por_pulso(partida):
    jefe = llegar_a_la_singularidad(partida)
    jugar(partida, 2)                           # el pulso 0 (al empezar la fase) ya lo movio
    inicio = jefe.objetivo_anillo
    jugar(partida, int(4 * jefe.ms_pulso / MS_POR_FRAME))
    assert abs(jefe.objetivo_anillo - inicio) == 4


def test_la_nova_deja_el_hueco_que_avisa(partida):
    jefe = llegar_a_la_singularidad(partida)
    jugar_hasta(partida, jefe, "inhalar")
    hueco = jefe.hueco_nova
    partida.balas.clear()
    jugar_hasta(partida, jefe, "exhalar")
    nova = partida.balas[-len(jefe.direcciones_nova()):]
    for bala in nova:
        angulo = math.atan2(bala.vy, bala.vx)
        assert abs((angulo - hueco + math.pi) % (2 * math.pi) - math.pi) > math.radians(44)


def test_solo_se_le_pega_con_el_nucleo_expuesto(partida):
    jefe = llegar_a_la_singularidad(partida)
    assert not jefe.puede_recibir_golpe()
    jugar_hasta(partida, jefe, "expuesta")
    assert jefe.puede_recibir_golpe()
    angulo_antes = jefe.objetivo_anillo
    jugar(partida, 30)
    assert jefe.objetivo_anillo == angulo_antes         # quieto: se puede entrar por un hueco
    partida.nave.x, partida.nave.y = jefe.centro()[0] - 25, jefe.centro()[1] - 25
    partida.nave.dash_hasta = partida.tiempo + 500
    partida._choques_jefe()
    assert jefe.vida == jefe.vida_max - 1
    assert jefe.fase == "estallido"
    assert math.hypot(partida.nave.vx, partida.nave.vy) > 8     # la onda te saca afuera


def test_cada_dos_golpes_un_hueco_menos(partida):
    jefe = llegar_a_la_singularidad(partida)
    jefe.vida -= 2
    jefe.armar_anillo()
    assert len(jefe.asteroides) == LUGARES - (SINGULARIDAD_HUECOS - 1)
    assert len(jefe.angulos_huecos()) == SINGULARIDAD_HUECOS - 1


def test_se_come_la_moneda(partida):
    jefe = llegar_a_la_singularidad(partida)
    centro_x, centro_y = jefe.centro()
    partida.moneda.x, partida.moneda.y = centro_x - 10, centro_y - 10
    jefe.comer_moneda(partida)
    moneda_x, moneda_y = partida.moneda.centro()
    assert math.hypot(moneda_x - centro_x, moneda_y - centro_y) > SINGULARIDAD_RADIO   # afuera del anillo


def test_mientras_nace_no_lastima(partida):
    partida.jefes_vencidos = 4
    jefe = crear_jefe("singularidad", partida)
    partida.jefe = jefe
    assert jefe.fase == "entrar"
    assert jefe.cajas_danio() == []
    for _ in range(60 * 5):
        jugar(partida)
        if jefe.fase != "entrar":
            break
    assert jefe.fase == "girar"
    assert jefe.radio_anillo == pytest.approx(SINGULARIDAD_RADIO, abs=20)


def test_una_pelea_entera_se_puede_ganar(partida):
    jefe = llegar_a_la_singularidad(partida)
    for _ in range(60 * 240):
        if partida.jefe is None:
            break
        if jefe.puede_recibir_golpe():
            partida.nave.x, partida.nave.y = jefe.centro()[0] - 25, jefe.centro()[1] - 25
            partida.nave.dash_hasta = partida.tiempo + 500
        jugar(partida)
        partida.nave.invulnerable_hasta = math.inf
    assert partida.jefe is None


def test_se_dibuja_en_todas_sus_fases(app):
    avanzar(app)
    partida = empezar_partida(app)
    jefe = llegar_a_la_singularidad(partida)
    for fase in ("girar", "inhalar", "exhalar", "colapsar", "expuesta", "estallido", "morir"):
        jefe.cambiar_fase(fase, 5000, partida.tiempo)
        avanzar(app, 5)
