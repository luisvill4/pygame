"""
Efectos visuales: particulas, textos flotantes ("+1"), temblor y destello de pantalla.

Particulas al estilo retro: cuadrados alineados a una cuadricula de 2 px que NO se
desvanecen con transparencia, sino que cambian de color por etapas segun una paleta
(ver las paletas en config.py).
"""
import math
import random

from juego import dibujo
from juego.config import BLANCO, FONDO, FUEGO


class Particula:
    __slots__ = ("x", "y", "vx", "vy", "paleta", "vida", "vida_inicial", "tamano")

    def __init__(self, x, y, vx, vy, paleta, vida, tamano):
        self.x, self.y = x, y               # posicion
        self.vx, self.vy = vx, vy           # velocidad
        self.paleta = paleta                # colores por los que va pasando
        self.vida = vida                    # frames que le quedan
        self.vida_inicial = vida
        self.tamano = tamano                # lado del cuadrado en pixeles


class TextoFlotante:
    __slots__ = ("texto", "x", "y", "color", "vida")

    def __init__(self, texto, x, y, color):
        self.texto, self.x, self.y, self.color = texto, x, y, color
        self.vida = 45


class Efectos:
    def __init__(self):
        self.particulas = []
        self.textos = []
        self.temblor = 0            # frames que le quedan al temblor de pantalla
        self.destello = 0           # frames que le quedan al destello de color
        self.color_destello = BLANCO

    def reiniciar(self):
        self.particulas.clear()
        self.textos.clear()
        self.temblor, self.destello = 0, 0

    # ---------- Crear ----------

    def particula(self, x, y, vx, vy, paleta, vida, tamano):
        self.particulas.append(Particula(x, y, vx, vy, paleta, vida, tamano))

    def explosion(self, cx, cy, paleta, cantidad, fuerza, tamano=4):
        # Lanza particulas en todas direcciones desde (cx, cy)
        for _ in range(cantidad):
            direccion = random.uniform(0, 2 * math.pi)
            rapidez = random.uniform(fuerza * 0.3, fuerza)
            self.particula(cx, cy, math.cos(direccion) * rapidez, math.sin(direccion) * rapidez,
                           paleta, random.randint(20, 40), tamano)

    def anillo(self, cx, cy, paleta, cantidad, fuerza, tamano=3):
        # Como la explosion, pero todas a la misma velocidad: forma un circulo que crece
        for i in range(cantidad):
            direccion = 2 * math.pi * i / cantidad
            self.particula(cx, cy, math.cos(direccion) * fuerza, math.sin(direccion) * fuerza,
                           paleta, 22, tamano)

    def texto_flotante(self, mensaje, x, y, color):
        self.textos.append(TextoFlotante(mensaje, x, y, color))

    def estela(self, cx, cy, angulo_nave, cantidad=1):
        # Fuego que sale por la parte de atras de la nave
        frente_x = -math.sin(math.radians(angulo_nave))
        frente_y = -math.cos(math.radians(angulo_nave))
        for _ in range(cantidad):
            salida_x = cx - frente_x * 26 + random.uniform(-4, 4)
            salida_y = cy - frente_y * 26 + random.uniform(-4, 4)
            self.particula(salida_x, salida_y,
                           -frente_x * random.uniform(1, 2.5), -frente_y * random.uniform(1, 2.5),
                           FUEGO, random.randint(8, 16), random.choice([2, 4]))

    def sacudir(self, frames, color=None):
        # Temblor de pantalla y, si se da un color, un destello
        self.temblor = max(self.temblor, frames)
        if color:
            self.destello = 4
            self.color_destello = color

    # ---------- Cada frame ----------

    def actualizar(self):
        for particula in self.particulas[:]:
            particula.x += particula.vx
            particula.y += particula.vy
            particula.vx *= 0.92        # friccion: se van frenando
            particula.vy *= 0.92
            particula.vida -= 1
            if particula.vida <= 0:
                self.particulas.remove(particula)
        for flotante in self.textos[:]:
            flotante.y -= 1
            flotante.vida -= 1
            if flotante.vida <= 0:
                self.textos.remove(flotante)
        # El temblor y el destello duran pasos de logica (no cuadros dibujados),
        # asi duran lo mismo a cualquier FPS
        if self.destello > 0:
            self.destello -= 1
        if self.temblor > 0:
            self.temblor -= 1

    def dibujar(self, pantalla):
        for particula in self.particulas:
            # El color y el tamaño bajan por etapas segun la vida que le queda
            fraccion = particula.vida / particula.vida_inicial
            paleta = particula.paleta
            color = paleta[min(int(fraccion * len(paleta)), len(paleta) - 1)]
            tamano = max(1, math.ceil(particula.tamano * fraccion))
            # Se alinea a una cuadricula de 2 pixeles para que se vea pixelado
            pantalla.fill(color, (int(particula.x) // 2 * 2, int(particula.y) // 2 * 2, tamano, tamano))
        for flotante in self.textos:
            # Parpadea en sus ultimos frames
            if flotante.vida > 12 or flotante.vida // 3 % 2 == 0:
                dibujo.texto(pantalla, flotante.texto, dibujo.CHICA, flotante.color, flotante.x, flotante.y)

    def dibujar_temblor_y_destello(self, pantalla):
        if self.destello > 0:
            dibujo.oscurecer(pantalla, self.color_destello, 70)
        if self.temblor > 0:
            # Mueve toda la imagen unos pixeles (siempre en pasos de 2, estilo retro)
            copia = pantalla.copy()
            pantalla.fill(FONDO)
            pantalla.blit(copia, (random.randint(-3, 3) * 2, random.randint(-3, 3) * 2))
