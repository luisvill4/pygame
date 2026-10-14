"""La presentacion: advertencia, "HECHO CON PYGAME" y el titulo (antes del menu)."""
import pygame

from juego.app import App
from juego.escenas.presentacion import Presentacion, MS_ADVERTENCIA, MS_PYGAME, LOGO_CAE, MS_SIN_SALTEAR
from juego.escenas.inicio import Inicio
from juego.config import MS_POR_FRAME
from juego.sonido import SILENCIO
from tests.ayudas import avanzar, tecla


def presentacion(app):
    app.cambiar_escena(Presentacion(app), transicion=False)
    return app.escena


def frames(ms):
    return int(ms / MS_POR_FRAME) + 5          # (con margen: las fases cambian cuando PASA el tiempo)


def test_el_juego_abre_con_la_presentacion(tmp_path):
    app = App(carpeta_datos=str(tmp_path), usar_mandos=False)
    assert isinstance(app.escena, Presentacion)


def test_las_pantallas_pasan_solas_y_el_logo_cae(app):
    escena = presentacion(app)
    avanzar(app, frames(MS_ADVERTENCIA))
    assert escena.fase == "pygame"
    avanzar(app, frames(MS_PYGAME))
    assert escena.fase == "titulo" and not escena.logo_cayo
    avanzar(app, frames(LOGO_CAE[1]))
    assert escena.logo_cayo
    assert isinstance(app.escena, Presentacion)        # el titulo espera a que se apriete


def test_un_boton_saltea_al_titulo_sin_pasarse_de_largo(app):
    escena = presentacion(app)
    avanzar(app, frames(MS_SIN_SALTEAR))
    tecla(pygame.K_SPACE)                   # cualquier tecla (no hace falta que sea una accion)
    avanzar(app)
    assert escena.fase == "titulo" and not escena.logo_cayo
    avanzar(app, frames(MS_SIN_SALTEAR))
    tecla(pygame.K_RETURN)                  # antes de que caiga: lo hace caer ya
    avanzar(app)
    assert escena.logo_cayo and isinstance(app.escena, Presentacion)
    tecla(pygame.K_RETURN)                  # apretar de nuevo enseguida no se pasa de largo
    avanzar(app)
    assert isinstance(app.escena, Presentacion)
    avanzar(app, frames(400))
    tecla(pygame.K_RETURN)                  # despues: al menu
    avanzar(app)
    assert isinstance(app.escena, Inicio)


def test_en_silencio_hasta_que_golpea_el_logo(app):
    escena = presentacion(app)
    avanzar(app)
    assert app.sonidos.actual == SILENCIO
    escena.pasar_a("titulo")
    avanzar(app, frames(LOGO_CAE[1]) + 1)
    assert app.sonidos.actual == "menu"


def test_pygame_se_escribe_de_a_una_letra(app):
    escena = presentacion(app)
    pedidos = []
    tocar = app.sonidos.reproducir
    app.sonidos.reproducir = lambda nombre, x=None: pedidos.append(nombre) or tocar(nombre, x)
    escena.pasar_a("pygame")
    avanzar(app, frames(MS_PYGAME - 100))
    assert pedidos.count("teclear") == len("PYGAME")


def test_la_advertencia_dice_si_los_destellos_ya_estan_reducidos(app):
    presentacion(app)
    avanzar(app, frames(1000))
    normal = pygame.image.tostring(app.pantalla, "RGB")
    app.opciones.destellos = "REDUCIDOS"
    avanzar(app)
    assert pygame.image.tostring(app.pantalla, "RGB") != normal
