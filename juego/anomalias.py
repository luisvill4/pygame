"""
Anomalias: una vez por sector, el espacio se pone raro por un rato.

Como los enemigos y los jefes, usan un registro (@registrar_anomalia) y una clase base
con "ganchos" que cada anomalia completa a su manera (patron Template Method):

    actualizar(partida)         en cada paso (lanzar asteroides, prender llamaradas...)
    terminar(partida)           al irse (o si llega el jefe antes)
    dibujar(pantalla, partida)  lo que se ve encima del juego (avisos, niebla)
    multiplicador_monedas()     para las que cambian las reglas (la fiebre del oro)
    factor_combo()

Las que atacan siguen la filosofia de los jefes: siempre AVISAN antes (una columna
punteada, una franja que parpadea) y atacan a ritmo, nunca de sorpresa.

- asteroides: caen asteroides; antes, una columna punteada marca por donde. El dash los rompe.
- tormenta:   llamaradas solares en franjas (horizontales o verticales) que avisan y queman.
- niebla:     solo se ve cerca de la nave; los enemigos son ojos en la oscuridad.
- oro:        fiebre del oro: las monedas valen el doble y el combo dura mas.

El director (progresion.py) decide cuando llega cada una y cual.
"""
import random

import pygame

from juego import dibujo
from juego.config import (ANCHO, ALTO, BLANCO, AMARILLO, ROJO, ORO, FUEGO, ANOMALIA_DURACION,
                          ASTEROIDES_ESPERA, ASTEROIDES_AVISO, ASTEROIDES_VELOCIDAD,
                          TORMENTA_AVISO, TORMENTA_LLAMARADA, TORMENTA_CALMA, TORMENTA_ANCHO,
                          NIEBLA_RADIO, ORO_MULTIPLICADOR, ORO_COMBO)
from juego.proyectiles import Meteoro

TIPOS_ANOMALIA = {}         # nombre -> clase


def registrar_anomalia(clase):
    TIPOS_ANOMALIA[clase.tipo] = clase
    return clase


def crear_anomalia(tipo, partida):
    return TIPOS_ANOMALIA[tipo](partida)


class Anomalia:
    tipo = None
    nombre = ""             # el cartel grande al llegar
    pista = ""              # el consejo debajo del nombre
    color = BLANCO

    def __init__(self, partida):
        self.desde = partida.tiempo
        self.hasta = partida.tiempo + ANOMALIA_DURACION

    def restante(self, partida):
        return max(0, self.hasta - partida.tiempo)

    def termino(self, partida):
        return partida.tiempo >= self.hasta

    # ---------- Ganchos (cada anomalia usa los que necesita) ----------

    def actualizar(self, partida):
        pass

    def terminar(self, partida):
        pass

    def dibujar(self, pantalla, partida):
        pass

    def multiplicador_monedas(self):
        return 1

    def factor_combo(self):
        return 1


@registrar_anomalia
class LluviaDeAsteroides(Anomalia):
    # A ritmo: aparece una columna de aviso y, al rato, cae un asteroide justo por ahi
    tipo = "asteroides"
    nombre = "LLUVIA DE ASTEROIDES"
    pista = "MIRA LAS COLUMNAS. EL DASH LOS ROMPE"
    color = (150, 160, 210)

    def __init__(self, partida):
        super().__init__(partida)
        self.avisos = []                    # [x, momento en que cae]
        self.proximo = partida.tiempo + 1500    # el primero, cuando se va el cartel

    def actualizar(self, partida):
        ahora = partida.tiempo
        # Los ultimos asteroides se avisan antes de que termine (asi no queda ninguno a medias)
        if ahora >= self.proximo and ahora < self.hasta - ASTEROIDES_AVISO:
            self.proximo = ahora + ASTEROIDES_ESPERA
            self.avisos.append([self.elegir_x(partida), ahora + ASTEROIDES_AVISO])
            partida.sonidos.reproducir("meteoro_aviso", self.avisos[-1][0])
        for aviso in self.avisos[:]:
            if ahora >= aviso[1]:
                self.avisos.remove(aviso)
                rapidez = ASTEROIDES_VELOCIDAD * partida.reglas["velocidad"]
                partida.balas.append(Meteoro(aviso[0], -20, 0, rapidez))

    def elegir_x(self, partida):
        # A veces cae cerca de la nave (para que haya que moverse); si no, en cualquier lado
        if random.random() < 0.4:
            nave_x, _ = partida.nave.centro()
            x = nave_x + random.randint(-60, 60)
        else:
            x = random.randint(20, ANCHO - 20)
        return max(20, min(x, ANCHO - 20))

    def terminar(self, partida):
        self.avisos.clear()

    def dibujar(self, pantalla, partida):
        # Columna punteada por donde va a caer; parpadea mas rapido cuando esta por caer
        for x, cae_en in self.avisos:
            falta = cae_en - partida.tiempo
            if not dibujo.parpadeo(60 if falta < 300 else 120):
                continue
            columna_x = int(x) // 2 * 2 - 2
            for punto_y in range(0, ALTO, 24):
                pantalla.fill(ROJO, (columna_x, punto_y, 4, 10))


@registrar_anomalia
class TormentaSolar(Anomalia):
    # Fases: calma -> aviso (la franja parpadea) -> llamarada (quema) -> calma...
    tipo = "tormenta"
    nombre = "TORMENTA SOLAR"
    pista = "SALI DE LAS FRANJAS QUE PARPADEAN"
    color = (255, 140, 0)

    def __init__(self, partida):
        super().__init__(partida)
        self.fase = "calma"
        self.fase_hasta = partida.tiempo + 1500
        self.franja = None              # el rectangulo que avisa y despues quema

    def actualizar(self, partida):
        ahora = partida.tiempo
        if self.fase == "llamarada":
            self.quemar(partida)
        if ahora < self.fase_hasta:
            return
        if self.fase == "calma":
            if ahora + TORMENTA_AVISO + TORMENTA_LLAMARADA > self.hasta:
                return              # ya no alcanza para otra llamarada entera
            self.franja = self.elegir_franja(partida)
            self.fase, self.fase_hasta = "aviso", ahora + TORMENTA_AVISO
            partida.sonidos.reproducir("tormenta_aviso", self.franja.centerx)
        elif self.fase == "aviso":
            self.fase, self.fase_hasta = "llamarada", ahora + TORMENTA_LLAMARADA
            partida.efectos.sacudir(8, self.color)
            partida.sonidos.reproducir("llamarada", self.franja.centerx)
            for _ in range(24):
                partida.efectos.particula(random.uniform(self.franja.left, self.franja.right),
                                          random.uniform(self.franja.top, self.franja.bottom),
                                          random.uniform(-2, 2), random.uniform(-2, 2), FUEGO, 30, 6)
        else:
            self.fase, self.fase_hasta = "calma", ahora + TORMENTA_CALMA

    def elegir_franja(self, partida):
        # Vertical u horizontal, pasando cerca de la nave (hay que moverse)
        nave_x, nave_y = partida.nave.centro()
        corrimiento = random.randint(-40, 40)
        if random.random() < 0.5:
            x = max(0, min(nave_x + corrimiento - TORMENTA_ANCHO // 2, ANCHO - TORMENTA_ANCHO))
            return pygame.Rect(int(x), 0, TORMENTA_ANCHO, ALTO)
        y = max(0, min(nave_y + corrimiento - TORMENTA_ANCHO // 2, ALTO - TORMENTA_ANCHO))
        return pygame.Rect(0, int(y), ANCHO, TORMENTA_ANCHO)

    def quemar(self, partida):
        nave = partida.nave
        if nave.atraviesa(partida.tiempo) or not nave.toca_rect(self.franja):
            return
        # El golpe "viene" del medio de la franja: el empujon te saca hacia afuera
        nave_x, nave_y = nave.centro()
        if self.vertical():
            partida.danar_jugador(self.franja.centerx, nave_y)
        else:
            partida.danar_jugador(nave_x, self.franja.centery)

    def vertical(self):
        return self.franja.height == ALTO

    def dibujar(self, pantalla, partida):
        if self.fase == "aviso" and dibujo.parpadeo(60 if self.fase_hasta - partida.tiempo < 300 else 120):
            # Los dos bordes de la franja, punteados
            franja = self.franja
            for paso in range(0, max(franja.width, franja.height), 24):
                if self.vertical():
                    pantalla.fill(self.color, (franja.left, paso, 4, 12))
                    pantalla.fill(self.color, (franja.right - 4, paso, 4, 12))
                else:
                    pantalla.fill(self.color, (paso, franja.top, 12, 4))
                    pantalla.fill(self.color, (paso, franja.bottom - 4, 12, 4))
        elif self.fase == "llamarada":
            # Capas de fuego: naranja, amarillo y un nucleo blanco que titila
            for achicar, color in ((0, ROJO), (20, self.color), (44, AMARILLO), (64, BLANCO)):
                if self.vertical():
                    capa = self.franja.inflate(-achicar, 0)
                else:
                    capa = self.franja.inflate(0, -achicar)
                if color is not BLANCO or dibujo.parpadeo(60):
                    pantalla.fill(color, capa)


BANDAS_NIEBLA = (200, 160, 115, 70, 30)    # transparencia del borde de la niebla, de afuera hacia adentro
ANCHO_BANDA_NIEBLA = 10                     # px de cada banda


@registrar_anomalia
class Niebla(Anomalia):
    # Solo se ve cerca de la nave. De los enemigos lejanos se ven solo los ojos,
    # y la moneda y los power-ups brillan a traves de la niebla
    tipo = "niebla"
    nombre = "NIEBLA CERRADA"
    pista = "LOS OJOS TE DICEN DONDE ESTAN"
    color = (120, 220, 170)

    def radio(self, partida):
        # Se cierra de a poco al llegar y se abre al irse (1.5 s)
        cerca_del_borde = min(partida.tiempo - self.desde, self.hasta - partida.tiempo) / 1500
        return NIEBLA_RADIO + (1 - max(0, min(1, cerca_del_borde))) * 700

    def dibujar(self, pantalla, partida):
        radio = self.radio(partida)
        nave_x, nave_y = partida.nave.centro()
        # Se dibuja a la mitad del tamaño y se agranda x2: bordes en escalones de 2 px (la
        # cuadricula del juego). El borde del agujero se desvanece en BANDAS_NIEBLA bandas
        chica = pygame.Surface((ANCHO // 2 + 1, ALTO // 2), pygame.SRCALPHA)
        # Bruma del color del sector (un poco mas clara que el espacio: se nota que es niebla)
        sector = partida.director.sector
        r, g, b = (fondo + color // 7 for fondo, color in zip(sector["fondo"], sector["color"]))
        chica.fill((r, g, b, 235))
        centro = (int(nave_x) // 2, int(nave_y) // 2)
        for i, alfa in enumerate(BANDAS_NIEBLA):
            borde = (len(BANDAS_NIEBLA) - i) * ANCHO_BANDA_NIEBLA
            pygame.draw.circle(chica, (r, g, b, alfa), centro, int(radio + borde) // 2)
        pygame.draw.circle(chica, (r, g, b, 0), centro, int(radio) // 2)
        pantalla.blit(pygame.transform.scale(chica, (chica.get_width() * 2, ALTO)), (0, 0))
        self.dibujar_lo_que_brilla(pantalla, partida, radio)

    def dibujar_lo_que_brilla(self, pantalla, partida, radio):
        nave_x, nave_y = partida.nave.centro()

        def lejos(x, y):
            return (x - nave_x) ** 2 + (y - nave_y) ** 2 > radio ** 2

        for enemigo in partida.enemigos:
            centro_x, centro_y = enemigo.centro()
            if not enemigo.activo(partida.tiempo) or not lejos(centro_x, centro_y):
                continue
            # Dos ojos de su color (que parpadean cada tanto, cada uno a su ritmo)
            if (pygame.time.get_ticks() + enemigo.desfase * 3) % 2500 < 150:
                continue
            ojo_x, ojo_y = int(centro_x) // 2 * 2, int(centro_y) // 2 * 2 - 4
            separacion = max(4, enemigo.tamano // 6)
            pantalla.fill(enemigo.color, (ojo_x - separacion - 2, ojo_y, 4, 4))
            pantalla.fill(enemigo.color, (ojo_x + separacion - 2, ojo_y, 4, 4))
        moneda_x, moneda_y = partida.moneda.centro()
        if lejos(moneda_x, moneda_y) and dibujo.parpadeo(200):
            self.destello(pantalla, moneda_x, moneda_y, AMARILLO)
        capsula = partida.capsula
        if capsula is not None and lejos(capsula.x, capsula.y) and dibujo.parpadeo(200):
            self.destello(pantalla, capsula.x, capsula.y, capsula.powerup.color)

    def destello(self, pantalla, x, y, color):
        # Una estrellita de 4 puntas
        x, y = int(x) // 2 * 2, int(y) // 2 * 2
        pantalla.fill(color, (x - 6, y - 2, 12, 4))
        pantalla.fill(color, (x - 2, y - 6, 4, 12))
        pantalla.fill(BLANCO, (x - 2, y - 2, 4, 4))


@registrar_anomalia
class FiebreDelOro(Anomalia):
    # La anomalia buena: llueve oro, las monedas valen el doble y el combo dura mas
    tipo = "oro"
    nombre = "FIEBRE DEL ORO"
    pista = "MONEDAS x2 Y EL COMBO DURA MAS"
    color = AMARILLO

    def actualizar(self, partida):
        # Polvo dorado que cae por toda la pantalla
        if random.random() < 0.5:
            partida.efectos.particula(random.randint(0, ANCHO), random.randint(0, ALTO),
                                      0, 0.6, ORO, 40, 2)

    def multiplicador_monedas(self):
        return ORO_MULTIPLICADOR

    def factor_combo(self):
        return ORO_COMBO
