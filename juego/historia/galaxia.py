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
    - VIAJAR cuesta tiempo (tiempo.py): la Alondra no es rapida y la distancia se paga en
      meses. Cerca del Abismo, ademas, las CORRIENTES de la Marea ('corrientes' del sistema)
      la arrastran y cada visita cuesta mas. Una PUERTA MENOR conocida es un atajo: casi no
      cuesta tiempo.
    - Un sistema puede tener un PELIGRO AMBIENTAL ('ambiente': calor, esporas, panal o gravedad,
      con intensidad 1 o 2): para entrar hace falta su MODULO (modulos.py). TODOS los sistemas
      libres tienen uno (pedido del usuario: al principio todo esta bloqueado y se abre
      mejorando la nave); solo la mision 1 esta abierta desde el principio. Estan mezclados por
      el mapa a proposito: cada modulo abre lugares en varias zonas (no es una escalera).
    - Algunos sistemas guardan el PLANO de un modulo ('plano'): se consigue al despejarlos.
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
    # 'ambiente': su peligro ambiental, ("calor", 1) (None = ninguno). 'plano': el del modulo que
    # guarda. 'radio': lo que se dice al llegar (como el de las misiones: {"tramo_1": [...]})
    def __init__(self, id_, nombre, lugar, tipo="libre", corrientes=0, eco=None, puerta=None, radio=None,
                 mision=None, ambiente=None, plano=None):
        self.id = id_
        self.nombre = nombre
        self.lugar = lugar
        self.tipo = tipo
        self.corrientes = corrientes    # años de mas en cada visita (las corrientes del Abismo)
        self.eco = eco
        self.puerta = puerta
        self.radio = radio or {}
        self.mision = mision        # la clase de la mision (si es una mision)
        self.ambiente = ambiente
        self.plano = plano

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
    Sistema("S01", "VEGA DEL SUR", (250, 140), eco="E01", ambiente=("calor", 1), plano="filtro",
            radio={"tramo_1": [("ines", "HAY UNA SONDA VIEJA EN ESE SISTEMA. ES NUESTRA. NADIE LA OYE HACE AÑOS.")]}),
    Sistema("S02", "PIEDRA ROJA", (290, 540), ambiente=("calor", 1)),
    Sistema("S03", "KEPLER", (560, 110), eco="E02", ambiente=("calor", 1), plano="casco_panal",
            radio={"tramo_1": [("ines", "LA ESTACION KEPLER. SE VACIO DE UN DIA PARA EL OTRO. NUNCA SUPIMOS POR QUE.")]}),
    Sistema("S04", "LOS GEMELOS", (600, 500), puerta="S14", ambiente=("calor", 1)),
    Sistema("S05", "BRASA", (920, 540), ambiente=("calor", 2), plano="compensador"),
    Sistema("S06", "ORACULO", (980, 90), eco="E03", ambiente=("calor", 1), plano="compensador",
            radio={"tramo_1": [("ines", "UN PULSAR. LATE UNA VEZ POR SEGUNDO, EXACTO. COMO UN RELOJ.")]}),
    Sistema("S07", "CICLOPE", (1010, 330), puerta="S15", ambiente=("esporas", 1)),
    Sistema("S08", "SEMILLERO", (1340, 110), eco="E04", ambiente=("esporas", 2),
            radio={"tramo_1": [("alba", "ESTE PLANETA... BRILLA COMO UNA MONEDA.")]}),
    Sistema("S09", "ESPORA", (1400, 560), ambiente=("esporas", 1), plano="casco_panal"),
    Sistema("S10", "VIGIA", (1470, 370), eco="E05", ambiente=("panal", 1),
            radio={"tramo_1": [("alba", "HAY UNA MAQUINA QUIETA EN EL MEDIO. ME ESTA MIRANDO.")]}),
    Sistema("S11", "PANAL VIEJO", (1780, 80), ambiente=("panal", 2)),
    Sistema("S12", "MIEL", (1820, 540), eco="E06", ambiente=("esporas", 1),
            radio={"tramo_1": [("ines", "UNA NAVE ENORME A LA DERIVA. LA SEÑAL DICE QUE TIENE TRESCIENTOS AÑOS.")]}),
    Sistema("S13", "CORONA", (1930, 520), corrientes=0.2, ambiente=("calor", 2)),
    Sistema("S14", "ESPEJO", (1700, 600), puerta="S04", ambiente=("esporas", 1)),
    Sistema("S15", "HORIZONTE", (2000, 110), corrientes=0.3, eco="E07", puerta="S07", ambiente=("gravedad", 1),
            radio={"tramo_1": [("ines", "CERCA DEL ABISMO LAS CORRIENTES DESVIAN LAS SEÑALES. A VECES NO LLEGAN NUNCA.")]}),
    Sistema("S16", "UMBRA", (2330, 480), corrientes=0.6, eco="E08", ambiente=("gravedad", 2),
            radio={"tramo_1": [("ines", "ALBA, NO DEBERIAS ESTAR TAN CERCA. ESAS CORRIENTES TE PUEDEN TENER MESES DANDO VUELTAS.")]}),
]


_TODOS = []         # se arman una sola vez: asi cada sistema es siempre el mismo objeto (se compara con "is")


def todos_los_sistemas():
    # Los de SISTEMAS y uno por cada mision (en su lugar)
    if not _TODOS:
        _TODOS.extend(SISTEMAS)
        for clase in misiones_en_orden():
            _TODOS.append(Sistema("M%d" % clase.numero, clase.titulo, clase.lugar, tipo="mision",
                                  corrientes=clase.corrientes, mision=clase, ambiente=clase.ambiente,
                                  plano=clase.plano))
    return list(_TODOS)


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
    # Años que pasan por ir de 'desde' a 'hasta' y jugar ahi: el viaje (o la puerta), mas la
    # estadia y las corrientes del lugar. El IMPULSOR del hangar acorta el viaje
    if unidos_por_puerta(desde, hasta, progreso):
        viaje = PUERTA_ANIOS
    else:
        viaje = distancia(desde, hasta) * VIAJE_ANIOS_POR_PX
        viaje *= 1 - IMPULSOR_DESCUENTO * progreso.hangar.get("impulsor", 0)
    return viaje + ESTADIA_ANIOS + hasta.corrientes
