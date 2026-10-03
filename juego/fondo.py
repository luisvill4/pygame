"""
Fondo con paralaje: nebulosas y planetas (sprites) y estrellas (pixeles).

Todo cae despacio; lo lejano mas lento que lo cercano. Mientras se juega, ademas,
el fondo se corre al reves de la nave (lo maneja quien llama a mover()).
Paleta del fondo: ningun canal por encima de ~110, para que no se confunda con
enemigos, monedas o power-ups.

mover() va en la logica (60 veces por segundo) y dibujar() en cada cuadro, interpolado.
"""
import random

import pygame

from juego import recursos, lienzo
from juego.config import ALTO, ANCHO_MENU, FONDO, PROFUNDIDAD
from juego.interpolacion import Interpolador


class ObjetoFondo:
    def __init__(self, imagen, x, y, profundidad):
        self.imagen, self.x, self.y, self.profundidad = imagen, x, y, profundidad


class Estrella:
    __slots__ = ("x", "y", "velocidad")

    def __init__(self, x, y, velocidad):
        # Las rapidas (velocidad 1 a 3) son mas grandes, brillantes y cercanas
        self.x, self.y, self.velocidad = x, y, velocidad


class Fondo:
    def __init__(self):
        # El fondo se arma para el ancho actual (al cambiar el formato se crea uno nuevo)
        escala = lienzo.ancho / ANCHO_MENU
        self.estrellas = []
        for _ in range(round(90 * escala)):
            self.estrellas.append(Estrella(random.randint(0, lienzo.ancho), random.randint(0, ALTO),
                                           random.choice([1, 1, 1, 2, 2, 3])))
        # Nebulosas y planetas, en orden de dibujo: primero lo mas lejano
        self.objetos = []
        self.agregar("nebulosa", 40 * escala, 60)
        self.agregar("nebulosa", 480 * escala, 360, voltear=True)
        self.agregar("planeta_chico", 660 * escala, 140)
        self.agregar("planeta_chico", 150 * escala, 470)
        self.agregar("planeta_grande", 520 * escala, 250)
        self.interpolador = Interpolador()

    def agregar(self, nombre, x, y, voltear=False):
        # Si falta el sprite, simplemente no se agrega
        imagen = recursos.sprite(nombre + ".png")
        if imagen is None:
            return
        if voltear:
            imagen = pygame.transform.flip(imagen, True, True)  # para que no se vean iguales
        self.objetos.append(ObjetoFondo(imagen, x, y, PROFUNDIDAD[nombre]))

    def mover(self, empuje_x=0, empuje_y=0):
        # Un paso de logica: cada capa cae a 0.6 * profundidad px, mas el empuje (paralaje)
        self.interpolador.guardar(self.objetos + self.estrellas)
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
            estrella.x += empuje_x * estrella.velocidad
            estrella.y += (0.6 + empuje_y) * estrella.velocidad
            if estrella.x < 0:
                estrella.x += lienzo.ancho
            elif estrella.x > lienzo.ancho:
                estrella.x -= lienzo.ancho
            if estrella.y > ALTO:
                estrella.x = random.randint(0, lienzo.ancho)
                estrella.y = 0
            elif estrella.y < 0:
                estrella.x = random.randint(0, lienzo.ancho)
                estrella.y = ALTO

    def dibujar(self, pantalla, fraccion=1):
        pantalla.fill(FONDO)
        with self.interpolador.aplicar(self.objetos + self.estrellas, fraccion):
            for objeto in self.objetos:
                pantalla.blit(objeto.imagen, (int(objeto.x), int(objeto.y)))
            for estrella in self.estrellas:
                brillo = 60 + estrella.velocidad * 60
                tamano = 1 if estrella.velocidad < 3 else 2
                pantalla.fill((brillo, brillo, brillo), (int(estrella.x), int(estrella.y), tamano, tamano))
