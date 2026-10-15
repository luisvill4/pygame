"""
Ayudas de dibujo con el estilo arcade retro: texto pixelado con sombra o contorno,
texto con relieve, marcos de doble linea, parpadeos...

Todas reciben la superficie donde dibujar (normalmente el lienzo de 1066x600).
Las lineas CRT no estan aca: las pone la ventana despues de escalar (ventana.py).

Accesibilidad: parpadeo() y color_arcoiris() se frenan solos si el jugador eligio
DESTELLOS REDUCIDOS, asi todo lo que parpadea respeta esa opcion sin hacer nada mas.
"""
import math

import pygame

from juego import recursos, accesibilidad
from juego.config import (ALTO, ANCHO_MENU, FONDO, GRIS, AMARILLO, ROJO, BLANCO, ARCOIRIS, ARCOIRIS_MS,
                          ARCOIRIS_REDUCIDO, PARPADEO_MINIMO, FILAS_RECORDS, LINEA_APAGADA, PIXEL_ARTE)

# Tamaños de letra (siempre multiplos de 8 para que la fuente pixelada se vea nitida)
MINI = 8                # el tamaño "real" de la fuente: para textos de apoyo
CHICA = 16
MEDIA = 24
GRANDE = 40
TITULO = 56

_textos = {}            # (mensaje, tamaño, colores...) -> imagen ya armada (ver _imagen_texto)
MAXIMO_TEXTOS = 1500    # si la cache crece mas que esto (numeros que cambian), se vacia


def zona_central(pantalla):
    # Parte central de 800x600 de la pantalla: los menus se dibujan ahi, centrados,
    # con el fondo a los costados
    margen = en_grilla((pantalla.get_width() - ANCHO_MENU) / 2)       # (par: la grilla de pixeles de arte)
    return pantalla.subsurface((margen, 0, ANCHO_MENU, ALTO))


def texto(pantalla, mensaje, tamano, color, x, y, sombra=(0, 0, 0), alinear="centro", contorno=None):
    # Texto pixelado (sin suavizar) con una sombra solida abajo a la derecha.
    # Con 'contorno' (un color oscuro) ademas lleva un borde de un pixel de la fuente:
    # es para lo que va encima del juego, asi se lee sobre cualquier fondo
    imagen, borde, letras = _imagen_texto(mensaje, tamano, color, sombra, contorno)
    letras = letras.copy()          # el rectangulo de las letras solas (sin sombra ni contorno)
    if alinear == "centro":
        letras.center = (x, y)
    elif alinear == "izquierda":
        letras.midleft = (x, y)
    else:
        letras.midright = (x, y)
    # En la grilla de pixeles de arte (en CHICA, cada pixel de la letra mide justo eso)
    pantalla.blit(imagen, (en_grilla(letras.x) - borde, en_grilla(letras.y) - borde))


def _imagen_texto(mensaje, tamano, color, sombra, contorno):
    # Arma el texto con su sombra y su contorno en una sola imagen y la guarda: los textos
    # se repiten cuadro a cuadro, asi despues dibujarlos es un solo blit.
    # Devuelve la imagen, cuanto sobresale el contorno (las letras empiezan ahi) y el
    # rectangulo de las letras solas (para alinear igual con o sin sombra y contorno)
    clave = (mensaje, tamano, tuple(color), sombra and tuple(sombra), contorno and tuple(contorno))
    if clave in _textos:
        return _textos[clave]
    if len(_textos) > MAXIMO_TEXTOS:
        _textos.clear()
    fuente = recursos.fuente(tamano)
    letras = fuente.render(mensaje, False, color)
    borde = max(1, tamano // 8) if contorno else 0       # un "pixel" de la fuente (8 px de base)
    caida = max(2, fuente.get_height() // 10) if sombra else 0
    imagen = pygame.Surface((letras.get_width() + 2 * borde + caida, letras.get_height() + 2 * borde + caida),
                            pygame.SRCALPHA)
    if sombra:
        imagen.blit(fuente.render(mensaje, False, sombra), (borde + caida, borde + caida))
    if contorno:
        oscuras = fuente.render(mensaje, False, contorno)
        for dx in (-borde, 0, borde):
            for dy in (-borde, 0, borde):
                imagen.blit(oscuras, (borde + dx, borde + dy))
    imagen.blit(letras, (borde, borde))
    _textos[clave] = (imagen, borde, letras.get_rect())
    return _textos[clave]


def texto_3d(pantalla, mensaje, tamano, color, color_relieve, y, profundidad=6, contorno=None, x=None,
             alinear="centro"):
    # Apila copias del texto hacia abajo para que parezca que tiene grosor (centrado en la
    # pantalla, o en 'x' con 'alinear'). Con 'contorno', primero se dibuja el borde de toda
    # la pila (asi rodea el relieve entero)
    if x is None:
        x = pantalla.get_width() // 2
    if contorno:
        for i in range(profundidad, -1, -1):
            texto(pantalla, mensaje, tamano, contorno, x + i, y + i, None, alinear, contorno)
    for i in range(profundidad, 0, -1):
        texto(pantalla, mensaje, tamano, color_relieve, x + i, y + i, None, alinear)
    texto(pantalla, mensaje, tamano, color, x, y, None, alinear)


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
        flecha(pantalla, izquierda - 14, y, fuente.get_height() // 3, 1, AMARILLO)


def flecha(pantalla, punta_x, y, lado, direccion, color):
    # Triangulo que apunta a la derecha (direccion 1) o a la izquierda (-1), con la punta en (punta_x, y)
    base_x = punta_x - lado * direccion
    pygame.draw.polygon(pantalla, color, [(base_x, y - lado), (base_x, y + lado), (punta_x, y)])


def pestanas(pantalla, rect, nombres, actual, color, color_fondo, enfocada=False):
    # Una fila de pestañas dentro de 'rect'; la actual va resaltada. El espacio que sobra
    # se reparte igual entre todas, asi un nombre largo no queda apretado.
    # 'enfocada' (la fila tiene el foco: IZQ/DER cambia de pestaña): la actual se invierte,
    # color de fondo y letras oscuras. Es una marca fija, sin parpadeo
    fuente = recursos.fuente(CHICA)
    anchos = [fuente.size(nombre)[0] for nombre in nombres]
    aire = (rect.width - sum(anchos)) / len(nombres)
    izquierda = rect.left
    for i, nombre in enumerate(nombres):
        pestana = pygame.Rect(round(izquierda), rect.top, round(anchos[i] + aire), rect.height)
        izquierda += anchos[i] + aire
        if i == actual and enfocada:
            pantalla.fill(color, pestana.inflate(-4, 0))
            texto(pantalla, nombre, CHICA, FONDO, pestana.centerx, pestana.centery, sombra=None)
        elif i == actual:
            pantalla.fill(color_fondo, pestana.inflate(-4, 0))
            texto(pantalla, nombre, CHICA, color, pestana.centerx, pestana.centery)
        else:
            texto(pantalla, nombre, CHICA, GRIS, pestana.centerx, pestana.centery)


_halos = {}             # (radio, color, nivel) -> imagen del resplandor (ver halo)
MAXIMO_HALOS = 800


def halo(pantalla, x, y, radio, color, fuerza=1.0):
    # Resplandor de neon alrededor de algo que brilla (balas, moneda, chispas): anillos
    # pixelados que se SUMAN a lo que hay debajo (BLEND_RGB_ADD). Lo oscuro se ilumina y
    # el dibujo de encima queda nitido. Respeta la opcion NEON (accesibilidad.fuerza_neon).
    # Sus bloques son pixeles de arte (PIXEL_ARTE) y el del centro cae justo sobre el pixel
    # de arte de (x, y): calza con los sprites y con las lineas del CRT
    nivel = round(accesibilidad.fuerza_neon() * fuerza * 4)     # 4 escalones: la cache no crece de mas
    radio = int(radio) // 2 * 2
    if nivel <= 0 or radio < 4:
        return
    clave = (radio, tuple(color), nivel)
    imagen = _halos.get(clave)
    if imagen is None:
        if len(_halos) > MAXIMO_HALOS:
            _halos.clear()
        mitad = radio // PIXEL_ARTE                 # en pixeles de arte
        chica = pygame.Surface((mitad * 2 + 1, mitad * 2 + 1))
        chica.fill((0, 0, 0))
        for proporcion, cuanto in ((1.0, 0.10), (0.7, 0.18), (0.42, 0.30)):
            tono = tuple(min(255, int(canal * cuanto * nivel / 4)) for canal in color)
            pygame.draw.circle(chica, tono, (mitad, mitad), max(1, round(mitad * proporcion)))
        imagen = pygame.transform.scale(chica, (chica.get_width() * PIXEL_ARTE, chica.get_height() * PIXEL_ARTE))
        _halos[clave] = imagen
    # El bloque del centro (mitad, mitad) va sobre el pixel de arte de (x, y)
    corrimiento = radio // PIXEL_ARTE * PIXEL_ARTE
    pantalla.blit(imagen, (en_grilla(x) - corrimiento, en_grilla(y) - corrimiento), special_flags=pygame.BLEND_RGB_ADD)


def resplandor_rect(pantalla, rect, color, ancho=12, fuerza=1.0):
    # Lo mismo que halo() pero alrededor de un rectangulo (un laser): dos franjas sumadas
    intensidad = accesibilidad.fuerza_neon() * fuerza
    if intensidad <= 0:
        return
    rect = pygame.Rect(en_grilla(rect.x), en_grilla(rect.y), en_grilla(rect.width), en_grilla(rect.height))
    for crece, cuanto in ((ancho * 2, 0.12), (ancho, 0.2)):
        tono = tuple(int(canal * cuanto * intensidad) for canal in color)
        pantalla.fill(tono, rect.inflate(en_grilla(crece), 0), special_flags=pygame.BLEND_RGB_ADD)


def barra(pantalla, rect, fraccion, color, borde=GRIS):
    # Barra retro: marco de 2 px y el relleno en bloques de 4 px con 2 de aire (todo en la
    # grilla de pixeles de arte). Sin borde (barras finitas): un riel oscuro y los bloques
    if borde:
        pygame.draw.rect(pantalla, borde, rect, 2)
        adentro = rect.inflate(-8, -8)
    else:
        pantalla.fill(LINEA_APAGADA, rect)
        adentro = rect
    llenos = int((adentro.width + 2) // 6 * min(1, max(0, fraccion)))
    for i in range(llenos):
        pantalla.fill(color, (adentro.left + i * 6, adentro.top, 4, adentro.height))


def barra_segmentos(pantalla, rect, llenos, total, color, destacado=None):
    # Una barra partida en 'total' segmentos (uno por golpe que aguanta un jefe).
    # Los llenos tienen brillo arriba; los vacios, solo el borde. 'destacado' (un indice)
    # se dibuja blanco: el segmento que se acaba de perder
    separacion = 4 if rect.width // total > 12 else 2
    ancho = (rect.width + separacion) / total
    for i in range(total):
        izquierda = en_grilla(rect.left + i * ancho)
        derecha = en_grilla(rect.left + (i + 1) * ancho) - separacion
        segmento = pygame.Rect(izquierda, rect.top, derecha - izquierda, rect.height)
        if i == destacado:
            pantalla.fill(BLANCO, segmento)
        elif i < llenos:
            pantalla.fill(color, segmento)
            pantalla.fill(tuple(min(255, c + 90) for c in color), (segmento.left, segmento.top, segmento.width, 2))
            pantalla.fill(tuple(c // 2 for c in color), (segmento.left, segmento.bottom - 3, segmento.width, 3))
        else:
            pygame.draw.rect(pantalla, LINEA_APAGADA, segmento, 2)


def partir_lineas(mensaje, tamano, ancho):
    # Corta un texto en renglones que no pasen de 'ancho' pixeles (sin cortar palabras)
    fuente = recursos.fuente(tamano)
    lineas = [""]
    for palabra in mensaje.split():
        probando = (lineas[-1] + " " + palabra).strip()
        if fuente.size(probando)[0] <= ancho or not lineas[-1]:
            lineas[-1] = probando
        else:
            lineas.append(palabra)
    return lineas


def pixel_art(pantalla, filas, centro_x, centro_y, color, tamano_pixel=4):
    # Dibuja un dibujo hecho con texto: cada "X" es un cuadrado de 'tamano_pixel' (centrado)
    ancho = len(filas[0]) * tamano_pixel
    alto = len(filas) * tamano_pixel
    izquierda, arriba = int(centro_x - ancho // 2), int(centro_y - alto // 2)
    for fila, linea in enumerate(filas):
        for columna, celda in enumerate(linea):
            if celda == "X":
                pantalla.fill(color, (izquierda + columna * tamano_pixel, arriba + fila * tamano_pixel,
                                      tamano_pixel, tamano_pixel))


def reloj(ms):
    # 754000 -> "12:34" (el tiempo de una partida)
    segundos = int(ms) // 1000
    return str(segundos // 60) + ":" + str(segundos % 60).zfill(2)


def en_grilla(valor):
    # El valor llevado a la grilla de pixeles de arte (PIXEL_ARTE): para que todo calce
    return math.floor(valor) // PIXEL_ARTE * PIXEL_ARTE


def pegar(pantalla, imagen, x, y, centrado=False):
    # Pega un sprite en la grilla de pixeles de arte: (x, y) es su esquina de arriba a la
    # izquierda, o su centro con 'centrado'. Sin esto, un sprite en una x impar quedaba
    # corrido medio pixel de arte respecto del resto (y de las lineas del CRT)
    if centrado:
        x -= imagen.get_width() / 2
        y -= imagen.get_height() / 2
    pantalla.blit(imagen, (en_grilla(x), en_grilla(y)))


def numero_arcade(numero):
    # 42 -> "000042"
    return str(numero).zfill(6)


def parpadeo(intervalo=400):
    # True y False alternados cada 'intervalo' milisegundos (reloj real: es solo visual).
    # Con DESTELLOS REDUCIDOS nunca va mas rapido que PARPADEO_MINIMO
    if accesibilidad.destellos_reducidos():
        intervalo = max(intervalo, PARPADEO_MINIMO)
    return pygame.time.get_ticks() // intervalo % 2 == 0


def color_arcoiris():
    # Cambia de color cada ARCOIRIS_MS (mas lento con DESTELLOS REDUCIDOS)
    paso = ARCOIRIS_REDUCIDO if accesibilidad.destellos_reducidos() else ARCOIRIS_MS
    return ARCOIRIS[pygame.time.get_ticks() // paso % len(ARCOIRIS)]


def oscurecer(pantalla, color, transparencia):
    # Cubre toda la pantalla con un color semitransparente (destellos y pausa)
    velo = pygame.Surface(pantalla.get_size())
    velo.fill(color)
    velo.set_alpha(transparencia)
    pantalla.blit(velo, (0, 0))


def tabla_records(pantalla, filas, y_titulo, resaltar=-1, titulo="MEJORES PUNTAJES", centro_x=400):
    # Los mejores puntajes; 'resaltar' es la fila recien agregada (va en arcoiris)
    texto(pantalla, titulo, CHICA, ROJO, centro_x, y_titulo)
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
        texto(pantalla, linea, CHICA, color, centro_x, fila_y)
