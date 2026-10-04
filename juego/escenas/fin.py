"""
Game Over: el resumen de la partida, la tabla de records y que hacer despues.

    izquierda: el puntaje (cuenta desde cero), las estadisticas (van saliendo de a una)
               y la letra del rango de cada sector cerrado
    derecha:   los mejores de esta dificultad, las mejoras elegidas y los logros nuevos
    ENTER otra partida (misma dificultad) · ESC al menu
"""
import random

import pygame

from juego import dibujo, lienzo
from juego.dibujo import texto, MINI, CHICA, MEDIA, GRANDE, TITULO
from juego.config import (ROJO, AMARILLO, CIAN, BLANCO, GRIS, FUEGO, ORO, ESCARCHA, ENERGIA, CORAZON, SECTORES)
from juego.entrada import ACEPTAR, VOLVER
from juego.escenas.base import Escena
from juego.hud import COLOR_RANGO
from juego.mejoras import TIPOS_MEJORA

MS_CONTADOR = 1500          # el puntaje tarda esto en contar
MS_POR_FILA = 120           # despues, las estadisticas salen de a una


def reloj(ms):
    # 754000 -> "12:34"
    segundos = int(ms) // 1000
    return str(segundos // 60) + ":" + str(segundos % 60).zfill(2)


class Fin(Escena):
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
        # Nuevo record: fuegos artificiales cuando termina de contar
        if self.fila_nueva == 0 and self.contador() == self.partida.puntaje and random.random() < 0.05:
            paleta = random.choice([FUEGO, ORO, ESCARCHA, ENERGIA, CORAZON])
            self.app.efectos.explosion(random.randint(80, lienzo.ancho - 80), random.randint(80, 560), paleta, 40, 6)
        # Las teclas se ignoran el primer momento (para no saltear esta pantalla sin querer)
        if self.tiempo_en_escena() <= 800:
            return
        if entrada.pulso(ACEPTAR):
            self.app.nueva_partida(self.partida.dificultad)     # otra vez, con la misma dificultad
        elif entrada.pulso(VOLVER):
            self._volver_al_menu()

    def _volver_al_menu(self):
        from juego.escenas.inicio import Inicio     # (aca adentro: Inicio tambien llega hasta Fin)
        self.app.efectos.reiniciar()
        self.app.fondo.ir_a_sector(SECTORES[0], instantaneo=True)
        self.app.sonidos.reproducir("seleccion")
        self.app.cambiar_escena(Inicio(self.app))

    def filas(self):
        # Las estadisticas: (nombre, valor)
        partida = self.partida
        estadisticas = partida.estadisticas
        return [
            ("TIEMPO", reloj(partida.tiempo)),
            ("SECTOR", str(partida.director.numero_sector) + " (NIVEL " + str(partida.nivel) + ")"),
            ("MONEDAS", str(estadisticas.monedas)),
            ("MEJOR COMBO", str(partida.mejor_combo)),
            ("ENEMIGOS", str(estadisticas.enemigos)),
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

    def dibujar(self, pantalla_completa):
        # Fondo y fuegos artificiales en todo el ancho; el resto en la zona central de 800x600
        self.dibujar_fondo(pantalla_completa)
        self.app.efectos.dibujar(pantalla_completa)     # fuegos artificiales detras de todo
        pantalla = dibujo.zona_central(pantalla_completa)
        dibujo.texto_3d(pantalla, "GAME OVER", TITULO, ROJO, (110, 0, 30), 58)
        self._dibujar_partida(pantalla)
        self._dibujar_records_y_mejoras(pantalla)

        contador = self.contador()
        if self.fila_nueva == 0 and contador == self.partida.puntaje:
            texto(pantalla, "¡NUEVO RECORD!", MEDIA, dibujo.color_arcoiris(), 400, 492)
        ayuda = self.app.entrada.ayuda
        if dibujo.parpadeo():
            texto(pantalla, ayuda("ENTER OTRA VEZ", "A OTRA VEZ"), MEDIA, CIAN, 400, 535)
        texto(pantalla, ayuda("ESC MENU", "B MENU"), CHICA, GRIS, 400, 570)
        dibujo.efecto_crt(pantalla_completa)

    def _dibujar_partida(self, pantalla):
        marco = pygame.Rect(30, 100, 360, 360)
        dibujo.marco(pantalla, marco, AMARILLO if self.fila_nueva == 0 else CIAN)
        texto(pantalla, "PUNTOS", CHICA, ROJO, marco.centerx, 130)
        texto(pantalla, dibujo.numero_arcade(self.contador()), GRANDE, BLANCO, marco.centerx, 168)

        # Las estadisticas salen de a una despues de que termina de contar el puntaje
        visibles = (self.tiempo_en_escena() - MS_CONTADOR) // MS_POR_FILA
        for i, (nombre, valor) in enumerate(self.filas()):
            if i >= visibles:
                break
            fila_y = 210 + i * 26
            texto(pantalla, nombre, CHICA, GRIS, marco.left + 24, fila_y, alinear="izquierda")
            texto(pantalla, valor, CHICA, BLANCO, marco.right - 24, fila_y, alinear="derecha")

        # El rango de cada sector cerrado
        rangos = self.partida.estadisticas.rangos
        if visibles > len(self.filas()):
            if rangos:
                texto(pantalla, "RANGOS", CHICA, GRIS, marco.left + 24, 412, alinear="izquierda")
                for i, letra in enumerate(rangos[:7]):
                    color = COLOR_RANGO[letra] or dibujo.color_arcoiris()
                    texto(pantalla, letra, MEDIA, color, marco.left + 150 + i * 30, 412)
            else:
                texto(pantalla, "NINGUN SECTOR COMPLETO", MINI, GRIS, marco.centerx, 412)

    def _dibujar_records_y_mejoras(self, pantalla):
        marco = pygame.Rect(410, 100, 360, 360)
        dibujo.marco(pantalla, marco, CIAN)
        dificultad = self.partida.dificultad
        dibujo.tabla_records(pantalla, self.app.records.filas(dificultad), 130, self.fila_nueva,
                             titulo="MEJORES - " + dificultad, centro_x=marco.centerx)

        # Las mejoras de esta partida: iconos (con un numero si se eligieron mas de una vez)
        mejoras = self.partida.mejoras_elegidas()
        texto(pantalla, "MEJORAS", CHICA, ROJO, marco.centerx, 318)
        if not mejoras:
            texto(pantalla, "NINGUNA", MINI, GRIS, marco.centerx, 348)
        for i, (tipo, veces) in enumerate(mejoras[:16]):
            mejora = TIPOS_MEJORA[tipo]
            icono_x = marco.left + 40 + (i % 8) * 40
            icono_y = 350 + (i // 8) * 34
            dibujo.pixel_art(pantalla, mejora.icono, icono_x, icono_y, mejora.color, 3)
            if veces > 1:
                texto(pantalla, str(veces), MINI, BLANCO, icono_x + 12, icono_y + 12)

        # Logros que se desbloquearon en esta partida
        if self.logros_nuevos:
            if dibujo.parpadeo(500):
                texto(pantalla, "¡LOGROS NUEVOS: " + str(len(self.logros_nuevos)) + "!", CHICA, AMARILLO,
                      marco.centerx, 430)
            else:
                texto(pantalla, self.logros_nuevos[0].nombre, CHICA, AMARILLO, marco.centerx, 430)
