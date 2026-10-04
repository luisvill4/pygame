"""
Mejoras: cartas que se eligen durante la partida y duran hasta el Game Over.

Cada tanto (en el nivel MEJORA_PRIMER_NIVEL y al cerrar cada sector) el juego ofrece
3 al azar y elegis una (escena Taller). Asi cada partida termina armando una nave
distinta: mas dash, mas puntos, mas vida...

Patron "registro" (como los power-ups): cada mejora es una clase con @registrar_mejora.
La mayoria no hace nada al elegirla: la Partida pregunta partida.mejora("tipo")
(cuantas veces la elegiste) donde haga falta. Las que cambian algo una sola vez
(ej: +1 vida maxima) lo hacen en al_elegir().

Para agregar una:
    1. Una clase que herede de Mejora, con @registrar_mejora.
    2. tipo, nombre (hasta 12 letras), descripcion (lineas de hasta 22 letras),
       color, icono (pixel art de 7x7), maximo (cuantas veces se puede elegir).
    3. Su efecto: en al_elegir() o preguntando partida.mejora("tipo") en la Partida.
"""
import random

from juego.config import (CIAN, AMARILLO, ROJO, MAGENTA, VERDE, HIELO, BLANCO, NARANJA, VIOLETA,
                          MEJORA_RECARGA, MEJORA_ONDA_RADIO, MEJORA_COMETA, MEJORA_ROCE, MEJORA_ATRACCION,
                          MEJORA_COMBO, MEJORA_SUERTE, MEJORA_POTENCIA, MEJORA_MOTOR)

TIPOS_MEJORA = {}           # tipo -> instancia, en el orden en que se registran


def registrar_mejora(clase):
    mejora = clase()
    if not mejora.tipo:
        raise ValueError(clase.__name__ + " necesita un 'tipo'")
    TIPOS_MEJORA[mejora.tipo] = mejora
    return clase


def sortear_mejoras(partida, cantidad=3):
    # Hasta 'cantidad' mejoras distintas al azar entre las disponibles (las fuertes salen menos)
    posibles = [m for m in TIPOS_MEJORA.values() if m.disponible(partida)]
    elegidas = []
    while posibles and len(elegidas) < cantidad:
        mejora = random.choices(posibles, weights=[m.peso for m in posibles])[0]
        elegidas.append(mejora)
        posibles.remove(mejora)
    return elegidas


def porcentaje(valor):
    # 0.2 -> "20%" (para las descripciones)
    return str(round(valor * 100)) + "%"


class Mejora:
    tipo = None
    nombre = ""             # entra en la carta: hasta 12 letras
    descripcion = []        # que hace, en lineas cortas
    color = BLANCO
    icono = ["......."] * 7     # pixel art de 7x7 ("X" = pixel pintado)
    maximo = 1              # cuantas veces se puede elegir
    peso = 1                # chances de salir en el sorteo (las mas fuertes, menos)
    desde_sector = 1        # sector desde el que puede salir

    def disponible(self, partida):
        return (partida.mejora(self.tipo) < self.maximo
                and partida.director.numero_sector >= self.desde_sector)

    def al_elegir(self, partida):
        # Para las que cambian algo una sola vez
        pass


# ---------- Dash ----------


@registrar_mejora
class DobleDash(Mejora):
    tipo, nombre, color = "doble_dash", "DOBLE DASH", CIAN
    descripcion = ["UN DASH MAS SEGUIDO", "ANTES DE RECARGAR"]
    maximo = 2
    icono = ["X..X...",
             ".X..X..",
             "..X..X.",
             "...X..X",
             "..X..X.",
             ".X..X..",
             "X..X..."]

    def al_elegir(self, partida):
        partida.nave.dash_extra_max += 1
        partida.nave.dash_extra += 1


@registrar_mejora
class Recarga(Mejora):
    tipo, nombre, color = "recarga", "RECARGA", CIAN
    descripcion = ["EL DASH SE RECARGA", porcentaje(MEJORA_RECARGA) + " MAS RAPIDO"]
    maximo = 3
    icono = ["...XX..",
             "..XX...",
             ".XX....",
             "XXXXXX.",
             "...XX..",
             "..XX...",
             ".XX...."]


@registrar_mejora
class Onda(Mejora):
    tipo, nombre, color = "onda", "ONDA", NARANJA
    descripcion = ["AL TERMINAR EL DASH:", "UNA ONDA ROMPE BALAS,", "DESTRUYE Y EMPUJA"]
    maximo = len(MEJORA_ONDA_RADIO)
    icono = ["..XXX..",
             ".X...X.",
             "X..X..X",
             "X.XXX.X",
             "X..X..X",
             ".X...X.",
             "..XXX.."]


@registrar_mejora
class Cometa(Mejora):
    tipo, nombre, color = "cometa", "COMETA", AMARILLO
    descripcion = ["DASH " + porcentaje(MEJORA_COMETA - 1) + " MAS LARGO"]
    icono = ["....XXX",
             "...XXXX",
             "..XXXXX",
             ".X.XXX.",
             "X.X....",
             ".X.....",
             "X......"]

    def al_elegir(self, partida):
        partida.nave.duracion_dash = round(partida.nave.duracion_dash * MEJORA_COMETA)


@registrar_mejora
class Filo(Mejora):
    tipo, nombre, color = "filo", "FILO", ROJO
    descripcion = ["EL DASH DESTRUYE", "A TODOS LOS ENEMIGOS"]
    peso = 0.5
    desde_sector = 2
    icono = ["......X",
             ".....XX",
             "....XX.",
             "X..XX..",
             ".XXX...",
             ".XX....",
             "X..X..."]


@registrar_mejora
class Roce(Mejora):
    tipo, nombre, color = "roce", "ESCUDO ROCE", HIELO
    descripcion = ["CADA " + str(MEJORA_ROCE[0]) + " DASH PERFECTOS", "GANAS UN ESCUDO",
                   "(NIVEL 2: CADA " + str(MEJORA_ROCE[1]) + ")"]
    maximo = len(MEJORA_ROCE)
    icono = ["...X...",
             ".X.X.X.",
             "..XXX..",
             "XXXXXXX",
             "..XXX..",
             ".X.X.X.",
             "...X..."]


@registrar_mejora
class Botin(Mejora):
    tipo, nombre, color = "botin", "BOTIN", VERDE
    descripcion = ["DESTRUIR CON EL DASH", "DA EL DOBLE DE PUNTOS", "Y RECARGA MAS"]
    maximo = 2
    icono = [".XXXXX.",
             "X.X.X.X",
             "XXXXXXX",
             ".X...X.",
             "..X.X..",
             "...X...",
             "......."]


# ---------- Nave y monedas ----------


@registrar_mejora
class Motor(Mejora):
    tipo, nombre, color = "motor", "MOTOR", AMARILLO
    descripcion = ["LA NAVE VA", porcentaje(MEJORA_MOTOR) + " MAS RAPIDO"]
    maximo = 2
    icono = ["...X...",
             "..XXX..",
             ".XXXXX.",
             "..XXX..",
             "..XXX..",
             ".X.X.X.",
             "X..X..X"]


@registrar_mejora
class Atraccion(Mejora):
    tipo, nombre, color = "atraccion", "ATRACCION", MAGENTA
    descripcion = ["LA MONEDA VIENE SOLA", "SI ESTAS CERCA"]
    maximo = len(MEJORA_ATRACCION)
    icono = ["XX...XX",
             "XX...XX",
             "X.....X",
             "X.....X",
             "X.....X",
             ".X...X.",
             "..XXX.."]


@registrar_mejora
class ComboLargo(Mejora):
    tipo, nombre, color = "combo", "COMBO LARGO", AMARILLO
    descripcion = ["EL COMBO TARDA", porcentaje(MEJORA_COMBO) + " MAS EN CORTARSE"]
    maximo = 2
    icono = ["..XXX..",
             ".X.X.X.",
             "X..X..X",
             "X..XX.X",
             "X.....X",
             ".X...X.",
             "..XXX.."]


# ---------- Supervivencia y power-ups ----------


@registrar_mejora
class Corazon(Mejora):
    tipo, nombre, color = "corazon", "CORAZON", ROJO
    descripcion = ["+1 VIDA MAXIMA", "Y TE CURA UNA"]
    maximo = 2
    icono = [".XX.XX.",
             "XXXXXXX",
             "XXXXXXX",
             "XXXXXXX",
             ".XXXXX.",
             "..XXX..",
             "...X..."]

    def al_elegir(self, partida):
        partida.vidas_max += 1
        partida.vidas = min(partida.vidas + 1, partida.vidas_max)


@registrar_mejora
class Fenix(Mejora):
    tipo, nombre, color = "fenix", "FENIX", NARANJA
    descripcion = ["SI PERDES LA ULTIMA", "VIDA, VOLVES CON UNA", "(UNA VEZ)"]
    peso = 0.5
    icono = ["...X...",
             "..XX...",
             "..XXX.X",
             ".XXXXXX",
             "XXX.XXX",
             "XX...XX",
             ".XXXXX."]


@registrar_mejora
class Suerte(Mejora):
    tipo, nombre, color = "suerte", "SUERTE", VERDE
    descripcion = ["LOS POWER-UPS CAEN", porcentaje(MEJORA_SUERTE) + " MAS SEGUIDO"]
    maximo = 2
    icono = [".XX.XX.",
             "XXX.XXX",
             ".XXXXX.",
             "..XXX..",
             ".XXXXX.",
             "XXX.XXX",
             ".XX.XX."]


@registrar_mejora
class Potencia(Mejora):
    tipo, nombre, color = "potencia", "POTENCIA", VIOLETA
    descripcion = ["LOS POWER-UPS DURAN", porcentaje(MEJORA_POTENCIA) + " MAS"]
    maximo = 2
    icono = ["XXXXXXX",
             ".X...X.",
             "..X.X..",
             "...X...",
             "..X.X..",
             ".XXXXX.",
             "XXXXXXX"]
