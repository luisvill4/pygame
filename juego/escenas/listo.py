"""READY? GO!: se ve la partida quieta durante 1.6 s antes de empezar."""
from juego import dibujo
from juego.dibujo import TITULO
from juego.config import AMARILLO, MAGENTA, VERDE
from juego.escenas.base import Escena
from juego.escenas.juego import Juego


class Listo(Escena):
    def __init__(self, app, partida):
        super().__init__(app)
        self.partida = partida

    def actualizar(self, entrada):
        self.mover_fondo()
        # Si se pierde el foco durante el READY, se pausa apenas empieza el juego
        if entrada.foco_perdido or entrada.mando_desconectado:
            self.partida.pausa_pendiente = True
        if self.tiempo_en_escena() > 1600:
            self.app.cambiar_escena(Juego(self.app, self.partida))

    def dibujar(self, pantalla):
        self.dibujar_partida(pantalla, self.partida)
        if self.tiempo_en_escena() < 1000:
            if dibujo.parpadeo(150):
                dibujo.texto_3d(pantalla, "READY?", TITULO, AMARILLO, MAGENTA, 300)
        else:
            dibujo.texto_3d(pantalla, "GO!", TITULO, VERDE, (0, 90, 40), 300)
        dibujo.efecto_crt(pantalla)
