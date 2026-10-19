"""
Los paisajes: la animacion grande y lenta del fondo de cada sector (su personalidad).

Cada bioma tiene una "pieza" que se ve lejos, detras de todo, y que se mueve despacio:

    asteroides  GIGANTE ANILLADO   un planeta con anillos que giran y una luna que lo rodea
    brasas      SOL MORIBUNDO      una estrella roja que respira, con arcos de plasma
    esporas     AURORA DEL PANTANO cortinas de luz verde y, cada tanto, la sombra de algo enorme
    panal       LATIDO DE LA COLMENA ondas de luz que recorren las celdas del panal
    abismo      EL OJO DEL ABISMO  un agujero negro con su disco girando (ahi cae el polvo)

Patron Registry (como los enemigos o los jefes): cada paisaje es una clase con el decorador
@paisaje("ambiente"), y el Fondo le pide el del sector con dibujar_paisaje(). Para darle un
paisaje a un bioma nuevo alcanza con escribir su clase aqui.

Reglas (las mismas del fondo):
- Colores apagados: ningun canal pasa de ~110, asi no se confunde con lo que importa
  (enemigos, monedas, balas). Mientras se juega, ademas, todo se ve a 'luz' (mas oscuro).
- Todo en la grilla de 2 px (cuadraditos de 2x2 en posiciones pares).
- Nada parpadea ni destella: todo cambia despacio (respira, gira, pasa).
- dibujar() no cambia nada: todo sale del tiempo 't' (pasos del fondo, con la fraccion para
  que se vea suave a cualquier FPS). Lo que parece azar (de donde sale la onda del panal)
  sale de un random.Random con la vuelta como semilla: siempre igual para el mismo t.
"""
import math
import random

import pygame

from juego.config import ANCHO, ALTO
from juego.dibujo import en_grilla

g = en_grilla                   # (se usa en cada linea: corto a proposito)
PAISAJES = {}                   # ambiente -> clase (el registro)
_hechos = {}                    # ambiente -> el paisaje ya armado (se arma una sola vez)


def paisaje(ambiente):
    # Decorador: anota la clase en el registro con el nombre de su ambiente
    def registrar(clase):
        PAISAJES[ambiente] = clase
        return clase
    return registrar


def dibujar_paisaje(ambiente, pantalla, t, luz=1.0, dx=0, dy=0, desplazamiento=0):
    # Dibuja el paisaje de un ambiente. 'dx', 'dy': cuanto se corre por el paralaje;
    # 'desplazamiento': cuanto bajo la baldosa del panal (para que las celdas calcen)
    if ambiente not in PAISAJES:
        return
    if ambiente not in _hechos:
        _hechos[ambiente] = PAISAJES[ambiente]()
    _hechos[ambiente].dibujar(pantalla, t, luz, dx, dy, desplazamiento)


# ---------- Piezas comunes ----------

def tono(color, luz):
    # El color a 'luz' de brillo (1 = como esta)
    return (int(color[0] * luz), int(color[1] * luz), int(color[2] * luz))


def mezclar(a, b, cuanto):
    # De 'a' (cuanto = 0) a 'b' (cuanto = 1)
    return tuple(int(x + (y - x) * cuanto) for x, y in zip(a, b))


def disco(pantalla, cx, cy, rx, color, ry=None):
    # Un ovalo lleno en la grilla: renglones de 2 px de alto y anchos pares
    ry = rx if ry is None else ry
    cx, cy = g(cx), g(cy)
    for y in range(-g(ry), g(ry), 2):
        mitad = g(rx * math.sqrt(max(0.0, 1 - ((y + 1) / ry) ** 2)))
        if mitad > 0:
            pantalla.fill(color, (cx - mitad, cy + y, mitad * 2, 2))


def esfera(radio, claro, oscuro, luz_desde=(-0.6, -0.5), bandas=0, semilla=0):
    # Un planeta en pixel art: cuatro tonos con luz y sombra, y un tramado entre tono y tono
    # (como los dibujos de 16 bits). 'bandas' > 0: franjas como las de un gigante gaseoso
    radio = g(radio)
    lado = radio * 2
    imagen = pygame.Surface((lado, lado), pygame.SRCALPHA)
    tonos = [mezclar(oscuro, (0, 0, 0), 0.5), oscuro, mezclar(claro, oscuro, 0.5), claro]
    largo = math.hypot(*luz_desde)
    lx, ly = luz_desde[0] / largo, luz_desde[1] / largo
    for y in range(0, lado, 2):
        for x in range(0, lado, 2):
            nx, ny = (x + 1 - radio) / radio, (y + 1 - radio) / radio
            d = nx * nx + ny * ny
            if d > 1:
                continue
            nz = math.sqrt(1 - d)
            luz_aqui = max(0.0, nx * lx + ny * ly + nz * 0.55)
            if bandas:
                luz_aqui *= 0.84 + 0.16 * math.sin(ny * bandas + semilla)
            nivel = luz_aqui * 3.2
            indice = int(nivel)
            if nivel - indice > 0.75 and (x // 2 + y // 2) % 2 == 0:     # el tramado entre tonos
                indice += 1
            imagen.fill(tonos[min(3, indice)], (x, y, 2, 2))
    return imagen


class Paisaje:
    # La base: guarda las imagenes armadas por brillo (jugando se ven mas oscuras)
    nombre = ""

    def __init__(self):
        self._imagenes = {}

    def imagen(self, clave, luz, fabrica):
        # La imagen 'clave' a ese brillo; 'fabrica(luz)' la arma la primera vez
        if (clave, luz) not in self._imagenes:
            self._imagenes[(clave, luz)] = fabrica(luz)
        return self._imagenes[(clave, luz)]

    def dibujar(self, pantalla, t, luz, dx, dy, desplazamiento=0):
        pass


# ---------- Cinturon Exterior: el gigante anillado ----------

@paisaje("asteroides")
class GiganteAnillado(Paisaje):
    nombre = "GIGANTE ANILLADO"
    CENTRO = (ANCHO - 240, ALTO - 130)
    RADIO = 96
    INCLINACION = -0.22             # radianes: el anillo se ve un poco torcido
    ACHATADO = 0.2                  # lo vemos casi de canto
    GIRO = 0.0016                   # radianes por paso del borde de adentro del anillo
    CLARO, OSCURO = (44, 74, 104), (14, 26, 44)
    GRANOS = ((84, 96, 110), (62, 72, 96), (40, 48, 72))

    def __init__(self):
        super().__init__()
        azar = random.Random(1)
        # Dos bandas de granos con un hueco entre ellas (como la division de Cassini)
        self.granos = []
        for i in range(560):
            banda = (1.45, 1.95) if i % 3 else (2.06, 2.5)
            distancia = azar.uniform(*banda)
            self.granos.append((azar.uniform(0, math.tau), distancia, azar.randrange(3)))
        self.coseno, self.seno = math.cos(self.INCLINACION), math.sin(self.INCLINACION)

    def girar(self, x, y):
        # Inclina un punto del plano del anillo
        return x * self.coseno - y * self.seno, x * self.seno + y * self.coseno

    def dibujar(self, pantalla, t, luz, dx, dy, desplazamiento=0):
        cx, cy = self.CENTRO[0] + dx, self.CENTRO[1] + dy
        colores = [tono(color, luz) for color in self.GRANOS]
        planeta = self.imagen("planeta", luz, lambda l: esfera(self.RADIO, tono(self.CLARO, l),
                                                              tono(self.OSCURO, l), bandas=11, semilla=2))
        luna = self.imagen("luna", luz, lambda l: esfera(12, tono((80, 86, 100), l), tono((24, 26, 36), l)))
        # La luna: una orbita grande e inclinada; tarda ~50 s en dar la vuelta
        angulo_luna = t * 0.002
        luna_x, luna_y = self.girar(math.cos(angulo_luna) * self.RADIO * 3.1,
                                    math.sin(angulo_luna) * self.RADIO * 3.1 * 0.3)
        luna_detras = math.sin(angulo_luna) < 0
        for detras in (True, False):
            if detras == luna_detras:
                pantalla.blit(luna, (g(cx + luna_x) - 12, g(cy + luna_y) - 12))
            for angulo, distancia, color in self.granos:
                # Los de adentro giran mas rapido (como en un sistema de verdad)
                a = angulo + t * self.GIRO * (1.5 / distancia) ** 1.5
                if (math.sin(a) < 0) != detras:
                    continue
                x, y = self.girar(math.cos(a) * distancia * self.RADIO,
                                  math.sin(a) * distancia * self.RADIO * self.ACHATADO)
                pantalla.fill(colores[color], (g(cx + x), g(cy + y), 2, 2))
            if detras:
                pantalla.blit(planeta, (g(cx) - g(self.RADIO), g(cy) - g(self.RADIO)))


# ---------- Nebulosa Carmesi: el sol moribundo ----------

@paisaje("brasas")
class SolMoribundo(Paisaje):
    nombre = "SOL MORIBUNDO"
    CENTRO = (ANCHO - 80, 56)       # en la esquina: la mitad afuera de la pantalla
    RADIO = 150
    VIDA_ARCO = 720                 # pasos que dura cada arco de plasma (12 s)
    ARCOS = 3
    CUERPO = ((76, 30, 18), (62, 22, 16), (48, 14, 13), (34, 9, 11))    # del centro al borde
    CORONA = (34, 8, 10)
    PLASMA = ((108, 52, 24), (84, 28, 18), (46, 12, 12))     # lo caliente, el plasma y el rastro

    def cuerpo(self, luz):
        # El disco con el borde mas oscuro (como se ve un sol) y unas manchas
        lado = g(self.RADIO) * 2
        imagen = pygame.Surface((lado, lado), pygame.SRCALPHA)
        radio = lado // 2
        azar = random.Random(4)
        manchas = [(azar.uniform(-0.7, 0.7), azar.uniform(-0.7, 0.7), azar.uniform(0.04, 0.1)) for _ in range(9)]
        for y in range(0, lado, 2):
            for x in range(0, lado, 2):
                nx, ny = (x + 1 - radio) / radio, (y + 1 - radio) / radio
                d = math.sqrt(nx * nx + ny * ny)
                if d > 1:
                    continue
                nivel = d * 3.4
                indice = int(nivel)
                if nivel - indice > 0.7 and (x // 2 + y // 2) % 2:
                    indice += 1
                if any((nx - mx) ** 2 + (ny - my) ** 2 < mr * mr for mx, my, mr in manchas):
                    indice += 1
                imagen.fill(tono(self.CUERPO[min(3, indice)], luz), (x, y, 2, 2))
        return imagen

    def dibujar(self, pantalla, t, luz, dx, dy, desplazamiento=0):
        cx, cy = self.CENTRO[0] + dx, self.CENTRO[1] + dy
        # La corona: un anillo tramado que respira (crece y se achica en ~8 s)
        respira = 12 + math.sin(t * 0.013) * 6
        corona = tono(self.CORONA, luz)
        for paso in range(0, 360, 3):
            a = math.radians(paso)
            for capa in range(0, int(respira), 4):
                if (paso // 3 + capa // 4) % 2:     # (un tramado quieto: nada parpadea)
                    continue
                r = self.RADIO + 2 + capa
                pantalla.fill(corona, (g(cx + math.cos(a) * r), g(cy + math.sin(a) * r), 2, 2))
        pantalla.blit(self.imagen("cuerpo", luz, self.cuerpo), (g(cx) - g(self.RADIO), g(cy) - g(self.RADIO)))
        colores = [tono(color, luz) for color in self.PLASMA]
        for arco in range(self.ARCOS):
            self._arco(pantalla, cx, cy, t + arco * self.VIDA_ARCO / self.ARCOS, arco, colores)

    def _arco(self, pantalla, cx, cy, t, numero, colores):
        # Un arco de plasma: sale del borde, sube, el plasma corre por adentro y se apaga.
        # Cada vuelta nace en otro lugar del borde (el que mira hacia la pantalla)
        vuelta, edad = divmod(t, self.VIDA_ARCO)
        azar = random.Random(int(vuelta) * 7 + numero)
        # cada arco en su parte del borde (asi no se amontonan como petalos)
        pie = math.radians(100 + numero * 30 + azar.uniform(0, 18))
        abertura = azar.uniform(0.2, 0.3)
        vida = edad / self.VIDA_ARCO
        alto = math.sin(math.pi * vida) * self.RADIO * azar.uniform(0.35, 0.6)

        def punto_del_arco(s):
            a = pie + (s - 0.5) * abertura
            r = self.RADIO + alto * math.sin(math.pi * s)
            return g(cx + math.cos(a) * r), g(cy + math.sin(a) * r)

        for i in range(0, 40, 2):           # el rastro: un arco punteado y oscuro
            pantalla.fill(colores[2], (*punto_del_arco(i / 40), 2, 2))
        for i in range(7):                  # el plasma: gotas que corren de un pie al otro
            s = (i / 7 + edad * 0.0025) % 1
            x, y = punto_del_arco(s)
            caliente = math.sin(math.pi * s) > 0.75 and 0.15 < vida < 0.85
            pantalla.fill(colores[0] if caliente else colores[1], (x, y, 4, 4))


# ---------- Campo Esmeralda: la aurora del pantano ----------

@paisaje("esporas")
class AuroraDelPantano(Paisaje):
    nombre = "AURORA DEL PANTANO"
    CORTINAS = ((150, 0.0), (250, 2.1))     # (altura del borde de abajo, desfase)
    LUCES = ((50, 110, 74), (26, 80, 52), (14, 44, 30))     # el borde brillante, el medio y lo alto
    SOMBRA = (8, 24, 17)
    VUELTA_SOMBRA = 3000            # cada 50 s pasa la sombra...
    CRUZA = 1500                    # ...y tarda 25 s en cruzar

    def dibujar(self, pantalla, t, luz, dx, dy, desplazamiento=0):
        self._sombra(pantalla, t, luz, dx, dy)
        colores = [tono(color, luz) for color in self.LUCES]
        for altura, desfase in self.CORTINAS:
            for x in range(0, ANCHO, 4):
                # Una luz que corre a lo largo de la cortina: donde no llega, la cortina se corta
                fuerza = 0.5 + 0.5 * math.sin(x / 140 - t * 0.012 + desfase)
                if fuerza < 0.2:
                    continue
                borde = (altura + dy + math.sin(x / 170 + t * 0.006 + desfase) * 28
                         + math.sin(x / 61 - t * 0.011 + desfase) * 10)
                largo = (40 + 34 * math.sin(x / 97 + t * 0.009 + desfase * 2)) * fuerza
                columna = g(x + dx)
                medio = g(largo * 0.4)
                pantalla.fill(colores[2], (columna, g(borde - largo), 2, max(0, g(largo) - medio)))
                pantalla.fill(colores[1], (columna, g(borde) - medio, 2, medio))
                if fuerza > 0.55:
                    pantalla.fill(colores[0], (columna, g(borde), 2, 4))

    def _sombra(self, pantalla, t, luz, dx, dy):
        # Algo enorme que nada muy lejos, detras de la aurora: una fila de discos oscuros que se
        # siguen como una serpiente. Solo se ve si uno se fija (el lema: "algo se mueve")
        vuelta, edad = divmod(t, self.VUELTA_SOMBRA)
        if edad > self.CRUZA:
            return
        azar = random.Random(int(vuelta))
        de_izquierda = azar.random() < 0.5
        altura = azar.uniform(ALTO * 0.45, ALTO * 0.75)
        color = tono(self.SOMBRA, luz)
        for segmento in range(16):
            avance = (edad - segmento * 26) / self.CRUZA
            x = -260 + avance * (ANCHO + 520)
            if not de_izquierda:
                x = ANCHO - x
            y = altura + math.sin(avance * 9 - segmento * 0.35) * 36
            disco(pantalla, x + dx * 0.5, y + dy * 0.5, 30 - segmento * 1.5, color, (30 - segmento * 1.5) * 0.7)


# ---------- Mar de Ambar: el latido de la colmena ----------

@paisaje("panal")
class LatidoDeLaColmena(Paisaje):
    nombre = "LATIDO DE LA COLMENA"
    # La misma cuadricula de hexagonos que la baldosa del Fondo (fondo.panal: radio 24)
    LADO = 24
    ALTO_HEXAGONO = 24 * math.sqrt(3)
    LATIDO = 330                    # pasos entre latido y latido (5.5 s)
    DOBLE = 26                      # el segundo golpe del latido llega 26 pasos despues (lub-dub)
    RAPIDEZ = 3.6                   # px por paso que avanza la onda
    APAGARSE = 1100                 # a cuantos px de donde nacio la onda ya no se ve
    ANCHO_ONDA = 60
    CELDA = ((78, 56, 14), (52, 36, 8), (34, 24, 6))      # de la cresta de la onda a la cola

    def celda(self, color):
        # Un hexagono lleno un poco mas pequeño que el del panal (queda adentro del borde)
        radio = 18
        lado = radio * 2 + 4
        imagen = pygame.Surface((lado, lado), pygame.SRCALPHA)
        centro = lado // 2
        for y in range(-g(radio * 0.86), g(radio * 0.86), 2):
            # el ancho de un hexagono con puntas a los costados, renglon por renglon
            mitad = g(radio - abs(y + 1) / math.sqrt(3))
            imagen.fill(color, (centro - mitad, centro + y, mitad * 2, 2))
        return imagen

    def dibujar(self, pantalla, t, luz, dx, dy, desplazamiento=0):
        vuelta, edad = divmod(t, self.LATIDO)
        azar = random.Random(int(vuelta))
        origen = (azar.uniform(100, ANCHO - 100), azar.uniform(80, ALTO - 80))
        # Los dos golpes del latido: el segundo mas suave
        for retraso, fuerza in ((0, 1.0), (self.DOBLE, 0.6)):
            frente = (edad - retraso) * self.RAPIDEZ
            if frente > 0:
                apagarse = fuerza * max(0.0, 1 - frente / self.APAGARSE)    # se apaga al alejarse
                self._onda(pantalla, origen, frente, apagarse, luz, desplazamiento)

    def _onda(self, pantalla, origen, frente, apagarse, luz, desplazamiento):
        # Prende las celdas que la onda esta cruzando (las de la cresta, mas)
        origen_x, origen_y = origen
        corrimiento = g(desplazamiento) - 84
        for columna in range(-1, int(ANCHO / (self.LADO * 1.5)) + 2):
            x = columna * self.LADO * 1.5
            for fila in range(-1, int((ALTO + 84) / self.ALTO_HEXAGONO) + 2):
                y = fila * self.ALTO_HEXAGONO + (self.ALTO_HEXAGONO / 2 if columna % 2 else 0) + corrimiento
                atras = frente - math.hypot(x - origen_x, y - origen_y)
                if not 0 <= atras < self.ANCHO_ONDA:
                    continue
                fuerza = (1 - atras / self.ANCHO_ONDA) * apagarse
                if fuerza < 0.2:
                    continue
                nivel = 0 if fuerza > 0.7 else 1 if fuerza > 0.4 else 2
                imagen = self.imagen(nivel, luz, lambda l: self.celda(tono(self.CELDA[nivel], l)))
                pantalla.blit(imagen, (g(x) - 20, g(y) - 20))


# ---------- Abismo Azul: el ojo del abismo ----------

@paisaje("abismo")
class OjoDelAbismo(Paisaje):
    nombre = "EL OJO DEL ABISMO"
    RADIO = 34
    ACHATADO = 0.3
    GIRO = 0.012                    # radianes por paso del borde de adentro del disco
    DISCO = ((92, 102, 110), (50, 70, 110), (24, 34, 72))   # de lo caliente (adentro) a lo frio
    ANILLO = (70, 84, 110)          # la luz que el agujero dobla a su alrededor

    def __init__(self):
        super().__init__()
        azar = random.Random(5)
        self.particulas = []
        for _ in range(460):
            distancia = self.RADIO * (1.35 + azar.random() ** 1.5 * 3.4)
            calor = 1 - (distancia - self.RADIO * 1.35) / (self.RADIO * 3.4)
            self.particulas.append((azar.uniform(0, math.tau), distancia,
                                    0 if calor > 0.75 else 1 if calor > 0.4 else 2))

    def dibujar(self, pantalla, t, luz, dx, dy, desplazamiento=0):
        cx, cy = g(ANCHO / 2 + dx * 0.4), g(ALTO / 2 + dy * 0.4)     # muy lejos: casi no se corre
        colores = [tono(color, luz) for color in self.DISCO]
        for detras in (True, False):
            for angulo, distancia, color in self.particulas:
                # Los de adentro giran mucho mas rapido (por eso se ve que "cae")
                a = angulo + t * self.GIRO * (self.RADIO * 1.35 / distancia) ** 1.5
                if (math.sin(a) < 0) != detras:
                    continue
                pantalla.fill(colores[color], (g(cx + math.cos(a) * distancia),
                                               g(cy + math.sin(a) * distancia * self.ACHATADO), 2, 2))
            if detras:
                anillo = tono(self.ANILLO, luz)
                for paso in range(0, 360, 5):
                    a = math.radians(paso)
                    pantalla.fill(anillo, (g(cx + math.cos(a) * (self.RADIO + 2)),
                                           g(cy + math.sin(a) * (self.RADIO + 2)), 2, 2))
                disco(pantalla, cx, cy, self.RADIO, (0, 0, 2))
