"""
La bateria, sintetizada como las cajas de ritmo clasicas (808/909) pero con cuerpo:
cada golpe tiene un "cuerpo" con altura (un seno que cae) y un "ataque" de ruido.

Cada funcion devuelve un golpe en estereo (2, muestras). 'fuerza' va de 0 a 1.
"""
import numpy as np

from herramientas.estudio.base import FS, muestras
from herramientas.estudio.sintesis import filtrar, onda, panear, ruido


def _caida(cuantas, constante):
    return np.exp(-np.arange(cuantas) / FS / constante)


def bombo(fuerza=1.0, tono=52.0, largo=0.4, golpe=1.0, azar=None):
    # El cuerpo: un seno que cae de ~3 veces su tono hasta el tono en 40 ms (el "punch").
    # El ataque: un clic corto de ruido filtrado (que se oiga en parlantes chicos)
    azar = azar or np.random.default_rng(1)
    cuantas = muestras(largo)
    t = np.arange(cuantas) / FS
    frecuencia = tono + tono * 2.2 * np.exp(-t / 0.035) + tono * 0.6 * np.exp(-t / 0.006)
    cuerpo = np.sin(2 * np.pi * np.cumsum(frecuencia) / FS) * _caida(cuantas, largo / 3.2)
    cuerpo = np.tanh(cuerpo * 1.6) / np.tanh(1.6)          # un poco de saturacion: mas redondo
    clic = filtrar(azar.uniform(-1, 1, cuantas), 3500.0) * _caida(cuantas, 0.004) * 0.5 * golpe
    return panear((cuerpo + clic) * fuerza, 0)


def caja(fuerza=1.0, tono=190.0, largo=0.22, azar=None):
    # El parche: dos senos cortos (tono y su modo de 1.6). La bordona: ruido entre 1.5 y 9 kHz
    azar = azar or np.random.default_rng(2)
    cuantas = muestras(largo)
    t = np.arange(cuantas) / FS
    parche = (np.sin(2 * np.pi * tono * (1 + 0.3 * np.exp(-t / 0.01)) * t) * 0.8
              + np.sin(2 * np.pi * tono * 1.6 * t) * 0.35) * _caida(cuantas, 0.045)
    bordona = ruido(largo, filtro=[(0, 9000)], forma=[(0, 1), (largo, 1)], ancho=0.4, azar=azar)
    bordona = filtrar(bordona, 1500.0, 0.0, "altos") * _caida(cuantas, largo / 4.5)
    return (panear(parche, 0) + bordona * 1.6) * fuerza


def palmas(fuerza=1.0, azar=None):
    # Tres palmadas casi juntas (como varias manos) y una cola: ruido alrededor de 1.2 kHz
    azar = azar or np.random.default_rng(3)
    cuantas = muestras(0.25)
    sobre = np.zeros(cuantas)
    for i, demora in enumerate((0.0, 0.011, 0.023)):
        desde = muestras(demora)
        sobre[desde:] += _caida(cuantas - desde, 0.006 if i < 2 else 0.07)
    golpe = ruido(0.25, filtro=[(0, 1200)], resonancia=0.4, modo="banda", forma=[(0, 1), (0.25, 1)],
                  ancho=0.6, azar=azar)
    return golpe * sobre * 2.2 * fuerza


def _metal(cuantas):
    # El sonido metalico de los hi-hats de las cajas de ritmo: seis cuadradas desafinadas
    t = np.ones(cuantas)
    total = np.zeros(cuantas)
    for frecuencia in (205.3, 304.4, 369.6, 522.7, 540.0, 800.0):
        total += onda("cuadrada", t * frecuencia * 1.7)
    return total / 6


def hat(fuerza=1.0, abierto=False, azar=None):
    # Cerrado: corto y fino. Abierto: mas largo. Metal + ruido, sin graves (pasa altos a 7 kHz)
    azar = azar or np.random.default_rng(4)
    largo = 0.32 if abierto else 0.06
    cuantas = muestras(largo)
    mezcla = panear(_metal(cuantas) * 0.6, 0) + ruido(largo, forma=[(0, 1), (largo, 1)], ancho=0.5, azar=azar) * 0.5
    mezcla = filtrar(mezcla, 7000.0, 0.1, "altos")
    mezcla = filtrar(mezcla, 15000.0)                       # sin el "siseo" de arriba de todo
    return mezcla * _caida(cuantas, largo / 4) * fuerza * 4.0      # (el pasa altos se come casi todo el nivel)


def tom(fuerza=1.0, tono=110.0, largo=0.4):
    # Un seno que cae un poco (como un parche grande)
    cuantas = muestras(largo)
    t = np.arange(cuantas) / FS
    frecuencia = tono * (1 + 0.5 * np.exp(-t / 0.05))
    cuerpo = np.sin(2 * np.pi * np.cumsum(frecuencia) / FS) * _caida(cuantas, largo / 3.5)
    return panear(np.tanh(cuerpo * 1.3) * fuerza, 0)


def platillo(fuerza=1.0, largo=2.2, azar=None):
    # Crash: ruido brillante + metal, con una caida larga
    azar = azar or np.random.default_rng(5)
    cuantas = muestras(largo)
    mezcla = ruido(largo, filtro=[(0, 11000)], forma=[(0, 1), (largo, 1)], ancho=1.0, azar=azar)
    mezcla += panear(_metal(cuantas) * 0.4, 0)
    mezcla = filtrar(mezcla, 3500.0, 0.0, "altos")
    sobre = np.minimum(np.arange(cuantas) / muestras(0.004), 1) * _caida(cuantas, largo / 4.5)
    return mezcla * sobre * fuerza * 0.8


def platillo_al_reves(fuerza=1.0, largo=1.2, azar=None):
    # El platillo dado vuelta: crece hasta el golpe (para entrar a una seccion nueva)
    return platillo(fuerza, largo, azar)[:, ::-1].copy()


# Letras de la grilla de bateria -> golpe (con su fuerza normal)
GOLPES = {
    "K": lambda f, azar: bombo(f, azar=azar),
    "S": lambda f, azar: caja(f, azar=azar),
    "C": lambda f, azar: palmas(f, azar=azar),
    "h": lambda f, azar: hat(f * 0.7, azar=azar),
    "H": lambda f, azar: hat(f * 0.8, abierto=True, azar=azar),
    "T": lambda f, azar: tom(f, 130.0),
    "t": lambda f, azar: tom(f, 90.0),
    "X": lambda f, azar: platillo(f, azar=azar),
    "R": lambda f, azar: platillo_al_reves(f, azar=azar),
}
