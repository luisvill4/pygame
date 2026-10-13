"""
Partes de un jefe: piezas que se rompen por separado (cañones, compuertas, segmentos...).

Cada parte tiene su propia caja de choque, su vida y su dibujo, y esta pegada al jefe:
su posicion se guarda RELATIVA a la esquina del jefe (dx, dy), asi se mueve con el sin
hacer nada (y se dibuja interpolada, porque el jefe lo esta).

El jefe guarda sus partes en self.partes. La clase base Jefe ya resuelve:
- el golpe con el dash (Partida le pregunta parte_golpeable() y llama a golpear_parte()),
- el daño al tocarlas (cajas_danio() incluye las partes vivas),
- el destello blanco, el cartel "¡DASH!" y dibujarlas.

Cada jefe decide CUANDO una parte se puede golpear (golpeable()) y que pasa al
golpearla o al romperla (al_golpear_parte() y al_romper_parte() en el jefe).
"""
import pygame


class Parte:
    margen_golpe = 0        # px de mas alrededor para pegarle con el dash (para el daño no cuenta)

    def __init__(self, dx, dy, ancho, alto, vida):
        self.dx, self.dy = dx, dy           # posicion relativa a la esquina del jefe
        self.ancho, self.alto = ancho, alto
        self.vida_max = vida
        self.vida = vida
        self.golpe_hasta = 0                # destello blanco despues de recibir un golpe

    def viva(self):
        return self.vida > 0

    def caja(self, jefe):
        return pygame.Rect(int(jefe.x) + self.dx, int(jefe.y) + self.dy, self.ancho, self.alto)

    def caja_golpe(self, jefe):
        # La caja para pegarle: la de siempre agrandada (asi es mas facil acertarle)
        return self.caja(jefe).inflate(2 * self.margen_golpe, 2 * self.margen_golpe)

    def centro(self, jefe):
        return jefe.x + self.dx + self.ancho / 2, jefe.y + self.dy + self.alto / 2

    def golpeable(self, jefe):
        # Para las subclases: ¿se le puede pegar con el dash ahora?
        return False

    def dibujar(self, pantalla, x, y, jefe, partida):
        # Para las subclases. (x, y) es donde va su esquina (el jefe ya sumo su temblor y su flotar)
        pass
