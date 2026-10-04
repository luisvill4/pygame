"""
Rango del sector: al vencer al jefe, una nota de S a C segun como jugaste el sector.

La Bitacora anota lo que pasa en el sector (como la bitacora de un barco) y
calcular_rango() la convierte en estrellas:

    golpes recibidos   ninguno -> 2 estrellas, 1 o 2 -> 1, mas -> 0
    mejor combo        llegaste a RANGO_COMBO monedas seguidas -> 1
    desafio            lo cumpliste -> 1
    jefe               lo venciste antes de RANGO_TIEMPO_JEFE -> 1

    5 estrellas = S, 4 = A, 2 o 3 = B, menos = C

El cartel con el detalle lo dibuja el HUD (hud.py).
"""
from juego.config import RANGO_COMBO, RANGO_TIEMPO_JEFE, RANGO_PUNTOS


class Bitacora:
    def __init__(self):
        self.golpes = 0                 # golpes recibidos (tambien los que paro el escudo)
        self.mejor_combo = 0
        self.perfectos = 0              # dash perfectos
        self.desafio_cumplido = False
        self.inicio_jefe = None         # momento en que aparecio el jefe
        self.tiempo_jefe = 0            # ms que tardaste en vencerlo


def limite_jefe(tipo_jefe, vuelta):
    # El tiempo para la estrella del jefe: 20% mas en cada vuelta (los jefes aguantan mas)
    return RANGO_TIEMPO_JEFE[tipo_jefe] * (1 + 0.2 * (vuelta - 1))


def minutos(ms):
    # 83000 -> "1:23"
    segundos = round(ms) // 1000          # (round: 60 pasos de 16.666 ms son 1000, no 999.99)
    return str(segundos // 60) + ":" + str(segundos % 60).zfill(2)


def calcular_rango(bitacora, tipo_jefe, vuelta):
    # Devuelve un diccionario con la letra, los puntos de premio y las filas del cartel:
    # (que se mide, el valor, las estrellas que dio, las que podia dar)
    if bitacora.golpes == 0:
        estrellas_golpes = 2
    elif bitacora.golpes <= 2:
        estrellas_golpes = 1
    else:
        estrellas_golpes = 0
    filas = [
        ("GOLPES", str(bitacora.golpes), estrellas_golpes, 2),
        ("MEJOR COMBO", str(bitacora.mejor_combo), int(bitacora.mejor_combo >= RANGO_COMBO), 1),
        ("DESAFIO", "SI" if bitacora.desafio_cumplido else "NO", int(bitacora.desafio_cumplido), 1),
        ("JEFE", minutos(bitacora.tiempo_jefe),
         int(bitacora.tiempo_jefe <= limite_jefe(tipo_jefe, vuelta)), 1),
    ]
    estrellas = sum(fila[2] for fila in filas)
    if estrellas >= 5:
        letra = "S"
    elif estrellas == 4:
        letra = "A"
    elif estrellas >= 2:
        letra = "B"
    else:
        letra = "C"
    return {"letra": letra, "estrellas": estrellas, "filas": filas, "puntos": RANGO_PUNTOS[letra]}
