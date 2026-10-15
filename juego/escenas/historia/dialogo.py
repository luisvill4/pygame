"""
DIALOGO: la escena de conversacion del modo historia (antes y despues de cada mision).

Arriba el nombre de la mision; abajo una caja con el retrato grande de quien habla, su
nombre y el texto que se escribe solo. ACEPTAR completa el renglon o pasa al siguiente;
VOLVER saltea todo. Al terminar llama a 'al_terminar' (la escena que sigue la decide
quien abrio el dialogo: asi esta escena no depende de ninguna otra).

El fondo es el del sector de la mision (la App lo deja en su bioma antes de abrirla).
"""
import pygame

from juego import dibujo, interfaz
from juego.dibujo import texto, CHICA, GRANDE
from juego.config import ANCHO, FONDO, TEXTO, TEXTO_SUAVE, DIALOGO_LETRAS_POR_PASO, BLANCO
from juego.entrada import ACEPTAR, VOLVER
from juego.escenas.base import Escena
from juego.historia.personajes import PERSONAJES, dibujar_retrato
from juego.sonido import SILENCIO

CAJA = pygame.Rect(64, 318, ANCHO - 128, 212)
RETRATO = 10                # lado de cada pixel del retrato (12 x 10 = 120 px)
ANCHO_TEXTO = CAJA.width - 12 * RETRATO - 96
FLECHITA = ["XXXXX", ".XXX.", "..X.."]     # "hay mas": late al terminar cada renglon


class Dialogo(Escena):
    musica = SILENCIO           # (las voces y el ambiente del sector, sin musica encima)

    def __init__(self, app, renglones, al_terminar, rotulo="", titulo="", color=BLANCO):
        super().__init__(app)
        self.renglones = renglones          # [(personaje, texto), ...] (historia/personajes.py)
        self.al_terminar = al_terminar
        self.rotulo, self.titulo, self.color = rotulo, titulo, color     # "MISION 1", "LA SEÑAL"
        self.indice = 0
        self.letras = 0.0
        self.terminado = False

    @property
    def ambiente(self):
        return self.app.fondo.sector["ambiente"]

    def renglon_completo(self):
        return self.letras >= len(self.renglones[self.indice][1])

    def actualizar(self, entrada):
        self.mover_fondo()
        if self.terminado:
            return
        antes = int(self.letras)
        self.letras += DIALOGO_LETRAS_POR_PASO
        if int(self.letras) > antes and not self.renglon_completo() and int(self.letras) % 3 == 0:
            self.app.sonidos.reproducir("teclear")      # el teletipo (con enfriamiento)
        if entrada.pulso(VOLVER):
            self.app.sonidos.reproducir("ui_volver")
            self._terminar()
        elif entrada.pulso(ACEPTAR):
            if not self.renglon_completo():
                self.letras = len(self.renglones[self.indice][1])
            elif self.indice + 1 < len(self.renglones):
                self.indice += 1
                self.letras = 0
                self.app.sonidos.reproducir("ui_mover")
            else:
                self.app.sonidos.reproducir("ui_aceptar")
                self._terminar()

    def _terminar(self):
        self.terminado = True
        self.al_terminar()

    # ---------- Dibujo ----------

    def dibujar(self, pantalla):
        self.dibujar_fondo(pantalla)
        if self.titulo:
            texto(pantalla, self.rotulo, CHICA, TEXTO_SUAVE, 64, 74, alinear="izquierda")
            interfaz.titulo(pantalla, self.titulo, 64, 120, self.color, interfaz.mezclar(self.color, FONDO, 0.6),
                            tamano=GRANDE)
        personaje, mensaje = self.renglones[self.indice]
        nombre, color = PERSONAJES[personaje]
        adentro = interfaz.panel(pantalla, CAJA, color, nombre)
        dibujar_retrato(pantalla, personaje, adentro.left + 4, adentro.top + 2, RETRATO)
        texto_x = adentro.left + 12 * RETRATO + 36
        letras = int(self.letras)
        for i, linea in enumerate(dibujo.partir_lineas(mensaje, CHICA, ANCHO_TEXTO)):
            if letras <= 0:
                break
            texto(pantalla, linea[:letras], CHICA, TEXTO, texto_x, adentro.top + 14 + i * 28, alinear="izquierda")
            letras -= len(linea) + 1
        if self.renglon_completo() and dibujo.parpadeo(400):
            dibujo.pixel_art(pantalla, FLECHITA, CAJA.right - 34, CAJA.bottom - 26, color, 4)
        texto(pantalla, "%d/%d" % (self.indice + 1, len(self.renglones)), CHICA, TEXTO_SUAVE, CAJA.right - 24,
              CAJA.top - 18, alinear="derecha")
        interfaz.ayudas(pantalla, self.app.entrada, [("volver", "SALTEAR"), ("aceptar", "SEGUIR")])
