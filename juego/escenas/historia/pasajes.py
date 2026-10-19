"""
Los pasajes del modo historia (ver escenas/pasajes.py). Todos vuelven a la GALAXIA:
    al_cumplir      una mision: se guarda cumplida, el dialogo de despues (y el plano que Ines
                    diseña con lo que trajiste) y a la galaxia (despues de la mision final, antes,
                    la pantalla final). Un sistema libre: piezas, su eco, su plano y su puerta menor
                    (si tiene), contado por Ines
    al_morir        la nave exploto: Ines te saca de ahi (con la mitad de las piezas)
En los dos casos los creditos de la partida se vuelven piezas para el hangar (historia/hangar.py).
Cada dialogo lleva sus cuadros (escenas/historia/cuadros/): los de la mision, el plano nuevo, el
sistema despejado con sus piezas, el eco, la puerta menor o el rescate.
Los dialogos se filtran con lo encontrado y los años (los renglones con condicion: mision.py).
"""
from juego.config import SECTORES, ROJO
from juego.escenas.historia.dialogo import Dialogo
from juego.escenas.historia.galaxia import Galaxia
from juego.escenas.historia.final import Final
from juego.historia.mision import filtrar
from juego.historia.exploracion import ModoExploracion
from juego.historia import hangar, galaxia, modulos
from juego.historia.ecos import POR_ID as ECOS

def renglones_del_plano(id_modulo, en_una_mision):
    # Lo que se dice al conseguir un plano (los modulos se fabrican en el hangar: modulos.py)
    nombre = modulos.POR_ID[id_modulo].nombre
    if en_una_mision:
        return [("cuadro", "plano"),
                ("ines", "CON LOS DATOS QUE TRAJISTE DISEÑE UN PLANO NUEVO: %s." % nombre),
                ("ines", "FABRICALO EN EL HANGAR. VAS A PODER IR MAS LEJOS.")]
    return [("cuadro", "plano"),
            ("alba", "ENTRE LOS RESTOS HAY UN PLANO. ES DE UN %s." % nombre),
            ("ines", "LO GUARDO EN EL HANGAR. CON PIEZAS, TE LO FABRICO.")]


def datos_del_plano(progreso, id_modulo):
    # Lo que el cuadro del plano necesita: el modulo y el nivel que se puede fabricar ahora
    if id_modulo is None:
        return {}
    return {"modulo": id_modulo, "nivel": modulos.nivel(progreso, id_modulo) + 1}


RESCATE = [("ines", "¡ALBA! ¿ME ESCUCHAS? ...TE TENGO. TE SACO DE AHI."),
           ("ines", "DESCANSA. LA MAREA NO ESPERA, PERO TU TAMPOCO TE RINDES.")]


def ir_a_la_galaxia(app, elegida=None):
    app.cambiar_escena(Galaxia(app, elegida))


def al_cumplir(app, partida):
    app.sonidos.parar_loops()
    if isinstance(partida.modo, ModoExploracion):
        _sistema_despejado(app, partida)
        return
    mision = partida.modo.mision
    progreso = app.progreso
    progreso.cumplir_mision(mision.numero)
    hangar.cobrar(progreso, partida, cumplida=True)
    renglones = filtrar(mision.despues, progreso.fragmentos, progreso.anios, progreso.misiones)
    if modulos.dar_plano(progreso, mision.plano):
        renglones += renglones_del_plano(mision.plano, en_una_mision=True)
    id_sistema = "M%d" % mision.numero
    if mision.final:
        siguiente = lambda: app.cambiar_escena(Final(app, lambda: ir_a_la_galaxia(app, id_sistema)))
    else:
        siguiente = lambda: ir_a_la_galaxia(app, id_sistema)
    app.cambiar_escena(Dialogo(app, renglones, siguiente, "MISION %d CUMPLIDA" % mision.numero, mision.titulo,
                               SECTORES[mision.sector - 1]["color"], datos=datos_del_plano(progreso, mision.plano)))


def _sistema_despejado(app, partida):
    # Las piezas; la primera vez, su eco y su puerta menor. Lo cuenta Ines
    progreso = app.progreso
    modo = partida.modo
    uno = modo.sistema
    primera = uno.id not in progreso.sistemas
    piezas = hangar.cobrar(progreso, partida, cumplida=True, peligro=modo.peligro if primera else 0)
    renglones = [("ines", "SISTEMA DESPEJADO. TRAES %d PIEZAS PARA EL HANGAR." % piezas)]
    datos = dict(datos_del_plano(progreso, uno.plano), color=uno.bioma["color"], piezas=piezas)
    progreso.sistemas.add(uno.id)
    if uno.eco and progreso.encontrar_fragmento(uno.eco):
        partida.sonidos.reproducir("fragmento")
        renglones.append(("cuadro", "eco"))
        renglones += filtrar(ECOS[uno.eco].reaccion, progreso.fragmentos, progreso.anios, progreso.misiones)
        datos["ritmo"] = ECOS[uno.eco].glifo
        renglones.append(("ines", "LO GUARDO EN EL ARCHIVO, CON LOS ECOS."))
    if modulos.dar_plano(progreso, uno.plano):
        renglones += renglones_del_plano(uno.plano, en_una_mision=False)
    if primera and uno.puerta:
        progreso.puertas.add(uno.id)
        otro = galaxia.sistema(uno.puerta)
        renglones.append(("cuadro", "puerta_menor"))
        renglones.append(("alba", "AQUI HAY UNA PUERTA MENOR. LLEVA DERECHO A %s." % otro.nombre))
        renglones.append(("ines", "UN ATAJO. CRUZARLA CASI NO GASTA TIEMPO."))
    progreso.guardar()
    app.cambiar_escena(Dialogo(app, renglones, lambda: ir_a_la_galaxia(app, uno.id), "SISTEMA DESPEJADO",
                               uno.nombre, uno.bioma["color"], cuadro="despejado", datos=datos))


def al_morir(app, partida):
    hangar.cobrar(app.progreso, partida, cumplida=False)
    modo = partida.modo
    if isinstance(modo, ModoExploracion):
        id_sistema, rotulo = modo.sistema.id, modo.sistema.nombre
    else:
        id_sistema, rotulo = "M%d" % modo.mision.numero, "MISION %d" % modo.mision.numero
    app.cambiar_escena(Dialogo(app, RESCATE, lambda: ir_a_la_galaxia(app, id_sistema), rotulo, "FALLIDA", ROJO,
                               cuadro="rescate"))
