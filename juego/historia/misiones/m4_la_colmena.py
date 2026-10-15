"""
Mision 4: LA COLMENA

MAR DE AMBAR (la Madre del Enjambre). La Colmena es una biblioteca. El mensaje se
lee entero: SEGUI LAS MONEDAS, con una firma en glifos.

Que cuenta y que esconde: HISTORIA.md. Como se escribe una mision: historia/mision.py.
"""
from juego.historia.mision import Mision, Fragmento, registrar_mision


@registrar_mision
class LaColmena(Mision):
    numero = 4
    titulo = "LA COLMENA"
    sector = 4

    antes = [
        ("ines", "EL MAR DE AMBAR ES UN PANAL DEL TAMAÑO DE UN SISTEMA SOLAR. CON INSCRIPCIONES. MILLONES."),
        ("alba", "UNA BIBLIOTECA."),
        ("ines", "ESO CREO. TRAEME TODO LO QUE SE PUEDA LEER."),
    ]

    radio = {
        "tramo_1": [
            ("ines", "LOS ESCUDEROS NO SE ROMPEN DE FRENTE. RODEALOS."),
        ],
        "jefe": [
            ("alba", "LA REINA. Y NO PARECE CONTENTA."),
        ],
    }

    despues = [
        ("ines", "ALBA... CON LO QUE TRAJISTE, EL COMPAS SE LEE ENTERO."),
        ("alba", "DECILO."),
        ("ines", "SEGUI LAS MONEDAS. Y DESPUES UNA FIRMA, EN GLIFOS. NO LA PUEDO LEER."),
        ("alba", "TODO ESTE VIAJE PARA QUE NOS DIGAN LO QUE YA ESTAMOS HACIENDO."),
        ("ines", "HAY ALGO MAS. EL COMPAS NO SALE DE LA MAREA. SALE DEL ABISMO."),
    ]

    fragmentos = [
        Fragmento("F07", "LA ERRANTE 3/3",
                  ["MATEO NO VOLVIO. LO ULTIMO QUE DIJO POR RADIO FUE UN NOMBRE: ALBA.",
                   "NO CONOCEMOS A NINGUNA ALBA."]),
        Fragmento("F08", "LAS BIBLIOTECARIAS",
                  ["LA VIMOS LLEGAR UNA VEZ.",
                   "LA VAMOS A VER LLEGAR OTRA."]),
    ]

    secretos = []
