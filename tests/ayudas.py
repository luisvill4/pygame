"""Funciones de ayuda para los tests (simular frames, teclas y botones)."""
import pygame

from juego.config import MS_POR_FRAME


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


def jugar(partida, frames=1, dx=0, dy=0, dash=False):
    # Avanza la partida sola (sin escenas), como si se jugara
    for _ in range(frames):
        partida.actualizar(dx, dy, dash)
        dash = False
