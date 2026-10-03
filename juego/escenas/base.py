"""
Clase base de las escenas (patron "State").

Cada pantalla del juego (Inicio, Juego, Pausa...) es una escena con dos metodos:
    actualizar(entrada): un paso de logica (siempre 60 por segundo): lee las acciones,
                         mueve las cosas y cambia el estado (o pasa a otra escena)
    dibujar(pantalla):   un cuadro (a la frecuencia elegida): SOLO dibuja, sin cambiar
                         nada (puede llamarse varias veces seguidas, o ninguna, por paso)

Para cambiar de pantalla: self.app.cambiar_escena(OtraEscena(self.app, ...)).
self.app.fraccion (0 a 1) es cuanto del paso actual ya paso: para dibujar interpolado.

Flujo:  Inicio -> Listo -> Juego <-> Pausa <-> Opciones
                          Juego -> Explosion -> Iniciales (si entra al top 5) -> Fin -> Listo
"""
from juego.config import REACCION_PARALAJE


class Escena:
    def __init__(self, app):
        self.app = app
        self.inicio = app.ahora()       # momento (reloj real) en que empezo la escena

    def tiempo_en_escena(self):
        return self.app.ahora() - self.inicio

    def actualizar(self, entrada):
        pass

    def dibujar(self, pantalla):
        pass

    def al_cerrar(self):
        # Se llama si se cierra la ventana estando en esta escena
        pass

    def mover_fondo(self, partida=None):
        # Un paso del fondo (va en actualizar). Con una partida, el fondo ademas se corre
        # al reves de la nave (paralaje)
        if partida is not None:
            self.app.fondo.mover(-partida.nave.vx * REACCION_PARALAJE, -partida.nave.vy * REACCION_PARALAJE)
        else:
            self.app.fondo.mover()

    def dibujar_fondo(self, pantalla):
        self.app.fondo.dibujar(pantalla, self.app.fraccion)

    def dibujar_partida(self, pantalla, partida, con_nave=True):
        # Fondo + todo el juego, interpolados
        self.dibujar_fondo(pantalla)
        partida.dibujar(pantalla, con_nave, self.app.fraccion)
