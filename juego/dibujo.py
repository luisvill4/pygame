"""
Ayudas de dibujo con el estilo arcade retro: texto pixelado con sombra, texto con
relieve, marcos de doble linea, lineas CRT, parpadeos...

Todas reciben la superficie donde dibujar (normalmente el lienzo de 800x600).
"""
import pygame

from juego import recursos
from juego.config import ANCHO, ALTO, FONDO, GRIS, AMARILLO, ROJO, BLANCO, ARCOIRIS, FILAS_RECORDS

# Tamaños de letra (siempre multiplos de 8 para que la fuente pixelada se vea nitida)
CHICA = 16
MEDIA = 24
GRANDE = 40
TITULO = 56

_lineas_crt = None      # se crea la primera vez que se usa


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
    # Apila copias del texto hacia abajo para que parezca que tiene grosor
    for i in range(profundidad, 0, -1):
        texto(pantalla, mensaje, tamano, color_relieve, ANCHO // 2 + i, y + i, sombra=None)
    texto(pantalla, mensaje, tamano, color, ANCHO // 2, y, sombra=None)


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
    global _lineas_crt
    if _lineas_crt is None:
        _lineas_crt = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
        for linea_y in range(0, ALTO, 3):
            pygame.draw.line(_lineas_crt, (0, 0, 0, 70), (0, linea_y), (ANCHO, linea_y))
    pantalla.blit(_lineas_crt, (0, 0))


def oscurecer(pantalla, color, transparencia):
    # Cubre toda la pantalla con un color semitransparente (destellos y pausa)
    velo = pygame.Surface((ANCHO, ALTO))
    velo.fill(color)
    velo.set_alpha(transparencia)
    pantalla.blit(velo, (0, 0))


def tabla_records(pantalla, filas, y_titulo, resaltar=-1):
    # Los mejores puntajes; 'resaltar' es la fila recien agregada (va en arcoiris)
    texto(pantalla, "MEJORES PUNTAJES", CHICA, ROJO, 400, y_titulo)
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
