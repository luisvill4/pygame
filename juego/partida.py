"""
Partida: todo el estado de UNA partida y sus reglas.

Reemplaza a las variables globales: la nave, la moneda, los enemigos, el jefe,
los power-ups activos, el puntaje, el combo, el nivel...
Las escenas (Listo, Juego, Explosion) la comparten.

Dos relojes, no mezclarlos:
- self.tiempo: avanza MS_POR_FRAME por frame, SOLO mientras se juega. Lo usan todos
  los temporizadores del juego, asi la pausa, el READY y el hit-stop no los gastan.
- pygame.time.get_ticks(): reloj real, solo para parpadeos y animaciones visuales.

Reglas importantes:
- Todo daño a la nave pasa por danar_jugador().
- Todos los puntos pasan por sumar_puntos() (aplica DOBLE y detecta el record).
- Toda la energia pasa por ganar_energia(): monedas, dash perfectos, enemigos destruidos,
  desafios y oleadas llenan la barra; llena, se sube de nivel.
- Dash perfecto: destruir con el dash a un enemigo destruible o interceptar a uno en pleno
  ataque (_interceptar). _dash_perfecto() premia (una vez por dash): puntos, el combo sigue
  y el dash se recarga casi enseguida.
- Lo que pasa queda anotado en self.estadisticas (Game Over y logros).
- Mejoras (mejoras.py): self.mejoras dice cuantas veces se eligio cada una; las reglas
  las consultan con self.mejora("tipo").
"""
import math
import random

from juego import hud, lienzo
from juego.config import (COMBO_TIEMPO, COMBO_MAXIMO, MS_POR_FRAME, ENERGIA_MONEDA, ENERGIA_COMBO,
                          ENERGIA_PERFECTO, ENERGIA_ENEMIGO, ENERGIA_INICIAL, ENERGIA_POR_NIVEL, ENERGIA_MAXIMA,
                          PUNTOS_ENEMIGO_CONGELADO, NAVE_VELOCIDAD, RECARGA_POR_DESTRUIR,
                          TURBO_VELOCIDAD, DASH_RECARGA, RECARGA_RAPIDA, PRIMER_POWERUP, ESPERA_POWERUP,
                          INVULNERABLE_GOLPE, INVULNERABLE_ESCUDO, JEFE_CADA_NIVELES, JEFE_PUNTOS,
                          DASH_PERFECTO_PUNTOS, DASH_PERFECTO_RECARGA, CADENA_PERFECTOS, CADENA_MAXIMA, MEJORA_RECARGA, MEJORA_ONDA_RADIO,
                          MEJORA_FILO_PUNTOS, MEJORA_ROCE, MEJORA_ROCE_ESCUDO, MEJORA_ATRACCION, MEJORA_COMBO,
                          MEJORA_SUERTE, MEJORA_POTENCIA, MEJORA_MOTOR, FENIX_INVULNERABLE, ATURDIDO_ONDA,
                          EMPUJE_ONDA, NARANJA, NOVA_RADIO, REPETIR_POWERUP, MEJORA_ECO, INTERCEPTAR_PUNTOS,
                          ATURDIDO_INTERCEPTAR, MAGENTA,
                          DIFICULTADES, AMARILLO, BLANCO, CIAN, ROJO, HIELO, ORO, FUEGO, ENERGIA,
                          ESCARCHA, EMBESTIDA, ARCOIRIS)
from juego.nave import Nave
from juego.moneda import Moneda
from juego.jefes import crear_jefe
from juego.progresion import Director
from juego.powerups import TIPOS_POWERUP, Capsula, HASTA_PERDER_VIDA
from juego.proyectiles import mover_balas, dibujar_balas
from juego.interpolacion import Interpolador
from juego.estadisticas import Estadisticas
from juego.mejoras import TIPOS_MEJORA
from juego.eco import Eco
from juego.logros import revisar_logros


class Partida:
    def __init__(self, efectos, sonidos, entrada, records, opciones, dificultad="NORMAL", progreso=None):
        # Servicios que usa (los crea la App y se comparten)
        self.efectos = efectos
        self.sonidos = sonidos
        self.entrada = entrada          # solo para vibrar el mando
        self.opciones = opciones        # se leen en vivo (ej: el aviso del jefe)
        self.progreso = progreso        # logros guardados (None = no se revisan logros)
        # Dificultad: sus reglas (vidas, velocidad, presupuesto...) y su propio record
        self.dificultad = dificultad
        self.reglas = DIFICULTADES[dificultad]
        self.puntaje_maximo = records.maximo(dificultad)

        # Reloj y control
        self.tiempo = 0
        self.congelar_frames = 0        # frames de "hit-stop" (el juego se detiene un instante)
        self.pausa_pendiente = False    # pausar apenas se pueda (se perdio el foco, se desconecto el mando)
        self.termino = False            # la nave exploto: hay que pasar a la escena Explosion
        self.interpolador = Interpolador()  # movimiento suave al dibujar a mas de 60 FPS

        # Jugador y puntaje
        self.nave = Nave()
        self.vidas_max = self.reglas["vidas"]
        self.vidas = self.vidas_max
        self.puntaje = 0
        self.combo = 0                  # monedas seguidas sin dejar pasar mucho tiempo
        self.mejor_combo = 0
        self.ultima_moneda = -10000
        self.energia = 0                # la barra de nivel (ver ganar_energia)
        self.tiempo_energia = -10000    # la ultima vez que se gano (para que la barra destelle)
        self.nivel = 1
        self.record_superado = False
        self.tiempo_cartel_nivel = -10000
        self.tiempo_moneda = -1000      # ultima moneda (para iluminar el puntaje)
        self.tiempo_golpe = -1000       # ultimo golpe (para hacer parpadear las vidas)
        self.estadisticas = Estadisticas()
        self.perfecto_en_este_dash = False  # el dash perfecto se premia una sola vez por dash
        self.tiempo_perfecto = -10000   # ultimo dash perfecto
        self.cadena = 0                 # perfectos seguidos (cada uno antes de CADENA_PERFECTOS)
        self.en_dash_antes = False      # para saber cuando termina un dash
        self.mejoras = {}               # tipo de mejora -> cuantas veces se eligio
        self.perfectos_para_escudo = 0  # cuenta de la mejora ESCUDO ROCE
        self.camino_dash = []           # por donde paso el ultimo dash (para el power-up ECO)
        self.ecos = []                  # copias que repiten un dash (ver eco.py)
        self.ultimo_powerup = None      # el ultimo que cayo (para no repetir tanto)
        self.logros_nuevos = []         # logros desbloqueados en esta partida (ver logros.py)
        self.fichas_logro = []          # [logro, desde]: cuando el HUD muestra la ficha de cada uno
        self.pasos = 0                  # pasos jugados (para revisar los logros cada tanto)

        # Moneda y power-ups
        self.moneda = Moneda()
        self.capsula = None             # power-up cayendo (None = ninguno)
        self.proximo_powerup = PRIMER_POWERUP * self.reglas["espera_powerup"]
        self.activos = {}               # tipo de power-up -> momento en que se acaba

        # Jefe (None = no hay pelea)
        self.jefe = None
        self.jefes_vencidos = 0
        self.tiempo_cartel_jefe = -10000
        self.balas = []

        # Enemigos (durante la pelea con el jefe se guardan aparte). Cuales y cuantos
        # los decide el director (presupuesto, sectores y oleadas: ver progresion.py)
        self.enemigos = []
        self.enemigos_guardados = []
        self.director = Director(self)
        self.director.al_empezar()

    # ================================== #
    # ============ CONSULTAS =========== #
    # ================================== #

    def factor_velocidad(self):
        # Desde el nivel 6 todos los enemigos se aceleran un poco por nivel (y segun la dificultad)
        return min(1 + max(0, self.nivel - 5) * 0.08, 1.5) * self.reglas["velocidad"]

    def mejora(self, tipo):
        # Cuantas veces se eligio esta mejora (0 = no la tenes)
        return self.mejoras.get(tipo, 0)

    def mejoras_elegidas(self):
        # [(tipo, veces)] de las mejoras que tenes, en el orden de mejoras.py
        return [(tipo, self.mejora(tipo)) for tipo in TIPOS_MEJORA if self.mejora(tipo)]

    def espera_powerup(self):
        suerte = (1 - MEJORA_SUERTE) ** self.mejora("suerte")
        return random.randint(*ESPERA_POWERUP) * self.reglas["espera_powerup"] * suerte

    def duracion_powerup(self, duracion):
        # La duracion de un power-up que se recoge (la mejora POTENCIA la alarga)
        if duracion == HASTA_PERDER_VIDA:
            return duracion
        return duracion * (1 + MEJORA_POTENCIA * self.mejora("potencia"))

    def energia_necesaria(self):
        # Lo que hay que juntar para pasar de nivel: un poco mas en cada nivel, con tope
        return min(ENERGIA_INICIAL + (self.nivel - 1) * ENERGIA_POR_NIVEL, ENERGIA_MAXIMA)

    def puede_ganar_energia(self):
        # Durante la pelea con el jefe (y el cierre del sector) no se sube de nivel
        return self.jefe is None and not self.director.cerrando_sector()

    def tiempo_combo(self):
        # ms maximos entre monedas para seguir el combo (la fiebre del oro y COMBO LARGO lo alargan)
        return COMBO_TIEMPO * self.director.factor_combo() * (1 + MEJORA_COMBO * self.mejora("combo"))

    def multiplicador_combo(self):
        # x1 con 1-2 monedas seguidas, x2 con 3-5, x3 con 6-8... hasta x5
        return min(1 + self.combo // 3, COMBO_MAXIMO)

    def activo(self, tipo):
        # ¿Este power-up esta activo?
        return self.tiempo < self.activos.get(tipo, 0)

    def restante(self, tipo):
        # Milisegundos que le quedan (0 si no esta activo)
        return max(0, self.activos.get(tipo, 0) - self.tiempo)

    def activar(self, tipo, duracion):
        if duracion == HASTA_PERDER_VIDA:
            self.activos[tipo] = math.inf
        else:
            self.activos[tipo] = self.tiempo + duracion

    def desactivar(self, tipo):
        self.activos.pop(tipo, None)

    def vel_max(self):
        base = TURBO_VELOCIDAD if self.activo("turbo") else NAVE_VELOCIDAD
        return base * (1 + MEJORA_MOTOR * self.mejora("motor"))

    def recarga_dash(self):
        base = RECARGA_RAPIDA if self.activo("recarga") else DASH_RECARGA
        return base * (1 - MEJORA_RECARGA) ** self.mejora("recarga")

    def puede_destruir(self, enemigo):
        # ¿El dash lo destruye? Los 'destruibles' siempre; con la mejora FILO, todos
        return enemigo.destruible or self.mejora("filo") > 0

    # ================================== #
    # ============= REGLAS ============= #
    # ================================== #

    def sumar_puntos(self, base):
        # Suma puntos (dobles si esta activo DOBLE) y avisa si superas el record
        puntos = base * 2 if self.activo("doble") else base
        self.puntaje += puntos
        if not self.record_superado and self.puntaje_maximo > 0 and self.puntaje > self.puntaje_maximo:
            self.record_superado = True
            self.sonidos.reproducir("nuevo_record")
            nave_x, nave_y = self.nave.centro()
            self.efectos.anillo(nave_x, nave_y, ARCOIRIS, 40, 7, 4)
            self.efectos.texto_flotante("¡NUEVO RECORD!", lienzo.centro_x(), 140, AMARILLO)
        return puntos

    def ganar_energia(self, cantidad):
        # Toda la energia pasa por aca. Con la barra llena se sube de nivel y lo que sobra
        # queda para el siguiente (pero nunca alcanza para saltear un nivel)
        if cantidad <= 0 or not self.puede_ganar_energia():
            return
        self.energia += cantidad
        self.tiempo_energia = self.tiempo
        necesaria = self.energia_necesaria()
        if self.energia < necesaria:
            return
        sobra = self.energia - necesaria
        self.subir_nivel()
        if self.jefe is not None:
            self.energia = 0                    # despues del jefe se empieza con la barra vacia
        else:
            self.energia = min(sobra, self.energia_necesaria() - 1)

    def subir_nivel(self):
        self.nivel += 1
        self.tiempo_cartel_nivel = self.tiempo
        self.sonidos.reproducir("seleccion")
        nave_x, nave_y = self.nave.centro()
        self.efectos.anillo(nave_x, nave_y, ORO, 32, 6)
        self.director.al_subir_nivel()      # sector nuevo cada tanto y mas enemigos
        if self.nivel % JEFE_CADA_NIVELES == 0:
            self.iniciar_jefe()

    def elegir_mejora(self, tipo):
        # Se eligio una carta del Taller: queda para toda la partida
        mejora = TIPOS_MEJORA[tipo]
        self.mejoras[tipo] = self.mejora(tipo) + 1
        mejora.al_elegir(self)
        self.estadisticas.mejoras.append(tipo)
        self.director.ofertas = []
        nave_x, nave_y = self.nave.centro()
        self.efectos.anillo(nave_x, nave_y, [(40, 40, 60), mejora.color, BLANCO], 32, 6)
        self.efectos.texto_flotante(mejora.nombre, nave_x, nave_y - 40, mejora.color)
        self.sonidos.reproducir("powerup")

    def danar_jugador(self, golpe_x, golpe_y):
        # Golpe de un enemigo, del jefe o de una bala: rompe el escudo o quita una vida
        nave = self.nave
        ahora = self.tiempo
        nave_x, nave_y = nave.centro()
        self.sonidos.reproducir("golpe")
        self.director.al_recibir_golpe()        # para el desafio y el rango

        if self.activo("escudo"):
            # El escudo aguanta el golpe y se rompe (medio segundo para alejarse)
            self.desactivar("escudo")
            nave.invulnerable_hasta = ahora + INVULNERABLE_ESCUDO
            nave.vx, nave.vy = nave.empujon(golpe_x, golpe_y, 7)
            self.efectos.anillo(nave_x, nave_y, ENERGIA, 32, 6)
            self.efectos.explosion(golpe_x, golpe_y, FUEGO, 20, 5)
            self.efectos.sacudir(8, CIAN)
            self.entrada.vibrar(0.3, 0.6, 150)
            self.congelar_frames = 2
            return

        self.vidas -= 1
        self.combo = 0
        self.tiempo_golpe = ahora
        # Se pierden los power-ups que duran hasta perder una vida
        aviso_y = nave.y - 10
        for powerup in TIPOS_POWERUP.values():
            if powerup.dura_hasta_perder_vida() and self.activo(powerup.tipo):
                self.desactivar(powerup.tipo)
                self.efectos.texto_flotante("-" + powerup.nombre, nave_x, aviso_y, powerup.color)
                aviso_y -= 24
        nave.vx, nave.vy = nave.empujon(golpe_x, golpe_y)
        nave.invulnerable_hasta = ahora + INVULNERABLE_GOLPE
        self.efectos.explosion(golpe_x, golpe_y, FUEGO, 35, 7, 5)
        self.efectos.sacudir(15, ROJO)
        self.entrada.vibrar(0.7, 1, 300)
        self.congelar_frames = 4

        if self.vidas <= 0 and self.mejora("fenix"):
            # FENIX: vuelve con una vida (y la mejora se gasta: puede volver a salir)
            self.mejoras["fenix"] -= 1
            self.vidas = 1
            nave.invulnerable_hasta = ahora + FENIX_INVULNERABLE
            self.efectos.explosion(nave_x, nave_y, FUEGO, 60, 8, 5)
            self.efectos.anillo(nave_x, nave_y, FUEGO, 40, 7, 4)
            self.efectos.texto_flotante("¡FENIX!", nave_x, nave_y - 40, NARANJA)
            self.sonidos.reproducir("nuevo_record")
            return

        if self.vidas <= 0:
            # Gran explosion de la nave; el Game Over aparece despues
            self.sonidos.parar_musica()
            self.efectos.explosion(nave_x, nave_y, FUEGO, 90, 10, 6)
            self.efectos.explosion(nave_x, nave_y, ORO, 30, 5, 4)
            self.efectos.sacudir(35, BLANCO)
            self.entrada.vibrar(1, 1, 700)
            self.congelar_frames = 8
            self.termino = True
            self._al_terminar()

    def iniciar_jefe(self):
        # Los enemigos explotan y se guardan hasta que venzas al jefe del sector
        tipo = self.director.jefe_del_sector()
        self.director.al_empezar_jefe()     # si habia una oleada, se corta
        self.jefe = crear_jefe(tipo, self)
        self.balas.clear()
        for enemigo in self.enemigos:
            centro_x, centro_y = enemigo.centro()
            self.efectos.explosion(centro_x, centro_y, EMBESTIDA, 20, 4, 3)
        self.enemigos_guardados.extend(self.enemigos)
        self.enemigos.clear()
        self.efectos.sacudir(20)

    def jefe_vencido(self):
        # Gran explosion y bonus de puntos (los enemigos vuelven cuando se va el cartel)
        centro_x, centro_y = self.jefe.centro()
        self.jefe.al_vencerlo(self)
        self.jefe.explotar(self)
        for esbirro in [e for e in self.enemigos if e.esbirro]:     # sus esbirros se van con el
            esbirro_x, esbirro_y = esbirro.centro()
            self.efectos.explosion(esbirro_x, esbirro_y, [(40, 40, 60), esbirro.color], 14, 3, 3)
            self.quitar_enemigo(esbirro)
        self.jefes_vencidos += 1
        ganados = self.sumar_puntos(JEFE_PUNTOS * self.jefes_vencidos)
        self.efectos.texto_flotante("+" + str(ganados), centro_x, centro_y - 40, AMARILLO)
        self.tiempo_cartel_jefe = self.tiempo
        self.jefe = None
        self.balas.clear()
        self.director.al_vencer_al_jefe()      # se pasa al sector siguiente

    # ================================== #
    # =========== CADA FRAME =========== #
    # ================================== #

    def objetos_que_se_mueven(self):
        # Todo lo que se dibuja interpolado (ver interpolacion.py)
        objetos = [self.nave, self.moneda] + self.enemigos + self.balas + self.ecos + self.efectos.particulas
        if self.capsula is not None:
            objetos.append(self.capsula)
        if self.jefe is not None:
            objetos.extend(self.jefe.objetos_que_se_mueven())
        return objetos

    def guardar_posiciones(self):
        # Al empezar cada paso: donde estaba todo (para dibujar los puntos intermedios)
        self.interpolador.guardar(self.objetos_que_se_mueven())

    def actualizar(self, dx, dy, pidio_dash):
        # Un paso de juego (1/60 s): (dx, dy) es hacia donde se quiere mover la nave
        self.guardar_posiciones()
        self.tiempo += MS_POR_FRAME
        vel_max = self.vel_max()
        dash_antes = self.nave.dash_hasta
        self.nave.actualizar(self.tiempo, dx, dy, pidio_dash, vel_max, self.recarga_dash(), self.efectos)
        if self.nave.dash_hasta != dash_antes:
            self._al_empezar_dash()
        en_dash = self.nave.en_dash(self.tiempo)
        if en_dash:
            self.camino_dash.append((self.nave.x, self.nave.y))
        if self.en_dash_antes and not en_dash:
            self._al_terminar_dash()
        self.en_dash_antes = en_dash
        self.ecos = [eco for eco in self.ecos if eco.actualizar(self)]

        # El combo se corta si pasa mucho tiempo sin monedas
        if self.combo > 0 and self.tiempo - self.ultima_moneda > self.tiempo_combo():
            self.combo = 0
        if self.activo("iman"):
            self.moneda.atraer(self.nave, self.efectos)
        elif self.mejora("atraccion"):
            self.moneda.atraer(self.nave, self.efectos, MEJORA_ATRACCION[self.mejora("atraccion") - 1], 4)

        self._revisar_moneda()
        self._actualizar_powerups()
        self.director.actualizar()          # oleadas, anomalias, desafios y rango
        self._devolver_enemigos()
        self._actualizar_enemigos()
        if self.jefe is not None and not self.termino:
            self._actualizar_jefe()
        elif self.balas and not self.termino:
            self._actualizar_balas_sueltas()

        self.nave.estela(self.tiempo, vel_max, self.efectos)
        self.moneda.brillar(self.efectos)
        self.efectos.actualizar()
        self.pasos += 1
        if self.pasos % 30 == 0:
            self.revisar_logros()

    def revisar_logros(self):
        # Cada medio segundo: ¿se cumplio algun logro nuevo? Cada uno tiene su ficha en el
        # HUD, una detras de la otra
        if self.progreso is None:
            return
        for logro in revisar_logros(self, self.progreso):
            desde = self.tiempo
            if self.fichas_logro:
                desde = max(desde, self.fichas_logro[-1][1] + hud.DURACION_FICHA)
            self.fichas_logro.append([logro, desde])
            self.logros_nuevos.append(logro)
            self.sonidos.reproducir("nuevo_record")

    def _al_terminar(self):
        # Game Over: ultima revision de logros y una partida mas en el progreso
        self.revisar_logros()
        if self.progreso is not None:
            self.progreso.partidas += 1
            self.progreso.guardar()

    def _al_empezar_dash(self):
        self.perfecto_en_este_dash = False
        self.camino_dash = []
        self.estadisticas.dashes += 1
        self.director.al_usar_dash()        # (para el desafio "SIN DASH")

    def _al_terminar_dash(self):
        nave_x, nave_y = self.nave.centro()
        # Power-up NOVA: el dash termina en una gran explosion (y se gasta)
        if self.activo("nova"):
            self.desactivar("nova")
            self.onda_expansiva(nave_x, nave_y, NOVA_RADIO)
            self.efectos.explosion(nave_x, nave_y, FUEGO, 60, 9, 6)
            self.efectos.sacudir(14, NARANJA)
            self.entrada.vibrar(0.8, 0.8, 250)
            self.sonidos.reproducir("golpe")
        # Mejora ONDA: al final de cada dash, una onda alrededor de la nave
        elif self.mejora("onda"):
            self.onda_expansiva(nave_x, nave_y, MEJORA_ONDA_RADIO[self.mejora("onda") - 1])
        # Mejora ECO: a veces una copia repite este dash
        if self.camino_dash and self.mejora("eco") and random.random() < MEJORA_ECO[self.mejora("eco") - 1]:
            self.ecos.append(Eco(self.camino_dash, self.nave.angulo))
        self.camino_dash = []

    def onda_expansiva(self, x, y, radio):
        # Rompe las balas, destruye a los enemigos destruibles y empuja (y aturde) a los demas.
        # Al jefe no le hace nada. La usan la mejora ONDA y el power-up NOVA
        self.efectos.anillo(x, y, [(120, 0, 30), NARANJA, AMARILLO, BLANCO], max(16, radio // 4), radio / 12, 4)
        for bala in [b for b in self.balas if math.hypot(b.x - x, b.y - y) < radio]:
            self.balas.remove(bala)
            self.efectos.explosion(bala.x, bala.y, FUEGO, 4, 2, 2)
            if bala.destruible:
                self.sumar_puntos(bala.puntos)
        for enemigo in list(self.enemigos):
            if enemigo not in self.enemigos or not enemigo.activo(self.tiempo):
                continue
            centro_x, centro_y = enemigo.centro()
            if math.hypot(centro_x - x, centro_y - y) > radio + enemigo.tamano / 2:
                continue
            if self.puede_destruir(enemigo):
                self.destruir_con_dash(enemigo)
            else:
                enemigo.empujar(self, x, y, EMPUJE_ONDA, ATURDIDO_ONDA)

    def _dash_perfecto(self, x, y, cartel="¡PERFECTO!", puntos_extra=0):
        # El dash destruyo a un enemigo destruible o freno a uno en pleno ataque: premio
        # (una vez por dash). 'cartel' y 'puntos_extra': la intercepcion usa los suyos
        if self.perfecto_en_este_dash:
            return
        self.perfecto_en_este_dash = True
        # Cadena: si el anterior fue hace poco, esta vale mas
        if self.tiempo - self.tiempo_perfecto < CADENA_PERFECTOS:
            self.cadena += 1
        else:
            self.cadena = 1
        self.tiempo_perfecto = self.tiempo
        self.estadisticas.perfectos += 1
        self.estadisticas.mejor_cadena = max(self.estadisticas.mejor_cadena, self.cadena)
        nave = self.nave
        nave.dash_listo = min(nave.dash_listo, self.tiempo + DASH_PERFECTO_RECARGA)
        if self.combo > 0:
            self.ultima_moneda = self.tiempo        # el combo no se corta
        multiplicador = min(self.cadena, CADENA_MAXIMA)
        ganados = self.sumar_puntos(DASH_PERFECTO_PUNTOS * self.multiplicador_combo() * multiplicador
                                    + puntos_extra)
        nave_x, nave_y = nave.centro()
        self.efectos.anillo(x, y, ENERGIA, 20 + 4 * multiplicador, 5, 3)
        self.efectos.explosion(x, y, [(0, 70, 110), CIAN, BLANCO], 12, 4, 2)
        if self.cadena >= 2:
            cartel = cartel[:-1] + " x" + str(multiplicador) + "!"        # "¡PERFECTO x3!"
        self.efectos.texto_flotante(cartel + " +" + str(ganados), nave_x, nave_y - 34,
                                    CIAN if self.cadena < 2 else AMARILLO)
        self.sonidos.reproducir("seleccion")
        self.entrada.vibrar(0.2, 0.4, 60)
        self.congelar_frames = max(self.congelar_frames, 3)
        self.ganar_energia(ENERGIA_PERFECTO)
        # Mejora ESCUDO ROCE: cada tantos perfectos, un escudo
        if self.mejora("roce"):
            self.perfectos_para_escudo += 1
            if self.perfectos_para_escudo >= MEJORA_ROCE[self.mejora("roce") - 1]:
                self.perfectos_para_escudo = 0
                self.activar("escudo", MEJORA_ROCE_ESCUDO)
                self.efectos.texto_flotante("+ESCUDO", nave_x, nave_y - 60, CIAN)

    def _revisar_moneda(self):
        if not self.nave.caja_recoger().colliderect(self.moneda.caja()):
            return
        ahora = self.tiempo
        self.estadisticas.monedas += 1
        if ahora - self.ultima_moneda < self.tiempo_combo():
            self.combo += 1
        else:
            self.combo = 1
        self.ultima_moneda = ahora
        self.mejor_combo = max(self.mejor_combo, self.combo)
        ganados = self.sumar_puntos(self.multiplicador_combo() * self.director.multiplicador_monedas())
        centro_x, centro_y = self.moneda.centro()
        if self.multiplicador_combo() > 1:
            self.efectos.explosion(centro_x, centro_y, ARCOIRIS, 20, 5, 3)
        else:
            self.efectos.explosion(centro_x, centro_y, ORO, 14, 4, 3)
        self.efectos.texto_flotante("+" + str(ganados), centro_x, self.moneda.y - 6, AMARILLO)
        self.sonidos.reproducir("moneda")
        self.tiempo_moneda = ahora
        self.moneda.mover_a_lugar_nuevo(self)
        self.director.al_recoger_moneda(self.combo)
        # Energia: mas con el combo alto
        self.ganar_energia(ENERGIA_MONEDA + ENERGIA_COMBO * (self.multiplicador_combo() - 1))

    def _actualizar_powerups(self):
        # Cada 8 a 13 segundos cae uno desde arriba; si no lo recoges, se va por abajo
        ahora = self.tiempo
        if self.capsula is None and ahora > self.proximo_powerup:
            self.capsula = Capsula(self.elegir_powerup(), random.randint(30, lienzo.ancho - 30))
        if self.capsula is None:
            return
        self.capsula.caer()
        if self.nave.caja_recoger().colliderect(self.capsula.caja()):
            powerup, x, y = self.capsula.powerup, self.capsula.x, self.capsula.y
            self.sonidos.reproducir("powerup")
            powerup.al_recoger(self, x, y)
            self.director.al_agarrar_powerup()
            self.estadisticas.powerups += 1
            self.efectos.texto_flotante(powerup.texto_al_recoger(), x, y - 24, powerup.color)
            self.capsula = None
            self.proximo_powerup = ahora + self.espera_powerup()
        elif self.capsula.salio():
            self.capsula = None
            self.proximo_powerup = ahora + self.espera_powerup()

    def elegir_powerup(self):
        # Al azar, pero con mas chances para el que mas sirve ahora (peso) y menos para
        # el mismo que cayo recien
        disponibles = [p for p in TIPOS_POWERUP.values() if p.disponible(self)]
        pesos = [p.peso(self) * (REPETIR_POWERUP if p.tipo == self.ultimo_powerup else 1) for p in disponibles]
        elegido = random.choices(disponibles, weights=pesos)[0]
        self.ultimo_powerup = elegido.tipo
        return elegido

    def _devolver_enemigos(self):
        # Despues del jefe, los enemigos vuelven cuando se cierra el sector (cuando se van
        # los carteles de "¡JEFE VENCIDO!" y del rango)
        if self.jefe is not None or not self.enemigos_guardados:
            return
        if self.director.cerrando_sector():
            return
        for enemigo in self.enemigos_guardados:
            enemigo.reaparecer(self)
            self.enemigos.append(enemigo)
        self.enemigos_guardados.clear()
        self.director.al_volver_del_jefe()      # y se completa el presupuesto del nivel

    def _actualizar_enemigos(self):
        ahora = self.tiempo
        congelados = self.activo("hielo")
        for enemigo in self.enemigos:
            enemigo.actualizar(self, congelados)

        nave = self.nave
        caja_nave = nave.caja_recoger()
        for enemigo in list(self.enemigos):         # (una copia: se pueden quitar o agregar enemigos)
            if enemigo not in self.enemigos or not enemigo.activo(ahora):
                continue
            golpe_x, golpe_y = enemigo.centro()        # donde estaba al chocar
            # Recoger (congelado) y destruir con el dash usan la caja grande, mas facil de acertar;
            # el daño a la nave usa los circulos, mas justos
            if congelados and caja_nave.colliderect(enemigo.caja()):
                # Enemigo congelado: lo rompes y ganas puntos (el hielo sigue)
                ganados = self.sumar_puntos(PUNTOS_ENEMIGO_CONGELADO)
                self.ganar_energia(ENERGIA_ENEMIGO)
                self.sonidos.reproducir("moneda")
                self.tiempo_moneda = ahora
                self.efectos.explosion(golpe_x, golpe_y, ESCARCHA, 40, 7, 5)
                self.efectos.texto_flotante("+" + str(ganados), golpe_x, golpe_y - 20, HIELO)
                self.efectos.sacudir(6)
                self.congelar_frames = 3
                if enemigo.destruible:
                    self.destruir_enemigo(enemigo, con_dash=False)
                else:
                    enemigo.reaparecer(self)
            elif congelados or enemigo.aturdido(ahora):
                continue        # (congelado o aturdido no lastima)
            elif self.puede_destruir(enemigo) and nave.en_dash(ahora) and caja_nave.colliderect(enemigo.caja()):
                # El perfecto es solo para los que el dash rompe de por si (con FILO se
                # destruyen todos, pero esos no cuentan)
                perfecto = enemigo.destruible
                self.destruir_con_dash(enemigo)
                if perfecto:
                    self._dash_perfecto(golpe_x, golpe_y)
            elif nave.en_dash(ahora) and enemigo.interceptable() and caja_nave.colliderect(enemigo.caja()):
                self._interceptar(enemigo)
            elif (enemigo.hace_danio() and nave.toca_circulo(golpe_x, golpe_y, enemigo.radio)
                  and not nave.atraviesa(ahora)):
                self.danar_jugador(golpe_x, golpe_y)
                if self.termino:
                    break
                if enemigo.muere_al_chocar:
                    self.efectos.explosion(golpe_x, golpe_y, [(40, 40, 60), enemigo.color], 16, 4, 3)
                    self.destruir_enemigo(enemigo, con_dash=False)
                else:
                    enemigo.reaparecer(self)

    def _interceptar(self, enemigo):
        # Dash contra un enemigo en pleno ataque (el embestidor cargando): lo frena en seco,
        # queda aturdido y da puntos (y es un dash perfecto)
        golpe_x, golpe_y = enemigo.centro()
        enemigo.al_interceptar(self)
        enemigo.vx, enemigo.vy = 0, 0
        enemigo.aturdido_hasta = self.tiempo + ATURDIDO_INTERCEPTAR
        self.efectos.explosion(golpe_x, golpe_y, EMBESTIDA, 24, 6, 4)
        self.efectos.sacudir(8)
        self.sonidos.reproducir("golpe")
        self.estadisticas.interceptados += 1
        self.director.al_interceptar()
        if self.perfecto_en_este_dash:
            # Ya hubo un perfecto en este dash: solo los puntos de la intercepcion
            ganados = self.sumar_puntos(INTERCEPTAR_PUNTOS)
            self.efectos.texto_flotante("¡INTERCEPTADO! +" + str(ganados), golpe_x, golpe_y - 30, MAGENTA)
        else:
            self._dash_perfecto(golpe_x, golpe_y, "¡INTERCEPTADO!", INTERCEPTAR_PUNTOS)

    def destruir_con_dash(self, enemigo):
        # El dash destruye a los enemigos 'destruibles': puntos, chispas, y el dash se recarga un poco
        centro_x, centro_y = enemigo.centro()
        botin = self.mejora("botin")
        ganados = self.sumar_puntos((enemigo.puntos_dash or MEJORA_FILO_PUNTOS) * (1 + botin))
        self.sonidos.reproducir("golpe")
        self.efectos.explosion(centro_x, centro_y, [(40, 40, 60), enemigo.color, BLANCO], 24, 6, 4)
        self.efectos.texto_flotante("+" + str(ganados), centro_x, centro_y - 20, enemigo.color)
        self.efectos.sacudir(4)
        self.entrada.vibrar(0.3, 0.5, 80)
        self.congelar_frames = 2
        self.nave.dash_listo = max(self.tiempo, self.nave.dash_listo - RECARGA_POR_DESTRUIR * (1 + botin))
        self.destruir_enemigo(enemigo, con_dash=True)
        self.estadisticas.enemigos += 1
        self.ganar_energia(ENERGIA_ENEMIGO)
        self.director.al_destruir_enemigo()

    def destruir_enemigo(self, enemigo, con_dash):
        # Lo saca del juego (si es un divisor, antes se parte)
        enemigo.al_destruirse(self, con_dash)
        self.quitar_enemigo(enemigo)

    def quitar_enemigo(self, enemigo):
        # Todo enemigo que sale del juego pasa por aca (destruido, fin de oleada, cambio de sector)
        if enemigo in self.enemigos:
            self.enemigos.remove(enemigo)
        enemigo.al_quitar(self)

    def _actualizar_jefe(self):
        mover_balas(self)
        self.jefe.actualizar(self)
        if self.jefe is not None:
            self._choques_jefe()

    def _choques_jefe(self):
        jefe, nave, ahora = self.jefe, self.nave, self.tiempo
        if nave.en_dash(ahora):
            # Dash contra una parte golpeable o contra el nucleo descubierto
            # (con la caja grande de la nave, para que sea facil acertarle)
            caja = nave.caja_recoger()
            self._destruir_proyectiles(caja)
            parte = jefe.parte_golpeable(caja)
            if parte is not None:
                self._rebotar_en(*parte.centro(jefe))
                jefe.golpear_parte(self, parte)
                return
            if jefe.puede_recibir_golpe() and caja.colliderect(jefe.caja_nucleo()):
                self._rebotar_en(*jefe.centro_nucleo())
                jefe.recibir_golpe(self)
                return
        if jefe.muriendo() or nave.atraviesa(ahora):
            return      # el dash y la invulnerabilidad atraviesan al jefe y sus balas
        if self._tocar_balas():
            return
        # Tocar su cuerpo o sus partes hace daño (congelado no)
        if not jefe.congelado(self) and any(nave.toca_rect(caja) for caja in jefe.cajas_danio()):
            centro_x, centro_y = jefe.centro()
            self.danar_jugador(centro_x, centro_y)

    def _actualizar_balas_sueltas(self):
        # Proyectiles sin jefe (los asteroides de una anomalia): se mueven, el dash
        # rompe los destruibles y los demas lastiman
        mover_balas(self)
        nave, ahora = self.nave, self.tiempo
        if nave.en_dash(ahora):
            self._destruir_proyectiles(nave.caja_recoger())
        if not nave.atraviesa(ahora):
            self._tocar_balas()

    def _tocar_balas(self):
        # Si una bala toca a la nave: se borra, hace daño y devuelve True
        for bala in self.balas:
            if self.nave.toca_circulo(bala.x, bala.y, bala.radio):
                self.balas.remove(bala)
                self.danar_jugador(bala.x, bala.y)
                return True
        return False

    def _destruir_proyectiles(self, caja):
        # Algunos proyectiles (misiles, asteroides) se destruyen con el dash y dan puntos
        for bala in [b for b in self.balas if b.destruible and caja.collidepoint(b.x, b.y)]:
            self.balas.remove(bala)
            ganados = self.sumar_puntos(bala.puntos)
            self.efectos.explosion(bala.x, bala.y, FUEGO, 16, 4, 3)
            self.efectos.texto_flotante("+" + str(ganados), bala.x, bala.y - 20, AMARILLO)
            self.sonidos.reproducir("golpe")
            self.congelar_frames = 2

    def _rebotar_en(self, x, y):
        # Despues de pegarle al jefe, la nave rebota y queda un rato invulnerable
        nave = self.nave
        nave.vx, nave.vy = nave.empujon(x, y, 9)
        nave.dash_hasta = 0
        nave.invulnerable_hasta = self.tiempo + 800     # para alcanzar a alejarse del cuerpo

    # ================================== #
    # ============= DIBUJO ============= #
    # ================================== #

    def dibujar(self, pantalla, con_nave=True, fraccion=1):
        # Todo lo que se ve mientras se juega (el fondo lo dibuja la escena antes).
        # 'fraccion': cuanto del paso actual ya paso (0 a 1), para dibujar interpolado
        with self.interpolador.aplicar(self.objetos_que_se_mueven(), fraccion):
            self._dibujar_todo(pantalla, con_nave)

    def _dibujar_todo(self, pantalla, con_nave):
        self.moneda.dibujar(pantalla)
        if self.capsula is not None:
            self.capsula.dibujar(pantalla)
        for enemigo in self.enemigos:
            enemigo.dibujar(pantalla, self)
        if self.jefe is not None:
            self.jefe.dibujar(pantalla, self)
        dibujar_balas(pantalla, self.balas)
        for eco in self.ecos:
            eco.dibujar(pantalla)
        self.nave.dibujar_fantasmas(pantalla)
        if con_nave:
            self.nave.dibujar(pantalla, self.tiempo, self.restante("escudo"))
        self.efectos.dibujar(pantalla)
        self.director.dibujar_anomalia(pantalla)    # encima de todo (la niebla tapa el juego)
        hud.dibujar(pantalla, self)
