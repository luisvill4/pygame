"""Formato 4:3 / 16:9: se cambia desde Opciones y en 16:9 se juega en todo el ancho."""
import json
import math

import pygame

from juego import lienzo
from juego.app import App
from juego.enemigos import crear_enemigo
from juego.escenas.opciones import Opciones
from juego.escenas.pausa import Pausa
from juego.hud import zonas_hud
from juego.moneda import lugar_para_moneda
from tests.ayudas import avanzar, tecla, jugar


def cambiar_formato_en_opciones(app, tecla_direccion):
    tecla(pygame.K_DOWN)                # fila FORMATO
    tecla(tecla_direccion)
    avanzar(app)


def pasar_a_16_9(app):
    app.opciones.formato = "16:9"
    app.aplicar_formato()


def test_cambiar_el_formato_desde_el_menu(app, tmp_path):
    app.cambiar_escena(Opciones(app, volver_a=app.escena))
    cambiar_formato_en_opciones(app, pygame.K_RIGHT)
    assert app.opciones.formato == "16:9"
    assert lienzo.ancho == 1066
    assert app.pantalla.get_size() == (1066, 600)
    assert app.opciones.resolucion == "1066x600"
    assert app.ventana.superficie.get_size() == (1066, 600)
    assert json.loads((tmp_path / "config.json").read_text())["formato"] == "16:9"

    tecla(pygame.K_LEFT)                # sigue en la fila FORMATO
    avanzar(app)
    assert app.opciones.formato == "4:3"
    assert app.pantalla.get_size() == (800, 600)
    assert app.opciones.resolucion == "800x600"


def test_desde_la_pausa_no_se_puede_cambiar(app):
    tecla(pygame.K_RETURN)
    avanzar(app, 101)                   # Inicio -> Listo -> Juego
    tecla(pygame.K_p)
    avanzar(app)
    assert isinstance(app.escena, Pausa)
    tecla(pygame.K_o)
    avanzar(app)
    cambiar_formato_en_opciones(app, pygame.K_RIGHT)
    assert app.opciones.formato == "4:3"
    assert lienzo.ancho == 800


def test_config_viejo_con_resolucion_de_otro_formato(tmp_path):
    (tmp_path / "config.json").write_text(json.dumps({"formato": "16:9", "resolucion": "800x600"}))
    aplicacion = App(carpeta_datos=str(tmp_path), usar_mandos=False)
    assert aplicacion.opciones.resolucion == "1066x600"
    assert aplicacion.pantalla.get_size() == (1066, 600)


def test_en_16_9_todo_usa_el_ancho_completo(app):
    pasar_a_16_9(app)
    app.nueva_partida()
    partida = app.escena.partida
    partida.enemigos.clear()
    partida.proximo_powerup = math.inf

    # Las zonas del HUD ocupan todo el ancho
    assert zonas_hud()[0].width == 1066

    # Los enemigos aparecen en todo el ancho, sin salirse
    xs = [crear_enemigo("perseguidor", partida).x for _ in range(300)]
    assert max(xs) > 800 and max(xs) <= 1066 - 40

    # La moneda aparece dentro de la pantalla
    for _ in range(300):
        partida.nave.x = 900
        x, y = lugar_para_moneda(partida)
        assert 0 <= x <= 1066 - 20

    # La nave llega hasta el borde derecho
    partida.nave.invulnerable_hasta = math.inf
    jugar(partida, 300, dx=1)
    assert partida.nave.x == 1066 - 50

    # El jefe aparece centrado y recorre todo el ancho
    partida.iniciar_jefe()
    assert partida.jefe.x == (1066 - 120) // 2
    partida.jefe.y = 70
    partida.jefe.cambiar_fase("flotar", 10 ** 9, partida.tiempo)
    xs_jefe = []
    for _ in range(400):
        jugar(partida)
        xs_jefe.append(partida.jefe.x)
    assert max(xs_jefe) + 120 > 900 and min(xs_jefe) < 150


def test_en_16_9_se_dibujan_todas_las_pantallas(app):
    pasar_a_16_9(app)
    tecla(pygame.K_RETURN)
    avanzar(app, 105)                   # Inicio, Listo y Juego
    tecla(pygame.K_p)
    avanzar(app, 3)                     # Pausa
    assert app.pantalla.get_size() == (1066, 600)
