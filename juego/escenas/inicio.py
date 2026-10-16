"""
Pantalla de inicio (usa todo el ancho 16:9):

- Arriba, una franja con los logros, el record y la dificultad.
- A la izquierda el logo (con un brillo que lo recorre cada tanto), el lema y el menu
  ARCADE / HISTORIA / LOGROS / OPCIONES / SALIR: ARRIBA/ABAJO elige (la nave es el cursor y se
  desliza) y debajo se explica la opcion elegida.
- A la derecha la nave grande volando y un panel con tres paginas (COMO JUGAR,
  POWER-UPS, RECORDS): cambian solas cada PAGINA_MS o con LB/RB (Q/E) o IZQ/DER.
- Abajo, la barra con los botones.

Todo lo de cada pagina tiene que entrar en el panel (test_inicio.py lo comprueba).
"""
import math

import pygame

from juego import dibujo, nave, recursos, interfaz
from juego.dibujo import texto, MINI, CHICA, TITULO
from juego.config import (ANCHO, ROJO, BLANCO, AMARILLO, MAGENTA, CIAN, GRIS, NARANJA, MS_CUADRO_ENEMIGO,
                          DIFICULTADES, ORDEN_DIFICULTADES, JEFE_CADA_NIVELES, FILAS_RECORDS, TEXTO_SUAVE,
                          TEXTO_APAGADO, LINEA_APAGADA)
from juego.entrada import ACEPTAR, IZQUIERDA, DERECHA, ARRIBA, ABAJO, PESTANA_ANTERIOR, PESTANA_SIGUIENTE
from juego.escenas.base import Escena
from juego.sonido import SILENCIO
from juego.escenas.opciones import Opciones
from juego.escenas.arcade.dificultad import Dificultad
from juego.escenas.logros import Logros
from juego.escenas.historia.galaxia import Galaxia
from juego.enemigos import TIPOS_ENEMIGO
from juego.moneda import imagen_moneda
from juego.powerups import TIPOS_POWERUP
from juego.logros import LOGROS
from juego.carteles import TROFEO

MENU = ["ARCADE", "HISTORIA", "LOGROS", "OPCIONES", "SALIR"]
DESCRIPCION_MENU = {        # (hasta 25 letras: entran en un renglon)
    "ARCADE": "LA RUTA SIN FIN Y RECORDS",
    "HISTORIA": "LA MAREA. SEGUI EL COMPAS",
    "LOGROS": "LOGROS Y HANGAR DE NAVES",
    "OPCIONES": "VIDEO, SONIDO Y MAS",
    "SALIR": "CERRAR EL JUEGO",
}
PESTANAS = ["GUIA", "POWER-UPS", "RECORDS"]
PAGINA_MS = 7000            # cada cuanto cambia sola la pagina del panel

# Disposicion
IZQUIERDA_X = 64            # el logo y el menu
MENU_X, MENU_Y, ALTO_FILA = 112, 286, 44
PANEL = pygame.Rect(514, 228, 504, 312)
BARRA_PESTANAS = pygame.Rect(PANEL.left + 14, PANEL.top + 14, PANEL.width - 28, 28)
CONTENIDO = pygame.Rect(PANEL.left + 18, PANEL.top + 64, PANEL.width - 36, PANEL.bottom - PANEL.top - 76)
NAVE_GRANDE = (780, 128)    # donde vuela la nave grande
ALTO_POWERUP = 29           # alto del renglon de cada power-up en su pagina
COLUMNA_DESCRIPCION = 172   # donde empieza la descripcion de cada power-up (desde el borde del contenido)
BRILLO_CADA, BRILLO_MS = 4500, 700      # cada cuanto pasa el brillo por el logo y cuanto tarda
CIAN_OSCURO = (0, 70, 110)
BRONCE = NARANJA
COLORES_PUESTO = [AMARILLO, BLANCO, BRONCE]     # 1º, 2º y 3º; el resto en gris


def altura_nave():
    # La nave grande sube y baja de a 3 pixeles (estilo retro)
    return NAVE_GRANDE[1] + round(math.sin(pygame.time.get_ticks() / 300) * 2) * 3


class Inicio(Escena):
    ambiente = SILENCIO
    musica = "menu"

    def __init__(self, app):
        super().__init__(app)
        self.opcion = 0                     # elegida en MENU
        self.cursor = interfaz.Cursor(0)    # donde se dibuja el cursor (se desliza)
        self.pagina = 0                     # pestaña del panel
        self.pagina_desde = app.ahora()     # cuando se mostro (para cambiarla sola)
        self.cerrar_en = None               # SALIR: se cierra cuando termina de sonar el apagado
        nave.cambiar_equipo(())             # en los menus, la nave limpia (los modulos son de la historia)

    def actualizar(self, entrada):
        self.mover_fondo()
        nave.preparar_giros(2)          # (los giros de la nave, de a poco: ver nave.girada)
        self.app.efectos.estela(NAVE_GRANDE[0], altura_nave() + 24, 0)     # (la nave grande mide el doble)
        self.app.efectos.actualizar()
        self.cursor.avanzar()

        # Las paginas cambian solas, o con LB/RB o IZQ/DER (y vuelve a contar el tiempo)
        if entrada.pulso(PESTANA_ANTERIOR) or entrada.pulso(IZQUIERDA):
            self.cambiar_pagina(-1)
        elif entrada.pulso(PESTANA_SIGUIENTE) or entrada.pulso(DERECHA):
            self.cambiar_pagina(1)
        elif self.app.ahora() - self.pagina_desde >= PAGINA_MS:
            self.cambiar_pagina(1, con_sonido=False)

        if entrada.pulso(ARRIBA):
            self._elegir((self.opcion - 1) % len(MENU))
        elif entrada.pulso(ABAJO):
            self._elegir((self.opcion + 1) % len(MENU))
        if self.cerrar_en is not None:
            if self.app.ahora() >= self.cerrar_en:
                self.app.ejecutando = False         # (despues de que se oye el apagado)
            return
        if entrada.pulso(ACEPTAR):
            elegida = MENU[self.opcion]
            self.app.sonidos.reproducir("ui_apagar" if elegida == "SALIR" else "ui_aceptar")
            if elegida == "ARCADE":
                self.app.cambiar_escena(Dificultad(self.app, volver_a=self))
            elif elegida == "HISTORIA":
                self.app.cambiar_escena(Galaxia(self.app))
            elif elegida == "LOGROS":
                self.app.cambiar_escena(Logros(self.app, volver_a=self))
            elif elegida == "OPCIONES":
                self.app.cambiar_escena(Opciones(self.app, volver_a=self))
            else:
                self.cerrar_en = self.app.ahora() + 450

    def _elegir(self, opcion):
        self.opcion = opcion
        self.cursor.ir_a(opcion)
        self.app.sonidos.reproducir("ui_mover")

    def cambiar_pagina(self, direccion, con_sonido=True):
        self.pagina = (self.pagina + direccion) % len(PESTANAS)
        self.pagina_desde = self.app.ahora()
        if con_sonido:
            self.app.sonidos.reproducir("ui_pestana")

    # ---------- Dibujo ----------

    def dibujar(self, pantalla):
        self.dibujar_fondo(pantalla)
        self._dibujar_franja_de_arriba(pantalla)
        self._dibujar_logo(pantalla)
        self.app.efectos.dibujar(pantalla)
        imagen_nave = nave.imagen("nave")
        grande = pygame.transform.scale(imagen_nave, (imagen_nave.get_width() * 2, imagen_nave.get_height() * 2))
        pantalla.blit(grande, grande.get_rect(center=(NAVE_GRANDE[0], altura_nave())))

        interfaz.menu(pantalla, MENU, self.cursor, MENU_X, MENU_Y, 380, ALTO_FILA)
        lineas = dibujo.partir_lineas(DESCRIPCION_MENU[MENU[self.opcion]], CHICA, 400)
        for i, linea in enumerate(lineas):
            texto(pantalla, linea, CHICA, TEXTO_SUAVE, MENU_X - 16, MENU_Y + len(MENU) * ALTO_FILA + 10 + i * 24,
                  alinear="izquierda")

        self._dibujar_panel(pantalla)
        [self._dibujar_como_se_juega, self._dibujar_powerups, self._dibujar_records][self.pagina](pantalla)
        interfaz.ayudas(pantalla, self.app.entrada,
                        [("elegir", "ELEGIR"), ("pestanas", "PAGINA"), ("aceptar", "ACEPTAR")])

    def _dibujar_franja_de_arriba(self, pantalla):
        # Logros a la izquierda; record y dificultad a la derecha (como en una maquina)
        dificultad = self.app.opciones.dificultad
        hechos = sum(1 for logro in LOGROS if logro.id in self.app.progreso.logros)
        dibujo.pixel_art(pantalla, TROFEO, IZQUIERDA_X + 10, 24, AMARILLO, 3)
        texto(pantalla, "LOGROS", CHICA, TEXTO_SUAVE, IZQUIERDA_X + 30, 24, alinear="izquierda")
        texto(pantalla, str(hechos) + "/" + str(len(LOGROS)), CHICA, BLANCO, IZQUIERDA_X + 136, 24,
              alinear="izquierda")

        # A la derecha, de derecha a izquierda: la dificultad y el record de esa dificultad
        fuente = recursos.fuente(CHICA)
        x = ANCHO - IZQUIERDA_X
        record = dibujo.numero_arcade(self.app.records.maximo(dificultad))
        for mensaje, color in ((dificultad, DIFICULTADES[dificultad]["color"]), ("DIFICULTAD", TEXTO_SUAVE),
                               (record, BLANCO), ("RECORD", ROJO)):
            texto(pantalla, mensaje, CHICA, color, x, 24, alinear="derecha")
            x -= fuente.size(mensaje)[0] + (16 if color in (TEXTO_SUAVE, ROJO) else 12)
            if mensaje == "DIFICULTAD":
                x -= 20             # mas aire entre los dos grupos
        interfaz.separador(pantalla, IZQUIERDA_X, 46, ANCHO - 2 * IZQUIERDA_X)

    def _dibujar_logo(self, pantalla):
        # El titulo con relieve, un brillo que lo cruza cada tanto y el lema
        for palabra, y in (("CAZA", 104), ("MONEDAS", 162)):
            dibujo.texto_3d(pantalla, palabra, TITULO, AMARILLO, MAGENTA, y, 6, None, IZQUIERDA_X, "izquierda")
            self._brillo(pantalla, palabra, y)
        texto(pantalla, "ATRAPA.  ESQUIVA.  SOBREVIVE.", CHICA, CIAN, IZQUIERDA_X, 218, alinear="izquierda")

    def _brillo(self, pantalla, palabra, y):
        # Una franja blanca inclinada recorre las letras (solo se pinta donde hay letra)
        momento = pygame.time.get_ticks() % BRILLO_CADA
        if momento > BRILLO_MS:
            return
        letras = recursos.fuente(TITULO).render(palabra, False, BLANCO)
        caja = letras.get_rect(midleft=(IZQUIERDA_X, y))
        franja_x = -60 + (letras.get_width() + 120) * momento / BRILLO_MS - (y - 104) * 0.4
        franja = pygame.Surface(letras.get_size(), pygame.SRCALPHA)
        alto = letras.get_height()
        pygame.draw.polygon(franja, (255, 255, 255, 255),
                            [(franja_x + 20, 0), (franja_x + 44, 0), (franja_x + 24, alto), (franja_x, alto)])
        letras = letras.convert_alpha()
        letras.blit(franja, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        pantalla.blit(letras, caja)

    def _dibujar_panel(self, pantalla):
        # Panel, pestañas (la actual resaltada) y la barrita del tiempo de la pagina
        interfaz.panel(pantalla, PANEL, CIAN)
        barra = interfaz.pestanas(pantalla, BARRA_PESTANAS, self.app.entrada, PESTANAS, self.pagina, CIAN,
                                  CIAN_OSCURO)
        linea_y = BARRA_PESTANAS.bottom + 4
        pantalla.fill(CIAN_OSCURO, (barra.left, linea_y, barra.width, 4))
        avance = min(1, (self.app.ahora() - self.pagina_desde) / PAGINA_MS)
        largo = int(barra.width * avance) // 4 * 4          # en bloques de 4 px
        pantalla.fill(CIAN, (barra.left, linea_y, largo, 4))

    # ---------- Paginas ----------

    def _dibujar_como_se_juega(self, pantalla):
        # Cuatro filas: dibujo, que hacer y que pasa; abajo, como se sube de nivel
        x = CONTENIDO.left
        filas_y = [CONTENIDO.top + 18 + i * 50 for i in range(4)]
        moneda = imagen_moneda()
        pantalla.blit(moneda, moneda.get_rect(center=(x + 18, filas_y[0])))
        self._fila(pantalla, filas_y[0], "RECOGE MONEDAS", "PUNTOS Y CREDITOS", AMARILLO)

        perseguidor = recursos.cuadro_animado(TIPOS_ENEMIGO["perseguidor"].cuadros(), MS_CUADRO_ENEMIGO)
        pantalla.blit(perseguidor, perseguidor.get_rect(center=(x + 18, filas_y[1])))
        self._fila(pantalla, filas_y[1], "ESQUIVA ENEMIGOS", "SI TE TOCAN, -1 VIDA", ROJO)

        # El dash: la nave cruzando con su estela cian
        fantasma = pygame.transform.rotate(pygame.transform.scale(nave.imagen("fantasma"), (26, 26)), -90)
        for i in range(3):
            fantasma.set_alpha(80 + i * 80)
            pantalla.blit(fantasma, fantasma.get_rect(center=(x + 6 + i * 8, filas_y[2])))
        self._fila(pantalla, filas_y[2], "ROMPE CON EL DASH", "¡DASH PERFECTO!", CIAN)

        embestidor = recursos.cuadro_animado(TIPOS_ENEMIGO["embestidor"].cuadros(), MS_CUADRO_ENEMIGO)
        embestidor = pygame.transform.scale(embestidor, (30, 30))
        pantalla.blit(embestidor, embestidor.get_rect(center=(x + 18, filas_y[3])))
        self._fila(pantalla, filas_y[3], "FRENA SU EMBESTIDA", "CON UN DASH A TIEMPO", MAGENTA)

        texto(pantalla, "CADA " + str(JEFE_CADA_NIVELES) + " NIVELES, UN JEFE", MINI, ROJO, CONTENIDO.centerx,
              CONTENIDO.bottom - 6)

    def _fila(self, pantalla, y, que_hacer, resultado, color):
        x = CONTENIDO.left + 48
        texto(pantalla, que_hacer, CHICA, BLANCO, x, y - 9, alinear="izquierda")
        texto(pantalla, resultado, CHICA, color, x, y + 11, alinear="izquierda")

    def _dibujar_powerups(self, pantalla):
        # Todos, uno por renglon: capsula, nombre y que hace
        for i, powerup in enumerate(TIPOS_POWERUP.values()):
            y = CONTENIDO.top + 14 + i * ALTO_POWERUP
            flotar = round(math.sin(pygame.time.get_ticks() / 300 + i)) * 2   # cada una a su ritmo
            powerup.dibujar_capsula(pantalla, CONTENIDO.left + 16, y + flotar)
            texto(pantalla, powerup.nombre, CHICA, powerup.color, CONTENIDO.left + 42, y, alinear="izquierda")
            texto(pantalla, powerup.descripcion, MINI, TEXTO_SUAVE, CONTENIDO.left + COLUMNA_DESCRIPCION, y,
                  alinear="izquierda")

    def _dibujar_records(self, pantalla):
        # Izquierda: el top 5 de la dificultad elegida. Derecha: el mejor de cada dificultad
        dificultad = self.app.opciones.dificultad
        color_dificultad = DIFICULTADES[dificultad]["color"]
        izquierda = CONTENIDO.left
        texto(pantalla, "TOP " + str(FILAS_RECORDS), CHICA, color_dificultad, izquierda, CONTENIDO.top + 8,
              alinear="izquierda")
        filas = self.app.records.filas(dificultad)
        for puesto in range(FILAS_RECORDS):
            y = CONTENIDO.top + 44 + puesto * 30
            color = COLORES_PUESTO[puesto] if puesto < len(COLORES_PUESTO) else GRIS
            texto(pantalla, str(puesto + 1) + ".", CHICA, color, izquierda, y, alinear="izquierda")
            if puesto < len(filas):
                texto(pantalla, filas[puesto]["nombre"], CHICA, color, izquierda + 40, y, alinear="izquierda")
                texto(pantalla, dibujo.numero_arcade(filas[puesto]["puntos"]), CHICA, color, izquierda + 208, y,
                      alinear="derecha")
            else:
                texto(pantalla, "---", CHICA, TEXTO_APAGADO, izquierda + 40, y, alinear="izquierda")
                texto(pantalla, "------", CHICA, TEXTO_APAGADO, izquierda + 208, y, alinear="derecha")
        if not filas:
            texto(pantalla, "¡SE EL PRIMERO!", MINI, AMARILLO if dibujo.parpadeo(400) else GRIS, izquierda + 104,
                  CONTENIDO.bottom - 6)

        pantalla.fill(LINEA_APAGADA, (CONTENIDO.left + 226, CONTENIDO.top, 2, CONTENIDO.height))
        derecha = CONTENIDO.right
        texto(pantalla, "MEJOR", CHICA, CIAN, CONTENIDO.left + 244, CONTENIDO.top + 8, alinear="izquierda")
        for i, nombre in enumerate(ORDEN_DIFICULTADES):
            y = CONTENIDO.top + 44 + i * 44
            maximo = self.app.records.maximo(nombre)
            texto(pantalla, nombre, MINI, DIFICULTADES[nombre]["color"], CONTENIDO.left + 244, y - 8, alinear="izquierda")
            texto(pantalla, dibujo.numero_arcade(maximo), CHICA, BLANCO if maximo else TEXTO_APAGADO, derecha, y + 8,
                  alinear="derecha")
