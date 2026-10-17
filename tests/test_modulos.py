"""Los modulos de la Alondra (modo historia): los peligros ambientales del mapa, los planos, el
hangar que los fabrica, el bloqueo de la galaxia, la nave que cambia y que la campaña entre a tiempo."""
import types

import pygame
import pytest

from juego import nave, dibujo, recursos
from juego.config import MAREA_ANIOS, MODULOS_PRECIOS, PIEZAS_POR_PELIGRO, CARTEL_JEFE, CARTEL_RANGO, MS_POR_FRAME, \
    ANCHO
from juego.guardado import Progreso
from juego.arcade.modo import ModoArcade
from juego.historia import modulos, galaxia
from juego.historia.galaxia import todos_los_sistemas, sistema, costo_viaje, peligro, UMBRAL
from juego.historia.mision import misiones_en_orden
from juego.historia.modo import ModoHistoria
from juego.escenas.historia.hangar import Hangar, MODULOS, PESTANAS
from juego.escenas.historia.dialogo import Dialogo, ANCHO_TEXTO
from juego.escenas.historia.pasajes import renglones_del_plano
from tests.ayudas import avanzar, tecla
from tests.test_historia import mision_en_juego, ir_al_jefe, ir_al_mapa, viajar
from tests.test_galaxia import explorar, despejar


# ---------- El mapa y los planos ----------

def test_cada_peligro_tiene_su_modulo_y_cada_plano_existe():
    for uno in todos_los_sistemas():
        if uno.ambiente is not None:
            tipo, intensidad = uno.ambiente
            assert tipo in modulos.POR_PELIGRO and 1 <= intensidad <= modulos.POR_PELIGRO[tipo].maximo, uno.id
        assert uno.plano is None or uno.plano in modulos.POR_ID, uno.id
    for modulo in modulos.MODULOS:
        assert modulo.id in MODULOS_PRECIOS
        lugares = [uno for uno in todos_los_sistemas() if uno.plano == modulo.id]
        primero = modulo.id == misiones_en_orden()[0].plano      # (el de la mision 1: el primero que se fabrica)
        assert len(lugares) >= (1 if primero else 2), modulo.id   # (cada plano en mas de un lugar)
        assert len(modulos.lo_que_abre(modulo.id, 1)) >= 2, modulo.id
        assert len(modulo.icono) == 7 and all(len(fila) == 7 for fila in modulo.icono)


def test_la_historia_nunca_se_traba():
    # El modulo que pide cada mision lo diseña Ines al cumplir una mision anterior
    planos = set()
    for clase in misiones_en_orden():
        if clase.ambiente is not None:
            assert modulos.POR_PELIGRO[clase.ambiente[0]].id in planos, clase.titulo
        if not clase.oculta and clase.plano:
            planos.add(clase.plano)


def test_toda_la_galaxia_se_puede_abrir():
    # Con todos los planos que se pueden conseguir (de a poco), se llega a todos lados
    planos, abiertos = set(), set()
    while True:
        nuevos = {uno.id for uno in todos_los_sistemas()
                  if uno.ambiente is None or modulos.POR_PELIGRO[uno.ambiente[0]].id in planos} - abiertos
        if not nuevos:
            break
        abiertos |= nuevos
        planos |= {sistema(id_).plano for id_ in nuevos if sistema(id_).plano}
    assert abiertos == {uno.id for uno in todos_los_sistemas()}


# ---------- Fabricar ----------

def test_fabricar_pide_el_plano_y_las_piezas(tmp_path):
    progreso = Progreso(str(tmp_path / "p.json"))
    progreso.piezas = 1000
    assert not modulos.fabricar(progreso, "filtro")                 # sin plano
    assert modulos.dar_plano(progreso, "filtro") and not modulos.dar_plano(progreso, "filtro")
    for _ in MODULOS_PRECIOS["filtro"]:
        assert modulos.fabricar(progreso, "filtro")
    assert not modulos.fabricar(progreso, "filtro")                 # al maximo
    assert progreso.piezas == 1000 - sum(MODULOS_PRECIOS["filtro"])
    otra_vez = Progreso(str(tmp_path / "p.json"))
    assert otra_vez.planos == {"filtro"} and modulos.nivel(otra_vez, "filtro") == 2
    progreso.piezas = 0
    progreso.planos.add("compensador")
    assert not modulos.fabricar(progreso, "compensador")            # sin piezas


def test_el_nivel_pedido_es_el_que_falta(tmp_path):
    progreso = Progreso(str(tmp_path / "p.json"))
    assert modulos.falta(progreso, None) is None
    modulo, nivel = modulos.falta(progreso, ("calor", 2))
    assert modulo.id == "escudo_termico" and nivel == 2
    progreso.hangar["escudo_termico"] = 1
    assert modulos.falta(progreso, ("calor", 1)) is None and modulos.falta(progreso, ("calor", 2)) is not None


def test_el_hangar_fabrica_en_su_pestaña(app):
    app.progreso.piezas = 500
    escena = Hangar(app, volver_a=None)
    app.cambiar_escena(escena, transicion=False)
    tecla(pygame.K_e)                       # a MODULOS
    avanzar(app)
    assert PESTANAS[escena.pestana] == MODULOS and escena.elegida().id == "escudo_termico"
    tecla(pygame.K_RETURN)                  # sin plano: no
    avanzar(app)
    assert modulos.nivel(app.progreso, "escudo_termico") == 0
    app.progreso.planos.add("escudo_termico")
    antes = nave.imagen("nave").copy()
    tecla(pygame.K_RETURN)
    avanzar(app, 3)
    assert modulos.nivel(app.progreso, "escudo_termico") == 1
    assert app.progreso.piezas == 500 - MODULOS_PRECIOS["escudo_termico"][0]
    assert _distintas(antes, nave.imagen("nave"))                   # la Alondra ya lo lleva puesto
    for _ in range(4):                      # se dibujan todas las cartas
        tecla(pygame.K_RIGHT)
        avanzar(app, 2)


def test_lo_que_dice_el_hangar_entra(app):
    escena = Hangar(app, volver_a=None)
    nota, _ = escena.nota()                 # (INSTALACIONES)
    assert recursos.fuente(dibujo.CHICA).size(nota)[0] <= ANCHO - 96, nota
    escena.pestana = PESTANAS.index(MODULOS)
    for planos in (set(), {modulo.id for modulo in modulos.MODULOS}):
        app.progreso.planos = planos
        for nivel in (0, 1, 2):
            for i, modulo in enumerate(modulos.MODULOS):
                app.progreso.hangar[modulo.id] = nivel
                escena.elegidas[MODULOS] = i
                nota, _ = escena.nota()
                assert recursos.fuente(dibujo.CHICA).size(nota)[0] <= ANCHO - 96, nota


# ---------- La galaxia bloquea ----------

def test_sin_el_modulo_no_se_viaja(app):
    mapa = ir_al_mapa(app)
    assert mapa.por_que_no(sistema("S02")) == "NECESITA ESCUDO TERMICO 1."
    viajar(app, mapa, "S02")
    assert app.escena is mapa and app.progreso.anios == 0
    app.progreso.hangar["escudo_termico"] = 1
    assert mapa.por_que_no(sistema("S02")) is None
    assert mapa.por_que_no(sistema("S05")) == "NECESITA ESCUDO TERMICO 2."      # (Brasa quema mas)
    viajar(app, mapa, "S02")
    assert app.escena is not mapa and app.progreso.ubicacion == "S02"


def test_la_galaxia_dibuja_los_peligros(app):
    mapa = ir_al_mapa(app)
    app.progreso.hangar["escudo_termico"] = 1
    for id_ in ("S02", "S05", "S08", "S16", "M2"):
        mapa.elegida = id_
        avanzar(app, 2)


# ---------- Los planos llegan jugando ----------

def test_cumplir_una_mision_da_su_plano(app):
    partida = mision_en_juego(app)
    ir_al_jefe(partida)
    partida.jefe_vencido()
    avanzar(app, int((CARTEL_JEFE + CARTEL_RANGO) / MS_POR_FRAME) + 40)
    assert isinstance(app.escena, Dialogo) and "escudo_termico" in app.progreso.planos
    assert any("ESCUDO TERMICO" in texto for _, texto in app.escena.renglones)


def test_despejar_un_sistema_da_su_plano_una_vez(app):
    partida = explorar(app, "S01")          # (guarda el del filtro)
    despejar(app, partida)
    assert "filtro" in app.progreso.planos
    assert any("FILTRO DE ESPORAS" in texto for _, texto in app.escena.renglones)
    partida = explorar(app, "S01")
    despejar(app, partida)
    assert not any("PLANO" in texto for _, texto in app.escena.renglones)       # (ya lo tenia)


def test_los_renglones_del_plano_entran():
    for modulo in modulos.MODULOS:
        for en_una_mision in (True, False):
            for _, texto in renglones_del_plano(modulo.id, en_una_mision):
                assert not set(texto) & set("ÁÉÍÓÚ")
                assert len(dibujo.partir_lineas(texto, dibujo.CHICA, ANCHO_TEXTO)) <= 4, texto


# ---------- La nave cambia ----------

def _distintas(una, otra):
    return any(una.get_at((x, y)) != otra.get_at((x, y)) for x in range(una.get_width())
               for y in range(una.get_height()))


def test_cada_nivel_de_cada_modulo_se_ve_en_la_nave(app):
    for modulo in modulos.MODULOS:
        anterior = nave.armar(())
        for nivel in range(1, modulo.maximo + 1):
            capas = [capa for n in range(1, nivel + 1) for capa in modulo.piezas[n]]
            imagen = nave.armar(capas)
            assert imagen.get_size() == (nave.TAMANO, nave.TAMANO)
            assert _distintas(anterior, imagen), (modulo.id, nivel)
            anterior = imagen


def test_las_piezas_calzan_en_la_grilla(app):
    # Todo el equipo puesto: cada cambio de color cae en el borde de un pixel de arte (2 px)
    capas = [capa for modulo in modulos.MODULOS for piezas in modulo.piezas.values() for capa in piezas]
    imagen = nave.armar(capas + [capa for piezas in modulos.PIEZAS_IMPULSOR.values() for capa in piezas])
    for y in range(nave.TAMANO):
        for x in range(1, nave.TAMANO):
            if imagen.get_at((x, y)) != imagen.get_at((x - 1, y)):
                assert x % 2 == 0, (x, y)


def test_la_historia_lleva_el_equipo_y_el_arcade_no(app):
    limpia = nave.armar(()).copy()
    app.progreso.hangar.update({"escudo_termico": 1, "filtro": 2})
    app.nueva_partida(modo=ModoHistoria(1))
    assert _distintas(limpia, nave.imagen("nave"))
    app.nueva_partida(modo=ModoArcade())
    assert not _distintas(limpia, nave.imagen("nave"))


# ---------- El tiempo alcanza ----------

def campaña(piezas_por_partida):
    # Una campaña codiciosa: la mision siguiente si se puede (fabricando lo que pida); si no, el
    # sistema libre que mas piezas da por año entre los que se puede entrar. Devuelve el año final
    progreso = types.SimpleNamespace(hangar={}, planos=set(), piezas=0, anios=0.0, puertas=set(), sistemas=set(),
                                     guardar=lambda: None)
    aqui = sistema(UMBRAL)
    for clase in [clase for clase in misiones_en_orden() if not clase.oculta]:
        objetivo = sistema("M%d" % clase.numero)
        while not _equipar(progreso, objetivo):
            opciones = [uno for uno in galaxia.SISTEMAS if uno.tipo == "libre" and uno.id not in progreso.sistemas
                        and _puede_equipar(progreso, uno)]
            if not opciones:                # sin piezas para nada: se repite la ultima mision
                progreso.anios += costo_viaje(aqui, aqui, progreso)
                progreso.piezas += piezas_por_partida
                continue
            uno = max(opciones, key=lambda uno: (PIEZAS_POR_PELIGRO * peligro(uno) + piezas_por_partida
                                                 + (200 if uno.plano not in progreso.planos | {None} else 0))
                      / costo_viaje(aqui, uno, progreso))
            _equipar(progreso, uno)
            progreso.anios += costo_viaje(aqui, uno, progreso)
            progreso.piezas += piezas_por_partida + PIEZAS_POR_PELIGRO * peligro(uno)
            progreso.sistemas.add(uno.id)
            modulos.dar_plano(progreso, uno.plano)
            aqui = uno
        progreso.anios += costo_viaje(aqui, objetivo, progreso)
        progreso.piezas += piezas_por_partida
        modulos.dar_plano(progreso, clase.plano)
        aqui = objetivo
    return progreso.anios


def _puede_equipar(progreso, uno):
    falta = modulos.falta(progreso, uno.ambiente)
    if falta is None:
        return True
    modulo, nivel = falta
    return (modulos.tiene_plano(progreso, modulo.id) and nivel == modulos.nivel(progreso, modulo.id) + 1
            and modulos.precio(progreso, modulo.id) <= progreso.piezas)


def _equipar(progreso, uno):
    while modulos.falta(progreso, uno.ambiente) is not None:
        if not modulos.fabricar(progreso, modulos.falta(progreso, uno.ambiente)[0].id):
            return False
    return True


@pytest.mark.parametrize("piezas_por_partida", [25, 35])
def test_la_campaña_con_modulos_llega_a_tiempo(piezas_por_partida):
    # Con 25 a 35 piezas por partida (250 a 350 creditos), el camino de la historia que explora
    # lo justo para fabricar los modulos llega con margen para explorar mas y comprar en el hangar
    assert campaña(piezas_por_partida) <= MAREA_ANIOS - 1
