"""Entrada: teclado y mando se convierten en las mismas acciones."""
import pygame

from juego.config import BOTON_A, BOTON_B, BOTON_X, BOTON_MENU, BOTON_VISTA
from juego.entrada import Entrada, ACEPTAR, VOLVER, PAUSA, OPCIONES, DASH, ARRIBA, IZQUIERDA, DERECHA
from tests.ayudas import TeclasFalsas


def evento(tipo, **datos):
    return pygame.event.Event(tipo, **datos)


def test_teclas():
    entrada = Entrada(usar_mandos=False)
    entrada.procesar([evento(pygame.KEYDOWN, key=pygame.K_RETURN), evento(pygame.KEYDOWN, key=pygame.K_SPACE)])
    assert entrada.acciones == [ACEPTAR, DASH]
    entrada.procesar([evento(pygame.KEYDOWN, key=pygame.K_ESCAPE)])
    assert entrada.pulso(VOLVER) and entrada.pulso(PAUSA)


def test_botones_del_mando():
    entrada = Entrada(usar_mandos=False)
    botones = [BOTON_A, BOTON_X, BOTON_MENU, BOTON_VISTA, BOTON_B]
    entrada.procesar([evento(pygame.JOYBUTTONDOWN, button=b, instance_id=0, joy=0) for b in botones])
    assert entrada.acciones == [ACEPTAR, DASH, PAUSA, OPCIONES, VOLVER]


def test_b_no_pausa():
    entrada = Entrada(usar_mandos=False)
    entrada.procesar([evento(pygame.JOYBUTTONDOWN, button=BOTON_B, instance_id=0, joy=0)])
    assert not entrada.pulso(PAUSA)


def test_el_stick_cuenta_un_toque_por_inclinacion():
    entrada = Entrada(usar_mandos=False)
    entrada.procesar([evento(pygame.JOYAXISMOTION, axis=0, value=-0.9, instance_id=0, joy=0)])
    assert entrada.acciones == [IZQUIERDA]
    entrada.consumir()
    entrada.procesar([evento(pygame.JOYAXISMOTION, axis=0, value=-0.95, instance_id=0, joy=0)])
    assert entrada.acciones == []
    entrada.procesar([evento(pygame.JOYAXISMOTION, axis=0, value=0.0, instance_id=0, joy=0),
                      evento(pygame.JOYAXISMOTION, axis=0, value=0.9, instance_id=0, joy=0)])
    assert entrada.acciones == [DERECHA]


def test_las_acciones_se_juntan_hasta_que_un_paso_las_usa():
    # A mas de 60 FPS hay cuadros sin paso de logica: las teclas no se pueden perder
    entrada = Entrada(usar_mandos=False)
    entrada.procesar([evento(pygame.KEYDOWN, key=pygame.K_SPACE)])
    entrada.procesar([])
    assert entrada.pulso(DASH)
    entrada.consumir()
    assert not entrada.pulso(DASH)


def test_cruceta():
    entrada = Entrada(usar_mandos=False)
    entrada.procesar([evento(pygame.JOYHATMOTION, hat=0, value=(1, 1), instance_id=0, joy=0)])
    assert entrada.acciones == [DERECHA, ARRIBA]


class MandoFalso:
    def __init__(self, cruceta=(0, 0), ejes=(0.0, 0.0)):
        self.cruceta, self.ejes = cruceta, ejes

    def get_numhats(self):
        return 1

    def get_hat(self, i):
        return self.cruceta

    def get_numaxes(self):
        return 2

    def get_axis(self, i):
        return self.ejes[i]


def test_direccion_teclado_tiene_prioridad_sobre_el_mando():
    entrada = Entrada(usar_mandos=False)
    entrada.mandos[7] = MandoFalso(ejes=(0.5, -0.3))
    entrada.teclas_mantenidas = lambda: TeclasFalsas({pygame.K_LEFT})
    assert entrada.direccion() == (-1, 0)
    entrada.teclas_mantenidas = lambda: TeclasFalsas(set())
    assert entrada.direccion() == (0.5, -0.3)           # stick: cualquier angulo
    entrada.mandos[7] = MandoFalso(ejes=(0.1, 0.1))
    assert entrada.direccion() == (0, 0)                # zona muerta
    entrada.mandos[7] = MandoFalso(cruceta=(0, 1))
    assert entrada.direccion() == (0, -1)               # cruceta: arriba


def test_desconectar_un_mando_que_se_usaba():
    entrada = Entrada(usar_mandos=False)
    entrada.mandos[7] = MandoFalso()
    entrada.procesar([evento(pygame.JOYDEVICEREMOVED, instance_id=99)])
    assert not entrada.mando_desconectado               # ese no se estaba usando
    entrada.procesar([evento(pygame.JOYDEVICEREMOVED, instance_id=7)])
    assert entrada.mando_desconectado and not entrada.hay_mando()
