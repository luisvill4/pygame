"""
Los pasajes del modo historia (ver escenas/pasajes.py):
    al_cumplir      vencio al jefe (o despejo la ruta): se guarda la mision cumplida, el dialogo
                    de despues y al mapa. Despues de la mision final, antes, la pantalla final
    al_morir        la nave exploto: Ines te saca de ahi y al mapa (lo encontrado queda guardado)
    ir_al_mapa      volver al mapa estelar, con una mision elegida
Los dialogos se filtran con lo encontrado (los renglones con condicion: historia/mision.py).
"""
from juego.config import SECTORES, ROJO
from juego.escenas.historia.dialogo import Dialogo
from juego.escenas.historia.mapa import Mapa
from juego.escenas.historia.final import Final
from juego.historia.mision import filtrar, misiones_en_orden

RESCATE = [("ines", "¡ALBA! ¿ME ESCUCHAS? ...TE TENGO. TE SACO DE AHI."),
           ("ines", "DESCANSA. LA MAREA NO ESPERA, PERO VOS TAMPOCO TE RENDIS.")]


def ir_al_mapa(app, elegida=None):
    app.cambiar_escena(Mapa(app, elegida))


def la_que_sigue(app, numero):
    # La siguiente que se ve en el mapa (o la misma, si es la ultima)
    visibles = [clase.numero for clase in misiones_en_orden() if clase.visible(app.progreso)]
    despues = [otro for otro in visibles if otro > numero]
    return despues[0] if despues else numero


def al_cumplir(app, partida):
    mision = partida.modo.mision
    progreso = app.progreso
    progreso.cumplir_mision(mision.numero)
    app.sonidos.parar_loops()
    renglones = filtrar(mision.despues, progreso.fragmentos)
    if mision.final:
        siguiente = lambda: app.cambiar_escena(Final(app, lambda: ir_al_mapa(app, mision.numero)))
    else:
        siguiente = lambda: ir_al_mapa(app, la_que_sigue(app, mision.numero))
    app.cambiar_escena(Dialogo(app, renglones, siguiente, "MISION %d CUMPLIDA" % mision.numero, mision.titulo,
                               SECTORES[mision.sector - 1]["color"]))


def al_morir(app, partida):
    numero = partida.modo.mision.numero
    app.cambiar_escena(Dialogo(app, RESCATE, lambda: ir_al_mapa(app, numero), "MISION %d" % numero, "FALLIDA",
                               ROJO))
