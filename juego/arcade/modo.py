"""
ModoArcade: las reglas del arcade (ver modos.py).

Empieza siempre en el Cinturon y recorre los sectores en orden; despues del ultimo vuelve al
primero. Despues de cada jefe hay gasolinera y sector nuevo. El Taller abre una sola vez,
en el nivel MEJORA_PRIMER_NIVEL, y el primer desafio llega en el nivel DESAFIO_DESDE_NIVEL
(los siguientes, al empezar cada sector: los programa el Director).
"""
from juego.config import (MEJORA_PRIMER_NIVEL, DESAFIO_DESDE_NIVEL, DIFICULTADES, TEXTO_SUAVE)
from juego.modos import Modo
from juego.rutas import RUTAS


class ModoArcade(Modo):
    nombre = "arcade"
    guarda_records = True

    def primer_sector(self):
        return 1

    def ruta(self, numero_sector):
        # Despues del ultimo sector, las rutas vuelven a empezar
        return RUTAS[(numero_sector - 1) % len(RUTAS)]

    def abre_el_taller(self, director):
        return self.partida.nivel == MEJORA_PRIMER_NIVEL

    def propone_desafio(self, director):
        return self.partida.nivel == DESAFIO_DESDE_NIVEL and director.numero_sector == 1

    def sigue_despues_del_jefe(self):
        return True

    def encabezado(self, director):
        dificultad = self.partida.dificultad
        return [("SECTOR " + str(director.numero_sector) + "  ", TEXTO_SUAVE),
                (director.sector["nombre"], director.sector["color"]), ("   ", TEXTO_SUAVE),
                (dificultad, DIFICULTADES[dificultad]["color"])]
