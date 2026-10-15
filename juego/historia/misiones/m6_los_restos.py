"""
Mision 6 (oculta): LOS RESTOS

Aparece en el mapa estelar al encontrar las tres bitacoras de la Errante (F02, F04 y F07):
con ellas Ines calcula donde se partio la nave. Una mision tranquila, sin jefe, al borde
del Abismo: los rebotadores (capsulas de memoria) repiten el ultimo segundo de la Errante y
la radio de los restos todavia reproduce el diario de Mateo.

Secretos: la caja negra (el ultimo registro: entraron a la puerta) y otra moneda grabada,
en la estela de la capsula, con una firma distinta: MATEO (se lee con la clave del compas).
Que cuenta y que esconde: HISTORIA.md. Como se escribe una mision: historia/mision.py.
"""
from juego.historia.mision import Mision, Fragmento, registrar_mision
from juego.historia.glifos import escribir


@registrar_mision
class LosRestos(Mision):
    numero = 6
    titulo = "LOS RESTOS"
    sector = 5
    lugar = (1010, 190)
    jefe = False
    oculta = True
    requisitos = ["F02", "F04", "F07"]
    rama_de = 5

    tramos = [
        {"nombre": "CEMENTERIO", "objetivo": ("monedas", 12), "a_la_vez": 1,
         "escuadrones": [("rebotador", 1, "flanco"), ("rebotador", 1, "esquinas")]},
        {"nombre": "EL CASCO", "objetivo": ("monedas", 14), "a_la_vez": 1,
         "escuadrones": [("rebotador", 2, "esquinas"), ("perseguidor", 2, "pinza")]},
        {"nombre": "LA CAJA NEGRA", "objetivo": ("monedas", 14), "a_la_vez": 1, "anomalia": "asteroides",
         "escuadrones": [("rebotador", 2, "esquinas")]},
        {"nombre": "LA ESTELA", "objetivo": ("monedas", 16), "a_la_vez": 1,
         "escuadrones": [("rebotador", 1, "flanco"), ("perseguidor", 1, "lluvia")]},
    ]

    antes = [
        ("ines", "ALBA. JUNTE LAS TRES BITACORAS Y CALCULE DONDE SE PARTIO LA ERRANTE."),
        ("ines", "ESTA AL BORDE DEL ABISMO, CERCA DE LA PUERTA. NADIE MAS LO SABE."),
        ("alba", "¿QUERES QUE VAYA?"),
        ("ines", "QUIERO SABER QUE LE PASO. NADA MAS. SIN GUARDIANES, SIN PELEAS. SOLO RESTOS."),
        ("alba", "VOY. Y LO QUE ENCUENTRE, TE LO TRAIGO."),
    ]

    radio = {
        "tramo_1": [
            ("mateo", "DIARIO DE A BORDO, DIA 1. INES DICE QUE ESTOY LOCO. PUEDE SER. PERO EL COMPAS ES REAL."),
            ("alba", "...ES SU VOZ. LA RADIO DE LOS RESTOS SIGUE ANDANDO."),
        ],
        "tramo_2": [
            ("mateo", "DIA 203. ROCIO DICE QUE LAS MONEDAS CANTAN. TOMAS, QUE LOS CAÑONES CUENTAN HACIA ATRAS."),
            ("mateo", "YO SOLO QUIERO VOLVER A CASA Y CONTARSELO A INES."),
        ],
        "tramo_3": [
            ("mateo", "DIA 377. LA MAREA NOS ALCANZO. EL CASCO NO AGUANTA. LA PUERTA ESTA AHI NOMAS."),
            ("alba", "LOS REBOTADORES REPITEN UN SEGUNDO... EL ULTIMO DE LA ERRANTE.", "!F10"),
        ],
        "tramo_4": [
            ("ines", "ALBA, ESTAS SIGUIENDO UNA ESTELA. ALGO SALIO DE LA ERRANTE HACIA LA PUERTA."),
        ],
    }

    despues = [
        ("alba", "RECORRI TODO. LA ERRANTE SE PARTIO EN TRES. NO HAY NADIE ADENTRO."),
        ("ines", "¿NADIE?"),
        ("alba", "NADIE. FALTA LA CAPSULA DE ESCAPE."),
        ("ines", "ESCUCHE LA CAJA NEGRA. ENTRARON, ALBA. ENTRARON A LA PUERTA.", "F10"),
        ("ines", "NO SE SI ESO ES BUENO O MALO. PERO EL DIJO QUE NO ES UN FINAL.", "F10"),
        ("ines", "ENTONCES SE FUERON. A ALGUN LADO.", "!F10"),
        ("alba", "Y HABIA OTRA MONEDA BLANCA EN LA ESTELA. CON OTRA FIRMA.", "F13"),
        ("ines", "LA MIRE CON LA CLAVE. DICE... NO. NO PUEDE SER.", "F13+F06"),
        ("ines", "NO LA PUEDO LEER. TODAVIA.", "F13+!F06"),
        ("ines", "GRACIAS, ALBA. DE VERDAD."),
    ]

    fragmentos = [
        Fragmento("F10", "EL ULTIMO REGISTRO",
                  ["CAJA NEGRA DE LA ERRANTE. ULTIMO REGISTRO DE MATEO SAAVEDRA:",
                   "LA NAVE NO AGUANTA. ROCIO Y TOMAS YA ESTAN EN LA CAPSULA. LA PUERTA ESTA A MIL KILOMETROS. VAMOS A ENTRAR.",
                   "INES, SI ESCUCHAS ESTO: NO ES UN FINAL. SEGUI LAS MONEDAS."],
                  reaccion=[("mateo", "INES, SI ESCUCHAS ESTO: NO ES UN FINAL. SEGUI LAS MONEDAS."),
                            ("ines", "...MATEO.")]),
        Fragmento("F13", "LA OTRA FIRMA",
                  ["UNA MONEDA GRABADA, COMO LA DEL CINTURON. EN LA ESTELA DE LA CAPSULA, RUMBO A LA PUERTA.",
                   "PERO LA FIRMA ES OTRA: MAS CORTA, TORPE. COMO HECHA A MANO."],
                  glifo=escribir("MATEO"),
                  reaccion=[("alba", "OTRA MONEDA BLANCA. EL DIBUJO ES DISTINTO... COMO HECHO A MANO.")]),
    ]

    secretos = [
        ("restos", "F10", {"tramo": 3, "pista": [("alba", "AHI VA UN PEDAZO DEL CASCO. LA CAJA NEGRA TIENE QUE ESTAR AHI.")]}),
        ("moneda_grabada", "F13", {"monedas": 6, "desde_tramo": 4,
                                   "pista": [("alba", "¿OTRA MONEDA BLANCA? ¿ACA?")]}),
    ]
