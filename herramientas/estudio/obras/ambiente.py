"""
El ambiente de cada sector (LISTA_DE_SONIDOS.md, seccion 10): loops de 24 s que dan la vuelta
sin costura y suenan MUY por debajo de la musica (-26 LUFS, y la categoria AMBIENTE de la
MEZCLA los baja mas). Son el "aire" del bioma: se sienten mas de lo que se escuchan.

Los drones estan en Do o Sol (afinan con el tema del juego). Todo lo que se mueve (el viento,
el crepitar, los grillos) usa curvas que terminan donde empiezan: asi el loop no tiene costura.
"""
from herramientas.estudio.obra import Obra
from herramientas.estudio.obras import obra
from herramientas.estudio import instrumentos as I
from herramientas.estudio.obras.capas import tono, aire

LARGO = 24.0


def _ambiente(nombre):
    return Obra(nombre, segundos=LARGO, vuelta=True, sala=(3.0, 0.3), objetivo=-26.0, pegamento=False, humano=0.0)


def _viento(ambiente, graves, agudos, volumen=0.0):
    # Un viento que sube y baja dos veces (la curva vuelve a donde empezo: sin costura)
    aire(ambiente, LARGO, [(0, graves), (6, agudos), (12, graves), (18, agudos * 0.8), (LARGO, graves)],
         volumen=volumen, reverb=0.3, forma=[(0, 1), (LARGO, 1)])


@obra("amb_cinturon")
def amb_cinturon():
    # Cinturon exterior: viento espacial grave y una quinta de Do muy quieta
    ambiente = _ambiente("amb_cinturon")
    _viento(ambiente, 250, 700)
    tono(ambiente, I.PAD_SUAVE, "C3+G3:24000", volumen=-6, reverb=0.4, legato=1.0)
    return ambiente


@obra("amb_carmesi")
def amb_carmesi():
    # Nebulosa carmesi: brasas que crepitan, un retumbo lejano y un La grave
    ambiente = _ambiente("amb_carmesi")
    aire(ambiente, LARGO, [(0, 2200)], modo="banda", chasquidos=7, volumen=-2, reverb=0.3, forma=[(0, 1), (LARGO, 1)])
    _viento(ambiente, 120, 260, volumen=-4)
    tono(ambiente, I.PAD_OSCURO, "A1+E2:24000", volumen=-10, reverb=0.3, legato=1.0)
    return ambiente


@obra("amb_esmeralda")
def amb_esmeralda():
    # Campo esmeralda: grillos lejanos (pares de notas cortas, al azar) sobre un Do quieto
    ambiente = _ambiente("amb_esmeralda")
    _viento(ambiente, 300, 900, volumen=-6)
    tono(ambiente, I.PAD_SUAVE, "C3+E3+G3:24000", volumen=-10, reverb=0.4, legato=1.0)
    azar = ambiente.azar
    for _ in range(26):
        inicio = azar.uniform(0, LARGO)
        nota = azar.choice(["E5", "G5", "A5"])
        tono(ambiente, I.MARIMBA, "%s:25 -:45 %s:25" % (nota, nota), inicio=inicio, volumen=-14,
             reverb=0.5, paneo=azar.uniform(-0.8, 0.8))
    return ambiente


@obra("amb_ambar")
def amb_ambar():
    # Mar de ambar: el zumbido lejano del panal, que se acerca y se aleja
    ambiente = _ambiente("amb_ambar")
    _viento(ambiente, 200, 500, volumen=-6)
    tono(ambiente, I.ZUMBIDO, "G2:24000", volumen=-8, reverb=0.5, legato=1.0, tremolo=(20, 20, 0.35))
    tono(ambiente, I.PAD_SUAVE, "G2+D3:24000", volumen=-10, reverb=0.4, legato=1.0)
    return ambiente


@obra("amb_abismo")
def amb_abismo():
    # Abismo azul: un drone grave que "respira" (sube y baja cada 4 s) y polvo que cae al centro
    ambiente = _ambiente("amb_abismo")
    tono(ambiente, I.PAD_OSCURO, "C2+G2:24000", volumen=-2, reverb=0.5, legato=1.0, tremolo=(0.25, 0.25, 0.6))
    tono(ambiente, I.BAJO_SUB, "C1:24000", volumen=-8, legato=1.0)
    _viento(ambiente, 150, 450, volumen=-6)
    return ambiente
