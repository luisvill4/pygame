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
import pygame

from juego.config import REACCION_PARALAJE


class Escena:
    # El tema que suena en esta escena ("menu", "juego", "jefe", "gasolinera", ver sonido.py).
    # None = no la cambia: sigue la que venia (Pausa, Opciones) o el silencio (Game Over)
    musica = None
    # El ambiente del bioma (sonido.AMBIENTES), igual que la musica: None = no lo cambio.
    # Fuera de la partida, SILENCIO
    ambiente = None

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
        relampago_antes = self.app.fondo.relampago
        if partida is not None:
            self.app.fondo.ir_a_sector(partida.director.sector)
            self.app.fondo.mover(-partida.nave.vx * REACCION_PARALAJE, -partida.nave.vy * REACCION_PARALAJE)
        else:
            self.app.fondo.mover()
        if self.app.fondo.relampago > relampago_antes:
            self.app.sonidos.reproducir_luego("trueno", 450)   # el trueno llega despues del destello

    def dibujar_fondo(self, pantalla):
        self.app.fondo.dibujar(pantalla, self.app.fraccion)

    def dibujar_partida(self, pantalla, partida, con_nave=True):
        # Por capas: fondo y mundo (interpolados) -> temblor y destello -> HUD.
        # El temblor y el destello van antes del HUD: mueven el mundo, no el marcador
        self.dibujar_fondo(pantalla)
        partida.dibujar(pantalla, con_nave, self.app.fraccion)
        self.app.efectos.dibujar_temblor_y_destello(pantalla)
        partida.dibujar_impactos(pantalla)
        partida.dibujar_hud(pantalla)

    def captura_del_mundo(self, partida):
        # El fondo y el juego, sin HUD ni temblor: el fondo de la Pausa, el Taller...
        imagen = pygame.Surface(self.app.pantalla.get_size())
        self.dibujar_fondo(imagen)
        partida.dibujar(imagen, True, self.app.fraccion)
        return imagen
