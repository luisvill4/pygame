"""
La ventana real del juego.

Todo se dibuja en un lienzo de 800x600 y mostrar() lo escala a la ventana sin
suavizar (pixeles nitidos), centrado y con barras negras si sobra espacio.
"""
import pygame

from juego.config import ANCHO, ALTO, RESOLUCIONES


class Ventana:
    def __init__(self):
        # Solo las resoluciones que caben en el monitor (80 px de margen para la barra
        # de tareas y el titulo de la ventana); la pantalla completa siempre esta
        alto_escritorio = pygame.display.get_desktop_sizes()[0][1]
        self.resoluciones = [r for r in RESOLUCIONES if r[0] == "COMPLETA" or r[2] + 80 <= alto_escritorio]
        self.superficie = None

    def nombres(self):
        return [r[0] for r in self.resoluciones]

    def aplicar(self, indice):
        # Abre la ventana con la resolucion elegida
        nombre, ancho, alto = self.resoluciones[indice]
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

    def mostrar(self, lienzo):
        # Escala el lienzo a la ventana y lo muestra (reemplaza a display.flip())
        ancho_ventana, alto_ventana = self.superficie.get_size()
        escala = min(ancho_ventana / ANCHO, alto_ventana / ALTO)
        if escala == 1:
            self.superficie.blit(lienzo, (0, 0))
        else:
            ancho, alto = int(ANCHO * escala), int(ALTO * escala)
            self.superficie.fill((0, 0, 0))
            self.superficie.blit(pygame.transform.scale(lienzo, (ancho, alto)),
                                 ((ancho_ventana - ancho) // 2, (alto_ventana - alto) // 2))
        pygame.display.flip()
