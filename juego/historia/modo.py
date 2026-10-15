"""
ModoHistoria: una partida del modo historia es UNA mision (ver modos.py y mision.py).

Las reglas: empieza en el sector de la mision y sigue su ruta; el Taller abre en el tramo
MEJORA_TRAMO_HISTORIA y el desafio llega en el tramo 2; al vencer al jefe la partida se
cumple (no hay gasolinera ni sector siguiente); no guarda records.

Ademas cuenta la historia mientras jugas:
- por la radio, lo que la mision tiene para cada momento ("tramo_2", "jefe"...);
- los secretos de la mision (secretos.py): les pasa los avisos, mueve las reliquias que
  sueltan y, cuando tocas una o se cumple una condicion, guarda el fragmento (encontrar).
Lo encontrado va a progreso.json AL INSTANTE (aunque despues pierdas) y se cuenta por la
radio, sin cartel de "¡SECRETO!".
"""
from juego.config import (RADIO_DEMORA_TRAMO, RADIO_DEMORA_JEFE, MEJORA_TRAMO_HISTORIA, VIOLETA, BLANCO,
                          TEXTO_SUAVE, DIFICULTADES)
from juego.modos import Modo
from juego.rutas import RUTAS
from juego.historia.mision import mision, buscar_fragmento
from juego.historia.secretos import crear_secreto
from juego.historia import misiones  # noqa: F401  (registra todas las misiones)


class ModoHistoria(Modo):
    nombre = "historia"
    guarda_records = False

    def __init__(self, numero):
        self.mision = mision(numero)        # la clase de la mision (historia/misiones/)

    def empezar(self, partida):
        super().empezar(partida)
        self.reliquias = []                 # lo que los secretos dejaron en pantalla
        self.encontrados = set()            # lo encontrado en esta partida (si no hay progreso guardado)
        self.secretos = [crear_secreto(datos, self) for datos in self.mision.secretos]

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

    def encabezado(self, director):
        dificultad = self.partida.dificultad
        return [("MISION " + str(self.mision.numero) + "  ", TEXTO_SUAVE),
                (self.mision.titulo, director.sector["color"]), ("   ", TEXTO_SUAVE),
                (dificultad, DIFICULTADES[dificultad]["color"])]

    # ---------- Avisos: la radio y los secretos ----------

    def al_empezar_tramo(self, numero):
        self.decir("tramo_%d" % numero, RADIO_DEMORA_TRAMO)
        for secreto in self.secretos:
            secreto.al_empezar_tramo(numero)

    def al_llegar_jefe(self):
        self.decir("jefe", RADIO_DEMORA_JEFE)       # (despues de su presentacion)
        for secreto in self.secretos:
            secreto.al_llegar_jefe()

    def al_vencer_jefe(self, golpes):
        for secreto in self.secretos:
            secreto.al_vencer_jefe(golpes)

    def al_recoger_moneda(self):
        for secreto in self.secretos:
            secreto.al_recoger_moneda()

    # ---------- Cada paso y el dibujo ----------

    def actualizar(self):
        partida = self.partida
        for secreto in self.secretos:
            secreto.actualizar()
        for reliquia in list(self.reliquias):
            reliquia.mover(partida)
            if reliquia.tocada(partida):
                self.reliquias.remove(reliquia)
                centro_x, centro_y = reliquia.caja().center
                partida.efectos.explosion(centro_x, centro_y, [(40, 20, 70), VIOLETA, BLANCO], 18, 4, 3)
                self.encontrar(reliquia.fragmento)
            elif reliquia.termino(partida):
                self.reliquias.remove(reliquia)

    def dibujar(self, pantalla):
        for reliquia in self.reliquias:
            reliquia.dibujar(pantalla, self.partida)

    def objetos_que_se_mueven(self):
        return self.reliquias

    # ---------- Lo que usan los secretos ----------

    def ya_encontrado(self, id_fragmento):
        progreso = self.partida.progreso
        return id_fragmento in self.encontrados or (progreso is not None and id_fragmento in progreso.fragmentos)

    def encontrar(self, id_fragmento):
        if self.ya_encontrado(id_fragmento):
            return
        self.encontrados.add(id_fragmento)
        partida = self.partida
        if partida.progreso is not None:
            partida.progreso.encontrar_fragmento(id_fragmento)
        partida.estadisticas.fragmentos += 1
        partida.sonidos.reproducir("logro")
        partida.radio.decir(buscar_fragmento(id_fragmento).reaccion, partida.tiempo)

    def decir(self, momento, demora=0):
        renglones = self.mision.radio.get(momento, [])
        self.partida.radio.decir(renglones, self.partida.tiempo, demora)
