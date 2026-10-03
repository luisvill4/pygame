"""La nave explota: 1.5 s de explosion y despues Iniciales (si entra al top 5) o Game Over."""
from juego import dibujo
from juego.escenas.base import Escena
from juego.escenas.iniciales import Iniciales
from juego.escenas.fin import Fin


class Explosion(Escena):
    def __init__(self, app, partida):
        super().__init__(app)
        self.partida = partida
        self.saltar_dibujo = False

    def actualizar(self, entrada):
        # El hit-stop del ultimo golpe tambien detiene la explosion un instante
        self.saltar_dibujo = False
        if self.partida.congelar_frames > 0:
            self.partida.congelar_frames -= 1
            self.saltar_dibujo = True
            return

        self.app.efectos.actualizar()
        if self.tiempo_en_escena() > 1500:
            self.app.efectos.reiniciar()
            self.app.sonidos.reproducir("game_over")
            if self.app.records.entra(self.partida.puntaje):
                self.app.cambiar_escena(Iniciales(self.app, self.partida))
            else:
                self.app.cambiar_escena(Fin(self.app, self.partida, fila_nueva=-1))

    def dibujar(self, pantalla):
        if self.saltar_dibujo:
            return
        self.dibujar_partida(pantalla, self.partida, con_nave=False)
        self.app.efectos.aplicar_temblor_y_destello(pantalla)
        dibujo.efecto_crt(pantalla)
