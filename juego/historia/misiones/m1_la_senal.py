"""
Mision 1: LA SEÑAL

CINTURON EXTERIOR (el Ojo). Se aprende a esquivar y despues a romper. Las monedas
reaccionan al compas; el Ojo es una lente que mira siempre al mismo punto.

Secretos: la moneda grabada (la firma: ALBA), la primera bitacora de la Errante y la mirada
del Ojo (la brujula que se usa en la mision 5).
Que cuenta y que esconde: HISTORIA.md. Como se escribe una mision: historia/mision.py.
"""
from juego.historia.mision import Mision, Fragmento, registrar_mision
from juego.historia.glifos import escribir
from juego.rutas import ASEDIO


@registrar_mision
class LaSenal(Mision):
    numero = 1
    titulo = "LA SEÑAL"
    sector = 1
    lugar = (150, 300)

    tramos = [
        {"nombre": "EL CINTURON", "objetivo": ("monedas", 10), "a_la_vez": 1,
         "escuadrones": [("perseguidor", 1, "flanco"), ("perseguidor", 2, "pinza"), ("perseguidor", 2, "lluvia")]},
        {"nombre": "ESPORAS", "objetivo": ("romper", 3, "divisor"), "a_la_vez": 2,
         "escuadrones": [("divisor", 1, "flanco"), ("perseguidor", 2, "pinza"), ("divisor", 1, "lluvia")]},
        {"nombre": "LA GRIETA", "objetivo": ("monedas", 12), "a_la_vez": 2, "anomalia": "asteroides",
         "escuadrones": [("rebotador", 2, "esquinas"), ("divisor", 1, "flanco"), ("perseguidor", 2, "pinza")]},
        {"nombre": "EL ASEDIO", "objetivo": ASEDIO, "a_la_vez": 3, "asedio": True,
         "escuadrones": [("perseguidor", 2, "pinza"), ("rebotador", 2, "esquinas"), ("divisor", 1, "lluvia"),
                         ("perseguidor", 3, "cerco")]},
    ]

    antes = [
        ("ines", "ALBA, ¿ME ESCUCHAS? ACA ESTACION UMBRAL. EL COMPAS VOLVIO A SONAR ESTA MAÑANA. MAS FUERTE QUE NUNCA."),
        ("alba", "BUEN DIA PARA VOS TAMBIEN, INES."),
        ("ines", "LA MAREA SIGUE EN CAMINO. SEIS AÑOS. NO LA PODEMOS FRENAR Y NO HAY A DONDE ESCAPAR."),
        ("ines", "PERO EL COMPAS NO ES RUIDO: ALGUIEN LO PUSO AHI. Y TODO EMPIEZA EN EL CINTURON EXTERIOR."),
        ("ines", "AHI ESTAN LAS MONEDAS. JUNTA TODAS LAS QUE PUEDAS: EL COMPAS SALE DE ELLAS."),
        ("alba", "PERSEGUIR MONEDAS EN EL FIN DEL MUNDO. ME ENCANTA. ALONDRA LISTA, DESPEGO."),
    ]

    radio = {
        "tramo_1": [
            ("ines", "LOS CENTINELAS NO TE QUIEREN MATAR. TE QUIEREN LEJOS DE LAS MONEDAS."),
            ("alba", "MALA SUERTE PARA ELLOS."),
        ],
        "tramo_2": [
            ("alba", "ESAS MASAS VERDES SE PARTEN... ¿ESTAN VIVAS?"),
            ("ines", "SON ESPORAS. ROMPELAS CON EL DASH."),
            ("ines", "Y MIRA LAS MONEDAS DE CERCA: TODAS TIENEN UN SIMBOLO GRABADO.", "!F01"),
        ],
        "tramo_3": [
            ("ines", "EL ESPACIO SE DOBLA. ES LA MAREA: YA SE SIENTE DESDE ACA."),
            ("ines", "HAY ALGO EN EL FONDO, ENTRE LAS ROCAS... NO. NADA. SEGUI.", "!F02"),
        ],
        "tramo_4": [
            ("ines", "MUCHAS SEÑALES DE GOLPE. ¡AGUANTA, ALBA!"),
        ],
        "jefe": [
            ("alba", "ESO ES UN OJO. UN OJO DEL TAMAÑO DE UNA LUNA."),
            ("ines", "ES UNA LENTE. Y NO TE MIRA A VOS: MIRA MAS ALLA. PEGALE CUANDO SE CANSE."),
            ("ines", "SI SALIS SIN UN RASGUÑO, PUEDO MEDIR A DONDE APUNTA.", "!F03"),
        ],
    }

    despues = [
        ("ines", "LO LOGRASTE. Y ESCUCHA ESTO: EL COMPAS CAMBIO. TIENE UNA NOTA NUEVA."),
        ("alba", "¿Y QUE DICE?"),
        ("ines", "TODAVIA NADA QUE PUEDA LEER. PERO APUNTA A LA NEBULOSA CARMESI."),
        ("ines", "ESA MONEDA BLANCA QUE TRAJISTE TIENE EL SIMBOLO DE TODAS, PERO GRANDE. COMO UNA FIRMA.", "F01"),
        ("alba", "Y ENCONTRE RESTOS DE UNA NAVE. TENIAN UNA BITACORA.", "F02"),
        ("ines", "...ES DE LA ERRANTE. LA ESCRIBIO ROCIO, SU INGENIERA.", "F02"),
        ("ines", "LA ERRANTE PASO POR AHI HACE TRES AÑOS. SIGUIENDO EL COMPAS, IGUAL QUE VOS."),
        ("alba", "LA ERRANTE NO VOLVIO, INES."),
        ("ines", "YA SE. POR ESO VAS VOS."),
    ]

    fragmentos = [
        Fragmento("F01", "LA MONEDA GRABADA",
                  ["UNA MONEDA MAS PESADA QUE LAS DEMAS. GIRA LENTO, COMO SI NO QUISIERA IRSE.",
                   "EL SIMBOLO QUE TODAS TIENEN CHIQUITO, ESTA LO TIENE GRANDE. INES CREE QUE ES UNA FIRMA."],
                  glifo=escribir("ALBA"),
                  reaccion=[("alba", "ESTA MONEDA ES DISTINTA. TIENE UN DIBUJO GRABADO. LA GUARDO.")]),
        Fragmento("F02", "LA ERRANTE 1/3",
                  ["BITACORA DE ROCIO VEGA, INGENIERA DE LA ERRANTE. DIA 41.",
                   "LAS MONEDAS CANTAN CUANDO LAS JUNTAS RAPIDO, UNA DETRAS DE OTRA. MATEO DICE QUE ES EL CASCO.",
                   "NO ES EL CASCO."],
                  reaccion=[("alba", "RESTOS DE UNA NAVE... TIENEN UNA BITACORA. LA GUARDO.")]),
        Fragmento("F03", "LA MIRADA DEL OJO",
                  ["INES MIDIO LA LENTE DEL OJO: NO APUNTABA A LA ALONDRA.",
                   "APUNTABA AL ABISMO AZUL, AL OTRO LADO DEL MAPA. SIEMPRE AL MISMO PUNTO.",
                   "COMO UNA BRUJULA."],
                  reaccion=[("ines", "ALBA, MIRA LOS DATOS DE LA LENTE. NO TE APUNTABA A VOS.")]),
    ]

    secretos = [
        ("moneda_grabada", "F01", {"monedas": 15, "desde_tramo": 2,
                                   "pista": [("alba", "¿Y ESA MONEDA BLANCA?")]}),
        ("restos", "F02", {"tramo": 3}),
        ("jefe_sin_golpes", "F03"),
    ]
