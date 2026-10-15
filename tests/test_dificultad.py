"""Dificultad: reglas de cada una, records separados y la pantalla ELIGE DIFICULTAD."""
import json

import pygame
import pytest

from juego.config import DIFICULTADES, ORDEN_DIFICULTADES, ESPERA_POWERUP
from juego.escenas.arcade.dificultad import Dificultad, PASOS_ANIMACION
from juego.escenas.inicio import Inicio
from juego.escenas.listo import Listo
from tests.ayudas import avanzar, tecla


def ir_al_selector(app):
    tecla(pygame.K_RETURN)
    avanzar(app)
    assert isinstance(app.escena, Dificultad)
    return app.escena


@pytest.mark.parametrize("nombre", ORDEN_DIFICULTADES)
def test_reglas_de_cada_dificultad(app, nombre):
    app.nueva_partida(nombre)
    partida = app.escena.partida
    reglas = DIFICULTADES[nombre]
    assert partida.vidas == partida.vidas_max == reglas["vidas"]
    assert partida.factor_velocidad() == pytest.approx(reglas["velocidad"])
    esperas = [partida.espera_powerup() for _ in range(50)]
    assert min(esperas) >= ESPERA_POWERUP[0] * reglas["espera_powerup"]


def test_mas_dificil_mas_enemigos(app):
    # Cada escuadron trae mas enemigos
    cantidades = []
    for nombre in ORDEN_DIFICULTADES:
        app.nueva_partida(nombre)
        cantidades.append(app.escena.partida.director._cantidad(3))
    assert cantidades == sorted(cantidades) and cantidades[0] < cantidades[-1]


def test_el_selector_cambia_con_animacion_y_vuelve_a_empezar(app):
    selector = ir_al_selector(app)
    assert selector.nombre() == "NORMAL"
    tecla(pygame.K_RIGHT)
    avanzar(app)
    assert selector.nombre() == "DIFICIL"
    assert selector.animacion == PASOS_ANIMACION            # arranco la animacion
    assert selector.direccion == 1
    avanzar(app, PASOS_ANIMACION)
    assert selector.animacion == 0
    tecla(pygame.K_LEFT)
    tecla(pygame.K_LEFT)                                    # dos toques en el mismo paso: cambia una vez
    avanzar(app)
    assert selector.nombre() == "NORMAL"


def test_pesadilla_hace_temblar_la_pantalla(app):
    selector = ir_al_selector(app)
    selector._cambiar(1)
    selector._cambiar(1)
    assert selector.nombre() == "PESADILLA"
    assert app.efectos.temblor > 0


def test_elegir_empieza_con_esa_dificultad_y_la_recuerda(app, tmp_path):
    ir_al_selector(app)
    tecla(pygame.K_LEFT)
    avanzar(app)
    tecla(pygame.K_RETURN)
    avanzar(app)
    assert isinstance(app.escena, Listo)
    assert app.escena.partida.dificultad == "FACIL"
    assert app.escena.partida.vidas == 5
    assert app.opciones.dificultad == "FACIL"
    assert json.loads((tmp_path / "config.json").read_text())["dificultad"] == "FACIL"


def test_escape_vuelve_al_inicio(app):
    ir_al_selector(app)
    tecla(pygame.K_ESCAPE)
    avanzar(app)
    assert isinstance(app.escena, Inicio)


def test_el_record_es_de_cada_dificultad(app):
    app.records.agregar("AAA", 999, "FACIL")
    app.nueva_partida("NORMAL")
    assert app.escena.partida.puntaje_maximo == 0
    app.nueva_partida("FACIL")
    assert app.escena.partida.puntaje_maximo == 999


def test_se_dibuja_cada_dificultad_durante_toda_la_animacion(app):
    selector = ir_al_selector(app)
    for _ in ORDEN_DIFICULTADES:
        selector._cambiar(1)
        avanzar(app, PASOS_ANIMACION)     # cada paso dibuja un cuadro de la animacion
    assert selector.nombre() == "NORMAL"     # dio la vuelta completa
