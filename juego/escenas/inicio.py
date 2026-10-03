"""Pantalla de inicio: titulo, reglas / mejores puntajes y el menu JUGAR / OPCIONES."""
import math

import pygame

from juego import dibujo, nave
from juego.dibujo import texto, CHICA, MEDIA, TITULO
from juego.config import ROJO, BLANCO, AMARILLO, MAGENTA, CIAN, GRIS, MS_CUADRO_ENEMIGO
from juego.entrada import ACEPTAR, IZQUIERDA, DERECHA
from juego.escenas.base import Escena
from juego.escenas.opciones import Opciones
from juego.enemigos import TIPOS_ENEMIGO
from juego.moneda import imagen_moneda
from juego.powerups import TIPOS_POWERUP
from juego import recursos


def altura_nave():
    # La nave flota en el titulo (se mueve de a 3 pixeles, estilo retro)
    return 250 + round(math.sin(pygame.time.get_ticks() / 300) * 2) * 3


class Inicio(Escena):
    def __init__(self, app):
        super().__init__(app)
        self.opcion = 0         # 0 = JUGAR, 1 = OPCIONES

    def actualizar(self, entrada):
        self.mover_fondo()
        self.app.efectos.estela(400, altura_nave(), 0)
        self.app.efectos.actualizar()

        if entrada.pulso(IZQUIERDA) or entrada.pulso(DERECHA):
            self.opcion = 1 - self.opcion
        if entrada.pulso(ACEPTAR):
            if self.opcion == 0:
                self.app.nueva_partida()
            else:
                self.app.sonidos.reproducir("seleccion")
                self.app.cambiar_escena(Opciones(self.app, volver_a=self))

    def dibujar(self, pantalla_completa):
        # Fondo en todo el ancho; el menu en la zona central de 800x600
        self.dibujar_fondo(pantalla_completa)
        pantalla = dibujo.zona_central(pantalla_completa)

        # Record arriba, como en las maquinas
        texto(pantalla, "RECORD", CHICA, ROJO, 400, 22)
        texto(pantalla, dibujo.numero_arcade(self.app.records.maximo), CHICA, BLANCO, 400, 46)

        # Titulo con relieve y la nave flotando
        dibujo.texto_3d(pantalla, "CAZA", TITULO, AMARILLO, MAGENTA, 115)
        dibujo.texto_3d(pantalla, "MONEDAS", TITULO, AMARILLO, MAGENTA, 180)
        self.app.efectos.dibujar(pantalla)
        imagen_nave = nave.imagen("nave")
        pantalla.blit(imagen_nave, imagen_nave.get_rect(center=(400, altura_nave())))

        # Panel que cambia cada 6 segundos: reglas / mejores puntajes
        dibujo.marco(pantalla, pygame.Rect(170, 290, 460, 180), CIAN)
        if self.app.records.filas and pygame.time.get_ticks() // 6000 % 2 == 1:
            dibujo.tabla_records(pantalla, self.app.records.filas, 315)
        else:
            self._dibujar_reglas(pantalla)

        # Menu: JUGAR / OPCIONES (se elige con izquierda y derecha)
        dibujo.opcion(pantalla, "JUGAR", MEDIA, 270, 530, self.opcion == 0)
        dibujo.opcion(pantalla, "OPCIONES", MEDIA, 540, 530, self.opcion == 1)
        texto(pantalla, self.app.entrada.ayuda("FLECHAS MOVER  ESPACIO DASH  P PAUSA",
                                               "STICK MOVER  X DASH  MENU PAUSA"), CHICA, GRIS, 400, 572)
        dibujo.efecto_crt(pantalla_completa)

    def _dibujar_reglas(self, pantalla):
        moneda = imagen_moneda()
        pantalla.blit(moneda, moneda.get_rect(center=(220, 327)))
        texto(pantalla, "RECOGE", CHICA, BLANCO, 255, 327, alinear="izquierda")
        texto(pantalla, "+1 PUNTO", CHICA, AMARILLO, 600, 327, alinear="derecha")
        enemigo = recursos.cuadro_animado(TIPOS_ENEMIGO["perseguidor"].cuadros(), MS_CUADRO_ENEMIGO)
        pantalla.blit(enemigo, enemigo.get_rect(center=(220, 377)))
        texto(pantalla, "ESQUIVA", CHICA, BLANCO, 255, 377, alinear="izquierda")
        texto(pantalla, "-1 VIDA", CHICA, ROJO, 600, 377, alinear="derecha")
        pygame.draw.line(pantalla, CIAN, (190, 405), (610, 405), 2)

        # Capsulas; una a la vez se explica abajo (cambia cada 2.5 segundos)
        powerups = list(TIPOS_POWERUP.values())
        explicado = powerups[pygame.time.get_ticks() // 2500 % len(powerups)]
        separacion = min(60, 420 // len(powerups))      # si hay muchos, se juntan para entrar en el panel
        primera_x = 400 - separacion * (len(powerups) - 1) // 2
        for i, powerup in enumerate(powerups):
            capsula_x = primera_x + i * separacion
            powerup.dibujar_capsula(pantalla, capsula_x, 437)
            if powerup is explicado:
                pygame.draw.polygon(pantalla, powerup.color,
                                    [(capsula_x - 6, 414), (capsula_x + 6, 414), (capsula_x, 420)])
        texto(pantalla, explicado.nombre + ": " + explicado.descripcion, CHICA, explicado.color, 400, 492)
