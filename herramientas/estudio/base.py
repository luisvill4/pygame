"""
Lo basico del estudio: la frecuencia de muestreo, notas, acordes, curvas y decibeles.
"""
import re

import numpy as np

try:
    from numba import njit
except ImportError:
    # Sin numba todo anda igual, solo que los filtros tardan mucho mas
    def njit(*args, **kwargs):
        if args and callable(args[0]):
            return args[0]
        return lambda funcion: funcion

FS = 44100                  # muestras por segundo

NOTAS = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}

# Intervalos (semitonos desde la fundamental) de cada tipo de acorde
TIPOS_ACORDE = {
    "": [0, 4, 7], "m": [0, 3, 7], "5": [0, 7], "sus2": [0, 2, 7], "sus4": [0, 5, 7],
    "6": [0, 4, 7, 9], "m6": [0, 3, 7, 9], "7": [0, 4, 7, 10], "m7": [0, 3, 7, 10], "maj7": [0, 4, 7, 11],
    "add9": [0, 4, 7, 14], "madd9": [0, 3, 7, 14], "9": [0, 4, 7, 10, 14], "m9": [0, 3, 7, 10, 14],
    "maj9": [0, 4, 7, 11, 14], "6/9": [0, 4, 7, 9, 14], "dim": [0, 3, 6], "aug": [0, 4, 8],
}


def midi(nombre):
    # "C#5" -> 73. El La de 440 Hz (A4) es el 69. Un numero ya es una nota midi
    if not isinstance(nombre, str):
        return nombre
    letra, alteracion, octava = re.fullmatch(r"([A-G])([#b]?)(-?\d)", nombre).groups()
    return 12 * (int(octava) + 1) + NOTAS[letra] + {"#": 1, "b": -1, "": 0}[alteracion]


def hertz(nota):
    # Una nota (nombre o midi, puede tener decimales) en Hz
    return 440.0 * 2 ** ((midi(nota) - 69) / 12)


def a_hertz(valor):
    # Una altura: un nombre de nota se convierte; un numero ya esta en Hz
    return hertz(valor) if isinstance(valor, str) else float(valor)


def leer_acorde(nombre):
    # "Am7" -> (9, [0, 3, 7, 10], None) y "C/E" -> (0, [0, 4, 7], 4): la fundamental (0 = Do),
    # sus intervalos y, si tiene barra, la nota del bajo
    nombre, _, bajo = nombre.partition("/")
    letra, alteracion, tipo = re.fullmatch(r"([A-G])([#b]?)(.*)", nombre).groups()
    fundamental = (NOTAS[letra] + {"#": 1, "b": -1, "": 0}[alteracion]) % 12
    nota_bajo = None
    if bajo:
        nota_bajo = (NOTAS[bajo[0]] + {"#": 1, "b": -1}.get(bajo[1:], 0)) % 12
    return fundamental, TIPOS_ACORDE[tipo], nota_bajo


def db(decibeles):
    # De decibeles a cuanto se multiplica (-6 dB = la mitad)
    return 10 ** (decibeles / 20)


def a_db(valor):
    return 20 * np.log10(max(valor, 1e-12))


def curva(puntos, cuantas, exponencial=False):
    # Una "automatizacion" de 'cuantas' muestras: puntos = [(segundo, valor), ...] unidos con
    # rectas. 'exponencial' los une en escala logaritmica: la que el oido escucha pareja
    # para alturas y filtros (de 100 a 200 Hz suena igual que de 1000 a 2000)
    tiempos = np.arange(cuantas) / FS
    segundos = np.array([p[0] for p in puntos], dtype=float)
    valores = np.array([p[1] for p in puntos], dtype=float)
    if exponencial:
        return np.exp(np.interp(tiempos, segundos, np.log(np.maximum(valores, 1e-9))))
    return np.interp(tiempos, segundos, valores)


def muestras(segundos):
    return int(round(segundos * FS))
