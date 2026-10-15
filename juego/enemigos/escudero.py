"""
Escudero: persigue lento con un escudo de frente que gira despacio hacia la nave.

- El escudo cubre ESCUDERO_ARCO grados y gira ESCUDERO_GIRO grados por paso: la nave es mas
  rapida, asi que se lo puede rodear.
- Un dash de frente rebota (como contra un jefe): ni la nave ni el sufren nada.
- Un dash por el costado o la espalda lo rompe (y es un dash perfecto). Las ondas (ONDA,
  NOVA) y el ECO tambien chocan contra el escudo.
- Tocarlo sin dash lastima, como a los demas.
El escudo se dibuja con codigo (en la grilla de 2 px), asi gira sin romper el pixel art:
el sprite es solo el cuerpo.
"""
import math

from juego import dibujo
from juego.config import (NARANJA, BLANCO, HIELO, ESCUDERO_VELOCIDAD, ESCUDERO_GIRO, ESCUDERO_ARCO,
                          ESCUDERO_PUNTOS)
from juego.enemigos.base import Enemigo, registrar_enemigo

RADIO_ESCUDO = 26           # px del centro al borde de adentro del escudo
GROSOR_ESCUDO = 6           # px (tres pixeles de arte)
DESTELLO_BLOQUEO = 150      # ms que el escudo se ve blanco despues de frenar un dash


def diferencia_angular(a, b):
    # Cuanto hay que girar desde b para llegar a a, entre -pi y pi (el camino mas corto)
    return (a - b + math.pi) % (2 * math.pi) - math.pi


def celdas_del_escudo(angulo):
    # Las celdas de 2x2 px (su esquina, relativa al centro) que forman el arco del escudo
    # mirando hacia 'angulo', y si son del borde de afuera. Se recorre la grilla y entra cada
    # celda cuyo centro cae dentro del arco: asi el borde sale parejo, sin huecos ni escalones
    celdas = {}
    medio_arco = math.radians(ESCUDERO_ARCO) / 2
    afuera = RADIO_ESCUDO + GROSOR_ESCUDO
    for celda_y in range(-afuera, afuera, 2):
        for celda_x in range(-afuera, afuera, 2):
            radio = math.hypot(celda_x + 1, celda_y + 1)
            if not RADIO_ESCUDO <= radio < afuera:
                continue
            if abs(diferencia_angular(math.atan2(celda_y + 1, celda_x + 1), angulo)) <= medio_arco:
                celdas[(celda_x, celda_y)] = radio >= afuera - 2
    return celdas


@registrar_enemigo
class Escudero(Enemigo):
    tipo = "escudero"
    plural = "ESCUDEROS"
    nombre = "ESCUDERO"
    pista = "RODEALO: DASH POR LA ESPALDA"
    color = NARANJA
    destruible = True
    puntos_dash = ESCUDERO_PUNTOS

    def al_aparecer(self, partida):
        dir_x, dir_y, _ = self.hacia_la_nave(partida)
        self.angulo_escudo = math.atan2(dir_y, dir_x)       # nace mirandote
        self.destello_hasta = 0

    def mover(self, partida):
        dir_x, dir_y, distancia = self.hacia_la_nave(partida)
        rapidez = self.rapidez(partida, ESCUDERO_VELOCIDAD)
        if distancia > 0:
            self.vx += (dir_x / distancia * rapidez - self.vx) * 0.05
            self.vy += (dir_y / distancia * rapidez - self.vy) * 0.05
        self.separarse(partida)
        self.girar_escudo(math.atan2(dir_y, dir_x))

    def girar_escudo(self, hacia):
        # Gira hacia 'hacia' como mucho ESCUDERO_GIRO grados (por eso se lo puede rodear)
        giro = math.radians(ESCUDERO_GIRO)
        falta = diferencia_angular(hacia, self.angulo_escudo)
        self.angulo_escudo += max(-giro, min(giro, falta))

    def bloquea_dash(self, desde_x, desde_y):
        centro_x, centro_y = self.centro()
        desde = math.atan2(desde_y - centro_y, desde_x - centro_x)
        return abs(diferencia_angular(desde, self.angulo_escudo)) <= math.radians(ESCUDERO_ARCO) / 2

    def al_bloquear(self, partida):
        # El escudo destella y el retrocede un poco por el golpe
        self.destello_hasta = partida.tiempo + DESTELLO_BLOQUEO
        self.vx = -math.cos(self.angulo_escudo) * 2
        self.vy = -math.sin(self.angulo_escudo) * 2

    def punto_de_bloqueo(self):
        # El medio del escudo (donde saltan las chispas al bloquear)
        centro_x, centro_y = self.centro()
        radio = RADIO_ESCUDO + GROSOR_ESCUDO / 2
        return centro_x + math.cos(self.angulo_escudo) * radio, centro_y + math.sin(self.angulo_escudo) * radio

    # ---------- Dibujo ----------

    def dibujar(self, pantalla, partida):
        # El cuerpo lo dibuja la base (tambien congelado o aturdido); el escudo va encima
        super().dibujar(pantalla, partida)
        if self.activo(partida.tiempo):
            self.dibujar_escudo(pantalla, partida)

    def dibujar_escudo(self, pantalla, partida):
        centro_x, centro_y = (dibujo.en_grilla(c) for c in self.centro())
        if partida.restante("hielo") > 0:
            adentro, afuera = HIELO, BLANCO
        elif partida.tiempo < self.destello_hasta:
            adentro, afuera = BLANCO, BLANCO
        else:
            adentro, afuera = self.color, BLANCO
        for (celda_x, celda_y), es_borde in celdas_del_escudo(self.angulo_escudo).items():
            pantalla.fill(afuera if es_borde else adentro, (centro_x + celda_x, centro_y + celda_y, 2, 2))
