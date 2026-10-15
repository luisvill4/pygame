"""
Mision 1: LA SEÑAL

CINTURON EXTERIOR (el Ojo). Se aprende a esquivar y despues a romper. Las monedas
reaccionan al compas; el Ojo es una lente que mira siempre al mismo punto.

Que cuenta y que esconde: HISTORIA.md. Como se escribe una mision: historia/mision.py.
"""
from juego.historia.mision import Mision, Fragmento, registrar_mision


@registrar_mision
class LaSenal(Mision):
    numero = 1
    titulo = "LA SEÑAL"
    sector = 1

    antes = [
        ("ines", "ALBA, ¿ME ESCUCHAS? EL COMPAS VOLVIO A SONAR ESTA MAÑANA. MAS FUERTE QUE NUNCA."),
        ("alba", "¿Y LA MAREA? ¿SIGUE VINIENDO?"),
        ("ines", "SEIS AÑOS. NADA LA FRENA. PERO ALGUIEN NOS DEJO UN CAMINO, Y EMPIEZA EN EL CINTURON."),
        ("ines", "ALLA ESTAN LAS MONEDAS. JUNTA TODAS LAS QUE PUEDAS: EL COMPAS SALE DE ELLAS."),
        ("alba", "PERSEGUIR MONEDAS EN EL FIN DEL MUNDO. ME ENCANTA. DESPEGO."),
    ]

    radio = {
        "tramo_1": [
            ("ines", "LOS CENTINELAS NO TE QUIEREN MATAR. TE QUIEREN LEJOS."),
        ],
        "tramo_2": [
            ("alba", "ESAS MASAS VERDES SE PARTEN... ¿ESTAN VIVAS?"),
            ("ines", "ESPORAS. ROMPELAS CON EL DASH."),
        ],
        "tramo_3": [
            ("ines", "EL ESPACIO SE DOBLA. ES LA MAREA: YA SE SIENTE DESDE ACA."),
        ],
        "tramo_4": [
            ("ines", "MUCHAS SEÑALES DE GOLPE. ¡AGUANTA, ALBA!"),
        ],
        "jefe": [
            ("alba", "ESO ES UN OJO. UN OJO DEL TAMAÑO DE UNA LUNA."),
            ("ines", "ES UNA LENTE. ESTA MIRANDO ALGO... PEGALE CUANDO SE CANSE."),
        ],
    }

    despues = [
        ("ines", "LO LOGRASTE. Y ESCUCHA ESTO: EL COMPAS CAMBIO. TIENE UNA NOTA NUEVA."),
        ("alba", "¿Y QUE DICE?"),
        ("ines", "TODAVIA NADA. PERO APUNTA A LA NEBULOSA CARMESI. AHI FUE LA ERRANTE, HACE TRES AÑOS."),
        ("alba", "LA ERRANTE NO VOLVIO, INES."),
        ("ines", "YA SE. POR ESO VAS VOS."),
    ]

    fragmentos = [
        Fragmento("F01", "LA MONEDA GRABADA",
                  ["UNA MONEDA MAS PESADA QUE LAS DEMAS. GIRA LENTO, COMO SI NO QUISIERA IRSE.",
                   "TIENE UN GLIFO GRABADO. INES: EL MISMO SIMBOLO ESTA EN TODAS, MAS CHICO. ¿UNA FIRMA?"],
                  glifo=".- .-.. -... .-",
                  reaccion=[("alba", "ESTA MONEDA ES DISTINTA. TIENE UN DIBUJO GRABADO. LA GUARDO.")]),
        Fragmento("F02", "LA ERRANTE 1/3",
                  ["DIA 41. LAS MONEDAS CANTAN CUANDO LAS JUNTAS RAPIDO, UNA DETRAS DE OTRA.",
                   "MATEO DICE QUE ES EL CASCO, QUE VIBRA. NO ES EL CASCO."],
                  reaccion=[("alba", "RESTOS DE UNA NAVE... TIENEN UNA BITACORA. LA GUARDO.")]),
        Fragmento("F03", "LA MIRADA DEL OJO",
                  ["LA LENTE NO APUNTABA A LA ALONDRA. APUNTABA AL ABISMO.",
                   "SIEMPRE AL MISMO PUNTO. COMO UNA BRUJULA."],
                  reaccion=[("ines", "ALBA, MIRA LOS DATOS DE LA LENTE. NO TE APUNTABA A VOS.")]),
    ]

    secretos = [
        ("moneda_grabada", "F01", {"monedas": 15, "desde_tramo": 2}),
        ("restos", "F02", {"tramo": 3}),
        ("jefe_sin_golpes", "F03"),
    ]
