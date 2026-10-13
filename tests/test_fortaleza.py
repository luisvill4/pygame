"""La Fortaleza y el sistema de partes: la marcha de los cañones, el ritmo y el baile final."""
import math

import pytest

from juego.config import (ANCHO, JEFE_VIDA, FORTALEZA_VIDA_CANON, FORTALEZA_PUNTOS_CANON, FORTALEZA_PULSOS,
                          MS_POR_FRAME, FORTALEZA_MARGEN_GOLPE, RADIO_NAVE)
from juego.jefes import crear_jefe
from juego.jefes.fortaleza import ABAJO_CASCO
from juego.proyectiles import Misil, Mina, Obus
from tests.ayudas import jugar, avanzar, empezar_partida


def llegar_a_la_fortaleza(partida):
    # La Fortaleza ya en su lugar, empezando su primer compas
    partida.jefes_vencidos = 1
    jefe = crear_jefe("fortaleza", partida)
    partida.jefe = jefe
    jefe.y = jefe.y_final
    jefe.al_terminar_de_entrar(partida)
    return jefe


def canon(jefe, ataque):
    return next(c for c in jefe.partes if c.ataque == ataque)


def preparar_compas(partida, jefe, ataque):
    # Fuerza que el proximo ataque sea el de ese cañon (cargando, a punto de disparar)
    jefe.compas = [canon(jefe, ataque)]
    jefe.turno = 0
    jefe.empezar_carga(partida, 2)


def dash_contra(partida, x, y):
    # La nave en dash, centrada en (x, y)
    partida.nave.x, partida.nave.y = x - 25, y - 25
    partida.nave.dash_hasta = partida.tiempo + 500


def sin_coraza(partida, jefe):
    for c in jefe.partes:
        c.vida = 1
        c.caliente = True
        jefe.golpear_parte(partida, c)


def test_tiene_cuatro_canones_y_la_barra_los_suma(partida):
    jefe = llegar_a_la_fortaleza(partida)
    assert sorted(c.ataque for c in jefe.partes) == ["laser", "minas", "misiles", "rafaga"]
    total = JEFE_VIDA + 4 * FORTALEZA_VIDA_CANON          # (sale segunda: 1 jefe vencido // 2 = 0)
    assert jefe.vida_barra() == (total, total)


def test_un_canon_solo_se_golpea_recalentado(partida):
    jefe = llegar_a_la_fortaleza(partida)
    rafaga = canon(jefe, "rafaga")
    dash_contra(partida, *rafaga.centro(jefe))
    partida._choques_jefe()
    assert rafaga.vida == FORTALEZA_VIDA_CANON          # frio: el dash lo atraviesa sin hacerle nada

    jefe.compas = [rafaga]
    jefe.recalentar(partida)
    dash_contra(partida, *rafaga.centro(jefe))
    partida._choques_jefe()
    assert rafaga.vida == FORTALEZA_VIDA_CANON - 1
    assert not rafaga.caliente                          # el golpe lo enfria
    assert partida.nave.dash_hasta == 0                 # la nave rebota
    assert partida.vidas == partida.vidas_max


def test_romper_un_canon_da_puntos_y_acelera_el_pulso(partida):
    jefe = llegar_a_la_fortaleza(partida)
    minas = canon(jefe, "minas")
    minas.vida = 1
    minas.caliente = True
    dash_contra(partida, *minas.centro(jefe))
    partida._choques_jefe()
    assert not minas.viva()
    assert partida.puntaje == FORTALEZA_PUNTOS_CANON
    assert minas.caja(jefe) not in jefe.cajas_danio()   # los restos ya no hacen daño
    jefe.empezar_compas(partida)
    assert jefe.ms_pulso == FORTALEZA_PULSOS[1] < FORTALEZA_PULSOS[0]


def test_ataca_de_a_un_canon_y_con_pocas_balas(partida):
    jefe = llegar_a_la_fortaleza(partida)
    partida.nave.invulnerable_hasta = math.inf
    atacaron = set()
    for _ in range(60 * 60):
        jugar(partida)
        if jefe.fase in ("cargar", "disparar"):
            atacaron.add(jefe.canon_actual().ataque)
        assert sum(c.caliente for c in jefe.partes) <= 1    # con 4 cañones, un solo blanco por vez
        assert len(partida.balas) <= 10
    assert atacaron == {"laser", "minas", "misiles", "rafaga"}


def test_los_obuses_salen_a_ritmo(partida):
    jefe = llegar_a_la_fortaleza(partida)
    partida.nave.invulnerable_hasta = math.inf
    preparar_compas(partida, jefe, "rafaga")
    salidas = []
    while jefe.fase in ("cargar", "disparar"):
        antes = len(partida.balas)
        jugar(partida)
        if len(partida.balas) > antes:
            salidas.append(partida.tiempo)
    assert len(salidas) == 3
    for anterior, siguiente in zip(salidas, salidas[1:]):
        assert siguiente - anterior == pytest.approx(jefe.ms_pulso, abs=MS_POR_FRAME)
    assert all(isinstance(bala, Obus) for bala in partida.balas)
    assert jefe.fase == "recalentado"


def test_el_laser_hace_dano_solo_prendido(partida):
    jefe = llegar_a_la_fortaleza(partida)
    preparar_compas(partida, jefe, "laser")
    rayo = canon(jefe, "laser").caja_laser(jefe)
    partida.nave.x, partida.nave.y = rayo.centerx - 25, 400
    partida._choques_jefe()
    assert partida.vidas == partida.vidas_max
    jefe.laser_prendido = True
    partida._choques_jefe()
    assert partida.vidas == partida.vidas_max - 1


def test_el_laser_barre_hacia_la_nave(partida):
    jefe = llegar_a_la_fortaleza(partida)
    partida.nave.invulnerable_hasta = math.inf
    jefe.x = 40
    partida.nave.x = 700
    preparar_compas(partida, jefe, "laser")
    assert jefe.barrido == 1
    while jefe.fase != "recalentado":
        jugar(partida)
    assert jefe.x > 40 + 100


def test_las_minas_caen_donde_avisan(partida):
    jefe = llegar_a_la_fortaleza(partida)
    preparar_compas(partida, jefe, "minas")
    objetivos = list(canon(jefe, "minas").objetivos)
    for pulso in range(len(objetivos)):
        jefe.disparar(partida, canon(jefe, "minas"), pulso)
    lanzadas = list(partida.balas)
    for _ in range(80):     # 80 pasos: ya frenaron, pero todavia no estallaron
        for mina in lanzadas:
            mina.mover(partida)
    for mina, (objetivo_x, objetivo_y) in zip(lanzadas, objetivos):
        assert math.hypot(mina.x - objetivo_x, mina.y - objetivo_y) < 10


def test_la_mina_estalla_en_cruz(partida):
    mina = Mina(400, 300, 0, 0, 2, 1000, "x")
    partida.balas.append(mina)
    while mina.mover(partida):
        pass
    cruz = [b for b in partida.balas if b is not mina]
    assert len(cruz) == 4
    for bala in cruz:
        assert abs(bala.vx) == pytest.approx(abs(bala.vy))     # en "x": todas en diagonal


def test_el_misil_te_sigue_y_el_dash_lo_destruye(partida):
    partida.jefe = crear_jefe("fortaleza", partida)
    nave_x, nave_y = partida.nave.centro()
    misil = Misil(nave_x - 300, nave_y - 300, 3, 0, 2500)     # arriba a la izquierda, yendo a la derecha
    for _ in range(40):
        misil.mover(partida)
    assert misil.vy > 0                 # giro hacia la nave
    partida.balas.append(misil)
    dash_contra(partida, misil.x, misil.y)
    partida._choques_jefe()
    assert misil not in partida.balas
    assert partida.puntaje == Misil.puntos


def test_sin_canones_cae_la_coraza_y_empieza_el_baile_final(partida):
    jefe = llegar_a_la_fortaleza(partida)
    partida.nave.invulnerable_hasta = math.inf
    sin_coraza(partida, jefe)
    assert jefe.fase == "descubrirse"
    fases = []
    for _ in range(60 * 20):
        jugar(partida)
        if not fases or fases[-1] != jefe.fase:
            fases.append(jefe.fase)
        if jefe.fase == "aturdida":
            break
    assert not jefe.con_coraza
    assert fases == ["descubrirse", "cortinas", "apuntar", "fijar", "caer", "aturdida"]
    assert jefe.puede_recibir_golpe()
    dash_contra(partida, *jefe.centro_nucleo())
    partida._choques_jefe()
    assert jefe.vida == jefe.vida_max - 1
    assert jefe.fase == "subir"


def test_las_cortinas_siempre_dejan_un_hueco(partida):
    jefe = llegar_a_la_fortaleza(partida)
    sin_coraza(partida, jefe)
    jefe.caer_coraza(partida)
    for hueco in jefe.huecos:
        partida.balas.clear()
        jefe.soltar_cortina(partida, hueco)
        xs = sorted(b.x for b in partida.balas)
        mayor_hueco = max(b - a for a, b in zip([0] + xs, xs + [ANCHO]))
        assert mayor_hueco >= 150           # entra la nave con margen


def test_al_fijar_deja_de_seguirte(partida):
    jefe = llegar_a_la_fortaleza(partida)
    partida.nave.invulnerable_hasta = math.inf
    sin_coraza(partida, jefe)
    while jefe.fase != "fijar":
        jugar(partida)
    x_fija = jefe.x
    partida.nave.x = 0 if x_fija > 300 else 700
    while jefe.fase == "fijar":
        jugar(partida)
    assert jefe.x == x_fija


def test_congelada_no_avanza_y_se_le_puede_pegar(partida):
    jefe = llegar_a_la_fortaleza(partida)
    misiles = canon(jefe, "misiles")
    jefe.compas = [misiles]
    jefe.recalentar(partida)
    hasta = jefe.fase_hasta
    partida.activar("hielo", 5000)
    jugar(partida, 60)
    assert jefe.fase_hasta == pytest.approx(hasta + 60 * MS_POR_FRAME)
    assert jefe.parte_golpeable(misiles.caja(jefe)) is misiles  # el hielo alarga la ventana para pegarle


def test_una_pelea_entera_se_puede_ganar(partida):
    # Un "bot" que espera cada cañon recalentado (y despues el nucleo) y le pega con el dash
    jefe = llegar_a_la_fortaleza(partida)
    partida.nave.invulnerable_hasta = math.inf
    for _ in range(60 * 240):
        if partida.jefe is None:
            break
        golpeables = [c for c in jefe.partes_vivas() if c.golpeable(jefe)]
        if golpeables:
            dash_contra(partida, *golpeables[0].centro(jefe))
        elif jefe.puede_recibir_golpe():
            dash_contra(partida, *jefe.centro_nucleo())
        jugar(partida)
        partida.nave.invulnerable_hasta = math.inf
    assert partida.jefe is None
    assert partida.jefes_vencidos == 2


def test_se_dibuja_en_todas_sus_fases(app):
    # Que ninguna fase rompa el dibujo (con la App entera: escena, HUD y avisos)
    avanzar(app)
    partida = empezar_partida(app)
    partida.nave.invulnerable_hasta = math.inf
    jefe = llegar_a_la_fortaleza(partida)
    for ataque in ("rafaga", "misiles", "laser", "minas"):
        preparar_compas(partida, jefe, ataque)
        avanzar(app, 5)
    jefe.laser_prendido = True
    avanzar(app, 3)
    jefe.laser_prendido = False
    jefe.compas = list(jefe.partes)
    jefe.recalentar(partida)
    avanzar(app, 5)
    jefe.empezar_cortinas(partida)
    for fase in ("cortinas", "apuntar", "fijar", "aturdida", "subir", "morir"):
        jefe.cambiar_fase(fase, 5000, partida.tiempo)
        avanzar(app, 5)


def test_medidas_de_la_fortaleza_y_sus_canones(partida):
    # Las medidas de los sprites (fortaleza.png: 6 cuadros de 384x192; fortaleza_canon.png: 2 de 48x48)
    jefe = llegar_a_la_fortaleza(partida)
    assert (jefe.ancho, jefe.alto) == (384, 192)
    assert all((c.ancho, c.alto) == (48, 48) for c in jefe.partes)
    for c in jefe.partes:
        assert jefe.caja_cuerpo().left <= c.caja(jefe).left and c.caja(jefe).right <= jefe.caja_cuerpo().right


def test_al_canon_se_le_pega_con_margen(partida):
    # El dash le pega aunque roce apenas afuera del dibujo (el margen solo sirve para pegarle)
    jefe = llegar_a_la_fortaleza(partida)
    rafaga = canon(jefe, "rafaga")
    jefe.compas = [rafaga]
    jefe.recalentar(partida)
    caja = rafaga.caja(jefe)
    nave_justo_afuera = caja.move(0, caja.height + FORTALEZA_MARGEN_GOLPE - 2)
    assert not nave_justo_afuera.colliderect(caja)
    assert jefe.parte_golpeable(nave_justo_afuera) is rafaga


def test_se_puede_escapar_de_la_caida_sin_dash(partida):
    # Arrancando justo debajo del centro: al fijarse, alcanza con moverse hacia un costado
    jefe = llegar_a_la_fortaleza(partida)
    for c in jefe.partes:
        c.vida = 0
    jefe.con_coraza = False
    jefe.ms_pulso = FORTALEZA_PULSOS[-1]
    partida.director.proximo_refuerzo = math.inf
    partida.nave.x, partida.nave.y = 375, 420
    jefe.x = jefe.x_sobre(400)
    jefe.cambiar_fase_pulsos("apuntar", 2, partida.tiempo)
    while jefe.fase == "apuntar":
        jugar(partida)
    vidas = partida.vidas
    afuera = False
    while jefe.fase in ("fijar", "caer"):
        jugar(partida, dx=1)
        nave = partida.nave
        afuera = afuera or nave.x + 25 - RADIO_NAVE > jefe.x + jefe.ancho
        if jefe.y + ABAJO_CASCO >= nave.y + 25 - RADIO_NAVE:
            # El casco llego a la altura de la nave: tiene que estar afuera de la columna,
            # con margen (no salvarse de casualidad)
            assert afuera
            break
    jugar(partida, 60)
    assert jefe.fase == "aturdida"
    assert partida.vidas == vidas
