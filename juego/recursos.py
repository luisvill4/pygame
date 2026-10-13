"""
Carga de imagenes y fuentes.

Todo pasa por una cache (un diccionario): cada archivo se lee del disco una sola
vez, la primera vez que alguien lo pide. Ademas, si un sprite no existe se
devuelve None y quien lo pidio usa su dibujo de respaldo: el juego nunca se cae
por un sprite que falta.

Necesita que pygame.init() ya se haya llamado.
"""
import pygame

from juego.config import ruta

_sprites = {}       # archivo -> Surface (o None si no existe)
_hojas = {}         # (archivo, ancho del cuadro) -> lista de cuadros (o None); por filas: un diccionario
_fuentes = {}       # tamaño -> Font


def fuente(tamano):
    # Fuente pixelada estilo arcade (Press Start 2P, licencia en fuentes/OFL.txt)
    if tamano not in _fuentes:
        try:
            _fuentes[tamano] = pygame.font.Font(ruta("fuentes/PressStart2P-Regular.ttf"), tamano)
        except (FileNotFoundError, OSError):
            _fuentes[tamano] = pygame.font.SysFont("consolas,couriernew", tamano, bold=True)
    return _fuentes[tamano]


def sprite(archivo):
    # Imagen de sprites/, o None si todavia no existe
    if archivo not in _sprites:
        try:
            _sprites[archivo] = pygame.image.load(ruta("sprites/" + archivo))
        except (FileNotFoundError, pygame.error):
            _sprites[archivo] = None
    return _sprites[archivo]


def sprite_obligatorio(archivo):
    # Para los pocos sprites sin respaldo (la nave): si falta, avisa claro
    imagen = sprite(archivo)
    if imagen is None:
        raise FileNotFoundError("Falta el sprite obligatorio sprites/" + archivo)
    return imagen


def cortar_hoja(hoja, ancho_cuadro):
    # Separa una hoja de animacion (cuadros uno al lado del otro) en una lista
    cuadros = []
    for cuadro_x in range(0, hoja.get_width(), ancho_cuadro):
        cuadros.append(hoja.subsurface((cuadro_x, 0, ancho_cuadro, hoja.get_height())))
    return cuadros


def hoja(archivo, ancho_cuadro):
    # Cuadros de una hoja de animacion, o None si el archivo no existe
    clave = (archivo, ancho_cuadro)
    if clave not in _hojas:
        imagen = sprite(archivo)
        _hojas[clave] = cortar_hoja(imagen, ancho_cuadro) if imagen is not None else None
    return _hojas[clave]


def hoja_por_filas(archivo, lado, nombres_filas):
    # Hoja con una animacion por fila (ej: una por direccion), de cuadros de lado x lado.
    # Devuelve {nombre de la fila: [cuadros]}, o None si el archivo no existe o le faltan filas
    clave = (archivo, lado, tuple(nombres_filas))
    if clave not in _hojas:
        imagen = sprite(archivo)
        if imagen is None or imagen.get_height() < lado * len(nombres_filas):
            _hojas[clave] = None
        else:
            _hojas[clave] = {nombre: cortar_hoja(imagen.subsurface((0, fila * lado, imagen.get_width(), lado)), lado)
                             for fila, nombre in enumerate(nombres_filas)}
    return _hojas[clave]


def cuadro_animado(cuadros, ms_por_cuadro, desfase=0):
    # Elige el cuadro que toca segun el reloj real (es solo visual)
    return cuadros[(pygame.time.get_ticks() + desfase) // ms_por_cuadro % len(cuadros)]


def tenir(imagen, color):
    # Copia de la imagen en tonos de un solo color (variantes sin dibujar sprites nuevos)
    copia = pygame.transform.grayscale(imagen)
    copia.fill((70, 70, 70), special_flags=pygame.BLEND_RGB_ADD)
    copia.fill(color, special_flags=pygame.BLEND_RGB_MULT)
    return copia


def blanquear(imagen):
    # Copia toda blanca (para el destello al recibir un golpe)
    copia = imagen.copy()
    copia.fill((255, 255, 255), special_flags=pygame.BLEND_RGB_MAX)
    return copia
