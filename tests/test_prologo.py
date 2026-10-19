"""El prologo del modo historia: la cinematica que cuenta que es la Marea antes de empezar."""
import pygame
import pytest

from juego import dibujo
from juego.config import PIXEL_ARTE
from juego.escenas.historia.galaxia import Galaxia
from juego.escenas.historia import cuadros
from juego.escenas.historia.prologo import Prologo, CUADROS, ESCENARIO, ANCHO_TEXTO, RENGLONES
from juego.sonido import SILENCIO
from tests.ayudas import avanzar, tecla, saltear


def elegir_historia(app):
    tecla(pygame.K_DOWN)                # HISTORIA
    avanzar(app)
    tecla(pygame.K_RETURN)
    avanzar(app)


def test_la_primera_vez_sale_el_prologo_y_despues_no(app):
    elegir_historia(app)
    assert isinstance(app.escena, Prologo)
    assert app.escena.musica == SILENCIO
    saltear(app)
    assert isinstance(app.escena, Galaxia)
    assert app.progreso.prologo                         # (queda guardado)
    from juego.escenas.inicio import Inicio
    assert isinstance(Inicio(app)._historia(), Galaxia)  # la segunda vez, directo a la galaxia


def test_con_aceptar_se_lee_entero_y_termina_en_la_galaxia(app):
    elegir_historia(app)
    prologo = app.escena
    vistos = set()
    for _ in range(80):                 # (de sobra: cada ACEPTAR completa o pasa de pagina)
        if not isinstance(app.escena, Prologo):
            break
        vistos.add(prologo.nombre_del_cuadro())
        tecla(pygame.K_RETURN)
        avanzar(app, 3)
    assert isinstance(app.escena, Galaxia)
    assert vistos == {nombre for nombre, _ in CUADROS}


def test_cada_pagina_entra_abajo_y_sin_tildes_que_la_fuente_dibuja_mal(app):
    for _, paginas in CUADROS:
        for pagina in paginas:
            assert len(dibujo.partir_lineas(pagina, dibujo.CHICA, ANCHO_TEXTO)) <= RENGLONES, pagina
            assert not set(pagina) & set("ÁÉÍÓÚ"), pagina


def test_la_marea_y_la_relatividad_se_explican(app):
    # Lo que el usuario no entendia: que es la Marea y por que viajar cuesta tiempo
    todo = " ".join(" ".join(paginas) for _, paginas in CUADROS)
    for palabra in ("LA MAREA", "GALAXIA", "GRAVEDAD", "COMPAS", "VELOCIDAD DE LA LUZ", "HORAS", "MESES"):
        assert palabra in todo, palabra


@pytest.mark.parametrize("nombre", [nombre for nombre, _ in CUADROS if nombre != "titulo"])
def test_cada_dibujo_calza_en_la_grilla_de_pixeles_de_arte(app, nombre):
    app.opciones.neon = "NORMAL"
    paginas = [paginas for n, paginas in CUADROS if n == nombre][0]
    pantalla = pygame.Surface(app.pantalla.get_size())
    for t in (1, 137, 501):             # en distintos momentos de la animacion
        cuadros.dibujar(pantalla, nombre, ESCENARIO, t, len(paginas) - 1)     # (la ultima pagina: con sus rotulos)
        for y in range(ESCENARIO.top, ESCENARIO.bottom, 3):
            for x in range(ESCENARIO.left + 1, ESCENARIO.right):
                if pantalla.get_at((x, y)) != pantalla.get_at((x - 1, y)):
                    assert x % PIXEL_ARTE == 0, (nombre, t, x, y)


def test_todos_los_cuadros_se_dibujan(app):
    prologo = Prologo(app, al_terminar=lambda: None)
    for i in range(len(prologo.paginas)):
        prologo.indice, prologo.letras = i, 999
        for t in (1, 300):
            prologo.pasos_en_cuadro = t
            prologo.dibujar(app.pantalla)
