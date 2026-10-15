"""READY? GO!: se ve la partida quieta durante 1.6 s antes de empezar."""
from juego import dibujo, interfaz, carteles
from juego.dibujo import CHICA, TITULO
from juego.config import CENTRO_X, AMARILLO, MAGENTA, VERDE, CIAN, CONTORNO
from juego.escenas.base import Escena
from juego.sonido import SILENCIO
from juego.escenas.juego import Juego, musica_del_sector


class Listo(Escena):
    @property
    def musica(self):
        # READY? en silencio (suena su pregunta); la musica del juego entra con el GO!
        return musica_del_sector(self.partida) if self.tiempo_en_escena() >= 1000 else SILENCIO

    @property
    def ambiente(self):
        return self.partida.director.sector["ambiente"]

    def __init__(self, app, partida):
        super().__init__(app)
        self.partida = partida

    def actualizar(self, entrada):
        self.mover_fondo()
        if not getattr(self, "ready_sonado", False):
            self.ready_sonado = True
            self.app.sonidos.reproducir_luego("listo_ready", 200)
        if self.tiempo_en_escena() >= 1000 and not getattr(self, "go_sonado", False):
            self.go_sonado = True
            self.app.sonidos.reproducir("listo_go")
        # Si se pierde el foco durante el READY, se pausa apenas empieza el juego
        if entrada.foco_perdido or entrada.mando_desconectado:
            self.partida.pausa_pendiente = True
        if self.tiempo_en_escena() > 1600:
            self.app.cambiar_escena(Juego(self.app, self.partida), transicion=False)

    def dibujar(self, pantalla):
        # Una franja de lado a lado (se abre al empezar) con "READY?" y despues "GO!", y
        # arriba el sector y la dificultad
        self.dibujar_partida(pantalla, self.partida)
        transcurrido = self.tiempo_en_escena()
        listo = transcurrido >= 1000
        color = VERDE if listo else CIAN
        alto = round(min(1, transcurrido / 180) * 120)
        franja = carteles.franja(pantalla, 300, alto, color)       # la misma de los momentos del juego
        if franja is None or alto < 120:
            return
        director = self.partida.director
        # El renglon de arriba lo arma el modo (el sector, o la mision en la historia)
        interfaz.renglon(pantalla, self.partida.modo.encabezado(director), CHICA, CENTRO_X, franja.top + 18)
        if listo:
            dibujo.texto_3d(pantalla, "GO!", TITULO, VERDE, (0, 90, 40), 312, 6, CONTORNO)
        elif dibujo.parpadeo(150):
            dibujo.texto_3d(pantalla, "READY?", TITULO, AMARILLO, MAGENTA, 312, 6, CONTORNO)
