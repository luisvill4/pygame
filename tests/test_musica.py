"""Musica: cada escena pide su tema y la App lo cambia con un fundido."""
import pygame

from juego.sonido import MUSICAS
from juego.config import ruta
from tests.ayudas import avanzar, empezar_partida, tecla


def test_los_temas_existen():
    for archivo in MUSICAS.values():
        with open(ruta("efectos/" + archivo), "rb"):
            pass


def test_el_menu_tiene_su_musica(app):
    avanzar(app)
    assert app.sonidos.actual == "menu"
    tecla(pygame.K_RETURN)          # JUGAR -> elegir dificultad: sigue la misma
    avanzar(app)
    assert app.sonidos.actual == "menu"


def test_al_jugar_suena_la_del_juego_y_con_el_jefe_la_suya(app):
    partida = empezar_partida(app)
    assert app.sonidos.actual == "juego"
    partida.iniciar_jefe()
    avanzar(app)
    assert app.sonidos.actual == "jefe"
    partida.jefe = None             # (como al terminar de morir)
    avanzar(app)
    assert app.sonidos.actual == "juego"


def test_la_pausa_no_cambia_la_musica_y_volver_al_menu_si(app):
    partida = empezar_partida(app)
    partida.pausa_pendiente = True
    avanzar(app, 2)
    assert app.sonidos.actual == "juego"
    app.escena._volver_al_menu()
    assert app.sonidos.actual is None
    avanzar(app)
    assert app.sonidos.actual == "menu"


def test_al_morir_la_musica_se_corta_y_no_vuelve(app):
    partida = empezar_partida(app)
    partida.vidas = 1
    partida.danar_jugador(partida.nave.x, partida.nave.y)
    assert app.sonidos.actual is None
    avanzar(app, 30)                # hit-stop y explosion
    assert app.sonidos.actual is None


def test_la_gasolinera_tiene_su_musica_y_al_salir_vuelve_la_del_juego(app):
    partida = empezar_partida(app)
    juego = app.escena
    partida.director.gasolinera = True
    avanzar(app, 2)                 # Juego la abre y en el paso siguiente pide su musica
    assert app.sonidos.actual == "gasolinera"
    partida.director.gasolinera = False
    app.cambiar_escena(juego)
    avanzar(app)
    assert app.sonidos.actual == "juego"
