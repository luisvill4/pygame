"""
Mision 2: EL ACORAZADO

NEBULOSA CARMESI (el Acorazado Imperial). La Errante paso por aqui; Ines cuenta quien era
Mateo. Los cañones disparan en compas: son metronomos. Ines traduce la primera palabra: SIGUE.

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
        ("cuadro", "nebulosa_carmesi"),
        ("ines", "LA NEBULOSA CARMESI QUEMA. LITERALMENTE: LA MAREA ESTA CALENTANDO EL GAS."),
        ("cuadro", "foto_vieja"),
        ("alba", "INES. ¿CONOCIAS A ALGUIEN DE LA ERRANTE?"),
        ("ines", "AL CAPITAN. MATEO SAAVEDRA."),
        ("ines", "VIVIMOS JUNTOS SIETE AÑOS. SE FUE A SEGUIR EL COMPAS CUANDO NADIE MAS LO OIA. NI YO."),
        ("cuadro", "alba_sola"),
        ("alba", "...LO SIENTO."),
        ("alba", "YO NO TENGO A NADIE QUE ME ESPERE, INES. POR ESO ME OFRECI."),
        ("ines", "AHORA TIENES. Y NO LO SIENTAS: ENCUENTRA LO QUE EL ENCONTRO. LA ERRANTE PASO POR AQUI."),
    ]

    radio = {
        "tramo_1": [
            ("ines", "ESOS ARIETES FIJAN LA MIRA ANTES DE EMBESTIR. CUANDO LA LINEA SE QUEDA QUIETA, APARTATE."),
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
        ("cuadro", "metronomos"),
        ("ines", "LOS CAÑONES ERAN METRONOMOS. CON SU RITMO PUDE TRADUCIR LA PRIMERA PALABRA DEL COMPAS."),
        ("alba", "¿CUAL?"),
        ("cuadro", "sigue"),
        ("ines", "SIGUE."),
        ("alba", "¿SEGUIR QUE?"),
        ("ines", "TODAVIA NO SE. PERO ALGUIEN SE TOMO MUCHO TRABAJO PARA DECIRNOSLO."),
        ("ines", "EN LA UMBRAL YA LES PUSIMOS NOMBRE A LOS QUE MANDAN EL COMPAS: LOS CANTORES."),
        ("cuadro", "baliza", "F12"),
        ("ines", "LA BALIZA QUE ENCONTRASTE PARPADEA CON ESA MISMA PALABRA. MATEO LA HABIA LEIDO ANTES QUE NADIE.", "F12"),
        ("cuadro", "cuenta_atras", "F04"),
        ("ines", "Y LA BITACORA DE TOMAS DICE QUE LOS CAÑONES SON RELOJES QUE CUENTAN HACIA ATRAS. ¿CUANTO NOS QUEDA?", "F04"),
        ("cuadro", "rumbo_esmeralda"),
        ("alba", "¿Y AHORA?"),
        ("ines", "EL CAMPO ESMERALDA. ALGO PASA CON LAS MONEDAS AHI: SE MUEVEN SOLAS."),
    ]

    fragmentos = [
        Fragmento("F04", "LA ERRANTE 2/3",
                  ["BITACORA DE TOMAS ILIC, NAVEGANTE. DIA 88.",
                   "CONTE LOS DISPAROS DE LOS CAÑONES TODA LA NOCHE. NO SON ARMAS: SON RELOJES.",
                   "Y NO CUENTAN HACIA ADELANTE: CUENTAN HACIA ATRAS, COMO UNA CUENTA REGRESIVA. EN CADA CAÑON HAY UN GLIFO:"],
                  glifo=escribir("ATRAS"),
                  reaccion=[("alba", "EL ULTIMO CAÑON TENIA ALGO ADENTRO... OTRA BITACORA DE LA ERRANTE.")]),
        Fragmento("F12", "LA BALIZA",
                  ["LA BALIZA DE EMERGENCIA DE LA ERRANTE. LLEVA AÑOS ENCENDIDA.",
                   "NO PIDE AYUDA. PARPADEA SIEMPRE LO MISMO, Y TIENE UNA GRABACION DE MATEO:",
                   "AQUI LA ERRANTE. ESTAMOS BIEN. SEGUIMOS. NO NOS ESPEREN."],
                  glifo=escribir("SIGUE"),
                  reaccion=[("alba", "UNA BALIZA DE LA ERRANTE. TODAVIA PARPADEA, A RITMO."),
                            ("ines", "...ES LA VOZ DE MATEO.")]),
    ]

    secretos = [
        ("partes_en_orden", "F04"),
        ("baliza", "F12", {"tramo": 3, "mensaje": "SIGUE"}),
    ]
