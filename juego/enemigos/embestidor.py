"""
Embestidor: se acerca lento, avisa y embiste en linea recta.

Fases:  acercarse -> apuntar (0.6 s quieto, linea roja punteada) -> cargar (0.5 s) -> acercarse...
Solo te sigue (y te embiste) si estas a menos de RANGO_EMBESTIDOR; si no, deambula.
Mientras apunta, la mira te sigue hasta "apunte_fijo" ms antes de embestir (depende de la
dificultad); desde ahi queda fija y la linea deja de parpadear: es el momento de correrse.
O de contraatacar: un dash contra el en plena embestida lo INTERCEPTA (queda aturdido).
"""
import random

from juego import recursos, dibujo
from juego.config import MAGENTA, ROJO, EMBESTIDA, RANGO_EMBESTIDOR, ATURDIDO_INTERCEPTAR
from juego.enemigos.base import Enemigo, registrar_enemigo

_blanco = []        # primer cuadro en blanco (respaldo si falta el sprite de carga)


@registrar_enemigo
class Embestidor(Enemigo):
    tipo = "embestidor"
    nombre = "EMBESTIDOR"
    pista = "CORRETE O FRENALO CON DASH"
    color = MAGENTA

    def al_aparecer(self, partida):
        self.fase = "acercarse"
        self.fase_hasta = self.aparece_en + random.randint(2000, 3500)
        self.mira = (0, 1, 0)       # hacia donde va a embestir: direccion (x, y) y distancia
        self.mira_fija = False

    def mover(self, partida):
        dir_x, dir_y, distancia = self.hacia_la_nave(partida)
        factor = partida.factor_velocidad()
        ahora = partida.tiempo

        if self.fase == "acercarse":
            if 0 < distancia < RANGO_EMBESTIDOR:
                # Te tiene cerca: va hacia ti
                rapidez = self.rapidez(partida, 1.2)
                self.vx += (dir_x / distancia * rapidez - self.vx) * 0.05
                self.vy += (dir_y / distancia * rapidez - self.vy) * 0.05
            else:
                self.deambular()
            self.separarse(partida)
            # Solo embiste si estas dentro del rango (si no, espera a que te acerques)
            if ahora > self.fase_hasta and 0 < distancia < RANGO_EMBESTIDOR:
                self.fase = "apuntar"
                self.fase_hasta = ahora + 600
                partida.sonidos.reproducir("embestidor_apunta", self.x)
                self.mira = (dir_x / distancia, dir_y / distancia, distancia)
                self.mira_fija = False

        elif self.fase == "apuntar":
            # Se queda quieto parpadeando: es el aviso de la embestida
            self.vx, self.vy = 0, 0
            fijo = partida.reglas["apunte_fijo"]
            if fijo and ahora >= self.fase_hasta - fijo:
                if not self.mira_fija:
                    partida.sonidos.reproducir("mira_fija", self.x)
                self.mira_fija = True           # ya no te sigue: embiste hacia donde estabas
            elif distancia > 0:
                self.mira = (dir_x / distancia, dir_y / distancia, distancia)
            if ahora > self.fase_hasta:
                self.fase = "cargar"
                self.fase_hasta = ahora + 500
                partida.sonidos.reproducir("embestida", self.x)
                mira_x, mira_y, _ = self.mira
                self.vx = mira_x * 9 * factor
                self.vy = mira_y * 9 * factor

        else:   # cargar
            centro_x, centro_y = self.centro()
            partida.efectos.particula(centro_x, centro_y, 0, 0, EMBESTIDA, 14, 4)
            if ahora > self.fase_hasta:
                self.fase = "acercarse"
                self.fase_hasta = ahora + random.randint(2500, 3500)
                self.vx *= 0.3
                self.vy *= 0.3

    def interceptable(self):
        return self.fase == "cargar"

    def al_interceptar(self, partida):
        # Lo frenaron en plena embestida: cuando se le pase el aturdido, vuelve a acercarse
        self.fase = "acercarse"
        self.fase_hasta = partida.tiempo + ATURDIDO_INTERCEPTAR + random.randint(2000, 3000)

    def dibujar_cuerpo(self, pantalla, partida):
        if self.fase != "apuntar":
            self.dibujar_animado(pantalla)
            return
        # Linea punteada hacia la mira y destellos: va a embestir.
        # Mientras te sigue, la linea parpadea; cuando la mira queda fija, se queda quieta y mas larga
        mira_x, mira_y, distancia = self.mira
        centro_x, centro_y = int(self.x) + 20, int(self.y) + 20
        largo = 260 if self.mira_fija else min(int(distancia), 220)
        if self.mira_fija or dibujo.parpadeo(100):
            for paso in range(24, largo, 16):
                punto_x = centro_x + mira_x * paso
                punto_y = centro_y + mira_y * paso
                pantalla.fill(ROJO, (int(punto_x) // 2 * 2, int(punto_y) // 2 * 2, 4, 4))
        carga = recursos.sprite("embestidor_carga.png")
        if carga is not None:
            dibujo.pegar(pantalla, carga, self.x, self.y)
        elif dibujo.parpadeo(80):
            if not _blanco:
                _blanco.append(recursos.blanquear(self.cuadros()[0]))
            dibujo.pegar(pantalla, _blanco[0], self.x, self.y)
        else:
            self.dibujar_animado(pantalla)
