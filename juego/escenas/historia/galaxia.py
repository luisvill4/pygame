"""
GALAXIA: el centro del modo historia. Un mapa mas grande que la pantalla, como el mapa estelar
de Starfield: la camara sigue al sistema elegido.

    - Las MISIONES de la historia (en orden: se puede jugar la primera, las cumplidas y la que
      sigue a una cumplida), los SISTEMAS LIBRES (cuando quieras: cuanto mas lejos de la Umbral,
      mas peligro y mas piezas) y la ESTACION UMBRAL, la casa (historia/galaxia.py).
    - VIAJAR CUESTA AÑOS en la Umbral (historia/tiempo.py): la Alondra vuela hasta el sistema
      mientras corre el reloj, y al llegar, si paso un año, Ines manda su mensaje. El frente de
      la Marea avanza desde la izquierda: a los 6 años se traga la Umbral.
    - El panel de abajo dice todo del sistema elegido: peligro, cuanto cuesta el viaje, en que
      año llegas, si tiene dilatacion y que encontraste ahi.
DIRECCIONES elige el sistema mas cercano hacia ese lado; ACEPTAR viaja y despega; OPCIONES abre
el Archivo; PAUSA, el Hangar; VOLVER, el inicio. Lo que pasa al terminar: pasajes.py.
"""
import math

import pygame

from juego import dibujo, interfaz, nave, accesibilidad, recursos
from juego.dibujo import texto, CHICA, MEDIA, MINI
from juego.config import (ANCHO, FONDO, SECTORES, ROJO, TEXTO, TEXTO_SUAVE, TEXTO_APAGADO, LINEA_APAGADA, VERDE,
                          CIAN, AMARILLO, VIOLETA, COMPAS_UNIDAD, MAREA_ANIOS, BLANCO, CONTORNO)
from juego.entrada import ACEPTAR, VOLVER, IZQUIERDA, DERECHA, ARRIBA, ABAJO, OPCIONES, PAUSA
from juego.escenas.base import Escena
from juego.escenas.historia.dialogo import Dialogo
from juego.escenas.historia.archivo import Archivo
from juego.escenas.historia.hangar import Hangar
from juego.historia.mision import filtrar
from juego.historia.modo import ModoHistoria
from juego.historia.exploracion import ModoExploracion
from juego.historia import galaxia, tiempo
from juego.historia.glifos import sonando, escribir
from juego.sonido import SILENCIO

VISTA = pygame.Rect(0, 72, ANCHO, 316)      # la ventana al mapa (lo de afuera no se dibuja)
INFORME = pygame.Rect(48, 400, ANCHO - 96, 144)
VIAJE_PASOS = 75            # lo que dura el vuelo en la pantalla (pasos)
RADIO_MISION = 14
LATE = "M5"                 # el sistema que late con el compas (de ahi sale)
VERDAD = "F11"
DIRECCIONES = {IZQUIERDA: (-1, 0), DERECHA: (1, 0), ARRIBA: (0, -1), ABAJO: (0, 1)}
TILDE = [".......", "......X", ".....XX", "X...XX.", "XX.XX..", ".XXX...", "..X...."]
ESTRELLA = ["..X..", ".XXX.", "XXXXX", ".XXX.", "..X.."]
ESTACION = ["...X...", "..XXX..", "X.XXX.X", "XXXXXXX", "X.XXX.X", "..XXX..", "...X..."]


class Galaxia(Escena):
    musica = "menu"
    ambiente = SILENCIO

    def __init__(self, app, elegida=None):
        super().__init__(app)
        self.progreso = app.progreso
        visibles = [uno.id for uno in self.sistemas()]
        self.elegida = elegida if elegida in visibles else self.progreso.ubicacion
        if self.elegida not in visibles:
            self.elegida = galaxia.UMBRAL
        self.camara = list(self._camara_para(self.sistema(self.elegida).lugar))
        self.viaje = None           # el vuelo en curso: {"desde", "hasta", "paso", "costo", "anios"}

    # ---------- Consultas ----------

    def sistemas(self):
        # Los que se ven: todos menos las misiones ocultas que todavia no aparecieron
        return [uno for uno in galaxia.todos_los_sistemas()
                if uno.mision is None or uno.mision.visible(self.progreso)]

    def sistema(self, id_):
        return next(uno for uno in self.sistemas() if uno.id == id_)

    def ubicacion(self):
        ids = [uno.id for uno in self.sistemas()]
        return self.sistema(self.progreso.ubicacion if self.progreso.ubicacion in ids else galaxia.UMBRAL)

    def por_que_no(self, uno):
        # Si no se puede ir: por que (None = se puede)
        if uno.tipo == "umbral":
            return "LA CASA. NO HAY NADA QUE HACER ACA."
        if tiempo.tragado(uno, self.progreso.anios):
            return "LA MAREA SE LO TRAGO."
        if tiempo.tragado(uno, self.progreso.anios + self.costo(uno)):
            return "LA MAREA LLEGA ANTES QUE VOS."      # (el frente sigue avanzando mientras viajas)
        if uno.mision is not None and not uno.mision.disponible(self.progreso):
            return "CUMPLI LA MISION %d PRIMERO." % (uno.mision.numero - 1)
        return None

    def costo(self, uno):
        return galaxia.costo_viaje(self.ubicacion(), uno, self.progreso)

    def anios_que_se_ven(self):
        # Durante el vuelo, el reloj corre
        if self.viaje is None:
            return self.progreso.anios
        avance = min(1, self.viaje["paso"] / VIAJE_PASOS)
        return self.viaje["anios"] + self.viaje["costo"] * avance

    # ---------- Cada paso ----------

    def actualizar(self, entrada):
        self.mover_fondo()
        if self.viaje is not None:
            self._volar()
            return
        for accion, (dx, dy) in DIRECCIONES.items():
            if entrada.pulso(accion):
                otro = self._vecino(dx, dy)
                if otro is not None:
                    self.elegida = otro.id
                    self.app.sonidos.reproducir("ui_mover")
                break
        else:
            if entrada.pulso(ACEPTAR):
                self._viajar(self.sistema(self.elegida))
            elif entrada.pulso(OPCIONES):
                self.app.sonidos.reproducir("ui_aceptar")
                self.app.cambiar_escena(Archivo(self.app, volver_a=self))
            elif entrada.pulso(PAUSA):
                self.app.sonidos.reproducir("ui_aceptar")
                self.app.cambiar_escena(Hangar(self.app, volver_a=self))
            elif entrada.pulso(VOLVER):
                from juego.escenas.inicio import Inicio        # (Inicio abre la Galaxia: se importa aca)
                self.app.sonidos.reproducir("ui_volver")
                self.app.cambiar_escena(Inicio(self.app))
        self._mover_camara(self.sistema(self.elegida).lugar)

    def _vecino(self, dx, dy):
        # El sistema mas cercano hacia ese lado (en un cono): el mas cerca y el mas derecho gana
        actual = self.sistema(self.elegida)
        mejor, puntaje_mejor = None, math.inf
        for otro in self.sistemas():
            lejos_x, lejos_y = otro.lugar[0] - actual.lugar[0], otro.lugar[1] - actual.lugar[1]
            distancia = math.hypot(lejos_x, lejos_y)
            if distancia == 0:
                continue
            derecho = (lejos_x * dx + lejos_y * dy) / distancia
            if derecho < 0.45:
                continue
            puntaje = distancia * (2 - derecho)
            if puntaje < puntaje_mejor:
                mejor, puntaje_mejor = otro, puntaje
        return mejor

    def _camara_para(self, lugar):
        x = min(max(lugar[0] - ANCHO / 2, 0), galaxia.ANCHO_GALAXIA - ANCHO)
        y = min(max(lugar[1] - VISTA.height / 2, 0), galaxia.ALTO_GALAXIA - VISTA.height)
        return x, y

    def _mover_camara(self, lugar):
        destino = self._camara_para(lugar)
        for i in (0, 1):
            self.camara[i] += (destino[i] - self.camara[i]) * 0.15

    # ---------- El viaje ----------

    def _viajar(self, uno):
        if self.por_que_no(uno) is not None:
            self.app.sonidos.reproducir("dash_vacio")      # "todavia no"
            return
        self.app.sonidos.reproducir("ui_aceptar")
        desde = self.ubicacion()
        self.viaje = {"desde": desde, "hasta": uno, "paso": 0 if desde is not uno else VIAJE_PASOS,
                      "costo": self.costo(uno), "anios": self.progreso.anios}
        if desde is not uno:
            self.app.sonidos.reproducir("nave_dash_1")

    def _volar(self):
        viaje = self.viaje
        viaje["paso"] += 1
        self._mover_camara(self._lugar_de_la_nave())
        if viaje["paso"] < VIAJE_PASOS:
            return
        # Llego: el reloj de la Umbral avanza y la Alondra queda ahi
        self.viaje = None
        hasta = viaje["hasta"]
        tiempo.pasar(self.progreso, viaje["costo"])
        self.progreso.ubicacion = hasta.id
        self.progreso.guardar()
        self._llegar(hasta)

    def _llegar(self, hasta):
        # Si pasaron años, primero el mensaje de Ines (para ella fueron años; para Alba, horas)
        pendientes = tiempo.mensajes_pendientes(self.progreso)
        renglones = [renglon for _, lista in pendientes for renglon in lista]
        for anio, _ in pendientes:
            self.progreso.mensajes.add(anio)
        self.progreso.guardar()
        if renglones:
            anio = int(self.progreso.anios)
            self.app.cambiar_escena(Dialogo(self.app, renglones, lambda: self._despegar(hasta), "ESTACION UMBRAL",
                                            "AÑO %d" % anio, AMARILLO))
        else:
            self._despegar(hasta)

    def _despegar(self, hasta):
        # Al bioma del sistema; una mision tiene su dialogo de antes, un sistema libre despega ya
        app = self.app
        app.fondo.ir_a_sector(hasta.bioma, instantaneo=True)
        if hasta.mision is None:
            app.nueva_partida(modo=ModoExploracion(hasta.id))
            return
        clase = hasta.mision
        renglones = filtrar(clase.antes, self.progreso.fragmentos, self.progreso.anios)
        app.cambiar_escena(Dialogo(app, renglones, lambda: app.nueva_partida(modo=ModoHistoria(clase.numero)),
                                   "MISION %d" % clase.numero, clase.titulo, hasta.bioma["color"]))

    def _lugar_de_la_nave(self):
        if self.viaje is None:
            return self.ubicacion().lugar
        (x1, y1), (x2, y2) = self.viaje["desde"].lugar, self.viaje["hasta"].lugar
        avance = min(1, self.viaje["paso"] / VIAJE_PASOS)
        avance = avance * avance * (3 - 2 * avance)        # arranca y frena suave
        return x1 + (x2 - x1) * avance, y1 + (y2 - y1) * avance

    # ---------- Dibujo ----------

    def en_pantalla(self, lugar):
        return (dibujo.en_grilla(lugar[0] - self.camara[0]), dibujo.en_grilla(lugar[1] - self.camara[1] + VISTA.top))

    def dibujar(self, pantalla):
        self.dibujar_fondo(pantalla)
        pantalla.set_clip(VISTA)
        self._dibujar_cuadricula(pantalla)
        self._dibujar_zonas(pantalla)
        self._dibujar_caminos(pantalla)
        for uno in self.sistemas():
            self._dibujar_sistema(pantalla, uno)
        self._dibujar_ruta_del_viaje(pantalla)
        self._dibujar_marea(pantalla)
        self._dibujar_nave(pantalla)
        pantalla.set_clip(None)
        pygame.draw.rect(pantalla, LINEA_APAGADA, VISTA.inflate(0, 4), 2)
        self._dibujar_cabecera(pantalla)
        self._dibujar_informe(pantalla)
        interfaz.ayudas(pantalla, self.app.entrada,
                        [("mover", "ELEGIR"), ("opciones", "ARCHIVO"), ("pausa", "HANGAR"), ("volver", "VOLVER"),
                         ("aceptar", "VIAJAR")])

    def _dibujar_cabecera(self, pantalla):
        texto(pantalla, "GALAXIA", MEDIA, CIAN, 48, 40, alinear="izquierda")
        anios = self.anios_que_se_ven()
        progreso = self.progreso
        if tiempo.historia_terminada(progreso):
            frase, color = ("SEGUI LAS MONEDAS", AMARILLO) if VERDAD in progreso.fragmentos else \
                ("EL COMPAS DICE: VENGAN", VIOLETA)
        elif anios >= MAREA_ANIOS:
            frase, color = "LA MAREA LLEGO", ROJO
        else:
            frase, color = "LA MAREA LLEGA EN %.1f AÑOS" % (MAREA_ANIOS - anios), ROJO
        texto(pantalla, frase, CHICA, color, ANCHO - 48, 32, alinear="derecha")
        texto(pantalla, "AÑO %.1f EN LA UMBRAL   PIEZAS %d" % (anios, progreso.piezas), CHICA, TEXTO_SUAVE,
              ANCHO - 48, 54, alinear="derecha")

    def _dibujar_cuadricula(self, pantalla):
        # Una grilla tenue cada 200 px del mapa (da escala, como una carta de navegacion)
        for x in range(0, galaxia.ANCHO_GALAXIA + 1, 200):
            pantalla_x, _ = self.en_pantalla((x, 0))
            for y in range(VISTA.top, VISTA.bottom, 8):
                pantalla.fill(LINEA_APAGADA, (pantalla_x, y, 2, 2))
        for y in range(0, galaxia.ALTO_GALAXIA + 1, 200):
            _, pantalla_y = self.en_pantalla((0, y))
            for x in range(0, ANCHO, 8):
                pantalla.fill(LINEA_APAGADA, (x, pantalla_y, 2, 2))

    def _dibujar_zonas(self, pantalla):
        # El nombre de cada bioma, abajo de su zona
        for numero, desde in enumerate(galaxia.ZONAS):
            sector = SECTORES[numero]
            x, _ = self.en_pantalla((desde + 20, 0))
            texto(pantalla, sector["nombre"], MINI, interfaz.mezclar(sector["color"], FONDO, 0.45), x,
                  VISTA.bottom - 14, alinear="izquierda")

    def _linea_punteada(self, pantalla, desde, hasta, color, separacion=14, margen=20):
        (x1, y1), (x2, y2) = self.en_pantalla(desde), self.en_pantalla(hasta)
        largo = math.hypot(x2 - x1, y2 - y1)
        if largo <= 2 * margen:
            return
        for paso in range(int((largo - 2 * margen) // separacion) + 1):
            avance = (margen + paso * separacion) / largo
            x = dibujo.en_grilla(x1 + (x2 - x1) * avance)
            y = dibujo.en_grilla(y1 + (y2 - y1) * avance)
            pantalla.fill(color, (x - 2, y - 2, 4, 4))

    def _dibujar_caminos(self, pantalla):
        # El camino de la historia (de mision en mision) y las puertas menores conocidas
        progreso = self.progreso
        misiones = [uno for uno in self.sistemas() if uno.mision is not None and not uno.mision.oculta]
        for desde, hasta in zip(misiones, misiones[1:]):
            color = hasta.bioma["color"] if hasta.mision.disponible(progreso) else LINEA_APAGADA
            self._linea_punteada(pantalla, desde.lugar, hasta.lugar, interfaz.mezclar(color, FONDO, 0.3))
        for uno in self.sistemas():
            if uno.mision is not None and uno.mision.oculta and uno.mision.rama_de is not None:
                self._linea_punteada(pantalla, self.sistema("M%d" % uno.mision.rama_de).lugar, uno.lugar, VIOLETA)
            if uno.puerta and galaxia.unidos_por_puerta(uno, galaxia.sistema(uno.puerta), progreso) \
                    and uno.id < uno.puerta:
                self._linea_punteada(pantalla, uno.lugar, galaxia.sistema(uno.puerta).lugar,
                                     interfaz.mezclar(VIOLETA, FONDO, 0.4), separacion=24)

    def _dibujar_sistema(self, pantalla, uno):
        x, y = self.en_pantalla(uno.lugar)
        progreso = self.progreso
        tragado = tiempo.tragado(uno, progreso.anios)
        color = TEXTO_APAGADO if tragado else uno.bioma["color"]
        radio = RADIO_MISION
        # El Abismo late con el compas (sin destellos reducidos)
        if uno.id == LATE and not accesibilidad.destellos_reducidos():
            if sonando(escribir("ALBA"), COMPAS_UNIDAD * 2, pygame.time.get_ticks()):
                _anillo(pantalla, x, y, radio + 6, interfaz.mezclar(VIOLETA, FONDO, 0.3))
        if uno.tipo == "umbral":
            dibujo.pixel_art(pantalla, ESTACION, x, y, TEXTO_APAGADO if tragado else AMARILLO, 4)
            radio = 16
        elif uno.mision is not None:
            clase = uno.mision
            if clase.oculta:
                color, radio = VIOLETA, 10
            elif not clase.disponible(progreso):
                color = TEXTO_APAGADO
            _circulo(pantalla, x, y, radio, interfaz.mezclar(color, FONDO, 0.55))
            _circulo(pantalla, x - 2, y - 2, radio - 6, color)
            texto(pantalla, "?" if clase.oculta else str(clase.numero), CHICA, TEXTO if not tragado else TEXTO_APAGADO,
                  x, y + radio + 14, contorno=CONTORNO)
            if clase.numero in progreso.misiones:
                dibujo.pixel_art(pantalla, TILDE, x + radio, y - radio, VERDE, 2)
        else:
            radio = 8
            brillo = color if uno.id in progreso.sistemas else interfaz.mezclar(color, FONDO, 0.35)
            dibujo.pixel_art(pantalla, ESTRELLA, x, y, brillo, 4)
            if uno.id in progreso.sistemas:
                dibujo.pixel_art(pantalla, TILDE, x + 12, y - 12, VERDE, 2)
        if uno.id == self.elegida and dibujo.parpadeo(300):
            _anillo(pantalla, x, y, radio + 10, BLANCO if self.por_que_no(uno) is None else TEXTO_APAGADO)

    def _dibujar_ruta_del_viaje(self, pantalla):
        # Del lugar de la Alondra al elegido: el camino que haria
        elegido = self.sistema(self.elegida)
        desde = self.ubicacion()
        if self.viaje is None and elegido is not desde and self.por_que_no(elegido) is None:
            self._linea_punteada(pantalla, desde.lugar, elegido.lugar, interfaz.mezclar(BLANCO, FONDO, 0.5),
                                 separacion=10, margen=24)

    def _dibujar_marea(self, pantalla):
        # El frente de la Marea: un muro rojo que avanza desde la izquierda, con su borde que ondula
        frente = tiempo.frente_de_la_marea(self.anios_que_se_ven())
        borde_x, _ = self.en_pantalla((frente, 0))
        if borde_x <= 0:
            return
        ahora = pygame.time.get_ticks()
        for y in range(VISTA.top, VISTA.bottom, 2):
            onda = dibujo.en_grilla(math.sin(y / 23 + ahora / 600) * 8)
            ancho = max(0, borde_x + onda)
            if (y // 2) % 2 == 0:
                pantalla.fill((40, 6, 22), (0, y, ancho, 2))
            pantalla.fill(ROJO, (ancho - 4, y, 4, 2))

    def _dibujar_nave(self, pantalla):
        # La Alondra flota arriba de donde esta (o vuela, durante el viaje)
        x, y = self.en_pantalla(self._lugar_de_la_nave())
        flota = round(math.sin(pygame.time.get_ticks() / 300) * 2) * 2
        dibujo.pegar(pantalla, nave.imagen("icono"), x, y - 34 + flota, centrado=True)

    def _dibujar_informe(self, pantalla):
        uno = self.sistema(self.elegida)
        progreso = self.progreso
        motivo = self.por_que_no(uno)
        color = uno.bioma["color"] if motivo is None or uno.tipo == "umbral" else TEXTO_APAGADO
        if uno.mision is not None:
            rotulo = "MISION %d" % uno.mision.numero
            nombre = uno.nombre if uno.mision.disponible(progreso) else "? ? ?"
        else:
            rotulo, nombre = ("CASA" if uno.tipo == "umbral" else "SISTEMA LIBRE"), uno.nombre
        adentro = interfaz.panel(pantalla, INFORME, color, rotulo)
        texto(pantalla, nombre, MEDIA, color, adentro.left, adentro.top + 8, alinear="izquierda")
        texto(pantalla, uno.bioma["nombre"], CHICA, TEXTO_SUAVE, adentro.left, adentro.top + 42, alinear="izquierda")
        # El peligro: cinco cuadraditos
        texto(pantalla, "PELIGRO", CHICA, TEXTO_SUAVE, adentro.left, adentro.top + 72, alinear="izquierda")
        for i in range(5):
            caja = pygame.Rect(adentro.left + 128 + i * 20, adentro.top + 66, 14, 14)
            if i < galaxia.peligro(uno):
                pantalla.fill(ROJO if i >= 3 else AMARILLO, caja)
            else:
                pygame.draw.rect(pantalla, LINEA_APAGADA, caja, 2)
        # A la derecha: el viaje (o por que no se puede) y lo que hay
        derecha = adentro.right
        if motivo is not None:
            texto(pantalla, motivo, CHICA, TEXTO_APAGADO, derecha, adentro.top + 8, alinear="derecha")
        else:
            costo = self.costo(uno)
            aca = uno is self.ubicacion()
            viaje = "ESTAS ACA: +%.2f AÑOS" % costo if aca else "VIAJE: +%.1f AÑOS" % costo
            texto(pantalla, viaje, CHICA, TEXTO, derecha, adentro.top + 8, alinear="derecha")
            llegada = progreso.anios + costo
            texto(pantalla, "LLEGAS EN EL AÑO %.1f" % llegada, CHICA, ROJO if llegada >= MAREA_ANIOS else TEXTO_SUAVE,
                  derecha, adentro.top + 32, alinear="derecha")
        notas = []
        if uno.gravedad:
            notas.append(("DILATACION +%.1f" % uno.gravedad, VIOLETA))
        if galaxia.unidos_por_puerta(self.ubicacion(), uno, progreso):
            notas.append(("PUERTA MENOR", VIOLETA))
        if uno.mision is not None and uno.mision.numero in progreso.misiones:
            notas.append(("CUMPLIDA", VERDE))
        elif uno.id in progreso.sistemas:
            notas.append(("DESPEJADO", VERDE))
        if uno.eco and uno.eco in progreso.fragmentos:
            notas.append(("ECO", VIOLETA))
        x = derecha
        for nota, color_nota in reversed(notas):
            texto(pantalla, nota, CHICA, color_nota, x, adentro.top + 72, alinear="derecha")
            x -= recursos.fuente(CHICA).size(nota)[0] + 24


def _circulo(pantalla, centro_x, centro_y, radio, color):
    # Un circulo lleno en la grilla de 2 px (de a renglones)
    for dy in range(-radio, radio + 1, 2):
        mitad = dibujo.en_grilla(math.sqrt(max(0, radio * radio - dy * dy)))
        pantalla.fill(color, (dibujo.en_grilla(centro_x) - mitad, dibujo.en_grilla(centro_y + dy), 2 * mitad, 2))


def _anillo(pantalla, centro_x, centro_y, radio, color):
    # Un anillo de cuadraditos (el sistema elegido)
    for i in range(24):
        angulo = 2 * math.pi * i / 24
        x = dibujo.en_grilla(centro_x + math.cos(angulo) * radio)
        y = dibujo.en_grilla(centro_y + math.sin(angulo) * radio)
        pantalla.fill(color, (x - 2, y - 2, 4, 4))
