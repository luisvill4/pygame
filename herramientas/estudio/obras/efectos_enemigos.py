"""
Efectos de los enemigos y los proyectiles (LISTA_DE_SONIDOS.md, seccion 5).

Los AVISOS de peligro duran exactamente lo que dura el aviso en la pantalla y terminan en
una tension que no resuelve: el oido aprende "ahora viene". La tension sale de la PROPIA
escala de la musica (La menor): el tritono Si-Fa y la sexta menor (Fa). Asi suena tensa
pero adentro del tema; con notas de afuera (Mib, Fa#), repetidas cada pocos segundos,
sonaba desafinado. Los golpes son ruido y graves (sin melodia: no chocan con la musica).
"""
from herramientas.estudio.obra import Efecto
from herramientas.estudio.obras import obra
from herramientas.estudio import instrumentos as I
from herramientas.estudio.obras.capas import tono, deslizar, cuerpo, aire, explosion, clic
from herramientas.estudio.obras.efectos_interfaz import registrar_familia


@obra("aparece")
def aparece():
    # Un enemigo se materializa (al final de la "X"): un blip que sube, discreto
    efecto = Efecto("aparece", 0.12, "pp", sala=(0.6, 0.4))
    deslizar(efecto, I.LASER, [(0, "C4"), (0.08, "C5")], volumen=-2)
    tono(efecto, I.MARIMBA, "-:70 D5:40", volumen=-6)
    return efecto


def _roto(numero, nota):
    # Lo rompiste con el dash: crujido, una nota que cae una octava y un golpe grave
    efecto = Efecto("enemigo_roto_%d" % numero, 0.3, "mf", sala=(0.8, 0.4))
    aire(efecto, 0.09, [(0, 4500), (0.09, 900)], volumen=-2)
    deslizar(efecto, I.PLUCK, [(0, nota), (0.08, nota.replace(nota[-1], str(int(nota[-1]) - 1)))], volumen=-3)
    cuerpo(efecto, 140, 55, 0.1, volumen=-4)
    return efecto


registrar_familia("enemigo_roto", ["G4", "E4", "A4"], _roto)


@obra("aturdido")
def aturdido():
    # Las estrellitas que giran: "pio-pio"
    efecto = Efecto("aturdido", 0.18, "pp", sala=(0.6, 0.5))
    tono(efecto, I.CRISTAL, "G5:40 D5:40 G5:40 D5:50")     # cuartas (La-Mi era tritono sobre un 7)
    return efecto


def _rebote(numero, nota):
    # El rebotador se aplasta contra la pared: un resorte (baja una quinta, o una cuarta, y
    # vuelve). Es de lo que mas suena (unas 30 veces por minuto): sigue al acorde, asi que
    # sus notas son de la pentatonica de Do
    efecto = Efecto("rebote_%d" % numero, 0.18, "p", sala=(0.6, 0.4))
    quinta_abajo = {"C4": "G3", "G4": "C4", "E4": "A3", "A4": "D4"}[nota]
    deslizar(efecto, I.LEAD_HUECO, [(0, nota), (0.05, quinta_abajo), (0.15, nota)], volumen=-2)
    cuerpo(efecto, 100, 60, 0.06, volumen=-8)
    return efecto


registrar_familia("rebote", ["C4", "G4", "E4", "A4"], _rebote)          # abajo, arriba, izquierda, derecha


@obra("embestidor_apunta")
def embestidor_apunta():
    # 600 ms (lo que dura su aviso): sube de Si3 a Fa4 (el tritono de la escala: no resuelve)
    # y el temblor se acelera
    efecto = Efecto("embestidor_apunta", 0.6, "mf", sala=(0.6, 0.4))
    deslizar(efecto, I.SIRENA, [(0, "B3"), (0.6, "F4")], tremolo=(6, 16, 0.6), volumen=-2)
    return efecto


@obra("mira_fija")
def mira_fija():
    # Ya no te sigue: una traba metalica y un pinchazo en el aire (Si y Fa: el tritono)
    efecto = Efecto("mira_fija", 0.12, "mf", sala=(0.5, 0.4))
    clic(efecto, volumen=-2, brillo=3000)
    tono(efecto, I.METAL, "B4+F5:90", volumen=-2)
    return efecto


@obra("embestida")
def embestida():
    # La carga: un whoosh que baja y la tension (Fa) que cae a La
    efecto = Efecto("embestida", 0.45, "mf", sala=(0.8, 0.4))
    aire(efecto, 0.4, [(0, 3000), (0.4, 400)], modo="banda", resonancia=0.3, forma=[(0, 0), (0.02, 1), (0.4, 0)])
    deslizar(efecto, I.LASER, [(0, "F4"), (0.35, "A3")], volumen=-6)
    return efecto


def _divisor(numero, nota):
    # El slime se parte: "splat" gelatinoso (el grave baja una sexta temblando); cada tamano
    # mas agudo
    efecto = Efecto("divisor_parte_%d" % numero, 0.25, "mf", sala=(0.7, 0.4))
    deslizar(efecto, I.BAJO_SUB, [(0, nota), (0.12, nota.replace(nota[-1], str(int(nota[-1]) - 1)))],
             tremolo=(30, 30, 0.5))
    aire(efecto, 0.12, [(0, 1500), (0.12, 400)], volumen=-6)
    return efecto


registrar_familia("divisor_parte", ["C4", "G4", "C5"], _divisor)        # grande, mediano, chico


@obra("enjambre_aviso")
def enjambre_aviso():
    # 450 ms: los drones destellan y el zumbido sube de Fa a Si (tritono)
    efecto = Efecto("enjambre_aviso", 0.45, "mf", sala=(0.6, 0.4))
    deslizar(efecto, I.ZUMBIDO, [(0, "F3"), (0.45, "B3")], tremolo=(28, 32, 0.4))
    return efecto


@obra("enjambre_picada")
def enjambre_picada():
    efecto = Efecto("enjambre_picada", 0.35, "p", sala=(0.6, 0.4))
    deslizar(efecto, I.ZUMBIDO, [(0, "C4"), (0.35, "C3")], tremolo=(30, 30, 0.4))
    aire(efecto, 0.3, [(0, 2500), (0.3, 600)], modo="banda", volumen=-8)
    return efecto


@obra("bonus")
def bonus():
    # Rompiste el enjambre entero
    efecto = Efecto("bonus", 0.4, "mf", sala=(1.2, 0.5))
    tono(efecto, I.CRISTAL, "D5:30 G5:30 D6:30 G6!:200", reverb=0.3)         # saltos, no escala
    tono(efecto, I.EPIANO, "-:150 C5+G5:200", volumen=-6)
    return efecto


@obra("abeja_sale")
def abeja_sale():
    efecto = Efecto("abeja_sale", 0.1, "pp", sala=(0.5, 0.4))
    tono(efecto, I.ZUMBIDO, "A3:100", tremolo=(35, 35, 0.5))
    return efecto


@obra("abeja_aviso")
def abeja_aviso():
    # 400 ms: el zumbido sube de Mi a Sib (el tritono de Re menor: las abejas son de la
    # Colmena, y la musica del jefe esta en Re menor) y se apura
    efecto = Efecto("abeja_aviso", 0.4, "mf", sala=(0.5, 0.4))
    deslizar(efecto, I.ZUMBIDO, [(0, "E3"), (0.4, "Bb3")], tremolo=(30, 45, 0.5))
    return efecto


@obra("retirada")
def retirada():
    # Los enemigos se van en una nube (uno solo para todo el grupo)
    efecto = Efecto("retirada", 0.3, "pp", sala=(0.8, 0.4))
    aire(efecto, 0.25, [(0, 2000), (0.25, 300)])
    tono(efecto, I.EPIANO, "E4:80 C4:150", volumen=-8)
    return efecto


@obra("mina_tic")
def mina_tic():
    # La mina por estallar: un bip que sigue al acorde (la tension la da el ritmo: suena cada
    # vez mas seguido)
    efecto = Efecto("mina_tic", 0.05, "mf", sala=(0.4, 0.4))
    tono(efecto, I.METAL, "A4:40")
    return efecto


@obra("mina_estalla")
def mina_estalla():
    efecto = Efecto("mina_estalla", 0.35, "f", sala=(0.9, 0.3))
    explosion(efecto, 0.3, brillo=5000, grave=(130, 45))
    return efecto
