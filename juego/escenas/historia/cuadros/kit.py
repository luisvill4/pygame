"""
El kit de los cuadros: las piezas con que se arma cada dibujo (todo en la grilla de 2 px).

Cielo:      estrellas, galaxia, nube (la Marea), frente_de_la_marea, nebulosa, niebla,
            agujero_negro, planeta (con luz y sombra, guardado en cache)
Cosas:      alondra (el sprite de la nave, con lo que tenga puesto), moneda, enemigo, jefe,
            estacion (la Umbral), errante, capsula, retrato, reloj
Señales:    osciloscopio (el compas con su ritmo de verdad), ondas (de radio), glifo, linea
Tiempo:     titila (un parpadeo que respeta DESTELLOS REDUCIDOS), vaiven, avance
Texto:      rotulo (con contorno: se lee sobre cualquier dibujo)

Reglas: nada parpadea mas rapido que PARPADEO_MINIMO (3 veces por segundo como mucho) y no hay
destellos de todo el escenario: lo que tiene que "brillar" lo hace con dibujo.halo.
"""
import math
import random

import pygame

from juego import dibujo, interfaz, nave, recursos, accesibilidad
from juego.config import (BLANCO, ROJO, AMARILLO, CIAN, NARANJA, VIOLETA, CONTORNO, PARPADEO_MINIMO,
                          MS_POR_FRAME)
from juego.dibujo import texto, CHICA
from juego.historia.personajes import dibujar_retrato, RETRATOS
from juego.historia.glifos import ritmo, dibujar_glifo, ancho_glifo
from juego.escenas.historia.cuadros.base import NOCHE

g = dibujo.en_grilla            # (se usa en cada linea: corto a proposito)
mezclar = interfaz.mezclar

# Los colores de las dos galaxias: del centro (brillante) al borde (apagado)
NUESTRA = [BLANCO, (190, 225, 255), (110, 170, 255), (50, 80, 170)]
MAREA = [(255, 210, 200), ROJO, (190, 30, 90), (100, 20, 50)]
SUYA = [(255, 240, 255), (220, 180, 255), VIOLETA, (80, 50, 140)]     # la galaxia de El Ultimo

ESTACION = ["...X...", "..XXX..", "X.XXX.X", "XXXXXXX", "X.XXX.X", "..XXX..", "...X..."]
ERRANTE = ["..XX......",
           "..XXX.....",
           "XXXXXXXX..",
           "XXXXXXXXXX",
           "XXXXXXXX..",
           "..XXX.....",
           "..XX......"]

# La silueta de El Ultimo (su retrato, de un solo color): se ve antes de que se lo conozca
RETRATO_ULTIMO_SILUETA = ["".join("." if letra == "." else "X" for letra in renglon)
                          for renglon in RETRATOS["ultimo"]["dibujo"]]

CAPSULA = ["..XX..", ".XXXX.", "XXooXX", "XXooXX", "XXXXXX", ".X..X."]


# ---------- El tiempo (todo en pasos de la escena) ----------

def titila(t, periodo=40):
    # Prendido y apagado cada medio periodo. Con DESTELLOS REDUCIDOS nunca mas rapido que
    # PARPADEO_MINIMO (el mismo limite que dibujo.parpadeo)
    if accesibilidad.destellos_reducidos():
        periodo = max(periodo, 2 * PARPADEO_MINIMO / MS_POR_FRAME)
    return int(t // (periodo / 2)) % 2 == 0


def vaiven(t, periodo, alto):
    # Un ir y venir suave (para flotar): siempre un numero par
    return g(math.sin(t * math.tau / periodo) * alto)


def avance(t, desde, dura):
    # De 0 a 1 entre el paso 'desde' y 'desde + dura', arrancando y frenando suave
    x = min(1.0, max(0.0, (t - desde) / dura))
    return x * x * (3 - 2 * x)


# ---------- Piezas sueltas ----------

def punto(pantalla, x, y, color, lado=2):
    pantalla.fill(color, (g(x), g(y), lado, lado))


def linea(pantalla, x1, y1, x2, y2, color, lado=2, hueco=0, hasta=1.0, corrimiento=0):
    # Una linea de cuadraditos en la grilla. 'hueco' > 0 la hace punteada (y 'corrimiento'
    # hace que los puntos caminen); 'hasta' dibuja solo una parte (para que se vaya trazando)
    largo = max(1, math.hypot(x2 - x1, y2 - y1))
    pasos = int(largo / 2 * hasta)
    for i in range(pasos):
        if hueco and (i + corrimiento) % (hueco * 2) >= hueco:
            continue
        f = i * 2 / largo
        pantalla.fill(color, (g(x1 + (x2 - x1) * f), g(y1 + (y2 - y1) * f), lado, lado))


def rotulo(pantalla, mensaje, x, y, color, alinear="centro"):
    texto(pantalla, mensaje, CHICA, color, g(x), g(y), alinear=alinear, contorno=CONTORNO)


_grandes = {}


def texto_grande(pantalla, mensaje, color, x, y, escala=2, alinear="centro"):
    # Un texto CHICA agrandado (x2 = 32 px de alto, x3 = 48, x4 = 64), con contorno. Asi cada
    # pixel de la letra mide 4, 6 u 8 px y calza en la grilla (en MEDIA o GRANDE la fuente tiene
    # pixeles de 3 y 5 px: se corria medio pixel de arte)
    clave = (mensaje, tuple(color), escala)
    if clave not in _grandes:
        if len(_grandes) > 200:
            _grandes.clear()
        imagen, borde, letras = dibujo._imagen_texto(mensaje, CHICA, color, None, CONTORNO)
        _grandes[clave] = (pygame.transform.scale(imagen, (imagen.get_width() * escala, imagen.get_height() * escala)),
                           borde * escala, letras.width * escala, letras.height * escala)
    imagen, borde, ancho, alto = _grandes[clave]
    izquierda = {"centro": x - ancho / 2, "izquierda": x, "derecha": x - ancho}[alinear]
    pantalla.blit(imagen, (g(izquierda) - borde, g(y - alto / 2) - borde))


def disco(pantalla, cx, cy, rx, color, ry=None):
    # Un circulo (o un ovalo) lleno, en la grilla: renglones de 2 px de alto y anchos pares
    ry = rx if ry is None else ry
    cx, cy = g(cx), g(cy)
    recorte = pantalla.get_clip()
    for y in range(max(-g(ry), g(recorte.top - cy) - 2), min(g(ry), recorte.bottom - cy + 2), 2):    # (solo lo que se ve)
        mitad = g(rx * math.sqrt(max(0.0, 1 - ((y + 1) / ry) ** 2)))
        if mitad > 0:
            pantalla.fill(color, (cx - mitad, cy + y, mitad * 2, 2))


def disco_tramado(pantalla, cx, cy, rx, color, ry=None, fase=0):
    # Un ovalo de cuadros alternados (un velo de gas o de luz que deja ver lo de atras)
    ry = rx if ry is None else ry
    cx, cy = g(cx), g(cy)
    for y in range(-g(ry), g(ry), 2):
        mitad = g(rx * math.sqrt(max(0.0, 1 - ((y + 1) / ry) ** 2)))
        inicio = cx - mitad + ((y // 2 + fase) % 2) * 2
        for x in range(inicio, cx + mitad, 4):
            pantalla.fill(color, (x, cy + y, 2, 2))


def tramado(pantalla, rect, color, fase=0):
    # Un velo de cuadros alternados (como las sombras del pixel art): no tapa del todo
    rect = pygame.Rect(g(rect.left), g(rect.top), g(rect.width), g(rect.height))
    for y in range(rect.top, rect.bottom, 2):
        inicio = rect.left + ((y // 2 + fase) % 2) * 2
        for x in range(inicio, rect.right, 4):
            pantalla.fill(color, (x, y, 2, 2))


# ---------- El cielo ----------

def estrellas(pantalla, zona, semilla, cuantas, deriva=0.0, t=0):
    # Estrellas fijas (la misma semilla, el mismo cielo). Con 'deriva' se corren hacia la
    # izquierda (la nave avanza); las mas brillantes, mas rapido (paralaje)
    azar = random.Random(semilla)
    for _ in range(cuantas):
        x0 = azar.randint(0, zona.width)
        y = g(azar.randint(zona.top, zona.bottom))
        gris = azar.choice((50, 80, 120, 170))
        x = zona.left + (x0 - t * deriva * gris / 120) % zona.width
        pantalla.fill((gris, gris, gris + 30), (g(x), y, 2, 2))


def estelas(pantalla, zona, semilla, cuantas, t, rapidez=6.0):
    # El viaje: rayas que pasan hacia la izquierda (mas largas las de adelante)
    azar = random.Random(semilla)
    for _ in range(cuantas):
        y = g(azar.randint(zona.top + 4, zona.bottom - 4))
        cerca = azar.random()
        largo = g(8 + cerca * 60)
        x = zona.right - (azar.randint(0, zona.width * 2) + t * rapidez * (0.4 + cerca)) % (zona.width + largo * 2)
        gris = int(70 + cerca * 150)
        pantalla.fill((gris, gris, min(255, gris + 30)), (g(x), y, largo, 2))


def galaxia(pantalla, cx, cy, radio, giro, colores, semilla, puntos=700, estirar=0.0):
    # Una espiral de dos brazos, inclinada (se ve aplastada): del centro brillante al borde apagado.
    # Los brazos tienen ancho y entre ellos hay polvo mas oscuro. 'estirar' (0 a 1) la deforma
    # hacia la derecha: la Marea tirando de ella
    azar = random.Random(semilla)
    for i in range(puntos):
        fraccion = azar.random() ** 0.8
        if i % 5 == 0:          # el polvo del disco, entre los brazos
            angulo, color = azar.uniform(0, math.tau), colores[-1]
        else:
            angulo = giro + fraccion * 3.8 + (i % 2) * math.pi + azar.gauss(0, 0.22)
            color = colores[min(len(colores) - 1, int(fraccion * len(colores)))]
        distancia = radio * fraccion
        x = cx + math.cos(angulo) * distancia
        y = cy + math.sin(angulo) * distancia * 0.5
        if estirar:
            x += (x - cx + radio) * estirar * fraccion * 0.9
            y += math.sin(angulo * 2) * estirar * fraccion * radio * 0.2
        pantalla.fill(color, (g(x), g(y), 2, 2))
    pantalla.fill(colores[1], (g(cx) - 6, g(cy) - 4, 12, 8))     # el nucleo
    pantalla.fill(colores[0], (g(cx) - 4, g(cy) - 2, 8, 4))
    dibujo.halo(pantalla, cx, cy, radio // 4, colores[1])


def nube(pantalla, cx, cy, radio, colores, semilla, puntos=220):
    # Una galaxia sin forma (la Marea): una nube con una cola que se estira hacia atras
    azar = random.Random(semilla)
    for i in range(puntos):
        if i % 4 == 0:      # la cola
            distancia = azar.uniform(0, radio * 1.6)
            x, y = cx + radio * 0.4 + distancia, cy + azar.gauss(0, 4 + distancia * 0.12)
            fraccion = min(1.0, 0.5 + distancia / (radio * 3))
        else:
            distancia = abs(azar.gauss(0, radio * 0.45))
            angulo = azar.uniform(0, math.tau)
            x, y = cx + math.cos(angulo) * distancia, cy + math.sin(angulo) * distancia * 0.7
            fraccion = min(1.0, distancia / radio)
        color = colores[min(len(colores) - 1, int(fraccion * len(colores)))]
        pantalla.fill(color, (g(x), g(y), 2, 2))
    dibujo.halo(pantalla, cx, cy, radio // 2, colores[1])


def frente_de_la_marea(pantalla, zona, borde, t, hacia="izquierda"):
    # El frente rojo que avanza (como en el mapa): una orilla que ondula y rayas detras.
    # 'hacia' es para donde avanza; 'borde' es la x de la orilla
    for y in range(zona.top, zona.bottom, 2):
        onda = g(math.sin(y / 19 + t / 30) * 6)
        x = g(borde) + onda
        if hacia == "izquierda":        # la Marea viene de la derecha
            if (y // 2) % 2 == 0:
                pantalla.fill((50, 8, 26), (x, y, zona.right - x, 2))
            pantalla.fill(ROJO, (x, y, 4, 2))
        else:                           # viene de la izquierda
            if (y // 2) % 2 == 0:
                pantalla.fill((50, 8, 26), (zona.left, y, x - zona.left, 2))
            pantalla.fill(ROJO, (x - 4, y, 4, 2))


def nebulosa(pantalla, zona, semilla, colores, t=0, puntos=900, deriva=0.0):
    # Nubes de gas: grumos de puntos (del borde oscuro al centro claro) que se corren despacio
    azar = random.Random(semilla)
    grumos = [(azar.randint(0, zona.width), azar.randint(zona.top, zona.bottom), azar.randint(30, 90))
              for _ in range(7)]
    for i, (gx, gy, radio) in enumerate(grumos):      # el cuerpo del gas: ovalos tramados
        x = zona.left + (gx - t * deriva) % (zona.width + 200) - 100
        disco_tramado(pantalla, x, gy, radio * 1.3, colores[-1], radio * 0.75, fase=i)
        disco_tramado(pantalla, x, gy, radio * 0.8, colores[-2], radio * 0.45, fase=i + 1)
    for i in range(puntos):
        gx, gy, radio = grumos[i % len(grumos)]
        distancia = abs(azar.gauss(0, radio * 0.5))
        angulo = azar.uniform(0, math.tau)
        x = zona.left + (gx + math.cos(angulo) * distancia * 1.6 - t * deriva) % (zona.width + 200) - 100
        y = gy + math.sin(angulo) * distancia * 0.7
        fraccion = min(1.0, distancia / radio)
        color = colores[min(len(colores) - 1, int(fraccion * len(colores)))]
        pantalla.fill(color, (g(x), g(y), 2, 2))


def niebla(pantalla, zona, t, color, densidad=0.5, semilla=0):
    # Bancos de niebla que pasan: franjas tramadas que ondulan (las esporas del Campo Esmeralda)
    azar = random.Random(semilla)
    for banco in range(5):
        alto = azar.randint(16, 40)
        y0 = zona.top + azar.randint(0, zona.height - alto)
        rapidez = azar.uniform(0.3, 0.8)
        largo = azar.randint(zona.width // 3, zona.width // 2)
        x0 = zona.right - (azar.randint(0, zona.width) + t * rapidez) % (zona.width + largo)
        for fila in range(0, alto, 2):
            curva = abs(fila - alto / 2) / (alto / 2)
            if azar.random() > densidad + 0.3:
                continue
            ancho = int(largo * (1 - curva * 0.7))
            x = x0 + (largo - ancho) / 2 + math.sin((y0 + fila) / 7 + t / 40) * 8
            inicio = g(x) + ((fila // 2) % 2) * 2
            for cx in range(inicio, g(x) + ancho, 4):
                pantalla.fill(color, (cx, g(y0 + fila), 2, 2))


def agujero_negro(pantalla, cx, cy, radio, t, color=(140, 190, 255), achatado=0.32):
    # El disco de acrecion gira alrededor de un circulo negro. Primero la mitad de atras del
    # disco, despues el agujero y el anillo de luz, y encima la mitad de adelante
    cx, cy = g(cx), g(cy)
    azar = random.Random(5)
    particulas = []
    for i in range(520):
        distancia = radio * (1.25 + azar.random() ** 1.6 * 1.9)
        angulo = azar.uniform(0, math.tau) + t * 0.02 * (radio * 1.6 / distancia) ** 1.5
        brillo = 1 - (distancia - radio * 1.25) / (radio * 1.9)
        particulas.append((angulo, distancia, brillo))
    caliente = mezclar(BLANCO, color, 0.4)
    for detras in (True, False):
        for angulo, distancia, brillo in particulas:
            if (math.sin(angulo) < 0) != detras:
                continue
            x = cx + math.cos(angulo) * distancia
            y = cy + math.sin(angulo) * distancia * achatado
            tono = caliente if brillo > 0.7 else color if brillo > 0.35 else mezclar(color, NOCHE, 0.55)
            pantalla.fill(tono, (g(x), g(y), 2, 2))
        if detras:
            # la luz que el agujero dobla por encima (el anillo de fotones) y el negro
            dibujo.halo(pantalla, cx, cy, radio * 1.6, color, 0.6)
            for paso in range(0, 360, 4):
                a = math.radians(paso)
                pantalla.fill(caliente, (g(cx + math.cos(a) * (radio + 2)), g(cy + math.sin(a) * (radio + 2)), 2, 2))
            disco(pantalla, cx, cy, radio, (0, 0, 0))


_planetas = {}


def planeta(pantalla, cx, cy, radio, claro, oscuro, luz=(-0.6, -0.5), semilla=0, bandas=False, tierra=None):
    # Un planeta con luz y sombra en pixel art: cuatro tonos y un tramado en cada borde de
    # tono (como los dibujos de 16 bits). 'tierra': el color de los continentes (si no, las
    # manchas solo oscurecen: crateres). Se arma una vez y se guarda
    radio = g(radio)
    clave = (radio, tuple(claro), tuple(oscuro), luz, semilla, bandas, tierra)
    if clave not in _planetas:
        lado = radio * 2
        imagen = pygame.Surface((lado, lado), pygame.SRCALPHA)
        tonos = [mezclar(oscuro, (0, 0, 0), 0.5), oscuro, mezclar(claro, oscuro, 0.5), claro]
        azar = random.Random(semilla)
        manchas = [(azar.uniform(-1, 1), azar.uniform(-1, 1), azar.uniform(0.15, 0.4))
                   for _ in range(6 if tierra is None else 14)]
        tonos_tierra = None if tierra is None else [mezclar(tierra, (0, 0, 0), 0.6), mezclar(tierra, (0, 0, 0), 0.35),
                                                    mezclar(tierra, (0, 0, 0), 0.15), tierra]
        largo = math.hypot(*luz) or 1
        lx, ly = luz[0] / largo, luz[1] / largo
        for y in range(0, lado, 2):
            for x in range(0, lado, 2):
                nx, ny = (x + 1 - radio) / radio, (y + 1 - radio) / radio
                d = nx * nx + ny * ny
                if d > 1:
                    continue
                nz = math.sqrt(1 - d)
                luz_aqui = max(0.0, nx * lx + ny * ly + nz * 0.55)
                if bandas:
                    luz_aqui *= 0.85 + 0.15 * math.sin(ny * 14 + semilla)
                en_tierra = False
                for mx, my, mr in manchas:
                    # (una mancha deformada por un ruido simple: bordes de continente, no circulos)
                    borde = mr * (1 + 0.25 * math.sin(nx * 9 + my * 5) * math.cos(ny * 7 + mx * 3))
                    if (nx - mx) ** 2 + (ny - my) ** 2 < borde * borde:
                        if tierra is None:
                            luz_aqui *= 0.8
                        else:
                            en_tierra = True
                nivel = luz_aqui * 3.2
                indice = int(nivel)
                if (nivel - indice) > 0.75 and (x // 2 + y // 2) % 2 == 0:     # el tramado entre tonos
                    indice += 1
                imagen.fill((tonos_tierra if en_tierra else tonos)[min(3, indice)], (x, y, 2, 2))
        _planetas[clave] = imagen
    dibujo.pegar(pantalla, _planetas[clave], g(cx) - radio, g(cy) - radio)


def brasas(pantalla, zona, t, colores, cuantas=40, semilla=3):
    # Chispas que suben y cambian de color (de brillante a oscuro) a medida que se enfrian
    azar = random.Random(semilla)
    for _ in range(cuantas):
        x0 = azar.randint(zona.left, zona.right)
        vida = azar.randint(90, 200)
        fase = azar.randint(0, vida)
        edad = (t + fase) % vida
        x = x0 + math.sin((edad + x0) / 15) * 6
        y = zona.bottom - edad * zona.height / vida
        color = colores[min(len(colores) - 1, edad * len(colores) // vida)]
        pantalla.fill(color, (g(x), g(y), 2, 2))


# ---------- Las cosas ----------

def alondra(pantalla, x, y, t=0, escala=2, mira="arriba", llama=1.0, imagen=None):
    # La nave de Alba (con los modulos que tenga puestos) y la llama del motor detras. (x, y) es
    # el centro. 'mira' = arriba, derecha, abajo o izquierda (giros de 90°: no rompen el pixel art)
    base = imagen if imagen is not None else nave.imagen("nave")
    giro = {"arriba": 0, "izquierda": 90, "abajo": 180, "derecha": -90}[mira]
    if giro:
        base = pygame.transform.rotate(base, giro)
    if escala != 1:
        base = pygame.transform.scale(base, (base.get_width() * escala, base.get_height() * escala))
    mitad = base.get_width() // 2
    if llama > 0:
        largo = g((10 + (math.sin(t / 3) + 1) * 6) * escala / 2 * llama)
        ancho = 3 * escala * 2
        dx, dy = {"arriba": (0, 1), "abajo": (0, -1), "derecha": (-1, 0), "izquierda": (1, 0)}[mira]
        for color, fraccion, angosto in ((NARANJA, 1.0, 1.0), (AMARILLO, 0.55, 0.5), (BLANCO, 0.25, 0.25)):
            l, a = g(largo * fraccion), max(2, g(ancho * angosto))
            if dx == 0:
                arriba = y + dy * (mitad - 6) if dy > 0 else y + dy * (mitad - 6) - l
                pantalla.fill(color, (g(x) - a // 2 // 2 * 2, g(arriba), a, l))
            else:
                izq = x + dx * (mitad - 6) if dx > 0 else x + dx * (mitad - 6) - l
                pantalla.fill(color, (g(izq), g(y) - a // 2 // 2 * 2, l, a))
        dibujo.halo(pantalla, x + dx * mitad, y + dy * mitad, 8 * escala, NARANJA, 0.5)
    dibujo.pegar(pantalla, base, x, y, centrado=True)
    return base.get_width()


def moneda(pantalla, x, y, t, escala=1, tinte=None, rapidez=6):
    # La moneda girando (la del juego), con su brillo de energia. 'tinte': la blanca de las firmas
    from juego.moneda import imagen_moneda          # (importarla arriba traeria todo el juego)
    cuadros = recursos.hoja("moneda_giro.png", 20)
    imagen = cuadros[int(t // rapidez) % len(cuadros)] if cuadros else imagen_moneda()
    if tinte is not None:
        imagen = recursos.tenir(imagen, tinte)
    if escala != 1:
        imagen = pygame.transform.scale(imagen, (imagen.get_width() * escala, imagen.get_height() * escala))
    dibujo.halo(pantalla, x, y, 8 * escala, tinte or AMARILLO, 0.7)
    dibujo.pegar(pantalla, imagen, x, y, centrado=True)


def enemigo(pantalla, tipo, x, y, t, escala=1, tinte=None, rapidez=12):
    from juego.enemigos import TIPOS_ENEMIGO
    cuadros = TIPOS_ENEMIGO[tipo].cuadros()
    imagen = cuadros[int(t // rapidez) % len(cuadros)]
    if tinte is not None:
        imagen = recursos.tenir(imagen, tinte)
    if escala != 1:
        imagen = pygame.transform.scale(imagen, (imagen.get_width() * escala, imagen.get_height() * escala))
    dibujo.pegar(pantalla, imagen, x, y, centrado=True)


_apagadas = {}


def apagada(imagen, brillo):
    # recursos.apagar guardado (los cuadros piden la misma imagen apagada en cada paso)
    clave = (id(imagen), brillo)
    if clave not in _apagadas:
        if len(_apagadas) > 100:
            _apagadas.clear()
        _apagadas[clave] = (imagen, recursos.apagar(imagen, brillo))      # (guarda la imagen: el id no se repite)
    return _apagadas[clave][1]


def jefe(pantalla, tipo, x, y, animacion, t, escala=1, brillo=1.0, rapidez=20):
    # Un guardian con su animacion del juego ('brillo' < 1: apagado, vencido)
    from juego.jefes import TIPOS_JEFE
    clase = TIPOS_JEFE[tipo]
    try:
        cuadros = clase.animaciones()[animacion]
    except (NotImplementedError, KeyError):
        cuadros = [clase.retrato()]
    imagen = cuadros[int(t // rapidez) % len(cuadros)]
    if brillo < 1:
        imagen = apagada(imagen, brillo)
    if escala != 1:
        imagen = pygame.transform.scale(imagen, (imagen.get_width() * escala, imagen.get_height() * escala))
    dibujo.pegar(pantalla, imagen, x, y, centrado=True)


def estacion(pantalla, cx, cy, t, pixel=4, luces=True):
    # La Estacion Umbral de cerca: los paneles solares, el anillo (la mitad de atras pasa detras del
    # cuerpo) con sus ventanas, el cuerpo con sus pisos iluminados y la antena. 'pixel' = 2 es la
    # pequeña; 4 la normal; 6 la grande. Devuelve el rectangulo del cuerpo
    k = pixel / 4
    cx, cy = g(cx), g(cy)
    metal, metal_claro, metal_oscuro = (150, 156, 190), (210, 214, 236), (70, 74, 104)
    panel, panel_claro = (28, 56, 130), (70, 110, 200)
    # los brazos y los paneles solares
    brazo = g(150 * k)
    pantalla.fill(metal_oscuro, (cx - brazo, cy - 2, brazo * 2, 4))
    for lado in (-1, 1):
        for i in range(3):
            ancho, alto = g(34 * k), g(22 * k)
            x = cx + lado * g((48 + i * 36) * k) - (ancho if lado < 0 else 0)
            for y0 in (cy - alto - 4, cy + 4):
                pantalla.fill(panel, (x, y0, ancho, alto))
                for linea_x in range(x, x + ancho, max(4, g(8 * k))):
                    pantalla.fill(panel_claro, (linea_x, y0, 2, alto))
                pantalla.fill(panel_claro, (x, y0, ancho, 2))
        punta = cx + lado * brazo
        if luces and titila(t + (0 if lado < 0 else 30), 70):
            pantalla.fill(ROJO if lado < 0 else (120, 255, 160), (punta - 2, cy - 2, 4, 4))
    # el anillo: la mitad de atras primero
    rx, ry = g(70 * k), g(26 * k)
    grueso = 6 if pixel >= 6 else 4

    def anillo(atras):
        for grado in range(0, 360, 3):
            a = math.radians(grado)
            if (math.sin(a) < 0) != atras:
                continue
            x, y = cx + math.cos(a) * rx, cy + math.sin(a) * ry
            pantalla.fill(metal_oscuro if atras else metal, (g(x) - 2, g(y) - 2, grueso, grueso))
            if not atras and grado % 15 == 0:
                ventana = AMARILLO if not luces or titila(t + grado, 160) else (140, 110, 30)
                pantalla.fill(ventana, (g(x), g(y), 2, 2))
    anillo(True)
    # el cuerpo: un cilindro con luz de la izquierda (tres franjas) y pisos con ventanas
    ancho, alto = g(14 * k) * 2, g(48 * k) * 2
    cuerpo = pygame.Rect(cx - ancho // 2, cy - alto // 2, ancho, alto)
    cuarto = max(2, g(ancho / 4))
    pantalla.fill(metal, cuerpo)
    pantalla.fill(metal_claro, (cuerpo.left + 2, cuerpo.top, cuarto, alto))
    pantalla.fill(metal_oscuro, (cuerpo.right - cuarto, cuerpo.top, cuarto, alto))
    for piso in range(cuerpo.top + 8, cuerpo.bottom - 6, max(4, g(12 * k))):
        pantalla.fill(metal_oscuro, (cuerpo.left, piso, ancho, 2))
        for columna in range(cuerpo.left + 6, cuerpo.right - 4, 6):
            if (piso + columna) % 4 == 0:
                continue
            prendida = not luces or titila(t + piso * 3 + columna, 240)
            pantalla.fill(AMARILLO if prendida else (150, 120, 30), (columna, piso + 4, 2, 2))
    pantalla.fill(metal_claro, (cuerpo.left - 2, cuerpo.top, ancho + 4, 4))
    pantalla.fill(metal_oscuro, (cuerpo.left - 2, cuerpo.bottom - 4, ancho + 4, 4))
    anillo(False)
    # la antena y su plato
    mastil = g(26 * k)
    pantalla.fill(metal_claro, (cx - 2, cuerpo.top - mastil, 2, mastil))
    for i in range(-3, 4):
        pantalla.fill(metal, (cx + g(i * 4 * k), cuerpo.top - mastil + abs(i) * 2, max(2, g(4 * k)), 2))
    if luces and titila(t, 100):
        pantalla.fill(ROJO, (cx - 2, cuerpo.top - mastil - 4, 4, 4))
    dibujo.halo(pantalla, cx, cy, g(40 * k), AMARILLO, 0.35)
    return cuerpo


def pintar(pantalla, filas, paleta, cx, cy, pixel=4):
    # Pixel art de varios colores (como los retratos): cada letra es un color de la paleta y "."
    # es transparente. (cx, cy) es el centro
    izquierda = g(cx - len(filas[0]) * pixel / 2)
    arriba = g(cy - len(filas) * pixel / 2)
    for fila, renglon in enumerate(filas):
        for columna, letra in enumerate(renglon):
            color = paleta.get(letra)
            if color is not None:
                pantalla.fill(color, (izquierda + columna * pixel, arriba + fila * pixel, pixel, pixel))


# Un pedazo del casco de la Errante: placas (P), juntas (j), una ventana (v), el borde roto (r, que
# todavia brilla) y la pintura de la nave (n)
CASCO_ROTO = ["......PPPPPPPPr...",
              "....PPPPjPPPPPrr..",
              "..PPPPPPjPPvvPPr..",
              ".PnnnnnnjnnvvnnPr.",
              "PPPPPPPPjPPPPPPrr.",
              "PPPPPPPPjPPPPPr...",
              ".PPPPPPPjPPPPrr...",
              "...PPPPPjPPPr.....",
              ".....PPPPPrr......"]
PALETA_CASCO = {"P": (150, 154, 176), "j": (80, 84, 106), "v": (60, 160, 200), "r": (255, 140, 0),
                "n": (200, 60, 70)}


def errante(pantalla, x, y, pixel=4, color=(200, 200, 215)):
    dibujo.pixel_art(pantalla, ERRANTE, g(x), g(y), color, pixel)


def capsula(pantalla, x, y, pixel=4, luz=True, t=0):
    dibujo.pixel_art(pantalla, CAPSULA, g(x), g(y), (170, 176, 196), pixel)
    if luz and titila(t, 60):
        pantalla.fill(AMARILLO, (g(x) - pixel, g(y) - pixel, pixel * 2, pixel * 2))


def retrato(pantalla, personaje, x, y, pixel, color_marco=None):
    # El retrato de un personaje (el de los dialogos) con escuadras alrededor
    dibujar_retrato(pantalla, personaje, g(x), g(y), pixel)
    if color_marco is not None:
        interfaz.esquinas(pantalla, pygame.Rect(g(x), g(y), 12 * pixel, 12 * pixel), color_marco, largo=8, grueso=2)


def reloj(pantalla, cx, cy, radio, angulo, color):
    # La esfera de puntos, las doce marcas y la aguja (cuadraditos a lo largo de la linea)
    for paso in range(0, 360, 6):
        a = math.radians(paso)
        lado = 4 if paso % 30 == 0 else 2
        pantalla.fill(mezclar(color, NOCHE, 0.3 if lado == 4 else 0.6),
                      (g(cx + math.cos(a) * radio), g(cy + math.sin(a) * radio), lado, lado))
    for paso in range(0, radio - 12, 2):
        x = cx + math.sin(angulo) * paso
        y = cy - math.cos(angulo) * paso
        pantalla.fill(color, (g(x) - 2, g(y) - 2, 4, 4))
    pantalla.fill(BLANCO, (g(cx) - 4, g(cy) - 4, 8, 8))


# ---------- Las señales ----------

def osciloscopio(pantalla, caja, t, glifo, color, ancho_unidad=14, nuevo=None):
    # Una pantallita con cuadricula: el ritmo del glifo pasa de derecha a izquierda. 'nuevo' (un
    # indice de pulso) sale en amarillo: la nota que el compas acaba de sumar
    caja = pygame.Rect(g(caja.left), g(caja.top), g(caja.width), g(caja.height))
    pantalla.fill(mezclar(NOCHE, (0, 0, 0), 0.4), caja)
    for x in range(caja.left, caja.right, 32):
        pantalla.fill((16, 20, 44), (x, caja.top, 2, caja.height))
    for y in range(caja.top, caja.bottom, 32):
        pantalla.fill((16, 20, 44), (caja.left, y, caja.width, 2))
    pulsos, vuelta = ritmo(glifo, 1)
    base, alto = caja.bottom - caja.height // 4, caja.height // 2
    azar = random.Random(t // 3)
    for x in range(caja.left, caja.right, 2):
        unidad = ((x - caja.left + t * 2) // ancho_unidad) % vuelta
        encendido = None
        for i, (inicio, largo, _) in enumerate(pulsos):
            if inicio <= unidad < inicio + largo:
                encendido = i
        if encendido is not None:
            tono = AMARILLO if encendido == nuevo else color
            pantalla.fill(tono, (x, base - alto, 2, alto + 2))
        else:
            pantalla.fill(mezclar(color, NOCHE, 0.5), (x, base - azar.choice((0, 2, 2, 4)), 2, 2))
    interfaz.esquinas(pantalla, caja, mezclar(color, NOCHE, 0.4), largo=8, grueso=2)


def ondas(pantalla, x, y, t, color, hacia=0.0, abertura=0.7, periodo=50, cuantas=3, alcance=80):
    # Arcos que salen de (x, y) hacia el angulo 'hacia' (radianes; 0 = a la derecha): la radio
    for i in range(cuantas):
        edad = (t + i * periodo / cuantas) % periodo / periodo
        radio = 8 + edad * alcance
        color_arco = mezclar(color, NOCHE, 0.2 + edad * 0.7)
        pasos = max(4, int(radio * abertura))
        for j in range(pasos + 1):
            a = hacia - abertura / 2 + abertura * j / pasos
            pantalla.fill(color_arco, (g(x + math.cos(a) * radio), g(y + math.sin(a) * radio), 2, 2))


def glifo(pantalla, palabra_en_glifos, cx, cy, color, encendidos=None):
    # Un glifo centrado. 'encendidos': cuantas letras se ven (para que se vaya escribiendo)
    letras = palabra_en_glifos.split(" ")
    if encendidos is not None:
        letras = letras[:encendidos]
    if not letras:
        return
    completo = ancho_glifo(palabra_en_glifos)
    dibujar_glifo(pantalla, " ".join(letras), g(cx - completo / 2), g(cy), color)
