"""
Entrada: teclado y mando de Xbox convertidos en "acciones".

El resto del juego nunca pregunta por teclas ni botones: pregunta por acciones
("¿se apreto ACEPTAR?", "¿se apreto DASH?"). Asi se puede cambiar una tecla, o
agregar otro control, tocando solo este archivo.

- Acciones de un toque: se juntan en la lista 'acciones' hasta que un paso de logica
  las usa (consumir()).
- Movimiento: direccion() lee las flechas mantenidas o, si no hay, el mando
  (cruceta en 8 direcciones, stick izquierdo en cualquier angulo).
"""
import math

import pygame

from juego.config import (BOTON_A, BOTON_B, BOTON_X, BOTON_VISTA, BOTON_MENU,
                          ZONA_MUERTA, ZONA_MUERTA_NAVE)

# Acciones
ACEPTAR = "aceptar"
VOLVER = "volver"
PAUSA = "pausa"
OPCIONES = "opciones"
DASH = "dash"
ARRIBA = "arriba"
ABAJO = "abajo"
IZQUIERDA = "izquierda"
DERECHA = "derecha"
SILENCIO = "silencio"           # M: apaga o prende todo el sonido (en cualquier pantalla)
PANTALLA_COMPLETA = "pantalla_completa"     # F11

# Que acciones dispara cada tecla
TECLAS = {
    pygame.K_RETURN: [ACEPTAR],
    pygame.K_KP_ENTER: [ACEPTAR],
    pygame.K_ESCAPE: [VOLVER, PAUSA],
    pygame.K_p: [PAUSA],
    pygame.K_o: [OPCIONES],
    pygame.K_SPACE: [DASH],
    pygame.K_UP: [ARRIBA],
    pygame.K_DOWN: [ABAJO],
    pygame.K_LEFT: [IZQUIERDA],
    pygame.K_RIGHT: [DERECHA],
    pygame.K_m: [SILENCIO],
    pygame.K_F11: [PANTALLA_COMPLETA],
}

# Que accion dispara cada boton del mando (B solo vuelve: en el juego no pausa)
BOTONES = {
    BOTON_A: ACEPTAR,
    BOTON_B: VOLVER,
    BOTON_X: DASH,
    BOTON_MENU: PAUSA,
    BOTON_VISTA: OPCIONES,
}


def direccion_stick(valor):
    # -1, 0 o 1 segun hacia donde este inclinado (ignora inclinaciones chicas)
    if valor < -ZONA_MUERTA:
        return -1
    if valor > ZONA_MUERTA:
        return 1
    return 0


class Entrada:
    def __init__(self, usar_mandos=True):
        self.usar_mandos = usar_mandos      # en los tests se apaga, para ignorar mandos reales
        self.mandos = {}                    # mandos conectados, por su numero de instancia
        self.stick_antes = [0, 0]           # direccion del stick en el frame anterior
        self.acciones = []                  # acciones de un toque de este frame, en orden
        self.cerrar = False                 # se cerro la ventana
        self.foco_perdido = False           # la ventana perdio el foco (Alt+Tab...)
        self.mando_desconectado = False     # se desconecto un mando que se estaba usando
        # Funcion que dice que teclas estan mantenidas (se puede reemplazar en los tests)
        self.teclas_mantenidas = pygame.key.get_pressed

    def procesar(self, eventos):
        # Lee los eventos y SUMA sus acciones a las pendientes. Se juntan hasta que un paso
        # de logica las usa y llama a consumir(): asi, dibujando a mas de 60 FPS (cuadros
        # sin paso de logica) o a menos (varios pasos por cuadro), no se pierde ninguna
        for evento in eventos:
            if evento.type == pygame.QUIT:
                self.cerrar = True
            elif evento.type == pygame.KEYDOWN:
                self.acciones.extend(TECLAS.get(evento.key, []))
            elif evento.type == pygame.WINDOWFOCUSLOST:
                self.foco_perdido = True
            else:
                self._evento_mando(evento)

    def _evento_mando(self, evento):
        if evento.type == pygame.JOYDEVICEADDED:
            # pygame avisa por cada mando, tambien los que ya estaban enchufados al abrir el juego
            if self.usar_mandos:
                mando = pygame.joystick.Joystick(evento.device_index)
                self.mandos[mando.get_instance_id()] = mando
        elif evento.type == pygame.JOYDEVICEREMOVED:
            if evento.instance_id in self.mandos:
                self.mando_desconectado = True
                del self.mandos[evento.instance_id]
        elif evento.type == pygame.JOYBUTTONDOWN:
            if evento.button in BOTONES:
                self.acciones.append(BOTONES[evento.button])
        elif evento.type == pygame.JOYHATMOTION:
            cruceta_x, cruceta_y = evento.value
            if cruceta_x == -1:
                self.acciones.append(IZQUIERDA)
            elif cruceta_x == 1:
                self.acciones.append(DERECHA)
            if cruceta_y == 1:
                self.acciones.append(ARRIBA)
            elif cruceta_y == -1:
                self.acciones.append(ABAJO)
        elif evento.type == pygame.JOYAXISMOTION and evento.axis in (0, 1):
            # El stick cuenta como un toque solo cuando recien se inclina
            direccion = direccion_stick(evento.value)
            if direccion != self.stick_antes[evento.axis]:
                if evento.axis == 0 and direccion == -1:
                    self.acciones.append(IZQUIERDA)
                elif evento.axis == 0 and direccion == 1:
                    self.acciones.append(DERECHA)
                elif evento.axis == 1 and direccion == -1:
                    self.acciones.append(ARRIBA)
                elif evento.axis == 1 and direccion == 1:
                    self.acciones.append(ABAJO)
            self.stick_antes[evento.axis] = direccion

    def consumir(self):
        # Un paso de logica ya uso las acciones pendientes: se borran
        self.acciones = []
        self.foco_perdido = False
        self.mando_desconectado = False

    def pulso(self, accion):
        # ¿Se apreto esta accion (desde el ultimo paso de logica)?
        return accion in self.acciones

    def direccion(self):
        # Hacia donde mover la nave: (dx, dy). Las flechas tienen prioridad sobre el mando
        teclas = self.teclas_mantenidas()
        dx = teclas[pygame.K_RIGHT] - teclas[pygame.K_LEFT]
        dy = teclas[pygame.K_DOWN] - teclas[pygame.K_UP]
        if dx != 0 or dy != 0:
            return dx, dy
        return self.direccion_mando()

    def direccion_mando(self):
        for mando in self.mandos.values():
            if mando.get_numhats() > 0:
                cruceta_x, cruceta_y = mando.get_hat(0)
                if cruceta_x != 0 or cruceta_y != 0:
                    return cruceta_x, -cruceta_y        # en la cruceta, arriba es +1
            if mando.get_numaxes() >= 2:
                stick_x = mando.get_axis(0)
                stick_y = mando.get_axis(1)
                # Se mide la inclinacion total (en circulo), asi ninguna direccion es mas sensible
                if math.hypot(stick_x, stick_y) > ZONA_MUERTA_NAVE:
                    return stick_x, stick_y
        return 0, 0

    def hay_mando(self):
        return len(self.mandos) > 0

    def ayuda(self, con_teclado, con_mando):
        # Texto de ayuda segun lo que se este usando
        if self.hay_mando():
            return con_mando
        return con_teclado

    def vibrar(self, suave, fuerte, ms):
        # Vibracion de todos los mandos: dos motores de 0 a 1 (suave = grave, fuerte = agudo)
        for mando in self.mandos.values():
            mando.rumble(suave, fuerte, ms)
