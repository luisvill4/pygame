"""
La Colmena: una madre que defiende a sus hijas. Un panal vivo (160x160) con el ojo de
la reina en el centro y 4 compuertas por donde salen las abejas.

Primera parte, con compuertas (un compas por compuerta):
    flotar (4 pulsos)    se pasea por arriba goteando miel
    abrir (2)            una compuerta tiembla y zumba: "BZZZ..."
    soltar (3)           sale una abeja por pulso (ver enemigos/abeja.py)
    expuesta (5)         la compuerta queda ABIERTA: ¡rompela con el dash! (mientras sus
                         hijas te persiguen). Si se la rompes, todas se enojan y pican ya
Con 2 compuertas o menos, abre todas las que le quedan a la vez.

Segunda parte, sin compuertas: llama a sus hijas a casa (vuelven sin hacer daño: asi
hay una sola cosa que esquivar), se enfurece y EMBISTE como una bola de billar.
    temblar (3 pulsos)   te apunta; el aviso dibuja el camino CON LOS REBOTES (en el
                         ultimo pulso queda fijo: ¡salí del camino!)
    embestir             cruza la pantalla rebotando en las paredes y en el ultimo choque...
    aturdida (5)         ...queda mareada con el ojo de la reina a la vista: ¡DASH!
    volver (3)           vuelve arriba. Cada golpe al ojo le suma un rebote
El aviso usa la misma cuenta que el movimiento (paso_embestida), asi muestra justo lo que va a pasar.

Sprites (opcionales):
    colmena.png           960x160: 6 cuadros de 160x160 de a pares (calma, furia, aturdida)
    colmena_compuerta.png 64x32:   2 cuadros de 32x32 (cerrada, abierta)
Si faltan, se dibujan de respaldo.
"""
import math
import random

import pygame

from juego import recursos, dibujo, lienzo
from juego.config import (ALTO, AMARILLO, BLANCO, ROJO, HIELO, ORO, JEFE_VIDA, COLMENA_PULSO, COLMENA_ABEJAS,
                          COLMENA_ABEJAS_MAX, COLMENA_EXPUESTA, COLMENA_EMBESTIDA, COLMENA_REBOTES,
                          COLMENA_ATURDIDA)
from juego.enemigos import crear_enemigo
from juego.jefes.base import Jefe, registrar_jefe
from juego.jefes.partes import Parte

LADO = 160
LADO_COMPUERTA = 32
AMBAR = (200, 130, 0)
AMBAR_OSCURO = (150, 90, 0)
CERA = (90, 50, 0)
MIEL = [CERA, AMBAR, AMARILLO]
PEDAZOS = [(60, 30, 0), CERA, AMBAR, AMARILLO]

# Las 4 compuertas en los lados del hexagono: (x, y de la esquina dentro de la Colmena,
# angulo hacia donde salen las abejas)
COMPUERTAS = [(4, 30, math.radians(210)), (124, 30, math.radians(330)),
              (4, 98, math.radians(150)), (124, 98, math.radians(30))]


# ================================== #
# ======= DIBUJOS DE RESPALDO ====== #
# ================================== #

def hexagono(centro_x, centro_y, radio):
    return [(centro_x + math.cos(math.pi / 3 * i) * radio, centro_y + math.sin(math.pi / 3 * i) * radio)
            for i in range(6)]


def colmena_respaldo(animo, cuadro):
    # Se dibuja a la mitad (80x80) y se agranda x2. animo: "calma", "furia" o "aturdida"
    imagen = pygame.Surface((LADO // 2, LADO // 2), pygame.SRCALPHA)
    cuerpo = hexagono(40, 41, 38)
    pygame.draw.polygon(imagen, AMBAR, cuerpo)
    # Celdas del panal
    for celda_x, celda_y in ((22, 22), (58, 22), (14, 40), (66, 40), (22, 58), (58, 58), (40, 66), (40, 16)):
        pygame.draw.polygon(imagen, AMBAR_OSCURO, hexagono(celda_x, celda_y, 6), 1)
    pygame.draw.polygon(imagen, CERA, cuerpo, 2)
    # Antenas
    for base_x, punta_x in ((34, 30), (46, 50)):
        pygame.draw.line(imagen, CERA, (base_x, 7), (punta_x, 1))
        imagen.fill(AMARILLO if cuadro == 0 else BLANCO, (punta_x - 1, 0, 2, 2))
    # Gotas de miel abajo
    for gota_x in (30, 50):
        largo = 3 if (cuadro + gota_x // 10) % 2 else 5
        imagen.fill(AMBAR, (gota_x, 74, 2, largo))
    # El ojo de la reina
    pygame.draw.ellipse(imagen, CERA, (27, 32, 26, 20))
    pygame.draw.ellipse(imagen, (255, 240, 200), (29, 34, 22, 16))
    if animo == "aturdida":
        pygame.draw.ellipse(imagen, BLANCO, (29, 34, 22, 16))
        for paso in range(8):                       # espiral: esta mareada
            angulo = paso * 0.9 + cuadro * 0.5
            imagen.fill(ORO[0], (40 + round(math.cos(angulo) * paso * 0.9), 42 + round(math.sin(angulo) * paso * 0.7),
                                 1, 1))
    else:
        iris = ROJO if animo == "furia" else AMARILLO
        pygame.draw.circle(imagen, iris, (40, 42), 5)
        pygame.draw.circle(imagen, (30, 10, 0), (40, 42), 2)
        imagen.fill(BLANCO, (37, 39, 2, 2))
        if animo == "calma":
            imagen.fill(AMBAR_OSCURO, (28, 33, 24, 4))     # parpado a medio cerrar
        else:
            pygame.draw.line(imagen, CERA, (27, 28), (37, 33), 2)     # cejas enojadas
            pygame.draw.line(imagen, CERA, (53, 28), (43, 33), 2)
    return pygame.transform.scale(imagen, (LADO, LADO))


def compuerta_respaldo(abierta):
    imagen = pygame.Surface((LADO_COMPUERTA // 2, LADO_COMPUERTA // 2), pygame.SRCALPHA)
    forma = hexagono(8, 8, 7)
    if abierta:
        pygame.draw.polygon(imagen, (30, 10, 0), forma)
        pygame.draw.polygon(imagen, (255, 140, 0), forma, 1)
        imagen.fill(AMARILLO, (6, 6, 1, 1))         # ojitos de abejas en la oscuridad
        imagen.fill(AMARILLO, (9, 9, 1, 1))
    else:
        pygame.draw.polygon(imagen, AMBAR_OSCURO, forma)
        pygame.draw.polygon(imagen, CERA, forma, 1)
        imagen.fill(CERA, (3, 7, 10, 1))
        imagen.fill(CERA, (7, 3, 1, 10))
    return pygame.transform.scale(imagen, (LADO_COMPUERTA, LADO_COMPUERTA))


_cuadros_compuerta = {}


def cuadros_compuerta(variante):
    if not _cuadros_compuerta:
        normales = recursos.hoja("colmena_compuerta.png", LADO_COMPUERTA)
        if normales is None or len(normales) < 2:
            normales = [compuerta_respaldo(False), compuerta_respaldo(True)]
        _cuadros_compuerta["normal"] = normales
        _cuadros_compuerta["hielo"] = [recursos.tenir(c, HIELO) for c in normales]
        _cuadros_compuerta["blanco"] = [recursos.blanquear(c) for c in normales]
    return _cuadros_compuerta[variante]


# ================================== #
# =========== COMPUERTA ============ #
# ================================== #

class Compuerta(Parte):
    def __init__(self, dx, dy, angulo):
        super().__init__(dx, dy, LADO_COMPUERTA, LADO_COMPUERTA, 1)
        self.angulo = angulo        # hacia donde salen las abejas
        self.abierta = False

    def golpeable(self, jefe):
        return self.abierta

    def salida(self, jefe):
        # Un poco afuera de la compuerta, para que las abejas no nazcan dentro de la Colmena
        centro_x, centro_y = self.centro(jefe)
        return centro_x + math.cos(self.angulo) * 24, centro_y + math.sin(self.angulo) * 24

    def dibujar(self, pantalla, x, y, jefe, partida):
        if not self.viva():
            # Rota: un agujero que gotea
            pantalla.fill((40, 20, 0), (x + 6, y + 6, 20, 20))
            pantalla.fill(AMBAR, (x + 14, y + 26, 4, 4 if dibujo.parpadeo(400) else 6))
            return
        if partida.tiempo < self.golpe_hasta and dibujo.parpadeo(60):
            variante = "blanco"
        elif jefe.congelado(partida):
            variante = "hielo"
        else:
            variante = "normal"
        por_abrir = jefe.fase == "abrir" and self in jefe.elegidas
        if por_abrir:
            x += random.randint(-1, 1) * 2         # tiembla: esta por abrirse
        pantalla.blit(cuadros_compuerta(variante)[1 if self.abierta else 0], (x, y))
        if (self.abierta or por_abrir) and dibujo.parpadeo(120):
            pygame.draw.rect(pantalla, AMARILLO, (x - 2, y - 2, LADO_COMPUERTA + 4, LADO_COMPUERTA + 4), 2)


# ================================== #
# ============ COLMENA ============= #
# ================================== #

@registrar_jefe
class Colmena(Jefe):
    tipo = "colmena"
    nombre = "LA COLMENA"
    apodo = "MADRE DEL ENJAMBRE"
    color = AMARILLO
    ancho = alto = LADO
    y_final = 100
    ms_pulso = COLMENA_PULSO
    fases_congelables = ("flotar", "abrir", "soltar", "expuesta", "temblar", "embestir", "aturdida", "volver")

    def __init__(self, partida):
        super().__init__(partida)
        # El ojo aguanta menos golpes que otros jefes: antes hay que romper las compuertas
        self.vida_max = self.vida = JEFE_VIDA + partida.jefes_vencidos // 2
        self.partes = [Compuerta(dx, dy, angulo) for dx, dy, angulo in COMPUERTAS]
        self.elegidas = []              # las compuertas del compas actual
        self.ultima = None
        self.direccion = 0              # hacia donde embiste
        self.vx = self.vy = 0
        self.rebotes = 0                # rebotes que le quedan a la embestida
        self.destino = (self.x, self.y_final)
        self.velocidad_dificultad = partida.reglas["velocidad"]

    @classmethod
    def cargar_animaciones(cls):
        cuadros = recursos.hoja("colmena.png", LADO)
        if cuadros is None:
            cuadros = [colmena_respaldo(animo, cuadro)
                       for animo in ("calma", "furia", "aturdida") for cuadro in (0, 1)]
        if len(cuadros) >= 6:
            return {"calma": cuadros[0:2], "furia": cuadros[2:4], "aturdida": cuadros[4:6]}
        return {"calma": cuadros, "furia": cuadros, "aturdida": cuadros}

    # ---------- Consultas ----------

    def centro_nucleo(self):
        return self.x + 80, self.y + 84

    def caja_nucleo(self):
        return pygame.Rect(int(self.x) + 52, int(self.y) + 60, 56, 48)

    def caja_cuerpo(self):
        return pygame.Rect(int(self.x) + 22, int(self.y) + 14, 116, 136)

    def cajas_danio(self):
        # El hexagono en dos cajas (alto en el medio, ancho a los costados) y las compuertas
        x, y = int(self.x), int(self.y)
        cajas = [self.caja_cuerpo(), pygame.Rect(x + 6, y + 50, 148, 66)]
        return cajas + [compuerta.caja(self) for compuerta in self.partes_vivas()]

    def puede_recibir_golpe(self):
        return self.fase == "aturdida"

    def vida_barra(self):
        return self.vida + len(self.partes_vivas()), self.vida_max + len(self.partes)

    def temblando(self):
        return self.fase in ("temblar", "enfurecerse", "morir")

    def abejas(self, partida):
        return [e for e in partida.enemigos if e.tipo == "abeja"]

    # ---------- Primera parte: las compuertas ----------

    def al_terminar_de_entrar(self, partida):
        self.cambiar_fase_pulsos("flotar", 4, partida.tiempo)

    def actualizar_fase(self, partida):
        ahora = partida.tiempo
        fase = self.fase
        self.gotear(partida)
        if fase == "flotar":
            self.pasear(ahora)
            if self.fin_de_fase(ahora):
                self.elegir_compuertas(partida)

        elif fase == "abrir":
            if self.nuevo_pulso and self.pulso == 0:
                for compuerta in self.elegidas:
                    salida_x, salida_y = compuerta.salida(self)
                    partida.efectos.texto_flotante("BZZZ", salida_x, salida_y - 20, AMARILLO)
            if self.fin_de_fase(ahora):
                for compuerta in self.elegidas:
                    compuerta.abierta = True
                self.cambiar_fase_pulsos("soltar", COLMENA_ABEJAS, ahora)

        elif fase == "soltar":
            if self.fin_de_fase(ahora):
                self.cambiar_fase_pulsos("expuesta", COLMENA_EXPUESTA, ahora)
            elif self.nuevo_pulso:
                for compuerta in self.elegidas:
                    if compuerta.viva():
                        self.soltar_abeja(partida, compuerta)

        elif fase == "expuesta":
            abiertas = [c for c in self.elegidas if c.viva() and c.abierta]
            if self.fin_de_fase(ahora) or not abiertas:
                for compuerta in self.partes:
                    compuerta.abierta = False
                if self.partes_vivas():
                    self.cambiar_fase_pulsos("flotar", 4, ahora)

        elif fase == "enfurecerse":
            self.recibir_abejas(partida)
            if self.fin_de_fase(ahora):
                self.empezar_embestida(partida)

        else:
            self.actualizar_furia(partida)

    def recibir_abejas(self, partida):
        # Las abejas que llegaron a casa entran (y se van del juego)
        for abeja in self.abejas(partida):
            if getattr(abeja, "llego", False):
                partida.efectos.explosion(abeja.x + 10, abeja.y + 10, MIEL, 6, 2, 2)
                partida.quitar_enemigo(abeja)

    def pasear(self, ahora):
        centro = (lienzo.ancho - LADO) / 2
        objetivo_x = centro + math.sin(ahora / 1600) * (centro - 30)
        objetivo_y = self.y_final + math.sin(ahora / 700) * 6
        self.x += (objetivo_x - self.x) * 0.03
        self.y += (objetivo_y - self.y) * 0.05

    def gotear(self, partida):
        if random.random() < 0.06 and self.fase not in ("embestir",):
            partida.efectos.particula(self.x + random.randint(50, 110), self.y + 150, 0, 0.3, MIEL, 45, 4,
                                      gravedad=0.12)

    def elegir_compuertas(self, partida):
        vivas = self.partes_vivas()
        if len(vivas) <= 2:
            self.elegidas = vivas                       # con pocas, abre todas
        else:
            opciones = [c for c in vivas if c is not self.ultima]
            self.elegidas = [random.choice(opciones)]
        self.ultima = self.elegidas[-1]
        self.cambiar_fase_pulsos("abrir", 2, partida.tiempo)

    def soltar_abeja(self, partida, compuerta):
        if len(self.abejas(partida)) >= COLMENA_ABEJAS_MAX:
            return
        abeja = crear_enemigo("abeja", partida)
        abeja.salir_de(partida, *compuerta.salida(self), compuerta.angulo)
        partida.enemigos.append(abeja)
        salida_x, salida_y = compuerta.salida(self)
        partida.efectos.explosion(salida_x, salida_y, MIEL, 8, 3, 2)

    def al_romper_parte(self, partida, compuerta):
        # ¡Le rompiste una compuerta!: llora miel y sus hijas se enojan
        compuerta.abierta = False
        centro_x, centro_y = compuerta.centro(self)
        partida.efectos.pedazos(centro_x, centro_y, PEDAZOS, 14, 5)
        partida.efectos.texto_flotante("¡BZZZT!", centro_x, centro_y - 30, AMARILLO)
        ganados = partida.sumar_puntos(10)
        partida.efectos.texto_flotante("+" + str(ganados), centro_x, centro_y - 6, AMARILLO)
        for abeja in self.abejas(partida):
            abeja.enojarse(partida)
        if not self.partes_vivas():
            nucleo_x, nucleo_y = self.centro_nucleo()
            partida.efectos.texto_flotante("¡A CASA, HIJAS!", nucleo_x, nucleo_y - 110, ROJO)
            for abeja in self.abejas(partida):
                abeja.volver_a_casa(nucleo_x, nucleo_y)
            partida.efectos.sacudir(16, AMARILLO)
            self.cambiar_fase_pulsos("enfurecerse", 3, partida.tiempo)

    # ---------- Segunda parte: la furia ----------

    def empezar_embestida(self, partida):
        self.rebotes = COLMENA_REBOTES + (self.vida_max - self.vida)
        self.apuntar(partida)
        self.cambiar_fase_pulsos("temblar", 3, partida.tiempo)
        for abeja in self.abejas(partida):          # por si alguna no llego a casa
            partida.quitar_enemigo(abeja)

    def apuntar(self, partida):
        nave_x, nave_y = partida.nave.centro()
        centro_x, centro_y = self.centro()
        self.direccion = math.atan2(nave_y - centro_y, nave_x - centro_x)

    def rapidez(self):
        return COLMENA_EMBESTIDA * self.velocidad_dificultad

    def paso_embestida(self, x, y, vx, vy):
        # Un paso de la embestida: devuelve la posicion y velocidad nuevas, y si reboto.
        # Lo usan el movimiento y el aviso (asi el aviso muestra justo el camino real)
        x, y = x + vx, y + vy
        reboto = False
        if x < 0 or x > lienzo.ancho - LADO:
            x = max(0, min(x, lienzo.ancho - LADO))
            vx = -vx
            reboto = True
        if y < 90 or y > ALTO - LADO:
            y = max(90, min(y, ALTO - LADO))
            vy = -vy
            reboto = True
        return x, y, vx, vy, reboto

    def camino(self):
        # Los puntos (centros) donde va a rebotar y donde va a terminar
        x, y = self.x, self.y
        vx, vy = math.cos(self.direccion) * self.rapidez(), math.sin(self.direccion) * self.rapidez()
        puntos = [(x + LADO / 2, y + LADO / 2)]
        rebotes = self.rebotes
        for _ in range(600):
            x, y, vx, vy, reboto = self.paso_embestida(x, y, vx, vy)
            if reboto:
                puntos.append((x + LADO / 2, y + LADO / 2))
                if rebotes == 0:
                    break
                rebotes -= 1
        return puntos

    def actualizar_furia(self, partida):
        ahora = partida.tiempo
        fase = self.fase
        if fase == "temblar":
            if self.pulso < 2:
                self.apuntar(partida)          # en el ultimo pulso la direccion queda fija
            if self.fin_de_fase(ahora):
                self.vx = math.cos(self.direccion) * self.rapidez()
                self.vy = math.sin(self.direccion) * self.rapidez()
                partida.efectos.texto_flotante("¡BZZZZZ!", *self.centro_nucleo(), ROJO)
                self.cambiar_fase("embestir", 10000, ahora)

        elif fase == "embestir":
            self.x, self.y, self.vx, self.vy, reboto = self.paso_embestida(self.x, self.y, self.vx, self.vy)
            if random.random() < 0.5:
                partida.efectos.particula(self.x + random.randint(40, 120), self.y + random.randint(40, 120),
                                          -self.vx * 0.2, -self.vy * 0.2, MIEL, 20, 4)
            if reboto:
                self.chocar(partida)

        elif fase == "aturdida":
            if random.random() < 0.25:
                nucleo_x, nucleo_y = self.centro_nucleo()
                partida.efectos.particula(nucleo_x + random.randint(-20, 20), nucleo_y + random.randint(-16, 16),
                                          random.uniform(-1, 1), random.uniform(-2, 0), ORO, 12, 2)
            if self.fin_de_fase(ahora):
                self.volver(partida)

        elif fase == "volver":
            destino_x, destino_y = self.destino
            self.x += (destino_x - self.x) * 0.06
            self.y += (destino_y - self.y) * 0.06
            if self.fin_de_fase(ahora):
                self.empezar_embestida(partida)

    def chocar(self, partida):
        # Contra la pared: temblor, pedazos de panal y una abeja. Si no le quedan rebotes, se marea
        centro_x, centro_y = self.centro()
        partida.efectos.pedazos(centro_x, centro_y, PEDAZOS, 8, 4)
        partida.efectos.sacudir(12, AMARILLO)
        partida.entrada.vibrar(0.5, 0.7, 150)
        partida.sonidos.reproducir("golpe")
        if self.rebotes > 0:
            self.rebotes -= 1
        else:
            self.vx = self.vy = 0
            partida.congelar_frames = 4
            self.cambiar_fase_pulsos("aturdida", COLMENA_ATURDIDA, partida.tiempo)

    def volver(self, partida):
        self.destino = ((lienzo.ancho - LADO) / 2 + random.randint(-150, 150), self.y_final)
        self.cambiar_fase_pulsos("volver", 3, partida.tiempo)

    def al_recibir_golpe(self, partida):
        self.volver(partida)

    # ---------- Dibujo ----------

    def animacion(self):
        if self.fase in ("aturdida", "morir"):
            return "aturdida"
        if not self.partes_vivas() or self.fase == "enfurecerse":
            return "furia"
        return "calma"

    def dibujar_extra(self, pantalla, partida):
        if self.congelado(partida):
            return
        if self.fase == "temblar" and dibujo.parpadeo(100 if self.pulso < 2 else 50):
            # El camino de la embestida, con los rebotes marcados
            puntos = self.camino()
            for desde, hasta in zip(puntos, puntos[1:]):
                largo = math.hypot(hasta[0] - desde[0], hasta[1] - desde[1]) or 1
                # El centro en rojo y los bordes del pasillo (lo que ocupa la Colmena) mas oscuros
                normal_x, normal_y = -(hasta[1] - desde[1]) / largo, (hasta[0] - desde[0]) / largo
                for paso in range(0, int(largo), 20):
                    punto_x = desde[0] + (hasta[0] - desde[0]) * paso / largo
                    punto_y = desde[1] + (hasta[1] - desde[1]) * paso / largo
                    pantalla.fill(ROJO, (int(punto_x) // 2 * 2, int(punto_y) // 2 * 2, 4, 4))
                    for lado in (-1, 1):
                        borde_x = punto_x + normal_x * 70 * lado
                        borde_y = punto_y + normal_y * 70 * lado
                        pantalla.fill((130, 20, 40), (int(borde_x) // 2 * 2, int(borde_y) // 2 * 2, 4, 4))
            for rebote_x, rebote_y in puntos[1:]:
                pantalla.fill(AMARILLO, (int(rebote_x) // 2 * 2 - 4, int(rebote_y) // 2 * 2 - 4, 8, 8))
        elif self.fase == "aturdida":
            nucleo_x, nucleo_y = self.centro_nucleo()
            for i in range(3):
                angulo = partida.tiempo / 200 + i * 2.1
                estrella_x = int(nucleo_x + math.cos(angulo) * 60) // 2 * 2
                estrella_y = int(self.y + 6 + math.sin(angulo) * 10) // 2 * 2
                pantalla.fill(AMARILLO, (estrella_x - 2, estrella_y - 6, 4, 12))
                pantalla.fill(AMARILLO, (estrella_x - 6, estrella_y - 2, 12, 4))
