"""
Rebotador: va en linea recta (en diagonal) y rebota en los bordes.

Tiene dos estados:
    volando  la animacion de vuelo (rebotador_vuelo.png), igual hacia cualquier pared
    choque   toco una pared: se aplasta contra ella (se queda pegado un ratito),
             sale disparado mareado y se recupera. Despues vuelve a "volando"

Sprites (opcionales):
    rebotador.png        320x160. Cuadros de 40x40 en 4 filas, una por pared (abajo,
                         arriba, izquierda, derecha). Columna 0 = vuelo (igual en las 4
                         filas); columnas 1 a 7 = el choque contra la pared de esa fila
    rebotador_vuelo.png  80x40, 2 cuadros de 40x40 mientras vuela. Si no esta, vuela
                         quieto con la columna 0 de rebotador.png
"""
import math
import random

from juego import recursos, dibujo
from juego.config import AMARILLO, ENEMIGO_VELOCIDAD_MAX, MS_CUADRO_REBOTE
from juego.enemigos.base import Enemigo, registrar_enemigo, enemigo_respaldo


RAPIDEZ = 3         # px por paso al aparecer (despues se acelera con el nivel)

PAREDES = ["abajo", "arriba", "izquierda", "derecha"]     # las filas de la hoja, en orden
CHOQUE = [1, 2, 2, 3, 4, 5, 6, 7]   # columnas del choque, MS_CUADRO_REBOTE cada una (la 2 se repite: dura el doble)
PEGADO = 4                          # los primeros 4 lugares de CHOQUE (columnas 1, 2 y 3) se queda pegado a la pared

_respaldo = {}      # si falta el sprite: el mismo dibujo para todas las paredes


@registrar_enemigo
class Rebotador(Enemigo):
    tipo = "rebotador"
    nombre = "REBOTADOR"
    pista = "REBOTA EN LOS BORDES"
    color = AMARILLO
    rebota_en_bordes = True

    # ---------- Sprites ----------

    @classmethod
    def cuadros_por_pared(cls):
        # {pared: [8 cuadros]} de la hoja, o el dibujo de respaldo si no esta
        filas = recursos.hoja_por_filas("rebotador.png", cls.tamano, PAREDES)
        if filas is None:
            if not _respaldo:
                cuadro = enemigo_respaldo(cls.color, cls.tamano)
                _respaldo.update({pared: [cuadro] * 8 for pared in PAREDES})
            filas = _respaldo
        return filas

    @classmethod
    def cuadros(cls):
        # Los cuadros de vuelo (tambien los usan la ficha del HUD, el congelado y el parpadeo
        # al nacer). Si falta rebotador_vuelo.png, uno solo: la columna 0 de la hoja
        vuelo = recursos.hoja("rebotador_vuelo.png", cls.tamano)
        return vuelo or [cls.cuadros_por_pared()["abajo"][0]]

    # ---------- Movimiento ----------

    def al_aparecer(self, partida):
        # Sale en una diagonal, un poco torcida al azar
        direccion = math.radians(random.choice([45, 135, 225, 315]) + random.randint(-15, 15))
        self.vx = math.cos(direccion) * RAPIDEZ
        self.vy = math.sin(direccion) * RAPIDEZ
        # Empieza volando (la pared se usa recien en el primer choque)
        self.estado = "volando"
        self.pared = "abajo"
        self.inicio_choque = 0

    def mover(self, partida):
        pass    # no cambia de direccion: solo rebota (eso lo hace la clase base)

    def empujar(self, partida, desde_x, desde_y, distancia, ms_aturdido):
        # La clase base lo deja quieto (vx = vy = 0) y, como el rebotador nunca cambia de
        # direccion por su cuenta, se quedaba quieto para siempre. Por eso se le da una
        # direccion nueva: al despertar sale disparado lejos de la onda, igual de rapido
        rapidez = math.hypot(self.vx, self.vy) or RAPIDEZ
        super().empujar(partida, desde_x, desde_y, distancia, ms_aturdido)
        centro_x, centro_y = self.centro()
        direccion = math.atan2(centro_y - desde_y, centro_x - desde_x)
        self.vx = math.cos(direccion) * rapidez
        self.vy = math.sin(direccion) * rapidez

    def actualizar(self, partida, congelado):
        # La clase base lo mueve y lo hace rebotar; aca solo se mira si choco
        antes_vx, antes_vy = self.vx, self.vy
        super().actualizar(partida, congelado)
        pared = self.pared_tocada(antes_vx, antes_vy)
        if pared:
            # Choco (tambien si ya estaba en un choque, ej: en una esquina): empieza de nuevo
            self.estado = "choque"
            self.pared = pared
            self.inicio_choque = partida.tiempo
        elif self.estado == "choque" and self.cuadro_del_choque(partida) >= len(CHOQUE):
            # Termino la animacion del choque: vuelve a volar
            self.estado = "volando"

    def pared_tocada(self, antes_vx, antes_vy):
        # Si la velocidad cambio de signo, reboto: la pared es hacia donde iba antes
        if antes_vy * self.vy < 0:
            return "abajo" if antes_vy > 0 else "arriba"
        if antes_vx * self.vx < 0:
            return "derecha" if antes_vx > 0 else "izquierda"
        return None

    def cuadro_del_choque(self, partida):
        # En que lugar de CHOQUE va (len(CHOQUE) o mas = ya termino)
        return int((partida.tiempo - self.inicio_choque) // MS_CUADRO_REBOTE)

    def paso(self, partida):
        # Pegado a la pared no se mueve
        if self.estado == "choque" and self.cuadro_del_choque(partida) < PEGADO:
            return 0
        # Se acelera con el nivel, pero nunca pasa de ENEMIGO_VELOCIDAD_MAX
        return min(partida.factor_velocidad(), ENEMIGO_VELOCIDAD_MAX / RAPIDEZ)

    # ---------- Dibujo ----------

    def dibujar_cuerpo(self, pantalla, partida):
        if self.estado == "choque":
            # El cuadro del choque que toca, en la fila de la pared que toco
            lugar = min(self.cuadro_del_choque(partida), len(CHOQUE) - 1)
            dibujo.pegar(pantalla, self.cuadros_por_pared()[self.pared][CHOQUE[lugar]], self.x, self.y)
        else:
            # Volando: la animacion de vuelo, como todos los enemigos (MS_CUADRO_ENEMIGO)
            self.dibujar_animado(pantalla)
