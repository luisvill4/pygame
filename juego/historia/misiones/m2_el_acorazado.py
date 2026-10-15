"""
Mision 2: EL ACORAZADO

NEBULOSA CARMESI (el Acorazado Imperial). La Errante paso por aca. Los cañones
disparan en compas: son metronomos. Ines traduce la primera palabra: SEGUI.

Que cuenta y que esconde: HISTORIA.md. Como se escribe una mision: historia/mision.py.
"""
from juego.historia.mision import Mision, Fragmento, registrar_mision


@registrar_mision
class ElAcorazado(Mision):
    numero = 2
    titulo = "EL ACORAZADO"
    sector = 2

    antes = [
        ("ines", "LA NEBULOSA QUEMA. LITERAL: LA MAREA ESTA CALENTANDO EL GAS."),
        ("alba", "¿ALGO MAS QUE DEBA SABER?"),
        ("ines", "LA ULTIMA SEÑAL DE LA ERRANTE SALIO DE ACA. Y HAY ALGO GRANDE. MUY GRANDE."),
    ]

    radio = {
        "tramo_1": [
            ("ines", "ESOS ARIETES FIJAN LA MIRA ANTES DE EMBESTIR. CUANDO LA LINEA SE QUEDA QUIETA, CORRETE."),
        ],
        "tramo_2": [
            ("alba", "UN ENJAMBRE. LO QUE ME FALTABA."),
        ],
        "tramo_4": [
            ("ines", "¡VIENEN DE TODOS LADOS!"),
        ],
        "jefe": [
            ("alba", "¿UN ACORAZADO? ¿QUIEN CONSTRUYO ESTO?"),
            ("ines", "ESCUCHA SUS CAÑONES. DISPARAN EN COMPAS."),
        ],
    }

    despues = [
        ("ines", "LOS CAÑONES ERAN METRONOMOS. CON SU RITMO PUDE TRADUCIR LA PRIMERA PALABRA DEL COMPAS."),
        ("alba", "¿CUAL?"),
        ("ines", "SEGUI."),
        ("alba", "¿SEGUI QUE?"),
        ("ines", "TODAVIA NO SE. SEGUI VOS."),
    ]

    fragmentos = [
        Fragmento("F04", "LA ERRANTE 2/3",
                  ["LOS CAÑONES DISPARAN EN COMPAS. MATEO LOS CONTO: SON RELOJES.",
                   "ESTAN MARCANDO EL TIEMPO. HACIA ATRAS."]),
    ]

    secretos = []
