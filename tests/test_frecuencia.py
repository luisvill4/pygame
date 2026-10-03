"""
Frecuencia (FPS): la logica va siempre a 60 pasos por segundo, se dibuje a la
frecuencia que se dibuje. Asi el juego se siente igual a 30, 60, 144 o sin limite.
"""
import json

import pygame
import pytest

from juego.config import MS_POR_FRAME, FRECUENCIAS, NAVE_VELOCIDAD, NAVE_ACELERACION
from juego.efectos import Efectos
from juego.guardado import Opciones as OpcionesGuardadas
from juego.escenas.juego import Juego
from juego.escenas.opciones import Opciones
from juego.interpolacion import Interpolador
from tests.ayudas import avanzar, tecla, empezar_partida


def empezar(app):
    partida = empezar_partida(app)
    assert isinstance(app.escena, Juego)
    partida.director.proxima_oleada = float("inf")
    partida.enemigos.clear()
    partida.proximo_powerup = float("inf")
    partida.moneda.x, partida.moneda.y = -500, -500
    return partida


def jugar_un_segundo(app, fps):
    # Simula un segundo real dibujando a 'fps' cuadros por segundo
    for _ in range(fps):
        app.cuadro(1000 / fps)


@pytest.mark.parametrize("fps", [30, 60, 90, 120, 144, 500])
def test_el_juego_va_a_la_misma_velocidad_a_cualquier_fps(app, fps):
    partida = empezar(app)
    app.teclas.add(pygame.K_RIGHT)
    tiempo_inicial, x_inicial = partida.tiempo, partida.nave.x
    jugar_un_segundo(app, fps)
    # En un segundo real la logica avanza un segundo, sin importar los FPS: lo que no
    # alcanzo para un paso entero queda guardado para el cuadro siguiente (no se pierde)
    pasos = round((partida.tiempo - tiempo_inicial) / MS_POR_FRAME)
    assert pasos in (59, 60)
    assert partida.tiempo - tiempo_inicial + app.acumulado == pytest.approx(1000)
    # Y la nave recorre lo mismo que si se jugara a 60 FPS esa cantidad de pasos
    assert partida.nave.x - x_inicial == pytest.approx(distancia_en_pasos(pasos))


def distancia_en_pasos(pasos):
    # Lo que recorre la nave acelerando desde quieta, paso a paso (como en Nave.actualizar)
    velocidad, recorrido = 0, 0
    for _ in range(pasos):
        velocidad += (NAVE_VELOCIDAD - velocidad) * NAVE_ACELERACION
        recorrido += velocidad
    return recorrido


def test_a_mas_de_60_fps_no_se_pierden_teclas(app):
    partida = empezar(app)
    tecla(pygame.K_SPACE)
    app.cuadro(1)               # cuadro muy corto: no toca ningun paso de logica
    assert partida.nave.dash_hasta == 0
    app.cuadro(MS_POR_FRAME)    # ahora si: el dash sale
    assert partida.nave.dash_hasta > 0


def test_si_la_ventana_se_traba_no_intenta_alcanzar(app):
    partida = empezar(app)
    tiempo = partida.tiempo
    app.cuadro(5000)            # 5 segundos trabado (ej: moviendo la ventana)
    assert partida.tiempo - tiempo <= 250 + MS_POR_FRAME


def test_interpolacion():
    class Cosa:
        def __init__(self, x, y):
            self.x, self.y = x, y

    cosa, teletransportada = Cosa(0, 0), Cosa(0, 0)
    interpolador = Interpolador()
    interpolador.guardar([cosa, teletransportada])
    cosa.x, teletransportada.x = 10, 500
    with interpolador.aplicar([cosa, teletransportada], 0.5):
        assert cosa.x == 5                  # a mitad de camino
        assert teletransportada.x == 500    # un salto enorme no se interpola
    assert cosa.x == 10                     # al terminar de dibujar vuelve a su posicion real


def test_el_temblor_dura_pasos_de_logica_no_cuadros():
    efectos = Efectos()
    efectos.sacudir(10)
    pantalla = pygame.Surface((800, 600))
    for _ in range(50):         # muchos cuadros dibujados (ej: a 144 FPS)...
        efectos.dibujar_temblor_y_destello(pantalla)
    assert efectos.temblor == 10                # ...no lo gastan
    for _ in range(10):
        efectos.actualizar()
    assert efectos.temblor == 0


def test_opcion_fps_en_el_menu(app, tmp_path):
    app.cambiar_escena(Opciones(app, volver_a=app.escena))
    tecla(pygame.K_DOWN)
    tecla(pygame.K_DOWN)        # fila FPS
    tecla(pygame.K_RIGHT)
    avanzar(app)
    assert app.opciones.fps == 90
    for _ in range(3):
        tecla(pygame.K_RIGHT)
    avanzar(app)
    assert app.opciones.fps == 0                # SIN LIMITE
    assert json.loads((tmp_path / "config.json").read_text())["fps"] == 0
    tecla(pygame.K_RIGHT)
    avanzar(app)
    assert app.opciones.fps == FRECUENCIAS[0]   # vuelve a 30


def test_fps_invalido_en_config_usa_60(tmp_path):
    archivo = tmp_path / "config.json"
    for invalido in [75, "144", False, None]:
        archivo.write_text(json.dumps({"fps": invalido}))
        assert OpcionesGuardadas(str(archivo)).fps == 60
