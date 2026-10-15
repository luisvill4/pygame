"""
La Serpiente: un jefe de MOVIMIENTO. Casi no dispara: su arma es el cuerpo.

Es una serpiente de cascabel: una cabeza (48x48) y una fila de segmentos (32x32) que
la siguen como una cuerda. Tocar cualquier parte hace daño (el dash lo atraviesa).
Pelea a su ritmo (el pulso), siempre en este orden:

    nadar (6 pulsos)   da vueltas a tu alrededor, buscando el angulo
    acechar (2)        se frena, abre la boca y te apunta (el aviso marca la linea;
                       en el ultimo pulso la direccion queda fija: ¡correte!)
    morder             se lanza en linea recta. Si se estrella contra un borde...
    aturdida (5)       ...queda mareada con el CASCABEL de la cola brillando: ¡DASH a la cola!

Cada corte le saca el ultimo segmento: queda mas corta, mas rapida y con el pulso mas
acelerado. Desde el segundo corte, a veces en vez de morder SE ENROSCA a tu alrededor
(un circulo punteado avisa donde): hay que salir del circulo antes de que apriete,
por el hueco o cruzando el cuerpo con el dash. Desde la mitad, ademas, escupe veneno
(una gota por vez). El ultimo corte la mata.

La vida del jefe son los cortes que faltan (el "nucleo" es la cola), asi la barra del HUD
y el golpe con el dash funcionan como con el Ojo.

Sprites (opcionales, todos mirando hacia arriba):
    serpiente_cabeza.png  96x48: 2 cuadros de 48x48 (boca cerrada, boca abierta), sin los ojos
    serpiente_cuerpo.png  64x32: 2 cuadros de 32x32 (dos dibujos de escamas, se alternan)
    serpiente_cola.png    32x32: el cascabel, con la punta hacia arriba
Los ojos y la lengua se dibujan aparte (los ojos te siguen).
"""
import math
import random

import pygame

from juego import recursos, dibujo
from juego.config import (ANCHO, ALTO, VERDE, AMARILLO, BLANCO, ROJO, HIELO, ORO, MS_POR_FRAME,
                          SERPIENTE_PULSOS, SERPIENTE_VELOCIDAD, SERPIENTE_GIRO, SERPIENTE_MORDIDA,
                          SERPIENTE_ESPACIO, SERPIENTE_CUELLO, SERPIENTE_VENTANA, SERPIENTE_CORTES_EXTRA)
from juego.jefes.base import Jefe, registrar_jefe
from juego.proyectiles import Veneno

CABEZA = 48
LADO_SEGMENTO = 32
VERDE_OSCURO = (0, 90, 40)
VERDE_MEDIO = (20, 170, 80)
ESCAMAS = [(0, 50, 20), VERDE_OSCURO, VERDE, (200, 255, 210)]     # paleta de sus pedazos


# ================================== #
# ======= DIBUJOS DE RESPALDO ====== #
# ================================== #

def cabeza_respaldo(abierta):
    # Cabeza en forma de rombo alargado, mirando hacia arriba (24x24 agrandado x2)
    imagen = pygame.Surface((CABEZA // 2, CABEZA // 2), pygame.SRCALPHA)
    forma = [(12, 1), (18, 5), (21, 12), (18, 20), (12, 23), (6, 20), (3, 12), (6, 5)]
    pygame.draw.polygon(imagen, VERDE, forma)
    pygame.draw.polygon(imagen, VERDE_OSCURO, forma, 1)
    imagen.fill(VERDE_MEDIO, (8, 13, 8, 6))           # mandibula mas oscura
    imagen.fill(AMARILLO, (11, 6, 2, 6))             # la raya de la frente
    imagen.fill(VERDE_OSCURO, (10, 3, 1, 1))         # fosas nasales
    imagen.fill(VERDE_OSCURO, (13, 3, 1, 1))
    if abierta:
        # Boca abierta: la punta se parte y asoman los colmillos
        pygame.draw.polygon(imagen, (60, 0, 20), [(9, 0), (15, 0), (12, 5)])
        imagen.fill(BLANCO, (9, 2, 1, 3))
        imagen.fill(BLANCO, (14, 2, 1, 3))
    return pygame.transform.scale(imagen, (CABEZA, CABEZA))


def segmento_respaldo(rayado):
    # Un anillo verde con escamas (16x16 agrandado x2); hay dos dibujos que se alternan
    imagen = pygame.Surface((LADO_SEGMENTO // 2, LADO_SEGMENTO // 2), pygame.SRCALPHA)
    pygame.draw.circle(imagen, VERDE_OSCURO, (8, 8), 8)
    pygame.draw.circle(imagen, VERDE, (8, 8), 7)
    pygame.draw.circle(imagen, VERDE_MEDIO, (8, 9), 4)
    if rayado:
        pygame.draw.polygon(imagen, AMARILLO, [(8, 4), (11, 8), (8, 12), (5, 8)])
        imagen.fill(VERDE_OSCURO, (8, 8, 1, 1))
    else:
        imagen.fill(AMARILLO, (4, 7, 8, 2))          # una banda (dos puntos parecian ojos)
        imagen.fill((150, 110, 0), (4, 9, 8, 1))
    imagen.fill((200, 255, 210), (4, 3, 2, 1))       # brillo
    return pygame.transform.scale(imagen, (LADO_SEGMENTO, LADO_SEGMENTO))


def cola_respaldo():
    # El cascabel: anillos amarillos que terminan en punta (mirando hacia arriba)
    imagen = pygame.Surface((LADO_SEGMENTO // 2, LADO_SEGMENTO // 2), pygame.SRCALPHA)
    pygame.draw.polygon(imagen, VERDE_OSCURO, [(8, 0), (13, 6), (13, 12), (8, 16), (3, 12), (3, 6)])
    for i, anillo_y in enumerate((2, 6, 10)):
        ancho = 4 + i * 2
        imagen.fill((150, 110, 0), (8 - ancho // 2, anillo_y, ancho, 3))
        imagen.fill(AMARILLO, (8 - ancho // 2, anillo_y, ancho, 2))
    return pygame.transform.scale(imagen, (LADO_SEGMENTO, LADO_SEGMENTO))


_imagenes = {}      # (nombre, variante) -> lista de cuadros


def cuadros(nombre, variante):
    # Cuadros de la cabeza, el cuerpo o la cola, en sus variantes: normal, hielo, blanco y brillo
    if (nombre, "normal") not in _imagenes:
        archivo, ancho, respaldo = {
            "cabeza": ("serpiente_cabeza.png", CABEZA, lambda: [cabeza_respaldo(False), cabeza_respaldo(True)]),
            "cuerpo": ("serpiente_cuerpo.png", LADO_SEGMENTO, lambda: [segmento_respaldo(True),
                                                                       segmento_respaldo(False)]),
            "cola": ("serpiente_cola.png", LADO_SEGMENTO, lambda: [cola_respaldo()]),
        }[nombre]
        normales = recursos.hoja(archivo, ancho) or respaldo()
        _imagenes[(nombre, "normal")] = normales
        _imagenes[(nombre, "hielo")] = [recursos.tenir(c, HIELO) for c in normales]
        _imagenes[(nombre, "blanco")] = [recursos.blanquear(c) for c in normales]
        _imagenes[(nombre, "brillo")] = [recursos.tenir(c, AMARILLO) for c in normales]
    return _imagenes[(nombre, variante)]


def rotar_hacia(imagen, angulo):
    # Las imagenes miran hacia arriba; angulo en radianes (0 = derecha, como atan2)
    return pygame.transform.rotate(imagen, -math.degrees(angulo) - 90)


class Segmento:
    # Un anillo del cuerpo. (x, y) es su CENTRO: sigue al de adelante como una cuerda
    __slots__ = ("x", "y")

    def __init__(self, x, y):
        self.x, self.y = x, y

    def caja(self):
        return pygame.Rect(int(self.x) - 12, int(self.y) - 12, 24, 24)


# ================================== #
# =========== SERPIENTE ============ #
# ================================== #

@registrar_jefe
class Serpiente(Jefe):
    tipo = "serpiente"
    nombre = "LA SERPIENTE"
    apodo = "DEVORADORA DE ESTRELLAS"
    color = VERDE
    ancho = alto = CABEZA
    ms_pulso = SERPIENTE_PULSOS[0]
    fases_congelables = ("nadar", "acechar", "morder", "aturdida", "enroscarse", "mareada")

    @classmethod
    def retrato(cls):
        # Esta hecha de partes: la cabeza la representa
        return cuadros("cabeza", "normal")[0]

    def __init__(self, partida):
        super().__init__(partida)
        self.vida_max = self.vida = self.vida_max + SERPIENTE_CORTES_EXTRA
        # Entra nadando desde la izquierda, con el cuerpo todavia afuera
        self.x, self.y = -CABEZA - 20, ALTO * 0.45
        self.angulo = 0                 # hacia donde mira y nada (radianes)
        centro_x, centro_y = self.centro()
        self.segmentos = [Segmento(centro_x - (i + 1) * SERPIENTE_ESPACIO, centro_y)
                          for i in range(self.vida_max + SERPIENTE_CUELLO)]
        self.orbita = math.pi           # angulo alrededor de la nave al nadar
        self.sentido = random.choice((-1, 1))
        self.mordida = 0                # direccion fija de la mordida
        self.recorrido = 0              # cuanto avanzo mordiendo
        self.ultimo_ataque = "enroscarse"
        self.centro_enrosque = (0, 0)
        self.radio_enrosque = 0
        self.velocidad_dificultad = partida.reglas["velocidad"]

    # ---------- Consultas ----------

    def centro(self):
        return self.x + CABEZA / 2, self.y + CABEZA / 2

    def cola(self):
        return self.segmentos[-1] if self.segmentos else None

    def centro_nucleo(self):
        # El "nucleo" de la Serpiente es su cascabel
        cola = self.cola()
        return (cola.x, cola.y) if cola else self.centro()

    def caja_cuerpo(self):
        return pygame.Rect(int(self.x) + 6, int(self.y) + 6, CABEZA - 12, CABEZA - 12)

    def caja_nucleo(self):
        cola = self.cola()
        return cola.caja().inflate(8, 8) if cola else pygame.Rect(0, 0, 0, 0)

    def cajas_danio(self):
        return [self.caja_cuerpo()] + [segmento.caja() for segmento in self.segmentos]

    def puede_recibir_golpe(self):
        return self.fase in ("aturdida", "mareada") and self.cola() is not None

    def objetos_que_se_mueven(self):
        return [self] + self.segmentos

    def cortes(self):
        return self.vida_max - self.vida

    def factor(self):
        # Mas rapida con cada corte
        return (1 + 0.08 * self.cortes()) * self.velocidad_dificultad

    def punto_cartel_dash(self):
        cola_x, cola_y = self.centro_nucleo()
        return cola_x, cola_y + 34

    def punto_de_explosion(self):
        # Al morir explota de la cola a la cabeza, segmento por segmento
        if self.segmentos and random.random() < 0.5:
            segmento = self.segmentos.pop()
            return segmento.x, segmento.y
        if self.segmentos:
            return self.segmentos[-1].x, self.segmentos[-1].y
        return self.centro()

    # ---------- Movimiento ----------

    def avanzar(self, velocidad):
        self.x += math.cos(self.angulo) * velocidad
        self.y += math.sin(self.angulo) * velocidad

    def girar_hacia(self, objetivo_x, objetivo_y, giro):
        centro_x, centro_y = self.centro()
        deseado = math.atan2(objetivo_y - centro_y, objetivo_x - centro_x)
        diferencia = (deseado - self.angulo + math.pi) % (2 * math.pi) - math.pi
        self.angulo += max(-giro, min(giro, diferencia))

    def arrastrar_cuerpo(self):
        # Cada segmento sigue al de adelante sin alejarse mas de SERPIENTE_ESPACIO (una cuerda)
        anterior_x, anterior_y = self.centro()
        for segmento in self.segmentos:
            lejos_x, lejos_y = segmento.x - anterior_x, segmento.y - anterior_y
            distancia = math.hypot(lejos_x, lejos_y) or 1
            if distancia > SERPIENTE_ESPACIO:
                segmento.x = anterior_x + lejos_x / distancia * SERPIENTE_ESPACIO
                segmento.y = anterior_y + lejos_y / distancia * SERPIENTE_ESPACIO
            anterior_x, anterior_y = segmento.x, segmento.y

    def choco_con_un_borde(self):
        return self.x < 4 or self.x > ANCHO - CABEZA - 4 or self.y < 90 or self.y > ALTO - CABEZA - 4

    def dentro_de_la_pantalla(self):
        self.x = max(4, min(self.x, ANCHO - CABEZA - 4))
        self.y = max(90, min(self.y, ALTO - CABEZA - 4))

    # ---------- Fases ----------

    def actualizar_entrada(self, partida):
        # Entra nadando en zigzag
        self.angulo = math.sin(partida.tiempo / 300) * 0.5
        self.avanzar(2.2)
        self.arrastrar_cuerpo()
        if self.x > ANCHO * 0.3:
            self.al_terminar_de_entrar(partida)

    SONIDO_ENTRADA = "siseo"            # entra nadando en zigzag
    SONIDOS_FASE = {"acechar": "cascabel", "morder": "mordida", "mareada": "mareo", "enroscarse": "enroscar"}
    FASES_VENTANA = ("aturdida", "mareada")

    def al_terminar_de_entrar(self, partida):
        self.empezar_a_nadar(partida)

    def empezar_a_nadar(self, partida):
        # El pulso se acelera con cada corte (de SERPIENTE_PULSOS[0] a [1])
        avance = self.cortes() / max(1, self.vida_max - 1)
        self.ms_pulso = SERPIENTE_PULSOS[0] + (SERPIENTE_PULSOS[1] - SERPIENTE_PULSOS[0]) * avance
        nave_x, nave_y = partida.nave.centro()
        centro_x, centro_y = self.centro()
        self.orbita = math.atan2(centro_y - nave_y, centro_x - nave_x)
        self.cambiar_fase_pulsos("nadar", 6, partida.tiempo)

    def actualizar_fase(self, partida):
        ahora = partida.tiempo
        fase = self.fase
        nave_x, nave_y = partida.nave.centro()
        if fase == "nadar":
            # Da vueltas a tu alrededor, a unos 230 px, buscando el angulo
            self.orbita += 0.012 * self.sentido * self.factor()
            objetivo_x = max(60, min(nave_x + math.cos(self.orbita) * 230, ANCHO - 60))
            objetivo_y = max(130, min(nave_y + math.sin(self.orbita) * 230, ALTO - 60))
            self.girar_hacia(objetivo_x, objetivo_y, SERPIENTE_GIRO * self.factor())
            self.avanzar(SERPIENTE_VELOCIDAD * self.factor())
            self.dentro_de_la_pantalla()
            if self.nuevo_pulso and self.pulso in (2, 4) and self.vida <= self.vida_max / 2:
                self.escupir(partida)
            if self.fin_de_fase(ahora):
                self.elegir_ataque(partida)

        elif fase == "acechar":
            # Se frena y te apunta; en el ultimo pulso la direccion queda fija
            if self.pulso == 0:
                self.girar_hacia(nave_x, nave_y, 0.15)
                centro_x, centro_y = self.centro()
                self.mordida = math.atan2(nave_y - centro_y, nave_x - centro_x)
            self.avanzar(0.6)
            self.dentro_de_la_pantalla()
            if self.fin_de_fase(ahora):
                self.angulo = self.mordida
                self.recorrido = 0
                self.cambiar_fase("morder", 5000, ahora)
                partida.efectos.texto_flotante("¡SSSS!", *self.centro(), VERDE)

        elif fase == "morder":
            velocidad = SERPIENTE_MORDIDA * self.factor()
            self.avanzar(velocidad)
            self.recorrido += velocidad
            if self.choco_con_un_borde():
                self.dentro_de_la_pantalla()
                self.estrellarse(partida)
            elif self.recorrido > ANCHO:
                self.cambiar_fase_pulsos("mareada", SERPIENTE_VENTANA - 1, ahora)

        elif fase == "enroscarse":
            # Da vueltas alrededor de donde estabas, cerrando el circulo hasta apretar
            avance = min(1, (ahora - self.fase_desde) / (self.fase_hasta - self.fase_desde))
            self.radio_enrosque = 220 - 190 * avance
            vuelta = 2 * math.pi / (2 * self.ms_pulso / MS_POR_FRAME)      # una vuelta cada 2 pulsos
            self.orbita += vuelta * self.sentido
            centro_x, centro_y = self.centro_enrosque
            destino_x = centro_x + math.cos(self.orbita) * self.radio_enrosque - CABEZA / 2
            destino_y = centro_y + math.sin(self.orbita) * self.radio_enrosque - CABEZA / 2
            self.angulo = math.atan2(destino_y - self.y, destino_x - self.x)
            self.x += (destino_x - self.x) * 0.35
            self.y += (destino_y - self.y) * 0.35
            if self.fin_de_fase(ahora):
                partida.efectos.texto_flotante("¡SSSS!", *self.centro(), VERDE)
                self.cambiar_fase_pulsos("mareada", SERPIENTE_VENTANA - 1, ahora)

        elif fase in ("aturdida", "mareada"):
            # Mareada: el cascabel brilla y suena (chispitas). ¡Es el momento!
            cola = self.cola()
            if cola is not None and random.random() < 0.3:
                partida.efectos.particula(cola.x + random.randint(-10, 10), cola.y + random.randint(-10, 10),
                                          random.uniform(-1, 1), -1, ORO, 12, 2)
            if self.fin_de_fase(ahora):
                self.empezar_a_nadar(partida)

        self.arrastrar_cuerpo()

    def elegir_ataque(self, partida):
        # Desde el segundo corte, se turna entre morder y enroscarse
        if self.cortes() >= 2 and self.ultimo_ataque == "morder":
            self.ultimo_ataque = "enroscarse"
            self.centro_enrosque = partida.nave.centro()
            nave_x, nave_y = self.centro_enrosque
            centro_x, centro_y = self.centro()
            self.orbita = math.atan2(centro_y - nave_y, centro_x - nave_x)
            self.sentido = random.choice((-1, 1))
            partida.efectos.texto_flotante("¡SSSSSS!", nave_x, nave_y - 60, VERDE)
            self.cambiar_fase_pulsos("enroscarse", 6, partida.tiempo)
        else:
            self.ultimo_ataque = "morder"
            self.cambiar_fase_pulsos("acechar", 2, partida.tiempo)

    def escupir(self, partida):
        # Una gota de veneno hacia la nave (lenta: se esquiva de costado)
        centro_x, centro_y = self.centro()
        nave_x, nave_y = partida.nave.centro()
        direccion = math.atan2(nave_y - centro_y, nave_x - centro_x)
        rapidez = 2.6 * partida.reglas["velocidad"]
        partida.balas.append(Veneno(centro_x, centro_y, math.cos(direccion) * rapidez, math.sin(direccion) * rapidez))
        self.sonar(partida, "escupir", centro_x)

    def estrellarse(self, partida):
        centro_x, centro_y = self.centro()
        partida.efectos.explosion(centro_x, centro_y, ESCAMAS, 24, 6, 4)
        partida.efectos.sacudir(14, VERDE)
        partida.entrada.vibrar("impacto")
        partida.congelar_frames = 4
        self.sonar(partida, "serpiente_choca", centro_x)
        self.cambiar_fase_pulsos("aturdida", SERPIENTE_VENTANA, partida.tiempo)

    def al_recibir_golpe(self, partida):
        # Le cortaste el cascabel: el segmento sale volando y la cola nueva es el anterior
        cola = self.segmentos.pop()
        partida.efectos.pedazos(cola.x, cola.y, ESCAMAS, 14, 5)
        partida.efectos.texto_flotante("¡SSSIII!", cola.x, cola.y - 30, VERDE)
        self.sonar(partida, "corte", cola.x)
        self.sentido = -self.sentido
        self.empezar_a_nadar(partida)

    # ---------- Dibujo ----------

    def variante(self, partida):
        if partida.tiempo < self.golpe_hasta and dibujo.parpadeo(60):
            return "blanco"
        if self.congelado(partida) and (partida.restante("hielo") > 1000 or dibujo.parpadeo(100)):
            return "hielo"
        return "normal"

    def dibujar_cuerpo(self, pantalla, partida):
        variante = self.variante(partida)
        # Del final hacia adelante, asi la cabeza queda encima
        anterior = [self.centro()] + [(s.x, s.y) for s in self.segmentos]
        for i in range(len(self.segmentos) - 1, -1, -1):
            segmento = self.segmentos[i]
            if i == len(self.segmentos) - 1:
                imagen = self.imagen_cola(partida, variante, anterior[i])
            else:
                imagen = cuadros("cuerpo", variante)[i % 2]
            dibujo.pegar(pantalla, imagen, segmento.x, segmento.y, centrado=True)
        abierta = 1 if self.fase in ("acechar", "morder") else 0
        cabeza = rotar_hacia(cuadros("cabeza", variante)[abierta], self.angulo)
        centro_x, centro_y = self.centro()
        dibujo.pegar(pantalla, cabeza, centro_x, centro_y, centrado=True)
        self.dibujar_cara(pantalla, partida)

    def imagen_cola(self, partida, variante, delante):
        # El cascabel apunta para el lado contrario al cuerpo; si se le puede pegar, brilla y tiembla
        cola = self.cola()
        angulo = math.atan2(cola.y - delante[1], cola.x - delante[0])
        if variante == "normal" and self.puede_recibir_golpe() and dibujo.parpadeo(120):
            variante = "brillo"
        if self.puede_recibir_golpe():
            angulo += math.sin(pygame.time.get_ticks() / 30) * 0.3      # el cascabel se sacude
        return rotar_hacia(cuadros("cola", variante)[0], angulo)

    def dibujar_cara(self, pantalla, partida):
        # Los ojos te siguen con la mirada, y cada tanto saca la lengua
        centro_x, centro_y = self.centro()
        adelante_x, adelante_y = math.cos(self.angulo), math.sin(self.angulo)
        derecha_x, derecha_y = -adelante_y, adelante_x
        nave_x, nave_y = partida.nave.centro()
        mirada = math.atan2(nave_y - centro_y, nave_x - centro_x)
        pupila_x, pupila_y = round(math.cos(mirada)) * 2, round(math.sin(mirada)) * 2
        enojada = self.fase in ("acechar", "morder", "enroscarse")
        for lado in (-1, 1):
            ojo_x = int(centro_x + adelante_x * 6 + derecha_x * 9 * lado) // 2 * 2
            ojo_y = int(centro_y + adelante_y * 6 + derecha_y * 9 * lado) // 2 * 2
            if self.fase in ("aturdida", "mareada"):
                # Ojos en cruz: esta mareada
                pantalla.fill(BLANCO, (ojo_x - 4, ojo_y - 1, 8, 2))
                pantalla.fill(BLANCO, (ojo_x - 1, ojo_y - 4, 2, 8))
                continue
            pantalla.fill(ROJO if enojada else AMARILLO, (ojo_x - 3, ojo_y - 3, 6, 6))
            pantalla.fill((20, 0, 0), (ojo_x - 1 + pupila_x, ojo_y - 2 + pupila_y, 2, 4))
        if self.fase not in ("morder", "aturdida", "mareada") and partida.tiempo % 1600 < 220:
            for paso in (28, 32, 36):
                lengua_x = int(centro_x + adelante_x * paso) // 2 * 2
                lengua_y = int(centro_y + adelante_y * paso) // 2 * 2
                pantalla.fill(ROJO, (lengua_x - 1, lengua_y - 1, 2, 2))
            for lado in (-1, 1):
                punta_x = int(centro_x + adelante_x * 40 + derecha_x * 3 * lado) // 2 * 2
                punta_y = int(centro_y + adelante_y * 40 + derecha_y * 3 * lado) // 2 * 2
                pantalla.fill(ROJO, (punta_x - 1, punta_y - 1, 2, 2))

    def dibujar_extra(self, pantalla, partida):
        if self.congelado(partida):
            return
        centro_x, centro_y = self.centro()
        if self.fase == "acechar":
            # La linea de la mordida: titila mas rapido cuando ya quedo fija
            if dibujo.parpadeo(100 if self.pulso == 0 else 50):
                for paso in range(40, 520, 20):
                    punto_x = centro_x + math.cos(self.mordida) * paso
                    punto_y = centro_y + math.sin(self.mordida) * paso
                    pantalla.fill(ROJO, (int(punto_x) // 2 * 2, int(punto_y) // 2 * 2, 4, 4))
        elif self.fase == "enroscarse" and self.pulso <= 1 and dibujo.parpadeo(100):
            # El circulo donde se va a cerrar
            nave_x, nave_y = self.centro_enrosque
            for i in range(36):
                angulo = 2 * math.pi * i / 36
                punto_x = nave_x + math.cos(angulo) * self.radio_enrosque
                punto_y = nave_y + math.sin(angulo) * self.radio_enrosque
                pantalla.fill(VERDE, (int(punto_x) // 2 * 2, int(punto_y) // 2 * 2, 4, 4))
        elif self.fase in ("aturdida", "mareada"):
            # Estrellitas girando sobre la cabeza
            for i in range(3):
                angulo = partida.tiempo / 180 + i * 2.1
                estrella_x = int(centro_x + math.cos(angulo) * 30) // 2 * 2
                estrella_y = int(centro_y - 34 + math.sin(angulo) * 8) // 2 * 2
                pantalla.fill(AMARILLO, (estrella_x - 2, estrella_y - 4, 4, 8))
                pantalla.fill(AMARILLO, (estrella_x - 4, estrella_y - 2, 8, 4))
