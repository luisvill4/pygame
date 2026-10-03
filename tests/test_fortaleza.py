"""La Fortaleza y el sistema de partes: cañones, laser, misiles, minas, coraza y nucleo."""
import math

import pytest

from juego.config import (JEFE_VIDA, FORTALEZA_VIDA_CANON, FORTALEZA_PUNTOS_CANON, FORTALEZA_RECALENTADO,
                          FORTALEZA_MINA_ESPERA, MS_POR_FRAME)
from juego.jefes import crear_jefe
from juego.proyectiles import Misil, Mina
from tests.ayudas import jugar, avanzar, empezar_partida


def llegar_a_la_fortaleza(partida):
    # La Fortaleza ya en su lugar, peleando (sin esperar a que baje)
    partida.jefes_vencidos = 1
    jefe = crear_jefe("fortaleza", partida)
    partida.jefe = jefe
    jefe.y = jefe.y_final
    jefe.al_terminar_de_entrar(partida)
    return jefe


def canon(jefe, ataque):
    return next(c for c in jefe.partes if c.ataque == ataque)


def dash_contra(partida, x, y):
    # La nave en dash, centrada en (x, y)
    partida.nave.x, partida.nave.y = x - 25, y - 25
    partida.nave.dash_hasta = partida.tiempo + 500


def test_tiene_cuatro_canones_y_la_barra_los_suma(partida):
    jefe = llegar_a_la_fortaleza(partida)
    assert sorted(c.ataque for c in jefe.partes) == ["laser", "minas", "misiles", "rafaga"]
    vida_nucleo = JEFE_VIDA + 1
    assert jefe.vida_barra() == (vida_nucleo + 4 * FORTALEZA_VIDA_CANON, vida_nucleo + 4 * FORTALEZA_VIDA_CANON)


def test_un_canon_solo_se_golpea_recalentado(partida):
    jefe = llegar_a_la_fortaleza(partida)
    rafaga = canon(jefe, "rafaga")
    dash_contra(partida, *rafaga.centro(jefe))
    partida._choques_jefe()
    assert rafaga.vida == FORTALEZA_VIDA_CANON          # listo: el dash lo atraviesa sin hacerle nada

    rafaga.cambiar_estado("recalentado", FORTALEZA_RECALENTADO, partida.tiempo)
    dash_contra(partida, *rafaga.centro(jefe))
    partida._choques_jefe()
    assert rafaga.vida == FORTALEZA_VIDA_CANON - 1
    assert rafaga.estado == "listo"                     # el golpe lo enfria
    assert partida.nave.dash_hasta == 0                 # la nave rebota
    assert partida.vidas == partida.vidas_max


def test_romper_un_canon_da_puntos(partida):
    jefe = llegar_a_la_fortaleza(partida)
    minas = canon(jefe, "minas")
    minas.vida = 1
    minas.cambiar_estado("recalentado", FORTALEZA_RECALENTADO, partida.tiempo)
    dash_contra(partida, *minas.centro(jefe))
    partida._choques_jefe()
    assert not minas.viva()
    assert partida.puntaje == FORTALEZA_PUNTOS_CANON
    assert minas.caja(jefe) not in jefe.cajas_danio()   # los restos ya no hacen daño


def test_los_canones_se_turnan_para_atacar(partida):
    jefe = llegar_a_la_fortaleza(partida)
    partida.nave.invulnerable_hasta = math.inf
    atacaron = set()
    for _ in range(600):
        jugar(partida)
        atacaron |= {c.ataque for c in jefe.partes if c.estado != "listo"}
    assert atacaron == {"laser", "minas", "misiles", "rafaga"}


def test_el_laser_hace_dano_solo_prendido(partida):
    jefe = llegar_a_la_fortaleza(partida)
    laser = canon(jefe, "laser")
    rayo = laser.caja_laser(jefe)
    partida.nave.x, partida.nave.y = rayo.centerx - 25, 400
    partida._choques_jefe()
    assert partida.vidas == partida.vidas_max
    laser.laser_prendido = True
    partida._choques_jefe()
    assert partida.vidas == partida.vidas_max - 1


def test_el_aviso_de_la_rafaga_muestra_justo_las_balas_que_salen(partida):
    jefe = llegar_a_la_fortaleza(partida)
    rafaga = canon(jefe, "rafaga")
    direcciones = jefe.direcciones_rafaga(partida, rafaga)
    jefe.disparar(partida, rafaga)
    assert len(partida.balas) == len(direcciones)
    for bala, direccion in zip(partida.balas, direcciones):
        assert math.atan2(bala.vy, bala.vx) == pytest.approx(math.atan2(math.sin(direccion), math.cos(direccion)))


def test_las_minas_caen_donde_avisan(partida):
    jefe = llegar_a_la_fortaleza(partida)
    minas = canon(jefe, "minas")
    jefe.empezar_carga(partida, minas)
    objetivos = list(minas.objetivos)
    minas.disparos = len(objetivos)
    for _ in objetivos:
        jefe.disparar(partida, minas)
        minas.disparos -= 1
    lanzadas = list(partida.balas)
    for _ in range(80):     # 80 pasos: ya frenaron, pero todavia no estallaron
        for mina in lanzadas:
            mina.mover(partida)
    for mina, (objetivo_x, objetivo_y) in zip(lanzadas, objetivos):
        assert math.hypot(mina.x - objetivo_x, mina.y - objetivo_y) < 10


def test_la_mina_estalla_en_un_anillo(partida):
    mina = Mina(400, 300, 0, 0, 2)
    partida.balas.append(mina)
    pasos = math.ceil(FORTALEZA_MINA_ESPERA / MS_POR_FRAME)
    for _ in range(pasos):
        if not mina.mover(partida):
            break
    assert len(partida.balas) == 1 + Mina.cantidad_balas     # la mina (que se borra afuera) + su anillo


def test_el_misil_te_sigue_y_despues_sigue_derecho(partida):
    nave_x, nave_y = partida.nave.centro()
    misil = Misil(nave_x - 300, nave_y - 300, 3, 0)         # arriba a la izquierda, yendo a la derecha
    for _ in range(40):
        misil.mover(partida)
    assert misil.vy > 0                 # giro hacia la nave
    misil.guiado = 0
    velocidad = (misil.vx, misil.vy)
    misil.mover(partida)
    assert (misil.vx, misil.vy) == velocidad


def test_sin_canones_se_cae_la_coraza_y_queda_el_nucleo(partida):
    jefe = llegar_a_la_fortaleza(partida)
    partida.nave.invulnerable_hasta = math.inf
    for c in jefe.partes:
        c.vida = 1
        c.estado = "recalentado"
        jefe.golpear_parte(partida, c)
    assert jefe.fase == "descubrirse"
    assert jefe.con_coraza
    jugar(partida, 120)
    assert not jefe.con_coraza
    assert jefe.fase == "furia"
    assert not jefe.puede_recibir_golpe()
    jefe.cambiar_fase("cansado", 2000, partida.tiempo)
    nucleo_x, nucleo_y = jefe.centro_nucleo()
    dash_contra(partida, nucleo_x, nucleo_y)
    partida._choques_jefe()
    assert jefe.vida == jefe.vida_max - 1
    assert jefe.fase == "furia"


def test_congelada_sus_canones_no_avanzan_y_se_les_puede_pegar(partida):
    jefe = llegar_a_la_fortaleza(partida)
    misiles = canon(jefe, "misiles")
    misiles.cambiar_estado("recalentado", FORTALEZA_RECALENTADO, partida.tiempo)
    hasta = misiles.estado_hasta
    partida.activar("hielo", 5000)
    jugar(partida, 60)
    assert misiles.estado_hasta == pytest.approx(hasta + 60 * MS_POR_FRAME)
    assert jefe.parte_golpeable(misiles.caja(jefe)) is misiles  # el hielo alarga la ventana para pegarle


def test_una_pelea_entera_se_puede_ganar(partida):
    # Un "bot" que espera cada cañon recalentado (y despues el nucleo) y le pega con el dash
    jefe = llegar_a_la_fortaleza(partida)
    partida.nave.invulnerable_hasta = math.inf
    for _ in range(60 * 180):
        if partida.jefe is None:
            break
        golpeables = [c for c in jefe.partes_vivas() if c.golpeable(jefe)]
        if golpeables and jefe.fase == "pelear":
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
    for c in jefe.partes:
        c.cambiar_estado("recalentado", FORTALEZA_RECALENTADO, partida.tiempo)
    canon(jefe, "laser").laser_prendido = True
    avanzar(app, 5)
    for fase in ("pelear", "descubrirse", "furia", "cansado", "morir"):
        jefe.cambiar_fase(fase, 5000, partida.tiempo)
        avanzar(app, 5)
