"""
Kit de interfaz: las piezas con las que se arman TODAS las pantallas (menus, tienda,
pausa, resultados). Usarlas en vez de dibujar a mano hace que el juego se vea como una
sola cosa: mismos paneles, mismos botones, misma forma de marcar lo elegido.

    panel(...)      recuadro con esquinas de visor y un encabezado con el titulo
    titulo(...)     el titulo grande de una pantalla, con relieve y una raya de color
    renglon(...)    un renglon centrado de varios colores
    menu(...)       lista vertical: la nave es el cursor y se desliza (ver Cursor)
    ayudas(...)     la barra de abajo con los botones del control que se esta usando
    boton(...)      un boton del mando (A, B, LB, la cruceta...) o una tecla, en pixel art
    carta(...)      una carta de mejora (la usan el Taller y la Gasolinera)
    pixelado(...)   la imagen del juego pixelada (fondo de la Pausa y del Taller)
    Cursor          un numero que se acerca de a poco a su objetivo (animaciones suaves)

Todo se dibuja con codigo, en la cuadricula retro: nada de imagenes nuevas.
"""
import math

import pygame

from juego import dibujo, recursos, nave
from juego.dibujo import texto, MINI, CHICA, MEDIA, TITULO
from juego.config import (FONDO, BLANCO, GRIS, MAGENTA, FUEGO, TEXTO, TEXTO_SUAVE, TEXTO_APAGADO, RESALTADO,
                          LINEA_APAGADA, FILA_ELEGIDA, PANEL_FONDO, COLORES_BOTON)

ALTO_AYUDAS = 40            # la barra de ayudas de abajo


def mezclar(color, otro, cuanto):
    # Un color entre 'color' (cuanto = 0) y 'otro' (cuanto = 1)
    return tuple(round(a + (b - a) * cuanto) for a, b in zip(color, otro))


class Cursor:
    # Un valor que se acerca de a poco a su objetivo: lo elegido se desliza en vez de saltar.
    # avanzar() va en actualizar() (60 veces por segundo), asi se mueve igual a cualquier FPS
    def __init__(self, valor=0, rapidez=0.3):
        self.valor = self.objetivo = valor
        self.rapidez = rapidez

    def ir_a(self, objetivo):
        self.objetivo = objetivo

    def saltar_a(self, objetivo):
        self.valor = self.objetivo = objetivo

    def avanzar(self):
        self.valor += (self.objetivo - self.valor) * self.rapidez
        if abs(self.objetivo - self.valor) < 0.01:
            self.valor = self.objetivo


# ---------- Paneles y titulos ----------

def panel(pantalla, rect, color, titulo=None, alfa=255):
    # Recuadro de la interfaz: fondo oscuro, borde fino del color apagado y esquinas
    # brillantes (como el visor de una nave). Con 'titulo', una franja arriba con el nombre
    # y unas rayitas de decoracion. Devuelve el rectangulo de adentro, para el contenido
    if alfa < 255:
        capa = pygame.Surface(rect.size)
        capa.fill(PANEL_FONDO)
        capa.set_alpha(alfa)
        pantalla.blit(capa, rect.topleft)
    else:
        pantalla.fill(PANEL_FONDO, rect)
    pygame.draw.rect(pantalla, mezclar(color, FONDO, 0.6), rect, 2)
    esquinas(pantalla, rect, color)
    if not titulo:
        return rect.inflate(-32, -32)
    franja = pygame.Rect(rect.left + 2, rect.top + 2, rect.width - 4, 30)
    pantalla.fill(mezclar(color, FONDO, 0.82), franja)
    pantalla.fill(color, (franja.left, franja.bottom - 2, franja.width, 2))
    texto(pantalla, titulo, CHICA, color, franja.left + 18, franja.centery, alinear="izquierda")
    # Rayitas inclinadas al final de la franja (decoracion de HUD)
    for i in range(4):
        x = franja.right - 22 - i * 12
        pygame.draw.polygon(pantalla, mezclar(color, FONDO, 0.45 + i * 0.12),
                            [(x, franja.top + 7), (x + 6, franja.top + 7), (x, franja.bottom - 7),
                             (x - 6, franja.bottom - 7)])
    return pygame.Rect(rect.left + 16, franja.bottom + 14, rect.width - 32, rect.bottom - franja.bottom - 28)


def esquinas(pantalla, rect, color, largo=14, grueso=3):
    # Escuadras en las cuatro esquinas, un poco por afuera del borde
    afuera = rect.inflate(4, 4)
    for x, y, dx, dy in ((afuera.left, afuera.top, 1, 1), (afuera.right, afuera.top, -1, 1),
                         (afuera.left, afuera.bottom, 1, -1), (afuera.right, afuera.bottom, -1, -1)):
        horizontal = pygame.Rect(0, 0, largo, grueso)
        vertical = pygame.Rect(0, 0, grueso, largo)
        horizontal.x = x if dx > 0 else x - largo
        horizontal.y = y if dy > 0 else y - grueso
        vertical.x = x if dx > 0 else x - grueso
        vertical.y = y if dy > 0 else y - largo
        pantalla.fill(color, horizontal)
        pantalla.fill(color, vertical)


def titulo(pantalla, mensaje, x, y, color, relieve, alinear="izquierda", tamano=TITULO):
    # El titulo de una pantalla: letras con relieve y debajo una raya de su color que sigue
    # en una linea apagada (asi el titulo "apoya" sobre algo)
    dibujo.texto_3d(pantalla, mensaje, tamano, color, relieve, y, 4, None, x, alinear)
    ancho = recursos.fuente(tamano).size(mensaje)[0]
    izquierda = x if alinear == "izquierda" else x - ancho // 2
    raya_y = y + tamano // 2 + 12
    pantalla.fill(color, (izquierda, raya_y, min(ancho, 120), 4))
    pantalla.fill(mezclar(color, FONDO, 0.7), (izquierda + min(ancho, 120) + 6, raya_y + 1, ancho // 2, 2))


def renglon(pantalla, partes, tamano, centro_x, y):
    # Un renglon centrado hecho de partes de distinto color: [("SECTOR 1", CIAN), ...]
    fuente = recursos.fuente(tamano)
    x = centro_x - sum(fuente.size(mensaje)[0] for mensaje, _ in partes) // 2
    for mensaje, color in partes:
        texto(pantalla, mensaje, tamano, color, x, y, alinear="izquierda")
        x += fuente.size(mensaje)[0]


def separador(pantalla, x, y, ancho, color=LINEA_APAGADA):
    # Una linea fina con un cuadradito en cada punta
    pantalla.fill(color, (x, y, ancho, 2))
    pantalla.fill(color, (x - 2, y - 2, 6, 6))
    pantalla.fill(color, (x + ancho - 4, y - 2, 6, 6))


# ---------- Menu con cursor ----------

_naves_cursor = {}          # (color de la nave) -> la nave chica mirando a la derecha


def menu(pantalla, opciones, cursor, x, y, ancho, alto_fila=48, tamano=MEDIA, color=RESALTADO, apagadas=(),
         iconos=None):
    # Lista vertical. La elegida tiene una franja de fondo con una raya de color a la
    # izquierda y la nave como cursor; franja y nave se deslizan (cursor.valor) hasta la
    # fila elegida (cursor.objetivo). Las filas cercanas al cursor se corren un poco.
    # 'iconos': un pixel art de 7x7 por opcion, a la izquierda del nombre
    elegida = round(cursor.objetivo)
    centro_y = y + cursor.valor * alto_fila
    franja = pygame.Rect(x - 16, round(centro_y) - alto_fila // 2 + 4, ancho, alto_fila - 8)
    pantalla.fill(FILA_ELEGIDA, franja)
    pantalla.fill(color, (franja.left, franja.top, 4, franja.height))
    # La franja se apaga hacia la derecha en escalones (sin transparencias)
    for i, cuanto in enumerate((0.35, 0.65)):
        pantalla.fill(mezclar(FILA_ELEGIDA, PANEL_FONDO, cuanto), (franja.right + i * 8, franja.top, 8, franja.height))
    _nave_cursor(pantalla, x - 46, round(centro_y))
    for i, nombre in enumerate(opciones):
        cerca = max(0.0, 1 - abs(cursor.valor - i))
        corrido = round(cerca * 6) * 2
        if i == elegida:
            color_texto = color
        elif i in apagadas:
            color_texto = TEXTO_APAGADO
        else:
            color_texto = TEXTO_SUAVE
        texto_x = x + corrido
        if iconos:
            dibujo.pixel_art(pantalla, iconos[i], texto_x + 10, y + i * alto_fila, color_texto, 3)
            texto_x += 34
        texto(pantalla, nombre, tamano, color_texto, texto_x, y + i * alto_fila, alinear="izquierda")


def _nave_cursor(pantalla, x, y):
    # La nave del jugador, chica y mirando a la derecha, con el fuego del motor titilando
    icono = nave.imagen("icono")
    clave = id(icono)
    if clave not in _naves_cursor:
        _naves_cursor.clear()
        _naves_cursor[clave] = pygame.transform.rotate(icono, -90)
    imagen = _naves_cursor[clave]
    pantalla.blit(imagen, imagen.get_rect(center=(x, y)))
    llama = 6 if dibujo.parpadeo(80) else 4
    pantalla.fill(FUEGO[3], (x - 18, y - 2, 4, 4))
    pantalla.fill(FUEGO[1], (x - 18 - llama, y - 1, llama, 2))


# ---------- Botones y ayudas ----------

CIRCULO = [
    "..XXXXX..",
    ".XXXXXXX.",
    "XXXXXXXXX",
    "XXXXXXXXX",
    "XXXXXXXXX",
    "XXXXXXXXX",
    "XXXXXXXXX",
    ".XXXXXXX.",
    "..XXXXX..",
]
CRUZ = [
    "...XXX...",
    "...XXX...",
    "...XXX...",
    "XXXXXXXXX",
    "XXXXXXXXX",
    "XXXXXXXXX",
    "...XXX...",
    "...XXX...",
    "...XXX...",
]
GRIS_BOTON = (84, 90, 130)
GRIS_OSCURO = (34, 36, 64)

# Que botones o teclas se muestran para cada cosa: (con teclado, con mando)
GLIFOS = {
    "aceptar": (["ENTER"], ["A"]),
    "volver": (["ESC"], ["B"]),
    "elegir": (["ARRIBA", "ABAJO"], ["CRUZ_V"]),
    "cambiar": (["IZQ", "DER"], ["CRUZ_H"]),
    "pestanas": (["Q", "E"], ["LB", "RB"]),
    "pausa": (["P"], ["MENU"]),
    "opciones": (["O"], ["VISTA"]),
    "dash": (["ESPACIO"], ["X"]),
    "mover": (["FLECHAS"], ["STICK"]),
    "desarrollador": (["F1"], ["F1"]),
}


def boton(pantalla, glifo, x, y):
    # Dibuja un boton del mando o una tecla con su borde izquierdo en x y centrado en y.
    # Devuelve cuanto ocupa de ancho
    if glifo in COLORES_BOTON:
        return _boton_redondo(pantalla, x, y, COLORES_BOTON[glifo], glifo)
    if glifo in ("LB", "RB"):
        cuerpo = pygame.Rect(x, y - 11, 44, 22)
        pantalla.fill(GRIS_OSCURO, cuerpo.move(0, 3))
        pantalla.fill(GRIS_BOTON, cuerpo)
        pantalla.fill(mezclar(GRIS_BOTON, BLANCO, 0.3), (cuerpo.left + 2, cuerpo.top, cuerpo.width - 4, 2))
        texto(pantalla, glifo, CHICA, BLANCO, cuerpo.centerx + 1, y, sombra=None)
        return cuerpo.width
    if glifo in ("MENU", "VISTA", "STICK"):
        ancho = _boton_redondo(pantalla, x, y, GRIS_BOTON, "")
        centro_x = x + ancho // 2
        if glifo == "MENU":
            for fila in (-5, -1, 3):
                pantalla.fill(BLANCO, (centro_x - 6, y + fila, 12, 2))
        elif glifo == "VISTA":
            pygame.draw.rect(pantalla, BLANCO, (centro_x - 6, y - 6, 8, 8), 2)
            pygame.draw.rect(pantalla, BLANCO, (centro_x - 2, y - 2, 8, 8), 2)
        else:
            texto(pantalla, "L", CHICA, BLANCO, centro_x + 1, y + 1, sombra=None)
        return ancho
    if glifo in ("CRUZ_V", "CRUZ_H"):
        izquierda, arriba = x, y - 13
        dibujo.pixel_art(pantalla, CRUZ, x + 13, y + 3, GRIS_OSCURO, 3)
        dibujo.pixel_art(pantalla, CRUZ, x + 13, y, GRIS_BOTON, 3)
        if glifo == "CRUZ_V":
            pantalla.fill(BLANCO, (izquierda + 9, arriba + 1, 9, 7))
            pantalla.fill(BLANCO, (izquierda + 9, arriba + 19, 9, 7))
        else:
            pantalla.fill(BLANCO, (izquierda + 1, arriba + 9, 7, 9))
            pantalla.fill(BLANCO, (izquierda + 19, arriba + 9, 7, 9))
        return 27
    return _tecla(pantalla, glifo, x, y)


def _boton_redondo(pantalla, x, y, color, letra):
    # Boton redondo de 27 px con relieve (una sombra mas oscura abajo) y su letra
    dibujo.pixel_art(pantalla, CIRCULO, x + 13, y + 2, mezclar(color, FONDO, 0.55), 3)
    dibujo.pixel_art(pantalla, CIRCULO, x + 13, y - 1, color, 3)
    if letra:
        texto(pantalla, letra, CHICA, FONDO, x + 14, y, sombra=None)
    return 27


FLECHAS_TECLA = {"ARRIBA": (0, -1), "ABAJO": (0, 1), "IZQ": (-1, 0), "DER": (1, 0)}


def _tecla(pantalla, nombre, x, y):
    # Una tecla del teclado: con su borde, un poco de relieve y el nombre (o una flecha)
    if nombre in FLECHAS_TECLA:
        ancho = 26
    else:
        ancho = max(26, recursos.fuente(CHICA).size(nombre)[0] + 14)
    tecla = pygame.Rect(x, y - 12, ancho, 24)
    pantalla.fill(GRIS_OSCURO, tecla.move(0, 3))
    pantalla.fill((40, 44, 82), tecla)
    pygame.draw.rect(pantalla, (150, 156, 196), tecla, 2)
    if nombre in FLECHAS_TECLA:
        dx, dy = FLECHAS_TECLA[nombre]
        cx, cy = tecla.center
        if dx:
            puntos = [(cx + 5 * dx, cy), (cx - 4 * dx, cy - 6), (cx - 4 * dx, cy + 6)]
        else:
            puntos = [(cx, cy + 5 * dy), (cx - 6, cy - 4 * dy), (cx + 6, cy - 4 * dy)]
        pygame.draw.polygon(pantalla, BLANCO, puntos)
    else:
        texto(pantalla, nombre, CHICA, BLANCO, tecla.centerx + 1, y + 1, sombra=None)
    return ancho


def ayudas(pantalla, entrada, pares, extra=None):
    # La barra de abajo: que hace cada boton, con los del control que se esta usando
    # (mando o teclado, segun lo ultimo que se toco). 'pares' = [("aceptar", "COMPRAR")...],
    # de izquierda a derecha, alineados a la derecha. 'extra': un texto suave a la izquierda
    # (si no entra sin pisar los botones, no se dibuja)
    ancho, alto = pantalla.get_size()
    franja = pygame.Rect(0, alto - ALTO_AYUDAS, ancho, ALTO_AYUDAS)
    capa = pygame.Surface(franja.size)
    capa.fill(FONDO)
    capa.set_alpha(215)
    pantalla.blit(capa, franja.topleft)
    pantalla.fill(LINEA_APAGADA, (0, franja.top, ancho, 2))
    con_mando = entrada.usando_mando()
    medidas = []
    for accion, etiqueta in pares:
        glifos = GLIFOS[accion][1 if con_mando else 0]
        ancho_glifos = sum(_ancho_glifo(g) for g in glifos) + 6 * (len(glifos) - 1)
        medidas.append((glifos, ancho_glifos, etiqueta, recursos.fuente(CHICA).size(etiqueta)[0]))
    total = sum(g + 10 + t for _, g, _, t in medidas) + 32 * (len(medidas) - 1)
    x = ancho - 28 - total
    y = franja.centery + 1
    if extra and 28 + recursos.fuente(CHICA).size(extra)[0] + 32 <= x:
        texto(pantalla, extra, CHICA, TEXTO_SUAVE, 28, y + 1, alinear="izquierda")
    for glifos, ancho_glifos, etiqueta, ancho_texto in medidas:
        for glifo in glifos:
            x += boton(pantalla, glifo, x, y) + 6
        x += 4
        texto(pantalla, etiqueta, CHICA, TEXTO, x, y + 1, alinear="izquierda")
        x += ancho_texto + 32


def pestanas(pantalla, rect, entrada, nombres, actual, color, color_fondo, enfocada=False):
    # Fila de pestañas con el boton para cambiar en cada punta (LB/RB en el mando, Q/E en
    # el teclado), como en las consolas: asi se ve sin leer ninguna ayuda
    izquierdo, derecho = GLIFOS["pestanas"][1 if entrada.usando_mando() else 0]
    ancho_glifo = _ancho_glifo(izquierdo)
    boton(pantalla, izquierdo, rect.left, rect.centery)
    boton(pantalla, derecho, rect.right - ancho_glifo, rect.centery)
    adentro = pygame.Rect(rect.left + ancho_glifo + 8, rect.top, rect.width - 2 * (ancho_glifo + 8), rect.height)
    dibujo.pestanas(pantalla, adentro, nombres, actual, color, color_fondo, enfocada)
    return adentro


def _ancho_glifo(glifo):
    if glifo in COLORES_BOTON or glifo in ("MENU", "VISTA", "STICK", "CRUZ_V", "CRUZ_H"):
        return 27
    if glifo in ("LB", "RB"):
        return 44
    if glifo in FLECHAS_TECLA:
        return 26
    return max(26, recursos.fuente(CHICA).size(glifo)[0] + 14)


# ---------- Cartas de mejora ----------

def carta(pantalla, rect, color, icono, nombre, lineas, elegida=False, apagada=False, rara=False, nivel=None):
    # Una carta: arriba el "arte" (su color con rayas y el icono grande), el nombre, que
    # hace y abajo los niveles (cuadraditos: llenos los que tienes, el de borde de color es
    # el que se suma). La elegida brilla con un borde blanco que late; la apagada (vendida
    # o sin sentido) va en gris. Devuelve el rectangulo libre de abajo (para el precio)
    if apagada:
        color = GRIS
    oscuro = mezclar(color, FONDO, 0.78)
    if elegida:
        latido = (math.sin(pygame.time.get_ticks() / 160) + 1) / 2
        pygame.draw.rect(pantalla, mezclar(color, FONDO, 0.35 + latido * 0.3), rect.inflate(10, 10), 2)
    pantalla.fill(PANEL_FONDO, rect)
    # El arte de arriba
    arte = pygame.Rect(rect.left + 4, rect.top + 4, rect.width - 8, rect.height * 42 // 100)
    pantalla.fill(oscuro, arte)
    recorte_antes = pantalla.get_clip()
    pantalla.set_clip(arte.clip(recorte_antes))         # las rayas no se salen del arte
    for raya_x in range(arte.left - arte.height, arte.right, 16):
        pygame.draw.line(pantalla, mezclar(color, FONDO, 0.7), (raya_x, arte.bottom), (raya_x + arte.height, arte.top), 2)
    pantalla.set_clip(recorte_antes)
    tamano_pixel = max(3, min(arte.width, arte.height) // 11)
    dibujo.pixel_art(pantalla, icono, arte.centerx + tamano_pixel // 2, arte.centery + tamano_pixel // 2,
                     mezclar(color, FONDO, 0.6), tamano_pixel)
    dibujo.pixel_art(pantalla, icono, arte.centerx, arte.centery, color if not apagada else (90, 90, 120), tamano_pixel)
    pygame.draw.rect(pantalla, BLANCO if elegida and not apagada else mezclar(color, FONDO, 0.45), rect, 2)
    esquinas(pantalla, rect, BLANCO if elegida else mezclar(color, FONDO, 0.2), largo=10, grueso=2)
    if rara and not apagada:
        cinta = pygame.Rect(rect.left + 8, rect.top + 8, 52, 16)
        pantalla.fill(MAGENTA, cinta)
        texto(pantalla, "RARA", MINI, BLANCO, cinta.centerx + 1, cinta.centery + 1, sombra=None)
    # Nombre y que hace
    y = arte.bottom + 18
    tamano_nombre = CHICA if recursos.fuente(CHICA).size(nombre)[0] <= rect.width - 16 else MINI
    texto(pantalla, nombre, tamano_nombre, color if (elegida or apagada) else TEXTO, rect.centerx, y)
    y += 22
    for linea in lineas:
        texto(pantalla, linea, MINI, TEXTO if elegida and not apagada else TEXTO_SUAVE, rect.centerx, y)
        y += 14
    # Niveles: un cuadradito por nivel
    abajo = rect.bottom - 30
    if nivel is not None:
        tiene, maximo = nivel
        ancho_pips = maximo * 14 - 4
        for i in range(maximo):
            pip = pygame.Rect(rect.centerx - ancho_pips // 2 + i * 14, abajo - 20, 10, 10)
            if i < tiene:
                pantalla.fill(color, pip)
            elif i == tiene and not apagada:
                pygame.draw.rect(pantalla, color if dibujo.parpadeo(300) or not elegida else BLANCO, pip, 2)
            else:
                pygame.draw.rect(pantalla, LINEA_APAGADA, pip, 2)
    return pygame.Rect(rect.left + 4, abajo - 4, rect.width - 8, 28)


# ---------- Fondos ----------

def pixelado(imagen, factor=4, oscuridad=150):
    # La imagen achicada 'factor' veces y agrandada sin suavizar (bloques grandes, como un
    # desenfoque retro) y oscurecida: el juego queda de fondo sin distraer
    ancho, alto = imagen.get_size()
    chica = pygame.transform.scale(imagen, (ancho // factor, alto // factor))
    grande = pygame.transform.scale(chica, (ancho, alto))
    dibujo.oscurecer(grande, FONDO, oscuridad)
    return grande
