"""
Transicion entre pantallas: un barrido de rombos, como en los juegos de 16 bits.

Al cambiar de escena, la App guarda la ultima imagen de la escena vieja. Durante la
primera mitad se ve esa imagen y unos rombos oscuros la van tapando en diagonal; en la
segunda mitad se ve la escena nueva y los rombos se achican hasta destaparla.

Es solo dibujo: la escena nueva ya esta funcionando desde el primer momento (las teclas
no se pierden y los tests no tienen que esperar). Dura TRANSICION_MS (reloj real).
"""
import pygame

from juego.config import FONDO, TRANSICION_MS

LADO = 40                   # tamaño de la cuadricula de rombos
RETRASO = 0.45              # que parte de la mitad tarda el barrido en cruzar la pantalla


class Transicion:
    def __init__(self, imagen_vieja, desde):
        self.imagen_vieja = imagen_vieja
        self.desde = desde          # ms (reloj real) en que empezo

    def dibujar(self, pantalla, ahora):
        # Dibuja la transicion encima de la escena nueva. Devuelve False cuando termino
        avance = (ahora - self.desde) / TRANSICION_MS
        if avance >= 1:
            return False
        tapando = avance < 0.5
        if tapando:
            pantalla.blit(self.imagen_vieja, (0, 0))
            mitad = avance * 2                  # 0 -> 1: los rombos crecen
        else:
            mitad = 2 - avance * 2              # 1 -> 0: los rombos se achican
        ancho, alto = pantalla.get_size()
        diagonal = ancho + alto
        for fila in range(-1, alto // LADO + 2):
            for columna in range(-1, ancho // LADO + 2):
                x, y = columna * LADO, fila * LADO
                # Cada rombo empieza un poco despues segun que tan a la derecha y abajo esta
                retraso = (x + y) / diagonal * RETRASO
                tamano = min(1, max(0, (mitad - retraso) / (1 - RETRASO)))
                if tamano <= 0:
                    continue
                radio = tamano * LADO          # con 1 los rombos vecinos se tocan y tapan todo
                pygame.draw.polygon(pantalla, FONDO, [(x, y - radio), (x + radio, y), (x, y + radio), (x - radio, y)])
        return True
