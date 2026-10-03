"""
Fondo con paralaje: nebulosas y planetas (sprites), estrellas (pixeles) y el AMBIENTE
de cada sector (particulas que le dan personalidad al bioma).

Todo cae despacio; lo lejano mas lento que lo cercano. Mientras se juega, ademas,
el fondo se corre al reves de la nave (lo maneja quien llama a mover()).
Paleta del fondo: ningun canal por encima de ~110, para que no se confunda con
enemigos, monedas o power-ups.

Ambientes (SECTORES en config.py):
    asteroides  rocas que pasan flotando y, cada tanto, una estrella fugaz
    brasas      chispas que suben como de un incendio y relampagos lejanos
    esporas     luciernagas que se prenden y apagan, y esporas que caen
    panal       un panal de abejas gigante y tenue detras de todo, y polen
    abismo      polvo que gira hacia el centro y ondas de gravedad

mover() va en la logica (60 veces por segundo) y dibujar() en cada cuadro, interpolado.
"""
import math
import random

import pygame

from juego import recursos, lienzo
from juego.config import ALTO, ANCHO_MENU, PROFUNDIDAD, TRANSICION_SECTOR, SECTORES
from juego.interpolacion import Interpolador

MAXIMO_MOTAS = {"asteroides": 14, "brasas": 45, "esporas": 40, "panal": 24, "abismo": 70}


class ObjetoFondo:
    def __init__(self, imagen, x, y, profundidad):
        self.imagen, self.x, self.y, self.profundidad = imagen, x, y, profundidad


class Estrella:
    __slots__ = ("x", "y", "velocidad")

    def __init__(self, x, y, velocidad):
        # Las rapidas (velocidad 1 a 3) son mas grandes, brillantes y cercanas
        self.x, self.y, self.velocidad = x, y, velocidad


class Mota:
    # Una particula del ambiente (una roca, una brasa, una luciernaga...)
    __slots__ = ("x", "y", "vx", "vy", "tipo", "tamano", "fase", "vida")

    def __init__(self, x, y, vx, vy, tipo, tamano, vida=100000):
        self.x, self.y, self.vx, self.vy = x, y, vx, vy
        self.tipo = tipo
        self.tamano = tamano
        self.fase = random.uniform(0, 2 * math.pi)     # para que no titilen todas juntas
        self.vida = vida


def panal(ancho, alto, color):
    # Una baldosa con hexagonos (se repite para llenar el fondo)
    imagen = pygame.Surface((ancho, alto), pygame.SRCALPHA)
    radio = 24
    alto_hexagono = radio * math.sqrt(3)
    for columna in range(-1, int(ancho / (radio * 1.5)) + 2):
        for fila in range(-1, int(alto / alto_hexagono) + 2):
            centro_x = columna * radio * 1.5
            centro_y = fila * alto_hexagono + (alto_hexagono / 2 if columna % 2 else 0)
            puntos = [(centro_x + math.cos(math.pi / 3 * i) * radio, centro_y + math.sin(math.pi / 3 * i) * radio)
                      for i in range(6)]
            pygame.draw.polygon(imagen, color, puntos, 2)
    return imagen


class Fondo:
    def __init__(self):
        # El fondo se arma para el ancho actual (al cambiar el formato se crea uno nuevo)
        escala = lienzo.ancho / ANCHO_MENU
        self.estrellas = []
        for _ in range(round(90 * escala)):
            self.estrellas.append(Estrella(random.randint(0, lienzo.ancho), random.randint(0, ALTO),
                                           random.choice([1, 1, 1, 2, 2, 3])))
        # Nebulosas y planetas, en orden de dibujo: primero lo mas lejano
        self.objetos = []
        self.agregar("nebulosa", 40 * escala, 60)
        self.agregar("nebulosa", 480 * escala, 360, voltear=True)
        self.agregar("planeta_chico", 660 * escala, 140)
        self.agregar("planeta_chico", 150 * escala, 470)
        self.agregar("planeta_grande", 520 * escala, 250)
        self.interpolador = Interpolador()
        # El sector actual y el anterior (para el cambio de colores en 4 etapas)
        self.sector = self.sector_anterior = SECTORES[0]
        self.transicion = 0             # pasos que le quedan al cambio de colores
        self._tenidas = {}              # (imagen, tinte) -> imagen teñida (se tiñe una sola vez)
        # Ambiente
        self.motas = []
        self.pasos = 0
        self.relampago = 0              # pasos que le quedan al destello de un relampago (brasas)
        self.ondas = []                 # radios de las ondas de gravedad (abismo)
        self.desplazamiento_panal = 0
        self._panal = None

    @property
    def tinte(self):
        return self.sector["tinte"]

    @property
    def color(self):
        return self.sector["fondo"]

    def ir_a_sector(self, sector, instantaneo=False):
        # Cambia los colores y el ambiente; los colores tardan TRANSICION_SECTOR pasos, en 4 etapas
        if sector is self.sector:
            return
        self.sector_anterior = self.sector
        self.sector = sector
        self.transicion = 0 if instantaneo else TRANSICION_SECTOR
        if instantaneo:
            self.motas.clear()
            self.ondas.clear()

    def _imagen(self, objeto, tinte):
        if tinte is None:
            return objeto.imagen
        clave = (id(objeto.imagen), tinte)
        if clave not in self._tenidas:
            self._tenidas[clave] = recursos.tenir(objeto.imagen, tinte)
        return self._tenidas[clave]

    def _etapa(self):
        # Avance del cambio de colores: 0, 0.25, 0.5 o 0.75 (1 = terminado), como en las
        # consolas viejas que cambiaban la paleta de a saltos en vez de fundir suave
        if self.transicion <= 0:
            return 1
        return int((1 - self.transicion / TRANSICION_SECTOR) * 4) / 4

    def agregar(self, nombre, x, y, voltear=False):
        # Si falta el sprite, simplemente no se agrega
        imagen = recursos.sprite(nombre + ".png")
        if imagen is None:
            return
        if voltear:
            imagen = pygame.transform.flip(imagen, True, True)  # para que no se vean iguales
        self.objetos.append(ObjetoFondo(imagen, x, y, PROFUNDIDAD[nombre]))

    # ---------- Cada paso ----------

    def mover(self, empuje_x=0, empuje_y=0):
        # Un paso de logica: cada capa cae a 0.6 * profundidad px, mas el empuje (paralaje)
        self.interpolador.guardar(self.objetos + self.estrellas + self.motas)
        self.pasos += 1
        if self.transicion > 0:
            self.transicion -= 1
        for objeto in self.objetos:
            ancho, alto = objeto.imagen.get_size()
            objeto.x += empuje_x * objeto.profundidad
            objeto.y += (0.6 + empuje_y) * objeto.profundidad
            # Si sale por un costado entra por el otro
            if objeto.x < -ancho:
                objeto.x = lienzo.ancho
            elif objeto.x > lienzo.ancho:
                objeto.x = -ancho
            # Si sale por arriba o por abajo vuelve por el otro lado, en otro lugar
            if objeto.y > ALTO:
                objeto.x = random.randint(-ancho // 2, lienzo.ancho - ancho // 2)
                objeto.y = -alto
            elif objeto.y < -alto:
                objeto.x = random.randint(-ancho // 2, lienzo.ancho - ancho // 2)
                objeto.y = ALTO

        for estrella in self.estrellas:
            estrella.x += empuje_x * estrella.velocidad
            estrella.y += (0.6 + empuje_y) * estrella.velocidad
            if estrella.x < 0:
                estrella.x += lienzo.ancho
            elif estrella.x > lienzo.ancho:
                estrella.x -= lienzo.ancho
            if estrella.y > ALTO:
                estrella.x = random.randint(0, lienzo.ancho)
                estrella.y = 0
            elif estrella.y < 0:
                estrella.x = random.randint(0, lienzo.ancho)
                estrella.y = ALTO
        self._mover_ambiente(empuje_x, empuje_y)

    def _mover_ambiente(self, empuje_x, empuje_y):
        ambiente = self.sector["ambiente"]
        self._crear_motas(ambiente)
        centro_x, centro_y = lienzo.ancho / 2, ALTO / 2
        for mota in self.motas[:]:
            if mota.tipo == "polvo":
                # Gira alrededor del centro y se va acercando (como el agua en un desague)
                lejos_x, lejos_y = mota.x - centro_x, mota.y - centro_y
                distancia = math.hypot(lejos_x, lejos_y) or 1
                mota.vx = -lejos_y / distancia * 1.2 - lejos_x / distancia * 0.5
                mota.vy = lejos_x / distancia * 1.2 - lejos_y / distancia * 0.5
                if distancia < 30:
                    mota.vida = 0
            elif mota.tipo in ("brasa", "luciernaga"):
                mota.vx = math.sin(self.pasos / 30 + mota.fase) * 0.4
            mota.x += mota.vx + empuje_x * 0.8
            mota.y += mota.vy + empuje_y * 0.8
            mota.vida -= 1
            fuera = mota.x < -40 or mota.x > lienzo.ancho + 40 or mota.y < -40 or mota.y > ALTO + 40
            if mota.vida <= 0 or fuera or (mota.tipo != "polvo" and self._de_otro_ambiente(mota, ambiente)):
                self.motas.remove(mota)
        if self.relampago > 0:
            self.relampago -= 1
        self.ondas = [radio + 3 for radio in self.ondas if radio < lienzo.ancho]
        self.desplazamiento_panal = (self.desplazamiento_panal + 0.3 + empuje_y * 0.3) % 84

    def _de_otro_ambiente(self, mota, ambiente):
        # Las motas del sector anterior se van apagando de a poco al cambiar
        propias = {"asteroides": ("roca", "fugaz"), "brasas": ("brasa",), "esporas": ("luciernaga", "espora"),
                   "panal": ("polen",), "abismo": ("polvo",)}[ambiente]
        return mota.tipo not in propias and random.random() < 0.02

    def _crear_motas(self, ambiente):
        cuantas = sum(1 for mota in self.motas if mota.tipo != "fugaz")
        hay_lugar = cuantas < MAXIMO_MOTAS[ambiente]
        ancho = lienzo.ancho
        if ambiente == "asteroides":
            if hay_lugar and random.random() < 0.02:
                self.motas.append(Mota(random.randint(0, ancho), -20, random.uniform(-0.3, 0.3),
                                       random.uniform(0.4, 1), "roca", random.choice([6, 8, 10])))
            if random.random() < 0.003:
                self.motas.append(Mota(random.randint(-100, ancho // 2), random.randint(0, ALTO // 2),
                                       9, 3, "fugaz", 2, 40))
        elif ambiente == "brasas":
            if hay_lugar and random.random() < 0.15:
                self.motas.append(Mota(random.randint(0, ancho), ALTO + 10, 0, random.uniform(-1.4, -0.5),
                                       "brasa", random.choice([2, 2, 4])))
            if random.random() < 0.002:
                self.relampago = 8
        elif ambiente == "esporas":
            if hay_lugar and random.random() < 0.06:
                if random.random() < 0.6:
                    self.motas.append(Mota(random.randint(0, ancho), random.randint(0, ALTO), 0,
                                           random.uniform(-0.3, 0.3), "luciernaga", 4, random.randint(300, 700)))
                else:
                    self.motas.append(Mota(random.randint(0, ancho), -10, random.uniform(-0.2, 0.2),
                                           random.uniform(0.3, 0.6), "espora", 2))
        elif ambiente == "panal":
            if hay_lugar and random.random() < 0.06:
                self.motas.append(Mota(random.randint(0, ancho), -10, random.uniform(-0.3, 0.3),
                                       random.uniform(0.3, 0.8), "polen", random.choice([2, 4])))
        elif ambiente == "abismo":
            if hay_lugar and random.random() < 0.35:
                # Nace en cualquier lugar de la pantalla lejos del centro, y gira hacia el
                polvo_x, polvo_y = random.randint(0, ancho), random.randint(0, ALTO)
                if math.hypot(polvo_x - ancho / 2, polvo_y - ALTO / 2) > 200:
                    self.motas.append(Mota(polvo_x, polvo_y, 0, 0, "polvo", random.choice([2, 2, 4])))
            if self.pasos % 360 == 0:
                self.ondas.append(0)

    # ---------- Dibujo ----------

    def dibujar(self, pantalla, fraccion=1):
        etapa = self._etapa()
        color = [round(a + (b - a) * etapa) for a, b in zip(self.sector_anterior["fondo"], self.sector["fondo"])]
        if self.relampago > 0 and self.relampago % 4 < 2:
            color = [min(110, c + 14) if i == 0 else c + 4 for i, c in enumerate(color)]
        pantalla.fill(color)
        if self.sector["ambiente"] == "panal" and etapa == 1:
            self._dibujar_panal(pantalla)
        for radio in self.ondas:
            pygame.draw.circle(pantalla, (22, 30, 64), (lienzo.ancho // 2, ALTO // 2), int(radio), 2)
        with self.interpolador.aplicar(self.objetos + self.estrellas + self.motas, fraccion):
            for objeto in self.objetos:
                posicion = (int(objeto.x), int(objeto.y))
                if etapa < 1:
                    # Durante el cambio: los colores viejos y encima los nuevos, cada vez mas
                    pantalla.blit(self._imagen(objeto, self.sector_anterior["tinte"]), posicion)
                    if etapa > 0:
                        nueva = self._imagen(objeto, self.tinte).copy()
                        nueva.set_alpha(int(255 * etapa))
                        pantalla.blit(nueva, posicion)
                else:
                    pantalla.blit(self._imagen(objeto, self.tinte), posicion)
            rojo, verde, azul = self.sector["estrellas"]
            for estrella in self.estrellas:
                brillo = 60 + estrella.velocidad * 60
                tamano = 1 if estrella.velocidad < 3 else 2
                pantalla.fill((brillo * rojo, brillo * verde, brillo * azul),
                              (int(estrella.x), int(estrella.y), tamano, tamano))
            for mota in self.motas:
                self._dibujar_mota(pantalla, mota)

    def _dibujar_panal(self, pantalla):
        if self._panal is None or self._panal.get_width() != lienzo.ancho:
            self._panal = panal(lienzo.ancho, ALTO + 84, (30, 22, 6))
        pantalla.blit(self._panal, (0, int(self.desplazamiento_panal) - 84))

    def _dibujar_mota(self, pantalla, mota):
        x, y = int(mota.x) // 2 * 2, int(mota.y) // 2 * 2
        tamano = mota.tamano
        if mota.tipo == "roca":
            pantalla.fill((30, 32, 50), (x - 2, y + 2, tamano, tamano))
            pantalla.fill((54, 60, 84), (x, y, tamano, tamano))
            pantalla.fill((86, 92, 110), (x, y, tamano // 2, tamano // 2))
        elif mota.tipo == "fugaz":
            for i, color in enumerate(((100, 100, 110), (60, 60, 80), (34, 34, 50))):
                pantalla.fill(color, (x - i * 8, y - i * 3, 4 - i // 2 * 2 or 2, 2))
        elif mota.tipo == "brasa":
            parpadea = (self.pasos // 6 + int(mota.fase * 10)) % 3
            color = ((110, 40, 20), (110, 70, 20), (90, 20, 20))[parpadea]
            pantalla.fill(color, (x, y, tamano, tamano))
        elif mota.tipo == "luciernaga":
            # Se prende y se apaga lento (y al final de su vida se apaga del todo)
            brillo = math.sin(self.pasos / 25 + mota.fase)
            if brillo > -0.2 and mota.vida > 30:
                pantalla.fill((24, 80, 44), (x - 4, y - 2, 12, 8))
                pantalla.fill((24, 80, 44), (x - 2, y - 4, 8, 12))
                pantalla.fill((90, 110, 70) if brillo > 0.5 else (50, 100, 60), (x, y, 4, 4))
        elif mota.tipo == "espora":
            pantalla.fill((40, 80, 50), (x, y, tamano, tamano))
        elif mota.tipo == "polen":
            pantalla.fill((100, 76, 20), (x, y, tamano, tamano))
        elif mota.tipo == "polvo":
            pantalla.fill((46, 66, 110), (x, y, tamano, tamano))
