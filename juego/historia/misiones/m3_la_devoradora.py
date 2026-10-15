"""
Mision 3: LA DEVORADORA

CAMPO ESMERALDA (la Devoradora de Estrellas). Alguien mas junta monedas: los
ladrones, que se las llevan hacia el Abismo. Aca esta la clave de los glifos.

Que cuenta y que esconde: HISTORIA.md. Como se escribe una mision: historia/mision.py.
"""
from juego.historia.mision import Mision, Fragmento, registrar_mision


@registrar_mision
class LaDevoradora(Mision):
    numero = 3
    titulo = "LA DEVORADORA"
    sector = 3

    antes = [
        ("ines", "EN EL CAMPO ESMERALDA LAS MONEDAS DESAPARECEN ANTES DE QUE LLEGUES."),
        ("alba", "¿OTRO PILOTO?"),
        ("ines", "NO HAY NADIE MAS AHI AFUERA. O NO DEBERIA HABER."),
    ]

    radio = {
        "tramo_1": [
            ("alba", "¡EH! ¡ESE SE LLEVO MI MONEDA!"),
            ("ines", "ALCANZALO CON EL DASH ANTES DE QUE SALGA."),
        ],
        "tramo_3": [
            ("ines", "NIEBLA. NO VEO NADA DESDE ACA. ESTAS SOLA, ALBA."),
        ],
        "jefe": [
            ("alba", "UNA SERPIENTE QUE SE COME LAS ESTRELLAS. CLARO. ¿POR QUE NO?"),
        ],
    }

    despues = [
        ("ines", "SEGUI A LOS LADRONES CON EL RADAR. TODOS VAN AL MISMO LUGAR: AL ABISMO."),
        ("alba", "ALGUIEN ESTA JUNTANDO MONEDAS ALLA."),
        ("ines", "O ALGO."),
    ]

    fragmentos = [
        Fragmento("F05", "EL CARTERO",
                  ["NO LA ROBO. LA LLEVO.",
                   "RUMBO AL ABISMO, EN LINEA RECTA, COMO QUIEN VUELVE A CASA."]),
        Fragmento("F06", "LA CLAVE DEL COMPAS",
                  ["EN EL SILENCIO SE OYE: CORTO, LARGO. CORTO, LARGO, CORTO, CORTO.",
                   "LOS GLIFOS NO SON DIBUJOS. SON RITMOS."]),
    ]

    secretos = []
