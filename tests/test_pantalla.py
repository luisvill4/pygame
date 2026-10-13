"""La pantalla es siempre 16:9 (ANCHO x ALTO): se juega en todo el ancho."""
import json
import math

import pygame

from juego.app import App
from juego.config import ANCHO, ALTO, RESOLUCIONES
from juego.enemigos import crear_enemigo
from juego.escenas.opciones import Opciones, AJUSTES
from juego.escenas.pausa import Pausa
from juego.hud import zonas_hud
from juego.moneda import lugar_para_moneda
from tests.ayudas import avanzar, tecla, jugar, empezar_partida


def test_el_lienzo_es_16_9(app):
    assert app.pantalla.get_size() == (ANCHO, ALTO) == (1066, 600)
    assert app.opciones.resolucion == "1066x600"
    assert app.ventana.superficie.get_size() == (1066, 600)


def test_config_viejo_de_4_3_abre_en_16_9(tmp_path):
    # Un config.json de antes, con el formato 4:3 y una resolucion que ya no existe
    (tmp_path / "config.json").write_text(json.dumps({"formato": "4:3", "resolucion": "1200x900"}))
    aplicacion = App(carpeta_datos=str(tmp_path), usar_mandos=False)
    assert aplicacion.opciones.resolucion == "1066x600"
    assert aplicacion.pantalla.get_size() == (1066, 600)


def test_solo_hay_resoluciones_16_9():
    for nombre, ancho, alto in RESOLUCIONES:
        if nombre != "COMPLETA":
            assert abs(ancho / alto - 16 / 9) < 0.01


def test_opciones_no_tiene_formato(app):
    assert "FORMATO" not in [ajuste.nombre for ajuste in AJUSTES]
    # Desde la pausa se abren las mismas opciones
    empezar_partida(app)
    tecla(pygame.K_p)
    avanzar(app)
    assert isinstance(app.escena, Pausa)
    tecla(pygame.K_o)
    avanzar(app)
    assert isinstance(app.escena, Opciones)


def test_todo_usa_el_ancho_completo(app):
    app.nueva_partida()
    partida = app.escena.partida
    partida.enemigos.clear()
    partida.proximo_powerup = math.inf

    # Las zonas del HUD ocupan todo el ancho
    assert zonas_hud()[0].width == ANCHO

    # Los enemigos aparecen en todo el ancho, sin salirse
    xs = [crear_enemigo("perseguidor", partida).x for _ in range(300)]
    assert max(xs) > 800 and max(xs) <= ANCHO - 40

    # La moneda aparece dentro de la pantalla
    for _ in range(300):
        partida.nave.x = 900
        x, y = lugar_para_moneda(partida)
        assert 0 <= x <= ANCHO - 20

    # La nave llega hasta el borde derecho
    partida.nave.invulnerable_hasta = math.inf
    jugar(partida, 300, dx=1)
    assert partida.nave.x == ANCHO - 50

    # El jefe aparece centrado y recorre todo el ancho
    partida.iniciar_jefe()
    assert partida.jefe.x == (ANCHO - 120) // 2
    partida.jefe.y = 70
    partida.jefe.cambiar_fase("flotar", 10 ** 9, partida.tiempo)
    xs_jefe = []
    for _ in range(400):
        jugar(partida)
        xs_jefe.append(partida.jefe.x)
    assert max(xs_jefe) + 120 > 900 and min(xs_jefe) < 150
