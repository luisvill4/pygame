"""
El compositor VIEJO: chiptune hecho con codigo.

YA NO HACE SONIDOS DEL JUEGO. Todo lo que suena sale del estudio (herramientas/componer.py).
Sus temas (menu, jefe, gasolinera y los de cada jefe) se rehicieron en el estudio para que
todo el juego tenga un solo sonido; estos quedan para escucharlos o compararlos, y se
guardan en herramientas/chiptune/ (nunca en efectos/: pisarian los del juego).

Uso (desde la carpeta del juego):
    python herramientas/componer_musica.py                  todo lo de COMPOSICIONES
    python herramientas/componer_musica.py musica_jefe      solo ese (o varios nombres)
    python herramientas/componer_musica.py --escuchar x     lo compone y lo hace sonar

Escribe en herramientas/chiptune/ lo que esta en COMPOSICIONES (abajo de todo): los temas
de menu, jefe y gasolinera. Solo usa la biblioteca de Python. Los temas se pasan a OGG con
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

Herramientas para EFECTOS (en segundos, no en la grilla; ver nuevo_efecto()):
- secuencia("G5:40 C6:90 -:20 C5+E5+G5:300"): notas seguidas con su duracion en ms
  ("-" silencio, "+" notas juntas: un acorde).
- barrido([(0, "A3"), (0.6, "Eb4")]): una nota que cambia de altura siguiendo una CURVA
  (puntos de segundo y valor, como la automatizacion de un programa de musica).
- ruido(segundos, filtro=[(0, 800), (0.06, 6000)]): ruido con un filtro que se mueve
  (dash, explosiones, viento, vapor); "chasquidos" lo vuelve crepitar.
- tremolo=(desde_hz, hasta_hz, profundidad) hace temblar el volumen y
  vibrato=(desde_hz, hasta_hz, semitonos) la afinacion, cada vez mas rapido si hasta > desde.
- dinamica ("pp", "p", "mf", "f", "ff"): que tan fuerte queda el archivo. La musica va a "ff".
Al guardar se mide cuanto dura y que tan fuerte suena (pico y RMS, en dB).
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
# Que tan fuerte queda el archivo (el pico de la mezcla). La musica va a "ff" y los efectos
# eligen la suya: asi un tic de menu no suena como una explosion
DINAMICAS = {"pp": 0.1, "p": 0.18, "mf": 0.3, "f": 0.45, "ff": 0.6}

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


def a_hertz(valor):
    # Una altura en Hz: un numero ya lo es; un nombre de nota ("A4") se convierte
    return hertz(midi(valor)) if isinstance(valor, str) else valor


def curva(puntos, t, exponencial=False):
    # Automatizacion: el valor en el segundo t de una lista de (segundo, valor), uniendo los
    # puntos con rectas. 'exponencial' los une con una curva que el oido escucha pareja:
    # es la que va para alturas y filtros (de 100 a 200 Hz suena igual que de 1000 a 2000)
    if t <= puntos[0][0]:
        return puntos[0][1]
    for (t0, v0), (t1, v1) in zip(puntos, puntos[1:]):
        if t <= t1:
            avance = (t - t0) / (t1 - t0) if t1 > t0 else 1
            if exponencial:
                return v0 * (v1 / v0) ** avance
            return v0 + (v1 - v0) * avance
    return puntos[-1][1]


class Oscilador:
    # Una oscilacion lenta (un "LFO") que va de 'desde' a 'hasta' Hz en 'duracion' segundos:
    # mueve el volumen (tremolo) o la afinacion (vibrato). Si 'hasta' es mayor, se acelera
    def __init__(self, desde, hasta, duracion):
        self.desde = desde
        self.hasta = hasta
        self.duracion = max(duracion, 0.001)
        self.fase = 0.0

    def siguiente(self, t):
        # -1 a 1 en el segundo t (hay que llamarlo una vez por muestra, en orden)
        self.fase += (self.desde + (self.hasta - self.desde) * min(1, t / self.duracion)) / FRECUENCIA
        return math.sin(2 * math.pi * self.fase)


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

    def tocar(self, pista, inicio, duracion, frecuencia, volumen, tremolo=None, vibrato=None):
        # Suma la nota a la pista (una lista que "da la vuelta": ver el comentario de arriba).
        # 'frecuencia' es un numero o una funcion del segundo (un barrido). 'tremolo' y
        # 'vibrato': (desde_hz, hasta_hz, profundidad o semitonos), o None
        largo = len(pista)
        muestras_nota = int(duracion * FRECUENCIA)
        muestras_liberacion = int(self.liberacion * FRECUENCIA)
        temblor = Oscilador(tremolo[0], tremolo[1], duracion) if tremolo else None
        ondulacion = Oscilador(vibrato[0], vibrato[1], duracion) if vibrato else None
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
            f = frecuencia(t) if callable(frecuencia) else frecuencia
            if self.vibrato and t > 0.12:
                f *= 1 + self.vibrato * math.sin(2 * math.pi * 5.5 * t)
            if ondulacion is not None:
                f *= 2 ** (vibrato[2] * ondulacion.siguiente(t) / 12)
            if temblor is not None:
                env *= 1 - tremolo[2] * (0.5 + 0.5 * temblor.siguiente(t))
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
    def __init__(self, nombre, bpm, acordes, swing=0.0, vuelta=True, dinamica="ff"):
        self.nombre = nombre
        self.pico = DINAMICAS[dinamica]     # que tan fuerte queda el archivo
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

    # ---------- Herramientas de efectos (en segundos) ----------

    def secuencia(self, notas, instrumento, volumen, inicio=0.0, eco=0.0, retraso_eco=0.12, legato=0.9,
                  tremolo=None, vibrato=None):
        # "G5:40 C6:90 -:20 C5+E5+G5:300": cada nota (o acorde, con "+") y cuantos ms dura,
        # una detras de otra desde el segundo 'inicio'. "-" es silencio
        pista = self.nueva_voz(volumen)
        t = inicio
        for simbolo in notas.split():
            alturas, ms = simbolo.split(":")
            segundos = int(ms) / 1000
            if alturas != "-":
                for nota in alturas.split("+"):
                    instrumento.tocar(pista, round(t * FRECUENCIA), segundos * legato, hertz(midi(nota)), 1.0,
                                      tremolo, vibrato)
            t += segundos
        if eco:
            agregar_eco(pista, round(retraso_eco * FRECUENCIA), eco, self.vuelta)

    def barrido(self, alturas, instrumento, volumen, inicio=0.0, eco=0.0, retraso_eco=0.12, tremolo=None,
                vibrato=None):
        # Una nota que cambia de altura: alturas = [(segundo, nota o Hz), ...] (al menos dos).
        # Dura hasta el ultimo punto (mas la liberacion del instrumento)
        puntos = [(t, a_hertz(valor)) for t, valor in alturas]
        pista = self.nueva_voz(volumen)
        instrumento.tocar(pista, round(inicio * FRECUENCIA), puntos[-1][0], lambda t: curva(puntos, t, True),
                          1.0, tremolo, vibrato)
        if eco:
            agregar_eco(pista, round(retraso_eco * FRECUENCIA), eco, self.vuelta)

    def ruido(self, segundos, volumen, inicio=0.0, filtro=((0, 8000),), pasa_altos=None, forma=None,
              tremolo=None, chasquidos=0):
        # Ruido (sin altura: nunca desafina) con un filtro que se mueve:
        # - filtro: curva de hasta donde deja pasar los agudos (Hz; mas alto = mas brillante)
        # - pasa_altos: curva opcional que ademas saca los graves (vapor, platillos)
        # - forma: curva del volumen (0 a 1); por defecto empieza de golpe y se apaga parejo
        # - tremolo: (desde_hz, hasta_hz, profundidad); chasquidos: cuantos "crac" por segundo
        #   en vez de un soplido continuo (brasas, chispas, un cascabel)
        pista = self.nueva_voz(volumen)
        largo = len(pista)
        comienzo = round(inicio * FRECUENCIA)
        filtro = [(t, a_hertz(valor)) for t, valor in filtro]
        if pasa_altos is not None:
            pasa_altos = [(t, a_hertz(valor)) for t, valor in pasa_altos]
        forma = forma or [(0, 0), (0.003, 1), (segundos, 0)]
        temblor = Oscilador(tremolo[0], tremolo[1], segundos) if tremolo else None
        bajo_1 = bajo_2 = alto_1 = alto_2 = 0.0     # dos filtros de un polo seguidos: corte mas marcado
        chasquido = 0                               # muestras que le quedan al "crac" que suena
        for i in range(int(segundos * FRECUENCIA)):
            t = i / FRECUENCIA
            valor = self.azar.uniform(-1, 1)
            if chasquidos:
                if chasquido <= 0 and self.azar.random() < chasquidos / FRECUENCIA:
                    chasquido = int(0.004 * FRECUENCIA)
                valor = valor if chasquido > 0 else 0.0
                chasquido -= 1
            corte = 1 - math.exp(-2 * math.pi * curva(filtro, t, True) / FRECUENCIA)
            bajo_1 += corte * (valor - bajo_1)
            bajo_2 += corte * (bajo_1 - bajo_2)
            salida = bajo_2
            if pasa_altos is not None:
                corte = 1 - math.exp(-2 * math.pi * curva(pasa_altos, t, True) / FRECUENCIA)
                alto_1 += corte * (salida - alto_1)
                alto_2 += corte * (alto_1 - alto_2)
                salida -= alto_2
            nivel = curva(forma, t)
            if temblor is not None:
                nivel *= 1 - tremolo[2] * (0.5 + 0.5 * temblor.siguiente(t))
            pista[(comienzo + i) % largo] += salida * nivel

    def mezclar(self):
        # Suma las voces, ajusta el volumen y lo "redondea" suave para que no se rompa
        mezcla = [0.0] * self.largo
        for pista, volumen in self.voces:
            for i, valor in enumerate(pista):
                mezcla[i] += valor * volumen
        if not self.vuelta:
            mezcla = recortar_silencio(mezcla)
        maximo = max(abs(valor) for valor in mezcla) or 1
        return [math.tanh(1.3 * valor / maximo) / math.tanh(1.3) * self.pico for valor in mezcla]


def nuevo_efecto(nombre, segundos, dinamica="mf"):
    # Un Tema para un efecto armado en segundos (secuencia, barrido, ruido): tiene lugar
    # para 'segundos' mas la cola, y al guardarlo se recorta el silencio del final.
    # (Si ademas usa grillas, son de compases de 2 s: 120 bpm)
    return Tema(nombre, 120, ["C"] * max(1, math.ceil(segundos / 2)), vuelta=False, dinamica=dinamica)


def medir(muestras):
    # (segundos, pico en dB, RMS en dB): cuanto dura y que tan fuerte suena. 0 dB es el
    # maximo; el RMS es el volumen "que se siente" (sirve para emparejar efectos)
    pico = max((abs(m) for m in muestras), default=0) or 1e-9
    rms = math.sqrt(sum(m * m for m in muestras) / max(len(muestras), 1)) or 1e-9
    return len(muestras) / FRECUENCIA, 20 * math.log10(pico), 20 * math.log10(rms)


def escuchar(muestras):
    # Lo hace sonar (para componer de oido sin abrir el juego)
    import pygame
    pygame.mixer.init(FRECUENCIA, -16, 1)
    sonido = pygame.mixer.Sound(buffer=array.array("h", (int(m * 32767) for m in muestras)).tobytes())
    sonido.play()
    pygame.time.wait(int(sonido.get_length() * 1000) + 150)


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


# ---------- Un tema para cada jefe (el Ojo usa musica_jefe) ----------
# Todos en Re menor (como musica_jefe): asi los efectos de los jefes, pensados en Re menor
# (LISTA_DE_SONIDOS.md, seccion 7), afinan con cualquiera. Cada uno con la personalidad de su jefe


def tema_fortaleza():
    # ACORAZADO IMPERIAL - "Marcha imperial": una marcha militar a 132 bpm. Redoblante de
    # desfile, bajo "oom-pah" (fundamental y quinta) y una melodia de metales con puntillos
    tema = Tema("jefe_fortaleza", 132, ["Dm", "Dm", "Gm", "A", "Dm", "Bb", "Gm", "A",
                                        "Bb", "C", "Dm", "Dm", "Gm", "A", "Dm", "A"])
    tema.melodia("""
        D4 . . A4 . . D5 . . . . . F5 . E5 . | D5 . . . . . . . A4 . . . . . . . |
        G4 . . Bb4 . . D5 . . . . . G5 . F5 . | E5 . . . . . . . C#5 . . . A4 . . . |
        D4 . . A4 . . D5 . . . . . F5 . A5 . | Bb5 . . . . . A5 . G5 . . . F5 . . . |
        G5 . . F5 . . E5 . . . D5 . E5 . . . | A4 . . . . . . . - - - - C#5 . E5 . |
        F5 . . . . . D5 . Bb4 . . . D5 . F5 . | G5 . . . . . E5 . C5 . . . E5 . G5 . |
        A5 . . . . . . . F5 . . . D5 . . . | A4 . . D5 . . F5 . . A5 . . . . . . |
        Bb5 . . . A5 . G5 . . . F5 . G5 . . . | A5 . . . . . . . E5 . . . C#5 . . . |
        D5 . . F5 . . A5 . . . D6 . . . . . | C#6 . . . . . . . A5 . . . E5 . C#5 .
    """, PULSO_REDONDO, 0.32, eco=0.2)
    tema.acompanar("X - - - X - - - X - - - X - X -", TECLADO, 0.22)
    tema.bajo("R . . . 5 . . . R . . . 5 . 5 .", BAJO, 0.5)
    marcha = ["K - - - S - - S K - - - S - S S"] * 7 + ["K - S S K - S S K S S S S S S S"]
    tema.bateria(" | ".join(marcha * 2), 0.4)
    return tema


def tema_serpiente():
    # DEVORADORA DE ESTRELLAS - "Danza de escamas": 120 bpm con swing, una flauta nasal de
    # encantador de serpientes (pulso fino) con adornos frigios (Mi bemol de paso) sobre Re menor
    tema = Tema("jefe_serpiente", 120, ["Dm", "Dm", "Gm", "Dm", "Bb", "A", "Dm", "Dm",
                                        "Gm", "Gm", "Dm", "Dm", "Bb", "A", "Dm", "A"], swing=0.3)
    tema.melodia("""
        D5 . Eb5 D5 C#5 . D5 . . . F5 . E5 . D5 . | A4 . . . . . . . - - - - - - - - |
        G4 . A4 Bb4 A4 . G4 . . . Bb4 . A4 . G4 . | F4 . . . E4 . D4 . . . . . - - - - |
        D5 . Eb5 D5 C5 . Bb4 . . . D5 . C5 . Bb4 . | A4 . . . . . . . C#5 . . . E5 . . . |
        F5 . E5 . D5 . Eb5 . D5 . . . . . . . | - - - - - - - - A4 . D5 . F5 . A5 . |
        Bb5 . A5 . G5 . . . A5 . Bb5 . A5 . G5 . | D5 . . . . . . . - - G4 . A4 . Bb4 . |
        A4 . . . D5 . . . F5 . E5 . D5 . C#5 . | D5 . . . . . . . - - - - - - - - |
        F5 . . . Eb5 . D5 . . . C5 . Bb4 . . . | C#5 . . . E5 . . . A5 . . . G5 . E5 . |
        F5 . E5 . D5 . . . A4 . . . D5 . . . | C#5 . . . . . . . E5 . . . A4 . . .
    """, PULSO_FINO, 0.34, eco=0.25)
    tema.arpegio([0, 2, 1, 2], CAMPANA, 0.06, eco=0.2)
    tema.bajo("R . . R . . 5 . R . . R . . 8 .", BAJO, 0.5)
    ritmo = ["K - - K - - S - K - K - S - - -"] * 7 + ["K - - K - - S - K - S - S S S S"]
    tema.bateria(" | ".join(ritmo * 2), 0.35)
    return tema


def tema_colmena():
    # MADRE DEL ENJAMBRE - "Enjambre de cristal": 160 bpm, un riff de semicorcheas que zumba
    # en el registro grave (como las alas), bajo en octavas y la bateria empujando siempre
    tema = Tema("jefe_colmena", 160, ["Dm", "C", "Bb", "A", "Dm", "C", "Bb", "C",
                                      "Gm", "A", "Dm", "Bb", "Gm", "A", "Dm", "A"])
    tema.melodia("""
        D5 . F5 . A5 . . . G5 . F5 . E5 . D5 . | E5 . . . C5 . . . G4 . . . C5 . E5 . |
        F5 . . . D5 . . . Bb4 . . . D5 . F5 . | E5 . . . . . . . C#5 . . . . . . . |
        A5 . . . G5 . F5 . . . E5 . F5 . A5 . | G5 . . . E5 . C5 . . . E5 . G5 . . . |
        F5 . . . D5 . Bb4 . . . D5 . F5 . . . | E5 . . . . . . . G5 . . . . . . . |
        Bb5 . . . A5 . G5 . . . D5 . G5 . . . | A5 . . . . . E5 . . . C#5 . E5 . . . |
        F5 . . . E5 . D5 . . . A4 . D5 . F5 . | D5 . . . . . . . F5 . . . Bb5 . . . |
        G5 . . . Bb5 . . . D6 . . . C6 . Bb5 . | A5 . . . . . . . E5 . . . C#5 . . . |
        D5 . . . F5 . . . A5 . . . D6 . . . | C#6 . . . . . . . A5 . . . E5 . . .
    """, PULSO_MEDIO, 0.3, eco=0.15)
    tema.arpegio([0, 0, 1, 0, 2, 0, 1, 0], PULSO_FINO, 0.16)        # el zumbido de las alas
    tema.bajo("R . 8 . R . 8 . R . 8 . R . 8 .", BAJO, 0.5)
    ritmo = ["K - h - S - h K K - h - S - h h"] * 7 + ["K - h h S - h h K S K S S S S S"]
    tema.bateria(" | ".join(ritmo * 2), 0.4)
    return tema


def tema_singularidad():
    # EL FIN DE LA LUZ - "Horizonte de sucesos": 100 bpm a medio tiempo, notas largas que caen
    # al centro, campanas lentas con mucho eco y un bajo que pesa (ni la luz escapa)
    tema = Tema("jefe_singularidad", 100, ["Dm", "Dm", "Bb", "Bb", "Gm", "Gm", "A", "A",
                                           "Dm", "Bb", "Gm", "A"])
    tema.melodia("""
        D5 . . . . . . . . . . . A4 . . . | F5 . . . . . . . E5 . . . D5 . . . |
        D5 . . . . . . . . . . . F5 . . . | Bb5 . . . . . . . A5 . . . F5 . . . |
        G5 . . . . . . . . . . . D5 . . . | Bb4 . . . . . . . C5 . . . D5 . . . |
        E5 . . . . . . . . . . . . . . . | C#5 . . . . . . . E5 . . . A5 . . . |
        A5 . . . . . . . F5 . . . D5 . . . | F5 . . . . . . . . . . . D5 . . . |
        G5 . . . . . . . Bb5 . . . A5 . . . | A5 . . . . . . . - - - - - - - -
    """, PULSO_REDONDO, 0.3, eco=0.35)
    tema.arpegio([0, 1, 2, 3], CAMPANA, 0.12, eco=0.35)
    tema.bajo("R . . . . . . . . . . . 5 . . .", BAJO, 0.55)
    ritmo = ["K - - - - - - - S - - - - - K -"] * 11 + ["K - - - - - K - S - S - S S S S"]
    tema.bateria(" | ".join(ritmo), 0.4)
    return tema


# Lo que compone este archivo: nombre del archivo (sin extension) -> funcion que arma el Tema.
# Para agregar un tema o un efecto: escribir su funcion y sumarla aca
COMPOSICIONES = {"musica_menu": tema_menu, "musica_jefe": tema_jefe, "musica_gasolinera": tema_gasolinera,
                 "musica_jefe_fortaleza": tema_fortaleza, "musica_jefe_serpiente": tema_serpiente,
                 "musica_jefe_colmena": tema_colmena, "musica_jefe_singularidad": tema_singularidad}
# (no en efectos/: los temas del juego ahora salen del estudio y estos los pisarian)
CARPETA_EFECTOS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chiptune")


def _guardar_ogg(archivo, muestras):
    # Sin ffmpeg, con soundfile (si esta). De a bloques: el codificador de Vorbis se queda sin
    # pila en Windows si recibe todo de una vez. Devuelve False si no se pudo
    try:
        import numpy
        import soundfile
    except ImportError:
        return False
    with soundfile.SoundFile(archivo, "w", FRECUENCIA, 1, format="OGG", subtype="VORBIS",
                             compression_level=0.4) as salida:
        for desde in range(0, len(muestras), 32768):
            salida.write(numpy.asarray(muestras[desde:desde + 32768], dtype=float))
    return True


def guardar(nombre, muestras, a_ogg=True, carpeta=CARPETA_EFECTOS):
    os.makedirs(carpeta, exist_ok=True)
    segundos, pico, rms = medir(muestras)
    print("  %.2f s, pico %.1f dB, RMS %.1f dB" % (segundos, pico, rms))
    archivo_wav = os.path.join(carpeta, nombre + ".wav")
    with wave.open(archivo_wav, "wb") as archivo:
        archivo.setnchannels(1)
        archivo.setsampwidth(2)
        archivo.setframerate(FRECUENCIA)
        archivo.writeframes(array.array("h", (int(m * 32767) for m in muestras)).tobytes())
    archivo_ogg = os.path.join(carpeta, nombre + ".ogg")
    if a_ogg and shutil.which("ffmpeg"):
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", archivo_wav,
                        "-c:a", "libvorbis", "-q:a", "5", archivo_ogg], check=True)
        os.remove(archivo_wav)
        print("  ->", os.path.normpath(archivo_ogg))
    elif a_ogg and _guardar_ogg(archivo_ogg, muestras):
        os.remove(archivo_wav)
        print("  ->", os.path.normpath(archivo_ogg))
    elif a_ogg:
        print("  ->", os.path.normpath(archivo_wav), "(sin ffmpeg: cambiar .ogg por .wav en sonido.py)")
    else:
        print("  ->", os.path.normpath(archivo_wav))


if __name__ == "__main__":
    con_escuchar = "--escuchar" in sys.argv
    pedidos = [nombre for nombre in sys.argv[1:] if not nombre.startswith("--")] or list(COMPOSICIONES)
    for nombre in pedidos:
        if nombre not in COMPOSICIONES:
            sys.exit("No existe '%s'. Se puede componer: %s" % (nombre, ", ".join(COMPOSICIONES)))
    for nombre in pedidos:
        print("Componiendo", nombre, "...")
        tema = COMPOSICIONES[nombre]()
        muestras = tema.mezclar()
        guardar(nombre, muestras, a_ogg=tema.vuelta)
        if con_escuchar:
            escuchar(muestras)
