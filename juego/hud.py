"""
HUD: el marcador que se dibuja encima del juego.

- Arriba: puntos y combo (izquierda), record (centro), vidas (derecha).
- Abajo: power-ups activos (izquierda), barra del jefe, de la oleada o de la anomalia
  (centro), dash y nivel (derecha).
- Debajo de las vidas: el desafio del sector y como va.
- Carteles: "NIVEL X", "¡JEFE VENCIDO!", el rango del sector, la anomalia que llega...
- Fichas: tarjetas chicas que entran deslizandose (enemigo nuevo a la izquierda,
  desafio a la derecha), asi no tapan el centro de la pantalla.

Lo de la izquierda se ancla al borde izquierdo, lo de la derecha al borde derecho y
lo del centro al centro, asi el HUD se acomoda solo al formato (4:3 o 16:9).

zonas_hud() son los rectangulos que ocupa el HUD: ahi no aparecen monedas.
Si el HUD cambia de lugar o crece, hay que actualizarlas.
"""
import random

import pygame

from juego import dibujo, nave, lienzo, recursos
from juego.dibujo import texto, MINI, CHICA, MEDIA, GRANDE, TITULO
from juego.config import (ALTO, ROJO, BLANCO, AMARILLO, GRIS, CIAN, MAGENTA, VERDE,
                          CARTEL_JEFE, CARTEL_RANGO, RANGO_SELLO, OLEADA_DURACION, ANOMALIA_DURACION)
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
    director = partida.director
    if partida.jefe is not None:
        _barra_jefe(pantalla, partida.jefe)
    elif director.en_oleada:
        color = ROJO if dibujo.parpadeo(300) else AMARILLO
        _barra_tiempo(pantalla, "OLEADA", director.restante_oleada() / OLEADA_DURACION, color)
    elif director.anomalia is not None:
        anomalia = director.anomalia
        _barra_tiempo(pantalla, "ANOMALIA", anomalia.restante(partida) / ANOMALIA_DURACION, anomalia.color)
    if director.desafio is not None and partida.jefe is None:
        _desafio(pantalla, director.desafio)
    # Carteles: nivel, sector nuevo, oleada, anomalia, jefe vencido y rango
    if partida.tiempo - partida.tiempo_cartel_nivel < 1500:
        dibujo.texto_3d(pantalla, "NIVEL " + str(partida.nivel), GRANDE, AMARILLO, MAGENTA, 250, 4)
    if 0 <= partida.tiempo - director.tiempo_cartel_sector < 2500:
        sector = director.sector
        texto(pantalla, "SECTOR " + str(director.numero_sector), CHICA, GRIS, lienzo.centro_x(), 300)
        dibujo.texto_3d(pantalla, sector["nombre"], MEDIA, sector["color"], (30, 30, 50), 330, 3)
        if partida.tiempo - director.tiempo_cartel_sector > 600:
            texto(pantalla, sector["lema"], CHICA, BLANCO, lienzo.centro_x(), 370)
    if director.nuevo_tipo is not None and partida.tiempo - director.tiempo_cartel_nuevo < DURACION_FICHA:
        _ficha_nuevo_enemigo(pantalla, director.nuevo_tipo, partida.tiempo - director.tiempo_cartel_nuevo)
    if director.desafio is not None and partida.tiempo - director.tiempo_cartel_desafio < DURACION_FICHA:
        _ficha_desafio(pantalla, director.desafio, partida.tiempo - director.tiempo_cartel_desafio)
    if director.en_oleada and director.restante_oleada() > OLEADA_DURACION - 2000 and dibujo.parpadeo(150):
        dibujo.texto_3d(pantalla, "¡OLEADA!", GRANDE, ROJO, (110, 0, 30), 200, 4)
    if director.anomalia is not None:
        _cartel_anomalia(pantalla, director.anomalia, partida.tiempo - director.anomalia.desde)
    if partida.tiempo - partida.tiempo_cartel_jefe < CARTEL_JEFE:
        dibujo.texto_3d(pantalla, "¡JEFE VENCIDO!", GRANDE, dibujo.color_arcoiris(), MAGENTA, 300, 4)
    if director.rango is not None and 0 <= partida.tiempo - director.tiempo_cartel_rango < CARTEL_RANGO:
        _cartel_rango(pantalla, director.rango, partida.tiempo - director.tiempo_cartel_rango)


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
        restante = max(0, 1 - (ahora - partida.ultima_moneda) / partida.tiempo_combo())
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


# ---------- Fichas ----------

DURACION_FICHA = 3500       # ms que se ve una ficha (enemigo nuevo, desafio)


def _ficha(pantalla, transcurrido, lado, color, titulo, color_titulo, nombre, pista, imagen=None):
    # Una tarjeta chica debajo del marcador (asi no tapa el juego): entra deslizandose
    # desde su lado, muestra un titulo, un nombre y un consejo, y se va por donde vino.
    # Mide 288 de ancho, o mas si el nombre no entra
    margen = 64 if imagen is not None else 16
    ancho = max(288, margen + recursos.fuente(CHICA).size(nombre)[0] + 20)
    alto = 64
    entrada = max(0, min(1, transcurrido / 250, (DURACION_FICHA - transcurrido) / 250))
    escondida = (1 - entrada) * (ancho + 30)
    if lado == "izquierda":
        x = int(20 - escondida) // 4 * 4
    else:
        x = int(lienzo.ancho - 20 - ancho + escondida) // 4 * 4
    y = 104
    dibujo.marco(pantalla, pygame.Rect(x, y, ancho, alto), color)
    texto_x = x + margen
    if imagen is not None:
        if imagen.get_width() > 40:
            imagen = pygame.transform.scale(imagen, (40, 40))
        pantalla.blit(imagen, imagen.get_rect(center=(x + 34, y + alto // 2)))
    if transcurrido > 1000 or dibujo.parpadeo(150):
        texto(pantalla, titulo, MINI, color_titulo, texto_x, y + 16, alinear="izquierda")
    texto(pantalla, nombre, CHICA, color, texto_x, y + 32, alinear="izquierda")
    texto(pantalla, pista, MINI, BLANCO, texto_x, y + 50, alinear="izquierda")


def _ficha_nuevo_enemigo(pantalla, tipo, transcurrido):
    _ficha(pantalla, transcurrido, "izquierda", tipo.color, "NUEVO ENEMIGO", GRIS, tipo.nombre, tipo.pista,
           tipo.cuadros()[0])


def _ficha_desafio(pantalla, desafio, transcurrido):
    # La misma ficha cuenta el desafio al proponerse y despues como termino
    if desafio.estado == "cumplido":
        titulo, color_titulo, pista = "¡DESAFIO CUMPLIDO!", VERDE, "PREMIO: PUNTOS Y UN POWER-UP"
    elif desafio.estado == "fallado":
        titulo, color_titulo, pista = "DESAFIO FALLADO", ROJO, "SUERTE EN EL PROXIMO SECTOR"
    else:
        titulo, color_titulo, pista = "DESAFIO (OPCIONAL)", GRIS, desafio.pista
    _ficha(pantalla, transcurrido, "derecha", desafio.color, titulo, color_titulo, desafio.nombre, pista)


def _desafio(pantalla, desafio):
    # Debajo de las vidas: el desafio del sector y como va
    derecha = lienzo.ancho - 20
    if desafio.estado == "cumplido":
        estado, color = "CUMPLIDO", VERDE
    elif desafio.estado == "fallado":
        estado, color = "FALLADO", ROJO
    else:
        estado, color = desafio.texto_progreso(), BLANCO
    texto(pantalla, desafio.nombre, MINI, desafio.color if desafio.en_curso() else GRIS, derecha, 72,
          alinear="derecha")
    if estado:
        texto(pantalla, estado, MINI, color, derecha, 86, alinear="derecha")


# ---------- Carteles ----------

def _cartel_anomalia(pantalla, anomalia, transcurrido):
    # Al llegar: el nombre (parpadea el primer segundo) y el consejo, arriba del centro
    if transcurrido > 2800 or (transcurrido < 1000 and not dibujo.parpadeo(150)):
        return
    oscuro = tuple(componente // 3 for componente in anomalia.color)
    dibujo.texto_3d(pantalla, anomalia.nombre, MEDIA, anomalia.color, oscuro, 190, 3)
    texto(pantalla, anomalia.pista, CHICA, BLANCO, lienzo.centro_x(), 228)


COLOR_RANGO = {"S": None, "A": AMARILLO, "B": CIAN, "C": GRIS}   # None = arcoiris


def _cartel_rango(pantalla, rango, transcurrido):
    # Las filas van saliendo de a una y al final cae la letra, como un sello
    centro = lienzo.centro_x()
    marco = pygame.Rect(centro - 180, 160, 360, 290)
    dibujo.marco(pantalla, marco, rango["color"])
    texto(pantalla, "SECTOR " + str(rango["sector"]) + " COMPLETO", CHICA, rango["color"], centro, 196)
    for i, (nombre, valor, estrellas, maximo) in enumerate(rango["filas"]):
        if transcurrido < 300 + i * 400:
            break
        fila_y = 244 + i * 34
        texto(pantalla, nombre, CHICA, BLANCO, marco.left + 28, fila_y, alinear="izquierda")
        texto(pantalla, valor, CHICA, VERDE if estrellas else ROJO, marco.left + 262, fila_y, alinear="derecha")
        for j in range(maximo):
            _estrella(pantalla, marco.left + 290 + j * 22, fila_y, AMARILLO if j < estrellas else (60, 60, 80))
    texto(pantalla, "RANGO", CHICA, GRIS, centro - 40, 406, alinear="derecha")
    if transcurrido < RANGO_SELLO:
        if dibujo.parpadeo(150):
            texto(pantalla, "?", GRANDE, GRIS, centro + 30, 404)
        return
    letra = rango["letra"]
    color = COLOR_RANGO[letra] or dibujo.color_arcoiris()
    # Al caer, la letra es enorme y se achica de golpe (en dos etapas: estilo retro)
    tamano = TITULO * 2 if transcurrido < RANGO_SELLO + 80 else TITULO
    texto(pantalla, letra, tamano, color, centro + 30, 400)
    if rango["puntos"] and transcurrido > RANGO_SELLO + 300:
        texto(pantalla, "+" + str(rango["puntos"]), CHICA, AMARILLO, centro + 110, 406)


ESTRELLA = [
    "...X...",
    "..XXX..",
    "XXXXXXX",
    ".XXXXX.",
    "..XXX..",
    ".XX.XX.",
    "XX...XX",
]


def _estrella(pantalla, centro_x, centro_y, color, tamano_pixel=2):
    # Pixel art de 7x7 (como las calaveras de la dificultad)
    izquierda, arriba = centro_x - 7, centro_y - 7
    for fila, linea in enumerate(ESTRELLA):
        for columna, celda in enumerate(linea):
            if celda == "X":
                pantalla.fill(color, (izquierda + columna * tamano_pixel, arriba + fila * tamano_pixel,
                                      tamano_pixel, tamano_pixel))


def _barra_tiempo(pantalla, nombre, restante, color):
    # Abajo al centro: cuanto le queda a la oleada o a la anomalia (restante de 0 a 1)
    centro = lienzo.centro_x()
    texto(pantalla, nombre, CHICA, color, centro - 82, 575, alinear="derecha")
    pygame.draw.rect(pantalla, GRIS, (centro - 70, 567, 200, 16), 2)
    pantalla.fill(color, (centro - 66, 571, int(192 * restante) // 4 * 4, 8))


def _barra_jefe(pantalla, jefe):
    # Abajo al centro: un bloque por cada golpe que le queda
    centro = lienzo.centro_x()
    texto(pantalla, "JEFE", CHICA, ROJO, centro - 82, 575, alinear="derecha")
    vida, vida_max = jefe.vida_barra()
    ancho_bloque = 200 // vida_max
    for i in range(vida_max):
        bloque = pygame.Rect(centro - 70 + i * ancho_bloque, 567, ancho_bloque - 4, 16)
        if i < vida:
            pantalla.fill(MAGENTA, bloque)
        else:
            pygame.draw.rect(pantalla, GRIS, bloque, 2)
