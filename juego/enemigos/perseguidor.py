"""Perseguidor: va hacia la nave con inercia (hace curvas y se pasa de largo)."""
from juego.config import ROJO
from juego.enemigos.base import Enemigo, registrar_enemigo


@registrar_enemigo
class Perseguidor(Enemigo):
    tipo = "perseguidor"
    plural = "PERSEGUIDORES"
    nombre = "PERSEGUIDOR"
    pista = "TE SIGUE: ESQUIVALO"
    color = ROJO

    def mover(self, partida):
        dir_x, dir_y, distancia = self.hacia_la_nave(partida)
        # Mas rapido en cada nivel (hasta 3.5), y desde el nivel 6 todos se aceleran
        # (con un tope: ver Enemigo.rapidez)
        rapidez = self.rapidez(partida, min(2 + (partida.nivel - 1) * 0.3, 3.5))
        if distancia > 0:
            self.vx += (dir_x / distancia * rapidez - self.vx) * 0.05
            self.vy += (dir_y / distancia * rapidez - self.vy) * 0.05
        self.separarse(partida)
