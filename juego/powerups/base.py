"""
Clase base de los power-ups, su registro y la capsula que cae.

Hay tres clases de power-up, segun su 'duracion':
- temporal:           duracion = milisegundos (escudo, hielo, iman, doble)
- hasta perder vida:  duracion = HASTA_PERDER_VIDA (turbo, recarga)
- instantaneo:        duracion = None (vida: hace su efecto al recogerlo y listo)

Para agregar un power-up nuevo:
    1. En powerups/tipos.py, una clase que herede de PowerUp con @registrar_powerup.
    2. Darle tipo, letra, color, nombre, descripcion, paleta y duracion.
    3. Si hace algo al recogerlo, sobrescribir al_recoger() (llamando a super()).
    4. Si cambia algo mientras esta activo, preguntar en la partida con
       partida.activo("mi_tipo") donde haga falta (ej: partida.vel_max()).
    5. (Opcional) peso(partida): las chances de que caiga segun lo que pasa en el juego.
    (Opcional) Un cuadro de 30x30 al final de sprites/powerups.png y su 'cuadro_sprite'.
       Si no tiene, se dibuja un cuadro con su letra.
El HUD, la aparicion al azar y el panel de la pantalla de inicio lo toman solos.

Power-ups "inteligentes": la capsula no cae del todo al azar. Cada power-up dice con
peso() que tan util es AHORA (la vida si te queda una, el hielo si hay muchos enemigos,
el escudo contra un jefe...) y se elige con esas chances.
"""
import pygame

from juego import recursos, dibujo
from juego.config import FONDO, ORO, VELOCIDAD_POWERUP

TAMANO = 30
HASTA_PERDER_VIDA = "hasta perder una vida"

TIPOS_POWERUP = {}          # tipo -> instancia, en el orden en que se registran
_capsulas = {}              # tipo -> imagen de su capsula (ver PowerUp.imagen_capsula)


def registrar_powerup(clase):
    # Decorador: crea el power-up y lo anota en el registro
    powerup = clase()
    if not powerup.tipo:
        raise ValueError(clase.__name__ + " necesita un 'tipo'")
    TIPOS_POWERUP[powerup.tipo] = powerup
    return clase


class PowerUp:
    tipo = None             # nombre unico
    letra = "?"             # letra de la capsula (si no hay sprite)
    color = (255, 255, 255)
    nombre = ""             # como se ve en el HUD y al recogerlo
    descripcion = ""        # se explica en la pantalla de inicio
    paleta = ORO            # colores del anillo al recogerlo
    cuadro_sprite = None    # posicion en sprites/powerups.png (None = cuadro con la letra)
    duracion = None         # milisegundos, HASTA_PERDER_VIDA o None (instantaneo)

    def dura_hasta_perder_vida(self):
        return self.duracion == HASTA_PERDER_VIDA

    def disponible(self, partida):
        # ¿Puede caer ahora? Los que duran hasta perder una vida, solo si no estan activos
        if self.dura_hasta_perder_vida():
            return not partida.activo(self.tipo)
        return True

    def peso(self, partida):
        # Chances de caer (1 = normal). Las subclases lo suben cuando el power-up sirve mas
        return 1

    def al_recoger(self, partida, x, y):
        # Lo activa (si dura) y hace el anillo de particulas
        if self.duracion is not None:
            partida.activar(self.tipo, partida.duracion_powerup(self.duracion))
        partida.efectos.anillo(x, y, self.paleta, 24, 5)

    def texto_al_recoger(self):
        return self.nombre

    def dibujar_capsula(self, pantalla, centro_x, centro_y):
        imagen = self.imagen_capsula()
        dibujo.pegar(pantalla, imagen, centro_x, centro_y, centrado=True)

    def imagen_capsula(self):
        # Sprite de la capsula; si no hay, cuadro con borde de color y la letra adentro.
        # (Tambien es el icono del power-up en el HUD)
        if self.tipo not in _capsulas:
            cuadros = recursos.hoja("powerups.png", TAMANO)
            if cuadros and self.cuadro_sprite is not None and self.cuadro_sprite < len(cuadros):
                _capsulas[self.tipo] = cuadros[self.cuadro_sprite]
            else:
                imagen = pygame.Surface((TAMANO, TAMANO), pygame.SRCALPHA)
                imagen.fill(FONDO)
                pygame.draw.rect(imagen, self.color, imagen.get_rect(), 3)
                dibujo.texto(imagen, self.letra, dibujo.CHICA, self.color, TAMANO // 2 + 1, TAMANO // 2 + 1,
                             sombra=None)
                _capsulas[self.tipo] = imagen
        return _capsulas[self.tipo]


class Capsula:
    # Un power-up cayendo desde arriba de la pantalla, en linea recta

    def __init__(self, powerup, x):
        self.powerup = powerup
        self.x = x
        self.y = -15            # empieza justo arriba de la pantalla, asi entra cayendo

    def caer(self):
        self.y += VELOCIDAD_POWERUP

    def salio(self):
        return self.y > 615

    def caja(self):
        return pygame.Rect(self.x - TAMANO // 2, self.y - TAMANO // 2, TAMANO, TAMANO)

    def dibujar(self, pantalla):
        dibujo.halo(pantalla, self.x, self.y, 30, self.powerup.color)
        self.powerup.dibujar_capsula(pantalla, self.x, self.y)
