"""
El Ojo: el primer jefe.

Fases:  entrar -> flotar (de lado a lado) -> atacar -> cansado (nucleo a la vista) -> flotar...
Al atacar se carga 0.7 s y dispara JEFE_RAFAGAS rafagas desde el ojo, turnandose entre:
    abanico: hacia la nave
    anillo:  hacia todos lados, con un giro distinto en cada rafaga
Sprite: sprites/jefe.png, 6 cuadros de 120x120 de a pares (flotar, atacar, cansado).
"""
import math
import random

import pygame

from juego import recursos, dibujo
from juego.config import (ANCHO, MAGENTA, GRIS, ROJO, AMARILLO, BLANCO, ORO, EMBESTIDA, MS_POR_FRAME,
                          JEFE_FLOTAR, JEFE_CANSADO, JEFE_RAFAGAS)
from juego.jefes.base import Jefe, registrar_jefe, TAMANO
from juego.proyectiles import Bala


def jefe_respaldo(color_nucleo):
    # Jefe dibujado a mano (escudo magenta con el nucleo al centro), por si falta su sprite
    imagen = pygame.Surface((TAMANO, TAMANO), pygame.SRCALPHA)
    puntos = [(8, 14), (112, 14), (112, 62), (60, 110), (8, 62)]
    pygame.draw.polygon(imagen, MAGENTA, puntos)
    pygame.draw.polygon(imagen, (58, 0, 40), puntos, 4)
    pygame.draw.circle(imagen, (58, 0, 40), (60, 50), 22)
    pygame.draw.circle(imagen, color_nucleo, (60, 50), 18)
    return imagen


@registrar_jefe
class JefeOjo(Jefe):
    tipo = "ojo"
    nombre = "EL OJO"
    apodo = "EL QUE TODO LO VE"
    color = MAGENTA

    def __init__(self, partida):
        super().__init__(partida)
        self.ataque = "anillo"          # ultimo ataque que hizo (se van turnando)
        self.rafagas = 0                # rafagas que le quedan en el ataque actual
        self.proximo_disparo = 0

    @classmethod
    def cargar_animaciones(cls):
        cuadros = recursos.hoja("jefe.png", TAMANO)
        if cuadros is None:
            cuadros = [jefe_respaldo(GRIS), jefe_respaldo(GRIS),
                       jefe_respaldo(ROJO), jefe_respaldo((255, 150, 140)),
                       jefe_respaldo(AMARILLO), jefe_respaldo(BLANCO)]
        if len(cuadros) >= 6:
            return {"flotar": cuadros[0:2], "atacar": cuadros[2:4], "cansado": cuadros[4:6]}
        # Con menos cuadros se usan los mismos para todo
        return {"flotar": cuadros, "atacar": cuadros, "cansado": cuadros}

    def ojo(self):
        # De donde salen las balas
        return self.x + 60, self.y + 92

    # ---------- Fases ----------

    def al_congelarse(self):
        self.proximo_disparo += MS_POR_FRAME

    def al_terminar_de_entrar(self, partida):
        self.cambiar_fase("flotar", JEFE_FLOTAR, partida.tiempo)

    def al_recibir_golpe(self, partida):
        self.cambiar_fase("flotar", JEFE_FLOTAR, partida.tiempo)

    def actualizar_fase(self, partida):
        ahora = partida.tiempo
        if self.fase == "flotar":
            # Va de lado a lado, dejando 80 px a cada costado (se acerca de a poco al punto,
            # asi no da saltos)
            centro = (ANCHO - TAMANO) / 2
            objetivo_x = centro + math.sin(ahora / 700) * (centro - 80)
            self.x += (objetivo_x - self.x) * 0.05
            if ahora > self.fase_hasta:
                self.ataque = "anillo" if self.ataque == "abanico" else "abanico"
                self.rafagas = JEFE_RAFAGAS
                self.proximo_disparo = ahora + 700      # antes de disparar se carga
                self.cambiar_fase("atacar", 0, ahora)

        elif self.fase == "atacar":
            ojo_x, ojo_y = self.ojo()
            if self.cargando() and random.random() < 0.6:
                # Cargando: chispas que se juntan en el ojo
                chispa_x = ojo_x + random.randint(-40, 40)
                chispa_y = ojo_y + random.randint(-30, 30)
                partida.efectos.particula(chispa_x, chispa_y, (ojo_x - chispa_x) * 0.1, (ojo_y - chispa_y) * 0.1,
                                          EMBESTIDA, 12, 2)
            if ahora >= self.proximo_disparo:
                if self.rafagas > 0:
                    self.disparar(partida)
                    self.rafagas -= 1
                    self.proximo_disparo = ahora + 450
                else:
                    # Despues de atacar queda cansado: se le abren las placas
                    self.cambiar_fase("cansado", JEFE_CANSADO, ahora)
                    nucleo_x, nucleo_y = self.centro_nucleo()
                    partida.efectos.explosion(nucleo_x, nucleo_y, ORO, 20, 4, 3)

        elif self.fase == "cansado":
            if random.random() < 0.2:
                nucleo_x, nucleo_y = self.centro_nucleo()
                partida.efectos.particula(nucleo_x + random.randint(-20, 20), nucleo_y + random.randint(-20, 20),
                                          random.uniform(-1, 1), random.uniform(-2, 0), ORO, 12, 2)
            if ahora > self.fase_hasta:
                self.cambiar_fase("flotar", JEFE_FLOTAR, ahora)

    def cargando(self):
        # Los 0.7 s antes de la primera rafaga
        return self.fase == "atacar" and self.rafagas == JEFE_RAFAGAS

    # ---------- Ataque ----------

    def direcciones_ataque(self, partida):
        # Angulos (en radianes) y rapidez de las balas de la proxima rafaga.
        # Las usan el disparo y el aviso, asi el aviso muestra justo lo que va a salir
        ojo_x, ojo_y = self.ojo()
        rapidez = min(3 + partida.jefes_vencidos * 0.3, 4.5) * partida.reglas["velocidad"]
        direcciones = []
        if self.ataque == "abanico":
            # Hacia la nave, abierto como un abanico
            cantidad = min(5 + partida.jefes_vencidos, 9)
            nave_x, nave_y = partida.nave.centro()
            hacia_nave = math.atan2(nave_y - ojo_y, nave_x - ojo_x)
            for i in range(cantidad):
                direcciones.append(hacia_nave + math.radians((i - (cantidad - 1) / 2) * 14))
        else:
            # Hacia todos lados, un poco mas lento (pocas balas: los huecos se tienen que ver)
            cantidad = min(12 + partida.jefes_vencidos // 5 * 2, 18)
            giro = self.rafagas * math.pi / cantidad    # cada rafaga sale girada: los huecos cambian
            for i in range(cantidad):
                direcciones.append(2 * math.pi * i / cantidad + giro)
            rapidez *= 0.8
        return direcciones, rapidez

    def disparar(self, partida):
        ojo_x, ojo_y = self.ojo()
        direcciones, rapidez = self.direcciones_ataque(partida)
        for direccion in direcciones:
            partida.balas.append(Bala(ojo_x, ojo_y, math.cos(direccion) * rapidez, math.sin(direccion) * rapidez))
        partida.efectos.anillo(ojo_x, ojo_y, EMBESTIDA, 10, 3, 2)

    # ---------- Dibujo ----------

    def animacion(self):
        if self.fase == "atacar":
            return "atacar"
        if self.fase in ("cansado", "morir"):
            return "cansado"
        return "flotar"

    def dibujar_extra(self, pantalla, partida):
        # Mientras se carga, muestra por donde van a salir las balas (se apaga en Opciones)
        if partida.opciones.aviso_jefe and self.cargando() and not self.congelado(partida):
            self.dibujar_aviso_ataque(pantalla, partida)

    def dibujar_aviso_ataque(self, pantalla, partida):
        # Abanico: lineas punteadas rojas hacia la nave (como el embestidor).
        # Anillo: rayitas magenta cortas alrededor del ojo, en la direccion de cada bala
        if not dibujo.parpadeo(100):
            return
        ojo_x, ojo_y = self.ojo()
        direcciones = self.direcciones_ataque(partida)[0]
        if self.ataque == "abanico":
            color, desde, hasta, separacion = ROJO, 24, 160, 16
        else:
            color, desde, hasta, separacion = MAGENTA, 20, 44, 8
        for direccion in direcciones:
            for paso in range(desde, hasta + 1, separacion):
                punto_x = ojo_x + math.cos(direccion) * paso
                punto_y = ojo_y + math.sin(direccion) * paso
                pantalla.fill(color, (int(punto_x) // 2 * 2, int(punto_y) // 2 * 2, 4, 4))
