"""Modo desarrollador: el panel de F1 trae jefes, enemigos y power-ups, y la partida no cuenta."""
import pygame
import pytest

from juego import recursos
from juego.dibujo import CHICA, MEDIA
from juego.escenas import desarrollador, juego as escena_juego
from juego.escenas.desarrollador import Desarrollador, ELEGIBLES, FILAS, nombre_de
from juego.escenas.explosion import Explosion
from juego.escenas.arcade.fin import Fin
from juego.escenas.arcade.iniciales import Iniciales
from juego.escenas.juego import Juego
from tests.ayudas import avanzar, tecla, empezar_partida


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
    for i in range(len(FILAS)):
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
