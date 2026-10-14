"""
Los temas del juego (dan la vuelta sin costura).

Base armonica (ver LISTA_DE_SONIDOS.md, seccion 0): todos los temas estan en tonalidades
que contienen la pentatonica de Do (Do Re Mi Sol La), asi los efectos de premio y de
interfaz suenan afinados encima de cualquier tema.
"""
from herramientas.estudio.obra import Obra
from herramientas.estudio.obras import obra
from herramientas.estudio import instrumentos as I


def compases(*grillas):
    return " | ".join(grillas)


# El color de "Neon en ruta" en cada sector: la misma cancion (acordes, melodia, forma) con
# otra paleta, otra sala y otro groove. Asi cambiar de bioma se escucha, pero el jugador
# reconoce su tema. Lo que no se dice, es el del Cinturon (el original)
COLORES = {
    1: {},
    # Nebulosa carmesi: mas rapido, oscuro y con mordida (el aire arde)
    2: {"bpm": 122, "sala": (2.0, 0.3), "pad": I.PAD_OSCURO, "bajo": I.BAJO_RUGIDO, "palmas_desde": 8,
        "contracanto": I.METAL, "contracanto_volumen": -20.0},
    # Campo esmeralda: mas lento y abierto, piano electrico en corcheas, flauta hueca y campanas
    3: {"bpm": 112, "sala": (3.2, 0.5), "pad": I.PAD_SUAVE, "arpegio": (I.EPIANO, 2, [0, 2, 1, 3], -14.0),
        "lead": I.LEAD_HUECO, "contracanto_desde": 8, "hats": "corcheas"},
    # Mar de ambar: con swing y calido (marimba y piano electrico)
    4: {"bpm": 110, "swing": 0.15, "sala": (2.0, 0.5), "pad": I.PAD_SUAVE, "bajo": I.BAJO_SUB,
        "arpegio": (I.MARIMBA, 1, [0, 1, 2, 3, 4, 3, 2, 1], -13.0), "lead": I.EPIANO},
    # Abismo azul: a medio tiempo, sala enorme y oscura, campanas lejanas (ni la luz escapa)
    5: {"sala": (4.0, 0.25), "pad": I.PAD_OSCURO, "bajo": I.BAJO_SUB, "medio_tiempo": True,
        "arpegio": (I.CAMPANA, 4, [0, 2, 1, 3], -16.0), "lead": I.LEAD_HUECO, "hats": "corcheas"},
}


def neon_en_ruta(nombre, color):
    # "Neon en ruta": synthwave en La menor, 24 compases (~49 s a 118 bpm).
    #   A (1-8)   respiro: bajo con groove, arpegio y el pad que bombea (sin melodia)
    #   B (9-16)  entra la melodia cantada
    #   C (17-24) climax: el bajo en octavas, palmas y una campana de contracanto
    # El ultimo acorde (Sol, el VII) vuelve a La menor: el loop no tiene costura
    tema = Obra(nombre, bpm=color.get("bpm", 118), swing=color.get("swing", 0.0), sala=color.get("sala", (2.6, 0.4)),
                eco=0.75, realimentacion=0.38, objetivo=-14.0,
                acordes=["Am", "F", "C", "G", "Am", "F", "C", "G",
                         "F", "G", "Em", "Am", "F", "G", "Esus4", "E",
                         "Dm", "Am", "F", "C", "Dm", "Am", "F", "G"])

    # ---------- Bateria (cada pieza en su pista: su volumen y su reverb) ----------
    bombo = tema.bateria("bombo", volumen=-2.0, eq=[("corte_graves", 35), ("campana", 3000, 3, 1.0)])
    caja = tema.bateria("caja", volumen=-6.0, reverb=0.35, eq=[("corte_graves", 120), ("campana", 4500, 2, 0.8), ("agudos", 8000, 2)])
    palmas = tema.bateria("palmas", volumen=-11.0, reverb=0.4, paneo=0.15)
    hats = tema.bateria("hats", volumen=-9.0, paneo=-0.2, reverb=0.1, eq=[("corte_agudos", 16000)])
    toms = tema.bateria("toms", volumen=-6.0, reverb=0.3)
    platillos = tema.bateria("platillos", volumen=-10.0, reverb=0.25, eq=[("corte_agudos", 14000)])

    medio_tiempo = color.get("medio_tiempo", False)
    golpe = "K - - - - - - - - - - - - - K? -" if medio_tiempo else "K - - - - - - - K - K - - - - -"
    for compas in range(24):
        bombo.grilla(golpe, desde=compas)
    caja_simple = "- - - - - - - - S - - - - - - -" if medio_tiempo else "- - - - S - - - - - - - S - - -"
    caja_redoble = "- - - - - - - - S - - - S - S? S" if medio_tiempo else "- - - - S - - - - - - - S - S? S"
    for compas in range(4, 24):
        caja.grilla(caja_redoble if compas in (7, 15, 23) else caja_simple, desde=compas)
    for compas in range(color.get("palmas_desde", 16), 24):
        palmas.grilla("- - - - - - - - C - - - - - - -" if medio_tiempo else "- - - - C - - - - - - - C - - -",
                      desde=compas)
    corcheas = "h - h? - h - h? - h - h? - h - h? -"
    semicorcheas = "h h? h h? h h? h H h h? h h? h h? h H"
    for compas in range(24):
        rapido = compas >= 16 and color.get("hats") != "corcheas"
        hats.grilla(semicorcheas if rapido else corcheas, desde=compas)
    for compas in (7, 15, 23):
        toms.grilla("- - - - - - - - - - - - T T t t", desde=compas)
    for compas in (0, 8, 16):
        platillos.grilla("X - - - - - - - - - - - - - - -", desde=compas)
    for compas in (8, 16):
        platillos.golpe("R", tema.segundo(compas * 16))         # el platillo al reves llega al compas

    # ---------- Bajo ----------
    bajo = tema.pista("bajo", color.get("bajo", I.BAJO_ANALOGICO), volumen=-4.0, bombeo=0.35, eq=[("corte_graves", 32)])
    bajo.bajo("R! . . R . . R . R . . R . . 8 .", desde=0, hasta=8)              # 3-3-2: con groove
    bajo.bajo("R! . 8 . R . 8 . R . 8 . R . 8 .", desde=8, hasta=24)             # octavas que empujan

    # ---------- Colchon y arpegio ----------
    pad = tema.pista("pad", color.get("pad", I.PAD_CALIDO), volumen=-12.0, reverb=0.35, bombeo=0.55,
                     chorus=(0.003, 0.5, 0.4), eq=[("corte_graves", 180)], ancho=1.3)
    pad.acordes("X . . . . . . . . . . . . . . .", registro=("A3", "E5"))
    instrumento, cada, orden, volumen = color.get("arpegio", (I.PLUCK, 1, [0, 1, 2, 3, 4, 3, 2, 1], -12.0))
    arpegio = tema.pista("arpegio", instrumento, volumen=volumen, delay=0.32, reverb=0.25, bombeo=0.3, ancho=1.4,
                         eq=[("corte_graves", 220)])
    arpegio.arpegio(orden, base="A3", cada=cada)

    # ---------- Melodia (B y C) ----------
    lead = tema.pista("lead", color.get("lead", I.LEAD_CALIDO), volumen=-7.0, delay=0.22, reverb=0.3,
                      eq=[("corte_graves", 200), ("campana", 2800, -2, 1.0)])
    lead.grilla(compases(
        "A4 . . . C5 . . . F5 . . . E5 . C5 .", "D5 . . . . . . . B4 . . . G4 . . .",
        "E5 . . . . . G5 . . . E5 . D5 . B4 .", "C5 . . . . . . . A4 . . . . . . -",
        "A4 . . . C5 . . . F5 . . . G5 . A5 .", "B5 . . . . . A5 . G5 . . . D5 . . .",
        "E5 . . . . . . . A4 . . . B4 . . .", "G#4 . . . . . . . B4 . . . E5 . . -",
        "D5 . . . F5 . A5 . . . G5 . F5 . E5 .", "E5 . . . . . . . C5 . . . A4 . . .",
        "F5 . . . A5 . C6 . . . A5 . G5 . F5 .", "G5 . . . . . . . E5 . . . C5 . . .",
        "D5 . . . F5 . A5 . . . G5 . F5 . E5 .", "E5 . . . . . A5 . . . G5 . E5 . C5 .",
        "D5 . . . . . . . C5 . . . A4 . . .", "B4 . . . . . . . - - - - - - - -"), desde=8)

    # ---------- Contracanto: una campana lejana en la quinta de cada acorde ----------
    campana = tema.pista("campana", color.get("contracanto", I.CAMPANA), volumen=color.get("contracanto_volumen", -17.0),
                         reverb=0.5, delay=0.2, paneo=0.3)
    contracanto = compases(
        "A5 . . . . . . . . . . . F5 . . .", "E5 . . . . . . . . . . . . . . .",
        "C6 . . . . . . . . . . . A5 . . .", "G5 . . . . . . . . . . . . . . .",
        "A5 . . . . . . . . . . . F5 . . .", "E5 . . . . . . . . . . . A5 . . .",
        "C6 . . . . . . . . . . . A5 . . .", "D5 . . . . . . . . . . . . . . .")
    for desde in range(color.get("contracanto_desde", 16), 24, 8):
        campana.grilla(contracanto, desde=desde, legato=1.0)
    return tema


@obra("musica_juego")
def musica_juego():
    return neon_en_ruta("musica_juego", COLORES[1])


for _sector in (2, 3, 4, 5):
    obra("musica_juego_%d" % _sector)(lambda sector=_sector: neon_en_ruta("musica_juego_%d" % sector, COLORES[sector]))


@obra("musica_tension")
def musica_tension():
    # El nivel antes del jefe ("PROXIMO NIVEL: ¡JEFE!"): La menor sobre un pedal de Mi (el V:
    # algo se acerca y no resuelve), 126 bpm, 8 compases (~15 s). Los acordes se mueven arriba
    # y el bajo martilla siempre la misma nota; los toms crecen hacia el final
    tema = Obra("musica_tension", bpm=126, sala=(2.4, 0.35), eco=0.75, realimentacion=0.35, objetivo=-14.0,
                acordes=["Am/E", "F/E", "Dm/E", "E", "Am/E", "F/E", "Dm/E", "E7"])
    bombo = tema.bateria("bombo", volumen=-2.0, eq=[("corte_graves", 35), ("campana", 3000, 3, 1.0)])
    caja = tema.bateria("caja", volumen=-8.0, reverb=0.4)
    hats = tema.bateria("hats", volumen=-10.0, paneo=0.2)
    toms = tema.bateria("toms", volumen=-6.0, reverb=0.3)
    for compas in range(8):
        bombo.grilla("K - - - K - - - K - - - K - - -", desde=compas)
        caja.grilla("- - - - - - - - S - - - - - - -", desde=compas)
        hats.grilla("h h? h h? h h? h h? h h? h h? h h? h h?", desde=compas)
    toms.grilla("- - - - - - - - T - T - t - t t", desde=3)
    toms.grilla("T - T - t - t - T T t t T T t t", desde=7)
    bajo = tema.pista("bajo", I.BAJO_RUGIDO, volumen=-5.0, bombeo=0.3)
    bajo.bajo("B . B B . B B . B . B B . B B .")            # el pedal de Mi (la nota de la barra)
    pad = tema.pista("pad", I.PAD_OSCURO, volumen=-11.0, reverb=0.4, bombeo=0.5, eq=[("corte_graves", 200)])
    pad.acordes("X . . . . . . . . . . . . . . .", registro=("A3", "E5"))
    arpegio = tema.pista("arpegio", I.PLUCK, volumen=-13.0, delay=0.3, reverb=0.25, ancho=1.4)
    arpegio.arpegio([0, 1, 2, 1], base="A3")
    sirena = tema.pista("sirena", I.LEAD_HUECO, volumen=-12.0, reverb=0.5, delay=0.3)
    sirena.grilla(compases(
        "E5 . . . . . . . . . . . . . . .", "F5 . . . . . . . . . . . . . . .",
        "F5 . . . . . . . E5 . . . . . . .", "G#5 . . . . . . . . . . . . . . .",
        "E5 . . . . . . . . . . . . . . .", "F5 . . . . . . . . . . . . . . .",
        "A5 . . . . . . . F5 . . . . . . .", "G#5 . . . . . . . B5 . . . . . . ."))
    return tema


@obra("musica_iniciales")
def musica_iniciales():
    # "Tu nombre en neon": la pantalla de ingresar las iniciales. Do mayor, 120 bpm, 8 compases
    # (16 s): alegre y con empuje, como las tablas de records de los arcades de los 80
    tema = Obra("musica_iniciales", bpm=120, sala=(1.8, 0.5), eco=0.75, realimentacion=0.3,
                acordes=["C", "Am", "F", "G", "C", "Am", "Dm", "G"])
    bombo = tema.bateria("bombo", volumen=-3.0, eq=[("corte_graves", 35), ("campana", 3000, 3, 1.0)])
    caja = tema.bateria("caja", volumen=-8.0, reverb=0.3, eq=[("corte_graves", 120), ("agudos", 8000, 2)])
    hats = tema.bateria("hats", volumen=-11.0, paneo=0.2)
    platillos = tema.bateria("platillos", volumen=-12.0, reverb=0.2)
    for compas in range(8):
        bombo.grilla("K - - - K - - - K - - - K - - -", desde=compas)
        caja.grilla("- - - - S - - - - - - - S - S? -" if compas == 7 else "- - - - S - - - - - - - S - - -",
                    desde=compas)
        hats.grilla("- - h - - - h - - - h - - - h h?", desde=compas)
    platillos.grilla("X - - - - - - - - - - - - - - -", desde=0)
    bajo = tema.pista("bajo", I.BAJO_ANALOGICO, volumen=-6.0, bombeo=0.3)
    bajo.bajo("R . 8 . R . 8 . R . 8 . R . 5 .")
    pad = tema.pista("pad", I.PAD_SUAVE, volumen=-14.0, reverb=0.3, bombeo=0.4, eq=[("corte_graves", 200)])
    pad.acordes("X . . . . . . . . . . . . . . .", registro=("G3", "D5"))
    arpegio = tema.pista("arpegio", I.PLUCK, volumen=-15.0, delay=0.25, reverb=0.2, ancho=1.3,
                         eq=[("corte_graves", 250)])
    arpegio.arpegio([0, 2, 1, 3], base="C4")
    lead = tema.pista("lead", I.EPIANO, volumen=-6.0, delay=0.2, reverb=0.3)
    lead.grilla(compases(
        "E5 . G5 . C6 . . . G5 . E5 . G5 . . .", "A5 . . . G5 . E5 . C5 . . . E5 . . .",
        "F5 . A5 . C6 . . . A5 . F5 . A5 . . .", "G5 . . . . . D5 . B4 . . . D5 . . .",
        "E5 . G5 . C6 . . . G5 . E5 . G5 . . .", "A5 . . . C6 . . . A5 . . . E5 . . .",
        "F5 . . . E5 . D5 . . . F5 . A5 . . .", "G5 . . . . . . . - - - - D5 . B4 ."), transponer=-12)
    return tema


@obra("musica_fin")
def musica_fin():
    # "Senal perdida": el Game Over. La menor, 80 bpm, 8 compases (24 s), sin bateria:
    # melancolia tranquila. El Mi mayor del final deja la vuelta en suspenso (vuelve a La)
    tema = Obra("musica_fin", bpm=80, sala=(3.2, 0.35), eco=0.75, realimentacion=0.4, objetivo=-16.0,
                acordes=["Am", "F", "C", "G", "Am", "F", "E", "E"])
    pad = tema.pista("pad", I.PAD_SUAVE, volumen=-9.0, reverb=0.45, chorus=(0.004, 0.3, 0.4),
                     eq=[("corte_graves", 150)])
    pad.acordes("X . . . . . . . . . . . . . . .", registro=("A3", "E5"))
    bajo = tema.pista("bajo", I.BAJO_SUB, volumen=-8.0)
    bajo.bajo("R . . . . . . . . . . . 5 . . .")
    piano = tema.pista("piano", I.EPIANO, volumen=-14.0, reverb=0.4, delay=0.15, paneo=-0.2)
    piano.acordes("- - - - X . . . - - - - - - X .", registro=("C4", "G5"), fuerza=0.6)
    campana = tema.pista("campana", I.CAMPANA, volumen=-8.0, reverb=0.55, delay=0.3, paneo=0.15)
    campana.grilla(compases(
        "E5 . . . . . . . C5 . . . B4 . . .", "A4 . . . . . . . . . . . - - - -",
        "G4 . . . . . C5 . . . E5 . . . . .", "D5 . . . . . . . B4 . . . . . . .",
        "E5 . . . . . A5 . . . G5 . E5 . . .", "F5 . . . . . . . E5 . . . C5 . . .",
        "B4 . . . . . . . G#4 . . . . . . .", "- - - - - - - - - - - - - - - -"), legato=1.0)
    return tema


@obra("musica_menu")
def musica_menu():
    # "Hangar": el menu. La menor, 112 bpm, 16 compases (~34 s): tranquilo, para leer el menu
    # sin apuro. Antes era chiptune; se rehizo en el estudio con su misma melodia y acordes.
    #   A (1-8)   Am F C G dos veces
    #   B (9-16)  F G Em Am F G y Mi mayor (el V de La: tensa para volver al principio)
    tema = Obra("musica_menu", bpm=112, sala=(2.8, 0.45), eco=0.75, realimentacion=0.35, objetivo=-14.0,
                acordes=["Am", "F", "C", "G", "Am", "F", "C", "G",
                         "F", "G", "Em", "Am", "F", "G", "E", "E"])
    bombo = tema.bateria("bombo", volumen=-4.0, eq=[("corte_graves", 35), ("campana", 3000, 3, 1.0)])
    caja = tema.bateria("caja", volumen=-9.0, reverb=0.4, eq=[("corte_graves", 120), ("agudos", 8000, 2)])
    hats = tema.bateria("hats", volumen=-12.0, paneo=-0.2, reverb=0.1, eq=[("corte_agudos", 15000)])
    toms = tema.bateria("toms", volumen=-8.0, reverb=0.3)
    for compas in range(16):
        bombo.grilla("K - - - - - - - K - - K - - - -", desde=compas)
        caja.grilla("- - - - S - - - - - - - S - S? S" if compas == 15 else "- - - - S - - - - - - - S - - -",
                    desde=compas)
        hats.grilla("h - h? - h - h? - h - h? - h - h? -", desde=compas)
    toms.grilla("- - - - - - - - - - - - T T t t", desde=7)

    bajo = tema.pista("bajo", I.BAJO_ANALOGICO, volumen=-6.0, bombeo=0.3, eq=[("corte_graves", 32)])
    bajo.bajo("R! . . . R . 8 . R . . . 5 . 8 .")
    pad = tema.pista("pad", I.PAD_SUAVE, volumen=-12.0, reverb=0.4, bombeo=0.4, chorus=(0.003, 0.5, 0.4),
                     eq=[("corte_graves", 180)], ancho=1.3)
    pad.acordes("X . . . . . . . . . . . . . . .", registro=("A3", "E5"))
    arpegio = tema.pista("arpegio", I.PLUCK, volumen=-14.0, delay=0.3, reverb=0.25, bombeo=0.25, ancho=1.4,
                         eq=[("corte_graves", 220)])
    arpegio.arpegio([0, 1, 2, 3, 4, 3, 2, 1], base="A3")
    lead = tema.pista("lead", I.LEAD_HUECO, volumen=-7.0, delay=0.25, reverb=0.35, eq=[("corte_graves", 200)])
    lead.grilla(compases(
        "A4 . . . C5 . E5 . . . . . D5 . C5 .", "C5 . . . . . A4 . . . F4 . A4 . C5 .",
        "E5 . . . G5 . . . E5 . D5 . C5 . . .", "D5 . . . . . . . B4 . . . G4 . . .",
        "A4 . . . C5 . E5 . . . . . A5 . G5 .", "F5 . . . E5 . . . C5 . . . A4 . C5 .",
        "E5 . . . D5 . C5 . . . G4 . C5 . E5 .", "D5 . . . . . . . . . . . - - - -",
        "A5 . . . . . G5 . F5 . . . E5 . F5 .", "G5 . . . . . . . D5 . . . B4 . D5 .",
        "E5 . . . G5 . B5 . . . A5 . G5 . E5 .", "A5 . . . . . . . E5 . . . C5 . E5 .",
        "F5 . . . E5 . F5 . A5 . . . G5 . F5 .", "G5 . . . F5 . G5 . B5 . . . A5 . G5 .",
        "G#5 . . . . . . . E5 . . . B4 . . .", "G#4 . . . B4 . . . E5 . . . - - - -"), transponer=-12)
    return tema


@obra("musica_gasolinera")
def musica_gasolinera():
    # "Parada tecnica": la gasolinera. Fa mayor, 96 bpm con swing, 16 compases (~40 s): un
    # lounge espacial. Vibrafono (la campana) cantando, piano electrico a contratiempo, bajo
    # caminante (R 3 5 6) y una bateria con escobillas. Antes era chiptune; misma melodia
    tema = Obra("musica_gasolinera", bpm=96, swing=0.3, sala=(1.8, 0.5), eco=0.75, realimentacion=0.3,
                objetivo=-14.0,
                acordes=["Fmaj7", "Dm7", "Gm7", "C7", "Fmaj7", "Dm7", "Gm7", "C7",
                         "Bbmaj7", "Bbm7", "Am7", "D7", "Gm7", "C7", "Fmaj7", "C7"])
    bombo = tema.bateria("bombo", volumen=-7.0, eq=[("corte_graves", 40), ("corte_agudos", 6000)])
    caja = tema.bateria("caja", volumen=-14.0, reverb=0.3, eq=[("corte_graves", 200), ("corte_agudos", 7000)])
    hats = tema.bateria("hats", volumen=-14.0, paneo=0.25, reverb=0.15, eq=[("corte_agudos", 12000)])
    for compas in range(16):
        bombo.grilla("K - - - - - - - K? - - - - - - -", desde=compas)
        caja.grilla("- - - - S? - - - - - S? - S - S? S" if compas == 15 else "- - - - S? - - - - - - - S? - - -",
                    desde=compas)
        hats.grilla("h - h? h h - h? h h - h? h h - h? h", desde=compas)

    bajo = tema.pista("bajo", I.BAJO_SUB, volumen=-4.0)
    bajo.bajo("R . . . 3 . . . 5 . . . 6 . . .", legato=0.8)
    piano = tema.pista("piano", I.EPIANO, volumen=-11.0, reverb=0.3, paneo=-0.2, chorus=(0.003, 0.6, 0.3),
                       eq=[("corte_graves", 160)])
    piano.acordes("- - - - X . - - - - X . - - - X", registro=("F3", "E5"), legato=0.7, fuerza=0.6)
    pad = tema.pista("pad", I.PAD_SUAVE, volumen=-17.0, reverb=0.4, eq=[("corte_graves", 200)])
    pad.acordes("X . . . . . . . . . . . . . . .", registro=("A3", "E5"))
    vibrafono = tema.pista("vibrafono", I.CAMPANA, volumen=-6.0, delay=0.2, reverb=0.35, paneo=0.15,
                           eq=[("corte_graves", 250)])
    vibrafono.grilla(compases(
        "A4 . . . C5 . E5 . . . . . D5 . C5 .", "D5 . . . . . . . A4 . . . C5 . . .",
        "Bb4 . . . D5 . F5 . . . E5 . D5 . . .", "E5 . . . . . . . G4 . Bb4 . C5 . E5 .",
        "F5 . . . E5 . C5 . A4 . . . C5 . F5 .", "E5 . D5 . . . . . - - A4 . D5 . F5 .",
        "A5 . . . G5 . F5 . D5 . . . F5 . E5 .", "C5 . . . . . . . - - - - G4 . Bb4 .",
        "A4 . . . D5 . F5 . . . A5 . . . G5 .", "F5 . . . Db5 . . . Bb4 . . . Db5 . F5 .",
        "E5 . . . . . C5 . A4 . . . C5 . E5 .", "F#5 . . . . . . . A5 . . . F#5 . D5 .",
        "G5 . . . F5 . D5 . Bb4 . . . D5 . F5 .", "E5 . . . . . G5 . Bb5 . . . A5 . G5 .",
        "A5 . . . . . . . F5 . . . C5 . A4 .", "G4 . . . . . . . - - - - - - - -"), legato=0.95)
    return tema
