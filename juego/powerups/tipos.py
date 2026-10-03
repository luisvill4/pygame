"""
Todos los power-ups. El orden en que estan aca es el orden del HUD y del panel de inicio
(los cinco primeros, ademas, son los cuadros de sprites/powerups.png).
"""
from juego.config import (CIAN, HIELO, ROJO, MAGENTA, VERDE, AMARILLO, ENERGIA, ESCARCHA,
                          CORAZON, IMANTADO, TREBOL, ORO, DURACION, VIDAS_MAX)
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


@registrar_powerup
class Hielo(PowerUp):
    # Congela enemigos y jefe; tocar un enemigo congelado da puntos
    tipo, letra, color, nombre = "hielo", "H", HIELO, "HIELO"
    descripcion = "CONGELA ENEMIGOS"
    paleta = ESCARCHA
    cuadro_sprite = 1
    duracion = DURACION["hielo"]

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
        return partida.vidas < VIDAS_MAX       # solo si falta alguna

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


@registrar_powerup
class Doble(PowerUp):
    # Puntos dobles: lo maneja Partida.sumar_puntos()
    tipo, letra, color, nombre = "doble", "2", VERDE, "DOBLE"
    descripcion = "PUNTOS DOBLES"
    paleta = TREBOL
    cuadro_sprite = 4
    duracion = DURACION["doble"]


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
