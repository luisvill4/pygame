"""
Efectos visuales: particulas, textos flotantes ("+1"), temblor y destello de pantalla.

Particulas al estilo retro: cuadrados alineados a una cuadricula de 2 px que NO se
desvanecen con transparencia, sino que cambian de color por etapas segun una paleta
(ver las paletas en config.py). Los textos flotantes hacen lo mismo al apagarse.

Textos flotantes: nacen blancos (un golpe de luz), suben frenando, nunca se pisan
(uno nuevo se apila arriba del que ya estaba ahi) y no se salen de la pantalla ni se
meten en el HUD.

Ondas de choque: anillos que crecen frenando y se apagan por etapas de color (los
impactos fuertes: romper enemigos, pegarle al jefe, la NOVA...). fogonazo(): el destello
chico donde nace una bala de un jefe.

Las chispas grandes y brillantes tienen un resplandor de neon (dibujo.halo, respeta
la opcion NEON).

Temblor y destello respetan las opciones de accesibilidad (accesibilidad.py). El
temblor se sortea en cada paso de logica y no en cada cuadro: asi tiembla igual a
30 o a 144 FPS.
"""
import math
import random

import pygame

from juego import dibujo, recursos, accesibilidad
from juego.config import ANCHO, BLANCO, FONDO, FUEGO, CONTORNO, PIXEL_ARTE

# Textos flotantes
VIDA_TEXTO = 50             # pasos que se ve cada uno
BLANCO_TEXTO = 3            # los primeros pasos se ve blanco y despues toma su color
APAGADO_TEXTO = 12          # en sus ultimos pasos se apaga en dos etapas (sin titilar)
SUBIDA_TEXTO = 2.6          # px por paso que sube al nacer...
FRENO_TEXTO = 0.93          # ...y cuanto conserva de esa velocidad en cada paso
ZONA_TEXTOS = pygame.Rect(8, 112, ANCHO - 16, 400)      # donde pueden estar (fuera del HUD)
SEPARACION_TEXTOS = 2       # px entre dos textos apilados
# Temblor: en los ultimos pasos se va calmando
CALMA_TEMBLOR = 8
MAXIMO_RESPLANDORES = 70    # chispas con resplandor por cuadro, como mucho (no gastar de mas)


class Particula:
    __slots__ = ("x", "y", "vx", "vy", "paleta", "vida", "vida_inicial", "tamano", "gravedad")

    def __init__(self, x, y, vx, vy, paleta, vida, tamano, gravedad=0):
        self.x, self.y = x, y               # posicion
        self.vx, self.vy = vx, vy           # velocidad
        self.paleta = paleta                # colores por los que va pasando
        self.vida = vida                    # frames que le quedan
        self.vida_inicial = vida
        self.tamano = tamano                # lado del cuadrado en pixeles
        self.gravedad = gravedad            # cuanto acelera hacia abajo por frame (0 = flota)


class OndaDeChoque:
    __slots__ = ("x", "y", "radio", "color", "vida", "vida_inicial")

    def __init__(self, x, y, radio, color, pasos):
        self.x, self.y, self.radio, self.color = x, y, radio, color
        self.vida = self.vida_inicial = pasos

    def dibujar(self, pantalla):
        # Crece rapido y frena; blanca al nacer, despues de su color y al final oscura
        avance = 1 - self.vida / self.vida_inicial
        radio = round(self.radio * (1 - (1 - avance) ** 2)) // 2 * 2
        if avance < 0.25:
            color = BLANCO
        elif avance < 0.6:
            color = self.color
        else:
            color = tuple(round(c + (f - c) * 0.55) for c, f in zip(self.color, FONDO))
        bloque = 4 if avance < 0.35 else 2
        if radio <= bloque:
            return
        # El anillo hecho de bloques en la grilla de pixeles de arte (un circulo de pygame
        # tiene escalones de 1 px: se veia mas fino que los sprites)
        centro_x, centro_y = dibujo.en_grilla(self.x), dibujo.en_grilla(self.y)
        puntos = max(8, int(2 * math.pi * radio / PIXEL_ARTE))
        hechos = set()
        for i in range(puntos):
            angulo = 2 * math.pi * i / puntos
            lugar = (dibujo.en_grilla(centro_x + math.cos(angulo) * radio - bloque / 2),
                     dibujo.en_grilla(centro_y + math.sin(angulo) * radio - bloque / 2))
            if lugar not in hechos:
                hechos.add(lugar)
                pantalla.fill(color, (lugar[0], lugar[1], bloque, bloque))


class TextoFlotante:
    __slots__ = ("texto", "x", "y", "color", "vida", "vy", "ancho", "alto")

    def __init__(self, texto, x, y, color):
        self.texto, self.x, self.y, self.color = texto, x, y, color   # (x, y) = el centro
        self.vida = VIDA_TEXTO
        self.vy = -SUBIDA_TEXTO
        self.ancho, self.alto = recursos.fuente(dibujo.CHICA).size(texto)

    def caja(self):
        caja = pygame.Rect(0, 0, self.ancho, self.alto)
        caja.center = (self.x, self.y)
        return caja

    def color_actual(self):
        # Blanco al nacer, despues su color y al final dos etapas cada vez mas oscuras
        if self.vida > VIDA_TEXTO - BLANCO_TEXTO:
            return BLANCO
        if self.vida > APAGADO_TEXTO:
            return self.color
        oscuridad = 0.45 if self.vida > APAGADO_TEXTO // 2 else 0.75
        return tuple(round(c + (f - c) * oscuridad) for c, f in zip(self.color, FONDO))


class Efectos:
    def __init__(self):
        self.particulas = []
        self.ondas = []             # ondas de choque (OndaDeChoque)
        self.textos = []
        self.temblor = 0            # frames que le quedan al temblor de pantalla
        self.desplazamiento = (0, 0)    # cuanto esta corrida la imagen en este paso (temblor)
        self.destello = 0           # frames que le quedan al destello de color
        self.color_destello = BLANCO

    def reiniciar(self):
        self.particulas.clear()
        self.ondas.clear()
        self.textos.clear()
        self.temblor, self.destello = 0, 0
        self.desplazamiento = (0, 0)

    # ---------- Crear ----------

    def particula(self, x, y, vx, vy, paleta, vida, tamano, gravedad=0):
        self.particulas.append(Particula(x, y, vx, vy, paleta, vida, tamano, gravedad))

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

    def pedazos(self, cx, cy, paleta, cantidad, fuerza):
        # Trozos grandes que saltan hacia arriba y caen (algo que se rompe: un cañon, una coraza)
        for _ in range(cantidad):
            self.particula(cx + random.randint(-8, 8), cy + random.randint(-8, 8),
                           random.uniform(-fuerza, fuerza), random.uniform(-fuerza, fuerza * 0.3),
                           paleta, random.randint(40, 60), random.choice([6, 8]), gravedad=0.35)

    def onda_de_choque(self, x, y, radio, color, pasos=18):
        self.ondas.append(OndaDeChoque(x, y, radio, color, pasos))

    def fogonazo(self, x, y, color):
        # El destello donde nace una bala: un anillo chico y unas chispas que se apagan rapido
        self.onda_de_choque(x, y, 16, color, 8)
        for _ in range(4):
            direccion = random.uniform(0, 2 * math.pi)
            self.particula(x, y, math.cos(direccion) * 2, math.sin(direccion) * 2, [color, BLANCO], 7, 4)

    def texto_flotante(self, mensaje, x, y, color):
        nuevo = TextoFlotante(mensaje, x, y, color)
        # Adentro de la zona de juego (ni cortado en un borde ni encima del HUD)
        caja = nuevo.caja().clamp(ZONA_TEXTOS)
        nuevo.x, nuevo.y = caja.center
        # Si cae encima de otro, se apila arriba; si arriba no hay lugar, abajo
        if not self._apilar(nuevo, -1):
            nuevo.y = caja.centery
            self._apilar(nuevo, 1)
        self.textos.append(nuevo)

    def _apilar(self, nuevo, direccion):
        # Corre 'nuevo' (direccion -1 = arriba, 1 = abajo) hasta que no toque a ningun texto.
        # Devuelve False si para eso tendria que salirse de la zona
        for _ in range(len(self.textos) + 1):
            caja = nuevo.caja()
            tocado = next((t for t in self.textos if t.caja().colliderect(caja)), None)
            if tocado is None:
                return ZONA_TEXTOS.contains(caja)
            otra = tocado.caja()
            if direccion < 0:
                nuevo.y = otra.top - SEPARACION_TEXTOS - nuevo.alto / 2
            else:
                nuevo.y = otra.bottom + SEPARACION_TEXTOS + nuevo.alto / 2
        return False

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
            particula.vy = particula.vy * 0.92 + particula.gravedad
            particula.vida -= 1
            if particula.vida <= 0:
                self.particulas.remove(particula)
        for onda in self.ondas:
            onda.vida -= 1
        self.ondas = [onda for onda in self.ondas if onda.vida > 0]
        # Los textos suben frenando y nunca se atraviesan: de arriba hacia abajo, cada uno
        # frena debajo del que tiene encima (como cajas apiladas) y ninguno se mete en el HUD
        ordenados = sorted(self.textos, key=lambda texto: texto.y)
        for i, flotante in enumerate(ordenados):
            techo = ZONA_TEXTOS.top
            caja = flotante.caja()
            for otro in ordenados[:i]:
                otra = otro.caja()
                if otra.right > caja.left and otra.left < caja.right:      # uno arriba del otro
                    techo = max(techo, otra.bottom + SEPARACION_TEXTOS)
            flotante.y = max(flotante.y + flotante.vy, techo + flotante.alto / 2)
            flotante.vy *= FRENO_TEXTO
            flotante.vida -= 1
        self.textos = [flotante for flotante in self.textos if flotante.vida > 0]
        # El temblor y el destello duran pasos de logica (no cuadros dibujados),
        # asi duran lo mismo a cualquier FPS
        if self.destello > 0:
            self.destello -= 1
        self.desplazamiento = (0, 0)
        if self.temblor > 0:
            self.temblor -= 1
            # Cuanto se corre la imagen en este paso (en pasos de 2 px, estilo retro).
            # Los ultimos pasos se calma; con TEMBLOR NO, no se mueve
            maximo = math.ceil(accesibilidad.temblor_maximo() * min(1, self.temblor / CALMA_TEMBLOR))
            self.desplazamiento = (random.randint(-maximo, maximo) * 2, random.randint(-maximo, maximo) * 2)

    def dibujar(self, pantalla):
        # Primero el resplandor de las chispas grandes (como mucho MAXIMO_RESPLANDORES),
        # despues las chispas, las ondas y los textos
        dibujadas = []
        resplandores = 0
        for particula in self.particulas:
            # El color y el tamaño bajan por etapas segun la vida que le queda
            fraccion = particula.vida / particula.vida_inicial
            paleta = particula.paleta
            color = paleta[min(int(fraccion * len(paleta)), len(paleta) - 1)]
            # (de a pixeles de arte: nunca mas fina que los sprites)
            tamano = max(PIXEL_ARTE, math.ceil(particula.tamano * fraccion / PIXEL_ARTE) * PIXEL_ARTE)
            if tamano >= 4 and fraccion > 0.5 and resplandores < MAXIMO_RESPLANDORES:
                dibujo.halo(pantalla, particula.x + tamano / 2 - 1, particula.y + tamano / 2 - 1, tamano * 2 + 8,
                            color, 0.7)
                resplandores += 1
            dibujadas.append((color, tamano, particula))
        for color, tamano, particula in dibujadas:
            # En la grilla de pixeles de arte, como los sprites
            pantalla.fill(color, (dibujo.en_grilla(particula.x), dibujo.en_grilla(particula.y), tamano, tamano))
        for onda in self.ondas:
            onda.dibujar(pantalla)
        for flotante in self.textos:
            dibujo.texto(pantalla, flotante.texto, dibujo.CHICA, flotante.color_actual(),
                         int(flotante.x) // 2 * 2, int(flotante.y) // 2 * 2, sombra=CONTORNO, contorno=CONTORNO)

    def dibujar_temblor_y_destello(self, pantalla):
        # Va despues de dibujar el mundo y antes del HUD: el HUD no tiembla ni se tiñe
        if self.destello > 0 and not accesibilidad.destellos_reducidos():
            dibujo.oscurecer(pantalla, self.color_destello, 70)
        dx, dy = self.desplazamiento
        if dx or dy:
            # Corre la imagen y tapa con el fondo la franja que quedo descubierta
            ancho, alto = pantalla.get_size()
            pantalla.scroll(dx, dy)
            if dx:
                pantalla.fill(FONDO, (0 if dx > 0 else ancho + dx, 0, abs(dx), alto))
            if dy:
                pantalla.fill(FONDO, (0, 0 if dy > 0 else alto + dy, ancho, abs(dy)))
