"""
HUD: el marcador que se dibuja encima del juego.

- Arriba: puntos, creditos y combo (izquierda), record (centro), vidas (derecha).
- Abajo: power-ups activos (izquierda), barra del jefe, de la oleada o de la anomalia
  (centro), dash, nivel y la barra de energia para subir de nivel (derecha).
- Debajo de las vidas: el desafio del sector y como va.
- Carteles (los dibuja carteles.py): el aviso de arriba ("NIVEL 7", "¡OLEADA!"...), las
  fichas de los costados, el logro de abajo y los momentos (jefe vencido, rango, sector).
- Carteles y fichas se dibujan primero en una capa aparte (_cartel). Si debajo hay algo
  que importa (la nave, la moneda, un enemigo, una bala...), la capa se pega casi
  transparente: el mensaje se sigue leyendo, pero no tapa el juego.
- La llegada del jefe: una cinematica que ocupa todo (_presentacion_jefe).

Lo de la izquierda se ancla al borde izquierdo (x=20), lo de la derecha al borde
derecho (ANCHO - 20) y lo del centro a CENTRO_X.

zonas_hud() son los rectangulos que ocupa el HUD: ahi no aparecen monedas.
Si el HUD cambia de lugar o crece, hay que actualizarlas.
"""
import math
import random

import pygame

from juego import impactos, dibujo, nave, recursos, accesibilidad, carteles
from juego.carteles import texto, cinta, franja, DURACION_FICHA, FONDO_CINE, ROJO_OSCURO
from juego.dibujo import MINI, CHICA, GRANDE
from juego.config import (ANCHO, CENTRO_X, ALTO, ROJO, BLANCO, AMARILLO, GRIS, CIAN, MAGENTA, VERDE, NARANJA,
                          CARTEL_JEFE, CARTEL_RANGO, CARTEL_SECTOR, OLEADA_DURACION, ANOMALIA_DURACION,
                          CARTEL_ALFA_TAPANDO, CARTEL_ALFA_MOMENTO, CARTEL_MARGEN, CARTEL_ESPERA_TAPANDO, CONTORNO,
                          COMBO_MAXIMO)
from juego.powerups import TIPOS_POWERUP


def zonas_hud():
    return [
        pygame.Rect(0, 0, ANCHO, 100),       # arriba: puntos, combo, record y vidas
        pygame.Rect(0, 524, ANCHO, 76),      # abajo: dash, nivel, energia y barra del jefe
        pygame.Rect(0, 430, 180, 170),              # abajo a la izquierda: power-ups activos
    ]


def posicion_libre(ancho, alto):
    # Esquina de arriba a la izquierda, al azar, de algo que no tape el HUD
    zonas = zonas_hud()
    while True:
        nueva_x = random.randint(0, ANCHO - ancho)
        nueva_y = random.randint(0, ALTO - alto)
        if pygame.Rect(nueva_x, nueva_y, ancho, alto).collidelist(zonas) == -1:
            return nueva_x, nueva_y


def dibujar(pantalla, partida):
    # Mientras el jefe se presenta, la cinematica ocupa todo: el resto del HUD se esconde
    jefe = partida.jefe
    if jefe is not None and (jefe.fin_entrada is None or partida.tiempo - jefe.fin_entrada < MS_FRANJAS):
        _presentacion_jefe(pantalla, jefe, partida.tiempo, partida.director.numero_sector)
        return
    _marcador(pantalla, partida)
    _activos(pantalla, partida)
    director = partida.director
    if partida.jefe is not None:
        _barra_jefe(pantalla, partida.jefe, partida.tiempo)
    elif director.en_oleada:
        color = ROJO if dibujo.parpadeo(300) else AMARILLO
        _barra_tiempo(pantalla, "OLEADA", director.restante_oleada() / OLEADA_DURACION, color)
    elif director.anomalia is not None:
        anomalia = director.anomalia
        _barra_tiempo(pantalla, anomalia.nombre, anomalia.restante(partida) / ANOMALIA_DURACION, anomalia.color)
    if director.desafio is not None and partida.jefe is None:
        _desafio(pantalla, director.desafio)
    # Carteles (ver carteles.py). Cada uno pasa por _cartel(), que lo vuelve transparente si tapa algo
    t = partida.tiempo
    pancarta = None
    aviso = partida.avisos.actual
    if aviso is not None and t < aviso.hasta:
        # El aviso de arriba (uno por vez, ver avisos.py); las fichas se corren si lo tocan
        pancarta = carteles.caja_pancarta(aviso, t - aviso.desde, aviso.hasta - t)
        _cartel(pantalla, partida, "aviso", carteles.pancarta, aviso, t - aviso.desde, aviso.hasta - t)
    if director.nuevo_tipo is not None and t - director.tiempo_cartel_nuevo < DURACION_FICHA:
        _cartel(pantalla, partida, "enemigo nuevo", carteles.ficha_nuevo_enemigo, director.nuevo_tipo,
                t - director.tiempo_cartel_nuevo, pancarta)
    if director.desafio is not None and t - director.tiempo_cartel_desafio < DURACION_FICHA:
        _cartel(pantalla, partida, "desafio", carteles.ficha_desafio, director.desafio,
                t - director.tiempo_cartel_desafio, pancarta)
    for logro, desde in partida.fichas_logro:
        if 0 <= t - desde < DURACION_FICHA:
            _cartel(pantalla, partida, "logro", carteles.logro, logro, t - desde)
    # Los momentos (despues del jefe no hay peligro): si tapan algo, se apagan menos
    if t - partida.tiempo_cartel_jefe < CARTEL_JEFE:
        _cartel(pantalla, partida, "jefe vencido", carteles.jefe_vencido, partida.ultimo_jefe, partida.bonus_jefe,
                t - partida.tiempo_cartel_jefe, alfa_tapando=CARTEL_ALFA_MOMENTO)
    if director.rango is not None and 0 <= t - director.tiempo_cartel_rango < CARTEL_RANGO:
        _cartel(pantalla, partida, "rango", carteles.rango, director.rango, t - director.tiempo_cartel_rango,
                alfa_tapando=CARTEL_ALFA_MOMENTO)
    if 0 <= t - director.tiempo_cartel_sector < CARTEL_SECTOR:
        _cartel(pantalla, partida, "sector", carteles.sector_nuevo, director.sector, director.numero_sector,
                t - director.tiempo_cartel_sector, alfa_tapando=CARTEL_ALFA_MOMENTO)


# ---------- Carteles que no tapan el juego ----------

_capas = {}             # tamaño de la pantalla -> [superficie transparente, zona usada la ultima vez]
_tapando_hasta = {}     # nombre del cartel -> hasta cuando (reloj real) sigue transparente


def _cartel(pantalla, partida, nombre, dibujar_cartel, *datos, alfa_tapando=CARTEL_ALFA_TAPANDO):
    # Dibuja el cartel en una capa transparente, mira que rectangulo ocupo y, si ahi
    # abajo hay algo que importa, lo pega casi transparente ('alfa_tapando').
    # dibujar_cartel(capa, *datos) es cualquier funcion que dibuja (la capa mide lo
    # mismo que la pantalla, asi los carteles centrados quedan en el mismo lugar)
    tamano = pantalla.get_size()
    if tamano not in _capas:
        _capas[tamano] = [pygame.Surface(tamano, pygame.SRCALPHA), pygame.Rect(0, 0, 0, 0)]
    capa, usada = _capas[tamano]
    capa.fill((0, 0, 0, 0), usada)              # el resto de la capa ya esta vacio
    dibujar_cartel(capa, *datos)
    ocupado = _zona_dibujada(capa)
    _capas[tamano][1] = ocupado
    if ocupado.width == 0:
        return                                  # (parpadeando: en este cuadro no dibujo nada)
    ahora = pygame.time.get_ticks()             # reloj real: es solo un efecto visual
    zona = ocupado.inflate(2 * CARTEL_MARGEN, 2 * CARTEL_MARGEN)
    if zona.collidelist(cosas_que_importan(partida)) != -1:
        _tapando_hasta[nombre] = ahora + CARTEL_ESPERA_TAPANDO
    if ahora < _tapando_hasta.get(nombre, 0):
        capa.set_alpha(alfa_tapando)
    else:
        capa.set_alpha(255)     # opaco (ojo: set_alpha(None) le sacaria la transparencia de cada pixel)
    pantalla.blit(capa, ocupado.topleft, ocupado)


def _zona_dibujada(capa):
    # El rectangulo de la capa que tiene algo dibujado (o uno vacio).
    # capa.get_bounding_rect() revisa pixel por pixel y tarda ~2 ms: demasiado a 144 FPS.
    # Achicar la capa 8 veces con smoothscale es 4 veces mas rapido, y como promedia los
    # pixeles, cualquier cosa dibujada deja algo de color en la chica. La zona queda unos
    # pixeles mas grande que el cartel: no importa
    ancho, alto = capa.get_size()
    chica = pygame.transform.smoothscale(capa, (ancho // 8, alto // 8))
    zona = chica.get_bounding_rect()
    if zona.width == 0:
        return zona
    escala_x, escala_y = ancho / chica.get_width(), alto / chica.get_height()
    grande = pygame.Rect(int(zona.x * escala_x), int(zona.y * escala_y),
                         int(zona.width * escala_x) + 1, int(zona.height * escala_y) + 1)
    return grande.inflate(4, 4).clip(capa.get_rect())


def cosas_que_importan(partida):
    # Los rectangulos de lo que el jugador tiene que ver siempre
    rectangulos = [partida.nave.caja_recoger(), partida.moneda.caja()]
    if partida.capsula is not None:
        rectangulos.append(partida.capsula.caja())
    rectangulos += [enemigo.caja() for enemigo in partida.enemigos]
    rectangulos += [pygame.Rect(bala.x - bala.radio, bala.y - bala.radio, 2 * bala.radio, 2 * bala.radio)
                    for bala in partida.balas]
    if partida.jefe is not None:
        rectangulos += partida.jefe.cajas_danio()
    return rectangulos


def _marcador(pantalla, partida):
    ahora = partida.tiempo

    # Puntaje (izquierda): cuenta de a poco hasta el real (puntaje_visible) y se pone
    # amarillo un instante al recoger una moneda
    texto(pantalla, "PUNTOS", CHICA, ROJO, 20, 22, alinear="izquierda")
    color = AMARILLO if ahora - partida.tiempo_moneda < 200 else BLANCO
    texto(pantalla, dibujo.numero_arcade(partida.puntaje_visible), CHICA, color, 20, 46, alinear="izquierda")

    # Creditos (al lado del puntaje): la plata de la gasolinera. Destellan al ganarlos
    texto(pantalla, "CREDITOS", MINI, GRIS, 136, 22, alinear="izquierda")
    icono_credito(pantalla, 144, 46)
    color = BLANCO if ahora - partida.tiempo_creditos < 200 else AMARILLO
    texto(pantalla, str(partida.creditos), CHICA, color, 160, 46, alinear="izquierda")

    _combo(pantalla, partida)

    centro = CENTRO_X
    derecha = ANCHO - 20

    # Record (centro): se actualiza en vivo si lo estas superando
    texto(pantalla, "RECORD", CHICA, ROJO, centro, 22)
    if partida.puntaje > partida.puntaje_maximo:
        texto(pantalla, dibujo.numero_arcade(partida.puntaje), CHICA, AMARILLO, centro, 46)
    else:
        texto(pantalla, dibujo.numero_arcade(partida.puntaje_maximo), CHICA, BLANCO, centro, 46)
    # Modo desarrollador: se avisa siempre, abajo de todo al centro, debajo de la barra del
    # jefe (esta partida no guarda record ni logros)
    if partida.modo_desarrollador:
        aviso = "MODO DEV" + ("  INVENCIBLE" if partida.invencible else "")
        texto(pantalla, aviso, MINI, MAGENTA, centro, 592)

    # Dash, nivel y la barra de energia (abajo a la derecha, de arriba hacia abajo)
    color = BLANCO if ahora - partida.tiempo_nivel < 200 else AMARILLO      # destella al subir
    texto(pantalla, "NIVEL " + str(partida.nivel), CHICA, color, derecha, 563, alinear="derecha")
    _barra_energia(pantalla, partida)
    # Dashes extra (mejora DOBLE DASH): cuadraditos a la izquierda, llenos si se pueden usar
    nave_jugador = partida.nave
    for i in range(nave_jugador.dash_extra_max):
        disponible = ahora >= nave_jugador.dash_listo or i < nave_jugador.dash_extra
        cuadrito = pygame.Rect(derecha - 84 - i * 12, 530, 8, 12)
        if disponible:
            pantalla.fill(CIAN, cuadrito)
        else:
            pygame.draw.rect(pantalla, GRIS, cuadrito, 2)
    if ahora >= partida.nave.dash_listo:
        texto(pantalla, "DASH", CHICA, CIAN, derecha, 536, alinear="derecha")
    else:
        texto(pantalla, "DASH", CHICA, GRIS, derecha, 536, alinear="derecha")
        cargado = 1 - (partida.nave.dash_listo - ahora) / partida.recarga_dash()
        dibujo.barra(pantalla, pygame.Rect(derecha - 64, 547, 64, 4), cargado, CIAN, borde=None)

    # Vidas (derecha): la que se acaba de perder destella en blanco antes de vaciarse, y la
    # ultima que queda late en rojo con el corazon (impactos.latiendo)
    texto(pantalla, "VIDAS", CHICA, ROJO, derecha, 22, alinear="derecha")
    recien_perdida = ahora - partida.tiempo_golpe < 800
    for i in range(partida.vidas_max):
        icono_x = derecha - partida.vidas_max * 28 + 3 + i * 28
        if i < partida.vidas:
            icono = _icono_rojo() if impactos.latiendo(partida) else nave.imagen("icono")
        elif i == partida.vidas and recien_perdida:
            icono = _icono_blanco() if dibujo.parpadeo(80) else nave.imagen("icono_vacio")
        else:
            icono = nave.imagen("icono_vacio")
        pantalla.blit(icono, (icono_x, 34))


_iconos_vida = {}       # (color de la nave, "blanco"/"rojo") -> el icono de vida en ese color


def _icono_vida(cual):
    # Variantes del icono de vida (se generan solas: recursos.blanquear y tenir). Se guardan
    # por el icono de la nave elegida (cambiar_color lo cambia)
    original = nave.imagen("icono")
    clave = (id(original), cual)
    if clave not in _iconos_vida:
        _iconos_vida[clave] = recursos.blanquear(original) if cual == "blanco" else recursos.tenir(original, ROJO)
    return _iconos_vida[clave]


def _icono_blanco():
    return _icono_vida("blanco")


def _icono_rojo():
    return _icono_vida("rojo")


COLOR_MULTIPLICADOR = {1: AMARILLO, 2: CIAN, 3: VERDE, 4: AMARILLO}    # x5, el maximo, va en arcoiris


def _combo(pantalla, partida):
    # Debajo del puntaje: el combo y una barra con el tiempo que falta para que se corte.
    # Cada multiplicador tiene su color (x5 en arcoiris) y destella blanco al subir
    if partida.combo < 2:
        return
    multiplicador = partida.multiplicador_combo()
    if partida.tiempo - partida.tiempo_multiplicador < 150:
        color = BLANCO
    elif multiplicador >= COMBO_MAXIMO:
        color = dibujo.color_arcoiris()
    else:
        color = COLOR_MULTIPLICADOR[multiplicador]
    if multiplicador > 1:
        texto(pantalla, "COMBO x" + str(multiplicador), CHICA, color, 20, 72, alinear="izquierda")
    else:
        texto(pantalla, "COMBO " + str(partida.combo), CHICA, GRIS, 20, 72, alinear="izquierda")
    restante = 1 - (partida.tiempo - partida.ultima_moneda) / partida.tiempo_combo()
    dibujo.barra(pantalla, pygame.Rect(20, 84, 128, 6), restante, color, borde=None)


def icono_credito(pantalla, centro_x, centro_y):
    # Una moneda quieta (el primer cuadro de moneda_giro.png, o un circulo si falta):
    # el simbolo de los creditos en el HUD y en la gasolinera
    cuadros = recursos.hoja("moneda_giro.png", 20)
    if cuadros:
        pantalla.blit(cuadros[0], cuadros[0].get_rect(center=(centro_x, centro_y)))
    else:
        pygame.draw.circle(pantalla, AMARILLO, (centro_x, centro_y), 8)


def _barra_energia(pantalla, partida):
    # Debajo de "NIVEL": cuanto falta para subir, en bloques de 4 px (estilo retro).
    # Destella en blanco al ganar energia y parpadea casi llena. Con el jefe queda vacia
    derecha = ANCHO - 20
    marco = pygame.Rect(derecha - 128, 576, 128, 12)
    if not partida.puede_ganar_energia():
        dibujo.barra(pantalla, marco, 0, GRIS)
        return
    lleno = partida.energia / partida.energia_necesaria()
    if partida.tiempo - partida.tiempo_energia < 120:
        color = BLANCO
    elif lleno > 0.8 and dibujo.parpadeo(150):
        color = NARANJA
    else:
        color = AMARILLO
    dibujo.barra(pantalla, marco, lleno, color)


ALTO_ACTIVO = 34        # px entre un power-up activo y el de arriba
_iconos_apagados = {}   # tipo -> icono en gris (ver _carga_escudo)


def _activos(pantalla, partida):
    # Abajo a la izquierda, de abajo hacia arriba: un renglon por power-up activo con su
    # capsula, el nombre y una barra con el tiempo que le queda. Los que duran hasta perder
    # una vida no tienen barra (el escudo de ESCUDO ROCE tampoco: dura hasta el golpe)
    fila_y = 572
    if partida.perfectos_para_regenerar() and not partida.activo("escudo"):
        _carga_escudo(pantalla, partida, fila_y)
        fila_y -= ALTO_ACTIVO
    for powerup in TIPOS_POWERUP.values():
        if not partida.activo(powerup.tipo):
            continue
        restante = partida.restante(powerup.tipo)
        temporal = not powerup.dura_hasta_perder_vida() and restante != math.inf
        # Cuando le queda poco, la capsula parpadea
        if not temporal or restante > 1500 or dibujo.parpadeo(150):
            powerup.dibujar_capsula(pantalla, 35, fila_y)
        if temporal:
            texto(pantalla, powerup.nombre, CHICA, powerup.color, 58, fila_y - 5, alinear="izquierda")
            total = partida.duracion_powerup(powerup.duracion)
            dibujo.barra(pantalla, pygame.Rect(58, fila_y + 7, 80, 4), restante / total, powerup.color, borde=None)
        else:
            texto(pantalla, powerup.nombre, CHICA, powerup.color, 58, fila_y, alinear="izquierda")
        fila_y -= ALTO_ACTIVO


def _carga_escudo(pantalla, partida, fila_y):
    # ESCUDO ROCE sin escudo: la capsula apagada y cuantos perfectos faltan para el proximo
    # escudo, en cuadraditos (llenos = hechos)
    if "escudo" not in _iconos_apagados:
        _iconos_apagados["escudo"] = recursos.tenir(TIPOS_POWERUP["escudo"].imagen_capsula(), GRIS)
    icono = _iconos_apagados["escudo"]
    pantalla.blit(icono, icono.get_rect(center=(35, fila_y)))
    texto(pantalla, "ESCUDO", CHICA, GRIS, 58, fila_y - 5, alinear="izquierda")
    for i in range(partida.perfectos_para_regenerar()):
        cuadrito = pygame.Rect(58 + i * 10, fila_y + 5, 6, 8)
        if i < partida.perfectos_para_escudo:
            pantalla.fill(CIAN, cuadrito)
        else:
            pygame.draw.rect(pantalla, GRIS, cuadrito, 2)


def _desafio(pantalla, desafio):
    # Debajo de las vidas, en un renglon: el desafio del sector y como va
    derecha = ANCHO - 20
    if desafio.estado == "cumplido":
        estado, color = "CUMPLIDO", VERDE
    elif desafio.estado == "fallado":
        estado, color = "FALLADO", ROJO
    else:
        estado, color = desafio.texto_progreso(), BLANCO
    nombre_x = derecha
    if estado:
        texto(pantalla, estado, CHICA, color, derecha, 76, alinear="derecha")
        nombre_x -= recursos.fuente(CHICA).size(estado)[0] + 16
    texto(pantalla, desafio.nombre, CHICA, desafio.color if desafio.en_curso() else GRIS, nombre_x, 76,
          alinear="derecha")


BARRA_CENTRAL = pygame.Rect(CENTRO_X - 160, 564, 320, 16)      # jefe, oleada o anomalia (abajo al centro)


def _barra_tiempo(pantalla, nombre, restante, color):
    # Abajo al centro: el nombre (de la oleada o de la anomalia) y cuanto le queda (de 0 a 1)
    texto(pantalla, nombre, CHICA, color, BARRA_CENTRAL.left, BARRA_CENTRAL.top - 14, alinear="izquierda")
    dibujo.barra(pantalla, BARRA_CENTRAL, restante, color)


MS_POR_SEGMENTO = 45        # al terminar la presentacion, la barra se llena de a un segmento


def _barra_jefe(pantalla, jefe, tiempo):
    # Abajo al centro: el nombre del jefe en su color y un segmento por cada golpe que le
    # queda. Cuando termina de entrar y se van las franjas de cine, se llena de a un
    # segmento (como en los arcades). El segmento que acaba de perder destella blanco
    if jefe.fin_entrada is None:
        return
    texto(pantalla, jefe.nombre, CHICA, jefe.color, BARRA_CENTRAL.left, BARRA_CENTRAL.top - 14, alinear="izquierda")
    vida, vida_max = jefe.vida_barra()
    llenos = min(vida, max(0, int((tiempo - jefe.fin_entrada - MS_FRANJAS) // MS_POR_SEGMENTO)))
    recien = vida if tiempo - jefe.ultimo_golpe < 400 else None
    dibujo.barra_segmentos(pantalla, BARRA_CENTRAL, llenos, vida_max, jefe.color, recien)


# ---------- La llegada del jefe ----------

ALTO_CINE = 64              # alto de las franjas negras de arriba y abajo
MS_FRANJAS = 350            # lo que tardan en entrar (y en irse)
MS_ALERTA = 1400            # cuanto dura "¡ALERTA!" antes de presentar al jefe
_sirena = {}                # la luz roja de los costados (se arma una vez)


def _presentacion_jefe(pantalla, jefe, tiempo, numero_sector):
    # La cinematica de llegada. Tapa el HUD con franjas de cine (con cinta de peligro),
    # prende luces de sirena a los costados, avisa "¡ALERTA!" y despues pasa una franja
    # con el nombre y el apodo. Cuando el jefe termina de entrar, todo se retira
    transcurrido = tiempo - jefe.creado_en
    if jefe.fin_entrada is None:
        abierto = min(1, transcurrido / MS_FRANJAS)
    else:
        abierto = 1 - (tiempo - jefe.fin_entrada) / MS_FRANJAS
        if abierto <= 0:
            return
    abierto = 1 - (1 - abierto) ** 2            # entra rapido y frena al final
    _luces_de_sirena(pantalla, transcurrido, abierto)
    _franjas_de_cine(pantalla, round(ALTO_CINE * abierto), transcurrido)
    centro_y = min(jefe.y_presentacion, 470)
    if transcurrido < MS_ALERTA:
        _alerta(pantalla, transcurrido, centro_y)
    else:
        _tarjeta_del_jefe(pantalla, jefe, transcurrido - MS_ALERTA, centro_y, abierto, numero_sector)


def _franjas_de_cine(pantalla, alto, transcurrido):
    # Negras arriba y abajo, con una cinta de peligro roja y negra en el borde de adentro
    if alto <= 0:
        return
    ancho, alto_pantalla = pantalla.get_size()
    pantalla.fill(FONDO_CINE, (0, 0, ancho, alto))
    pantalla.fill(FONDO_CINE, (0, alto_pantalla - alto, ancho, alto))
    corrimiento = int(transcurrido * 0.06)
    cinta(pantalla, pygame.Rect(0, alto - 12, ancho, 12), corrimiento)
    cinta(pantalla, pygame.Rect(0, alto_pantalla - alto, ancho, 12), -corrimiento)


def _luces_de_sirena(pantalla, transcurrido, abierto):
    # Un resplandor rojo en los dos costados que late (fijo con DESTELLOS REDUCIDOS)
    ancho, alto = pantalla.get_size()
    if alto not in _sirena:
        luz = pygame.Surface((48, alto), pygame.SRCALPHA)
        for i, alfa in enumerate((110, 70, 40, 18)):
            luz.fill((255, 30, 50, alfa), (i * 12, 0, 12, alto))
        _sirena[alto] = (luz, pygame.transform.flip(luz, True, False))
    izquierda, derecha = _sirena[alto]
    if accesibilidad.destellos_reducidos():
        latido = 0.5
    else:
        latido = (math.sin(transcurrido / 160) + 1) / 2
    izquierda.set_alpha(round(255 * latido * abierto))
    derecha.set_alpha(round(255 * latido * abierto))
    pantalla.blit(izquierda, (0, 0))
    pantalla.blit(derecha, (ancho - 48, 0))


def _alerta(pantalla, transcurrido, centro_y):
    # "¡ALERTA!" entre dos rayas que se abren desde el centro
    largo = round(min(1, transcurrido / 400) * 220) // 4 * 4
    for y in (centro_y - 44, centro_y + 52):
        pantalla.fill(ROJO, (CENTRO_X - largo, y, 2 * largo, 2))
    if transcurrido > 900 or dibujo.parpadeo(220):
        dibujo.texto_3d(pantalla, "¡ALERTA!", GRANDE, ROJO, ROJO_OSCURO, centro_y - 10, 4, CONTORNO)
    if transcurrido > 300:
        texto(pantalla, "SE ACERCA UN JEFE", CHICA, BLANCO, CENTRO_X, centro_y + 30)


def _tarjeta_del_jefe(pantalla, jefe, transcurrido, centro_y, abierto, numero_sector):
    # Una franja de lado a lado con el nombre (entra desde la izquierda) y el apodo (desde
    # la derecha), en el color del jefe
    caja = franja(pantalla, centro_y, round(104 * abierto), jefe.color)
    if caja is None or abierto < 1:
        return
    entra_nombre = 1 - (1 - min(1, transcurrido / 320)) ** 3
    entra_apodo = 1 - (1 - min(1, max(0, transcurrido - 140) / 320)) ** 3
    x_nombre = round(CENTRO_X - (1 - entra_nombre) * 700) // 4 * 4
    x_apodo = round(CENTRO_X + (1 - entra_apodo) * 700) // 4 * 4
    texto(pantalla, "JEFE DEL SECTOR " + str(numero_sector), MINI, jefe.color, CENTRO_X, caja.top + 14)
    dibujo.texto_3d(pantalla, jefe.nombre, GRANDE, jefe.color, (30, 10, 40), centro_y - 4, 4, CONTORNO, x_nombre)
    texto(pantalla, jefe.apodo, CHICA, BLANCO, x_apodo, caja.bottom - 18)
