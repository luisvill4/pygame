"""
Armonia: que los efectos de premio sigan al acorde que suena en la musica.

Como en Rez o Tetris Effect: la moneda no suena siempre en las mismas notas, sino en las
del acorde de ese momento. Asi nunca choca con la musica (antes, sobre el Mi mayor del tema,
cada Sol de la moneda chocaba con el Sol# del acorde).

Como funciona:
- Cada acorde tiene un COLOR: la pentatonica que mejor le queda (5 notas que suenan bien
  con el). Un acorde mayor usa la pentatonica mayor de su fundamental (Do: Do Re Mi Sol La).
  Uno menor, la de su relativo mayor, que tiene las mismas notas (La menor -> la de Do). Uno
  con septima (Do7) cambia la sexta por la septima (Do Re Mi Sol Sib) y uno suspendido
  (Mi sus4) usa la pentatonica mayor de su septima (Re: Re Mi Fa# La Si, sin la tercera).
- Los efectos ARMONICOS se escriben en la pentatonica de Do (Do Re Mi Sol La), como siempre.
  Para cada color, el estudio los vuelve a componer cambiando cada nota por la del mismo
  GRADO en la pentatonica del color: el 1er grado de Do (Do) pasa a ser el 1er grado del
  color, el 2do (Re) el 2do... y en la misma octava (corrido como mucho media octava).
  La escalera de la moneda (cada combo, un grado mas arriba) sigue siendo una escalera.
- componer.py guarda un archivo por color (moneda_1_fa.ogg...) y anota en la ficha de cada
  tema el color de cada compas. El juego sabe en que compas va el tema y elige el archivo
  (juego/sonido.py, color_actual()).
"""
from herramientas.estudio.base import leer_acorde

PENTATONICA_DE_DO = [0, 2, 4, 7, 9]         # Do Re Mi Sol La: en lo que se escriben los efectos

# Las formas de pentatonica (semitonos desde la fundamental del color)
FORMAS = {
    "mayor": [0, 2, 4, 7, 9],           # Do Re Mi Sol La
    "dominante": [0, 2, 4, 7, 10],      # Do Re Mi Sol Sib (para los acordes con septima: Do7)
    # Para Mi sus4 (sin tercera): Re Mi Fa# La Si. Son las mismas notas que Mi Fa# La Si Re,
    # pero contadas desde Re: es la pentatonica MAYOR de Re, asi un efecto suena igual que en Do,
    # un tono mas arriba. Contadas desde Mi, la tercera Mi-Sol de un efecto se volvia una
    # segunda (La-Si) y raspaba
    "suspendida": [-2, 0, 2, 5, 7],
}

# Los colores que usa la musica del juego: nombre -> (fundamental, forma). "do" es el de
# siempre (y el que suena sin musica). Si un tema nuevo trae un acorde con otro color, el
# test test_cada_acorde_tiene_su_color avisa: hay que sumarlo aca y en juego/sonido.py
COLORES = {
    "do": (0, "mayor"), "reb": (1, "mayor"), "re7": (2, "dominante"), "mi": (4, "mayor"),
    "mi7": (4, "dominante"), "misus": (4, "suspendida"), "fa": (5, "mayor"), "sol": (7, "mayor"),
    "la": (9, "mayor"), "sib": (10, "mayor"), "do7": (0, "dominante"),
}

# Mientras se compone un efecto armonico, el color en que se compone (None = tal cual)
color_actual = None


class FueraDeLaPentatonica(ValueError):
    pass


def color_de_acorde(nombre):
    # "Am" -> "do", "Bb" -> "sib", "C7" -> "do7", "Esus4" -> "misus" ("F/E": se usa el acorde)
    fundamental, intervalos, _ = leer_acorde(nombre)
    if 5 in intervalos and 3 not in intervalos and 4 not in intervalos:
        buscado = (fundamental, "suspendida")
    elif 3 in intervalos and 4 not in intervalos:
        buscado = ((fundamental + 3) % 12, "mayor")        # menor: su relativo mayor
    elif 4 in intervalos and 10 in intervalos:
        buscado = (fundamental, "dominante")
    else:
        buscado = (fundamental, "mayor")
    for color, datos in COLORES.items():
        if datos == buscado:
            return color
    raise KeyError("El acorde %s no tiene color: sumarlo a armonia.COLORES" % nombre)


def armonizar(nota, color):
    # La nota (midi) de un efecto escrito en Do, llevada al mismo grado del color
    if color is None or color == "do":
        return nota
    nota = int(round(nota))
    clase, octava = nota % 12, nota // 12
    if clase not in PENTATONICA_DE_DO:
        raise FueraDeLaPentatonica("Un efecto armonico solo usa Do Re Mi Sol La (y tiene la nota %d)" % nota)
    grado = PENTATONICA_DE_DO.index(clase)
    fundamental, forma = COLORES[color]
    corrimiento = (fundamental + 6) % 12 - 6          # de -6 a +5: la nota se mueve poco
    return 12 * octava + corrimiento + FORMAS[forma][grado]


class en_color:
    # with en_color("fa"): todo lo que se componga adentro sale en ese color
    def __init__(self, color):
        self.color = color

    def __enter__(self):
        global color_actual
        self.antes, color_actual = color_actual, self.color

    def __exit__(self, *error):
        global color_actual
        color_actual = self.antes
