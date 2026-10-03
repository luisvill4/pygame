"""Pausa: muestra la ultima imagen del juego oscurecida. Desde aca se abren las Opciones."""
from juego import dibujo
from juego.dibujo import texto, CHICA, TITULO
from juego.config import FONDO, CIAN, BLANCO, GRIS
from juego.entrada import PAUSA, VOLVER, OPCIONES
from juego.escenas.base import Escena
from juego.escenas.opciones import Opciones


class Pausa(Escena):
    def __init__(self, app, escena_juego, captura):
        super().__init__(app)
        self.escena_juego = escena_juego    # a donde se vuelve al seguir
        self.captura = captura              # imagen del juego al pausar

    def actualizar(self, entrada):
        if entrada.pulso(PAUSA) or entrada.pulso(VOLVER):
            self.app.sonidos.reanudar_todo()
            self.app.cambiar_escena(self.escena_juego)
        elif entrada.pulso(OPCIONES):
            self.app.sonidos.reproducir("seleccion")
            self.app.cambiar_escena(Opciones(self.app, volver_a=self, en_partida=True))

    def dibujar(self, pantalla_completa):
        pantalla_completa.blit(self.captura, (0, 0))
        dibujo.oscurecer(pantalla_completa, FONDO, 160)
        pantalla = dibujo.zona_central(pantalla_completa)
        dibujo.texto_3d(pantalla, "PAUSA", TITULO, CIAN, (0, 70, 110), 270)
        ayuda = self.app.entrada.ayuda
        if dibujo.parpadeo():
            texto(pantalla, ayuda("P PARA SEGUIR", "MENU PARA SEGUIR"), CHICA, BLANCO, 400, 350)
        texto(pantalla, ayuda("O OPCIONES", "VISTA OPCIONES"), CHICA, GRIS, 400, 385)
        dibujo.efecto_crt(pantalla_completa)
