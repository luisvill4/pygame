"""
Eco (power-up ECO): una copia violeta de la nave que repite tu dash un momento despues.

Mientras ECO esta activo, la Partida anota el camino de cada dash. Al terminar el dash
nace un Eco con ese camino: espera ECO_RETRASO pasos y lo recorre igual que vos.
Lo que toca: destruye a los enemigos que el dash destruye, aturde a los demas y rompe
las balas. (Tiene x/y: se dibuja interpolado como todo lo que se mueve)
"""
import pygame

from juego import recursos, nave as modulo_nave
from juego.config import VIOLETA, ECO_RETRASO, ATURDIDO_ONDA

_imagen = []        # la nave teñida de violeta (se crea la primera vez)


def imagen_eco():
    if not _imagen:
        _imagen.append(recursos.tenir(modulo_nave.imagen("nave"), VIOLETA))
    return _imagen[0]


class Eco:
    def __init__(self, camino, angulo):
        self.camino = camino                # posiciones (x, y) de la nave durante el dash
        self.angulo = angulo
        self.indice = -ECO_RETRASO          # negativo: todavia esta esperando
        self.x, self.y = camino[0]
        self.tocados = set()                # enemigos ya aturdidos por este eco (uno por vez)

    def visible(self):
        return 0 <= self.indice < len(self.camino)

    def actualizar(self, partida):
        # Un paso por el camino. Devuelve False cuando termino (y hay que borrarlo)
        self.indice += 1
        if self.indice < 0:
            return True
        if self.indice >= len(self.camino):
            return False
        self.x, self.y = self.camino[self.indice]
        caja = pygame.Rect(self.x, self.y, modulo_nave.TAMANO, modulo_nave.TAMANO)
        for bala in [b for b in partida.balas if caja.collidepoint(b.x, b.y)]:
            partida.balas.remove(bala)
            partida.efectos.explosion(bala.x, bala.y, [(60, 20, 90), VIOLETA], 6, 3, 2)
        for enemigo in list(partida.enemigos):
            if (enemigo not in partida.enemigos or not enemigo.activo(partida.tiempo)
                    or not caja.colliderect(enemigo.caja())):
                continue
            if partida.puede_destruir(enemigo):
                partida.destruir_con_dash(enemigo)
            elif id(enemigo) not in self.tocados:
                self.tocados.add(id(enemigo))
                centro_x, centro_y = self.x + modulo_nave.TAMANO / 2, self.y + modulo_nave.TAMANO / 2
                enemigo.empujar(partida, centro_x, centro_y, 30, ATURDIDO_ONDA)
        return True

    def dibujar(self, pantalla):
        if not self.visible():
            return
        copia = pygame.transform.rotate(imagen_eco(), self.angulo)
        copia.set_alpha(190)
        pantalla.blit(copia, copia.get_rect(center=(self.x + 25, self.y + 25)))
