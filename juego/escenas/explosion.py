"""
La nave explota: 1.5 s de explosion y despues Iniciales (si entra al top 5) o Game Over.

Para que se sienta: los primeros CAMARA_LENTA ms las particulas van a la mitad de
velocidad, una vineta roja se va cerrando y aparece "NAVE DESTRUIDA".
"""
import pygame

from juego import dibujo, impactos
from juego.dibujo import GRANDE
from juego.config import ROJO, CONTORNO
from juego.escenas.base import Escena
from juego.sonido import SILENCIO
from juego.escenas.pasajes import pasajes_de


CAMARA_LENTA = 600          # ms en que las particulas van a la mitad de velocidad


class Explosion(Escena):
    ambiente = SILENCIO
    def __init__(self, app, partida):
        super().__init__(app)
        self.partida = partida
        self.saltar_dibujo = False
        self.pasos = 0

    def actualizar(self, entrada):
        # El hit-stop del ultimo golpe tambien detiene la explosion un instante
        self.saltar_dibujo = False
        if self.partida.congelar_frames > 0:
            self.partida.congelar_frames -= 1
            self.saltar_dibujo = True
            return

        self.partida.guardar_posiciones()   # las particulas de la explosion se dibujan interpoladas
        self.pasos += 1
        if self.tiempo_en_escena() > CAMARA_LENTA or self.pasos % 2 == 0:
            self.app.efectos.actualizar()      # (en camara lenta, un paso si y uno no)
        self.mover_fondo()
        if self.tiempo_en_escena() > 450 and not getattr(self, "cartel_sonado", False):
            self.cartel_sonado = True
            self.app.sonidos.reproducir("destruida")      # cuando aparece "NAVE DESTRUIDA"
        if self.tiempo_en_escena() > 1500:
            self.app.efectos.reiniciar()
            self.app.sonidos.reproducir("game_over")
            # Que sigue lo decide el modo: el arcade, las iniciales o el Game Over; la
            # historia, Ines te saca y se vuelve al mapa (escenas/pasajes.py)
            pasajes_de(self.partida).al_morir(self.app, self.partida)

    def dibujar(self, pantalla):
        if self.saltar_dibujo:
            return
        self.dibujar_partida(pantalla, self.partida, con_nave=False)
        # La vineta roja se va cerrando y despues aparece el cartel
        avance = min(1, self.tiempo_en_escena() / 1500)
        vineta = impactos.vineta(pantalla.get_size(), (60, 0, 12))
        vineta.set_alpha(round(220 * avance))
        pantalla.blit(vineta, (0, 0))
        if self.tiempo_en_escena() > 450:
            dibujo.texto_3d(pantalla, "NAVE DESTRUIDA", GRANDE, ROJO, (90, 0, 20), pantalla.get_height() // 2,
                            4, CONTORNO)

