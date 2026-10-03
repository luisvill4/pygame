"""
Jugando: avanza la partida un frame, con hit-stop y pausa.

Hit-stop: mientras partida.congelar_frames > 0 no se actualiza ni se redibuja
nada (la pantalla queda quieta un instante despues de un impacto).
"""
from juego import dibujo
from juego.entrada import PAUSA, DASH
from juego.escenas.base import Escena
from juego.escenas.pausa import Pausa
from juego.escenas.explosion import Explosion


class Juego(Escena):
    def __init__(self, app, partida):
        super().__init__(app)
        self.partida = partida
        self.saltar_dibujo = False

    def actualizar(self, entrada):
        partida = self.partida
        if partida.termino:
            self.app.cambiar_escena(Explosion(self.app, partida))
            return
        # Si la ventana pierde el foco o se desconecta el mando, se pausa solo
        if entrada.foco_perdido or entrada.mando_desconectado:
            partida.pausa_pendiente = True

        self.saltar_dibujo = False
        if partida.congelar_frames > 0:
            partida.congelar_frames -= 1
            self.saltar_dibujo = True
            return

        if partida.pausa_pendiente or entrada.pulso(PAUSA):
            partida.pausa_pendiente = False
            self.app.sonidos.pausar_todo()
            self.app.cambiar_escena(Pausa(self.app, self, self.app.pantalla.copy()))
            return

        dx, dy = entrada.direccion()
        partida.actualizar(dx, dy, entrada.pulso(DASH))
        self.mover_fondo(partida)       # con paralaje: el fondo se corre al reves de la nave

        if partida.termino:
            self.app.cambiar_escena(Explosion(self.app, partida))

    def dibujar(self, pantalla):
        if self.saltar_dibujo:
            return
        self.dibujar_partida(pantalla, self.partida, con_nave=True)
        self.app.efectos.dibujar_temblor_y_destello(pantalla)
        dibujo.efecto_crt(pantalla)
