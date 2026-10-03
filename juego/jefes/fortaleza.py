"""
La Fortaleza: un acorazado gigante (256x128) que pelea como una MARCHA MILITAR.

Todo va al ritmo de su pulso (las cuatro lamparitas amarillas del casco marcan el
compas). Nunca ataca con dos cosas a la vez: cada compas es

    reubicarse (2 pulsos) -> cargar (2) -> disparar (a ritmo) -> RECALENTADO (5)

y recalentado es el momento de pegarle con el dash al cañon que disparo.
Cada cañon tiene su ataque (y una lucecita de su color para reconocerlo):
    rafaga  (rojo):     3 obuses, uno por pulso: "¡pum, pum, pum!"
    misiles (amarillo): 2 misiles que te siguen (el dash los destruye y da puntos)
    laser   (cian):     un rayo que barre la pantalla hacia vos: hay que cruzarlo con el dash
    minas   (magenta):  2 minas que caen en las X y estallan en cruz, una por pulso
Con cada cañon roto el pulso se acelera, y con 2 o menos los ataques vienen de a dos.

Sin cañones se le cae la coraza y empieza el baile final:
    cortinas (escombros que caen con un hueco: busca el hueco) -> apuntar (se pone
    encima tuyo) -> fijar (se queda quieta un pulso, temblando: ¡salí de abajo!) ->
    CAER (se desploma hasta el piso y suelta ondas de choque) ->
    aturdida (nucleo a la vista: ¡DASH!) -> subir -> cortinas...

Los cañones son Partes (ver partes.py): la clase base ya resuelve el golpe con el dash,
el daño al tocarlos y la flechita. Aca solo se decide cuando se les puede pegar.

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
                          FORTALEZA_VIDA_CANON, FORTALEZA_PUNTOS_CANON, FORTALEZA_PULSOS, FORTALEZA_RECALENTADO,
                          FORTALEZA_MISIL_GUIADO, FORTALEZA_LASER_VELOCIDAD, FORTALEZA_ATURDIDA)
from juego.jefes.base import Jefe, registrar_jefe
from juego.jefes.partes import Parte
from juego.proyectiles import Obus, Misil, Mina, Escombro, Onda, romper_balas

ANCHO, ALTO_FORTALEZA = 256, 128
LADO_CANON = 32

# Colores del metal (oscuro -> claro) y paletas de sus pedazos, el humo y el recalentado
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
PULSOS_ATAQUE = {"rafaga": 3, "misiles": 2, "laser": 3, "minas": 2}


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
        self.caliente = False       # recalentado: se le puede pegar
        self.objetivos = []         # adonde van a caer las minas (se eligen al cargar, para el aviso)

    def golpeable(self, jefe):
        return self.caliente

    def boca(self, jefe):
        # Por donde sale lo que dispara
        return jefe.x + self.dx + LADO_CANON / 2, jefe.y + self.dy + LADO_CANON - 2

    def caja_laser(self, jefe):
        boca_x, boca_y = self.boca(jefe)
        return pygame.Rect(int(boca_x) - 8, int(boca_y), 16, ALTO - int(boca_y))

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
        elif self.caliente:
            variante = "brasa" if dibujo.parpadeo(150) else "normal"
        else:
            variante = "normal"
        pantalla.blit(cuadros[variante][indice], (x, y))
        # La lucecita de su color (al cargar parpadea en blanco)
        cargando = jefe.fase == "cargar" and jefe.canon_actual() is self
        luz = BLANCO if cargando and dibujo.parpadeo(80) else self.color
        pantalla.fill(luz, (x + 14, y + 4, 4, 4))


# ================================== #
# =========== FORTALEZA ============ #
# ================================== #

@registrar_jefe
class Fortaleza(Jefe):
    tipo = "fortaleza"
    nombre = "LA FORTALEZA"
    apodo = "ACORAZADO IMPERIAL"
    color = ROJO
    ancho = ANCHO
    alto = ALTO_FORTALEZA
    y_final = 56                # un poco mas abajo que el Ojo, para no tapar el HUD
    ms_pulso = FORTALEZA_PULSOS[0]
    fases_congelables = ("reubicarse", "cargar", "disparar", "recalentado",
                         "cortinas", "apuntar", "fijar", "aturdida", "subir")

    def __init__(self, partida):
        super().__init__(partida)
        self.partes = [Canon(dx, ataque, color) for dx, ataque, color in CANONES]
        self.con_coraza = True
        self.compas = []                # los cañones que atacan en este compas (1 o 2)
        self.turno = 0                  # cual de ellos esta cargando/disparando
        self.ultimo = None              # el ultimo que ataco (para no repetir)
        self.destino_x = self.x
        self.barrido = 1                # hacia donde barre el laser (+1 derecha, -1 izquierda)
        self.laser_prendido = False
        self.huecos = []                # donde quedan los huecos de las cortinas
        self.velocidad_caida = 0

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
        # El casco en dos cajas que siguen su forma (abajo es mas angosto: asi no te
        # pega con una esquina que no se ve), los cañones y el rayo laser prendido
        x, y = int(self.x), int(self.y)
        cajas = [pygame.Rect(x + 4, y + 6, 248, 62), pygame.Rect(x + 26, y + 68, 204, 32)]
        cajas += [canon.caja(self) for canon in self.partes_vivas()]
        if self.laser_prendido:
            cajas.append(self.canon_actual().caja_laser(self))
        return cajas

    def puede_recibir_golpe(self):
        return self.fase == "aturdida"

    def vida_barra(self):
        # La barra muestra los golpes de los cañones y los del nucleo, todos juntos
        vida = self.vida + sum(canon.vida for canon in self.partes)
        vida_max = self.vida_max + sum(canon.vida_max for canon in self.partes)
        return vida, vida_max

    def temblando(self):
        return self.fase in ("descubrirse", "fijar", "morir")

    def canon_actual(self):
        return self.compas[self.turno] if self.turno < len(self.compas) else None

    def rapidez(self, partida):
        return min(3.2 + partida.jefes_vencidos * 0.2, 4) * partida.reglas["velocidad"]

    def x_sobre(self, x_centro):
        # La x de la Fortaleza para que su centro quede en x_centro (sin salirse)
        return max(10, min(x_centro - ANCHO / 2, lienzo.ancho - ANCHO - 10))

    # ---------- La marcha (con coraza) ----------

    def al_terminar_de_entrar(self, partida):
        self.empezar_compas(partida)

    def empezar_compas(self, partida):
        # Elige quien ataca y se acomoda. Con cada cañon roto el pulso se acelera
        vivos = self.partes_vivas()
        self.ms_pulso = FORTALEZA_PULSOS[len(self.partes) - len(vivos)]
        opciones = [c for c in vivos if c is not self.ultimo] or vivos
        primero = random.choice(opciones)
        if len(vivos) >= 3:
            self.compas = [primero]
        elif len(vivos) == 2:
            self.compas = [primero] + [c for c in vivos if c is not primero]
        else:
            self.compas = [primero, primero]        # el ultimo cañon ataca dos veces seguidas
        self.ultimo = self.compas[-1]
        self.turno = 0
        nave_x = partida.nave.centro()[0]
        if primero.ataque == "laser":
            # Para barrer hacia vos, se pone del otro lado de la pantalla
            lejos = lienzo.ancho * 0.8 if nave_x < lienzo.ancho / 2 else lienzo.ancho * 0.2
            self.destino_x = self.x_sobre(lejos)
        else:
            self.destino_x = self.x_sobre(nave_x + random.randint(-80, 80))
        self.cambiar_fase_pulsos("reubicarse", 2, partida.tiempo)

    def empezar_carga(self, partida, pulsos):
        canon = self.canon_actual()
        boca_x = canon.boca(self)[0]
        nave_x, nave_y = partida.nave.centro()
        if canon.ataque == "laser":
            self.barrido = 1 if nave_x > boca_x else -1
        elif canon.ataque == "minas":
            # Una mina donde estas y otra al azar (asi el aviso las muestra antes)
            canon.objetivos = [(max(60, min(nave_x, lienzo.ancho - 60)), max(230, min(nave_y, 480))),
                               (random.randint(60, lienzo.ancho - 60), random.randint(230, 480))]
        self.cambiar_fase_pulsos("cargar", pulsos, partida.tiempo)

    def actualizar_fase(self, partida):
        ahora = partida.tiempo
        fase = self.fase
        if fase == "reubicarse":
            self.x += (self.destino_x - self.x) * 0.08
            self.y += (self.y_final - self.y) * 0.1
            if self.fin_de_fase(ahora):
                self.empezar_carga(partida, 2)

        elif fase == "cargar":
            self.chispas_de_carga(partida, self.canon_actual())
            if self.fin_de_fase(ahora):
                pulsos = PULSOS_ATAQUE[self.canon_actual().ataque]
                self.cambiar_fase_pulsos("disparar", pulsos, ahora)

        elif fase == "disparar":
            # Primero se revisa el final: el paso en que termina la fase es tambien el
            # comienzo de un pulso nuevo, y no tiene que disparar de mas
            canon = self.canon_actual()
            if self.fin_de_fase(ahora):
                self.laser_prendido = False
                self.turno += 1
                if self.turno < len(self.compas):
                    self.empezar_carga(partida, 1)      # el segundo cañon carga mas rapido
                else:
                    self.recalentar(partida)
            else:
                if self.nuevo_pulso:
                    self.disparar(partida, canon, self.pulso)
                if self.laser_prendido:
                    self.x = max(10, min(self.x + self.barrido * FORTALEZA_LASER_VELOCIDAD,
                                         lienzo.ancho - ANCHO - 10))
                    boca_x = canon.boca(self)[0]
                    partida.efectos.particula(boca_x + random.randint(-8, 8), random.randint(200, ALTO),
                                              random.uniform(-2, 2), 0, ENERGIA, 10, 2)

        elif fase == "recalentado":
            # Quieta y un poco hundida: el momento de pegarle
            self.y += (self.y_final + 10 - self.y) * 0.1
            for canon in self.compas:
                if canon.caliente and random.random() < 0.3:
                    boca_x, boca_y = canon.boca(self)
                    partida.efectos.particula(boca_x + random.randint(-12, 12), boca_y - random.randint(4, 28),
                                              0, -1, FUEGO, 16, 2)
            sin_calientes = not any(c.caliente and c.viva() for c in self.compas)
            if self.fin_de_fase(ahora) or sin_calientes:
                for canon in self.compas:
                    canon.caliente = False
                self.empezar_compas(partida)

        else:
            self.actualizar_baile_final(partida)

        self.humo_de_canones(partida)

    def chispas_de_carga(self, partida, canon):
        if random.random() < 0.5:
            boca_x, boca_y = canon.boca(self)
            chispa_x = boca_x + random.randint(-24, 24)
            chispa_y = boca_y + random.randint(-10, 30)
            partida.efectos.particula(chispa_x, chispa_y, (boca_x - chispa_x) * 0.1, (boca_y - chispa_y) * 0.1,
                                      [(40, 40, 60), canon.color, BLANCO], 12, 2)

    def humo_de_canones(self, partida):
        for canon in self.partes:
            if canon.viva() and canon.vida == canon.vida_max:
                continue
            if random.random() < (0.08 if not canon.viva() else 0.05):
                boca_x, boca_y = canon.boca(self)
                partida.efectos.particula(boca_x + random.randint(-8, 8), boca_y - 20, 0, -1, HUMO, 30, 4)

    def recalentar(self, partida):
        for canon in self.compas:
            if canon.viva():
                canon.caliente = True
                boca_x, boca_y = canon.boca(self)
                partida.efectos.explosion(boca_x, boca_y - 14, FUEGO, 10, 3, 3)
        self.cambiar_fase_pulsos("recalentado", FORTALEZA_RECALENTADO, partida.tiempo)

    def disparar(self, partida, canon, pulso):
        # Un disparo por pulso (cada ataque sabe que hacer en cada pulso)
        boca_x, boca_y = canon.boca(self)
        rapidez = self.rapidez(partida)
        if canon.ataque == "rafaga":
            nave_x, nave_y = partida.nave.centro()
            direccion = math.atan2(nave_y - boca_y, nave_x - boca_x)
            partida.balas.append(Obus(boca_x, boca_y, math.cos(direccion) * rapidez, math.sin(direccion) * rapidez))
            partida.efectos.sacudir(3)
        elif canon.ataque == "misiles" and pulso < 2:
            lado = -1 if pulso == 0 else 1
            escala = partida.reglas["velocidad"]
            partida.balas.append(Misil(boca_x, boca_y, lado * 1.6 * escala, 1.2 * escala, FORTALEZA_MISIL_GUIADO))
        elif canon.ataque == "minas" and pulso < len(canon.objetivos):
            # Viaja frenando hasta su X (con friccion 0.95 recorre 20 veces su velocidad)
            # y estalla 3 pulsos despues de salir: la primera en "+", la segunda en "x"
            objetivo_x, objetivo_y = canon.objetivos[pulso]
            partida.balas.append(Mina(boca_x, boca_y, (objetivo_x - boca_x) / 20, (objetivo_y - boca_y) / 20,
                                      rapidez * 0.8, 3 * self.ms_pulso, "+" if pulso == 0 else "x"))
        elif canon.ataque == "laser" and pulso == 0:
            self.laser_prendido = True
            partida.efectos.sacudir(6, CIAN)
            partida.sonidos.reproducir("golpe")
        else:
            return
        partida.efectos.anillo(boca_x, boca_y, [(40, 40, 60), canon.color, BLANCO], 8, 3, 2)

    # ---------- Partes rotas ----------

    def al_golpear_parte(self, partida, canon):
        canon.caliente = False          # el golpe lo enfria

    def al_romper_parte(self, partida, canon):
        canon.caliente = False
        centro_x, centro_y = canon.centro(self)
        partida.efectos.pedazos(centro_x, centro_y, METAL, 12, 5)
        partida.efectos.pedazos(centro_x, centro_y, [(60, 20, 0), BRASA, AMARILLO], 6, 4)
        ganados = partida.sumar_puntos(FORTALEZA_PUNTOS_CANON)
        partida.efectos.texto_flotante("+" + str(ganados), centro_x, centro_y - 40, AMARILLO)
        if not self.partes_vivas():
            # Sin cañones: tiembla un rato y se le cae la coraza
            romper_balas(partida.balas, partida.efectos, EMBESTIDA)
            self.ms_pulso = FORTALEZA_PULSOS[-1]
            self.cambiar_fase_pulsos("descubrirse", 4, partida.tiempo)

    # ---------- El baile final (sin coraza) ----------

    def actualizar_baile_final(self, partida):
        ahora = partida.tiempo
        fase = self.fase
        if fase == "descubrirse":
            nucleo_x, nucleo_y = self.centro_nucleo()
            if random.random() < 0.4:
                partida.efectos.explosion(nucleo_x + random.randint(-30, 30), nucleo_y + random.randint(-24, 24),
                                          FUEGO, 8, 3, 3)
            if self.fin_de_fase(ahora):
                self.caer_coraza(partida)

        elif fase == "cortinas":
            # Pulso 0: avisa la primera cortina; 1: cae. Pulso 2: avisa la segunda; 3: cae.
            # Los pulsos 4 y 5 son de respiro: los escombros terminan de caer antes de apuntar
            self.y += (self.y_final - self.y) * 0.1
            if self.fin_de_fase(ahora):
                self.cambiar_fase_pulsos("apuntar", 2, ahora)
            elif self.nuevo_pulso and self.pulso in (1, 3):
                self.soltar_cortina(partida, self.huecos[self.pulso // 2])

        elif fase == "apuntar":
            # Se pone encima tuyo (el aviso marca la columna donde va a caer)
            self.x += (self.x_sobre(partida.nave.centro()[0]) - self.x) * 0.12
            if self.fin_de_fase(ahora):
                self.cambiar_fase_pulsos("fijar", 1, ahora)

        elif fase == "fijar":
            # Deja de seguirte y junta fuerzas: el tiempo justo para salir de abajo
            if self.fin_de_fase(ahora):
                self.velocidad_caida = 0
                self.cambiar_fase("caer", 5000, ahora)

        elif fase == "caer":
            self.velocidad_caida += 1.2
            self.y += self.velocidad_caida
            if self.y >= self.y_suelo():
                self.y = self.y_suelo()
                self.estrellarse(partida)

        elif fase == "aturdida":
            if random.random() < 0.25:
                nucleo_x, nucleo_y = self.centro_nucleo()
                partida.efectos.particula(nucleo_x + random.randint(-20, 20), nucleo_y + random.randint(-20, 20),
                                          random.uniform(-1, 1), random.uniform(-2, 0), ORO, 12, 2)
            if self.fin_de_fase(ahora):
                self.cambiar_fase_pulsos("subir", 3, ahora)

        elif fase == "subir":
            self.y += (self.y_final - self.y) * 0.06
            if self.fin_de_fase(ahora):
                self.empezar_cortinas(partida)

    def y_suelo(self):
        # Hasta donde cae: el casco (88 px de alto) queda apoyado abajo de todo
        return ALTO - 100

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
        self.empezar_cortinas(partida)

    def empezar_cortinas(self, partida):
        # Dos cortinas con el hueco en tercios distintos de la pantalla (hay que moverse)
        tercios = [lienzo.ancho * (i + 0.5) / 3 for i in range(3)]
        primero = random.choice(tercios)
        segundo = random.choice([t for t in tercios if t != primero])
        self.huecos = [primero + random.randint(-40, 40), segundo + random.randint(-40, 40)]
        self.cambiar_fase_pulsos("cortinas", 6, partida.tiempo)

    def soltar_cortina(self, partida, hueco):
        rapidez = 3.6 * partida.reglas["velocidad"]
        for x in range(24, lienzo.ancho, 72):
            if abs(x - hueco) > 90:
                partida.balas.append(Escombro(x, self.y + 96, 0, rapidez))
        partida.efectos.sacudir(4)
        partida.sonidos.reproducir("golpe")

    def estrellarse(self, partida):
        # Golpe contra el piso: temblor, pedazos y dos ondas de choque a los costados
        centro_x = self.x + ANCHO / 2
        piso = ALTO - 14
        rapidez = 4.5 * partida.reglas["velocidad"]
        partida.balas.append(Onda(self.x + 10, piso, -rapidez, 0))
        partida.balas.append(Onda(self.x + ANCHO - 10, piso, rapidez, 0))
        partida.efectos.pedazos(centro_x, piso - 10, METAL, 16, 6)
        partida.efectos.sacudir(22, BLANCO)
        partida.entrada.vibrar(1, 1, 300)
        partida.congelar_frames = 5
        partida.sonidos.reproducir("golpe")
        self.cambiar_fase_pulsos("aturdida", FORTALEZA_ATURDIDA, partida.tiempo)

    def al_recibir_golpe(self, partida):
        self.cambiar_fase_pulsos("subir", 3, partida.tiempo)

    # ---------- Dibujo ----------

    def animacion(self):
        if self.con_coraza:
            return "coraza"
        if self.fase in ("aturdida", "morir"):
            return "cansado"
        return "furia"

    def dibujar_extra(self, pantalla, partida):
        self.dibujar_compas(pantalla)
        congelada = self.congelado(partida)
        if self.laser_prendido:
            self.dibujar_laser(pantalla)
        elif self.fase == "cargar" and not congelada:
            self.dibujar_aviso(pantalla, partida, self.canon_actual())
        elif self.fase == "cortinas" and self.pulso in (0, 2) and dibujo.parpadeo(100):
            self.dibujar_aviso_cortina(pantalla, self.huecos[self.pulso // 2])
        elif self.fase in ("apuntar", "fijar") and dibujo.parpadeo(100 if self.fase == "apuntar" else 50):
            # La columna donde va a caer
            columna = pygame.Rect(int(self.x) + 4, int(self.y) + 100, ANCHO - 8, ALTO - int(self.y) - 100)
            for borde_y in range(columna.top, columna.bottom, 16):
                pantalla.fill(ROJO, (columna.left, borde_y, 4, 8))
                pantalla.fill(ROJO, (columna.right - 4, borde_y, 4, 8))
        elif self.fase == "aturdida":
            # Estrellitas girando: esta mareada
            nucleo_x, nucleo_y = self.centro_nucleo()
            for i in range(3):
                angulo = partida.tiempo / 200 + i * 2.1
                estrella_x = int(nucleo_x + math.cos(angulo) * 50) // 2 * 2
                estrella_y = int(nucleo_y - 60 + math.sin(angulo) * 12) // 2 * 2
                pantalla.fill(AMARILLO, (estrella_x - 2, estrella_y - 6, 4, 12))
                pantalla.fill(AMARILLO, (estrella_x - 6, estrella_y - 2, 12, 4))

    def dibujar_compas(self, pantalla):
        # Las cuatro lamparitas del casco marcan el pulso, como un metronomo
        if self.fase in ("entrar", "morir", "caer") or self.pulso < 0:
            return
        prendida = self.pulso % 4
        for i in range(4):
            color = AMARILLO if i == prendida else (70, 50, 0)
            pantalla.fill(color, (int(self.x) + 106 + i * 12, int(self.y) + 88, 8, 6))

    def dibujar_laser(self, pantalla):
        # Un rayo grueso que titila: borde cian y centro blanco
        rayo = self.canon_actual().caja_laser(self)
        ancho = 16 if dibujo.parpadeo(60) else 12
        pantalla.fill(CIAN, (rayo.centerx - ancho // 2, rayo.top - 4, ancho, rayo.height + 4))
        pantalla.fill(BLANCO, (rayo.centerx - 3, rayo.top - 4, 6, rayo.height + 4))

    def dibujar_aviso(self, pantalla, partida, canon):
        boca_x, boca_y = canon.boca(self)
        if canon.ataque == "laser":
            # Siempre avisa: una linea fina y flechas hacia donde va a barrer
            if dibujo.parpadeo(80):
                pantalla.fill(CIAN, (int(boca_x) // 2 * 2 - 1, int(boca_y), 2, ALTO - int(boca_y)))
            for flecha_y in range(int(boca_y) + 60, ALTO - 40, 120):
                for i in range(3):
                    punta_x = int(boca_x + self.barrido * (16 + i * 10)) // 2 * 2
                    pantalla.fill(CIAN, (punta_x, flecha_y - 4, 4, 4))
                    pantalla.fill(CIAN, (punta_x - self.barrido * 4, flecha_y - 8, 4, 4))
                    pantalla.fill(CIAN, (punta_x - self.barrido * 4, flecha_y, 4, 4))
        elif canon.ataque == "minas":
            # Siempre: una X donde va a caer cada mina
            for objetivo_x, objetivo_y in canon.objetivos:
                for paso in range(-8, 9, 4):
                    pantalla.fill(MAGENTA, (int(objetivo_x) + paso - 2, int(objetivo_y) + paso - 2, 4, 4))
                    pantalla.fill(MAGENTA, (int(objetivo_x) + paso - 2, int(objetivo_y) - paso - 2, 4, 4))
        elif not partida.opciones.aviso_jefe or not dibujo.parpadeo(100):
            return
        elif canon.ataque == "rafaga":
            # Hacia donde va a salir el primer obus
            nave_x, nave_y = partida.nave.centro()
            direccion = math.atan2(nave_y - boca_y, nave_x - boca_x)
            for paso in range(24, 161, 16):
                punto_x = boca_x + math.cos(direccion) * paso
                punto_y = boca_y + math.sin(direccion) * paso
                pantalla.fill(ROJO, (int(punto_x) // 2 * 2, int(punto_y) // 2 * 2, 4, 4))
        elif canon.ataque == "misiles":
            # Flechitas amarillas hacia los dos costados
            for lado in (-1, 1):
                for paso in range(1, 4):
                    pantalla.fill(AMARILLO, (int(boca_x + lado * paso * 14) // 2 * 2, int(boca_y + paso * 10), 4, 4))

    def dibujar_aviso_cortina(self, pantalla, hueco):
        # Rayitas rojas donde van a caer los escombros (y el hueco libre)
        for x in range(24, lienzo.ancho, 72):
            if abs(x - hueco) > 90:
                pantalla.fill(ROJO, (x - 8, int(self.y) + 104, 16, 4))
                pantalla.fill(ROJO, (x - 2, int(self.y) + 112, 4, 12))
