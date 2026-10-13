"""Escenas: el recorrido completo por las pantallas, como lo haria un jugador."""
import pygame

from juego.config import BOTON_B
from juego.escenas.inicio import Inicio
from juego.escenas.opciones import Opciones
from juego.escenas.listo import Listo
from juego.escenas.juego import Juego
from juego.escenas.pausa import Pausa
from juego.escenas.explosion import Explosion
from juego.escenas.iniciales import Iniciales
from juego.escenas.fin import Fin
from juego.escenas.dificultad import Dificultad
from tests.ayudas import avanzar, tecla, boton, ir_al_ajuste


def empezar(app):
    tecla(pygame.K_RETURN)
    avanzar(app)
    assert isinstance(app.escena, Dificultad)
    tecla(pygame.K_RETURN)
    avanzar(app)
    assert isinstance(app.escena, Listo)
    avanzar(app, 100)
    assert isinstance(app.escena, Juego)
    return app.escena.partida


def test_inicio_opciones_y_volver(app):
    avanzar(app, 3)
    assert isinstance(app.escena, Inicio)
    tecla(pygame.K_UP)                      # da la vuelta: JUGAR -> SALIR -> OPCIONES
    avanzar(app)
    tecla(pygame.K_UP)
    tecla(pygame.K_RETURN)
    avanzar(app)
    assert isinstance(app.escena, Opciones)
    tecla(pygame.K_ESCAPE)
    avanzar(app)
    assert isinstance(app.escena, Inicio)


def test_inicio_logros_y_elegir_nave(app):
    from juego.escenas.logros import Logros
    from juego.config import NAVES
    app.progreso.desbloquear(NAVES[1][2])           # el logro de la segunda nave
    avanzar(app, 3)
    tecla(pygame.K_DOWN)                    # LOGROS
    tecla(pygame.K_RETURN)
    avanzar(app)
    assert isinstance(app.escena, Logros)
    tecla(pygame.K_RIGHT)
    avanzar(app)
    assert app.progreso.nave == NAVES[1][0]
    tecla(pygame.K_RIGHT)                   # solo hay dos: vuelve a la primera
    avanzar(app)
    assert app.progreso.nave == NAVES[0][0]
    tecla(pygame.K_ESCAPE)
    avanzar(app)
    assert isinstance(app.escena, Inicio)


def test_opcion_aviso_jefe_se_cambia_y_se_guarda(app):
    app.cambiar_escena(Opciones(app, volver_a=app.escena))
    ir_al_ajuste(app, "AVISO JEFE")
    tecla(pygame.K_RETURN)
    avanzar(app)
    assert app.opciones.aviso_jefe is False
    tecla(pygame.K_LEFT)
    avanzar(app)
    assert app.opciones.aviso_jefe is True


def test_pausa_y_opciones_desde_la_pausa(app):
    empezar(app)
    tecla(pygame.K_p)
    avanzar(app)
    assert isinstance(app.escena, Pausa)
    tecla(pygame.K_o)
    avanzar(app)
    assert isinstance(app.escena, Opciones)
    boton(BOTON_B)
    avanzar(app)
    assert isinstance(app.escena, Pausa)
    tecla(pygame.K_p)
    avanzar(app)
    assert isinstance(app.escena, Juego)


def pausar(app):
    tecla(pygame.K_p)
    avanzar(app)
    assert isinstance(app.escena, Pausa)
    return app.escena


def test_menu_de_pausa_continuar_y_opciones(app):
    empezar(app)
    pausar(app)
    tecla(pygame.K_RETURN)                  # CONTINUAR (la primera)
    avanzar(app)
    assert isinstance(app.escena, Juego)
    pausa = pausar(app)
    tecla(pygame.K_DOWN)
    tecla(pygame.K_RETURN)                  # OPCIONES
    avanzar(app)
    assert isinstance(app.escena, Opciones)
    tecla(pygame.K_ESCAPE)
    avanzar(app)
    assert app.escena is pausa


def ir_a_volver_al_menu(app):
    pausa = pausar(app)
    tecla(pygame.K_UP)                      # da la vuelta: la ultima es VOLVER AL MENU
    tecla(pygame.K_RETURN)
    avanzar(app)
    assert pausa.confirmando and not pausa.confirmar_si     # pregunta, con NO elegido
    return pausa


def test_volver_al_menu_pregunta_y_no_cancela(app):
    partida = empezar(app)
    partida.puntaje = 321
    pausa = ir_a_volver_al_menu(app)
    tecla(pygame.K_RETURN)                  # NO
    avanzar(app)
    assert not pausa.confirmando and app.escena is pausa
    tecla(pygame.K_ESCAPE)                  # ESC en el menu de pausa: sigue el juego
    avanzar(app)
    assert isinstance(app.escena, Juego) and app.escena.partida.puntaje == 321


def test_escape_en_la_pregunta_es_no(app):
    empezar(app)
    pausa = ir_a_volver_al_menu(app)
    tecla(pygame.K_ESCAPE)
    avanzar(app)
    assert not pausa.confirmando and app.escena is pausa


def test_volver_al_menu_si_pierde_la_partida(app):
    partida = empezar(app)
    partida.puntaje = 500
    ir_a_volver_al_menu(app)
    tecla(pygame.K_RIGHT)                   # SI
    tecla(pygame.K_RETURN)
    avanzar(app)
    assert isinstance(app.escena, Inicio)
    assert app.records.filas("NORMAL") == []        # el puntaje no se guardo
    tecla(pygame.K_RETURN)                  # y se puede jugar otra vez, desde cero
    avanzar(app)
    tecla(pygame.K_RETURN)
    avanzar(app, 101)
    assert isinstance(app.escena, Juego) and app.escena.partida.puntaje == 0


def test_b_del_mando_no_pausa_el_juego(app):
    empezar(app)
    boton(BOTON_B)
    avanzar(app)
    assert isinstance(app.escena, Juego)


def test_pausa_automatica_al_perder_el_foco(app):
    empezar(app)
    pygame.event.post(pygame.event.Event(pygame.WINDOWFOCUSLOST))
    avanzar(app)
    assert isinstance(app.escena, Pausa)


def test_foco_perdido_durante_ready_pausa_al_empezar(app):
    tecla(pygame.K_RETURN)
    avanzar(app)
    tecla(pygame.K_RETURN)
    avanzar(app)
    pygame.event.post(pygame.event.Event(pygame.WINDOWFOCUSLOST))
    avanzar(app, 101)
    assert isinstance(app.escena, Pausa)


def test_el_tiempo_del_juego_no_corre_en_pausa(app):
    partida = empezar(app)
    tecla(pygame.K_p)
    avanzar(app)
    tiempo = partida.tiempo
    avanzar(app, 120)
    assert partida.tiempo == tiempo


def perder(app, partida, puntaje):
    partida.puntaje = puntaje
    partida.vidas = 1
    partida.nave.invulnerable_hasta = 0
    partida.danar_jugador(*partida.nave.centro())
    avanzar(app)
    assert isinstance(app.escena, Explosion)
    avanzar(app, 110)


def test_game_over_con_record_iniciales_y_otra_partida(app):
    partida = empezar(app)
    perder(app, partida, 25)
    assert isinstance(app.escena, Iniciales)
    tecla(pygame.K_UP)              # A -> B
    for _ in range(3):
        tecla(pygame.K_RETURN)
    avanzar(app)
    assert isinstance(app.escena, Fin)
    assert app.records.filas("NORMAL")[0] == {"nombre": "BAA", "puntos": 25}
    tecla(pygame.K_RETURN)          # muy pronto: se ignora
    avanzar(app)
    assert isinstance(app.escena, Fin)
    avanzar(app, 50)
    tecla(pygame.K_RETURN)
    avanzar(app)
    assert isinstance(app.escena, Listo)


def test_game_over_sin_puntos_va_directo_al_fin(app):
    partida = empezar(app)
    perder(app, partida, 0)
    assert isinstance(app.escena, Fin)


def test_cerrar_en_las_iniciales_guarda_el_record(app):
    partida = empezar(app)
    perder(app, partida, 40)
    pygame.event.post(pygame.event.Event(pygame.QUIT))
    avanzar(app)
    assert not app.ejecutando
    assert app.records.filas("NORMAL")[0]["puntos"] == 40


def test_m_silencia_y_vuelve_a_prender(app):
    avanzar(app)
    tecla(pygame.K_m)
    avanzar(app)
    assert not app.opciones.musica and not app.opciones.efectos
    tecla(pygame.K_m)
    avanzar(app)
    assert app.opciones.musica and app.opciones.efectos


def test_f11_pantalla_completa_y_vuelve(app):
    avanzar(app)
    antes = app.opciones.resolucion
    tecla(pygame.K_F11)
    avanzar(app)
    assert app.opciones.resolucion == "COMPLETA"
    tecla(pygame.K_F11)
    avanzar(app)
    assert app.opciones.resolucion == antes


def test_el_dash_apretado_en_el_hit_stop_sale_al_terminar(app):
    # Bug: durante el hit-stop las acciones se borraban y el dash se perdia
    app.nueva_partida()
    avanzar(app, 101)
    partida = app.escena.partida
    partida.congelar_frames = 3
    tecla(pygame.K_SPACE)
    avanzar(app, 5)
    assert partida.estadisticas.dashes == 1


def test_la_pausa_apretada_en_el_hit_stop_se_abre_al_terminar(app):
    app.nueva_partida()
    avanzar(app, 101)
    partida = app.escena.partida
    partida.congelar_frames = 3
    tecla(pygame.K_p)
    avanzar(app, 5)
    assert isinstance(app.escena, Pausa)
