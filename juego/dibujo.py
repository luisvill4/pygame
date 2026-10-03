"""
Ayudas de dibujo con el estilo arcade retro: texto pixelado con sombra, texto con
relieve, marcos de doble linea, lineas CRT, parpadeos...

Todas reciben la superficie donde dibujar (normalmente el lienzo de 800x600).
"""
import pygame

from juego import recursos
from juego.config import ALTO, ANCHO_MENU, FONDO, GRIS, AMARILLO, ROJO, BLANCO, ARCOIRIS, FILAS_RECORDS

# Tamaños de letra (siempre multiplos de 8 para que la fuente pixelada se vea nitida)
MINI = 8                # el tamaño "real" de la fuente: para textos de apoyo
CHICA = 16
MEDIA = 24
GRANDE = 40
TITULO = 56

_lineas_crt = {}        # tamaño -> superficie con las lineas (se crea la primera vez)


def zona_central(pantalla):
    # Parte central de 800x600 de la pantalla: los menus se dibujan ahi con las mismas
    # coordenadas en 4:3 y en 16:9 (en 16:9 quedan centrados, con el fondo a los costados)
    margen = (pantalla.get_width() - ANCHO_MENU) // 2
    return pantalla.subsurface((margen, 0, ANCHO_MENU, ALTO))


def texto(pantalla, mensaje, tamano, color, x, y, sombra=(0, 0, 0), alinear="centro"):
    # Texto pixelado (sin suavizar) con una sombra solida abajo a la derecha
    fuente = recursos.fuente(tamano)
    imagen = fuente.render(mensaje, False, color)
    rect = imagen.get_rect()
    if alinear == "centro":
        rect.center = (x, y)
    elif alinear == "izquierda":
        rect.midleft = (x, y)
    else:
        rect.midright = (x, y)
    if sombra:
        desplazamiento = max(2, fuente.get_height() // 10)
        pantalla.blit(fuente.render(mensaje, False, sombra), rect.move(desplazamiento, desplazamiento))
    pantalla.blit(imagen, rect)


def texto_3d(pantalla, mensaje, tamano, color, color_relieve, y, profundidad=6):
    # Apila copias del texto hacia abajo para que parezca que tiene grosor (centrado)
    centro = pantalla.get_width() // 2
    for i in range(profundidad, 0, -1):
        texto(pantalla, mensaje, tamano, color_relieve, centro + i, y + i, sombra=None)
    texto(pantalla, mensaje, tamano, color, centro, y, sombra=None)


def marco(pantalla, rect, color):
    # Recuadro de doble linea, como las pantallas de arcade
    pygame.draw.rect(pantalla, FONDO, rect)
    pygame.draw.rect(pantalla, color, rect, 4)
    pygame.draw.rect(pantalla, color, rect.inflate(-14, -14), 2)


def opcion(pantalla, mensaje, tamano, x, y, elegida, alinear="centro"):
    # Opcion de un menu: la elegida va en amarillo con una flecha que parpadea
    if not elegida:
        texto(pantalla, mensaje, tamano, GRIS, x, y, alinear=alinear)
        return
    texto(pantalla, mensaje, tamano, AMARILLO, x, y, alinear=alinear)
    if parpadeo(250):
        fuente = recursos.fuente(tamano)
        izquierda = x
        if alinear == "centro":
            izquierda = x - fuente.size(mensaje)[0] // 2
        punta = izquierda - 14
        lado = fuente.get_height() // 3
        pygame.draw.polygon(pantalla, AMARILLO, [(punta - lado, y - lado), (punta - lado, y + lado), (punta, y)])


def numero_arcade(numero):
    # 42 -> "000042"
    return str(numero).zfill(6)


def parpadeo(intervalo=400):
    # True y False alternados cada 'intervalo' milisegundos (reloj real: es solo visual)
    return pygame.time.get_ticks() // intervalo % 2 == 0


def color_arcoiris():
    # Cambia de color cada 100 milisegundos
    return ARCOIRIS[pygame.time.get_ticks() // 100 % len(ARCOIRIS)]


def efecto_crt(pantalla):
    # Lineas horizontales oscuras que imitan una pantalla de arcade
    tamano = pantalla.get_size()
    if tamano not in _lineas_crt:
        lineas = pygame.Surface(tamano, pygame.SRCALPHA)
        for linea_y in range(0, tamano[1], 3):
            pygame.draw.line(lineas, (0, 0, 0, 70), (0, linea_y), (tamano[0], linea_y))
        _lineas_crt[tamano] = lineas
    pantalla.blit(_lineas_crt[tamano], (0, 0))


def oscurecer(pantalla, color, transparencia):
    # Cubre toda la pantalla con un color semitransparente (destellos y pausa)
    velo = pygame.Surface(pantalla.get_size())
    velo.fill(color)
    velo.set_alpha(transparencia)
    pantalla.blit(velo, (0, 0))


def tabla_records(pantalla, filas, y_titulo, resaltar=-1, titulo="MEJORES PUNTAJES"):
    # Los mejores puntajes; 'resaltar' es la fila recien agregada (va en arcoiris)
    texto(pantalla, titulo, CHICA, ROJO, 400, y_titulo)
    for i in range(FILAS_RECORDS):
        fila_y = y_titulo + 32 + i * 26
        if i < len(filas):
            linea = str(i + 1) + ". " + filas[i]["nombre"] + "  " + numero_arcade(filas[i]["puntos"])
            if i == resaltar:
                color = color_arcoiris()
            elif i == 0:
                color = AMARILLO
            else:
                color = BLANCO
        else:
            linea = str(i + 1) + ". ---  ------"
            color = GRIS
        texto(pantalla, linea, CHICA, color, 400, fila_y)
