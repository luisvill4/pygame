"""
ARCHIVO: los fragmentos de la historia que encontraste (como las terminales de Fallout).

A la izquierda la lista: los encontrados con su nombre y los que faltan como "???" con su
mision (dice cuantos hay, no donde estan). Los 'ocultos' ni aparecen hasta encontrarlos.
A la derecha, el elegido: su texto y, si tiene, el glifo de los Cantores. Con la clave
del compas (glifos.CLAVE_DE_LOS_GLIFOS) los glifos se traducen. Los fragmentos salen de
las misiones registradas (cada mision declara los suyos): uno nuevo aparece solo.
"""
import pygame

from juego import dibujo, interfaz
from juego.dibujo import texto, CHICA, GRANDE
from juego.config import ANCHO, FONDO, VIOLETA, TEXTO, TEXTO_SUAVE, TEXTO_APAGADO, RESALTADO, FILA_ELEGIDA, AMARILLO
from juego.entrada import VOLVER, ACEPTAR, ARRIBA, ABAJO
from juego.escenas.base import Escena
from juego.historia.mision import todos_los_fragmentos
from juego.historia.glifos import CLAVE_DE_LOS_GLIFOS, traducir, dibujar_glifo

LISTA = pygame.Rect(48, 122, 460, 418)
DETALLE = pygame.Rect(532, 122, ANCHO - 580, 418)
COLUMNA_NOMBRE = 84         # donde empieza el nombre en cada renglon de la lista
ALTO_FILA = 34


class Archivo(Escena):
    musica = None
    ambiente = None

    def __init__(self, app, volver_a):
        super().__init__(app)
        self.volver_a = volver_a
        self.elegido = 0
        self.cursor = interfaz.Cursor(0)

    def encontrados(self):
        return self.app.progreso.fragmentos

    def visibles(self):
        # [(fragmento, mision), ...]: todos menos los ocultos que todavia no aparecieron
        return [(fragmento, mision) for fragmento, mision in todos_los_fragmentos()
                if not fragmento.oculto or fragmento.id in self.encontrados()]

    def actualizar(self, entrada):
        self.mover_fondo()
        self.cursor.avanzar()
        cuantos = len(self.visibles())
        if entrada.pulso(ARRIBA) or entrada.pulso(ABAJO):
            self.elegido = (self.elegido + (-1 if entrada.pulso(ARRIBA) else 1)) % cuantos
            self.cursor.ir_a(self.elegido)
            self.app.sonidos.reproducir("ui_mover")
        elif entrada.pulso(VOLVER) or entrada.pulso(ACEPTAR):
            self.app.sonidos.reproducir("ui_volver")
            self.app.cambiar_escena(self.volver_a)

    # ---------- Dibujo ----------

    def dibujar(self, pantalla):
        self.dibujar_fondo(pantalla)
        interfaz.titulo(pantalla, "ARCHIVO", 48, 60, VIOLETA, interfaz.mezclar(VIOLETA, FONDO, 0.6),
                        tamano=GRANDE)
        ids = {fragmento.id for fragmento, _ in todos_los_fragmentos()}
        texto(pantalla, "FRAGMENTOS %d/%d" % (len(self.encontrados() & ids), len(ids)), CHICA, TEXTO_SUAVE,
              ANCHO - 48, 60, alinear="derecha")
        self._dibujar_lista(pantalla)
        self._dibujar_detalle(pantalla)
        interfaz.ayudas(pantalla, self.app.entrada, [("elegir", "ELEGIR"), ("volver", "VOLVER")])

    def _dibujar_lista(self, pantalla):
        adentro = interfaz.panel(pantalla, LISTA, VIOLETA, "REGISTROS")
        franja_y = adentro.top + round(self.cursor.valor * ALTO_FILA)
        pantalla.fill(FILA_ELEGIDA, (adentro.left - 8, franja_y, adentro.width + 16, ALTO_FILA - 6))
        pantalla.fill(VIOLETA, (adentro.left - 8, franja_y, 4, ALTO_FILA - 6))
        for i, (fragmento, mision) in enumerate(self.visibles()):
            y = adentro.top + i * ALTO_FILA + (ALTO_FILA - 6) // 2
            texto(pantalla, "M%d" % mision.numero, CHICA, TEXTO_SUAVE, adentro.left + 4, y, alinear="izquierda")
            if fragmento.id in self.encontrados():
                color = RESALTADO if i == self.elegido else TEXTO
                texto(pantalla, fragmento.nombre, CHICA, color, adentro.left + COLUMNA_NOMBRE, y, alinear="izquierda")
            else:
                texto(pantalla, "? ? ?", CHICA, TEXTO_APAGADO, adentro.left + COLUMNA_NOMBRE, y, alinear="izquierda")

    def _dibujar_detalle(self, pantalla):
        fragmento, mision = self.visibles()[self.elegido]
        if fragmento.id not in self.encontrados():
            adentro = interfaz.panel(pantalla, DETALLE, interfaz.mezclar(VIOLETA, FONDO, 0.5), "SIN DATOS")
            texto(pantalla, "TODAVIA NO LO ENCONTRASTE.", CHICA, TEXTO_SUAVE, adentro.left, adentro.top + 12,
                  alinear="izquierda")
            texto(pantalla, "ESTA EN LA MISION %d." % mision.numero, CHICA, TEXTO_SUAVE, adentro.left,
                  adentro.top + 40, alinear="izquierda")
            return
        adentro = interfaz.panel(pantalla, DETALLE, VIOLETA, fragmento.nombre)
        y = adentro.top + 12
        for parrafo in fragmento.texto:
            for linea in dibujo.partir_lineas(parrafo, CHICA, adentro.width):
                texto(pantalla, linea, CHICA, TEXTO, adentro.left, y, alinear="izquierda")
                y += 26
            y += 14
        if fragmento.glifo:
            y += 10
            texto(pantalla, "GLIFO", CHICA, TEXTO_SUAVE, adentro.left, y, alinear="izquierda")
            dibujar_glifo(pantalla, fragmento.glifo, adentro.left + 96, y, VIOLETA)
            y += 34
            if CLAVE_DE_LOS_GLIFOS in self.encontrados():
                texto(pantalla, "DICE: " + traducir(fragmento.glifo), CHICA, AMARILLO, adentro.left, y,
                      alinear="izquierda")
            else:
                texto(pantalla, "SIN TRADUCIR", CHICA, TEXTO_APAGADO, adentro.left, y, alinear="izquierda")
