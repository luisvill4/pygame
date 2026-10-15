"""Modos de juego: cada uno cumple su parte (modos.py) y el arcade y la historia no se mezclan."""
import ast
import os

import pytest

from juego.config import CARPETA, SECTORES
from juego.arcade.modo import ModoArcade
from juego.historia.modo import ModoHistoria
from juego.escenas.pasajes import PASAJES

REGLAS = ["primer_sector", "abre_el_taller", "propone_desafio", "sigue_despues_del_jefe"]


def modos():
    return [ModoArcade(), ModoHistoria(1), ModoHistoria(3)]


@pytest.mark.parametrize("modo", modos(), ids=lambda modo: modo.nombre)
def test_cada_modo_responde_todas_sus_reglas_y_tiene_sus_pasajes(app, modo):
    app.nueva_partida(modo=modo)
    partida = app.escena.partida
    director = partida.director
    assert partida.modo is modo
    for regla in REGLAS:
        metodo = getattr(modo, regla)
        metodo(director) if regla in ("abre_el_taller", "propone_desafio") else metodo()
    assert len(modo.ruta(director.numero_sector)) == 4
    assert modo.encabezado(director)
    pasajes = PASAJES[modo.nombre]
    assert callable(pasajes.al_morir) and callable(pasajes.al_cumplir)


def test_cada_modo_empieza_en_su_sector(app):
    app.nueva_partida()                             # (por defecto, el arcade)
    assert app.escena.partida.director.sector is SECTORES[0]
    app.nueva_partida(modo=ModoHistoria(3))
    director = app.escena.partida.director
    assert director.sector is SECTORES[2] and director.numero_tramo == 1


def test_solo_el_arcade_sigue_despues_del_jefe_y_guarda_records():
    arcade, historia = ModoArcade(), ModoHistoria(1)
    assert arcade.sigue_despues_del_jefe() and arcade.guarda_records
    assert not historia.sigue_despues_del_jefe() and not historia.guarda_records


# ---------- Que las partes no se mezclen ----------

def importados(carpeta):
    # {archivo: [modulos que importa]} de todos los .py de una carpeta de juego/ (con subcarpetas)
    resultado = {}
    raiz = os.path.join(CARPETA, "juego", carpeta)
    for actual, _, archivos in os.walk(raiz):
        for nombre in archivos:
            if not nombre.endswith(".py"):
                continue
            ruta = os.path.join(actual, nombre)
            with open(ruta, encoding="utf-8") as abierto:
                arbol = ast.parse(abierto.read())
            modulos = []
            for nodo in ast.walk(arbol):
                if isinstance(nodo, ast.ImportFrom) and nodo.module:
                    modulos.append(nodo.module)
                elif isinstance(nodo, ast.Import):
                    modulos.extend(alias.name for alias in nodo.names)
            resultado[os.path.relpath(ruta, CARPETA)] = modulos
    return resultado


def test_el_arcade_y_la_historia_no_se_importan_entre_si():
    for archivo, modulos in importados("arcade").items():
        assert not any(m.startswith("juego.historia") for m in modulos), archivo
    for archivo, modulos in importados("historia").items():
        assert not any(m.startswith("juego.arcade") for m in modulos), archivo
    for archivo, modulos in importados(os.path.join("escenas", "arcade")).items():
        assert not any("historia" in m for m in modulos), archivo
    for archivo, modulos in importados(os.path.join("escenas", "historia")).items():
        assert not any("arcade" in m for m in modulos), archivo


def test_la_logica_de_los_modos_no_importa_pantallas():
    # Las reglas y los datos no saben de escenas (dependencias: ... <- partida <- escenas <- app)
    for carpeta in ("arcade", "historia"):
        for archivo, modulos in importados(carpeta).items():
            assert not any(m.startswith("juego.escenas") for m in modulos), archivo
