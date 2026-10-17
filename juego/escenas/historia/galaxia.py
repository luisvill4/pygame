"""
GALAXIA: el centro del modo historia. Un mapa mas grande que la pantalla: la camara sigue al
sistema elegido.

    - Las MISIONES de la historia (en orden: se puede jugar la primera, las cumplidas y la que
      sigue a una cumplida), los SISTEMAS LIBRES (cuanto mas lejos de la Umbral, mas peligro y
      mas piezas) y la ESTACION UMBRAL, la casa (historia/galaxia.py).
    - VIAJAR CUESTA AÑOS (historia/tiempo.py): la Alondra vuela hasta el sistema mientras corre
      el reloj, y al llegar, si paso un año, Ines manda su mensaje. El frente de la Marea avanza
      desde la izquierda: a los 6 años se traga la Umbral. Un VIAJE LARGO (VIAJE_LARGO_ANIOS) o
      uno que cruza un año en que la historia cambia (tiempo.HITOS) pregunta antes de salir.
    - TODO SISTEMA LIBRE ESTA BLOQUEADO al principio: tiene un PELIGRO AMBIENTAL (calor,
      esporas, panal, gravedad) y para entrar hace falta su modulo (historia/modulos.py). Al lado
      de cada uno va el icono de su modulo (brillante si falta) y un CANDADO si no se puede ir.
    - El panel de abajo dice todo del sistema elegido: peligro, cuanto cuesta el viaje, en que
      año llegas, sus corrientes y que encontraste ahi.

COMO SE ELIGE (pedido del usuario: "no se pueden seleccionar bien"; antes las flechas buscaban
el mas cercano en un cono y saltaban a lugares inesperados). Reglas fijas, siempre iguales:
    DIRECCIONES             el mas cercano hacia ese lado, prefiriendo el que esta mas derecho:
                            lo que se corre de costado cuenta doble (DESVIO). Un test comprueba
                            que desde cualquier sistema se llega a todos
    LB / RB (Q / E)         el anterior o siguiente (de izquierda a derecha) al que SE PUEDE VIAJAR
En el mapa, una flechita arriba de cada vecino dice a donde lleva cada direccion; el cursor no
titila y lleva el nombre del sistema; el bioma elegido se nombra grande abajo.
ACEPTAR viaja; OPCIONES abre el Archivo; PAUSA, el Hangar; VOLVER, el inicio. Lo que pasa al
terminar: pasajes.py.
"""
import math

import pygame

from juego import dibujo, interfaz, nave, accesibilidad, recursos
from juego.dibujo import texto, CHICA, MEDIA, MINI
from juego.config import (ANCHO, FONDO, SECTORES, ROJO, TEXTO, TEXTO_SUAVE, TEXTO_APAGADO, LINEA_APAGADA, VERDE,
                          CIAN, AMARILLO, VIOLETA, COMPAS_UNIDAD, MAREA_ANIOS, BLANCO, CONTORNO, VIAJE_LARGO_ANIOS,
                          CENTRO_X)
from juego.entrada import (ACEPTAR, VOLVER, IZQUIERDA, DERECHA, ARRIBA, ABAJO, OPCIONES, PAUSA, PESTANA_ANTERIOR,
                           PESTANA_SIGUIENTE)
from juego.escenas.base import Escena
from juego.escenas.historia.dialogo import Dialogo
from juego.escenas.historia.archivo import Archivo
from juego.escenas.historia.hangar import Hangar
from juego.historia.mision import filtrar
from juego.historia.modo import ModoHistoria
from juego.historia.exploracion import ModoExploracion
from juego.historia import galaxia, tiempo, modulos
from juego.historia.glifos import sonando, escribir
from juego.sonido import SILENCIO

VISTA = pygame.Rect(0, 72, ANCHO, 316)      # la ventana al mapa (lo de afuera no se dibuja)
INFORME = pygame.Rect(48, 400, ANCHO - 96, 144)
AVISO = pygame.Rect(0, 0, 680, 268)          # la pregunta antes de un viaje largo (el alto, segun el texto)
VIAJE_PASOS = 75            # lo que dura el vuelo en la pantalla (pasos)
RADIO_MISION = 14
LATE = "M5"                 # el sistema que late con el compas (de ahi sale)
VERDAD = "F11"
TILDE = [".......", "......X", ".....XX", "X...XX.", "XX.XX..", ".XXX...", "..X...."]
ESTRELLA = ["..X..", ".XXX.", "XXXXX", ".XXX.", "..X.."]
ESTACION = ["...X...", "..XXX..", "X.XXX.X", "XXXXXXX", "X.XXX.X", "..XXX..", "...X..."]
CANDADO = [".XXX.", "X...X", "XXXXX", "XX.XX", "XXXXX"]     # no se puede ir (una forma, no solo un color)
DESVIO = 2                  # al elegir hacia un lado, lo que se corre de costado pesa esto
FLECHAS = {(1, 0): ["X...", "XX..", "XXX.", "XXXX", "XXX.", "XX..", "X..."],
           (-1, 0): ["...X", "..XX", ".XXX", "XXXX", ".XXX", "..XX", "...X"],
           (0, -1): ["...X...", "..XXX..", ".XXXXX.", "XXXXXXX"],
           (0, 1): ["XXXXXXX", ".XXXXX.", "..XXX..", "...X..."]}


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
        self.aviso = None           # la pregunta de un viaje largo: {"hasta", "lineas", "viajar"}
        nave.cambiar_equipo(modulos.equipo(self.progreso))     # la Alondra con lo que se le compro

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
        falta = modulos.falta(self.progreso, uno.ambiente)
        if falta is not None:
            modulo, nivel = falta
            return "NECESITA %s %d." % (modulo.nombre, nivel)      # (se fabrica en el hangar)
        return None

    def costo(self, uno):
        return galaxia.costo_viaje(self.ubicacion(), uno, self.progreso)

    def anios_que_se_ven(self):
        # Durante el vuelo, el reloj corre
        if self.viaje is None:
            return self.progreso.anios
        avance = min(1, self.viaje["paso"] / VIAJE_PASOS)
        return self.viaje["anios"] + self.viaje["costo"] * avance

    def aviso_del_viaje(self, uno):
        # Lo que hay que saber antes de un viaje largo (o que cambia la historia). None = sin aviso
        costo = self.costo(uno)
        hitos = tiempo.hitos_que_cruza(self.progreso, costo)
        if tiempo.historia_terminada(self.progreso) or (costo < VIAJE_LARGO_ANIOS and not hitos):
            return None
        llegada = self.progreso.anios + costo
        return (["VAN A PASAR %.1f AÑOS EN LA UMBRAL." % costo,
                 "LLEGAS EN EL AÑO %.1f. LA MAREA, EN EL %d." % (llegada, MAREA_ANIOS)] + hitos)

    # ---------- La navegacion ----------

    def columna(self, uno):
        # En que bioma (columna del mapa) esta: el ultimo cuyo borde izquierdo ya paso
        return max(i for i, desde in enumerate(galaxia.ZONAS) if uno.lugar[0] >= desde)

    def de_izquierda_a_derecha(self):
        return sorted(self.sistemas(), key=lambda uno: (uno.lugar[0], uno.lugar[1]))

    def vecino(self, dx, dy, desde=None):
        # El sistema hacia ese lado (None = no hay): entre los que estan de ese lado, el mas
        # cercano contando lo que se corre de costado DESVIO veces (asi gana el mas derecho)
        actual = desde or self.sistema(self.elegida)
        mejor, puntaje_mejor = None, math.inf
        for otro in self.sistemas():
            adelante = (otro.lugar[0] - actual.lugar[0]) * dx + (otro.lugar[1] - actual.lugar[1]) * dy
            costado = abs((otro.lugar[0] - actual.lugar[0]) * dy) + abs((otro.lugar[1] - actual.lugar[1]) * dx)
            if adelante <= 0:
                continue
            puntaje = adelante + DESVIO * costado
            if puntaje < puntaje_mejor:
                mejor, puntaje_mejor = otro, puntaje
        return mejor

    def disponible_siguiente(self, paso):
        # El anterior o siguiente (de izquierda a derecha) al que se puede viajar
        actual = self.sistema(self.elegida)
        orden = self.de_izquierda_a_derecha()
        se_puede = [uno for uno in orden if self.por_que_no(uno) is None and uno is not actual]
        if not se_puede:
            return None
        lugar = orden.index(actual)
        siguientes = [uno for uno in se_puede if (orden.index(uno) - lugar) * paso > 0]
        if not siguientes:
            return se_puede[0] if paso > 0 else se_puede[-1]       # (da la vuelta)
        return siguientes[0] if paso > 0 else siguientes[-1]

    # ---------- Cada paso ----------

    def actualizar(self, entrada):
        self.mover_fondo()
        nave.preparar_giros(2)          # (los giros de la nave equipada, para el despegue: ver nave.girada)
        if self.viaje is not None:
            self._volar()
            return
        if self.aviso is not None:
            self._actualizar_aviso(entrada)
            return
        movidas = {IZQUIERDA: lambda: self.vecino(-1, 0), DERECHA: lambda: self.vecino(1, 0),
                   ARRIBA: lambda: self.vecino(0, -1), ABAJO: lambda: self.vecino(0, 1),
                   PESTANA_ANTERIOR: lambda: self.disponible_siguiente(-1),
                   PESTANA_SIGUIENTE: lambda: self.disponible_siguiente(1)}
        accion = next((accion for accion in movidas if entrada.pulso(accion)), None)
        if accion is not None:
            otro = movidas[accion]()
            if otro is not None:
                self.elegida = otro.id
                self.app.sonidos.reproducir("ui_mover")
        elif entrada.pulso(ACEPTAR):
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

    def _actualizar_aviso(self, entrada):
        # La pregunta del viaje largo: dos botones (por defecto QUEDARME), como la de la Pausa
        for accion in (IZQUIERDA, DERECHA, ARRIBA, ABAJO):
            if entrada.pulso(accion):
                self.aviso["viajar"] = not self.aviso["viajar"]
                self.app.sonidos.reproducir("ui_mover")
                return
        if entrada.pulso(ACEPTAR) and self.aviso["viajar"]:
            hasta = self.aviso["hasta"]
            self.aviso = None
            self._partir(hasta)
        elif entrada.pulso(ACEPTAR) or entrada.pulso(VOLVER):
            self.aviso = None
            self.app.sonidos.reproducir("ui_volver")

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
        lineas = self.aviso_del_viaje(uno)
        if lineas:
            self.app.sonidos.reproducir("ui_aceptar")
            self.aviso = {"hasta": uno, "lineas": lineas, "viajar": False}
            return
        self._partir(uno)

    def _partir(self, uno):
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
        # Si paso un año, primero el mensaje de Ines desde la Umbral
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
        if self.viaje is None and self.aviso is None:
            self._dibujar_vecinos(pantalla)
            self._dibujar_cursor(pantalla)
        pantalla.set_clip(None)
        pygame.draw.rect(pantalla, LINEA_APAGADA, VISTA.inflate(0, 4), 2)
        self._dibujar_cabecera(pantalla)
        self._dibujar_informe(pantalla)
        interfaz.ayudas(pantalla, self.app.entrada, [("mover", "ELEGIR"), ("pestanas", "DISPONIBLES"),
                                                     ("volver", "VOLVER"), ("aceptar", "VIAJAR")])
        if self.aviso is not None:
            self._dibujar_aviso(pantalla)

    def _dibujar_cabecera(self, pantalla):
        texto(pantalla, "GALAXIA", MEDIA, CIAN, 48, 40, alinear="izquierda")
        # Los atajos al Archivo y al Hangar, arriba (en la barra de abajo no entran)
        x = 236
        for accion, etiqueta in (("opciones", "ARCHIVO"), ("pausa", "HANGAR")):
            for glifo in interfaz.GLIFOS[accion][1 if self.app.entrada.usando_mando() else 0]:
                x += interfaz.boton(pantalla, glifo, x, 40) + 6
            texto(pantalla, etiqueta, CHICA, TEXTO, x + 4, 41, alinear="izquierda")
            x += recursos.fuente(CHICA).size(etiqueta)[0] + 36
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
        texto(pantalla, "AÑO %.1f   PIEZAS %d" % (anios, progreso.piezas), CHICA, TEXTO_SUAVE,
              ANCHO - 48, 54, alinear="derecha")

    def _rango_de_columna(self, numero):
        # De donde a donde va la columna en la pantalla (x)
        desde = galaxia.ZONAS[numero]
        hasta = galaxia.ZONAS[numero + 1] if numero + 1 < len(galaxia.ZONAS) else galaxia.ANCHO_GALAXIA
        return self.en_pantalla((desde, 0))[0], self.en_pantalla((hasta, 0))[0]

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
        # El nombre de cada bioma, abajo de su columna (el de la elegida, grande y en su color)
        elegida = self.columna(self.sistema(self.elegida))
        for numero in range(len(galaxia.ZONAS)):
            sector = SECTORES[numero]
            izquierda, _ = self._rango_de_columna(numero)
            if numero == elegida:
                texto(pantalla, sector["nombre"], CHICA, sector["color"], izquierda + 16, VISTA.bottom - 16,
                      alinear="izquierda", contorno=CONTORNO)
            else:
                texto(pantalla, sector["nombre"], MINI, interfaz.mezclar(sector["color"], FONDO, 0.45), izquierda + 16,
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

    def _radio(self, uno):
        if uno.tipo == "umbral":
            return 16
        if uno.mision is not None:
            return 10 if uno.mision.oculta else RADIO_MISION
        return 8

    def _dibujar_sistema(self, pantalla, uno):
        x, y = self.en_pantalla(uno.lugar)
        progreso = self.progreso
        tragado = tiempo.tragado(uno, progreso.anios)
        bloqueado = uno.tipo != "umbral" and self.por_que_no(uno) is not None
        color = TEXTO_APAGADO if tragado else uno.bioma["color"]
        radio = self._radio(uno)
        # El Abismo late con el compas (sin destellos reducidos)
        if uno.id == LATE and not accesibilidad.destellos_reducidos():
            if sonando(escribir("ALBA"), COMPAS_UNIDAD * 2, pygame.time.get_ticks()):
                _anillo(pantalla, x, y, radio + 6, interfaz.mezclar(VIOLETA, FONDO, 0.3))
        if uno.tipo == "umbral":
            dibujo.pixel_art(pantalla, ESTACION, x, y, TEXTO_APAGADO if tragado else AMARILLO, 4)
        elif uno.mision is not None:
            clase = uno.mision
            if clase.oculta:
                color = VIOLETA
            elif not clase.disponible(progreso):
                color = TEXTO_APAGADO
            _circulo(pantalla, x, y, radio, interfaz.mezclar(color, FONDO, 0.55))
            _circulo(pantalla, x - 2, y - 2, radio - 6, color)
            texto(pantalla, "?" if clase.oculta else str(clase.numero), CHICA, TEXTO if not tragado else TEXTO_APAGADO,
                  x, y + radio + 14, contorno=CONTORNO)
            if clase.numero in progreso.misiones:
                dibujo.pixel_art(pantalla, TILDE, x + radio + 1, y - radio + 1, VERDE, 2)
        else:
            if uno.id in progreso.sistemas:
                brillo = color
            else:
                brillo = interfaz.mezclar(color, FONDO, 0.45 if bloqueado else 0.25)
            dibujo.pixel_art(pantalla, ESTRELLA, x, y, brillo, 4)
            if uno.id in progreso.sistemas:
                dibujo.pixel_art(pantalla, TILDE, x + 13, y - 11, VERDE, 2)
        self._dibujar_ambiente(pantalla, uno, x - radio - 14, y)
        if bloqueado and not tragado:
            dibujo.pixel_art(pantalla, CANDADO, x + radio + 7, y - radio + 1, TEXTO_SUAVE, 2)

    def _dibujar_ambiente(self, pantalla, uno, x, y):
        # El icono del modulo que pide (brillante: falta; apagado: ya lo tenes) y un puntito por nivel
        if uno.ambiente is None:
            return
        tipo, intensidad = uno.ambiente
        modulo = modulos.POR_PELIGRO[tipo]
        falta = modulos.falta(self.progreso, uno.ambiente) is not None
        color = modulo.color if falta else interfaz.mezclar(modulo.color, FONDO, 0.55)
        dibujo.pixel_art(pantalla, modulo.icono, x + 1, y + 1, color, 2)     # (+1: 7 columnas calzan en la grilla)
        for i in range(intensidad):
            pantalla.fill(color, (x - 4 * intensidad + 2 + i * 8, y + 10, 4, 4))

    def _dibujar_vecinos(self, pantalla):
        # Una flechita arriba de cada vecino: a donde lleva cada direccion (no hay que adivinar)
        for (dx, dy), dibujo_flecha in FLECHAS.items():
            otro = self.vecino(dx, dy)
            if otro is None:
                continue
            x, y = self.en_pantalla(otro.lugar)
            ancho, alto = len(dibujo_flecha[0]) * 2, len(dibujo_flecha) * 2
            izquierda, arriba = x - ancho // 2 // 2 * 2, y - self._radio(otro) - 10 - alto
            for fila, linea in enumerate(dibujo_flecha):        # (con su sombra: se lee sobre cualquier fondo)
                for columna, celda in enumerate(linea):
                    if celda == "X":
                        pantalla.fill(CONTORNO, (izquierda + columna * 2 + 2, arriba + fila * 2 + 2, 2, 2))
            dibujo.pixel_art(pantalla, dibujo_flecha, izquierda + ancho // 2, arriba + alto // 2, AMARILLO, 2)

    def _dibujar_cursor(self, pantalla):
        # El elegido: cuatro escuadras quietas (no titilan) y su nombre arriba, con contorno
        uno = self.sistema(self.elegida)
        x, y = self.en_pantalla(uno.lugar)
        radio = self._radio(uno) + 12
        color = BLANCO if self.por_que_no(uno) is None else TEXTO_SUAVE
        caja = pygame.Rect(x - radio, y - radio, 2 * radio, 2 * radio)
        interfaz.esquinas(pantalla, caja, color, largo=8, grueso=2)
        nombre = uno.nombre if uno.mision is None or uno.mision.disponible(self.progreso) else "? ? ?"
        ancho = recursos.fuente(CHICA).size(nombre)[0]
        centro = min(max(x, VISTA.left + 8 + ancho // 2), VISTA.right - 8 - ancho // 2)
        arriba = y - radio - 14 if y - radio - 14 > VISTA.top + 12 else y + radio + 30
        texto(pantalla, nombre, CHICA, color, dibujo.en_grilla(centro), arriba, contorno=CONTORNO)

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
        if uno.ambiente is not None:            # al lado del bioma: su peligro ambiental
            tipo, intensidad = uno.ambiente
            modulo = modulos.POR_PELIGRO[tipo]
            x = adentro.left + recursos.fuente(CHICA).size(uno.bioma["nombre"])[0] + 32
            dibujo.pixel_art(pantalla, modulo.icono, x + 7, adentro.top + 43, modulo.color, 2)
            texto(pantalla, "%s %d" % (tipo.upper(), intensidad), CHICA, modulo.color, x + 22, adentro.top + 42,
                  alinear="izquierda")
        # El peligro: cinco cuadraditos (y el numero, para no depender del color)
        texto(pantalla, "PELIGRO %d" % galaxia.peligro(uno), CHICA, TEXTO_SUAVE, adentro.left, adentro.top + 72,
              alinear="izquierda")
        for i in range(5):
            caja = pygame.Rect(adentro.left + 160 + i * 20, adentro.top + 66, 14, 14)
            if i < galaxia.peligro(uno):
                pantalla.fill(ROJO if i >= 3 else AMARILLO, caja)
            else:
                pygame.draw.rect(pantalla, LINEA_APAGADA, caja, 2)
        # A la derecha: el viaje (o por que no se puede) y lo que hay
        derecha = adentro.right
        if motivo is not None:
            if uno.tipo != "umbral":
                dibujo.pixel_art(pantalla, CANDADO, derecha - recursos.fuente(CHICA).size(motivo)[0] - 17,
                                 adentro.top + 9, TEXTO_SUAVE, 2)
            texto(pantalla, motivo, CHICA, TEXTO_SUAVE, derecha, adentro.top + 8, alinear="derecha")
        else:
            costo = self.costo(uno)
            aca = uno is self.ubicacion()
            viaje = "ESTAS ACA: +%.2f AÑOS" % costo if aca else "VIAJE: +%.1f AÑOS" % costo
            largo = costo >= VIAJE_LARGO_ANIOS and not tiempo.historia_terminada(progreso)
            texto(pantalla, viaje + ("  (LARGO)" if largo else ""), CHICA, AMARILLO if largo else TEXTO, derecha,
                  adentro.top + 8, alinear="derecha")
            llegada = progreso.anios + costo
            texto(pantalla, "LLEGAS EN EL AÑO %.1f" % llegada, CHICA, ROJO if llegada >= MAREA_ANIOS else TEXTO_SUAVE,
                  derecha, adentro.top + 32, alinear="derecha")
        notas = []
        if uno.corrientes:
            notas.append(("CORRIENTES +%.1f" % uno.corrientes, VIOLETA))
        if galaxia.unidos_por_puerta(self.ubicacion(), uno, progreso):
            notas.append(("PUERTA MENOR", VIOLETA))
        if uno.mision is not None and uno.mision.numero in progreso.misiones:
            notas.append(("CUMPLIDA", VERDE))
        elif uno.id in progreso.sistemas:
            notas.append(("DESPEJADO", VERDE))
        if uno.eco and uno.eco in progreso.fragmentos:
            notas.append(("ECO", VIOLETA))
        if uno.plano and uno.plano not in progreso.planos:
            notas.append(("PLANO", CIAN))       # (se consigue al despejarlo o cumplirla)
        x = derecha
        for nota, color_nota in reversed(notas):
            texto(pantalla, nota, CHICA, color_nota, x, adentro.top + 72, alinear="derecha")
            x -= recursos.fuente(CHICA).size(nota)[0] + 24

    def _dibujar_aviso(self, pantalla):
        # La pregunta antes de un viaje largo: cuanto tiempo pasa y que cambia. Por defecto, QUEDARME
        dibujo.oscurecer(pantalla, FONDO, 150)
        caja = AVISO.copy()
        caja.height = 46 + 10 + 24 * len(self.aviso["lineas"]) + 16 + 44 + 30      # franja, texto, aire y botones
        caja.center = (CENTRO_X, 280)
        hasta = self.aviso["hasta"]
        cambia = len(self.aviso["lineas"]) > 2
        color = ROJO if cambia else AMARILLO
        adentro = interfaz.panel(pantalla, caja, color, "¿VIAJAR A %s?" % hasta.nombre)
        y = adentro.top + 10
        for i, linea in enumerate(self.aviso["lineas"]):
            for renglon in dibujo.partir_lineas(linea, CHICA, adentro.width):
                texto(pantalla, renglon, CHICA, BLANCO if i < 2 else color, caja.centerx, y)
                y += 24
        for i, (nombre, es_viajar) in enumerate((("QUEDARME", False), ("VIAJAR", True))):
            boton = pygame.Rect(0, 0, 220, 44)
            boton.center = (caja.centerx - 124 + i * 248, adentro.bottom - 24)
            if self.aviso["viajar"] == es_viajar:
                pantalla.fill(color if es_viajar else CIAN, boton)
                texto(pantalla, nombre, MEDIA, FONDO, boton.centerx + 2, boton.centery + 1, sombra=None)
            else:
                pygame.draw.rect(pantalla, LINEA_APAGADA, boton, 2)
                texto(pantalla, nombre, MEDIA, TEXTO_SUAVE, boton.centerx + 2, boton.centery + 1)


def _circulo(pantalla, centro_x, centro_y, radio, color):
    # Un circulo lleno en la grilla de 2 px (de a renglones)
    for dy in range(-radio, radio + 1, 2):
        mitad = dibujo.en_grilla(math.sqrt(max(0, radio * radio - dy * dy)))
        pantalla.fill(color, (dibujo.en_grilla(centro_x) - mitad, dibujo.en_grilla(centro_y + dy), 2 * mitad, 2))


def _anillo(pantalla, centro_x, centro_y, radio, color):
    # Un anillo de cuadraditos (el latido del Abismo)
    for i in range(24):
        angulo = 2 * math.pi * i / 24
        x = dibujo.en_grilla(centro_x + math.cos(angulo) * radio)
        y = dibujo.en_grilla(centro_y + math.sin(angulo) * radio)
        pantalla.fill(color, (x - 2, y - 2, 4, 4))
