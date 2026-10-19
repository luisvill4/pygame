"""
Accesibilidad: lo que el jugador puede suavizar en Opciones > ACCESIBILIDAD.

Los efectos le preguntan a este modulo (y no a las opciones directamente). Asi, un
efecto nuevo respeta lo que eligio el jugador con solo usar estas funciones:
    temblor_maximo()       cuantos pasos de 2 px puede moverse la pantalla (0 = nada)
    destellos_reducidos()  sin destellos de pantalla completa ni parpadeos rapidos
    brillo_crt()           que tan oscuras son las lineas CRT (255 = sin lineas)
    fuerza_neon()          cuanto brillan las cosas de neon (0 = nada, 1 = normal)
    escalado_suave()       la ventana agranda con pixeles parejos (ver ORDEN_ESCALADO)
    letras_por_paso()      que tan rapido se escriben los dialogos (VELOCIDADES_TEXTO)
    factor_lectura()       cuanto mas dura un mensaje de radio (con TEXTO LENTO)

La App le pasa sus opciones al arrancar (accesibilidad.opciones = ...).
Sin opciones (por ejemplo, en algunos tests) todo funciona como siempre.
"""
from juego.config import NIVELES_TEMBLOR, NIVELES_CRT, NIVELES_NEON, VELOCIDADES_TEXTO, LECTURA_LENTA

opciones = None         # las opciones del jugador (guardado.Opciones); las pone la App


def temblor_maximo():
    if opciones is None:
        return NIVELES_TEMBLOR["NORMAL"]
    return NIVELES_TEMBLOR[opciones.temblor]


def destellos_reducidos():
    return opciones is not None and opciones.destellos == "REDUCIDOS"


def brillo_crt():
    if opciones is None:
        return NIVELES_CRT["NORMAL"]
    return NIVELES_CRT[opciones.crt]


def fuerza_neon():
    if opciones is None:
        return NIVELES_NEON["NORMAL"]
    return NIVELES_NEON[opciones.neon]


def escalado_suave():
    return opciones is not None and opciones.escalado == "SUAVE"


def letras_por_paso():
    if opciones is None:
        return VELOCIDADES_TEXTO["NORMAL"]
    return VELOCIDADES_TEXTO[opciones.texto]


def factor_lectura():
    return LECTURA_LENTA if opciones is not None and opciones.texto == "LENTO" else 1
