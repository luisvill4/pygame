"""
Los procesos de la consola: lo que convierte sonidos sueltos en una mezcla con calidad.

Todos reciben y devuelven estereo (2, muestras). 'vuelta' = True cuando la senal es un tema
que se repite: entonces todo "da la vuelta" (la cola de la reverb y los ecos del final
suenan al principio, y los procesos con memoria pasan dos veces) y el loop no tiene costura.

- reverb: convolucion con una "respuesta al impulso" generada (ruido que se apaga y se
  oscurece, distinto en cada lado): una sala amplia y suave, sin el metalico de las
  reverbs baratas.
- delay: ecos ping-pong (izquierda, derecha...) que se van oscureciendo.
- chorus: dos copias que se desafinan un poco: ensancha y engorda.
- ecualizador: en el dominio de la frecuencia (FFT), sin cambiar la fase.
- compresor: emparejar el volumen ("pegamento" de la mezcla).
- limitador: que nada pase del techo (-1 dB), mirando un poquito adelante.
- loudness: volumen percibido en LUFS (el estandar de streaming y de los juegos).
"""
import math

import numpy as np

from herramientas.estudio.base import FS, njit, db, muestras
from herramientas.estudio.sintesis import filtrar


# ---------- Reverb ----------

_respuestas = {}        # (segundos, brillo, prepausa, semilla) -> respuesta al impulso


def respuesta_sala(segundos=2.2, brillo=0.5, prepausa=0.02, semilla=7):
    # La "huella" de una sala: ruido distinto en cada lado (amplitud) que se apaga en
    # 'segundos' (-60 dB) y se va oscureciendo (como el aire y las paredes se comen los agudos)
    clave = (segundos, brillo, prepausa, semilla)
    if clave not in _respuestas:
        azar = np.random.default_rng(semilla)
        cuantas = muestras(segundos)
        t = np.arange(cuantas) / FS
        apagarse = np.exp(-6.9 * t / segundos)
        corte = 1500 + 9000 * brillo * np.exp(-t / (segundos / 3))
        lados = filtrar(azar.uniform(-1, 1, (2, cuantas)), corte) * apagarse
        lados[:, :muestras(0.005)] *= np.linspace(0, 1, muestras(0.005))   # entra suave
        lados = np.pad(lados, ((0, 0), (muestras(prepausa), 0)))
        _respuestas[clave] = lados / np.sqrt(np.sum(lados ** 2) / 2)
    return _respuestas[clave]


def convolucionar(senal, respuesta, vuelta):
    # Convolucion por FFT. Con 'vuelta' es circular: lo que se pasa del final cae al principio
    largo = senal.shape[1]
    tamano = largo if vuelta else largo + respuesta.shape[1] - 1
    if vuelta and respuesta.shape[1] > largo:
        # una respuesta mas larga que el tema se "dobla" sobre si misma
        doblada = np.zeros((2, largo))
        for desde in range(0, respuesta.shape[1], largo):
            pedazo = respuesta[:, desde:desde + largo]
            doblada[:, :pedazo.shape[1]] += pedazo
        respuesta = doblada
    n = 1 << (tamano - 1).bit_length()
    if vuelta:
        n = largo
    espectro = np.fft.rfft(senal, n) * np.fft.rfft(respuesta, n)
    salida = np.fft.irfft(espectro, n)
    return salida[:, :tamano]


def reverb(senal, segundos=2.2, brillo=0.5, prepausa=0.02, vuelta=False):
    # Solo lo "mojado" (la reverb sola): se usa en un bus de envio
    return convolucionar(senal, respuesta_sala(segundos, brillo, prepausa), vuelta)


# ---------- Delay ----------

@njit(cache=True)
def _ping_pong(izquierda, derecha, retraso, realimentacion, oscuridad, pasadas):
    largo = izquierda.shape[0]
    salida_i = np.zeros(largo)
    salida_d = np.zeros(largo)
    linea_i = np.zeros(retraso)
    linea_d = np.zeros(retraso)
    filtro_i = 0.0
    filtro_d = 0.0
    posicion = 0
    for pasada in range(pasadas):
        for n in range(largo):
            eco_i = linea_i[posicion]
            eco_d = linea_d[posicion]
            filtro_i += (1.0 - oscuridad) * (eco_i - filtro_i)
            filtro_d += (1.0 - oscuridad) * (eco_d - filtro_d)
            # cruzado: lo que sale por un lado vuelve a entrar por el otro
            linea_i[posicion] = 0.5 * (izquierda[n] + derecha[n]) + realimentacion * filtro_d
            linea_d[posicion] = realimentacion * filtro_i
            posicion = (posicion + 1) % retraso
            salida_i[n] = filtro_i
            salida_d[n] = filtro_d
    return salida_i, salida_d


def delay(senal, segundos, realimentacion=0.35, oscuridad=0.5, vuelta=False):
    # Solo los ecos. 'oscuridad' 0 a 1: cuanto se apaga el brillo en cada vuelta
    if not vuelta:
        cola = muestras(segundos) * 12
        senal = np.pad(senal, ((0, 0), (0, cola)))
    izquierda, derecha = _ping_pong(np.ascontiguousarray(senal[0]), np.ascontiguousarray(senal[1]),
                                    max(muestras(segundos), 1), realimentacion, oscuridad, 2 if vuelta else 1)
    return np.array([izquierda, derecha])


# ---------- Chorus ----------

def chorus(senal, profundidad=0.004, velocidad=0.6, mezcla=0.5, vuelta=False):
    # Cada lado escucha una copia de si mismo un poco atrasada, y el atraso oscila: la
    # afinacion se mueve apenas y el sonido se abre
    largo = senal.shape[1]
    indices = np.arange(largo)
    salida = senal.copy()
    for lado in range(2):
        fase = 0 if lado == 0 else math.pi / 2
        atraso = (0.008 + profundidad * (0.5 + 0.5 * np.sin(2 * np.pi * velocidad * indices / FS + fase))) * FS
        desde = indices - atraso
        if vuelta:
            copia = np.interp(desde % largo, indices, senal[lado], period=largo)
        else:
            copia = np.interp(desde, indices, senal[lado], left=0.0)
        salida[lado] = senal[lado] * (1 - mezcla * 0.5) + copia * mezcla * 0.7
    return salida


# ---------- Color ----------

def saturar(senal, cuanto):
    # Saturacion suave (como una cinta o un valvular): redondea los picos y agrega
    # armonicos graves que dan "cuerpo". 0 = nada
    if cuanto <= 0:
        return senal
    empuje = 1 + 4 * cuanto
    return np.tanh(senal * empuje) / math.tanh(empuje) * (1 / max(1, empuje ** 0.3))


def ecualizar(senal, bandas, vuelta=True):
    # Ecualizador en el dominio de la frecuencia (sin cambiar la fase). Como la FFT es
    # circular, lo que el filtro "adelanta" cae al final: en un tema que da la vuelta esta
    # bien, pero en un efecto (vuelta=False) se rellena con silencio y despues se saca.
    # bandas = lista de:
    #   ("corte_graves", hz)          saca lo de abajo (retumbe que no se oye y ensucia)
    #   ("corte_agudos", hz)          saca lo de arriba (lo chillon)
    #   ("graves", hz, decibeles)     estante: sube o baja todo lo de abajo de hz
    #   ("agudos", hz, decibeles)     estante: lo de arriba
    #   ("campana", hz, decibeles, q) una campana alrededor de hz (q alto = angosta)
    largo = senal.shape[1]
    frecuencias = np.fft.rfftfreq(largo, 1 / FS)
    ganancia = np.ones_like(frecuencias)
    f = np.maximum(frecuencias, 1.0)
    for banda in bandas:
        tipo, hz = banda[0], banda[1]
        if tipo == "corte_graves":
            ganancia *= 1 / np.sqrt(1 + (hz / f) ** 4)
        elif tipo == "corte_agudos":
            ganancia *= 1 / np.sqrt(1 + (f / hz) ** 4)
        elif tipo == "graves":
            ganancia *= 1 + (db(banda[2]) - 1) / (1 + (f / hz) ** 2)
        elif tipo == "agudos":
            ganancia *= 1 + (db(banda[2]) - 1) / (1 + (hz / f) ** 2)
        elif tipo == "campana":
            q = banda[3] if len(banda) > 3 else 1.0
            ganancia *= 1 + (db(banda[2]) - 1) * np.exp(-(np.log2(f / hz) * q * 1.5) ** 2)
    if vuelta:
        return np.fft.irfft(np.fft.rfft(senal) * ganancia, largo)
    relleno = muestras(1.0)
    con_silencio = np.pad(senal, ((0, 0), (relleno, relleno)))
    return ecualizar(con_silencio, bandas, vuelta=True)[:, relleno:relleno + largo]


def ensanchar(senal, cuanto):
    # Mas o menos estereo: separa el "medio" (lo comun) del "costado" (la diferencia)
    medio = (senal[0] + senal[1]) / 2
    costado = (senal[0] - senal[1]) / 2 * cuanto
    return np.array([medio + costado, medio - costado])


# ---------- Dinamica ----------

@njit(cache=True)
def _envolvente(nivel, ataque, liberacion, pasadas):
    # Sigue al nivel: sube rapido (ataque) y baja lento (liberacion), en coeficientes por muestra
    salida = np.empty_like(nivel)
    actual = 0.0
    for pasada in range(pasadas):
        for n in range(nivel.shape[0]):
            coeficiente = ataque if nivel[n] > actual else liberacion
            actual += (1.0 - coeficiente) * (nivel[n] - actual)
            salida[n] = actual
    return salida


def _coeficiente(segundos):
    return math.exp(-1.0 / max(segundos * FS, 1.0))


def comprimir(senal, umbral_db=-18.0, relacion=3.0, ataque=0.01, liberacion=0.15, rodilla=6.0, vuelta=False):
    # Compresor (los dos lados juntos): lo que pasa del umbral se achica 'relacion' veces.
    # Devuelve la senal comprimida (sin compensar: eso lo hace el master)
    nivel = np.maximum(np.abs(senal[0]), np.abs(senal[1]))
    seguido = _envolvente(np.ascontiguousarray(nivel), _coeficiente(ataque), _coeficiente(liberacion),
                          2 if vuelta else 1)
    nivel_db = 20 * np.log10(np.maximum(seguido, 1e-9))
    sobra = nivel_db - umbral_db
    # rodilla suave: la compresion entra de a poco alrededor del umbral
    sobra = np.where(sobra < -rodilla / 2, 0.0,
                     np.where(sobra > rodilla / 2, sobra, (sobra + rodilla / 2) ** 2 / (2 * rodilla)))
    reduccion = sobra * (1 - 1 / relacion)
    return senal * 10 ** (-reduccion / 20)


@njit(cache=True)
def _maximo_adelante(nivel, ventana):
    # El maximo de las proximas 'ventana' muestras (para que el limitador llegue a tiempo)
    largo = nivel.shape[0]
    salida = np.empty_like(nivel)
    for n in range(largo):
        maximo = 0.0
        for k in range(n, min(n + ventana, largo)):
            if nivel[k] > maximo:
                maximo = nivel[k]
        salida[n] = maximo
    return salida


def limitar(senal, techo_db=-1.0, liberacion=0.08, vuelta=False):
    # Limitador: nada pasa de 'techo_db'. Mira 3 ms adelante y vuelve suave
    techo = db(techo_db)
    nivel = np.maximum(np.abs(senal[0]), np.abs(senal[1]))
    adelante = _maximo_adelante(np.ascontiguousarray(nivel), muestras(0.003))
    objetivo = np.minimum(1.0, techo / np.maximum(adelante, 1e-9))
    # la ganancia baja enseguida y sube de a poco (se sigue a la "reduccion")
    reduccion = _envolvente(np.ascontiguousarray(1 - objetivo), _coeficiente(0.0005), _coeficiente(liberacion),
                            2 if vuelta else 1)
    salida = senal * np.minimum(1 - reduccion, objetivo + 0.0)
    return np.clip(salida, -techo, techo)


def bombeo(cuantas, golpes, profundidad=0.6, liberacion=0.18, vuelta=False):
    # "Sidechain": el volumen baja en cada golpe de bombo y vuelve en 'liberacion' segundos.
    # Es el "bombeo" del synthwave y el house: deja lugar al bombo y hace respirar la mezcla
    ganancia = np.ones(cuantas)
    largo = muestras(liberacion * 3)
    t = np.arange(largo) / FS
    hueco = profundidad * np.exp(-((t / liberacion) ** 1.6))
    hueco[:muestras(0.004)] *= np.linspace(0, 1, muestras(0.004))        # sin clic al bajar
    for golpe in golpes:
        indices = np.arange(golpe, golpe + largo)
        if vuelta:
            indices %= cuantas
        else:
            indices = indices[indices < cuantas]
        ganancia[indices] = np.minimum(ganancia[indices], 1 - hueco[:len(indices)])
    return ganancia


# ---------- Medir ----------

def a_db_pico(senal):
    # El pico de la senal en dB (0 = el maximo posible)
    return 20 * math.log10(max(float(np.max(np.abs(senal))), 1e-12))


def loudness(senal):
    # Volumen percibido aproximado en LUFS (ITU BS.1770): pondera las frecuencias como el
    # oido (menos graves, un poco mas de agudos), promedia en bloques de 400 ms y descarta
    # los silencios. La musica de juegos y streaming esta entre -14 y -18 LUFS
    pesada = ecualizar(senal, [("corte_graves", 60), ("agudos", 1700, 4.0)])
    bloque, paso = muestras(0.4), muestras(0.1)
    potencias = []
    for desde in range(0, max(pesada.shape[1] - bloque, 0) + 1, paso):
        trozo = pesada[:, desde:desde + bloque]
        potencias.append(np.mean(trozo ** 2) * 2)
    potencias = np.array(potencias) if potencias else np.array([np.mean(pesada ** 2) * 2])
    sonoras = potencias[potencias > 10 ** ((-70 + 0.691) / 10)]
    if len(sonoras) == 0:
        return -70.0
    relativo = 10 * math.log10(np.mean(sonoras)) - 10
    sonoras = sonoras[10 * np.log10(sonoras) > relativo]
    return -0.691 + 10 * math.log10(np.mean(sonoras))


def loudness_maximo(senal):
    # El bloque de 400 ms mas fuerte (para efectos cortos: el "momentary" maximo)
    pesada = ecualizar(senal, [("corte_graves", 60), ("agudos", 1700, 4.0)])
    bloque = min(muestras(0.4), pesada.shape[1])
    mejor = 1e-12
    for desde in range(0, max(pesada.shape[1] - bloque, 0) + 1, muestras(0.05)):
        mejor = max(mejor, np.mean(pesada[:, desde:desde + bloque] ** 2) * 2)
    return -0.691 + 10 * math.log10(mejor)


def centroide(senal):
    # El "centro de gravedad" del espectro, en Hz: mas alto = mas brillante (o chillon)
    espectro = np.abs(np.fft.rfft(senal[0] + senal[1]))
    frecuencias = np.fft.rfftfreq(senal.shape[1], 1 / FS)
    return float(np.sum(espectro * frecuencias) / max(np.sum(espectro), 1e-12))


def correlacion(senal):
    # 1 = mono, 0 = muy abierto, negativo = problemas en mono. Una mezcla sana: 0.3 a 0.9
    izquierda, derecha = senal[0] - senal[0].mean(), senal[1] - senal[1].mean()
    return float(np.sum(izquierda * derecha) / max(math.sqrt(np.sum(izquierda ** 2) * np.sum(derecha ** 2)), 1e-12))
