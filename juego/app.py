"""
App: crea todos los servicios del juego y corre el bucle principal.

Servicios (se crean una sola vez y las escenas los usan con self.app.<servicio>):
    ventana, opciones, sonidos, records, entrada, fondo, efectos

En cada frame: lee la entrada -> la escena actual se actualiza -> se dibuja -> se muestra.
"""
import os

import pygame

from juego.config import CARPETA, ANCHO, ALTO, FPS, NOMBRE_CONFIG, NOMBRE_RECORDS
from juego.ventana import Ventana
from juego.guardado import Opciones, TablaRecords
from juego.sonido import Sonidos
from juego.entrada import Entrada
from juego.fondo import Fondo
from juego.efectos import Efectos
from juego.partida import Partida
from juego.escenas.inicio import Inicio
from juego.escenas.listo import Listo


class App:
    def __init__(self, carpeta_datos=CARPETA, usar_mandos=True):
        # carpeta_datos: donde se guardan records.json y config.json (los tests usan otra)
        pygame.init()
        pygame.display.set_caption("Caza Monedas")

        self.ventana = Ventana()
        self.opciones = Opciones(os.path.join(carpeta_datos, NOMBRE_CONFIG), self.ventana.nombres())
        self.ventana.aplicar(self.opciones.resolucion)
        self.sonidos = Sonidos()
        self.sonidos.aplicar_volumen(self.opciones)
        self.records = TablaRecords(os.path.join(carpeta_datos, NOMBRE_RECORDS))
        self.entrada = Entrada(usar_mandos)
        self.fondo = Fondo()
        self.efectos = Efectos()

        self.pantalla = pygame.Surface((ANCHO, ALTO))   # lienzo donde se dibuja todo
        self.reloj = pygame.time.Clock()
        self.ejecutando = True
        self.escena = Inicio(self)

    def ahora(self):
        # Reloj real en milisegundos (los tests lo reemplazan para no tener que esperar)
        return pygame.time.get_ticks()

    def cambiar_escena(self, escena):
        self.escena = escena

    def nueva_partida(self):
        # Deja todo como al principio y muestra "READY?"
        self.efectos.reiniciar()
        partida = Partida(self.efectos, self.sonidos, self.entrada, self.records, self.opciones)
        self.sonidos.reproducir("seleccion")
        self.sonidos.empezar_musica()
        self.cambiar_escena(Listo(self, partida))

    def paso(self):
        # Un frame completo (sin esperar: eso lo hace ejecutar())
        self.entrada.procesar(pygame.event.get())
        if self.entrada.cerrar:
            self.escena.al_cerrar()
            self.ejecutando = False
            return
        self.escena.actualizar(self.entrada)
        self.escena.dibujar(self.pantalla)
        self.ventana.mostrar(self.pantalla)

    def ejecutar(self):
        while self.ejecutando:
            self.paso()
            self.reloj.tick(FPS)
        pygame.quit()
