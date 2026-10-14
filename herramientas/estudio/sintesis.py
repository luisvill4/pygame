"""
Sintesis: de donde sale cada sonido.

- Osciladores SIN ALIASING (PolyBLEP): una sierra o una cuadrada "ingenuas" tienen agudos
  que se doblan y suenan asperos y chillones; PolyBLEP redondea cada salto y los saca.
- Envolventes ADSR con curvas exponenciales (como un sinte analogico, no rectas).
- Filtro "state variable" (TPT, el de los sintes virtuales analogicos): pasa bajos con
  resonancia, que se abre y se cierra con su propia envolvente. Es lo que le da "cuerpo"
  y calidez a un sonido: el brillo aparece al tocar la nota y despues se apaga.
- Tres tipos de instrumento:
    Sinte   sustractivo: varias voces desafinadas y abiertas en estereo (como un pad
            o un "supersaw"), sub-oscilador, filtro, deriva analogica y vibrato.
    FM      modulacion de frecuencia: pianos electricos, campanas, metales, marimbas.
    ruido() ruido filtrado con curvas: dash, explosiones, viento, vapor, chispas.
Todo devuelve estereo: un arreglo de numpy de (2, muestras).
"""
import math

import numpy as np

from herramientas.estudio.base import FS, njit, hertz, midi, curva, muestras


# ---------- Osciladores ----------

def _polyblep(t, dt):
    # La correccion de PolyBLEP alrededor del salto de la onda (t = fase de 0 a 1)
    correccion = np.zeros_like(t)
    antes = t < dt
    x = t[antes] / dt[antes]
    correccion[antes] = x + x - x * x - 1
    despues = t > 1 - dt
    x = (t[despues] - 1) / dt[despues]
    correccion[despues] = x * x + x + x + 1
    return correccion


def onda(forma, frecuencia, fase=0.0, ancho_pulso=0.5):
    # Una onda que sigue a 'frecuencia' (un arreglo: una frecuencia por muestra)
    t = (fase + np.cumsum(frecuencia) / FS) % 1.0
    dt = np.minimum(frecuencia / FS, 0.5)
    if forma == "sierra":
        return 2 * t - 1 - _polyblep(t, dt)
    if forma == "cuadrada":
        valor = np.where(t < ancho_pulso, 1.0, -1.0)
        return valor + _polyblep(t, dt) - _polyblep((t + 1 - ancho_pulso) % 1.0, dt)
    if forma == "triangulo":
        return 4 * np.abs(t - 0.5) - 1
    if forma == "seno":
        return np.sin(2 * np.pi * t)
    raise ValueError("forma de onda desconocida: " + forma)


# ---------- Envolventes ----------

def adsr(segundos_nota, ataque, decaimiento, sostenido, liberacion):
    # Volumen de 0 a 1: sube en 'ataque' s, cae hacia 'sostenido' (constante de tiempo
    # 'decaimiento') y, al soltar la nota, se apaga con constante 'liberacion'. Devuelve
    # la nota mas su cola (5 constantes de liberacion: -43 dB) y termina en 0 justo
    ataque = max(ataque, 0.001)
    n_nota = max(muestras(segundos_nota), 1)
    n_cola = muestras(5 * max(liberacion, 0.002))
    t = np.arange(n_nota + n_cola) / FS
    envolvente = np.where(t < ataque, t / ataque,
                          sostenido + (1 - sostenido) * np.exp(-(t - ataque) / max(decaimiento, 1e-4)))
    nivel = envolvente[n_nota - 1]
    envolvente[n_nota:] = nivel * np.exp(-(t[n_nota:] - t[n_nota - 1]) / max(liberacion, 1e-4))
    final = min(len(envolvente), muestras(0.003))
    envolvente[-final:] *= np.linspace(1, 0, final)        # nunca termina de golpe (sin "clic")
    return envolvente


# ---------- Filtro ----------

@njit(cache=True)
def _svf(senal, corte, resonancia, modo):
    # Filtro "state variable" con integradores trapezoidales (TPT, de Zavalishin): estable
    # aunque el corte cambie en cada muestra. modo 0 = pasa bajos, 1 = pasa banda, 2 = pasa altos
    salida = np.empty_like(senal)
    k = 2.0 - 2.0 * resonancia
    memoria_1 = 0.0
    memoria_2 = 0.0
    for n in range(senal.shape[0]):
        g = math.tan(math.pi * corte[n] / 44100.0)
        a1 = 1.0 / (1.0 + g * (g + k))
        a2 = g * a1
        a3 = g * a2
        v3 = senal[n] - memoria_2
        v1 = a1 * memoria_1 + a2 * v3
        v2 = memoria_2 + a2 * memoria_1 + a3 * v3
        memoria_1 = 2.0 * v1 - memoria_1
        memoria_2 = 2.0 * v2 - memoria_2
        if modo == 0:
            salida[n] = v2
        elif modo == 1:
            salida[n] = v1
        else:
            salida[n] = senal[n] - k * v1 - v2
    return salida


MODOS_FILTRO = {"bajos": 0, "banda": 1, "altos": 2}


def filtrar(senal, corte, resonancia=0.0, modo="bajos", polos=2):
    # Filtra una senal (mono o estereo). 'corte': Hz (un numero o un arreglo). polos=4 son dos
    # filtros seguidos: corte mas marcado (24 dB por octava, como un Moog)
    corte = np.clip(np.broadcast_to(np.asarray(corte, dtype=float), senal.shape[-1:]), 20.0, FS * 0.45)
    corte = np.ascontiguousarray(corte)
    resonancia = min(max(resonancia, 0.0), 0.97)
    if senal.ndim == 2:
        return np.array([filtrar(canal, corte, resonancia, modo, polos) for canal in senal])
    salida = _svf(np.ascontiguousarray(senal, dtype=float), corte, resonancia, MODOS_FILTRO[modo])
    if polos == 4:
        salida = _svf(salida, corte, resonancia * 0.5, MODOS_FILTRO[modo])
    return salida


def panear(mono, paneo):
    # Mono a estereo con "potencia constante": -1 izquierda, 0 centro, 1 derecha
    angulo = (paneo + 1) * math.pi / 4
    return np.array([mono * math.cos(angulo), mono * math.sin(angulo)]) * math.sqrt(2)


def _frecuencias(nota, cuantas):
    # La frecuencia de cada muestra: una nota fija, o [(segundo, nota o Hz), ...] (un glissando)
    if isinstance(nota, (list, tuple)):
        puntos = [(t, hertz(valor) if isinstance(valor, str) else float(valor)) for t, valor in nota]
        return curva(puntos, cuantas, exponencial=True)
    return np.full(cuantas, hertz(nota))


def _modular_altura(frecuencias, vibrato, deriva, azar):
    # Vibrato (velocidad Hz, semitonos, desde que segundo) y deriva analogica: dos ondas muy
    # lentas que mueven la afinacion unos centesimos, como un oscilador de verdad que "respira"
    t = np.arange(len(frecuencias)) / FS
    semitonos = np.zeros(len(frecuencias))
    if vibrato and vibrato[1]:
        velocidad, profundidad, desde = vibrato
        entrada = np.clip((t - desde) / 0.25, 0, 1)
        semitonos += profundidad * entrada * np.sin(2 * np.pi * velocidad * t)
    if deriva:
        for _ in range(2):
            semitonos += deriva / 100 * np.sin(2 * np.pi * azar.uniform(0.15, 0.7) * t + azar.uniform(0, 6.3))
    return frecuencias * 2 ** (semitonos / 12)


# ---------- Instrumentos ----------

class Sinte:
    # Un sintetizador sustractivo. Ver los presets en instrumentos.py
    def __init__(self, osciladores=(("sierra", 1.0, 0),), voces=1, desafinacion=0.0, ancho=0.0, sub=0.0,
                 ruido=0.0, ancho_pulso=0.5, corte=2000.0, resonancia=0.1, env_filtro=0.0, seguimiento=0.5,
                 polos=2, amp=(0.005, 0.3, 0.7, 0.2), filtro_adsr=(0.005, 0.3, 0.0, 0.2), vibrato=None,
                 deriva=2.0, saturacion=0.0, volumen=1.0):
        self.osciladores = osciladores      # [(forma, nivel, semitonos)]: se suman
        self.voces = voces                  # copias desafinadas (unisono): el "ancho" de un pad
        self.desafinacion = desafinacion    # centesimos entre la voz mas grave y la mas aguda / 2
        self.ancho = ancho                  # 0 = todas al centro, 1 = abiertas de lado a lado
        self.sub = sub                      # un seno una octava abajo (peso en los graves)
        self.ruido = ruido                  # un poco de soplido (aire en un pad, ataque de un pluck)
        self.ancho_pulso = ancho_pulso
        self.corte = corte                  # Hz del filtro en reposo
        self.resonancia = resonancia        # 0 a ~0.9: el "pico" del filtro
        self.env_filtro = env_filtro        # cuantas octavas se abre el filtro con su envolvente
        self.seguimiento = seguimiento      # 1 = el filtro sube con la nota (notas agudas igual de brillantes)
        self.polos = polos
        self.amp = amp                      # (ataque, decaimiento, sostenido, liberacion) del volumen
        self.filtro_adsr = filtro_adsr      # la del filtro
        self.vibrato = vibrato              # (velocidad, semitonos, desde) o None
        self.deriva = deriva                # centesimos de "respiracion" analogica
        self.saturacion = saturacion        # calidez: redondea los picos (0 = nada)
        self.volumen = volumen

    def tocar(self, nota, segundos, fuerza=1.0, azar=None):
        azar = azar or np.random.default_rng(0)
        envolvente = adsr(segundos, *self.amp)
        cuantas = len(envolvente)
        frecuencias = _modular_altura(_frecuencias(nota, cuantas), self.vibrato, self.deriva, azar)
        estereo = np.zeros((2, cuantas))
        for voz in range(self.voces):
            lugar = voz / (self.voces - 1) * 2 - 1 if self.voces > 1 else 0.0   # -1 a 1
            afinacion = 2 ** (self.desafinacion * lugar / 1200)
            mono = np.zeros(cuantas)
            for forma, nivel, semitonos in self.osciladores:
                mono += nivel * onda(forma, frecuencias * afinacion * 2 ** (semitonos / 12), azar.uniform(0, 1),
                                     self.ancho_pulso)
            estereo += panear(mono, lugar * self.ancho)
        estereo /= math.sqrt(self.voces)
        if self.sub:
            estereo += panear(self.sub * onda("seno", frecuencias / 2), 0)
        if self.ruido:
            estereo += self.ruido * azar.uniform(-1, 1, (2, cuantas))
        # El filtro: se abre con su envolvente (mas con mas fuerza) y sigue a la nota
        abrir = adsr(segundos, *self.filtro_adsr)
        abrir = np.pad(abrir, (0, max(0, cuantas - len(abrir))))[:cuantas]
        corte = (self.corte * 2 ** (self.env_filtro * abrir * (0.6 + 0.4 * fuerza))
                 * (frecuencias / hertz("C4")) ** self.seguimiento)
        estereo = filtrar(estereo, corte, self.resonancia, "bajos", self.polos)
        estereo *= envolvente * (fuerza ** 1.3) * self.volumen
        if self.saturacion:
            estereo = np.tanh(estereo * (1 + 3 * self.saturacion)) / (1 + 3 * self.saturacion) ** 0.5
        return estereo


class FM:
    # Modulacion de frecuencia: un seno (la portadora) cuya fase empujan otros senos (los
    # moduladores). Con relaciones enteras suena armonico (piano electrico, organo); con
    # relaciones raras, inarmonico (campanas, metales). El indice (cuanto empujan) cae con
    # el tiempo: por eso el ataque es brillante y despues se vuelve redondo
    def __init__(self, moduladores=((1.0, 1.5, 0.5),), amp=(0.002, 1.0, 0.0, 0.3), voces=1, desafinacion=0.0,
                 ancho=0.0, vibrato=None, deriva=1.0, corte=12000.0, volumen=1.0):
        self.moduladores = moduladores      # [(relacion de frecuencia, indice, cuanto tarda en caer el indice)]
        self.amp = amp
        self.voces = voces
        self.desafinacion = desafinacion
        self.ancho = ancho
        self.vibrato = vibrato
        self.deriva = deriva
        self.corte = corte                  # un pasa bajos suave al final (saca lo aspero)
        self.volumen = volumen

    def tocar(self, nota, segundos, fuerza=1.0, azar=None):
        azar = azar or np.random.default_rng(0)
        envolvente = adsr(segundos, *self.amp)
        cuantas = len(envolvente)
        t = np.arange(cuantas) / FS
        frecuencias = _modular_altura(_frecuencias(nota, cuantas), self.vibrato, self.deriva, azar)
        estereo = np.zeros((2, cuantas))
        for voz in range(self.voces):
            lugar = voz / (self.voces - 1) * 2 - 1 if self.voces > 1 else 0.0
            portadora = frecuencias * 2 ** (self.desafinacion * lugar / 1200)
            empuje = np.zeros(cuantas)
            for relacion, indice, caida in self.moduladores:
                fase = np.cumsum(portadora * relacion) / FS
                empuje += indice * (0.4 + 0.6 * fuerza) * np.exp(-t / caida) * np.sin(2 * np.pi * fase)
            mono = np.sin(2 * np.pi * np.cumsum(portadora) / FS + empuje)
            estereo += panear(mono, lugar * self.ancho)
        estereo /= math.sqrt(self.voces)
        if self.corte < FS * 0.45:
            estereo = filtrar(estereo, self.corte, 0.0)
        return estereo * envolvente * (fuerza ** 1.3) * self.volumen


def ruido(segundos, filtro=((0, 8000),), resonancia=0.0, modo="bajos", polos=2, forma=None, chasquidos=0,
          ancho=1.0, tremolo=None, azar=None):
    # Ruido filtrado (sin altura: nunca desafina):
    # - filtro: curva del corte en Hz [(segundo, hz)]; modo "bajos", "banda" o "altos"
    # - forma: curva del volumen (0 a 1); por defecto, golpe y caida pareja
    # - chasquidos: "crac" por segundo en vez de un soplido continuo (brasas, chispas)
    # - ancho: 0 = mono, 1 = cada lado su propio ruido (se siente amplio)
    # - tremolo: (desde_hz, hasta_hz, profundidad): el volumen tiembla, cada vez mas rapido
    azar = azar or np.random.default_rng(0)
    cuantas = max(muestras(segundos), 1)
    centro = azar.uniform(-1, 1, cuantas)
    estereo = np.array([centro * (1 - ancho) + azar.uniform(-1, 1, cuantas) * ancho for _ in range(2)])
    if chasquidos:
        golpes = azar.random(cuantas) < chasquidos / FS
        compuerta = np.convolve(golpes.astype(float), np.exp(-np.arange(muestras(0.006)) / muestras(0.0015)))
        estereo *= np.minimum(compuerta[:cuantas], 1.0)
    corte = curva([(t, float(hz)) for t, hz in filtro], cuantas, exponencial=True)
    estereo = filtrar(estereo, corte, resonancia, modo, polos)
    forma = forma or [(0, 0), (0.002, 1), (segundos, 0)]
    volumen = curva(forma, cuantas)
    if tremolo:
        volumen = volumen * temblor(cuantas, *tremolo)
    return estereo * volumen


def temblor(cuantas, desde, hasta, profundidad):
    # 1 - profundidad * (onda de 0 a 1) que va de 'desde' a 'hasta' Hz: el volumen tiembla
    velocidad = np.linspace(desde, hasta, cuantas)
    return 1 - profundidad * (0.5 + 0.5 * np.sin(2 * np.pi * np.cumsum(velocidad) / FS))
