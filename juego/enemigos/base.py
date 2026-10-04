"""
Clase base de los enemigos y su registro.

Patron "registro": cada tipo de enemigo es una clase con el decorador
@registrar_enemigo, que la anota en TIPOS_ENEMIGO con su nombre. El resto del
juego crea enemigos por nombre (crear_enemigos("perseguidor", partida)), asi que
para agregar un enemigo nuevo NO hay que tocar ningun otro archivo:

    1. Crear enemigos/mi_enemigo.py con una clase que herede de Enemigo.
    2. Ponerle @registrar_enemigo, un 'tipo' unico, un 'color', 'nombre' y 'pista'.
    3. Escribir mover(): como cambia su velocidad en cada paso.
    4. Importarlo en enemigos/__init__.py.
    5. Darle un costo en COSTO_ENEMIGO y un nivel en DESBLOQUEO_ENEMIGO (config.py).
    (Opcional) sprites/mi_enemigo.png: 2 cuadros de 'tamano' x 'tamano' (40 por defecto).
               Si no esta, se dibuja uno de respaldo.

Todo lo comun ya lo resuelve la clase base: la "X" de aviso al aparecer, el
congelado del hielo, los bordes, la animacion y el sprite de respaldo.
Opciones para cada tipo (atributos de la clase):
    tamano, radio          tamaño del dibujo y radio del circulo de daño
    destruible             el dash lo destruye (da 'puntos_dash' y llama a al_destruirse)
    muere_al_chocar        si te pega, se destruye (en vez de reaparecer lejos)
    crear()                si un "enemigo" son varios a la vez (como el enjambre)
"""
import math
import random

import pygame

from juego import recursos, dibujo, lienzo
from juego.config import (ALTO, BLANCO, HIELO, AMARILLO, AVISO_APARICION, DISTANCIA_APARICION, MS_CUADRO_ENEMIGO,
                          PUNTOS_ENEMIGO_CONGELADO, SEPARACION_ENEMIGOS, FUERZA_SEPARACION, RADIO_ENEMIGO,
                          COSTO_ENEMIGO, ENEMIGO_VELOCIDAD_MAX)

TIPOS_ENEMIGO = {}          # nombre -> clase


def registrar_enemigo(clase):
    # Decorador: anota la clase en el registro con su nombre
    if not clase.tipo:
        raise ValueError(clase.__name__ + " necesita un 'tipo'")
    TIPOS_ENEMIGO[clase.tipo] = clase
    return clase


def _clase(tipo):
    if tipo not in TIPOS_ENEMIGO:
        raise ValueError("No existe el enemigo '" + tipo + "'. Hay: " + ", ".join(TIPOS_ENEMIGO))
    return TIPOS_ENEMIGO[tipo]


def crear_enemigos(tipo, partida):
    # Lista con los enemigos nuevos de ese tipo (casi siempre uno; el enjambre son varios)
    return _clase(tipo).crear(partida)


def crear_enemigo(tipo, partida):
    # Un solo enemigo (para los tipos que son de a uno)
    return _clase(tipo)(partida)


def lugar_lejos_de_la_nave(nave, tamano):
    # Un lugar al azar lejos de la nave (y fuera del marcador de arriba)
    while True:
        nuevo_x = random.randint(0, lienzo.ancho - tamano)
        nuevo_y = random.randint(70, ALTO - tamano)
        if math.hypot(nuevo_x - nave.x, nuevo_y - nave.y) > DISTANCIA_APARICION:
            return nuevo_x, nuevo_y


def enemigo_respaldo(color, tamano=40):
    # Enemigo dibujado a mano (cuadrado con dos ojos), por si falta su sprite
    imagen = pygame.Surface((40, 40), pygame.SRCALPHA)
    pygame.draw.rect(imagen, color, (4, 4, 32, 32), 4)
    pygame.draw.rect(imagen, color, (12, 14, 6, 6))
    pygame.draw.rect(imagen, color, (22, 14, 6, 6))
    if tamano != 40:
        imagen = pygame.transform.scale(imagen, (tamano, tamano))
    return imagen


_cuadros = {}               # tipo -> cuadros de la animacion
_congelados = {}            # tipo -> imagen congelada


class Enemigo:
    tipo = None                 # nombre unico (lo usan el registro y config.py)
    nombre = ""                 # como se presenta la primera vez ("NUEVO ENEMIGO: ...")
    pista = "ESQUIVALO"         # consejo que se muestra al presentarlo
    color = BLANCO              # color de la "X" de aviso y del dibujo de respaldo
    archivo_sprite = None       # por defecto: tipo + ".png"
    tamano = 40                 # lado del dibujo (y de cada cuadro del sprite)
    radio = RADIO_ENEMIGO       # radio del circulo de daño
    rebota_en_bordes = False    # si no rebota, al tocar un borde se detiene
    destruible = False          # el dash lo destruye
    puntos_dash = 0             # puntos por destruirlo con el dash
    muere_al_chocar = False     # si te pega, se destruye (si no, reaparece lejos)
    de_oleada = False           # los de una oleada se van cuando termina
    esbirro = False             # es de un jefe (ej: las abejas de la Colmena): se va cuando lo vencen

    # ---------- Sprites (compartidos por todos los enemigos del mismo tipo) ----------

    @classmethod
    def cuadros(cls):
        if cls.tipo not in _cuadros:
            hoja = recursos.hoja(cls.archivo_sprite or cls.tipo + ".png", cls.tamano)
            _cuadros[cls.tipo] = hoja if hoja else cls.cuadros_de_respaldo()
        return _cuadros[cls.tipo]

    @classmethod
    def cuadros_de_respaldo(cls):
        # Para las subclases que quieran un dibujo de respaldo propio
        return [enemigo_respaldo(cls.color, cls.tamano)]

    @classmethod
    def imagen_congelado(cls):
        # Version azul del primer cuadro (no necesita sprite)
        if cls.tipo not in _congelados:
            _congelados[cls.tipo] = recursos.tenir(cls.cuadros()[0], HIELO)
        return _congelados[cls.tipo]

    # ---------- Ciclo de vida ----------

    @classmethod
    def crear(cls, partida):
        # Los enemigos nuevos de este tipo (el enjambre lo cambia para crear varios)
        return [cls(partida)]

    def __init__(self, partida):
        self.desfase = random.randint(0, 1000)      # para que no se animen todos al mismo tiempo
        self.costo = COSTO_ENEMIGO.get(self.tipo, 0)    # lo que ocupa del presupuesto del nivel
        self.naciendo = False       # recien nacido en un lugar (parpadea en vez de mostrar la X)
        self.aturdido_hasta = 0     # aturdido por una onda: quieto y sin lastimar hasta este momento
        self.reaparecer(partida)

    def reaparecer(self, partida):
        # Lejos de la nave; antes de aparecer se ve una "X" de aviso y no hace nada
        self.x, self.y = lugar_lejos_de_la_nave(partida.nave, self.tamano)
        self.vx, self.vy = 0, 0
        self.aparece_en = partida.tiempo + AVISO_APARICION
        self.naciendo = False
        self.aturdido_hasta = 0
        self.al_aparecer(partida)

    def nacer_en(self, partida, centro_x, centro_y, espera):
        # Aparecer en un lugar exacto (ej: al partirse un divisor). Durante 'espera' ms
        # parpadea y no hace daño, para que no te golpee apenas nace
        self.x, self.y = centro_x - self.tamano / 2, centro_y - self.tamano / 2
        self.aparece_en = partida.tiempo + espera
        self.naciendo = True

    def al_aparecer(self, partida):
        # Para las subclases: preparar su estado al (re)aparecer
        pass

    def al_destruirse(self, partida, con_dash):
        # Para las subclases: que pasa cuando lo destruyen (ej: el divisor se parte)
        pass

    def al_quitar(self, partida):
        # Para las subclases: se lo saca del juego por cualquier motivo (destruido,
        # fin de la oleada, cambio de sector...). Ej: el dron deja su bandada
        pass

    # ---------- Consultas ----------

    def activo(self, tiempo):
        return tiempo >= self.aparece_en

    def hace_danio(self):
        # Para las subclases: un enemigo que por un rato no lastima (ej: una abeja volviendo a casa)
        return True

    def aturdido(self, tiempo):
        return tiempo < self.aturdido_hasta

    def empujar(self, partida, desde_x, desde_y, distancia, ms_aturdido):
        # Una onda lo empuja lejos de (desde_x, desde_y) y lo deja aturdido
        centro_x, centro_y = self.centro()
        lejos_x, lejos_y = centro_x - desde_x, centro_y - desde_y
        largo = math.hypot(lejos_x, lejos_y) or 1
        self.x += lejos_x / largo * distancia
        self.y += lejos_y / largo * distancia
        self.vx, self.vy = 0, 0
        self.aturdido_hasta = partida.tiempo + ms_aturdido
        self._bordes()

    def centro(self):
        return self.x + self.tamano / 2, self.y + self.tamano / 2

    def caja(self):
        # Caja un poco mas chica que el dibujo (para recogerlo congelado o destruirlo con el dash)
        margen = self.tamano // 10
        return pygame.Rect(self.x + margen, self.y + margen, self.tamano - 2 * margen, self.tamano - 2 * margen)

    def rapidez(self, partida, base):
        # La velocidad 'base' ajustada al nivel y la dificultad, pero nunca mas rapida que
        # ENEMIGO_VELOCIDAD_MAX: la nave siempre puede escaparse de los que la persiguen
        return min(base * partida.factor_velocidad(), ENEMIGO_VELOCIDAD_MAX)

    def hacia_la_nave(self, partida):
        # Vector del enemigo a la nave y su largo
        nave_x, nave_y = partida.nave.centro()
        centro_x, centro_y = self.centro()
        dir_x, dir_y = nave_x - centro_x, nave_y - centro_y
        return dir_x, dir_y, math.hypot(dir_x, dir_y)

    # ---------- Movimiento ----------

    def actualizar(self, partida, congelado):
        if not self.activo(partida.tiempo) or congelado or self.aturdido(partida.tiempo):
            return
        self.naciendo = False
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
        limite_x, limite_y = lienzo.ancho - self.tamano, ALTO - self.tamano
        if self.x < 0 or self.x > limite_x:
            self.vx = -self.vx if self.rebota_en_bordes else 0
        if self.y < 0 or self.y > limite_y:
            self.vy = -self.vy if self.rebota_en_bordes else 0
        self.x = max(0, min(self.x, limite_x))
        self.y = max(0, min(self.y, limite_y))

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
        centro_x, centro_y = (int(c) for c in self.centro())
        if not self.activo(partida.tiempo):
            if self.naciendo:
                # Recien nacido: parpadea (todavia no hace daño)
                if dibujo.parpadeo(80):
                    self.dibujar_animado(pantalla)
                return
            # Aviso de aparicion: una X parpadeante del color del enemigo
            if dibujo.parpadeo(100):
                lado = max(6, round(self.tamano * 0.35))
                pygame.draw.line(pantalla, self.color, (centro_x - lado, centro_y - lado),
                                 (centro_x + lado, centro_y + lado), 4)
                pygame.draw.line(pantalla, self.color, (centro_x - lado, centro_y + lado),
                                 (centro_x + lado, centro_y - lado), 4)
            return
        restante_hielo = partida.restante("hielo")
        if restante_hielo > 0:
            # Congelado: azul y con los puntos que da encima (parpadea al final)
            if restante_hielo > 1000 or dibujo.parpadeo(100):
                pantalla.blit(self.imagen_congelado(), (self.x, self.y))
                dibujo.texto(pantalla, "+" + str(PUNTOS_ENEMIGO_CONGELADO), dibujo.CHICA, HIELO,
                             centro_x, self.y - 14)
            else:
                self.dibujar_animado(pantalla)
            return
        self.dibujar_cuerpo(pantalla, partida)
        if self.aturdido(partida.tiempo):
            self._dibujar_estrellitas(pantalla, centro_x, self.y - 6)

    def _dibujar_estrellitas(self, pantalla, centro_x, arriba):
        # Aturdido: tres estrellitas que giran sobre la cabeza (en saltos, estilo retro)
        vuelta = pygame.time.get_ticks() // 120
        for i in range(3):
            angulo = (vuelta + i * 3) % 8 * math.pi / 4
            punto_x = centro_x + round(math.cos(angulo) * self.tamano * 0.35 / 2) * 2
            punto_y = arriba + round(math.sin(angulo) * 2) * 2
            pantalla.fill(AMARILLO, (punto_x - 2, punto_y - 2, 4, 4))

    def dibujar_cuerpo(self, pantalla, partida):
        # Para las subclases que se dibujan distinto segun lo que estan haciendo
        self.dibujar_animado(pantalla)

    def dibujar_animado(self, pantalla):
        pantalla.blit(recursos.cuadro_animado(self.cuadros(), MS_CUADRO_ENEMIGO, self.desfase), (self.x, self.y))
