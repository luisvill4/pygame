"""Modo desarrollador: el panel de F1 trae jefes, enemigos y power-ups, salta tramos y la partida no cuenta."""
import math

import pygame
import pytest

from juego import recursos
from juego.dibujo import CHICA, MEDIA
from juego.escenas import desarrollador, juego as escena_juego
from juego.config import JEFE_CADA_NIVELES
from juego.jefes import TIPOS_JEFE
from juego.escenas.desarrollador import Desarrollador, ELEGIBLES, nombre_de
from juego.escenas.historia.dialogo import Dialogo
from juego.historia.modo import ModoHistoria
from juego.escenas.explosion import Explosion
from juego.escenas.arcade.fin import Fin
from juego.escenas.arcade.iniciales import Iniciales
from juego.escenas.juego import Juego
from tests.ayudas import avanzar, tecla, empezar_partida, jugar


def abrir_panel(app, partida):
    juego = Juego(app, partida)
    panel = Desarrollador(app, juego, app.pantalla.copy())
    app.cambiar_escena(panel)
    return panel


def elegir(monkeypatch, fila, tipo):
    monkeypatch.setitem(desarrollador._elegido, fila, ELEGIBLES[fila].index(tipo))


def test_f1_abre_el_panel_y_vuelve_al_mismo_juego(app):
    empezar_partida(app)
    juego = app.escena
    tiempo = juego.partida.tiempo
    tecla(pygame.K_F1)
    avanzar(app)
    assert isinstance(app.escena, Desarrollador)
    avanzar(app, 30)
    assert juego.partida.tiempo == tiempo           # con el panel abierto la partida no corre
    tecla(pygame.K_F1)
    avanzar(app)
    assert app.escena is juego
    assert not juego.partida.modo_desarrollador     # abrirlo y cerrarlo no cuenta como usarlo


def test_apagado_en_config_f1_no_hace_nada(app, monkeypatch):
    monkeypatch.setattr(escena_juego, "MODO_DESARROLLADOR", False)
    empezar_partida(app)
    tecla(pygame.K_F1)
    avanzar(app)
    assert isinstance(app.escena, Juego)


def test_trae_el_jefe_elegido_y_lo_cambia_si_ya_habia_uno(app, partida, monkeypatch):
    panel = abrir_panel(app, partida)
    elegir(monkeypatch, "JEFE", "serpiente")
    panel.hacer("JEFE")
    assert partida.jefe.tipo == "serpiente"
    assert partida.modo_desarrollador
    elegir(monkeypatch, "JEFE", "colmena")
    panel.hacer("JEFE")
    assert partida.jefe.tipo == "colmena"
    assert partida.jefes_vencidos == 0              # cambiarlo no cuenta como vencerlo


def test_trae_un_enemigo_del_tipo_elegido(app, partida, monkeypatch):
    panel = abrir_panel(app, partida)
    elegir(monkeypatch, "ENEMIGO", "embestidor")
    panel.hacer("ENEMIGO")
    assert [e.tipo for e in partida.enemigos] == ["embestidor"]
    assert "abeja" not in ELEGIBLES["ENEMIGO"]       # las abejas solo existen con la Colmena


def test_da_el_power_up_elegido_si_se_puede(app, partida, monkeypatch):
    panel = abrir_panel(app, partida)
    elegir(monkeypatch, "POWER-UP", "escudo")
    panel.hacer("POWER-UP")
    assert partida.activo("escudo")
    # Con las vidas llenas, la vida no se da (no puede haber mas que vidas_max)
    elegir(monkeypatch, "POWER-UP", "vida")
    panel.hacer("POWER-UP")
    assert partida.vidas == partida.vidas_max


def test_invencible_no_pierde_vidas(app, partida):
    panel = abrir_panel(app, partida)
    panel.hacer("INVENCIBLE")
    partida.danar_jugador(100, 100)
    assert partida.vidas == partida.vidas_max
    panel.hacer("INVENCIBLE")
    partida.danar_jugador(100, 100)
    assert partida.vidas == partida.vidas_max - 1


def test_limpiar_saca_enemigos_y_balas(app, partida, monkeypatch):
    panel = abrir_panel(app, partida)
    elegir(monkeypatch, "ENEMIGO", "enjambre")
    panel.hacer("ENEMIGO")
    assert partida.enemigos
    panel.hacer("LIMPIAR")
    assert partida.enemigos == [] and partida.balas == []


def test_con_el_modo_desarrollador_no_hay_logros(partida, monkeypatch):
    monkeypatch.setattr("juego.partida.revisar_logros", lambda partida, progreso: ["un logro"])
    partida.progreso = object()
    partida.modo_desarrollador = True
    partida.revisar_logros()
    assert partida.fichas_logro == []


@pytest.mark.parametrize("con_trampa, escena_esperada", [(False, Iniciales), (True, Fin)])
def test_con_el_modo_desarrollador_no_se_guarda_el_record(app, partida, con_trampa, escena_esperada):
    partida.puntaje = 5000
    partida.modo_desarrollador = con_trampa
    partida.termino = True
    app.cambiar_escena(Explosion(app, partida))
    avanzar(app, 100)
    assert isinstance(app.escena, escena_esperada)


def test_el_panel_se_dibuja_y_los_nombres_entran(app, partida):
    panel = abrir_panel(app, partida)
    for pestana, (_, filas) in enumerate(panel.pestanas()):
        panel.pestana = pestana
        for i in range(len(filas)):
            panel.fila = i
            panel.dibujar(app.pantalla)
    # Cada valor (a la derecha, hasta x 700) no se pisa con el nombre de su fila (desde x 120)
    for fila, tipos in ELEGIBLES.items():
        for tipo in tipos:
            ancho_valor = recursos.fuente(CHICA).size("< " + nombre_de(fila, tipo) + " >")[0]
            ancho_fila = recursos.fuente(MEDIA).size(fila)[0]
            assert 120 + ancho_fila + 24 < 700 - ancho_valor, (fila, tipo)


def test_gasolinera_da_creditos_y_abre_la_tienda(app, partida):
    panel = abrir_panel(app, partida)
    panel.hacer("GASOLINERA")
    assert partida.creditos == desarrollador.CREDITOS_DE_PRUEBA
    assert partida.director.gasolinera
    assert partida.modo_desarrollador


def test_anomalia_la_trae_ahora_pero_no_con_un_jefe(app, partida, monkeypatch):
    elegir(monkeypatch, "ANOMALIA", "oro")
    panel = abrir_panel(app, partida)
    panel.hacer("ANOMALIA")
    assert partida.director.anomalia.tipo == "oro"
    partida.iniciar_jefe("ojo")
    panel.hacer("ANOMALIA")
    assert partida.director.anomalia is None


# ---------- AVANZAR: saltar tramos, vencer al jefe y dar secretos ----------

def test_las_pestanas_cambian_con_q_y_e_y_se_recuerdan(app, partida, monkeypatch):
    monkeypatch.setattr(Desarrollador, "recuerdo", {"pestana": 0, "fila": 0, "secreto": 0})
    panel = abrir_panel(app, partida)
    tecla(pygame.K_e)
    avanzar(app)
    assert panel.pestanas()[panel.pestana][0] == "AVANZAR"
    assert panel.filas()[panel.fila] == "SALTAR TRAMO"
    otro = Desarrollador(app, Juego(app, partida), app.pantalla.copy())
    assert otro.filas()[otro.fila] == "SALTAR TRAMO"       # (F1 + ENTER repite lo mismo)


def test_saltar_tramo_pasa_al_siguiente(app, partida):
    panel = abrir_panel(app, partida)
    partida.director.con_escuadrones = True
    jugar(partida, 400)                  # (ya llego algun escuadron)
    assert partida.director.numero_tramo == 1
    panel.hacer("SALTAR TRAMO")
    assert partida.enemigos == []
    jugar(partida, 2)
    assert partida.director.numero_tramo == 2
    assert partida.modo_desarrollador


def test_saltar_el_asedio_trae_al_jefe(app, partida):
    panel = abrir_panel(app, partida)
    while partida.director.numero_tramo < 4:
        partida.subir_nivel()
    partida.director.empezar_asedio()
    panel.hacer("SALTAR TRAMO")
    jugar(partida, 2)
    assert partida.jefe is not None
    assert not partida.director.en_asedio


def test_con_el_jefe_no_hay_tramo_que_saltar(app, partida):
    panel = abrir_panel(app, partida)
    partida.iniciar_jefe("ojo")
    assert not partida.director.saltar_tramo()


@pytest.mark.parametrize("tipo", list(TIPOS_JEFE))
@pytest.mark.parametrize("espera", [1, 400])          # recien llegado (entrando) o peleando
def test_vencer_jefe_lo_mata_con_el_golpe_final(app, partida, tipo, espera):
    panel = abrir_panel(app, partida)
    partida.nave.invulnerable_hasta = math.inf
    partida.iniciar_jefe(tipo)
    jugar(partida, espera)
    panel.hacer("VENCER JEFE")
    assert partida.jefe.muriendo()
    for _ in range(600):
        if partida.congelar_frames > 0:
            partida.congelar_frames -= 1        # (el hit-stop lo descuenta la escena Juego)
        else:
            jugar(partida)
        if partida.jefe is None:
            break
    assert partida.jefes_vencidos == 1


def test_vencer_jefe_sin_jefe_no_hace_nada(app, partida):
    panel = abrir_panel(app, partida)
    panel.hacer("VENCER JEFE")
    assert partida.jefes_vencidos == 0


def test_en_el_arcade_no_hay_secretos(app, partida):
    panel = abrir_panel(app, partida)
    assert panel.secretos() == []
    assert panel.valor("SECRETO") == "NINGUNO"
    panel.hacer("SECRETO")                      # (no se rompe)


def test_en_la_historia_da_los_secretos_de_la_mision(app, monkeypatch):
    monkeypatch.setattr(Desarrollador, "recuerdo", {"pestana": 1, "fila": 2, "secreto": 0})
    app.nueva_partida(modo=ModoHistoria(1))
    partida = app.escena.partida
    panel = abrir_panel(app, partida)
    assert [id_ for id_, _, _ in panel.secretos()] == [f.id for f in partida.modo.mision.fragmentos]
    panel.hacer("SECRETO")
    assert "F01" in app.progreso.fragmentos
    assert partida.radio.actual or partida.radio.esperando          # (la radio cuenta la reaccion)
    assert panel.secretos()[0][2]                                   # ahora sale como encontrado


def test_saltando_todo_se_llega_al_dialogo_de_despues(app):
    # Lo que se usa para leer la historia: F1 -> SALTAR TRAMO (4 veces) y VENCER JEFE
    app.nueva_partida(modo=ModoHistoria(1))
    avanzar(app, 101)
    juego = app.escena
    partida = juego.partida
    partida.nave.invulnerable_hasta = math.inf
    partida.director.con_mejoras = False        # (sin el Taller en el medio)
    panel = Desarrollador(app, juego, app.pantalla.copy())
    for _ in range(4):
        panel.hacer("SALTAR TRAMO")
        avanzar(app, 3)
    assert partida.jefe is not None
    avanzar(app, 30)
    panel.hacer("VENCER JEFE")
    for _ in range(1500):
        avanzar(app)
        if isinstance(app.escena, Dialogo):
            break
    assert isinstance(app.escena, Dialogo)
    assert 1 in app.progreso.misiones
