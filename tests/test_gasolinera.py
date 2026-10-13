"""Gasolinera: los creditos, la tienda (precios y compras) y la escena."""
import math

import pygame
import pytest

from juego import recursos
from juego.config import (PRECIO_CARTA, PRECIO_POR_NIVEL, PRECIO_RARA, PRECIO_POR_SECTOR, PRECIO_SORTEAR,
                          DIFICULTADES, CREDITOS_POR_MONEDA, ANCHO)
from juego import dibujo
from juego.dibujo import MINI, CHICA
from juego.mejoras import TIPOS_MEJORA
from juego.tienda import Tienda, Carta, SERVICIOS, redondear
from juego.escenas.gasolinera import Gasolinera, PASOS_SIN_ELEGIR, ANCHO_CARTA, ANCHO_DESCRIPCION
from juego.escenas.juego import Juego
from tests.ayudas import jugar, avanzar, tecla, empezar_partida


def recoger_moneda(partida):
    partida.moneda.x, partida.moneda.y = partida.nave.x + 15, partida.nave.y + 15
    jugar(partida)


def carta(tienda, tipo):
    # Pone en el mostrador la carta que se quiere probar
    nueva = Carta(TIPOS_MEJORA[tipo])
    tienda.cartas = [nueva]
    return nueva


# ---------- Creditos ----------


def test_las_monedas_dan_creditos_con_el_combo(partida):
    recoger_moneda(partida)
    assert partida.creditos == CREDITOS_POR_MONEDA
    partida.combo = 8                               # la proxima es la 9: combo x4
    recoger_moneda(partida)
    assert partida.creditos == CREDITOS_POR_MONEDA * (1 + 4)


def test_los_creditos_no_son_puntos(partida):
    partida.activar("doble", 5000)                  # DOBLE duplica los puntos, no los creditos
    recoger_moneda(partida)
    assert partida.puntaje == 2
    assert partida.creditos == CREDITOS_POR_MONEDA
    puntaje = partida.puntaje
    assert partida.gastar_creditos(1)
    assert partida.puntaje == puntaje               # gastar no baja el puntaje


def test_gastar_solo_si_alcanza(partida):
    partida.creditos = 30
    assert not partida.gastar_creditos(31)
    assert partida.creditos == 30
    assert partida.gastar_creditos(30)
    assert partida.creditos == 0


# ---------- La tienda ----------


def test_comprar_una_carta(partida):
    tienda = Tienda(partida)
    motor = carta(tienda, "motor")
    partida.creditos = 100
    assert tienda.comprar(motor)
    assert partida.mejora("motor") == 1
    assert partida.creditos == 100 - PRECIO_CARTA
    assert motor.vendido
    assert not tienda.comprar(motor)                # una sola vez por parada
    assert partida.mejora("motor") == 1


def test_si_no_alcanza_no_se_compra(partida):
    tienda = Tienda(partida)
    motor = carta(tienda, "motor")
    partida.creditos = PRECIO_CARTA - 1
    assert not tienda.comprar(motor)
    assert partida.mejora("motor") == 0 and partida.creditos == PRECIO_CARTA - 1


def test_el_precio_sube_con_el_nivel_la_rareza_y_el_sector(partida):
    tienda = Tienda(partida)
    motor = carta(tienda, "motor")
    assert motor.precio(tienda) == PRECIO_CARTA
    partida.sumar_mejora("motor")
    assert motor.precio(tienda) == PRECIO_CARTA + PRECIO_POR_NIVEL
    fenix = carta(tienda, "fenix")                  # rara
    assert fenix.precio(tienda) == redondear(PRECIO_CARTA * PRECIO_RARA)
    partida.director.numero_sector = 4              # la parada despues del sector 3
    assert fenix.precio(tienda) == redondear(PRECIO_CARTA * PRECIO_RARA * (1 + 2 * PRECIO_POR_SECTOR))


def test_sortear_cambia_las_cartas_y_cada_vez_es_mas_caro(partida):
    partida.reglas = DIFICULTADES["NORMAL"]
    tienda = Tienda(partida)
    sortear = next(s for s in tienda.servicios if s.tipo == "sortear")
    partida.creditos = 1000
    viejas = tienda.cartas
    assert tienda.comprar(sortear)
    assert tienda.cartas is not viejas and len(tienda.cartas) == 3
    assert partida.creditos == 1000 - PRECIO_SORTEAR
    assert sortear.precio(tienda) == 2 * PRECIO_SORTEAR
    assert tienda.comprar(sortear)                  # se puede repetir


@pytest.mark.parametrize("dificultad, servicios", [
    ("FACIL", ["sortear", "escudo", "reparar"]),
    ("NORMAL", ["sortear", "escudo"]),
    ("DIFICIL", ["sortear"]),
    ("PESADILLA", []),
])
def test_los_servicios_dependen_de_la_dificultad(partida, dificultad, servicios):
    partida.reglas = DIFICULTADES[dificultad]
    tienda = Tienda(partida)
    assert [s.tipo for s in tienda.servicios] == servicios
    assert len(tienda.cartas) == 3


def test_reparar_solo_si_falta_una_vida(partida):
    partida.reglas = DIFICULTADES["FACIL"]
    tienda = Tienda(partida)
    reparar = next(s for s in tienda.servicios if s.tipo == "reparar")
    partida.creditos = 1000
    assert not tienda.comprar(reparar)              # vidas llenas: no hace falta
    partida.vidas -= 1
    assert tienda.comprar(reparar)
    assert partida.vidas == partida.vidas_max


def test_el_escudo_del_viaje_dura_hasta_el_golpe(partida):
    tienda = Tienda(partida)
    tienda.servicios = [SERVICIOS["escudo"]()]
    partida.creditos = 1000
    assert tienda.comprar(tienda.servicios[0])
    assert partida.restante("escudo") == math.inf
    vidas = partida.vidas
    partida.danar_jugador(0, 0)
    assert partida.vidas == vidas and not partida.activo("escudo")


# ---------- La escena ----------


def test_despues_del_jefe_se_para_en_la_gasolinera_y_se_vuelve_al_juego(app):
    avanzar(app)
    partida = empezar_partida(app)
    juego = app.escena
    partida.nave.invulnerable_hasta = math.inf
    partida.director.gasolinera = True
    avanzar(app)
    assert isinstance(app.escena, Gasolinera)
    tiempo = partida.tiempo
    gasolinera = app.escena
    partida.creditos = 1000
    avanzar(app, PASOS_SIN_ELEGIR)
    elegida = gasolinera.elegido_actual()
    tecla(pygame.K_RETURN)
    avanzar(app)
    assert partida.mejora(elegida.tipo) == 1
    assert partida.creditos < 1000
    tecla(pygame.K_ESCAPE)
    avanzar(app)
    assert app.escena is juego
    assert not partida.director.gasolinera
    assert partida.tiempo == tiempo                 # el juego estuvo quieto mientras se compraba


def test_todo_entra_en_las_cartas_y_en_el_cartel(app, partida):
    partida.reglas = DIFICULTADES["FACIL"]          # la que mas vende: 6 cosas
    gasolinera = Gasolinera(app, Juego(app, partida))
    articulos = [Carta(mejora) for mejora in TIPOS_MEJORA.values()] + gasolinera.tienda.servicios
    for articulo in articulos:
        # El nombre entra en la carta (con letra MINI si no entra en CHICA)
        assert recursos.fuente(MINI).size(articulo.nombre)[0] <= ANCHO_CARTA - 16, articulo.nombre
        # La descripcion entra en dos renglones del panel de detalle
        lineas = dibujo.partir_lineas(" ".join(articulo.descripcion), CHICA, ANCHO_DESCRIPCION)
        assert len(lineas) <= 2, articulo.nombre
    # Las 6 entran en la pantalla y se dibujan sin errores
    assert gasolinera._x_carta(0) >= 20
    assert gasolinera._x_carta(len(gasolinera.tienda.articulos()) - 1) + ANCHO_CARTA <= ANCHO - 20
    gasolinera.pasos = 200
    for i in range(len(gasolinera.tienda.articulos())):
        gasolinera.elegido = i
        gasolinera.dibujar(app.pantalla)
