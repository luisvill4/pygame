"""
Efectos de los jefes (LISTA_DE_SONIDOS.md, secciones 7 y 8).

Todo en Re menor (la musica de los jefes). La tension sale de la PROPIA escala de Re menor:
la sexta menor (Sib, que quiere caer a La), el tritono Mi-Sib y la segunda menor La-Sib.
Antes usaba La bemol y Mi bemol (de afuera): repetidos en cada ataque, sonaban desafinados
contra la musica. Solo la ¡ALERTA! (que suena sola, en silencio) sigue con el tritono de
afuera. La ventana para pegarle ('vulnerable') resuelve SIN
tercera (La Re Mi La): suena bien sobre menor y mayor, y siempre es igual: el jugador
aprende "¡ahora!". La victoria (jefe_vencido) es en Re MAYOR: la tercera de picardia.
"""
from herramientas.estudio.obra import Efecto, Obra
from herramientas.estudio.obras import obra
from herramientas.estudio import instrumentos as I
from herramientas.estudio.obras.capas import tono, deslizar, cuerpo, aire, explosion, golpe, clic, abrir_acorde
from herramientas.estudio.obras.efectos_interfaz import registrar_familia


# ---------- Comunes ----------

@obra("alerta")
def alerta():
    # ¡ALERTA! (1.4 s): sirena de tritono Re / La bemol, 4 por segundo
    efecto = Efecto("alerta", 1.4, "f", sala=(1.4, 0.4), cola=0.3)
    sirena = " ".join(["D4+D5:175 Ab4+Ab5:175"] * 4)
    tono(efecto, I.SIRENA, sirena, legato=0.95, reverb=0.25)
    tono(efecto, I.BAJO_SUB, "D2:1400", volumen=-8, tremolo=(5.7, 5.7, 0.6))
    return efecto


@obra("franjas")
def franjas():
    # Las franjas de cine entran: un clunk metalico grave
    efecto = Efecto("franjas", 0.3, "f", sala=(1.0, 0.3))
    aire(efecto, 0.08, [(0, 2500), (0.08, 600)], volumen=-4)
    tono(efecto, I.METAL, "D2:250", volumen=-2)
    cuerpo(efecto, 90, 45, 0.15, volumen=-4)
    return efecto


@obra("presentacion_nombre")
def presentacion_nombre():
    # El nombre del jefe: golpe + acorde de La (el V de Re). La musica entra en Re (i)
    efecto = Efecto("presentacion_nombre", 0.6, "ff", sala=(2.0, 0.4))
    golpe(efecto, "K", 0.0, 1.0, volumen=-2)
    golpe(efecto, "X", 0.0, 0.7, volumen=-10, reverb=0.3)
    tono(efecto, I.PAD_OSCURO, "A3+C#4+E4:550", reverb=0.35)
    tono(efecto, I.BAJO_RUGIDO, "A1:550", volumen=-6)
    return efecto


@obra("presentacion_apodo")
def presentacion_apodo():
    efecto = Efecto("presentacion_apodo", 0.6, "ff", sala=(2.0, 0.4))
    golpe(efecto, "K", 0.0, 1.0, volumen=-2)
    tono(efecto, I.PAD_OSCURO, "A2+A3+E4:550", reverb=0.35)
    tono(efecto, I.BAJO_RUGIDO, "A1:550", volumen=-4)
    return efecto


@obra("vulnerable")
def vulnerable():
    # ¡Ahora se le puede pegar!: arpegio de quintas y cuartas que sube y brilla, sobre quintas abiertas
    # (Do Sol Re). Antes el acorde era La Re Mi en el grave: Re y Mi a un tono, en el registro
    # donde una segunda raspa. Do, Re y Sol son consonantes en todos los colores
    efecto = Efecto("vulnerable", 0.5, "f", sala=(1.4, 0.5))
    tono(efecto, I.CRISTAL, "G4:30 D5:30 G5:30 D6!:350", reverb=0.35, delay=0.15)
    abrir_acorde(efecto, I.EPIANO, ["C4", "G4", "D5"], largo=0.4, volumen=-6)
    return efecto


@obra("jefe_golpe")
def jefe_golpe():
    # Le pegaste en el nucleo: un impacto grande que cae
    efecto = Efecto("jefe_golpe", 0.5, "ff", sala=(1.4, 0.3))
    explosion(efecto, 0.35, brillo=5500, grave=(147, 37))
    tono(efecto, I.METAL, "D3:300", volumen=-8)
    return efecto


@obra("jefe_parte")
def jefe_parte():
    efecto = Efecto("jefe_parte", 0.3, "f", sala=(1.0, 0.3))
    explosion(efecto, 0.2, brillo=4500, grave=(110, 55))
    tono(efecto, I.METAL, "A2:200", volumen=-8)
    return efecto


@obra("parte_rota")
def parte_rota():
    # Una parte se rompe: crash y un arpegio de Re menor que se derrumba
    efecto = Efecto("parte_rota", 0.6, "ff", sala=(1.4, 0.3))
    explosion(efecto, 0.5, brillo=6000, grave=(120, 35))
    tono(efecto, I.PAD_OSCURO, "A4:50 F4:50 D4:50 A3:300", volumen=-6, reverb=0.3)
    return efecto


@obra("golpe_final")
def golpe_final():
    # El golpe que lo mata: el impacto mas grande (la musica se corta ahi)
    efecto = Efecto("golpe_final", 0.9, "ff", sala=(2.4, 0.3))
    explosion(efecto, 0.8, brillo=8000, grave=(147, 25))
    golpe(efecto, "X", 0.0, 1.0, volumen=-8, reverb=0.4)
    tono(efecto, I.METAL, "D2:700", volumen=-6, reverb=0.3)
    return efecto


def _agonia(numero, grave):
    # Las explosiones por el cuerpo mientras muere (Re menor que se derrumba)
    efecto = Efecto("agonia_%d" % numero, 0.25, "mf", sala=(1.0, 0.3))
    explosion(efecto, 0.22, brillo=4000, grave=(grave, grave / 2.5))
    return efecto


registrar_familia("agonia", [147, 110, 175], _agonia)


@obra("jefe_explota")
def jefe_explota():
    efecto = Efecto("jefe_explota", 2.0, "ff", sala=(2.6, 0.3))
    explosion(efecto, 1.8, brillo=9000, grave=(147, 25))
    explosion(efecto, 0.8, brillo=4000, inicio=0.4, volumen=-6)
    explosion(efecto, 0.6, brillo=3000, inicio=0.9, volumen=-10)
    return efecto


@obra("jefe_vencido")
def jefe_vencido():
    # ¡JEFE VENCIDO!: fanfarria en Re MAYOR (la pelea era en Re menor: tercera de picardia)
    efecto = Efecto("jefe_vencido", 1.6, "ff", sala=(2.0, 0.5))
    tono(efecto, I.LEAD_CALIDO, "A4:100 D5:100 F#5:100 A5:200 -:100 D6!:900", reverb=0.3, delay=0.15)
    tono(efecto, I.BAJO_ANALOGICO, "D3:200 A2:200 D3:900", volumen=-6)
    abrir_acorde(efecto, I.EPIANO, ["D4", "F#4", "A4", "D5"], inicio=0.6, largo=0.9, volumen=-4)
    tono(efecto, I.PAD_CALIDO, "-:600 D4+F#4+A4:900", volumen=-8, reverb=0.4)
    golpe(efecto, "K", 0.0, 0.8, volumen=-6)
    golpe(efecto, "K", 0.6, 1.0, volumen=-4)
    golpe(efecto, "X", 0.6, 0.9, volumen=-8, reverb=0.4)
    return efecto


# ---------- EL OJO ----------

@obra("ojo_carga")
def ojo_carga():
    # 700 ms: sube de Re a Sib (la sexta menor: no resuelve) y el temblor se acelera
    efecto = Efecto("ojo_carga", 0.7, "f", sala=(0.8, 0.4))
    deslizar(efecto, I.LASER, [(0, "D4"), (0.7, "Bb4")], tremolo=(5, 20, 0.5))
    aire(efecto, 0.7, [(0, 800), (0.7, 4000)], modo="banda", volumen=-12, forma=[(0, 0), (0.7, 1)])
    return efecto


@obra("ojo_abanico")
def ojo_abanico():
    # Un disparo en abanico: zap que cae dos octavas
    efecto = Efecto("ojo_abanico", 0.15, "mf", sala=(0.6, 0.4))
    deslizar(efecto, I.LASER, [(0, "A5"), (0.12, "A3")])
    return efecto


@obra("ojo_anillo")
def ojo_anillo():
    # El anillo: mas grave y con eco
    efecto = Efecto("ojo_anillo", 0.2, "mf", sala=(0.9, 0.4))
    deslizar(efecto, I.LASER, [(0, "D5"), (0.16, "D3")], delay=0.3)
    cuerpo(efecto, 80, 50, 0.1, volumen=-8)
    return efecto


@obra("ojo_cansado")
def ojo_cansado():
    # Se abren las placas: vapor y dos notas que se desinflan
    efecto = Efecto("ojo_cansado", 0.4, "mf", sala=(1.0, 0.4))
    aire(efecto, 0.3, [(0, 3000), (0.3, 1200)], modo="banda", resonancia=0.15, volumen=-6)
    deslizar(efecto, I.LEAD_HUECO, [(0, "F4"), (0.12, "F4"), (0.15, "D4"), (0.35, "A3")], volumen=-2)
    return efecto


@obra("ojo_voz")
def ojo_voz():
    # El grito del Ojo al recibir un golpe: un barrido electronico que cae
    efecto = Efecto("ojo_voz", 0.25, "f", sala=(1.0, 0.4))
    deslizar(efecto, I.LEAD_CALIDO, [(0, "A4"), (0.2, "D4")], tremolo=(14, 14, 0.4))
    return efecto


# ---------- ACORAZADO IMPERIAL ----------

@obra("compas_acento")
def compas_acento():
    # La marcha: el primer pulso del compas (las lamparitas del casco). Suena en cada pulso de
    # la pelea (23 por minuto): seco y corto, la tonica y la quinta (nunca molesta a la musica)
    efecto = Efecto("compas_acento", 0.1, "p", sala=(0.6, 0.3), cola=0.05)
    clic(efecto, volumen=-6, brillo=3000)
    tono(efecto, I.METAL, "D3:80")
    return efecto


@obra("compas")
def compas():
    efecto = Efecto("compas", 0.08, "pp", sala=(0.6, 0.3), cola=0.05)
    clic(efecto, volumen=-8, brillo=3000)
    tono(efecto, I.METAL, "A3:60")
    return efecto


@obra("carga_canon")
def carga_canon():
    # Un cañon carga: chispas que se juntan y una nota que sube un semitono (La a Sib)
    efecto = Efecto("carga_canon", 0.5, "p", sala=(0.6, 0.4))
    aire(efecto, 0.5, [(0, 3000)], modo="banda", chasquidos=50, volumen=-4, forma=[(0, 0.3), (0.5, 1)])
    deslizar(efecto, I.LASER, [(0, "A3"), (0.5, "Bb3")], volumen=-6)
    return efecto


@obra("obus")
def obus():
    # Cañonazo grave
    efecto = Efecto("obus", 0.35, "f", sala=(1.0, 0.3))
    explosion(efecto, 0.3, brillo=3500, grave=(73, 37))
    return efecto


@obra("misil")
def misil():
    # Lanzamiento: el silbido que se va y dos bips (te esta siguiendo)
    efecto = Efecto("misil", 0.5, "mf", sala=(0.8, 0.4))
    aire(efecto, 0.4, [(0, 1200), (0.4, 2800)], modo="banda", resonancia=0.3,
         forma=[(0, 0), (0.03, 1), (0.4, 0)])
    tono(efecto, I.METAL, "-:150 A4:40 -:160 A4:40", volumen=-8)
    return efecto


@obra("laser_carga")
def laser_carga():
    # Un pulso (520 ms): sube de La3 a La5 y tiembla cada vez mas rapido
    efecto = Efecto("laser_carga", 0.52, "f", sala=(0.8, 0.4))
    deslizar(efecto, I.LASER, [(0, "A3"), (0.52, "A5")], tremolo=(6, 24, 0.5))
    return efecto


@obra("laser")
def laser():
    # El laser prendido (loop): zumbido en octavas de Re que vibra. Es una Obra que da la
    # vuelta (1 s exacto, como un tema): suena sin cortes todo lo que dure prendido
    efecto = Obra("laser", segundos=1.0, vuelta=True, sala=(0.3, 0.3), objetivo=-14.0, pegamento=False, humano=0.0)
    tono(efecto, I.SIRENA, "D3+D4:1000", tremolo=(16, 16, 0.25), reverb=0.0, legato=1.0)
    aire(efecto, 1.0, [(0, 3000)], modo="banda", volumen=-14, forma=[(0, 1), (1.0, 1)])
    return efecto


@obra("mina_lanza")
def mina_lanza():
    efecto = Efecto("mina_lanza", 0.15, "mf", sala=(0.6, 0.3))
    tono(efecto, I.BAJO_SUB, "D3:80")
    clic(efecto, volumen=-6, brillo=2000)
    return efecto


@obra("recalentado")
def recalentado():
    # Los cañones echan vapor y el metal hace tic al enfriarse
    efecto = Efecto("recalentado", 1.0, "p", sala=(1.0, 0.4))
    aire(efecto, 1.0, [(0, 2200), (1.0, 1400)], modo="banda", resonancia=0.15, forma=[(0, 0), (0.05, 1), (1.0, 0)],
         eq=[("corte_agudos", 5000)])
    for i, inicio in enumerate((0.15, 0.4, 0.75)):
        tono(efecto, I.METAL, "A5:20", inicio=inicio, volumen=-12 - 2 * i, transponer=-12)
    return efecto


@obra("coraza")
def coraza():
    # ¡SIN CORAZA!: crash enorme y un arpegio de Re menor que se viene abajo
    efecto = Efecto("coraza", 1.0, "ff", sala=(2.0, 0.3))
    explosion(efecto, 0.9, brillo=7000, grave=(110, 30))
    tono(efecto, I.METAL, "D3:600", volumen=-4, reverb=0.3)
    tono(efecto, I.PAD_OSCURO, "D5:60 A4:60 F4:60 D4:60 A3:60 D3:400", volumen=-6, reverb=0.3)
    return efecto


@obra("cortina_aviso")
def cortina_aviso():
    # Un retumbo de techo (un pulso): algo va a caer
    efecto = Efecto("cortina_aviso", 0.5, "mf", sala=(1.0, 0.3))
    aire(efecto, 0.5, [(0, 500)], forma=[(0, 0), (0.1, 1), (0.5, 0)], tremolo=(10, 10, 0.5))
    tono(efecto, I.BAJO_SUB, "D2:450", volumen=-4, tremolo=(10, 10, 0.5))
    return efecto


@obra("escombros")
def escombros():
    efecto = Efecto("escombros", 0.4, "f", sala=(1.0, 0.3))
    for i, inicio in enumerate((0.0, 0.07, 0.13, 0.2, 0.28)):
        aire(efecto, 0.1, [(0, 1800 - 200 * i), (0.1, 300)], inicio=inicio, volumen=-2 - i)
    cuerpo(efecto, 90, 45, 0.2, volumen=-6)
    return efecto


@obra("fijar")
def fijar():
    # Deja de seguirte: una traba y Sib sobre el Re grave (la sexta menor, que quiere caer)
    # que tiembla
    efecto = Efecto("fijar", 1.0, "f", sala=(0.8, 0.4))
    clic(efecto, volumen=-2, brillo=2500)
    tono(efecto, I.SIRENA, "Bb3:960", tremolo=(4, 18, 0.5), legato=1.0)
    tono(efecto, I.BAJO_SUB, "D2:960", volumen=-8)
    return efecto


@obra("caida")
def caida():
    # Cae: de la sexta menor (Sib) a la tonica (Re)
    efecto = Efecto("caida", 0.5, "f", sala=(0.6, 0.4))
    deslizar(efecto, I.LASER, [(0, "Bb5"), (0.5, "D4")])
    aire(efecto, 0.5, [(0, 1000), (0.5, 4000)], modo="banda", volumen=-10, forma=[(0, 0), (0.5, 1)])
    return efecto


@obra("estrellarse")
def estrellarse():
    efecto = Efecto("estrellarse", 0.8, "ff", sala=(1.6, 0.3))
    explosion(efecto, 0.7, brillo=5000, grave=(73, 25))
    golpe(efecto, "K", 0.0, 1.0, volumen=-2)
    tono(efecto, I.METAL, "D2:500", volumen=-6)
    return efecto


@obra("onda_suelo")
def onda_suelo():
    # Las ondas que corren a ras del piso
    efecto = Efecto("onda_suelo", 0.8, "mf", sala=(0.8, 0.3))
    aire(efecto, 0.8, [(0, 900), (0.8, 300)], forma=[(0, 0), (0.05, 1), (0.8, 0)], tremolo=(6, 6, 0.6))
    return efecto


# ---------- DEVORADORA DE ESTRELLAS ----------

@obra("siseo")
def siseo():
    efecto = Efecto("siseo", 1.0, "mf", sala=(1.0, 0.4))
    aire(efecto, 1.0, [(0, 2400), (1.0, 3000)], modo="banda", resonancia=0.2, forma=[(0, 0), (0.3, 1), (1.0, 0)],
         eq=[("corte_agudos", 5000)])
    return efecto


@obra("cascabel")
def cascabel():
    # El cascabel: rafagas cortas de ruido, 8 por pulso, durante 2 pulsos (~900 ms)
    efecto = Efecto("cascabel", 0.9, "f", sala=(0.6, 0.4))
    for i in range(16):
        aire(efecto, 0.03, [(0, 2400)], inicio=i * 0.057, modo="banda", resonancia=0.3, eq=[("corte_agudos", 5000)],
             volumen=-2 if i % 4 == 0 else -6)
    return efecto


@obra("mordida")
def mordida():
    efecto = Efecto("mordida", 0.35, "f", sala=(0.8, 0.4))
    aire(efecto, 0.2, [(0, 3800)], modo="banda", resonancia=0.2, forma=[(0, 0), (0.15, 1), (0.2, 0)])
    aire(efecto, 0.03, [(0, 2500)], inicio=0.2, volumen=0)
    deslizar(efecto, I.LASER, [(0, "D4"), (0.15, "Bb3")], inicio=0.2, volumen=-4)
    return efecto


@obra("serpiente_choca")
def serpiente_choca():
    efecto = Efecto("serpiente_choca", 0.5, "f", sala=(1.0, 0.3))
    explosion(efecto, 0.35, brillo=2500, grave=(110, 40))
    return efecto


@obra("mareo")
def mareo():
    # Mareada: notas que se tambalean y se desafinan
    efecto = Efecto("mareo", 0.6, "mf", sala=(1.0, 0.4))
    deslizar(efecto, I.LEAD_HUECO, [(0, "D5"), (0.15, "E5"), (0.3, "D5"), (0.6, "B4")], tremolo=(7, 4, 0.4))
    return efecto


@obra("enroscar")
def enroscar():
    # Se enrosca a tu alrededor: el siseo sube de Re a Sib mientras el circulo se cierra
    efecto = Efecto("enroscar", 2.7, "f", sala=(1.0, 0.4))
    aire(efecto, 2.7, [(0, 2200), (2.7, 4500)], modo="banda", resonancia=0.2, forma=[(0, 0.3), (2.5, 1), (2.7, 0)])
    deslizar(efecto, I.SIRENA, [(0, "D4"), (2.7, "Bb4")], volumen=-6, tremolo=(3, 12, 0.4))
    return efecto


@obra("escupir")
def escupir():
    efecto = Efecto("escupir", 0.15, "mf", sala=(0.6, 0.4))
    aire(efecto, 0.04, [(0, 1800)], volumen=0)
    deslizar(efecto, I.LASER, [(0, "G4"), (0.1, "C5")], volumen=-4)
    return efecto


@obra("corte")
def corte():
    # Le cortaste el cascabel: el tajo y su grito
    efecto = Efecto("corte", 0.5, "ff", sala=(1.2, 0.4))
    aire(efecto, 0.1, [(0, 4000), (0.1, 1500)], modo="banda", resonancia=0.2)
    deslizar(efecto, I.LEAD_CALIDO, [(0, "D5"), (0.35, "A4")], inicio=0.05, tremolo=(12, 12, 0.3))
    cuerpo(efecto, 150, 60, 0.15, volumen=-6)
    return efecto


# ---------- MADRE DEL ENJAMBRE ----------

@obra("compuerta_abre")
def compuerta_abre():
    # Rechina la compuerta y crece el zumbido (2 pulsos)
    efecto = Efecto("compuerta_abre", 1.0, "mf", sala=(0.8, 0.4))
    deslizar(efecto, I.LEAD_HUECO, [(0, "D4"), (0.25, "A4")], volumen=-6, tremolo=(20, 9, 0.5))
    tono(efecto, I.ZUMBIDO, "A2:900", volumen=-2, tremolo=(28, 28, 0.4))
    return efecto


@obra("llamado")
def llamado():
    # "¡A CASA, HIJAS!": un llamado que va y viene
    efecto = Efecto("llamado", 0.9, "f", sala=(1.4, 0.4))
    deslizar(efecto, I.SIRENA, [(0, "A3"), (0.2, "D4"), (0.45, "A3"), (0.65, "D4"), (0.9, "D4")], reverb=0.3)
    return efecto


@obra("furia")
def furia():
    efecto = Efecto("furia", 1.5, "f", sala=(1.0, 0.4))
    # (sube de Mi a Sib: el tritono de Re menor)
    deslizar(efecto, I.ZUMBIDO, [(0, "E3"), (1.5, "Bb3")], tremolo=(25, 40, 0.5))
    tono(efecto, I.PAD_OSCURO, "E3+Bb3:1400", volumen=-6, reverb=0.3)
    return efecto


@obra("temblar")
def temblar():
    # 3 pulsos: un traqueteo que crece y, en el segundo pulso, la traba (la direccion queda fija)
    efecto = Efecto("temblar", 1.5, "f", sala=(0.8, 0.4))
    aire(efecto, 1.5, [(0, 900), (1.5, 2500)], forma=[(0, 0.2), (1.5, 1)], tremolo=(8, 20, 0.7))
    clic(efecto, inicio=1.0, volumen=0, brillo=2500)
    tono(efecto, I.METAL, "-:1000 Bb3:400", volumen=-4)
    return efecto


@obra("embestida_colmena")
def embestida_colmena():
    efecto = Efecto("embestida_colmena", 0.6, "f", sala=(0.8, 0.4))
    aire(efecto, 0.6, [(0, 2500), (0.6, 500)], forma=[(0, 0), (0.04, 1), (0.6, 0)])
    tono(efecto, I.ZUMBIDO, "D3:500", volumen=-4, tremolo=(35, 35, 0.4))
    return efecto


@obra("colmena_choca")
def colmena_choca():
    efecto = Efecto("colmena_choca", 0.5, "f", sala=(1.0, 0.3))
    explosion(efecto, 0.3, brillo=2000, grave=(73, 35))
    aire(efecto, 0.15, [(0, 700)], inicio=0.05, volumen=-6)
    return efecto


# ---------- EL FIN DE LA LUZ ----------

@obra("nacer")
def nacer():
    # Nace de un punto: una implosion al reves que sube
    efecto = Efecto("nacer", 2.0, "f", sala=(2.0, 0.4))
    aire(efecto, 2.0, [(0, 100), (2.0, 4000)], forma=[(0, 0), (1.9, 1), (2.0, 0)], reverb=0.3)
    deslizar(efecto, I.PAD_OSCURO, [(0, "D1"), (2.0, "D4")], volumen=-4, reverb=0.3)
    return efecto


@obra("anillo_tic")
def anillo_tic():
    # El anillo avanza un lugar: piedra contra piedra, en el pulso
    efecto = Efecto("anillo_tic", 0.12, "p", sala=(0.8, 0.3))
    aire(efecto, 0.03, [(0, 1500)], volumen=-2)
    tono(efecto, I.BAJO_SUB, "D2:100")
    return efecto


@obra("brazos")
def brazos():
    efecto = Efecto("brazos", 0.1, "p", sala=(0.8, 0.4))
    deslizar(efecto, I.LASER, [(0, "D5"), (0.08, "A4")])
    return efecto


@obra("inhalar")
def inhalar():
    # 3 pulsos (1.5 s): la succion crece y el grave sube de Re a Sib (la sexta menor)
    efecto = Efecto("inhalar", 1.5, "f", sala=(1.4, 0.4))
    aire(efecto, 1.5, [(0, 300), (1.5, 6000)], forma=[(0, 0), (1.5, 1)], reverb=0.3)
    deslizar(efecto, I.PAD_OSCURO, [(0, "D2"), (1.5, "Bb2")], volumen=-4)
    return efecto


@obra("exhalar")
def exhalar():
    efecto = Efecto("exhalar", 0.8, "ff", sala=(1.8, 0.4))
    explosion(efecto, 0.5, brillo=6000, grave=(147, 50))
    aire(efecto, 0.8, [(0, 4000), (0.8, 500)], forma=[(0, 0), (0.05, 1), (0.8, 0)], volumen=-4, reverb=0.4)
    tono(efecto, I.PAD_OSCURO, "D3+A3:300", volumen=-6)
    return efecto


@obra("colapso")
def colapso():
    efecto = Efecto("colapso", 1.0, "mf", sala=(1.4, 0.4))
    deslizar(efecto, I.PAD_OSCURO, [(0, "D5"), (1.0, "D2")], reverb=0.3)
    aire(efecto, 1.0, [(0, 6000), (1.0, 200)], forma=[(0, 1), (1.0, 0)], volumen=-6)
    return efecto


@obra("estallido")
def estallido():
    efecto = Efecto("estallido", 0.4, "f", sala=(1.2, 0.4))
    explosion(efecto, 0.3, brillo=5000, grave=(73, 147))
    return efecto


@obra("moneda_tragada")
def moneda_tragada():
    # Se comio la moneda: la moneda resbalando hacia abajo (un detalle con humor)
    efecto = Efecto("moneda_tragada", 0.4, "p", sala=(0.8, 0.4))
    deslizar(efecto, I.CRISTAL, [(0, "C6"), (0.4, "C4")])
    return efecto


# ---------- Detalles de los jefes (P3) ----------

@obra("ojo_flota")
def ojo_flota():
    # El Ojo cierra las placas y vuelve a flotar: un clac y un zumbido grave que crece y se va
    efecto = Efecto("ojo_flota", 1.5, "p", sala=(1.0, 0.3))
    clic(efecto, volumen=0, brillo=2000)
    tono(efecto, I.PAD_OSCURO, "D2+A2:1400", volumen=-2, tremolo=(1, 1, 0.5))
    return efecto


@obra("motor_pesado")
def motor_pesado():
    # La Fortaleza se reubica: orugas (un ruido grave que pulsa)
    efecto = Efecto("motor_pesado", 0.9, "p", sala=(0.8, 0.3))
    aire(efecto, 0.9, [(0, 400)], tremolo=(8, 8, 0.7), forma=[(0, 0), (0.1, 1), (0.8, 1), (0.9, 0)])
    tono(efecto, I.BAJO_SUB, "D2:850", volumen=-6, tremolo=(8, 8, 0.5))
    return efecto


@obra("servo")
def servo():
    # Se pone encima tuyo: un servo que va y viene
    efecto = Efecto("servo", 0.8, "pp", sala=(0.6, 0.3))
    deslizar(efecto, I.LEAD_HUECO, [(0, "D4"), (0.2, "E4"), (0.4, "D4"), (0.6, "E4"), (0.8, "D4")], volumen=-2)
    return efecto


@obra("hidraulica")
def hidraulica():
    # Vuelve a subir: hidraulica (un siseo largo y una nota que sube)
    efecto = Efecto("hidraulica", 1.4, "pp", sala=(0.8, 0.3))
    aire(efecto, 1.4, [(0, 1800)], modo="banda", forma=[(0, 0), (0.1, 1), (1.3, 0.6), (1.4, 0)])
    deslizar(efecto, I.LEAD_HUECO, [(0, "D3"), (1.4, "A3")], volumen=-8)
    return efecto


@obra("panal")
def panal():
    # La Colmena flota: el zumbido de su panal, que se acerca y se aleja
    efecto = Efecto("panal", 2.0, "pp", sala=(1.0, 0.4))
    tono(efecto, I.ZUMBIDO, "A2:1900", tremolo=(25, 25, 0.4))
    efecto.pistas[-1].volumen = -2
    return efecto


@obra("inestable")
def inestable():
    # La Singularidad expuesta: un zumbido de segunda menor (La + Sib) que tiembla
    efecto = Efecto("inestable", 2.0, "p", sala=(1.4, 0.4))
    tono(efecto, I.PAD_OSCURO, "A3+Bb3:1900", tremolo=(6, 10, 0.5), reverb=0.4)
    return efecto
