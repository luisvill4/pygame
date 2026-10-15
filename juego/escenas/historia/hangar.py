"""
HANGAR: las mejoras para siempre de la Alondra (historia/hangar.py), compradas con piezas.

Las seis instalaciones en cartas (las mismas del Taller: interfaz.carta), en dos filas de tres,
con sus niveles y el precio del siguiente abajo. Las flechas eligen; ACEPTAR instala (si
alcanzan las piezas); VOLVER vuelve a la galaxia. Lo instalado se suma al empezar cada partida de la historia.
"""
import pygame

from juego import interfaz
from juego.dibujo import texto, CHICA, GRANDE
from juego.config import ANCHO, FONDO, AMARILLO, TEXTO_SUAVE, VERDE, ROJO
from juego.entrada import ACEPTAR, VOLVER, IZQUIERDA, DERECHA, ARRIBA, ABAJO
from juego.escenas.base import Escena
from juego.historia import hangar

ARRIBA_CARTAS, ALTO_CARTA, SEPARACION, POR_FILA = 108, 200, 24, 3


class Hangar(Escena):
    musica = None
    ambiente = None

    def __init__(self, app, volver_a):
        super().__init__(app)
        self.volver_a = volver_a
        self.instalaciones = hangar.instalaciones()
        self.elegida = 0
        self.cursor = interfaz.Cursor(0)

    def actualizar(self, entrada):
        self.mover_fondo()
        self.cursor.avanzar()
        progreso = self.app.progreso
        pasos = {IZQUIERDA: -1, DERECHA: 1, ARRIBA: -POR_FILA, ABAJO: POR_FILA}
        movida = next((paso for accion, paso in pasos.items() if entrada.pulso(accion)), None)
        if movida is not None:
            self.elegida = (self.elegida + movida) % len(self.instalaciones)
            self.app.sonidos.reproducir("ui_mover")
        elif entrada.pulso(ACEPTAR):
            if hangar.comprar(progreso, self.instalaciones[self.elegida].tipo):
                self.app.sonidos.reproducir("mejora_elegida")
            else:
                self.app.sonidos.reproducir("dash_vacio")
        elif entrada.pulso(VOLVER):
            self.app.sonidos.reproducir("ui_volver")
            self.app.cambiar_escena(self.volver_a)

    def caja(self, i):
        ancho = (ANCHO - 96 - SEPARACION * (POR_FILA - 1)) // POR_FILA // 2 * 2
        fila, columna = divmod(i, POR_FILA)
        return pygame.Rect(48 + columna * (ancho + SEPARACION), ARRIBA_CARTAS + fila * (ALTO_CARTA + 16), ancho,
                           ALTO_CARTA)

    def dibujar(self, pantalla):
        self.dibujar_fondo(pantalla)
        progreso = self.app.progreso
        interfaz.titulo(pantalla, "HANGAR", 48, 60, AMARILLO, interfaz.mezclar(AMARILLO, FONDO, 0.6), tamano=GRANDE)
        texto(pantalla, "PIEZAS %d" % progreso.piezas, CHICA, AMARILLO, ANCHO - 48, 60, alinear="derecha")
        for i, instalacion in enumerate(self.instalaciones):
            caja = self.caja(i)
            nivel = hangar.nivel(progreso, instalacion.tipo)
            precio = hangar.precio(progreso, instalacion.tipo)
            completa = precio is None
            interfaz.carta(pantalla, caja, instalacion.color, instalacion.icono, instalacion.nombre,
                           instalacion.descripcion, elegida=i == self.elegida, apagada=completa,
                           nivel=(nivel, instalacion.maximo))
            if completa:
                etiqueta, color = "COMPLETO", VERDE
            else:
                etiqueta, color = "%d PIEZAS" % precio, AMARILLO if progreso.piezas >= precio else ROJO
            texto(pantalla, etiqueta, CHICA, color, caja.centerx, caja.bottom - 16)
        texto(pantalla, "LAS PIEZAS SALEN DE LAS MONEDAS. LOS SISTEMAS LEJANOS DAN MAS.", CHICA, TEXTO_SUAVE,
              ANCHO // 2, ARRIBA_CARTAS + 2 * ALTO_CARTA + 44)
        interfaz.ayudas(pantalla, self.app.entrada, [("mover", "ELEGIR"), ("volver", "VOLVER"),
                                                     ("aceptar", "INSTALAR")])
