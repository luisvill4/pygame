"""
ELIGE DIFICULTAD: se abre al elegir JUGAR en el inicio.

IZQ/DER cambian la dificultad con una animacion: el nombre entra deslizandose desde
el costado (y destella), las calaveras aparecen de a una, saltan chispas del color de
la dificultad y en PESADILLA tiembla la pantalla. Muestra que cambia y el record de
esa dificultad (cada una tiene su propia tabla). ENTER empieza la partida.
"""
import pygame

from juego import dibujo
from juego.dibujo import texto, CHICA, MEDIA, GRANDE
from juego.config import (BLANCO, GRIS, CIAN, AMARILLO, ROJO, ORDEN_DIFICULTADES, DIFICULTADES)
from juego.entrada import ACEPTAR, VOLVER, IZQUIERDA, DERECHA
from juego.escenas.base import Escena

PASOS_ANIMACION = 14        # pasos (1/60 s) que dura la entrada del nombre
DESLIZAMIENTO = 160         # px desde donde entra el nombre

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
        self.app.efectos.explosion(400, 255, reglas["paleta"], 30, 6, 4)
        self.app.efectos.anillo(400, 255, reglas["paleta"], 20, 5, 3)
        if self.nombre() == "PESADILLA":
            self.app.efectos.sacudir(10, ROJO)
            self.app.entrada.vibrar(0.6, 0.9, 200)

    # ---------- Dibujo ----------

    def dibujar(self, pantalla_completa):
        self.dibujar_fondo(pantalla_completa)
        pantalla = dibujo.zona_central(pantalla_completa)
        nombre = self.nombre()
        reglas = DIFICULTADES[nombre]
        color = reglas["color"]
        recien_cambiada = self.animacion > PASOS_ANIMACION - 4     # los primeros pasos destella

        dibujo.texto_3d(pantalla, "ELIGE DIFICULTAD", GRANDE, CIAN, (0, 70, 110), 80, 4)
        dibujo.marco(pantalla, pygame.Rect(150, 140, 500, 320), BLANCO if recien_cambiada else color)
        self.app.efectos.dibujar(pantalla)

        self._dibujar_calaveras(pantalla, reglas, color)

        # Nombre: entra deslizandose desde el costado (en saltos de 4 px, estilo retro)
        avance = self.animacion / PASOS_ANIMACION
        corrimiento = round(self.direccion * avance * avance * DESLIZAMIENTO / 4) * 4
        texto(pantalla, nombre, GRANDE, BLANCO if recien_cambiada else color, 400 + corrimiento, 255)

        # Flechas: parpadean, y la apretada se corre un poco hacia afuera
        for lado, x in ((-1, 190), (1, 610)):
            empujada = self.empujon_flecha > 0 and lado == self.direccion
            x_flecha = x + lado * 8 if empujada else x
            if empujada or dibujo.parpadeo(400):
                texto(pantalla, "<" if lado < 0 else ">", MEDIA, AMARILLO if empujada else GRIS, x_flecha, 255)

        # Que cambia y el record de esta dificultad
        for i, linea in enumerate(reglas["descripcion"]):
            if linea:
                texto(pantalla, linea, CHICA, BLANCO, 400, 315 + i * 28)
        texto(pantalla, "RECORD " + dibujo.numero_arcade(self.app.records.maximo(nombre)), CHICA, color, 400, 420)

        ayuda = self.app.entrada.ayuda
        texto(pantalla, ayuda("IZQ/DER ELEGIR   ENTER JUGAR", "IZQ/DER ELEGIR   A JUGAR"), CHICA, GRIS, 400, 520)
        texto(pantalla, ayuda("ESC VOLVER", "B VOLVER"), CHICA, GRIS, 400, 550)
        self.app.efectos.dibujar_temblor_y_destello(pantalla_completa)
        dibujo.efecto_crt(pantalla_completa)

    def _dibujar_calaveras(self, pantalla, reglas, color):
        # Una calavera por nivel de dificultad; despues de cambiar aparecen de a una
        pasos_desde_cambio = PASOS_ANIMACION - self.animacion
        for i in range(len(ORDEN_DIFICULTADES)):
            x = 400 + (i - 1.5) * 44
            llena = i < reglas["calaveras"]
            if not llena:
                dibujar_calavera(pantalla, x, 192, (40, 40, 60))
                continue
            aparece_en = i * 3
            if self.animacion > 0 and pasos_desde_cambio < aparece_en:
                dibujar_calavera(pantalla, x, 192, (40, 40, 60))        # todavia no aparecio
            elif self.animacion > 0 and pasos_desde_cambio < aparece_en + 3:
                dibujar_calavera(pantalla, x, 192, BLANCO, 5)           # aparece grande y blanca
            else:
                dibujar_calavera(pantalla, x, 192, color)
