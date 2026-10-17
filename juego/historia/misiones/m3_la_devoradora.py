"""
Mision 3: LA DEVORADORA

CAMPO ESMERALDA (la Devoradora de Estrellas). Alguien mas junta monedas: los ladrones, que
se las llevan hacia el Abismo. En la niebla, quieta, Alba oye el compas: la clave de los glifos.

Secretos: el cartero (seguir a un ladron sin alcanzarlo: seguir las monedas) y la clave
del compas (quedarse quieta en la niebla hasta oir la palabra entera).
Que cuenta y que esconde: HISTORIA.md. Como se escribe una mision: historia/mision.py.
"""
from juego.historia.mision import Mision, Fragmento, registrar_mision
from juego.historia.glifos import escribir
from juego.rutas import ASEDIO


@registrar_mision
class LaDevoradora(Mision):
    numero = 3
    titulo = "LA DEVORADORA"
    sector = 3
    lugar = (1190, 400)
    ambiente = ("esporas", 1)
    plano = "casco_panal"

    tramos = [
        {"nombre": "EL SAQUEO", "objetivo": ("monedas", 10), "a_la_vez": 2,
         "escuadrones": [("ladron", 1, "flanco"), ("divisor", 2, "pinza"), ("ladron", 1, "lluvia")]},
        {"nombre": "LA COSECHA", "objetivo": ("perfectos", 8), "a_la_vez": 2,
         "escuadrones": [("divisor", 2, "lluvia"), ("embestidor", 1, "flanco"), ("ladron", 1, "flanco")]},
        {"nombre": "LA NIEBLA", "objetivo": ("monedas", 12), "a_la_vez": 1, "anomalia": "niebla",
         "escuadrones": [("divisor", 1, "flanco"), ("rebotador", 1, "esquinas"), ("ladron", 1, "lluvia")]},
        {"nombre": "EL ASEDIO", "objetivo": ASEDIO, "a_la_vez": 3, "asedio": True,
         "escuadrones": [("divisor", 2, "pinza"), ("perseguidor", 3, "cerco"), ("embestidor", 2, "pinza"),
                         ("ladron", 1, "flanco")]},
    ]

    antes = [
        ("ines", "CADA VIAJE TUYO SE NOS COME MESES. NO TE LO RECLAMO... PERO APURATE.", "T3+!T6"),
        ("ines", "EN EL CAMPO ESMERALDA LAS MONEDAS DESAPARECEN ANTES DE QUE LLEGUES."),
        ("alba", "¿OTRO PILOTO?"),
        ("ines", "NO HAY NADIE MAS AHI AFUERA. O NO DEBERIA HABER."),
        ("ines", "Y HAY NIEBLA: ESPORAS TAN DENSAS QUE LA RADIO NO PASA. AHI ADENTRO VAS A ESTAR SOLA."),
        ("alba", "SIEMPRE ESTOY SOLA, INES. VOS SOS UNA VOZ."),
        ("ines", "UNA VOZ QUE TE CUIDA. Y MATEO DECIA QUE EN EL SILENCIO SE ESCUCHA MEJOR EL COMPAS."),
    ]

    radio = {
        "tramo_1": [
            ("alba", "¡EH! ¡ESE SE LLEVO MI MONEDA!"),
            ("ines", "ALCANZALO CON EL DASH ANTES DE QUE SALGA."),
        ],
        "tramo_2": [
            ("alba", "ESPORAS OTRA VEZ. ESTAS SON MAS GRANDES."),
            ("ines", "ESOS LADRONES NO SON PIRATAS. QUIERO SABER A DONDE LLEVAN LAS MONEDAS.", "!F05"),
        ],
        "tramo_3": [
            ("ines", "NIEBLA. NO VEO NADA DESDE ACA. ESTAS SOLA, ALBA."),
        ],
        "tramo_4": [
            ("ines", "¡ALBA! TE PERDI EN LA NIEBLA... ¿ESTAS AHI? ¡VIENEN TODOS!"),
        ],
        "jefe": [
            ("alba", "UNA SERPIENTE QUE SE COME LAS ESTRELLAS. CLARO. ¿POR QUE NO?"),
            ("ines", "SU COLA BRILLA. AHI TIENE EL NUCLEO."),
        ],
    }

    despues = [
        ("ines", "EL RADAR PIERDE A LOS LADRONES EN EL BORDE. PERO TODOS SALEN RUMBO AL MISMO LUGAR: EL ABISMO AZUL."),
        ("alba", "ALGUIEN ESTA JUNTANDO MONEDAS ALLA."),
        ("ines", "O ALGO. ¿Y POR QUE LAS DEJARON DESPARRAMADAS EN PRIMER LUGAR?"),
        ("alba", "NO LAS ROBAN, INES. LAS LLEVAN. COMO CARTEROS.", "F05"),
        ("alba", "INES. EN LA NIEBLA ESCUCHE EL COMPAS: CORTO, LARGO. LOS GLIFOS SON RITMOS.", "F06"),
        ("ines", "...¡CLARO! LOS GLIFOS SE LEEN COMO EL COMPAS. CADA RITMO ES UNA LETRA.", "F06"),
        ("ines", "LA FIRMA DE LA MONEDA BLANCA DICE... ALBA.", "F06+F01"),
        ("alba", "¿COMO YO?", "F06+F01"),
        ("ines", "O COMO EL AMANECER. ALBA TAMBIEN QUIERE DECIR AMANECER. NO TE LO TOMES PERSONAL.", "F06+F01"),
        ("ines", "VOY A PASAR TODO EL ARCHIVO POR ESTA CLAVE.", "F06"),
        ("ines", "LO QUE SIGUE ES EL MAR DE AMBAR. LA ERRANTE IBA PARA ALLA."),
    ]

    fragmentos = [
        Fragmento("F05", "EL CARTERO",
                  ["LO SEGUISTE HASTA EL BORDE DEL CAMPO SIN TOCARLO.",
                   "NO LA ROBO. LA LLEVO: RUMBO AL ABISMO, EN LINEA RECTA, COMO QUIEN VUELVE A CASA.",
                   "EN LA ESPALDA TENIA UN GLIFO GRABADO:"],
                  glifo=escribir("CASA"),
                  reaccion=[("alba", "SE FUE... PERO NO HUYENDO. IBA DERECHO AL ABISMO. COMO UN CARTERO.")]),
        Fragmento("F06", "LA CLAVE DEL COMPAS",
                  ["EN LA NIEBLA NO HAY RUIDO. QUIETA, ALBA LO OYE: CORTO, LARGO. CORTO, LARGO, CORTO, CORTO.",
                   "LOS GLIFOS NO SON DIBUJOS. SON RITMOS: CADA UNO ES UNA LETRA.",
                   "DESDE AHORA, EL ARCHIVO LOS TRADUCE."],
                  reaccion=[("alba", "CORTO, LARGO... ¡ES EL COMPAS! LOS GLIFOS SON RITMOS. SE PUEDEN LEER.")]),
    ]

    secretos = [
        ("seguir_al_ladron", "F05"),
        ("quieto_en_anomalia", "F06", {"anomalia": "niebla", "mensaje": "ALBA"}),
    ]
