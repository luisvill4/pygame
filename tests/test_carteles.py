"""Carteles del juego: la cola de avisos (de a uno, los urgentes primero), que todo entre,
que las fichas no toquen el aviso de arriba, el logro, los momentos y la grilla de 2 px."""
import pygame

from juego import carteles, hud
from juego.anomalias import TIPOS_ANOMALIA
from juego.avisos import Aviso, ColaDeAvisos, SALIDA_RAPIDA
from juego.carteles import (medidas_pancarta, caja_pancarta, ANCHO_PANCARTA, ENTRA_PANCARTA, Y_FICHAS,
                            DURACION_FICHA, SALIDA_RAYA)
from juego.config import (ANCHO, ALTO, AMARILLO, ROJO, CIAN, PIXEL_ARTE, JEFE_CADA_NIVELES, CARTEL_JEFE,
                          CARTEL_RANGO, MS_POR_FRAME)
from juego.desafios import TIPOS_DESAFIO
from juego.logros import LOGROS
from tests.ayudas import jugar


def aviso(titulo="NIVEL 2", subtitulo="JEFE EN 3 NIVELES", duracion=1000):
    return Aviso("¡SUBISTE!", titulo, subtitulo, AMARILLO, duracion)


# ---------- La cola ----------

def test_los_avisos_salen_de_a_uno():
    cola = ColaDeAvisos()
    primero, segundo = aviso(), aviso("NIVEL 3")
    cola.agregar(primero, 0)
    cola.agregar(segundo, 300)
    assert cola.actual is primero               # el segundo espera su turno...
    cola.actualizar(999)
    assert cola.actual is primero
    cola.actualizar(1000)
    assert cola.actual is segundo and segundo.desde == 1000         # ...y sale cuando termina el primero


def test_un_aviso_urgente_pasa_primero():
    cola = ColaDeAvisos()
    nivel, despues = aviso(), aviso("NIVEL 3")
    urgente = Aviso("ALERTA", "¡OLEADA!", "", ROJO, 2000, alerta=True)
    cola.agregar(nivel, 0)
    cola.agregar(despues, 100)
    cola.agregar(urgente, 400, urgente=True)
    assert nivel.hasta == 400 + SALIDA_RAPIDA                    # el que se veia se va enseguida
    cola.actualizar(400 + SALIDA_RAPIDA)
    assert cola.actual is urgente                                # el urgente se colo adelante
    cola.actualizar(urgente.hasta)
    assert cola.actual is despues


def test_subir_de_nivel_avisa_cuanto_falta_para_el_jefe(partida):
    partida.subir_nivel()
    assert partida.avisos.actual.titulo == "NIVEL 2"
    assert partida.avisos.actual.subtitulo == "JEFE EN " + str(JEFE_CADA_NIVELES - 2) + " NIVELES"
    partida.avisos.vaciar()
    partida.nivel = JEFE_CADA_NIVELES - 2
    partida.subir_nivel()
    assert partida.avisos.actual.subtitulo == "PROXIMO NIVEL: ¡JEFE!"
    # En el nivel del jefe no hay aviso: llega su presentacion
    partida.subir_nivel()
    assert partida.jefe is not None and partida.avisos.actual is None


def test_la_oleada_no_espera_al_aviso_del_nivel(partida):
    partida.subir_nivel()
    partida.director.empezar_oleada()
    jugar(partida, int(SALIDA_RAPIDA / MS_POR_FRAME) + 2)
    assert partida.avisos.actual.titulo == "¡OLEADA!" and partida.avisos.actual.alerta


# ---------- Que todo entre ----------

def test_todo_entra_en_los_avisos():
    textos = [(clase.nombre, clase.pista) for clase in TIPOS_ANOMALIA.values()]
    textos += [("NIVEL 99", "PROXIMO NIVEL: ¡JEFE!"), ("¡OLEADA!", "AGUANTA SIN PERDER VIDAS"),
               ("¡OLEADA SUPERADA!", "+9999 PUNTOS Y UN POWER-UP"), ("¡NUEVO RECORD!", "SUPERASTE 999999")]
    minimo, maximo = ANCHO_PANCARTA
    for titulo, subtitulo in textos:
        ancho, alto, tamano = medidas_pancarta(aviso(titulo, subtitulo))
        assert minimo <= ancho <= maximo, titulo
        assert carteles.ancho_texto(titulo, tamano) <= ancho - 32, titulo
        assert carteles.ancho_texto(subtitulo, carteles.CHICA) <= ancho - 32, subtitulo


def test_el_aviso_del_nivel_entra_entre_las_dos_fichas():
    # El mas angosto (con su raya de afuera) no toca a las fichas: ellas no se corren
    ancho, _, _ = medidas_pancarta(aviso())
    assert ancho == ANCHO_PANCARTA[0]
    izquierda = carteles.CENTRO_X - ancho // 2 - SALIDA_RAYA
    assert izquierda > 20 + 304 + 8 and ANCHO - izquierda > 20 + 304 + 8


# ---------- Las fichas esquivan el aviso ----------

def _zona_de(funcion, *datos):
    capa = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
    funcion(capa, *datos)
    return capa.get_bounding_rect()


def test_las_fichas_bajan_si_el_aviso_las_tocaria(app):
    desafio = TIPOS_DESAFIO["cazador"]()
    sola = _zona_de(carteles.ficha_desafio, desafio, 1000)
    assert sola.top == Y_FICHAS - 8                              # (la pestañita asoma arriba)
    # Con una anomalia (aviso ancho) abierta del todo: la ficha queda debajo
    clase = TIPOS_ANOMALIA["asteroides"]
    ancho = Aviso("ANOMALIA", clase.nombre, clase.pista, CIAN, 3000)
    caja = caja_pancarta(ancho, 1000, 2000)
    assert caja.height > 0
    assert _zona_de(carteles.ficha_desafio, desafio, 1000, caja).top > caja.bottom
    # Con el aviso del nivel (angosto) no se corre
    angosto = caja_pancarta(aviso(), 1000, 2000)
    assert _zona_de(carteles.ficha_desafio, desafio, 1000, angosto).top == Y_FICHAS - 8


def test_la_ficha_baja_de_a_poco_mientras_el_aviso_se_abre(app):
    # Sin saltos: cada paso se corre poco
    desafio = TIPOS_DESAFIO["cazador"]()
    clase = TIPOS_ANOMALIA["asteroides"]
    ancho = Aviso("ANOMALIA", clase.nombre, clase.pista, CIAN, 3000)
    antes = None
    for paso in range(0, ENTRA_PANCARTA + 40, round(MS_POR_FRAME)):
        arriba = _zona_de(carteles.ficha_desafio, desafio, 1000, caja_pancarta(ancho, paso, 3000)).top
        if antes is not None:
            assert 0 <= arriba - antes <= 24
        antes = arriba


# ---------- Logro y momentos ----------

def test_el_logro_dice_que_nave_regala():
    primer_jefe = [logro for logro in LOGROS if logro.id == "primer_jefe"][0]
    mil = [logro for logro in LOGROS if logro.id == "mil"][0]
    assert carteles.nave_del_logro(primer_jefe) == ("CIAN", CIAN)
    assert carteles.nave_del_logro(mil) is None


def test_el_logro_se_abre_desde_el_trofeo(app):
    logro = LOGROS[0]
    chico = _zona_de(carteles.logro, logro, 200)
    abierto = _zona_de(carteles.logro, logro, 1000)
    assert 0 < chico.width < abierto.width                       # primero la insignia, despues todo
    assert abierto.bottom <= hud.zonas_hud()[1].top + 8          # no se mete en el HUD de abajo
    assert _zona_de(carteles.logro, logro, DURACION_FICHA - 10).width < abierto.width


def test_se_dibujan_los_momentos_del_cierre_del_sector(app, partida):
    partida.iniciar_jefe()
    partida.jefe_vencido()
    assert partida.ultimo_jefe is not None and partida.bonus_jefe > 0
    pantalla = pygame.Surface((ANCHO, ALTO))
    for _ in range(int((CARTEL_JEFE + CARTEL_RANGO) / MS_POR_FRAME) + 60):
        jugar(partida)
        hud.dibujar(pantalla, partida)                # jefe vencido, rango y sector nuevo, sin errores


# ---------- La grilla de pixeles de arte ----------

def test_las_piezas_de_los_carteles_calzan_en_la_grilla():
    pantalla = pygame.Surface((240, 120))
    carteles.cinta(pantalla, pygame.Rect(20, 20, 120, 12), 37)
    carteles.rayitas(pantalla, 151, 63, ROJO)
    carteles.raya(pantalla, 40, 200, 90, AMARILLO)
    carteles.franja(pantalla, 101, 13, CIAN)
    ancho, alto = pantalla.get_size()
    for y in range(alto):
        for x in range(1, ancho):
            if pantalla.get_at((x, y)) != pantalla.get_at((x - 1, y)):
                assert x % PIXEL_ARTE == 0, (x, y)
    for x in range(ancho):
        for y in range(1, alto):
            if pantalla.get_at((x, y)) != pantalla.get_at((x, y - 1)):
                assert y % PIXEL_ARTE == 0, (x, y)
