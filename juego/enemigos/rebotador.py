"""Rebotador: va en linea recta (en diagonal) y rebota en los bordes."""
import math
import random

from juego.config import AMARILLO
from juego.enemigos.base import Enemigo, registrar_enemigo


@registrar_enemigo
class Rebotador(Enemigo):
    tipo = "rebotador"
    nombre = "REBOTADOR"
    pista = "REBOTA EN LOS BORDES"
    color = AMARILLO
    rebota_en_bordes = True

    def al_aparecer(self, partida):
        # Sale en una diagonal, un poco torcida al azar
        direccion = math.radians(random.choice([45, 135, 225, 315]) + random.randint(-15, 15))
        self.vx = math.cos(direccion) * 3
        self.vy = math.sin(direccion) * 3

    def mover(self, partida):
        pass    # no cambia de direccion: solo rebota (eso lo hace la clase base)

    def paso(self, partida):
        return partida.factor_velocidad()
