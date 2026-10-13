"""Vibracion del mando: patrones, prioridad, intensidad y cuando vibra (y cuando no)."""
import json
import os

import pygame

from juego.config import VIBRACIONES, MS_POR_FRAME, NOMBRE_CONFIG
from juego.enemigos import crear_enemigo
from juego.escenas.opciones import Opciones
from juego.escenas.pausa import Pausa
from tests.ayudas import avanzar, tecla, jugar, ir_al_ajuste


class MandoFalso:
    # Anota lo que se le pide a los motores (sin cruceta ni stick: no mueve la nave)
    def __init__(self):
        self.motores = []           # (grave, agudo, ms)
        self.parado = False

    def rumble(self, grave, agudo, ms):
        self.motores.append((grave, agudo, ms))
        return True

    def stop_rumble(self):
        self.parado = True

    def get_numhats(self):
        return 0

    def get_numaxes(self):
        return 0


def conectar_mando(app):
    mando = MandoFalso()
    app.entrada.mandos[1] = mando
    return mando


def test_todos_los_patrones_estan_bien_armados():
    for nombre, (prioridad, pasos) in VIBRACIONES.items():
        assert 1 <= prioridad <= 4, nombre
        for paso in pasos:
            ms, *fuerzas = paso
            assert ms > 0 and len(fuerzas) == 2, nombre
            assert all(0 <= fuerza <= 0.5 for fuerza in fuerzas), nombre     # suave: nada al maximo


def test_un_patron_avanza_paso_a_paso_y_termina(app):
    mando = conectar_mando(app)
    haptica = app.entrada.haptica
    _, pasos = VIBRACIONES["oleada"]          # tres pasos: pulso, silencio, pulso
    haptica.reproducir("oleada")
    assert mando.motores[-1][0] == pasos[0][1]
    avanzar(app, int(pasos[0][0] // MS_POR_FRAME) + 2)     # (el reloj falso avanza despues de cada paso)
    assert mando.motores[-1][0] == 0            # el silencio del medio
    avanzar(app, 30)
    assert len(mando.motores) == 3
    assert mando.motores[-1][2] == pasos[-1][0]     # el ultimo se manda justo (sin solapar)
    assert not haptica.sonando()


def test_uno_chico_no_corta_a_uno_grande(app):
    conectar_mando(app)
    haptica = app.entrada.haptica
    haptica.reproducir("muerte")
    haptica.reproducir("combo_sube")
    assert haptica.nombre == "muerte"
    haptica.parar()
    haptica.reproducir("combo_sube")
    haptica.reproducir("golpe")                 # uno mas fuerte si corta al chico
    assert haptica.nombre == "golpe"


def test_la_intensidad_sale_de_las_opciones(app):
    mando = conectar_mando(app)
    app.opciones.vibracion = "SUAVE"
    app.entrada.vibrar("golpe")
    assert mando.motores[-1][0] == VIBRACIONES["golpe"][1][0][1] * 0.5
    app.entrada.haptica.parar()
    app.opciones.vibracion = "FUERTE"
    app.entrada.vibrar("powerup")
    assert mando.motores[-1][1] > VIBRACIONES["powerup"][1][0][2]      # los chicos se sienten mas
    app.entrada.haptica.parar()
    app.opciones.vibracion = "NO"
    cantidad = len(mando.motores)
    app.entrada.vibrar("muerte")
    assert len(mando.motores) == cantidad
    assert not app.entrada.haptica.sonando()


def test_solo_vibra_cuando_sube_el_combo(partida, app):
    haptica = app.entrada.haptica
    nombres = []
    for _ in range(12):
        partida.moneda.x, partida.moneda.y = partida.nave.x + 15, partida.nave.y + 15
        jugar(partida)
        partida.moneda.x, partida.moneda.y = -500, -500
        nombres.append(haptica.nombre)
        haptica.parar()
    assert nombres[0] is None                   # cada moneda no vibra (seria todo el tiempo)
    assert nombres[2] == "combo_sube"           # la tercera moneda: x2
    assert nombres[11] == "combo_maximo"        # la duodecima: x5


def test_el_dash_no_vibra_pero_romper_y_el_golpe_si(partida, app):
    haptica = app.entrada.haptica
    jugar(partida, dash=True)
    assert not haptica.sonando()
    jugar(partida, 30)
    partida.nave.dash_listo = 0                 # el dash ya se recargo
    partida.nave.x, partida.nave.y = 100, 300
    partida.nave.vx, partida.nave.vy = 0, 0
    divisor = crear_enemigo("divisor_chico", partida)
    divisor.aparece_en = 0
    divisor.x, divisor.y = 165, 315
    partida.enemigos.append(divisor)
    jugar(partida, dx=1, dash=True)
    jugar(partida, 8, dx=1)
    assert divisor not in partida.enemigos
    assert haptica.nombre == "perfecto"         # lo rompio con el dash (pisa al de destruir)
    haptica.parar()
    partida.nave.invulnerable_hasta = 0
    partida.danar_jugador(partida.nave.x - 100, partida.nave.y)
    assert haptica.nombre == "golpe"


def test_la_pausa_corta_la_vibracion(app):
    mando = conectar_mando(app)
    tecla(pygame.K_RETURN)
    avanzar(app)
    tecla(pygame.K_RETURN)
    avanzar(app, 101)
    app.entrada.vibrar("muerte")
    tecla(pygame.K_p)
    avanzar(app)
    assert isinstance(app.escena, Pausa)
    assert mando.parado
    assert not app.entrada.haptica.sonando()


def test_opcion_vibracion_se_cambia_prueba_y_se_guarda(app, tmp_path):
    mando = conectar_mando(app)
    app.cambiar_escena(Opciones(app, volver_a=app.escena))
    ir_al_ajuste(app, "VIBRACION")
    tecla(pygame.K_LEFT)
    avanzar(app)
    assert app.opciones.vibracion == "SUAVE"
    assert app.entrada.haptica.nombre == "prueba"       # vibra para que se sienta como queda
    assert mando.motores
    for _ in range(5):
        tecla(pygame.K_LEFT)
    avanzar(app)
    assert app.opciones.vibracion == "NO"               # no da la vuelta
    with open(os.path.join(tmp_path, NOMBRE_CONFIG), encoding="utf-8") as archivo:
        assert json.load(archivo)["vibracion"] == "NO"

