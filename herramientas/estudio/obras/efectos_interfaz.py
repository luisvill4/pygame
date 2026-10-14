"""
Efectos de la interfaz y de las pantallas (LISTA_DE_SONIDOS.md, secciones 1 y 9).

Estilo: suaves y redondos (madera, cristal y piano electrico FM): se escuchan cientos de
veces, asi que nunca pinchan. Las notas de "si/no/elegir" son de la pentatonica de Do (afinan
con todos los temas); las de error y alerta salen a proposito (tritono: algo no esta bien).
"""
from herramientas.estudio.obra import Efecto
from herramientas.estudio.obras import obra
from herramientas.estudio import instrumentos as I
from herramientas.estudio.obras.capas import tono, deslizar, cuerpo, aire, golpe, clic, abrir_acorde


def registrar_familia(prefijo, valores, fabrica):
    # Una obra por valor: prefijo_1, prefijo_2... (variantes o escalas)
    for numero, valor in enumerate(valores, start=1):
        obra("%s_%d" % (prefijo, numero), fabrica.__module__)(
            lambda numero=numero, valor=valor: fabrica(numero, valor))


# ---------- Moverse, aceptar, volver ----------

def _mover(numero, nota):
    # Dos variantes (Mi y Sol) que se turnan: recorrer un menu largo no suena a metralleta
    efecto = Efecto("ui_mover_%d" % numero, 0.15, "p", sala=(0.6, 0.4))
    tono(efecto, I.MARIMBA, nota + ":60", reverb=0.15)
    clic(efecto, volumen=-12)
    return efecto


registrar_familia("ui_mover", ["E5", "G5"], _mover)


def _dos_notas(nombre, primera, segunda, dinamica="mf"):
    # La cuarta que sube (si) o baja (volver): el piano electrico canta y la madera marca
    efecto = Efecto(nombre, 0.35, dinamica, sala=(0.9, 0.4))
    tono(efecto, I.EPIANO, "%s:55 %s:220" % (primera, segunda))
    tono(efecto, I.MARIMBA, "%s:55 %s:120" % (primera, segunda), volumen=-11, reverb=0.1, transponer=12)
    return efecto


@obra("ui_aceptar")
def ui_aceptar():
    return _dos_notas("ui_aceptar", "G4", "C5")


@obra("ui_volver")
def ui_volver():
    return _dos_notas("ui_volver", "C5", "G4")


@obra("ui_error")
def ui_error():
    # No se puede: dos golpes graves en tritono (Si + Fa, el de la escala), apagados
    efecto = Efecto("ui_error", 0.25, "mf", sala=(0.5, 0.3))
    tono(efecto, I.SIRENA, "B2+F3:70 -:35 B2+F3:90", legato=0.8, reverb=0.05)
    cuerpo(efecto, 90, 60, 0.08, volumen=-8)
    cuerpo(efecto, 90, 60, 0.08, inicio=0.105, volumen=-8)
    return efecto


@obra("ui_pestana")
def ui_pestana():
    # Pasar de pagina: un "fsst" de aire que sube y una nota de madera
    efecto = Efecto("ui_pestana", 0.12, "p", sala=(0.6, 0.4))
    aire(efecto, 0.07, [(0, 1000), (0.07, 3000)], modo="banda", resonancia=0.3, volumen=-6)
    tono(efecto, I.MARIMBA, "-:50 D5:60")
    return efecto


@obra("ui_valor_sube")
def ui_valor_sube():
    efecto = Efecto("ui_valor_sube", 0.08, "p", sala=(0.5, 0.4))
    tono(efecto, I.MARIMBA, "C5:25 E5:50")       # una tercera (Re-Mi, a un tono, raspaba)
    return efecto


@obra("ui_valor_baja")
def ui_valor_baja():
    efecto = Efecto("ui_valor_baja", 0.08, "p", sala=(0.5, 0.4))
    tono(efecto, I.MARIMBA, "E5:25 C5:50")
    return efecto


def _llave(nombre, notas):
    efecto = Efecto(nombre, 0.18, "mf", sala=(0.6, 0.4))
    clic(efecto, volumen=-6, brillo=3500)
    tono(efecto, I.EPIANO, notas)
    return efecto


@obra("ui_llave_si")
def ui_llave_si():
    return _llave("ui_llave_si", "C5:50 G5:130")


@obra("ui_llave_no")
def ui_llave_no():
    return _llave("ui_llave_no", "G4:50 C4:130")


@obra("ui_alerta")
def ui_alerta():
    # Una pregunta seria ("¿volver al menu?"): tritono que tiembla y despues se apoya en La
    efecto = Efecto("ui_alerta", 0.3, "mf", sala=(0.9, 0.4))
    tono(efecto, I.EPIANO, "B4+F5:150 A4:200")
    tono(efecto, I.PAD_OSCURO, "B3+F4:150", volumen=-10, reverb=0.2)
    return efecto


@obra("ui_empezar")
def ui_empezar():
    # "Insert coin": arpegio de Do que sube y un acorde abierto (Cadd9) con golpe de bombo
    efecto = Efecto("ui_empezar", 0.6, "f", sala=(1.4, 0.5))
    tono(efecto, I.PLUCK, "C4:40 E4:40 G4:40 C5:40 C4+E4+G4+D5!:420", reverb=0.25)
    tono(efecto, I.EPIANO, "-:160 C4+G4+D5+E5:420", volumen=-3, reverb=0.3)
    tono(efecto, I.CRISTAL, "-:160 C6:300", volumen=-10, reverb=0.4)
    golpe(efecto, "K", 0.16, 0.9, volumen=-4)
    return efecto


@obra("ui_apagar")
def ui_apagar():
    # Salir del juego: baja y se apaga como una pantalla CRT
    efecto = Efecto("ui_apagar", 0.6, "mf", sala=(1.0, 0.4))
    tono(efecto, I.EPIANO, "G4:60 E4:60 C4:240")
    deslizar(efecto, I.BAJO_SUB, [(0, "C3"), (0.35, 40)], inicio=0.12, volumen=-6)
    clic(efecto, inicio=0.45, volumen=-4, brillo=2500)
    return efecto


registrar_familia("ui_tecla", ["C5", "D5", "E5", "G5", "A5"],
                  lambda numero, nota: _letra(numero, nota))


def _letra(numero, nota):
    # Cambiar de letra en las iniciales: cada letra con su nota de la pentatonica
    efecto = Efecto("ui_tecla_%d" % numero, 0.1, "p", sala=(0.5, 0.4))
    tono(efecto, I.MARIMBA, nota + ":45")
    return efecto


@obra("pausa")
def pausa():
    # Todo se congela: dos notas que caen, con eco
    efecto = Efecto("pausa", 0.4, "mf", sala=(1.2, 0.4))
    tono(efecto, I.EPIANO, "E5:70 A4:260", delay=0.25)
    tono(efecto, I.CRISTAL, "E6:70 A5:200", volumen=-12, reverb=0.3)
    return efecto


@obra("seguir")
def seguir():
    efecto = Efecto("seguir", 0.35, "mf", sala=(1.0, 0.4))
    tono(efecto, I.EPIANO, "A4:70 E5:220")
    tono(efecto, I.CRISTAL, "A5:70 E6:160", volumen=-12, reverb=0.3)
    return efecto


# ---------- Dificultad ----------

def _dificultad(numero, acorde):
    # El nombre llega con un golpe: cada dificultad mas grave, mas hueca y con mas golpe. Sigue
    # al acorde del menu (es ARMONICO): antes era un acorde fijo en Do que, sobre el Mi mayor
    # del tema, chocaba medio tono (Sol contra Sol#). Y PESADILLA era un acorde disminuido
    # cerrado con un pad una octava abajo: barro aspero. Su amenaza la pone el sonido 'pesadilla'
    efecto = Efecto("dificultad_%d" % numero, 0.4, "mf", sala=(1.2, 0.4))
    aire(efecto, 0.1, [(0, 800), (0.1, 2500)], modo="banda", resonancia=0.15, volumen=-12)
    abrir_acorde(efecto, I.EPIANO, acorde, inicio=0.09, entre=0.015, largo=0.32)
    tono(efecto, I.PAD_OSCURO if numero > 2 else I.PAD_SUAVE, "-:90 %s:320" % acorde[0], volumen=-9,
         transponer=-12)
    if numero == 1:
        tono(efecto, I.CRISTAL, "-:90 %s:250" % acorde[-1], volumen=-12, transponer=12)
    golpe(efecto, "K", 0.09, 0.4 + 0.12 * numero, volumen=-8)
    return efecto


# Cada vez mas grave: Do mayor arriba, abierto en el medio, cuartas huecas y quintas en el grave.
# Los acordes se arman con Do, Re y Sol (y el Mi arriba): son las notas que siguen siendo
# consonantes en todos los colores (ver armonia.py)
registrar_familia("dificultad", [["C5", "E5", "G5"], ["C4", "G4", "E5"], ["D4", "G4", "D5"], ["G3", "D4", "G4"]],
                  _dificultad)


@obra("pesadilla")
def pesadilla():
    # Un rugido: tritono grave (Do + Fa#) y un trueno
    efecto = Efecto("pesadilla", 0.9, "f", sala=(2.0, 0.3))
    tono(efecto, I.BAJO_RUGIDO, "C2+F#2:700", volumen=-2)
    tono(efecto, I.PAD_OSCURO, "C3+F#3+C4:700", volumen=-6, reverb=0.4)
    aire(efecto, 0.9, [(0, 2500), (0.9, 150)], volumen=-4, reverb=0.4, forma=[(0, 0), (0.01, 1), (0.25, 0.6), (0.9, 0)])
    return efecto


# ---------- Taller y gasolinera ----------

def _carta(numero, nota):
    # Cada carta que cae al mostrador: un roce de papel y su nota, redonda (suben de a una). Antes
    # era una marimba (un "toc" muy brillante) con un roce resonante que pinchaba
    efecto = Efecto("carta_%d" % numero, 0.12, "p", sala=(0.9, 0.4))
    aire(efecto, 0.05, [(0, 900), (0.05, 2200)], modo="banda", resonancia=0.1, volumen=-12,
         forma=[(0, 0), (0.01, 1), (0.05, 0)])
    tono(efecto, I.EPIANO, "-:15 %s:150" % nota)
    tono(efecto, I.CRISTAL, "-:15 %s:90" % nota, volumen=-14, transponer=12)
    return efecto


registrar_familia("carta", ["C5", "D5", "E5", "G5", "A5", "C6"], _carta)


@obra("carta_rara")
def carta_rara():
    efecto = Efecto("carta_rara", 0.25, "p", sala=(1.4, 0.5))
    # Una cuarta (Sol + Do): sigue siendo cuarta en todos los colores (Mi + La se volvia tritono)
    tono(efecto, I.CRISTAL, "G5+C6:250", reverb=0.4, delay=0.2)
    return efecto


@obra("taller")
def taller():
    # Se abre el Taller: un telon que se abre (aire que sube) y una quinta que flota. No canta:
    # la melodia la ponen las cartas que caen (Do, Re, Mi) y la cierra el Sol del final. Antes
    # era un arpegio fijo en Fa mientras las cartas seguian al acorde: sonaban juntos en dos
    # tonalidades (Fa contra Fa#, La contra Sol#). Ahora es ARMONICO, como las cartas
    efecto = Efecto("taller", 0.6, "mf", sala=(1.8, 0.5))
    aire(efecto, 0.45, [(0, 500), (0.45, 2500)], modo="banda", resonancia=0.15, volumen=-8, reverb=0.3,
         forma=[(0, 0), (0.35, 1), (0.45, 0)])
    tono(efecto, I.PAD_SUAVE, "C4+G4:600", volumen=-2, reverb=0.4)
    tono(efecto, I.CRISTAL, "-:350 G5:250", volumen=-8, reverb=0.4, delay=0.2)
    return efecto


@obra("tienda")
def tienda():
    # "Ding-dong" de tienda, en Fa (el tema de la gasolinera)
    efecto = Efecto("tienda", 0.5, "mf", sala=(1.5, 0.5))
    tono(efecto, I.CAMPANA, "A5:220 F5:300", reverb=0.3, transponer=-12)
    tono(efecto, I.CRISTAL, "A5:220 F5:300", volumen=-10, reverb=0.3)
    return efecto


@obra("caja")
def caja():
    # "Ka-ching": el trinquete de la caja registradora y la campana en Fa mayor
    efecto = Efecto("caja", 0.5, "f", sala=(1.0, 0.5))
    for i in range(5):
        clic(efecto, inicio=i * 0.012, volumen=-4, brillo=4000)
    tono(efecto, I.CRISTAL, "-:70 F5+A5+C6:350", reverb=0.3)
    tono(efecto, I.EPIANO, "-:70 F4+C5:300", volumen=-6)
    return efecto


@obra("vendedor_no")
def vendedor_no():
    # El robot niega con la cabeza: dos notas que van y vienen, un poco desafinadas
    efecto = Efecto("vendedor_no", 0.2, "p", sala=(0.5, 0.4))
    tono(efecto, I.LEAD_HUECO, "E4:40 C4:40 E4:40 C4:60", legato=0.8)
    return efecto


@obra("sello")
def sello():
    efecto = Efecto("sello", 0.15, "mf", sala=(0.6, 0.3))
    aire(efecto, 0.06, [(0, 900)], volumen=-2)
    cuerpo(efecto, 120, 70, 0.1, volumen=-3)
    return efecto


@obra("barajar")
def barajar():
    efecto = Efecto("barajar", 0.25, "mf", sala=(0.6, 0.4))
    for i in range(6):
        aire(efecto, 0.03, [(0, 900 + 150 * i), (0.03, 2000)], inicio=i * 0.035, modo="banda", resonancia=0.2,
             eq=[("corte_agudos", 4500)])
    return efecto


@obra("hangar_nave")
def hangar_nave():
    # El motor de la nave que arranca: sube y se abre en una quinta
    efecto = Efecto("hangar_nave", 0.45, "mf", sala=(1.0, 0.4))
    deslizar(efecto, I.LASER, [(0, "C3"), (0.3, "C5")], volumen=-4)
    tono(efecto, I.EPIANO, "-:280 C5+G5:200")
    return efecto


@obra("record_guardado")
def record_guardado():
    efecto = Efecto("record_guardado", 0.6, "f", sala=(1.4, 0.5))
    tono(efecto, I.EPIANO, "C4:45 E4:45 G4:45 C4+E4+G4+C5!:420")
    tono(efecto, I.CRISTAL, "-:135 C6:400", volumen=-8, reverb=0.4)
    return efecto


# ---------- Detalles (P3) ----------

@obra("logo")
def logo():
    # Al arrancar el juego: el logo se abre (Do con novena que crece) y brilla con las letras
    efecto = Efecto("logo", 1.0, "f", sala=(2.2, 0.5))
    tono(efecto, I.PAD_CALIDO, "C3:200 G3:200 C4+D4+E4+G4:900", volumen=-2, reverb=0.45)
    tono(efecto, I.EPIANO, "-:400 C4+G4+D5+E5:700", volumen=-4, reverb=0.4, delay=0.2)
    tono(efecto, I.CRISTAL, "-:550 C6:500", volumen=-10, reverb=0.5)
    aire(efecto, 0.6, [(0, 300), (0.6, 3000)], modo="banda", volumen=-12, forma=[(0, 0), (0.55, 1), (0.6, 0)])
    return efecto


@obra("ui_transicion")
def ui_transicion():
    # El barrido de rombos entre pantallas (420 ms): un soplido que sube y baja, casi nada
    efecto = Efecto("ui_transicion", 0.42, "pp", sala=(0.6, 0.4))
    aire(efecto, 0.42, [(0, 400), (0.21, 1300), (0.42, 400)], modo="banda", resonancia=0.2,
         forma=[(0, 0), (0.21, 1), (0.42, 0)])
    return efecto


@obra("mando_dentro")
def mando_dentro():
    efecto = Efecto("mando_dentro", 0.2, "p", sala=(0.8, 0.4))
    tono(efecto, I.MARIMBA, "C5:60 G5:120")
    return efecto


@obra("mando_fuera")
def mando_fuera():
    efecto = Efecto("mando_fuera", 0.2, "p", sala=(0.8, 0.4))
    tono(efecto, I.MARIMBA, "G5:60 C5:120")
    return efecto


registrar_familia("contador", ["C5", "D5", "E5", "G5", "A5", "C6", "D6", "E6"],
                  lambda numero, nota: _contador(numero, nota))


def _contador(numero, nota):
    # El puntaje del Game Over cuenta: tics que suben por la pentatonica (8 en 1.5 s)
    efecto = Efecto("contador_%d" % numero, 0.05, "p", sala=(0.5, 0.4), cola=0.1)
    tono(efecto, I.MARIMBA, nota + ":35", transponer=-12)
    clic(efecto, volumen=-10, brillo=3000)
    return efecto


@obra("contador_fin")
def contador_fin():
    # Termino de contar: un "ding" de Do y Sol
    efecto = Efecto("contador_fin", 0.4, "mf", sala=(1.4, 0.5))
    tono(efecto, I.CRISTAL, "C5+G5:350", reverb=0.35)
    tono(efecto, I.EPIANO, "C4+G4:300", volumen=-6)
    return efecto


registrar_familia("fuego_artificial", [(5000, 90), (4000, 70), (6000, 110)],
                  lambda numero, valores: _fuego(numero, *valores))


def _fuego(numero, brillo, grave):
    # Los fuegos artificiales del record: un estallido lejano y su chisporroteo
    efecto = Efecto("fuego_artificial_%d" % numero, 0.6, "p", sala=(1.8, 0.4))
    aire(efecto, 0.15, [(0, brillo), (0.15, 800)], reverb=0.4)
    cuerpo(efecto, grave, grave / 2, 0.15, volumen=-6)
    aire(efecto, 0.45, [(0, 3000)], inicio=0.1, modo="banda", chasquidos=60, volumen=-6, reverb=0.4)
    return efecto


@obra("surtidor")
def surtidor():
    # La bomba de nafta mientras se llena el tanque (2.5 s): glu-glu y un "clunk" al final
    efecto = Efecto("surtidor", 2.6, "p", sala=(0.8, 0.4))
    tono(efecto, I.BAJO_SUB, " ".join(["F3:150 C4:150"] * 8), volumen=-2, legato=0.6)
    aire(efecto, 2.4, [(0, 700)], volumen=-10, tremolo=(6.6, 6.6, 0.7), forma=[(0, 1), (2.4, 1)])
    clic(efecto, inicio=2.45, volumen=0, brillo=1500)
    cuerpo(efecto, 90, 50, 0.1, inicio=2.45, volumen=-4)
    return efecto


@obra("neon")
def neon():
    # El cartel de neon "GAS" que vuelve a prender: un zumbido electrico cortito
    efecto = Efecto("neon", 0.1, "pp", sala=(0.5, 0.4), cola=0.05)
    tono(efecto, I.SIRENA, "C3:90", tremolo=(60, 60, 0.6))
    aire(efecto, 0.06, [(0, 2500)], modo="banda", volumen=-8)
    return efecto
