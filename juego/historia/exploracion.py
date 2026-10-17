"""
ModoExploracion: una partida en un SISTEMA LIBRE de la galaxia (galaxia.py).

Es como una mision de la historia (hereda de ModoHistoria: la radio, las fichas, el hangar),
pero sin dialogos ni jefe: cuatro tramos y listo. Lo distinto:
    - la RUTA se arma sola, siempre la misma para cada sistema (el azar sale de su id): los
      enemigos son los de su bioma y los objetivos crecen con el peligro (ruta_del_sistema);
    - el PELIGRO (de 1 a 5, por la distancia a la Umbral) trae escuadrones mas grandes y mas
      rapidos; desde peligro 3 el ultimo tramo es un asedio;
    - al despejarlo, piezas (hangar.py), su eco si tiene (ecos.py) y su puerta menor si tiene.
"""
import random

from juego.config import DIFICULTADES, TEXTO_SUAVE
from juego.enemigos import TIPOS_ENEMIGO
from juego.rutas import ASEDIO
from juego.historia.mision import Mision
from juego.historia.modo import ModoHistoria
from juego.historia import galaxia

# Los enemigos de cada bioma: los que la historia ya presento hasta ese sector
ENEMIGOS_DEL_BIOMA = [
    ["perseguidor", "divisor", "rebotador"],
    ["perseguidor", "divisor", "rebotador", "embestidor", "enjambre"],
    ["divisor", "rebotador", "embestidor", "enjambre", "ladron"],
    ["divisor", "rebotador", "embestidor", "enjambre", "ladron", "escudero"],
    ["perseguidor", "divisor", "rebotador", "embestidor", "enjambre", "ladron", "escudero"],
]
FORMACIONES = ["flanco", "pinza", "lluvia", "esquinas", "cerco"]
ANOMALIA_DEL_BIOMA = ["asteroides", "tormenta", "niebla", "oro", "asteroides"]
ESCUADRONES_POR_PELIGRO = 0.2       # cada punto de peligro: escuadrones 20% mas grandes...
VELOCIDAD_POR_PELIGRO = 0.05        # ...y enemigos 5% mas rapidos


def ruta_del_sistema(uno):
    # Los 4 tramos de un sistema libre (con la forma de rutas.py), siempre los mismos
    azar = random.Random(uno.id)
    peligro = galaxia.peligro(uno)
    enemigos = ENEMIGOS_DEL_BIOMA[uno.sector - 1]
    rompibles = [tipo for tipo in enemigos if TIPOS_ENEMIGO[tipo].destruible]

    def escuadrones(cuantos, obligado=None):
        lista = [(azar.choice(enemigos), 1 + azar.randrange(1 + peligro // 2), azar.choice(FORMACIONES))
                 for _ in range(cuantos)]
        if obligado is not None:
            lista[0] = (obligado, 1 + peligro // 2, azar.choice(FORMACIONES))
        return lista

    a_romper = azar.choice(rompibles)
    ultimo = ({"nombre": "EL ASEDIO", "objetivo": ASEDIO, "a_la_vez": 3, "asedio": True,
               "escuadrones": escuadrones(4)} if peligro >= 3 else
              {"nombre": "LA SALIDA", "objetivo": ("perfectos", 2 + peligro), "a_la_vez": 2,
               "escuadrones": escuadrones(3, azar.choice(rompibles))})
    return [
        {"nombre": "LA LLEGADA", "objetivo": ("monedas", 8 + 2 * peligro), "a_la_vez": 1 + peligro // 3,
         "escuadrones": escuadrones(3)},
        {"nombre": "LA CAZA", "objetivo": ("romper", 2 + peligro, a_romper), "a_la_vez": 2,
         "escuadrones": escuadrones(3, a_romper)},
        {"nombre": "EL CORAZON", "objetivo": ("monedas", 10 + 2 * peligro), "a_la_vez": 2,
         "anomalia": ANOMALIA_DEL_BIOMA[uno.sector - 1], "escuadrones": escuadrones(3)},
        ultimo,
    ]


def como_mision(uno):
    # El sistema escrito como una mision (asi el ModoHistoria lo juega sin preguntar nada)
    return type("Sistema" + uno.id, (Mision,), {
        "numero": None, "titulo": uno.nombre, "sector": uno.sector, "lugar": uno.lugar,
        "gravedad": uno.gravedad, "tramos": ruta_del_sistema(uno), "jefe": False, "radio": uno.radio,
        "fragmentos": [], "secretos": [], "antes": [], "despues": []})


class ModoExploracion(ModoHistoria):
    def __init__(self, id_sistema):
        self.sistema = galaxia.sistema(id_sistema)
        self.mision = como_mision(self.sistema)
        self.peligro = galaxia.peligro(self.sistema)

    def empezar(self, partida):
        super().empezar(partida)
        # El peligro: escuadrones mas grandes y enemigos mas rapidos (sobre la dificultad elegida)
        extra = self.peligro - 1
        partida.reglas = dict(partida.reglas)
        partida.reglas["escuadrones"] *= 1 + ESCUADRONES_POR_PELIGRO * extra
        partida.reglas["velocidad"] *= 1 + VELOCIDAD_POR_PELIGRO * extra

    def abre_el_taller(self, director):
        return False                # (las mejoras de la exploracion son las del hangar)

    def propone_desafio(self, director):
        return False

    def encabezado(self, director):
        dificultad = self.partida.dificultad
        return [("SISTEMA  ", TEXTO_SUAVE), (self.sistema.nombre, director.sector["color"]),
                ("   PELIGRO %d   " % self.peligro, TEXTO_SUAVE), (dificultad, DIFICULTADES[dificultad]["color"])]
