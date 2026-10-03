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
"""
import math
import random

from juego import hud, lienzo
from juego.config import (COMBO_TIEMPO, COMBO_MAXIMO, MONEDAS_POR_NIVEL, MS_POR_FRAME,
                          PUNTOS_ENEMIGO_CONGELADO, NAVE_VELOCIDAD, RECARGA_POR_DESTRUIR,
                          TURBO_VELOCIDAD, DASH_RECARGA, RECARGA_RAPIDA, PRIMER_POWERUP, ESPERA_POWERUP,
                          INVULNERABLE_GOLPE, INVULNERABLE_ESCUDO, JEFE_CADA_NIVELES, JEFE_PUNTOS,
                          CARTEL_JEFE, DIFICULTADES, AMARILLO, BLANCO, CIAN, ROJO, HIELO, ORO, FUEGO, ENERGIA,
                          ESCARCHA, EMBESTIDA, ARCOIRIS)
from juego.nave import Nave
from juego.moneda import Moneda
from juego.jefes import crear_jefe
from juego.progresion import Director
from juego.powerups import TIPOS_POWERUP, Capsula, HASTA_PERDER_VIDA
from juego.proyectiles import mover_balas, dibujar_balas
from juego.interpolacion import Interpolador


class Partida:
    def __init__(self, efectos, sonidos, entrada, records, opciones, dificultad="NORMAL"):
        # Servicios que usa (los crea la App y se comparten)
        self.efectos = efectos
        self.sonidos = sonidos
        self.entrada = entrada          # solo para vibrar el mando
        self.opciones = opciones        # se leen en vivo (ej: el aviso del jefe)
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
        self.monedas_recogidas = 0
        self.nivel = 1
        self.record_superado = False
        self.tiempo_cartel_nivel = -10000
        self.tiempo_moneda = -1000      # ultima moneda (para iluminar el puntaje)
        self.tiempo_golpe = -1000       # ultimo golpe (para hacer parpadear las vidas)

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

    def espera_powerup(self):
        return random.randint(*ESPERA_POWERUP) * self.reglas["espera_powerup"]

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
        return TURBO_VELOCIDAD if self.activo("turbo") else NAVE_VELOCIDAD

    def recarga_dash(self):
        return RECARGA_RAPIDA if self.activo("recarga") else DASH_RECARGA

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

    def subir_nivel(self):
        self.nivel += 1
        self.tiempo_cartel_nivel = self.tiempo
        self.sonidos.reproducir("seleccion")
        nave_x, nave_y = self.nave.centro()
        self.efectos.anillo(nave_x, nave_y, ORO, 32, 6)
        self.director.al_subir_nivel()      # sector nuevo cada tanto y mas enemigos
        if self.nivel % JEFE_CADA_NIVELES == 0:
            self.iniciar_jefe()

    def danar_jugador(self, golpe_x, golpe_y):
        # Golpe de un enemigo, del jefe o de una bala: rompe el escudo o quita una vida
        nave = self.nave
        ahora = self.tiempo
        nave_x, nave_y = nave.centro()
        self.sonidos.reproducir("golpe")

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

        if self.vidas <= 0:
            # Gran explosion de la nave; el Game Over aparece despues
            self.sonidos.parar_musica()
            self.efectos.explosion(nave_x, nave_y, FUEGO, 90, 10, 6)
            self.efectos.explosion(nave_x, nave_y, ORO, 30, 5, 4)
            self.efectos.sacudir(35, BLANCO)
            self.entrada.vibrar(1, 1, 700)
            self.congelar_frames = 8
            self.termino = True

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
        objetos = [self.nave, self.moneda] + self.enemigos + self.balas + self.efectos.particulas
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
        self.nave.actualizar(self.tiempo, dx, dy, pidio_dash, vel_max, self.recarga_dash(), self.efectos)

        # El combo se corta si pasa mucho tiempo sin monedas
        if self.combo > 0 and self.tiempo - self.ultima_moneda > COMBO_TIEMPO:
            self.combo = 0
        if self.activo("iman"):
            self.moneda.atraer(self.nave, self.efectos)

        self._revisar_moneda()
        self._actualizar_powerups()
        self.director.actualizar()          # oleadas
        self._devolver_enemigos()
        self._actualizar_enemigos()
        if self.jefe is not None and not self.termino:
            self._actualizar_jefe()

        self.nave.estela(self.tiempo, vel_max, self.efectos)
        self.moneda.brillar(self.efectos)
        self.efectos.actualizar()

    def _revisar_moneda(self):
        if not self.nave.caja_recoger().colliderect(self.moneda.caja()):
            return
        ahora = self.tiempo
        if ahora - self.ultima_moneda < COMBO_TIEMPO:
            self.combo += 1
        else:
            self.combo = 1
        self.ultima_moneda = ahora
        self.mejor_combo = max(self.mejor_combo, self.combo)
        ganados = self.sumar_puntos(self.multiplicador_combo())
        centro_x, centro_y = self.moneda.centro()
        if self.multiplicador_combo() > 1:
            self.efectos.explosion(centro_x, centro_y, ARCOIRIS, 20, 5, 3)
        else:
            self.efectos.explosion(centro_x, centro_y, ORO, 14, 4, 3)
        self.efectos.texto_flotante("+" + str(ganados), centro_x, self.moneda.y - 6, AMARILLO)
        self.sonidos.reproducir("moneda")
        self.tiempo_moneda = ahora
        self.moneda.mover_a_lugar_nuevo(self)
        # Durante la pelea con el jefe las monedas dan puntos pero no suben de nivel
        if self.jefe is None:
            self.monedas_recogidas += 1
            if self.monedas_recogidas % MONEDAS_POR_NIVEL == 0:
                self.subir_nivel()

    def _actualizar_powerups(self):
        # Cada 8 a 13 segundos cae uno desde arriba; si no lo recoges, se va por abajo
        ahora = self.tiempo
        if self.capsula is None and ahora > self.proximo_powerup:
            disponibles = [p for p in TIPOS_POWERUP.values() if p.disponible(self)]
            self.capsula = Capsula(random.choice(disponibles), random.randint(30, lienzo.ancho - 30))
        if self.capsula is None:
            return
        self.capsula.caer()
        if self.nave.caja_recoger().colliderect(self.capsula.caja()):
            powerup, x, y = self.capsula.powerup, self.capsula.x, self.capsula.y
            self.sonidos.reproducir("powerup")
            powerup.al_recoger(self, x, y)
            self.efectos.texto_flotante(powerup.texto_al_recoger(), x, y - 24, powerup.color)
            self.capsula = None
            self.proximo_powerup = ahora + self.espera_powerup()
        elif self.capsula.salio():
            self.capsula = None
            self.proximo_powerup = ahora + self.espera_powerup()

    def _devolver_enemigos(self):
        # Despues del jefe, los enemigos vuelven cuando se va el cartel (asi no quedan tapados)
        if self.jefe is not None or not self.enemigos_guardados:
            return
        if self.tiempo - self.tiempo_cartel_jefe < CARTEL_JEFE:
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
            elif congelados:
                continue
            elif enemigo.destruible and nave.en_dash(ahora) and caja_nave.colliderect(enemigo.caja()):
                self.destruir_con_dash(enemigo)
            elif nave.toca_circulo(golpe_x, golpe_y, enemigo.radio) and not nave.atraviesa(ahora):
                self.danar_jugador(golpe_x, golpe_y)
                if self.termino:
                    break
                if enemigo.muere_al_chocar:
                    self.efectos.explosion(golpe_x, golpe_y, [(40, 40, 60), enemigo.color], 16, 4, 3)
                    self.destruir_enemigo(enemigo, con_dash=False)
                else:
                    enemigo.reaparecer(self)

    def destruir_con_dash(self, enemigo):
        # El dash destruye a los enemigos 'destruibles': puntos, chispas, y el dash se recarga un poco
        centro_x, centro_y = enemigo.centro()
        ganados = self.sumar_puntos(enemigo.puntos_dash)
        self.sonidos.reproducir("golpe")
        self.efectos.explosion(centro_x, centro_y, [(40, 40, 60), enemigo.color, BLANCO], 24, 6, 4)
        self.efectos.texto_flotante("+" + str(ganados), centro_x, centro_y - 20, enemigo.color)
        self.efectos.sacudir(4)
        self.entrada.vibrar(0.3, 0.5, 80)
        self.congelar_frames = 2
        self.nave.dash_listo = max(self.tiempo, self.nave.dash_listo - RECARGA_POR_DESTRUIR)
        self.destruir_enemigo(enemigo, con_dash=True)

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
        for bala in self.balas:
            if nave.toca_circulo(bala.x, bala.y, bala.radio):
                self.balas.remove(bala)
                self.danar_jugador(bala.x, bala.y)
                return
        # Tocar su cuerpo o sus partes hace daño (congelado no)
        if not jefe.congelado(self) and any(nave.toca_rect(caja) for caja in jefe.cajas_danio()):
            centro_x, centro_y = jefe.centro()
            self.danar_jugador(centro_x, centro_y)

    def _destruir_proyectiles(self, caja):
        # Algunos proyectiles (los misiles) se destruyen con el dash y dan puntos
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
        self.nave.dibujar_fantasmas(pantalla)
        if con_nave:
            self.nave.dibujar(pantalla, self.tiempo, self.restante("escudo"))
        self.efectos.dibujar(pantalla)
        hud.dibujar(pantalla, self)
