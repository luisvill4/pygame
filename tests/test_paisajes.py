"""Los paisajes: la animacion grande del fondo de cada sector (paisajes.py)."""
import numpy
import pygame
import pytest

from juego import paisajes
from juego.config import ANCHO, ALTO, SECTORES, PIXEL_ARTE, BRILLO_FONDO_JUGANDO

AMBIENTES = sorted({sector["ambiente"] for sector in SECTORES})
NEGRO = (0, 0, 0)


def dibujado(ambiente, t, luz=1.0, dx=0, dy=0):
    # El paisaje solo, sobre negro: un arreglo (ancho, alto, 3) con los colores
    pantalla = pygame.Surface((ANCHO, ALTO))
    pantalla.fill(NEGRO)
    paisajes.dibujar_paisaje(ambiente, pantalla, t, luz, dx, dy)
    return pygame.surfarray.array3d(pantalla)


def test_cada_sector_tiene_su_paisaje():
    for sector in SECTORES:
        assert sector["ambiente"] in paisajes.PAISAJES, sector["nombre"]


@pytest.mark.parametrize("ambiente", AMBIENTES)
def test_el_paisaje_calza_en_la_grilla(app, ambiente):
    # En momentos y corrimientos con decimales: todo cambio de color en una x y una y par
    for t, dx, dy in ((0, 0, 0), (37.3, 3.7, -5.1), (433.9, -1.3, 2.9), (1777.5, 0, 0)):
        colores = dibujado(ambiente, t, dx=dx, dy=dy)
        cambia_en_x = (colores[1:, :] != colores[:-1, :]).any(axis=(1, 2))
        cambia_en_y = (colores[:, 1:] != colores[:, :-1]).any(axis=(0, 2))
        columnas = numpy.nonzero(cambia_en_x)[0] + 1
        filas = numpy.nonzero(cambia_en_y)[0] + 1
        assert not [x for x in columnas if x % PIXEL_ARTE], (ambiente, t)
        assert not [y for y in filas if y % PIXEL_ARTE], (ambiente, t)


@pytest.mark.parametrize("ambiente", AMBIENTES)
def test_el_paisaje_es_apagado_y_jugando_mas(app, ambiente):
    # La paleta del fondo: ningun canal por encima de ~110 (asi no se confunde con lo que
    # importa), y mientras se juega todavia mas oscuro
    for t in (60, 250, 900):
        assert dibujado(ambiente, t).max() <= 110, (ambiente, t)
        assert dibujado(ambiente, t, BRILLO_FONDO_JUGANDO).max() <= 110 * BRILLO_FONDO_JUGANDO + 1, (ambiente, t)


@pytest.mark.parametrize("ambiente", AMBIENTES)
def test_dibujar_no_cambia_nada_y_el_paisaje_se_mueve(app, ambiente):
    # El mismo t da siempre el mismo dibujo (dibujar puede correr varias veces por paso)...
    assert (dibujado(ambiente, 500) == dibujado(ambiente, 500)).all()
    # ...y con el tiempo cambia: esta vivo
    assert (dibujado(ambiente, 500) != dibujado(ambiente, 560)).any()


def test_el_fondo_dibuja_el_paisaje_del_sector(app):
    fondo = app.fondo
    for sector in SECTORES:
        fondo.ir_a_sector(sector, instantaneo=True)
        fondo.mover()
        dibujados = []
        original = paisajes.dibujar_paisaje
        paisajes.dibujar_paisaje = lambda ambiente, *datos: dibujados.append(ambiente)
        try:
            fondo.dibujar(app.pantalla)
        finally:
            paisajes.dibujar_paisaje = original
        assert dibujados == [sector["ambiente"]]
