"""
Los temas de los jefes (dan la vuelta sin costura). Antes eran chiptune (del compositor
viejo); se rehicieron en el estudio para que todo el juego tenga un solo sonido: mismas
melodias, acordes y personalidad, con los sintes, la sala y el master de "Neon en ruta".

Todos en Re menor: los efectos de los jefes (efectos_jefes.py) estan pensados en Re menor y
afinan con cualquiera de estos temas. Cada uno con el caracter de su jefe:

    musica_jefe              EL OJO              150 bpm, riff de semicorcheas al final
    musica_jefe_fortaleza    ACORAZADO IMPERIAL  marcha militar, 132 bpm
    musica_jefe_serpiente    DEVORADORA          120 bpm con swing, flauta de encantador
    musica_jefe_colmena      MADRE DEL ENJAMBRE  160 bpm, las alas zumban en el grave
    musica_jefe_singularidad EL FIN DE LA LUZ    100 bpm a medio tiempo, sala enorme

El ultimo compas de cada uno (La, el V de Re) prepara la vuelta al primero (Re menor).
"""
from herramientas.estudio.obra import Obra
from herramientas.estudio.obras import obra
from herramientas.estudio import instrumentos as I


def compases(*grillas):
    return " | ".join(grillas)


def bateria(tema, bombo, caja, hats, compases_de_corte=(), corte=None, platillos=(0,), volumen_hats=-10.0):
    # La bateria de un jefe: cada pieza en su pista. 'bombo', 'caja' y 'hats' son el patron
    # de un compas; en 'compases_de_corte' (los finales de frase) la caja hace 'corte'
    pistas = {
        "bombo": tema.bateria("bombo", volumen=-2.0, eq=[("corte_graves", 35), ("campana", 3000, 3, 1.0)]),
        "caja": tema.bateria("caja", volumen=-6.0, reverb=0.35, eq=[("corte_graves", 120), ("agudos", 8000, 2)]),
        "hats": tema.bateria("hats", volumen=volumen_hats, paneo=-0.2, reverb=0.1, eq=[("corte_agudos", 16000)]),
        "toms": tema.bateria("toms", volumen=-6.0, reverb=0.3),
        "platillos": tema.bateria("platillos", volumen=-11.0, reverb=0.25, eq=[("corte_agudos", 14000)]),
    }
    for compas in range(len(tema.acordes)):
        pistas["bombo"].grilla(bombo(compas) if callable(bombo) else bombo, desde=compas)
        pistas["caja"].grilla(corte if compas in compases_de_corte and corte else caja, desde=compas)
        pistas["hats"].grilla(hats(compas) if callable(hats) else hats, desde=compas)
    for compas in compases_de_corte:
        pistas["toms"].grilla("- - - - - - - - - - - - T T t t", desde=compas)
    for compas in platillos:
        pistas["platillos"].grilla("X - - - - - - - - - - - - - - -", desde=compas)
    return pistas


@obra("musica_jefe")
def musica_jefe():
    # EL OJO - "Mirada fija": Re menor, 150 bpm, 24 compases (~38 s).
    #   A (1-8)   la melodia presenta al jefe
    #   B (9-16)  sube: la melodia en el agudo y los hats en semicorcheas
    #   C (17-24) el riff de semicorcheas (la melodia calla salvo dos frases) y el bajo empuja
    tema = Obra("musica_jefe", bpm=150, sala=(2.0, 0.35), eco=0.75, realimentacion=0.3, objetivo=-14.0,
                acordes=["Dm", "Dm", "Bb", "C", "Dm", "Dm", "Bb", "A",
                         "Gm", "Dm", "Bb", "A", "Gm", "Dm", "E", "A",
                         "Bb", "C", "Dm", "Dm", "Bb", "C", "A", "A"])
    corcheas = "h - h? - h - h? - h - h? - h - h? -"
    semicorcheas = "h h? h h? h h? h H h h? h h? h h? h H"
    bateria(tema, lambda c: "K - - - - - - K K - - - - - - -" if c < 16 else "K - - K - - K - K - - K - - K -",
            "- - - - S - - - - - - - S - - -", lambda c: corcheas if c < 8 else semicorcheas,
            compases_de_corte=(7, 15, 23), corte="- - - - S - - - - - - - S - S? S", platillos=(0, 8, 16))

    bajo = tema.pista("bajo", I.BAJO_RUGIDO, volumen=-5.0, bombeo=0.3, eq=[("corte_graves", 32)])
    bajo.bajo("R! . R 8 R . R 8 R . R 8 R . 8 R")
    pad = tema.pista("pad", I.PAD_OSCURO, volumen=-12.0, reverb=0.35, bombeo=0.5, eq=[("corte_graves", 180)],
                     ancho=1.3)
    pad.acordes("X . . . . . . . . . . . . . . .", registro=("A3", "E5"))
    arpegio = tema.pista("arpegio", I.PLUCK, volumen=-15.0, delay=0.3, reverb=0.2, ancho=1.4,
                         eq=[("corte_graves", 250)])
    arpegio.arpegio([0, 2, 1, 2], base="D4")

    lead = tema.pista("lead", I.LEAD_CALIDO, volumen=-7.0, delay=0.2, reverb=0.3,
                      eq=[("corte_graves", 200), ("campana", 2800, -2, 1.0)])
    lead.grilla(compases(
        "D5 . . . . . A4 . D5 . F5 . . . E5 .", "D5 . . . . . . . - - A4 . C5 . D5 .",
        "F5 . . . . . D5 . Bb4 . . . D5 . F5 .", "E5 . . . . . C5 . G4 . . . C5 . E5 .",
        "D5 . . . . . A4 . D5 . F5 . . . A5 .", "G5 . F5 . E5 . D5 . . . . . C5 . D5 .",
        "F5 . . . D5 . . . Bb5 . . . A5 . G5 .", "A5 . . . . . . . C#5 . . . E5 . . .",
        "G5 . . . . . Bb5 . . . A5 . G5 . F5 .", "A5 . . . . . . . F5 . . . D5 . . .",
        "D6 . . . C6 . Bb5 . . . A5 . Bb5 . C6 .", "A5 . . . . . . . E5 . . . C#5 . . .",
        "G5 . . . Bb5 . D6 . . . C6 . Bb5 . A5 .", "A5 . . . F5 . A5 . D6 . . . . . . .",
        "G#5 . . . B5 . . . E6 . . . D6 . B5 .", "C#6 . . . . . . . A5 . . . E5 . C#5 .",
        "- - - - - - - - - - - - - - - -", "- - - - - - - - - - - - - - - -",
        "- - - - - - - - - - - - - - - -", "D6 . . . . . . . A5 . . . F5 . . .",
        "- - - - - - - - - - - - - - - -", "- - - - - - - - - - - - - - - -",
        "- - - - - - - - - - - - - - - -", "C#5 . . . E5 . . . G5 . . . A5 . . ."), transponer=-12)

    # El riff (compases 17 a 19 y 21 a 23): semicorcheas que suben con cada acorde
    riff = tema.pista("riff", I.PLUCK, volumen=-8.0, delay=0.15, reverb=0.15, paneo=0.15, eq=[("corte_graves", 220)])
    riff.grilla(compases(
        "D5 F5 Bb5 F5 D5 F5 Bb5 F5 D5 F5 Bb5 F5 C6 Bb5 A5 F5",
        "E5 G5 C6 G5 E5 G5 C6 G5 E5 G5 C6 G5 D6 C6 Bb5 G5",
        "F5 A5 D6 A5 F5 A5 D6 A5 F5 A5 D6 A5 E6 D6 C6 A5",
        "- - - - - - - - - - - - - - - -",
        "D5 F5 Bb5 F5 D5 F5 Bb5 F5 D5 F5 Bb5 F5 C6 Bb5 A5 F5",
        "E5 G5 C6 G5 E5 G5 C6 G5 E5 G5 C6 G5 D6 C6 Bb5 G5",
        "E5 A5 C#6 A5 E5 A5 C#6 A5 E6 . C#6 . A5 . E5 .",
        "- - - - - - - - - - - - - - - -"), desde=16, transponer=-12, legato=0.7)
    return tema


@obra("musica_jefe_fortaleza")
def musica_jefe_fortaleza():
    # ACORAZADO IMPERIAL - "Marcha imperial": Re menor, 132 bpm, 16 compases (~29 s). Redoblante
    # de desfile, bajo "oom-pah" (fundamental y quinta), acordes cortos como golpes de metal y
    # una melodia de metales con puntillos (el lead doblado por el metal una octava abajo)
    tema = Obra("musica_jefe_fortaleza", bpm=132, sala=(2.2, 0.3), eco=0.75, realimentacion=0.25, objetivo=-14.0,
                acordes=["Dm", "Dm", "Gm", "A", "Dm", "Bb", "Gm", "A",
                         "Bb", "C", "Dm", "Dm", "Gm", "A", "Dm", "A"])
    bateria(tema, "K - - - - - - - K - - - - - - -", "- - - - S - - S? - - - - S - S? S",
            "h - - - h - - - h - - - h - - -", compases_de_corte=(7, 15),
            corte="S? S? S S S? S? S S S? S? S S S S S! S", platillos=(0, 8), volumen_hats=-13.0)

    bajo = tema.pista("bajo", I.BAJO_ANALOGICO, volumen=-4.0, bombeo=0.25, eq=[("corte_graves", 32)])
    bajo.bajo("R! . . . 5 . . . R . . . 5 . 5 .")
    golpes = tema.pista("golpes", I.PLUCK, volumen=-11.0, reverb=0.25, ancho=1.2, eq=[("corte_graves", 200)])
    golpes.acordes("X - - - X - - - X - - - X - X -", registro=("A3", "E5"), legato=0.5)
    pad = tema.pista("pad", I.PAD_OSCURO, volumen=-15.0, reverb=0.35, eq=[("corte_graves", 180)])
    pad.acordes("X . . . . . . . . . . . . . . .", registro=("D3", "A4"))

    melodia = compases(
        "D4 . . A4 . . D5 . . . . . F5 . E5 .", "D5 . . . . . . . A4 . . . . . . .",
        "G4 . . Bb4 . . D5 . . . . . G5 . F5 .", "E5 . . . . . . . C#5 . . . A4 . . .",
        "D4 . . A4 . . D5 . . . . . F5 . A5 .", "Bb5 . . . . . A5 . G5 . . . F5 . . .",
        "G5 . . F5 . . E5 . . . D5 . E5 . . .", "A4 . . . . . . . - - - - C#5 . E5 .",
        "F5 . . . . . D5 . Bb4 . . . D5 . F5 .", "G5 . . . . . E5 . C5 . . . E5 . G5 .",
        "A5 . . . . . . . F5 . . . D5 . . .", "A4 . . D5 . . F5 . . A5 . . . . . .",
        "Bb5 . . . A5 . G5 . . . F5 . G5 . . .", "A5 . . . . . . . E5 . . . C#5 . . .",
        "D5 . . F5 . . A5 . . . D6 . . . . .", "C#6 . . . . . . . A5 . . . E5 . C#5 .")
    lead = tema.pista("lead", I.LEAD_CALIDO, volumen=-7.0, delay=0.15, reverb=0.3, saturacion=0.2,
                      eq=[("corte_graves", 200), ("campana", 1800, 2, 1.0)])
    lead.grilla(melodia, transponer=-12)
    metal = tema.pista("metal", I.METAL, volumen=-19.0, reverb=0.25, paneo=-0.2, eq=[("corte_graves", 150)])
    metal.grilla(melodia, transponer=-24)
    return tema


@obra("musica_jefe_serpiente")
def musica_jefe_serpiente():
    # DEVORADORA DE ESTRELLAS - "Danza de escamas": Re menor, 120 bpm con swing, 16 compases
    # (~32 s). Una flauta de encantador de serpientes con adornos frigios (Mib de paso) sobre
    # un ritmo que se balancea, y campanas que ondulan
    tema = Obra("musica_jefe_serpiente", bpm=120, swing=0.3, sala=(2.6, 0.4), eco=0.75, realimentacion=0.35,
                objetivo=-14.0,
                acordes=["Dm", "Dm", "Gm", "Dm", "Bb", "A", "Dm", "Dm",
                         "Gm", "Gm", "Dm", "Dm", "Bb", "A", "Dm", "A"])
    bateria(tema, "K - - K - - - - K - K - - - - -", "- - - - - - S - - - - - S - - -",
            "h - h? h h - h? h h - h? h h - h? h", compases_de_corte=(7, 15),
            corte="- - - - - - S - - - S - S S? S S", platillos=(0, 8), volumen_hats=-12.0)

    bajo = tema.pista("bajo", I.BAJO_SUB, volumen=-4.0, bombeo=0.25)
    bajo.bajo("R! . . R . . 5 . R . . R . . 8 .")
    pad = tema.pista("pad", I.PAD_OSCURO, volumen=-14.0, reverb=0.4, bombeo=0.4, chorus=(0.004, 0.4, 0.4),
                     eq=[("corte_graves", 180)], ancho=1.3)
    pad.acordes("X . . . . . . . . . . . . . . .", registro=("A3", "E5"))
    campanas = tema.pista("campanas", I.CAMPANA, volumen=-18.0, delay=0.3, reverb=0.35, paneo=0.25,
                          eq=[("corte_graves", 300)])
    campanas.arpegio([0, 2, 1, 2], base="D4", cada=2)

    flauta = tema.pista("flauta", I.LEAD_HUECO, volumen=-6.0, delay=0.25, reverb=0.35, eq=[("corte_graves", 220)])
    flauta.grilla(compases(
        "D5 . Eb5 D5 C#5 . D5 . . . F5 . E5 . D5 .", "A4 . . . . . . . - - - - - - - -",
        "G4 . A4 Bb4 A4 . G4 . . . Bb4 . A4 . G4 .", "F4 . . . E4 . D4 . . . . . - - - -",
        "D5 . Eb5 D5 C5 . Bb4 . . . D5 . C5 . Bb4 .", "A4 . . . . . . . C#5 . . . E5 . . .",
        "F5 . E5 . D5 . Eb5 . D5 . . . . . . .", "- - - - - - - - A4 . D5 . F5 . A5 .",
        "Bb5 . A5 . G5 . . . A5 . Bb5 . A5 . G5 .", "D5 . . . . . . . - - G4 . A4 . Bb4 .",
        "A4 . . . D5 . . . F5 . E5 . D5 . C#5 .", "D5 . . . . . . . - - - - - - - -",
        "F5 . . . Eb5 . D5 . . . C5 . Bb4 . . .", "C#5 . . . E5 . . . A5 . . . G5 . E5 .",
        "F5 . E5 . D5 . . . A4 . . . D5 . . .", "C#5 . . . . . . . E5 . . . A4 . . ."))
    return tema


@obra("musica_jefe_colmena")
def musica_jefe_colmena():
    # MADRE DEL ENJAMBRE - "Enjambre de cristal": Re menor, 160 bpm, 16 compases (~24 s). Las
    # alas: un zumbido grave en semicorcheas que sigue los acordes; bajo en octavas y la
    # bateria empujando siempre
    tema = Obra("musica_jefe_colmena", bpm=160, sala=(1.8, 0.4), eco=0.75, realimentacion=0.3, objetivo=-14.0,
                acordes=["Dm", "C", "Bb", "A", "Dm", "C", "Bb", "C",
                         "Gm", "A", "Dm", "Bb", "Gm", "A", "Dm", "A"])
    bateria(tema, "K - - - - - - K K - - - - - - -", "- - - - S - - - - - - - S - - -",
            "h h? h h? h h? h h? h h? h h? h h? h h?", compases_de_corte=(7, 15),
            corte="- - - - S - - - - - S - S S S S", platillos=(0, 8), volumen_hats=-12.0)

    bajo = tema.pista("bajo", I.BAJO_RUGIDO, volumen=-5.0, bombeo=0.3, eq=[("corte_graves", 32)])
    bajo.bajo("R! . 8 . R . 8 . R . 8 . R . 8 .")
    alas = tema.pista("alas", I.ZUMBIDO, volumen=-15.0, reverb=0.15, paneo=-0.15, bombeo=0.3,
                      eq=[("corte_graves", 150), ("corte_agudos", 3500)])
    alas.arpegio([0, 0, 1, 0, 2, 0, 1, 0], base="D3", legato=0.7)
    pad = tema.pista("pad", I.PAD_OSCURO, volumen=-14.0, reverb=0.35, bombeo=0.5, eq=[("corte_graves", 180)],
                     ancho=1.3)
    pad.acordes("X . . . . . . . . . . . . . . .", registro=("A3", "E5"))

    lead = tema.pista("lead", I.LEAD_CALIDO, volumen=-7.0, delay=0.15, reverb=0.25,
                      eq=[("corte_graves", 200), ("campana", 2800, -2, 1.0)])
    lead.grilla(compases(
        "D5 . F5 . A5 . . . G5 . F5 . E5 . D5 .", "E5 . . . C5 . . . G4 . . . C5 . E5 .",
        "F5 . . . D5 . . . Bb4 . . . D5 . F5 .", "E5 . . . . . . . C#5 . . . . . . .",
        "A5 . . . G5 . F5 . . . E5 . F5 . A5 .", "G5 . . . E5 . C5 . . . E5 . G5 . . .",
        "F5 . . . D5 . Bb4 . . . D5 . F5 . . .", "E5 . . . . . . . G5 . . . . . . .",
        "Bb5 . . . A5 . G5 . . . D5 . G5 . . .", "A5 . . . . . E5 . . . C#5 . E5 . . .",
        "F5 . . . E5 . D5 . . . A4 . D5 . F5 .", "D5 . . . . . . . F5 . . . Bb5 . . .",
        "G5 . . . Bb5 . . . D6 . . . C6 . Bb5 .", "A5 . . . . . . . E5 . . . C#5 . . .",
        "D5 . . . F5 . . . A5 . . . D6 . . .", "C#6 . . . . . . . A5 . . . E5 . . ."), transponer=-12)
    return tema


@obra("musica_jefe_singularidad")
def musica_jefe_singularidad():
    # EL FIN DE LA LUZ - "Horizonte de sucesos": Re menor, 100 bpm a medio tiempo, 12 compases
    # (~29 s). Notas largas que caen al centro, campanas lentas con mucho eco y un bajo que
    # pesa, en una sala enorme y oscura (ni la luz escapa)
    tema = Obra("musica_jefe_singularidad", bpm=100, sala=(4.0, 0.25), eco=0.75, realimentacion=0.45,
                objetivo=-14.0,
                acordes=["Dm", "Dm", "Bb", "Bb", "Gm", "Gm", "A", "A", "Dm", "Bb", "Gm", "A"])
    bateria(tema, "K - - - - - - - - - - - - - K? -", "- - - - - - - - S - - - - - - -",
            "h - - - h? - - - h - - - h? - - -", compases_de_corte=(11,),
            corte="- - - - - - - - S - S? - S S S S", platillos=(0,), volumen_hats=-14.0)

    bajo = tema.pista("bajo", I.BAJO_SUB, volumen=-3.0, bombeo=0.2)
    bajo.bajo("R! . . . . . . . . . . . 5 . . .")
    pad = tema.pista("pad", I.PAD_OSCURO, volumen=-11.0, reverb=0.45, bombeo=0.3, chorus=(0.004, 0.3, 0.4),
                     eq=[("corte_graves", 160)], ancho=1.4)
    pad.acordes("X . . . . . . . . . . . . . . .", registro=("A3", "E5"))
    campanas = tema.pista("campanas", I.CAMPANA, volumen=-16.0, delay=0.4, reverb=0.45, paneo=0.2,
                          eq=[("corte_graves", 300)])
    campanas.arpegio([0, 1, 2, 3], base="D4", cada=4)

    lead = tema.pista("lead", I.LEAD_HUECO, volumen=-6.0, delay=0.3, reverb=0.45, eq=[("corte_graves", 200)])
    lead.grilla(compases(
        "D5 . . . . . . . . . . . A4 . . .", "F5 . . . . . . . E5 . . . D5 . . .",
        "D5 . . . . . . . . . . . F5 . . .", "Bb5 . . . . . . . A5 . . . F5 . . .",
        "G5 . . . . . . . . . . . D5 . . .", "Bb4 . . . . . . . C5 . . . D5 . . .",
        "E5 . . . . . . . . . . . . . . .", "C#5 . . . . . . . E5 . . . A5 . . .",
        "A5 . . . . . . . F5 . . . D5 . . .", "F5 . . . . . . . . . . . D5 . . .",
        "G5 . . . . . . . Bb5 . . . A5 . . .", "A5 . . . . . . . - - - - - - - -"), legato=0.97)
    return tema
