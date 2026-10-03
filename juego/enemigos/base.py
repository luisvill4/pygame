"""
Clase base de los enemigos y su registro.

Patron "registro": cada tipo de enemigo es una clase con el decorador
@registrar_enemigo, que la anota en TIPOS_ENEMIGO con su nombre. El resto del
juego crea enemigos por nombre (crear_enemigo("perseguidor", partida)), asi que
para agregar un enemigo nuevo NO hay que tocar ningun otro archivo:

    1. Crear enemigos/mi_enemigo.py con una clase que herede de Enemigo.
    2. Ponerle @registrar_enemigo, un 'tipo' unico y un 'color'.
    3. Escribir mover(): como cambia su velocidad en cada frame.
    4. Importarlo en enemigos/__init__.py.
    5. Usarlo en ENEMIGOS_POR_NIVEL o ENEMIGOS_POR_JEFE (config.py).
    (Opcional) sprites/mi_enemigo.png: 2 cuadros de 40x40. Si no esta, se dibuja uno de respaldo.

Todo lo comun ya lo resuelve la clase base: la "X" de aviso al aparecer, el
congelado del hielo, los bordes, la animacion y el sprite de respaldo.
"""
import math
import random

import pygame

from juego import recursos, dibujo
from juego.config import (BLANCO, HIELO, AVISO_APARICION, DISTANCIA_APARICION, MS_CUADRO_ENEMIGO,
                          PUNTOS_ENEMIGO_CONGELADO, SEPARACION_ENEMIGOS, FUERZA_SEPARACION)

TAMANO = 40

TIPOS_ENEMIGO = {}          # nombre -> clase


def registrar_enemigo(clase):
    # Decorador: anota la clase en el registro con su nombre
    if not clase.tipo:
        raise ValueError(clase.__name__ + " necesita un 'tipo'")
    TIPOS_ENEMIGO[clase.tipo] = clase
    return clase


def crear_enemigo(tipo, partida):
    if tipo not in TIPOS_ENEMIGO:
        raise ValueError("No existe el enemigo '" + tipo + "'. Hay: " + ", ".join(TIPOS_ENEMIGO))
    return TIPOS_ENEMIGO[tipo](partida)


def lugar_lejos_de_la_nave(nave):
    # Un lugar al azar lejos de la nave (y fuera del marcador de arriba)
    while True:
        nuevo_x = random.randint(0, 760)
        nuevo_y = random.randint(70, 560)
        if math.hypot(nuevo_x - nave.x, nuevo_y - nave.y) > DISTANCIA_APARICION:
            return nuevo_x, nuevo_y


def enemigo_respaldo(color):
    # Enemigo dibujado a mano (cuadrado con dos ojos), por si falta su sprite
    imagen = pygame.Surface((TAMANO, TAMANO), pygame.SRCALPHA)
    pygame.draw.rect(imagen, color, (4, 4, 32, 32), 4)
    pygame.draw.rect(imagen, color, (12, 14, 6, 6))
    pygame.draw.rect(imagen, color, (22, 14, 6, 6))
    return imagen


_cuadros = {}               # tipo -> cuadros de la animacion
_congelados = {}            # tipo -> imagen congelada


class Enemigo:
    tipo = None                 # nombre unico (lo usan el registro y config.py)
    color = BLANCO              # color de la "X" de aviso y del dibujo de respaldo
    archivo_sprite = None       # por defecto: tipo + ".png"
    rebota_en_bordes = False    # si no rebota, al tocar un borde se detiene

    # ---------- Sprites (compartidos por todos los enemigos del mismo tipo) ----------

    @classmethod
    def cuadros(cls):
        if cls.tipo not in _cuadros:
            hoja = recursos.hoja(cls.archivo_sprite or cls.tipo + ".png", TAMANO)
            _cuadros[cls.tipo] = hoja if hoja else [enemigo_respaldo(cls.color)]
        return _cuadros[cls.tipo]

    @classmethod
    def imagen_congelado(cls):
        # Version azul del primer cuadro (no necesita sprite)
        if cls.tipo not in _congelados:
            _congelados[cls.tipo] = recursos.tenir(cls.cuadros()[0], HIELO)
        return _congelados[cls.tipo]

    # ---------- Ciclo de vida ----------

    def __init__(self, partida):
        self.desfase = random.randint(0, 1000)      # para que no se animen todos al mismo tiempo
        self.reaparecer(partida)

    def reaparecer(self, partida):
        # Lejos de la nave; antes de aparecer se ve una "X" de aviso y no hace nada
        self.x, self.y = lugar_lejos_de_la_nave(partida.nave)
        self.vx, self.vy = 0, 0
        self.aparece_en = partida.tiempo + AVISO_APARICION
        self.al_aparecer(partida)

    def al_aparecer(self, partida):
        # Para las subclases: preparar su estado al (re)aparecer
        pass

    # ---------- Consultas ----------

    def activo(self, tiempo):
        return tiempo >= self.aparece_en

    def centro(self):
        return self.x + TAMANO / 2, self.y + TAMANO / 2

    def caja(self):
        # Caja un poco mas chica que el dibujo (para recogerlo congelado)
        return pygame.Rect(self.x + 4, self.y + 4, 32, 32)

    def hacia_la_nave(self, partida):
        # Vector del enemigo a la nave y su largo
        nave_x, nave_y = partida.nave.centro()
        centro_x, centro_y = self.centro()
        dir_x, dir_y = nave_x - centro_x, nave_y - centro_y
        return dir_x, dir_y, math.hypot(dir_x, dir_y)

    # ---------- Movimiento ----------

    def actualizar(self, partida, congelado):
        if not self.activo(partida.tiempo) or congelado:
            return
        self.mover(partida)
        paso = self.paso(partida)
        self.x += self.vx * paso
        self.y += self.vy * paso
        self._bordes()

    def mover(self, partida):
        # Para las subclases: cambiar self.vx / self.vy segun su comportamiento
        raise NotImplementedError

    def paso(self, partida):
        # Multiplicador de la velocidad al moverse (el rebotador se acelera con el nivel)
        return 1

    def _bordes(self):
        if self.x < 0 or self.x > 800 - TAMANO:
            self.vx = -self.vx if self.rebota_en_bordes else 0
        if self.y < 0 or self.y > 600 - TAMANO:
            self.vy = -self.vy if self.rebota_en_bordes else 0
        self.x = max(0, min(self.x, 800 - TAMANO))
        self.y = max(0, min(self.y, 600 - TAMANO))

    def separarse(self, partida):
        # Se aleja de los otros enemigos que tiene muy cerca (mas fuerte mientras mas cerca),
        # para que los que persiguen no terminen todos encimados en el mismo punto
        for otro in partida.enemigos:
            if otro is self or not otro.activo(partida.tiempo):
                continue
            lejos_x = self.x - otro.x
            lejos_y = self.y - otro.y
            distancia = math.hypot(lejos_x, lejos_y)
            if distancia >= SEPARACION_ENEMIGOS:
                continue
            if distancia == 0:
                # Justo en el mismo lugar: se separan hacia un lado al azar
                angulo_azar = random.uniform(0, 2 * math.pi)
                lejos_x, lejos_y, distancia = math.cos(angulo_azar), math.sin(angulo_azar), 1
            fuerza = (1 - distancia / SEPARACION_ENEMIGOS) * FUERZA_SEPARACION
            self.vx += lejos_x / distancia * fuerza
            self.vy += lejos_y / distancia * fuerza

    # ---------- Dibujo ----------

    def dibujar(self, pantalla, partida):
        centro_x, centro_y = int(self.x) + 20, int(self.y) + 20
        if not self.activo(partida.tiempo):
            # Aviso de aparicion: una X parpadeante del color del enemigo
            if dibujo.parpadeo(100):
                pygame.draw.line(pantalla, self.color, (centro_x - 14, centro_y - 14), (centro_x + 14, centro_y + 14), 4)
                pygame.draw.line(pantalla, self.color, (centro_x - 14, centro_y + 14), (centro_x + 14, centro_y - 14), 4)
            return
        restante_hielo = partida.restante("hielo")
        if restante_hielo > 0:
            # Congelado: azul y con los puntos que da encima (parpadea al final)
            if restante_hielo > 1000 or dibujo.parpadeo(100):
                pantalla.blit(self.imagen_congelado(), (self.x, self.y))
                dibujo.texto(pantalla, "+" + str(PUNTOS_ENEMIGO_CONGELADO), dibujo.CHICA, HIELO, centro_x, self.y - 14)
            else:
                self.dibujar_animado(pantalla)
            return
        self.dibujar_cuerpo(pantalla, partida)

    def dibujar_cuerpo(self, pantalla, partida):
        # Para las subclases que se dibujan distinto segun lo que estan haciendo
        self.dibujar_animado(pantalla)

    def dibujar_animado(self, pantalla):
        pantalla.blit(recursos.cuadro_animado(self.cuadros(), MS_CUADRO_ENEMIGO, self.desfase), (self.x, self.y))
