"""
Director de la progresion: decide QUE enemigos hay, en que SECTOR estas y cuando
llega una OLEADA. (Los juegos le dicen "director" a esta parte: dirige la tension.)

- Presupuesto: cada enemigo cuesta puntos (COSTO_ENEMIGO) y cada nivel tiene un
  presupuesto que crece. Se completa con enemigos al azar entre los desbloqueados,
  con mas chances para el favorito del sector. Asi la dificultad crece controlada,
  pero cada partida es distinta.
- Sectores: cada SECTOR_CADA_NIVELES niveles cambia el ambiente y parte de los
  enemigos se van y llegan otros.
- Oleadas: picos de tension. Llegan muchos enemigos de golpe, duran unos segundos
  y se van; pasarla sin perder una vida da un bonus y un power-up.

La Partida le avisa lo que pasa (al_subir_nivel, al_volver_del_jefe...) y le pide
actualizar() en cada paso.
"""
import random

from juego.config import (COSTO_ENEMIGO, DESBLOQUEO_ENEMIGO, PRESUPUESTO_INICIAL, PRESUPUESTO_POR_NIVEL,
                          PRESUPUESTO_MAXIMO, ENEMIGOS_MAX, SECTORES, SECTOR_CADA_NIVELES, PESO_FAVORITO,
                          RECAMBIO_SECTOR, OLEADA_DESDE_NIVEL, OLEADA_ESPERA, OLEADA_DURACION,
                          OLEADA_PRESUPUESTO, OLEADA_PUNTOS, REFUERZO_ESPERA, AMARILLO, ROJO)
from juego.enemigos import crear_enemigos, TIPOS_ENEMIGO


class Director:
    def __init__(self, partida):
        self.partida = partida
        self.sector = SECTORES[0]           # el primero es siempre el mas tranquilo
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
        if (self.partida.nivel - 1) % SECTOR_CADA_NIVELES == 0:
            self.cambiar_sector()
        self.completar_presupuesto()

    def al_volver_del_jefe(self):
        self.completar_presupuesto()

    def al_empezar_jefe(self):
        # Si habia una oleada, se corta (sus enemigos no se guardan)
        self.terminar_oleada(superada=False)

    # ---------- Sectores ----------

    def cambiar_sector(self):
        partida = self.partida
        otros = [s for s in SECTORES if s is not self.sector]
        self.sector = random.choice(otros)
        self.numero_sector += 1
        self.tiempo_cartel_sector = partida.tiempo
        # Parte de los enemigos se va (desaparecen en una nube) y despues llegan otros
        fijos = self.fijos()
        for enemigo in random.sample(fijos, int(len(fijos) * RECAMBIO_SECTOR)):
            centro_x, centro_y = enemigo.centro()
            partida.efectos.explosion(centro_x, centro_y, [(40, 40, 60), enemigo.color], 14, 3, 3)
            partida.quitar_enemigo(enemigo)

    # ---------- Oleadas ----------

    def actualizar(self):
        partida = self.partida
        if self.en_oleada:
            if partida.tiempo >= self.oleada_hasta:
                self.terminar_oleada(superada=partida.vidas >= self.vidas_al_empezar_oleada)
        elif (partida.tiempo >= self.proxima_oleada and partida.nivel >= OLEADA_DESDE_NIVEL
              and partida.jefe is None and not partida.enemigos_guardados):
            self.empezar_oleada()
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
