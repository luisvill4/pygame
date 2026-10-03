"""La Colmena: compuertas, abejas, la embestida con rebotes y el ojo de la reina."""
import math

from juego.config import COLMENA_ABEJAS, COLMENA_ABEJAS_MAX, COLMENA_REBOTES, MS_POR_FRAME
from juego.jefes import crear_jefe
from tests.ayudas import jugar, avanzar, empezar_partida


def llegar_a_la_colmena(partida):
    partida.jefes_vencidos = 3
    jefe = crear_jefe("colmena", partida)
    partida.jefe = jefe
    jefe.y = jefe.y_final
    jefe.al_terminar_de_entrar(partida)
    partida.nave.invulnerable_hasta = math.inf
    return jefe


def abejas(partida):
    return [e for e in partida.enemigos if e.tipo == "abeja"]


def dash_contra(partida, x, y):
    partida.nave.x, partida.nave.y = x - 25, y - 25
    partida.nave.dash_hasta = partida.tiempo + 500


def jugar_hasta(partida, jefe, fase, maximo=60 * 30):
    for _ in range(maximo):
        if jefe.fase == fase:
            return
        jugar(partida)
    raise AssertionError("nunca llego a " + fase)


def sin_compuertas(partida, jefe):
    for compuerta in jefe.partes:
        compuerta.abierta = True
        jefe.golpear_parte(partida, compuerta)


def test_tiene_cuatro_compuertas_y_la_barra_las_suma(partida):
    jefe = llegar_a_la_colmena(partida)
    assert len(jefe.partes) == 4
    assert jefe.vida_barra() == (jefe.vida_max + 4, jefe.vida_max + 4)


def test_abre_una_compuerta_suelta_abejas_a_ritmo_y_la_deja_abierta(partida):
    jefe = llegar_a_la_colmena(partida)
    jugar_hasta(partida, jefe, "soltar")
    salidas = []
    while jefe.fase == "soltar":
        antes = len(abejas(partida))
        jugar(partida)
        if len(abejas(partida)) > antes:
            salidas.append(partida.tiempo)
    assert len(salidas) == COLMENA_ABEJAS
    for anterior, siguiente in zip(salidas, salidas[1:]):
        assert abs(siguiente - anterior - jefe.ms_pulso) <= MS_POR_FRAME
    assert jefe.fase == "expuesta"
    abiertas = [c for c in jefe.partes if c.abierta]
    assert abiertas == jefe.elegidas and len(abiertas) == 1


def test_la_compuerta_solo_se_rompe_abierta_y_las_abejas_se_enojan(partida):
    jefe = llegar_a_la_colmena(partida)
    compuerta = jefe.partes[0]
    dash_contra(partida, *compuerta.centro(jefe))
    partida._choques_jefe()
    assert compuerta.viva()                     # cerrada: el dash la atraviesa
    jugar_hasta(partida, jefe, "expuesta")
    abierta = jefe.elegidas[0]
    for abeja in abejas(partida):
        abeja.estado = "rondar"
        abeja.proxima_picada = partida.tiempo + 99999
    dash_contra(partida, *abierta.centro(jefe))
    partida._choques_jefe()
    assert not abierta.viva()
    assert all(abeja.proxima_picada <= partida.tiempo for abeja in abejas(partida))


def test_nunca_hay_demasiadas_abejas(partida):
    jefe = llegar_a_la_colmena(partida)
    for _ in range(60 * 40):
        jugar(partida)
        partida.nave.invulnerable_hasta = math.inf
        assert len(abejas(partida)) <= COLMENA_ABEJAS_MAX


def test_sin_compuertas_llama_a_las_abejas_y_embiste(partida):
    jefe = llegar_a_la_colmena(partida)
    jugar_hasta(partida, jefe, "expuesta")
    assert abejas(partida)
    sin_compuertas(partida, jefe)
    assert jefe.fase == "enfurecerse"
    assert all(not abeja.hace_danio() for abeja in abejas(partida))     # vuelven a casa sin lastimar
    jugar_hasta(partida, jefe, "temblar")
    assert not abejas(partida)                  # en la embestida no hay abejas: una sola cosa por vez


def test_el_aviso_muestra_justo_los_rebotes_que_hace(partida):
    jefe = llegar_a_la_colmena(partida)
    sin_compuertas(partida, jefe)
    jugar_hasta(partida, jefe, "temblar")
    while jefe.fase == "temblar":
        avisados = jefe.camino()                # el ultimo aviso antes de embestir
        jugar(partida)
    assert jefe.rebotes == COLMENA_REBOTES
    reales = [jefe.centro()]
    while jefe.fase == "embestir":
        antes = (jefe.vx, jefe.vy)
        jugar(partida)
        if (jefe.vx, jefe.vy) != antes:
            reales.append(jefe.centro())
    assert jefe.fase == "aturdida"
    assert len(reales) == len(avisados) == COLMENA_REBOTES + 2
    for real, avisado in zip(reales, avisados):
        assert math.hypot(real[0] - avisado[0], real[1] - avisado[1]) < 1


def test_aturdida_se_le_pega_en_el_ojo_y_despues_rebota_mas(partida):
    jefe = llegar_a_la_colmena(partida)
    sin_compuertas(partida, jefe)
    jugar_hasta(partida, jefe, "aturdida")
    assert jefe.puede_recibir_golpe()
    dash_contra(partida, *jefe.centro_nucleo())
    partida._choques_jefe()
    assert jefe.vida == jefe.vida_max - 1
    assert jefe.fase == "volver"
    jugar_hasta(partida, jefe, "temblar")
    assert jefe.rebotes == COLMENA_REBOTES + 1


def test_las_abejas_se_van_cuando_vences_a_la_colmena(partida):
    jefe = llegar_a_la_colmena(partida)
    jugar_hasta(partida, jefe, "expuesta")
    assert abejas(partida)
    partida.jefe_vencido()
    assert not abejas(partida)


def test_una_pelea_entera_se_puede_ganar(partida):
    jefe = llegar_a_la_colmena(partida)
    for _ in range(60 * 240):
        if partida.jefe is None:
            break
        abiertas = [c for c in jefe.partes_vivas() if c.golpeable(jefe)]
        if abiertas:
            dash_contra(partida, *abiertas[0].centro(jefe))
        elif jefe.puede_recibir_golpe():
            dash_contra(partida, *jefe.centro_nucleo())
        jugar(partida)
        partida.nave.invulnerable_hasta = math.inf
    assert partida.jefe is None


def test_se_dibuja_en_todas_sus_fases(app):
    avanzar(app)
    partida = empezar_partida(app)
    jefe = llegar_a_la_colmena(partida)
    jefe.elegidas = [jefe.partes[0]]
    for fase in ("flotar", "abrir", "soltar", "expuesta", "enfurecerse", "temblar", "embestir",
                 "aturdida", "volver", "morir"):
        jefe.cambiar_fase(fase, 5000, partida.tiempo)
        avanzar(app, 5)
