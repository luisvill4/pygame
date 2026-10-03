"""
Preparacion comun de los tests.

- Sin ventana ni sonido reales (drivers "dummy" de SDL).
- records.json y config.json van a una carpeta temporal (no tocan los tuyos).
- Los mandos reales se ignoran (para que no vibren).
- El reloj real es falso: avanzar() suma 1/60 s por frame, sin esperar.
- Las teclas mantenidas se simulan con el conjunto app.teclas.
"""
import math
import os

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import pygame  # noqa: E402
import pytest  # noqa: E402

from juego.app import App  # noqa: E402
from tests.ayudas import TeclasFalsas  # noqa: E402


@pytest.fixture
def app(tmp_path):
    aplicacion = App(carpeta_datos=str(tmp_path), usar_mandos=False)
    aplicacion.reloj_falso = 0
    aplicacion.ahora = lambda: aplicacion.reloj_falso
    aplicacion.teclas = set()
    aplicacion.entrada.teclas_mantenidas = lambda: TeclasFalsas(aplicacion.teclas)
    pygame.event.clear()
    yield aplicacion
    pygame.event.clear()


@pytest.fixture
def partida(app):
    # Una partida recien empezada y "limpia": sin enemigos, sin power-ups cayendo
    # y con la moneda lejos, para probar una cosa a la vez
    app.nueva_partida()
    nueva = app.escena.partida
    nueva.enemigos.clear()
    nueva.proximo_powerup = math.inf
    nueva.moneda.x, nueva.moneda.y = -500, -500
    return nueva
