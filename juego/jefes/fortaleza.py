"""
La Fortaleza: un acorazado gigante (256x128) con 4 cañones destruibles.

Fases:  entrar -> pelear -> descubrirse -> furia <-> cansado -> morir

- pelear: se mueve despacio de lado a lado y los cañones se turnan para atacar.
  Cada cañon: listo -> cargando -> disparando -> RECALENTADO -> listo.
  Recalentado brilla naranja y es el momento de pegarle con el dash.
  Cada cañon tiene su ataque (y una lucecita de su color para reconocerlo):
      rafaga  (rojo):     balas hacia la nave
      misiles (amarillo): misiles lentos que te siguen
      laser   (cian):     un rayo hacia abajo que barre la pantalla
      minas   (magenta):  minas que se quedan quietas y estallan en un anillo
  Con menos cañones, los que quedan atacan mas seguido (FORTALEZA_ESPERA).
- descubrirse: sin cañones, tiembla y se le cae la coraza.
- furia: el nucleo dispara en espiral y la Fortaleza se mueve rapido.
- cansado: el nucleo queda a la vista; ahi se le pega con el dash.

Los cañones son Partes (ver partes.py): la clase base ya resuelve el golpe con el dash,
el daño al tocarlos y el cartel "¡DASH!". Aca solo se decide cuando se les puede pegar
(golpeable) y que pasa al golpearlos o romperlos.

Sprites (opcionales):
    fortaleza.png       1536x128: 6 cuadros de 256x128 de a pares (coraza, furia, cansado)
    fortaleza_canon.png 64x32:    2 cuadros de 32x32 (sano, dañado), con el caño hacia abajo
Si faltan, se dibujan de respaldo.
"""
import math
import random

import pygame

from juego import recursos, dibujo, lienzo
from juego.config import (ALTO, ROJO, AMARILLO, CIAN, MAGENTA, BLANCO, HIELO, ORO, FUEGO, ENERGIA, EMBESTIDA,
                          MS_POR_FRAME, FORTALEZA_VIDA_CANON, FORTALEZA_PUNTOS_CANON, FORTALEZA_ESPERA,
                          FORTALEZA_CARGA, FORTALEZA_RECALENTADO, FORTALEZA_DISPAROS, FORTALEZA_LASER,
                          FORTALEZA_FURIA, FORTALEZA_CANSADO, FORTALEZA_BRAZOS, FORTALEZA_ESPIRAL_CADA)
from juego.jefes.base import Jefe, registrar_jefe
from juego.jefes.partes import Parte
from juego.proyectiles import Bala, Misil, Mina, romper_balas

ANCHO, ALTO_FORTALEZA = 256, 128
LADO_CANON = 32

# Colores del metal (oscuro -> claro) y paletas de sus pedazos y del recalentado
BORDE = (16, 16, 36)
ACERO = (44, 48, 86)
ACERO_CLARO = (90, 100, 150)
CORAZA = (80, 20, 70)
METAL = [(24, 24, 48), ACERO, ACERO_CLARO, (200, 210, 255)]
HUMO = [(30, 30, 40), (60, 60, 75), (100, 100, 120)]
BRASA = (255, 120, 0)

# Los 4 cañones, de izquierda a derecha: (x dentro de la Fortaleza, ataque, color de la luz)
CANONES = [(16, "misiles", AMARILLO), (76, "rafaga", ROJO), (148, "laser", CIAN), (208, "minas", MAGENTA)]
Y_CANONES = 96          # cuelgan de la parte de abajo del casco


# ================================== #
# ======= DIBUJOS DE RESPALDO ====== #
# ================================== #

def fortaleza_respaldo(con_coraza, color_nucleo, luces):
    # Se dibuja a la mitad (128x64) y se agranda x2: pixeles gruesos, retro
    imagen = pygame.Surface((ANCHO // 2, ALTO_FORTALEZA // 2), pygame.SRCALPHA)
    casco = [(10, 2), (118, 2), (127, 14), (127, 34), (116, 50), (12, 50), (0, 34), (0, 14)]
    pygame.draw.polygon(imagen, ACERO, casco)
    pygame.draw.polygon(imagen, BORDE, casco, 1)
    # Placas: una linea a lo largo y dos costuras
    imagen.fill(ACERO_CLARO, (4, 26, 120, 1))
    for costura_x in (32, 96):
        imagen.fill(BORDE, (costura_x, 4, 1, 44))
    # Ventanitas arriba (se prenden alternadas segun el cuadro) y motores rojos a los costados
    for i, ventana_x in enumerate(range(16, 112, 8)):
        prendida = (i % 2 == 0) == luces
        imagen.fill(CIAN if prendida else BORDE, (ventana_x, 8, 2, 2))
    for motor_x in (2, 122):
        imagen.fill(ROJO if luces else (110, 0, 30), (motor_x, 18, 4, 10))
    if con_coraza:
        # Placas magenta remachadas tapando el nucleo
        placas = [(56, 14), (72, 14), (78, 20), (78, 36), (72, 42), (56, 42), (50, 36), (50, 20)]
        pygame.draw.polygon(imagen, CORAZA, placas)
        pygame.draw.polygon(imagen, MAGENTA, placas, 1)
        imagen.fill(BORDE, (64, 15, 1, 27))
        imagen.fill(BORDE, (51, 28, 27, 1))
        for remache in ((56, 20), (71, 20), (56, 35), (71, 35)):
            imagen.fill(MAGENTA, (*remache, 1, 1))
    else:
        # El agujero de la coraza, con el nucleo brillando adentro
        pygame.draw.circle(imagen, BORDE, (64, 28), 15)
        pygame.draw.circle(imagen, color_nucleo, (64, 28), 11)
        imagen.fill(BLANCO, (59, 22, 3, 3))
        for diente_x, diente_y in ((52, 18), (74, 20), (50, 34), (76, 36), (63, 13)):
            imagen.fill(ACERO, (diente_x, diente_y, 3, 3))
    return pygame.transform.scale(imagen, (ANCHO, ALTO_FORTALEZA))


def canon_respaldo(danado):
    # Torreta con el caño hacia abajo (16x16 agrandado x2)
    imagen = pygame.Surface((LADO_CANON // 2, LADO_CANON // 2), pygame.SRCALPHA)
    cuerpo = ACERO if not danado else (34, 34, 60)
    imagen.fill(BORDE, (1, 0, 14, 10))
    imagen.fill(cuerpo, (2, 0, 12, 9))
    imagen.fill(ACERO_CLARO, (3, 1, 10, 1))
    cano_x = 6 if not danado else 7     # dañado: el caño queda torcido
    imagen.fill(BORDE, (cano_x - 1, 9, 6, 7))
    imagen.fill(ACERO_CLARO, (cano_x, 9, 4, 5))
    imagen.fill(BORDE, (cano_x, 14, 4, 1))
    if danado:
        # Grietas
        for grieta in ((3, 2, 1, 3), (4, 5, 2, 1), (11, 1, 1, 4), (10, 5, 1, 2)):
            imagen.fill(BORDE, grieta)
    return pygame.transform.scale(imagen, (LADO_CANON, LADO_CANON))


_cuadros_canon = {}     # variante ("normal", "brasa", "hielo", "blanco") -> [sano, dañado]


def cuadros_canon():
    if not _cuadros_canon:
        normales = recursos.hoja("fortaleza_canon.png", LADO_CANON)
        if normales is None:
            normales = [canon_respaldo(False), canon_respaldo(True)]
        if len(normales) < 2:
            normales = [normales[0], normales[0]]
        _cuadros_canon["normal"] = normales
        _cuadros_canon["brasa"] = [recursos.tenir(c, BRASA) for c in normales]
        _cuadros_canon["hielo"] = [recursos.tenir(c, HIELO) for c in normales]
        _cuadros_canon["blanco"] = [recursos.blanquear(c) for c in normales]
    return _cuadros_canon


# ================================== #
# ============= CAÑON ============== #
# ================================== #

class Canon(Parte):
    def __init__(self, dx, ataque, color):
        super().__init__(dx, Y_CANONES, LADO_CANON, LADO_CANON, FORTALEZA_VIDA_CANON)
        self.ataque = ataque
        self.color = color
        self.estado = "listo"       # listo -> cargando -> disparando -> recalentado -> listo
        self.estado_hasta = 0
        self.disparos = 0           # disparos que le quedan en este ataque
        self.proximo_disparo = 0
        self.laser_hasta = 0        # mientras tiempo < laser_hasta, el rayo esta prendido
        self.laser_prendido = False
        self.objetivos = []         # adonde van a caer las minas (se eligen al cargar, para el aviso)

    def golpeable(self, jefe):
        return self.estado == "recalentado"

    def boca(self, jefe):
        # Por donde sale lo que dispara
        return jefe.x + self.dx + LADO_CANON / 2, jefe.y + self.dy + LADO_CANON - 2

    def caja_laser(self, jefe):
        boca_x, boca_y = self.boca(jefe)
        return pygame.Rect(int(boca_x) - 8, int(boca_y), 16, ALTO - int(boca_y))

    def cambiar_estado(self, estado, duracion, tiempo):
        self.estado = estado
        self.estado_hasta = tiempo + duracion

    def dibujar(self, pantalla, x, y, jefe, partida):
        if not self.viva():
            # Restos: un muñon chamuscado con el borde al rojo
            pantalla.fill(BORDE, (x + 2, y, 28, 14))
            pantalla.fill(ACERO, (x + 4, y, 24, 10))
            pantalla.fill((110, 0, 30), (x + 6, y + 10, 20, 4))
            pantalla.fill(BRASA if dibujo.parpadeo(300) else ROJO, (x + 10, y + 12, 4, 2))
            pantalla.fill(BRASA if dibujo.parpadeo(300) else ROJO, (x + 18, y + 12, 4, 2))
            return
        indice = 0 if self.vida == self.vida_max else 1
        cuadros = cuadros_canon()
        if partida.tiempo < self.golpe_hasta and dibujo.parpadeo(60):
            variante = "blanco"
        elif jefe.congelado(partida):
            variante = "hielo"
        elif self.estado == "recalentado":
            # Brilla: alterna entre brasa y blanco, cada vez mas rapido al enfriarse
            variante = "brasa" if dibujo.parpadeo(150) else "normal"
        else:
            variante = "normal"
        pantalla.blit(cuadros[variante][indice], (x, y))
        # La lucecita de su color (al cargar parpadea en blanco)
        luz = BLANCO if self.estado == "cargando" and dibujo.parpadeo(80) else self.color
        pantalla.fill(luz, (x + 14, y + 4, 4, 4))


# ================================== #
# =========== FORTALEZA ============ #
# ================================== #

@registrar_jefe
class Fortaleza(Jefe):
    tipo = "fortaleza"
    ancho = ANCHO
    alto = ALTO_FORTALEZA
    y_final = 56                # un poco mas abajo que el Ojo, para no tapar el HUD
    fases_congelables = ("pelear", "furia", "cansado")

    def __init__(self, partida):
        super().__init__(partida)
        self.partes = [Canon(dx, ataque, color) for dx, ataque, color in CANONES]
        self.turno = -1                 # indice del ultimo cañon que ataco (se van turnando)
        self.proximo_ataque = 0
        self.con_coraza = True
        self.giro_espiral = 0           # angulo de la espiral (furia)
        self.sentido = 1                # para que lado gira (cambia en cada furia)
        self.proximo_disparo = 0

    @classmethod
    def cargar_animaciones(cls):
        cuadros = recursos.hoja("fortaleza.png", ANCHO)
        if cuadros is None:
            cuadros = [fortaleza_respaldo(True, None, True), fortaleza_respaldo(True, None, False),
                       fortaleza_respaldo(False, ROJO, True), fortaleza_respaldo(False, (255, 150, 140), False),
                       fortaleza_respaldo(False, AMARILLO, True), fortaleza_respaldo(False, BLANCO, False)]
        if len(cuadros) >= 6:
            return {"coraza": cuadros[0:2], "furia": cuadros[2:4], "cansado": cuadros[4:6]}
        return {"coraza": cuadros, "furia": cuadros, "cansado": cuadros}

    # ---------- Consultas ----------

    def centro_nucleo(self):
        return self.x + 128, self.y + 56

    def caja_cuerpo(self):
        return pygame.Rect(int(self.x) + 8, int(self.y) + 8, 240, 88)

    def caja_nucleo(self):
        return pygame.Rect(int(self.x) + 104, int(self.y) + 32, 48, 48)

    def cajas_danio(self):
        # Ademas del casco y los cañones, los rayos laser prendidos
        cajas = super().cajas_danio()
        for canon in self.partes_vivas():
            if canon.laser_prendido:
                cajas.append(canon.caja_laser(self))
        return cajas

    def vida_barra(self):
        # La barra muestra los golpes de los cañones y los del nucleo, todos juntos
        vida = self.vida + sum(canon.vida for canon in self.partes)
        vida_max = self.vida_max + sum(canon.vida_max for canon in self.partes)
        return vida, vida_max

    def temblando(self):
        return self.fase in ("descubrirse", "morir")

    def rapidez(self, partida):
        # Rapidez de sus balas (como las del Ojo)
        return min(3 + partida.jefes_vencidos * 0.3, 4.5) * partida.reglas["velocidad"]

    # ---------- Fases ----------

    def al_terminar_de_entrar(self, partida):
        self.cambiar_fase("pelear", 0, partida.tiempo)
        self.proximo_ataque = partida.tiempo + 800

    def al_congelarse(self):
        # Congelada, sus temporizadores tampoco corren
        self.proximo_ataque += MS_POR_FRAME
        self.proximo_disparo += MS_POR_FRAME
        for canon in self.partes:
            canon.estado_hasta += MS_POR_FRAME
            canon.proximo_disparo += MS_POR_FRAME
            canon.laser_hasta += MS_POR_FRAME

    def actualizar_fase(self, partida):
        ahora = partida.tiempo
        if self.fase == "pelear":
            self.moverse(ahora, lento=True)
            if ahora >= self.proximo_ataque:
                self.elegir_canon(partida)
            for canon in self.partes:
                self.actualizar_canon(partida, canon)

        elif self.fase == "descubrirse":
            # Tiembla, echa humo y chispas, y al final se le cae la coraza
            nucleo_x, nucleo_y = self.centro_nucleo()
            if random.random() < 0.4:
                partida.efectos.explosion(nucleo_x + random.randint(-30, 30), nucleo_y + random.randint(-24, 24),
                                          FUEGO, 8, 3, 3)
            if random.random() < 0.3:
                partida.efectos.sacudir(2)
            if ahora > self.fase_hasta:
                self.caer_coraza(partida)

        elif self.fase == "furia":
            self.moverse(ahora, lento=False)
            if ahora >= self.proximo_disparo:
                self.disparar_espiral(partida)
                self.proximo_disparo = ahora + FORTALEZA_ESPIRAL_CADA
            if ahora > self.fase_hasta:
                self.cambiar_fase("cansado", FORTALEZA_CANSADO, ahora)
                nucleo_x, nucleo_y = self.centro_nucleo()
                partida.efectos.explosion(nucleo_x, nucleo_y, ORO, 20, 4, 3)

        elif self.fase == "cansado":
            if random.random() < 0.25:
                nucleo_x, nucleo_y = self.centro_nucleo()
                partida.efectos.particula(nucleo_x + random.randint(-20, 20), nucleo_y + random.randint(-20, 20),
                                          random.uniform(-1, 1), random.uniform(-2, 0), ORO, 12, 2)
            if ahora > self.fase_hasta:
                self.empezar_furia(ahora)

    def moverse(self, ahora, lento):
        # De lado a lado, acercandose de a poco al punto (asi no da saltos)
        centro = (lienzo.ancho - ANCHO) / 2
        if lento:
            objetivo_x = centro + math.sin(ahora / 1400) * (centro - 30)
            self.x += (objetivo_x - self.x) * 0.03
        else:
            objetivo_x = centro + math.sin(ahora / 500) * (centro - 20)
            self.x += (objetivo_x - self.x) * 0.06

    def empezar_furia(self, ahora):
        self.sentido = -self.sentido
        self.proximo_disparo = ahora
        self.cambiar_fase("furia", FORTALEZA_FURIA, ahora)

    def al_recibir_golpe(self, partida):
        self.empezar_furia(partida.tiempo)

    # ---------- Cañones ----------

    def elegir_canon(self, partida):
        # El proximo cañon (en orden) que este sano y listo empieza a cargar
        ahora = partida.tiempo
        vivos = self.partes_vivas()
        for paso in range(1, len(self.partes) + 1):
            indice = (self.turno + paso) % len(self.partes)
            canon = self.partes[indice]
            if canon.viva() and canon.estado == "listo":
                self.turno = indice
                self.empezar_carga(partida, canon)
                self.proximo_ataque = ahora + FORTALEZA_ESPERA[len(vivos)]
                return
        self.proximo_ataque = ahora + 200       # todos ocupados: prueba en un rato

    def empezar_carga(self, partida, canon):
        canon.cambiar_estado("cargando", FORTALEZA_CARGA, partida.tiempo)
        if canon.ataque == "minas":
            # Las minas ya saben adonde van a caer (asi el aviso las muestra)
            disparos = FORTALEZA_DISPAROS["minas"][0]
            canon.objetivos = [(random.randint(60, lienzo.ancho - 60), random.randint(260, 500))
                               for _ in range(disparos)]

    def actualizar_canon(self, partida, canon):
        ahora = partida.tiempo
        if not canon.viva():
            # Restos humeantes
            if random.random() < 0.08:
                boca_x, boca_y = canon.boca(self)
                partida.efectos.particula(boca_x + random.randint(-8, 8), boca_y - 20, 0, -1, HUMO, 30, 4)
            return
        boca_x, boca_y = canon.boca(self)
        if canon.vida < canon.vida_max and random.random() < 0.05:
            partida.efectos.particula(boca_x + random.randint(-10, 10), boca_y - 24, 0, -0.8, HUMO, 24, 2)

        if canon.estado == "cargando":
            if random.random() < 0.5:
                # Chispas de su color que se juntan en la boca
                chispa_x = boca_x + random.randint(-24, 24)
                chispa_y = boca_y + random.randint(-10, 30)
                partida.efectos.particula(chispa_x, chispa_y, (boca_x - chispa_x) * 0.1, (boca_y - chispa_y) * 0.1,
                                          [(40, 40, 60), canon.color, BLANCO], 12, 2)
            if ahora >= canon.estado_hasta:
                canon.disparos = FORTALEZA_DISPAROS[canon.ataque][0]
                canon.proximo_disparo = ahora
                canon.cambiar_estado("disparando", 0, ahora)

        elif canon.estado == "disparando":
            if canon.laser_prendido:
                if random.random() < 0.6:
                    partida.efectos.particula(boca_x + random.randint(-8, 8), random.randint(int(boca_y), ALTO),
                                              random.uniform(-2, 2), 0, ENERGIA, 10, 2)
                if ahora >= canon.laser_hasta:
                    canon.laser_prendido = False
                    self.recalentar(partida, canon)
            elif canon.disparos > 0:
                if ahora >= canon.proximo_disparo:
                    self.disparar(partida, canon)
                    canon.disparos -= 1
                    canon.proximo_disparo = ahora + FORTALEZA_DISPAROS[canon.ataque][1]
            else:
                self.recalentar(partida, canon)

        elif canon.estado == "recalentado":
            if random.random() < 0.3:
                partida.efectos.particula(boca_x + random.randint(-12, 12), boca_y - random.randint(4, 28),
                                          0, -1, FUEGO, 16, 2)
            if ahora >= canon.estado_hasta:
                canon.cambiar_estado("listo", 0, ahora)

    def recalentar(self, partida, canon):
        canon.cambiar_estado("recalentado", FORTALEZA_RECALENTADO, partida.tiempo)
        boca_x, boca_y = canon.boca(self)
        partida.efectos.explosion(boca_x, boca_y - 14, FUEGO, 10, 3, 3)

    def disparar(self, partida, canon):
        boca_x, boca_y = canon.boca(self)
        rapidez = self.rapidez(partida)
        if canon.ataque == "rafaga":
            for direccion in self.direcciones_rafaga(partida, canon):
                partida.balas.append(Bala(boca_x, boca_y, math.cos(direccion) * rapidez,
                                          math.sin(direccion) * rapidez))
        elif canon.ataque == "misiles":
            # Salen hacia abajo, abiertos, y despues te buscan
            lado = random.choice((-1, 1))
            partida.balas.append(Misil(boca_x, boca_y, lado * rapidez * 0.4, rapidez * 0.6))
        elif canon.ataque == "minas":
            # Cada mina viaja frenando hasta su objetivo (con friccion 0.95 recorre 20 veces su velocidad)
            objetivo_x, objetivo_y = canon.objetivos[len(canon.objetivos) - canon.disparos]
            partida.balas.append(Mina(boca_x, boca_y, (objetivo_x - boca_x) / 20, (objetivo_y - boca_y) / 20,
                                      rapidez * 0.7))
        elif canon.ataque == "laser":
            canon.laser_prendido = True
            canon.laser_hasta = partida.tiempo + FORTALEZA_LASER
            partida.efectos.sacudir(6, CIAN)
            partida.sonidos.reproducir("golpe")
        partida.efectos.anillo(boca_x, boca_y, [(40, 40, 60), canon.color, BLANCO], 8, 3, 2)

    def direcciones_rafaga(self, partida, canon):
        # 3 balas hacia la nave, un poco abiertas. Las usan el disparo y el aviso
        boca_x, boca_y = canon.boca(self)
        nave_x, nave_y = partida.nave.centro()
        hacia_nave = math.atan2(nave_y - boca_y, nave_x - boca_x)
        return [hacia_nave + math.radians(abertura) for abertura in (-10, 0, 10)]

    def disparar_espiral(self, partida):
        # Sin coraza: el nucleo dispara en espiral, girando
        nucleo_x, nucleo_y = self.centro_nucleo()
        rapidez = self.rapidez(partida) * 0.75
        for brazo in range(FORTALEZA_BRAZOS):
            direccion = self.giro_espiral + 2 * math.pi * brazo / FORTALEZA_BRAZOS
            partida.balas.append(Bala(nucleo_x, nucleo_y, math.cos(direccion) * rapidez,
                                      math.sin(direccion) * rapidez))
        self.giro_espiral += 0.22 * self.sentido

    # ---------- Partes rotas ----------

    def al_golpear_parte(self, partida, canon):
        # El golpe lo enfria: hay que esperar a que vuelva a disparar
        canon.cambiar_estado("listo", 0, partida.tiempo)

    def al_romper_parte(self, partida, canon):
        canon.laser_prendido = False
        centro_x, centro_y = canon.centro(self)
        partida.efectos.pedazos(centro_x, centro_y, METAL, 12, 5)
        partida.efectos.pedazos(centro_x, centro_y, [(60, 20, 0), BRASA, AMARILLO], 6, 4)
        ganados = partida.sumar_puntos(FORTALEZA_PUNTOS_CANON)
        partida.efectos.texto_flotante("+" + str(ganados), centro_x, centro_y - 40, AMARILLO)
        if not self.partes_vivas():
            # Sin cañones: tiembla un rato y se le cae la coraza
            romper_balas(partida.balas, partida.efectos, EMBESTIDA)
            self.cambiar_fase("descubrirse", 1800, partida.tiempo)

    def caer_coraza(self, partida):
        self.con_coraza = False
        nucleo_x, nucleo_y = self.centro_nucleo()
        partida.efectos.pedazos(nucleo_x, nucleo_y, [(40, 0, 30), CORAZA, MAGENTA, (255, 150, 230)], 30, 7)
        partida.efectos.explosion(nucleo_x, nucleo_y, FUEGO, 50, 9, 5)
        partida.efectos.anillo(nucleo_x, nucleo_y, EMBESTIDA, 32, 7, 4)
        partida.efectos.sacudir(25, MAGENTA)
        partida.efectos.texto_flotante("¡SIN CORAZA!", nucleo_x, nucleo_y + 90, MAGENTA)
        partida.entrada.vibrar(0.8, 1, 400)
        partida.congelar_frames = 6
        partida.sonidos.reproducir("golpe")
        self.empezar_furia(partida.tiempo)

    # ---------- Dibujo ----------

    def animacion(self):
        if self.con_coraza:
            return "coraza"
        if self.fase in ("cansado", "morir"):
            return "cansado"
        return "furia"

    def dibujar_extra(self, pantalla, partida):
        for canon in self.partes_vivas():
            if canon.laser_prendido:
                self.dibujar_laser(pantalla, canon)
            elif canon.estado == "cargando" and not self.congelado(partida):
                self.dibujar_aviso(pantalla, partida, canon)

    def dibujar_laser(self, pantalla, canon):
        # Un rayo grueso que titila: borde cian y centro blanco
        rayo = canon.caja_laser(self)
        rayo.top -= 4
        rayo.height += 4
        ancho = 16 if dibujo.parpadeo(60) else 12
        pantalla.fill(CIAN, (rayo.centerx - ancho // 2, rayo.top, ancho, rayo.height))
        pantalla.fill(BLANCO, (rayo.centerx - 3, rayo.top, 6, rayo.height))

    def dibujar_aviso(self, pantalla, partida, canon):
        boca_x, boca_y = canon.boca(self)
        if canon.ataque == "laser":
            # El laser siempre avisa: una linea fina por donde va a pasar
            if dibujo.parpadeo(80):
                pantalla.fill(CIAN, (int(boca_x) // 2 * 2 - 1, int(boca_y), 2, ALTO - int(boca_y)))
            return
        # Los demas avisan solo si esta prendido el aviso del jefe (Opciones)
        if not partida.opciones.aviso_jefe or not dibujo.parpadeo(100):
            return
        if canon.ataque == "rafaga":
            for direccion in self.direcciones_rafaga(partida, canon):
                for paso in range(24, 161, 16):
                    punto_x = boca_x + math.cos(direccion) * paso
                    punto_y = boca_y + math.sin(direccion) * paso
                    pantalla.fill(ROJO, (int(punto_x) // 2 * 2, int(punto_y) // 2 * 2, 4, 4))
        elif canon.ataque == "minas":
            # Una X donde va a caer cada mina
            for objetivo_x, objetivo_y in canon.objetivos:
                for paso in range(-6, 7, 3):
                    for signo in (1, -1):
                        pantalla.fill(MAGENTA, (objetivo_x + paso // 2 * 2, objetivo_y + signo * paso // 2 * 2, 4, 4))
        elif canon.ataque == "misiles":
            # Flechitas amarillas hacia abajo
            for paso in range(16, 49, 16):
                for lado in (-4, 0, 4):
                    pantalla.fill(AMARILLO, (int(boca_x) // 2 * 2 + lado - 2, int(boca_y) + paso - abs(lado), 4, 4))
