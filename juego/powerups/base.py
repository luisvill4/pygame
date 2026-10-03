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
    (Opcional) Un cuadro de 30x30 al final de sprites/powerups.png y su 'cuadro_sprite'.
       Si no tiene, se dibuja un cuadro con su letra.
El HUD, la aparicion al azar y el panel de la pantalla de inicio lo toman solos.
"""
import pygame

from juego import recursos, dibujo
from juego.config import FONDO, ORO, VELOCIDAD_POWERUP

TAMANO = 30
HASTA_PERDER_VIDA = "hasta perder una vida"

TIPOS_POWERUP = {}          # tipo -> instancia, en el orden en que se registran


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

    def al_recoger(self, partida, x, y):
        # Lo activa (si dura) y hace el anillo de particulas
        if self.duracion is not None:
            partida.activar(self.tipo, self.duracion)
        partida.efectos.anillo(x, y, self.paleta, 24, 5)

    def texto_al_recoger(self):
        return self.nombre

    def dibujar_capsula(self, pantalla, centro_x, centro_y):
        # Sprite de la capsula; si no hay, cuadro con borde de color y la letra adentro
        cuadros = recursos.hoja("powerups.png", TAMANO)
        if cuadros and self.cuadro_sprite is not None and self.cuadro_sprite < len(cuadros):
            imagen = cuadros[self.cuadro_sprite]
            pantalla.blit(imagen, imagen.get_rect(center=(centro_x, centro_y)))
            return
        rect = pygame.Rect(0, 0, TAMANO, TAMANO)
        rect.center = (centro_x, centro_y)
        pygame.draw.rect(pantalla, FONDO, rect)
        pygame.draw.rect(pantalla, self.color, rect, 3)
        dibujo.texto(pantalla, self.letra, dibujo.CHICA, self.color, centro_x + 1, centro_y + 1, sombra=None)


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
        self.powerup.dibujar_capsula(pantalla, self.x, self.y)
