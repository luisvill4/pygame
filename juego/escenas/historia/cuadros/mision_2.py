"""
Los cuadros de la MISION 2: EL ACORAZADO (la Nebulosa Carmesi).

    antes:    nebulosa_carmesi (el gas que arde) → foto_vieja (Ines y Mateo) → alba_sola (la linea
              de radio que, con "AHORA TIENES", se enciende)
    despues:  metronomos (los cañones laten en orden) → sigue (la primera palabra; con el cuarto
              renglon, los Cantores) → baliza (F12) → cuenta_atras (F04) → rumbo_esmeralda
"""
import math

import pygame

from juego import dibujo, interfaz, recursos
from juego.config import BLANCO, ROJO, AMARILLO, CIAN, VIOLETA, NARANJA, TEXTO, TEXTO_SUAVE, GRIS
from juego.historia.glifos import escribir, sonando
from juego.escenas.historia.cuadros.base import cuadro, NOCHE
from juego.escenas.historia.cuadros import kit
from juego.escenas.historia.cuadros.kit import g, rotulo, mezclar

GAS = [(255, 190, 150), (230, 80, 80), (150, 30, 60), (70, 12, 34)]
BRASAS = [(255, 240, 200), AMARILLO, NARANJA, ROJO, (120, 20, 40)]
CANONES_X = (24, 114, 222, 312)     # donde cuelgan los cañones del Acorazado (en su sprite)
CANONES_Y = 144


@cuadro("nebulosa_carmesi", "NEBULOSA CARMESI")
def nebulosa_carmesi(pantalla, zona, t, paso, datos):
    # El gas rojo que arde, brasas que suben y la Alondra cruzando con el escudo termico encendido
    kit.estrellas(pantalla, zona, 31, 60)
    kit.nebulosa(pantalla, zona, 32, GAS, t, puntos=1400, deriva=0.12)
    sol_x, sol_y = zona.right - 140, zona.top + 90
    kit.disco(pantalla, sol_x, sol_y, 30, (255, 220, 160))
    kit.disco(pantalla, sol_x, sol_y, 22, BLANCO)
    dibujo.halo(pantalla, sol_x, sol_y, 90, NARANJA)
    kit.brasas(pantalla, zona, t, BRASAS, cuantas=50)
    x = zona.left + 120 + (t * 0.8) % (zona.width + 200) - 100
    y = zona.centery + 40 + kit.vaiven(t, 120, 4)
    calor = 0.6 + 0.4 * math.sin(t / 10)
    dibujo.halo(pantalla, x, y, 44, NARANJA, calor)
    kit.alondra(pantalla, x, y, t, escala=2, mira="derecha")


@cuadro("foto_vieja", "UNA FOTO VIEJA")
def foto_vieja(pantalla, zona, t, paso, datos):
    # Una foto de antes de que se fuera la Errante: Ines y Mateo en el muelle. Cae polvo despacio
    kit.estrellas(pantalla, zona, 33, 50)
    marco = pygame.Rect(g(zona.centerx - 220), zona.top + 40, 440, 208)
    pantalla.fill((90, 80, 66), marco.move(6, 6))                       # la sombra de la foto
    pantalla.fill((214, 204, 180), marco)
    foto = pygame.Rect(marco.left + 12, marco.top + 12, marco.width - 24, marco.height - 50)
    pantalla.fill((44, 50, 70), foto)
    kit.tramado(pantalla, foto, (70, 60, 56))                            # el color gastado de las fotos viejas
    pantalla.fill((30, 30, 44), (foto.left, foto.bottom - 30, foto.width, 30))         # el piso del muelle
    kit.errante(pantalla, foto.right - 70, foto.top + 34, 2, (170, 176, 196))
    for personaje, x in (("ines", foto.left + 30), ("mateo", foto.left + 136)):
        dibujo_retrato = pygame.Surface((96, 96))
        kit.retrato(dibujo_retrato, personaje, 0, 0, 8)
        dibujo_retrato.set_colorkey((8, 10, 26))
        pantalla.blit(dibujo_retrato, (g(x), foto.bottom - 96))
    dibujo.texto(pantalla, "INES Y MATEO, EL ULTIMO DIA", dibujo.CHICA, (90, 70, 50), marco.centerx,
                 marco.bottom - 20, sombra=None)
    if paso >= 2:      # "SE FUE A SEGUIR EL COMPAS": la Errante de la foto ya no esta
        hueco = pygame.Rect(foto.right - 110, foto.top + 14, 90, 40)
        pantalla.fill((44, 50, 70), hueco)
        kit.tramado(pantalla, hueco, (70, 60, 56))
    kit.brasas(pantalla, zona, t // 3, [(200, 190, 170), (120, 110, 100), (60, 56, 60)], cuantas=24, semilla=34)


@cuadro("alba_sola")
def alba_sola(pantalla, zona, t, paso, datos):
    # La Alondra sola en lo oscuro y, muy lejos, la Umbral. Entre las dos, la radio: apagada al
    # principio; con "AHORA TIENES" (el tercer renglon) se enciende y los pulsos viajan hacia Alba
    kit.estrellas(pantalla, zona, 35, 140)
    umbral_x, umbral_y = zona.left + 100, zona.top + 80
    nave_x, nave_y = zona.right - 160, zona.bottom - 80 + kit.vaiven(t, 200, 2)
    kit.estacion(pantalla, umbral_x, umbral_y, t, pixel=2)
    encendida = paso >= 2 or datos.get("encendida")
    color = AMARILLO if encendida else mezclar(GRIS, NOCHE, 0.5)
    kit.linea(pantalla, umbral_x + 30, umbral_y + 8, nave_x - 30, nave_y - 8, color, hueco=0 if encendida else 3)
    if encendida:
        for i in range(3):
            f = ((t * 0.006) + i / 3) % 1
            x = umbral_x + 30 + (nave_x - umbral_x - 60) * f
            y = umbral_y + 8 + (nave_y - umbral_y - 16) * f
            pantalla.fill(BLANCO, (g(x) - 2, g(y) - 2, 6, 6))
            dibujo.halo(pantalla, x, y, 12, AMARILLO)
    kit.alondra(pantalla, nave_x, nave_y, t, escala=1, mira="derecha", llama=0.5)


@cuadro("gracias")
def gracias(pantalla, zona, t, paso, datos):
    # El mismo cuadro con la radio ya encendida (al final de LOS RESTOS: "GRACIAS, ALBA")
    alba_sola(pantalla, zona, t, paso, dict(datos, encendida=True))


@cuadro("metronomos", "NEBULOSA CARMESI")
def metronomos(pantalla, zona, t, paso, datos):
    # El Acorazado vencido, quieto. Sus cuatro cañones laten en orden, de izquierda a derecha,
    # como un metronomo (eran relojes: secreto F04)
    kit.estrellas(pantalla, zona, 36, 70)
    kit.nebulosa(pantalla, zona, 37, [mezclar(c, NOCHE, 0.5) for c in GAS], t, puntos=500, deriva=0.05)
    cx, cy = zona.centerx, zona.centery + 30 + kit.vaiven(t, 360, 4)
    kit.jefe(pantalla, "fortaleza", cx, cy, "cansado", t, brillo=0.7, rapidez=60)
    izquierda, arriba = g(cx - 192), g(cy - 96)
    canones = recursos.hoja("fortaleza_canon.png", 48)
    golpe = (t // 30) % 4
    for i, x in enumerate(CANONES_X):
        if canones:
            dibujo.pegar(pantalla, kit.apagada(canones[1], 0.7), izquierda + x, arriba + CANONES_Y - 48)
        luz = AMARILLO if i == golpe else (90, 60, 20)
        pantalla.fill(luz, (izquierda + x + 20, arriba + CANONES_Y - 42, 6, 6))
        if i == golpe:
            dibujo.halo(pantalla, izquierda + x + 24, arriba + CANONES_Y - 40, 18, AMARILLO)
    rotulo(pantalla, "TIC" if golpe % 2 == 0 else "TAC", izquierda + CANONES_X[golpe] + 24, arriba + 40, AMARILLO)


@cuadro("sigue", "LA PRIMERA PALABRA")
def sigue(pantalla, zona, t, paso, datos):
    # SIGUE en glifos, grande; debajo de cada letra aparece su traduccion. Con el cuarto renglon
    # ("LOS CANTORES"), llegan las ondas del compas desde lo lejos
    kit.estrellas(pantalla, zona, 38, 70)
    palabra = "SIGUE"
    traducidas = min(len(palabra), max(0, (t - 30) // 24))
    glifo_grande(pantalla, palabra, zona.centerx, zona.centery - 30, VIOLETA, traducidas)
    if paso >= 3:
        kit.ondas(pantalla, zona.right - 40, zona.centery - 30, t, VIOLETA, hacia=math.pi, abertura=1.4, alcance=160,
                  cuantas=4)
        rotulo(pantalla, "LOS CANTORES", zona.right - 140, zona.bottom - 32, VIOLETA)


def glifo_grande(pantalla, palabra, cx, cy, color, traducidas=0, escala=2):
    # Un glifo al doble de tamaño (dibujado aparte y agrandado: sigue en la grilla) con la
    # traduccion de sus primeras letras debajo de cada una
    glifos = [escribir(letra) for letra in palabra]
    anchos = [kit.ancho_glifo(un_glifo) for un_glifo in glifos]
    entre = 20
    total = sum(anchos) + entre * (len(glifos) - 1)
    lienzo = pygame.Surface((total + 4, 16), pygame.SRCALPHA)
    x = 0
    centros = []
    for i, (un_glifo, ancho) in enumerate(zip(glifos, anchos)):
        tono = color if i >= traducidas else mezclar(color, BLANCO, 0.5)
        kit.dibujar_glifo(lienzo, un_glifo, x, 8, tono)
        centros.append(x + ancho / 2)
        x += ancho + entre
    grande = pygame.transform.scale(lienzo, (lienzo.get_width() * escala, lienzo.get_height() * escala))
    izquierda = g(cx - grande.get_width() / 2)
    dibujo.pegar(pantalla, grande, izquierda, g(cy) - 16)
    for i in range(traducidas):
        kit.texto_grande(pantalla, palabra[i], AMARILLO, izquierda + centros[i] * escala, g(cy) + 44)


@cuadro("baliza", "LA BALIZA")
def baliza(pantalla, zona, t, paso, datos):
    # La baliza de la Errante: la luz parpadea SIGUE con el ritmo del compas
    kit.estrellas(pantalla, zona, 39, 80)
    kit.nebulosa(pantalla, zona, 40, [mezclar(c, NOCHE, 0.6) for c in GAS], t, puntos=400, deriva=0.04)
    x, y = zona.left + 260, zona.centery + kit.vaiven(t, 220, 6)
    cuerpo = ["..XX..", ".XXXX.", "XXXXXX", "XoooXX", "XXXXXX", "XoooXX", "XXXXXX", ".X..X.", "X....X"]
    kit.pintar(pantalla, cuerpo, {"X": (150, 154, 176), "o": (200, 60, 70)}, x, y + 30, 8)
    prendida = sonando(escribir("SIGUE"), 12, t)
    pantalla.fill(AMARILLO if prendida else (90, 70, 20), (g(x) - 8, g(y) - 18, 16, 12))
    if prendida:
        dibujo.halo(pantalla, x, y - 12, 40, AMARILLO)
    glifo_grande(pantalla, "SIGUE", zona.left + 640, zona.centery - 20, VIOLETA, traducidas=5)
    rotulo(pantalla, "LA LEYO MATEO ANTES QUE NADIE", zona.left + 640, zona.bottom - 36, TEXTO_SUAVE)


@cuadro("cuenta_atras", "LOS RELOJES DEL ACORAZADO")
def cuenta_atras(pantalla, zona, t, paso, datos):
    # Un reloj que corre al reves y los numeros que bajan: alguien sabe cuanto falta
    kit.estrellas(pantalla, zona, 41, 60)
    cx, cy = zona.left + 260, zona.centery
    kit.reloj(pantalla, cx, cy, 90, -t * 0.03, AMARILLO)
    quedan = max(0, 6 * 365 * 24 * 60 - t * 37)     # (minutos que faltan: bajan)
    anios, resto = divmod(quedan, 365 * 24 * 60)
    dias, resto = divmod(resto, 24 * 60)
    izquierda = zona.left + 470
    kit.texto_grande(pantalla, "%d AÑOS %03d DIAS" % (anios, dias), ROJO, izquierda, zona.centery - 30,
                     alinear="izquierda")
    rotulo(pantalla, "%02d:%02d" % (resto // 60, resto % 60), izquierda, zona.centery + 6, ROJO, alinear="izquierda")
    rotulo(pantalla, "HASTA QUE LLEGUE LA MAREA", izquierda, zona.centery + 44, TEXTO_SUAVE, alinear="izquierda")
