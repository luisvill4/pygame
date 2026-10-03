"""
Menu de opciones. Se abre desde Inicio o desde Pausa y al salir vuelve a esa escena.

Cada cambio se aplica al instante y se guarda en config.json.
Para agregar una opcion: sumarla a FILAS, dibujar su valor en _dibujar_valor(),
manejarla en _cambiar() y guardarla en guardado.Opciones.
"""
import pygame

from juego import dibujo
from juego.dibujo import texto, CHICA, MEDIA, TITULO
from juego.config import CIAN, AMARILLO, BLANCO, GRIS, VOLUMEN_MAX
from juego.entrada import ACEPTAR, VOLVER, ARRIBA, ABAJO, IZQUIERDA, DERECHA
from juego.escenas.base import Escena

FILAS = ["RESOLUCION", "VOLUMEN", "MUSICA", "EFECTOS", "AVISO JEFE", "VOLVER"]
INTERRUPTORES = ("MUSICA", "EFECTOS", "AVISO JEFE")     # opciones de SI / NO (ENTER tambien las cambia)


class Opciones(Escena):
    def __init__(self, app, volver_a):
        super().__init__(app)
        self.volver_a = volver_a        # escena a la que se regresa al salir
        self.fila = 0                   # fila elegida

    def actualizar(self, entrada):
        # Cada accion se procesa en orden
        for accion in entrada.acciones:
            if self.app.escena is not self:
                break
            fila = FILAS[self.fila]
            if accion == ARRIBA:
                self.fila = (self.fila - 1) % len(FILAS)
            elif accion == ABAJO:
                self.fila = (self.fila + 1) % len(FILAS)
            elif accion == DERECHA and fila != "VOLVER":
                self._cambiar(fila, 1)
            elif accion == IZQUIERDA and fila != "VOLVER":
                self._cambiar(fila, -1)
            elif accion == ACEPTAR and fila in INTERRUPTORES:
                self._cambiar(fila, 1)
            elif accion == VOLVER or (accion == ACEPTAR and fila == "VOLVER"):
                self.app.sonidos.reproducir("seleccion")
                self.app.cambiar_escena(self.volver_a)

    def _cambiar(self, fila, direccion):
        # Cambia el valor de una fila (direccion: -1 o 1), lo aplica al instante y lo guarda
        opciones = self.app.opciones
        if fila == "RESOLUCION":
            opciones.resolucion = (opciones.resolucion + direccion) % len(self.app.ventana.resoluciones)
            self.app.ventana.aplicar(opciones.resolucion)
        elif fila == "VOLUMEN":
            opciones.volumen = min(max(opciones.volumen + direccion, 0), VOLUMEN_MAX)
        elif fila == "MUSICA":
            opciones.musica = not opciones.musica
        elif fila == "EFECTOS":
            opciones.efectos = not opciones.efectos
        elif fila == "AVISO JEFE":
            opciones.aviso_jefe = not opciones.aviso_jefe
        self.app.sonidos.aplicar_volumen(opciones)
        opciones.guardar()
        self.app.sonidos.reproducir("seleccion")

    def dibujar(self, pantalla):
        self.app.fondo.mover_y_dibujar(pantalla)
        dibujo.texto_3d(pantalla, "OPCIONES", TITULO, CIAN, (0, 70, 110), 130)

        dibujo.marco(pantalla, pygame.Rect(80, 190, 640, 290), CIAN)
        for i, fila in enumerate(FILAS):
            fila_y = 230 + i * 45
            elegida = i == self.fila
            dibujo.opcion(pantalla, fila, MEDIA, 120, fila_y, elegida, alinear="izquierda")
            self._dibujar_valor(pantalla, fila, fila_y, AMARILLO if elegida else BLANCO)

        texto(pantalla, "ARRIBA/ABAJO ELEGIR  IZQ/DER CAMBIAR", CHICA, GRIS, 400, 520)
        texto(pantalla, self.app.entrada.ayuda("ESC VOLVER", "B VOLVER"), CHICA, GRIS, 400, 550)
        dibujo.efecto_crt(pantalla)

    def _dibujar_valor(self, pantalla, fila, fila_y, color):
        # Valor de la fila, a la derecha
        opciones = self.app.opciones
        if fila == "RESOLUCION":
            nombre = self.app.ventana.resoluciones[opciones.resolucion][0]
            texto(pantalla, "< " + nombre + " >", MEDIA, color, 700, fila_y, alinear="derecha")
        elif fila == "VOLUMEN":
            # Barra de cuadritos: llenos hasta el volumen actual, el resto solo el borde
            inicio_barra = 660 - VOLUMEN_MAX * 16
            texto(pantalla, "<", MEDIA, color, inicio_barra - 16, fila_y, alinear="derecha")
            texto(pantalla, ">", MEDIA, color, 700, fila_y, alinear="derecha")
            for paso in range(VOLUMEN_MAX):
                cuadrito = pygame.Rect(inicio_barra + paso * 16, fila_y - 10, 12, 20)
                if paso < opciones.volumen:
                    pantalla.fill(color, cuadrito)
                else:
                    pygame.draw.rect(pantalla, GRIS, cuadrito, 2)
        elif fila in INTERRUPTORES:
            encendida = {"MUSICA": opciones.musica, "EFECTOS": opciones.efectos,
                         "AVISO JEFE": opciones.aviso_jefe}[fila]
            if encendida:
                texto(pantalla, "< SI >", MEDIA, color, 700, fila_y, alinear="derecha")
            else:
                texto(pantalla, "< NO >", MEDIA, GRIS, 700, fila_y, alinear="derecha")
