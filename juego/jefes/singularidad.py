"""
La Singularidad: un agujero negro en el centro de la pantalla. Una pelea de CONTROL
DEL ESPACIO: te atrae todo el tiempo (el dash no lo siente: es tu forma de escapar).

La rodea un anillo de asteroides con huecos que gira A SALTOS, un lugar por pulso
(tic, tic, tic...): mirando el ritmo se sabe cuando pasar por un hueco.
Su compas:
    girar (6 pulsos)    suelta brazos de galaxia: dos balas por pulso, en espiral
    inhalar (3)         te tira MUY fuerte (las particulas vuelan hacia el centro). Al final
                        marca con dos lineas donde va a quedar el hueco de la nova...
    exhalar (1)         ...y suelta la nova: un anillo de balas con ese hueco, y un empujon
    colapsar (2)        se achica y el anillo se detiene: "¡COLAPSO!"
    expuesta (6)        el nucleo brilla a la vista: entra por un hueco del anillo (unas
                        flechitas los marcan) y ¡DASH!
    estallido (2)       (si le pegaste) una onda te empuja afuera y el anillo se abre
Cada 2 golpes el anillo tiene un hueco menos y los brazos una bala mas.
Si una moneda cae en el agujero, se la come (y aparece otra en otro lado).

Sprites (opcionales):
    singularidad.png            768x128: 6 cuadros de 128x128 de a pares (girar, inhalar, expuesta)
    singularidad_asteroide.png  64x32:   2 cuadros de 32x32 (dos rocas distintas)
Si faltan, se dibujan de respaldo.
"""
import math
import random

import pygame

from juego import recursos, dibujo, lienzo
from juego.config import (HIELO, CIAN, MAGENTA, BLANCO, ORO, ENERGIA, SINGULARIDAD_PULSO,
                          SINGULARIDAD_GRAVEDAD, SINGULARIDAD_INHALAR, SINGULARIDAD_RADIO, SINGULARIDAD_HUECOS,
                          SINGULARIDAD_EXPUESTA)
from juego.jefes.base import Jefe, registrar_jefe
from juego.proyectiles import Bala

LADO = 128
LADO_ASTEROIDE = 32
LUGARES = 20                    # lugares del anillo (entre dos asteroides no pasa la nave)
CENTRO_Y = 318
VIOLETA = (40, 20, 80)
DISCO = [VIOLETA, (120, 0, 90), HIELO, BLANCO]
ROCA = (110, 120, 160)          # mas claras que las del fondo: estas lastiman
ROCA_OSCURA = (50, 56, 90)


# ================================== #
# ======= DIBUJOS DE RESPALDO ====== #
# ================================== #

def singularidad_respaldo(animo, cuadro):
    # Disco de acrecion y horizonte negro (64x64 agrandado x2). animo: girar, inhalar o expuesta
    imagen = pygame.Surface((LADO // 2, LADO // 2), pygame.SRCALPHA)
    colores = [VIOLETA, (120, 0, 90), (90, 120, 200), HIELO]
    if animo == "inhalar":
        colores = [(80, 0, 60), MAGENTA, (255, 150, 230), BLANCO]
    for i, color in enumerate(colores):
        radio = 30 - i * 4
        pygame.draw.circle(imagen, color, (32, 32), radio)
    # Grumos del disco que giran (cambian de lugar en cada cuadro)
    for i in range(8):
        angulo = i * math.pi / 4 + cuadro * math.pi / 8
        punto = (32 + round(math.cos(angulo) * 25), 32 + round(math.sin(angulo) * 25))
        imagen.fill(BLANCO if i % 2 else colores[2], (*punto, 2, 2))
    if animo == "expuesta":
        pygame.draw.circle(imagen, (0, 0, 0), (32, 32), 12)
        pygame.draw.circle(imagen, CIAN, (32, 32), 9)
        pygame.draw.circle(imagen, BLANCO, (32, 32), 6 if cuadro == 0 else 7)
    else:
        pygame.draw.circle(imagen, BLANCO, (32, 32), 15)        # anillo de fotones
        pygame.draw.circle(imagen, (0, 0, 0), (32, 32), 14)     # el horizonte: nada escapa
    return pygame.transform.scale(imagen, (LADO, LADO))


def asteroide_respaldo(variante):
    imagen = pygame.Surface((LADO_ASTEROIDE // 2, LADO_ASTEROIDE // 2), pygame.SRCALPHA)
    if variante == 0:
        forma = [(4, 1), (11, 1), (15, 6), (14, 12), (8, 15), (2, 12), (1, 5)]
    else:
        forma = [(6, 0), (13, 3), (15, 9), (11, 15), (4, 14), (0, 8), (2, 3)]
    pygame.draw.polygon(imagen, ROCA, forma)
    pygame.draw.polygon(imagen, ROCA_OSCURA, forma, 1)
    imagen.fill(ROCA_OSCURA, (5, 6, 3, 3))          # crateres
    imagen.fill(ROCA_OSCURA, (10, 9, 2, 2))
    imagen.fill((200, 210, 240), (4, 3, 3, 1))      # brillo
    return pygame.transform.scale(imagen, (LADO_ASTEROIDE, LADO_ASTEROIDE))


_asteroides = {}


def cuadros_asteroide(variante):
    if not _asteroides:
        normales = recursos.hoja("singularidad_asteroide.png", LADO_ASTEROIDE)
        if normales is None:
            normales = [asteroide_respaldo(0), asteroide_respaldo(1)]
        if len(normales) < 2:
            normales = [normales[0], normales[0]]
        _asteroides["normal"] = normales
        _asteroides["hielo"] = [recursos.tenir(c, HIELO) for c in normales]
    return _asteroides[variante]


class Asteroide:
    # Una roca del anillo. (x, y) es su centro; lo calcula la Singularidad en cada paso
    __slots__ = ("x", "y", "lugar")

    def __init__(self, lugar):
        self.lugar = lugar          # en cual de los LUGARES del anillo esta
        self.x = self.y = 0

    def caja(self):
        return pygame.Rect(int(self.x) - 15, int(self.y) - 15, 30, 30)


# ================================== #
# ========== SINGULARIDAD ========== #
# ================================== #

@registrar_jefe
class Singularidad(Jefe):
    tipo = "singularidad"
    nombre = "LA SINGULARIDAD"
    apodo = "EL FIN DE LA LUZ"
    color = HIELO
    ancho = alto = LADO
    y_presentacion = 500        # el centro lo ocupa ella
    ms_pulso = SINGULARIDAD_PULSO
    fases_congelables = ("girar", "inhalar", "exhalar", "colapsar", "expuesta", "estallido")

    def __init__(self, partida):
        super().__init__(partida)
        self.x, self.y = lienzo.centro_x() - LADO / 2, CENTRO_Y - LADO / 2
        self.escala = 0                 # al nacer crece desde un punto
        self.angulo_anillo = 0          # cuanto giro el anillo (en lugares)
        self.objetivo_anillo = 0
        self.sentido = 1
        self.radio_anillo = 0
        self.asteroides = []
        self.armar_anillo()
        self.giro_brazos = 0
        self.hueco_nova = 0             # hacia donde queda el hueco de la nova
        self.velocidad_dificultad = partida.reglas["velocidad"]

    @classmethod
    def cargar_animaciones(cls):
        cuadros = recursos.hoja("singularidad.png", LADO)
        if cuadros is None:
            cuadros = [singularidad_respaldo(animo, cuadro)
                       for animo in ("girar", "inhalar", "expuesta") for cuadro in (0, 1)]
        if len(cuadros) >= 6:
            return {"girar": cuadros[0:2], "inhalar": cuadros[2:4], "expuesta": cuadros[4:6]}
        return {"girar": cuadros, "inhalar": cuadros, "expuesta": cuadros}

    # ---------- Consultas ----------

    def golpes(self):
        return self.vida_max - self.vida

    def huecos(self):
        return max(1, SINGULARIDAD_HUECOS - self.golpes() // 2)

    def armar_anillo(self):
        # Los huecos repartidos parejo; el resto, asteroides
        huecos = self.huecos()
        vacios = {round(i * LUGARES / huecos) for i in range(huecos)}
        self.asteroides = [Asteroide(lugar) for lugar in range(LUGARES) if lugar not in vacios]
        self.ubicar_asteroides()

    def ubicar_asteroides(self):
        centro_x, centro_y = self.centro()
        for asteroide in self.asteroides:
            angulo = 2 * math.pi * (asteroide.lugar + self.angulo_anillo) / LUGARES
            asteroide.x = centro_x + math.cos(angulo) * self.radio_anillo
            asteroide.y = centro_y + math.sin(angulo) * self.radio_anillo

    def angulos_huecos(self):
        # Hacia donde quedan los huecos del anillo (para el aviso)
        ocupados = {asteroide.lugar for asteroide in self.asteroides}
        return [2 * math.pi * (lugar + self.angulo_anillo) / LUGARES
                for lugar in range(LUGARES) if lugar not in ocupados]

    def zonas_sin_monedas(self):
        # Ni en el anillo ni adentro (ahi la moneda no se alcanza y se la come enseguida)
        centro_x, centro_y = self.centro()
        lado = int(self.radio_anillo + 30) * 2
        return [pygame.Rect(int(centro_x) - lado // 2, int(centro_y) - lado // 2, lado, lado)]

    def centro_nucleo(self):
        return self.centro()

    def caja_cuerpo(self):
        # El horizonte de sucesos (crece al nacer y se achica al colapsar)
        lado = int(56 * self.escala)
        centro_x, centro_y = self.centro()
        return pygame.Rect(int(centro_x) - lado // 2, int(centro_y) - lado // 2, lado, lado)

    def caja_nucleo(self):
        centro_x, centro_y = self.centro()
        return pygame.Rect(int(centro_x) - 30, int(centro_y) - 30, 60, 60)

    def cajas_danio(self):
        if self.fase == "entrar":
            return []           # mientras nace no lastima
        return [self.caja_cuerpo()] + [asteroide.caja() for asteroide in self.asteroides]

    def puede_recibir_golpe(self):
        return self.fase == "expuesta"

    def objetos_que_se_mueven(self):
        return [self] + self.asteroides

    def punto_cartel_dash(self):
        centro_x, centro_y = self.centro()
        return centro_x, centro_y - 60

    def punto_de_explosion(self):
        if self.asteroides and random.random() < 0.4:
            asteroide = random.choice(self.asteroides)
            return asteroide.x, asteroide.y
        centro_x, centro_y = self.centro()
        return centro_x + random.randint(-40, 40), centro_y + random.randint(-40, 40)

    # ---------- Cada paso ----------

    def actualizar_entrada(self, partida):
        # Nace de un punto: crece mientras el polvo cae hacia el centro
        self.escala = min(1, self.escala + 0.008)
        self.radio_anillo += (SINGULARIDAD_RADIO - self.radio_anillo) * 0.02
        self.chupar_particulas(partida, 2)
        self.ubicar_asteroides()
        if self.escala >= 1:
            self.al_terminar_de_entrar(partida)

    def al_terminar_de_entrar(self, partida):
        self.cambiar_fase_pulsos("girar", 6, partida.tiempo)

    def actualizar_fase(self, partida):
        ahora = partida.tiempo
        fase = self.fase
        if fase == "girar":
            self.atraer(partida, SINGULARIDAD_GRAVEDAD)
            if self.fin_de_fase(ahora):
                self.empezar_a_inhalar(partida)
            elif self.nuevo_pulso:
                self.tic(partida)
                self.soltar_brazos(partida)

        elif fase == "inhalar":
            # Tira fuerte (va subiendo en el primer pulso, asi se siente venir)
            subida = min(1, (ahora - self.fase_desde) / self.ms_pulso)
            self.atraer(partida, SINGULARIDAD_GRAVEDAD + (SINGULARIDAD_INHALAR - SINGULARIDAD_GRAVEDAD) * subida)
            self.chupar_particulas(partida, 3)
            if self.fin_de_fase(ahora):
                self.exhalar(partida)
            elif self.nuevo_pulso:
                self.tic(partida)

        elif fase == "exhalar":
            if self.fin_de_fase(ahora):
                self.cambiar_fase_pulsos("colapsar", 2, ahora)
                partida.efectos.texto_flotante("¡COLAPSO!", *self.centro(), HIELO)

        elif fase == "colapsar":
            self.escala += (0.6 - self.escala) * 0.08
            if self.fin_de_fase(ahora):
                self.cambiar_fase_pulsos("expuesta", SINGULARIDAD_EXPUESTA, ahora)

        elif fase == "expuesta":
            if random.random() < 0.4:
                centro_x, centro_y = self.centro()
                partida.efectos.particula(centro_x + random.randint(-14, 14), centro_y + random.randint(-14, 14),
                                          random.uniform(-1, 1), random.uniform(-1, 1), ENERGIA, 12, 2)
            if self.fin_de_fase(ahora):
                self.volver_a_girar(partida)

        elif fase == "estallido":
            # El anillo se abre (empujado por la onda) y vuelve
            self.radio_anillo += (SINGULARIDAD_RADIO - self.radio_anillo) * 0.05
            if self.fin_de_fase(ahora):
                self.volver_a_girar(partida)

        # El anillo se acomoda (suave) al lugar que le toca; el horizonte recupera su tamaño
        self.angulo_anillo += (self.objetivo_anillo - self.angulo_anillo) * 0.25
        if fase not in ("colapsar", "expuesta"):
            self.escala += (1 - self.escala) * 0.08
        self.ubicar_asteroides()
        self.comer_moneda(partida)

    def tic(self, partida):
        # El anillo avanza un lugar (dos, desde el tercer golpe)
        self.objetivo_anillo += self.sentido * (2 if self.golpes() >= 3 else 1)

    def atraer(self, partida, fuerza):
        # La gravedad tira de la nave hacia el centro (en el dash no la siente)
        nave = partida.nave
        if nave.en_dash(partida.tiempo):
            return
        nave_x, nave_y = nave.centro()
        centro_x, centro_y = self.centro()
        distancia = math.hypot(centro_x - nave_x, centro_y - nave_y) or 1
        nave.vx += (centro_x - nave_x) / distancia * fuerza
        nave.vy += (centro_y - nave_y) / distancia * fuerza

    def chupar_particulas(self, partida, cantidad):
        # Polvo que viene desde los bordes hacia el centro (se ve la fuerza)
        centro_x, centro_y = self.centro()
        for _ in range(cantidad):
            angulo = random.uniform(0, 2 * math.pi)
            distancia = random.randint(250, 420)
            punto_x = centro_x + math.cos(angulo) * distancia
            punto_y = centro_y + math.sin(angulo) * distancia
            partida.efectos.particula(punto_x, punto_y, -math.cos(angulo) * 7, -math.sin(angulo) * 7,
                                      DISCO, 30, 2)

    def soltar_brazos(self, partida):
        # Brazos de galaxia: una bala por brazo y por pulso, girando
        brazos = 2 + (1 if self.golpes() >= 2 else 0)
        rapidez = 2.4 * self.velocidad_dificultad
        centro_x, centro_y = self.centro()
        for brazo in range(brazos):
            angulo = self.giro_brazos + 2 * math.pi * brazo / brazos
            partida.balas.append(Bala(centro_x, centro_y, math.cos(angulo) * rapidez, math.sin(angulo) * rapidez))
        self.giro_brazos += 0.45 * self.sentido

    def empezar_a_inhalar(self, partida):
        self.hueco_nova = random.uniform(0, 2 * math.pi)
        self.cambiar_fase_pulsos("inhalar", 3, partida.tiempo)

    def direcciones_nova(self):
        # 20 balas en circulo, menos 5 seguidas: el hueco (el aviso marca sus bordes)
        direcciones = []
        for i in range(20):
            angulo = self.hueco_nova + math.pi + 2 * math.pi * i / 20
            diferencia = (angulo - self.hueco_nova + math.pi) % (2 * math.pi) - math.pi
            if abs(diferencia) > math.radians(45):
                direcciones.append(angulo)
        return direcciones

    def exhalar(self, partida):
        centro_x, centro_y = self.centro()
        rapidez = 3 * self.velocidad_dificultad
        for angulo in self.direcciones_nova():
            partida.balas.append(Bala(centro_x, centro_y, math.cos(angulo) * rapidez, math.sin(angulo) * rapidez))
        # Y un empujon hacia afuera
        nave = partida.nave
        if not nave.en_dash(partida.tiempo):
            nave_x, nave_y = nave.centro()
            distancia = math.hypot(nave_x - centro_x, nave_y - centro_y) or 1
            nave.vx += (nave_x - centro_x) / distancia * 5
            nave.vy += (nave_y - centro_y) / distancia * 5
        partida.efectos.anillo(centro_x, centro_y, DISCO, 40, 8, 4)
        partida.efectos.sacudir(10, HIELO)
        partida.sonidos.reproducir("golpe")
        self.cambiar_fase_pulsos("exhalar", 1, partida.tiempo)

    def volver_a_girar(self, partida):
        self.cambiar_fase_pulsos("girar", 6, partida.tiempo)

    def al_recibir_golpe(self, partida):
        # Estallido: la onda empuja a la nave afuera, el anillo se abre y cambia de sentido
        centro_x, centro_y = self.centro()
        nave = partida.nave
        nave_x, nave_y = nave.centro()
        lejos_x, lejos_y = nave_x - centro_x, nave_y - centro_y
        distancia = math.hypot(lejos_x, lejos_y)
        if distancia < 1:
            lejos_x, lejos_y, distancia = 0, 1, 1        # justo en el centro: hacia abajo
        nave.vx = lejos_x / distancia * 12
        nave.vy = lejos_y / distancia * 12
        nave.invulnerable_hasta = partida.tiempo + 1200
        partida.efectos.anillo(centro_x, centro_y, ENERGIA, 48, 10, 4)
        self.radio_anillo = SINGULARIDAD_RADIO + 110
        self.sentido = -self.sentido
        self.armar_anillo()                 # cada 2 golpes, un hueco menos
        self.cambiar_fase_pulsos("estallido", 2, partida.tiempo)

    def comer_moneda(self, partida):
        # La moneda tambien cae hacia el agujero; si llega, se la come
        moneda = partida.moneda
        moneda_x, moneda_y = moneda.centro()
        centro_x, centro_y = self.centro()
        distancia = math.hypot(centro_x - moneda_x, centro_y - moneda_y) or 1
        if distancia < 300:
            moneda.x += (centro_x - moneda_x) / distancia * 0.4
            moneda.y += (centro_y - moneda_y) / distancia * 0.4
        if distancia < 36:
            partida.efectos.explosion(moneda_x, moneda_y, ORO, 16, 4, 3)
            moneda.mover_a_lugar_nuevo(partida)

    # ---------- Dibujo ----------

    def animacion(self):
        if self.fase in ("expuesta", "colapsar", "morir"):
            return "expuesta"
        if self.fase in ("inhalar", "exhalar"):
            return "inhalar"
        return "girar"

    def dibujar_cuerpo(self, pantalla, partida):
        imagen = self.imagen_actual(partida)
        lado = max(2, int(LADO * self.escala) // 2 * 2)
        if lado != LADO:
            imagen = pygame.transform.scale(imagen, (lado, lado))
        dibujo_x, dibujo_y = self.posicion_dibujo(partida)
        pantalla.blit(imagen, imagen.get_rect(center=(dibujo_x + LADO // 2, dibujo_y + LADO // 2)))
        variante = "hielo" if self.congelado(partida) else "normal"
        for asteroide in self.asteroides:
            roca = cuadros_asteroide(variante)[asteroide.lugar % 2]
            pantalla.blit(roca, roca.get_rect(center=(int(asteroide.x), int(asteroide.y))))

    def posicion_dibujo(self, partida):
        # No flota: es un agujero en el espacio (al morir tiembla igual)
        if self.temblando():
            return int(self.x) + random.randint(-2, 2) * 2, int(self.y) + random.randint(-2, 2) * 2
        return int(self.x), int(self.y)

    def dibujar_extra(self, pantalla, partida):
        if self.congelado(partida):
            return
        centro_x, centro_y = self.centro()
        if self.fase in ("colapsar", "expuesta"):
            # Flechitas en cada hueco, apuntando hacia el nucleo: "entra por aca"
            vaiven = 6 if dibujo.parpadeo(200) else 0
            for angulo in self.angulos_huecos():
                for fila, ancho in enumerate((4, 12, 20)):
                    distancia = self.radio_anillo + 44 - fila * 4 - vaiven
                    punto_x = centro_x + math.cos(angulo) * distancia
                    punto_y = centro_y + math.sin(angulo) * distancia
                    lado_x, lado_y = -math.sin(angulo), math.cos(angulo)
                    for paso in range(-ancho // 2, ancho // 2 + 1, 4):
                        pantalla.fill(CIAN, (int(punto_x + lado_x * paso) // 2 * 2,
                                             int(punto_y + lado_y * paso) // 2 * 2, 4, 4))
        if self.fase == "inhalar" and self.pulso >= 1 and dibujo.parpadeo(80):
            # Los bordes del hueco de la nova
            for borde in (-45, 45):
                angulo = self.hueco_nova + math.radians(borde)
                for paso in range(70, 330, 16):
                    punto_x = centro_x + math.cos(angulo) * paso
                    punto_y = centro_y + math.sin(angulo) * paso
                    pantalla.fill(CIAN, (int(punto_x) // 2 * 2, int(punto_y) // 2 * 2, 4, 4))
