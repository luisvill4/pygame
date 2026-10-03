"""
Tamaño del lienzo donde se dibuja todo: 800x600 (4:3) o 1066x600 (16:9).

La altura es siempre la misma; en 16:9 el campo de juego es mas ancho.
Se lee en vivo (lienzo.ancho), porque se puede cambiar desde Opciones.
Los menus se dibujan en una zona central de 800x600 (ver dibujo.zona_central).
"""
from juego.config import ALTO, FORMATOS

formato = "4:3"
ancho = FORMATOS[formato]


def cambiar(nuevo_formato):
    global formato, ancho
    if nuevo_formato not in FORMATOS:
        nuevo_formato = "4:3"
    formato = nuevo_formato
    ancho = FORMATOS[formato]


def tamano():
    return ancho, ALTO


def centro_x():
    return ancho // 2
