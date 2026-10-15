"""Director de la progresion: la ruta de tramos, los escuadrones, el asedio y los sectores."""
import math
import random

import pytest

from juego.config import (SECTORES, CARTEL_JEFE, CARTEL_RANGO, CARTEL_SECTOR, MS_POR_FRAME, JEFE_CADA_NIVELES, ANCHO, ALTO,
                          AVISO_ESCUADRON, ENTRADA_ESCUADRON, TURNO_ESCUADRON, INICIO_TRAMO, ESCUADRON_PUNTOS,
                          ASEDIO_DURACION, ASEDIO_INICIO, DIFICULTADES, PERMANENCIA_MINIMA)
from juego.enemigos import TIPOS_ENEMIGO
from juego.escuadrones import FORMACIONES, lugares
from juego.rutas import RUTAS, tipos_de_las_rutas
from tests.ayudas import jugar

PASOS_ENTRADA = int((AVISO_ESCUADRON + ENTRADA_ESCUADRON + 600) / MS_POR_FRAME)   # (+ el escalonado)


def con_escuadrones(partida):
    # El fixture los apaga: aca se prenden (y la nave no recibe daño)
    partida.director.con_escuadrones = True
    partida.nave.invulnerable_hasta = math.inf
    return partida.director


def subir_hasta_el_jefe(partida):
    # Sube de nivel hasta que aparece el jefe (sin limpiar la pelea)
    partida.nivel = (partida.nivel // JEFE_CADA_NIVELES + 1) * JEFE_CADA_NIVELES - 1
    partida.subir_nivel()


def vencer_y_cerrar(partida):
    partida.jefe_vencido()
    jugar(partida, int((CARTEL_JEFE + CARTEL_RANGO) / MS_POR_FRAME) + 2)


# ---------- El guion ----------

def test_el_guion_arcade_tiene_una_ruta_por_sector():
    assert len(RUTAS) == len(SECTORES)
    for sector in RUTAS:
        assert len(sector) == JEFE_CADA_NIVELES - 1             # 4 tramos y el jefe
        assert [tramo.get("asedio", False) for tramo in sector] == [False, False, False, True]


def test_el_guion_usa_enemigos_y_formaciones_que_existen():
    for sector in RUTAS:
        for tramo in sector:
            assert len(tramo["nombre"]) <= 16       # (entra en el cartel; el objetivo: test_objetivos.py)
            for tipo, cantidad, formacion in tramo["escuadrones"]:
                assert tipo in TIPOS_ENEMIGO and not TIPOS_ENEMIGO[tipo].esbirro
                assert formacion in FORMACIONES and cantidad >= 1


def test_todos_los_enemigos_aparecen_en_el_guion():
    # (los hijos del divisor y las abejas de la Colmena no llegan solos)
    sueltos = {tipo for tipo, clase in TIPOS_ENEMIGO.items()
               if not clase.esbirro and not tipo.startswith("divisor_")}
    assert tipos_de_las_rutas(RUTAS) == sueltos


def test_un_enemigo_nuevo_por_tramo_y_nunca_en_el_asedio():
    vistos = set()
    for sector in RUTAS:
        for tramo in sector:
            nuevos = {tipo for tipo, _, _ in tramo["escuadrones"]} - vistos
            assert len(nuevos) <= 1, tramo["nombre"]
            if tramo.get("asedio"):
                assert not nuevos, tramo["nombre"]
            vistos |= nuevos


@pytest.mark.parametrize("formacion", sorted(FORMACIONES))
def test_las_formaciones_entran_desde_afuera_lejos_de_la_nave(formacion):
    random.seed(1)
    for nave_x, nave_y in [(ANCHO / 2, ALTO / 2), (80, 300), (ANCHO - 80, 520), (500, 130)]:
        for cantidad in range(1, 7):
            pares = lugares(formacion, cantidad, nave_x, nave_y)
            assert len(pares) == cantidad
            for (desde_x, desde_y), (hasta_x, hasta_y) in pares:
                assert not (0 <= desde_x <= ANCHO and 0 <= desde_y <= ALTO)     # arranca afuera...
                assert 40 <= hasta_x <= ANCHO - 40 and 100 <= hasta_y <= ALTO - 80  # ...y llega adentro
                assert math.hypot(hasta_x - nave_x, hasta_y - nave_y) > 150, (formacion, nave_x, nave_y)


# ---------- Los tramos ----------

def test_la_partida_empieza_en_el_tramo_1_del_cinturon(app):
    app.nueva_partida()
    director = app.escena.partida.director
    assert director.sector is SECTORES[0]
    assert director.numero_tramo == 1
    assert director.tramo is RUTAS[0][0]
    assert app.escena.partida.enemigos == []        # el primer escuadron llega al rato
    assert director.proximo_escuadron == INICIO_TRAMO


def test_cada_nivel_es_el_tramo_siguiente_con_su_cartel(partida):
    director = partida.director
    partida.avisos.vaciar()                     # (el cartel del tramo 1)
    partida.subir_nivel()
    assert director.numero_tramo == 2 and director.tramo is RUTAS[0][1]
    assert partida.avisos.actual.etiqueta == "TRAMO 2/4"
    assert partida.avisos.actual.titulo == RUTAS[0][1]["nombre"]


def test_al_cambiar_de_tramo_los_escuadrones_se_retiran(partida):
    director = con_escuadrones(partida)
    escuadron = director.lanzar_escuadron(("perseguidor", 2, "pinza"))
    jugar(partida, PASOS_ENTRADA)
    partida.subir_nivel()
    assert all(enemigo.saliendo for enemigo in escuadron.miembros)
    jugar(partida, 90)
    assert not any(enemigo in partida.enemigos for enemigo in escuadron.miembros)    # se fueron volando


# ---------- Los escuadrones ----------

def test_un_escuadron_entra_volando_desde_el_borde_sin_lastimar(partida):
    director = con_escuadrones(partida)
    partida.nave.invulnerable_hasta = 0
    escuadron = director.lanzar_escuadron(("perseguidor", 2, "flanco"))
    enemigo = escuadron.miembros[0]
    assert enemigo.fuera_de_la_pantalla() and not enemigo.activo(partida.tiempo)
    # Mientras entra no hace daño, aunque pase por encima de la nave
    partida.nave.x, partida.nave.y = enemigo.x, enemigo.y
    jugar(partida, int(AVISO_ESCUADRON / MS_POR_FRAME) + 5)
    assert partida.vidas == partida.vidas_max
    partida.nave.x, partida.nave.y = 500, 300
    jugar(partida, PASOS_ENTRADA)
    assert enemigo.activo(partida.tiempo) and not enemigo.fuera_de_la_pantalla()
    assert enemigo.entrada is None


def test_nunca_hay_mas_escuadrones_que_los_del_tramo(partida):
    director = con_escuadrones(partida)
    random.seed(4)
    for _ in range(2):
        partida.subir_nivel()                   # (el tramo 3: su objetivo no se cumple solo)
    for _ in range(60 * 40):
        jugar(partida)
        atacando = [e for e in director.escuadrones if not e.se_retiro]
        assert len(atacando) <= director.tramo["a_la_vez"]
    assert partida.enemigos


def test_al_terminar_su_turno_un_escuadron_se_retira_sin_bonus(partida):
    director = con_escuadrones(partida)
    director.proximo_escuadron = math.inf       # (que no llegue otro)
    escuadron = director.lanzar_escuadron(("perseguidor", 2, "pinza"))
    puntaje = partida.puntaje
    jugar(partida, int((AVISO_ESCUADRON + TURNO_ESCUADRON) / MS_POR_FRAME) + 2)
    assert all(enemigo.saliendo for enemigo in escuadron.vivos(partida))
    assert not any(enemigo.hace_danio() and enemigo.activo(partida.tiempo) for enemigo in escuadron.vivos(partida))
    jugar(partida, 120)
    assert escuadron.termino(partida) and escuadron not in director.escuadrones
    assert partida.puntaje == puntaje


def test_los_hijos_de_un_divisor_que_se_retira_tambien_se_van(partida):
    # Bug: si lo partias mientras se iba, sus hijos se quedaban para siempre y el tramo no terminaba
    director = con_escuadrones(partida)
    director.proximo_escuadron = math.inf
    escuadron = director.lanzar_escuadron(("divisor", 1, "flanco"))
    jugar(partida, PASOS_ENTRADA)
    divisor = escuadron.miembros[0]
    escuadron.retirarse(partida)
    jugar(partida, 5)
    partida.destruir_con_dash(divisor)          # (las ondas pueden romper a uno que se va)
    assert len(escuadron.vivos(partida)) == 2
    jugar(partida, 180)
    assert escuadron.termino(partida) and director.escuadrones == []


def test_eliminar_un_escuadron_entero_da_bonus(partida):
    director = con_escuadrones(partida)
    director.proximo_escuadron = math.inf
    escuadron = director.lanzar_escuadron(("ladron", 3, "lluvia"))
    jugar(partida, PASOS_ENTRADA)
    for enemigo in list(escuadron.miembros):
        partida.destruir_con_dash(enemigo)
    puntaje = partida.puntaje
    jugar(partida)
    assert partida.estadisticas.escuadrones == 1
    assert partida.puntaje >= puntaje + ESCUADRON_PUNTOS * 3


def test_un_enemigo_que_te_choca_se_retira(partida):
    director = con_escuadrones(partida)
    escuadron = director.lanzar_escuadron(("perseguidor", 1, "flanco"))
    jugar(partida, PASOS_ENTRADA)
    enemigo = escuadron.miembros[0]
    partida.nave.invulnerable_hasta = 0
    partida.nave.x, partida.nave.y = enemigo.centro()[0] - 25, enemigo.centro()[1] - 25
    jugar(partida)
    assert partida.vidas == partida.vidas_max - 1
    assert enemigo.saliendo                     # (no reaparece en otro lado: se va)


def test_un_tipo_nuevo_se_presenta_con_su_ficha(partida):
    director = con_escuadrones(partida)
    director.vistos = {"perseguidor"}
    director.lanzar_escuadron(("divisor", 1, "flanco"))
    assert director.nuevo_tipo is TIPOS_ENEMIGO["divisor"]


def test_en_cada_vuelta_y_en_dificil_los_escuadrones_traen_mas(partida):
    director = partida.director
    normal = director._cantidad(3)
    director.numero_sector = len(SECTORES) + 1          # la segunda vuelta
    assert director._cantidad(3) > normal
    director.numero_sector = 1
    cantidades = []
    for dificultad in ("FACIL", "NORMAL", "DIFICIL", "PESADILLA"):
        partida.reglas = DIFICULTADES[dificultad]
        cantidades.append(director._cantidad(3))
    assert cantidades == sorted(cantidades) and cantidades[0] < cantidades[-1]
    assert director._cantidad(1) >= 1


# ---------- El asedio ----------

def preparar_asedio(partida):
    director = con_escuadrones(partida)
    partida.nivel = 3
    partida.subir_nivel()                       # nivel 4: el tramo 4 es el asedio
    assert director.tramo.get("asedio")
    jugar(partida, int(ASEDIO_INICIO / MS_POR_FRAME) + 2)
    assert director.en_asedio
    return director


def test_el_asedio_llega_en_el_tramo_4_y_al_superarlo_viene_el_jefe(partida):
    director = preparar_asedio(partida)
    jugar(partida, 120)
    assert partida.enemigos and partida.nivel == 4 and partida.jefe is None     # el jefe espera
    puntaje = partida.puntaje
    jugar(partida, int(ASEDIO_DURACION / MS_POR_FRAME) + 2)
    assert not director.en_asedio
    assert partida.puntaje > puntaje                            # premio
    assert partida.jefe is None                                 # los que quedan se despiden...
    jugar(partida, int((PERMANENCIA_MINIMA + 2000) / MS_POR_FRAME))
    assert partida.nivel == 5 and partida.jefe is not None      # ...y ahora si: el jefe
    assert partida.enemigos == []


def test_asedio_sin_premio_si_perdiste_una_vida(partida):
    director = preparar_asedio(partida)
    partida.nave.invulnerable_hasta = 0
    partida.danar_jugador(*partida.nave.centro())
    partida.nave.invulnerable_hasta = math.inf
    puntaje = partida.puntaje
    jugar(partida, int(ASEDIO_DURACION / MS_POR_FRAME) + 2)
    assert not director.en_asedio
    assert partida.puntaje == puntaje
    assert partida.jefe is None             # (la barra no estaba llena: se sigue en el tramo 4)


def test_el_jefe_corta_el_asedio(partida):
    director = preparar_asedio(partida)
    jugar(partida, 120)
    partida.iniciar_jefe()
    assert not director.en_asedio and partida.enemigos == []
    assert director.escuadrones == []


# ---------- Los sectores ----------

def test_cada_sector_termina_con_su_jefe_y_despues_viene_el_siguiente(partida):
    partida.nave.invulnerable_hasta = math.inf
    director = partida.director
    assert director.sector is SECTORES[0]       # siempre se empieza en el Cinturon
    for vuelta in range(len(SECTORES) + 1):
        sector = director.sector
        subir_hasta_el_jefe(partida)
        assert partida.jefe.tipo == sector["jefe"]
        assert director.sector is sector        # el sector no cambia durante la pelea
        vencer_y_cerrar(partida)
        siguiente = SECTORES[(vuelta + 1) % len(SECTORES)]
        assert director.sector is siguiente     # en orden, y despues del ultimo vuelve al primero
        assert director.numero_sector == vuelta + 2


def test_despues_del_jefe_empieza_el_tramo_1_del_sector_nuevo(partida):
    director = partida.director
    subir_hasta_el_jefe(partida)
    assert director.numero_tramo == 0           # (el jefe)
    partida.jefe_vencido()
    jugar(partida, 5)
    assert partida.nivel == 5                   # mientras se cierra el sector, nada
    jugar(partida, int((CARTEL_JEFE + CARTEL_RANGO) / MS_POR_FRAME))
    assert partida.nivel == 6
    assert director.numero_tramo == 1 and director.tramo is RUTAS[1][0]
    # Primero la franja del sector nuevo; el cartel del tramo 1 espera a que termine
    assert partida.avisos.actual is None
    jugar(partida, int(CARTEL_SECTOR / MS_POR_FRAME) + 2)
    assert partida.avisos.actual.etiqueta == "TRAMO 1/4"


def test_en_cada_sector_el_fondo_tiene_su_ambiente(app):
    fondo = app.fondo
    for sector in SECTORES:
        fondo.ir_a_sector(sector, instantaneo=True)
        for _ in range(400):
            fondo.mover()
        fondo.dibujar(app.pantalla)
        assert fondo.motas, sector["nombre"]
