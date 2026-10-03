"""Choques: el daño usa circulos (justos aunque la nave este girada); recoger usa la caja grande."""
import math

import pygame

from juego.config import RADIO_BALA, RADIO_ENEMIGO
from juego.enemigos import crear_enemigo
from tests.ayudas import jugar


def poner_enemigo(partida, distancia, angulo=45):
    # Enemigo activo y quieto, con su centro a 'distancia' del centro de la nave
    enemigo = crear_enemigo("perseguidor", partida)
    enemigo.aparece_en = 0
    nave_x, nave_y = partida.nave.centro()
    enemigo.x = nave_x + math.cos(math.radians(angulo)) * distancia - 20
    enemigo.y = nave_y + math.sin(math.radians(angulo)) * distancia - 20
    enemigo.mover = lambda partida: None
    enemigo.vx = enemigo.vy = 0
    partida.enemigos.append(enemigo)
    return enemigo


def test_circulo_de_la_nave(partida):
    nave = partida.nave
    nave_x, nave_y = nave.centro()
    assert not nave.toca_circulo(nave_x + 16, nave_y, RADIO_BALA)
    assert nave.toca_circulo(nave_x + 12, nave_y, RADIO_BALA)
    # En diagonal a 30 px el cuadrado viejo de 30x30 pegaba; el circulo no
    assert not nave.toca_circulo(nave_x + 21.2, nave_y + 21.2, RADIO_ENEMIGO)


def test_circulo_contra_rectangulo(partida):
    nave = partida.nave
    nave_x, nave_y = nave.centro()
    assert nave.toca_rect(pygame.Rect(nave_x + 5, nave_y - 50, 100, 100))
    assert not nave.toca_rect(pygame.Rect(nave_x + 12, nave_y - 50, 100, 100))


def test_enemigo_en_diagonal_lejos_no_pega(partida):
    poner_enemigo(partida, 30)
    jugar(partida)
    assert partida.vidas == 3


def test_enemigo_cerca_pega_y_reaparece(partida):
    enemigo = poner_enemigo(partida, 20)
    jugar(partida)
    assert partida.vidas == 2
    assert not enemigo.activo(partida.tiempo)       # volvio a su "X" de aviso


def test_el_dash_atraviesa_enemigos(partida):
    poner_enemigo(partida, 10)
    partida.nave.dash_hasta = partida.tiempo + 500
    jugar(partida)
    assert partida.vidas == 3


def test_enemigo_con_aviso_no_pega(partida):
    enemigo = poner_enemigo(partida, 5)
    enemigo.aparece_en = partida.tiempo + 1000
    jugar(partida)
    assert partida.vidas == 3


def test_enemigo_congelado_se_recoge_con_la_caja_grande(partida):
    poner_enemigo(partida, 35)
    partida.activar("hielo", 5000)
    jugar(partida)
    assert partida.vidas == 3
    assert partida.puntaje == 5
