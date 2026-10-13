"""
Modo desarrollador: un panel para probar jefes, enemigos y power-ups sin tener que
llegar jugando. Se abre con F1 en plena partida (si MODO_DESARROLLADOR esta prendido
en config.py) y, como la pausa, el tiempo de la partida no corre mientras esta abierto.

    JEFE         < EL OJO >        trae ese jefe ahora (si ya hay uno, lo cambia)
    ENEMIGO      < PERSEGUIDOR >   trae un enemigo de ese tipo (aparece con su "X")
    POWER-UP     < ESCUDO >        te lo da enseguida, como si agarraras la capsula
    ANOMALIA     < NIEBLA CERRADA > la trae ahora (si ya habia una, la cambia; con un jefe, no)
    INVENCIBLE   NO                nada te hace daño
    LIMPIAR                        saca a todos los enemigos y las balas
    GASOLINERA   +200 CREDITOS     abre la tienda (con 200 creditos de regalo para probar)
    VOLVER

ARRIBA/ABAJO elige la fila, IZQ/DER cambia el valor y ENTER lo hace y vuelve al juego.
F1 o ESC vuelven sin hacer nada.

Apenas se usa algo, la partida queda marcada (partida.modo_desarrollador): ya no guarda
record ni logros, y el HUD muestra "MODO DEV".

Las listas salen de los registros (TIPOS_JEFE, TIPOS_ENEMIGO, TIPOS_POWERUP, TIPOS_ANOMALIA):
un jefe, enemigo, power-up o anomalia nuevo aparece aca solo, sin tocar este archivo.
"""
import pygame

from juego import dibujo, interfaz
from juego.dibujo import texto, CHICA, MEDIA, GRANDE
from juego.config import MAGENTA, AMARILLO, BLANCO, ROJO, FILA_ELEGIDA
from juego.entrada import VOLVER, DESARROLLADOR, ACEPTAR, ARRIBA, ABAJO, IZQUIERDA, DERECHA
from juego.escenas.base import Escena
from juego.jefes import TIPOS_JEFE
from juego.enemigos import TIPOS_ENEMIGO
from juego.powerups import TIPOS_POWERUP
from juego.anomalias import TIPOS_ANOMALIA

FILAS = ["JEFE", "ENEMIGO", "POWER-UP", "ANOMALIA", "INVENCIBLE", "LIMPIAR", "GASOLINERA", "VOLVER"]
FILA_Y = 188            # y de la primera fila
ALTO_FILA = 33          # (con 8 filas, mas que esto se sale del marco)
CREDITOS_DE_PRUEBA = 200

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


class Desarrollador(Escena):
    def __init__(self, app, escena_juego, captura):
        super().__init__(app)
        self.escena_juego = escena_juego    # a donde se vuelve
        self.partida = escena_juego.partida
        self.captura = captura              # imagen del juego al abrir el panel
        self.fondo = interfaz.pixelado(captura, oscuridad=180)
        self.fila = 0

    def elegido(self, fila):
        # El tipo elegido ahora en esa fila (ej: "ojo")
        return ELEGIBLES[fila][_elegido[fila]]

    # ---------- Logica ----------

    def actualizar(self, entrada):
        if entrada.pulso(DESARROLLADOR) or entrada.pulso(VOLVER):
            self._volver_al_juego()
            return
        for accion in entrada.acciones:
            if accion == ARRIBA:
                self.fila = (self.fila - 1) % len(FILAS)
            elif accion == ABAJO:
                self.fila = (self.fila + 1) % len(FILAS)
            elif accion in (IZQUIERDA, DERECHA):
                self._cambiar_valor(1 if accion == DERECHA else -1)
            elif accion == ACEPTAR:
                # Primero se vuelve (asi el sonido de lo que pasa ya no esta en pausa)
                self._volver_al_juego()
                self.hacer(FILAS[self.fila])
                return

    def _cambiar_valor(self, direccion):
        fila = FILAS[self.fila]
        if fila in ELEGIBLES:
            _elegido[fila] = (_elegido[fila] + direccion) % len(ELEGIBLES[fila])

    def _volver_al_juego(self):
        self.app.sonidos.reanudar_todo()
        self.app.cambiar_escena(self.escena_juego, transicion=False)

    def hacer(self, fila):
        # Lo que hace cada fila al apretar ENTER
        if fila == "VOLVER":
            return
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

    def _traer_jefe(self, tipo):
        partida = self.partida
        if partida.jefe is not None:
            # Ya habia un jefe: se va sin dar premio, y sus esbirros con el
            for esbirro in [e for e in partida.enemigos if e.esbirro]:
                partida.quitar_enemigo(esbirro)
            partida.jefe = None
        partida.iniciar_jefe(tipo)
        self.app.avisar("JEFE: " + nombre_de("JEFE", tipo))

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
        # Los enemigos explotan y se van (el director manda refuerzos al rato, como siempre)
        partida = self.partida
        for enemigo in list(partida.enemigos):
            centro_x, centro_y = enemigo.centro()
            partida.efectos.explosion(centro_x, centro_y, [(40, 40, 60), enemigo.color], 14, 3, 3)
            partida.quitar_enemigo(enemigo)
        partida.balas.clear()
        self.app.avisar("SIN ENEMIGOS")

    # ---------- Dibujo ----------

    def dibujar(self, pantalla_completa):
        pantalla_completa.blit(self.fondo, (0, 0))
        pantalla = dibujo.zona_central(pantalla_completa)
        dibujo.texto_3d(pantalla, "DESARROLLADOR", GRANDE, MAGENTA, (90, 0, 60), 100)

        interfaz.panel(pantalla, pygame.Rect(80, 160, 640, 290), MAGENTA)
        for i, fila in enumerate(FILAS):
            fila_y = FILA_Y + i * ALTO_FILA
            elegida = i == self.fila
            if elegida:
                pantalla.fill(FILA_ELEGIDA, (96, fila_y - ALTO_FILA // 2 + 2, 608, ALTO_FILA - 4))
                pantalla.fill(AMARILLO, (96, fila_y - ALTO_FILA // 2 + 2, 4, ALTO_FILA - 4))
            texto(pantalla, fila, MEDIA, AMARILLO if elegida else BLANCO, 120, fila_y, alinear="izquierda")
            texto(pantalla, self._valor(fila), CHICA, AMARILLO if elegida else BLANCO, 700, fila_y, alinear="derecha")

        texto(pantalla, AYUDA_FILA[FILAS[self.fila]], CHICA, BLANCO, 400, 480)
        texto(pantalla, "LA PARTIDA NO GUARDA RECORD NI LOGROS", CHICA, ROJO, 400, 510)
        interfaz.ayudas(pantalla_completa, self.app.entrada, [("elegir", "ELEGIR"), ("cambiar", "CAMBIAR"),
                                                              ("aceptar", "HACER"), ("desarrollador", "VOLVER")])

    def _valor(self, fila):
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
        return ""
