"""
Clase base de las escenas (patron "State").

Cada pantalla del juego (Inicio, Juego, Pausa...) es una escena con dos metodos:
    actualizar(entrada): lee las acciones y cambia el estado (o pasa a otra escena)
    dibujar(pantalla):   solo dibuja, sin cambiar nada del juego

La App llama a los dos en cada frame sobre la escena actual. Para cambiar de
pantalla: self.app.cambiar_escena(OtraEscena(self.app, ...)).

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

    def dibujar_partida(self, pantalla, partida, con_nave=True, paralaje=False):
        # Fondo + todo el juego. Con paralaje, el fondo se corre al reves de la nave
        if paralaje:
            empuje_x = -partida.nave.vx * REACCION_PARALAJE
            empuje_y = -partida.nave.vy * REACCION_PARALAJE
        else:
            empuje_x, empuje_y = 0, 0
        self.app.fondo.mover_y_dibujar(pantalla, empuje_x, empuje_y)
        partida.dibujar(pantalla, con_nave)
