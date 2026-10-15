"""
MAPA ESTELAR: el centro del modo historia. Las misiones como planetas unidos por la ruta;
lo recorrido brilla en el color de cada sector y lo que falta esta apagado.

IZQ/DER elige una mision; ACEPTAR despega (dialogo de antes -> READY -> la mision). Se
puede jugar la primera, las cumplidas (para buscar lo que falta del Archivo) y la que
sigue a una cumplida (Mision.disponible). OPCIONES abre el Archivo; VOLVER, el inicio.
Los planetas salen de las misiones registradas (historia/misiones/), cada una en su 'lugar':
una mision nueva aparece sola. Una mision OCULTA no se ve hasta encontrar sus requisitos;
su camino sale de la mision 'rama_de'.

Detalles que cuentan la historia sin decirla: la frase de arriba cambia con lo que pasa
(la Marea, despues el compas, despues el mensaje) y el planeta del Abismo late en el ritmo
del compas (corto, largo...). Lo que pasa al terminar una mision: escenas/historia/pasajes.py.
"""
import math

import pygame

from juego import dibujo, interfaz, nave, accesibilidad
from juego.dibujo import texto, CHICA, MEDIA, GRANDE
from juego.config import (ANCHO, FONDO, SECTORES, ROJO, TEXTO, TEXTO_SUAVE, TEXTO_APAGADO, LINEA_APAGADA, VERDE,
                          CIAN, AMARILLO, VIOLETA, COMPAS_UNIDAD)
from juego.entrada import ACEPTAR, VOLVER, IZQUIERDA, DERECHA, OPCIONES
from juego.escenas.base import Escena
from juego.escenas.historia.dialogo import Dialogo
from juego.escenas.historia.archivo import Archivo
from juego.historia.mision import misiones_en_orden, filtrar
from juego.historia.modo import ModoHistoria
from juego.historia.glifos import sonando, escribir
from juego.sonido import SILENCIO

RADIO_PLANETA = 26
RADIO_OCULTA = 18           # la mision oculta es mas chica (son restos, no un planeta)
INFORME = pygame.Rect(48, 392, ANCHO - 96, 148)
TILDE = [".......", "......X", ".....XX", "X...XX.", "XX.XX..", ".XXX...", "..X...."]
LATE = 5                    # el planeta que late con el compas (el Abismo: de ahi sale)
ULTIMA, VERDAD = 5, "F11"   # la frase de arriba cambia al cumplir la ultima y con la verdad


class Mapa(Escena):
    musica = "menu"
    ambiente = SILENCIO

    def __init__(self, app, elegida=None):
        super().__init__(app)
        self.misiones = [clase for clase in misiones_en_orden() if clase.visible(app.progreso)]
        numeros = [clase.numero for clase in self.misiones]
        elegida = elegida if elegida in numeros else self._la_que_sigue()
        self.indice = numeros.index(elegida)
        self.cursor = interfaz.Cursor(self.indice, rapidez=0.25)

    def _la_que_sigue(self):
        # La primera mision sin cumplir (si estan todas, la ultima del camino principal)
        for clase in self.misiones:
            if clase.numero not in self.app.progreso.misiones and not clase.oculta:
                return clase.numero
        return [clase for clase in self.misiones if not clase.oculta][-1].numero

    @property
    def elegida(self):
        return self.misiones[self.indice].numero

    def mision(self, numero):
        return next(clase for clase in self.misiones if clase.numero == numero)

    def disponible(self, numero):
        return self.mision(numero).disponible(self.app.progreso)

    def actualizar(self, entrada):
        self.mover_fondo()
        self.cursor.avanzar()
        if entrada.pulso(IZQUIERDA) or entrada.pulso(DERECHA):
            paso = -1 if entrada.pulso(IZQUIERDA) else 1
            self.indice = max(0, min(len(self.misiones) - 1, self.indice + paso))
            self.cursor.ir_a(self.indice)
            self.app.sonidos.reproducir("ui_mover")
        elif entrada.pulso(ACEPTAR):
            if self.disponible(self.elegida):
                self.app.sonidos.reproducir("ui_aceptar")
                self._despegar()
            else:
                self.app.sonidos.reproducir("dash_vacio")      # "todavia no"
        elif entrada.pulso(OPCIONES):
            self.app.sonidos.reproducir("ui_aceptar")
            self.app.cambiar_escena(Archivo(self.app, volver_a=self))
        elif entrada.pulso(VOLVER):
            from juego.escenas.inicio import Inicio        # (Inicio abre el Mapa: se importa aca)
            self.app.sonidos.reproducir("ui_volver")
            self.app.cambiar_escena(Inicio(self.app))

    def _despegar(self):
        # El dialogo de antes, en el bioma de la mision, y despues READY -> la mision
        mision = self.mision(self.elegida)
        sector = SECTORES[mision.sector - 1]
        app = self.app
        app.fondo.ir_a_sector(sector, instantaneo=True)
        renglones = filtrar(mision.antes, app.progreso.fragmentos)
        app.cambiar_escena(Dialogo(app, renglones, lambda: app.nueva_partida(modo=ModoHistoria(mision.numero)),
                                   "MISION %d" % mision.numero, mision.titulo, sector["color"]))

    # ---------- Dibujo ----------

    def dibujar(self, pantalla):
        self.dibujar_fondo(pantalla)
        interfaz.titulo(pantalla, "MAPA ESTELAR", 48, 60, CIAN, interfaz.mezclar(CIAN, FONDO, 0.6), tamano=GRANDE)
        self._dibujar_frase(pantalla)
        self._dibujar_ruta(pantalla)
        for clase in self.misiones:
            self._dibujar_planeta(pantalla, clase)
        self._dibujar_nave(pantalla)
        self._dibujar_informe(pantalla)
        interfaz.ayudas(pantalla, self.app.entrada,
                        [("cambiar", "ELEGIR"), ("opciones", "ARCHIVO"), ("volver", "VOLVER"),
                         ("aceptar", "DESPEGAR")])

    def _dibujar_frase(self, pantalla):
        # Arriba a la derecha, lo que importa ahora: la amenaza; despues de la puerta, lo
        # que dice el compas; con la verdad, el mensaje
        progreso = self.app.progreso
        if VERDAD in progreso.fragmentos:
            texto(pantalla, "SEGUI LAS MONEDAS", CHICA, AMARILLO, ANCHO - 48, 60, alinear="derecha")
        elif ULTIMA in progreso.misiones:
            texto(pantalla, "EL COMPAS DICE: VENGAN", CHICA, VIOLETA, ANCHO - 48, 60, alinear="derecha")
        elif dibujo.parpadeo(900):
            texto(pantalla, "LA MAREA LLEGA EN 6 AÑOS", CHICA, ROJO, ANCHO - 48, 60, alinear="derecha")

    def _caminos(self):
        # [(desde, hasta), ...]: cada mision del camino principal con la siguiente, y cada
        # oculta con la mision de donde sale
        principales = [clase for clase in self.misiones if not clase.oculta]
        caminos = list(zip(principales, principales[1:]))
        for clase in self.misiones:
            if clase.oculta and clase.rama_de is not None:
                caminos.append((self.mision(clase.rama_de), clase))
        return caminos

    def _dibujar_ruta(self, pantalla):
        # Puntitos entre un planeta y el siguiente: del color del sector si ya se puede ir
        for desde, hasta in self._caminos():
            (x1, y1), (x2, y2) = desde.lugar, hasta.lugar
            if hasta.disponible(self.app.progreso):
                color = VIOLETA if hasta.oculta else SECTORES[hasta.sector - 1]["color"]
            else:
                color = LINEA_APAGADA
            largo = math.hypot(x2 - x1, y2 - y1)
            pasos = int((largo - 2 * RADIO_PLANETA - 16) // 14)
            for paso in range(pasos + 1):
                avance = (RADIO_PLANETA + 8 + paso * 14) / largo
                x = dibujo.en_grilla(x1 + (x2 - x1) * avance)
                y = dibujo.en_grilla(y1 + (y2 - y1) * avance)
                pantalla.fill(color, (x - 2, y - 2, 4, 4))

    def _dibujar_planeta(self, pantalla, clase):
        centro_x, centro_y = clase.lugar
        numero = clase.numero
        sector = SECTORES[clase.sector - 1]
        radio = RADIO_OCULTA if clase.oculta else RADIO_PLANETA
        disponible = self.disponible(numero)
        if disponible:
            base = VIOLETA if clase.oculta else sector["color"]
            color, sombra = base, interfaz.mezclar(base, FONDO, 0.55)
        else:
            color, sombra = TEXTO_APAGADO, LINEA_APAGADA
        # El Abismo late con el compas (sin destellos reducidos): de ahi sale
        if numero == LATE and not accesibilidad.destellos_reducidos():
            if sonando(escribir("ALBA"), COMPAS_UNIDAD * 2, pygame.time.get_ticks()):
                _anillo(pantalla, centro_x, centro_y, radio + 4, interfaz.mezclar(VIOLETA, FONDO, 0.3))
        _circulo(pantalla, centro_x, centro_y, radio, sombra)
        _circulo(pantalla, centro_x - 4, centro_y - 4, radio - 8, color)
        if numero == self.elegida and dibujo.parpadeo(300):
            _anillo(pantalla, centro_x, centro_y, radio + 10, color)
        texto(pantalla, str(numero) if not clase.oculta else "?", CHICA, TEXTO if disponible else TEXTO_APAGADO,
              centro_x, centro_y + radio + 22)
        if numero in self.app.progreso.misiones:
            dibujo.pixel_art(pantalla, TILDE, centro_x + radio, centro_y - radio, VERDE, 4)
        elif not disponible:
            texto(pantalla, "?", MEDIA, TEXTO_APAGADO, centro_x - 2, centro_y - 2)

    def _dibujar_nave(self, pantalla):
        # La Alondra flota arriba del planeta elegido y se desliza al cambiar
        indice = self.cursor.valor
        base = int(indice)
        siguiente = min(base + 1, len(self.misiones) - 1)
        mezcla = indice - base
        (x1, y1), (x2, y2) = self.misiones[base].lugar, self.misiones[siguiente].lugar
        x = x1 + (x2 - x1) * mezcla
        y = y1 + (y2 - y1) * mezcla
        flota = round(math.sin(pygame.time.get_ticks() / 300) * 2) * 2
        dibujo.pegar(pantalla, nave.imagen("nave"), x, y - RADIO_PLANETA - 44 + flota, centrado=True)

    def _dibujar_informe(self, pantalla):
        numero = self.elegida
        mision = self.mision(numero)
        sector = SECTORES[mision.sector - 1]
        disponible = self.disponible(numero)
        color = (VIOLETA if mision.oculta else sector["color"]) if disponible else TEXTO_APAGADO
        adentro = interfaz.panel(pantalla, INFORME, color, "MISION %d" % numero)
        texto(pantalla, mision.titulo if disponible else "? ? ?", MEDIA, color, adentro.left,
              adentro.top + 10, alinear="izquierda")
        lugar = "AL BORDE DEL ABISMO" if mision.oculta else sector["nombre"]
        texto(pantalla, lugar, CHICA, TEXTO_SUAVE, adentro.left, adentro.top + 46, alinear="izquierda")
        if numero in self.app.progreso.misiones:
            estado, color_estado = "CUMPLIDA", VERDE
        elif disponible:
            estado, color_estado = "NUEVA", AMARILLO
        else:
            estado, color_estado = "CUMPLI LA MISION %d" % (numero - 1), TEXTO_APAGADO
        texto(pantalla, estado, CHICA, color_estado, adentro.right, adentro.top + 10, alinear="derecha")
        # Cuantos fragmentos del Archivo hay en esta mision (no dice donde)
        propios = mision.fragmentos_visibles()
        hallados = len([fragmento for fragmento in propios if fragmento.id in self.app.progreso.fragmentos])
        texto(pantalla, "ARCHIVO %d/%d" % (hallados, len(propios)), CHICA, TEXTO_SUAVE, adentro.right,
              adentro.top + 46, alinear="derecha")
        if not mision.jefe:
            texto(pantalla, "SIN GUARDIAN", CHICA, TEXTO_SUAVE, adentro.right, adentro.top + 82, alinear="derecha")


def _circulo(pantalla, centro_x, centro_y, radio, color):
    # Un circulo lleno en la grilla de 2 px (de a renglones)
    for dy in range(-radio, radio + 1, 2):
        mitad = dibujo.en_grilla(math.sqrt(max(0, radio * radio - dy * dy)))
        pantalla.fill(color, (dibujo.en_grilla(centro_x) - mitad, dibujo.en_grilla(centro_y + dy), 2 * mitad, 2))


def _anillo(pantalla, centro_x, centro_y, radio, color):
    # Un anillo de cuadraditos (el planeta elegido)
    for i in range(24):
        angulo = 2 * math.pi * i / 24
        x = dibujo.en_grilla(centro_x + math.cos(angulo) * radio)
        y = dibujo.en_grilla(centro_y + math.sin(angulo) * radio)
        pantalla.fill(color, (x - 2, y - 2, 4, 4))
