"""HUD: los carteles se vuelven transparentes si tapan algo del juego."""
import random

import pygame

from juego import hud, lienzo
from juego.config import ALTO, CARTEL_ALFA_TAPANDO
from juego.enemigos import crear_enemigo


def brillo_del_cartel_de_nivel(partida):
    pantalla = pygame.Surface((lienzo.ancho, ALTO))
    hud.dibujar(pantalla, partida)
    zona = pygame.Rect(lienzo.centro_x() - 150, 225, 300, 50)        # donde sale "NIVEL X"
    return sum(pygame.transform.average_color(pantalla, zona)[:3])


def test_el_cartel_se_vuelve_transparente_si_tapa_un_enemigo(partida):
    hud._tapando_hasta.clear()
    partida.nave.x, partida.nave.y = 60, 480
    partida.tiempo_cartel_nivel = partida.tiempo
    normal = brillo_del_cartel_de_nivel(partida)
    assert normal > 0

    enemigo = crear_enemigo("perseguidor", partida)
    enemigo.x, enemigo.y = lienzo.centro_x(), 240
    partida.enemigos.append(enemigo)
    tapando = brillo_del_cartel_de_nivel(partida)
    assert tapando < normal * (CARTEL_ALFA_TAPANDO + 30) / 255


def test_la_zona_del_cartel_tiene_todo_lo_dibujado():
    # La busqueda rapida (capa achicada) nunca deja afuera un pixel: si no, se cortaria el cartel
    random.seed(1)
    capa = pygame.Surface((lienzo.ancho, ALTO), pygame.SRCALPHA)
    for _ in range(200):
        capa.fill((0, 0, 0, 0))
        for _ in range(random.randint(1, 3)):
            capa.fill((255, 255, 255, 255), (random.randrange(lienzo.ancho), random.randrange(ALTO), 1, 1))
        assert hud._zona_dibujada(capa).contains(capa.get_bounding_rect())
    capa.fill((0, 0, 0, 0))
    assert hud._zona_dibujada(capa).width == 0
