"""
Embestidor: se acerca lento, avisa y embiste en linea recta.

Fases:  acercarse -> apuntar (0.6 s quieto, linea roja punteada) -> cargar (0.5 s) -> acercarse...
Solo te sigue (y te embiste) si estas a menos de RANGO_EMBESTIDOR; si no, deambula.
"""
import math
import random

from juego import recursos, dibujo
from juego.config import MAGENTA, ROJO, EMBESTIDA, RANGO_EMBESTIDOR
from juego.enemigos.base import Enemigo, registrar_enemigo

_blanco = []        # primer cuadro en blanco (respaldo si falta el sprite de carga)


@registrar_enemigo
class Embestidor(Enemigo):
    tipo = "embestidor"
    color = MAGENTA

    def al_aparecer(self, partida):
        self.fase = "acercarse"
        self.fase_hasta = self.aparece_en + random.randint(2000, 3500)
        self.rumbo = random.uniform(0, 2 * math.pi)     # hacia donde deambula

    def mover(self, partida):
        dir_x, dir_y, distancia = self.hacia_la_nave(partida)
        factor = partida.factor_velocidad()
        ahora = partida.tiempo

        if self.fase == "acercarse":
            if 0 < distancia < RANGO_EMBESTIDOR:
                # Te tiene cerca: va hacia ti
                rapidez = 1.2 * factor
                self.vx += (dir_x / distancia * rapidez - self.vx) * 0.05
                self.vy += (dir_y / distancia * rapidez - self.vy) * 0.05
            else:
                self._deambular()
            self.separarse(partida)
            # Solo embiste si estas dentro del rango (si no, espera a que te acerques)
            if ahora > self.fase_hasta and distancia < RANGO_EMBESTIDOR:
                self.fase = "apuntar"
                self.fase_hasta = ahora + 600

        elif self.fase == "apuntar":
            # Se queda quieto parpadeando: es el aviso de la embestida
            self.vx, self.vy = 0, 0
            if ahora > self.fase_hasta and distancia > 0:
                self.fase = "cargar"
                self.fase_hasta = ahora + 500
                self.vx = dir_x / distancia * 9 * factor
                self.vy = dir_y / distancia * 9 * factor

        else:   # cargar
            centro_x, centro_y = self.centro()
            partida.efectos.particula(centro_x, centro_y, 0, 0, EMBESTIDA, 14, 4)
            if ahora > self.fase_hasta:
                self.fase = "acercarse"
                self.fase_hasta = ahora + random.randint(2500, 3500)
                self.vx *= 0.3
                self.vy *= 0.3

    def _deambular(self):
        # Despacio y de vez en cuando cambia de rumbo
        if random.random() < 0.01:
            self.rumbo = random.uniform(0, 2 * math.pi)
        if self.x <= 0 or self.x >= 760 or self.y <= 0 or self.y >= 560:
            # Contra un borde: vuelve hacia el centro de la pantalla
            self.rumbo = math.atan2(300 - (self.y + 20), 400 - (self.x + 20))
        self.vx += (math.cos(self.rumbo) * 0.5 - self.vx) * 0.05
        self.vy += (math.sin(self.rumbo) * 0.5 - self.vy) * 0.05

    def dibujar_cuerpo(self, pantalla, partida):
        if self.fase != "apuntar":
            self.dibujar_animado(pantalla)
            return
        # Linea punteada hacia la nave y destellos: va a embestir
        dir_x, dir_y, distancia = self.hacia_la_nave(partida)
        centro_x, centro_y = int(self.x) + 20, int(self.y) + 20
        if distancia > 0 and dibujo.parpadeo(100):
            for paso in range(24, min(int(distancia), 220), 16):
                punto_x = centro_x + dir_x / distancia * paso
                punto_y = centro_y + dir_y / distancia * paso
                pantalla.fill(ROJO, (int(punto_x) // 2 * 2, int(punto_y) // 2 * 2, 4, 4))
        carga = recursos.sprite("embestidor_carga.png")
        if carga is not None:
            pantalla.blit(carga, (self.x, self.y))
        elif dibujo.parpadeo(80):
            if not _blanco:
                _blanco.append(recursos.blanquear(self.cuadros()[0]))
            pantalla.blit(_blanco[0], (self.x, self.y))
        else:
            self.dibujar_animado(pantalla)
