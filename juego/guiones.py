"""
Guiones: la ruta de cada sector, tramo por tramo, escrita a mano (como las fases de un
juego de naves o los niveles de Mega Man). Aca van SOLO datos.

Cada sector tiene 4 TRAMOS y despues el jefe: un tramo por nivel (niveles 1-4, el jefe en
el 5; niveles 6-9, el jefe en el 10...). Cada tramo dice:
    nombre        lo que sale en el cartel al llegar ("TRAMO 2: BLANCO FACIL")
    pista         el consejo debajo del nombre
    escuadrones   los grupos que llegan, en orden: (tipo de enemigo, cuantos, formacion).
                  Si el tramo dura mas que la lista, vuelve a empezar
    a_la_vez      cuantos escuadrones puede haber en pantalla al mismo tiempo
    asedio        (opcional) el tramo es un ASEDIO: hay que aguantar (ver progresion.py)
Las formaciones (por donde entran) estan en escuadrones.py.

Por que un guion y no enemigos al azar: antes la dificultad crecia sumando enemigos, que
aparecian en cualquier lado y no se iban nunca, y la pantalla se "ensuciaba". Asi cada
tramo tiene su idea (presentar un enemigo, encerrarte, una lluvia...) y el siguiente se
siente distinto, no solo mas lleno. Las reglas para escribir uno:
    - Un enemigo NUEVO por tramo como mucho, y nunca en el asedio (se aprende con calma).
    - El tramo 3 trae la anomalia del sector: pocos enemigos, la anomalia es la estrella.
    - El tramo 4 es el asedio: lo que ya conoces, de todos lados a la vez.
Un modo historia puede tener su propio guion con la misma forma (GUIONES["historia"]).
"""

# El tramo 3 de cada sector (el de la anomalia) y el 4 (el asedio) tienen el mismo cartel
INESTABLE = "ZONA INESTABLE"
PISTA_INESTABLE = "EL ESPACIO SE PONE RARO"
PISTA_ASEDIO = "AGUANTA: DESPUES LLEGA EL JEFE"

GUION_ARCADE = [
    # Sector 1: CINTURON EXTERIOR (el Ojo). Se aprende a esquivar y despues a romper
    [
        {"nombre": "PATRULLA", "pista": "ESQUIVALOS Y JUNTA MONEDAS", "a_la_vez": 1,
         "escuadrones": [("perseguidor", 1, "flanco"), ("perseguidor", 2, "pinza"), ("perseguidor", 2, "lluvia")]},
        {"nombre": "BLANCO FACIL", "pista": "¡ROMPELOS CON EL DASH!", "a_la_vez": 2,
         "escuadrones": [("divisor", 1, "flanco"), ("perseguidor", 2, "pinza"), ("divisor", 1, "lluvia")]},
        {"nombre": INESTABLE, "pista": PISTA_INESTABLE, "a_la_vez": 2,
         "escuadrones": [("rebotador", 2, "esquinas"), ("divisor", 1, "flanco"), ("perseguidor", 2, "pinza")]},
        {"nombre": "ASEDIO", "pista": PISTA_ASEDIO, "a_la_vez": 3, "asedio": True,
         "escuadrones": [("perseguidor", 2, "pinza"), ("rebotador", 2, "esquinas"), ("divisor", 1, "lluvia"),
                         ("perseguidor", 3, "cerco")]},
    ],
    # Sector 2: NEBULOSA CARMESI (el Acorazado). Embestidas y el primer enjambre
    [
        {"nombre": "CARGA", "pista": "CORRETE CUANDO FIJA LA MIRA", "a_la_vez": 2,
         "escuadrones": [("embestidor", 1, "flanco"), ("perseguidor", 2, "lluvia"), ("embestidor", 2, "pinza")]},
        {"nombre": "ENJAMBRE", "pista": "CAZALOS DE A UNO", "a_la_vez": 2,
         "escuadrones": [("enjambre", 1, "flanco"), ("rebotador", 2, "esquinas"), ("embestidor", 1, "flanco")]},
        {"nombre": INESTABLE, "pista": PISTA_INESTABLE, "a_la_vez": 2,
         "escuadrones": [("embestidor", 2, "pinza"), ("divisor", 1, "lluvia"), ("enjambre", 1, "flanco")]},
        {"nombre": "ASEDIO", "pista": PISTA_ASEDIO, "a_la_vez": 3, "asedio": True,
         "escuadrones": [("embestidor", 2, "pinza"), ("enjambre", 1, "flanco"), ("perseguidor", 3, "cerco"),
                         ("rebotador", 2, "esquinas")]},
    ],
    # Sector 3: CAMPO ESMERALDA (la Devoradora). Ladrones y divisores
    [
        {"nombre": "SAQUEO", "pista": "¡QUE NO SE LLEVEN LA MONEDA!", "a_la_vez": 2,
         "escuadrones": [("ladron", 1, "flanco"), ("divisor", 2, "pinza"), ("ladron", 1, "lluvia")]},
        {"nombre": "COSECHA", "pista": "PARTILOS EN PEDAZOS", "a_la_vez": 2,
         "escuadrones": [("divisor", 2, "lluvia"), ("embestidor", 1, "flanco"), ("ladron", 1, "flanco")]},
        {"nombre": INESTABLE, "pista": PISTA_INESTABLE, "a_la_vez": 2,
         "escuadrones": [("divisor", 1, "flanco"), ("enjambre", 1, "flanco"), ("rebotador", 2, "esquinas"),
                         ("ladron", 1, "lluvia")]},
        {"nombre": "ASEDIO", "pista": PISTA_ASEDIO, "a_la_vez": 3, "asedio": True,
         "escuadrones": [("divisor", 2, "pinza"), ("perseguidor", 3, "cerco"), ("embestidor", 2, "pinza"),
                         ("ladron", 1, "flanco")]},
    ],
    # Sector 4: MAR DE AMBAR (la Madre del Enjambre). Escuderos y nubes de drones
    [
        {"nombre": "MURALLA", "pista": "ATACALOS POR LA ESPALDA", "a_la_vez": 2,
         "escuadrones": [("escudero", 1, "flanco"), ("enjambre", 1, "lluvia"), ("escudero", 2, "pinza")]},
        {"nombre": "PANAL", "pista": "LLEGAN EN NUBES", "a_la_vez": 2,
         "escuadrones": [("enjambre", 2, "pinza"), ("rebotador", 2, "esquinas"), ("ladron", 1, "flanco")]},
        {"nombre": INESTABLE, "pista": PISTA_INESTABLE, "a_la_vez": 2,
         "escuadrones": [("escudero", 2, "lluvia"), ("enjambre", 1, "flanco"), ("embestidor", 2, "pinza")]},
        {"nombre": "ASEDIO", "pista": PISTA_ASEDIO, "a_la_vez": 3, "asedio": True,
         "escuadrones": [("enjambre", 2, "pinza"), ("escudero", 2, "lluvia"), ("perseguidor", 3, "cerco"),
                         ("embestidor", 2, "esquinas")]},
    ],
    # Sector 5: ABISMO AZUL (el Fin de la Luz). Todo lo aprendido, mezclado
    [
        {"nombre": "CAOS", "pista": "NADA SE QUEDA QUIETO", "a_la_vez": 2,
         "escuadrones": [("rebotador", 3, "esquinas"), ("divisor", 1, "flanco"), ("rebotador", 2, "pinza")]},
        {"nombre": "VANGUARDIA", "pista": "LO MEJOR DEL ENEMIGO", "a_la_vez": 2,
         "escuadrones": [("escudero", 2, "pinza"), ("embestidor", 2, "lluvia"), ("enjambre", 1, "flanco")]},
        {"nombre": INESTABLE, "pista": PISTA_INESTABLE, "a_la_vez": 3,
         "escuadrones": [("perseguidor", 3, "cerco"), ("ladron", 1, "flanco"), ("rebotador", 2, "esquinas"),
                         ("divisor", 2, "lluvia")]},
        {"nombre": "ASEDIO FINAL", "pista": PISTA_ASEDIO, "a_la_vez": 3, "asedio": True,
         "escuadrones": [("enjambre", 2, "pinza"), ("escudero", 2, "lluvia"), ("embestidor", 2, "esquinas"),
                         ("perseguidor", 3, "cerco"), ("divisor", 2, "pinza")]},
    ],
]

GUIONES = {"arcade": GUION_ARCADE}


def tipos_del_guion(guion):
    # Todos los tipos de enemigo que aparecen en un guion
    return {tipo for sector in guion for tramo in sector for tipo, _, _ in tramo["escuadrones"]}
