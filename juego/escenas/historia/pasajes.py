"""
Los pasajes del modo historia (ver escenas/pasajes.py):
    al_cumplir      vencio al jefe: se guarda la mision cumplida, el dialogo de despues y al mapa
    al_morir        la nave exploto: Ines te saca de ahi y al mapa (lo encontrado queda guardado)
    ir_al_mapa      volver al mapa estelar, con una mision elegida
"""
from juego.config import SECTORES, ROJO
from juego.escenas.historia.dialogo import Dialogo
from juego.escenas.historia.mapa import Mapa
from juego.historia.mision import misiones_en_orden

RESCATE = [("ines", "¡ALBA! ¿ME ESCUCHAS? ...TE TENGO. TE SACO DE AHI."),
           ("ines", "DESCANSA. LA MAREA NO ESPERA, PERO VOS TAMPOCO TE RENDIS.")]


def ir_al_mapa(app, elegida=None):
    app.cambiar_escena(Mapa(app, elegida))


def al_cumplir(app, partida):
    mision = partida.modo.mision
    if partida.progreso is not None:
        partida.progreso.cumplir_mision(mision.numero)
    app.sonidos.parar_loops()
    siguiente = min(mision.numero + 1, len(misiones_en_orden()))
    app.cambiar_escena(Dialogo(app, mision.despues, lambda: ir_al_mapa(app, siguiente),
                               "MISION %d CUMPLIDA" % mision.numero, mision.titulo,
                               SECTORES[mision.sector - 1]["color"]))


def al_morir(app, partida):
    numero = partida.modo.mision.numero
    app.cambiar_escena(Dialogo(app, RESCATE, lambda: ir_al_mapa(app, numero), "MISION %d" % numero, "FALLIDA",
                               ROJO))
