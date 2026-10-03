"""Escribir las iniciales del record: tres letras que se eligen con arriba/abajo."""
import pygame

from juego import dibujo
from juego.dibujo import texto, CHICA, GRANDE, TITULO
from juego.config import MAGENTA, AMARILLO, CIAN, GRIS, BLANCO, ALFABETO
from juego.entrada import ARRIBA, ABAJO, IZQUIERDA, DERECHA, ACEPTAR
from juego.escenas.base import Escena
from juego.escenas.fin import Fin


class Iniciales(Escena):
    def __init__(self, app, partida):
        super().__init__(app)
        self.partida = partida
        self.letras = ["A", "A", "A"]
        self.actual = 0             # casilla elegida

    def actualizar(self, entrada):
        # Cada accion se procesa en orden
        for accion in entrada.acciones:
            if self.app.escena is not self:
                break
            posicion = ALFABETO.index(self.letras[self.actual])
            if accion == ARRIBA:
                self.letras[self.actual] = ALFABETO[(posicion + 1) % len(ALFABETO)]
            elif accion == ABAJO:
                self.letras[self.actual] = ALFABETO[(posicion - 1) % len(ALFABETO)]
            elif accion == IZQUIERDA and self.actual > 0:
                self.actual -= 1
            elif accion in (ACEPTAR, DERECHA):
                self.app.sonidos.reproducir("seleccion")
                self.actual += 1
                if self.actual == 3:
                    fila = self.app.records.agregar("".join(self.letras), self.partida.puntaje)
                    self.app.cambiar_escena(Fin(self.app, self.partida, fila_nueva=fila))

    def al_cerrar(self):
        # Si se cierra la ventana aca, el record se guarda igual
        self.app.records.agregar("".join(self.letras), self.partida.puntaje)

    def dibujar(self, pantalla_completa):
        # Fondo en todo el ancho; el resto en la zona central de 800x600
        self.app.fondo.mover_y_dibujar(pantalla_completa)
        pantalla = dibujo.zona_central(pantalla_completa)
        filas = self.app.records.filas
        if not filas or self.partida.puntaje > filas[0]["puntos"]:
            dibujo.texto_3d(pantalla, "NUEVO RECORD", GRANDE, dibujo.color_arcoiris(), MAGENTA, 110, 4)
        else:
            dibujo.texto_3d(pantalla, "PUNTAJE ALTO", GRANDE, AMARILLO, MAGENTA, 110, 4)
        texto(pantalla, "PUNTOS " + dibujo.numero_arcade(self.partida.puntaje), CHICA, BLANCO, 400, 180)
        texto(pantalla, "ESCRIBE TUS INICIALES", CHICA, GRIS, 400, 235)

        # Tres casillas; la actual parpadea y tiene flechas arriba y abajo
        for i in range(3):
            casilla = pygame.Rect(0, 0, 70, 84)
            casilla.center = (320 + i * 80, 330)
            if i == self.actual:
                dibujo.marco(pantalla, casilla, AMARILLO if dibujo.parpadeo(250) else CIAN)
                pygame.draw.polygon(pantalla, AMARILLO, [(casilla.centerx - 10, 278), (casilla.centerx + 10, 278),
                                                         (casilla.centerx, 266)])
                pygame.draw.polygon(pantalla, AMARILLO, [(casilla.centerx - 10, 382), (casilla.centerx + 10, 382),
                                                         (casilla.centerx, 394)])
                texto(pantalla, self.letras[i], TITULO, AMARILLO, casilla.centerx + 3, casilla.centery + 3)
            else:
                dibujo.marco(pantalla, casilla, GRIS)
                texto(pantalla, self.letras[i], TITULO, BLANCO, casilla.centerx + 3, casilla.centery + 3)

        texto(pantalla, "ARRIBA/ABAJO: LETRA", CHICA, GRIS, 400, 460)
        texto(pantalla, self.app.entrada.ayuda("ENTER: ACEPTAR   IZQ: VOLVER", "A: ACEPTAR   IZQ: VOLVER"),
              CHICA, GRIS, 400, 490)
        dibujo.efecto_crt(pantalla_completa)
