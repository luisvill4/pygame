"""
HUD: el marcador que se dibuja encima del juego.

- Arriba: puntos y combo (izquierda), record (centro), vidas (derecha).
- Abajo: power-ups activos (izquierda), barra del jefe (centro), dash y nivel (derecha).
- Carteles: "NIVEL X" y "¡JEFE VENCIDO!".

Lo de la izquierda se ancla al borde izquierdo, lo de la derecha al borde derecho y
lo del centro al centro, asi el HUD se acomoda solo al formato (4:3 o 16:9).

zonas_hud() son los rectangulos que ocupa el HUD: ahi no aparecen monedas.
Si el HUD cambia de lugar o crece, hay que actualizarlas.
"""
import random

import pygame

from juego import dibujo, nave, lienzo
from juego.dibujo import texto, CHICA, MEDIA, GRANDE
from juego.config import (ALTO, ROJO, BLANCO, AMARILLO, GRIS, CIAN, MAGENTA,
                          COMBO_TIEMPO, CARTEL_JEFE, OLEADA_DURACION)
from juego.powerups import TIPOS_POWERUP


def zonas_hud():
    return [
        pygame.Rect(0, 0, lienzo.ancho, 100),       # arriba: puntos, combo, record y vidas
        pygame.Rect(0, 530, lienzo.ancho, 70),      # abajo: dash, nivel y barra del jefe
        pygame.Rect(0, 430, 180, 170),              # abajo a la izquierda: power-ups activos
    ]


def posicion_libre(ancho, alto):
    # Esquina de arriba a la izquierda, al azar, de algo que no tape el HUD
    zonas = zonas_hud()
    while True:
        nueva_x = random.randint(0, lienzo.ancho - ancho)
        nueva_y = random.randint(0, ALTO - alto)
        if pygame.Rect(nueva_x, nueva_y, ancho, alto).collidelist(zonas) == -1:
            return nueva_x, nueva_y


def dibujar(pantalla, partida):
    _marcador(pantalla, partida)
    _activos(pantalla, partida)
    if partida.jefe is not None:
        _barra_jefe(pantalla, partida.jefe)
    director = partida.director
    if director.en_oleada:
        _barra_oleada(pantalla, director)
    # Carteles: nivel, sector nuevo, oleada y jefe vencido
    if partida.tiempo - partida.tiempo_cartel_nivel < 1500:
        dibujo.texto_3d(pantalla, "NIVEL " + str(partida.nivel), GRANDE, AMARILLO, MAGENTA, 250, 4)
    if partida.tiempo - director.tiempo_cartel_sector < 2500:
        sector = director.sector
        texto(pantalla, "SECTOR " + str(director.numero_sector), CHICA, GRIS, lienzo.centro_x(), 300)
        dibujo.texto_3d(pantalla, sector["nombre"], MEDIA, sector["color"], (30, 30, 50), 330, 3)
    if director.nuevo_tipo is not None and partida.tiempo - director.tiempo_cartel_nuevo < 3500:
        _cartel_nuevo_enemigo(pantalla, director.nuevo_tipo, partida.tiempo - director.tiempo_cartel_nuevo)
    if director.en_oleada and director.restante_oleada() > OLEADA_DURACION - 2000 and dibujo.parpadeo(150):
        dibujo.texto_3d(pantalla, "¡OLEADA!", GRANDE, ROJO, (110, 0, 30), 200, 4)
    if partida.tiempo - partida.tiempo_cartel_jefe < CARTEL_JEFE:
        dibujo.texto_3d(pantalla, "¡JEFE VENCIDO!", GRANDE, dibujo.color_arcoiris(), MAGENTA, 300, 4)


def _marcador(pantalla, partida):
    ahora = partida.tiempo

    # Puntaje (izquierda): se pone amarillo un instante al recoger una moneda
    texto(pantalla, "PUNTOS", CHICA, ROJO, 20, 22, alinear="izquierda")
    color = AMARILLO if ahora - partida.tiempo_moneda < 200 else BLANCO
    texto(pantalla, dibujo.numero_arcade(partida.puntaje), CHICA, color, 20, 46, alinear="izquierda")

    # Combo (debajo del puntaje) con una barra del tiempo que le queda
    if partida.combo >= 2:
        multiplicador = partida.multiplicador_combo()
        if multiplicador > 1:
            texto(pantalla, "COMBO x" + str(multiplicador), CHICA, dibujo.color_arcoiris(), 20, 72, alinear="izquierda")
        else:
            texto(pantalla, "COMBO " + str(partida.combo), CHICA, GRIS, 20, 72, alinear="izquierda")
        restante = max(0, 1 - (ahora - partida.ultima_moneda) / COMBO_TIEMPO)
        pantalla.fill(AMARILLO, (20, 86, int(128 * restante), 4))

    centro = lienzo.centro_x()
    derecha = lienzo.ancho - 20

    # Record (centro): se actualiza en vivo si lo estas superando
    texto(pantalla, "RECORD", CHICA, ROJO, centro, 22)
    if partida.puntaje > partida.puntaje_maximo:
        texto(pantalla, dibujo.numero_arcade(partida.puntaje), CHICA, AMARILLO, centro, 46)
    else:
        texto(pantalla, dibujo.numero_arcade(partida.puntaje_maximo), CHICA, BLANCO, centro, 46)

    # Nivel y dash (abajo a la derecha)
    texto(pantalla, "NIVEL " + str(partida.nivel), CHICA, AMARILLO, derecha, 575, alinear="derecha")
    if ahora >= partida.nave.dash_listo:
        texto(pantalla, "DASH", CHICA, CIAN, derecha, 545, alinear="derecha")
    else:
        texto(pantalla, "DASH", CHICA, GRIS, derecha, 545, alinear="derecha")
        # max(0, ...) por si RECARGA cambia a mitad de una recarga
        cargado = max(0, 1 - (partida.nave.dash_listo - ahora) / partida.recarga_dash())
        pantalla.fill(CIAN, (derecha - 64, 557, int(64 * cargado), 3))

    # Vidas (derecha): parpadean despues de recibir un golpe
    texto(pantalla, "VIDAS", CHICA, ROJO, derecha, 22, alinear="derecha")
    if ahora - partida.tiempo_golpe < 800 and dibujo.parpadeo(80):
        return
    for i in range(partida.vidas_max):
        icono_x = derecha - partida.vidas_max * 28 + 3 + i * 28
        icono = nave.imagen("icono") if i < partida.vidas else nave.imagen("icono_vacio")
        pantalla.blit(icono, (icono_x, 34))


def _activos(pantalla, partida):
    # Abajo a la izquierda: power-ups activos; los temporales con los segundos que les quedan
    fila_y = 575
    for powerup in TIPOS_POWERUP.values():
        if not partida.activo(powerup.tipo):
            continue
        if powerup.dura_hasta_perder_vida():
            mensaje = powerup.nombre
        else:
            segundos = int(partida.restante(powerup.tipo) // 1000) + 1
            mensaje = powerup.nombre + " " + str(segundos)
        texto(pantalla, mensaje, CHICA, powerup.color, 20, fila_y, alinear="izquierda")
        fila_y -= 26


def _cartel_nuevo_enemigo(pantalla, tipo, transcurrido):
    # "NUEVO ENEMIGO: DIVISOR" con su dibujo y un consejo (parpadea el primer segundo)
    centro = lienzo.centro_x()
    titulo = "NUEVO ENEMIGO: " + tipo.nombre
    if transcurrido > 1000 or dibujo.parpadeo(150):
        texto(pantalla, titulo, CHICA, tipo.color, centro + 16, 420)
        imagen = tipo.cuadros()[0]
        ancho_titulo = len(titulo) * CHICA
        pantalla.blit(imagen, imagen.get_rect(midright=(centro + 16 - ancho_titulo // 2 - 10, 420)))
    texto(pantalla, tipo.pista, CHICA, BLANCO, centro, 448)


def _barra_oleada(pantalla, director):
    # Abajo al centro: cuanto le queda a la oleada
    centro = lienzo.centro_x()
    color = ROJO if dibujo.parpadeo(300) else AMARILLO
    texto(pantalla, "OLEADA", CHICA, color, centro - 82, 575, alinear="derecha")
    restante = director.restante_oleada() / OLEADA_DURACION
    pygame.draw.rect(pantalla, GRIS, (centro - 70, 567, 200, 16), 2)
    pantalla.fill(color, (centro - 66, 571, int(192 * restante) // 4 * 4, 8))


def _barra_jefe(pantalla, jefe):
    # Abajo al centro: un bloque por cada golpe que le queda
    centro = lienzo.centro_x()
    texto(pantalla, "JEFE", CHICA, ROJO, centro - 82, 575, alinear="derecha")
    ancho_bloque = 200 // jefe.vida_max
    for i in range(jefe.vida_max):
        bloque = pygame.Rect(centro - 70 + i * ancho_bloque, 567, ancho_bloque - 4, 16)
        if i < jefe.vida:
            pantalla.fill(MAGENTA, bloque)
        else:
            pygame.draw.rect(pantalla, GRIS, bloque, 2)
