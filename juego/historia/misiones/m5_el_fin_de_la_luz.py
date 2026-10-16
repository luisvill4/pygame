"""
Mision 5: EL FIN DE LA LUZ

ABISMO AZUL (el Fin de la Luz). El compas sale de la Singularidad: es una puerta. Alba
entra; su ultima frase por radio es el mensaje del compas. Tres dias despues, el compas
suma una palabra: VENGAN. Es el final de la historia (final = True).

Secretos: la brujula (con la mirada del Ojo: pegarle a la puerta desde el lado de casa) y
la Bitacora sin fecha (con todo lo demas encontrado: la verdad, y el final verdadero).
Que cuenta y que esconde: HISTORIA.md. Como se escribe una mision: historia/mision.py.
"""
from juego.historia.mision import Mision, Fragmento, registrar_mision
from juego.historia.glifos import escribir
from juego.rutas import ASEDIO


@registrar_mision
class ElFinDeLaLuz(Mision):
    numero = 5
    titulo = "EL FIN DE LA LUZ"
    sector = 5
    lugar = (2060, 350)
    ambiente = ("gravedad", 2)      # la puerta: el compensador al maximo
    gravedad = 0.5          # al lado del agujero negro: cada visita, medio año mas en la Umbral
    final = True

    tramos = [
        {"nombre": "EL BORDE", "objetivo": ("monedas", 15), "a_la_vez": 2,
         "escuadrones": [("rebotador", 3, "esquinas"), ("divisor", 1, "flanco"), ("rebotador", 2, "pinza")]},
        {"nombre": "LA DESPEDIDA", "objetivo": ("romper", 4, "escudero"), "a_la_vez": 2,
         "escuadrones": [("escudero", 2, "pinza"), ("embestidor", 2, "lluvia"), ("enjambre", 1, "flanco")]},
        {"nombre": "EL COMPAS", "objetivo": ("perfectos", 10), "a_la_vez": 3, "anomalia": "asteroides",
         "escuadrones": [("perseguidor", 3, "cerco"), ("ladron", 1, "flanco"), ("rebotador", 2, "esquinas"),
                         ("divisor", 2, "lluvia")]},
        {"nombre": "ASEDIO FINAL", "objetivo": ASEDIO, "a_la_vez": 3, "asedio": True,
         "escuadrones": [("enjambre", 2, "pinza"), ("escudero", 2, "lluvia"), ("embestidor", 2, "esquinas"),
                         ("perseguidor", 3, "cerco"), ("divisor", 2, "pinza")]},
    ]

    antes = [
        ("ines", "ALBA... LA MAREA YA LLEGO. LA UMBRAL NO EXISTE MAS. TE HABLO DESDE UNA NAVE.", "T6"),
        ("ines", "ES UN AGUJERO NEGRO, ALBA. Y EL COMPAS SALE DE ADENTRO."),
        ("alba", "LO QUE ESTA ADENTRO DE UN AGUJERO NEGRO NO SALE, INES. ES LA REGLA."),
        ("ines", "ESTE SI. Y SE ESTA ABRIENDO. LAS MONEDAS, LOS LADRONES... TODO VA HACIA AHI."),
        ("alba", "ENTONCES VAMOS HACIA AHI."),
        ("ines", "ALBA. GRACIAS POR SEGUIR."),
        ("alba", "NO ME AGRADEZCAS TODAVIA."),
    ]

    radio = {
        "tramo_1": [
            ("ines", "LA GRAVEDAD TE VA A TIRAR. NO PELEES CONTRA ELLA: USALA."),
        ],
        "tramo_2": [
            ("alba", "ESCUDEROS, ARIETES, DRONES... TODOS JUNTOS."),
            ("ines", "ES COMO SI EL CAMINO ENTERO HUBIERA VENIDO A DESPEDIRTE."),
        ],
        "tramo_3": [
            ("cantores", ".- .-.. -... .-"),
            ("ines", "¿ESCUCHASTE? EL COMPAS. NUNCA LO HABIA OIDO TAN CLARO."),
        ],
        "tramo_4": [
            ("ines", "¡ULTIMO EMPUJON, ALBA!"),
        ],
        "jefe": [
            ("alba", "ES... HERMOSO."),
            ("ines", "ALBA. CONCENTRATE."),
            ("ines", "LA LENTE DEL OJO APUNTABA ACA. DESDE EL CINTURON... DESDE CASA.", "F03+!F09"),
        ],
    }

    despues = [
        ("ines", "SE ABRIO. ALBA, LA PUERTA SE ABRIO."),
        ("alba", "LO VEO. ADENTRO HAY... LUZ. Y MONEDAS. MILES."),
        ("ines", "NO SABEMOS QUE HAY DEL OTRO LADO. NO TENES QUE ENTRAR."),
        ("alba", "INES. EL COMPAS DIJO SEGUI LAS MONEDAS. NUNCA DIJO HASTA DONDE."),
        ("alba", "SI NO VUELVO..."),
        ("alba", "SEGUI LAS MONEDAS."),
        ("ines", "¿ALBA? ...¿ALBA?"),
        # A tiempo: hay tiempo para que todos crucen
        ("ines", "TRES DIAS SIN SEÑAL DE LA ALONDRA. PERO EL COMPAS CAMBIO OTRA VEZ.", "!T6"),
        ("ines", "AHORA TERMINA CON UNA PALABRA NUEVA. LA TRADUJE CIEN VECES.", "!T6"),
        ("ines", "DICE: VENGAN.", "!T6"),
        # Tarde: la Marea ya llego a la Umbral
        ("ines", "LA MAREA YA ESTA ACA. LA UMBRAL SE PARTIO. QUEDAMOS POCOS, EN TRES NAVES.", "T6"),
        ("ines", "Y EL COMPAS CAMBIO. TERMINA CON UNA PALABRA NUEVA: VENGAN.", "T6"),
        ("ines", "LLEGAMOS TARDE PARA LOS DEMAS. PERO VAMOS.", "T6"),
        # El final verdadero: con todo encontrado, llega la Bitacora sin fecha
        ("ines", "...Y LLEGO OTRA COSA. UNA GRABACION. NO TIENE FECHA. TIENE MILLONES DE AÑOS.", "F11"),
        ("voz", "INES. SI ESCUCHAS ESTO, YA PASO. TODO.", "F11"),
        ("voz", "DEL OTRO LADO DE LA PUERTA NO HAY MAREA TODAVIA. FALTAN MILLONES DE AÑOS. HAY TIEMPO.", "F11"),
        ("voz", "MATEO LLEGO ANTES QUE YO. ESTA BIEN. DICE QUE TENIAS RAZON CON EL COMPAS.", "F11"),
        ("voz", "GRABAMOS LAS MONEDAS. DESPERTAMOS A LOS GUARDIANES. APRENDIMOS A CANTAR.", "F11"),
        ("voz", "LA MAREA NO SE PUEDE FRENAR. PERO SE PUEDE CRUZAR. VENGAN TODOS.", "F11"),
        ("voz", "SEGUI LAS MONEDAS. LAS DEJAMOS NOSOTROS.", "F11"),
        ("ines", "...NOSOTROS. LOS CANTORES. SIEMPRE FUIMOS NOSOTROS.", "F11"),
        ("ines", "ATENCION, ESTACION UMBRAL. PREPAREN TODAS LAS NAVES.", "F11+!T6"),
        ("ines", "NOS VAMOS.", "F11+!T6"),
        ("ines", "TODOS NO, ALBA. LLEGAMOS TARDE. PERO LOS QUE QUEDAMOS... VAMOS.", "F11+T6"),
    ]

    fragmentos = [
        Fragmento("F09", "LA BRUJULA",
                  ["ALBA LE PEGO A LA PUERTA DESDE EL LADO DE CASA, HACIA DONDE MIRABA EL OJO.",
                   "LOS INSTRUMENTOS SE VOLVIERON LOCOS: EL RELOJ DE LA ALONDRA EMPEZO A CONTAR HACIA ATRAS.",
                   "LA PUERTA NO LLEVA A OTRO LUGAR. LLEVA A OTRO:"],
                  glifo=escribir("CUANDO"),
                  reaccion=[("alba", "¡EL RELOJ! INES, EL RELOJ DE LA ALONDRA VA PARA ATRAS.")]),
        Fragmento("F11", "BITACORA SIN FECHA",
                  ["UNA GRABACION QUE LLEGO DESDE LA PUERTA. SEGUN INES, TIENE MILLONES DE AÑOS.",
                   "LA VOZ ES LA DE ALBA.",
                   "SI ENCONTRAS ESTO, YA LO HICISTE. SEGUI LAS MONEDAS. LAS DEJAMOS NOSOTROS."],
                  reaccion=[("ines", "ALBA... ESTA LLEGANDO ALGO POR EL COMPAS. UNA GRABACION... CON TU VOZ.")],
                  oculto=True),
    ]

    secretos = [
        ("golpe_desde", "F09", {"angulo": 180, "requiere": ["F03"]}),
        ("jefe_vencido", "F11", {"requiere": "todos"}),
    ]
