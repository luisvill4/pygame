"""
Mision 4: LA COLMENA

MAR DE AMBAR (la Madre del Enjambre). La Colmena es una biblioteca. El mensaje se lee
entero: SEGUI LAS MONEDAS, y despues una firma.

Secretos: la tercera bitacora (20 monedas seguidas: cantan tan fuerte que la radio capta
un eco de hace tres años) y las bibliotecarias (vencer a la Colmena sin romper una abeja).
Que cuenta y que esconde: HISTORIA.md. Como se escribe una mision: historia/mision.py.
"""
from juego.historia.mision import Mision, Fragmento, registrar_mision
from juego.historia.glifos import escribir
from juego.rutas import ASEDIO


@registrar_mision
class LaColmena(Mision):
    numero = 4
    titulo = "LA COLMENA"
    sector = 4
    lugar = (750, 190)

    tramos = [
        {"nombre": "LA MURALLA", "objetivo": ("romper", 3, "escudero"), "a_la_vez": 2,
         "escuadrones": [("escudero", 1, "flanco"), ("enjambre", 1, "lluvia"), ("escudero", 2, "pinza")]},
        {"nombre": "EL PANAL", "objetivo": ("romper", 15, "enjambre"), "a_la_vez": 2,
         "escuadrones": [("enjambre", 2, "pinza"), ("rebotador", 2, "esquinas"), ("ladron", 1, "flanco")]},
        {"nombre": "LA FIEBRE", "objetivo": ("monedas", 30), "a_la_vez": 2, "anomalia": "oro",
         "escuadrones": [("escudero", 1, "lluvia"), ("enjambre", 1, "flanco"), ("embestidor", 2, "pinza")]},
        {"nombre": "EL ASEDIO", "objetivo": ASEDIO, "a_la_vez": 3, "asedio": True,
         "escuadrones": [("enjambre", 2, "pinza"), ("escudero", 2, "lluvia"), ("perseguidor", 3, "cerco"),
                         ("embestidor", 2, "esquinas")]},
    ]

    antes = [
        ("ines", "EL MAR DE AMBAR ES UN PANAL DEL TAMAÑO DE UN SISTEMA SOLAR. CON INSCRIPCIONES. MILLONES."),
        ("alba", "UNA BIBLIOTECA."),
        ("ines", "ESO CREO. Y SEGUN LAS BITACORAS, LA ERRANTE TAMBIEN LLEGO HASTA ACA."),
        ("ines", "TRAEME TODO LO QUE SE PUEDA LEER, ALBA. TODO."),
    ]

    radio = {
        "tramo_1": [
            ("ines", "LOS ESCUDEROS NO SE ROMPEN DE FRENTE. RODEALOS."),
        ],
        "tramo_2": [
            ("alba", "EL PANAL ESTA LLENO DE DRONES."),
            ("ines", "OBRERAS. LLEVAN Y TRAEN PAGINAS... SI ES QUE SON PAGINAS."),
        ],
        "tramo_3": [
            ("ines", "¡FIEBRE DEL ORO! LAS MONEDAS LLUEVEN Y CANTAN TODAS JUNTAS."),
            ("ines", "SI LAS JUNTAS SIN PARAR, EL COMPAS SUENA TAN FUERTE QUE LA RADIO SE ACOPLA.", "!F07"),
        ],
        "tramo_4": [
            ("ines", "¡LA COLMENA SE DEFIENDE!"),
        ],
        "jefe": [
            ("alba", "LA REINA. Y NO PARECE CONTENTA."),
            ("ines", "ROMPE LAS COMPUERTAS. Y ALBA... LAS ABEJAS SON BIBLIOTECARIAS. NO SON SOLDADOS.", "!F08"),
        ],
    }

    despues = [
        ("ines", "ALBA... CON LO QUE TRAJISTE, EL COMPAS SE LEE ENTERO."),
        ("alba", "DECILO."),
        ("ines", "SEGUI LAS MONEDAS."),
        ("ines", "Y DESPUES UNA FIRMA EN GLIFOS. NO LA PUEDO LEER.", "!F06"),
        ("ines", "Y DESPUES UNA FIRMA. LA MISMA DE LA MONEDA BLANCA: ALBA.", "F06+F01"),
        ("ines", "Y DESPUES UNA FIRMA. LA LEI CON LA CLAVE DEL COMPAS: DICE ALBA.", "F06+!F01"),
        ("alba", "TODO ESTE VIAJE PARA QUE NOS DIGAN LO QUE YA ESTAMOS HACIENDO."),
        ("ines", "HAY ALGO MAS. EL COMPAS NO SALE DE LA MAREA. SALE DEL ABISMO AZUL. DE UN AGUJERO NEGRO."),
        ("ines", "Y ALBA... LA TRANSMISION QUE CAPTASTE ES LA ULTIMA DE MATEO. DICE TU NOMBRE.", "F07"),
        ("ines", "HACE TRES AÑOS. ANTES DE QUE NOS CONOCIERAMOS.", "F07"),
        ("alba", "...HABRA LEIDO LA FIRMA DE LAS MONEDAS. NADA MAS.", "F07"),
        ("ines", "SI. SERA ESO.", "F07"),
    ]

    fragmentos = [
        Fragmento("F07", "LA ERRANTE 3/3",
                  ["ULTIMA TRANSMISION DE LA ERRANTE. LA CAPTO LA RADIO DE LA ALONDRA CUANDO LAS MONEDAS CANTARON.",
                   "MATEO: ...LLEGAMOS A LA... (ESTATICA) ...ALBA. DECILE A ALBA...",
                   "NADIE EN LA ERRANTE CONOCIA A NINGUNA ALBA."],
                  reaccion=[("mateo", "...LLEGAMOS A LA... (ESTATICA) ...ALBA. DECILE A ALBA..."),
                            ("alba", "¿QUE FUE ESO? ¿DIJO MI NOMBRE?")]),
        Fragmento("F08", "LAS BIBLIOTECARIAS",
                  ["LAS ABEJAS VOLVIERON A CASA Y LA CELDA MAS VIEJA SE ABRIO. ADENTRO, UN POEMA DE LOS CANTORES:",
                   "LA VIMOS LLEGAR UNA VEZ. LA VAMOS A VER LLEGAR OTRA.",
                   "NO TENEMOS MIEDO. YA CONOCEMOS EL CAMINO."],
                  glifo=escribir("OTRA"),
                  reaccion=[("alba", "LAS ABEJAS VOLVIERON A CASA... Y SE ABRIO UNA CELDA. HAY UN TEXTO.")]),
    ]

    secretos = [
        ("racha", "F07", {"monedas": 20}),
        ("jefe_sin_romper", "F08", {"enemigo": "abeja"}),
    ]
