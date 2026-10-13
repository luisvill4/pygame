"""HUD: los carteles se vuelven transparentes si tapan algo del juego, el marcador
cuenta de a poco y la barra del jefe destella al pegarle."""
import random

import pygame

from juego import hud
from juego.avisos import Aviso
from juego.config import ANCHO, CENTRO_X, ALTO, CARTEL_ALFA_TAPANDO, AMARILLO
from juego.enemigos import crear_enemigo
from juego.hud import BARRA_CENTRAL
from juego.jefes import crear_jefe
from tests.ayudas import jugar


def brillo_del_cartel_de_nivel(partida):
    pantalla = pygame.Surface((ANCHO, ALTO))
    hud.dibujar(pantalla, partida)
    zona = pygame.Rect(CENTRO_X - 150, 130, 300, 60)        # donde sale el aviso "NIVEL X"
    return sum(pygame.transform.average_color(pantalla, zona)[:3])


def test_el_cartel_se_vuelve_transparente_si_tapa_un_enemigo(partida):
    hud._tapando_hasta.clear()
    partida.nave.x, partida.nave.y = 60, 480
    partida.avisar(Aviso("¡SUBISTE!", "NIVEL 2", "JEFE EN 3 NIVELES", AMARILLO, 5000))
    partida.tiempo += 1000                                  # ya termino de abrirse
    normal = brillo_del_cartel_de_nivel(partida)
    assert normal > 0

    enemigo = crear_enemigo("perseguidor", partida)
    enemigo.x, enemigo.y = CENTRO_X, 150
    partida.enemigos.append(enemigo)
    tapando = brillo_del_cartel_de_nivel(partida)
    assert tapando < normal * (CARTEL_ALFA_TAPANDO + 30) / 255


def test_la_zona_del_cartel_tiene_todo_lo_dibujado():
    # La busqueda rapida (capa achicada) nunca deja afuera un pixel: si no, se cortaria el cartel
    random.seed(1)
    capa = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
    for _ in range(200):
        capa.fill((0, 0, 0, 0))
        for _ in range(random.randint(1, 3)):
            capa.fill((255, 255, 255, 255), (random.randrange(ANCHO), random.randrange(ALTO), 1, 1))
        assert hud._zona_dibujada(capa).contains(capa.get_bounding_rect())
    capa.fill((0, 0, 0, 0))
    assert hud._zona_dibujada(capa).width == 0


def test_el_marcador_cuenta_de_a_poco(partida):
    partida.sumar_puntos(600)
    jugar(partida)
    assert 0 < partida.puntaje_visible < partida.puntaje       # todavia contando
    jugar(partida, 60)
    assert partida.puntaje_visible == partida.puntaje          # y llega justo


def test_la_barra_del_jefe_destella_al_pegarle(partida):
    jefe = crear_jefe("fortaleza", partida)
    partida.jefe = jefe
    jefe.y = jefe.y_final
    jefe.al_terminar_de_entrar(partida)
    jefe.fin_entrada -= 5000                # (ya termino la presentacion y la barra se lleno)
    vida, total = jefe.vida_barra()
    # El segmento que se pierde es el ultimo lleno: queda blanco un instante
    ancho = (BARRA_CENTRAL.width + 4) / total
    centro_segmento = (round(BARRA_CENTRAL.left + (vida - 1) * ancho) + 4, BARRA_CENTRAL.centery)
    pantalla = pygame.Surface((ANCHO, ALTO))
    jefe.golpear_parte(partida, jefe.partes[0])
    hud.dibujar(pantalla, partida)
    assert pantalla.get_at(centro_segmento)[:3] == (255, 255, 255)
    partida.tiempo += 500
    pantalla.fill((0, 0, 0))
    hud.dibujar(pantalla, partida)
    assert pantalla.get_at(centro_segmento)[:3] != (255, 255, 255)


def test_la_barra_del_jefe_aparece_al_terminar_de_entrar_y_se_llena(partida):
    jefe = crear_jefe("ojo", partida)
    partida.jefe = jefe
    pantalla = pygame.Surface((ANCHO, ALTO))
    hud.dibujar(pantalla, partida)
    assert jefe.fin_entrada is None                         # entrando: la cinematica tapa todo
    jefe.y = jefe.y_final
    jefe.al_terminar_de_entrar(partida)
    assert jefe.fin_entrada == partida.tiempo
    partida.tiempo += hud.MS_FRANJAS + 2 * hud.MS_POR_SEGMENTO + 1
    pantalla.fill((0, 0, 0))
    hud.dibujar(pantalla, partida)
    vida, total = jefe.vida_barra()
    ancho = (BARRA_CENTRAL.width + 4) / total
    llenos = [pantalla.get_at((round(BARRA_CENTRAL.left + i * ancho) + 4, BARRA_CENTRAL.centery))[:3] == jefe.color
              for i in range(total)]
    assert llenos[:2] == [True, True] and not any(llenos[3:])       # de a uno
