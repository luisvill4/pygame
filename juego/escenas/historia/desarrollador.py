"""
El panel del desarrollador en la GALAXIA (F1, si MODO_DESARROLLADOR esta encendido en config.py):
para ver la historia sin jugarla entera. Es un PanelDesarrollador (escenas/desarrollador.py):
la base pone las filas, el dibujo y la vuelta; aqui va solo lo de cada fila.

    MISION       < 1 LA SEÑAL >    va ya al dialogo de antes: sin viajar, sin que pasen años
                                   y sin bloqueos (tambien la oculta)
    SECRETO      < F01 >  SI       ENTER lo encuentra o lo olvida (los dialogos cambian con eso)
    AÑO          < 1.5 >           IZQ/DER mueven el reloj de la Umbral (al volver atras, los
                                   mensajes de Ines de esos años se pueden ver otra vez)
    MODULOS      3 DE 8            todos los planos y todos los modulos al maximo
    PIEZAS       TIENES 30         +500 piezas para el hangar
    VOLVER

OJO: todo esto se guarda en progreso.json, como si lo hubieras jugado.
"""
from juego.config import MAREA_ANIOS
from juego.escenas.desarrollador import PanelDesarrollador
from juego.historia.mision import misiones_en_orden, todos_los_fragmentos
from juego.historia import galaxia, modulos

FILAS = ["MISION", "SECRETO", "AÑO", "MODULOS", "PIEZAS", "VOLVER"]
PIEZAS_DE_PRUEBA = 500
PASO_ANIOS = 0.5

AYUDA = {
    "MISION": "VA YA AL DIALOGO DE ANTES (SIN VIAJAR)",
    "AÑO": "IZQ/DER MUEVEN EL RELOJ DE LA UMBRAL",
    "MODULOS": "TODOS LOS PLANOS Y MODULOS AL MAXIMO",
    "PIEZAS": "+%d PIEZAS PARA EL HANGAR" % PIEZAS_DE_PRUEBA,
    "VOLVER": "VUELVE A LA GALAXIA",
}


class DesarrolladorGalaxia(PanelDesarrollador):
    recuerdo = {"pestana": 0, "fila": 0, "mision": 0, "secreto": 0}

    def __init__(self, app, escena_galaxia, captura):
        super().__init__(app, escena_galaxia, captura)
        self.galaxia = escena_galaxia
        self.progreso = app.progreso

    def pestanas(self):
        return [("GALAXIA", FILAS)]

    # ---------- Lo elegido ----------

    def mision(self):
        misiones = misiones_en_orden()
        return misiones[self.recuerdo["mision"] % len(misiones)]

    def fragmento(self):
        fragmentos = [fragmento for fragmento, _ in todos_los_fragmentos()]
        return fragmentos[self.recuerdo["secreto"] % len(fragmentos)]

    def cambiar(self, fila, paso):
        if fila == "MISION":
            self.recuerdo["mision"] = (self.recuerdo["mision"] + paso) % len(misiones_en_orden())
        elif fila == "SECRETO":
            self.recuerdo["secreto"] = (self.recuerdo["secreto"] + paso) % len(todos_los_fragmentos())
        elif fila == "AÑO":
            self._mover_el_reloj(paso * PASO_ANIOS)

    # ---------- Lo que hace cada fila ----------

    def hacer(self, fila):
        progreso = self.progreso
        if fila == "MISION":
            uno = galaxia.sistema("M%d" % self.mision().numero)
            progreso.ubicacion = uno.id
            progreso.guardar()
            self.galaxia.despegar(uno)
        elif fila == "SECRETO":
            fragmento = self.fragmento()
            if fragmento.id in progreso.fragmentos:
                progreso.fragmentos.discard(fragmento.id)
                self.app.avisar(fragmento.id + " OLVIDADO")
            else:
                progreso.fragmentos.add(fragmento.id)
                self.app.sonidos.reproducir("fragmento")
                self.app.avisar(fragmento.id + " ENCONTRADO")
            progreso.guardar()
        elif fila == "MODULOS":
            for modulo in modulos.MODULOS:
                progreso.planos.add(modulo.id)
                progreso.hangar[modulo.id] = modulo.maximo
            progreso.guardar()
            self.app.avisar("MODULOS AL MAXIMO")
        elif fila == "PIEZAS":
            progreso.piezas += PIEZAS_DE_PRUEBA
            progreso.guardar()
            self.app.avisar("+%d PIEZAS" % PIEZAS_DE_PRUEBA)
        self.galaxia.refrescar()        # (la nave con sus modulos, lo que se ve en el mapa)

    def _mover_el_reloj(self, anios):
        # Volver atras deja ver otra vez los mensajes de Ines de esos años
        progreso = self.progreso
        progreso.anios = min(max(0.0, progreso.anios + anios), float(MAREA_ANIOS))
        progreso.mensajes = {anio for anio in progreso.mensajes if anio <= progreso.anios}
        progreso.guardar()

    def al_volver(self):
        self.galaxia.refrescar()

    # ---------- Lo que se ve ----------

    def valor(self, fila):
        progreso = self.progreso
        if fila == "MISION":
            mision = self.mision()
            return "< %d %s >" % (mision.numero, mision.titulo)
        if fila == "SECRETO":
            id_ = self.fragmento().id
            return "< " + id_ + " >  " + ("SI" if id_ in progreso.fragmentos else "NO")
        if fila == "AÑO":
            return "< %.1f >" % progreso.anios
        if fila == "MODULOS":
            niveles = sum(modulos.nivel(progreso, modulo.id) for modulo in modulos.MODULOS)
            return "%d DE %d" % (niveles, sum(modulo.maximo for modulo in modulos.MODULOS))
        if fila == "PIEZAS":
            return "TIENES %d" % progreso.piezas
        return ""

    def ayuda(self, fila):
        if fila == "SECRETO":
            # El nombre no entra en la fila: va abajo
            fragmento = self.fragmento()
            return fragmento.nombre + (": LO OLVIDA" if fragmento.id in self.progreso.fragmentos else ": LO ENCUENTRA")
        return AYUDA.get(fila, "")

    def advertencia(self):
        return "TODO SE GUARDA EN TU PROGRESO"
