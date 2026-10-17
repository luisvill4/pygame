"""
Todos los power-ups. El orden en que estan aqui es el orden del HUD y del panel de inicio
(los cinco primeros, ademas, son los cuadros de sprites/powerups.png).
"""
import math

from juego.config import (CIAN, HIELO, ROJO, MAGENTA, VERDE, AMARILLO, NARANJA, ENERGIA, ESCARCHA,
                          CORAZON, IMANTADO, TREBOL, ORO, FUEGO, DURACION)
from juego.powerups.base import PowerUp, registrar_powerup, HASTA_PERDER_VIDA
from juego.proyectiles import romper_balas

# ---------- Temporales (duran unos segundos) ----------


@registrar_powerup
class Escudo(PowerUp):
    # Aguanta un golpe: lo maneja Partida.danar_jugador()
    tipo, letra, color, nombre = "escudo", "E", CIAN, "ESCUDO"
    descripcion = "AGUANTA UN GOLPE"
    paleta = ENERGIA
    cuadro_sprite = 0
    duracion = DURACION["escudo"]

    def disponible(self, partida):
        # Con el escudo de ESCUDO ROCE (dura hasta un golpe) no sirve otro
        return partida.restante(self.tipo) != math.inf

    def peso(self, partida):
        return 2 if partida.jefe is not None else 1         # contra un jefe sirve mas


@registrar_powerup
class Hielo(PowerUp):
    # Congela enemigos y jefe; tocar un enemigo congelado da puntos
    tipo, letra, color, nombre = "hielo", "H", HIELO, "HIELO"
    descripcion = "CONGELA ENEMIGOS"
    paleta = ESCARCHA
    cuadro_sprite = 1
    duracion = DURACION["hielo"]

    def peso(self, partida):
        # Mas enemigos y balas, mas util
        return 1 + min(2, (len(partida.enemigos) + len(partida.balas) / 3) / 5)

    def al_recoger(self, partida, x, y):
        super().al_recoger(partida, x, y)
        for enemigo in partida.enemigos:
            centro_x, centro_y = enemigo.centro()
            partida.efectos.explosion(centro_x, centro_y, ESCARCHA, 20, 3, 3)
        # Las balas del jefe se rompen y el jefe se congela
        romper_balas(partida.balas, partida.efectos, ESCARCHA)
        if partida.jefe is not None:
            centro_x, centro_y = partida.jefe.centro()
            partida.efectos.explosion(centro_x, centro_y, ESCARCHA, 40, 5, 4)


# ---------- Instantaneo ----------


@registrar_powerup
class Vida(PowerUp):
    tipo, letra, color, nombre = "vida", "+", ROJO, "VIDA"
    descripcion = "RECUPERA UNA VIDA"
    paleta = CORAZON
    cuadro_sprite = 2
    duracion = None

    def disponible(self, partida):
        return partida.vidas < partida.vidas_max       # solo si falta alguna

    def peso(self, partida):
        return 4 if partida.vidas == 1 else 1.5         # con una sola vida, casi seguro

    def al_recoger(self, partida, x, y):
        super().al_recoger(partida, x, y)
        partida.vidas += 1

    def texto_al_recoger(self):
        return "+1 VIDA"


# ---------- Mas temporales ----------


@registrar_powerup
class Iman(PowerUp):
    # La moneda cercana vuela hacia la nave: lo maneja Partida
    tipo, letra, color, nombre = "iman", "I", MAGENTA, "IMAN"
    descripcion = "ATRAE LAS MONEDAS"
    paleta = IMANTADO
    cuadro_sprite = 3
    duracion = DURACION["iman"]

    def peso(self, partida):
        return 1.5 if partida.combo >= 3 else 1         # ayuda a no cortar el combo


@registrar_powerup
class Doble(PowerUp):
    # Puntos dobles: lo maneja Partida.sumar_puntos()
    tipo, letra, color, nombre = "doble", "2", VERDE, "DOBLE"
    descripcion = "PUNTOS DOBLES"
    paleta = TREBOL
    cuadro_sprite = 4
    duracion = DURACION["doble"]

    def peso(self, partida):
        return 1.5 if partida.multiplicador_combo() >= 3 else 1     # con el combo alto rinde mas


# ---------- Duran hasta perder una vida (el escudo los protege) ----------


@registrar_powerup
class Turbo(PowerUp):
    # Mas velocidad maxima: lo maneja Partida.vel_max()
    tipo, letra, color, nombre = "turbo", "T", AMARILLO, "TURBO"
    descripcion = "RAPIDA HASTA PERDER VIDA"
    paleta = ORO
    duracion = HASTA_PERDER_VIDA


@registrar_powerup
class Recarga(PowerUp):
    # El dash se recarga mas rapido: lo maneja Partida.recarga_dash()
    tipo, letra, color, nombre = "recarga", "R", CIAN, "RECARGA"
    descripcion = "DASH x2 HASTA PERDER VIDA"
    paleta = ENERGIA
    duracion = HASTA_PERDER_VIDA

    def peso(self, partida):
        return 1.5 if partida.jefe is not None else 1


# ---------- Para el dash ----------


@registrar_powerup
class Nova(PowerUp):
    # Tu proximo dash termina en una explosion: lo maneja Partida._al_terminar_dash()
    tipo, letra, color, nombre = "nova", "N", NARANJA, "NOVA"
    descripcion = "TU PROXIMO DASH EXPLOTA"
    paleta = FUEGO
    duracion = HASTA_PERDER_VIDA        # hasta que la uses (o pierdas una vida)

    def peso(self, partida):
        return 1 + min(2, len(partida.balas) / 8 + len(partida.enemigos) / 10)

    def texto_al_recoger(self):
        return "NOVA: ¡DASH!"
