"""
EL GUION: arma GUION.md con todo lo que se dice en el modo historia, en el orden en que pasa.

Pedido del usuario: "solo escribiste la historia pero no hay ningun guion". Los textos viven en
el codigo (el prologo, cada mision, los mensajes de Ines, los ecos), asi que el guion no se
escribe a mano: se ARMA con esos mismos datos. Si cambia un dialogo, se vuelve a correr y el
guion queda al dia (nunca dice algo distinto de lo que dice el juego).

    python herramientas/guion.py          # escribe GUION.md en la carpeta del juego

Los renglones con condicion (mision.filtrar) llevan una nota: [CON F06: LA CLAVE DEL COMPAS],
[SI LLEGAS TARDE]... Asi se lee tambien lo que solo ve quien encontro los secretos. Los cuadros
(los dibujos animados de arriba: escenas/historia/cuadros/) salen como acotaciones: (SE VE: ...).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from juego.config import MAREA_ANIOS, ruta                               # noqa: E402
from juego.escenas.historia.prologo import CUADROS                       # noqa: E402
from juego.escenas.historia import cuadros                               # noqa: E402
from juego.historia.mision import misiones_en_orden, buscar_fragmento    # noqa: E402
from juego.historia.personajes import PERSONAJES                         # noqa: E402
from juego.historia import tiempo, ecos, misiones                        # noqa: E402,F401  (misiones: las registra)

MOMENTOS = [("tramo_1", "TRAMO 1"), ("tramo_2", "TRAMO 2"), ("tramo_3", "TRAMO 3"), ("tramo_4", "TRAMO 4"),
            ("jefe", "EL GUARDIAN")]


def nota(condicion):
    # "F06+!T6+M5" -> "[CON F06: LA CLAVE DEL COMPAS · A TIEMPO · DESPUES DE LA MISION 5]"
    if not condicion:
        return ""
    partes = []
    for parte in condicion.split("+"):
        sin = parte.startswith("!")
        clave = parte.lstrip("!")
        if clave.startswith("T"):
            anio = int(clave[1:])
            if anio == MAREA_ANIOS:
                partes.append("A TIEMPO" if sin else "SI LLEGAS TARDE")
            else:
                partes.append(("ANTES DEL AÑO %d" if sin else "DESDE EL AÑO %d") % anio)
        elif clave.startswith("M") and clave[1:].isdigit():
            partes.append(("ANTES DE CUMPLIR LA MISION %s" if sin else "DESPUES DE LA MISION %s") % clave[1:])
        elif sin:
            partes.append("SIN " + clave)
        else:
            partes.append("CON %s: %s" % (clave, buscar_fragmento(clave).nombre))
    return " _[" + " · ".join(partes) + "]_"


def renglones(lista):
    lineas = []
    for renglon in lista:
        quien, texto = renglon[0], renglon[1]
        condicion = renglon[2] if len(renglon) > 2 else None
        if quien == "cuadro":           # la acotacion: que dibujo se ve desde aqui
            lugar = cuadros.rotulo(texto)
            lineas.append("- _(SE VE: %s%s)_%s" % (texto.upper().replace("_", " "), " · " + lugar if lugar else "",
                                                   nota(condicion)))
            continue
        lineas.append("- **%s:** %s%s" % (PERSONAJES[quien][0], texto, nota(condicion)))
    return lineas


def prologo():
    lineas = ["## Prólogo", "", "_La primera vez que se entra a la HISTORIA. Habla un narrador; cada "
              "cuadro tiene su dibujo._", ""]
    for nombre, paginas in CUADROS:
        if not paginas:
            lineas += ["**(Título: LA MAREA. SIGUE EL COMPAS.)**", ""]
            continue
        lineas.append("**(%s)**" % nombre.upper())
        lineas += ["> " + pagina for pagina in paginas]
        lineas.append("")
    return lineas


def mision(clase):
    rotulo = "Misión %d%s: %s" % (clase.numero, " (oculta)" if clase.oculta else "", clase.titulo)
    lineas = ["## " + rotulo, ""]
    if clase.oculta:
        lineas += ["_Aparece al encontrar %s._" % ", ".join(clase.requisitos), ""]
    lineas += ["### Antes", ""] + renglones(clase.antes) + [""]
    lineas += ["### Por la radio, jugando", ""]
    for momento, nombre in MOMENTOS:
        if clase.radio.get(momento):
            lineas += ["**%s**" % nombre] + renglones(clase.radio[momento]) + [""]
    lineas += ["### Los secretos (al encontrarlos)", ""]
    for fragmento in clase.fragmentos:
        lineas.append("**%s %s**" % (fragmento.id, fragmento.nombre))
        lineas += renglones(fragmento.reaccion)
        lineas.append("")
    lineas += ["### Después", ""] + renglones(clase.despues) + [""]
    return lineas


def mensajes_de_ines():
    lineas = ["## Los mensajes de Inés", "", "_Cada año que pasa en la Umbral, al llegar a donde ibas._", ""]
    for anio, lista in tiempo.MENSAJES:
        lineas += ["**AÑO %d**" % anio] + renglones(lista) + [""]
    return lineas


def los_ecos():
    lineas = ["## Los ecos de los sistemas libres", "", "_Se encuentran al despejar un sistema por primera vez._", ""]
    for eco in ecos.ECOS:
        lineas.append("**%s %s**" % (eco.id, eco.nombre))
        lineas += ["> " + parrafo for parrafo in eco.texto]
        lineas += renglones(eco.reaccion) + [""]
    return lineas


def armar():
    lineas = ["# La Marea — el guion", "",
              "> Generado por `herramientas/guion.py` con los textos del juego: **no se edita a mano**. "
              "Para cambiar un diálogo, cambiarlo en el código y volver a correr la herramienta. La "
              "verdad de fondo y el porqué de cada cosa están en `HISTORIA.md`.", ""]
    lineas += prologo()
    for clase in misiones_en_orden():
        lineas += mision(clase)
    lineas += mensajes_de_ines() + los_ecos()
    return "\n".join(lineas)


if __name__ == "__main__":
    destino = ruta("GUION.md")
    with open(destino, "w", encoding="utf-8") as archivo:
        archivo.write(armar())
    print("Listo:", destino)
