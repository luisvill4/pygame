"""
Haptica: la vibracion del mando, con "patrones" en vez de un zumbido parejo.

Se usan los dos motores grandes del mando:
- grave: el de la izquierda, pesado (golpes fuertes, el latido del jefe).
- agudo: el de la derecha, un zumbido fino y mas suave (premios, chispas).
(Los gatillos del mando de Xbox tambien vibran, pero se sentia muy brusco: no se usan.)

Un patron es una lista de pasos (ms, grave, agudo), con fuerzas de 0 a 1. Para que
se sienta suave, los patrones suben y bajan de a poco (varios pasos) en vez de
arrancar y cortar de golpe. Estan en config.VIBRACIONES, cada uno con su PRIORIDAD:
uno chico (subir el combo) no corta a uno grande (perder una vida).

Los patrones avanzan con el reloj real (actualizar() en cada paso de la App): la
vibracion sigue durante el hit-stop, igual que el sonido.
"""
import pygame

from juego.config import VIBRACIONES, NIVELES_VIBRACION

# Cada paso se manda un poco mas largo de lo que dura: asi no queda un hueco entre un
# paso y el siguiente (el siguiente lo reemplaza). El ultimo se manda justo.
SOLAPAR_MS = 40


def _limitar(valor):
    return min(max(valor, 0), 1)


class Haptica:
    def __init__(self, mandos):
        self.mandos = mandos            # el diccionario de mandos de Entrada (el mismo objeto)
        self.opciones = None            # para leer la intensidad elegida (None = NORMAL)
        self.reloj = pygame.time.get_ticks      # reloj real (la App pone el suyo)
        self.nombre = None              # patron que esta sonando (None = ninguno)
        self.prioridad = 0
        self.pasos = []                 # los pasos ya calculados (con la intensidad)
        self.paso = 0                   # cual se esta tocando
        self.fin_paso = 0               # cuando termina ese paso (reloj real)

    def intensidad(self):
        # Multiplicador de la opcion VIBRACION (NO = 0)
        if self.opciones is None:
            return NIVELES_VIBRACION["NORMAL"]
        return NIVELES_VIBRACION[self.opciones.vibracion]

    def sonando(self):
        return self.nombre is not None

    def reproducir(self, nombre, fuerza=1):
        # Empieza un patron de config.VIBRACIONES.
        # fuerza: multiplica todo (ej: la cadena de perfectos lo sube un poco)
        prioridad, pasos = VIBRACIONES[nombre]
        if self.sonando() and prioridad < self.prioridad:
            return          # hay uno mas importante: este no lo corta
        intensidad = self.intensidad() * fuerza
        if intensidad <= 0:
            return
        self.nombre = nombre
        self.prioridad = prioridad
        self.pasos = [(ms, _limitar(grave * intensidad), _limitar(agudo * intensidad))
                      for ms, grave, agudo in pasos]
        self.paso = 0
        self._tocar_paso()

    def _tocar_paso(self):
        ms, grave, agudo = self.pasos[self.paso]
        self.fin_paso = self.reloj() + ms
        ultimo = self.paso == len(self.pasos) - 1
        duracion = ms if ultimo else ms + SOLAPAR_MS
        for mando in self.mandos.values():
            mando.rumble(grave, agudo, duracion)

    def actualizar(self):
        # En cada paso de la App: si el paso del patron termino, sigue con el proximo
        if not self.sonando():
            return
        ahora = self.reloj()
        while self.sonando() and ahora >= self.fin_paso:
            self.paso += 1
            if self.paso >= len(self.pasos):
                self.nombre = None          # termino (los motores ya se apagan solos)
                self.prioridad = 0
            else:
                self._tocar_paso()

    def parar(self):
        # Corta todo enseguida (pausa, cerrar el juego)
        self.nombre = None
        self.prioridad = 0
        for mando in self.mandos.values():
            mando.stop_rumble()
