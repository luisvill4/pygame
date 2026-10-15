"""
Pasajes: que pantalla sigue cuando la partida termina, segun su modo (patron Strategy, la
mitad "de pantallas" de modos.py).

Juego y Explosion no preguntan de que modo es la partida: le piden sus pasajes y llaman a
    al_morir(app, partida)      la nave exploto
    al_cumplir(app, partida)    el modo dijo que la partida se cumplio (partida.cumplida)
Cada modo tiene los suyos en escenas/<modo>/pasajes.py. Un modo nuevo suma su modulo aca.
"""
from juego.escenas.arcade import pasajes as pasajes_arcade
from juego.escenas.historia import pasajes as pasajes_historia

PASAJES = {"arcade": pasajes_arcade, "historia": pasajes_historia}


def pasajes_de(partida):
    return PASAJES[partida.modo.nombre]
