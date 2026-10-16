"""
HANGAR: las mejoras para siempre de la Alondra, compradas con piezas. Dos pestañas (LB/RB o Q/E):

    INSTALACIONES   las seis de historia/hangar.py en cartas (las mismas del Taller: interfaz.carta),
                    en dos filas de tres. Lo instalado se suma al empezar cada partida de la historia
    MODULOS         los de historia/modulos.py: abren los sistemas con peligro ambiental. Se
                    fabrican con su PLANO y piezas. A la izquierda, la Alondra en grande (como un
                    plano de ingenieria) con la pieza del nivel siguiente titilando encima: asi se
                    ve como queda antes de comprarla

Las flechas eligen; ACEPTAR compra (si alcanzan las piezas); VOLVER vuelve a la galaxia.
"""
import pygame

from juego import interfaz, nave, dibujo
from juego.dibujo import texto, CHICA, MEDIA
from juego.config import ANCHO, FONDO, AMARILLO, TEXTO_SUAVE, TEXTO_APAGADO, VERDE, ROJO, LINEA_APAGADA, CIAN
from juego.entrada import (ACEPTAR, VOLVER, IZQUIERDA, DERECHA, ARRIBA, ABAJO, PESTANA_ANTERIOR,
                           PESTANA_SIGUIENTE)
from juego.escenas.base import Escena
from juego.historia import hangar, modulos

INSTALACIONES, MODULOS = "INSTALACIONES", "MODULOS"
PESTANAS = [INSTALACIONES, MODULOS]
BARRA_PESTANAS = pygame.Rect(48, 64, ANCHO - 96, 28)
# (las cartas necesitan 200 de alto: mas bajas, los cuadraditos del nivel pisan la descripcion)
ARRIBA_CARTAS, ALTO_CARTA, SEPARACION, ENTRE_FILAS = 108, 200, 24, 12
POR_FILA = {INSTALACIONES: 3, MODULOS: 2}
PANEL_NAVE = pygame.Rect(48, ARRIBA_CARTAS, 320, 2 * ALTO_CARTA + ENTRE_FILAS)     # la Alondra en grande
ESCALA_NAVE = 5             # 50 x 50 -> 250 x 250 (entero: los pixeles de arte siguen cuadrados)
NOTA_Y = PANEL_NAVE.bottom + 18         # el renglon de abajo (que hace lo elegido)


class Hangar(Escena):
    musica = None
    ambiente = None

    def __init__(self, app, volver_a):
        super().__init__(app)
        self.volver_a = volver_a
        self.instalaciones = hangar.instalaciones()
        self.pestana = 0
        self.elegidas = {INSTALACIONES: 0, MODULOS: 0}      # cada pestaña recuerda su carta

    # ---------- Consultas ----------

    @property
    def seccion(self):
        return PESTANAS[self.pestana]

    def cartas(self):
        return self.instalaciones if self.seccion == INSTALACIONES else modulos.MODULOS

    def elegida(self):
        return self.cartas()[self.elegidas[self.seccion]]

    def caja(self, i, seccion=None):
        # Donde va la carta i: tres por fila a todo el ancho, o dos al lado de la nave
        seccion = seccion or self.seccion
        por_fila = POR_FILA[seccion]
        izquierda = 48 if seccion == INSTALACIONES else PANEL_NAVE.right + SEPARACION
        ancho = (ANCHO - 48 - izquierda - SEPARACION * (por_fila - 1)) // por_fila // 2 * 2
        fila, columna = divmod(i, por_fila)
        return pygame.Rect(izquierda + columna * (ancho + SEPARACION), ARRIBA_CARTAS + fila * (ALTO_CARTA + ENTRE_FILAS),
                           ancho, ALTO_CARTA)

    # ---------- Cada paso ----------

    def actualizar(self, entrada):
        self.mover_fondo()
        nave.preparar_giros(2)          # (los giros de la nave equipada, para el despegue: ver nave.girada)
        if entrada.pulso(PESTANA_ANTERIOR) or entrada.pulso(PESTANA_SIGUIENTE):
            self.pestana = (self.pestana + (1 if entrada.pulso(PESTANA_SIGUIENTE) else -1)) % len(PESTANAS)
            self.app.sonidos.reproducir("ui_pestana")
            return
        por_fila = POR_FILA[self.seccion]
        pasos = {IZQUIERDA: -1, DERECHA: 1, ARRIBA: -por_fila, ABAJO: por_fila}
        movida = next((paso for accion, paso in pasos.items() if entrada.pulso(accion)), None)
        if movida is not None:
            self.elegidas[self.seccion] = (self.elegidas[self.seccion] + movida) % len(self.cartas())
            self.app.sonidos.reproducir("ui_mover")
        elif entrada.pulso(ACEPTAR):
            self._comprar()
        elif entrada.pulso(VOLVER):
            self.app.sonidos.reproducir("ui_volver")
            self.app.cambiar_escena(self.volver_a)

    def _comprar(self):
        progreso = self.app.progreso
        elegida = self.elegida()
        if self.seccion == INSTALACIONES:
            listo = hangar.comprar(progreso, elegida.tipo)
        else:
            listo = modulos.fabricar(progreso, elegida.id)
        if listo:
            nave.cambiar_equipo(modulos.equipo(progreso))      # (el impulsor y los modulos se ven)
            self.app.sonidos.reproducir("mejora_elegida")
        else:
            self.app.sonidos.reproducir("dash_vacio")

    # ---------- Dibujo ----------

    def dibujar(self, pantalla):
        self.dibujar_fondo(pantalla)
        progreso = self.app.progreso
        interfaz.titulo(pantalla, "HANGAR", 48, 36, AMARILLO, interfaz.mezclar(AMARILLO, FONDO, 0.6), tamano=MEDIA)
        texto(pantalla, "PIEZAS %d" % progreso.piezas, CHICA, AMARILLO, ANCHO - 48, 36, alinear="derecha")
        interfaz.pestanas(pantalla, BARRA_PESTANAS, self.app.entrada, PESTANAS, self.pestana, AMARILLO,
                          interfaz.mezclar(AMARILLO, FONDO, 0.8))
        if self.seccion == INSTALACIONES:
            self._dibujar_instalaciones(pantalla)
        else:
            self._dibujar_modulos(pantalla)
        nota, color = self.nota()
        texto(pantalla, nota, CHICA, color, ANCHO // 2, NOTA_Y)
        interfaz.ayudas(pantalla, self.app.entrada, [("pestanas", "SECCION"), ("mover", "ELEGIR"),
                                                     ("volver", "VOLVER"), ("aceptar", "COMPRAR")])

    def _carta(self, pantalla, i, color, icono, nombre, descripcion, nivel, precio, sin_plano=False):
        # Una carta con su etiqueta abajo: el precio, COMPLETO o SIN PLANO. 'nivel' = (tiene, maximo)
        caja = self.caja(i)
        completa = precio is None
        interfaz.carta(pantalla, caja, color, icono, nombre, descripcion, elegida=i == self.elegidas[self.seccion],
                       apagada=completa or sin_plano, nivel=nivel)
        if sin_plano:
            etiqueta, color_etiqueta = "SIN PLANO", TEXTO_APAGADO
        elif completa:
            etiqueta, color_etiqueta = "COMPLETO", VERDE
        else:
            etiqueta = "%d PIEZAS" % precio
            color_etiqueta = AMARILLO if self.app.progreso.piezas >= precio else ROJO
        texto(pantalla, etiqueta, CHICA, color_etiqueta, caja.centerx, caja.bottom - 16)

    def _dibujar_instalaciones(self, pantalla):
        progreso = self.app.progreso
        for i, instalacion in enumerate(self.instalaciones):
            self._carta(pantalla, i, instalacion.color, instalacion.icono, instalacion.nombre, instalacion.descripcion,
                        (hangar.nivel(progreso, instalacion.tipo), instalacion.maximo),
                        hangar.precio(progreso, instalacion.tipo))

    def _dibujar_modulos(self, pantalla):
        progreso = self.app.progreso
        for i, modulo in enumerate(modulos.MODULOS):
            self._carta(pantalla, i, modulo.color, modulo.icono, modulo.nombre, modulo.descripcion,
                        (modulos.nivel(progreso, modulo.id), modulo.maximo), modulos.precio(progreso, modulo.id),
                        sin_plano=not modulos.tiene_plano(progreso, modulo.id))
        self._dibujar_nave(pantalla)

    def _dibujar_nave(self, pantalla):
        # La Alondra en grande sobre una cuadricula de plano. Si el modulo elegido tiene un nivel
        # mas, su pieza titila encima (la nave con y sin ella, alternadas)
        progreso = self.app.progreso
        modulo = self.elegida()
        siguiente = modulos.nivel(progreso, modulo.id) + 1
        adentro = interfaz.panel(pantalla, PANEL_NAVE, CIAN, "ALONDRA")
        for x in range(adentro.left, adentro.right, 16):
            for y in range(adentro.top, adentro.bottom, 16):
                pantalla.fill(LINEA_APAGADA, (x, y, 2, 2))
        capas = modulos.equipo(progreso)
        if siguiente <= modulo.maximo and dibujo.parpadeo(500):
            capas = modulos.equipo(progreso, extra=(modulo.id, siguiente))
        imagen = nave.armar(capas)
        grande = pygame.transform.scale(imagen, (imagen.get_width() * ESCALA_NAVE, imagen.get_height() * ESCALA_NAVE))
        dibujo.pegar(pantalla, grande, adentro.centerx, adentro.centery - 12, centrado=True)
        if siguiente <= modulo.maximo:
            rotulo, color = "%s %d" % (modulo.nombre, siguiente), modulo.color
        else:
            rotulo, color = "%s AL MAXIMO" % modulo.peligro.upper(), VERDE
        texto(pantalla, rotulo, CHICA, color, adentro.centerx, adentro.bottom - 8)

    def nota(self):
        # El renglon de abajo: que hace lo elegido (o donde se consigue su plano)
        progreso = self.app.progreso
        if self.seccion == INSTALACIONES:
            return "LAS PIEZAS SALEN DE LAS MONEDAS. LO LEJANO DA MAS.", TEXTO_SUAVE
        modulo = self.elegida()
        if not modulos.tiene_plano(progreso, modulo.id):
            biomas, misiones = modulos.donde_esta_el_plano(modulo.id)
            lugares = biomas + ["LA MISION %d" % numero for numero in misiones]
            if len(lugares) > 1:                    # "A, B O C"
                lugares = [", ".join(lugares[:-1]) + " O " + lugares[-1]]
            return "PLANO: %s." % lugares[0], TEXTO_SUAVE
        siguiente = modulos.nivel(progreso, modulo.id) + 1
        if siguiente > modulo.maximo:
            return "ENTRA A CUALQUIER LUGAR CON %s." % modulo.peligro.upper(), VERDE
        abre = len(modulos.lo_que_abre(modulo.id, siguiente))
        return "NIVEL %d: ABRE %d LUGARES CON %s %d." % (siguiente, abre, modulo.peligro.upper(), siguiente), \
            TEXTO_SUAVE
