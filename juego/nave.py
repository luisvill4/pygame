"""
La nave del jugador: fisica con inercia, giro suavizado, dash y su dibujo.

Angulos: 0 = arriba, 90 = izquierda (como pygame.transform.rotate).
La nave mide 50x50; (x, y) es su esquina de arriba a la izquierda.
"""
import math

import pygame

from juego import recursos
from juego.dibujo import parpadeo, pegar
from juego.config import (ANCHO, ALTO, CIAN, ENERGIA, MS_CUADRO_ESCUDO, NAVE_ACELERACION,
                          NAVE_FRICCION, NAVE_FRENADO, NAVE_VELOCIDAD_GIRO, DASH_FUERZA, DASH_DURACION,
                          BUFFER_DASH, RADIO_NAVE)

TAMANO = 50
PASOS_GIRO = 72             # angulos distintos que se guardan (cada 5 grados)
ESCALONES_INCLINACION = 4   # inclinaciones distintas que se guardan

_imagenes = {}      # equipo -> {nombre: imagen}; se arman la primera vez que se usan
_giradas = {}       # (equipo, nombre, paso de angulo, escalon de inclinacion) -> imagen girada (ver girada)
_color = [None]     # color de la nave elegida (None = el del sprite). Ver NAVES en config.py
_equipo = [()]      # las piezas que lleva encima (el modo historia: historia/modulos.py)


def cambiar_color(color):
    # Otra nave (se desbloquean con logros): las imagenes se vuelven a armar con ese color
    _color[0] = color
    _imagenes.clear()
    _giradas.clear()


def _clave(capas):
    # Las capas como algo que sirve de clave (cada equipo guarda sus imagenes y sus giros)
    return tuple((tuple(pixeles), tuple(color), solo_casco) for pixeles, color, solo_casco in capas)


def cambiar_equipo(capas):
    # Las piezas que lleva la nave: [(pixeles, color, solo_sobre_el_casco), ...], con los pixeles
    # en la grilla de pixeles de arte (25 x 25). () = la nave limpia (el arcade). No borra nada:
    # cada equipo tiene sus imagenes, asi volver a uno ya visto no recalcula los giros
    _equipo[0] = _clave(capas)


def armar(capas):
    # La nave con esas piezas encima (para mostrar una antes de comprarla, como en el hangar)
    clave = _clave(capas)
    if clave not in _imagenes:
        nave = recursos.sprite_obligatorio("nave.png")
        if _color[0] is not None:
            nave = recursos.tenir(nave, _color[0])
        nave = _con_piezas(nave, clave)
        icono = pygame.transform.scale(nave, (25, 25))
        icono_vacio = icono.copy()
        icono_vacio.set_alpha(40)
        _imagenes[clave] = {"nave": nave, "icono": icono, "icono_vacio": icono_vacio,
                            "fantasma": recursos.tenir(nave, CIAN)}
    return _imagenes[clave]["nave"]


def _con_piezas(base, clave):
    # Pinta cada pixel de arte (2x2) de las piezas. Las 'solo_sobre_el_casco' (placas, panal)
    # solo pintan donde ya hay nave y no es el contorno negro
    nave = base.copy()
    for pixeles, color, solo_casco in clave:
        for columna, fila in pixeles:
            x, y = columna * 2, fila * 2
            if not (0 <= x < TAMANO and 0 <= y < TAMANO):
                continue
            if solo_casco:
                rojo, verde, azul, alfa = nave.get_at((x, y))
                if alfa < 128 or rojo + verde + azul < 60:
                    continue
            nave.fill(color, (x, y, 2, 2))
    return nave


def imagen(nombre="nave"):
    # "nave", "icono" (vidas del HUD), "icono_vacio" y "fantasma" (estela del dash), con el equipo actual
    armar(_equipo[0])
    return _imagenes[_equipo[0]][nombre]


def girada(nombre, angulo, inclinacion=0):
    # La imagen girada sin romper el pixel art (un metodo tipo "RotSprite"): se agranda
    # 8 veces con Scale2x (redondea los bordes sin inventar colores), se gira, y se
    # achica tomando el pixel del centro de cada bloque de 8x8. Con rotate() directo, los
    # pixeles salian torcidos y de distinto tamaño. Cada angulo (de a 5 grados) e
    # inclinacion se calcula una sola vez y se guarda
    paso = round(angulo / (360 / PASOS_GIRO)) % PASOS_GIRO
    escalon = round(inclinacion * ESCALONES_INCLINACION)
    clave = (_equipo[0], nombre, paso, escalon)
    if clave not in _giradas:
        base = imagen(nombre)
        if escalon:
            # Al ladearse se ve mas angosta (hasta un 35%)
            ancho = round(TAMANO * (1 - escalon / ESCALONES_INCLINACION * 0.35))
            base = pygame.transform.scale(base, (ancho, TAMANO))
        grande = pygame.transform.scale2x(pygame.transform.scale2x(pygame.transform.scale2x(base)))
        grande = pygame.transform.rotate(grande, paso * 360 / PASOS_GIRO)
        ancho, alto = grande.get_size()
        con_margen = pygame.Surface((ancho + 8, alto + 8), pygame.SRCALPHA)
        con_margen.blit(grande, (0, 0))
        centros = con_margen.subsurface((4, 4, ancho // 8 * 8, alto // 8 * 8))
        _giradas[clave] = pygame.transform.scale(centros, (ancho // 8, alto // 8))
    return _giradas[clave]


def preparar_giros(cantidad):
    # Calcula de antemano 'cantidad' giros que todavia no estan guardados (primero los de
    # la nave derecha, despues los ladeados y los fantasmas del dash). Se llama de a poco
    # desde los menus, asi en la partida ninguno se calcula por primera vez (~4 ms cada uno)
    for escalon in range(ESCALONES_INCLINACION + 1):
        for nombre in ("nave", "fantasma"):
            if nombre == "fantasma" and escalon:
                continue
            for paso in range(PASOS_GIRO):
                if (_equipo[0], nombre, paso, escalon) in _giradas:
                    continue
                girada(nombre, paso * 360 / PASOS_GIRO, escalon / ESCALONES_INCLINACION)
                cantidad -= 1
                if cantidad <= 0:
                    return


class Nave:
    def __init__(self, x=100, y=200):
        self.x, self.y = x, y
        self.vx, self.vy = 0, 0             # velocidad actual
        self.angulo = 0                     # angulo con el que se dibuja
        self.angulo_objetivo = 0            # angulo al que queremos llegar
        self.inclinacion = 0                # 0 = recta, 1 = totalmente ladeada al girar
        self.acelerando = False             # si en este frame se pidio moverse
        self.invulnerable_hasta = 0         # despues de un golpe parpadea y no recibe daño
        self.dash_hasta = 0                 # el dash esta activo hasta este momento
        self.dash_listo = 0                 # desde este momento se puede volver a usar
        self.dash_pedido_en = -10000        # ultima vez que se apreto el dash (para el buffer)
        self.dash_avisado = True            # si ya destello avisando que el dash esta listo
        self.duracion_dash = DASH_DURACION  # ms que dura cada dash (la mejora COMETA lo alarga)
        self.dash_extra_max = 0             # dashes seguidos de mas (la mejora DOBLE DASH)
        self.dash_extra = 0                 # los que quedan: se recargan junto con el dash
        self.fantasmas = []                 # copias que deja el dash: [x, y, angulo, vida]

    # ---------- Consultas ----------

    def centro(self):
        return self.x + TAMANO / 2, self.y + TAMANO / 2

    def caja_recoger(self):
        # Caja grande para recoger cosas (el daño usa el circulo, mas chico)
        return pygame.Rect(self.x, self.y, TAMANO, TAMANO)

    def toca_circulo(self, centro_x, centro_y, radio):
        # Choque entre el circulo de daño de la nave y otro circulo
        cx, cy = self.centro()
        return math.hypot(cx - centro_x, cy - centro_y) < RADIO_NAVE + radio

    def toca_rect(self, rect):
        # Choque entre el circulo de daño de la nave y un rectangulo:
        # se busca el punto del rectangulo mas cercano al centro de la nave
        cx, cy = self.centro()
        cerca_x = max(rect.left, min(cx, rect.right))
        cerca_y = max(rect.top, min(cy, rect.bottom))
        return math.hypot(cx - cerca_x, cy - cerca_y) < RADIO_NAVE

    def en_dash(self, tiempo):
        return tiempo < self.dash_hasta

    def invulnerable(self, tiempo):
        return tiempo < self.invulnerable_hasta

    def atraviesa(self, tiempo):
        # El dash y la invulnerabilidad atraviesan enemigos, balas y al jefe
        return self.en_dash(tiempo) or self.invulnerable(tiempo)

    def empujon(self, desde_x, desde_y, fuerza=10):
        # Velocidad que aleja a la nave del punto (desde_x, desde_y)
        cx, cy = self.centro()
        empuje_x, empuje_y = cx - desde_x, cy - desde_y
        largo = math.hypot(empuje_x, empuje_y)
        if largo == 0:
            return 0, -fuerza
        return empuje_x / largo * fuerza, empuje_y / largo * fuerza

    # ---------- Cada frame ----------

    def actualizar(self, tiempo, dx, dy, pidio_dash, vel_max, recarga_dash, efectos):
        self.acelerando = dx != 0 or dy != 0
        if self.acelerando:
            # Apunta hacia donde presionas (0 = arriba, 90 = izquierda...)
            self.angulo_objetivo = math.degrees(math.atan2(-dx, -dy)) % 360

        self._dash(tiempo, dx, dy, pidio_dash, recarga_dash, efectos)

        if self.en_dash(tiempo):
            # Durante el dash no hay control: la nave sigue disparada y deja copias
            self.fantasmas.append([self.x, self.y, self.angulo, 10])
        elif self.acelerando:
            self._acelerar(dx, dy, vel_max)
        else:
            # Al soltar la nave se desliza un poco antes de frenar
            self.vx *= NAVE_FRICCION
            self.vy *= NAVE_FRICCION
        self.x += self.vx
        self.y += self.vy

        # Giro suave: rapido al empezar y mas lento al llegar al angulo
        diferencia = (self.angulo_objetivo - self.angulo + 180) % 360 - 180
        giro = max(-NAVE_VELOCIDAD_GIRO, min(diferencia * 0.25, NAVE_VELOCIDAD_GIRO))
        self.angulo = (self.angulo + giro) % 360
        # Inclinacion: mientras mas rapido gira, mas se ladea
        self.inclinacion += (min(abs(giro) / NAVE_VELOCIDAD_GIRO, 1) - self.inclinacion) * 0.2

        # Las copias del dash se van apagando
        for fantasma in self.fantasmas[:]:
            fantasma[3] -= 1
            if fantasma[3] <= 0:
                self.fantasmas.remove(fantasma)

        # Limites de la pantalla (al chocar con un borde se pierde esa velocidad)
        if self.x < 0 or self.x > ANCHO - TAMANO:
            self.vx = 0
        if self.y < 0 or self.y > ALTO - TAMANO:
            self.vy = 0
        self.x = max(0, min(self.x, ANCHO - TAMANO))
        self.y = max(0, min(self.y, ALTO - TAMANO))

    def _acelerar(self, dx, dy, vel_max):
        # Inercia: la velocidad se acerca poco a poco a la deseada. Se separa en dos partes:
        #   avance: lo que ya va hacia donde apretas
        #   deriva: lo que va de costado
        # Arrancar es suave (NAVE_ACELERACION), pero lo que va "para otro lado" (ir hacia
        # atras o de costado) se corrige mas fuerte (NAVE_FRENADO): asi la nave dobla y
        # frena enseguida, sin perder la sensacion de inercia
        largo = math.hypot(dx, dy)          # asi en diagonal no va mas rapido
        dir_x, dir_y = dx / largo, dy / largo
        avance = self.vx * dir_x + self.vy * dir_y
        deriva_x = self.vx - avance * dir_x
        deriva_y = self.vy - avance * dir_y
        fuerza = NAVE_FRENADO if avance < 0 else NAVE_ACELERACION
        avance += (vel_max - avance) * fuerza
        deriva_x *= 1 - NAVE_FRENADO
        deriva_y *= 1 - NAVE_FRENADO
        self.vx = avance * dir_x + deriva_x
        self.vy = avance * dir_y + deriva_y

    def dash_disponible(self, tiempo):
        # Se puede usar si ya se recargo, o si quedan dashes extra (y no esta en medio de uno)
        if self.en_dash(tiempo):
            return False
        return tiempo >= self.dash_listo or self.dash_extra > 0

    def _dash(self, tiempo, dx, dy, pidio_dash, recarga_dash, efectos):
        # Impulso hacia donde presionas (o hacia donde mira la nave).
        # Si lo apretas justo antes de que se recargue, se guarda y sale apenas este listo
        cx, cy = self.centro()
        if tiempo >= self.dash_listo:
            self.dash_extra = self.dash_extra_max       # recargado: vuelven los dashes extra
        if pidio_dash:
            self.dash_pedido_en = tiempo
        if tiempo - self.dash_pedido_en <= BUFFER_DASH and self.dash_disponible(tiempo):
            self.dash_pedido_en = -10000
            if tiempo >= self.dash_listo:
                self.dash_listo = tiempo + recarga_dash
                self.dash_avisado = False
            else:
                self.dash_extra -= 1                    # uno extra: no reinicia la recarga
            if self.acelerando:
                largo = math.hypot(dx, dy)
                dash_x, dash_y = dx / largo, dy / largo
            else:
                dash_x = -math.sin(math.radians(self.angulo))
                dash_y = -math.cos(math.radians(self.angulo))
            self.vx, self.vy = dash_x * DASH_FUERZA, dash_y * DASH_FUERZA
            self.dash_hasta = tiempo + self.duracion_dash
            efectos.anillo(cx, cy, ENERGIA, 16, 3, 2)
        elif tiempo >= self.dash_listo and not self.dash_avisado:
            # Destello chico en la nave: el dash ya esta listo
            self.dash_avisado = True
            efectos.anillo(cx, cy, ENERGIA, 12, 3, 2)

    def estela(self, tiempo, vel_max, efectos):
        # Fuego del motor al moverse: mas al arrancar que cuando ya va a toda velocidad
        if not self.acelerando or self.en_dash(tiempo):
            return
        cx, cy = self.centro()
        if math.hypot(self.vx, self.vy) < vel_max * 0.8:
            efectos.estela(cx, cy, self.angulo, 3)
        else:
            efectos.estela(cx, cy, self.angulo, 2)

    # ---------- Dibujo ----------

    def dibujar_fantasmas(self, pantalla):
        # Copias cian de la nave que deja el dash; se apagan poco a poco
        for fantasma in self.fantasmas:
            copia = girada("fantasma", fantasma[2]).copy()     # (copia: la girada esta guardada)
            copia.set_alpha(fantasma[3] * 18)
            pegar(pantalla, copia, fantasma[0] + 25, fantasma[1] + 25, centrado=True)

    def dibujar(self, pantalla, tiempo, restante_escudo):
        cx, cy = self.centro()
        # Escudo: burbuja alrededor de la nave (parpadea cuando se esta acabando)
        if restante_escudo > 0 and (restante_escudo > 1500 or parpadeo(100)):
            cuadros = recursos.hoja("escudo.png", 76)
            if cuadros:
                burbuja = recursos.cuadro_animado(cuadros, MS_CUADRO_ESCUDO)
                pegar(pantalla, burbuja, cx, cy, centrado=True)
            else:
                pygame.draw.circle(pantalla, CIAN, (int(cx), int(cy)), 36, 3)
        # Si es invulnerable, parpadea
        if self.invulnerable(tiempo) and not parpadeo(60):
            return
        # Girada (y mas angosta si esta ladeada) sin romper el pixel art: ver girada()
        dibujo_nave = girada("nave", self.angulo, self.inclinacion)
        # Casi quieta, flota subiendo y bajando de a 2 pixeles
        flotar = 0
        if math.hypot(self.vx, self.vy) < 1:
            flotar = round(math.sin(pygame.time.get_ticks() / 250)) * 2
        pegar(pantalla, dibujo_nave, cx, cy + flotar, centrado=True)
