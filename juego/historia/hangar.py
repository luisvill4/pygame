"""
El HANGAR de la Alondra: mejoras para siempre, que se compran con PIEZAS (progreso.piezas).

Las piezas salen de jugar en la galaxia: los creditos de cada partida de la historia (las
monedas) se vuelven piezas (PIEZAS_POR_CREDITO), y despejar un sistema libre por primera vez da
mas cuanto mas peligroso es. Repetir un sistema da solo lo de las monedas: farmear se puede,
pero cada salida gasta tiempo en la Umbral. Si la nave explota, Ines rescata la mitad.

Cada instalacion tiene niveles (sus precios en HANGAR_PRECIOS, config.py):
    impulsor    acorta los viajes (tiempo.py: menos años en la Umbral)
    el resto    son las cartas del Taller (mejoras.py), puestas desde el despegue: al empezar
                cada partida de la historia, se suman como si las hubieras elegido
Asi el Taller y el hangar comparten las mismas reglas (patron: reusar, no copiar).
"""
from juego.config import HANGAR_PRECIOS, PIEZAS_POR_PELIGRO, PIEZAS_POR_CREDITO, IMPULSOR_DESCUENTO, AMARILLO
from juego.mejoras import TIPOS_MEJORA

ORDEN = ["impulsor", "corazon", "recarga", "combo", "atraccion", "motor"]

ICONO_IMPULSOR = [".XXX...", "X...X..", "X.X.XXX", "X...X..", ".XXX...", "..X....", ".X.X..."]


class Instalacion:
    # Lo que se muestra en la carta del hangar
    def __init__(self, tipo, nombre, descripcion, color, icono):
        self.tipo, self.nombre, self.descripcion, self.color, self.icono = tipo, nombre, descripcion, color, icono

    @property
    def precios(self):
        return HANGAR_PRECIOS[self.tipo]

    @property
    def maximo(self):
        return len(self.precios)


def instalaciones():
    # Las del hangar, en orden: el impulsor y las cartas del Taller que se pueden instalar
    lista = [Instalacion("impulsor", "IMPULSOR", ["LOS VIAJES GASTAN", "%d%% MENOS AÑOS" % round(IMPULSOR_DESCUENTO * 100)], AMARILLO,
                         ICONO_IMPULSOR)]
    for tipo in ORDEN[1:]:
        mejora = TIPOS_MEJORA[tipo]
        lista.append(Instalacion(tipo, mejora.nombre, mejora.descripcion, mejora.color, mejora.icono))
    return lista


def nivel(progreso, tipo):
    return progreso.hangar.get(tipo, 0)


def precio(progreso, tipo):
    # Lo que cuesta el nivel siguiente (None: ya esta al maximo)
    precios = HANGAR_PRECIOS[tipo]
    actual = nivel(progreso, tipo)
    return precios[actual] if actual < len(precios) else None


def comprar(progreso, tipo):
    # Devuelve True si se pudo
    costo = precio(progreso, tipo)
    if costo is None or progreso.piezas < costo:
        return False
    progreso.piezas -= costo
    progreso.hangar[tipo] = nivel(progreso, tipo) + 1
    progreso.guardar()
    return True


def instalar(partida, progreso):
    # Al empezar una partida de la historia: las cartas compradas, como si las hubieras elegido
    for tipo in ORDEN[1:]:
        for _ in range(nivel(progreso, tipo)):
            partida.sumar_mejora(tipo)


def cobrar(progreso, partida, cumplida, peligro=0):
    # Al terminar: los creditos se vuelven piezas (la mitad si exploto); 'peligro' es el del
    # sistema libre despejado por primera vez (si no, 0). Devuelve las piezas ganadas
    piezas = round(partida.creditos * PIEZAS_POR_CREDITO)
    if not cumplida:
        piezas //= 2
    else:
        piezas += PIEZAS_POR_PELIGRO * peligro
    progreso.piezas += piezas
    progreso.guardar()
    return piezas
