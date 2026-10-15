"""
Game Over: el resumen de la partida, la tabla de records y que hacer despues.

    RESULTADO:     el puntaje (cuenta desde cero), hasta donde llegaste y el rango de cada
                   sector cerrado, cada uno en su medalla
    ESTADISTICAS:  van saliendo de a una
    RECORDS:       los mejores de esta dificultad, las mejoras elegidas y los logros nuevos
    ENTER otra partida (misma dificultad) · ESC al menu
"""
import random

import pygame

from juego import dibujo, interfaz
from juego.dibujo import texto, MINI, CHICA, MEDIA, GRANDE, TITULO
from juego.config import (ANCHO, CENTRO_X, FONDO, ROJO, AMARILLO, CIAN, MAGENTA, BLANCO, FUEGO, ORO, ESCARCHA,
                          ENERGIA, CORAZON, SECTORES, DIFICULTADES, FILAS_RECORDS, CONTORNO, TEXTO_SUAVE,
                          TEXTO_APAGADO)
from juego.entrada import ACEPTAR, VOLVER
from juego.escenas.base import Escena
from juego.sonido import SILENCIO
from juego.carteles import COLOR_RANGO
from juego.mejoras import TIPOS_MEJORA

MS_CONTADOR = 1500          # el puntaje tarda esto en contar
MS_POR_FILA = 120           # despues, las estadisticas salen de a una

# Los tres paneles (de izquierda a derecha)
RESULTADO = pygame.Rect(48, 140, 330, 400)
ESTADISTICAS = pygame.Rect(398, 140, 300, 400)
RECORDS = pygame.Rect(718, 140, ANCHO - 766, 400)


def reloj(ms):
    # 754000 -> "12:34"
    segundos = int(ms) // 1000
    return str(segundos // 60) + ":" + str(segundos % 60).zfill(2)


class Fin(Escena):
    ambiente = SILENCIO
    musica = "fin"
    def __init__(self, app, partida, fila_nueva):
        super().__init__(app)
        self.partida = partida
        self.fila_nueva = fila_nueva    # fila de la tabla que se acaba de agregar (-1 = ninguna)
        self.logros_nuevos = list(partida.logros_nuevos)

    def contador(self):
        # El puntaje cuenta desde cero hasta el resultado en 1.5 segundos
        puntaje = self.partida.puntaje
        return min(puntaje, int(puntaje * self.tiempo_en_escena() / MS_CONTADOR))

    def actualizar(self, entrada):
        self.mover_fondo()
        self.app.efectos.actualizar()
        self._sonidos()
        # Nuevo record: fuegos artificiales cuando termina de contar
        if self.fila_nueva == 0 and self.contador() == self.partida.puntaje and random.random() < 0.05:
            paleta = random.choice([FUEGO, ORO, ESCARCHA, ENERGIA, CORAZON])
            self.app.sonidos.reproducir("fuego_artificial")
            self.app.efectos.explosion(random.randint(80, ANCHO - 80), random.randint(80, 560), paleta, 40, 6)
        # Las teclas se ignoran el primer momento (para no saltear esta pantalla sin querer)
        if self.tiempo_en_escena() <= 800:
            return
        if entrada.pulso(ACEPTAR):
            self.app.nueva_partida(self.partida.dificultad)     # otra vez, con la misma dificultad
        elif entrada.pulso(VOLVER):
            self._volver_al_menu()

    def _sonidos(self):
        # El puntaje cuenta con tics que suben (8 en MS_CONTADOR) y termina en un "ding";
        # despues, cada fila de estadisticas que sale hace un tic
        t = self.tiempo_en_escena()
        sonados = getattr(self, "sonados", 0)
        if self.partida.puntaje > 0 and sonados < 8 and t >= (sonados + 1) * MS_CONTADOR / 9:
            self.app.sonidos.reproducir("contador_%d" % (sonados + 1))
            self.sonados = sonados + 1
        if t >= MS_CONTADOR and not getattr(self, "ding", False):
            self.ding = True
            if self.partida.puntaje > 0:
                self.app.sonidos.reproducir("contador_fin")
        filas = min(len(self.filas()), max(0, int((t - MS_CONTADOR) // MS_POR_FILA)))
        if filas > getattr(self, "filas_sonadas", 0):
            self.filas_sonadas = filas
            self.app.sonidos.reproducir("teclear")

    def _volver_al_menu(self):
        from juego.escenas.inicio import Inicio     # (aca adentro: Inicio tambien llega hasta Fin)
        self.app.efectos.reiniciar()
        self.app.fondo.ir_a_sector(SECTORES[0], instantaneo=True)
        self.app.sonidos.reproducir("ui_volver")
        self.app.cambiar_escena(Inicio(self.app))

    def filas(self):
        # Las estadisticas: (nombre, valor)
        partida = self.partida
        estadisticas = partida.estadisticas
        return [
            ("TIEMPO", reloj(partida.tiempo)),
            ("CREDITOS", str(estadisticas.creditos)),
            ("MONEDAS", str(estadisticas.monedas)),
            ("MEJOR COMBO", str(partida.mejor_combo)),
            ("ENEMIGOS", str(estadisticas.enemigos)),
            ("ESCUADRONES", str(estadisticas.escuadrones)),
            ("PERFECTOS", self._perfectos()),
            ("DESAFIOS", str(estadisticas.desafios)),
        ]

    def _perfectos(self):
        # "21", o con la mejor cadena si hubo: "21 (x3)"
        estadisticas = self.partida.estadisticas
        if estadisticas.mejor_cadena < 2:
            return str(estadisticas.perfectos)
        return str(estadisticas.perfectos) + " (x" + str(estadisticas.mejor_cadena) + ")"

    # ---------- Dibujo ----------

    def dibujar(self, pantalla):
        # Fondo y fuegos artificiales en todo el ancho; tres paneles: resultado,
        # estadisticas y records
        self.dibujar_fondo(pantalla)
        self.app.efectos.dibujar(pantalla)     # fuegos artificiales detras de todo
        dibujo.texto_3d(pantalla, "GAME OVER", TITULO, ROJO, (110, 0, 30), 56, 6, CONTORNO)
        contador = self.contador()
        if self.fila_nueva == 0 and contador == self.partida.puntaje:
            texto(pantalla, "¡NUEVO RECORD!", MEDIA, dibujo.color_arcoiris(), CENTRO_X, 112)
        self._dibujar_resultado(pantalla)
        self._dibujar_estadisticas(pantalla)
        self._dibujar_records(pantalla)
        if self.tiempo_en_escena() > 800:
            interfaz.ayudas(pantalla, self.app.entrada, [("aceptar", "OTRA VEZ"), ("volver", "MENU")])

    def _dibujar_resultado(self, pantalla):
        # El puntaje (cuenta desde cero), donde llegaste y el rango de cada sector cerrado
        color = AMARILLO if self.fila_nueva == 0 else CIAN
        adentro = interfaz.panel(pantalla, RESULTADO, color, "RESULTADO")
        texto(pantalla, "PUNTOS", CHICA, ROJO, adentro.centerx, adentro.top + 12)
        texto(pantalla, dibujo.numero_arcade(self.contador()), GRANDE, BLANCO, adentro.centerx, adentro.top + 52)
        partida = self.partida
        dificultad = partida.dificultad
        texto(pantalla, dificultad, CHICA, DIFICULTADES[dificultad]["color"], adentro.centerx, adentro.top + 96)
        texto(pantalla, "SECTOR " + partida.director.rotulo(), CHICA, TEXTO_SUAVE, adentro.centerx, adentro.top + 122)
        interfaz.separador(pantalla, adentro.left, adentro.top + 148, adentro.width)
        texto(pantalla, "RANGOS", MINI, TEXTO_SUAVE, adentro.centerx, adentro.top + 168)
        rangos = partida.estadisticas.rangos[:6]
        if not rangos:
            texto(pantalla, "NINGUN SECTOR COMPLETO", MINI, TEXTO_APAGADO, adentro.centerx, adentro.top + 206)
            return
        # Cada rango en su medalla: un cuadrado del color de la letra
        ancho = len(rangos) * 44 - 8
        for i, letra in enumerate(rangos):
            medalla = pygame.Rect(adentro.centerx - ancho // 2 + i * 44, adentro.top + 184, 36, 40)
            color = COLOR_RANGO[letra] or dibujo.color_arcoiris()
            pantalla.fill(interfaz.mezclar(color, FONDO, 0.75), medalla)
            pygame.draw.rect(pantalla, color, medalla, 2)
            texto(pantalla, letra, MEDIA, color, medalla.centerx + 2, medalla.centery + 1)
            texto(pantalla, str(i + 1), MINI, TEXTO_SUAVE, medalla.centerx, medalla.bottom + 10)

    def _dibujar_estadisticas(self, pantalla):
        # Salen de a una despues de que termina de contar el puntaje
        adentro = interfaz.panel(pantalla, ESTADISTICAS, CIAN, "ESTADISTICAS")
        visibles = (self.tiempo_en_escena() - MS_CONTADOR) // MS_POR_FILA
        for i, (nombre, valor) in enumerate(self.filas()):
            if i >= visibles:
                break
            fila_y = adentro.top + 12 + i * 34
            texto(pantalla, nombre, CHICA, TEXTO_SUAVE, adentro.left, fila_y, alinear="izquierda")
            texto(pantalla, valor, CHICA, BLANCO, adentro.right, fila_y, alinear="derecha")

    def _dibujar_records(self, pantalla):
        # Los mejores de esta dificultad (la fila nueva en arcoiris), las mejoras y los logros
        dificultad = self.partida.dificultad
        adentro = interfaz.panel(pantalla, RECORDS, MAGENTA, "RECORDS")
        filas = self.app.records.filas(dificultad)
        for i in range(FILAS_RECORDS):
            y = adentro.top + 12 + i * 28
            if i < len(filas):
                color = dibujo.color_arcoiris() if i == self.fila_nueva else (AMARILLO if i == 0 else BLANCO)
                texto(pantalla, str(i + 1) + ". " + filas[i]["nombre"], CHICA, color, adentro.left, y,
                      alinear="izquierda")
                texto(pantalla, dibujo.numero_arcade(filas[i]["puntos"]), CHICA, color, adentro.right, y,
                      alinear="derecha")
            else:
                texto(pantalla, str(i + 1) + ". ---", CHICA, TEXTO_APAGADO, adentro.left, y, alinear="izquierda")
                texto(pantalla, "------", CHICA, TEXTO_APAGADO, adentro.right, y, alinear="derecha")
        y = adentro.top + 12 + FILAS_RECORDS * 28 + 4
        interfaz.separador(pantalla, adentro.left, y, adentro.width)
        # Las mejoras de esta partida: iconos (con un numero si se eligieron mas de una vez)
        mejoras = self.partida.mejoras_elegidas()
        texto(pantalla, "MEJORAS", MINI, TEXTO_SUAVE, adentro.left, y + 18, alinear="izquierda")
        if not mejoras:
            texto(pantalla, "NINGUNA", MINI, TEXTO_APAGADO, adentro.left + 70, y + 18, alinear="izquierda")
        for i, (tipo, veces) in enumerate(mejoras[:12]):
            mejora = TIPOS_MEJORA[tipo]
            icono_x = adentro.left + 12 + (i % 6) * 42
            icono_y = y + 46 + (i // 6) * 32
            dibujo.pixel_art(pantalla, mejora.icono, icono_x, icono_y, mejora.color, 3)
            if veces > 1:
                texto(pantalla, str(veces), MINI, BLANCO, icono_x + 14, icono_y + 10)
        # Logros que se desbloquearon en esta partida
        if self.logros_nuevos:
            if dibujo.parpadeo(500):
                mensaje = "¡LOGROS NUEVOS: " + str(len(self.logros_nuevos)) + "!"
            else:
                mensaje = self.logros_nuevos[0].nombre
            texto(pantalla, mensaje, CHICA, AMARILLO, adentro.centerx, adentro.bottom - 8)
