"""
Fondo con paralaje: nebulosas y planetas (sprites) y estrellas (pixeles).

Todo cae despacio; lo lejano mas lento que lo cercano. Mientras se juega, ademas,
el fondo se corre al reves de la nave (lo maneja quien llama a mover()).
Paleta del fondo: ningun canal por encima de ~110, para que no se confunda con
enemigos, monedas o power-ups.
"""
import random

import pygame

from juego import recursos, lienzo
from juego.config import ALTO, ANCHO_MENU, FONDO, PROFUNDIDAD


class ObjetoFondo:
    def __init__(self, imagen, x, y, profundidad):
        self.imagen, self.x, self.y, self.profundidad = imagen, x, y, profundidad


class Fondo:
    def __init__(self):
        # El fondo se arma para el ancho actual (al cambiar el formato se crea uno nuevo)
        escala = lienzo.ancho / ANCHO_MENU
        # Estrellas: [x, y, velocidad]; las rapidas son mas grandes, brillantes y cercanas
        self.estrellas = []
        for _ in range(round(90 * escala)):
            self.estrellas.append([random.randint(0, lienzo.ancho), random.randint(0, ALTO),
                                   random.choice([1, 1, 1, 2, 2, 3])])
        # Nebulosas y planetas, en orden de dibujo: primero lo mas lejano
        self.objetos = []
        self.agregar("nebulosa", 40 * escala, 60)
        self.agregar("nebulosa", 480 * escala, 360, voltear=True)
        self.agregar("planeta_chico", 660 * escala, 140)
        self.agregar("planeta_chico", 150 * escala, 470)
        self.agregar("planeta_grande", 520 * escala, 250)

    def agregar(self, nombre, x, y, voltear=False):
        # Si falta el sprite, simplemente no se agrega
        imagen = recursos.sprite(nombre + ".png")
        if imagen is None:
            return
        if voltear:
            imagen = pygame.transform.flip(imagen, True, True)  # para que no se vean iguales
        self.objetos.append(ObjetoFondo(imagen, x, y, PROFUNDIDAD[nombre]))

    def mover(self, empuje_x=0, empuje_y=0):
        # Cada capa cae a 0.6 * profundidad px por frame, mas el empuje (paralaje de la nave)
        for objeto in self.objetos:
            ancho, alto = objeto.imagen.get_size()
            objeto.x += empuje_x * objeto.profundidad
            objeto.y += (0.6 + empuje_y) * objeto.profundidad
            # Si sale por un costado entra por el otro
            if objeto.x < -ancho:
                objeto.x = lienzo.ancho
            elif objeto.x > lienzo.ancho:
                objeto.x = -ancho
            # Si sale por arriba o por abajo vuelve por el otro lado, en otro lugar
            if objeto.y > ALTO:
                objeto.x = random.randint(-ancho // 2, lienzo.ancho - ancho // 2)
                objeto.y = -alto
            elif objeto.y < -alto:
                objeto.x = random.randint(-ancho // 2, lienzo.ancho - ancho // 2)
                objeto.y = ALTO

        for estrella in self.estrellas:
            estrella[0] += empuje_x * estrella[2]
            estrella[1] += (0.6 + empuje_y) * estrella[2]
            if estrella[0] < 0:
                estrella[0] += lienzo.ancho
            elif estrella[0] > lienzo.ancho:
                estrella[0] -= lienzo.ancho
            if estrella[1] > ALTO:
                estrella[0] = random.randint(0, lienzo.ancho)
                estrella[1] = 0
            elif estrella[1] < 0:
                estrella[0] = random.randint(0, lienzo.ancho)
                estrella[1] = ALTO

    def dibujar(self, pantalla):
        pantalla.fill(FONDO)
        for objeto in self.objetos:
            pantalla.blit(objeto.imagen, (int(objeto.x), int(objeto.y)))
        for estrella in self.estrellas:
            brillo = 60 + estrella[2] * 60
            tamano = 1 if estrella[2] < 3 else 2
            pantalla.fill((brillo, brillo, brillo), (int(estrella[0]), int(estrella[1]), tamano, tamano))

    def mover_y_dibujar(self, pantalla, empuje_x=0, empuje_y=0):
        self.mover(empuje_x, empuje_y)
        self.dibujar(pantalla)
