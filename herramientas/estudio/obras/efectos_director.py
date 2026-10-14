"""
Efectos del director (oleadas, anomalias, desafios), de los carteles y los jingles de los
grandes momentos (LISTA_DE_SONIDOS.md, seccion 6).

Los jingles estan en la tonalidad de lo que suena debajo: el juego en La menor / Do mayor
(la misma escala), asi que los de premio van en Do. El rango va en Do porque es el V de Fa:
despues del sello llega la gasolinera (Fa mayor) y suena a "llegue a casa".
"""
from herramientas.estudio.obra import Efecto
from herramientas.estudio.obras import obra
from herramientas.estudio import instrumentos as I
from herramientas.estudio.obras.capas import tono, deslizar, cuerpo, aire, explosion, golpe, clic, abrir_acorde
from herramientas.estudio.obras.efectos_interfaz import registrar_familia


# ---------- Oleadas ----------

@obra("oleada")
def oleada():
    # ¡OLEADA!: alarma de tritono (Si / Fa, el de la escala) tres veces, con bombo en cada Si
    efecto = Efecto("oleada", 0.8, "f", sala=(1.2, 0.4))
    tono(efecto, I.SIRENA, "B3+B4:120 F4+F5:120 B3+B4:120 F4+F5:120 B3+B4:120 F4+F5:200", legato=0.9)
    for i in range(3):
        golpe(efecto, "K", i * 0.24, 0.9, volumen=-4)
    return efecto


@obra("oleada_superada")
def oleada_superada():
    # Fanfarria corta en Do
    efecto = Efecto("oleada_superada", 0.8, "f", sala=(1.6, 0.5))
    tono(efecto, I.LEAD_CALIDO, "G4:90 C5:90 E5:90 G5:90 C6!:450", reverb=0.25, delay=0.15)
    tono(efecto, I.EPIANO, "-:360 C4+E4+G4+C5:450", volumen=-4)
    tono(efecto, I.BAJO_ANALOGICO, "C3:360 C2:450", volumen=-8)
    golpe(efecto, "X", 0.36, 0.6, volumen=-12, reverb=0.3)
    return efecto


# ---------- Anomalias ----------

@obra("asteroides_llega")
def asteroides_llega():
    # Un retumbo: La grave con Fa (la sexta menor de La: amenaza, y de la escala)
    efecto = Efecto("asteroides_llega", 1.0, "f", sala=(2.0, 0.3))
    aire(efecto, 1.0, [(0, 600), (1.0, 150)], forma=[(0, 0), (0.1, 1), (1.0, 0)], reverb=0.3)
    tono(efecto, I.PAD_OSCURO, "A2+F3:900", volumen=-2, reverb=0.4)
    tono(efecto, I.BAJO_SUB, "A1:900", volumen=-4)
    return efecto


@obra("meteoro_aviso")
def meteoro_aviso():
    # 900 ms: un silbido que cae (es una caida, no un ataque: sin tritono)
    efecto = Efecto("meteoro_aviso", 0.9, "p", sala=(0.8, 0.4))
    deslizar(efecto, I.LEAD_HUECO, [(0, "G5"), (0.9, "G4")], volumen=-2)
    aire(efecto, 0.9, [(0, 3000), (0.9, 800)], modo="banda", volumen=-12, forma=[(0, 0), (0.8, 1), (0.9, 0)])
    return efecto


@obra("tormenta_llega")
def tormenta_llega():
    # Electricidad: crepitar y un arpegio disminuido rapido (Si Re Fa: el de la escala)
    efecto = Efecto("tormenta_llega", 0.8, "f", sala=(1.4, 0.4))
    aire(efecto, 0.8, [(0, 3200)], modo="banda", chasquidos=80, volumen=-2, reverb=0.3)
    tono(efecto, I.PLUCK, "B3:30 D4:30 F4:30 B4:30 D5:30 F5:30 B5:200", reverb=0.3)
    return efecto


@obra("tormenta_aviso")
def tormenta_aviso():
    # 1.2 s: el crepitar se hace denso y una nota sube de Fa a Si (tritono)
    efecto = Efecto("tormenta_aviso", 1.2, "mf", sala=(0.8, 0.4))
    aire(efecto, 1.2, [(0, 3000)], modo="banda", chasquidos=40, volumen=-4,
         forma=[(0, 0.2), (1.2, 1)], tremolo=(4, 16, 0.4))
    deslizar(efecto, I.SIRENA, [(0, "F3"), (1.2, "B3")], volumen=-6)
    return efecto


@obra("llamarada")
def llamarada():
    # La llamarada quema: un rugido ancho (no suena a "te pegaron": eso es nave_golpe)
    efecto = Efecto("llamarada", 0.5, "f", sala=(1.0, 0.3))
    aire(efecto, 0.45, [(0, 3000), (0.45, 1200)], forma=[(0, 0), (0.03, 1), (0.45, 0)], reverb=0.2)
    tono(efecto, I.BAJO_RUGIDO, "C2:400", volumen=-6)
    return efecto


@obra("niebla_llega")
def niebla_llega():
    # Viento hueco y una quinta con novena que aparece y se va (fantasmal)
    efecto = Efecto("niebla_llega", 1.5, "mf", sala=(2.4, 0.4))
    aire(efecto, 1.5, [(0, 400), (0.7, 1500), (1.5, 400)], modo="banda", resonancia=0.3,
         forma=[(0, 0), (0.6, 1), (1.5, 0)], reverb=0.4)
    tono(efecto, I.PAD_SUAVE, "A3+E4+B4:1300", volumen=-4, reverb=0.5)
    return efecto


@obra("oro_llega")
def oro_llega():
    # Lluvia de oro: campanitas que caen y un arpegio que sube. Por las notas del acorde (Do Sol
    # Mi): la escala entera, con cada nota sonando debajo de la siguiente, apilaba segundas
    efecto = Efecto("oro_llega", 0.9, "f", sala=(1.6, 0.5))
    tono(efecto, I.CRISTAL, "C6:45 G5:45 E5:45 C5:45 G4:45 C5:45 E5:45 G5:45 C6!:400", reverb=0.3, delay=0.15)
    tono(efecto, I.EPIANO, "-:270 C4+E4+G4:400", volumen=-6)
    return efecto


@obra("anomalia_fin")
def anomalia_fin():
    # Se disipa: el aire baja y una quinta abierta se apaga
    efecto = Efecto("anomalia_fin", 0.7, "p", sala=(1.6, 0.4))
    aire(efecto, 0.6, [(0, 3000), (0.6, 300)], forma=[(0, 0), (0.05, 1), (0.6, 0)], reverb=0.3)
    tono(efecto, I.PAD_SUAVE, "C4+G4:600", volumen=-3, reverb=0.4)
    return efecto


# ---------- Desafios ----------

@obra("desafio_nuevo")
def desafio_nuevo():
    # Una quinta que sube y queda abierta: "¿podras?"
    efecto = Efecto("desafio_nuevo", 0.3, "mf", sala=(1.0, 0.5))
    tono(efecto, I.EPIANO, "G4:60 D5:240", delay=0.2)
    return efecto


@obra("desafio_cumplido")
def desafio_cumplido():
    efecto = Efecto("desafio_cumplido", 0.6, "f", sala=(1.4, 0.5))
    tono(efecto, I.EPIANO, "G4:45 C5:45 E5:45")
    abrir_acorde(efecto, I.CRISTAL, ["C5", "E5", "G5", "C6"], inicio=0.135, largo=0.4, reverb=0.3)   # sin Sol+La
    abrir_acorde(efecto, I.EPIANO, ["C4", "E4", "G4"], inicio=0.135, largo=0.4, volumen=-4)
    return efecto


@obra("desafio_fallado")
def desafio_fallado():
    # El "trombon triste": baja por semitonos y la ultima se desinfla temblando
    efecto = Efecto("desafio_fallado", 0.7, "mf", sala=(1.0, 0.4))
    tono(efecto, I.LEAD_HUECO, "E4:110 Eb4:110 D4:110", legato=0.95)
    deslizar(efecto, I.LEAD_HUECO, [(0, "Db4"), (0.35, 265)], inicio=0.33, tremolo=(6, 6, 0.3))
    return efecto


# ---------- Carteles ----------

@obra("ficha_enemigo")
def ficha_enemigo():
    # Llega un enemigo nuevo: la ficha entra deslizando y un tritono que sube: "ojo con este"
    efecto = Efecto("ficha_enemigo", 0.35, "mf", sala=(1.0, 0.4))
    aire(efecto, 0.12, [(0, 800), (0.12, 3000)], modo="banda", resonancia=0.2, volumen=-6)
    tono(efecto, I.EPIANO, "-:100 B3:80 F4:200")
    return efecto


@obra("logro")
def logro():
    # Un trofeo: campana y piano (sin bajo: distinto del record)
    efecto = Efecto("logro", 0.9, "f", sala=(1.8, 0.5))
    tono(efecto, I.CAMPANA, "E5:100 G5:100 C6:100 E6:100 G6!:450", reverb=0.35, delay=0.2, transponer=-12)
    tono(efecto, I.CRISTAL, "-:400 C6:450", volumen=-6, reverb=0.4)
    abrir_acorde(efecto, I.EPIANO, ["C4", "G4", "E5"], inicio=0.4, largo=0.45, volumen=-6)
    return efecto


@obra("nave_nueva")
def nave_nueva():
    efecto = Efecto("nave_nueva", 0.35, "mf", sala=(1.2, 0.5))
    tono(efecto, I.CRISTAL, "G5:60 C6:60 E6:250", reverb=0.35)
    return efecto


registrar_familia("teclear", ["E6", "G6", "A6"], lambda numero, nota: _teclear(numero, nota))


def _teclear(numero, nota):
    # Una letra que se escribe: un clic y una nota casi imperceptible
    efecto = Efecto("teclear_%d" % numero, 0.03, "pp", sala=(0.3, 0.4), cola=0.05)
    clic(efecto, volumen=-6, brillo=3500)
    tono(efecto, I.MARIMBA, nota + ":20", volumen=-8, transponer=-12)
    return efecto


registrar_familia("estrella", ["C5", "D5", "E5", "G5", "A5"], lambda numero, nota: _estrella(numero, nota))


def _estrella(numero, nota):
    # Cada estrella del rango: una campanita, mas aguda cada vez
    efecto = Efecto("estrella_%d" % numero, 0.25, "mf", sala=(1.4, 0.5))
    tono(efecto, I.CRISTAL, nota + ":220", reverb=0.35, delay=0.15)
    tono(efecto, I.EPIANO, nota + ":150", volumen=-8, transponer=-12)
    return efecto


def _sello(letra, notas, acorde, dinamica, bajo, platillo):
    # La letra del rango cae: golpe + jingle en Do (el V de Fa: despues viene la gasolinera)
    efecto = Efecto("sello_" + letra, 1.0 if letra in "SA" else 0.5, dinamica, sala=(1.8, 0.5))
    golpe(efecto, "K", 0.0, 1.0, volumen=-2)
    if notas:
        tono(efecto, I.LEAD_CALIDO, notas, reverb=0.3, delay=0.15)
    tono(efecto, I.EPIANO, acorde, volumen=-4, reverb=0.3)
    tono(efecto, I.BAJO_ANALOGICO, bajo, volumen=-8)
    if platillo:
        golpe(efecto, "X", 0.0, 0.8, volumen=-10, reverb=0.3)
    return efecto


@obra("sello_S")
def sello_s():
    efecto = _sello("S", "G4:70 C5:70 E5:70 G5:70 C6!:600", "-:280 C4+E4+G4+C5+E5:650", "ff", "C3:280 C2:650", True)
    tono(efecto, I.CRISTAL, "-:280 C6:40 E6:40 G6:40 C6:40 E6:40 G6:400", volumen=-10, reverb=0.4)
    return efecto


@obra("sello_A")
def sello_a():
    return _sello("A", "E5:60 G5:60 C6!:400", "-:120 C4+E4+G4+C5:400", "f", "C3:120 C2:400", True)


@obra("sello_B")
def sello_b():
    # Neutro: un Do suspendido que resuelve (Fa -> Mi): "esta bien"
    return _sello("B", None, "C4+F4+G4:180 C4+E4+G4:300", "mf", "C2:480", False)


@obra("sello_C")
def sello_c():
    # Seco: una quinta sin tercera, sin brillo
    return _sello("C", None, "C3+G3:150", "mf", "C2:150", False)


SECTORES = [["C4", "E4", "G4", "D5"], ["A3", "C4", "E4", "A4"], ["F3", "A3", "C4", "E4"],
            ["G3", "C4", "D4", "G4"], ["E3", "G3", "B3", "E4"]]


def _sector(numero, notas):
    # Llega un sector nuevo: su acorde arpegiado (Cinturon Cadd9 luminoso, Carmesi Am oscuro,
    # Esmeralda Fmaj7 magico, Ambar Gsus4 expectante, Abismo Em el mas oscuro)
    efecto = Efecto("sector_nuevo_%d" % numero, 1.0, "f", sala=(2.2, 0.45))
    abrir_acorde(efecto, I.EPIANO, notas, entre=0.06, largo=0.9, reverb=0.35, delay=0.2)
    tono(efecto, I.PAD_CALIDO, "+".join(notas) + ":900", volumen=-6, reverb=0.4)
    tono(efecto, I.CAMPANA, notas[-1] + ":700", inicio=0.24, volumen=-10, reverb=0.4, transponer=12)
    cuerpo(efecto, 70, 45, 0.5, volumen=-10)
    return efecto


registrar_familia("sector_nuevo", SECTORES, _sector)


registrar_familia("barra_jefe", ["D4", "E4", "F4", "G4", "A4", "Bb4", "C5", "D5", "E5", "F5", "G5", "A5"],
                  lambda numero, nota: _barra(numero, nota))


def _barra(numero, nota):
    # La barra del jefe se llena: un tic por segmento, subiendo por Re menor
    efecto = Efecto("barra_jefe_%d" % numero, 0.05, "p", sala=(0.5, 0.4), cola=0.1)
    tono(efecto, I.PLUCK, nota + ":40")
    return efecto


# ---------- READY / GO y el final ----------

@obra("listo_ready")
def listo_ready():
    # READY?: termina en el V (Mi, el V de La menor): es una pregunta
    efecto = Efecto("listo_ready", 0.5, "f", sala=(1.2, 0.5))
    tono(efecto, I.LEAD_CALIDO, "A4:150 E5:300", delay=0.2)
    tono(efecto, I.PAD_CALIDO, "A3+E4:150 G#3+B3+E4:300", volumen=-8, reverb=0.3)
    return efecto


@obra("listo_go")
def listo_go():
    # GO!: el acorde de La abierto (sin tercera: la musica entra en este tiempo), un bombo y un
    # soplo que cae. Antes era un acorde de sierras saturadas (LEAD_CALIDO) con un platillo, a
    # la dinamica mas fuerte (ff): lo mas aspero de la lista. El brillo lo pone un cristal arriba
    efecto = Efecto("listo_go", 0.5, "f", sala=(1.4, 0.5))
    golpe(efecto, "K", 0.0, 0.9, volumen=-3)
    aire(efecto, 0.4, [(0, 3500), (0.4, 700)], volumen=-14, reverb=0.3, forma=[(0, 0), (0.004, 1), (0.4, 0)])
    abrir_acorde(efecto, I.EPIANO, ["A3", "E4", "A4", "E5"], entre=0.008, largo=0.38, reverb=0.25)
    tono(efecto, I.LEAD_HUECO, "A4+E5:300", volumen=-8, reverb=0.25)
    tono(efecto, I.CRISTAL, "A5:280", volumen=-9, reverb=0.3)
    tono(efecto, I.BAJO_SUB, "A2:300", volumen=-6)
    return efecto


@obra("destruida")
def destruida():
    # NAVE DESTRUIDA: La menor grave que se hunde un cuarto de tono mientras se apaga
    efecto = Efecto("destruida", 1.0, "mf", sala=(2.4, 0.4))
    deslizar(efecto, I.PAD_OSCURO, [(0, "A2"), (1.0, 107)], reverb=0.4)
    deslizar(efecto, I.PAD_OSCURO, [(0, "E3"), (1.0, 160)], reverb=0.4)
    tono(efecto, I.EPIANO, "A3+C4+E4:900", volumen=-6, reverb=0.4)
    return efecto


@obra("game_over")
def game_over():
    # El fin: La menor lento (La, Mi, Do) y un acorde grave que cae
    efecto = Efecto("game_over", 1.6, "f", sala=(2.4, 0.4))
    tono(efecto, I.EPIANO, "A4:300 E4:300 C4:300 A3+E4+A4:800", reverb=0.35, delay=0.15)
    tono(efecto, I.PAD_OSCURO, "-:900 A2+E3+A3:800", volumen=-6, reverb=0.4)
    tono(efecto, I.BAJO_SUB, "A2:300 E2:300 C2:300 A1:800", volumen=-6)
    golpe(efecto, "K", 0.0, 0.7, volumen=-6)
    return efecto


@obra("trueno")
def trueno():
    # El relampago lejano del Carmesi: un retumbo con dos picos
    efecto = Efecto("trueno", 1.5, "p", sala=(2.0, 0.3))
    aire(efecto, 1.5, [(0, 900), (1.5, 120)], forma=[(0, 0), (0.05, 1), (0.3, 0.4), (0.45, 0.8), (1.5, 0)],
         reverb=0.4)
    explosion(efecto, 0.8, brillo=1200, volumen=-8, grave=(60, 30))
    return efecto
