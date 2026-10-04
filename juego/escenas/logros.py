"""
LOGROS: los logros (desbloqueados en color, los demas en gris) y el hangar de naves.

Arriba se elige la nave con IZQ/DER entre las desbloqueadas (cada logro de NAVES en
config.py da un color nuevo). ESC vuelve al inicio. La nave elegida se guarda.
"""
import pygame

from juego import dibujo, nave
from juego.dibujo import texto, MINI, CHICA, MEDIA, TITULO
from juego.config import AMARILLO, BLANCO, GRIS, CIAN, MAGENTA, VERDE, NAVES
from juego.entrada import VOLVER, ACEPTAR, IZQUIERDA, DERECHA
from juego.escenas.base import Escena
from juego.logros import LOGROS

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

    def dibujar(self, pantalla_completa):
        self.dibujar_fondo(pantalla_completa)
        pantalla = dibujo.zona_central(pantalla_completa)
        progreso = self.app.progreso
        dibujo.texto_3d(pantalla, "LOGROS", TITULO, AMARILLO, MAGENTA, 58)
        hechos = sum(1 for logro in LOGROS if logro.id in progreso.logros)
        texto(pantalla, str(hechos) + "/" + str(len(LOGROS)) + "   PARTIDAS " + str(progreso.partidas),
              CHICA, GRIS, 400, 108)
        self._dibujar_hangar(pantalla, progreso)
        self._dibujar_lista(pantalla, progreso)
        texto(pantalla, self.app.entrada.ayuda("IZQ/DER NAVE   ESC VOLVER", "IZQ/DER NAVE   B VOLVER"),
              CHICA, GRIS, 400, 578)
        dibujo.efecto_crt(pantalla_completa)

    def _dibujar_hangar(self, pantalla, progreso):
        # La nave elegida (girando de a 45 grados) y cuantas quedan por desbloquear
        marco = pygame.Rect(170, 126, 460, 92)
        dibujo.marco(pantalla, marco, CIAN)
        angulo = pygame.time.get_ticks() // 400 % 8 * 45
        imagen = pygame.transform.rotate(nave.imagen("nave"), angulo)
        pantalla.blit(imagen, imagen.get_rect(center=(marco.left + 60, marco.centery)))
        disponibles = len(progreso.naves_disponibles())
        texto(pantalla, "< " + progreso.nave + " >", MEDIA, AMARILLO, marco.centerx + 30, marco.centery - 12)
        if disponibles < len(NAVES):
            texto(pantalla, "BLOQUEADAS: " + str(len(NAVES) - disponibles) + " (LOGROS)", MINI, GRIS,
                  marco.centerx + 30, marco.centery + 20)
        else:
            texto(pantalla, "¡TODAS LAS NAVES!", MINI, VERDE, marco.centerx + 30, marco.centery + 20)

    def _dibujar_lista(self, pantalla, progreso):
        # Dos columnas: icono (tilde o candado), nombre y que hay que hacer
        dibujo.marco(pantalla, pygame.Rect(16, 226, 768, 322), (60, 60, 90))
        mitad = (len(LOGROS) + 1) // 2
        for i, logro in enumerate(LOGROS):
            columna, fila = divmod(i, mitad)
            x = 30 + columna * 380
            y = 248 + fila * 38
            hecho = logro.id in progreso.logros
            if hecho:
                dibujo.pixel_art(pantalla, TILDE, x + 10, y + 6, VERDE, 3)
            else:
                dibujo.pixel_art(pantalla, CANDADO, x + 10, y + 6, (70, 70, 100), 3)
            texto(pantalla, logro.nombre, CHICA, AMARILLO if hecho else GRIS, x + 30, y, alinear="izquierda")
            texto(pantalla, logro.descripcion, MINI, BLANCO if hecho else (90, 90, 120), x + 30, y + 16,
                  alinear="izquierda")
            # Si da una nave, un cuadradito de su color
            for nombre, color, id_logro in NAVES:
                if id_logro == logro.id:
                    pantalla.fill(color if hecho else (50, 50, 70), (x + 340, y - 6, 12, 12))
