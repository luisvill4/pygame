"""
Logros: metas que quedan guardadas entre partidas (en progreso.json).

Cada logro tiene una 'condicion': una funcion que recibe la partida y dice si ya se
cumplio. La Partida llama a revisar_logros() cada medio segundo; los nuevos se
anotan en el Progreso (y se guardan) y el HUD muestra la ficha "¡LOGRO!".
Algunos logros desbloquean una nave de otro color (NAVES en config.py).

Para agregar uno: sumarlo a LOGROS con un id unico, nombre (hasta 16 letras),
descripcion (hasta 34) y su condicion.
"""


class Logro:
    def __init__(self, id, nombre, descripcion, condicion):
        self.id = id
        self.nombre = nombre
        self.descripcion = descripcion
        self.condicion = condicion          # funcion(partida) -> True si se cumplio


def _e(partida):
    # Atajo para las condiciones: las estadisticas de la partida
    return partida.estadisticas


LOGROS = [
    Logro("primer_jefe", "PRIMER TROFEO", "VENCE A TU PRIMER JEFE",
          lambda partida: partida.jefes_vencidos >= 1),
    Logro("explorador", "EXPLORADOR", "LLEGA AL SECTOR 3",
          lambda partida: partida.director.numero_sector >= 3),
    Logro("viajero", "VIAJERO", "COMPLETA LOS 5 SECTORES",
          lambda partida: partida.jefes_vencidos >= 5),
    Logro("rango_s", "PERFECCION", "LOGRA RANGO S EN UN SECTOR",
          lambda partida: "S" in _e(partida).rangos),
    Logro("intocable", "INTOCABLE", "CIERRA UN SECTOR SIN RECIBIR GOLPES",
          lambda partida: _e(partida).sectores_limpios >= 1),
    Logro("al_filo", "AL FILO", "10 DASH PERFECTOS EN UNA PARTIDA",
          lambda partida: _e(partida).perfectos >= 10),
    Logro("maestro_roce", "MAESTRO DEL DASH", "30 DASH PERFECTOS EN UNA PARTIDA",
          lambda partida: _e(partida).perfectos >= 30),
    Logro("imparable", "IMPARABLE", "UN COMBO DE 25 MONEDAS",
          lambda partida: partida.mejor_combo >= 25),
    Logro("cazador", "CAZADOR", "DESTRUYE 50 ENEMIGOS EN UNA PARTIDA",
          lambda partida: _e(partida).enemigos >= 50),
    Logro("retador", "RETADOR", "CUMPLE 3 DESAFIOS EN UNA PARTIDA",
          lambda partida: _e(partida).desafios >= 3),
    Logro("coleccionista", "COLECCIONISTA", "RECOGE 20 POWER-UPS EN UNA PARTIDA",
          lambda partida: _e(partida).powerups >= 20),
    Logro("arsenal", "ARSENAL", "ELIGE 6 MEJORAS EN UNA PARTIDA",
          lambda partida: len(_e(partida).mejoras) >= 6),
    Logro("mil", "MIL PUNTOS", "1000 PUNTOS EN UNA PARTIDA",
          lambda partida: partida.puntaje >= 1000),
    Logro("leyenda", "LEYENDA", "5000 PUNTOS EN UNA PARTIDA",
          lambda partida: partida.puntaje >= 5000),
    Logro("valiente", "VALIENTE", "VENCE A UN JEFE EN DIFICIL",
          lambda partida: partida.jefes_vencidos >= 1 and partida.dificultad in ("DIFICIL", "PESADILLA")),
    Logro("sin_piedad", "SIN PIEDAD", "VENCE A UN JEFE EN PESADILLA",
          lambda partida: partida.jefes_vencidos >= 1 and partida.dificultad == "PESADILLA"),
]

LOGROS_POR_ID = {logro.id: logro for logro in LOGROS}


def revisar_logros(partida, progreso):
    # Los logros que se cumplen ahora y todavia no estaban: se guardan y se devuelven
    nuevos = [logro for logro in LOGROS
              if logro.id not in progreso.logros and logro.condicion(partida)]
    for logro in nuevos:
        progreso.desbloquear(logro.id)
    return nuevos
