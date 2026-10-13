"""
ELIGE DIFICULTAD: se abre al elegir JUGAR en el inicio.

IZQ/DER cambian la dificultad con una animacion: el nombre entra deslizandose desde
el costado (y destella), las calaveras aparecen de a una, saltan chispas del color de
la dificultad y en PESADILLA tiembla la pantalla. Muestra que cambia y el record de
esa dificultad (cada una tiene su propia tabla). ENTER empieza la partida.
"""
import pygame

from juego import dibujo, interfaz
from juego.dibujo import texto, CHICA, GRANDE
from juego.config import (CENTRO_X, FONDO, BLANCO, CIAN, AMARILLO, ROJO, ORDEN_DIFICULTADES, DIFICULTADES)
from juego.entrada import ACEPTAR, VOLVER, IZQUIERDA, DERECHA
from juego.escenas.base import Escena

PASOS_ANIMACION = 14        # pasos (1/60 s) que dura la entrada del nombre
DESLIZAMIENTO = 160         # px desde donde entra el nombre
FILA_DIFICULTADES = pygame.Rect(CENTRO_X - 340, 140, 680, 30)     # las cuatro, arriba
TARJETA = pygame.Rect(CENTRO_X - 300, 192, 600, 330)              # la elegida

# Calavera de 7x7 pixeles (se dibuja a 4x, en la cuadricula retro)
CALAVERA = [
    ".XXXXX.",
    "XXXXXXX",
    "X..X..X",
    "X..X..X",
    "XXX.XXX",
    ".XXXXX.",
    ".X.X.X.",
]


def dibujar_calavera(pantalla, centro_x, centro_y, color, tamano_pixel=4):
    lado = len(CALAVERA) * tamano_pixel
    izquierda, arriba = centro_x - lado // 2, centro_y - lado // 2
    for fila, linea in enumerate(CALAVERA):
        for columna, celda in enumerate(linea):
            if celda == "X":
                pantalla.fill(color, (izquierda + columna * tamano_pixel, arriba + fila * tamano_pixel,
                                      tamano_pixel, tamano_pixel))


class Dificultad(Escena):
    musica = "menu"

    def __init__(self, app, volver_a):
        super().__init__(app)
        self.volver_a = volver_a
        self.elegida = ORDEN_DIFICULTADES.index(app.opciones.dificultad)
        self.animacion = PASOS_ANIMACION    # pasos que le quedan a la animacion de cambio
        self.direccion = 1                  # de que lado entra el nombre (-1 izquierda, 1 derecha)
        self.empujon_flecha = 0             # pasos que la flecha apretada queda corrida

    def nombre(self):
        return ORDEN_DIFICULTADES[self.elegida]

    def actualizar(self, entrada):
        self.mover_fondo()
        self.app.efectos.actualizar()
        if self.animacion > 0:
            self.animacion -= 1
        if self.empujon_flecha > 0:
            self.empujon_flecha -= 1

        if entrada.pulso(IZQUIERDA):
            self._cambiar(-1)
        elif entrada.pulso(DERECHA):
            self._cambiar(1)
        elif entrada.pulso(ACEPTAR):
            self.app.opciones.dificultad = self.nombre()
            self.app.opciones.guardar()
            self.app.nueva_partida(self.nombre())
        elif entrada.pulso(VOLVER):
            self.app.sonidos.reproducir("seleccion")
            self.app.cambiar_escena(self.volver_a)

    def _cambiar(self, direccion):
        self.elegida = (self.elegida + direccion) % len(ORDEN_DIFICULTADES)
        self.direccion = direccion
        self.animacion = PASOS_ANIMACION
        self.empujon_flecha = 6
        reglas = DIFICULTADES[self.nombre()]
        self.app.sonidos.reproducir("seleccion")
        # Chispas del color de la dificultad (en coordenadas de la zona central)
        self.app.efectos.explosion(CENTRO_X, TARJETA.top + 116, reglas["paleta"], 30, 6, 4)
        self.app.efectos.anillo(CENTRO_X, TARJETA.top + 116, reglas["paleta"], 20, 5, 3)
        if self.nombre() == "PESADILLA":
            self.app.efectos.sacudir(10, ROJO)
            self.app.entrada.vibrar("pesadilla")

    # ---------- Dibujo ----------

    def dibujar(self, pantalla):
        self.dibujar_fondo(pantalla)
        nombre = self.nombre()
        reglas = DIFICULTADES[nombre]
        color = reglas["color"]
        recien_cambiada = self.animacion > PASOS_ANIMACION - 4     # los primeros pasos destella

        interfaz.titulo(pantalla, "DIFICULTAD", 64, 76, CIAN, (0, 70, 110))
        # Las cuatro, arriba: se ve donde estas parado
        dibujo.pestanas(pantalla, FILA_DIFICULTADES, ORDEN_DIFICULTADES, self.elegida, color,
                        interfaz.mezclar(color, FONDO, 0.75))
        interfaz.panel(pantalla, TARJETA, BLANCO if recien_cambiada else color)
        self.app.efectos.dibujar(pantalla)
        self._dibujar_calaveras(pantalla, reglas, color)

        # Nombre: entra deslizandose desde el costado (en saltos de 4 px, estilo retro)
        avance = self.animacion / PASOS_ANIMACION
        corrimiento = round(self.direccion * avance * avance * DESLIZAMIENTO / 4) * 4
        dibujo.texto_3d(pantalla, nombre, GRANDE, BLANCO if recien_cambiada else color,
                        interfaz.mezclar(color, FONDO, 0.7), TARJETA.top + 116, 4, None, CENTRO_X + corrimiento)

        # Flechas grandes a los costados: la apretada se corre hacia afuera
        for lado in (-1, 1):
            empujada = self.empujon_flecha > 0 and lado == self.direccion
            x = (TARJETA.right + 44 if lado > 0 else TARJETA.left - 44) + (lado * 10 if empujada else 0)
            dibujo.flecha(pantalla, x, TARJETA.centery, 18, lado, AMARILLO if empujada else color)

        # Que cambia y el record de esta dificultad
        for i, linea in enumerate(reglas["descripcion"]):
            if linea:
                texto(pantalla, linea, CHICA, BLANCO, CENTRO_X, TARJETA.top + 172 + i * 28)
        interfaz.separador(pantalla, TARJETA.left + 40, TARJETA.bottom - 58, TARJETA.width - 80)
        texto(pantalla, "RECORD " + dibujo.numero_arcade(self.app.records.maximo(nombre)), CHICA, color,
              CENTRO_X, TARJETA.bottom - 32)
        self.app.efectos.dibujar_temblor_y_destello(pantalla)
        interfaz.ayudas(pantalla, self.app.entrada, [("cambiar", "ELEGIR"), ("aceptar", "JUGAR"),
                                                     ("volver", "VOLVER")])

    def _dibujar_calaveras(self, pantalla, reglas, color):
        # Una calavera por nivel de dificultad; despues de cambiar aparecen de a una
        pasos_desde_cambio = PASOS_ANIMACION - self.animacion
        y = TARJETA.top + 52
        for i in range(len(ORDEN_DIFICULTADES)):
            x = CENTRO_X + (i - 1.5) * 44
            llena = i < reglas["calaveras"]
            if not llena:
                dibujar_calavera(pantalla, x, y, (40, 40, 60))
                continue
            aparece_en = i * 3
            if self.animacion > 0 and pasos_desde_cambio < aparece_en:
                dibujar_calavera(pantalla, x, y, (40, 40, 60))        # todavia no aparecio
            elif self.animacion > 0 and pasos_desde_cambio < aparece_en + 3:
                dibujar_calavera(pantalla, x, y, BLANCO, 5)           # aparece grande y blanca
            else:
                dibujar_calavera(pantalla, x, y, color)
