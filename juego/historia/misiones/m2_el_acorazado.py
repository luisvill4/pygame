"""
Mision 2: EL ACORAZADO

NEBULOSA CARMESI (el Acorazado Imperial). La Errante paso por aca; Ines cuenta quien era
Mateo. Los cañones disparan en compas: son metronomos. Ines traduce la primera palabra: SEGUI.

Secretos: la segunda bitacora (romper los cañones en orden: un reloj se lee como un libro)
y la baliza de la Errante, que titila en la tormenta.
Que cuenta y que esconde: HISTORIA.md. Como se escribe una mision: historia/mision.py.
"""
from juego.historia.mision import Mision, Fragmento, registrar_mision
from juego.historia.glifos import escribir
from juego.rutas import ASEDIO


@registrar_mision
class ElAcorazado(Mision):
    numero = 2
    titulo = "EL ACORAZADO"
    sector = 2
    lugar = (780, 220)
    ambiente = ("calor", 1)
    plano = "filtro"

    tramos = [
        {"nombre": "LOS ARIETES", "objetivo": ("interceptar", 2), "a_la_vez": 2,
         "escuadrones": [("embestidor", 1, "flanco"), ("perseguidor", 2, "lluvia"), ("embestidor", 2, "pinza")]},
        {"nombre": "LAS OBRERAS", "objetivo": ("romper", 10, "enjambre"), "a_la_vez": 2,
         "escuadrones": [("enjambre", 1, "flanco"), ("rebotador", 2, "esquinas"), ("embestidor", 1, "flanco")]},
        {"nombre": "LA TORMENTA", "objetivo": ("perfectos", 6), "a_la_vez": 2, "anomalia": "tormenta",
         "escuadrones": [("embestidor", 2, "pinza"), ("divisor", 1, "lluvia"), ("enjambre", 1, "flanco")]},
        {"nombre": "EL ASEDIO", "objetivo": ASEDIO, "a_la_vez": 3, "asedio": True,
         "escuadrones": [("embestidor", 2, "pinza"), ("enjambre", 1, "flanco"), ("perseguidor", 3, "cerco"),
                         ("rebotador", 2, "esquinas")]},
    ]

    antes = [
        ("ines", "LA NEBULOSA CARMESI QUEMA. LITERAL: LA MAREA ESTA CALENTANDO EL GAS."),
        ("alba", "INES. ¿CONOCIAS A ALGUIEN DE LA ERRANTE?"),
        ("ines", "AL CAPITAN. MATEO SAAVEDRA."),
        ("ines", "VIVIMOS JUNTOS SIETE AÑOS. SE FUE A SEGUIR EL COMPAS CUANDO NADIE MAS LO OIA. NI YO."),
        ("alba", "...LO SIENTO."),
        ("alba", "YO NO TENGO A NADIE QUE ME ESPERE, INES. POR ESO ME OFRECI."),
        ("ines", "AHORA TENES. Y NO LO SIENTAS: ENCONTRA LO QUE EL ENCONTRO. LA ERRANTE PASO POR ACA."),
    ]

    radio = {
        "tramo_1": [
            ("ines", "ESOS ARIETES FIJAN LA MIRA ANTES DE EMBESTIR. CUANDO LA LINEA SE QUEDA QUIETA, CORRETE."),
        ],
        "tramo_2": [
            ("alba", "UN ENJAMBRE. LO QUE ME FALTABA."),
            ("ines", "VUELAN A COMPAS, COMO SI ALGUIEN LES MARCARA EL PASO."),
        ],
        "tramo_3": [
            ("ines", "TORMENTA SOLAR. LA MAREA EMPUJA A LAS ESTRELLAS Y ESCUPEN FUEGO."),
            ("ines", "...ENTRE LA ESTATICA ME LLEGA UNA BALIZA. MUY DEBIL. ¿LA VES?", "!F12"),
        ],
        "tramo_4": [
            ("ines", "¡VIENEN DE TODOS LADOS! AGUANTA."),
        ],
        "jefe": [
            ("alba", "¿UN ACORAZADO? ¿QUIEN CONSTRUYO ESTO?"),
            ("ines", "ESCUCHA SUS CAÑONES: DISPARAN EN COMPAS. COMO UN RELOJ."),
            ("ines", "MATEO DECIA QUE UN RELOJ SE LEE COMO UN LIBRO. EN ORDEN.", "!F04"),
        ],
    }

    despues = [
        ("ines", "LOS CAÑONES ERAN METRONOMOS. CON SU RITMO PUDE TRADUCIR LA PRIMERA PALABRA DEL COMPAS."),
        ("alba", "¿CUAL?"),
        ("ines", "SEGUI."),
        ("alba", "¿SEGUI QUE?"),
        ("ines", "TODAVIA NO SE. PERO ALGUIEN SE TOMO MUCHO TRABAJO PARA DECIRNOSLO."),
        ("ines", "LA BALIZA QUE ENCONTRASTE TITILA ESA MISMA PALABRA. MATEO LA HABIA LEIDO HACE TRES AÑOS.", "F12"),
        ("ines", "Y LA BITACORA DE TOMAS... DICE QUE LOS RELOJES CUENTAN HACIA ATRAS. NO LO ENTIENDO.", "F04"),
        ("alba", "¿Y AHORA?"),
        ("ines", "EL CAMPO ESMERALDA. ALGO PASA CON LAS MONEDAS AHI: SE MUEVEN SOLAS."),
    ]

    fragmentos = [
        Fragmento("F04", "LA ERRANTE 2/3",
                  ["BITACORA DE TOMAS ILIC, NAVEGANTE. DIA 88.",
                   "CONTE LOS DISPAROS DE LOS CAÑONES TODA LA NOCHE. NO SON ARMAS: SON RELOJES.",
                   "Y NO CUENTAN HACIA ADELANTE. CUENTAN HACIA ATRAS. EN CADA CAÑON HAY UN GLIFO:"],
                  glifo=escribir("ATRAS"),
                  reaccion=[("alba", "EL ULTIMO CAÑON TENIA ALGO ADENTRO... OTRA BITACORA DE LA ERRANTE.")]),
        Fragmento("F12", "LA BALIZA",
                  ["LA BALIZA DE EMERGENCIA DE LA ERRANTE. TRES AÑOS PRENDIDA.",
                   "NO PIDE AYUDA. TITILA SIEMPRE LO MISMO, Y TIENE UNA GRABACION DE MATEO:",
                   "ACA LA ERRANTE. ESTAMOS BIEN. SEGUIMOS. NO NOS ESPEREN."],
                  glifo=escribir("SEGUI"),
                  reaccion=[("alba", "UNA BALIZA DE LA ERRANTE. TODAVIA TITILA, A RITMO."),
                            ("ines", "...ES LA VOZ DE MATEO.")]),
    ]

    secretos = [
        ("partes_en_orden", "F04"),
        ("baliza", "F12", {"tramo": 3, "mensaje": "SEGUI"}),
    ]
