"""
Ladron: va hacia la moneda y, si la agarra, huye con ella al borde mas cercano.

Fases:  buscar -> agarrar (LADRON_AGARRE ms quieto: tu momento para reaccionar) -> huir
No lastima: lo que te roba es el combo. Mientras lleva la moneda, el reloj del combo espera
(si no, el combo se cortaria solo en plena persecucion y perseguirlo no serviria).
- Si lo alcanzas con el dash: recuperas la moneda (se cobra en el momento, con bonus) y
  es un dash perfecto. Tambien se lo puede romper antes de que robe.
- Si sale de la pantalla: se corta el combo y la moneda aparece en otro lugar.
Las reglas de la moneda robada estan en la Partida (robar_moneda, recuperar_moneda,
moneda_escapada y soltar_moneda); el ladron solo avisa.
"""
import math

import pygame

from juego.config import VIOLETA, BLANCO, LADRON_VELOCIDAD, LADRON_HUIDA, LADRON_AGARRE, LADRON_PUNTOS
from juego.enemigos.base import Enemigo, registrar_enemigo

ESTELA_HUIDA = [(40, 20, 70), VIOLETA]      # las particulas que deja al huir


def ladron_respaldo(color, mira):
    # Dibujo de respaldo: el cuadrado de los enemigos con un antifaz y los ojos blancos; 'mira'
    # corre los ojos a un lado (los dos cuadros: mira a la izquierda y a la derecha, como quien vigila)
    imagen = pygame.Surface((40, 40), pygame.SRCALPHA)
    pygame.draw.rect(imagen, color, (4, 4, 32, 32), 4)
    pygame.draw.rect(imagen, color, (4, 12, 32, 10))
    pygame.draw.rect(imagen, BLANCO, (10 + mira, 15, 6, 4))
    pygame.draw.rect(imagen, BLANCO, (24 + mira, 15, 6, 4))
    return imagen


@registrar_enemigo
class Ladron(Enemigo):
    tipo = "ladron"
    plural = "LADRONES"
    nombre = "LADRON"
    pista = "ROBA LA MONEDA: ¡ALCANZALO!"
    color = VIOLETA
    destruible = True
    puntos_dash = LADRON_PUNTOS

    @classmethod
    def cuadros_de_respaldo(cls):
        return [ladron_respaldo(cls.color, -2), ladron_respaldo(cls.color, 2)]

    def al_aparecer(self, partida):
        self.fase = "buscar"
        self.fase_hasta = 0
        self.huida = (0, 0)         # hacia donde huye (un vector de largo 1)

    def hace_danio(self):
        return False

    def lleva_la_moneda(self, partida):
        return partida.moneda.robada_por is self

    def mover(self, partida):
        if self.fase != "buscar" and not self.lleva_la_moneda(partida):
            self.fase = "buscar"        # se la sacaron (ej: llego el jefe): a buscarla de nuevo
        if self.fase == "buscar":
            self._buscar(partida)
        elif self.fase == "agarrar":
            # Quieto con la moneda: el aviso de que va a huir
            self.vx, self.vy = 0, 0
            if partida.tiempo >= self.fase_hasta:
                self.fase = "huir"
                self.huida = self.borde_mas_cercano()
        else:
            self._huir(partida)

    def _buscar(self, partida):
        moneda = partida.moneda
        if moneda.robada_por is not None:
            self.deambular()            # otro ladron ya se la llevo
            self.separarse(partida)
            return
        moneda_x, moneda_y = moneda.centro()
        centro_x, centro_y = self.centro()
        dir_x, dir_y = moneda_x - centro_x, moneda_y - centro_y
        distancia = math.hypot(dir_x, dir_y)
        rapidez = self.rapidez(partida, LADRON_VELOCIDAD)
        if distancia > 0:
            self.vx += (dir_x / distancia * rapidez - self.vx) * 0.06
            self.vy += (dir_y / distancia * rapidez - self.vy) * 0.06
        self.separarse(partida)
        if self.caja().colliderect(moneda.caja()):
            self.fase = "agarrar"
            self.fase_hasta = partida.tiempo + LADRON_AGARRE
            self.vx, self.vy = 0, 0
            partida.robar_moneda(self)

    def _huir(self, partida):
        if self.fuera_de_la_pantalla():
            partida.moneda_escapada(self)
            return
        huida_x, huida_y = self.huida
        rapidez = self.rapidez(partida, LADRON_HUIDA)
        self.vx += (huida_x * rapidez - self.vx) * 0.08
        self.vy += (huida_y * rapidez - self.vy) * 0.08
        centro_x, centro_y = self.centro()
        partida.efectos.particula(centro_x, centro_y, 0, 0, ESTELA_HUIDA, 10, 4)

    def _bordes(self):
        # Huyendo puede salir de la pantalla (asi se escapa); si no, los bordes de siempre
        if self.fase != "huir":
            super()._bordes()

    def al_destruirse(self, partida, con_dash):
        # Lo alcanzaste: la moneda vuelve con bonus
        if self.lleva_la_moneda(partida):
            partida.recuperar_moneda(self)

    def al_retirarse(self, partida):
        # Se le termino el turno (o termino el asedio): la suelta sin castigo (no se va con ella)
        if self.lleva_la_moneda(partida):
            partida.soltar_moneda()

    def al_quitar(self, partida):
        # Sale del juego por otra cosa (llega el jefe, el modo desarrollador...): la suelta
        if self.lleva_la_moneda(partida):
            partida.soltar_moneda()
