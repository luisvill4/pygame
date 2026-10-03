"""
Pausa: la ultima imagen del juego oscurecida y un menu para elegir con ARRIBA/ABAJO + ENTER:

    CONTINUAR        vuelve al juego (tambien con P, ESC o el boton Menu del mando)
    OPCIONES         el menu de opciones (tambien con O o el boton Vista)
    VOLVER AL MENU   pide confirmacion: se pierde la partida y su puntaje
"""
import pygame

from juego import dibujo
from juego.dibujo import texto, CHICA, MEDIA, TITULO
from juego.config import FONDO, CIAN, BLANCO, GRIS, ROJO, AMARILLO, SECTORES
from juego.entrada import PAUSA, VOLVER, OPCIONES, ACEPTAR, ARRIBA, ABAJO, IZQUIERDA, DERECHA
from juego.escenas.base import Escena
from juego.escenas.opciones import Opciones
from juego.escenas.inicio import Inicio

FILAS_PAUSA = ["CONTINUAR", "OPCIONES", "VOLVER AL MENU"]


class Pausa(Escena):
    def __init__(self, app, escena_juego, captura):
        super().__init__(app)
        self.escena_juego = escena_juego    # a donde se vuelve al seguir
        self.captura = captura              # imagen del juego al pausar
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
        for accion in entrada.acciones:
            if accion == ARRIBA:
                self.fila = (self.fila - 1) % len(FILAS_PAUSA)
            elif accion == ABAJO:
                self.fila = (self.fila + 1) % len(FILAS_PAUSA)
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
            self.app.sonidos.reproducir("seleccion")
            self.confirmando = True
            self.confirmar_si = False

    def _actualizar_confirmacion(self, entrada):
        for accion in entrada.acciones:
            if accion in (IZQUIERDA, DERECHA):
                self.confirmar_si = not self.confirmar_si
            elif accion == ACEPTAR:
                if self.confirmar_si:
                    self._volver_al_menu()
                else:
                    self.confirmando = False
                return
            elif accion == VOLVER:          # ESC o B: es lo mismo que NO
                self.confirmando = False
                return

    def _seguir(self):
        self.app.sonidos.reanudar_todo()
        self.app.cambiar_escena(self.escena_juego)

    def _abrir_opciones(self):
        self.app.sonidos.reproducir("seleccion")
        self.app.cambiar_escena(Opciones(self.app, volver_a=self, en_partida=True))

    def _volver_al_menu(self):
        # Se abandona la partida (sin guardar el puntaje) y se vuelve a la pantalla de inicio
        self.app.sonidos.reanudar_todo()
        self.app.sonidos.parar_musica()
        self.app.efectos.reiniciar()
        self.app.fondo.ir_a_sector(SECTORES[0], instantaneo=True)
        self.app.sonidos.reproducir("seleccion")
        self.app.cambiar_escena(Inicio(self.app))

    # ---------- Dibujo ----------

    def dibujar(self, pantalla_completa):
        pantalla_completa.blit(self.captura, (0, 0))
        dibujo.oscurecer(pantalla_completa, FONDO, 160)
        pantalla = dibujo.zona_central(pantalla_completa)
        dibujo.texto_3d(pantalla, "PAUSA", TITULO, CIAN, (0, 70, 110), 170)

        dibujo.marco(pantalla, pygame.Rect(200, 240, 400, 170), CIAN)
        for i, fila in enumerate(FILAS_PAUSA):
            dibujo.opcion(pantalla, fila, MEDIA, 400, 285 + i * 40, i == self.fila)

        if self.confirmando:
            self._dibujar_confirmacion(pantalla_completa, pantalla)

        # Ayuda de abajo, segun lo que este en pantalla
        ayuda = self.app.entrada.ayuda
        if self.confirmando:
            lineas = (ayuda("IZQ/DER ELEGIR   ENTER ACEPTAR", "IZQ/DER ELEGIR   A ACEPTAR"),
                      ayuda("ESC CANCELAR", "B CANCELAR"))
        else:
            lineas = (ayuda("ARRIBA/ABAJO ELEGIR   ENTER ACEPTAR", "ARRIBA/ABAJO ELEGIR   A ACEPTAR"),
                      ayuda("P SEGUIR   O OPCIONES", "MENU SEGUIR   VISTA OPCIONES"))
        texto(pantalla, lineas[0], CHICA, GRIS, 400, 470)
        texto(pantalla, lineas[1], CHICA, GRIS, 400, 500)
        dibujo.efecto_crt(pantalla_completa)

    def _dibujar_confirmacion(self, pantalla_completa, pantalla):
        dibujo.oscurecer(pantalla_completa, FONDO, 140)
        dibujo.marco(pantalla, pygame.Rect(130, 200, 540, 240), ROJO)
        texto(pantalla, "¿VOLVER AL MENU?", MEDIA, AMARILLO, 400, 245)
        texto(pantalla, "SE PERDERA LA PARTIDA", CHICA, BLANCO, 400, 295)
        texto(pantalla, "Y SU PUNTAJE: " + dibujo.numero_arcade(self.escena_juego.partida.puntaje),
              CHICA, ROJO, 400, 323)
        dibujo.opcion(pantalla, "NO", MEDIA, 320, 385, not self.confirmar_si)
        dibujo.opcion(pantalla, "SI", MEDIA, 480, 385, self.confirmar_si)
