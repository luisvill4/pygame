"""
Clase base de los enemigos y su registro.

Patron "registro": cada tipo de enemigo es una clase con el decorador
@registrar_enemigo, que la anota en TIPOS_ENEMIGO con su nombre. El resto del
juego crea enemigos por nombre (crear_enemigos("perseguidor", partida)), asi que
para agregar un enemigo nuevo NO hay que tocar ningun otro archivo:

    1. Crear enemigos/mi_enemigo.py con una clase que herede de Enemigo.
    2. Ponerle @registrar_enemigo, un 'tipo' unico, un 'color', 'nombre' y 'pista'.
    3. Escribir mover(): como cambia su velocidad en cada paso.
    4. Importarlo en enemigos/__init__.py.
    5. Ponerlo en los tramos de guiones.py (cuantos, con que formacion y en que sector).
    (Opcional) sprites/mi_enemigo.png: 2 cuadros de 'tamano' x 'tamano' (40 por defecto).
               Si no esta, se dibuja uno de respaldo.

Todo lo comun ya lo resuelve la clase base: la entrada volando desde un borde (con su
flecha de aviso), la retirada, el congelado del hielo, los bordes, la animacion y el
sprite de respaldo.
Opciones para cada tipo (atributos de la clase):
    tamano, radio          tamaño del dibujo y radio del circulo de daño
    destruible             el dash lo destruye (da 'puntos_dash' y llama a al_destruirse)
    muere_al_chocar        si te pega, se destruye (en vez de reaparecer lejos)
    crear()                si un "enemigo" son varios a la vez (como el enjambre)
Y avisos que la Partida le pregunta (metodos, por defecto "no"):
    hace_danio()           ¿lastima si lo tocas? (el ladron nunca)
    interceptable()        ¿un dash lo frena ahora? (el embestidor cargando)
    bloquea_dash(x, y)     ¿un dash que viene desde (x, y) rebota? (el escudo del escudero)
"""
import math
import random

import pygame

from juego import recursos, dibujo
from juego.config import (ANCHO, ALTO, BLANCO, HIELO, AMARILLO, AVISO_APARICION, DISTANCIA_APARICION, MS_CUADRO_ENEMIGO,
                          PUNTOS_ENEMIGO_CONGELADO, SEPARACION_ENEMIGOS, FUERZA_SEPARACION, RADIO_ENEMIGO,
                          ENEMIGO_VELOCIDAD_MAX, CONTORNO, ENTRADA_ESCUADRON, RETIRADA_VELOCIDAD)

DISTANCIA_PUNTOS_HIELO = 170    # el "+5" de un congelado solo se ve si la nave esta a menos de esto

TIPOS_ENEMIGO = {}          # nombre -> clase


def registrar_enemigo(clase):
    # Decorador: anota la clase en el registro con su nombre
    if not clase.tipo:
        raise ValueError(clase.__name__ + " necesita un 'tipo'")
    TIPOS_ENEMIGO[clase.tipo] = clase
    return clase


def _clase(tipo):
    if tipo not in TIPOS_ENEMIGO:
        raise ValueError("No existe el enemigo '" + tipo + "'. Hay: " + ", ".join(TIPOS_ENEMIGO))
    return TIPOS_ENEMIGO[tipo]


def crear_enemigos(tipo, partida):
    # Lista con los enemigos nuevos de ese tipo (casi siempre uno; el enjambre son varios)
    return _clase(tipo).crear(partida)


def crear_enemigo(tipo, partida):
    # Un solo enemigo (para los tipos que son de a uno)
    return _clase(tipo)(partida)


def lugar_lejos_de_la_nave(nave, tamano):
    # Un lugar al azar lejos de la nave (y fuera del marcador de arriba)
    while True:
        nuevo_x = random.randint(0, ANCHO - tamano)
        nuevo_y = random.randint(70, ALTO - tamano)
        if math.hypot(nuevo_x - nave.x, nuevo_y - nave.y) > DISTANCIA_APARICION:
            return nuevo_x, nuevo_y


def enemigo_respaldo(color, tamano=40):
    # Enemigo dibujado a mano (cuadrado con dos ojos), por si falta su sprite
    imagen = pygame.Surface((40, 40), pygame.SRCALPHA)
    pygame.draw.rect(imagen, color, (4, 4, 32, 32), 4)
    pygame.draw.rect(imagen, color, (12, 14, 6, 6))
    pygame.draw.rect(imagen, color, (22, 14, 6, 6))
    if tamano != 40:
        imagen = pygame.transform.scale(imagen, (tamano, tamano))
    return imagen


def flecha_de_aviso(pantalla, punta_x, punta_y, angulo, color):
    # Dos chevrones ">>" de cuadraditos en la grilla de 2 px, apuntando hacia 'angulo', con la
    # punta en (punta_x, punta_y); el de adelante en el color del enemigo y el de atras mas
    # oscuro (da sensacion de movimiento). Con contorno oscuro: se lee sobre cualquier fondo
    dir_x, dir_y = math.cos(angulo), math.sin(angulo)
    costado_x, costado_y = -dir_y, dir_x
    oscuro = tuple(c // 2 for c in color)
    for atras, tono in ((LARGO_CHEVRON, oscuro), (0, color)):
        cuadros = []
        for paso in range(5):
            for lado in (-1, 1):
                cuadros.append((punta_x - dir_x * (atras + paso * 4) + costado_x * lado * paso * 4,
                                punta_y - dir_y * (atras + paso * 4) + costado_y * lado * paso * 4))
        for relleno, borde in ((CONTORNO, 5), (tono, 3)):
            for x, y in cuadros:
                pantalla.fill(relleno, (dibujo.en_grilla(x) - borde + 1, dibujo.en_grilla(y) - borde + 1,
                                        2 * borde, 2 * borde))


_cuadros = {}               # tipo -> cuadros de la animacion
_congelados = {}            # tipo -> imagen congelada
_retirados = {}             # tipo -> imagen en gris (retirandose)
LARGO_CHEVRON = 14          # px entre los dos chevrones de la flecha de aviso
MARGEN_FLECHA = 48          # px desde el borde hasta la punta de la flecha (entra entera)
FLECHA_ARRIBA, FLECHA_ABAJO = 130, ALTO - 110   # arriba y abajo, fuera de las franjas del HUD


class Enemigo:
    tipo = None                 # nombre unico (lo usan el registro y config.py)
    nombre = ""                 # como se presenta la primera vez ("NUEVO ENEMIGO: ...")
    plural = "ENEMIGOS"         # para los objetivos de los tramos ("ROMPE 3 DIVISORES")
    pista = "ESQUIVALO"         # consejo que se muestra al presentarlo
    color = BLANCO              # color de la "X" de aviso y del dibujo de respaldo
    sonido_roto = "enemigo_roto"    # lo que suena cuando el dash lo rompe (sonido.CATALOGO)
    archivo_sprite = None       # por defecto: tipo + ".png"
    tamano = 40                 # lado del dibujo (y de cada cuadro del sprite)
    radio = RADIO_ENEMIGO       # radio del circulo de daño
    rebota_en_bordes = False    # si no rebota, al tocar un borde se detiene
    destruible = False          # el dash lo destruye
    puntos_dash = 0             # puntos por destruirlo con el dash
    muere_al_chocar = False     # si te pega, se destruye (si no, se retira)
    bonus_propio = False        # su grupo ya tiene su bonus (el enjambre): sin el del escuadron
    esbirro = False             # es de un jefe (ej: las abejas de la Colmena): se va cuando lo vencen

    # ---------- Sprites (compartidos por todos los enemigos del mismo tipo) ----------

    @classmethod
    def cuadros(cls):
        if cls.tipo not in _cuadros:
            hoja = recursos.hoja(cls.archivo_sprite or cls.tipo + ".png", cls.tamano)
            _cuadros[cls.tipo] = hoja if hoja else cls.cuadros_de_respaldo()
        return _cuadros[cls.tipo]

    @classmethod
    def cuadros_de_respaldo(cls):
        # Para las subclases que quieran un dibujo de respaldo propio
        return [enemigo_respaldo(cls.color, cls.tamano)]

    @classmethod
    def imagen_congelado(cls):
        # Version azul del primer cuadro (no necesita sprite)
        if cls.tipo not in _congelados:
            _congelados[cls.tipo] = recursos.tenir(cls.cuadros()[0], HIELO)
        return _congelados[cls.tipo]

    # ---------- Ciclo de vida ----------

    @classmethod
    def crear(cls, partida):
        # Los enemigos nuevos de este tipo (el enjambre lo cambia para crear varios)
        return [cls(partida)]

    def __init__(self, partida):
        self.desfase = random.randint(0, 1000)      # para que no se animen todos al mismo tiempo
        self.escuadron = None       # el grupo con el que llego (escuadrones.py; None = suelto)
        self.entrada = None         # entrando volando: (desde, hasta, cuando arranca); None = ya entro
        self.saliendo = False       # retirandose: vuela hacia afuera y no lastima
        self.naciendo = False       # recien nacido en un lugar (parpadea en vez de mostrar la X)
        self.aturdido_hasta = 0     # aturdido por una onda: quieto y sin lastimar hasta este momento
        self.rumbo = random.uniform(0, 2 * math.pi)     # hacia donde va cuando deambula
        self.reaparecer(partida)

    def reaparecer(self, partida):
        # Lejos de la nave; antes de aparecer se ve una "X" de aviso y no hace nada
        self.x, self.y = lugar_lejos_de_la_nave(partida.nave, self.tamano)
        self.vx, self.vy = 0, 0
        self.aparece_en = partida.tiempo + AVISO_APARICION
        self.naciendo = False
        self.sonar_al_aparecer = True       # (el que entra volando ya sono con su escuadron)
        self.aturdido_hasta = 0
        self.al_aparecer(partida)

    def entrar(self, partida, desde, hasta, demora):
        # Entrar volando desde 'desde' (un punto afuera de la pantalla) hasta 'hasta' (su lugar),
        # como en los juegos de naves. Durante 'demora' ms solo se ve su flecha en el borde (el
        # aviso); despues vuela ENTRADA_ESCUADRON ms sin hacer daño, y recien ahi ataca
        self.x, self.y = desde[0] - self.tamano / 2, desde[1] - self.tamano / 2
        self.vx, self.vy = 0, 0
        self.entrada = (desde, hasta, partida.tiempo + demora)
        self.aparece_en = partida.tiempo + demora + ENTRADA_ESCUADRON
        self.naciendo = False
        self.sonar_al_aparecer = False
        self.saliendo = False
        self.aturdido_hasta = 0
        self.al_aparecer(partida)
        self.al_entrar(partida, hasta)

    def al_entrar(self, partida, hasta):
        # Para las subclases: algo mas que preparar al entrar (el enjambre ubica su bandada)
        pass

    def retirarse(self, partida):
        # Se va volando por el borde mas cercano, sin lastimar (se le termino el turno, te
        # choco, termino el asedio...). Cuando sale de la pantalla, sale del juego
        if self.saliendo:
            return
        if self.entrada is not None:
            if partida.tiempo < self.entrada[2]:
                partida.quitar_enemigo(self)    # (solo se veia la flecha: se va sin que se vea)
                return
            self.entrada = None                 # (venia entrando: pega la vuelta)
        self.saliendo = True
        self.naciendo = False               # (un recien nacido que se va ya no parpadea)
        self.aturdido_hasta = 0
        self.al_retirarse(partida)

    def al_retirarse(self, partida):
        # Para las subclases: que hace al empezar a irse (el ladron suelta la moneda)
        pass

    def nacer_en(self, partida, centro_x, centro_y, espera):
        # Aparecer en un lugar exacto (ej: al partirse un divisor). Durante 'espera' ms
        # parpadea y no hace daño, para que no te golpee apenas nace
        self.x, self.y = centro_x - self.tamano / 2, centro_y - self.tamano / 2
        self.aparece_en = partida.tiempo + espera
        self.naciendo = True

    def al_aparecer(self, partida):
        # Para las subclases: preparar su estado al (re)aparecer
        pass

    def al_destruirse(self, partida, con_dash):
        # Para las subclases: que pasa cuando lo destruyen (ej: el divisor se parte)
        pass

    def al_quitar(self, partida):
        # Para las subclases: se lo saca del juego por cualquier motivo (destruido,
        # retirado, llega el jefe...). Ej: el dron deja su bandada
        pass

    # ---------- Consultas ----------

    def activo(self, tiempo):
        # Ya llego y todavia no se va: ataca, choca y se puede romper
        return tiempo >= self.aparece_en and not self.saliendo

    def hace_danio(self):
        # Para las subclases: un enemigo que por un rato no lastima (ej: una abeja volviendo a casa)
        return True

    def interceptable(self):
        # Para las subclases: ¿un dash lo frena ahora? (ej: el embestidor en plena embestida)
        return False

    def al_interceptar(self, partida):
        # Para las subclases: que hace despues de que lo frenaron con el dash
        pass

    def bloquea_dash(self, desde_x, desde_y):
        # Para las subclases: ¿un dash (o una onda) que llega desde (desde_x, desde_y) choca
        # contra su defensa? Entonces la nave rebota y el no sufre nada (ej: el escudero de frente)
        return False

    def al_bloquear(self, partida):
        # Para las subclases: que hace despues de frenar un dash (ej: el escudo destella)
        pass

    def punto_de_bloqueo(self):
        # Donde saltan las chispas cuando frena un dash (el escudero: el medio del escudo)
        return self.centro()

    def aturdido(self, tiempo):
        return tiempo < self.aturdido_hasta

    def empujar(self, partida, desde_x, desde_y, distancia, ms_aturdido):
        # Una onda lo empuja lejos de (desde_x, desde_y) y lo deja aturdido
        centro_x, centro_y = self.centro()
        lejos_x, lejos_y = centro_x - desde_x, centro_y - desde_y
        largo = math.hypot(lejos_x, lejos_y) or 1
        self.x += lejos_x / largo * distancia
        self.y += lejos_y / largo * distancia
        self.vx, self.vy = 0, 0
        self.aturdido_hasta = partida.tiempo + ms_aturdido
        self._bordes()

    def centro(self):
        return self.x + self.tamano / 2, self.y + self.tamano / 2

    def caja(self):
        # Caja un poco mas chica que el dibujo (para recogerlo congelado o destruirlo con el dash)
        margen = self.tamano // 10
        return pygame.Rect(self.x + margen, self.y + margen, self.tamano - 2 * margen, self.tamano - 2 * margen)

    def rapidez(self, partida, base):
        # La velocidad 'base' ajustada al nivel y la dificultad, pero nunca mas rapida que
        # ENEMIGO_VELOCIDAD_MAX: la nave siempre puede escaparse de los que la persiguen
        return min(base * partida.factor_velocidad(), ENEMIGO_VELOCIDAD_MAX)

    def hacia_la_nave(self, partida):
        # Vector del enemigo a la nave y su largo
        nave_x, nave_y = partida.nave.centro()
        centro_x, centro_y = self.centro()
        dir_x, dir_y = nave_x - centro_x, nave_y - centro_y
        return dir_x, dir_y, math.hypot(dir_x, dir_y)

    # ---------- Movimiento ----------

    def actualizar(self, partida, congelado):
        if self.saliendo:
            self._salir(partida)
            return
        if self.entrada is not None:
            self._entrar_volando(partida)
            return
        if not self.activo(partida.tiempo) or congelado or self.aturdido(partida.tiempo):
            return
        if self.sonar_al_aparecer and not self.naciendo and partida.tiempo - self.aparece_en < 20:
            partida.sonidos.reproducir("aparece", self.x)      # se materializo (termino la "X")
        self.naciendo = False
        self.mover(partida)
        paso = self.paso(partida)
        self.x += self.vx * paso
        self.y += self.vy * paso
        self._bordes()

    def mover(self, partida):
        # Para las subclases: cambiar self.vx / self.vy segun su comportamiento
        raise NotImplementedError

    def _entrar_volando(self, partida):
        # De 'desde' a 'hasta', frenando al final (la curva "ease out": rapido y despues suave)
        desde, hasta, arranca = self.entrada
        if partida.tiempo < arranca:
            return
        avance = min(1, (partida.tiempo - arranca) / ENTRADA_ESCUADRON)
        suave = 1 - (1 - avance) ** 3
        self.x = desde[0] + (hasta[0] - desde[0]) * suave - self.tamano / 2
        self.y = desde[1] + (hasta[1] - desde[1]) * suave - self.tamano / 2
        if avance >= 1:
            self.entrada = None

    def _salir(self, partida):
        # Acelera hacia el borde mas cercano; afuera de la pantalla, sale del juego
        if self.fuera_de_la_pantalla():
            if self.escuadron is not None:
                self.escuadron.escaparon += 1
            partida.quitar_enemigo(self)
            return
        huida_x, huida_y = self.borde_mas_cercano()
        self.vx += (huida_x * RETIRADA_VELOCIDAD - self.vx) * 0.08
        self.vy += (huida_y * RETIRADA_VELOCIDAD - self.vy) * 0.08
        self.x += self.vx
        self.y += self.vy

    def borde_mas_cercano(self):
        # Hacia donde queda el borde mas cercano: (-1, 0), (1, 0), (0, -1) o (0, 1)
        centro_x, centro_y = self.centro()
        distancias = {(-1, 0): centro_x, (1, 0): ANCHO - centro_x, (0, -1): centro_y, (0, 1): ALTO - centro_y}
        return min(distancias, key=distancias.get)

    def fuera_de_la_pantalla(self):
        return self.x <= -self.tamano or self.x >= ANCHO or self.y <= -self.tamano or self.y >= ALTO

    def deambular(self, velocidad=0.5):
        # Despacio y de vez en cuando cambia de rumbo; contra un borde, vuelve hacia el centro
        if random.random() < 0.01:
            self.rumbo = random.uniform(0, 2 * math.pi)
        if self.x <= 0 or self.x >= ANCHO - self.tamano or self.y <= 0 or self.y >= ALTO - self.tamano:
            centro_x, centro_y = self.centro()
            self.rumbo = math.atan2(ALTO / 2 - centro_y, ANCHO / 2 - centro_x)
        self.vx += (math.cos(self.rumbo) * velocidad - self.vx) * 0.05
        self.vy += (math.sin(self.rumbo) * velocidad - self.vy) * 0.05

    def paso(self, partida):
        # Multiplicador de la velocidad al moverse (el rebotador se acelera con el nivel)
        return 1

    def _bordes(self):
        limite_x, limite_y = ANCHO - self.tamano, ALTO - self.tamano
        if self.x < 0 or self.x > limite_x:
            self.vx = -self.vx if self.rebota_en_bordes else 0
        if self.y < 0 or self.y > limite_y:
            self.vy = -self.vy if self.rebota_en_bordes else 0
        self.x = max(0, min(self.x, limite_x))
        self.y = max(0, min(self.y, limite_y))

    def separarse(self, partida):
        # Se aleja de los otros enemigos que tiene muy cerca (mas fuerte mientras mas cerca),
        # para que los que persiguen no terminen todos encimados en el mismo punto
        for otro in partida.enemigos:
            if otro is self or not otro.activo(partida.tiempo):
                continue
            lejos_x = self.x - otro.x
            lejos_y = self.y - otro.y
            distancia = math.hypot(lejos_x, lejos_y)
            if distancia >= SEPARACION_ENEMIGOS:
                continue
            if distancia == 0:
                # Justo en el mismo lugar: se separan hacia un lado al azar
                angulo_azar = random.uniform(0, 2 * math.pi)
                lejos_x, lejos_y, distancia = math.cos(angulo_azar), math.sin(angulo_azar), 1
            fuerza = (1 - distancia / SEPARACION_ENEMIGOS) * FUERZA_SEPARACION
            self.vx += lejos_x / distancia * fuerza
            self.vy += lejos_y / distancia * fuerza

    # ---------- Dibujo ----------

    def dibujar(self, pantalla, partida):
        centro_x, centro_y = (int(c) for c in self.centro())
        if self.saliendo:
            # Retirandose: en gris (ya no lastima)
            dibujo.pegar(pantalla, self.imagen_retirada(), self.x, self.y)
            return
        if self.entrada is not None:
            if partida.tiempo < self.entrada[2]:
                self._dibujar_aviso_de_entrada(pantalla)
            else:
                self.dibujar_animado(pantalla)
            return
        if not self.activo(partida.tiempo):
            if self.naciendo:
                # Recien nacido: parpadea (todavia no hace daño)
                if dibujo.parpadeo(80):
                    self.dibujar_animado(pantalla)
                return
            # Aviso de aparicion: una X parpadeante del color del enemigo
            if dibujo.parpadeo(100):
                lado = max(6, round(self.tamano * 0.35))
                pygame.draw.line(pantalla, self.color, (centro_x - lado, centro_y - lado),
                                 (centro_x + lado, centro_y + lado), 4)
                pygame.draw.line(pantalla, self.color, (centro_x - lado, centro_y + lado),
                                 (centro_x + lado, centro_y - lado), 4)
            return
        restante_hielo = partida.restante("hielo")
        if restante_hielo > 0:
            # Congelado: azul (parpadea al final). Los puntos que da se ven encima solo si
            # la nave esta cerca (con muchos congelados, tantos "+5" llenaban la pantalla)
            if restante_hielo > 1000 or dibujo.parpadeo(100):
                dibujo.pegar(pantalla, self.imagen_congelado(), self.x, self.y)
                nave_x, nave_y = partida.nave.centro()
                if math.hypot(nave_x - centro_x, nave_y - centro_y) < DISTANCIA_PUNTOS_HIELO:
                    dibujo.texto(pantalla, "+" + str(PUNTOS_ENEMIGO_CONGELADO), dibujo.CHICA, HIELO,
                                 centro_x, self.y - 14, sombra=CONTORNO, contorno=CONTORNO)
            else:
                self.dibujar_animado(pantalla)
            return
        self.dibujar_cuerpo(pantalla, partida)
        if self.aturdido(partida.tiempo):
            self._dibujar_estrellitas(pantalla, centro_x, self.y - 6)

    @classmethod
    def imagen_retirada(cls):
        # El primer cuadro en gris oscuro (no necesita sprite): "este ya no es peligroso"
        if cls.tipo not in _retirados:
            _retirados[cls.tipo] = recursos.tenir(cls.cuadros()[0], (90, 90, 120))
        return _retirados[cls.tipo]

    def _dibujar_aviso_de_entrada(self, pantalla):
        # Una flecha en el borde, del color del enemigo, que apunta hacia adentro: "por aca
        # entran". Late (dibujo.parpadeo respeta DESTELLOS REDUCIDOS)
        if not dibujo.parpadeo(120):
            return
        desde_x, desde_y = self.entrada[0]
        hasta_x, hasta_y = self.entrada[1]
        punta_x = max(MARGEN_FLECHA, min(desde_x, ANCHO - MARGEN_FLECHA))
        punta_y = max(FLECHA_ARRIBA, min(desde_y, FLECHA_ABAJO))
        angulo = math.atan2(hasta_y - desde_y, hasta_x - desde_x)
        flecha_de_aviso(pantalla, punta_x, punta_y, angulo, self.color)

    def _dibujar_estrellitas(self, pantalla, centro_x, arriba):
        # Aturdido: tres estrellitas que giran sobre la cabeza (en saltos, estilo retro)
        vuelta = pygame.time.get_ticks() // 120
        for i in range(3):
            angulo = (vuelta + i * 3) % 8 * math.pi / 4
            punto_x = centro_x + round(math.cos(angulo) * self.tamano * 0.35 / 2) * 2
            punto_y = arriba + round(math.sin(angulo) * 2) * 2
            pantalla.fill(AMARILLO, (punto_x - 2, punto_y - 2, 4, 4))

    def dibujar_cuerpo(self, pantalla, partida):
        # Para las subclases que se dibujan distinto segun lo que estan haciendo
        self.dibujar_animado(pantalla)

    def dibujar_animado(self, pantalla):
        dibujo.pegar(pantalla, recursos.cuadro_animado(self.cuadros(), MS_CUADRO_ENEMIGO, self.desfase), self.x, self.y)
