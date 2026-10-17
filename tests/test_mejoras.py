"""Mejoras: el sorteo, el Taller y el efecto de cada carta."""
import math

import pygame
import pytest

from juego.config import (DASH_RECARGA, NAVE_VELOCIDAD, COMBO_TIEMPO, MEJORA_RECARGA, MEJORA_MOTOR, MEJORA_COMBO,
                          MEJORA_COMETA, MEJORA_ROCE, MEJORA_POTENCIA, MEJORA_ONDA_RADIO, ESPERA_POWERUP,
                          MEJORA_SUERTE, MEJORA_FILO_PUNTOS, DURACION, MEJORA_PRIMER_NIVEL, MS_POR_FRAME,
                          CARTEL_JEFE, CARTEL_RANGO)
from juego.mejoras import TIPOS_MEJORA, sortear_mejoras
from juego.enemigos import crear_enemigo
from juego.powerups import TIPOS_POWERUP
from juego.proyectiles import Bala
from juego.escenas.juego import Juego
from juego.escenas.taller import Taller, PASOS_SIN_ELEGIR
from tests.ayudas import jugar, avanzar, tecla, empezar_partida


def enemigo_en(partida, tipo, x, y):
    enemigo = crear_enemigo(tipo, partida)
    enemigo.aparece_en = 0
    enemigo.x, enemigo.y = x, y
    partida.enemigos.append(enemigo)
    return enemigo


def test_todas_estan_completas():
    for mejora in TIPOS_MEJORA.values():
        assert mejora.nombre and len(mejora.nombre) <= 12
        assert mejora.descripcion and all(len(linea) <= 22 for linea in mejora.descripcion)
        assert len(mejora.icono) == 7 and all(len(fila) == 7 for fila in mejora.icono)


def test_el_sorteo_da_tres_distintas_y_respeta_el_maximo(partida):
    for _ in range(50):
        ofertas = sortear_mejoras(partida)
        assert len(ofertas) == 3 and len(set(ofertas)) == 3
    partida.mejoras = {tipo: mejora.maximo for tipo, mejora in TIPOS_MEJORA.items()}
    assert sortear_mejoras(partida) == []


def test_filo_no_sale_en_el_primer_sector(partida):
    assert not TIPOS_MEJORA["filo"].disponible(partida)
    partida.director.numero_sector = 2
    assert TIPOS_MEJORA["filo"].disponible(partida)


def test_gratis_en_el_nivel_3_y_gasolinera_al_cerrar_un_sector(partida):
    director = partida.director
    director.con_mejoras = True
    partida.nivel = MEJORA_PRIMER_NIVEL - 1
    partida.subir_nivel()
    assert len(director.ofertas) == 3
    partida.elegir_mejora(director.ofertas[0].tipo)
    assert director.ofertas == []
    # Al vencer a un jefe: cuando termina el cierre del sector se para en la gasolinera
    # (ahi se compran: el Taller gratis ya no se abre)
    partida.nivel = 4
    partida.nave.invulnerable_hasta = math.inf
    partida.subir_nivel()
    partida.jefe_vencido()
    jugar(partida, int((CARTEL_JEFE + CARTEL_RANGO) / MS_POR_FRAME) - 5)
    assert not director.gasolinera
    jugar(partida, 10)
    assert director.gasolinera
    assert director.ofertas == []


def test_el_taller_se_abre_y_al_elegir_vuelve_al_juego(app):
    avanzar(app)
    partida = empezar_partida(app)
    partida.nave.invulnerable_hasta = math.inf
    partida.director.ofertas = sortear_mejoras(partida)
    avanzar(app)
    assert isinstance(app.escena, Taller)
    tiempo = partida.tiempo
    tecla(pygame.K_RETURN)
    avanzar(app)
    assert isinstance(app.escena, Taller)          # muy pronto: se ignora
    avanzar(app, PASOS_SIN_ELEGIR)
    elegida = app.escena.ofertas[app.escena.elegida]
    tecla(pygame.K_RETURN)
    avanzar(app)
    assert isinstance(app.escena, Juego)
    assert partida.mejora(elegida.tipo) == 1
    assert partida.tiempo == tiempo                # el juego estuvo quieto mientras se elegia


# ---------- Efectos ----------


def test_recarga_motor_combo_y_cometa(partida):
    for tipo in ("recarga", "motor", "combo", "cometa"):
        partida.elegir_mejora(tipo)
    assert partida.recarga_dash() == pytest.approx(DASH_RECARGA * (1 - MEJORA_RECARGA))
    assert partida.vel_max() == pytest.approx(NAVE_VELOCIDAD * (1 + MEJORA_MOTOR))
    assert partida.tiempo_combo() == pytest.approx(COMBO_TIEMPO * (1 + MEJORA_COMBO))
    assert partida.nave.duracion_dash == round(180 * MEJORA_COMETA)


def test_corazon_suma_una_vida_maxima_y_cura(partida):
    partida.vidas = 1
    vidas_max = partida.vidas_max
    partida.elegir_mejora("corazon")
    assert partida.vidas_max == vidas_max + 1
    assert partida.vidas == 2


def test_fenix_salva_una_vez(partida):
    partida.elegir_mejora("fenix")
    partida.vidas = 1
    partida.danar_jugador(0, 0)
    assert not partida.termino and partida.vidas == 1
    assert partida.mejora("fenix") == 0
    partida.nave.invulnerable_hasta = 0
    partida.danar_jugador(0, 0)
    assert partida.termino


def test_onda_al_terminar_el_dash(partida):
    partida.elegir_mejora("onda")
    partida.nave.x, partida.nave.y = 300, 300
    jugar(partida, dx=1, dash=True)
    jugar(partida, int(partida.nave.duracion_dash / MS_POR_FRAME) - 1, dx=1)
    nave_x, nave_y = partida.nave.centro()
    radio = MEJORA_ONDA_RADIO[0]
    divisor = enemigo_en(partida, "divisor_chico", nave_x + radio - 30, nave_y - 10)
    perseguidor = enemigo_en(partida, "perseguidor", nave_x - 20, nave_y + radio - 40)
    partida.balas.append(Bala(nave_x + 10, nave_y - radio + 20, 0, 0))
    jugar(partida, 3)
    assert divisor not in partida.enemigos              # destruido
    assert perseguidor.aturdido(partida.tiempo)         # empujado y aturdido
    assert not partida.balas


def test_un_aturdido_no_lastima_ni_se_mueve(partida):
    enemigo = enemigo_en(partida, "perseguidor", 300, 300)
    enemigo.aturdido_hasta = partida.tiempo + 1000
    partida.nave.x, partida.nave.y = 295, 295
    x_antes = enemigo.x
    jugar(partida, 10)
    assert partida.vidas == partida.vidas_max
    assert enemigo.x == x_antes


def test_filo_destruye_a_los_que_el_dash_atraviesa(partida):
    partida.director.numero_sector = 2
    partida.elegir_mejora("filo")
    partida.nave.x, partida.nave.y = 100, 300
    perseguidor = enemigo_en(partida, "perseguidor", 150, 305)
    jugar(partida, dx=1, dash=True)
    jugar(partida, 6, dx=1)
    assert perseguidor not in partida.enemigos
    assert partida.puntaje >= MEJORA_FILO_PUNTOS


def hacer_perfectos(partida, cantidad):
    for _ in range(cantidad):
        partida.perfecto_en_este_dash = False
        partida._dash_perfecto(0, 0)


def test_escudo_roce_se_regenera_toda_la_partida(partida):
    partida.elegir_mejora("roce")
    assert MEJORA_ROCE == [6, 4, 3]
    for _ in range(3):              # tres veces seguidas: no se gasta
        hacer_perfectos(partida, MEJORA_ROCE[0] - 1)
        assert not partida.activo("escudo")
        hacer_perfectos(partida, 1)
        assert partida.activo("escudo")
        jugar(partida, 60 * 12)     # dura hasta el golpe (antes se iba a los 8 s)
        assert partida.activo("escudo")
        hacer_perfectos(partida, 10)        # con el escudo puesto no se cuenta
        assert partida.perfectos_para_escudo == 0
        partida.nave.invulnerable_hasta = 0
        partida.danar_jugador(partida.nave.x, partida.nave.y)
        assert not partida.activo("escudo")
        assert partida.vidas == partida.vidas_max


def test_escudo_roce_pide_menos_perfectos_por_nivel(partida):
    for nivel, necesarios in enumerate(MEJORA_ROCE, start=1):
        partida.elegir_mejora("roce")
        assert partida.perfectos_para_regenerar() == necesarios
        hacer_perfectos(partida, necesarios)
        assert partida.activo("escudo"), nivel
        partida.desactivar("escudo")
    assert TIPOS_MEJORA["roce"].maximo == 3


def test_la_capsula_no_acorta_el_escudo_roce(partida):
    partida.elegir_mejora("roce")
    hacer_perfectos(partida, MEJORA_ROCE[0])
    assert not TIPOS_POWERUP["escudo"].disponible(partida)
    partida.activar("escudo", 5000)
    assert partida.restante("escudo") == math.inf


def test_atraccion_acerca_la_moneda(partida):
    partida.elegir_mejora("atraccion")
    nave_x, nave_y = partida.nave.centro()
    partida.moneda.x, partida.moneda.y = nave_x + 80, nave_y
    jugar(partida, 5)
    assert partida.moneda.x < nave_x + 80


def test_suerte_y_potencia_con_los_power_ups(partida):
    partida.elegir_mejora("suerte")
    for _ in range(50):
        assert partida.espera_powerup() <= ESPERA_POWERUP[1] * (1 - MEJORA_SUERTE) * partida.reglas["espera_powerup"]
    partida.elegir_mejora("potencia")
    TIPOS_POWERUP["doble"].al_recoger(partida, 0, 0)
    assert partida.restante("doble") == pytest.approx(DURACION["doble"] * (1 + MEJORA_POTENCIA))


def test_botin_duplica_los_puntos_del_dash(partida):
    partida.elegir_mejora("botin")
    enemigo = enemigo_en(partida, "divisor_chico", 300, 300)
    partida.destruir_con_dash(enemigo)
    assert partida.puntaje == enemigo.puntos_dash * 2


def test_doble_dash_da_un_dash_extra_y_es_dificil_de_conseguir(partida):
    doble = TIPOS_MEJORA["doble_dash"]
    assert doble.peso < 1 and doble.maximo == 1
    assert not doble.disponible(partida)            # solo desde el sector 3
    partida.director.numero_sector = 3
    assert doble.disponible(partida)
    partida.elegir_mejora("doble_dash")
    assert partida.nave.dash_extra_max == 1
    assert not doble.disponible(partida)            # una sola vez


def dash_con_eco(partida, monkeypatch, azar):
    # Un dash a la derecha con la mejora ECO y el azar fijo
    import random
    monkeypatch.setattr(random, "random", lambda: azar)
    partida.elegir_mejora("eco")
    partida.nave.x, partida.nave.y = 100, 300
    jugar(partida, dx=1, dash=True)
    jugar(partida, int(partida.nave.duracion_dash / MS_POR_FRAME) + 1)


def test_eco_a_veces_repite_el_dash_y_destruye(partida, monkeypatch):
    from juego.config import ECO_RETRASO, MEJORA_ECO
    dash_con_eco(partida, monkeypatch, MEJORA_ECO[0] - 0.01)     # salio la chance
    assert len(partida.ecos) == 1
    # Un enemigo destruible justo en el camino que hizo el dash
    camino = partida.ecos[0].camino
    enemigo = enemigo_en(partida, "divisor_chico", *camino[len(camino) // 2])
    enemigo.x, enemigo.y = enemigo.x + 15, enemigo.y + 15
    partida.nave.x, partida.nave.y = 600, 500                  # la nave ya esta lejos
    jugar(partida, ECO_RETRASO + len(camino) + 2)
    assert enemigo not in partida.enemigos
    assert partida.ecos == []


def test_eco_sin_suerte_no_deja_copia(partida, monkeypatch):
    from juego.config import MEJORA_ECO
    dash_con_eco(partida, monkeypatch, MEJORA_ECO[0] + 0.01)
    assert partida.ecos == []
