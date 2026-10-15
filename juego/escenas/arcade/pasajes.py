"""
Los pasajes del arcade (ver escenas/pasajes.py): al morir, las iniciales (si entra al top 5)
y el Game Over. El arcade no se "cumple": la ruta sigue hasta que te quedas sin vidas.
"""
from juego.escenas.arcade.iniciales import Iniciales
from juego.escenas.arcade.fin import Fin


def al_morir(app, partida):
    # Con el modo desarrollador no se guarda el record (seria trampa)
    if not partida.modo_desarrollador and app.records.entra(partida.puntaje, partida.dificultad):
        app.cambiar_escena(Iniciales(app, partida))
    else:
        app.cambiar_escena(Fin(app, partida, fila_nueva=-1))


def al_cumplir(app, partida):
    # (no pasa: el ModoArcade siempre sigue despues del jefe)
    al_morir(app, partida)
