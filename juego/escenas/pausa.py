"""
Pausa: la ultima imagen del juego pixelada y oscurecida, y un menu (ARRIBA/ABAJO + ENTER):

    CONTINUAR        vuelve al juego (tambien con P, ESC o el boton Menu del mando)
    OPCIONES         el menu de opciones (tambien con O o el boton Vista)
    VOLVER AL MENU   pide confirmacion: se pierde la partida y su puntaje

A la derecha, la ficha de la partida: el sector, los numeros, el desafio y las mejoras.
"""
import pygame

from juego import dibujo, interfaz
from juego.dibujo import texto, MINI, CHICA, MEDIA
from juego.config import (ANCHO, CENTRO_X, FONDO, CIAN, BLANCO, ROJO, SECTORES, TEXTO_SUAVE, TEXTO_APAGADO,
                          LINEA_APAGADA)
from juego.entrada import PAUSA, VOLVER, OPCIONES, ACEPTAR, ARRIBA, ABAJO, IZQUIERDA, DERECHA
from juego.escenas.base import Escena
from juego.escenas.opciones import Opciones
from juego.escenas.inicio import Inicio
from juego.escenas.fin import reloj
from juego.mejoras import TIPOS_MEJORA

FILAS_PAUSA = ["CONTINUAR", "OPCIONES", "VOLVER AL MENU"]
CIAN_OSCURO = (0, 70, 110)


class Pausa(Escena):
    def __init__(self, app, escena_juego, captura):
        super().__init__(app)
        self.escena_juego = escena_juego    # a donde se vuelve al seguir
        self.captura = captura              # imagen del juego al pausar
        self.fondo = interfaz.pixelado(captura)     # la misma, pixelada y oscurecida (se arma una vez)
        self.cursor = interfaz.Cursor(0)    # la franja del menu (se desliza)
        self.fila = 0                       # opcion elegida del menu
        self.confirmando = False            # se esta preguntando "¿VOLVER AL MENU?"
        self.confirmar_si = False           # en la pregunta, elegido SI (por defecto NO)

    # ---------- Logica ----------

    def actualizar(self, entrada):
        if self.confirmando:
            self._actualizar_confirmacion(entrada)
            return
        # Atajos de siempre
        if entrada.pulso(PAUSA) or entrada.pulso(VOLVER):
            self._seguir()
            return
        if entrada.pulso(OPCIONES):
            self._abrir_opciones()
            return
        self.cursor.avanzar()
        for accion in entrada.acciones:
            if accion == ARRIBA:
                self.fila = (self.fila - 1) % len(FILAS_PAUSA)
                self.cursor.ir_a(self.fila)
                self.app.sonidos.reproducir("ui_mover")
            elif accion == ABAJO:
                self.fila = (self.fila + 1) % len(FILAS_PAUSA)
                self.cursor.ir_a(self.fila)
                self.app.sonidos.reproducir("ui_mover")
            elif accion == ACEPTAR:
                self._elegir(FILAS_PAUSA[self.fila])
                return

    def _elegir(self, fila):
        if fila == "CONTINUAR":
            self._seguir()
        elif fila == "OPCIONES":
            self._abrir_opciones()
        else:
            # Antes de salir se pregunta: se pierde la partida
            self.app.sonidos.reproducir("ui_alerta")
            self.confirmando = True
            self.confirmar_si = False

    def _actualizar_confirmacion(self, entrada):
        for accion in entrada.acciones:
            if accion in (IZQUIERDA, DERECHA):
                self.confirmar_si = not self.confirmar_si
                self.app.sonidos.reproducir("ui_mover")
            elif accion == ACEPTAR:
                if self.confirmar_si:
                    self._volver_al_menu()
                else:
                    self.confirmando = False
                    self.app.sonidos.reproducir("ui_volver")
                return
            elif accion == VOLVER:          # ESC o B: es lo mismo que NO
                self.confirmando = False
                self.app.sonidos.reproducir("ui_volver")
                return

    def _seguir(self):
        self.app.sonidos.reproducir("seguir")
        self.app.sonidos.reanudar_todo()
        self.app.cambiar_escena(self.escena_juego, transicion=False)

    def _abrir_opciones(self):
        self.app.sonidos.reproducir("ui_aceptar")
        self.app.cambiar_escena(Opciones(self.app, volver_a=self))

    def _volver_al_menu(self):
        # Se abandona la partida (sin guardar el puntaje) y se vuelve a la pantalla de inicio
        self.app.sonidos.reanudar_todo()
        self.app.sonidos.parar_musica()
        self.app.sonidos.parar_loops()
        self.app.sonidos.cancelar_pendientes()
        self.app.efectos.reiniciar()
        self.app.fondo.ir_a_sector(SECTORES[0], instantaneo=True)
        self.app.sonidos.reproducir("ui_volver")
        self.app.cambiar_escena(Inicio(self.app))

    # ---------- Dibujo ----------

    @staticmethod
    def _tramo(director):
        # "3/4" o "JEFE" (el tramo de la ruta del sector)
        return "%d/4" % director.numero_tramo if director.numero_tramo else "JEFE"

    def dibujar(self, pantalla):
        pantalla.blit(self.fondo, (0, 0))
        interfaz.titulo(pantalla, "PAUSA", 64, 92, CIAN, CIAN_OSCURO)
        interfaz.menu(pantalla, FILAS_PAUSA, self.cursor, 112, 224, 360, 58)
        self._dibujar_partida(pantalla)
        if self.confirmando:
            self._dibujar_confirmacion(pantalla)
            interfaz.ayudas(pantalla, self.app.entrada, [("cambiar", "ELEGIR"), ("aceptar", "ACEPTAR"),
                                                         ("volver", "CANCELAR")])
        else:
            interfaz.ayudas(pantalla, self.app.entrada, [("elegir", "ELEGIR"), ("aceptar", "ACEPTAR"),
                                                         ("pausa", "SEGUIR"), ("opciones", "OPCIONES")])

    def _dibujar_partida(self, pantalla):
        # La ficha de la partida: el sector, los numeros, el desafio y las mejoras
        partida = self.escena_juego.partida
        director = partida.director
        sector = director.sector
        panel = pygame.Rect(520, 104, ANCHO - 568, 432)
        adentro = interfaz.panel(pantalla, panel, sector["color"], "SECTOR " + str(director.numero_sector))
        texto(pantalla, sector["nombre"], MEDIA, sector["color"], adentro.left, adentro.top + 12, alinear="izquierda")
        texto(pantalla, sector["lema"], CHICA, TEXTO_SUAVE, adentro.left, adentro.top + 40, alinear="izquierda")

        # Los numeros, en una grilla de 3 x 2
        datos = [("PUNTOS", dibujo.numero_arcade(partida.puntaje)), ("TRAMO", self._tramo(director)),
                 ("TIEMPO", reloj(partida.tiempo)), ("CREDITOS", str(partida.creditos)),
                 ("PERFECTOS", str(partida.estadisticas.perfectos)), ("MEJOR COMBO", str(partida.mejor_combo))]
        ancho_columna = adentro.width // 3
        for i, (nombre, valor) in enumerate(datos):
            x = adentro.left + (i % 3) * ancho_columna
            y = adentro.top + 78 + (i // 3) * 50
            texto(pantalla, nombre, MINI, TEXTO_SUAVE, x, y, alinear="izquierda")
            texto(pantalla, valor, CHICA, BLANCO, x, y + 18, alinear="izquierda")

        # El desafio del sector, si hay
        y = adentro.top + 196
        interfaz.separador(pantalla, adentro.left, y - 18, adentro.width)
        desafio = director.desafio
        if desafio is not None:
            estado = {"cumplido": "CUMPLIDO", "fallado": "FALLADO"}.get(desafio.estado, desafio.texto_progreso())
            texto(pantalla, "DESAFIO", MINI, TEXTO_SUAVE, adentro.left, y, alinear="izquierda")
            texto(pantalla, desafio.nombre + "  " + estado, CHICA, desafio.color, adentro.left, y + 18,
                  alinear="izquierda")
            y += 52

        # Las mejoras: icono, nombre y niveles, en dos columnas
        texto(pantalla, "MEJORAS", MINI, TEXTO_SUAVE, adentro.left, y, alinear="izquierda")
        mejoras = partida.mejoras_elegidas()
        if not mejoras:
            texto(pantalla, "TODAVIA NINGUNA", CHICA, TEXTO_APAGADO, adentro.left, y + 22, alinear="izquierda")
            return
        ancho_columna = adentro.width // 2
        for i, (tipo, veces) in enumerate(mejoras[:8]):
            mejora = TIPOS_MEJORA[tipo]
            x = adentro.left + (i % 2) * ancho_columna
            fila_y = y + 26 + (i // 2) * 30
            if fila_y > adentro.bottom - 8:
                break
            dibujo.pixel_art(pantalla, mejora.icono, x + 10, fila_y, mejora.color, 3)
            texto(pantalla, mejora.nombre, MINI, BLANCO, x + 28, fila_y - 5, alinear="izquierda")
            for nivel in range(mejora.maximo):
                pip = pygame.Rect(x + 28 + nivel * 12, fila_y + 5, 8, 4)
                pantalla.fill(mejora.color if nivel < veces else LINEA_APAGADA, pip)

    def _dibujar_confirmacion(self, pantalla):
        # Ventana encima de todo: se pierde la partida. Dos botones; por defecto, NO
        dibujo.oscurecer(pantalla, FONDO, 150)
        panel = pygame.Rect(0, 0, 560, 240)
        panel.center = (CENTRO_X, 290)
        adentro = interfaz.panel(pantalla, panel, ROJO, "¿VOLVER AL MENU?")
        texto(pantalla, "SE PIERDE LA PARTIDA Y SU PUNTAJE", CHICA, BLANCO, panel.centerx, adentro.top + 20)
        texto(pantalla, dibujo.numero_arcade(self.escena_juego.partida.puntaje) + " PUNTOS", CHICA, ROJO,
              panel.centerx, adentro.top + 48)
        for i, (nombre, es_si) in enumerate((("NO", False), ("SI", True))):
            boton = pygame.Rect(0, 0, 150, 44)
            boton.center = (panel.centerx - 90 + i * 180, adentro.bottom - 30)
            elegido = self.confirmar_si == es_si
            if elegido:
                pantalla.fill(ROJO if es_si else CIAN, boton)
                texto(pantalla, nombre, MEDIA, FONDO, boton.centerx + 2, boton.centery + 1, sombra=None)
            else:
                pygame.draw.rect(pantalla, LINEA_APAGADA, boton, 2)
                texto(pantalla, nombre, MEDIA, TEXTO_SUAVE, boton.centerx + 2, boton.centery + 1)
