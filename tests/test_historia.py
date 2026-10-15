"""Modo historia: el estandar de las misiones, el avance guardado, el recorrido, la radio,
cada secreto, la mision oculta, los dos finales y las fichas del Archivo."""
import math
import types

import pygame
import pytest

from juego import carteles, dibujo, recursos
from juego.config import (SECTORES, JEFE_CADA_NIVELES, CARTEL_JEFE, CARTEL_RANGO, MS_POR_FRAME, RADIO_DEMORA_TRAMO,
                          MONEDA_GRABADA_DURA, RESTOS_ESPERA, BALIZA_ESPERA, MEJORA_TRAMO_HISTORIA, ANCHO, ALTO,
                          AVISO_TRAMO, SEGUIR_MINIMO)
from juego.guardado import Progreso
from juego.enemigos import TIPOS_ENEMIGO, crear_enemigo
from juego.jefes import TIPOS_JEFE
from juego.powerups import TIPOS_POWERUP
from juego.anomalias import TIPOS_ANOMALIA
from juego.escuadrones import FORMACIONES
from juego.objetivos import crear_objetivo
from juego.historia.mision import (misiones_en_orden, todos_los_fragmentos, mision, filtrar, ids_de_la_condicion,
                                   ids_de_fragmentos, buscar_fragmento)
from juego.historia.modo import ModoHistoria, MIRAR_CADA
from juego.historia.personajes import PERSONAJES
from juego.historia.secretos import TIPOS_SECRETO
from juego.historia.glifos import traducir, escribir, CLAVE_DE_LOS_GLIFOS
from juego.historia.reliquias import MonedaGrabada, Restos, Baliza
from juego.historia import fichas
from juego.escenas.historia.archivo import Archivo, LISTA, DETALLE, COLUMNA_NOMBRE, PESTANAS, ALTO_GLIFO, acomodar
from juego.escenas.historia.dialogo import Dialogo, ANCHO_TEXTO
from juego.escenas.historia.galaxia import Galaxia, VIAJE_PASOS
from juego.historia.galaxia import ANCHO_GALAXIA, ALTO_GALAXIA
from juego.escenas.historia.final import Final
from juego.escenas.juego import Juego
from juego.escenas.listo import Listo
from tests.ayudas import avanzar, tecla, jugar

MOMENTOS_DE_RADIO = {"tramo_1", "tramo_2", "tramo_3", "tramo_4", "jefe"}


def renglones_de(clase):
    # Todos los renglones de una mision (dialogos, radio, reacciones y pistas)
    yield from clase.antes
    yield from clase.despues
    for renglones in clase.radio.values():
        yield from renglones
    for fragmento in clase.fragmentos:
        yield from fragmento.reaccion
    for _, _, *opciones in clase.secretos:
        yield from (opciones[0].get("pista", []) if opciones else [])


def renglones_de_radio(clase):
    # Los que salen en la caja de la radio (tienen menos lugar que el dialogo)
    for renglones in clase.radio.values():
        yield from renglones
    for fragmento in clase.fragmentos:
        yield from fragmento.reaccion
    for _, _, *opciones in clase.secretos:
        yield from (opciones[0].get("pista", []) if opciones else [])


# ---------- El estandar de las misiones (lo que tiene que cumplir un archivo nuevo) ----------

def test_las_misiones_van_en_orden_y_cada_una_en_un_sector_y_un_lugar():
    misiones = misiones_en_orden()
    assert [clase.numero for clase in misiones] == list(range(1, len(misiones) + 1))
    for clase in misiones:
        assert clase.titulo and clase.antes and clase.despues
        assert 1 <= clase.sector <= len(SECTORES)
        x, y = clase.lugar
        assert 40 <= x <= ANCHO_GALAXIA - 40 and 40 <= y <= ALTO_GALAXIA - 40, clase.titulo   # (en la galaxia)
        if clase.oculta:
            assert clase.requisitos and set(clase.requisitos) <= set(ids_de_fragmentos())
            assert clase.rama_de in [otra.numero for otra in misiones]
    assert sum(1 for clase in misiones if clase.final) == 1


def test_las_rutas_de_las_misiones_siguen_las_reglas_de_las_rutas():
    # Las mismas que el arcade (rutas.py), en el orden de la historia: un enemigo nuevo por
    # tramo como mucho y nunca en el asedio; el objetivo se puede cumplir con lo que trae
    vistos = set()
    for clase in misiones_en_orden():
        assert clase.tramos is None or len(clase.tramos) == JEFE_CADA_NIVELES - 1
        for numero, tramo in enumerate(clase.tramos or [], start=1):
            assert len(tramo["nombre"]) <= 16, tramo["nombre"]
            tipos = {tipo for tipo, _, _ in tramo["escuadrones"]}
            for tipo, cantidad, formacion in tramo["escuadrones"]:
                assert tipo in TIPOS_ENEMIGO and not TIPOS_ENEMIGO[tipo].esbirro
                assert formacion in FORMACIONES and cantidad >= 1
            nuevos = tipos - vistos
            assert len(nuevos) <= 1, tramo["nombre"]
            assert not (tramo.get("asedio") and nuevos), tramo["nombre"]
            vistos |= nuevos
            objetivo = crear_objetivo(tramo["objetivo"], 1.5)
            if objetivo.tipo == "romper":
                assert objetivo.enemigo in tipos
            elif objetivo.tipo == "interceptar":
                assert "embestidor" in tipos
            elif objetivo.tipo == "perfectos":
                assert any(TIPOS_ENEMIGO[tipo].destruible for tipo in tipos)
            objetivo.progreso = objetivo.meta
            assert len(objetivo.texto()) <= 32 and len(objetivo.etiqueta()) <= 15
            # Con jefe: el tramo 4 es el asedio. Sin jefe, no hay asedio
            assert bool(tramo.get("asedio")) == (clase.jefe and numero == 4), tramo["nombre"]
            assert tramo.get("anomalia") is None or tramo["anomalia"] in TIPOS_ANOMALIA


def test_la_radio_habla_solo_en_momentos_que_existen():
    for clase in misiones_en_orden():
        assert set(clase.radio) <= MOMENTOS_DE_RADIO, clase.titulo
        if not clase.jefe:
            assert "jefe" not in clase.radio


def test_los_fragmentos_no_se_repiten_y_cada_secreto_da_uno_de_su_mision():
    ids = ids_de_fragmentos()
    assert len(ids) == len(set(ids))
    for clase in misiones_en_orden():
        propios = {fragmento.id for fragmento in clase.fragmentos}
        secretos = [fragmento for _, fragmento, *_ in clase.secretos]
        assert set(secretos) == propios, clase.titulo          # cada fragmento se puede encontrar
        for tipo, fragmento, *opciones in clase.secretos:
            assert tipo in TIPOS_SECRETO, tipo
            requiere = opciones[0].get("requiere", []) if opciones else []
            assert requiere == "todos" or set(requiere) <= set(ids), (fragmento, requiere)


def test_las_condiciones_nombran_fragmentos_que_existen():
    ids = set(ids_de_fragmentos())
    for clase in misiones_en_orden():
        for renglon in renglones_de(clase):
            if len(renglon) > 2:
                assert set(ids_de_la_condicion(renglon[2])) <= ids, renglon


def test_quien_habla_existe_y_los_textos_entran(app):
    for clase in misiones_en_orden():
        for renglon in renglones_de(clase):
            personaje, texto = renglon[0], renglon[1]
            assert personaje in PERSONAJES
            assert not set(texto) & set("ÁÉÍÓÚ"), texto         # (la fuente las dibuja mal)
            assert len(dibujo.partir_lineas(texto, dibujo.CHICA, ANCHO_TEXTO)) <= 4, texto


def test_la_radio_tiene_lugar_para_cada_mensaje(app):
    for clase in misiones_en_orden():
        for renglon in renglones_de_radio(clase):
            assert len(carteles.lineas_radio(renglon[1])) <= 3, renglon[1]


def alto_del_detalle(parrafos, glifo, con_dibujo):
    # Lo que ocupa el texto en el panel de la derecha del Archivo (la misma cuenta que el dibujo)
    _, alto = acomodar(parrafos, DETALLE.width - 32, con_dibujo)
    return alto + (ALTO_GLIFO if glifo else 0)


def test_cada_fragmento_y_cada_ficha_entran_en_el_archivo(app):
    lugar = LISTA.width - 32 - COLUMNA_NOMBRE
    alto = DETALLE.height - 40
    for fragmento, _ in todos_los_fragmentos():
        assert recursos.fuente(dibujo.CHICA).size(fragmento.nombre)[0] <= lugar, fragmento.nombre
        assert recursos.fuente(dibujo.CHICA).size(fragmento.nombre)[0] <= DETALLE.width - 60, fragmento.nombre
        assert alto_del_detalle(fragmento.texto, fragmento.glifo, False) <= alto, fragmento.nombre
    for ficha in fichas.FICHAS:
        assert recursos.fuente(dibujo.CHICA).size(ficha.nombre)[0] <= LISTA.width - 40, ficha.nombre
        assert not set(" ".join(ficha.texto)) & set("ÁÉÍÓÚ"), ficha.nombre
        assert alto_del_detalle(ficha.texto, ficha.glifo, True) <= alto, ficha.nombre


def test_los_glifos_se_traducen_y_la_firma_dice_alba():
    assert traducir(buscar_fragmento("F01").glifo) == "ALBA"
    assert CLAVE_DE_LOS_GLIFOS in ids_de_fragmentos()
    for fragmento, _ in todos_los_fragmentos():
        if fragmento.glifo:
            assert "?" not in traducir(fragmento.glifo), fragmento.id
            assert escribir(traducir(fragmento.glifo)) == fragmento.glifo


def test_todo_lo_del_juego_tiene_su_ficha():
    # Un enemigo, jefe, power-up o anomalia nuevo necesita su porque en el Archivo
    for tipo in TIPOS_ENEMIGO:
        assert fichas.id_de("enemigo", tipo) in fichas.POR_ID, tipo
    for tipo in TIPOS_JEFE:
        assert fichas.id_de("jefe", tipo) in fichas.POR_ID, tipo
    for tipo in TIPOS_POWERUP:
        assert fichas.id_de("powerup", tipo) in fichas.POR_ID, tipo
    for tipo in TIPOS_ANOMALIA:
        assert fichas.id_de("anomalia", tipo) in fichas.POR_ID, tipo
    assert set(fichas.BASICAS) <= set(fichas.POR_ID)
    assert len(fichas.POR_ID) == len(fichas.FICHAS)


def test_los_renglones_se_filtran_con_lo_encontrado():
    renglones = [("alba", "SIEMPRE"), ("alba", "CON F01", "F01"), ("alba", "SIN F01", "!F01"),
                 ("alba", "LAS DOS", "F01+F06")]
    assert [texto for _, texto in filtrar(renglones, set())] == ["SIEMPRE", "SIN F01"]
    assert [texto for _, texto in filtrar(renglones, {"F01"})] == ["SIEMPRE", "CON F01"]
    assert [texto for _, texto in filtrar(renglones, {"F01", "F06"})] == ["SIEMPRE", "CON F01", "LAS DOS"]


# ---------- El avance guardado ----------

def test_el_avance_se_guarda_y_se_vuelve_a_cargar(tmp_path):
    archivo = str(tmp_path / "progreso.json")
    progreso = Progreso(archivo)
    assert mision(1).disponible(progreso) and not mision(2).disponible(progreso)
    progreso.cumplir_mision(1)
    assert progreso.encontrar_fragmento("F01") and not progreso.encontrar_fragmento("F01")
    assert progreso.anotar_ficha("enemigo:ladron") and not progreso.anotar_ficha("enemigo:ladron")
    otra_vez = Progreso(archivo)
    assert otra_vez.misiones == {1} and otra_vez.fragmentos == {"F01"} and otra_vez.fichas == {"enemigo:ladron"}
    assert mision(2).disponible(otra_vez) and not mision(3).disponible(otra_vez)


def test_la_mision_oculta_aparece_con_las_tres_bitacoras(tmp_path):
    progreso = Progreso(str(tmp_path / "progreso.json"))
    oculta = next(clase for clase in misiones_en_orden() if clase.oculta)
    assert not oculta.visible(progreso)
    for id_ in oculta.requisitos[:-1]:
        progreso.encontrar_fragmento(id_)
    assert not oculta.visible(progreso)
    progreso.encontrar_fragmento(oculta.requisitos[-1])
    assert oculta.visible(progreso) and oculta.disponible(progreso)


# ---------- El recorrido ----------

def ir_al_mapa(app):
    tecla(pygame.K_DOWN)                # HISTORIA
    avanzar(app)
    tecla(pygame.K_RETURN)
    avanzar(app)
    assert isinstance(app.escena, Galaxia)
    return app.escena


def viajar(app, galaxia, id_sistema):
    # Elegir un sistema en la galaxia y viajar (el vuelo dura VIAJE_PASOS)
    galaxia.elegida = id_sistema
    tecla(pygame.K_RETURN)
    avanzar(app, VIAJE_PASOS + 2)


def test_del_inicio_al_mapa_al_dialogo_y_a_la_mision(app):
    mapa = ir_al_mapa(app)
    assert mapa.elegida == "UMBRAL"             # la Alondra sale de casa
    tecla(pygame.K_RIGHT)
    avanzar(app)
    assert mapa.elegida == "M1"                 # (a la derecha, la mas cercana)
    viajar(app, mapa, "M1")
    assert isinstance(app.escena, Dialogo)
    tecla(pygame.K_ESCAPE)              # saltear el dialogo
    avanzar(app)
    assert isinstance(app.escena, Listo)
    partida = app.escena.partida
    assert isinstance(partida.modo, ModoHistoria) and partida.modo.mision is mision(1)
    assert partida.nivel == 1 and partida.director.sector is SECTORES[0]
    assert partida.director.tramo is mision(1).tramos[0]          # su ruta, no la del arcade
    avanzar(app, 101)
    assert isinstance(app.escena, Juego)


def test_una_mision_bloqueada_no_despega(app):
    mapa = ir_al_mapa(app)
    viajar(app, mapa, "M2")
    assert app.escena is mapa and app.progreso.anios == 0 and app.progreso.ubicacion == "UMBRAL"


def test_el_mapa_muestra_la_oculta_solo_con_sus_requisitos(app):
    assert "M6" not in [uno.id for uno in ir_al_mapa(app).sistemas()]
    for id_ in ("F02", "F04", "F07"):
        app.progreso.encontrar_fragmento(id_)
    mapa = Galaxia(app)
    assert "M6" in [uno.id for uno in mapa.sistemas()]
    app.cambiar_escena(mapa, transicion=False)
    viajar(app, mapa, "M6")
    assert isinstance(app.escena, Dialogo)


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
    partida.director.con_mejoras = False        # (sin el Taller en el medio)
    partida.proximo_powerup = math.inf
    partida.moneda.x, partida.moneda.y = -500, -500
    return partida


def ir_al_tramo(partida, numero):
    while partida.director.numero_tramo < numero:
        partida.subir_nivel()


def ir_al_jefe(partida):
    clase = partida.modo.mision
    partida.nivel = (clase.sector - 1) * JEFE_CADA_NIVELES + JEFE_CADA_NIVELES - 1
    partida.subir_nivel()
    assert partida.jefe is not None


def test_vencer_al_jefe_cumple_la_mision_y_vuelve_al_mapa(app):
    partida = mision_en_juego(app)
    ir_al_jefe(partida)
    partida.jefe_vencido()
    avanzar(app, int((CARTEL_JEFE + CARTEL_RANGO) / MS_POR_FRAME) + 40)     # (+ el hit-stop de la explosion)
    assert isinstance(app.escena, Dialogo)          # el dialogo de despues
    assert 1 in app.progreso.misiones
    assert partida.director.sector is SECTORES[0]   # (no pasa al sector siguiente)
    tecla(pygame.K_ESCAPE)
    avanzar(app)
    assert isinstance(app.escena, Galaxia) and app.escena.elegida == "M1"


def test_el_dialogo_de_despues_cambia_con_lo_encontrado(app):
    partida = mision_en_juego(app)
    app.progreso.encontrar_fragmento("F02")
    ir_al_jefe(partida)
    partida.jefe_vencido()
    avanzar(app, int((CARTEL_JEFE + CARTEL_RANGO) / MS_POR_FRAME) + 40)
    textos = [texto for _, texto in app.escena.renglones]
    assert "Y ENCONTRE RESTOS DE UNA NAVE. TENIAN UNA BITACORA." in textos
    assert not any("FIRMA" in texto for texto in textos)            # (sin F01, eso no se dice)


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
    assert isinstance(app.escena, Galaxia) and app.escena.elegida == "M1"


def test_en_la_historia_no_salen_logros(app):
    # Miden el avance del arcade: empezar una mision en el sector 5 no es llegar al sector 5
    partida = mision_en_juego(app, 5)
    jugar(partida, 60)
    partida.revisar_logros()
    assert not app.progreso.logros and not partida.logros_nuevos


def test_en_cada_mision_abre_el_taller(app):
    partida = mision_en_juego(app, 2)
    partida.director.con_mejoras = True
    ir_al_tramo(partida, MEJORA_TRAMO_HISTORIA)
    assert partida.director.ofertas


def test_cada_tramo_trae_la_anomalia_que_pide_su_ruta(app):
    partida = mision_en_juego(app, 3)
    ir_al_tramo(partida, 3)
    for _ in range(20):
        assert partida.director.elegir_anomalia() == "niebla"


# ---------- La mision oculta: sin jefe ----------

def test_la_mision_sin_jefe_se_cumple_al_despejar_el_ultimo_tramo(app):
    partida = mision_en_juego(app, 6)
    ir_al_tramo(partida, 4)
    partida.director.cumplir_objetivo()
    jugar(partida, 2)
    assert partida.jefe is None and partida.director.tramo is None
    assert app.escena.musica != "tension"
    avanzar(app, int(AVISO_TRAMO / MS_POR_FRAME) + 10)
    assert isinstance(app.escena, Dialogo) and 6 in app.progreso.misiones
    tecla(pygame.K_ESCAPE)
    avanzar(app)
    assert isinstance(app.escena, Galaxia)


# ---------- La radio ----------

def test_cada_tramo_tiene_su_mensaje_de_radio(app):
    partida = mision_en_juego(app)
    partida.radio.vaciar()                  # (el del tramo 1)
    partida.subir_nivel()                   # tramo 2
    jugar(partida, int(RADIO_DEMORA_TRAMO / MS_POR_FRAME) + 2)
    assert partida.radio.actual is not None
    assert partida.radio.actual.texto == mision(1).radio["tramo_2"][0][1]
    avanzar(app)                            # (y se dibuja)


def test_la_radio_dice_las_pistas_solo_si_falta_lo_que_buscan(app):
    partida = mision_en_juego(app)
    partida.radio.vaciar()
    app.progreso.encontrar_fragmento("F01")
    partida.subir_nivel()                   # tramo 2: la pista de la moneda grabada ya no va
    textos = [mensaje.texto for mensaje in partida.radio.esperando]
    assert not any("SIMBOLO GRABADO" in texto for texto in textos)


def test_en_el_arcade_nadie_habla(partida):
    partida.subir_nivel()
    jugar(partida, int(RADIO_DEMORA_TRAMO / MS_POR_FRAME) + 2)
    assert partida.radio.actual is None and partida.modo.nombre == "arcade"


# ---------- Los secretos: lo que aparece en pantalla ----------

def juntar_monedas(partida, cuantas):
    for _ in range(cuantas):
        partida.moneda.x, partida.moneda.y = partida.nave.x + 15, partida.nave.y + 15
        jugar(partida)
    partida.moneda.x, partida.moneda.y = -500, -500


def opciones_del_secreto(clase, tipo):
    return next(datos[2] for datos in clase.secretos if datos[0] == tipo)


def secreto(partida, tipo):
    return next(s for s in partida.modo.secretos if s.tipo == tipo)


def test_la_moneda_grabada_aparece_una_vez_y_va_al_archivo(app):
    partida = mision_en_juego(app)
    partida.subir_nivel()                   # (desde el tramo 2)
    pedidas = opciones_del_secreto(mision(1), "moneda_grabada")["monedas"]
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
    juntar_monedas(partida, opciones_del_secreto(mision(1), "moneda_grabada")["monedas"])
    partida.nave.x, partida.nave.y = 500, 500
    partida.modo.reliquias[0].x, partida.modo.reliquias[0].y = 100, 150
    jugar(partida, int(MONEDA_GRABADA_DURA / MS_POR_FRAME) + 2)
    assert partida.modo.reliquias == [] and "F01" not in app.progreso.fragmentos


def abrir_con_el_dash(partida, reliquia):
    caja = reliquia.caja()
    partida.nave.x, partida.nave.y = caja.centerx - 25, caja.centery - 25
    jugar(partida)
    assert reliquia.fragmento not in partida.modo.lo_encontrado()       # pasar por encima no alcanza
    partida.nave.dash_hasta = partida.tiempo + 500
    caja = reliquia.caja()
    partida.nave.x, partida.nave.y = caja.centerx - 25, caja.centery - 25
    jugar(partida)


def test_los_restos_de_la_errante_solo_se_abren_con_el_dash(app):
    partida = mision_en_juego(app)
    ir_al_tramo(partida, 3)
    jugar(partida, int(RESTOS_ESPERA / MS_POR_FRAME) + 2)
    restos = partida.modo.reliquias[0]
    assert isinstance(restos, Restos)
    abrir_con_el_dash(partida, restos)
    assert "F02" in app.progreso.fragmentos


def test_la_baliza_titila_su_mensaje_y_se_abre_con_el_dash(app):
    partida = mision_en_juego(app, 2)
    ir_al_tramo(partida, 3)
    partida.radio.vaciar()
    jugar(partida, int(BALIZA_ESPERA / MS_POR_FRAME) + 2)
    baliza = partida.modo.reliquias[0]
    assert isinstance(baliza, Baliza) and traducir(baliza.glifo) == "SEGUI"
    avanzar(app)                            # (se dibuja)
    abrir_con_el_dash(partida, baliza)
    assert "F12" in app.progreso.fragmentos


# ---------- Los secretos: lo que se encuentra jugando distinto ----------

@pytest.mark.parametrize("golpes, encontrado", [(0, True), (1, False)])
def test_la_mirada_del_ojo_pide_un_sector_sin_golpes(app, golpes, encontrado):
    partida = mision_en_juego(app)
    ir_al_jefe(partida)
    partida.director.bitacora.golpes = golpes
    partida.jefe_vencido()
    assert ("F03" in app.progreso.fragmentos) == encontrado


@pytest.mark.parametrize("en_orden", [True, False])
def test_los_cañones_del_acorazado_se_rompen_en_orden(app, en_orden):
    partida = mision_en_juego(app, 2)
    ir_al_jefe(partida)
    jefe = partida.jefe
    orden = sorted(jefe.partes, key=lambda parte: parte.dx)
    if not en_orden:
        orden[0], orden[1] = orden[1], orden[0]
    for parte in orden:
        parte.vida = 0
        partida.modo.al_romper_parte(jefe, parte)
    assert ("F04" in app.progreso.fragmentos) == en_orden


def ladron_con_la_moneda(partida):
    ladron = crear_enemigo("ladron", partida)
    partida.enemigos.append(ladron)
    partida.moneda.robada_por = ladron
    return ladron


@pytest.mark.parametrize("de_cerca", [True, False])
def test_el_cartero_pide_seguir_al_ladron_hasta_que_se_escapa(app, de_cerca):
    partida = mision_en_juego(app, 3)
    cartero = secreto(partida, "seguir_al_ladron")
    ladron = ladron_con_la_moneda(partida)
    for _ in range(int(SEGUIR_MINIMO / MS_POR_FRAME) + 5):
        ladron_x, ladron_y = ladron.centro()
        lejos = 60 if de_cerca else 400
        partida.nave.x, partida.nave.y = ladron_x - 25 - lejos, ladron_y - 25
        partida.tiempo += MS_POR_FRAME
        cartero.actualizar()
    partida.moneda_escapada(ladron)
    assert ("F05" in app.progreso.fragmentos) == de_cerca


def test_quieta_en_la_niebla_se_oye_el_compas(app, monkeypatch):
    partida = mision_en_juego(app, 3)
    sonidos = []
    original = partida.sonidos.reproducir
    monkeypatch.setattr(partida.sonidos, "reproducir", lambda nombre, *otros: sonidos.append(nombre)
                        or original(nombre, *otros))
    ir_al_tramo(partida, 3)
    partida.director.empezar_anomalia()
    assert partida.director.anomalia.tipo == "niebla"
    compas = secreto(partida, "quieto_en_anomalia")
    # Moverse vuelve a empezar la cuenta
    jugar(partida, 200, dx=1)
    assert "F06" not in app.progreso.fragmentos
    partida.nave.vx = partida.nave.vy = 0
    sonidos.clear()
    jugar(partida, int(compas.duracion / MS_POR_FRAME) + 5)
    assert "F06" in app.progreso.fragmentos
    # Sonaron los 12 pulsos de A-L-B-A (.- .-.. -... .-): 8 cortos y 4 largos
    assert sonidos.count("onda_corta") == 8 and sonidos.count("onda_larga") == 4


def test_veinte_monedas_seguidas_captan_el_eco_de_la_errante(app):
    partida = mision_en_juego(app, 4)
    partida.combo = opciones_del_secreto(mision(4), "racha")["monedas"] - 2
    partida.ultima_moneda = partida.tiempo
    juntar_monedas(partida, 1)
    assert "F07" not in app.progreso.fragmentos
    juntar_monedas(partida, 1)
    assert "F07" in app.progreso.fragmentos


@pytest.mark.parametrize("rompio_una_abeja", [False, True])
def test_las_bibliotecarias_no_se_tocan(app, rompio_una_abeja):
    partida = mision_en_juego(app, 4)
    ir_al_jefe(partida)
    if rompio_una_abeja:
        partida.director.al_romper(types.SimpleNamespace(tipo="abeja"))
    partida.director.al_romper(types.SimpleNamespace(tipo="enjambre"))      # (otra cosa, si)
    partida.jefe_vencido()
    assert ("F08" in app.progreso.fragmentos) != rompio_una_abeja


@pytest.mark.parametrize("con_la_mirada, desde, encontrado",
                         [(True, "izquierda", True), (True, "derecha", False), (False, "izquierda", False)])
def test_la_brujula_pide_pegarle_desde_el_lado_de_casa(app, con_la_mirada, desde, encontrado):
    if con_la_mirada:
        app.progreso.encontrar_fragmento("F03")
    partida = mision_en_juego(app, 5)
    ir_al_jefe(partida)
    centro_x, centro_y = partida.jefe.centro_nucleo()
    lado = -1 if desde == "izquierda" else 1
    partida.nave.x, partida.nave.y = centro_x + lado * 120 - 25, centro_y - 25
    partida.modo.al_golpear_jefe(partida.jefe)
    assert ("F09" in app.progreso.fragmentos) == encontrado


@pytest.mark.parametrize("falta_uno", [False, True])
def test_la_bitacora_sin_fecha_pide_todo_lo_demas(app, falta_uno):
    demas = [id_ for id_ in ids_de_fragmentos() if id_ != "F11"]
    for id_ in demas[:-1] if falta_uno else demas:
        app.progreso.encontrar_fragmento(id_)
    partida = mision_en_juego(app, 5)
    ir_al_jefe(partida)
    partida.jefe_vencido()
    assert ("F11" in app.progreso.fragmentos) != falta_uno


def test_la_otra_firma_esta_en_la_estela(app):
    partida = mision_en_juego(app, 6)
    pedidas = opciones_del_secreto(mision(6), "moneda_grabada")["monedas"]
    juntar_monedas(partida, pedidas + 2)
    assert not partida.modo.reliquias                    # (antes del tramo 4 no cuenta)
    ir_al_tramo(partida, 4)
    juntar_monedas(partida, pedidas)
    grabada = partida.modo.reliquias[0]
    assert grabada.fragmento == "F13" and traducir(buscar_fragmento("F13").glifo) == "MATEO"


def test_encontrar_algo_suena_y_lo_cuenta_la_radio(app, monkeypatch):
    partida = mision_en_juego(app)
    sonidos = []
    monkeypatch.setattr(partida.sonidos, "reproducir", lambda nombre, *otros: sonidos.append(nombre))
    partida.radio.vaciar()
    partida.modo.encontrar("F02")
    jugar(partida)
    assert "fragmento" in sonidos
    assert partida.radio.actual.texto == buscar_fragmento("F02").reaccion[0][1]


# ---------- Los finales ----------

def terminar_la_ultima(app):
    partida = mision_en_juego(app, 5)
    ir_al_jefe(partida)
    partida.jefe_vencido()
    avanzar(app, int((CARTEL_JEFE + CARTEL_RANGO) / MS_POR_FRAME) + 40)
    assert isinstance(app.escena, Dialogo)
    return [personaje for personaje, _ in app.escena.renglones]


@pytest.mark.parametrize("verdadero", [False, True])
def test_despues_de_la_ultima_mision_viene_el_final(app, verdadero):
    if verdadero:
        app.progreso.encontrar_fragmento("F11")
    quienes = terminar_la_ultima(app)
    assert ("voz" in quienes) == verdadero              # la Bitacora sin fecha, solo con la verdad
    tecla(pygame.K_ESCAPE)
    avanzar(app)
    assert isinstance(app.escena, Final)
    assert app.escena.musica == ("iniciales" if verdadero else "fin")
    avanzar(app, 300)                       # (se dibuja todo)
    tecla(pygame.K_RETURN)
    avanzar(app)
    assert isinstance(app.escena, Galaxia)


def test_el_mapa_cambia_su_frase_con_la_historia(app):
    mapa = ir_al_mapa(app)
    avanzar(app)
    app.progreso.cumplir_mision(5)
    avanzar(app)
    app.progreso.encontrar_fragmento("F11")
    avanzar(app)
    assert isinstance(app.escena, Galaxia) and mapa is app.escena


# ---------- Las fichas del Archivo ----------

def test_lo_que_aparece_en_pantalla_se_anota_en_las_fichas(app):
    partida = mision_en_juego(app, 3)
    assert set(fichas.BASICAS) <= app.progreso.fichas
    ladron = crear_enemigo("ladron", partida)
    ladron.x, ladron.y = 300, 300
    partida.enemigos.append(ladron)
    chico = crear_enemigo("divisor_chico", partida)
    chico.x, chico.y = 500, 300
    partida.enemigos.append(chico)
    partida.director.empezar_anomalia("niebla")
    jugar(partida, MIRAR_CADA + 1)
    assert {"enemigo:ladron", "enemigo:divisor", "anomalia:niebla"} <= app.progreso.fichas


# ---------- Que todo se dibuje ----------

def test_el_archivo_no_cuenta_los_secretos_de_una_mision_oculta(app):
    archivo = Archivo(app, volver_a=None)
    ids = [entrada.id for entrada in archivo.entradas()]
    assert "F10" not in ids and "F11" not in ids          # (ni la mision oculta ni la verdad)
    for id_ in ("F02", "F04", "F07"):
        app.progreso.encontrar_fragmento(id_)
    assert "F10" in [entrada.id for entrada in archivo.entradas()]


def test_el_archivo_se_desplaza_y_muestra_todas_las_secciones(app):
    mapa = ir_al_mapa(app)
    app.progreso.cumplir_mision(1)
    for id_ in ids_de_fragmentos():
        app.progreso.encontrar_fragmento(id_)
    for ficha in fichas.FICHAS[::2]:
        app.progreso.anotar_ficha(ficha.id)
    archivo = Archivo(app, volver_a=mapa)
    app.cambiar_escena(archivo, transicion=False)
    for _ in range(len(archivo.entradas()) - 1):        # hasta el ultimo: la lista se desplaza
        tecla(pygame.K_DOWN)
        avanzar(app)
    assert archivo.elegido == len(archivo.entradas()) - 1 and archivo.primera > 0
    for _ in range(len(PESTANAS)):                      # cada seccion, con sus dibujos
        tecla(pygame.K_e)
        avanzar(app, 2)
        for _ in range(len(archivo.entradas())):
            tecla(pygame.K_DOWN)
            avanzar(app)
    assert archivo.pestana == 0
    app.cambiar_escena(Dialogo(app, mision(1).antes, lambda: None, "MISION 1", "LA SEÑAL"), transicion=False)
    avanzar(app, 30)


def test_la_pantalla_entra_en_la_ventana():
    assert LISTA.bottom <= ALTO - 50 and DETALLE.right <= ANCHO - 40
