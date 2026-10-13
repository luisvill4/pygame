"""
LOGROS: los logros (desbloqueados en color, los demas en gris) y el hangar de naves.

Arriba se elige la nave con IZQ/DER entre las desbloqueadas (cada logro de NAVES en
config.py da un color nuevo). ESC vuelve al inicio. La nave elegida se guarda.
"""
import pygame

from juego import dibujo, nave, interfaz, recursos
from juego.dibujo import texto, MINI, CHICA, MEDIA
from juego.config import ANCHO, AMARILLO, BLANCO, GRIS, CIAN, MAGENTA, VERDE, NAVES, TEXTO_SUAVE
from juego.entrada import VOLVER, ACEPTAR, IZQUIERDA, DERECHA
from juego.escenas.base import Escena
from juego.logros import LOGROS

HANGAR = pygame.Rect(48, 122, ANCHO - 96, 92)
LISTA = pygame.Rect(48, 234, ANCHO - 96, 310)

CANDADO = [
    "..XXX..",
    ".X...X.",
    ".X...X.",
    "XXXXXXX",
    "XXX.XXX",
    "XXX.XXX",
    "XXXXXXX",
]
TILDE = [
    ".......",
    "......X",
    ".....XX",
    "X...XX.",
    "XX.XX..",
    ".XXX...",
    "..X....",
]


class Logros(Escena):
    musica = "menu"

    def __init__(self, app, volver_a):
        super().__init__(app)
        self.volver_a = volver_a

    def actualizar(self, entrada):
        self.mover_fondo()
        if entrada.pulso(IZQUIERDA):
            self._cambiar_nave(-1)
        elif entrada.pulso(DERECHA):
            self._cambiar_nave(1)
        elif entrada.pulso(VOLVER) or entrada.pulso(ACEPTAR):
            self.app.sonidos.reproducir("seleccion")
            self.app.cambiar_escena(self.volver_a)

    def _cambiar_nave(self, direccion):
        # La siguiente nave desbloqueada; se aplica y se guarda al instante
        progreso = self.app.progreso
        nombres = [nombre for nombre, _, _ in progreso.naves_disponibles()]
        if len(nombres) < 2:
            return
        progreso.nave = nombres[(nombres.index(progreso.nave) + direccion) % len(nombres)]
        progreso.guardar()
        nave.cambiar_color(progreso.color_nave())
        self.app.sonidos.reproducir("seleccion")

    # ---------- Dibujo ----------

    def dibujar(self, pantalla):
        self.dibujar_fondo(pantalla)
        progreso = self.app.progreso
        interfaz.titulo(pantalla, "LOGROS", 64, 70, AMARILLO, MAGENTA)
        hechos = sum(1 for logro in LOGROS if logro.id in progreso.logros)
        texto(pantalla, str(hechos) + "/" + str(len(LOGROS)), MEDIA, BLANCO, ANCHO - 64, 58, alinear="derecha")
        texto(pantalla, "PARTIDAS " + str(progreso.partidas), CHICA, TEXTO_SUAVE, ANCHO - 64, 88, alinear="derecha")
        self._dibujar_hangar(pantalla, progreso)
        self._dibujar_lista(pantalla, progreso)
        interfaz.ayudas(pantalla, self.app.entrada, [("cambiar", "NAVE"), ("volver", "VOLVER")])

    def _dibujar_hangar(self, pantalla, progreso):
        # La nave elegida (girando de a 45 grados) y cuantas quedan por desbloquear
        adentro = interfaz.panel(pantalla, HANGAR, CIAN, "HANGAR")
        angulo = pygame.time.get_ticks() // 400 % 8 * 45
        imagen = pygame.transform.rotate(nave.imagen("nave"), angulo)
        pantalla.blit(imagen, imagen.get_rect(center=(adentro.left + 40, adentro.centery)))
        x = adentro.left + 100
        dibujo.flecha(pantalla, x, adentro.centery, 9, -1, AMARILLO)
        texto(pantalla, progreso.nave, MEDIA, AMARILLO, x + 22, adentro.centery, alinear="izquierda")
        ancho = recursos.fuente(MEDIA).size(progreso.nave)[0]
        dibujo.flecha(pantalla, x + 44 + ancho, adentro.centery, 9, 1, AMARILLO)
        disponibles = len(progreso.naves_disponibles())
        if disponibles < len(NAVES):
            mensaje, color = "BLOQUEADAS: " + str(len(NAVES) - disponibles) + "  (SE GANAN CON LOGROS)", TEXTO_SUAVE
        else:
            mensaje, color = "¡TODAS LAS NAVES!", VERDE
        texto(pantalla, mensaje, CHICA, color, adentro.right, adentro.centery, alinear="derecha")

    def _dibujar_lista(self, pantalla, progreso):
        # Dos columnas: icono (tilde o candado), nombre y que hay que hacer
        adentro = interfaz.panel(pantalla, LISTA, AMARILLO)
        mitad = (len(LOGROS) + 1) // 2
        ancho_columna = adentro.width // 2
        for i, logro in enumerate(LOGROS):
            columna, fila = divmod(i, mitad)
            x = adentro.left + columna * ancho_columna
            y = adentro.top + 8 + fila * 36
            hecho = logro.id in progreso.logros
            if hecho:
                dibujo.pixel_art(pantalla, TILDE, x + 10, y + 6, VERDE, 3)
            else:
                dibujo.pixel_art(pantalla, CANDADO, x + 10, y + 6, (70, 70, 100), 3)
            texto(pantalla, logro.nombre, CHICA, AMARILLO if hecho else GRIS, x + 32, y, alinear="izquierda")
            texto(pantalla, logro.descripcion, MINI, BLANCO if hecho else (90, 90, 120), x + 32, y + 16,
                  alinear="izquierda")
            # Si da una nave, un cuadradito de su color
            for nombre, color, id_logro in NAVES:
                if id_logro == logro.id:
                    pantalla.fill(color if hecho else (50, 50, 70), (x + ancho_columna - 28, y - 6, 12, 12))
