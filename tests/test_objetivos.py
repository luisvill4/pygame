"""Objetivos de los tramos: que cuenta cada uno, que el guion se pueda cumplir y como se pasa de tramo."""
import math

import pygame

from juego import hud
from juego.config import (ANCHO, ALTO, JEFE_CADA_NIVELES, MS_POR_FRAME, AVISO_ESCUADRON, ENTRADA_ESCUADRON,
                          OBJETIVO_PUNTOS, PACIENCIA_OBJETIVO, PERMANENCIA_MINIMA, SECTORES)
from juego.desafios import TIPOS_DESAFIO
from juego.enemigos import TIPOS_ENEMIGO, crear_enemigo
from juego.guiones import GUION_ARCADE
from juego.objetivos import TIPOS_OBJETIVO, crear_objetivo
from tests.ayudas import jugar

PASOS_ENTRADA = int((AVISO_ESCUADRON + ENTRADA_ESCUADRON + 600) / MS_POR_FRAME)


def recoger_moneda(partida):
    partida.moneda.x, partida.moneda.y = partida.nave.x + 15, partida.nave.y + 15
    jugar(partida)


def con_escuadrones(partida):
    partida.director.con_escuadrones = True
    partida.nave.invulnerable_hasta = math.inf
    return partida.director


# ---------- El guion ----------

def test_cada_tramo_tiene_un_objetivo_que_se_puede_cumplir():
    # Si pide romper divisores, el tramo trae divisores (si no, no se podria pasar nunca)
    for sector in GUION_ARCADE:
        for tramo in sector:
            tipos = {tipo for tipo, _, _ in tramo["escuadrones"]}
            objetivo = crear_objetivo(tramo["objetivo"])
            assert objetivo.tipo in TIPOS_OBJETIVO
            if objetivo.tipo == "romper":
                assert objetivo.enemigo in tipos and TIPOS_ENEMIGO[objetivo.enemigo].destruible
            elif objetivo.tipo == "interceptar":
                assert "embestidor" in tipos
            elif objetivo.tipo == "perfectos":
                assert any(TIPOS_ENEMIGO[tipo].destruible for tipo in tipos), tramo["nombre"]
            assert (objetivo.tipo == "asedio") == tramo.get("asedio", False)


def test_los_objetivos_entran_en_el_cartel_y_en_el_hud():
    # El cartel tiene lugar para 32 letras; el renglon del HUD, para 15 (aun en la segunda vuelta)
    for sector in GUION_ARCADE:
        for tramo in sector:
            objetivo = crear_objetivo(tramo["objetivo"], 1.5)
            objetivo.progreso = objetivo.meta
            assert len(objetivo.texto()) <= 32, objetivo.texto()
            assert len(objetivo.etiqueta()) <= 15, objetivo.etiqueta()


def test_en_la_segunda_vuelta_se_pide_mas(partida):
    director = partida.director
    meta = director.objetivo.meta
    director.numero_sector = len(SECTORES) + 1
    director.empezar_tramo()
    assert director.objetivo.meta > meta


# ---------- Que cuenta cada uno ----------

def test_juntar_monedas(partida):
    director = partida.director
    assert director.objetivo.tipo == "monedas"          # PATRULLA
    recoger_moneda(partida)
    recoger_moneda(partida)
    assert director.objetivo.progreso == 2
    assert director.tiempo_avance == partida.tiempo     # (el HUD destella)


def test_romper_cuenta_solo_su_enemigo(partida):
    director = partida.director
    director.objetivo = crear_objetivo(("romper", 3, "divisor"))
    for tipo in ("divisor_chico", "perseguidor"):
        otro = crear_enemigo(tipo, partida)
        partida.enemigos.append(otro)
        partida.destruir_con_dash(otro)
    assert director.objetivo.progreso == 0
    divisor = crear_enemigo("divisor", partida)
    partida.enemigos.append(divisor)
    partida.destruir_con_dash(divisor)
    assert director.objetivo.progreso == 1


def test_romper_congelado_tambien_cuenta(partida):
    director = partida.director
    director.objetivo = crear_objetivo(("romper", 3, "ladron"))
    ladron = crear_enemigo("ladron", partida)
    ladron.aparece_en = 0
    ladron.x, ladron.y = partida.nave.x + 5, partida.nave.y + 5
    partida.enemigos.append(ladron)
    partida.activar("hielo", 5000)
    jugar(partida)
    assert director.objetivo.progreso == 1


def test_interceptar_y_perfectos(partida):
    director = partida.director
    director.objetivo = crear_objetivo(("interceptar", 2))
    director.al_interceptar()
    assert director.objetivo.progreso == 1
    director.objetivo = crear_objetivo(("perfectos", 2))
    partida._dash_perfecto(0, 0)
    assert director.objetivo.progreso == 1


def test_el_asedio_se_cumple_al_terminar(partida):
    director = con_escuadrones(partida)
    partida.nivel = JEFE_CADA_NIVELES - 2
    partida.subir_nivel()
    assert director.objetivo.tipo == "asedio"
    director.empezar_asedio()
    assert not director.objetivo.cumplido()
    director.terminar_asedio(superado=True)
    assert director.objetivo.cumplido()


# ---------- Como se pasa de tramo ----------

def test_cumplido_el_objetivo_festeja_despide_y_pasa_de_tramo(partida):
    director = con_escuadrones(partida)
    director.proximo_escuadron = math.inf
    viejo = director.lanzar_escuadron(("perseguidor", 2, "pinza"))
    jugar(partida, int(PERMANENCIA_MINIMA / MS_POR_FRAME) + PASOS_ENTRADA)     # ya estuvo un buen rato
    puntaje = partida.puntaje
    director.cumplir_objetivo()
    jugar(partida, 2)
    assert partida.puntaje == puntaje + OBJETIVO_PUNTOS
    assert all(enemigo.saliendo for enemigo in viejo.miembros)          # el que ya peleo se va...
    assert partida.nivel == 1                                           # ...y el tramo espera
    for _ in range(60 * 5):
        jugar(partida)
        if partida.nivel == 2:
            break
    assert partida.nivel == 2 and director.numero_tramo == 2            # zona despejada: tramo 2
    assert not director.objetivo.cumplido()                             # con su objetivo nuevo


def test_el_que_acaba_de_llegar_se_queda_un_rato_aunque_termine_el_tramo(partida):
    # Pedido del usuario: "apenas llegan se van". Ahora pelea al menos PERMANENCIA_MINIMA ms
    director = con_escuadrones(partida)
    director.proximo_escuadron = math.inf
    recien = director.lanzar_escuadron(("perseguidor", 2, "pinza"))
    jugar(partida, PASOS_ENTRADA)
    director.cumplir_objetivo()
    jugar(partida, int((PERMANENCIA_MINIMA - 1500) / MS_POR_FRAME))
    assert not any(enemigo.saliendo for enemigo in recien.miembros) and partida.nivel == 1
    for _ in range(60 * 6):
        jugar(partida)
        if partida.nivel == 2:
            break
    assert partida.nivel == 2


def test_cumplido_el_objetivo_no_llegan_mas_escuadrones(partida):
    director = con_escuadrones(partida)
    director.objetivo.progreso = director.objetivo.meta
    director.objetivo_festejado = True
    escuadron = director.lanzar_escuadron(("perseguidor", 1, "flanco"))     # (uno que ya estaba)
    director.proximo_escuadron = 0
    jugar(partida)
    assert director.escuadrones == [escuadron]


def test_los_escuadrones_se_quedan_su_turno_mientras_avanzas(partida):
    # Pedido del usuario: antes, al llenarse la barra, los enemigos se iban apenas llegaban
    director = con_escuadrones(partida)
    director.proximo_escuadron = math.inf
    escuadron = director.lanzar_escuadron(("perseguidor", 2, "pinza"))
    turno = escuadron.retirada_en
    for _ in range(director.objetivo.meta - 1):
        recoger_moneda(partida)
    assert escuadron.retirada_en == turno and not escuadron.se_retiro


def test_lo_que_pasa_con_el_jefe_no_cuenta(partida):
    director = partida.director
    partida.nivel = JEFE_CADA_NIVELES - 1
    partida.subir_nivel()
    assert partida.jefe is not None and director.objetivo is None
    recoger_moneda(partida)                 # (no se rompe nada)


def test_un_desafio_cumplido_cuando_llega_el_jefe_no_saltea_su_nivel(partida):
    # Bug viejo: "SIN DASH" se cumple al llegar el jefe y su premio hacia saltear un nivel
    director = partida.director
    director.desafio = TIPOS_DESAFIO["sin_dash"]()
    partida.nivel = JEFE_CADA_NIVELES - 2
    partida.subir_nivel()                   # el tramo 4 (el asedio)
    director.cumplir_objetivo()
    jugar(partida, 2)
    assert partida.jefe is not None and partida.nivel == JEFE_CADA_NIVELES
    assert director.desafio.estado == "cumplido"


def test_el_objetivo_se_dibuja_en_la_ruta(partida):
    pantalla = pygame.Surface((ANCHO, ALTO))
    partida.director.objetivo.progreso = partida.director.objetivo.meta // 2
    hud.dibujar(pantalla, partida)
    # Algun bloque amarillo en el camino del tramo actual (la ruta, abajo a la derecha)
    inicio = ANCHO - 20 - 4 * hud.RUTA_PASO - 14
    camino = pygame.Rect(inicio + 16, hud.RUTA_Y - 2, hud.RUTA_PASO - 20, 4)
    colores = {tuple(pantalla.get_at((x, camino.centery)))[:3] for x in range(camino.left, camino.right)}
    assert any(color[0] > 200 and color[1] > 150 and color[2] < 100 for color in colores)


def test_uno_que_venia_entrando_pega_la_vuelta(partida):
    # Si el tramo termina mientras un escuadron entra, no desaparece de golpe: se va volando
    director = con_escuadrones(partida)
    escuadron = director.lanzar_escuadron(("perseguidor", 1, "flanco"))
    jugar(partida, int((AVISO_ESCUADRON + ENTRADA_ESCUADRON / 2) / MS_POR_FRAME))
    enemigo = escuadron.miembros[0]
    assert enemigo.entrada is not None
    enemigo.retirarse(partida)
    assert enemigo in partida.enemigos and enemigo.saliendo and enemigo.entrada is None


def test_si_no_se_cumple_a_tiempo_el_paso_se_abre_sin_premio(partida):
    # Nadie se queda trabado para siempre (ej: si todavia no sabe frenar embestidas)
    director = con_escuadrones(partida)
    director.proximo_escuadron = math.inf
    puntaje = partida.puntaje
    jugar(partida, int(PACIENCIA_OBJETIVO / MS_POR_FRAME) - 5)
    assert partida.nivel == 1
    jugar(partida, 10)
    assert partida.nivel == 2 and partida.puntaje == puntaje
