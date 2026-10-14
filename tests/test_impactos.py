"""El impacto de los momentos clave: el golpe final al jefe, la herida y la ultima vida."""
import pygame
import pytest

from juego import impactos, accesibilidad
from juego.config import (IMPACTO_PASOS, CAMARA_LENTA_JEFE, MS_POR_FRAME, HERIDA_MS, LATIDO_MS, BLANCO,
                          ANCHO, ALTO)
from juego.escenas.juego import Juego
from tests.ayudas import avanzar


def en_juego(app, partida):
    # Directo al juego, y se espera a que termine la transicion de rombos de la partida nueva
    app.cambiar_escena(Juego(app, partida), transicion=False)
    avanzar(app, 30)
    return app.escena


def traer_jefe(app, partida):
    # Un jefe que ya termino de entrar (sin la cinematica, que tapa el HUD)
    partida.iniciar_jefe("ojo")
    jefe = partida.jefe
    jefe.cambiar_fase("cansado", 5000, partida.tiempo)     # (anota fin_entrada: por eso va primero)
    jefe.creado_en -= 10000
    jefe.fin_entrada = partida.tiempo - 5000
    avanzar(app)
    return jefe


def matar_al_jefe(app, partida):
    jefe = partida.jefe or traer_jefe(app, partida)
    jefe.vida = 1
    jefe.recibir_golpe(partida)


def colores(pantalla, rect):
    return [pantalla.get_at((x, y))[:3] for x in range(rect.left, rect.right, 4) for y in range(rect.top, rect.bottom, 4)]


# ---------- El golpe final ----------

def test_el_golpe_final_congela_y_despues_va_en_camara_lenta(app, partida):
    en_juego(app, partida)
    matar_al_jefe(app, partida)
    assert partida.impacto is not None
    assert partida.congelar_frames == IMPACTO_PASOS and partida.camara_lenta == CAMARA_LENTA_JEFE
    antes = partida.tiempo
    avanzar(app, IMPACTO_PASOS)
    assert partida.tiempo == antes and partida.impacto is None          # congelado
    avanzar(app, 20)
    assert partida.tiempo - antes == pytest.approx(10 * MS_POR_FRAME)  # a media velocidad
    avanzar(app, CAMARA_LENTA_JEFE)
    assert partida.camara_lenta == 0


def test_el_cuadro_de_impacto_oscurece_el_mundo_y_salen_rayos_del_color_del_jefe(app, partida):
    en_juego(app, partida)
    matar_al_jefe(app, partida)
    avanzar(app, 8)                         # (despues del destello)
    pantalla = app.pantalla
    zona = pygame.Rect(0, 120, ANCHO, ALTO - 240)
    pixeles = colores(pantalla, zona)
    rayos = sum(1 for c in pixeles if c == tuple(partida.jefe.color))
    assert rayos > 20
    oscuros = sum(1 for c in pixeles if sum(c) < 90)
    assert oscuros > len(pixeles) * 0.5


def test_el_destello_no_sale_con_destellos_reducidos(app, partida):
    en_juego(app, partida)
    matar_al_jefe(app, partida)
    avanzar(app, 1)
    claros = sum(1 for c in colores(app.pantalla, pygame.Rect(0, 120, ANCHO, 360)) if min(c) > 150)
    assert claros > 1000                    # el destello blanco
    app.opciones.destellos = "REDUCIDOS"
    avanzar(app, IMPACTO_PASOS + CAMARA_LENTA_JEFE)
    matar_al_jefe(app, partida)
    avanzar(app, 1)
    claros = sum(1 for c in colores(app.pantalla, pygame.Rect(0, 120, ANCHO, 360)) if min(c) > 150)
    assert claros < 300


def test_el_hud_no_queda_tapado_por_el_impacto(app, partida):
    en_juego(app, partida)
    traer_jefe(app, partida)
    marcador = colores(app.pantalla, pygame.Rect(20, 10, 100, 40))
    assert any(sum(c) > 300 for c in marcador)              # (se ve el marcador: el texto claro)
    matar_al_jefe(app, partida)
    avanzar(app, 8)
    durante = colores(app.pantalla, pygame.Rect(20, 10, 100, 40))
    # El texto del marcador (los pixeles claros) sigue igual de nitido: el velo va debajo del HUD
    claros = [i for i, c in enumerate(marcador) if sum(c) > 300]
    assert claros and all(durante[i] == marcador[i] for i in claros)


# ---------- Herida y ultima vida ----------

def test_la_herida_deja_una_vineta_roja_que_se_apaga(app, partida):
    en_juego(app, partida)
    avanzar(app)
    esquina = pygame.Rect(30, 300, 8, 8)
    sin_herida = colores(app.pantalla, esquina)
    partida.danar_jugador(partida.nave.x, partida.nave.y)
    avanzar(app, 8)
    herida = colores(app.pantalla, esquina)
    assert all(r > g for r, g, b in herida) and herida != sin_herida
    partida.vidas = partida.vidas_max           # (sin la vineta de la ultima vida)
    avanzar(app, int(HERIDA_MS / MS_POR_FRAME) + 2)
    assert not any(r > g + 20 for r, g, b in colores(app.pantalla, esquina))      # ya no queda rojo


def test_la_ultima_vida_avisa_y_late(app, partida):
    partida.vidas = 2
    partida.danar_jugador(partida.nave.x, partida.nave.y)
    avisos = [partida.avisos.actual] + partida.avisos.esperando
    assert any(a is not None and a.titulo == "¡ULTIMA VIDA!" for a in avisos)
    partida.tiempo = 10 * LATIDO_MS + 50            # en el golpe del latido
    assert impactos.latiendo(partida)
    partida.tiempo = 10 * LATIDO_MS + LATIDO_MS // 2
    assert not impactos.latiendo(partida)
    partida.tiempo = 10 * LATIDO_MS + 50
    accesibilidad.opciones.destellos = "REDUCIDOS"
    assert not impactos.latiendo(partida)           # con destellos reducidos no late


def test_con_una_vida_la_vineta_late_y_con_destellos_reducidos_queda_quieta(app, partida):
    partida.vidas = 1
    fuerzas = set()
    for paso in range(0, LATIDO_MS, 50):
        partida.tiempo = 100 * LATIDO_MS + paso
        fuerzas.add(round(impactos.fuerza_de_la_vineta(partida), 3))
    assert len(fuerzas) > 5 and min(fuerzas) > 0          # late (y nunca se apaga del todo)
    app.opciones.destellos = "REDUCIDOS"
    fuerzas = set()
    for paso in range(0, LATIDO_MS, 50):
        partida.tiempo = 100 * LATIDO_MS + paso
        fuerzas.add(impactos.fuerza_de_la_vineta(partida))
    assert len(fuerzas) == 1 and fuerzas.pop() > 0        # quieta
