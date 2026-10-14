"""
Las capas con que se arma un efecto (como en un estudio, un efecto "caro" son varias capas):

    tono       lo que canta: notas en milisegundos ("G5:40 C6:90", ver Pista.secuencia)
    deslizar   una nota que cambia de altura (laser, sirena, caida, carga)
    cuerpo     un grave corto que baja: le da peso sin ensuciar
    aire       ruido filtrado: swish, chispa, vapor, viento
    explosion  ruido que se oscurece + un grave que cae
    golpe      un golpe de bateria (K bombo, S caja, X platillo...)
    abrir_acorde  un acorde que se abre nota por nota (como un rasgueo)

Cada funcion agrega una pista nueva al efecto. 'volumen' en dB (relativo: al final el
efecto entero se lleva a su dinamica).
"""
from herramientas.estudio import instrumentos as I


def _pista(efecto, instrumento, volumen, reverb, delay, paneo, eq=()):
    return efecto.pista("capa%d" % len(efecto.pistas), instrumento, volumen=volumen, reverb=reverb, delay=delay,
                        paneo=paneo, eq=eq)


def tono(efecto, instrumento, notas, inicio=0.0, volumen=0.0, reverb=0.2, delay=0.0, transponer=0, legato=0.92,
         paneo=0.0, tremolo=None):
    _pista(efecto, instrumento, volumen, reverb, delay, paneo).secuencia(notas, inicio, legato, transponer, tremolo)


def deslizar(efecto, instrumento, puntos, inicio=0.0, volumen=0.0, reverb=0.15, delay=0.0, fuerza=0.8, tremolo=None,
             eq=()):
    _pista(efecto, instrumento, volumen, reverb, delay, 0.0, eq).barrido(puntos, inicio, fuerza, tremolo)


def cuerpo(efecto, desde, hasta, segundos, inicio=0.0, volumen=-6.0, instrumento=I.BAJO_SUB):
    deslizar(efecto, instrumento, [(0, desde), (segundos, hasta)], inicio, volumen, reverb=0.0)


def aire(efecto, segundos, filtro, inicio=0.0, volumen=0.0, reverb=0.1, modo="bajos", resonancia=0.0, forma=None,
         eq=(), **otros):
    # Un techo suave a 7.5 kHz en todo el aire: el brillo de un efecto vive mas abajo; lo de
    # arriba es el siseo que cansa (lo "chillon")
    pista = _pista(efecto, None, volumen, reverb, 0.0, 0.0, list(eq) + [("corte_agudos", 7500)])
    pista.ruido(segundos, inicio, filtro=filtro, modo=modo, resonancia=resonancia, forma=forma, **otros)


def explosion(efecto, segundos, brillo=6000, inicio=0.0, volumen=0.0, grave=(100, 32), reverb=0.2):
    aire(efecto, segundos, [(0, brillo), (segundos, 120)], inicio, volumen, reverb,
         forma=[(0, 0), (0.004, 1), (segundos * 0.3, 0.5), (segundos, 0)])
    cuerpo(efecto, grave[0], grave[1], segundos * 0.6, inicio, volumen - 2, I.BAJO_RUGIDO)


def golpe(efecto, letra, inicio=0.0, fuerza=0.8, volumen=0.0, reverb=0.1):
    efecto.bateria("golpe%d" % len(efecto.pistas), volumen=volumen, reverb=reverb).golpe(letra, inicio, fuerza)


def clic(efecto, inicio=0.0, volumen=-8.0, brillo=5000):
    aire(efecto, 0.012, [(0, brillo)], inicio, volumen, 0.0)


def abrir_acorde(efecto, instrumento, notas, inicio=0.0, entre=0.025, largo=0.45, volumen=0.0, reverb=0.25,
                 delay=0.0):
    # Un acorde que se abre: cada nota entra un poquito despues que la anterior y todas se sostienen
    for i, nota in enumerate(notas):
        tono(efecto, instrumento, "%s:%d" % (nota, int((largo - i * entre) * 1000)), inicio + i * entre, volumen,
             reverb, delay)
