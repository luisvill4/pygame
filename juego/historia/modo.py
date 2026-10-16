"""
ModoHistoria: una partida del modo historia es UNA mision (ver modos.py y mision.py).

Las reglas: empieza en el sector de la mision y sigue su ruta; el Taller abre en el tramo
MEJORA_TRAMO_HISTORIA y el desafio llega en el tramo 2; al vencer al jefe la partida se
cumple (no hay gasolinera ni sector siguiente); una mision sin jefe se cumple al despejar
el ultimo tramo; no guarda records.

Ademas cuenta la historia mientras jugas:
- por la radio, lo que la mision tiene para cada momento ("tramo_2", "jefe"...), segun lo
  que ya encontraste (los renglones con condicion, ver mision.py);
- los secretos de la mision (secretos.py): les pasa los avisos, mueve las reliquias que
  sueltan y, cuando tocas una o se cumple una condicion, guarda el fragmento (encontrar);
- las fichas del Archivo (fichas.py): lo que aparece en pantalla por primera vez se anota.
Lo encontrado va a progreso.json AL INSTANTE (aunque despues pierdas) y se cuenta por la
radio, sin cartel de "¡SECRETO!".
"""
from juego.config import (RADIO_DEMORA_TRAMO, RADIO_DEMORA_JEFE, MEJORA_TRAMO_HISTORIA, VIOLETA, BLANCO,
                          TEXTO_SUAVE, DIFICULTADES)
from juego.modos import Modo
from juego.rutas import RUTAS
from juego.historia.mision import mision, buscar_fragmento, filtrar
from juego.historia.secretos import crear_secreto
from juego.historia import fichas, hangar, ecos, modulos
from juego.historia import misiones  # noqa: F401  (registra todas las misiones)

MIRAR_CADA = 30             # cada cuantos pasos se fija que hay en pantalla (para las fichas)


class ModoHistoria(Modo):
    nombre = "historia"
    guarda_records = False
    cuenta_logros = False       # (empezar una mision en el sector 5 no es "llegar al sector 5")

    def __init__(self, numero):
        self.mision = mision(numero)        # la clase de la mision (historia/misiones/)

    def empezar(self, partida):
        super().empezar(partida)
        self.reliquias = []                 # lo que los secretos dejaron en pantalla
        self.encontrados = set()            # lo encontrado en esta partida (si no hay progreso guardado)
        self.secretos = [crear_secreto(datos, self) for datos in self.mision.secretos]
        self.pasos = 0
        for id_ficha in fichas.BASICAS:
            self.anotar(id_ficha)
        if partida.progreso is not None:
            hangar.instalar(partida, partida.progreso)      # lo comprado en el hangar, desde el despegue

    # ---------- Reglas ----------

    def primer_sector(self):
        return self.mision.sector

    def ruta(self, numero_sector):
        return self.mision.tramos or RUTAS[self.mision.sector - 1]

    def abre_el_taller(self, director):
        return director.numero_tramo == MEJORA_TRAMO_HISTORIA

    def propone_desafio(self, director):
        return director.numero_tramo == 2

    def sigue_despues_del_jefe(self):
        return False

    def hay_jefe(self):
        return self.mision.jefe

    def equipo(self):
        # Los modulos y el impulsor que se compraron se ven en la Alondra
        progreso = self.partida.progreso
        return modulos.equipo(progreso) if progreso is not None else ()

    def encabezado(self, director):
        dificultad = self.partida.dificultad
        return [("MISION " + str(self.mision.numero) + "  ", TEXTO_SUAVE),
                (self.mision.titulo, director.sector["color"]), ("   ", TEXTO_SUAVE),
                (dificultad, DIFICULTADES[dificultad]["color"])]

    # ---------- Avisos: la radio y los secretos ----------

    def _avisar_a_los_secretos(self, aviso, *datos):
        for secreto in self.secretos:
            getattr(secreto, aviso)(*datos)

    def al_empezar_tramo(self, numero):
        self.decir("tramo_%d" % numero, RADIO_DEMORA_TRAMO)
        self._avisar_a_los_secretos("al_empezar_tramo", numero)

    def al_llegar_jefe(self):
        self.decir("jefe", RADIO_DEMORA_JEFE)       # (despues de su presentacion)
        self._avisar_a_los_secretos("al_llegar_jefe")

    def al_vencer_jefe(self, golpes):
        self._avisar_a_los_secretos("al_vencer_jefe", golpes)

    def al_recoger_moneda(self):
        self._avisar_a_los_secretos("al_recoger_moneda")

    def al_romper(self, enemigo):
        self._avisar_a_los_secretos("al_romper", enemigo)

    def al_romper_parte(self, jefe, parte):
        self._avisar_a_los_secretos("al_romper_parte", jefe, parte)

    def al_golpear_jefe(self, jefe):
        self._avisar_a_los_secretos("al_golpear_jefe", jefe)

    def al_escapar_moneda(self, ladron):
        self._avisar_a_los_secretos("al_escapar_moneda", ladron)

    # ---------- Cada paso y el dibujo ----------

    def actualizar(self):
        partida = self.partida
        self._avisar_a_los_secretos("actualizar")
        for reliquia in list(self.reliquias):
            reliquia.mover(partida)
            if reliquia.tocada(partida):
                self.reliquias.remove(reliquia)
                centro_x, centro_y = reliquia.caja().center
                partida.efectos.explosion(centro_x, centro_y, [(40, 20, 70), VIOLETA, BLANCO], 18, 4, 3)
                self.encontrar(reliquia.fragmento)
            elif reliquia.termino(partida):
                self.reliquias.remove(reliquia)
        self.pasos += 1
        if self.pasos % MIRAR_CADA == 0:
            self._mirar_la_pantalla()

    def _mirar_la_pantalla(self):
        # Lo que se ve por primera vez va a las fichas del Archivo
        partida = self.partida
        for enemigo in partida.enemigos:
            if not enemigo.fuera_de_la_pantalla():
                self.anotar(fichas.id_de("enemigo", enemigo.tipo))
        if partida.jefe is not None:
            self.anotar(fichas.id_de("jefe", partida.jefe.tipo))
        if partida.capsula is not None:
            self.anotar(fichas.id_de("powerup", partida.capsula.powerup.tipo))
        if partida.director.anomalia is not None:
            self.anotar(fichas.id_de("anomalia", partida.director.anomalia.tipo))

    def dibujar(self, pantalla):
        for reliquia in self.reliquias:
            reliquia.dibujar(pantalla, self.partida)

    def objetos_que_se_mueven(self):
        return self.reliquias

    # ---------- Lo que usan los secretos ----------

    def ya_encontrado(self, id_fragmento):
        return id_fragmento in self.lo_encontrado()

    def lo_encontrado(self):
        progreso = self.partida.progreso
        return self.encontrados | (progreso.fragmentos if progreso is not None else set())

    def encontrar(self, id_fragmento):
        if self.ya_encontrado(id_fragmento):
            return
        self.encontrados.add(id_fragmento)
        partida = self.partida
        if partida.progreso is not None:
            partida.progreso.encontrar_fragmento(id_fragmento)
        partida.estadisticas.fragmentos += 1
        partida.sonidos.reproducir("fragmento")
        fragmento = ecos.POR_ID.get(id_fragmento) or buscar_fragmento(id_fragmento)
        partida.radio.decir(filtrar(fragmento.reaccion, self.lo_encontrado(), self.anios()), partida.tiempo)

    def anios(self):
        # Los años de la Umbral (para los renglones con "T6")
        progreso = self.partida.progreso
        return progreso.anios if progreso is not None else 0

    def anotar(self, id_ficha):
        progreso = self.partida.progreso
        if progreso is not None and id_ficha in fichas.POR_ID:
            progreso.anotar_ficha(id_ficha)

    def decir(self, momento, demora=0):
        renglones = filtrar(self.mision.radio.get(momento, []), self.lo_encontrado(), self.anios())
        self.partida.radio.decir(renglones, self.partida.tiempo, demora)
