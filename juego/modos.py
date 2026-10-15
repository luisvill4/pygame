"""
Modos de juego: ARCADE (juego/arcade/) e HISTORIA (juego/historia/).

Patron Strategy: la Partida y el Director no preguntan "¿es la historia?". Le preguntan
al MODO que tienen (partida.modo) lo que cambia de uno a otro:
    - en que sector empieza y que ruta de tramos sigue;
    - cuando abre el Taller y cuando llega el desafio;
    - si despues del jefe sigue la ruta (arcade) o se cumple la partida (historia);
    - y le avisan lo que pasa (empieza un tramo, llega el jefe...), por si quiere contar algo.
Asi, para cambiar como funciona un modo se toca solo su archivo, y un modo nuevo (un
desafio diario, un tutorial...) es otra clase que hereda de Modo.

Esta clase es la base (patron Template Method): los avisos y el dibujo no hacen nada por
defecto y las reglas las escribe cada modo. Lo que pasa ENTRE PANTALLAS segun el modo (al
morir, al cumplir) esta en las escenas: escenas/pasajes.py.
"""
from juego.config import JEFE_CADA_NIVELES


class Modo:
    nombre = None               # "arcade", "historia": con esto se buscan sus pasajes (escenas/pasajes.py)
    guarda_records = True       # ¿la partida entra a la tabla de records?
    cuenta_logros = True        # ¿se desbloquean logros? (miden el avance del arcade: sectores, niveles...)

    def empezar(self, partida):
        # Al crear la partida, antes que el Director: el modo se guarda la partida y la prepara
        self.partida = partida
        partida.nivel = (self.primer_sector() - 1) * JEFE_CADA_NIVELES + 1

    # ---------- Reglas (cada modo escribe las suyas) ----------

    def primer_sector(self):
        # Numero del sector donde empieza (1 = el Cinturon)
        raise NotImplementedError

    def ruta(self, numero_sector):
        # Los 4 tramos de ese sector (rutas.py)
        raise NotImplementedError

    def abre_el_taller(self, director):
        # ¿Al empezar este nivel se ofrecen las cartas gratis del Taller?
        raise NotImplementedError

    def propone_desafio(self, director):
        # ¿Al empezar este nivel llega el desafio del sector?
        raise NotImplementedError

    def sigue_despues_del_jefe(self):
        # True: despues del jefe, gasolinera y sector siguiente. False: la partida se cumple
        raise NotImplementedError

    def encabezado(self, director):
        # El renglon de arriba en READY: [(texto, color), ...]
        raise NotImplementedError

    def hay_jefe(self):
        # False: despues del ultimo tramo no viene el jefe y la partida se cumple ahi
        # (una mision tranquila de la historia). Casi siempre hay jefe
        return True

    # ---------- Avisos (el Director y la Partida le cuentan lo que pasa) ----------

    def al_empezar_tramo(self, numero):
        pass

    def al_llegar_jefe(self):
        pass

    def al_vencer_jefe(self, golpes):
        pass

    def al_recoger_moneda(self):
        pass

    def al_romper(self, enemigo):
        # Rompiste un enemigo (con el dash, una onda o congelado)
        pass

    def al_romper_parte(self, jefe, parte):
        # Rompiste una pieza del jefe (un cañon, una compuerta)
        pass

    def al_golpear_jefe(self, jefe):
        # Le pegaste en el nucleo (se avisa antes del rebote: la nave sigue donde pego)
        pass

    def al_escapar_moneda(self, ladron):
        # Un ladron salio de la pantalla con la moneda
        pass

    # ---------- Cada paso y el dibujo (lo propio del modo) ----------

    def actualizar(self):
        pass

    def dibujar(self, pantalla):
        # Debajo de todo lo demas del mundo (ver Partida._dibujar_todo)
        pass

    def objetos_que_se_mueven(self):
        # Lo suyo que se dibuja interpolado
        return []
