"""
Los MODULOS de la Alondra: lo que abre la galaxia (solo en el modo historia).

Cada sistema de la galaxia puede tener un PELIGRO AMBIENTAL (galaxia.py): calor, esporas, panal o
gravedad, con una intensidad (1 o 2). Para entrar hace falta el modulo de ese peligro con ese
nivel o mas. Los peligros estan MEZCLADOS por el mapa (casi todos los de un bioma son el suyo,
pero hay excepciones en todos lados), asi que cada modulo abre lugares en varias zonas y el
orden lo elige el jugador. No es una escalera: es una red.

Para fabricar un modulo hace falta su PLANO, que se encuentra despejando ciertos sistemas (cada
plano esta en mas de un lugar) o al cumplir la mision anterior de la historia (Ines lo diseña
con los datos: asi la historia nunca se traba). Con el plano, cada nivel se compra en el hangar
con piezas (MODULOS_PRECIOS, config.py).

Cada modulo SE VE en la nave: 'piezas' son capas de pixel art (en la grilla de 25x25 pixeles de
arte del sprite de 50x50) que nave.py dibuja encima. Asi la Alondra cambia a medida que la mejoras.
Para un peligro nuevo: un Modulo aqui (con su dibujo) y el peligro en los sistemas que lo tengan.
"""
from juego.config import MODULOS_PRECIOS, ROJO, VERDE, AMARILLO, VIOLETA
from juego.historia import galaxia


class Modulo:
    def __init__(self, id_, nombre, peligro, color, icono, descripcion, piezas):
        self.id = id_
        self.nombre = nombre
        self.peligro = peligro          # el peligro ambiental que deja pasar
        self.color = color
        self.icono = icono              # pixel art de 7x7 (para la carta del hangar)
        self.descripcion = descripcion  # dos renglones cortos
        self.piezas = piezas            # {nivel: [(pixeles, color, solo_sobre_el_casco), ...]}

    @property
    def precios(self):
        return MODULOS_PRECIOS[self.id]

    @property
    def maximo(self):
        return len(self.precios)


def _espejo(pixeles):
    # Los mismos pixeles y su reflejo (la nave es simetrica: 25 columnas, la del medio es la 12)
    return sorted(set(pixeles) | {(24 - columna, fila) for columna, fila in pixeles})


# El borde de ataque del ala izquierda (columna, fila) en el sprite: de la cabina a la punta
BORDE_DEL_ALA = [(8, 11), (7, 12), (6, 13), (5, 14), (4, 15), (3, 16), (2, 17), (1, 18)]
# Un panal ralo en el ala izquierda (sin tocar el fuselaje): una celda cada cuatro, corrida en
# las filas impares, como las celdas de una colmena
PANAL = [(columna, fila) for fila in range(14, 20) for columna in range(9)
         if columna % 4 == (1 if fila % 2 == 0 else 3)]
METAL, METAL_CLARO = (70, 80, 95), (150, 150, 170)

MODULOS = [
    # Placas naranjas sobre el borde de ataque de las alas (y una fila roja mas adentro)
    Modulo("escudo_termico", "ESCUDO TERMICO", "calor", ROJO,
           [".XXXXX.", "XX...XX", "X.X.X.X", "X..X..X", "X.X.X.X", "XX...XX", ".XXXXX."],
           ["AGUANTA EL CALOR", "DE LAS ESTRELLAS"],
           {1: [(_espejo([(columna + 1, fila) for columna, fila in BORDE_DEL_ALA[1:]]), (255, 140, 0), False)],
            2: [(_espejo([(columna + 2, fila) for columna, fila in BORDE_DEL_ALA[2:]]), (190, 40, 20), True)]}),
    # Dos capsulas de metal al lado de la cabina, con su luz verde (mas largas y con dos luces)
    Modulo("filtro", "FILTRO DE ESPORAS", "esporas", VERDE,
           ["..XXX..", ".X...X.", "X.X.X.X", "X..X..X", "X.X.X.X", ".X...X.", "..XXX.."],
           ["RESPIRA ENTRE", "LAS ESPORAS"],
           {1: [(_espejo([(7, 7), (8, 7), (8, 8), (8, 9), (7, 10), (8, 10)]), METAL, False),
                (_espejo([(7, 8), (7, 9)]), (60, 255, 120), False)],
            2: [(_espejo([(7, 6), (8, 6), (7, 11)]), METAL, False),
                (_espejo([(8, 8), (8, 9)]), (200, 255, 210), False)]}),
    # Un panal ralo sobre las alas; despues, una placa dorada en el borde de atras
    Modulo("casco_panal", "CASCO DE PANAL", "panal", AMARILLO,
           [".X.X.X.", "X.X.X.X", ".X.X.X.", "X.X.X.X", ".X.X.X.", "X.X.X.X", ".X.X.X."],
           ["NI LAS OBRERAS", "LO PUEDEN COMER"],
           {1: [(_espejo(PANAL), (250, 210, 50), True)],
            2: [(_espejo([(columna, 20) for columna in range(1, 10)] + [(columna, 21) for columna in range(1, 5)]),
                 (170, 110, 20), True)]}),
    # Un anillo violeta abajo del motor; despues, aletas estabilizadoras en las puntas de las alas
    Modulo("compensador", "COMPENSADOR", "gravedad", VIOLETA,
           ["..XXX..", ".X...X.", "X..X..X", "X.XXX.X", "X..X..X", ".X...X.", "..XXX.."],
           ["RESISTE LA GRAVEDAD", "DE LOS AGUJEROS NEGROS"],
           {1: [(_espejo([(7, 23), (8, 24), (9, 24), (10, 24)]), (190, 120, 255), False)],
            2: [(_espejo([(0, 17), (0, 18), (1, 17)]), (190, 120, 255), False),
                (_espejo([(0, 16)]), (230, 200, 255), False)]}),
]

POR_ID = {modulo.id: modulo for modulo in MODULOS}
POR_PELIGRO = {modulo.peligro: modulo for modulo in MODULOS}

# El impulsor del hangar tambien se ve: toberas al lado del motor (un nivel, una tobera mas)
PIEZAS_IMPULSOR = {1: [(_espejo([(9, 22), (9, 23)]), METAL_CLARO, False)],
                   2: [(_espejo([(10, 23)]), (255, 140, 0), False)],
                   3: [(_espejo([(8, 22), (10, 22)]), (110, 110, 130), False)]}


# ---------- Las reglas ----------

def nivel(progreso, id_modulo):
    return progreso.hangar.get(id_modulo, 0)


def falta(progreso, peligro):
    # Que falta para entrar a un lugar con ese peligro: None (nada) o (modulo, nivel pedido)
    if peligro is None:
        return None
    tipo, intensidad = peligro
    modulo = POR_PELIGRO[tipo]
    return None if nivel(progreso, modulo.id) >= intensidad else (modulo, intensidad)


def tiene_plano(progreso, id_modulo):
    return id_modulo in progreso.planos


def dar_plano(progreso, id_modulo):
    # Al despejar un sistema o cumplir una mision que lo guarda. True si es nuevo (para contarlo)
    if id_modulo is None or id_modulo in progreso.planos:
        return False
    progreso.planos.add(id_modulo)
    progreso.guardar()
    return True


def donde_esta_el_plano(id_modulo):
    # Los lugares que lo guardan: (los biomas de los sistemas libres, las misiones que lo dan)
    biomas, misiones = [], []
    for uno in galaxia.todos_los_sistemas():
        if uno.plano != id_modulo:
            continue
        if uno.mision is not None:
            misiones.append(uno.mision.numero)
        elif uno.bioma["nombre"] not in biomas:
            biomas.append(uno.bioma["nombre"])
    return biomas, misiones


def lo_que_abre(id_modulo, nivel_modulo):
    # Los sistemas (y misiones) que piden justo ese nivel del modulo
    peligro = POR_ID[id_modulo].peligro
    return [uno for uno in galaxia.todos_los_sistemas() if uno.ambiente == (peligro, nivel_modulo)]


def precio(progreso, id_modulo):
    # El del nivel siguiente (None: ya esta al maximo)
    precios = MODULOS_PRECIOS[id_modulo]
    actual = nivel(progreso, id_modulo)
    return precios[actual] if actual < len(precios) else None


def fabricar(progreso, id_modulo):
    # Con el plano y las piezas, un nivel mas. Devuelve True si se pudo
    costo = precio(progreso, id_modulo)
    if not tiene_plano(progreso, id_modulo) or costo is None or progreso.piezas < costo:
        return False
    progreso.piezas -= costo
    progreso.hangar[id_modulo] = nivel(progreso, id_modulo) + 1
    progreso.guardar()
    return True


def equipo(progreso, extra=None):
    # Las capas de pixel art de todo lo instalado (nave.py las dibuja). 'extra' = (id, nivel)
    # suma uno mas para mostrarlo antes de comprarlo (el hangar)
    niveles = {modulo.id: nivel(progreso, modulo.id) for modulo in MODULOS}
    niveles["impulsor"] = progreso.hangar.get("impulsor", 0)
    if extra is not None:
        niveles[extra[0]] = max(niveles.get(extra[0], 0), extra[1])
    capas = []
    for id_, piezas in [(modulo.id, modulo.piezas) for modulo in MODULOS] + [("impulsor", PIEZAS_IMPULSOR)]:
        for nivel_pieza in range(1, niveles[id_] + 1):
            capas.extend(piezas[nivel_pieza])
    return capas
