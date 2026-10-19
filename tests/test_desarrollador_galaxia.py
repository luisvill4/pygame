"""El panel del desarrollador en la galaxia: ir a cualquier mision, secretos, el reloj, modulos y piezas."""
import pygame
import pytest

from juego import recursos
from juego.config import MAREA_ANIOS
from juego.dibujo import CHICA, MEDIA
from juego.escenas.historia import desarrollador
from juego.escenas.historia.desarrollador import DesarrolladorGalaxia, FILAS, PIEZAS_DE_PRUEBA
from juego.escenas.historia.dialogo import Dialogo
from juego.escenas.historia.galaxia import Galaxia
from juego.historia import modulos
from juego.historia.mision import misiones_en_orden, todos_los_fragmentos
from tests.ayudas import avanzar, tecla


@pytest.fixture
def panel(app, monkeypatch):
    monkeypatch.setattr(DesarrolladorGalaxia, "recuerdo", {"pestana": 0, "fila": 0, "mision": 0, "secreto": 0})
    galaxia = Galaxia(app)
    nuevo = DesarrolladorGalaxia(app, galaxia, app.pantalla.copy())
    app.cambiar_escena(nuevo)
    return nuevo


def test_f1_lo_abre_desde_la_galaxia_y_vuelve(app):
    galaxia = Galaxia(app)
    app.cambiar_escena(galaxia)
    tecla(pygame.K_F1)
    avanzar(app)
    assert isinstance(app.escena, DesarrolladorGalaxia)
    tecla(pygame.K_F1)
    avanzar(app)
    assert app.escena is galaxia


def test_va_a_cualquier_mision_sin_viajar_ni_bloqueos(app, panel):
    oculta = next(clase for clase in misiones_en_orden() if clase.oculta)
    panel.recuerdo["mision"] = misiones_en_orden().index(oculta)
    assert not oculta.disponible(app.progreso)
    panel.hacer("MISION")
    assert isinstance(app.escena, Dialogo)
    assert app.progreso.anios == 0                  # sin viajar: no pasa el tiempo
    assert app.progreso.ubicacion == "M%d" % oculta.numero


def test_el_secreto_se_encuentra_y_se_olvida(app, panel):
    panel.hacer("SECRETO")
    assert "F01" in app.progreso.fragmentos
    panel.hacer("SECRETO")
    assert "F01" not in app.progreso.fragmentos


def test_olvidar_un_requisito_esconde_la_mision_oculta_sin_romper_el_mapa(app, panel):
    oculta = next(clase for clase in misiones_en_orden() if clase.oculta)
    app.progreso.fragmentos.update(oculta.requisitos)
    galaxia = panel.galaxia
    galaxia.elegida = "M%d" % oculta.numero
    panel.recuerdo["secreto"] = [f.id for f, _ in todos_los_fragmentos()].index(oculta.requisitos[0])
    panel.hacer("SECRETO")
    assert galaxia.elegida != "M%d" % oculta.numero
    app.cambiar_escena(galaxia)
    avanzar(app, 2)                                 # (se dibuja sin la oculta)


def test_el_reloj_se_mueve_y_los_mensajes_vuelven(app, panel):
    panel.cambiar("AÑO", 1)
    assert app.progreso.anios == desarrollador.PASO_ANIOS
    app.progreso.anios = 2.0
    app.progreso.mensajes = {1, 2}
    panel.cambiar("AÑO", -1)
    assert app.progreso.anios == 1.5
    assert app.progreso.mensajes == {1}             # el del año 2 se puede ver otra vez
    for _ in range(40):
        panel.cambiar("AÑO", 1)
    assert app.progreso.anios == MAREA_ANIOS
    for _ in range(40):
        panel.cambiar("AÑO", -1)
    assert app.progreso.anios == 0


def test_modulos_al_maximo_y_piezas(app, panel):
    panel.hacer("MODULOS")
    for modulo in modulos.MODULOS:
        assert modulos.tiene_plano(app.progreso, modulo.id)
        assert modulos.nivel(app.progreso, modulo.id) == modulo.maximo
    panel.hacer("PIEZAS")
    assert app.progreso.piezas == PIEZAS_DE_PRUEBA


def test_se_dibuja_y_los_valores_entran(app, panel):
    for i in range(len(FILAS)):
        panel.fila = i
        panel.dibujar(app.pantalla)
    # Cada valor (a la derecha, hasta x 700) no se pisa con el nombre de su fila (desde x 120)
    for numero in range(len(misiones_en_orden())):
        panel.recuerdo["mision"] = numero
        ancho_valor = recursos.fuente(CHICA).size(panel.valor("MISION"))[0]
        assert 120 + recursos.fuente(MEDIA).size("MISION")[0] + 24 < 700 - ancho_valor
    for numero in range(len(todos_los_fragmentos())):
        panel.recuerdo["secreto"] = numero
        assert recursos.fuente(CHICA).size(panel.ayuda("SECRETO"))[0] <= 760
