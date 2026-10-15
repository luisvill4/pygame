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
- Se sube de nivel (un tramo mas de la ruta) al cumplir el OBJETIVO del tramo y despejar
  la zona: lo decide el Director (progresion.py y objetivos.py). La Partida le avisa lo que
  pasa: monedas, enemigos rotos (al_romper), perfectos, intercepciones.
- Los creditos (la plata de la gasolinera) pasan por ganar_creditos() y gastar_creditos().
  Los dan las monedas; no son puntos (gastarlos no baja el puntaje).
- Dash perfecto: destruir con el dash a un enemigo destruible o interceptar a uno en pleno
  ataque (_interceptar). _dash_perfecto() premia (una vez por dash): puntos, el combo sigue
  y el dash se recarga casi enseguida.
- Lo que pasa queda anotado en self.estadisticas (Game Over y logros).
- Mejoras (mejoras.py): self.mejoras dice cuantas veces se eligio cada una; las reglas
  las consultan con self.mejora("tipo").
- Modo desarrollador (escenas/desarrollador.py): si se uso, la partida no guarda record ni
  logros (modo_desarrollador), y con 'invencible' nada le hace daño.
- Los avisos de arriba ("TRAMO 2/4", "¡ASEDIO SUPERADO!"...) pasan por avisar(): salen de a
  uno, en una cola (avisos.py).
- Los enemigos llegan en escuadrones (progresion.py): un enemigo que te choca, o que se rompe
  con el hielo sin ser destruible, se retira (se va volando) en vez de reaparecer.
- La moneda robada (enemigos/ladron.py): robar_moneda, recuperar_moneda, moneda_escapada y
  soltar_moneda. Mientras un ladron la lleva, el reloj del combo espera.
- Un enemigo con defensa (bloquea_dash: el escudo del escudero) hace rebotar el dash y
  frena las ondas y el ECO que le llegan de frente.
"""
import math
import random

from juego import hud, dibujo, carteles, impactos
from juego.config import (ANCHO, COMBO_TIEMPO, COMBO_MAXIMO, MS_POR_FRAME,
                          PUNTOS_ENEMIGO_CONGELADO, NAVE_VELOCIDAD, RECARGA_POR_DESTRUIR,
                          TURBO_VELOCIDAD, DASH_RECARGA, RECARGA_RAPIDA, PRIMER_POWERUP, ESPERA_POWERUP,
                          INVULNERABLE_GOLPE, INVULNERABLE_ESCUDO, JEFE_CADA_NIVELES, JEFE_PUNTOS,
                          DASH_PERFECTO_PUNTOS, DASH_PERFECTO_RECARGA, CADENA_PERFECTOS, CADENA_MAXIMA, MEJORA_RECARGA, MEJORA_ONDA_RADIO,
                          MEJORA_FILO_PUNTOS, MEJORA_ROCE, MEJORA_ATRACCION, MEJORA_COMBO,
                          MEJORA_SUERTE, MEJORA_POTENCIA, MEJORA_MOTOR, FENIX_INVULNERABLE, ATURDIDO_ONDA,
                          EMPUJE_ONDA, NARANJA, NOVA_RADIO, REPETIR_POWERUP, MEJORA_ECO, INTERCEPTAR_PUNTOS,
                          ATURDIDO_INTERCEPTAR, MAGENTA, CREDITOS_POR_MONEDA, ECO_RETRASO, BUFFER_DASH,
                          IMPACTO_PASOS, CAMARA_LENTA_JEFE, LATIDO_MS, AVISO_ULTIMA_VIDA,
                          DIFICULTADES, AMARILLO, BLANCO, CIAN, ROJO, HIELO, ORO, FUEGO, ENERGIA,
                          ESCARCHA, EMBESTIDA, ARCOIRIS, AVISO_RECORD, LADRON_BONUS, VIOLETA)
from juego.avisos import Aviso, ColaDeAvisos
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
    def __init__(self, efectos, sonidos, entrada, records, opciones, dificultad="NORMAL", progreso=None,
                 modo="arcade"):
        # Servicios que usa (los crea la App y se comparten)
        self.efectos = efectos
        self.sonidos = sonidos
        self.entrada = entrada          # solo para vibrar el mando (entrada.vibrar, ver haptica.py)
        self.opciones = opciones        # se leen en vivo (ej: el aviso del jefe)
        self.progreso = progreso        # logros guardados (None = no se revisan logros)
        # Dificultad: sus reglas (vidas, velocidad, presupuesto...) y su propio record
        self.dificultad = dificultad
        self.reglas = DIFICULTADES[dificultad]
        self.modo = modo                # el guion que se juega (guiones.py): "arcade"
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
        self.segmentos_sonados = 0          # segmentos de la barra del jefe que ya sonaron al llenarse
        self.proximo_latido = 0             # cuando late el corazon (con una sola vida y la opcion LATIDO)
        self.tiempo_herida = -100000        # cuando se perdio la ultima vida (la vineta roja)
        self.impacto = None                 # el cuadro de impacto del golpe final (impactos.nuevo_impacto)
        self.camara_lenta = 0               # pasos de camara lenta que quedan (despues del golpe final)
        self.puntaje = 0
        self.puntaje_visible = 0        # el del marcador: cuenta hacia el puntaje de a poco
        self.combo = 0                  # monedas seguidas sin dejar pasar mucho tiempo
        self.mejor_combo = 0
        self.ultima_moneda = -10000
        self.creditos = 0               # la plata de la gasolinera (ver ganar_creditos)
        self.tiempo_creditos = -10000   # la ultima vez que se ganaron (para que el HUD destelle)
        self.nivel = 1
        self.record_superado = False
        self.tiempo_nivel = -10000      # cuando se subio de nivel (el HUD lo destaca)
        self.avisos = ColaDeAvisos()    # los carteles de arriba, de a uno (ver avisar)
        self.tiempo_moneda = -1000      # ultima moneda (para iluminar el puntaje)
        self.tiempo_multiplicador = -10000  # cuando subio el multiplicador del combo (el HUD lo destaca)
        self.tiempo_golpe = -1000       # ultimo golpe (para hacer parpadear las vidas)
        self.estadisticas = Estadisticas()
        self.perfecto_en_este_dash = False  # el dash perfecto se premia una sola vez por dash
        self.tiempo_perfecto = -10000   # ultimo dash perfecto
        self.cadena = 0                 # perfectos seguidos (cada uno antes de CADENA_PERFECTOS)
        self.en_dash_antes = False      # para saber cuando termina un dash
        self.mejoras = {}               # tipo de mejora -> cuantas veces se eligio
        self.perfectos_para_escudo = 0  # cuenta de la mejora ESCUDO ROCE (ver _regenerar_escudo)
        self.camino_dash = []           # por donde paso el ultimo dash (para el power-up ECO)
        self.ecos = []                  # copias que repiten un dash (ver eco.py)
        self.ultimo_powerup = None      # el ultimo que cayo (para no repetir tanto)
        self.logros_nuevos = []         # logros desbloqueados en esta partida (ver logros.py)
        self.fichas_logro = []          # [logro, desde]: cuando el HUD muestra la ficha de cada uno
        self.pasos = 0                  # pasos jugados (para revisar los logros cada tanto)
        self.modo_desarrollador = False # se uso el panel de desarrollador: sin record ni logros
        self.invencible = False         # (modo desarrollador) nada le hace daño

        # Moneda y power-ups
        self.moneda = Moneda()
        self.capsula = None             # power-up cayendo (None = ninguno)
        self.proximo_powerup = PRIMER_POWERUP * self.reglas["espera_powerup"]
        self.activos = {}               # tipo de power-up -> momento en que se acaba

        # Jefe (None = no hay pelea)
        self.jefe = None
        self.jefes_vencidos = 0
        self.tiempo_cartel_jefe = -10000
        self.ultimo_jefe = None         # el ultimo vencido y su premio (para el cartel)
        self.bonus_jefe = 0
        self.balas = []

        # Enemigos: quienes, cuando y como llegan lo decide el director (tramos, escuadrones
        # y el asedio: ver progresion.py)
        self.enemigos = []
        self.director = Director(self, modo)
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
        # Nunca lo acorta: un escudo de ESCUDO ROCE (hasta el golpe) no pasa a durar segundos
        # por agarrar la capsula del escudo
        if duracion == HASTA_PERDER_VIDA:
            hasta = math.inf
        else:
            hasta = self.tiempo + duracion
        self.activos[tipo] = max(hasta, self.activos.get(tipo, 0))

    def desactivar(self, tipo):
        self.activos.pop(tipo, None)

    def vel_max(self):
        base = TURBO_VELOCIDAD if self.activo("turbo") else NAVE_VELOCIDAD
        return base * (1 + MEJORA_MOTOR * self.mejora("motor"))

    def recarga_dash(self):
        base = RECARGA_RAPIDA if self.activo("recarga") else DASH_RECARGA
        return base * (1 - MEJORA_RECARGA) ** self.mejora("recarga")

    def puede_destruir(self, enemigo, desde=None):
        # ¿El dash lo destruye? Los 'destruibles' siempre; con la mejora FILO, todos. Pero si el
        # golpe llega 'desde' (x, y) contra su defensa (el escudo del escudero), no
        if desde is not None and enemigo.bloquea_dash(*desde):
            return False
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
            self.sonidos.reproducir("record")
            self.entrada.vibrar("record")
            nave_x, nave_y = self.nave.centro()
            self.efectos.anillo(nave_x, nave_y, ARCOIRIS, 40, 7, 4)
            self.avisar(Aviso("RECORD", "¡NUEVO RECORD!", "SUPERASTE " + dibujo.numero_arcade(self.puntaje_maximo),
                              None, AVISO_RECORD))
        return puntos

    def ganar_creditos(self, cantidad):
        # Todos los creditos pasan por aca (hoy solo los dan las monedas)
        self.creditos += cantidad
        self.tiempo_creditos = self.tiempo
        self.estadisticas.creditos += cantidad

    def gastar_creditos(self, cantidad):
        # Paga si alcanza (devuelve True) o no hace nada (devuelve False)
        if cantidad > self.creditos:
            return False
        self.creditos -= cantidad
        return True

    def avisar(self, aviso, urgente=False):
        # Un cartel en la franja de arriba. Hace fila detras del que se esta viendo; los
        # urgentes (una amenaza) pasan primero (ver avisos.py)
        self.avisos.agregar(aviso, self.tiempo, urgente)

    def subir_nivel(self, anunciar=True):
        # Un nivel mas = el tramo siguiente de la ruta (el Director lo anuncia con su cartel).
        # 'anunciar' = False: el primer nivel de un sector nuevo (ya sale el cartel del sector)
        self.nivel += 1
        self.tiempo_nivel = self.tiempo
        if anunciar:
            if self.nivel % JEFE_CADA_NIVELES:
                self.sonidos.reproducir("nivel")        # (en el nivel del jefe suena la alerta)
            self.entrada.vibrar("subir_nivel")
            nave_x, nave_y = self.nave.centro()
            self.efectos.anillo(nave_x, nave_y, ORO, 32, 6)
        self.director.al_subir_nivel()      # el tramo nuevo (o, en su nivel, el jefe)
        if self.nivel % JEFE_CADA_NIVELES == 0:
            self.iniciar_jefe()

    def sumar_mejora(self, tipo):
        # La regla: una carta mas de ese tipo, para toda la partida (Taller o gasolinera)
        self.mejoras[tipo] = self.mejora(tipo) + 1
        TIPOS_MEJORA[tipo].al_elegir(self)
        self.estadisticas.mejoras.append(tipo)

    def elegir_mejora(self, tipo):
        # Se eligio una carta del Taller: se suma, se cierra la oferta y se festeja en la nave
        # (la gasolinera usa sumar_mejora: tiene sus propios efectos)
        mejora = TIPOS_MEJORA[tipo]
        self.sumar_mejora(tipo)
        self.director.ofertas = []
        nave_x, nave_y = self.nave.centro()
        self.efectos.anillo(nave_x, nave_y, [(40, 40, 60), mejora.color, BLANCO], 32, 6)
        self.efectos.texto_flotante(mejora.nombre, nave_x, nave_y - 40, mejora.color)
        self.sonidos.reproducir("mejora_elegida")
        self.entrada.vibrar("mejora")

    def danar_jugador(self, golpe_x, golpe_y):
        # Golpe de un enemigo, del jefe o de una bala: rompe el escudo o quita una vida
        if self.invencible:
            return
        nave = self.nave
        ahora = self.tiempo
        nave_x, nave_y = nave.centro()
        self.director.al_recibir_golpe()        # para el desafio y el rango

        if self.activo("escudo"):
            # El escudo aguanta el golpe y se rompe (medio segundo para alejarse)
            self.desactivar("escudo")
            nave.invulnerable_hasta = ahora + INVULNERABLE_ESCUDO
            nave.vx, nave.vy = nave.empujon(golpe_x, golpe_y, 7)
            self.efectos.anillo(nave_x, nave_y, ENERGIA, 32, 6)
            self.efectos.onda_de_choque(nave_x, nave_y, 70, CIAN)
            self.efectos.explosion(golpe_x, golpe_y, FUEGO, 20, 5)
            self.efectos.sacudir(8, CIAN)
            self.sonidos.reproducir("escudo_roto", nave_x)
            self.entrada.vibrar("escudo_roto")
            self.congelar_frames = 2
            return

        self.vidas -= 1
        self.combo = 0
        self.tiempo_golpe = ahora
        self.tiempo_herida = ahora              # la vineta roja (impactos.peligro)
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
        self.efectos.onda_de_choque(nave_x, nave_y, 90, ROJO, 22)
        self.efectos.sacudir(15, ROJO)
        self.entrada.vibrar("golpe")
        self.congelar_frames = 4
        if self.vidas > 0:
            self.sonidos.reproducir("nave_golpe", nave_x)       # (sin vidas suena el FENIX o la explosion)
        if self.vidas == 1 and self.vidas_max > 1:
            self.sonidos.reproducir_luego("ultima_vida", 350)     # te queda una: alarma
            self.avisar(Aviso("PELIGRO", "¡ULTIMA VIDA!", "UN GOLPE MAS Y SE ACABA", ROJO, AVISO_ULTIMA_VIDA,
                              alerta=True), urgente=True)

        if self.vidas <= 0 and self.mejora("fenix"):
            # FENIX: vuelve con una vida (y la mejora se gasta: puede volver a salir)
            self.mejoras["fenix"] -= 1
            self.vidas = 1
            nave.invulnerable_hasta = ahora + FENIX_INVULNERABLE
            self.efectos.explosion(nave_x, nave_y, FUEGO, 60, 8, 5)
            self.efectos.anillo(nave_x, nave_y, FUEGO, 40, 7, 4)
            self.efectos.texto_flotante("¡FENIX!", nave_x, nave_y - 40, NARANJA)
            self.entrada.vibrar("fenix")
            self.sonidos.reproducir("fenix")
            return

        if self.vidas <= 0:
            # Gran explosion de la nave; el Game Over aparece despues
            self.sonidos.parar_musica(fundido=0)       # se corta en seco
            self.sonidos.parar_loops()
            self.sonidos.cancelar_pendientes()
            self.sonidos.reproducir("nave_muerte", nave_x)
            self.efectos.explosion(nave_x, nave_y, FUEGO, 90, 10, 6)
            self.efectos.explosion(nave_x, nave_y, ORO, 30, 5, 4)
            self.efectos.sacudir(35, BLANCO)
            self.entrada.vibrar("muerte")
            self.congelar_frames = 8
            self.termino = True
            self._al_terminar()

    def golpe_final(self, x, y, color):
        # El golpe que mata al jefe: el cuadro de impacto (el juego se congela, el mundo se
        # oscurece y salen rayos del golpe) y despues un rato de camara lenta (lo hace Juego)
        self.impacto = impactos.nuevo_impacto(x, y, color)
        self.congelar_frames = max(self.congelar_frames, IMPACTO_PASOS)
        self.camara_lenta = CAMARA_LENTA_JEFE

    def iniciar_jefe(self, tipo=None):
        # Los enemigos que quedan explotan: el jefe pelea solo. Despues del jefe empieza el
        # sector siguiente, con su propio guion ('tipo' elige otro jefe: el modo desarrollador)
        if tipo is None:
            tipo = self.director.jefe_del_sector()
        self.director.al_empezar_jefe()     # si habia un asedio o una anomalia, se cortan
        self.avisos.vaciar()                # la presentacion del jefe ocupa la pantalla
        self.jefe = crear_jefe(tipo, self)
        self.balas.clear()
        for enemigo in list(self.enemigos):
            centro_x, centro_y = enemigo.centro()
            self.efectos.explosion(centro_x, centro_y, EMBESTIDA, 20, 4, 3)
            self.quitar_enemigo(enemigo)    # (un ladron suelta la moneda)
        self.efectos.sacudir(20)
        self.entrada.vibrar("jefe_llega")        # un latido: llego el jefe
        self.sonidos.reproducir("alerta")       # (la musica se calla: ver Juego.musica)
        self.sonidos.reproducir("franjas")
        self.sonidos.reproducir_luego("presentacion_nombre", hud.MS_ALERTA)
        self.sonidos.reproducir_luego("presentacion_apodo", hud.MS_ALERTA + 160)
        if self.jefe.SONIDO_ENTRADA:
            self.sonidos.reproducir_luego(self.jefe.SONIDO_ENTRADA, 500)
        self.segmentos_sonados = 0

    def jefe_vencido(self):
        # Gran explosion y bonus de puntos (el sector nuevo empieza cuando se va el cartel)
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
        self.ultimo_jefe, self.bonus_jefe = self.jefe, ganados
        self.jefe = None
        self.balas.clear()
        self.sonidos.parar_loops()
        self.sonidos.reproducir_luego("jefe_vencido", 500)
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
        extras_antes = self.nave.dash_extra
        avisado_antes = self.nave.dash_avisado
        self.nave.actualizar(self.tiempo, dx, dy, pidio_dash, vel_max, self.recarga_dash(), self.efectos)
        if self.nave.dash_hasta != dash_antes:
            self._al_empezar_dash(extra=self.nave.dash_extra < extras_antes)
        elif self.nave.dash_avisado and not avisado_antes:
            self.sonidos.reproducir("dash_listo")        # el destello cian: el dash se recargo
        elif pidio_dash and self._dash_vacio():
            self.sonidos.reproducir("dash_vacio")        # "todavia no"
        self._latir()
        en_dash = self.nave.en_dash(self.tiempo)
        if en_dash:
            self.camino_dash.append((self.nave.x, self.nave.y))
        if self.en_dash_antes and not en_dash:
            self._al_terminar_dash()
        self.en_dash_antes = en_dash
        self.ecos = [eco for eco in self.ecos if eco.actualizar(self)]

        # El combo se corta si pasa mucho tiempo sin monedas. Mientras un ladron se lleva la
        # moneda, el reloj del combo espera (si no, perseguirlo no serviria de nada)
        if self.moneda.robada_por is not None:
            self.ultima_moneda += MS_POR_FRAME
        if self.combo > 0 and self.tiempo - self.ultima_moneda > self.tiempo_combo():
            if self.multiplicador_combo() > 1:
                self.sonidos.reproducir("combo_cortado")
            self.combo = 0
        if self.moneda.robada_por is not None:
            pass                # (el iman no se la puede sacar al ladron)
        elif self.activo("iman"):
            self.moneda.atraer(self.nave, self.efectos)
        elif self.mejora("atraccion"):
            self.moneda.atraer(self.nave, self.efectos, MEJORA_ATRACCION[self.mejora("atraccion") - 1], 4)

        self._revisar_moneda()
        self._actualizar_powerups()
        self._avisar_powerups()
        self.director.actualizar()          # escuadrones, asedio, anomalias, desafios y rango
        self.avisos.actualizar(self.tiempo)
        self._actualizar_enemigos()
        if self.jefe is not None and not self.termino:
            self._actualizar_jefe()
        elif self.balas and not self.termino:
            self._actualizar_balas_sueltas()

        self.nave.estela(self.tiempo, vel_max, self.efectos)
        self.moneda.brillar(self.efectos)
        self.efectos.actualizar()
        self._contar_marcador()
        self.pasos += 1
        if self.pasos % 30 == 0:
            self.revisar_logros()

    def _contar_marcador(self):
        # El marcador no salta: cuenta hacia el puntaje real (como en las maquinas). Va en
        # la logica para contar igual a cualquier FPS; lo que falta se recorre en ~6 pasos
        if self.puntaje_visible < self.puntaje:
            self.puntaje_visible += max(1, (self.puntaje - self.puntaje_visible) // 6)
        self.puntaje_visible = min(self.puntaje_visible, self.puntaje)

    def revisar_logros(self):
        # Cada medio segundo: ¿se cumplio algun logro nuevo? Cada uno tiene su ficha en el
        # HUD, una detras de la otra
        if self.progreso is None or self.modo_desarrollador:
            return
        for logro in revisar_logros(self, self.progreso):
            desde = self.tiempo
            if self.fichas_logro:
                desde = max(desde, self.fichas_logro[-1][1] + carteles.DURACION_FICHA)
            self.fichas_logro.append([logro, desde])
            self.logros_nuevos.append(logro)
            demora = max(0, desde - self.tiempo)        # (suena cuando sale su ficha)
            self.sonidos.reproducir_luego("logro", demora)
            if carteles.nave_del_logro(logro) is not None:
                self.sonidos.reproducir_luego("nave_nueva", demora + 900)
            self.entrada.vibrar("logro")

    def _al_terminar(self):
        # Game Over: ultima revision de logros y una partida mas en el progreso
        self.revisar_logros()
        if self.progreso is not None:
            self.progreso.partidas += 1
            self.progreso.guardar()

    def _dash_vacio(self):
        # ¿Pidio el dash y no sale, ni siquiera por el buffer? (falta mas que BUFFER_DASH)
        nave = self.nave
        return (not nave.en_dash(self.tiempo) and nave.dash_extra == 0
                and nave.dash_listo - self.tiempo > BUFFER_DASH)

    def _latir(self):
        # Con una sola vida (y la opcion LATIDO), un latido suave cada 1.6 s
        if self.vidas != 1 or self.vidas_max == 1 or not getattr(self.opciones, "latido", False):
            return
        if self.tiempo >= self.proximo_latido:
            # (en el golpe del latido de la vineta: impactos.peligro usa el mismo LATIDO_MS)
            self.proximo_latido = (self.tiempo // LATIDO_MS + 1) * LATIDO_MS
            self.sonidos.reproducir("latido")

    def _al_empezar_dash(self, extra=False):
        self.sonidos.reproducir("nave_dash_extra" if extra else "nave_dash", self.nave.centro()[0])
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
            self.entrada.vibrar("nova")
            self.sonidos.reproducir("nova", nave_x)
        # Mejora ONDA: al final de cada dash, una onda alrededor de la nave
        elif self.mejora("onda"):
            self.onda_expansiva(nave_x, nave_y, MEJORA_ONDA_RADIO[self.mejora("onda") - 1])
            self.sonidos.reproducir("onda", nave_x)
        # Mejora ECO: a veces una copia repite este dash
        if self.camino_dash and self.mejora("eco") and random.random() < MEJORA_ECO[self.mejora("eco") - 1]:
            self.ecos.append(Eco(self.camino_dash, self.nave.angulo))
            self.sonidos.reproducir_luego("eco", ECO_RETRASO * MS_POR_FRAME, self.camino_dash[0][0])
        self.camino_dash = []

    def onda_expansiva(self, x, y, radio):
        # Rompe las balas, destruye a los enemigos destruibles y empuja (y aturde) a los demas.
        # Al jefe no le hace nada. La usan la mejora ONDA y el power-up NOVA
        self.efectos.anillo(x, y, [(120, 0, 30), NARANJA, AMARILLO, BLANCO], max(16, radio // 4), radio / 12, 4)
        self.efectos.onda_de_choque(x, y, radio, NARANJA, 20)
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
            if self.puede_destruir(enemigo, (x, y)):
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
        self.efectos.onda_de_choque(x, y, 50 + 10 * min(multiplicador, 5), CIAN, 16)
        self.efectos.anillo(x, y, ENERGIA, 20 + 4 * multiplicador, 5, 3)
        self.efectos.explosion(x, y, [(0, 70, 110), CIAN, BLANCO], 12, 4, 2)
        if self.cadena >= 2:
            cartel = cartel[:-1] + " x" + str(multiplicador) + "!"        # "¡PERFECTO x3!"
        self.efectos.texto_flotante(cartel + " +" + str(ganados), nave_x, nave_y - 34,
                                    CIAN if self.cadena < 2 else AMARILLO)
        self.sonidos.reproducir("perfecto_%d" % multiplicador, x)
        self.entrada.vibrar("perfecto", 1 + 0.08 * (multiplicador - 1))    # la cadena vibra un poco mas
        self.congelar_frames = max(self.congelar_frames, 3)
        self.director.al_perfecto()             # (para el objetivo del tramo)
        self._regenerar_escudo()

    def perfectos_para_regenerar(self):
        # Cuantos dash perfectos pide ESCUDO ROCE en su nivel (0 = no la tenes)
        nivel = self.mejora("roce")
        return MEJORA_ROCE[nivel - 1] if nivel else 0

    def _regenerar_escudo(self):
        # Mejora ESCUDO ROCE: con la nave sin escudo, cada perfecto carga uno. Al completarse,
        # el escudo dura hasta el proximo golpe, y despues se vuelve a cargar (toda la partida)
        necesarios = self.perfectos_para_regenerar()
        if not necesarios or self.activo("escudo"):
            return
        self.perfectos_para_escudo += 1
        if self.perfectos_para_escudo < necesarios:
            self.sonidos.reproducir("roce_carga_%d" % min(self.perfectos_para_escudo, 6))
            return
        self.perfectos_para_escudo = 0
        self.activar("escudo", HASTA_PERDER_VIDA)
        nave_x, nave_y = self.nave.centro()
        self.efectos.anillo(nave_x, nave_y, ENERGIA, 32, 6)
        self.efectos.texto_flotante("+ESCUDO", nave_x, nave_y - 60, CIAN)
        self.sonidos.reproducir("pw_escudo", nave_x)

    def _revisar_moneda(self):
        # (la robada no se puede agarrar: hay que alcanzar al ladron con el dash)
        if self.moneda.robada_por is None and self.nave.caja_recoger().colliderect(self.moneda.caja()):
            self._recoger_moneda()

    def _recoger_moneda(self, bonus=0, cartel=""):
        # Cobrar la moneda: combo, puntos y creditos. 'bonus' y 'cartel': la que se
        # le recupera a un ladron (ver recuperar_moneda)
        ahora = self.tiempo
        self.estadisticas.monedas += 1
        multiplicador_antes = self.multiplicador_combo()
        if ahora - self.ultima_moneda < self.tiempo_combo():
            self.combo += 1
        else:
            self.combo = 1
        self.ultima_moneda = ahora
        self.mejor_combo = max(self.mejor_combo, self.combo)
        ganados = self.sumar_puntos(self.multiplicador_combo() * self.director.multiplicador_monedas() + bonus)
        # Creditos: tambien con el combo (jugar bien te hace mas rico), pero no con DOBLE
        self.ganar_creditos(CREDITOS_POR_MONEDA * self.multiplicador_combo() * self.director.multiplicador_monedas())
        centro_x, centro_y = self.moneda.centro()
        if self.multiplicador_combo() > 1:
            self.efectos.explosion(centro_x, centro_y, ARCOIRIS, 20, 5, 3)
        else:
            self.efectos.explosion(centro_x, centro_y, ORO, 14, 4, 3)
        self.efectos.texto_flotante(cartel + "+" + str(ganados), centro_x, self.moneda.y - 6, AMARILLO)
        # La moneda sube de tono con el multiplicador (el oido "lee" el combo)
        self.sonidos.reproducir("moneda_%d" % self.multiplicador_combo(), centro_x)
        if self.director.multiplicador_monedas() > 1:
            self.sonidos.reproducir("oro_brillo", centro_x)
        self._vibrar_moneda(multiplicador_antes)
        if self.multiplicador_combo() > multiplicador_antes:
            self.tiempo_multiplicador = ahora
        self.tiempo_moneda = ahora
        self.moneda.mover_a_lugar_nuevo(self)
        self.director.al_recoger_moneda(self.combo)

    def _vibrar_moneda(self, multiplicador_antes):
        # Cada moneda no vibra (seria todo el tiempo): solo cuando sube el multiplicador
        multiplicador = self.multiplicador_combo()
        if multiplicador > multiplicador_antes and multiplicador == COMBO_MAXIMO:
            self.entrada.vibrar("combo_maximo")
            self.sonidos.reproducir_luego("combo_max", 90)
        elif multiplicador > multiplicador_antes:
            self.entrada.vibrar("combo_sube")
            self.sonidos.reproducir_luego("combo_sube_%d" % min(multiplicador - 1, 3), 90)

    def _actualizar_powerups(self):
        # Cada 8 a 13 segundos cae uno desde arriba; si no lo recoges, se va por abajo
        ahora = self.tiempo
        if self.capsula is None and ahora > self.proximo_powerup:
            self.capsula = Capsula(self.elegir_powerup(), random.randint(30, ANCHO - 30))
            self.sonidos.reproducir("capsula", self.capsula.x)
        if self.capsula is None:
            return
        self.capsula.caer()
        if self.nave.caja_recoger().colliderect(self.capsula.caja()):
            self.recoger_powerup(self.capsula.powerup, self.capsula.x, self.capsula.y)
            self.capsula = None
            self.proximo_powerup = ahora + self.espera_powerup()
        elif self.capsula.salio():
            self.capsula = None
            self.proximo_powerup = ahora + self.espera_powerup()

    def _avisar_powerups(self):
        # A un power-up con tiempo le queda poco: un tic a 1.5, 1 y 0.5 s (cuando parpadea en el
        # HUD); y cuando se termina, su "power-down". (Uno solo por paso)
        for tipo, hasta in self.activos.items():
            if hasta == math.inf:
                continue
            restante = hasta - self.tiempo
            antes = restante + MS_POR_FRAME
            if antes > 0 >= restante:
                self.sonidos.reproducir("pw_fin")
                return
            if any(antes > umbral >= restante for umbral in (1500, 1000, 500)):
                self.sonidos.reproducir("pw_acaba")
                return

    def recoger_powerup(self, powerup, x, y):
        # Agarrar un power-up en (x, y): la capsula, o el modo desarrollador
        self.sonidos.reproducir("pw_" + powerup.tipo, x)
        self.entrada.vibrar("powerup")
        powerup.al_recoger(self, x, y)
        self.efectos.onda_de_choque(x, y, 56, powerup.color, 16)
        self.director.al_agarrar_powerup()
        self.estadisticas.powerups += 1
        self.efectos.texto_flotante(powerup.texto_al_recoger(), x, y - 24, powerup.color)

    def elegir_powerup(self):
        # Al azar, pero con mas chances para el que mas sirve ahora (peso) y menos para
        # el mismo que cayo recien
        disponibles = [p for p in TIPOS_POWERUP.values() if p.disponible(self)]
        pesos = [p.peso(self) * (REPETIR_POWERUP if p.tipo == self.ultimo_powerup else 1) for p in disponibles]
        elegido = random.choices(disponibles, weights=pesos)[0]
        self.ultimo_powerup = elegido.tipo
        return elegido

    def _actualizar_enemigos(self):
        ahora = self.tiempo
        congelados = self.activo("hielo")
        for enemigo in list(self.enemigos):         # (una copia: un ladron que escapa sale del juego)
            if enemigo in self.enemigos:
                enemigo.actualizar(self, congelados)
        if self.moneda.robada_por is not None:
            self.moneda.seguir_al_ladron()

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
                self.sonidos.reproducir("hielo_roto", golpe_x)
                self.tiempo_moneda = ahora
                self.efectos.explosion(golpe_x, golpe_y, ESCARCHA, 40, 7, 5)
                self.efectos.texto_flotante("+" + str(ganados), golpe_x, golpe_y - 20, HIELO)
                self.efectos.sacudir(6)
                self.entrada.vibrar("hielo_roto")
                self.congelar_frames = 3
                if enemigo.destruible:
                    self.director.al_romper(enemigo)
                    self.destruir_enemigo(enemigo, con_dash=False)
                else:
                    enemigo.retirarse(self)     # se va (no se puede romper)
            elif congelados or enemigo.aturdido(ahora):
                continue        # (congelado o aturdido no lastima)
            elif (nave.en_dash(ahora) and caja_nave.colliderect(enemigo.caja())
                  and enemigo.bloquea_dash(*nave.centro())):
                self._rebotar_en_escudo(enemigo)
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
                    enemigo.retirarse(self)     # te pego y se va (como en los juegos de naves)

    def _interceptar(self, enemigo):
        # Dash contra un enemigo en pleno ataque (el embestidor cargando): lo frena en seco,
        # queda aturdido y da puntos (y es un dash perfecto)
        golpe_x, golpe_y = enemigo.centro()
        enemigo.al_interceptar(self)
        enemigo.vx, enemigo.vy = 0, 0
        enemigo.aturdido_hasta = self.tiempo + ATURDIDO_INTERCEPTAR
        self.efectos.explosion(golpe_x, golpe_y, EMBESTIDA, 24, 6, 4)
        self.efectos.sacudir(8)
        self.sonidos.reproducir("interceptado", golpe_x)
        self.sonidos.reproducir("aturdido", golpe_x)
        self.entrada.vibrar("interceptar")
        self.estadisticas.interceptados += 1
        self.director.al_interceptar()
        if self.perfecto_en_este_dash:
            # Ya hubo un perfecto en este dash: solo los puntos de la intercepcion
            ganados = self.sumar_puntos(INTERCEPTAR_PUNTOS)
            self.efectos.texto_flotante("¡INTERCEPTADO! +" + str(ganados), golpe_x, golpe_y - 30, MAGENTA)
        else:
            self._dash_perfecto(golpe_x, golpe_y, "¡INTERCEPTADO!", INTERCEPTAR_PUNTOS)

    def _rebotar_en_escudo(self, enemigo):
        # Dash contra una defensa (el escudo del escudero de frente): la nave rebota como contra
        # un jefe y nadie sufre nada
        chispa_x, chispa_y = enemigo.punto_de_bloqueo()
        self._rebotar_en(*enemigo.centro())
        enemigo.al_bloquear(self)
        self.efectos.explosion(chispa_x, chispa_y, [(90, 50, 0), enemigo.color, BLANCO], 14, 5, 2)
        self.efectos.onda_de_choque(chispa_x, chispa_y, 40, BLANCO, 12)
        self.efectos.sacudir(5)
        self.sonidos.reproducir("escudo_bloquea", chispa_x)
        self.entrada.vibrar("bloqueo")
        self.congelar_frames = max(self.congelar_frames, 2)

    def robar_moneda(self, ladron):
        # Un ladron agarro la moneda: se la lleva encima (ver Moneda.seguir_al_ladron)
        self.moneda.robada_por = ladron
        centro_x, centro_y = self.moneda.centro()
        self.efectos.explosion(centro_x, centro_y, [(40, 20, 70), VIOLETA, AMARILLO], 10, 3, 2)
        self.efectos.texto_flotante("¡ROBADA!", centro_x, centro_y - 30, VIOLETA)
        self.sonidos.reproducir("ladron_roba", centro_x)

    def recuperar_moneda(self, ladron):
        # Alcanzaste al ladron: la moneda se cobra en el momento, con bonus, y el combo sigue
        self.moneda.robada_por = None
        self.sonidos.reproducir("moneda_recuperada", self.moneda.centro()[0])
        self.estadisticas.recuperadas += 1
        self._recoger_moneda(LADRON_BONUS, "¡RECUPERADA! ")

    def moneda_escapada(self, ladron):
        # El ladron salio de la pantalla con la moneda: se corta el combo y la moneda aparece
        # en otro lugar. El ladron se va (cuenta como que se escapo de su escuadron)
        self.moneda.robada_por = None
        self.combo = 0
        self.sonidos.reproducir("ladron_escapa", max(0, min(ladron.centro()[0], ANCHO)))
        self.entrada.vibrar("robo_escapa")
        nave_x, nave_y = self.nave.centro()
        self.efectos.texto_flotante("¡SE LLEVO LA MONEDA!", nave_x, nave_y - 40, VIOLETA)
        self.moneda.mover_a_lugar_nuevo(self)
        if ladron.escuadron is not None:
            ladron.escuadron.escaparon += 1
        self.quitar_enemigo(ladron)

    def soltar_moneda(self):
        # El ladron sale del juego por otra cosa (se retira, llega el jefe...): la
        # moneda vuelve a otro lugar sin castigo
        if self.moneda.robada_por is not None:
            self.moneda.robada_por = None
            self.moneda.mover_a_lugar_nuevo(self)

    def destruir_con_dash(self, enemigo):
        # El dash destruye a los enemigos 'destruibles': puntos, chispas, y el dash se recarga un poco
        centro_x, centro_y = enemigo.centro()
        botin = self.mejora("botin")
        ganados = self.sumar_puntos((enemigo.puntos_dash or MEJORA_FILO_PUNTOS) * (1 + botin))
        self.sonidos.reproducir(enemigo.sonido_roto, centro_x)
        self.efectos.explosion(centro_x, centro_y, [(40, 40, 60), enemigo.color, BLANCO], 24, 6, 4)
        self.efectos.onda_de_choque(centro_x, centro_y, 36 + enemigo.tamano // 2, enemigo.color, 14)
        self.efectos.texto_flotante("+" + str(ganados), centro_x, centro_y - 20, enemigo.color)
        self.efectos.sacudir(4)
        self.entrada.vibrar("destruir")
        self.congelar_frames = 2
        self.nave.dash_listo = max(self.tiempo, self.nave.dash_listo - RECARGA_POR_DESTRUIR * (1 + botin))
        self.destruir_enemigo(enemigo, con_dash=True)
        self.estadisticas.enemigos += 1
        self.director.al_romper(enemigo)
        self.director.al_destruir_enemigo()

    def destruir_enemigo(self, enemigo, con_dash):
        # Lo saca del juego (si es un divisor, antes se parte)
        enemigo.al_destruirse(self, con_dash)
        self.quitar_enemigo(enemigo)

    def quitar_enemigo(self, enemigo):
        # Todo enemigo que sale del juego pasa por aca (destruido, retirado, llega el jefe)
        if enemigo in self.enemigos:
            self.enemigos.remove(enemigo)
        enemigo.al_quitar(self)

    def _actualizar_jefe(self):
        mover_balas(self)
        antes = len(self.balas)
        self.jefe.actualizar(self)
        self._llenar_barra_del_jefe()
        # Cada bala que acaba de disparar nace con un destello (como mucho unas pocas por paso)
        for bala in self.balas[antes:antes + 6]:
            self.efectos.fogonazo(bala.x, bala.y, bala.brillo or BLANCO)
        if self.jefe is not None:
            self._choques_jefe()

    def _llenar_barra_del_jefe(self):
        # Al terminar la presentacion, la barra se llena de a un segmento (hud._barra_jefe):
        # un tic por segmento, subiendo por Re menor (como en los juegos de pelea)
        jefe = self.jefe
        if jefe is None or jefe.fin_entrada is None:
            return
        llenos = min(jefe.vida_barra()[0], int((self.tiempo - jefe.fin_entrada - hud.MS_FRANJAS) // hud.MS_POR_SEGMENTO))
        if llenos > self.segmentos_sonados:
            self.segmentos_sonados = llenos
            self.sonidos.reproducir("barra_jefe_%d" % ((llenos - 1) % 12 + 1))

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
            self.sonidos.reproducir("bala_rota", bala.x)
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
        # El mundo: todo lo que se ve mientras se juega, menos el fondo (lo dibuja la escena
        # antes) y el HUD (dibujar_hud, despues del temblor: asi el marcador no tiembla).
        # 'fraccion': cuanto del paso actual ya paso (0 a 1), para dibujar interpolado
        with self.interpolador.aplicar(self.objetos_que_se_mueven(), fraccion):
            self._dibujar_todo(pantalla, con_nave)

    def dibujar_hud(self, pantalla):
        hud.dibujar(pantalla, self)

    def dibujar_impactos(self, pantalla):
        # Encima del mundo y debajo del HUD (el marcador siempre se lee): el cuadro de impacto
        # del golpe final, y la vineta de la herida y de la ultima vida
        if self.impacto is not None and self.congelar_frames > 0:
            impactos.cuadro_de_impacto(pantalla, self, self.impacto, self.congelar_frames)
        impactos.peligro(pantalla, self)

    def _dibujar_todo(self, pantalla, con_nave):
        robada = self.moneda.robada_por is not None
        if not robada:
            self.moneda.dibujar(pantalla)
        if self.capsula is not None:
            self.capsula.dibujar(pantalla)
        for enemigo in self.enemigos:
            enemigo.dibujar(pantalla, self)
        if robada:
            self.moneda.dibujar(pantalla)       # encima del ladron que se la lleva
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
