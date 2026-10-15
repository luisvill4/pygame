"""
Enjambre: ENJAMBRE_CANTIDAD drones chiquitos que vuelan juntos, en formacion.

- La Bandada es el "centro" del grupo: te sigue despacio, gira y la formacion se abre
  y se cierra (como si respirara). Cada dron vuela hacia su lugar en la formacion.
- Cada tanto se frena, los drones destellan en blanco (el aviso) y se lanza en
  PICADA contra la nave.
- El dash destruye los drones de a uno. Si destruis el enjambre entero con el dash,
  hay un bonus. Si un dron te choca, explota (se pierde).

En las rutas, un "enjambre" es una bandada entera (entra volando en su formacion).
Sprite (opcional): enjambre.png, 2 cuadros de 20x20.
"""
import math
import random

import pygame

from juego import dibujo, recursos
from juego.config import (ANCHO, CIAN, BLANCO, AMARILLO, ALTO, AVISO_APARICION, ENJAMBRE_CANTIDAD,
                          ENJAMBRE_VELOCIDAD, ENJAMBRE_PICADA, ENJAMBRE_ESPERA_PICADA, ENJAMBRE_PUNTOS,
                          ENJAMBRE_BONUS, ARCOIRIS)
from juego.enemigos.base import Enemigo, registrar_enemigo, lugar_lejos_de_la_nave

AVISO_PICADA = 450          # ms que destella antes de lanzarse
DURACION_PICADA = 600       # ms que dura la picada


class Bandada:
    # El centro del grupo y su comportamiento (no es un enemigo: no se dibuja ni choca)

    def __init__(self, partida):
        self.drones = []
        self.vx, self.vy = 0, 0
        self.angulo = random.uniform(0, 2 * math.pi)
        self.ultimo_paso = None         # para moverse una sola vez por paso (la llaman todos los drones)
        self.ubicada_en = None          # para reubicarse una sola vez cuando reaparecen todos
        self.todos_con_dash = True      # si todos los que murieron fueron con el dash (para el bonus)
        self.ubicar(partida)

    def ubicar(self, partida):
        # Un lugar nuevo lejos de la nave (al aparecer, o al volver despues del jefe)
        if self.ubicada_en == partida.tiempo:
            return
        self.ubicada_en = partida.tiempo
        self.x, self.y = lugar_lejos_de_la_nave(partida.nave, 80)
        self.x += 40
        self.y += 40
        self.vx, self.vy = 0, 0
        self.fase = "volar"             # volar, aviso o picada
        self.fase_hasta = 0
        self.proxima_picada = partida.tiempo + AVISO_APARICION + random.randint(*ENJAMBRE_ESPERA_PICADA)

    def radio_formacion(self, tiempo):
        if self.fase == "picada":
            return 16                   # en la picada van apretados
        return 30 + 12 * math.sin(tiempo / 350)

    def lugar(self, dron, tiempo):
        # Donde le toca estar a cada dron (repartidos en circulo, girando)
        indice = self.drones.index(dron)
        angulo = self.angulo + 2 * math.pi * indice / len(self.drones)
        radio = self.radio_formacion(tiempo)
        return self.x + math.cos(angulo) * radio, self.y + math.sin(angulo) * radio

    def actualizar(self, partida):
        ahora = partida.tiempo
        if self.ultimo_paso == ahora:
            return
        self.ultimo_paso = ahora
        nave_x, nave_y = partida.nave.centro()
        dir_x, dir_y = nave_x - self.x, nave_y - self.y
        distancia = math.hypot(dir_x, dir_y) or 1
        factor = partida.factor_velocidad()

        if self.fase == "volar":
            rapidez = ENJAMBRE_VELOCIDAD * factor
            self.vx += (dir_x / distancia * rapidez - self.vx) * 0.04
            self.vy += (dir_y / distancia * rapidez - self.vy) * 0.04
            if ahora >= self.proxima_picada:
                self.fase, self.fase_hasta = "aviso", ahora + AVISO_PICADA
                partida.sonidos.reproducir("enjambre_aviso", self.x)
        elif self.fase == "aviso":
            # Se frena y destella: va a lanzarse
            self.vx *= 0.85
            self.vy *= 0.85
            if ahora >= self.fase_hasta:
                self.fase, self.fase_hasta = "picada", ahora + DURACION_PICADA
                partida.sonidos.reproducir("enjambre_picada", self.x)
                self.vx = dir_x / distancia * ENJAMBRE_PICADA * factor
                self.vy = dir_y / distancia * ENJAMBRE_PICADA * factor
        elif ahora >= self.fase_hasta:      # termino la picada
            self.fase = "volar"
            self.vx *= 0.4
            self.vy *= 0.4
            self.proxima_picada = ahora + random.randint(*ENJAMBRE_ESPERA_PICADA)

        self.x = max(40, min(self.x + self.vx, ANCHO - 40))
        self.y = max(80, min(self.y + self.vy, ALTO - 40))
        self.angulo += 0.04


def dron_respaldo(alas_abiertas):
    # Dron de respaldo: un rombo con nucleo blanco y alitas (dibujado a 10x10 y agrandado x2)
    imagen = pygame.Surface((10, 10), pygame.SRCALPHA)
    pygame.draw.polygon(imagen, CIAN, [(5, 1), (8, 5), (5, 8), (2, 5)])
    imagen.fill(BLANCO, (4, 4, 2, 2))
    if alas_abiertas:
        imagen.fill(CIAN, (0, 4, 2, 2))
        imagen.fill(CIAN, (8, 4, 2, 2))
    else:
        imagen.fill(CIAN, (1, 5, 1, 2))
        imagen.fill(CIAN, (8, 5, 1, 2))
    return pygame.transform.scale(imagen, (20, 20))


_blancos = []               # dron en blanco (para el destello del aviso de picada)


@registrar_enemigo
class Dron(Enemigo):
    tipo = "enjambre"
    plural = "DRONES"
    nombre = "ENJAMBRE"
    pista = "¡DESTRUILOS CON EL DASH!"
    color = CIAN
    tamano = 20
    radio = 7
    destruible = True
    muere_al_chocar = True
    bonus_propio = True                 # (el de destruir el enjambre entero)
    puntos_dash = ENJAMBRE_PUNTOS

    @classmethod
    def crear(cls, partida):
        # Un enjambre son varios drones que comparten una bandada
        bandada = Bandada(partida)
        for _ in range(ENJAMBRE_CANTIDAD):
            bandada.drones.append(cls(partida, bandada))
        for dron in bandada.drones:             # cada uno con su X en su lugar de la formacion
            lugar_x, lugar_y = bandada.lugar(dron, partida.tiempo)
            dron.x, dron.y = lugar_x - dron.tamano / 2, lugar_y - dron.tamano / 2
        return list(bandada.drones)

    @classmethod
    def cuadros_de_respaldo(cls):
        return [dron_respaldo(True), dron_respaldo(False)]

    def __init__(self, partida, bandada):
        self.bandada = bandada              # (antes de super: reaparecer() la usa)
        super().__init__(partida)

    def reaparecer(self, partida):
        # Aparece (con su X) en su lugar de la formacion
        super().reaparecer(partida)
        self.bandada.ubicar(partida)
        if self in self.bandada.drones:
            lugar_x, lugar_y = self.bandada.lugar(self, partida.tiempo)
        else:
            lugar_x, lugar_y = self.bandada.x, self.bandada.y
        self.x, self.y = lugar_x - self.tamano / 2, lugar_y - self.tamano / 2

    def al_entrar(self, partida, hasta):
        # El centro de la bandada queda donde termina de entrar el grupo, y la primera picada
        # se cuenta desde que llego (no desde que se vio la flecha)
        # ('hasta' es el lugar de este dron: el centro esta a la misma distancia que ahora)
        bandada = self.bandada
        lugar_x, lugar_y = bandada.lugar(self, partida.tiempo)
        bandada.x += hasta[0] - lugar_x
        bandada.y += hasta[1] - lugar_y
        bandada.proxima_picada = self.aparece_en + random.randint(*ENJAMBRE_ESPERA_PICADA)

    def _dibujar_aviso_de_entrada(self, pantalla):
        # Una sola flecha por enjambre (la del primer dron), no cinco encimadas
        if self.bandada.drones and self.bandada.drones[0] is self:
            super()._dibujar_aviso_de_entrada(pantalla)

    def mover(self, partida):
        # Vuela hacia su lugar en la formacion (como un resorte)
        self.bandada.actualizar(partida)
        lugar_x, lugar_y = self.bandada.lugar(self, partida.tiempo)
        centro_x, centro_y = self.centro()
        deseada_x = max(-9, min((lugar_x - centro_x) * 0.25, 9))
        deseada_y = max(-9, min((lugar_y - centro_y) * 0.25, 9))
        self.vx += (deseada_x - self.vx) * 0.5
        self.vy += (deseada_y - self.vy) * 0.5

    def al_destruirse(self, partida, con_dash):
        bandada = self.bandada
        if not con_dash:
            bandada.todos_con_dash = False
        # ¿Era el ultimo y cayeron todos con el dash? Bonus
        if con_dash and bandada.todos_con_dash and bandada.drones == [self]:
            ganados = partida.sumar_puntos(ENJAMBRE_BONUS)
            centro_x, centro_y = self.centro()
            partida.efectos.anillo(centro_x, centro_y, ARCOIRIS, 24, 5, 3)
            partida.efectos.texto_flotante("¡ENJAMBRE DESTRUIDO! +" + str(ganados), centro_x, centro_y - 30, AMARILLO)
            partida.sonidos.reproducir_luego("bonus", 120, centro_x)

    def al_quitar(self, partida):
        # Ya no es parte de la bandada (los demas se reparten su lugar)
        if self in self.bandada.drones:
            self.bandada.drones.remove(self)

    def dibujar_cuerpo(self, pantalla, partida):
        if self.bandada.fase == "aviso" and dibujo.parpadeo(60):
            if not _blancos:
                _blancos.append(recursos.blanquear(self.cuadros()[0]))
            dibujo.pegar(pantalla, _blancos[0], self.x, self.y)
        else:
            self.dibujar_animado(pantalla)
