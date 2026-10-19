"""
Modo desarrollador: paneles para probar sin tener que llegar jugando (si MODO_DESARROLLADOR
esta encendido en config.py).

PanelDesarrollador es la base (patron Template Method): las pestañas, las filas, moverse,
el dibujo y volver. Cada panel escribe solo lo suyo:
    pestanas()              [(nombre, [filas]), ...]
    valor(fila)             lo que se ve a la derecha de la fila
    ayuda(fila)             lo que hace (debajo del panel)
    cambiar(fila, paso)     IZQ/DER
    hacer(fila)             ENTER (despues de volver: asi el sonido de lo que pasa no queda en pausa)
El panel recuerda la pestaña y la fila de la ultima vez (asi "F1 + ENTER" repite lo mismo).

Desarrollador: el de la partida. Se abre con F1 jugando y, como la pausa, el tiempo de la
partida no corre mientras esta abierto. Dos pestañas:

    PROBAR
    JEFE         < EL OJO >        trae ese jefe ahora (si ya hay uno, lo cambia)
    ENEMIGO      < PERSEGUIDOR >   trae un enemigo de ese tipo (aparece con su "X")
    POWER-UP     < ESCUDO >        te lo da enseguida, como si recogieras la capsula
    ANOMALIA     < NIEBLA CERRADA > la trae ahora (si ya habia una, la cambia; con un jefe, no)
    INVENCIBLE   NO                nada te hace daño
    LIMPIAR                        saca a todos los enemigos y las balas
    GASOLINERA   +200 CREDITOS     abre la tienda (con 200 creditos de regalo para probar)

    AVANZAR (para ver la historia sin jugar cada tramo)
    SALTAR TRAMO 1-2               el tramo cumplido y la zona despejada: pasa al siguiente
    VENCER JEFE                    el golpe final, ya (y lo que sigue: el dialogo de despues)
    SECRETO      < F01 >           lo encuentra ahora (la lista se la pide al modo)

Apenas se usa algo, la partida queda marcada (partida.modo_desarrollador): ya no guarda
record ni logros, y el HUD muestra "MODO DEV".

Las listas salen de los registros (TIPOS_JEFE, TIPOS_ENEMIGO, TIPOS_POWERUP, TIPOS_ANOMALIA):
un jefe, enemigo, power-up o anomalia nuevo aparece aqui solo, sin tocar este archivo.
"""
import pygame

from juego import dibujo, interfaz
from juego.dibujo import texto, CHICA, MEDIA, GRANDE
from juego.config import MAGENTA, AMARILLO, BLANCO, ROJO, FILA_ELEGIDA, FONDO
from juego.entrada import (VOLVER, DESARROLLADOR, ACEPTAR, ARRIBA, ABAJO, IZQUIERDA, DERECHA, PESTANA_ANTERIOR,
                           PESTANA_SIGUIENTE)
from juego.escenas.base import Escena
from juego.jefes import TIPOS_JEFE
from juego.enemigos import TIPOS_ENEMIGO
from juego.powerups import TIPOS_POWERUP
from juego.anomalias import TIPOS_ANOMALIA

FILA_Y = 188            # y de la primera fila
ALTO_FILA = 33          # (con 8 filas, mas que esto se sale del marco)
BARRA_PESTANAS = pygame.Rect(80, 124, 640, 28)
CREDITOS_DE_PRUEBA = 200

FILAS = ["JEFE", "ENEMIGO", "POWER-UP", "ANOMALIA", "INVENCIBLE", "LIMPIAR", "GASOLINERA", "VOLVER"]
FILAS_AVANZAR = ["SALTAR TRAMO", "VENCER JEFE", "SECRETO", "INVENCIBLE", "VOLVER"]

# Lo que se elige con IZQ/DER en cada fila (las abejas no: solo existen con la Colmena)
ELEGIBLES = {
    "JEFE": list(TIPOS_JEFE),
    "ENEMIGO": [tipo for tipo, clase in TIPOS_ENEMIGO.items() if not clase.esbirro],
    "POWER-UP": list(TIPOS_POWERUP),
    "ANOMALIA": list(TIPOS_ANOMALIA),
}
_elegido = {fila: 0 for fila in ELEGIBLES}     # lo ultimo elegido (se recuerda al volver a abrir)

# Que hace cada fila (se ve debajo del panel)
AYUDA_FILA = {
    "JEFE": "LO TRAE AHORA (SI YA HAY UNO, LO CAMBIA)",
    "ENEMIGO": "APARECE LEJOS DE LA NAVE, CON SU X",
    "POWER-UP": "TE LO DA ENSEGUIDA",
    "ANOMALIA": "LA TRAE AHORA (CON UN JEFE NO SE PUEDE)",
    "INVENCIBLE": "NADA TE QUITA VIDAS",
    "LIMPIAR": "SACA A LOS ENEMIGOS Y LAS BALAS",
    "GASOLINERA": "ABRE LA TIENDA CON CREDITOS DE REGALO",
    "SALTAR TRAMO": "CUMPLIDO Y DESPEJADO: PASA AL SIGUIENTE",
    "VENCER JEFE": "EL GOLPE FINAL, YA",
    "VOLVER": "VUELVE AL JUEGO",
}


def nombre_de(fila, tipo):
    # Como se ve cada opcion en el panel
    if fila == "JEFE":
        return TIPOS_JEFE[tipo].nombre
    if fila == "POWER-UP":
        return TIPOS_POWERUP[tipo].nombre
    if fila == "ANOMALIA":
        # El nombre del cartel, si entra ("LLUVIA DE ASTEROIDES" es muy largo: se usa el tipo)
        nombre = TIPOS_ANOMALIA[tipo].nombre
        return nombre if len(nombre) <= 14 else tipo.upper()
    return tipo.upper().replace("_", " ")       # los 3 divisores se llaman "DIVISOR": se usa el tipo


class PanelDesarrollador(Escena):
    titulo = "DESARROLLADOR"
    recuerdo = None             # cada panel el suyo: {"pestana": n, "fila": n}

    def __init__(self, app, volver_a, captura):
        super().__init__(app)
        self.volver_a = volver_a            # la escena a donde se vuelve
        self.captura = captura              # imagen de esa escena al abrir el panel
        self.fondo = interfaz.pixelado(captura, oscuridad=180)
        self.pestana = min(self.recuerdo["pestana"], len(self.pestanas()) - 1)
        self.fila = min(self.recuerdo["fila"], len(self.filas()) - 1)

    def filas(self):
        return self.pestanas()[self.pestana][1]

    # ---------- Lo que escribe cada panel ----------

    def pestanas(self):
        raise NotImplementedError

    def valor(self, fila):
        return ""

    def ayuda(self, fila):
        return ""

    def cambiar(self, fila, paso):
        pass

    def hacer(self, fila):
        raise NotImplementedError

    def al_volver(self):
        # Para los paneles: algo que hacer antes de volver a su escena
        pass

    # ---------- Logica ----------

    def actualizar(self, entrada):
        if entrada.pulso(DESARROLLADOR) or entrada.pulso(VOLVER):
            self._volver()
            return
        if len(self.pestanas()) > 1 and (entrada.pulso(PESTANA_ANTERIOR) or entrada.pulso(PESTANA_SIGUIENTE)):
            paso = 1 if entrada.pulso(PESTANA_SIGUIENTE) else -1
            self.pestana = (self.pestana + paso) % len(self.pestanas())
            self.fila = min(self.fila, len(self.filas()) - 1)
            self.app.sonidos.reproducir("ui_mover")
            self._recordar()
            return
        for accion in entrada.acciones:
            if accion in (ARRIBA, ABAJO):
                self.fila = (self.fila + (1 if accion == ABAJO else -1)) % len(self.filas())
                self.app.sonidos.reproducir("ui_mover")
                self._recordar()
            elif accion in (IZQUIERDA, DERECHA):
                self.cambiar(self.filas()[self.fila], 1 if accion == DERECHA else -1)
                self.app.sonidos.reproducir("ui_valor_sube" if accion == DERECHA else "ui_valor_baja")
            elif accion == ACEPTAR:
                # Primero se vuelve (asi el sonido de lo que pasa ya no esta en pausa)
                fila = self.filas()[self.fila]
                self._volver()
                if fila != "VOLVER":
                    self.hacer(fila)
                return

    def _recordar(self):
        self.recuerdo["pestana"] = self.pestana
        self.recuerdo["fila"] = self.fila

    def _volver(self):
        self.al_volver()
        self.app.sonidos.reanudar_todo()
        self.app.cambiar_escena(self.volver_a, transicion=False)

    # ---------- Dibujo ----------

    def dibujar(self, pantalla_completa):
        pantalla_completa.blit(self.fondo, (0, 0))
        pantalla = dibujo.zona_central(pantalla_completa)
        dibujo.texto_3d(pantalla, self.titulo, GRANDE, MAGENTA, (90, 0, 60), 84)
        pestanas = self.pestanas()
        if len(pestanas) > 1:
            interfaz.pestanas(pantalla, BARRA_PESTANAS, self.app.entrada, [nombre for nombre, _ in pestanas],
                              self.pestana, MAGENTA, FONDO)

        interfaz.panel(pantalla, pygame.Rect(80, 160, 640, 290), MAGENTA)
        for i, fila in enumerate(self.filas()):
            fila_y = FILA_Y + i * ALTO_FILA
            elegida = i == self.fila
            if elegida:
                pantalla.fill(FILA_ELEGIDA, (96, fila_y - ALTO_FILA // 2 + 2, 608, ALTO_FILA - 4))
                pantalla.fill(AMARILLO, (96, fila_y - ALTO_FILA // 2 + 2, 4, ALTO_FILA - 4))
            texto(pantalla, fila, MEDIA, AMARILLO if elegida else BLANCO, 120, fila_y, alinear="izquierda")
            texto(pantalla, self.valor(fila), CHICA, AMARILLO if elegida else BLANCO, 700, fila_y, alinear="derecha")

        fila = self.filas()[self.fila]
        texto(pantalla, self.ayuda(fila) or AYUDA_FILA.get(fila, ""), CHICA, BLANCO, 400, 480)
        texto(pantalla, self.advertencia(), CHICA, ROJO, 400, 510)
        pares = [("elegir", "ELEGIR"), ("cambiar", "CAMBIAR"), ("aceptar", "HACER"), ("desarrollador", "VOLVER")]
        if len(pestanas) > 1:
            pares.insert(0, ("pestanas", "SECCION"))
        interfaz.ayudas(pantalla_completa, self.app.entrada, pares)

    def advertencia(self):
        return ""


class Desarrollador(PanelDesarrollador):
    recuerdo = {"pestana": 0, "fila": 0, "secreto": 0}     # (el secreto: cual de la lista del modo)

    def __init__(self, app, escena_juego, captura):
        super().__init__(app, escena_juego, captura)
        self.escena_juego = escena_juego
        self.partida = escena_juego.partida

    def pestanas(self):
        return [("PROBAR", FILAS), ("AVANZAR", FILAS_AVANZAR)]

    def elegido(self, fila):
        # El tipo elegido ahora en esa fila (ej: "ojo")
        return ELEGIBLES[fila][_elegido[fila]]

    def secretos(self):
        # [(id, nombre, encontrado)]: los que el modo deja dar (el arcade, ninguno)
        return self.partida.modo.secretos_de_prueba()

    def cambiar(self, fila, paso):
        if fila in ELEGIBLES:
            _elegido[fila] = (_elegido[fila] + paso) % len(ELEGIBLES[fila])
        elif fila == "SECRETO" and self.secretos():
            self.recuerdo["secreto"] = (self.recuerdo["secreto"] + paso) % len(self.secretos())

    def hacer(self, fila):
        # Lo que hace cada fila al apretar ENTER
        partida = self.partida
        partida.modo_desarrollador = True       # desde ahora: sin record ni logros
        if fila == "JEFE":
            self._traer_jefe(self.elegido("JEFE"))
        elif fila == "ENEMIGO":
            tipo = self.elegido("ENEMIGO")
            partida.director.agregar(tipo)
            self.app.avisar("+ " + nombre_de("ENEMIGO", tipo))
        elif fila == "POWER-UP":
            self._dar_powerup(TIPOS_POWERUP[self.elegido("POWER-UP")])
        elif fila == "ANOMALIA":
            self._traer_anomalia(self.elegido("ANOMALIA"))
        elif fila == "INVENCIBLE":
            partida.invencible = not partida.invencible
            self.app.avisar("INVENCIBLE: " + ("SI" if partida.invencible else "NO"))
        elif fila == "LIMPIAR":
            self._limpiar()
        elif fila == "GASOLINERA":
            # La escena Juego la abre en el proximo paso (como despues de un jefe)
            partida.ganar_creditos(CREDITOS_DE_PRUEBA)
            partida.director.gasolinera = True
            self.app.avisar("+" + str(CREDITOS_DE_PRUEBA) + " CREDITOS")
        elif fila == "SALTAR TRAMO":
            rotulo = partida.director.rotulo()
            if partida.director.saltar_tramo():
                self.app.avisar("SALTADO: " + rotulo)
            else:
                self.app.avisar("AHORA NO HAY TRAMO QUE SALTAR")
        elif fila == "VENCER JEFE":
            self._vencer_jefe()
        elif fila == "SECRETO":
            self._dar_secreto()

    def _traer_jefe(self, tipo):
        partida = self.partida
        if partida.jefe is not None:
            # Ya habia un jefe: se va sin dar premio, y sus esbirros con el
            for esbirro in [e for e in partida.enemigos if e.esbirro]:
                partida.quitar_enemigo(esbirro)
            partida.jefe = None
        partida.iniciar_jefe(tipo)
        self.app.avisar("JEFE: " + nombre_de("JEFE", tipo))

    def _vencer_jefe(self):
        # Como el ultimo golpe del dash (el cuadro de impacto, la muerte y lo que sigue)
        jefe = self.partida.jefe
        if jefe is None or jefe.muriendo():
            self.app.avisar("NO HAY JEFE: SALTA LOS TRAMOS")
            return
        jefe.vida = 1
        jefe.recibir_golpe(self.partida)

    def _dar_secreto(self):
        secretos = self.secretos()
        if not secretos:
            self.app.avisar("AQUI NO HAY SECRETOS")
            return
        id_, nombre, encontrado = secretos[self.recuerdo["secreto"] % len(secretos)]
        if encontrado:
            self.app.avisar(id_ + ": YA LO TIENES")
            return
        self.partida.modo.revelar_secreto(id_)      # (suena y lo cuenta la radio, como jugando)

    def _traer_anomalia(self, tipo):
        # Con un jefe no: la pelea corta las anomalias (las balas del jefe y los asteroides
        # se mezclarian)
        partida = self.partida
        if partida.jefe is not None:
            self.app.avisar("ANOMALIA: NO CON UN JEFE")
            return
        partida.director.terminar_anomalia()
        partida.director.empezar_anomalia(tipo)
        self.app.avisar("ANOMALIA: " + nombre_de("ANOMALIA", tipo))

    def _dar_powerup(self, powerup):
        partida = self.partida
        if not powerup.disponible(partida):
            # Ej: VIDA con las vidas llenas, o TURBO si ya lo tienes
            self.app.avisar(powerup.nombre + ": NO SE PUEDE AHORA")
            return
        centro_x, centro_y = partida.nave.centro()
        partida.recoger_powerup(powerup, centro_x, centro_y)
        self.app.avisar("POWER-UP: " + powerup.nombre)

    def _limpiar(self):
        # Los enemigos explotan y se van (despues llegan los escuadrones que siguen, como siempre)
        partida = self.partida
        for enemigo in list(partida.enemigos):
            centro_x, centro_y = enemigo.centro()
            partida.efectos.explosion(centro_x, centro_y, [(40, 40, 60), enemigo.color], 14, 3, 3)
            partida.quitar_enemigo(enemigo)
        partida.balas.clear()
        self.app.avisar("SIN ENEMIGOS")

    # ---------- Lo que se ve ----------

    def valor(self, fila):
        # Lo que se ve a la derecha de cada fila
        if fila in ELEGIBLES:
            return "< " + nombre_de(fila, self.elegido(fila)) + " >"
        if fila == "INVENCIBLE":
            return "SI" if self.partida.invencible else "NO"
        if fila == "LIMPIAR":
            cantidad = len(self.partida.enemigos)
            return str(cantidad) + (" ENEMIGO" if cantidad == 1 else " ENEMIGOS")
        if fila == "GASOLINERA":
            return "+" + str(CREDITOS_DE_PRUEBA) + " CREDITOS"
        if fila == "SALTAR TRAMO":
            return self.partida.director.rotulo()
        if fila == "SECRETO":
            secretos = self.secretos()
            if not secretos:
                return "NINGUNO"
            id_, _, encontrado = secretos[self.recuerdo["secreto"] % len(secretos)]
            return "< " + id_ + " >" + ("  YA" if encontrado else "")
        return ""

    def ayuda(self, fila):
        # El nombre del secreto no entra en la fila: va abajo
        if fila == "SECRETO" and self.secretos():
            _, nombre, encontrado = self.secretos()[self.recuerdo["secreto"] % len(self.secretos())]
            return nombre + (" (YA LO TIENES)" if encontrado else ": LO ENCUENTRA YA")
        return ""

    def advertencia(self):
        return "LA PARTIDA NO GUARDA RECORD NI LOGROS"
