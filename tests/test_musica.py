"""Musica: cada escena pide su tema y la App lo cambia con un fundido."""
import pygame

from juego.sonido import MUSICAS, SILENCIO, ruta_del_sonido
from juego.config import MS_POR_FRAME
from juego.hud import MS_ALERTA
from tests.ayudas import avanzar, empezar_partida, tecla


def test_los_temas_existen():
    for archivo in MUSICAS.values():
        assert ruta_del_sonido(archivo) is not None, archivo


def test_el_menu_tiene_su_musica(app):
    avanzar(app)
    assert app.sonidos.actual == "menu"
    tecla(pygame.K_RETURN)          # JUGAR -> elegir dificultad: sigue la misma
    avanzar(app)
    assert app.sonidos.actual == "menu"


def test_al_jugar_suena_la_del_juego_y_con_el_jefe_la_suya(app):
    partida = empezar_partida(app)
    assert app.sonidos.actual == "juego"
    partida.iniciar_jefe()
    avanzar(app)
    assert app.sonidos.actual == SILENCIO          # la ¡ALERTA!: solo la sirena
    avanzar(app, int(MS_ALERTA / MS_POR_FRAME) + 2)
    assert app.sonidos.actual == "jefe"            # entra con el nombre del jefe
    partida.jefe.empezar_a_morir(partida)
    avanzar(app)
    assert app.sonidos.actual == SILENCIO          # el golpe final corta la musica
    partida.jefe = None             # (como al terminar de morir)
    avanzar(app)
    assert app.sonidos.actual == "juego"


def test_el_cierre_del_sector_va_sin_musica(app):
    partida = empezar_partida(app)
    partida.director.fin_del_cierre = partida.tiempo + 5000     # (como despues de vencer al jefe)
    avanzar(app)
    assert app.sonidos.actual == SILENCIO


def test_ready_en_silencio_y_la_musica_entra_en_el_go(app):
    tecla(pygame.K_RETURN)
    avanzar(app)
    tecla(pygame.K_RETURN)
    avanzar(app, 5)
    assert app.sonidos.actual == SILENCIO
    avanzar(app, 60)                # pasa el segundo del READY?
    assert app.sonidos.actual == "juego"


def test_iniciales_y_game_over_tienen_su_musica(app):
    from juego.escenas.arcade.iniciales import Iniciales
    from juego.escenas.arcade.fin import Fin
    partida = empezar_partida(app)
    app.cambiar_escena(Iniciales(app, partida))
    avanzar(app)
    assert app.sonidos.actual == "iniciales"
    app.cambiar_escena(Fin(app, partida, fila_nueva=-1))
    avanzar(app)
    assert app.sonidos.actual == "fin"


def test_la_pausa_no_cambia_la_musica_y_volver_al_menu_si(app):
    partida = empezar_partida(app)
    partida.pausa_pendiente = True
    avanzar(app, 2)
    assert app.sonidos.actual == "juego"
    app.escena._volver_al_menu()
    assert app.sonidos.actual is None
    avanzar(app)
    assert app.sonidos.actual == "menu"


def test_al_morir_la_musica_se_corta_y_no_vuelve(app):
    partida = empezar_partida(app)
    partida.vidas = 1
    partida.danar_jugador(partida.nave.x, partida.nave.y)
    assert app.sonidos.actual is None
    avanzar(app, 30)                # hit-stop y explosion
    assert app.sonidos.actual is None


def test_la_gasolinera_tiene_su_musica_y_al_salir_vuelve_la_del_juego(app):
    partida = empezar_partida(app)
    juego = app.escena
    partida.director.gasolinera = True
    avanzar(app, 2)                 # Juego la abre y en el paso siguiente pide su musica
    assert app.sonidos.actual == "gasolinera"
    partida.director.gasolinera = False
    app.cambiar_escena(juego)
    avanzar(app)
    assert app.sonidos.actual == "juego"


def test_cada_sector_tiene_su_color_y_el_nivel_antes_del_jefe_su_tension(app):
    from juego.config import SECTORES, JEFE_CADA_NIVELES
    partida = empezar_partida(app)
    partida.director.sector = SECTORES[2]
    avanzar(app)
    assert app.sonidos.actual == "juego_3"
    partida.nivel = JEFE_CADA_NIVELES - 1
    avanzar(app)
    assert app.sonidos.actual == "tension"


def test_el_ambiente_del_bioma_se_calla_en_la_pelea_y_en_los_menus(app):
    from juego.config import SECTORES
    partida = empezar_partida(app)
    assert app.sonidos.ambiente.actual == SECTORES[0]["ambiente"]
    partida.iniciar_jefe()
    avanzar(app)
    assert app.sonidos.ambiente.actual == SILENCIO
    app.escena._volver_al_menu = None           # (no hace falta)
    from juego.escenas.inicio import Inicio
    app.cambiar_escena(Inicio(app))
    avanzar(app)
    assert app.sonidos.ambiente.actual == SILENCIO


def test_cada_jefe_tiene_su_tema_y_el_ojo_el_de_siempre(app):
    from juego.jefes import TIPOS_JEFE
    partida = empezar_partida(app)
    for tipo in TIPOS_JEFE:
        partida.iniciar_jefe(tipo)
        avanzar(app, int(MS_ALERTA / MS_POR_FRAME) + 2)
        assert app.sonidos.actual == ("jefe" if tipo == "ojo" else "jefe_" + tipo)
        partida.jefe = None


def test_el_modo_historia_mapa_con_la_del_menu_y_el_dialogo_en_silencio(app):
    # El mapa sigue con la del menu; el dialogo de antes de la mision va sin musica, con el
    # ambiente del sector de la mision (las voces y el lugar); despues, la del juego
    from juego.config import SECTORES
    from juego.escenas.historia.mapa import Mapa
    from juego.escenas.historia.dialogo import Dialogo
    tecla(pygame.K_DOWN)            # HISTORIA
    avanzar(app)
    tecla(pygame.K_RETURN)
    avanzar(app)
    assert isinstance(app.escena, Mapa) and app.sonidos.actual == "menu"
    tecla(pygame.K_RETURN)          # la mision 1
    avanzar(app, 2)                 # (el tema se pide antes de cada paso)
    assert isinstance(app.escena, Dialogo)
    assert app.sonidos.actual == SILENCIO and app.escena.ambiente == SECTORES[0]["ambiente"]
