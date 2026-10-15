"""Logros, progreso guardado (naves) y el Game Over con el resumen."""
import json
import os

import pygame

from juego.config import NAVES, NOMBRE_PROGRESO
from juego.guardado import Progreso
from juego.logros import LOGROS, LOGROS_POR_ID, revisar_logros
from juego.escenas.arcade.fin import Fin
from juego.escenas.inicio import Inicio
from tests.ayudas import jugar, avanzar, tecla


def test_todos_los_logros_estan_completos():
    assert len({logro.id for logro in LOGROS}) == len(LOGROS)
    for logro in LOGROS:
        assert logro.nombre and len(logro.nombre) <= 16
        assert len(logro.descripcion) <= 36
    # Cada nave se desbloquea con un logro que existe
    assert all(id_logro is None or id_logro in LOGROS_POR_ID for _, _, id_logro in NAVES)


def test_un_logro_se_desbloquea_una_vez_y_se_guarda(partida, tmp_path):
    progreso = Progreso(str(tmp_path / "progreso.json"))
    partida.puntaje = 1000
    nuevos = revisar_logros(partida, progreso)
    assert [logro.id for logro in nuevos] == ["mil"]
    assert revisar_logros(partida, progreso) == []
    assert "mil" in Progreso(str(tmp_path / "progreso.json")).logros     # quedo en el archivo


def test_la_partida_avisa_con_una_ficha_por_logro(partida):
    partida.progreso.logros.clear()
    partida.puntaje = 5000
    partida.estadisticas.perfectos = 10
    jugar(partida, 30)
    ids = [logro.id for logro in partida.logros_nuevos]
    assert {"mil", "leyenda", "al_filo"} <= set(ids)
    # Las fichas salen una detras de otra
    desdes = [desde for _, desde in partida.fichas_logro]
    assert desdes == sorted(desdes) and len(set(desdes)) == len(desdes)


def test_progreso_danado_o_con_una_nave_bloqueada(tmp_path):
    archivo = tmp_path / "progreso.json"
    archivo.write_text("{esto no es json")
    assert Progreso(str(archivo)).logros == set()
    archivo.write_text(json.dumps({"logros": [], "nave": NAVES[-1][0], "partidas": 3}))
    progreso = Progreso(str(archivo))
    assert progreso.nave == NAVES[0][0]            # esa nave no estaba desbloqueada
    assert progreso.partidas == 3


def test_el_game_over_suma_una_partida(app):
    avanzar(app)
    app.nueva_partida()
    avanzar(app, 101)
    partida = app.escena.partida
    partida.vidas = 1
    partida.danar_jugador(0, 0)
    assert app.progreso.partidas == 1
    with open(os.path.join(os.path.dirname(app.records.archivo), NOMBRE_PROGRESO)) as abierto:
        assert json.load(abierto)["partidas"] == 1


def test_el_fin_muestra_el_resumen_y_esc_vuelve_al_menu(app):
    avanzar(app)
    app.nueva_partida()
    avanzar(app, 101)
    partida = app.escena.partida
    partida.estadisticas.rangos = ["S", "B"]
    partida.mejoras = {"onda": 2, "fenix": 1}
    app.cambiar_escena(Fin(app, partida, fila_nueva=-1))
    avanzar(app, 200)                   # cuenta el puntaje y salen todas las filas
    tecla(pygame.K_ESCAPE)
    avanzar(app)
    assert isinstance(app.escena, Inicio)
