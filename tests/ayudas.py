"""Funciones de ayuda para los tests (simular frames, teclas y botones)."""
import pygame

from juego.config import MS_POR_FRAME
from juego.escenas.opciones import AJUSTES, PESTANAS, ajustes_de


class TeclasFalsas:
    # Reemplaza a pygame.key.get_pressed(): solo estan "mantenidas" las del conjunto
    def __init__(self, mantenidas):
        self.mantenidas = mantenidas

    def __getitem__(self, tecla):
        return tecla in self.mantenidas


def avanzar(app, frames=1):
    # Corre frames completos de la App (eventos, escena, dibujo)
    for _ in range(frames):
        app.paso()
        app.reloj_falso += MS_POR_FRAME


def tecla(codigo):
    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=codigo))


def boton(numero):
    pygame.event.post(pygame.event.Event(pygame.JOYBUTTONDOWN, button=numero, instance_id=0, joy=0))


def ir_al_ajuste(app, nombre):
    # En Opciones recien abierto: pasa a la seccion del ajuste (con E) y baja hasta el.
    # Solo aprieta las teclas (despues hay que avanzar la App)
    ajuste = next(a for a in AJUSTES if a.nombre == nombre)
    for _ in range(PESTANAS.index(ajuste.pestana)):
        tecla(pygame.K_e)
    for _ in range(ajustes_de(ajuste.pestana).index(ajuste)):
        tecla(pygame.K_DOWN)


def empezar_partida(app):
    # Desde el inicio: JUGAR -> ELIGE DIFICULTAD (la ultima elegida) -> READY -> juego.
    # Devuelve la partida
    tecla(pygame.K_RETURN)
    avanzar(app)
    tecla(pygame.K_RETURN)
    avanzar(app, 101)
    return app.escena.partida


def entrar_a_la_historia(app):
    # Desde el Inicio: HISTORIA y, si sale el prologo (la primera vez), saltearlo. Devuelve la galaxia
    from juego.escenas.historia.prologo import Prologo
    tecla(pygame.K_DOWN)                # HISTORIA
    avanzar(app)
    tecla(pygame.K_RETURN)
    avanzar(app)
    if isinstance(app.escena, Prologo):
        tecla(pygame.K_ESCAPE)
        avanzar(app)
    return app.escena


def jugar(partida, frames=1, dx=0, dy=0, dash=False):
    # Avanza la partida sola (sin escenas), como si se jugara
    for _ in range(frames):
        partida.actualizar(dx, dy, dash)
        dash = False
