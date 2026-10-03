"""
Director de la progresion: decide QUE enemigos hay, en que SECTOR estas y cuando
llega una OLEADA. (Los juegos le dicen "director" a esta parte: dirige la tension.)

- Presupuesto: cada enemigo cuesta puntos (COSTO_ENEMIGO) y cada nivel tiene un
  presupuesto que crece. Se completa con enemigos al azar entre los desbloqueados,
  con mas chances para el favorito del sector. Asi la dificultad crece controlada,
  pero cada partida es distinta.
- Sectores: cada sector termina con su jefe; al vencerlo se pasa al siguiente
  (otro ambiente, otro enemigo favorito) y parte de los enemigos se van y llegan otros.
- Oleadas: picos de tension. Llegan muchos enemigos de golpe, duran unos segundos
  y se van; pasarla sin perder una vida da un bonus y un power-up.
- Anomalias: a mitad de cada sector el espacio se pone raro un rato (anomalias.py).
- Desafios: un reto opcional por sector (desafios.py).
- Rango: al vencer al jefe, una nota de S a C para el sector (rango.py). Mientras se ve
  el cartel, el sector se esta "cerrando": los enemigos esperan para volver.

La Partida le avisa lo que pasa (al_subir_nivel, al_recibir_golpe, al_usar_dash...) y
le pide actualizar() en cada paso.
"""
import math
import random

from juego.config import (COSTO_ENEMIGO, DESBLOQUEO_ENEMIGO, PRESUPUESTO_INICIAL, PRESUPUESTO_POR_NIVEL,
                          PRESUPUESTO_MAXIMO, ENEMIGOS_MAX, SECTORES, PESO_FAVORITO,
                          RECAMBIO_SECTOR, OLEADA_DESDE_NIVEL, OLEADA_ESPERA, OLEADA_DURACION,
                          OLEADA_PRESUPUESTO, OLEADA_PUNTOS, REFUERZO_ESPERA, CARTEL_JEFE, AMARILLO, ROJO,
                          JEFE_CADA_NIVELES, ANOMALIA_NIVEL, ANOMALIA_ESPERA, RESPIRO_ANOMALIA,
                          DESAFIO_DESDE_NIVEL, DESAFIO_ESPERA, DESAFIO_PUNTOS, CARTEL_RANGO, RANGO_SELLO, VERDE)
from juego.enemigos import crear_enemigos, TIPOS_ENEMIGO
from juego.anomalias import TIPOS_ANOMALIA, crear_anomalia
from juego.desafios import TIPOS_DESAFIO
from juego.rango import Bitacora, calcular_rango


class Director:
    def __init__(self, partida):
        self.partida = partida
        self.sector = SECTORES[0]           # el primero es siempre el Cinturon
        self.numero_sector = 1
        self.tiempo_cartel_sector = -10000
        # Oleadas
        self.en_oleada = False
        self.oleada_hasta = 0
        self.vidas_al_empezar_oleada = 0
        self.proxima_oleada = random.randint(*OLEADA_ESPERA)
        # Refuerzos: si destruis enemigos, cada tanto llega otro hasta llenar el presupuesto
        self.proximo_refuerzo = REFUERZO_ESPERA
        # Cartel "NUEVO ENEMIGO" la primera vez que aparece un tipo
        self.nuevo_tipo = None
        self.tiempo_cartel_nuevo = -10000
        # Anomalias (los tests las apagan con con_anomalias = False)
        self.con_anomalias = True
        self.anomalia = None
        self.proxima_anomalia = math.inf
        # Desafios (igual: con_desafios = False los apaga)
        self.con_desafios = True
        self.desafio = None
        self.ultimo_desafio = None
        self.proximo_desafio = math.inf
        self.tiempo_cartel_desafio = -10000
        # Rango: la bitacora del sector actual y el rango del ultimo sector cerrado
        self.bitacora = Bitacora()
        self.rango = None
        self.tiempo_cartel_rango = -10000
        self.rango_pagado = True
        self.fin_del_cierre = -10000

    # ---------- Presupuesto ----------

    def presupuesto(self):
        nivel = self.partida.nivel
        base = min(PRESUPUESTO_INICIAL + (nivel - 1) * PRESUPUESTO_POR_NIVEL, PRESUPUESTO_MAXIMO)
        return base * self.partida.reglas["presupuesto"]

    def fijos(self):
        # Los enemigos que se quedan (los de las oleadas se van)
        return [e for e in self.partida.enemigos if not e.de_oleada]

    def costo_actual(self):
        # Lo que "cuestan" los enemigos fijos (cada uno sabe su costo: los hijos del
        # divisor no cuestan nada y cada dron cuesta una parte del enjambre)
        return sum(e.costo for e in self.fijos())

    def cantidad_actual(self):
        # Cuantos "enemigos" hay (un enjambre cuenta como uno)
        return sum(e.costo / COSTO_ENEMIGO[e.tipo] for e in self.fijos() if e.costo)

    def agregar(self, tipo, de_oleada=False):
        nuevos = crear_enemigos(tipo, self.partida)
        for enemigo in nuevos:
            enemigo.de_oleada = de_oleada
        self.partida.enemigos.extend(nuevos)

    def desbloqueados(self):
        return [tipo for tipo, nivel in DESBLOQUEO_ENEMIGO.items() if self.partida.nivel >= nivel]

    def elegir_tipo(self, disponible):
        # Un enemigo al azar que entre en 'disponible'; el favorito del sector pesa mas
        opciones = [t for t in self.desbloqueados() if COSTO_ENEMIGO[t] <= disponible]
        if not opciones:
            return None
        pesos = [PESO_FAVORITO if t == self.sector["favorito"] else 1 for t in opciones]
        return random.choices(opciones, weights=pesos)[0]

    def completar_presupuesto(self):
        # Agrega enemigos hasta gastar el presupuesto del nivel
        partida = self.partida
        # Si recien se desbloqueo un tipo, se presenta primero (para conocerlo), con su cartel
        for tipo, nivel in DESBLOQUEO_ENEMIGO.items():
            if partida.nivel == nivel and not any(e.tipo == tipo for e in self.fijos()):
                self.agregar(tipo)
                if nivel > 1:
                    self.nuevo_tipo = TIPOS_ENEMIGO[tipo]
                    self.tiempo_cartel_nuevo = partida.tiempo
        disponible = self.presupuesto() - self.costo_actual()
        while self.cantidad_actual() < ENEMIGOS_MAX:
            tipo = self.elegir_tipo(disponible)
            if tipo is None:
                break
            self.agregar(tipo)
            disponible -= COSTO_ENEMIGO[tipo]

    # ---------- Avisos de la Partida ----------

    def al_empezar(self):
        self.completar_presupuesto()

    def al_subir_nivel(self):
        partida = self.partida
        self.completar_presupuesto()
        if partida.nivel % JEFE_CADA_NIVELES == ANOMALIA_NIVEL and self.con_anomalias:
            self.proxima_anomalia = partida.tiempo + ANOMALIA_ESPERA
        if partida.nivel == DESAFIO_DESDE_NIVEL and self.numero_sector == 1:
            self.proximo_desafio = partida.tiempo + DESAFIO_ESPERA

    def al_vencer_al_jefe(self):
        # Vencido el jefe, se cierra el sector: "¡JEFE VENCIDO!", el cartel del rango, y
        # recien despues el sector nuevo (los carteles salen uno detras de otro)
        partida = self.partida
        bitacora = self.bitacora
        if bitacora.inicio_jefe is not None:
            bitacora.tiempo_jefe = partida.tiempo - bitacora.inicio_jefe
        self.rango = calcular_rango(bitacora, self.sector["jefe"], self.vuelta())
        self.rango["sector"] = self.numero_sector
        self.rango["color"] = self.sector["color"]
        self.tiempo_cartel_rango = partida.tiempo + CARTEL_JEFE
        self.rango_pagado = False
        self.fin_del_cierre = self.tiempo_cartel_rango + CARTEL_RANGO
        self.cambiar_sector()
        self.tiempo_cartel_sector = self.fin_del_cierre
        # El sector nuevo empieza con la bitacora en blanco y, al rato, un desafio nuevo
        self.bitacora = Bitacora()
        self.desafio = None
        self.proximo_desafio = self.fin_del_cierre + DESAFIO_ESPERA

    def cerrando_sector(self):
        # Despues del jefe, mientras se ven "¡JEFE VENCIDO!" y el rango
        return self.partida.tiempo < self.fin_del_cierre

    def al_volver_del_jefe(self):
        self.completar_presupuesto()

    def jefe_del_sector(self):
        return self.sector["jefe"]

    def al_empezar_jefe(self):
        # Si habia una oleada o una anomalia, se cortan (sus enemigos no se guardan),
        # y el desafio se decide: llegaste al jefe
        self.terminar_oleada(superada=False)
        self.terminar_anomalia()
        self.proxima_anomalia = math.inf
        self.proximo_desafio = math.inf
        self.bitacora.inicio_jefe = self.partida.tiempo
        if self.desafio_en_curso():
            self.desafio.al_llegar_el_jefe()
            self.revisar_desafio()

    def vuelta(self):
        # 1 la primera vez que se recorren los sectores, 2 la segunda...
        return (self.numero_sector - 1) // len(SECTORES) + 1

    # ---------- Lo que pasa en la partida (para el desafio y la bitacora) ----------

    def al_recibir_golpe(self):
        self.bitacora.golpes += 1
        if self.desafio_en_curso():
            self.desafio.al_recibir_golpe()
            self.revisar_desafio()

    def al_usar_dash(self):
        if self.desafio_en_curso():
            self.desafio.al_usar_dash()
            self.revisar_desafio()

    def al_agarrar_powerup(self):
        if self.desafio_en_curso():
            self.desafio.al_agarrar_powerup()
            self.revisar_desafio()

    def al_recoger_moneda(self, combo):
        self.bitacora.mejor_combo = max(self.bitacora.mejor_combo, combo)
        if self.desafio_en_curso():
            self.desafio.al_recoger_moneda(combo)
            self.revisar_desafio()

    def al_destruir_enemigo(self):
        if self.desafio_en_curso():
            self.desafio.al_destruir_enemigo()
            self.revisar_desafio()

    # ---------- Sectores ----------

    def cambiar_sector(self):
        # El siguiente de la lista (despues del ultimo, vuelve al primero)
        partida = self.partida
        self.sector = SECTORES[(SECTORES.index(self.sector) + 1) % len(SECTORES)]
        self.numero_sector += 1
        self.tiempo_cartel_sector = partida.tiempo
        # Parte de los enemigos se va y despues llegan otros. Si estaban guardados por la
        # pelea con el jefe, directamente no vuelven; si estan en pantalla, se van en una nube.
        # Un enjambre se va entero (cuenta como un grupo)
        guardados = partida.enemigos_guardados
        grupos = {}
        for enemigo in (guardados if guardados else self.fijos()):
            grupos.setdefault(id(getattr(enemigo, "bandada", enemigo)), []).append(enemigo)
        for grupo in random.sample(list(grupos.values()), int(len(grupos) * RECAMBIO_SECTOR)):
            for enemigo in grupo:
                if enemigo in guardados:
                    guardados.remove(enemigo)
                    enemigo.al_quitar(partida)
                else:
                    centro_x, centro_y = enemigo.centro()
                    partida.efectos.explosion(centro_x, centro_y, [(40, 40, 60), enemigo.color], 14, 3, 3)
                    partida.quitar_enemigo(enemigo)

    # ---------- Cada paso ----------

    def actualizar(self):
        partida = self.partida
        tranquilo = partida.jefe is None and not partida.enemigos_guardados and not self.cerrando_sector()
        if self.en_oleada:
            if partida.tiempo >= self.oleada_hasta:
                self.terminar_oleada(superada=partida.vidas >= self.vidas_al_empezar_oleada)
        elif (partida.tiempo >= self.proxima_oleada and partida.nivel >= OLEADA_DESDE_NIVEL
              and tranquilo and self.anomalia is None):
            self.empezar_oleada()
        if self.anomalia is not None:
            self.anomalia.actualizar(partida)
            if self.anomalia.termino(partida):
                self.terminar_anomalia()
        elif partida.tiempo >= self.proxima_anomalia and tranquilo and not self.en_oleada:
            self.empezar_anomalia()
        if partida.tiempo >= self.proximo_desafio and partida.jefe is None:
            self.proponer_desafio()
        if not self.rango_pagado and partida.tiempo >= self.tiempo_cartel_rango + RANGO_SELLO:
            self.pagar_rango()
        self._refuerzos()

    def _refuerzos(self):
        # Si destruiste enemigos y sobra presupuesto, cada REFUERZO_ESPERA llega uno
        partida = self.partida
        if partida.tiempo < self.proximo_refuerzo:
            return
        self.proximo_refuerzo = partida.tiempo + REFUERZO_ESPERA
        if self.en_oleada or partida.jefe is not None or partida.enemigos_guardados:
            return
        if self.cantidad_actual() >= ENEMIGOS_MAX:
            return
        tipo = self.elegir_tipo(self.presupuesto() - self.costo_actual())
        if tipo is not None:
            self.agregar(tipo)

    def empezar_oleada(self):
        partida = self.partida
        self.en_oleada = True
        self.oleada_hasta = partida.tiempo + OLEADA_DURACION
        self.vidas_al_empezar_oleada = partida.vidas
        partida.sonidos.reproducir("nuevo_record")
        partida.efectos.sacudir(10, ROJO)
        disponible = self.presupuesto() * OLEADA_PRESUPUESTO
        while True:
            tipo = self.elegir_tipo(disponible)
            if tipo is None:
                break
            self.agregar(tipo, de_oleada=True)
            disponible -= COSTO_ENEMIGO[tipo]

    def terminar_oleada(self, superada):
        partida = self.partida
        if not self.en_oleada:
            return
        self.en_oleada = False
        self.proxima_oleada = partida.tiempo + random.randint(*OLEADA_ESPERA)
        # Los enemigos de la oleada se retiran
        for enemigo in [e for e in partida.enemigos if e.de_oleada]:
            centro_x, centro_y = enemigo.centro()
            partida.efectos.explosion(centro_x, centro_y, [(40, 40, 60), enemigo.color], 14, 3, 3)
            partida.quitar_enemigo(enemigo)
        if superada:
            # Premio: puntos y un power-up que cae enseguida
            ganados = partida.sumar_puntos(OLEADA_PUNTOS * partida.nivel)
            nave_x, nave_y = partida.nave.centro()
            partida.efectos.texto_flotante("¡OLEADA SUPERADA! +" + str(ganados), nave_x, nave_y - 40, AMARILLO)
            partida.sonidos.reproducir("powerup")
            if partida.capsula is None:
                partida.proximo_powerup = partida.tiempo

    def restante_oleada(self):
        return max(0, self.oleada_hasta - self.partida.tiempo) if self.en_oleada else 0

    # ---------- Anomalias ----------

    def empezar_anomalia(self):
        # La del sector; desde la segunda vuelta (o si el sector no tiene), una al azar
        partida = self.partida
        tipo = self.sector["anomalia"]
        if tipo is None or self.vuelta() > 1:
            tipo = random.choice(list(TIPOS_ANOMALIA))
        self.anomalia = crear_anomalia(tipo, partida)
        self.proxima_anomalia = math.inf
        # Ninguna oleada encima de la anomalia ni justo despues
        self.proxima_oleada = max(self.proxima_oleada, self.anomalia.hasta + RESPIRO_ANOMALIA)
        partida.sonidos.reproducir("nuevo_record")
        partida.efectos.sacudir(10, self.anomalia.color)

    def terminar_anomalia(self):
        if self.anomalia is not None:
            self.anomalia.terminar(self.partida)
            self.anomalia = None

    def multiplicador_monedas(self):
        return self.anomalia.multiplicador_monedas() if self.anomalia else 1

    def factor_combo(self):
        return self.anomalia.factor_combo() if self.anomalia else 1

    def dibujar_anomalia(self, pantalla):
        if self.anomalia is not None:
            self.anomalia.dibujar(pantalla, self.partida)

    # ---------- Desafios ----------

    def proponer_desafio(self):
        # Uno al azar entre los que se pueden ahora (distinto del anterior)
        partida = self.partida
        self.proximo_desafio = math.inf
        if not self.con_desafios:
            return
        posibles = [clase for clase in TIPOS_DESAFIO.values()
                    if clase.disponible(partida) and clase.tipo != self.ultimo_desafio]
        clase = random.choice(posibles)
        self.desafio = clase()
        self.ultimo_desafio = clase.tipo
        self.tiempo_cartel_desafio = partida.tiempo
        partida.sonidos.reproducir("seleccion")

    def desafio_en_curso(self):
        return self.desafio is not None and self.desafio.en_curso()

    def revisar_desafio(self):
        # Despues de cada aviso: si el desafio se cumplio o se fallo, se anuncia (y se premia)
        partida = self.partida
        desafio = self.desafio
        if desafio.en_curso():
            return
        self.tiempo_cartel_desafio = partida.tiempo
        if desafio.estado == "fallado":
            return
        self.bitacora.desafio_cumplido = True
        ganados = partida.sumar_puntos(DESAFIO_PUNTOS * self.numero_sector)
        nave_x, nave_y = partida.nave.centro()
        partida.efectos.texto_flotante("¡DESAFIO! +" + str(ganados), nave_x, nave_y - 40, VERDE)
        partida.efectos.anillo(nave_x, nave_y, [(0, 90, 40), VERDE, (255, 255, 255)], 32, 6)
        partida.sonidos.reproducir("powerup")
        if partida.capsula is None:
            partida.proximo_powerup = partida.tiempo     # de premio, un power-up enseguida

    # ---------- Rango ----------

    def pagar_rango(self):
        # Cuando la letra aparece en el cartel: el premio y un golpe de efecto
        partida = self.partida
        self.rango_pagado = True
        if self.rango["puntos"]:
            partida.sumar_puntos(self.rango["puntos"])
        if self.rango["letra"] in ("S", "A"):
            partida.sonidos.reproducir("nuevo_record")
        else:
            partida.sonidos.reproducir("seleccion")
        partida.efectos.sacudir(10)
