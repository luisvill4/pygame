"""
Mision 5: EL FIN DE LA LUZ

ABISMO AZUL (el Fin de la Luz). El compas sale de la Singularidad: es una puerta.
Alba entra. Su ultima frase por radio es el mensaje del compas.

Que cuenta y que esconde: HISTORIA.md. Como se escribe una mision: historia/mision.py.
"""
from juego.historia.mision import Mision, Fragmento, registrar_mision


@registrar_mision
class ElFinDeLaLuz(Mision):
    numero = 5
    titulo = "EL FIN DE LA LUZ"
    sector = 5

    antes = [
        ("ines", "ES UN AGUJERO NEGRO. Y EL COMPAS SALE DE ADENTRO."),
        ("alba", "LO QUE ESTA ADENTRO DE UN AGUJERO NEGRO NO SALE, INES."),
        ("ines", "ESTE SI. Y SE ESTA ABRIENDO."),
        ("alba", "VOY."),
    ]

    radio = {
        "tramo_1": [
            ("ines", "LA GRAVEDAD TE VA A TIRAR. NO PELEES CONTRA ELLA: USALA."),
        ],
        "jefe": [
            ("alba", "ES... HERMOSO."),
            ("ines", "ALBA. CONCENTRATE."),
        ],
    }

    despues = [
        ("ines", "SE ABRIO. ALBA, LA PUERTA SE ABRIO."),
        ("alba", "LO VEO. ADENTRO HAY... LUZ."),
        ("ines", "NO SABEMOS QUE HAY DEL OTRO LADO. NO TENES QUE ENTRAR."),
        ("alba", "INES. SI NO VUELVO..."),
        ("alba", "SEGUI LAS MONEDAS."),
    ]

    fragmentos = [
        Fragmento("F09", "LA BRUJULA",
                  ["LA PUERTA NO LLEVA A OTRO LUGAR.",
                   "LLEVA A OTRO CUANDO."]),
        Fragmento("F11", "BITACORA SIN FECHA",
                  ["SI ENCONTRAS ESTO, YA LO HICISTE.",
                   "SEGUI LAS MONEDAS.",
                   "LAS DEJE YO."],
                  oculto=True),
    ]

    secretos = []
