"""
Director de la progresion: decide QUIEN viene, CUANDO y COMO. (Los juegos le dicen
"director" a esta parte: dirige la tension.)

- Ruta: cada sector tiene 4 TRAMOS y el jefe, uno por nivel (rutas.py). Cada tramo trae
  un OBJETIVO (objetivos.py: juntar monedas, romper divisores, frenar embestidas...). Al
  cumplirlo dejan de llegar escuadrones, los que quedan se retiran y, con la zona despejada,
  empieza el tramo siguiente con su cartel. Asi se siente que avanzas por lo que hiciste.
- Escuadrones: en cada tramo los enemigos llegan en grupos (escuadrones.py), en el orden del
  guion: flecha de aviso en el borde, entran volando en formacion, atacan su turno y se
  retiran. Si los eliminas a todos: bonus. Nunca hay mas de "a_la_vez" grupos en pantalla.
- Asedio: el tramo 4. Escuadrones de todos lados por ASEDIO_DURACION ms; el objetivo es
  aguantar hasta que termine (despues llega el jefe). Pasarlo sin perder una vida da un
  bonus y un power-up.
- Sectores: cada sector termina con su jefe; al vencerlo se pasa al siguiente (otro ambiente,
  otro guion). Despues del ultimo se vuelve al primero, con escuadrones mas grandes (vuelta()).
- Anomalias: en el tramo 3 de cada sector el espacio se pone raro (anomalias.py): la del
  sector la mitad de las veces, si no otra (asi se ven todas desde el principio).
- Desafios: un reto opcional por sector (desafios.py).
- Rango: al vencer al jefe, una nota de S a C para el sector (rango.py). Mientras se ve
  el cartel, el sector se esta "cerrando": todavia no llega nadie.
- Mejoras: cuando el modo dice (abre_el_taller) deja 3 cartas gratis en 'ofertas'
  (mejoras.py) y la escena Juego abre el Taller. En el arcade, al cerrar cada sector se para
  en la GASOLINERA ('gasolinera' = True): ahi las cartas se compran (arcade/tienda.py).
- Lo que cambia segun el modo de juego (modos.py) se lo pregunta a partida.modo: en que
  sector empieza y que ruta sigue, cuando abre el Taller y llega el desafio, y si despues
  del jefe sigue la ruta (arcade) o la partida se cumple (historia). Y le avisa cuando
  empieza un tramo, cuando llega o cae el jefe y cuando juntas una moneda.

La Partida le avisa lo que pasa (al_subir_nivel, al_recibir_golpe, al_usar_dash...) y
le pide actualizar() en cada paso.
"""
import math
import random

from juego.config import (ANCHO, SECTORES, CARTEL_JEFE, CARTEL_SECTOR, AMARILLO, ROJO, VERDE, JEFE_CADA_NIVELES, ANOMALIA_NIVEL,
                          ANOMALIA_ESPERA, ANOMALIA_PROPIA, DESAFIO_ESPERA, DESAFIO_PUNTOS,
                          CARTEL_RANGO, RANGO_SELLO, AVISO_ASEDIO, AVISO_ANOMALIA,
                          AVISO_TRAMO, MS_POR_FRAME, AVISO_ESCUADRON, ESCALONADO, TURNO_ESCUADRON, RESPIRO_ESCUADRON,
                          INICIO_TRAMO, ESCUADRON_PUNTOS, VUELTA_CANTIDAD, VUELTA_OBJETIVO, ASEDIO_DURACION,
                          ASEDIO_INICIO, ASEDIO_RESPIRO, ASEDIO_TURNO, ASEDIO_PUNTOS, OBJETIVO_PUNTOS,
                          PACIENCIA_OBJETIVO, PERMANENCIA_MINIMA, ENTRADA_ESCUADRON)
from juego.avisos import Aviso
from juego.enemigos import crear_enemigos, TIPOS_ENEMIGO
from juego.escuadrones import Escuadron, lugares
from juego.objetivos import crear_objetivo
from juego.anomalias import TIPOS_ANOMALIA, crear_anomalia
from juego.desafios import TIPOS_DESAFIO
from juego.rango import Bitacora, calcular_rango
from juego.mejoras import sortear_mejoras

TRAMOS = JEFE_CADA_NIVELES - 1      # tramos de cada sector (el nivel que sigue es el del jefe)


class Director:
    def __init__(self, partida):
        self.partida = partida
        self.numero_sector = partida.modo.primer_sector()     # (el arcade empieza siempre en el Cinturon)
        self.sector = SECTORES[self.numero_sector - 1]
        self.fin_de_la_partida = math.inf   # cuando se cumple la partida (si el modo no sigue despues del jefe)
        self.tiempo_cartel_sector = -10000
        # El tramo en curso (None = no hay: el jefe o el cierre del sector)
        self.tramo = None
        self.numero_tramo = 0
        self.tiempo_tramo = -10000
        self.anuncio_en = math.inf          # cuando sale el cartel del tramo (espera al del sector)
        self.objetivo = None                # lo que pide el tramo para pasar (objetivos.py)
        self.objetivo_festejado = False     # ya se cumplio y se festejo: a despejar la zona
        self.tiempo_avance = -10000         # cuando avanzo el objetivo por ultima vez (el HUD destella)
        # Escuadrones: los que estan en pantalla y los que faltan llegar en este tramo
        # (con_escuadrones = False no llega ninguno: lo usa el fixture de los tests)
        self.con_escuadrones = True
        self.escuadrones = []
        self.cola = []
        self.proximo_escuadron = math.inf
        # Asedio (el tramo 4)
        self.en_asedio = False
        self.asedio_hasta = 0
        self.proximo_asedio = math.inf
        self.asedio_cumplido = False
        self.vidas_al_empezar_asedio = 0
        # Cartel "NUEVO ENEMIGO" la primera vez que llega un tipo
        self.vistos = set()
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
        self.sector_por_empezar = False     # al terminar el cierre empieza el tramo 1 del sector nuevo
        # Mejoras (con_mejoras = False apaga el Taller y la gasolinera)
        self.con_mejoras = True
        self.ofertas = []                   # cartas gratis del Taller, esperando que elijas una
        self.gasolinera_tras_cierre = False # al terminar el cierre del sector, a la gasolinera
        self.gasolinera = False             # hay que parar ahora (la escena Juego la abre)

    # ---------- Consultas ----------

    def tramos_del_sector(self):
        # Los 4 tramos del sector actual: los da el modo (rutas.py, o los de la mision)
        return self.partida.modo.ruta(self.numero_sector)

    def tipos_del_sector(self):
        # Los enemigos que trae este sector (para los desafios: INTERCEPTOR pide embestidores)
        return {tipo for tramo in self.tramos_del_sector() for tipo, _, _ in tramo["escuadrones"]}

    def rotulo(self):
        # Donde estas, como en los juegos de plataformas: "2-3" (sector 2, tramo 3) o "2-JEFE"
        return "%d-%s" % (self.numero_sector, self.numero_tramo if self.numero_tramo else "JEFE")

    def vuelta(self):
        # 1 la primera vez que se recorren los sectores, 2 la segunda...
        return (self.numero_sector - 1) // len(SECTORES) + 1

    def cerrando_sector(self):
        # Despues del jefe, mientras se ven "¡JEFE VENCIDO!" y el rango
        return self.partida.tiempo < self.fin_del_cierre

    def restante_asedio(self):
        return max(0, self.asedio_hasta - self.partida.tiempo) if self.en_asedio else 0

    def jefe_del_sector(self):
        return self.sector["jefe"]

    def _a_la_vez(self):
        # Cuantos escuadrones puede haber en pantalla (uno mas desde la segunda vuelta)
        return self.tramo["a_la_vez"] + (1 if self.vuelta() > 1 else 0)

    def _cantidad(self, cantidad):
        # Cuantos trae un escuadron, segun la dificultad y la vuelta (al menos uno)
        factor = self.partida.reglas["escuadrones"] * (1 + VUELTA_CANTIDAD * (self.vuelta() - 1))
        return max(1, round(cantidad * factor))

    # ---------- Tramos ----------

    def al_empezar(self):
        self.empezar_tramo()

    def al_subir_nivel(self):
        partida = self.partida
        if partida.nivel % JEFE_CADA_NIVELES:       # (en el nivel del jefe, el jefe: lo trae la Partida)
            self.empezar_tramo()
        if partida.modo.propone_desafio(self):
            self.proximo_desafio = partida.tiempo + DESAFIO_ESPERA
        if partida.modo.abre_el_taller(self):
            self.ofrecer_mejoras()

    def empezar_tramo(self):
        # El tramo del nivel actual: los escuadrones del anterior se retiran, se anuncia el
        # nuevo y al rato llega su primer escuadron
        partida = self.partida
        self.retirar_todos()
        if self.anomalia is not None:
            self.terminar_anomalia()                    # la anomalia era del tramo anterior
            partida.sonidos.reproducir("anomalia_fin")
        indice = (partida.nivel - 1) % JEFE_CADA_NIVELES
        self.numero_tramo = indice + 1
        self.tramo = self.tramos_del_sector()[indice]
        self.cola = list(self.tramo["escuadrones"])
        self.objetivo = crear_objetivo(self.tramo["objetivo"], 1 + VUELTA_OBJETIVO * (self.vuelta() - 1))
        self.objetivo_festejado = False
        self.tiempo_tramo = partida.tiempo
        # Si se esta viendo el cartel del sector nuevo, el del tramo y su primer escuadron esperan
        self.anuncio_en = max(partida.tiempo, self.tiempo_cartel_sector + CARTEL_SECTOR)
        self.proximo_escuadron = self.anuncio_en + INICIO_TRAMO
        self.asedio_cumplido = False
        self.proximo_asedio = math.inf
        if self.tramo.get("asedio"):
            self.proximo_asedio = partida.tiempo + ASEDIO_INICIO
            self.proximo_escuadron = self.proximo_asedio
        if self.numero_tramo == ANOMALIA_NIVEL and self.con_anomalias:
            self.proxima_anomalia = partida.tiempo + ANOMALIA_ESPERA
        if self.anuncio_en <= partida.tiempo:
            self._anunciar_tramo()
        partida.modo.al_empezar_tramo(self.numero_tramo)

    def _anunciar_tramo(self):
        # "TRAMO 2/4 - BLANCO FACIL" (el asedio, con cinta de peligro)
        self.anuncio_en = math.inf
        tramo = self.tramo
        asedio = tramo.get("asedio", False)
        color = ROJO if asedio else self.sector["color"]
        self.partida.avisar(Aviso("TRAMO %d/%d" % (self.numero_tramo, TRAMOS), tramo["nombre"],
                                  self.objetivo.texto(), color, AVISO_TRAMO, alerta=asedio))

    def retirar_todos(self):
        # Todos los escuadrones se van volando ya (cambio de tramo)
        for escuadron in self.escuadrones:
            escuadron.retirarse(self.partida)

    def despedir_escuadrones(self):
        # Se termino el tramo (o el asedio): los escuadrones se van, pero el que acaba de llegar
        # se queda al menos PERMANENCIA_MINIMA ms (si no, se iban apenas llegaban). El que
        # todavia era solo la flecha no llega a entrar
        ahora = self.partida.tiempo
        for escuadron in self.escuadrones:
            if ahora < escuadron.llega_en - ENTRADA_ESCUADRON:
                escuadron.retirarse(self.partida)
            else:
                escuadron.retirada_en = min(escuadron.retirada_en, max(ahora, escuadron.llega_en + PERMANENCIA_MINIMA))

    # ---------- Escuadrones ----------

    def _escuadrones(self):
        partida = self.partida
        ahora = partida.tiempo
        # Los que se quedaron sin turno se retiran (tambien los que se sumaron despues de la
        # orden, como los hijos de un divisor partido mientras se iba)
        for escuadron in self.escuadrones:
            if escuadron.se_retiro or ahora >= escuadron.retirada_en:
                escuadron.retirarse(partida)
        # Los que ya no estan (rotos o idos) dejan lugar al siguiente; si los rompiste a todos, bonus
        respiro = ASEDIO_RESPIRO if self.en_asedio else RESPIRO_ESCUADRON
        for escuadron in [e for e in self.escuadrones if e.termino(partida)]:
            self.escuadrones.remove(escuadron)
            if escuadron.eliminado(partida):
                self._premiar_escuadron(escuadron)
            self.proximo_escuadron = max(self.proximo_escuadron, ahora + respiro)
        if (not self.con_escuadrones or self.tramo is None or partida.jefe is not None or self.cerrando_sector()
                or self.sector_por_empezar):
            return
        if self.tramo.get("asedio") and not self.en_asedio and not self.asedio_cumplido:
            return                                      # (el asedio todavia no empezo)
        if self.en_asedio and self.restante_asedio() < 3 * AVISO_ESCUADRON:
            return                                      # (no llegarian a entrar)
        if self.objetivo is not None and self.objetivo.cumplido():
            return                                      # (objetivo cumplido: a despejar la zona)
        if len(self.escuadrones) < self._a_la_vez() and ahora >= self.proximo_escuadron:
            self.lanzar_escuadron()
            # El siguiente no entra al mismo tiempo: asi se lee cada grupo por separado
            self.proximo_escuadron = ahora + (respiro if self.en_asedio else 2 * respiro)

    # ---------- El objetivo del tramo ----------

    def _revisar_objetivo(self):
        # Cumplido el objetivo: se festeja y los que quedan se retiran. Con la zona despejada
        # (no queda ningun escuadron), se pasa al tramo siguiente
        partida = self.partida
        if self.objetivo is None or self.tramo is None or partida.jefe is not None or self.cerrando_sector():
            return
        if not self.objetivo.cumplido():
            if self.con_escuadrones and partida.tiempo - self.tiempo_tramo > PACIENCIA_OBJETIVO:
                self._abrir_el_paso()
            return
        if not self.objetivo_festejado:
            self.objetivo_festejado = True
            self._festejar_objetivo()
            self.despedir_escuadrones()
        if not self.escuadrones:
            if self.numero_tramo == TRAMOS and not partida.modo.hay_jefe():
                self._terminar_sin_jefe()
            else:
                partida.subir_nivel()

    def _terminar_sin_jefe(self):
        # Una ruta sin jefe (una mision tranquila de la historia): con el ultimo tramo despejado,
        # el cartel de la zona despejada y la partida se cumple cuando se va
        partida = self.partida
        self.tramo = None
        self.objetivo = None
        self.terminar_anomalia()
        self.fin_de_la_partida = partida.tiempo + AVISO_TRAMO
        partida.avisar(Aviso("FIN DE LA RUTA", "ZONA DESPEJADA", "", VERDE, AVISO_TRAMO))
        partida.sonidos.reproducir("oleada_superada")

    def _festejar_objetivo(self):
        # El asedio tiene su propio festejo (terminar_asedio); los demas: puntos y un anillo verde
        partida = self.partida
        if self.objetivo.tipo == "asedio":
            return
        ganados = partida.sumar_puntos(OBJETIVO_PUNTOS * self.numero_sector)
        nave_x, nave_y = partida.nave.centro()
        partida.efectos.anillo(nave_x, nave_y, [(0, 90, 40), VERDE, (255, 255, 255)], 32, 6)
        partida.efectos.texto_flotante("¡OBJETIVO CUMPLIDO! +" + str(ganados), nave_x, nave_y - 40, VERDE)
        partida.sonidos.reproducir("bonus", nave_x)
        partida.entrada.vibrar("desafio")

    def _abrir_el_paso(self):
        # Demasiado tiempo sin cumplirlo: se pasa igual, pero sin premio (nadie se queda trabado)
        partida = self.partida
        self.objetivo.progreso = self.objetivo.meta
        self.objetivo_festejado = True
        self.despedir_escuadrones()
        nave_x, nave_y = partida.nave.centro()
        partida.efectos.texto_flotante("EL PASO SE ABRE", nave_x, nave_y - 40, AMARILLO)
        partida.sonidos.reproducir("anomalia_fin")

    def cumplir_objetivo(self):
        # Da el objetivo por cumplido (los tests; tambien sirve para probar desde el modo desarrollador)
        if self.objetivo is not None:
            self.objetivo.progreso = self.objetivo.meta

    def lanzar_escuadron(self, pedido=None):
        # El siguiente escuadron del guion (o 'pedido' = (tipo, cantidad, formacion), como el
        # modo desarrollador): cada miembro entra volando desde su lugar de la formacion
        partida = self.partida
        if pedido is None:
            if not self.cola:
                self.cola = list(self.tramo["escuadrones"])     # el tramo vuelve a empezar
            pedido = self.cola.pop(0)
            tipo, cantidad, formacion = pedido
            cantidad = self._cantidad(cantidad)
        else:
            tipo, cantidad, formacion = pedido
        turno = ASEDIO_TURNO if self.en_asedio else TURNO_ESCUADRON     # (al terminar el asedio se despiden)
        llega_en = partida.tiempo + AVISO_ESCUADRON + ENTRADA_ESCUADRON
        escuadron = Escuadron(tipo, llega_en, partida.tiempo + AVISO_ESCUADRON + turno)
        nave_x, nave_y = partida.nave.centro()
        for i, (desde, hasta) in enumerate(lugares(formacion, cantidad, nave_x, nave_y)):
            # Una "unidad" casi siempre es un enemigo; un enjambre son varios drones juntos
            unidad = crear_enemigos(tipo, partida)
            centro_x = sum(e.centro()[0] for e in unidad) / len(unidad)
            centro_y = sum(e.centro()[1] for e in unidad) / len(unidad)
            for enemigo in unidad:
                lejos_x, lejos_y = enemigo.centro()[0] - centro_x, enemigo.centro()[1] - centro_y
                enemigo.entrar(partida, (desde[0] + lejos_x, desde[1] + lejos_y),
                               (hasta[0] + lejos_x, hasta[1] + lejos_y), AVISO_ESCUADRON + i * ESCALONADO)
                escuadron.sumar(enemigo)
                partida.enemigos.append(enemigo)
            if i == 0:
                partida.sonidos.reproducir("escuadron_llega", max(0, min(desde[0], ANCHO)))  # (de que lado)
        self.escuadrones.append(escuadron)
        self._presentar(tipo)
        return escuadron

    def agregar(self, tipo):
        # Un enemigo suelto de ese tipo (lo usa el modo desarrollador)
        return self.lanzar_escuadron((tipo, 1, "flanco"))

    def _presentar(self, tipo):
        # La primera vez que llega un tipo en la partida, su ficha de "NUEVO ENEMIGO" (menos
        # el primero de todos: ese lo presenta el juego entero)
        if tipo in self.vistos:
            return
        self.vistos.add(tipo)
        if len(self.vistos) > 1:
            self.nuevo_tipo = TIPOS_ENEMIGO[tipo]
            self.tiempo_cartel_nuevo = self.partida.tiempo
            self.partida.sonidos.reproducir("ficha_enemigo")

    def _premiar_escuadron(self, escuadron):
        # Rompiste a todo el grupo (de dos o mas): puntos por cada uno. El enjambre ya tiene
        # su propio bonus
        partida = self.partida
        if len(escuadron.miembros) < 2 or escuadron.miembros[0].bonus_propio:
            return
        partida.estadisticas.escuadrones += 1
        ganados = partida.sumar_puntos(ESCUADRON_PUNTOS * len(escuadron.miembros))
        nave_x, nave_y = partida.nave.centro()
        partida.efectos.texto_flotante("¡ESCUADRON! +" + str(ganados), nave_x, nave_y - 40, AMARILLO)
        partida.sonidos.reproducir_luego("bonus", 120, nave_x)

    # ---------- Asedio ----------

    def empezar_asedio(self):
        partida = self.partida
        self.en_asedio = True
        self.proximo_asedio = math.inf
        self.asedio_hasta = partida.tiempo + ASEDIO_DURACION
        self.vidas_al_empezar_asedio = partida.vidas
        self.proximo_escuadron = partida.tiempo
        partida.sonidos.reproducir("oleada")
        partida.entrada.vibrar("oleada")
        partida.efectos.sacudir(10, ROJO)

    def terminar_asedio(self, superado):
        partida = self.partida
        if not self.en_asedio:
            return
        self.en_asedio = False
        self.asedio_cumplido = True
        if self.objetivo is not None:
            self.objetivo.al_terminar_asedio()      # (el objetivo del tramo 4: aguantar)
        if not superado and partida.enemigos:
            partida.sonidos.reproducir("retirada")
        self.despedir_escuadrones()
        self.proximo_escuadron = partida.tiempo + INICIO_TRAMO
        if superado:
            # Premio: puntos y un power-up que cae enseguida
            ganados = partida.sumar_puntos(ASEDIO_PUNTOS * partida.nivel)
            nave_x, nave_y = partida.nave.centro()
            partida.efectos.texto_flotante("+" + str(ganados), nave_x, nave_y - 40, AMARILLO)
            partida.avisar(Aviso("PREMIO", "¡ASEDIO SUPERADO!", "+" + str(ganados) + " PUNTOS Y UN POWER-UP",
                                 VERDE, AVISO_ASEDIO))
            partida.sonidos.reproducir("oleada_superada")
            if partida.capsula is None:
                partida.proximo_powerup = partida.tiempo

    # ---------- El jefe y el cierre del sector ----------

    def al_empezar_jefe(self):
        # Se corta todo lo del tramo (el asedio, la anomalia) y el desafio se decide: llegaste al jefe
        self.en_asedio = False
        self.terminar_anomalia()
        self.tramo = None
        self.numero_tramo = 0
        self.objetivo = None
        self.escuadrones = []
        self.proxima_anomalia = math.inf
        self.proximo_desafio = math.inf
        self.bitacora.inicio_jefe = self.partida.tiempo
        self.partida.modo.al_llegar_jefe()
        if self.desafio_en_curso():
            self.desafio.al_llegar_el_jefe()
            self.revisar_desafio()

    def al_vencer_al_jefe(self):
        # Vencido el jefe, se cierra el sector: "¡JEFE VENCIDO!", el cartel del rango, y
        # solo despues el sector nuevo (los carteles salen uno detras de otro)
        partida = self.partida
        bitacora = self.bitacora
        if bitacora.inicio_jefe is not None:
            bitacora.tiempo_jefe = partida.tiempo - bitacora.inicio_jefe
        self.rango = calcular_rango(bitacora, self.sector["jefe"], self.vuelta())
        self.rango["sector"] = self.numero_sector
        self.rango["color"] = self.sector["color"]
        partida.estadisticas.rangos.append(self.rango["letra"])
        if bitacora.golpes == 0:
            partida.estadisticas.sectores_limpios += 1
        self.tiempo_cartel_rango = partida.tiempo + CARTEL_JEFE
        self.rango_pagado = False
        self.fin_del_cierre = self.tiempo_cartel_rango + CARTEL_RANGO
        partida.modo.al_vencer_jefe(bitacora.golpes)
        if not partida.modo.sigue_despues_del_jefe():
            self.fin_de_la_partida = self.fin_del_cierre    # (la historia: se cumple la mision)
            return
        self.cambiar_sector()
        self.tiempo_cartel_sector = self.fin_del_cierre
        # El sector nuevo empieza con la bitacora en blanco y, al rato, un desafio nuevo
        self.bitacora = Bitacora()
        self.desafio = None
        self.proximo_desafio = self.fin_del_cierre + DESAFIO_ESPERA
        self.sector_por_empezar = True
        self.gasolinera_tras_cierre = True  # al terminar el cierre, a la gasolinera

    def cambiar_sector(self):
        # El siguiente de la lista (despues del ultimo, vuelve al primero)
        self.sector = SECTORES[(SECTORES.index(self.sector) + 1) % len(SECTORES)]
        self.numero_sector += 1
        self.tiempo_cartel_sector = self.partida.tiempo

    def _empezar_sector(self):
        # Termino el cierre: se pasa al primer nivel del sector nuevo (su tramo 1). Sin el
        # cartel del nivel: ya sale el del sector
        partida = self.partida
        self.sector_por_empezar = False
        primer_nivel = (self.numero_sector - 1) * JEFE_CADA_NIVELES + 1
        partida.nivel = max(partida.nivel, primer_nivel - 1)
        partida.subir_nivel(anunciar=False)

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
        self.partida.modo.al_recoger_moneda()
        if self._objetivo_en_curso():
            antes = self.objetivo.progreso
            self.objetivo.al_recoger_moneda(combo)
            self._si_avanzo(antes)
        if self.desafio_en_curso():
            self.desafio.al_recoger_moneda(combo)
            self.revisar_desafio()

    def al_interceptar(self):
        if self._objetivo_en_curso():
            antes = self.objetivo.progreso
            self.objetivo.al_interceptar()
            self._si_avanzo(antes)
        if self.desafio_en_curso():
            self.desafio.al_interceptar()
            self.revisar_desafio()

    def al_romper(self, enemigo):
        # Lo rompiste (con el dash, una onda o congelado): para el objetivo del tramo y el modo
        self.partida.modo.al_romper(enemigo)
        if self._objetivo_en_curso():
            antes = self.objetivo.progreso
            self.objetivo.al_romper(enemigo)
            self._si_avanzo(antes)

    def al_perfecto(self):
        if self._objetivo_en_curso():
            antes = self.objetivo.progreso
            self.objetivo.al_perfecto()
            self._si_avanzo(antes)

    def _si_avanzo(self, antes):
        # El objetivo sumo algo: el HUD lo hace destellar
        if self.objetivo.progreso > antes:
            self.tiempo_avance = self.partida.tiempo

    def _objetivo_en_curso(self):
        # Solo cuenta lo que pasa en un tramo, antes de cumplirlo
        return self.objetivo is not None and self.tramo is not None and not self.objetivo.cumplido()

    def al_destruir_enemigo(self):
        if self.desafio_en_curso():
            self.desafio.al_destruir_enemigo()
            self.revisar_desafio()

    # ---------- Cada paso ----------

    def actualizar(self):
        partida = self.partida
        if self.sector_por_empezar and not self.cerrando_sector():
            self._empezar_sector()
        if partida.tiempo >= self.fin_de_la_partida:
            partida.cumplida = True
        if partida.tiempo >= self.anuncio_en and self.tramo is not None:
            self._anunciar_tramo()
        if self.en_asedio and partida.tiempo >= self.asedio_hasta:
            self.terminar_asedio(superado=partida.vidas >= self.vidas_al_empezar_asedio)
        elif partida.tiempo >= self.proximo_asedio and partida.jefe is None and self.con_escuadrones:
            self.empezar_asedio()
        if self.anomalia is not None:
            self.anomalia.actualizar(partida)
            if self.anomalia.termino(partida):
                self.terminar_anomalia()
                partida.sonidos.reproducir("anomalia_fin")      # (si la corta el jefe, no suena)
        elif partida.tiempo >= self.proxima_anomalia and partida.jefe is None and not self.en_asedio:
            self.empezar_anomalia()
        self._escuadrones()
        self._revisar_objetivo()
        if partida.tiempo >= self.proximo_desafio and partida.jefe is None:
            self.proponer_desafio()
        self._sonidos_del_rango()
        if not self.rango_pagado and partida.tiempo >= self.tiempo_cartel_rango + RANGO_SELLO:
            self.pagar_rango()
        if self.gasolinera_tras_cierre and not self.cerrando_sector():
            self.gasolinera_tras_cierre = False
            self.gasolinera = self.con_mejoras

    # ---------- Anomalias ----------

    def elegir_anomalia(self):
        # Si el tramo dice cual ("anomalia" en su ruta: una mision de la historia la necesita),
        # esa. Si no, la del sector la mitad de las veces (ANOMALIA_PROPIA) y si no, una de las
        # otras: asi cada bioma tiene su personalidad, pero las cuatro se ven desde el principio
        if self.tramo is not None and self.tramo.get("anomalia"):
            return self.tramo["anomalia"]
        propia = self.sector["anomalia"]
        if propia is not None and random.random() < ANOMALIA_PROPIA:
            return propia
        return random.choice([tipo for tipo in TIPOS_ANOMALIA if tipo != propia])

    def empezar_anomalia(self, tipo=None):
        # 'tipo' elige cual (lo usa el modo desarrollador); sin tipo, elegir_anomalia()
        partida = self.partida
        if tipo is None:
            tipo = self.elegir_anomalia()
        self.anomalia = crear_anomalia(tipo, partida)
        self.proxima_anomalia = math.inf
        partida.sonidos.reproducir(self.anomalia.tipo + "_llega")
        partida.entrada.vibrar("anomalia")
        partida.efectos.sacudir(10, self.anomalia.color)
        partida.avisar(Aviso("ANOMALIA", self.anomalia.nombre, self.anomalia.pista, self.anomalia.color,
                             AVISO_ANOMALIA), urgente=True)

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
        partida.sonidos.reproducir("desafio_nuevo")

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
            partida.sonidos.reproducir("desafio_fallado")
            return
        self.bitacora.desafio_cumplido = True
        partida.estadisticas.desafios += 1
        ganados = partida.sumar_puntos(DESAFIO_PUNTOS * self.numero_sector)
        nave_x, nave_y = partida.nave.centro()
        partida.efectos.texto_flotante("¡DESAFIO! +" + str(ganados), nave_x, nave_y - 40, VERDE)
        partida.efectos.anillo(nave_x, nave_y, [(0, 90, 40), VERDE, (255, 255, 255)], 32, 6)
        partida.sonidos.reproducir("desafio_cumplido")
        partida.entrada.vibrar("desafio")
        if partida.capsula is None:
            partida.proximo_powerup = partida.tiempo     # de premio, un power-up enseguida

    # ---------- Mejoras ----------

    def ofrecer_mejoras(self):
        if self.con_mejoras:
            self.ofertas = sortear_mejoras(self.partida)

    # ---------- Rango ----------

    def _sonidos_del_rango(self):
        # Las filas del cartel del rango salen de a una (carteles.rango: la fila i a los
        # 300 + 400 * i ms y cada estrella 80 ms despues de la anterior): cada estrella suena
        # una nota mas arriba (estrella_1 a _5); una fila sin estrellas, un tic
        if self.rango is None or self.rango_pagado:
            return
        partida = self.partida
        transcurrido = partida.tiempo - self.tiempo_cartel_rango
        antes = transcurrido - MS_POR_FRAME
        estrellas = 0
        for i, fila in enumerate(self.rango["filas"]):
            desde_fila = 300 + i * 400
            ganadas = fila[2]
            momentos = [desde_fila + j * 80 for j in range(ganadas)] or [desde_fila]
            for j, momento in enumerate(momentos):
                if antes < momento <= transcurrido:
                    if ganadas:
                        partida.sonidos.reproducir("estrella_%d" % min(estrellas + j + 1, 5))
                    else:
                        partida.sonidos.reproducir("teclear")
            estrellas += ganadas

    def pagar_rango(self):
        # Cuando la letra aparece en el cartel: el premio y un golpe de efecto
        partida = self.partida
        self.rango_pagado = True
        if self.rango["puntos"]:
            partida.sumar_puntos(self.rango["puntos"])
        partida.sonidos.reproducir("sello_" + self.rango["letra"])
        partida.efectos.sacudir(10)
        # El sello de la letra: S y A pegan mas fuerte
        partida.entrada.vibrar("sello", fuerza=1.3 if self.rango["letra"] in ("S", "A") else 1)
