"""
Tienda de la gasolinera: que se vende, cuanto cuesta y que pasa al comprar.
(La escena escenas/gasolinera.py solo la dibuja y lee las teclas.)

Despues de cada jefe se para en la gasolinera y se paga con CREDITOS (los dan las
monedas, ver Partida.ganar_creditos). Hay dos clases de articulos:

- CARTAS de mejora (mejoras.py), sorteadas como en el Taller. Su precio:
      PRECIO_CARTA + PRECIO_POR_NIVEL por cada nivel que ya tenes de ella
      (x PRECIO_RARA si es rara) y todo sube un poco en cada sector.
- SERVICIOS, segun la dificultad ("servicios" en DIFICULTADES, config.py):
      sortear  cambia las cartas del mostrador (cada vez un poco mas caro)
      escudo   un escudo que dura hasta el proximo golpe
      reparar  recupera una vida
Cada cosa se compra una sola vez por parada (menos sortear, que se repite).

Patron Template Method (otra vez): Articulo dice que hay que tener (nombre, icono,
precio, disponible y al_comprar) y cada articulo lo completa a su manera.
Para agregar un servicio: una clase que herede de Articulo, anotarla en SERVICIOS y
sumar su tipo a "servicios" en las dificultades que lo vendan.
"""
import math

from juego.config import (CIAN, ROJO, AMARILLO, PRECIO_CARTA, PRECIO_POR_NIVEL, PRECIO_RARA, PRECIO_POR_SECTOR,
                          PRECIO_SORTEAR, PRECIO_ESCUDO, PRECIO_REPARAR, TIENDA_CARTAS)
from juego.mejoras import sortear_mejoras
from juego.powerups import HASTA_PERDER_VIDA


def redondear(precio):
    # Precios de a 5 creditos (40, 45, 50...): se leen mas facil
    return int(round(precio / 5) * 5)


class Articulo:
    tipo = None
    nombre = ""             # hasta 12 letras (entra en la carta del mostrador)
    descripcion = []        # lineas de hasta 22 letras (el cartel de abajo)
    color = CIAN
    icono = ["......."] * 7
    rara = False
    se_repite = False       # True = se puede comprar varias veces en la misma parada

    def __init__(self):
        self.vendido = False

    def precio(self, tienda):
        raise NotImplementedError

    def disponible(self, partida):
        # ¿Tiene sentido comprarlo ahora? (ej: reparar con las vidas llenas, no)
        return True

    def al_comprar(self, tienda):
        raise NotImplementedError

    def etiqueta(self, partida):
        # Lo que dice la carta abajo del nombre (ej: "NIVEL 2/3")
        return ""


class Carta(Articulo):
    # Una carta de mejora a la venta (envuelve a una Mejora de mejoras.py)

    def __init__(self, mejora):
        super().__init__()
        self.mejora = mejora
        self.tipo = mejora.tipo
        self.nombre = mejora.nombre
        self.descripcion = mejora.descripcion
        self.color = mejora.color
        self.icono = mejora.icono
        self.rara = mejora.peso < 1

    def precio(self, tienda):
        precio = PRECIO_CARTA + PRECIO_POR_NIVEL * tienda.partida.mejora(self.tipo)
        if self.rara:
            precio *= PRECIO_RARA
        return redondear(precio * tienda.inflacion())

    def disponible(self, partida):
        return self.mejora.disponible(partida)

    def al_comprar(self, tienda):
        tienda.partida.sumar_mejora(self.tipo)

    def etiqueta(self, partida):
        tenes = partida.mejora(self.tipo)
        if self.vendido:
            return "NIVEL " + str(tenes) + "/" + str(self.mejora.maximo)
        if tenes == 0:
            return "NUEVA"
        return "NIVEL " + str(tenes + 1) + "/" + str(self.mejora.maximo)


class Sortear(Articulo):
    tipo = "sortear"
    nombre = "SORTEAR"
    descripcion = ["CAMBIA LAS CARTAS", "DEL MOSTRADOR", "(CADA VEZ MAS CARO)"]
    color = AMARILLO
    se_repite = True
    icono = [".XXXX.X",
             "X....XX",
             "X...XXX",
             "X......",
             "X.....X",
             ".X...X.",
             "..XXX.."]

    def precio(self, tienda):
        return redondear(PRECIO_SORTEAR * (1 + tienda.sorteos) * tienda.inflacion())

    def disponible(self, partida):
        # Solo si quedan cartas que se puedan sortear
        return bool(sortear_mejoras(partida, 1))

    def al_comprar(self, tienda):
        tienda.sorteos += 1
        tienda.cartas = tienda.sortear_cartas()


class EscudoDeViaje(Articulo):
    tipo = "escudo"
    nombre = "ESCUDO"
    descripcion = ["SALIS CON ESCUDO.", "DURA HASTA UN GOLPE"]
    color = CIAN
    icono = ["XXXXXXX",
             "X.....X",
             "X..X..X",
             "X.XXX.X",
             ".X.X.X.",
             "..X.X..",
             "...X..."]

    def precio(self, tienda):
        return redondear(PRECIO_ESCUDO * tienda.inflacion())

    def disponible(self, partida):
        # Con un escudo que ya dura hasta el golpe (ESCUDO ROCE) no sirve otro
        return partida.restante("escudo") != math.inf

    def al_comprar(self, tienda):
        tienda.partida.activar("escudo", HASTA_PERDER_VIDA)


class Reparar(Articulo):
    tipo = "reparar"
    nombre = "REPARAR"
    descripcion = ["RECUPERA UNA VIDA"]
    color = ROJO
    icono = ["..XXX..",
             ".X...X.",
             "XXXXXXX",
             "XXX.XXX",
             "X.....X",
             "XXX.XXX",
             "XXXXXXX"]

    def precio(self, tienda):
        return redondear(PRECIO_REPARAR * tienda.inflacion())

    def disponible(self, partida):
        return partida.vidas < partida.vidas_max

    def al_comprar(self, tienda):
        tienda.partida.vidas += 1


# Los servicios que se pueden vender (cuales vende cada dificultad: "servicios" en config.py)
SERVICIOS = {clase.tipo: clase for clase in (Sortear, EscudoDeViaje, Reparar)}


class Tienda:
    def __init__(self, partida):
        self.partida = partida
        self.sorteos = 0                    # veces que se sorteo en esta parada
        self.cartas = self.sortear_cartas()
        self.servicios = [SERVICIOS[tipo]() for tipo in partida.reglas["servicios"]]

    def sortear_cartas(self):
        return [Carta(mejora) for mejora in sortear_mejoras(self.partida, TIENDA_CARTAS)]

    def articulos(self):
        # Todo lo del mostrador, en orden: primero las cartas y despues los servicios
        return self.cartas + self.servicios

    def inflacion(self):
        # Todo sube un poco en cada sector (cada vez se juntan mas creditos). En la primera
        # parada (al terminar el sector 1) no hay inflacion
        sector_cerrado = self.partida.director.numero_sector - 1
        return 1 + PRECIO_POR_SECTOR * max(0, sector_cerrado - 1)

    def a_la_venta(self, articulo):
        # ¿Esta en el mostrador? (vendido o sin sentido ahora, no)
        return not articulo.vendido and articulo.disponible(self.partida)

    def alcanza(self, articulo):
        return self.partida.creditos >= articulo.precio(self)

    def comprar(self, articulo):
        # Paga y lo aplica. Devuelve True si se pudo comprar
        if not self.a_la_venta(articulo) or not self.alcanza(articulo):
            return False
        self.partida.gastar_creditos(articulo.precio(self))
        if not articulo.se_repite:
            articulo.vendido = True
        articulo.al_comprar(self)
        return True
