"""
Compositor de la musica del juego: chiptune hecho con codigo.

Uso (desde la carpeta del juego):
    python herramientas/componer_musica.py                  todo lo de COMPOSICIONES
    python herramientas/componer_musica.py musica_jefe      solo ese (o varios nombres)

Escribe en efectos/ lo que esta en COMPOSICIONES (abajo de todo): los temas de menu,
jefe y gasolinera. Solo usa la biblioteca de Python. Los temas se pasan a OGG con
ffmpeg si esta (pesan 10 veces menos); si no, quedan en WAV y avisa (hay que cambiar
la extension en sonido.py). Los efectos (vuelta=False) quedan siempre en WAV.

Como funciona (como una consola de 8 bits):
- Instrumento: una onda (pulso, triangulo) con su envolvente (ataque, caida,
  sostenido y liberacion). El pulso "finito" (ciclo 0.125) suena nasal; el de 0.5, redondo.
- La bateria es ruido y un tono que baja (bombo).
- Cada voz se escribe en una GRILLA de semicorcheas, 16 por compas, como un "tracker":
      "A4 . . . C5 . E5 . - - ..."   nota | "." sigue sonando | "-" silencio
  La bateria usa letras: K bombo, S caja, h platillo cerrado, H abierto.
- El bajo, los arpegios y los acordes salen solos de la lista de ACORDES (uno por compas).
- El tema dura un numero exacto de compases y lo que sobra al final (los ecos, las
  notas que se apagan) se suma al principio: asi da la vuelta sin un "clic".
  Un EFECTO (vuelta=False) no da la vuelta: tiene una cola de silencio para que las
  notas se apaguen y al final se recorta lo que quedo callado.
"""
import array
import math
import os
import random
import re
import shutil
import subprocess
import sys
import wave

FRECUENCIA = 44100          # muestras por segundo
PASOS_POR_COMPAS = 16       # semicorcheas
COLA_EFECTO = 2.0           # segundos de mas al final de un efecto (para que se apague)

NOTAS = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
# Intervalos (en semitonos desde la fundamental) de cada tipo de acorde
TIPOS_ACORDE = {"": [0, 4, 7], "m": [0, 3, 7], "7": [0, 4, 7, 10], "m7": [0, 3, 7, 10], "maj7": [0, 4, 7, 11]}


def midi(nombre):
    # "C#5" -> 73. El La de 440 Hz (A4) es el 69
    letra, alteracion, octava = re.fullmatch(r"([A-G])([#b]?)(-?\d)", nombre).groups()
    semitono = NOTAS[letra] + {"#": 1, "b": -1, "": 0}[alteracion]
    return 12 * (int(octava) + 1) + semitono


def hertz(nota_midi):
    return 440 * 2 ** ((nota_midi - 69) / 12)


def leer_acorde(nombre):
    # "Bbm7" -> (10, [0, 3, 7, 10]): la fundamental (0 = Do) y sus intervalos
    letra, alteracion, tipo = re.fullmatch(r"([A-G])([#b]?)(.*)", nombre).groups()
    fundamental = (NOTAS[letra] + {"#": 1, "b": -1, "": 0}[alteracion]) % 12
    return fundamental, TIPOS_ACORDE[tipo]


# ---------- Instrumentos ----------

class Instrumento:
    def __init__(self, onda, ciclo=0.5, ataque=0.005, caida=0.15, sostenido=0.5, liberacion=0.08,
                 vibrato=0.0, suavizado=0.5):
        self.onda = onda                # "pulso" o "triangulo"
        self.ciclo = ciclo              # del pulso: que parte de la onda esta arriba
        self.ataque = ataque            # segundos hasta el maximo
        self.caida = caida              # segundos que tarda en bajar al sostenido
        self.sostenido = sostenido      # volumen mientras se mantiene la nota (0 a 1)
        self.liberacion = liberacion    # segundos que tarda en apagarse al soltarla
        self.vibrato = vibrato          # cuanto se mueve la afinacion (0.004 = poco)
        self.suavizado = suavizado      # filtro: 1 = sin filtro, menos = mas apagado

    def envolvente(self, t):
        if t < self.ataque:
            return t / self.ataque
        return self.sostenido + (1 - self.sostenido) * math.exp(-(t - self.ataque) / self.caida)

    def tocar(self, pista, inicio, duracion, frecuencia, volumen):
        # Suma la nota a la pista (una lista que "da la vuelta": ver el comentario de arriba)
        largo = len(pista)
        muestras_nota = int(duracion * FRECUENCIA)
        muestras_liberacion = int(self.liberacion * FRECUENCIA)
        fase = 0.0
        filtrada = 0.0
        al_soltar = 0.0
        for i in range(muestras_nota + muestras_liberacion):
            t = i / FRECUENCIA
            if i < muestras_nota:
                al_soltar = self.envolvente(t)
                env = al_soltar
            else:
                env = al_soltar * (1 - (i - muestras_nota) / muestras_liberacion)
            f = frecuencia
            if self.vibrato and t > 0.12:
                f *= 1 + self.vibrato * math.sin(2 * math.pi * 5.5 * t)
            fase = (fase + f / FRECUENCIA) % 1
            if self.onda == "pulso":
                valor = 1.0 if fase < self.ciclo else -1.0
            else:
                # triangulo en 16 escalones, como el de las consolas viejas
                valor = round((4 * abs(fase - 0.5) - 1) * 8) / 8
            filtrada += self.suavizado * (valor - filtrada)
            pista[(inicio + i) % largo] += filtrada * env * volumen


def bombo(pista, inicio, volumen, azar):
    # Un tono que cae de golpe de 200 a 45 Hz
    fase = 0.0
    for i in range(int(0.25 * FRECUENCIA)):
        t = i / FRECUENCIA
        fase += (45 + 155 * math.exp(-t / 0.025)) / FRECUENCIA
        pista[(inicio + i) % len(pista)] += math.sin(2 * math.pi * fase) * math.exp(-t / 0.09) * volumen


def caja(pista, inicio, volumen, azar):
    # Ruido apagado + un "toc" grave
    filtrada = 0.0
    for i in range(int(0.2 * FRECUENCIA)):
        t = i / FRECUENCIA
        filtrada += 0.45 * (azar.uniform(-1, 1) - filtrada)
        tono = math.sin(2 * math.pi * 185 * t) * math.exp(-t / 0.03)
        pista[(inicio + i) % len(pista)] += (filtrada * 1.4 * math.exp(-t / 0.06) + tono * 0.6) * volumen


def platillo(pista, inicio, volumen, azar, largo=0.018):
    # Ruido agudo: la resta de dos muestras seguidas deja solo lo agudo
    anterior = 0.0
    for i in range(int(largo * 6 * FRECUENCIA)):
        t = i / FRECUENCIA
        ruido = azar.uniform(-1, 1)
        pista[(inicio + i) % len(pista)] += (ruido - anterior) * 0.5 * math.exp(-t / largo) * volumen
        anterior = ruido


def platillo_abierto(pista, inicio, volumen, azar):
    platillo(pista, inicio, volumen, azar, largo=0.08)


BATERIA = {"K": bombo, "S": caja, "h": platillo, "H": platillo_abierto}


# ---------- El tema ----------

class Tema:
    def __init__(self, nombre, bpm, acordes, swing=0.0, vuelta=True):
        self.nombre = nombre
        self.vuelta = vuelta            # True: musica que se repite; False: un efecto que suena una vez
        self.bpm = bpm
        self.acordes = acordes          # uno por compas
        self.swing = swing              # cuanto se atrasa la corchea de "contratiempo" (0 a 0.5)
        self.paso = 60 / bpm / 4        # segundos por semicorchea
        self.pasos = len(acordes) * PASOS_POR_COMPAS
        self.largo = round(self.pasos * self.paso * FRECUENCIA)
        if not vuelta:
            self.largo += round(COLA_EFECTO * FRECUENCIA)      # lugar para que se apague (sin dar la vuelta)
        self.voces = []                 # (pista, volumen)
        self.azar = random.Random(nombre)   # el mismo ruido cada vez que se compone

    def muestra(self, paso):
        # En que muestra empieza un paso (con swing, la 2da corchea de cada tiempo llega tarde)
        segundos = paso * self.paso
        if paso % 4 == 2:
            segundos += self.swing * 2 * self.paso
        return round(segundos * FRECUENCIA)

    def nueva_voz(self, volumen):
        pista = [0.0] * self.largo
        self.voces.append((pista, volumen))
        return pista

    def tocar_notas(self, notas, instrumento, volumen, eco=0.0, legato=0.9):
        # notas: [(paso, pasos que dura, nota midi)]
        pista = self.nueva_voz(volumen)
        for paso, pasos, nota in notas:
            inicio = self.muestra(paso)
            duracion = (self.muestra(paso + pasos) - inicio) / FRECUENCIA * legato
            instrumento.tocar(pista, inicio, duracion, hertz(nota), 1.0)
        if eco:
            agregar_eco(pista, round(3 * self.paso * FRECUENCIA), eco, self.vuelta)

    def melodia(self, grilla, instrumento, volumen, eco=0.0):
        self.tocar_notas(leer_grilla(grilla, self.pasos), instrumento, volumen, eco)

    def bateria(self, grilla, volumen):
        pista = self.nueva_voz(volumen)
        for paso, golpe in enumerate(pasos_de(grilla, self.pasos)):
            if golpe in BATERIA:
                BATERIA[golpe](pista, self.muestra(paso), 1.0, self.azar)

    def bajo(self, patron, instrumento, volumen):
        # patron de 16 pasos: R fundamental, 3/5/6/7 esos grados, 8 la octava, "." sigue, "-" nada
        grados = {"R": 0, "8": 12}
        notas = []
        for compas, nombre in enumerate(self.acordes):
            fundamental, intervalos = leer_acorde(nombre)
            grados.update({"3": intervalos[1], "5": 7, "6": 9, "7": intervalos[3] if len(intervalos) > 3 else 10})
            base = 36 + fundamental if fundamental >= 4 else 48 + fundamental   # entre Mi2 y Re#3 (MIDI 40 a 51)
            for paso, pasos, grado in duraciones(patron.split()):
                notas.append((compas * PASOS_POR_COMPAS + paso, pasos, base + grados[grado]))
        self.tocar_notas(notas, instrumento, volumen)

    def arpegio(self, orden, instrumento, volumen, eco=0.0):
        # orden: que nota del acorde va en cada semicorchea (0 la fundamental, sigue hacia arriba)
        notas = []
        for compas, nombre in enumerate(self.acordes):
            fundamental, intervalos = leer_acorde(nombre)
            for paso in range(PASOS_POR_COMPAS):
                i = orden[paso % len(orden)]
                nota = 60 + fundamental + intervalos[i % len(intervalos)] + 12 * (i // len(intervalos))
                notas.append((compas * PASOS_POR_COMPAS + paso, 1, nota))
        self.tocar_notas(notas, instrumento, volumen, eco, legato=0.7)

    def acompanar(self, patron, instrumento, volumen):
        # El acorde entero en los pasos marcados con X (". " lo sostiene)
        notas = []
        for compas, nombre in enumerate(self.acordes):
            fundamental, intervalos = leer_acorde(nombre)
            for paso, pasos, _ in duraciones(patron.split()):
                for intervalo in intervalos:
                    nota = 48 + fundamental + intervalo
                    while nota < 53:
                        nota += 12
                    while nota >= 65:
                        nota -= 12
                    notas.append((compas * PASOS_POR_COMPAS + paso, pasos, nota))
        self.tocar_notas(notas, instrumento, volumen / 3)

    def mezclar(self):
        # Suma las voces, ajusta el volumen y lo "redondea" suave para que no se rompa
        mezcla = [0.0] * self.largo
        for pista, volumen in self.voces:
            for i, valor in enumerate(pista):
                mezcla[i] += valor * volumen
        if not self.vuelta:
            mezcla = recortar_silencio(mezcla)
        maximo = max(abs(valor) for valor in mezcla) or 1
        return [math.tanh(1.3 * valor / maximo) / math.tanh(1.3) * 0.6 for valor in mezcla]


def pasos_de(grilla, pasos_esperados):
    # La grilla sin las rayas de compas "|"; comprueba que no falte ni sobre nada
    pasos = [simbolo for simbolo in grilla.split() if simbolo != "|"]
    assert len(pasos) == pasos_esperados, "la grilla tiene %d pasos y el tema %d" % (len(pasos), pasos_esperados)
    return pasos


def duraciones(simbolos):
    # ["A4", ".", ".", "-", "C5"] -> [(0, 3, "A4"), (4, 1, "C5")]
    resultado = []
    for paso, simbolo in enumerate(simbolos):
        if simbolo == ".":
            if resultado and resultado[-1][0] + resultado[-1][1] == paso:
                inicio, pasos, nota = resultado[-1]
                resultado[-1] = (inicio, pasos + 1, nota)
        elif simbolo != "-":
            resultado.append((paso, 1, simbolo))
    return resultado


def leer_grilla(grilla, pasos_esperados):
    return [(paso, pasos, midi(nota)) for paso, pasos, nota in duraciones(pasos_de(grilla, pasos_esperados))]


def agregar_eco(pista, retraso, fuerza, vuelta=True):
    # Dos repeticiones mas suaves (dando la vuelta, como todo; un efecto no la da)
    original = pista[:]
    for i in range(len(pista)):
        for veces, volumen in ((1, fuerza), (2, fuerza * fuerza)):
            antes = i - veces * retraso
            if vuelta or antes >= 0:
                pista[i] += original[antes] * volumen


def recortar_silencio(muestras, umbral=0.0005):
    # Saca el silencio del final de un efecto (deja 10 ms para que no corte en seco)
    fin = len(muestras)
    while fin > 0 and abs(muestras[fin - 1]) < umbral:
        fin -= 1
    return muestras[:fin + round(0.01 * FRECUENCIA)]


# ---------- La musica ----------

PULSO_FINO = Instrumento("pulso", ciclo=0.125, caida=0.08, sostenido=0.3, liberacion=0.05, suavizado=0.35)
PULSO_MEDIO = Instrumento("pulso", ciclo=0.25, caida=0.25, sostenido=0.6, liberacion=0.12, vibrato=0.004,
                          suavizado=0.4)
PULSO_REDONDO = Instrumento("pulso", ciclo=0.5, caida=0.4, sostenido=0.5, liberacion=0.15, vibrato=0.003,
                            suavizado=0.25)
CAMPANA = Instrumento("pulso", ciclo=0.25, caida=0.3, sostenido=0.15, liberacion=0.3, vibrato=0.005,
                      suavizado=0.2)
TECLADO = Instrumento("pulso", ciclo=0.5, ataque=0.01, caida=0.1, sostenido=0.25, liberacion=0.06,
                      suavizado=0.15)
BAJO = Instrumento("triangulo", caida=0.2, sostenido=0.7, liberacion=0.03, suavizado=1.0)


def tema_menu():
    # El hangar: tranquilo, en La menor, para leer el menu sin apuro
    tema = Tema("menu", 112, ["Am", "F", "C", "G", "Am", "F", "C", "G",
                              "F", "G", "Em", "Am", "F", "G", "E", "E"])
    tema.melodia("""
        A4 . . . C5 . E5 . . . . . D5 . C5 . | C5 . . . . . A4 . . . F4 . A4 . C5 . |
        E5 . . . G5 . . . E5 . D5 . C5 . . . | D5 . . . . . . . B4 . . . G4 . . . |
        A4 . . . C5 . E5 . . . . . A5 . G5 . | F5 . . . E5 . . . C5 . . . A4 . C5 . |
        E5 . . . D5 . C5 . . . G4 . C5 . E5 . | D5 . . . . . . . . . . . - - - - |
        A5 . . . . . G5 . F5 . . . E5 . F5 . | G5 . . . . . . . D5 . . . B4 . D5 . |
        E5 . . . G5 . B5 . . . A5 . G5 . E5 . | A5 . . . . . . . E5 . . . C5 . E5 . |
        F5 . . . E5 . F5 . A5 . . . G5 . F5 . | G5 . . . F5 . G5 . B5 . . . A5 . G5 . |
        G#5 . . . . . . . E5 . . . B4 . . . | G#4 . . . B4 . . . E5 . . . - - - -
    """, PULSO_MEDIO, 0.30, eco=0.3)
    tema.arpegio([0, 1, 2, 3, 4, 3, 2, 1], PULSO_FINO, 0.11, eco=0.25)
    tema.bajo("R . . . R . 8 . R . . . 5 . 8 .", BAJO, 0.45)
    tema.bateria(" | ".join(["K - h - S - h - K - h K S - h h"] * 15 + ["K - h - S - h - K - S - S S S S"]),
                 0.35)
    return tema


def tema_jefe():
    # La pelea: rapido, en Re menor, con el bajo empujando y una seccion de "riff" al final
    tema = Tema("jefe", 150, ["Dm", "Dm", "Bb", "C", "Dm", "Dm", "Bb", "A",
                              "Gm", "Dm", "Bb", "A", "Gm", "Dm", "E", "A",
                              "Bb", "C", "Dm", "Dm", "Bb", "C", "A", "A"])
    tema.melodia("""
        D5 . . . . . A4 . D5 . F5 . . . E5 . | D5 . . . . . . . - - A4 . C5 . D5 . |
        F5 . . . . . D5 . Bb4 . . . D5 . F5 . | E5 . . . . . C5 . G4 . . . C5 . E5 . |
        D5 . . . . . A4 . D5 . F5 . . . A5 . | G5 . F5 . E5 . D5 . . . . . C5 . D5 . |
        F5 . . . D5 . . . Bb5 . . . A5 . G5 . | A5 . . . . . . . C#5 . . . E5 . . . |
        G5 . . . . . Bb5 . . . A5 . G5 . F5 . | A5 . . . . . . . F5 . . . D5 . . . |
        D6 . . . C6 . Bb5 . . . A5 . Bb5 . C6 . | A5 . . . . . . . E5 . . . C#5 . . . |
        G5 . . . Bb5 . D6 . . . C6 . Bb5 . A5 . | A5 . . . F5 . A5 . D6 . . . . . . . |
        G#5 . . . B5 . . . E6 . . . D6 . B5 . | C#6 . . . . . . . A5 . . . E5 . C#5 . |
        - - - - - - - - - - - - - - - - | - - - - - - - - - - - - - - - - |
        - - - - - - - - - - - - - - - - | D6 . . . . . . . A5 . . . F5 . . . |
        - - - - - - - - - - - - - - - - | - - - - - - - - - - - - - - - - |
        - - - - - - - - - - - - - - - - | C#5 . . . E5 . . . G5 . . . A5 . . .
    """, PULSO_MEDIO, 0.30, eco=0.2)
    # El riff de 16 notas seguidas (compases 17 a 19, 21 a 23), con un pulso mas fino
    riff = ["- " * 16] * 16 + [
        "D5 F5 Bb5 F5 D5 F5 Bb5 F5 D5 F5 Bb5 F5 C6 Bb5 A5 F5",
        "E5 G5 C6 G5 E5 G5 C6 G5 E5 G5 C6 G5 D6 C6 Bb5 G5",
        "F5 A5 D6 A5 F5 A5 D6 A5 F5 A5 D6 A5 E6 D6 C6 A5",
        "- " * 16,
        "D5 F5 Bb5 F5 D5 F5 Bb5 F5 D5 F5 Bb5 F5 C6 Bb5 A5 F5",
        "E5 G5 C6 G5 E5 G5 C6 G5 E5 G5 C6 G5 D6 C6 Bb5 G5",
        "E5 A5 C#6 A5 E5 A5 C#6 A5 E6 . C#6 . A5 . E5 .",
        "- " * 16]
    tema.melodia(" | ".join(riff), PULSO_FINO, 0.26, eco=0.15)
    tema.arpegio([0, 2, 1, 2], PULSO_FINO, 0.07)
    tema.bajo("R . R 8 R . R 8 R . R 8 R . 8 R", BAJO, 0.5)
    ritmo = (["K - h - S - h K K - h - S - h h"] * 8 + ["K - h h S - h h K - h h S - h h"] * 8 +
             ["K h h h S h h h K h K h S h h h"] * 7 + ["K - S - S - S S K S S S S S S S"])
    tema.bateria(" | ".join(ritmo), 0.4)
    return tema


def tema_gasolinera():
    # La parada: un "lounge" con swing en Fa mayor, como musica de ascensor espacial
    tema = Tema("gasolinera", 96, ["Fmaj7", "Dm7", "Gm7", "C7", "Fmaj7", "Dm7", "Gm7", "C7",
                                   "Bbmaj7", "Bbm7", "Am7", "D7", "Gm7", "C7", "Fmaj7", "C7"], swing=0.3)
    tema.melodia("""
        A4 . . . C5 . E5 . . . . . D5 . C5 . | D5 . . . . . . . A4 . . . C5 . . . |
        Bb4 . . . D5 . F5 . . . E5 . D5 . . . | E5 . . . . . . . G4 . Bb4 . C5 . E5 . |
        F5 . . . E5 . C5 . A4 . . . C5 . F5 . | E5 . D5 . . . . . - - A4 . D5 . F5 . |
        A5 . . . G5 . F5 . D5 . . . F5 . E5 . | C5 . . . . . . . - - - - G4 . Bb4 . |
        A4 . . . D5 . F5 . . . A5 . . . G5 . | F5 . . . Db5 . . . Bb4 . . . Db5 . F5 . |
        E5 . . . . . C5 . A4 . . . C5 . E5 . | F#5 . . . . . . . A5 . . . F#5 . D5 . |
        G5 . . . F5 . D5 . Bb4 . . . D5 . F5 . | E5 . . . . . G5 . Bb5 . . . A5 . G5 . |
        A5 . . . . . . . F5 . . . C5 . A4 . | G4 . . . . . . . - - - - - - - -
    """, CAMPANA, 0.34, eco=0.3)
    tema.acompanar("- - - - X . - - - - X . - - - X", TECLADO, 0.2)
    tema.bajo("R . . . 3 . . . 5 . . . 6 . . .", BAJO, 0.5)
    tema.bateria(" | ".join(["K - h - S - h h K - h - S - h -"] * 15 + ["K - h - S - h h K - S - S S S -"]),
                 0.25)
    return tema


# Lo que compone este archivo: nombre del archivo (sin extension) -> funcion que arma el Tema.
# Para agregar un tema o un efecto: escribir su funcion y sumarla aca
COMPOSICIONES = {"musica_menu": tema_menu, "musica_jefe": tema_jefe, "musica_gasolinera": tema_gasolinera}
CARPETA_EFECTOS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "efectos")


def guardar(nombre, muestras, a_ogg=True, carpeta=CARPETA_EFECTOS):
    archivo_wav = os.path.join(carpeta, nombre + ".wav")
    with wave.open(archivo_wav, "wb") as archivo:
        archivo.setnchannels(1)
        archivo.setsampwidth(2)
        archivo.setframerate(FRECUENCIA)
        archivo.writeframes(array.array("h", (int(m * 32767) for m in muestras)).tobytes())
    if a_ogg and shutil.which("ffmpeg"):
        archivo_ogg = os.path.join(carpeta, nombre + ".ogg")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", archivo_wav,
                        "-c:a", "libvorbis", "-q:a", "5", archivo_ogg], check=True)
        os.remove(archivo_wav)
        print("  ->", os.path.normpath(archivo_ogg))
    elif a_ogg:
        print("  ->", os.path.normpath(archivo_wav), "(sin ffmpeg: cambiar .ogg por .wav en sonido.py)")
    else:
        print("  ->", os.path.normpath(archivo_wav))


if __name__ == "__main__":
    pedidos = sys.argv[1:] or list(COMPOSICIONES)
    for nombre in pedidos:
        if nombre not in COMPOSICIONES:
            sys.exit("No existe '%s'. Se puede componer: %s" % (nombre, ", ".join(COMPOSICIONES)))
    for nombre in pedidos:
        print("Componiendo", nombre, "...")
        tema = COMPOSICIONES[nombre]()
        guardar(nombre, tema.mezclar(), a_ogg=tema.vuelta)
