"""Pantalla de inicio: el menu vertical, las paginas del panel y que todo entre adentro."""
import pygame

from juego import recursos
from juego.config import BOTON_RB
from juego.dibujo import MINI, CHICA
from juego.escenas.inicio import (Inicio, MENU, DESCRIPCION_MENU, PESTANAS, PAGINA_MS, CONTENIDO, BARRA_PESTANAS,
                                  COLUMNA_DESCRIPCION, ALTO_POWERUP)
from juego.powerups import TIPOS_POWERUP
from tests.ayudas import avanzar, tecla, boton


def test_la_pagina_cambia_sola_y_con_lb_rb_q_e(app):
    inicio = app.escena
    assert isinstance(inicio, Inicio) and inicio.pagina == 0
    inicio.pagina_desde = app.ahora()           # (se creo antes de que el test pusiera su reloj falso)
    avanzar(app, PAGINA_MS // 16 + 2)
    assert inicio.pagina == 1                   # cambio sola
    tecla(pygame.K_e)
    avanzar(app)
    assert inicio.pagina == 2
    boton(BOTON_RB)                             # con el mando: RB (da la vuelta)
    avanzar(app)
    assert inicio.pagina == 0
    tecla(pygame.K_LEFT)                        # IZQ/DER tambien
    avanzar(app)
    assert inicio.pagina == 2
    avanzar(app, PAGINA_MS // 16 - 30)
    assert inicio.pagina == 2                   # tocar una tecla vuelve a contar el tiempo


def test_el_menu_es_vertical_y_da_la_vuelta(app):
    inicio = app.escena
    tecla(pygame.K_DOWN)
    avanzar(app)
    assert MENU[inicio.opcion] == "LOGROS"
    tecla(pygame.K_UP)
    avanzar(app)
    tecla(pygame.K_UP)
    avanzar(app)
    assert MENU[inicio.opcion] == "SALIR"
    assert inicio.cursor.objetivo == inicio.opcion      # el cursor va hacia la elegida...
    avanzar(app, 30)
    assert inicio.cursor.valor == inicio.opcion         # ...y llega


def test_salir_cierra_el_juego(app):
    tecla(pygame.K_UP)                          # SALIR
    avanzar(app)
    tecla(pygame.K_RETURN)
    avanzar(app)
    assert app.ejecutando                       # primero suena el apagado...
    avanzar(app, 30)
    assert not app.ejecutando                   # ...y medio segundo despues se cierra


def test_las_tres_paginas_se_dibujan_con_y_sin_records(app):
    for con_records in (False, True):
        if con_records:
            app.records.agregar("AAA", 1234, app.opciones.dificultad)
        for pagina in range(len(PESTANAS)):
            app.escena.pagina = pagina
            avanzar(app)


def test_los_power_ups_entran_en_el_panel(app):
    # Uno por renglon: el nombre despues de la capsula y la descripcion en su columna
    for powerup in TIPOS_POWERUP.values():
        assert 42 + recursos.fuente(CHICA).size(powerup.nombre)[0] + 8 <= COLUMNA_DESCRIPCION, powerup.tipo
        assert COLUMNA_DESCRIPCION + recursos.fuente(MINI).size(powerup.descripcion)[0] <= CONTENIDO.width, powerup.tipo
    assert 14 + (len(TIPOS_POWERUP) - 1) * ALTO_POWERUP + 15 <= CONTENIDO.height


def test_las_pestanas_y_las_descripciones_entran(app):
    # Las pestañas, entre los dos botones (LB/RB son los mas anchos: 44 px)
    adentro = BARRA_PESTANAS.width - 2 * (44 + 8)
    assert sum(recursos.fuente(CHICA).size(nombre)[0] for nombre in PESTANAS) + 16 * len(PESTANAS) <= adentro
    # La descripcion de cada opcion del menu, en un renglon
    for descripcion in DESCRIPCION_MENU.values():
        assert recursos.fuente(CHICA).size(descripcion)[0] <= 400, descripcion
