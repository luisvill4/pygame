"""
La GALAXIA: el mapa del modo historia, que se recorre libre (como el mapa estelar de Starfield).

Un mapa de 2400 x 640 px (mas grande que la pantalla: la camara sigue al cursor) con:
    la ESTACION UMBRAL     la casa, a la izquierda: de ahi sale Alba (e Ines habla desde ahi)
    las MISIONES           los sistemas de la historia (historia/misiones/, cada una en su 'lugar')
    los SISTEMAS LIBRES    los de SISTEMAS: se exploran cuando quieras (exploracion.py)

Reglas del mapa (patron: datos + funciones chicas, para que las use la escena y los tests):
    - el BIOMA (sector) de un sistema sale de la zona donde esta (de izquierda a derecha, los
      cinco sectores en el orden de la historia);
    - el PELIGRO sale de la distancia a la Umbral: cuanto mas lejos, mas dificil (y mas piezas);
    - VIAJAR cuesta tiempo en la Umbral (tiempo.py): la distancia, y en cada visita la
      dilatacion de la 'gravedad' del sistema (cerca del Abismo el tiempo de Alba va mas lento
      que el de afuera). Una PUERTA MENOR conocida es un atajo: casi no cuesta tiempo.
Para agregar un sistema: una linea en SISTEMAS (y si guarda un eco, el eco en ecos.py).
"""
import math

from juego.config import (SECTORES, PELIGRO_CADA_PX, VIAJE_ANIOS_POR_PX, ESTADIA_ANIOS, PUERTA_ANIOS,
                          IMPULSOR_DESCUENTO)
from juego.historia.mision import misiones_en_orden
from juego.historia import misiones  # noqa: F401  (registra las misiones: cada una es un sistema)

ANCHO_GALAXIA, ALTO_GALAXIA = 2400, 640
UMBRAL = "UMBRAL"
# Donde empieza cada bioma (x): Cinturon, Nebulosa, Esmeralda, Ambar y Abismo
ZONAS = [0, 560, 980, 1420, 1880]


class Sistema:
    # Un punto del mapa. 'tipo': "umbral", "mision" o "libre". 'eco': el id del eco que guarda
    # (ecos.py). 'puerta': con que otro sistema esta unido por una puerta menor (un atajo).
    # 'radio': lo que se dice al llegar (como el de las misiones: {"tramo_1": [...]})
    def __init__(self, id_, nombre, lugar, tipo="libre", gravedad=0, eco=None, puerta=None, radio=None,
                 mision=None):
        self.id = id_
        self.nombre = nombre
        self.lugar = lugar
        self.tipo = tipo
        self.gravedad = gravedad
        self.eco = eco
        self.puerta = puerta
        self.radio = radio or {}
        self.mision = mision        # la clase de la mision (si es una mision)

    @property
    def sector(self):
        # El numero de bioma (1 a 5): el de la mision, o el de la zona donde esta
        if self.mision is not None:
            return self.mision.sector
        return sum(1 for desde in ZONAS if self.lugar[0] >= desde)

    @property
    def bioma(self):
        return SECTORES[self.sector - 1]


SISTEMAS = [
    Sistema(UMBRAL, "ESTACION UMBRAL", (120, 320), tipo="umbral"),
    Sistema("S01", "VEGA DEL SUR", (250, 140), eco="E01",
            radio={"tramo_1": [("ines", "HAY UNA SONDA VIEJA EN ESE SISTEMA. ES NUESTRA. NADIE LA OYE HACE AÑOS.")]}),
    Sistema("S02", "PIEDRA ROJA", (290, 540)),
    Sistema("S03", "KEPLER", (560, 110), eco="E02",
            radio={"tramo_1": [("ines", "LA ESTACION KEPLER. SE VACIO DE UN DIA PARA EL OTRO. NUNCA SUPIMOS POR QUE.")]}),
    Sistema("S04", "LOS GEMELOS", (600, 500), puerta="S14"),
    Sistema("S05", "BRASA", (920, 540)),
    Sistema("S06", "ORACULO", (980, 90), eco="E03",
            radio={"tramo_1": [("ines", "UN PULSAR. LATE UNA VEZ POR SEGUNDO, EXACTO. COMO UN RELOJ.")]}),
    Sistema("S07", "CICLOPE", (1010, 330), puerta="S15"),
    Sistema("S08", "SEMILLERO", (1340, 110), eco="E04",
            radio={"tramo_1": [("alba", "ESTE PLANETA... BRILLA COMO UNA MONEDA.")]}),
    Sistema("S09", "ESPORA", (1400, 560)),
    Sistema("S10", "VIGIA", (1470, 370), eco="E05",
            radio={"tramo_1": [("alba", "HAY UNA MAQUINA QUIETA EN EL MEDIO. ME ESTA MIRANDO.")]}),
    Sistema("S11", "PANAL VIEJO", (1780, 80)),
    Sistema("S12", "MIEL", (1820, 540), eco="E06",
            radio={"tramo_1": [("ines", "UNA NAVE ENORME A LA DERIVA. LA SEÑAL DICE QUE TIENE TRESCIENTOS AÑOS.")]}),
    Sistema("S13", "CORONA", (1930, 520), gravedad=0.2),
    Sistema("S14", "ESPEJO", (1700, 600), puerta="S04"),
    Sistema("S15", "HORIZONTE", (2000, 110), gravedad=0.3, eco="E07", puerta="S07",
            radio={"tramo_1": [("ines", "CERCA DEL ABISMO LOS MENSAJES TARDAN AÑOS EN LLEGAR. A VECES SE QUEDAN.")]}),
    Sistema("S16", "UMBRA", (2330, 480), gravedad=0.6, eco="E08",
            radio={"tramo_1": [("ines", "ALBA, NO DEBERIAS ESTAR TAN CERCA. CADA MINUTO AHI SON SEMANAS ACA.")]}),
]


def todos_los_sistemas():
    # Los de SISTEMAS y uno por cada mision (en su lugar), por id
    sistemas = list(SISTEMAS)
    for clase in misiones_en_orden():
        sistemas.append(Sistema("M%d" % clase.numero, clase.titulo, clase.lugar, tipo="mision",
                                gravedad=clase.gravedad, mision=clase))
    return sistemas


def sistema(id_):
    return next(uno for uno in todos_los_sistemas() if uno.id == id_)


# ---------- Las reglas del mapa ----------

def distancia(desde, hasta):
    return math.hypot(hasta.lugar[0] - desde.lugar[0], hasta.lugar[1] - desde.lugar[1])


def peligro(uno):
    # De 1 (al lado de casa) a 5 (el Abismo)
    return max(1, min(5, 1 + int(distancia(sistema(UMBRAL), uno) // PELIGRO_CADA_PX)))


def unidos_por_puerta(desde, hasta, progreso):
    # ¿Hay una puerta menor conocida entre los dos? (se conoce al despejar uno de sus lados)
    return (desde.puerta == hasta.id and (desde.id in progreso.puertas or hasta.id in progreso.puertas))


def costo_viaje(desde, hasta, progreso):
    # Años que pasan en la Umbral por ir de 'desde' a 'hasta' y jugar ahi: el viaje (o la
    # puerta), mas la estadia y la dilatacion del lugar. El IMPULSOR del hangar acorta el viaje
    if unidos_por_puerta(desde, hasta, progreso):
        viaje = PUERTA_ANIOS
    else:
        viaje = distancia(desde, hasta) * VIAJE_ANIOS_POR_PX
        viaje *= 1 - IMPULSOR_DESCUENTO * progreso.hangar.get("impulsor", 0)
    return viaje + ESTADIA_ANIOS + hasta.gravedad
