"""
Clase base de los jefes y su registro.

Todo jefe tiene fases (self.fase). La clase base resuelve las comunes:
    entrar  -> baja desde arriba hasta y_final con el cartel "¡CUIDADO!"
    morir   -> explosiones por todo el cuerpo durante 2 s y despues la grande
y ademas: la vida, el destello al recibir un golpe, el congelado del hielo, el
cartel "¡DASH!" cuando se le puede pegar, las variantes de sus sprites y las
PARTES (piezas que se rompen por separado, ver jefes/partes.py).

El tamaño de cada jefe va en 'ancho' y 'alto' (el Ojo es de 120x120).

Cada jefe (una subclase) define el resto de sus fases en actualizar_fase().
Para agregar un jefe nuevo:
    1. Crear jefes/mi_jefe.py con una clase que herede de Jefe y @registrar_jefe.
    2. Darle un 'tipo' y escribir: cargar_animaciones(), al_terminar_de_entrar(),
       actualizar_fase() y animacion(). Si ataca de otra forma, tambien
       caja_cuerpo(), caja_nucleo() y puede_recibir_golpe(). Si tiene partes, las
       agrega a self.partes y escribe al_golpear_parte() y al_romper_parte().
    3. Importarlo en jefes/__init__.py y agregarlo a ORDEN_JEFES (config.py).
"""
import math
import random

import pygame

from juego import recursos, dibujo, lienzo
from juego.proyectiles import romper_balas
from juego.config import (ROJO, CIAN, ORO, FUEGO, ENERGIA, ARCOIRIS, BLANCO, HIELO, EMBESTIDA,
                          MS_POR_FRAME, MS_CUADRO_JEFE, JEFE_VIDA)

TAMANO = 120                # tamaño del Ojo (y de los jefes que no digan otro)

TIPOS_JEFE = {}             # nombre -> clase


def registrar_jefe(clase):
    if not clase.tipo:
        raise ValueError(clase.__name__ + " necesita un 'tipo'")
    TIPOS_JEFE[clase.tipo] = clase
    return clase


def crear_jefe(tipo, partida):
    if tipo not in TIPOS_JEFE:
        raise ValueError("No existe el jefe '" + tipo + "'. Hay: " + ", ".join(TIPOS_JEFE))
    return TIPOS_JEFE[tipo](partida)


_animaciones = {}       # tipo -> {animacion: [cuadros]}
_congeladas = {}
_blancas = {}


class Jefe:
    tipo = None
    ancho = TAMANO
    alto = TAMANO
    y_final = 70                # altura a la que baja al entrar
    fases_congelables = ("flotar", "atacar", "cansado")    # el hielo no lo congela al entrar ni al morir

    def __init__(self, partida):
        self.x = (lienzo.ancho - self.ancho) // 2   # esquina de arriba a la izquierda del sprite,
        self.y = -self.alto - 10                    # centrado y arriba de la pantalla
        self.fase = "entrar"
        self.fase_hasta = 0                 # momento en que termina la fase actual
        self.vida_max = JEFE_VIDA + partida.jefes_vencidos
        self.vida = self.vida_max
        self.golpe_hasta = 0                # destello blanco despues de recibir un golpe
        self.partes = []                    # piezas que se rompen por separado (ver partes.py)

    # ---------- Sprites ----------

    @classmethod
    def cargar_animaciones(cls):
        # Para las subclases: {"nombre de la animacion": [cuadros de 120x120]}
        raise NotImplementedError

    @classmethod
    def animaciones(cls):
        if cls.tipo not in _animaciones:
            normales = cls.cargar_animaciones()
            _animaciones[cls.tipo] = normales
            # Variantes sin sprites nuevos: congelado (hielo) y blanco (al recibir un golpe)
            _congeladas[cls.tipo] = {nombre: [recursos.tenir(c, HIELO) for c in cuadros]
                                     for nombre, cuadros in normales.items()}
            _blancas[cls.tipo] = {nombre: [recursos.blanquear(c) for c in cuadros]
                                  for nombre, cuadros in normales.items()}
        return _animaciones[cls.tipo]

    # ---------- Consultas ----------

    def centro(self):
        return self.x + self.ancho / 2, self.y + self.alto / 2

    def centro_nucleo(self):
        return self.x + 60, self.y + 50

    def caja_cuerpo(self):
        # Un poco mas chica que el dibujo, para no ser injusta
        return pygame.Rect(self.x + 14, self.y + 16, 92, 76)

    def caja_nucleo(self):
        return pygame.Rect(self.x + 40, self.y + 30, 40, 40)

    def cajas_danio(self):
        # Todo lo que hace daño al tocarlo: el cuerpo y las partes que quedan
        return [self.caja_cuerpo()] + [parte.caja(self) for parte in self.partes_vivas()]

    def puede_recibir_golpe(self):
        # Por defecto: con el dash contra el nucleo mientras esta cansado
        return self.fase == "cansado"

    def vida_barra(self):
        # (vida, vida maxima) para la barra del HUD. Los jefes con partes suman las de ellas
        return self.vida, self.vida_max

    def partes_vivas(self):
        return [parte for parte in self.partes if parte.viva()]

    def parte_golpeable(self, caja):
        # La parte que se puede golpear y toca la caja (la de la nave en dash), o None
        if self.fase not in self.fases_congelables:
            return None
        for parte in self.partes_vivas():
            if parte.golpeable(self) and caja.colliderect(parte.caja(self)):
                return parte
        return None

    def muriendo(self):
        return self.fase == "morir"

    def temblando(self):
        # Se dibuja temblando (al morir; algunos jefes tambien en otras fases)
        return self.fase == "morir"

    def congelado(self, partida):
        return partida.activo("hielo") and self.fase in self.fases_congelables

    def cambiar_fase(self, fase, duracion, tiempo):
        self.fase = fase
        self.fase_hasta = tiempo + duracion

    # ---------- Cada frame ----------

    def actualizar(self, partida):
        if self.congelado(partida):
            # Congelado no se mueve ni ataca, y su fase no avanza
            self.fase_hasta += MS_POR_FRAME
            self.al_congelarse()
            return
        if self.fase == "entrar":
            self.y += 1.2
            if self.y >= self.y_final:
                self.y = self.y_final
                self.al_terminar_de_entrar(partida)
        elif self.fase == "morir":
            # Explosiones por todo el cuerpo y despues la grande
            if random.random() < 0.35:
                partida.efectos.explosion(self.x + random.randint(10, self.ancho - 10),
                                          self.y + random.randint(10, self.alto - 20), FUEGO, 12, 4, 4)
                partida.efectos.sacudir(3)
            if partida.tiempo > self.fase_hasta:
                partida.jefe_vencido()
        else:
            self.actualizar_fase(partida)

    def al_congelarse(self):
        # Para las subclases: correr sus propios temporizadores mientras esta congelado
        pass

    def al_terminar_de_entrar(self, partida):
        raise NotImplementedError

    def actualizar_fase(self, partida):
        # Para las subclases: todas las fases que no son entrar ni morir
        raise NotImplementedError

    def recibir_golpe(self, partida):
        # Le quita una vida; con 0 empieza a morir
        efectos = partida.efectos
        nucleo_x, nucleo_y = self.centro_nucleo()
        self.vida -= 1
        self.golpe_hasta = partida.tiempo + 300
        partida.sonidos.reproducir("golpe")
        efectos.explosion(nucleo_x, nucleo_y, ORO, 40, 8, 5)
        efectos.anillo(nucleo_x, nucleo_y, ENERGIA, 24, 6)
        efectos.sacudir(12, BLANCO)
        partida.entrada.vibrar(0.5, 0.8, 200)
        partida.congelar_frames = 6
        if self.vida <= 0:
            romper_balas(partida.balas, efectos, EMBESTIDA)
            self.cambiar_fase("morir", 2000, partida.tiempo)
        else:
            efectos.texto_flotante("¡GOLPE!", nucleo_x, nucleo_y - 50, CIAN)
            self.al_recibir_golpe(partida)

    def al_recibir_golpe(self, partida):
        # Para las subclases: que hace despues de un golpe que no lo mata
        pass

    def golpear_parte(self, partida, parte):
        # Le quita una vida a una parte; con 0 se rompe (lo que pasa lo decide cada jefe)
        efectos = partida.efectos
        parte_x, parte_y = parte.centro(self)
        parte.vida -= 1
        parte.golpe_hasta = partida.tiempo + 300
        partida.sonidos.reproducir("golpe")
        efectos.explosion(parte_x, parte_y, ORO, 24, 6, 4)
        efectos.sacudir(8, BLANCO)
        partida.entrada.vibrar(0.4, 0.6, 150)
        partida.congelar_frames = 4
        if parte.viva():
            efectos.texto_flotante("¡GOLPE!", parte_x, parte_y - 40, CIAN)
            self.al_golpear_parte(partida, parte)
        else:
            efectos.explosion(parte_x, parte_y, FUEGO, 40, 8, 5)
            efectos.sacudir(16, BLANCO)
            partida.congelar_frames = 6
            self.al_romper_parte(partida, parte)

    def al_golpear_parte(self, partida, parte):
        # Para las subclases: un golpe que no la rompe
        pass

    def al_romper_parte(self, partida, parte):
        # Para las subclases: la parte se rompio
        pass

    def explotar(self, partida):
        # La gran explosion final
        centro_x, centro_y = self.centro()
        partida.efectos.explosion(centro_x, centro_y, FUEGO, 90, 11, 6)
        partida.efectos.explosion(centro_x, centro_y, ORO, 40, 7, 4)
        partida.efectos.anillo(centro_x, centro_y, ARCOIRIS, 40, 8, 4)
        partida.efectos.sacudir(35, BLANCO)
        partida.entrada.vibrar(1, 1, 600)
        partida.congelar_frames = 8
        partida.sonidos.reproducir("golpe")
        partida.sonidos.reproducir("powerup")

    # ---------- Dibujo ----------

    def animacion(self):
        # Para las subclases: que animacion mostrar segun la fase
        return next(iter(self.animaciones()))

    def dibujar(self, pantalla, partida):
        nombre = self.animacion()
        cuadros = self.animaciones()[nombre]
        indice = pygame.time.get_ticks() // MS_CUADRO_JEFE % len(cuadros)

        restante_hielo = partida.restante("hielo")
        if partida.tiempo < self.golpe_hasta and dibujo.parpadeo(60):
            imagen = _blancas[self.tipo][nombre][indice]
        elif self.congelado(partida) and (restante_hielo > 1000 or dibujo.parpadeo(100)):
            imagen = _congeladas[self.tipo][nombre][indice]
        else:
            imagen = cuadros[indice]

        # Flota de a 2 pixeles; al morir tiembla
        dibujo_x, dibujo_y = int(self.x), int(self.y)
        if self.temblando():
            dibujo_x += random.randint(-2, 2) * 2
            dibujo_y += random.randint(-2, 2) * 2
        elif self.fase != "entrar" and not self.congelado(partida):
            dibujo_y += round(math.sin(pygame.time.get_ticks() / 300)) * 2
        pantalla.blit(imagen, (dibujo_x, dibujo_y))
        # Las partes van encima, movidas igual que el cuerpo
        for parte in self.partes:
            parte.dibujar(pantalla, dibujo_x + parte.dx, dibujo_y + parte.dy, self, partida)

        self.dibujar_extra(pantalla, partida)

        # Avisos: al entrar y cuando se le puede pegar (al nucleo o a una parte)
        if self.fase == "entrar" and dibujo.parpadeo(200):
            dibujo.texto_3d(pantalla, "¡CUIDADO!", dibujo.GRANDE, ROJO, (110, 0, 30), 330, 4)
        if dibujo.parpadeo(200):
            if self.puede_recibir_golpe():
                nucleo_x = self.centro_nucleo()[0]
                dibujo.texto(pantalla, "¡DASH!", dibujo.CHICA, CIAN, int(nucleo_x), int(self.y) + self.alto + 12)
            if self.fase in self.fases_congelables:
                self.dibujar_avisos_partes(pantalla)

    def dibujar_avisos_partes(self, pantalla):
        # Una flechita debajo de cada parte golpeable y un solo "¡DASH!" entre todas
        # (con un cartel por parte, los de partes vecinas se pisaban)
        golpeables = [parte for parte in self.partes_vivas() if parte.golpeable(self)]
        if not golpeables:
            return
        for parte in golpeables:
            flecha_x = int(parte.centro(self)[0]) // 2 * 2
            flecha_y = int(self.y) + parte.dy + parte.alto + 4
            for fila, ancho in enumerate((4, 12, 20)):
                pantalla.fill(CIAN, (flecha_x - ancho // 2, flecha_y + fila * 4, ancho, 4))
        medio_x = sum(parte.centro(self)[0] for parte in golpeables) / len(golpeables)
        abajo = max(parte.dy + parte.alto for parte in golpeables)
        dibujo.texto(pantalla, "¡DASH!", dibujo.CHICA, CIAN, int(medio_x), int(self.y) + abajo + 30)

    def dibujar_extra(self, pantalla, partida):
        # Para las subclases: avisos propios (ej: hacia donde va a disparar)
        pass
