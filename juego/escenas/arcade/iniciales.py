"""Escribir las iniciales del record: tres letras que se eligen con arriba/abajo."""
import pygame

from juego import dibujo, interfaz
from juego.dibujo import texto, CHICA, GRANDE, TITULO
from juego.config import (CENTRO_X, FONDO, MAGENTA, AMARILLO, CIAN, BLANCO, ALFABETO, FILAS_RECORDS, CONTORNO,
                          TEXTO_SUAVE, FILA_ELEGIDA, LINEA_APAGADA)
from juego.entrada import ARRIBA, ABAJO, IZQUIERDA, DERECHA, ACEPTAR
from juego.escenas.base import Escena
from juego.sonido import SILENCIO
from juego.escenas.arcade.fin import Fin


PANEL = pygame.Rect(CENTRO_X - 280, 132, 560, 336)


class Iniciales(Escena):
    ambiente = SILENCIO
    musica = "iniciales"
    def __init__(self, app, partida):
        super().__init__(app)
        self.partida = partida
        self.letras = ["A", "A", "A"]
        self.actual = 0             # casilla elegida

    def actualizar(self, entrada):
        self.mover_fondo()
        # Cada accion se procesa en orden
        for accion in entrada.acciones:
            if self.app.escena is not self:
                break
            posicion = ALFABETO.index(self.letras[self.actual])
            if accion in (ARRIBA, ABAJO):
                posicion = (posicion + (1 if accion == ARRIBA else -1)) % len(ALFABETO)
                self.letras[self.actual] = ALFABETO[posicion]
                self.app.sonidos.reproducir("ui_tecla_%d" % (posicion % 5 + 1))   # cada letra, su nota
            elif accion == IZQUIERDA and self.actual > 0:
                self.actual -= 1
                self.app.sonidos.reproducir("ui_volver")
            elif accion in (ACEPTAR, DERECHA):
                self.actual += 1
                self.app.sonidos.reproducir("record_guardado" if self.actual == 3 else "ui_aceptar")
                if self.actual == 3:
                    fila = self.app.records.agregar("".join(self.letras), self.partida.puntaje,
                                                    self.partida.dificultad)
                    self.app.cambiar_escena(Fin(self.app, self.partida, fila_nueva=fila))

    def al_cerrar(self):
        # Si se cierra la ventana aqui, el record se guarda igual
        self.app.records.agregar("".join(self.letras), self.partida.puntaje, self.partida.dificultad)

    def dibujar(self, pantalla):
        self.dibujar_fondo(pantalla)
        filas = self.app.records.filas(self.partida.dificultad)
        puntaje = self.partida.puntaje
        if not filas or puntaje > filas[0]["puntos"]:
            dibujo.texto_3d(pantalla, "NUEVO RECORD", GRANDE, dibujo.color_arcoiris(), MAGENTA, 78, 4, CONTORNO)
        else:
            dibujo.texto_3d(pantalla, "PUNTAJE ALTO", GRANDE, AMARILLO, MAGENTA, 78, 4, CONTORNO)
        adentro = interfaz.panel(pantalla, PANEL, CIAN, "TUS INICIALES")
        texto(pantalla, dibujo.numero_arcade(puntaje), GRANDE, BLANCO, PANEL.centerx, adentro.top + 26)
        puesto = sum(1 for fila in filas if fila["puntos"] >= puntaje) + 1
        texto(pantalla, "PUESTO " + str(puesto) + " DE " + str(FILAS_RECORDS) + " EN " + self.partida.dificultad,
              CHICA, TEXTO_SUAVE, PANEL.centerx, adentro.top + 62)

        # Tres casillas; la elegida resaltada, con flechas arriba y abajo
        for i in range(3):
            casilla = pygame.Rect(0, 0, 84, 100)
            casilla.center = (PANEL.centerx + (i - 1) * 104, adentro.top + 170)
            if i == self.actual:
                pantalla.fill(interfaz.mezclar(AMARILLO, FONDO, 0.8), casilla)
                pygame.draw.rect(pantalla, AMARILLO, casilla, 3)
                pygame.draw.polygon(pantalla, AMARILLO, [(casilla.centerx - 12, casilla.top - 10),
                                                          (casilla.centerx + 12, casilla.top - 10),
                                                          (casilla.centerx, casilla.top - 24)])
                pygame.draw.polygon(pantalla, AMARILLO, [(casilla.centerx - 12, casilla.bottom + 10),
                                                          (casilla.centerx + 12, casilla.bottom + 10),
                                                          (casilla.centerx, casilla.bottom + 24)])
                texto(pantalla, self.letras[i], TITULO, AMARILLO, casilla.centerx + 3, casilla.centery + 3)
            else:
                pantalla.fill(FILA_ELEGIDA, casilla)
                pygame.draw.rect(pantalla, LINEA_APAGADA, casilla, 2)
                texto(pantalla, self.letras[i], TITULO, BLANCO if i < self.actual else TEXTO_SUAVE,
                      casilla.centerx + 3, casilla.centery + 3)
        interfaz.ayudas(pantalla, self.app.entrada, [("elegir", "LETRA"), ("cambiar", "MOVERSE"),
                                                     ("aceptar", "SIGUIENTE")])
