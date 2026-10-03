"""Escenas: el recorrido completo por las pantallas, como lo haria un jugador."""
import pygame

from juego.config import BOTON_B
from juego.escenas.inicio import Inicio
from juego.escenas.opciones import Opciones
from juego.escenas.listo import Listo
from juego.escenas.juego import Juego
from juego.escenas.pausa import Pausa
from juego.escenas.explosion import Explosion
from juego.escenas.iniciales import Iniciales
from juego.escenas.fin import Fin
from tests.ayudas import avanzar, tecla, boton


def empezar(app):
    tecla(pygame.K_RETURN)
    avanzar(app)
    assert isinstance(app.escena, Listo)
    avanzar(app, 100)
    assert isinstance(app.escena, Juego)
    return app.escena.partida


def test_inicio_opciones_y_volver(app):
    avanzar(app, 3)
    assert isinstance(app.escena, Inicio)
    tecla(pygame.K_RIGHT)
    tecla(pygame.K_RETURN)
    avanzar(app)
    assert isinstance(app.escena, Opciones)
    tecla(pygame.K_ESCAPE)
    avanzar(app)
    assert isinstance(app.escena, Inicio)


def test_opcion_aviso_jefe_se_cambia_y_se_guarda(app):
    app.cambiar_escena(Opciones(app, volver_a=app.escena))
    for _ in range(5):              # hasta la fila AVISO JEFE
        tecla(pygame.K_DOWN)
    tecla(pygame.K_RETURN)
    avanzar(app)
    assert app.opciones.aviso_jefe is False
    tecla(pygame.K_LEFT)
    avanzar(app)
    assert app.opciones.aviso_jefe is True


def test_pausa_y_opciones_desde_la_pausa(app):
    empezar(app)
    tecla(pygame.K_p)
    avanzar(app)
    assert isinstance(app.escena, Pausa)
    tecla(pygame.K_o)
    avanzar(app)
    assert isinstance(app.escena, Opciones)
    boton(BOTON_B)
    avanzar(app)
    assert isinstance(app.escena, Pausa)
    tecla(pygame.K_p)
    avanzar(app)
    assert isinstance(app.escena, Juego)


def test_b_del_mando_no_pausa_el_juego(app):
    empezar(app)
    boton(BOTON_B)
    avanzar(app)
    assert isinstance(app.escena, Juego)


def test_pausa_automatica_al_perder_el_foco(app):
    empezar(app)
    pygame.event.post(pygame.event.Event(pygame.WINDOWFOCUSLOST))
    avanzar(app)
    assert isinstance(app.escena, Pausa)


def test_foco_perdido_durante_ready_pausa_al_empezar(app):
    tecla(pygame.K_RETURN)
    avanzar(app)
    pygame.event.post(pygame.event.Event(pygame.WINDOWFOCUSLOST))
    avanzar(app, 101)
    assert isinstance(app.escena, Pausa)


def test_el_tiempo_del_juego_no_corre_en_pausa(app):
    partida = empezar(app)
    tecla(pygame.K_p)
    avanzar(app)
    tiempo = partida.tiempo
    avanzar(app, 120)
    assert partida.tiempo == tiempo


def perder(app, partida, puntaje):
    partida.puntaje = puntaje
    partida.vidas = 1
    partida.nave.invulnerable_hasta = 0
    partida.danar_jugador(*partida.nave.centro())
    avanzar(app)
    assert isinstance(app.escena, Explosion)
    avanzar(app, 110)


def test_game_over_con_record_iniciales_y_otra_partida(app):
    partida = empezar(app)
    perder(app, partida, 25)
    assert isinstance(app.escena, Iniciales)
    tecla(pygame.K_UP)              # A -> B
    for _ in range(3):
        tecla(pygame.K_RETURN)
    avanzar(app)
    assert isinstance(app.escena, Fin)
    assert app.records.filas[0] == {"nombre": "BAA", "puntos": 25}
    tecla(pygame.K_RETURN)          # muy pronto: se ignora
    avanzar(app)
    assert isinstance(app.escena, Fin)
    avanzar(app, 50)
    tecla(pygame.K_RETURN)
    avanzar(app)
    assert isinstance(app.escena, Listo)


def test_game_over_sin_puntos_va_directo_al_fin(app):
    partida = empezar(app)
    perder(app, partida, 0)
    assert isinstance(app.escena, Fin)


def test_cerrar_en_las_iniciales_guarda_el_record(app):
    partida = empezar(app)
    perder(app, partida, 40)
    pygame.event.post(pygame.event.Event(pygame.QUIT))
    avanzar(app)
    assert not app.ejecutando
    assert app.records.filas[0]["puntos"] == 40
