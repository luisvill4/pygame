"""Modo historia: el estandar de las misiones, el avance guardado, el recorrido, la radio y los secretos."""
import math

import pygame
import pytest

from juego import carteles, dibujo, recursos
from juego.config import (SECTORES, JEFE_CADA_NIVELES, CARTEL_JEFE, CARTEL_RANGO, MS_POR_FRAME, RADIO_DEMORA_TRAMO,
                          MONEDA_GRABADA_DURA, RESTOS_ESPERA, MEJORA_TRAMO_HISTORIA)
from juego.guardado import Progreso
from juego.historia.mision import misiones_en_orden, todos_los_fragmentos, mision
from juego.historia.modo import ModoHistoria
from juego.historia.personajes import PERSONAJES
from juego.historia.secretos import TIPOS_SECRETO
from juego.historia.glifos import traducir, CLAVE_DE_LOS_GLIFOS
from juego.historia.reliquias import MonedaGrabada, Restos
from juego.escenas.historia.archivo import Archivo, LISTA, COLUMNA_NOMBRE
from juego.escenas.historia.dialogo import Dialogo, ANCHO_TEXTO
from juego.escenas.historia.mapa import Mapa
from juego.escenas.juego import Juego
from juego.escenas.listo import Listo
from tests.ayudas import avanzar, tecla, jugar

MOMENTOS_DE_RADIO = {"tramo_1", "tramo_2", "tramo_3", "tramo_4", "jefe"}


def renglones_de_todo():
    for clase in misiones_en_orden():
        yield from clase.antes
        yield from clase.despues
        for renglones in clase.radio.values():
            yield from renglones
        for fragmento in clase.fragmentos:
            yield from fragmento.reaccion


# ---------- El estandar de las misiones (lo que tiene que cumplir un archivo nuevo) ----------

def test_las_misiones_van_del_1_al_5_y_cada_una_en_un_sector():
    misiones = misiones_en_orden()
    assert [clase.numero for clase in misiones] == list(range(1, len(misiones) + 1))
    for clase in misiones:
        assert clase.titulo and clase.antes and clase.despues
        assert 1 <= clase.sector <= len(SECTORES)
        assert clase.tramos is None or len(clase.tramos) == JEFE_CADA_NIVELES - 1


def test_la_radio_habla_solo_en_momentos_que_existen():
    for clase in misiones_en_orden():
        assert set(clase.radio) <= MOMENTOS_DE_RADIO, clase.titulo


def test_los_fragmentos_no_se_repiten_y_cada_secreto_da_uno_de_su_mision():
    ids = [fragmento.id for fragmento, _ in todos_los_fragmentos()]
    assert len(ids) == len(set(ids))
    for clase in misiones_en_orden():
        propios = {fragmento.id for fragmento in clase.fragmentos}
        for tipo, fragmento, *_ in clase.secretos:
            assert tipo in TIPOS_SECRETO, tipo
            assert fragmento in propios, (clase.titulo, fragmento)


def test_quien_habla_existe_y_los_textos_entran(app):
    for personaje, texto in renglones_de_todo():
        assert personaje in PERSONAJES
        assert not set(texto) & set("ÁÉÍÓÚ"), texto         # (la fuente las dibuja mal)
        assert len(dibujo.partir_lineas(texto, dibujo.CHICA, ANCHO_TEXTO)) <= 4, texto


def test_la_radio_tiene_lugar_para_cada_mensaje(app):
    for clase in misiones_en_orden():
        for renglones in list(clase.radio.values()) + [f.reaccion for f in clase.fragmentos]:
            for _, texto in renglones:
                assert len(carteles.lineas_radio(texto)) <= 3, texto


def test_los_nombres_del_archivo_entran_en_su_lista(app):
    lugar = LISTA.width - 32 - COLUMNA_NOMBRE
    for fragmento, _ in todos_los_fragmentos():
        assert recursos.fuente(dibujo.CHICA).size(fragmento.nombre)[0] <= lugar, fragmento.nombre


def test_la_firma_de_los_cantores_dice_alba():
    firma = next(f for f, _ in todos_los_fragmentos() if f.id == "F01")
    assert traducir(firma.glifo) == "ALBA"
    assert CLAVE_DE_LOS_GLIFOS in {f.id for f, _ in todos_los_fragmentos()}


# ---------- El avance guardado ----------

def test_el_avance_se_guarda_y_se_vuelve_a_cargar(tmp_path):
    archivo = str(tmp_path / "progreso.json")
    progreso = Progreso(archivo)
    assert mision(1).disponible(progreso) and not mision(2).disponible(progreso)
    progreso.cumplir_mision(1)
    assert progreso.encontrar_fragmento("F01") and not progreso.encontrar_fragmento("F01")
    otra_vez = Progreso(archivo)
    assert otra_vez.misiones == {1} and otra_vez.fragmentos == {"F01"}
    assert mision(2).disponible(otra_vez) and not mision(3).disponible(otra_vez)


# ---------- El recorrido ----------

def ir_al_mapa(app):
    tecla(pygame.K_DOWN)                # HISTORIA
    avanzar(app)
    tecla(pygame.K_RETURN)
    avanzar(app)
    assert isinstance(app.escena, Mapa)
    return app.escena


def test_del_inicio_al_mapa_al_dialogo_y_a_la_mision(app):
    mapa = ir_al_mapa(app)
    assert mapa.elegida == 1
    tecla(pygame.K_RETURN)
    avanzar(app)
    assert isinstance(app.escena, Dialogo)
    tecla(pygame.K_ESCAPE)              # saltear el dialogo
    avanzar(app)
    assert isinstance(app.escena, Listo)
    partida = app.escena.partida
    assert isinstance(partida.modo, ModoHistoria) and partida.modo.mision is mision(1)
    assert partida.nivel == 1 and partida.director.sector is SECTORES[0]
    avanzar(app, 101)
    assert isinstance(app.escena, Juego)


def test_una_mision_bloqueada_no_despega(app):
    mapa = ir_al_mapa(app)
    tecla(pygame.K_RIGHT)
    avanzar(app)
    assert mapa.elegida == 2
    tecla(pygame.K_RETURN)
    avanzar(app)
    assert app.escena is mapa


def test_la_mision_2_empieza_en_su_sector(app):
    app.nueva_partida(modo=ModoHistoria(2))
    partida = app.escena.partida
    assert partida.nivel == JEFE_CADA_NIVELES + 1
    assert partida.director.sector is SECTORES[1] and partida.director.numero_tramo == 1


def mision_en_juego(app, numero=1):
    app.nueva_partida(modo=ModoHistoria(numero))
    avanzar(app, 101)
    partida = app.escena.partida
    partida.nave.invulnerable_hasta = math.inf
    partida.director.con_escuadrones = False
    partida.proximo_powerup = math.inf
    partida.moneda.x, partida.moneda.y = -500, -500
    return partida


def test_vencer_al_jefe_cumple_la_mision_y_vuelve_al_mapa(app):
    partida = mision_en_juego(app)
    partida.nivel = JEFE_CADA_NIVELES - 1
    partida.subir_nivel()
    partida.jefe_vencido()
    avanzar(app, int((CARTEL_JEFE + CARTEL_RANGO) / MS_POR_FRAME) + 40)     # (+ el hit-stop de la explosion)
    assert isinstance(app.escena, Dialogo)          # el dialogo de despues
    assert 1 in app.progreso.misiones
    assert partida.director.sector is SECTORES[0]   # (no pasa al sector siguiente)
    tecla(pygame.K_ESCAPE)
    avanzar(app)
    assert isinstance(app.escena, Mapa) and app.escena.elegida == 2


def test_si_la_nave_explota_ines_te_saca_y_no_hay_records(app):
    partida = mision_en_juego(app)
    partida.nave.invulnerable_hasta = 0
    partida.vidas = 1
    partida.danar_jugador(*partida.nave.centro())
    avanzar(app, 140)
    assert isinstance(app.escena, Dialogo)
    assert app.records.maximo(partida.dificultad) == 0
    tecla(pygame.K_ESCAPE)
    avanzar(app)
    assert isinstance(app.escena, Mapa) and app.escena.elegida == 1


def test_en_cada_mision_abre_el_taller(app):
    partida = mision_en_juego(app, 2)
    partida.director.con_mejoras = True
    for _ in range(MEJORA_TRAMO_HISTORIA - 1):
        partida.subir_nivel()
    assert partida.director.numero_tramo == MEJORA_TRAMO_HISTORIA and partida.director.ofertas


# ---------- La radio ----------

def test_cada_tramo_tiene_su_mensaje_de_radio(app):
    partida = mision_en_juego(app)
    partida.radio.vaciar()                  # (el del tramo 1)
    partida.subir_nivel()                   # tramo 2
    jugar(partida, int(RADIO_DEMORA_TRAMO / MS_POR_FRAME) + 2)
    assert partida.radio.actual is not None
    assert partida.radio.actual.texto == mision(1).radio["tramo_2"][0][1]
    avanzar(app)                            # (y se dibuja)


def test_en_el_arcade_nadie_habla(partida):
    partida.subir_nivel()
    jugar(partida, int(RADIO_DEMORA_TRAMO / MS_POR_FRAME) + 2)
    assert partida.radio.actual is None and partida.modo.nombre == "arcade"


# ---------- Los secretos de la mision 1 ----------

def juntar_monedas(partida, cuantas):
    for _ in range(cuantas):
        partida.moneda.x, partida.moneda.y = partida.nave.x + 15, partida.nave.y + 15
        jugar(partida)
    partida.moneda.x, partida.moneda.y = -500, -500


def opciones_del_secreto(tipo):
    return next(datos[2] for datos in mision(1).secretos if datos[0] == tipo)


def test_la_moneda_grabada_aparece_una_vez_y_va_al_archivo(app):
    partida = mision_en_juego(app)
    partida.subir_nivel()                   # (desde el tramo 2)
    pedidas = opciones_del_secreto("moneda_grabada")["monedas"]
    juntar_monedas(partida, pedidas - 1)
    assert not partida.modo.reliquias
    juntar_monedas(partida, 1)
    grabada = partida.modo.reliquias[0]
    assert isinstance(grabada, MonedaGrabada) and grabada.fragmento == "F01"
    partida.nave.x, partida.nave.y = grabada.x - 15, grabada.y - 15
    jugar(partida)
    assert "F01" in app.progreso.fragmentos and partida.modo.reliquias == []
    juntar_monedas(partida, 20)
    assert partida.modo.reliquias == []             # una sola vez


def test_la_moneda_grabada_se_apaga_si_no_la_agarras(app):
    partida = mision_en_juego(app)
    partida.subir_nivel()
    juntar_monedas(partida, opciones_del_secreto("moneda_grabada")["monedas"])
    partida.nave.x, partida.nave.y = 500, 500
    partida.modo.reliquias[0].x, partida.modo.reliquias[0].y = 100, 150
    jugar(partida, int(MONEDA_GRABADA_DURA / MS_POR_FRAME) + 2)
    assert partida.modo.reliquias == [] and "F01" not in app.progreso.fragmentos


def test_los_restos_de_la_errante_solo_se_abren_con_el_dash(app):
    partida = mision_en_juego(app)
    partida.subir_nivel()
    partida.subir_nivel()                   # tramo 3
    jugar(partida, int(RESTOS_ESPERA / MS_POR_FRAME) + 2)
    restos = partida.modo.reliquias[0]
    assert isinstance(restos, Restos)
    partida.nave.x, partida.nave.y = restos.caja().centerx - 25, restos.caja().centery - 25
    jugar(partida)
    assert "F02" not in app.progreso.fragmentos      # pasar por encima no alcanza
    partida.nave.dash_hasta = partida.tiempo + 500
    partida.nave.x, partida.nave.y = restos.caja().centerx - 25, restos.caja().centery - 25
    jugar(partida)
    assert "F02" in app.progreso.fragmentos


@pytest.mark.parametrize("golpes, encontrado", [(0, True), (1, False)])
def test_la_mirada_del_ojo_pide_un_sector_sin_golpes(app, golpes, encontrado):
    partida = mision_en_juego(app)
    partida.nivel = JEFE_CADA_NIVELES - 1
    partida.subir_nivel()
    partida.director.bitacora.golpes = golpes
    partida.jefe_vencido()
    assert ("F03" in app.progreso.fragmentos) == encontrado


def test_encontrar_algo_lo_cuenta_la_radio(app):
    partida = mision_en_juego(app)
    partida.radio.vaciar()
    partida.modo.encontrar("F02")
    jugar(partida)
    assert partida.radio.actual.texto == next(f for f in mision(1).fragmentos if f.id == "F02").reaccion[0][1]


# ---------- Que todo se dibuje ----------

def test_el_mapa_el_dialogo_y_el_archivo_se_dibujan(app):
    mapa = ir_al_mapa(app)
    app.progreso.cumplir_mision(1)
    app.progreso.encontrar_fragmento("F01")
    avanzar(app)
    app.cambiar_escena(Archivo(app, volver_a=mapa), transicion=False)
    avanzar(app)
    app.progreso.encontrar_fragmento(CLAVE_DE_LOS_GLIFOS)       # con la clave, el glifo se traduce
    avanzar(app)
    app.cambiar_escena(Dialogo(app, mision(1).antes, lambda: None, "MISION 1", "LA SEÑAL"), transicion=False)
    avanzar(app, 30)
