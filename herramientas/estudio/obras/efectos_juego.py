"""
Efectos de la partida: la nave, las monedas, el combo, los power-ups y las mejoras
(LISTA_DE_SONIDOS.md, secciones 2, 3 y 4).

Cada efecto en capas: el TONO (lo que canta, en la pentatonica de Do), el CUERPO (un grave
corto que le da peso) y el AIRE (ruido filtrado: el swish o el brillo del ataque).
"""
from herramientas.estudio.obra import Efecto
from herramientas.estudio.obras import obra
from herramientas.estudio import instrumentos as I
from herramientas.estudio.obras.capas import tono, deslizar, cuerpo, aire, explosion, golpe, abrir_acorde
from herramientas.estudio.obras.efectos_interfaz import registrar_familia

# La moneda por multiplicador: (subida, principal, armonia). La principal sube por la pentatonica
# y cada multiplicador suma una capa (x2 una segunda voz, x3 el brillo de la octava, x4 una
# nota mas en la subida, x5 un destello): el oido "lee" el combo sin mirar el HUD. La segunda
# voz es la ultima nota de la subida, que se queda sonando: nunca dos notas vecinas a la vez
# (a un tono de distancia, en el agudo, raspan)
MONEDAS = [("G5", "C6", None), ("A5", "D6", "A5"), ("C6", "E6", "C6"), ("G5 D6", "G6", "D6"), ("A5 D6", "A6", "D6")]

# La cadena de dash perfectos arma un acorde de Do abierto: cada perfecto agrega una nota. Antes
# era un Do 6/9 (Mi Sol La Do Re): Sol y La juntos en el medio raspaban (una segunda)
CADENA = [["G5"], ["C5", "G5"], ["C5", "G5", "E6"], ["C5", "G5", "C6", "E6"], ["G4", "C5", "G5", "C6", "E6"]]


# ---------- La nave ----------

def _dash(numero, pico):
    # Sin altura (nunca desafina): el aire sube y baja en 180 ms (lo que dura el dash) y un
    # "fum" grave le da el empujon. Tres variantes con el pico del filtro en otro lugar
    efecto = Efecto("nave_dash_%d" % numero, 0.3, "mf", sala=(0.8, 0.4))
    aire(efecto, 0.2, [(0, 600), (0.06, pico), (0.2, 900)], modo="banda", resonancia=0.35, reverb=0.12,
         forma=[(0, 0), (0.015, 1), (0.08, 0.7), (0.2, 0)], eq=[("corte_agudos", 5000)])
    cuerpo(efecto, 110, 55, 0.12)
    return efecto


registrar_familia("nave_dash", [2200, 2600, 1900], _dash)


@obra("nave_dash_extra")
def nave_dash_extra():
    # El segundo dash (DOBLE DASH): el mismo soplido mas arriba y una chispa
    efecto = _dash(4, 3400)
    efecto.nombre = "nave_dash_extra"
    tono(efecto, I.CRISTAL, "-:40 E5:120", volumen=-10)
    return efecto


@obra("dash_listo")
def dash_listo():
    # El dash se recargo: una gota de luz, casi imperceptible
    efecto = Efecto("dash_listo", 0.08, "pp", sala=(0.6, 0.5))
    tono(efecto, I.CRISTAL, "E6:60", reverb=0.3)
    return efecto


@obra("escudo_roto")
def escudo_roto():
    # Vidrio de energia que se quiebra: chasquido agudo, los pedazos que caen y un golpe
    efecto = Efecto("escudo_roto", 0.45, "f", sala=(1.0, 0.5))
    aire(efecto, 0.15, [(0, 4000), (0.15, 2000)], modo="banda", resonancia=0.2, volumen=-3)
    tono(efecto, I.CRISTAL, "E6:30 C6:30 A5:30 E5:200", reverb=0.3)
    cuerpo(efecto, 160, 60, 0.2, volumen=-4)
    return efecto


@obra("nave_golpe")
def nave_golpe():
    # Te pegaron: un impacto grave que cae, una explosion corta y un acorde apagado que
    # "duele" (Si Do Fa: el tritono y la segunda menor de la escala, sin salirse de ella)
    efecto = Efecto("nave_golpe", 0.7, "f", sala=(1.2, 0.3))
    deslizar(efecto, I.BAJO_RUGIDO, [(0, 180), (0.25, 45)], volumen=-2, fuerza=1.0, reverb=0.0)
    aire(efecto, 0.45, [(0, 5000), (0.4, 300)], reverb=0.2, forma=[(0, 0), (0.004, 1), (0.45, 0)])
    tono(efecto, I.PAD_OSCURO, "B3+C4+F4:250", volumen=-10, reverb=0.3)
    return efecto


@obra("ultima_vida")
def ultima_vida():
    # Te queda una vida: alarma de tritono (Si / Fa) dos veces, con cuerpo (no un pitido)
    efecto = Efecto("ultima_vida", 1.0, "f", sala=(1.0, 0.4))
    tono(efecto, I.SIRENA, "B4:90 F5:90 B4:90 F5:90 -:120 B4:90 F5:90 B4:90 F5:90", legato=0.85, reverb=0.15)
    return efecto


@obra("fenix")
def fenix():
    # Renaces: una llamarada que sube y de La menor a Do mayor (de la muerte a la vida)
    efecto = Efecto("fenix", 0.9, "f", sala=(1.8, 0.5))
    aire(efecto, 0.35, [(0, 400), (0.35, 6000)], forma=[(0, 0), (0.3, 1), (0.35, 0)], volumen=-4, reverb=0.3)
    tono(efecto, I.EPIANO, "A3:60 C4:60 E4:60 C4+E4+G4+C5!:600", inicio=0.2)
    tono(efecto, I.PAD_CALIDO, "-:180 C4+G4+E5:600", inicio=0.2, volumen=-6, reverb=0.4)
    tono(efecto, I.CRISTAL, "-:180 C6:500", inicio=0.2, volumen=-8, reverb=0.4)
    return efecto


@obra("nave_muerte")
def nave_muerte():
    # La nave explota: la explosion mas grande y un acorde de La menor que se hunde
    efecto = Efecto("nave_muerte", 1.6, "ff", sala=(2.2, 0.3))
    explosion(efecto, 1.4, brillo=7000, grave=(110, 28))
    explosion(efecto, 0.6, brillo=3000, inicio=0.15, volumen=-6)
    deslizar(efecto, I.PAD_OSCURO, [(0, "A3"), (1.4, "E3")], inicio=0.05, volumen=-8, reverb=0.4)
    return efecto


@obra("hiperespacio")
def hiperespacio():
    # El salto: sube y baja en 1.5 s como la velocidad de las estrellas (velocidad_salto)
    efecto = Efecto("hiperespacio", 1.5, "f", sala=(1.6, 0.5))
    aire(efecto, 1.5, [(0, 300), (0.75, 3200), (1.5, 400)], modo="banda", resonancia=0.4,
         forma=[(0, 0), (0.6, 1), (1.5, 0)], reverb=0.2)
    deslizar(efecto, I.LASER, [(0, "C3"), (0.75, "C6"), (1.5, "C4")], volumen=-8, delay=0.2, tremolo=(2, 10, 0.3))
    cuerpo(efecto, 50, 80, 1.2, volumen=-8)
    return efecto


# ---------- Monedas y puntos ----------

def _moneda(numero, notas):
    # Un "ding-ding" de cristal (sube una cuarta, como las monedas de siempre) con un piano
    # electrico una octava abajo que le da cuerpo. Antes el cuerpo era un PLUCK (sierras
    # saturadas): zumbaba debajo del cristal
    subida, principal, armonia = notas
    pasos = subida.split()
    llegada = 45 * len(pasos)                   # ms hasta la nota principal
    notas_subida = " ".join("%s:45" % nota for nota in pasos) + " "
    efecto = Efecto("moneda_%d" % numero, 0.4, "mf", sala=(1.0, 0.45))
    tono(efecto, I.CRISTAL, notas_subida + "%s!:260" % principal, reverb=0.18)
    tono(efecto, I.EPIANO, notas_subida + "%s:200" % principal, volumen=-9, reverb=0.1, transponer=-12)
    if armonia:
        tono(efecto, I.CRISTAL, "-:%d %s:220" % (llegada, armonia), volumen=-7, reverb=0.18)
    if numero >= 3:
        tono(efecto, I.CRISTAL, "-:%d %s:160" % (llegada, principal), volumen=-15, reverb=0.25, transponer=12)
    if numero == 5:
        aire(efecto, 0.12, [(0, 3000), (0.12, 6000)], inicio=0.08, modo="banda", resonancia=0.3, volumen=-16,
             chasquidos=90, reverb=0.3)
    return efecto


registrar_familia("moneda", MONEDAS, _moneda)


@obra("oro_brillo")
def oro_brillo():
    # En la fiebre del oro, encima de la moneda: una campanita mas
    efecto = Efecto("oro_brillo", 0.4, "p", sala=(1.2, 0.5))
    tono(efecto, I.CAMPANA, "-:30 G5:120 C6:250", reverb=0.4, transponer=-12)
    return efecto


def _combo_sube(numero, notas):
    # Sube el multiplicador: tres notas que terminan en la moneda del multiplicador nuevo
    efecto = Efecto("combo_sube_%d" % numero, 0.3, "mf", sala=(1.0, 0.5))
    tono(efecto, I.CRISTAL, "%s:40 %s:40 %s!:220" % notas, reverb=0.25)
    tono(efecto, I.EPIANO, "%s:40 %s:40 %s:200" % notas, volumen=-6, transponer=-12)
    return efecto


# Arpegios con saltos (quintas, cuartas, sextas), nunca escalas: el cristal sigue sonando debajo
# de la nota siguiente y una escala rapida (Sol La Re) dejaba segundas apiladas que raspaban
registrar_familia("combo_sube", [("D5", "G5", "D6"), ("C5", "G5", "E6"), ("G5", "D6", "G6")], _combo_sube)


@obra("combo_max")
def combo_max():
    # x5: el arpegio de Do que sube de a saltos y el acorde abierto, lo mas brillante de la paleta.
    # Antes era la escala entera y un acorde con La y Sol juntos en el agudo: un racimo
    efecto = Efecto("combo_max", 0.7, "f", sala=(1.6, 0.5))
    tono(efecto, I.CRISTAL, "C5:30 G5:30 C6:30 E6:30 G6:30 C6+G6+C7!:450", reverb=0.3, delay=0.15)
    tono(efecto, I.EPIANO, "-:150 C4+G4+E5:450", volumen=-4, reverb=0.3)
    golpe(efecto, "K", 0.15, 0.5, volumen=-10)
    return efecto


@obra("combo_cortado")
def combo_cortado():
    # Se corto el combo: dos notas que caen (una tercera menor) y se desinflan
    efecto = Efecto("combo_cortado", 0.3, "p", sala=(0.8, 0.4))
    deslizar(efecto, I.LEAD_HUECO, [(0, "G4"), (0.08, "G4"), (0.1, "E4"), (0.28, "D4")], volumen=-2)
    return efecto


def _perfecto(numero, notas):
    # Un "corte" de aire + un golpe grave + el acorde de la cadena que se arma nota por nota
    efecto = Efecto("perfecto_%d" % numero, 0.9, "f", sala=(1.4, 0.5))
    aire(efecto, 0.09, [(0, 3500), (0.09, 1200)], modo="banda", resonancia=0.3, volumen=-4, reverb=0.15,
         forma=[(0, 0), (0.003, 1), (0.09, 0)])
    cuerpo(efecto, 130, 65, 0.08, volumen=-8)
    abrir_acorde(efecto, I.CRISTAL, notas, inicio=0.02, largo=0.4, reverb=0.3, delay=0.15)
    abrir_acorde(efecto, I.EPIANO, notas, inicio=0.02, largo=0.35, volumen=-6)
    return efecto


registrar_familia("perfecto", CADENA, _perfecto)


@obra("interceptado")
def interceptado():
    # Frenaste una embestida: "clang" de metal (inarmonico a proposito) y un golpe seco
    efecto = Efecto("interceptado", 0.5, "f", sala=(1.0, 0.4))
    tono(efecto, I.METAL, "A3:400", reverb=0.2)
    aire(efecto, 0.04, [(0, 4000)], volumen=-4)
    cuerpo(efecto, 150, 60, 0.12, volumen=-4)
    return efecto


@obra("record")
def record():
    # ¡Nuevo record!: jingle arcade en Do con bajo y platillo (distinto del logro)
    efecto = Efecto("record", 1.0, "ff", sala=(1.6, 0.5))
    tono(efecto, I.LEAD_CALIDO, "C5:80 E5:80 G5:80 C6:160 G5:80 C6!:500", reverb=0.25, delay=0.15)
    tono(efecto, I.BAJO_ANALOGICO, "C3:240 G2:160 C3:500", volumen=-6)
    tono(efecto, I.EPIANO, "-:400 C4+E4+G4+C5:500", volumen=-6)
    golpe(efecto, "X", 0.48, 0.7, volumen=-10, reverb=0.3)
    golpe(efecto, "K", 0.0, 0.7, volumen=-8)
    golpe(efecto, "K", 0.48, 0.8, volumen=-8)
    return efecto


@obra("nivel")
def nivel():
    # Subiste de nivel: arpegio de Do que sube y queda vibrando
    efecto = Efecto("nivel", 0.5, "mf", sala=(1.2, 0.5))
    tono(efecto, I.EPIANO, "C4:35 E4:35 G4:35 C5!:300")
    tono(efecto, I.CRISTAL, "C5:35 E5:35 G5:35 C6:280", volumen=-6, reverb=0.3)
    return efecto


@obra("bala_rota")
def bala_rota():
    # Rompiste un misil o un meteoro con el dash: pop metalico
    efecto = Efecto("bala_rota", 0.2, "mf", sala=(0.6, 0.4))
    aire(efecto, 0.06, [(0, 3000), (0.06, 800)], volumen=-2)
    tono(efecto, I.MARIMBA, "D5:60", volumen=-4)
    cuerpo(efecto, 120, 60, 0.06, volumen=-8)
    return efecto


# ---------- Power-ups ----------

@obra("capsula")
def capsula():
    # Cae una capsula: dos gotas de cristal que bajan una cuarta ("llego algo"). Sol -> Re: una
    # cuarta en todos los colores (antes La -> Mi, que sobre un acorde con septima era un
    # tritono) y en su octava (antes era una campana una octava abajo, metalica y hueca)
    efecto = Efecto("capsula", 0.3, "p", sala=(1.2, 0.5))
    tono(efecto, I.CRISTAL, "G5:60 D5:220", reverb=0.3, delay=0.15)
    tono(efecto, I.EPIANO, "G4:60 D4:200", volumen=-9, reverb=0.1)
    return efecto


@obra("pw_escudo")
def pw_escudo():
    # Una armadura de energia: sube y se cierra en una quinta abierta
    efecto = Efecto("pw_escudo", 0.5, "f", sala=(1.2, 0.5))
    deslizar(efecto, I.LASER, [(0, "C3"), (0.15, "C4")], volumen=-6)
    tono(efecto, I.PAD_CALIDO, "-:140 C4+G4+C5:350", volumen=-2, reverb=0.3)
    tono(efecto, I.CRISTAL, "-:140 G5:300", volumen=-8)
    return efecto


@obra("pw_hielo")
def pw_hielo():
    # Todo se congela: una cascada de cristal que cae y un crujido. Cae por quintas y cuartas
    # (Sol Re Sol Re Sol): cada nota sigue sonando debajo de la siguiente, y con la escala
    # entera (Do La Sol Mi Re Do) se apilaban segundas: un racimo que raspaba
    efecto = Efecto("pw_hielo", 0.6, "f", sala=(1.6, 0.6))
    tono(efecto, I.CRISTAL, "G6:35 D6:35 G5:35 D5:35 G4!:300", reverb=0.4, delay=0.15)
    aire(efecto, 0.25, [(0, 3500)], modo="banda", volumen=-8, chasquidos=60)
    return efecto


@obra("pw_vida")
def pw_vida():
    # Una vida mas: un "1UP" propio, alegre
    efecto = Efecto("pw_vida", 0.6, "f", sala=(1.2, 0.5))
    # Termina en la octava (Do): antes en La, que sobre un acorde con septima chocaba con el Mi
    tono(efecto, I.EPIANO, "G4:75 C5:75 E5:75 G5:150 E5:75 C6!:300")
    tono(efecto, I.CRISTAL, "G5:75 C6:75 E6:75 G6:150 E6:75 C7:300", volumen=-10, reverb=0.3)
    return efecto


@obra("pw_iman")
def pw_iman():
    # Un iman: una nota que ondula fuerte y sube
    efecto = Efecto("pw_iman", 0.4, "mf", sala=(1.0, 0.4))
    deslizar(efecto, I.LEAD_HUECO, [(0, "D4"), (0.35, "A4")], tremolo=(12, 12, 0.6))
    return efecto


@obra("pw_doble")
def pw_doble():
    # El doble: la misma nota y su octava
    efecto = Efecto("pw_doble", 0.4, "f", sala=(1.2, 0.5))
    tono(efecto, I.CRISTAL, "C5:90 C6!:300", reverb=0.3)
    tono(efecto, I.EPIANO, "C4:90 C5:300", volumen=-6)
    return efecto


@obra("pw_turbo")
def pw_turbo():
    # El motor acelera: un arpegio que se apura mientras todo sube
    efecto = Efecto("pw_turbo", 0.5, "f", sala=(0.8, 0.4))
    tono(efecto, I.PLUCK, "C4:60 E4:55 G4:50 C5:45 E5:40 G5:35 C6:200")
    deslizar(efecto, I.BAJO_ANALOGICO, [(0, "C2"), (0.45, "C3")], volumen=-6)
    return efecto


@obra("pw_recarga")
def pw_recarga():
    # Carga electrica: arpegio de fusas que sube y una chispa
    efecto = Efecto("pw_recarga", 0.35, "f", sala=(0.9, 0.4))
    tono(efecto, I.PLUCK, "C4:30 E4:30 G4:30 C5:30 E5:30 G5:30 C6:150")
    aire(efecto, 0.06, [(0, 3000)], inicio=0.2, modo="banda", volumen=-6)
    return efecto


@obra("pw_nova")
def pw_nova():
    # Queda armada: una quinta grave que tiembla cada vez mas rapido. Do + Sol: quinta en todos
    # los colores (La + Mi, sobre un acorde con septima, se volvia un tritono)
    efecto = Efecto("pw_nova", 0.6, "mf", sala=(1.0, 0.4))
    tono(efecto, I.PAD_OSCURO, "C3+G3:550", tremolo=(4, 14, 0.5))
    tono(efecto, I.BAJO_SUB, "C2:550", volumen=-4)
    return efecto


@obra("nova")
def nova():
    # La nova estalla al terminar el dash
    efecto = Efecto("nova", 0.8, "f", sala=(1.6, 0.4))
    explosion(efecto, 0.7, brillo=7000, grave=(165, 40))
    tono(efecto, I.CAMPANA, "-:150 A5:400", volumen=-10, reverb=0.4)
    return efecto


@obra("pw_acaba")
def pw_acaba():
    # A un power-up le queda poco: un tic suave (suena tres veces)
    efecto = Efecto("pw_acaba", 0.06, "pp", sala=(0.4, 0.4))
    tono(efecto, I.MARIMBA, "E5:40")
    return efecto


@obra("pw_fin")
def pw_fin():
    # Se termino: tres notas que caen y la ultima se desinfla
    efecto = Efecto("pw_fin", 0.35, "p", sala=(0.8, 0.4))
    tono(efecto, I.EPIANO, "G4:50 E4:50")
    deslizar(efecto, I.EPIANO, [(0, "C4"), (0.2, "A3")], inicio=0.1)
    return efecto


def _hielo_roto(numero, nota):
    efecto = Efecto("hielo_roto_%d" % numero, 0.25, "mf", sala=(1.0, 0.5))
    aire(efecto, 0.08, [(0, 3500), (0.08, 2200)], modo="banda", volumen=-4, chasquidos=200)
    tono(efecto, I.CRISTAL, nota + ":200", reverb=0.3)
    cuerpo(efecto, 140, 70, 0.06, volumen=-10)
    return efecto


registrar_familia("hielo_roto", ["E5", "G5", "A5"], _hielo_roto)


# ---------- Mejoras ----------

@obra("mejora_elegida")
def mejora_elegida():
    # El acorde de Do que se abre nota por nota, abierto (antes un Do 6/9: Re y Mi juntos raspaban)
    efecto = Efecto("mejora_elegida", 0.7, "f", sala=(1.6, 0.5))
    abrir_acorde(efecto, I.EPIANO, ["C4", "G4", "C5", "E5", "C6"], largo=0.6)
    tono(efecto, I.CRISTAL, "-:100 G5:450", volumen=-8, reverb=0.4, delay=0.2)
    tono(efecto, I.PAD_CALIDO, "C4+G4+E5:550", volumen=-10, reverb=0.4)
    return efecto


def _onda(numero, desde):
    # La mejora ONDA al final de cada dash: un "fum" grave y corto (suena mucho: bajito)
    efecto = Efecto("onda_%d" % numero, 0.25, "p", sala=(0.8, 0.4))
    cuerpo(efecto, desde, desde / 2, 0.2, volumen=0)
    aire(efecto, 0.2, [(0, 1500), (0.2, 200)], volumen=-6)
    return efecto


registrar_familia("onda", [110, 98], _onda)


@obra("eco")
def eco():
    # La copia del ECO repite el dash: el mismo soplido, mas lejano y con ecos
    efecto = Efecto("eco", 0.6, "p", sala=(1.4, 0.5))
    aire(efecto, 0.2, [(0, 400), (0.06, 1400), (0.2, 500)], modo="banda", resonancia=0.35, reverb=0.4,
         forma=[(0, 0), (0.015, 1), (0.2, 0)])
    efecto.pistas[-1].delay = 0.6
    tono(efecto, I.CRISTAL, "-:20 E5:150", volumen=-12, delay=0.4)
    return efecto


def _roce(numero, nota):
    # ESCUDO ROCE: cada perfecto suma carga (una nota mas arriba cada vez)
    efecto = Efecto("roce_carga_%d" % numero, 0.1, "pp", sala=(0.6, 0.5))
    tono(efecto, I.CRISTAL, nota + ":60")
    return efecto


registrar_familia("roce_carga", ["C5", "D5", "E5", "G5", "A5", "C6"], _roce)


@obra("dash_vacio")
def dash_vacio():
    # Pediste el dash sin recarga: un clic seco y apagado ("todavia no")
    efecto = Efecto("dash_vacio", 0.06, "pp", sala=(0.4, 0.4), cola=0.05)
    aire(efecto, 0.015, [(0, 1500)])
    tono(efecto, I.BAJO_SUB, "C3:40", volumen=-4)
    return efecto


@obra("latido")
def latido():
    # Te queda una vida (opcion LATIDO): dos golpes graves, como un corazon
    efecto = Efecto("latido", 0.4, "p", sala=(0.5, 0.3))
    cuerpo(efecto, 70, 45, 0.08, volumen=0)
    cuerpo(efecto, 65, 42, 0.06, inicio=0.16, volumen=-3)
    return efecto
