"""
La ventana real del juego.

Todo se dibuja en un lienzo (800x600 en 4:3, 1066x600 en 16:9) y mostrar() lo
escala a la ventana sin suavizar (pixeles nitidos), centrado y con barras negras
si sobra espacio.
"""
import pygame

from juego import lienzo
from juego.config import RESOLUCIONES


class Ventana:
    def __init__(self):
        self.alto_escritorio = pygame.display.get_desktop_sizes()[0][1]
        self.superficie = None

    @property
    def resoluciones(self):
        # Las del formato actual que caben en el monitor (80 px de margen para la barra
        # de tareas y el titulo de la ventana); la pantalla completa siempre esta
        return [r for r in RESOLUCIONES[lienzo.formato]
                if r[0] == "COMPLETA" or r[2] + 80 <= self.alto_escritorio]

    def nombres(self):
        return [r[0] for r in self.resoluciones]

    def aplicar(self, nombre):
        # Abre la ventana con la resolucion elegida (por nombre, ej: "800x600")
        _, ancho, alto = next(r for r in self.resoluciones if r[0] == nombre)
        if nombre == "COMPLETA":
            self.superficie = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
            pygame.mouse.set_visible(False)
        else:
            self.superficie = pygame.display.set_mode((ancho, alto))
            # Trampa: al salir de pantalla completa la ventana vuelve a su tamaño
            # anterior y no al pedido; pedirlo otra vez lo corrige
            if self.superficie.get_size() != (ancho, alto):
                self.superficie = pygame.display.set_mode((ancho, alto))
            pygame.mouse.set_visible(True)

    def mostrar(self, lienzo_dibujado):
        # Escala el lienzo a la ventana y lo muestra (reemplaza a display.flip())
        ancho_lienzo, alto_lienzo = lienzo_dibujado.get_size()
        ancho_ventana, alto_ventana = self.superficie.get_size()
        escala = min(ancho_ventana / ancho_lienzo, alto_ventana / alto_lienzo)
        if escala == 1:
            self.superficie.blit(lienzo_dibujado, (0, 0))
        else:
            ancho, alto = int(ancho_lienzo * escala), int(alto_lienzo * escala)
            self.superficie.fill((0, 0, 0))
            self.superficie.blit(pygame.transform.scale(lienzo_dibujado, (ancho, alto)),
                                 ((ancho_ventana - ancho) // 2, (alto_ventana - alto) // 2))
        pygame.display.flip()
