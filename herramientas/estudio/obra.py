"""
Obra: una composicion (un tema que da la vuelta o un efecto que suena una vez), con sus
pistas, la consola de mezcla y el master.

Como en un estudio:
- Cada Pista tiene un instrumento y su "tira" de consola: volumen (dB), paneo, ecualizador,
  saturacion, chorus, cuanto manda a la reverb y al delay, y cuanto "bombea" con el bombo.
- La Obra suma las pistas, pasa los envios por la reverb (una sala) y el delay (ecos con
  el tempo) y masteriza: ecualizador final, compresion de "pegamento", saturacion de cinta,
  volumen al objetivo en LUFS y limitador a -1 dB.

Notacion (como un "tracker": una grilla de semicorcheas, 16 por compas, "|" se ignora):
    "A4 . . . C5 . E5! . - - C5+E5+G5? . . ."
    nota = empieza ahi ("C5+E5" un acorde), "." sigue sonando, "-" silencio.
    "!" acento (fuerte), "?" suave (fantasma). Sin nada, fuerza normal.
Para efectos, en milisegundos: secuencia("G5:40 C6:90 -:20 C5+E5:300").
"""
import numpy as np

from herramientas.estudio.base import FS, muestras, midi, hertz, leer_acorde, db
from herramientas.estudio import procesos, armonia
from herramientas.estudio.sintesis import ruido as ruido_filtrado, temblor
from herramientas.estudio.bateria import GOLPES

PASOS_POR_COMPAS = 16
FUERZA_NORMAL, FUERZA_ACENTO, FUERZA_SUAVE = 0.8, 1.0, 0.5
COLA = 3.0                  # segundos de lugar para que un efecto se apague (despues se recorta)
NIVEL_CINTA = 0.5            # el pico con que la mezcla entra a la cinta del master (-6 dB)


def leer_simbolo(simbolo):
    # "C5+E5!" -> (["C5", "E5"], 1.0)
    fuerza = FUERZA_NORMAL
    if simbolo.endswith("!"):
        simbolo, fuerza = simbolo[:-1], FUERZA_ACENTO
    elif simbolo.endswith("?"):
        simbolo, fuerza = simbolo[:-1], FUERZA_SUAVE
    return simbolo.split("+"), fuerza


def pasos_de(texto):
    return [simbolo for simbolo in texto.split() if simbolo != "|"]


def eventos(pasos):
    # ["A4", ".", "-", "C5!"] -> [(0, 2, "A4"), (3, 1, "C5!")]: (paso, cuantos dura, simbolo)
    resultado = []
    for paso, simbolo in enumerate(pasos):
        if simbolo == ".":
            if resultado and resultado[-1][0] + resultado[-1][1] == paso:
                inicio, largo, nota = resultado[-1]
                resultado[-1] = (inicio, largo + 1, nota)
        elif simbolo != "-":
            resultado.append((paso, 1, simbolo))
    return resultado


class Pista:
    def __init__(self, obra, nombre, instrumento=None, volumen=0.0, paneo=0.0, reverb=0.0, delay=0.0, bombeo=0.0,
                 eq=(), saturacion=0.0, chorus=None, ancho=1.0):
        self.obra = obra
        self.nombre = nombre
        self.instrumento = instrumento
        self.volumen = volumen              # dB
        self.paneo = paneo                  # -1 izquierda, 1 derecha (balance)
        self.reverb = reverb                # cuanto manda a la sala (0 a 1)
        self.delay = delay                  # cuanto manda a los ecos (0 a 1)
        self.bombeo = bombeo                # cuanto baja con cada bombo (0 a 1)
        self.eq = eq                        # bandas de procesos.ecualizar
        self.saturacion = saturacion
        self.chorus = chorus                # (profundidad, velocidad, mezcla) o None
        self.ancho = ancho                  # 0 mono, 1 como viene, >1 mas abierto
        self.audio = np.zeros((2, obra.largo))

    # ---------- Poner sonido ----------

    def poner(self, sonido, inicio):
        # Suma 'sonido' desde la muestra 'inicio'. En un tema que da la vuelta, lo que se pasa
        # del final entra por el principio (y lo de antes del principio, por el final)
        largo = self.audio.shape[1]
        if self.obra.vuelta:
            inicio %= largo
            puesto = 0
            while puesto < sonido.shape[1]:
                lugar = (inicio + puesto) % largo
                cuanto = min(sonido.shape[1] - puesto, largo - lugar)
                self.audio[:, lugar:lugar + cuanto] += sonido[:, puesto:puesto + cuanto]
                puesto += cuanto
        else:
            if inicio < 0:
                sonido, inicio = sonido[:, -inicio:], 0
            cuanto = min(sonido.shape[1], largo - inicio)
            if cuanto > 0:
                self.audio[:, inicio:inicio + cuanto] += sonido[:, :cuanto]

    def nota(self, nota, inicio, segundos, fuerza=FUERZA_NORMAL, tremolo=None):
        # Una nota del instrumento en el segundo 'inicio' (con un poco de "humano").
        # tremolo: (desde_hz, hasta_hz, profundidad): el volumen tiembla, cada vez mas rapido
        azar = self.obra.azar
        nota = armonia.armonizar(nota, self.obra.color)        # (un efecto armonico, en su color)
        corrido = azar.normal(0, self.obra.humano) if self.obra.humano else 0.0
        fuerza = min(1.0, fuerza * (1 + azar.normal(0, 0.04))) if self.obra.humano else fuerza
        sonido = self.instrumento.tocar(nota, segundos, fuerza, azar)
        if tremolo:
            sonido = sonido * temblor(sonido.shape[1], *tremolo)
        self.poner(sonido, muestras(inicio + corrido))

    # ---------- Grillas (temas) ----------

    def grilla(self, texto, desde=0, legato=0.92, transponer=0):
        # Notas en la grilla de semicorcheas, desde el compas 'desde'
        for paso, largo, simbolo in eventos(pasos_de(texto)):
            notas, fuerza = leer_simbolo(simbolo)
            inicio = self.obra.segundo(desde * PASOS_POR_COMPAS + paso)
            final = self.obra.segundo(desde * PASOS_POR_COMPAS + paso + largo)
            for nota in notas:
                self.nota(midi(nota) + transponer, inicio, (final - inicio) * legato, fuerza)

    def acordes(self, patron, desde=0, hasta=None, registro=("A3", "E5"), legato=0.98, fuerza=FUERZA_NORMAL):
        # Los acordes de la obra en los pasos marcados con X de 'patron' (16 pasos, se repite
        # cada compas). Cada acorde se acomoda cerca del anterior (conduccion de voces: las
        # notas se mueven lo menos posible, como lo haria un pianista)
        hasta = len(self.obra.acordes) if hasta is None else hasta
        anterior = None
        for compas in range(desde, hasta):
            voces = self.obra.voces_del_acorde(compas, registro, anterior)
            anterior = voces
            for paso, largo, simbolo in eventos(pasos_de(patron)):
                _, fuerza_simbolo = leer_simbolo(simbolo)
                inicio = self.obra.segundo(compas * PASOS_POR_COMPAS + paso)
                final = self.obra.segundo(compas * PASOS_POR_COMPAS + paso + largo)
                for nota in voces:
                    self.nota(nota, inicio, (final - inicio) * legato, fuerza * fuerza_simbolo / FUERZA_NORMAL)

    def bajo(self, patron, desde=0, hasta=None, legato=0.85, octava=1):
        # El bajo sigue los acordes. 16 simbolos: R fundamental, 3 tercera, 5 quinta, 6 sexta
        # mayor, 7 septima, 8 octava, B la nota de la barra ("C/E": el Mi), "." sigue, "-"
        # silencio, "!"/"?" fuerza
        hasta = len(self.obra.acordes) if hasta is None else hasta
        for compas in range(desde, hasta):
            fundamental, intervalos, nota_bajo = leer_acorde(self.obra.acordes[compas])
            base = 12 * (octava + 1) + fundamental
            if base < 12 * (octava + 1) + 4:        # que la fundamental quede entre Mi y Re# de esa octava
                base += 12
            grados = {"R": 0, "3": intervalos[1] if len(intervalos) > 2 else 4, "5": 7, "6": 9,
                      "7": intervalos[3] if len(intervalos) > 3 else 10, "8": 12,
                      "B": ((nota_bajo - fundamental) % 12) if nota_bajo is not None else 0}
            for paso, largo, simbolo in eventos(pasos_de(patron)):
                grados_simbolo, fuerza = leer_simbolo(simbolo)
                inicio = self.obra.segundo(compas * PASOS_POR_COMPAS + paso)
                final = self.obra.segundo(compas * PASOS_POR_COMPAS + paso + largo)
                for grado in grados_simbolo:
                    self.nota(base + grados[grado], inicio, (final - inicio) * legato, fuerza)

    def arpegio(self, orden, desde=0, hasta=None, base="C4", cada=1, legato=0.8, fuerza=FUERZA_NORMAL):
        # Una nota del acorde cada 'cada' semicorcheas. 'orden' dice cual: 0 la mas grave del
        # acorde (desde 'base' para arriba), 1 la siguiente... y vuelve a empezar
        hasta = len(self.obra.acordes) if hasta is None else hasta
        for compas in range(desde, hasta):
            notas = self.obra.notas_desde(compas, midi(base), 8)
            for i, paso in enumerate(range(0, PASOS_POR_COMPAS, cada)):
                nota = notas[orden[i % len(orden)] % len(notas)]
                inicio = self.obra.segundo(compas * PASOS_POR_COMPAS + paso)
                final = self.obra.segundo(compas * PASOS_POR_COMPAS + paso + cada)
                self.nota(nota, inicio, (final - inicio) * legato, fuerza)

    # ---------- En segundos (efectos) ----------

    def secuencia(self, texto, inicio=0.0, legato=0.92, transponer=0, tremolo=None):
        # "G5:40 C6:90 -:20 C5+E5!:300": nota(s), fuerza y cuantos ms, una detras de otra
        t = inicio
        for simbolo in texto.split():
            alturas, ms = simbolo.rsplit(":", 1)
            segundos = int(ms) / 1000
            if alturas != "-":
                notas, fuerza = leer_simbolo(alturas)
                for nota in notas:
                    self.nota(midi(nota) + transponer, t, segundos * legato, fuerza, tremolo)
            t += segundos

    def barrido(self, puntos, inicio=0.0, fuerza=FUERZA_NORMAL, tremolo=None):
        # Una nota que cambia de altura: puntos = [(segundo, nota o Hz), ...]. Las notas con
        # nombre se llevan al color (las de Hz son graves sin altura que importe: se quedan)
        if self.obra.color is not None:
            puntos = [(t, hertz(armonia.armonizar(midi(v), self.obra.color)) if isinstance(v, str) else v)
                      for t, v in puntos]
        sonido = self.instrumento.tocar(list(puntos), puntos[-1][0], fuerza, self.obra.azar)
        if tremolo:
            sonido = sonido * temblor(sonido.shape[1], *tremolo)
        self.poner(sonido, muestras(inicio))

    def ruido(self, segundos, inicio=0.0, volumen=1.0, **opciones):
        # Ruido filtrado (ver sintesis.ruido: filtro, forma, chasquidos, tremolo...)
        self.poner(ruido_filtrado(segundos, azar=self.obra.azar, **opciones) * volumen, muestras(inicio))

    def golpe(self, letra, inicio=0.0, fuerza=FUERZA_NORMAL):
        sonido = GOLPES[letra](fuerza, self.obra.azar)
        comienzo = muestras(inicio)
        if letra == "R":
            comienzo -= sonido.shape[1]         # el platillo al reves TERMINA en ese momento
        self.poner(sonido, comienzo)

    # ---------- La tira de consola ----------

    def procesada(self, bombeo):
        # El audio con su tira de consola (todo menos los envios)
        audio = self.audio * db(self.volumen)
        if self.eq:
            audio = procesos.ecualizar(audio, self.eq, self.obra.vuelta)
        if self.saturacion:
            audio = procesos.saturar(audio, self.saturacion)
        if self.chorus:
            audio = procesos.chorus(audio, *self.chorus, vuelta=self.obra.vuelta)
        if self.ancho != 1.0:
            audio = procesos.ensanchar(audio, self.ancho)
        if self.paneo:
            audio = audio * np.array([[min(1, 1 - self.paneo)], [min(1, 1 + self.paneo)]])
        if self.bombeo and bombeo is not None:
            audio = audio * (1 - self.bombeo + self.bombeo * bombeo)
        return audio


class Bateria(Pista):
    def grilla(self, texto, desde=0, legato=None, transponer=0):
        # Letras de bateria (ver bateria.GOLPES): K bombo, S caja, C palmas, h hat cerrado,
        # H abierto, T/t toms, X platillo, R platillo al reves (termina en ese paso)
        for paso, simbolo in enumerate(pasos_de(texto)):
            if simbolo in (".", "-"):
                continue
            letra, fuerza = leer_simbolo(simbolo)
            letra = letra[0]
            numero = desde * PASOS_POR_COMPAS + paso
            corrido = self.obra.azar.normal(0, self.obra.humano * 0.5) if self.obra.humano and letra in "hH" else 0
            self.golpe(letra, self.obra.segundo(numero) + corrido, fuerza)
            if letra == "K":
                self.obra.golpes_bombo.append(muestras(self.obra.segundo(numero)))


class Obra:
    def __init__(self, nombre, bpm=120, acordes=None, segundos=None, vuelta=True, swing=0.0, sala=(2.2, 0.45),
                 eco=0.75, realimentacion=0.35, oscuridad_eco=0.5, objetivo=-14.0, master_eq=None, pegamento=True,
                 humano=0.003, cinta=0.08):
        self.nombre = nombre
        self.bpm = bpm
        self.acordes = acordes or []
        self.vuelta = vuelta
        self.swing = swing                      # cuanto se atrasa la corchea de contratiempo (0 a 0.5)
        self.paso = 60 / bpm / 4                # segundos por semicorchea
        if self.acordes:
            self.segundos = len(self.acordes) * PASOS_POR_COMPAS * self.paso
        else:
            self.segundos = segundos
        self.largo = muestras(self.segundos + (0 if vuelta else COLA))
        self.sala = sala                        # (segundos de reverb, brillo)
        self.eco = eco * 60 / bpm               # el delay en tiempos (0.75 = corchea con puntillo)
        self.realimentacion = realimentacion
        self.oscuridad_eco = oscuridad_eco
        self.objetivo = objetivo                # LUFS del master
        self.master_eq = master_eq if master_eq is not None else [
            ("corte_graves", 30), ("graves", 55, -2.0), ("campana", 3500, -1.0, 1.2), ("agudos", 11000, 1.5),
            ("corte_agudos", 18000)]
        self.pegamento = pegamento              # compresion suave del master
        self.cinta = cinta                      # saturacion de cinta del master (0 = limpio)
        self.humano = humano                    # segundos de imprecision al tocar (0 = maquina)
        self.azar = np.random.default_rng(sum(nombre.encode()) * 7919)     # el mismo resultado siempre
        self.pistas = []
        self.golpes_bombo = []
        self.retorno_sala = 0.5                 # cuanto de la reverb vuelve a la mezcla
        self.color = armonia.color_actual       # un efecto armonico se compone en un color (armonia.py)

    # ---------- Tiempo y armonia ----------

    def segundo(self, paso):
        # En que segundo empieza un paso de semicorchea (con swing)
        segundos = paso * self.paso
        if paso % 4 == 2:
            segundos += self.swing * 2 * self.paso
        return segundos

    def notas_desde(self, compas, desde, cuantas):
        # Las notas del acorde de ese compas, de 'desde' (midi) para arriba
        fundamental, intervalos, _ = leer_acorde(self.acordes[compas])
        clases = sorted({(fundamental + i) % 12 for i in intervalos})
        notas = []
        nota = desde
        while len(notas) < cuantas:
            if nota % 12 in clases:
                notas.append(nota)
            nota += 1
        return notas

    def voces_del_acorde(self, compas, registro, anterior):
        # Una posicion del acorde dentro del registro, la mas cercana a la anterior
        fundamental, intervalos, _ = leer_acorde(self.acordes[compas])
        bajo, alto = midi(registro[0]), midi(registro[1])
        clases = [(fundamental + i) % 12 for i in intervalos]
        candidatas = []
        for inicio in range(bajo, bajo + 12):
            if inicio % 12 not in clases:
                continue
            voces = [inicio]
            for clase in clases[clases.index(inicio % 12) + 1:] + clases[:clases.index(inicio % 12)]:
                nota = voces[-1] + 1
                while nota % 12 != clase:
                    nota += 1
                voces.append(nota)
            if voces[-1] <= alto:
                candidatas.append(voces)
        if not candidatas:
            candidatas = [[bajo + (c - bajo) % 12 for c in clases]]
        if anterior is None:
            return min(candidatas, key=lambda v: abs(sum(v) / len(v) - (bajo + alto) / 2))
        return min(candidatas, key=lambda voces: _distancia(voces, anterior))

    # ---------- Pistas ----------

    def pista(self, nombre, instrumento=None, **consola):
        pista = Pista(self, nombre, instrumento, **consola)
        self.pistas.append(pista)
        return pista

    def bateria(self, nombre="bateria", **consola):
        pista = Bateria(self, nombre, None, **consola)
        self.pistas.append(pista)
        return pista

    # ---------- Mezcla y master ----------

    def mezclar(self):
        bombeo = None
        if self.golpes_bombo:
            bombeo = procesos.bombeo(self.largo, self.golpes_bombo, 1.0, 0.16, self.vuelta)
        seco = np.zeros((2, self.largo))
        a_la_sala = np.zeros((2, self.largo))
        a_los_ecos = np.zeros((2, self.largo))
        for pista in self.pistas:
            audio = pista.procesada(bombeo)
            seco += audio
            if pista.reverb:
                a_la_sala += audio * pista.reverb
            if pista.delay:
                a_los_ecos += audio * pista.delay
        mezcla = seco
        if np.any(a_los_ecos):
            ecos = procesos.delay(a_los_ecos, self.eco, self.realimentacion, self.oscuridad_eco, self.vuelta)
            ecos = procesos.ecualizar(ecos[:, :self.largo], [("corte_graves", 250), ("corte_agudos", 7000)],
                                      self.vuelta)
            mezcla = mezcla + ecos[:, :self.largo]
            a_la_sala += ecos[:, :self.largo] * 0.3
        if np.any(a_la_sala):
            sala = procesos.reverb(a_la_sala, *self.sala, vuelta=self.vuelta)
            sala = procesos.ecualizar(sala[:, :self.largo], [("corte_graves", 200), ("corte_agudos", 8000)],
                                      self.vuelta)
            mezcla = mezcla + sala[:, :self.largo] * self.retorno_sala
        return self.masterizar(mezcla)

    def masterizar(self, mezcla):
        mezcla = procesos.ecualizar(mezcla, self.master_eq, self.vuelta)
        if self.pegamento:
            mezcla = procesos.comprimir(mezcla, procesos.a_db_pico(mezcla) - 10, 2.0, 0.02, 0.25, vuelta=self.vuelta)
        if self.cinta:
            # La cinta trabaja SIEMPRE al mismo nivel (el pico en NIVEL_CINTA). Antes recibia la
            # mezcla tal como salia de las pistas: un acorde de 3 notas llegaba al triple que una
            # nota sola y la curva lo aplastaba. Las notas se "ensuciaban" entre ellas
            # (intermodulacion): eso era lo "saturado" de las monedas, los menus y los premios
            mezcla = mezcla * (NIVEL_CINTA / max(np.max(np.abs(mezcla)), 1e-9))
            mezcla = procesos.saturar(mezcla, self.cinta)
        mezcla = mezcla * db(self.objetivo - self.medir_volumen(mezcla))
        mezcla = procesos.limitar(mezcla, -1.0, vuelta=self.vuelta)
        if not self.vuelta:
            mezcla = recortar_silencio(mezcla)
        return mezcla

    def medir_volumen(self, mezcla):
        return procesos.loudness(mezcla)


class Efecto(Obra):
    # Un efecto de sonido: suena una vez, se arma en segundos y su volumen sale de la dinamica
    # (el bloque de 400 ms mas fuerte, en LUFS). Sin compresion ni cinta en el master: conserva
    # su golpe y suena limpio (las notas de un acorde no se mezclan entre ellas)
    # Calibrado contra la musica (-14 LUFS): una moneda (mf) suena apenas por encima del tema,
    # un tic de menu (p) por debajo y un gran momento (ff) bien arriba
    DINAMICAS = {"pp": -24.0, "p": -19.0, "mf": -15.0, "f": -12.0, "ff": -9.0}

    def __init__(self, nombre, segundos, dinamica="mf", bpm=120, sala=(1.2, 0.5), cola=None, **otros):
        super().__init__(nombre, bpm=bpm, segundos=segundos, vuelta=False, sala=sala,
                         objetivo=self.DINAMICAS[dinamica], pegamento=False, humano=0.0, cinta=0.0,
                         **otros)
        self.dinamica = dinamica
        # Cuanto puede seguir sonando despues de 'segundos' (la cola de la sala). En el juego
        # los efectos se pisan: con colas largas, tres monedas seguidas eran un solo ruido que
        # no terminaba. Por eso un efecto es mas seco que un tema (menos sala y una cola corta)
        self.cola = sala[0] * 0.3 if cola is None else cola
        self.retorno_sala = 0.3

    def medir_volumen(self, mezcla):
        return procesos.loudness_maximo(mezcla)

    def masterizar(self, mezcla):
        mezcla = super().masterizar(mezcla)
        maximo = muestras(self.segundos + self.cola)
        if mezcla.shape[1] > maximo:
            mezcla = mezcla[:, :maximo].copy()
            apagar = min(muestras(0.25), maximo)
            mezcla[:, -apagar:] *= np.cos(np.linspace(0, np.pi / 2, apagar)) ** 2
        return mezcla


def _distancia(voces, anterior):
    # Cuanto se mueven las voces de un acorde al otro, voz por voz (la mas grave con la mas
    # grave...). Si tienen distinta cantidad de notas, cada una contra la mas cercana
    if len(voces) == len(anterior):
        return sum(abs(a - b) for a, b in zip(sorted(voces), sorted(anterior)))
    return sum(min(abs(nota - otra) for otra in anterior) for nota in voces)


def recortar_silencio(mezcla, debajo_del_pico=50.0):
    # Saca el final que ya no se oye: lo que esta 50 dB por debajo del pico (deja 20 ms que se
    # apagan). Relativo al pico: un efecto suave tambien se recorta bien
    nivel = np.max(np.abs(mezcla), axis=0)
    sonoras = np.nonzero(nivel > np.max(nivel) * db(-debajo_del_pico))[0]
    fin = (sonoras[-1] if len(sonoras) else 0) + muestras(0.02)
    mezcla = mezcla[:, :fin].copy()
    apagar = min(muestras(0.02), mezcla.shape[1])
    mezcla[:, -apagar:] *= np.linspace(1, 0, apagar)
    return mezcla
