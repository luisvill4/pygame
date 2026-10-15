"""
Carteles del juego: todo lo que aparece encima de la partida para contar algo.

Tres tamaños, cada uno en su lugar (asi nunca se pisan):
    pancarta(...)       los AVISOS, arriba al centro: "TRAMO 2/4", "¡ASEDIO SUPERADO!", una anomalia,
                        "¡NUEVO RECORD!". Salen de a uno, en una cola (avisos.py)
    ficha_*(...)        tarjetas chicas a los costados: enemigo nuevo (izquierda) y desafio
                        (derecha). Si el aviso de arriba es ancho, bajan para no tocarlo
    logro(...)          el logro desbloqueado: abajo al centro, se abre desde el trofeo
    radio(...)          el mensaje de radio del modo historia: abajo al centro, con retrato
    jefe_vencido(...)   los MOMENTOS: una franja de lado a lado, como la de la llegada del
    sector_nuevo(...)   jefe (el jefe llega y se va con el mismo lenguaje)
    rango(...)          el resultado del sector: un panel con las estrellas y la medalla

Todos se arman con las mismas piezas: fondo semitransparente, rayas que se apagan hacia
afuera, escuadras en las esquinas, una pestañita con la categoria (etiqueta) y, si es una
amenaza, cinta de peligro. Todos se abren y se cierran (apertura) y lo que aparece nace
blanco y despues toma su color.

Son solo dibujo: reciben cuanto hace que empezaron (con partida.tiempo, asi la pausa no
los gasta). El HUD los pasa por hud._cartel(), que los vuelve transparentes si tapan algo.
"""
import pygame

from juego import dibujo, recursos, accesibilidad
from juego.dibujo import MINI, CHICA, MEDIA, GRANDE, TITULO
from juego.interfaz import mezclar, esquinas, separador
from juego.historia.personajes import PERSONAJES, dibujar_retrato
from juego.config import (ANCHO, CENTRO_X, FONDO, PANEL_FONDO, CONTORNO, BLANCO, AMARILLO, GRIS, ROJO, CIAN, VERDE,
                          MAGENTA, TEXTO, TEXTO_SUAVE, LINEA_APAGADA, NAVES, CARTEL_JEFE, CARTEL_RANGO,
                          CARTEL_SECTOR, RANGO_SELLO)

FONDO_CINE = (4, 4, 12)     # el negro de las franjas de lado a lado
ROJO_OSCURO = (70, 0, 20)


def texto(pantalla, mensaje, tamano, color, x, y, alinear="centro"):
    # Todo lo que va encima del juego lleva un contorno oscuro: tiene que leerse sobre
    # cualquier cosa (nebulosas, planetas, explosiones). Lo usa tambien el HUD
    dibujo.texto(pantalla, mensaje, tamano, color, x, y, sombra=CONTORNO, alinear=alinear, contorno=CONTORNO)


def ancho_texto(mensaje, tamano):
    return recursos.fuente(tamano).size(mensaje)[0]


# ---------- Movimiento ----------

def suave(fraccion):
    # De 0 a 1, arrancando rapido y frenando al final: asi se mueve todo en la interfaz
    fraccion = max(0.0, min(1.0, fraccion))
    return 1 - (1 - fraccion) ** 3


def apertura(transcurrido, restante, entra, sale):
    # Cuanto esta abierto un cartel (de 0 a 1): se abre en 'entra' ms y se cierra en los
    # ultimos 'sale' ms. Vale 1 solo mientras esta abierto del todo
    return suave(min(transcurrido / entra, restante / sale))


# ---------- Piezas ----------

def fondo(pantalla, rect, color=PANEL_FONDO, alfa=230):
    # Un relleno semitransparente. En la capa de los carteles (que tiene transparencia por
    # pixel) alcanza con pintar el color con su alfa; en la pantalla se pega una capa
    if pantalla.get_flags() & pygame.SRCALPHA:
        pantalla.fill(tuple(color) + (alfa,), rect)
    else:
        capa = pygame.Surface(rect.size)
        capa.fill(color)
        capa.set_alpha(alfa)
        pantalla.blit(capa, rect.topleft)


SALIDA_RAYA = 16           # cuanto sigue la raya por afuera de la caja (dos escalones de 8)


def raya(pantalla, izquierda, derecha, y, color):
    # Una linea de 2 px que sigue un poco por afuera en dos escalones que se apagan
    pantalla.fill(color, (izquierda, y, derecha - izquierda, 2))
    for i, cuanto in enumerate((0.4, 0.75)):
        apagado = mezclar(color, FONDO, cuanto)
        pantalla.fill(apagado, (izquierda - (i + 1) * 8, y, 8, 2))
        pantalla.fill(apagado, (derecha + i * 8, y, 8, 2))


def etiqueta(pantalla, mensaje, x, centro_y, color, alinear="izquierda"):
    # Una pestañita de color con la categoria ("ALERTA", "NUEVO ENEMIGO"...), montada
    # sobre un borde. Devuelve su rectangulo
    ancho = (ancho_texto(mensaje, MINI) + 13) // 2 * 2
    if alinear == "derecha":
        x -= ancho
    caja = pygame.Rect(dibujo.en_grilla(x), dibujo.en_grilla(centro_y) - 8, ancho, 16)
    pantalla.fill(color, caja)
    dibujo.texto(pantalla, mensaje, MINI, FONDO, caja.centerx, caja.centery, sombra=None)
    return caja


def rayitas(pantalla, izquierda, centro_y, color, cantidad=3):
    # Rayitas inclinadas de decoracion (como las de los paneles), en escalones de 2 px
    arriba = dibujo.en_grilla(centro_y) - 6
    for i in range(cantidad):
        x = dibujo.en_grilla(izquierda) + i * 12
        tono = mezclar(color, FONDO, 0.25 + i * 0.2)
        for paso in range(6):
            pantalla.fill(tono, (x + (5 - paso) * 2, arriba + paso * 2, 6, 2))


def cinta(pantalla, rect, corrimiento, color=ROJO, oscuro=ROJO_OSCURO):
    # Cinta de peligro: rayas inclinadas que se desplazan 'corrimiento' px, en escalones
    # de 2 px (la grilla de los pixeles de arte)
    pantalla.fill(oscuro, rect)
    alto = rect.height
    periodo = 2 * alto
    recorte_antes = pantalla.get_clip()
    pantalla.set_clip(rect.clip(recorte_antes))
    for fila in range(0, alto, 2):
        inicio = dibujo.en_grilla((corrimiento + alto - fila) % periodo)
        for x in range(rect.left - periodo + inicio, rect.right, periodo):
            pantalla.fill(color, (x, rect.top + fila, alto, 2))
    pantalla.set_clip(recorte_antes)


def franja(pantalla, centro_y, alto, color, alfa=215):
    # Una franja de lado a lado: fondo de cine y una raya de color arriba y abajo. La usan
    # la llegada del jefe, el jefe vencido, el sector nuevo y READY. Devuelve su rectangulo
    alto = alto // 2 * 2
    if alto <= 0:
        return None
    ancho = pantalla.get_width()
    caja = pygame.Rect(0, dibujo.en_grilla(centro_y - alto // 2), ancho, alto)
    fondo(pantalla, caja, FONDO_CINE, alfa)
    pantalla.fill(color, (0, caja.top, ancho, 2))
    pantalla.fill(color, (0, caja.bottom - 2, ancho, 2))
    return caja


def deslizar(transcurrido, desde, distancia, ms=320):
    # Cuanto le falta a algo que entra deslizandose (de 'distancia' px a 0), en la grilla
    return dibujo.en_grilla((1 - suave((transcurrido - desde) / ms)) * distancia)


# ---------- Avisos (la franja de arriba) ----------

Y_PANCARTA = 112            # el borde de arriba de los avisos (debajo del marcador)
ANCHO_PANCARTA = (352, 640) # el mas angosto (entra entre las dos fichas) y el mas ancho
ENTRA_PANCARTA = 260        # ms que tarda en abrirse
SALE_PANCARTA = 200         # y en cerrarse


def medidas_pancarta(aviso):
    # (ancho, alto, tamaño del titulo). El titulo va GRANDE si entra y si no, MEDIA
    minimo, maximo = ANCHO_PANCARTA
    tamano = GRANDE if ancho_texto(aviso.titulo, GRANDE) <= maximo - 64 else MEDIA
    contenido = max(ancho_texto(aviso.titulo, tamano), ancho_texto(aviso.subtitulo, CHICA))
    ancho = min(maximo, max(minimo, contenido + 64)) // 4 * 4
    alto = 16 + tamano + 10 + CHICA + 16
    return ancho, alto, tamano


def caja_pancarta(aviso, transcurrido, restante):
    # El rectangulo que ocupa ahora: al abrirse crece hacia abajo. Las fichas lo usan
    # para correrse y no tocarlo
    ancho, alto, _ = medidas_pancarta(aviso)
    abierto = apertura(transcurrido, restante, ENTRA_PANCARTA, SALE_PANCARTA)
    alto_ahora = dibujo.en_grilla(alto * max(0.0, (abierto - 0.3) / 0.7))
    return pygame.Rect(dibujo.en_grilla(CENTRO_X - ancho // 2), Y_PANCARTA, ancho, alto_ahora)


def pancarta(pantalla, aviso, transcurrido, restante):
    # Primero una raya que se estira desde el centro, despues la caja que baja y al final
    # el contenido: el titulo cae y nace blanco, y el subtitulo se escribe solo
    ancho, alto, tamano = medidas_pancarta(aviso)
    color = aviso.color or dibujo.color_arcoiris()
    abierto = apertura(transcurrido, restante, ENTRA_PANCARTA, SALE_PANCARTA)
    caja = caja_pancarta(aviso, transcurrido, restante)
    if caja.height < 4:
        media_raya = dibujo.en_grilla(ancho / 2 * min(1.0, abierto * 2))
        pantalla.fill(color, (caja.centerx - media_raya, caja.top, 2 * media_raya, 2))
        return
    fondo(pantalla, caja)
    raya(pantalla, caja.left, caja.right, caja.top, color)
    raya(pantalla, caja.left, caja.right, caja.bottom - 2, mezclar(color, FONDO, 0.45))
    esquinas(pantalla, caja, color, largo=10, grueso=2)
    if aviso.alerta:
        cinta(pantalla, pygame.Rect(caja.left + 2, caja.bottom - 10, caja.width - 4, 8), int(transcurrido * 0.05))
    if abierto < 1:
        return
    desde = transcurrido - ENTRA_PANCARTA
    pestana = etiqueta(pantalla, aviso.etiqueta, caja.left + 16, caja.top, color)
    rayitas(pantalla, pestana.right + 6, caja.top, color)
    caida = deslizar(desde, 0, 8, 120)
    color_titulo = BLANCO if desde < 90 else color
    dibujo.texto_3d(pantalla, aviso.titulo, tamano, color_titulo, mezclar(color, FONDO, 0.65),
                    caja.top + 16 + tamano // 2 - caida, 4 if tamano == GRANDE else 3, CONTORNO, caja.centerx)
    # El subtitulo se escribe de a una letra (como una computadora de a bordo)
    letras = int((desde - 100) / 18)
    if letras > 0:
        izquierda = caja.centerx - ancho_texto(aviso.subtitulo, CHICA) // 2
        texto(pantalla, aviso.subtitulo[:letras], CHICA, TEXTO, izquierda, caja.bottom - 24, alinear="izquierda")


# ---------- Fichas (a los costados) ----------

Y_FICHAS = 112              # el borde de arriba de las fichas (a la altura de los avisos)
ALTO_FICHA = 64
DURACION_FICHA = 3500       # ms que se ve una ficha (enemigo nuevo, desafio) y el logro


def ficha(pantalla, transcurrido, lado, color, titulo, color_titulo, nombre, pista, imagen=None, pancarta=None):
    # Una tarjeta chica que entra deslizandose desde su lado: la categoria en una
    # pestañita, el dibujo (si tiene), el nombre y un consejo. 'pancarta' es lo que ocupa
    # el aviso de arriba: si la ficha lo tocaria, baja (de a poco, mientras se abre)
    margen = 72 if imagen is not None else 24
    ancho = (max(304, margen + max(ancho_texto(nombre, CHICA), ancho_texto(pista, MINI)) + 24) + 1) // 2 * 2
    entrada = suave(min(transcurrido / 260, (DURACION_FICHA - transcurrido) / 220))
    escondida = (1 - entrada) * (ancho + 40)
    if lado == "izquierda":
        final_x = 20
        x = final_x - escondida
    else:
        final_x = ANCHO - 20 - ancho
        x = final_x + escondida
    y = Y_FICHAS
    lejos = SALIDA_RAYA + 8         # (la raya del aviso sigue por afuera de su caja)
    if pancarta is not None and pancarta.left - lejos < final_x + ancho and pancarta.right + lejos > final_x:
        y += pancarta.height + min(12, pancarta.height)
    caja = pygame.Rect(dibujo.en_grilla(x), dibujo.en_grilla(y), ancho, ALTO_FICHA)
    fondo(pantalla, caja, alfa=235)
    pygame.draw.rect(pantalla, mezclar(color, FONDO, 0.55), caja, 2)
    acento_x = caja.left if lado == "izquierda" else caja.right - 4
    pantalla.fill(color, (acento_x, caja.top, 4, caja.height))       # la raya del lado de donde vino
    esquinas(pantalla, caja, color, largo=10, grueso=2)
    etiqueta(pantalla, titulo, caja.left + 16, caja.top, color_titulo)
    texto_x = caja.left + margen
    if imagen is not None:
        hueco = pygame.Rect(caja.left + 14, caja.top + 12, 44, 44)
        pantalla.fill(mezclar(color, FONDO, 0.85), hueco)
        pygame.draw.rect(pantalla, mezclar(color, FONDO, 0.5), hueco, 2)
        if imagen.get_width() > 40:
            imagen = pygame.transform.scale(imagen, (40, 40))
        dibujo.pegar(pantalla, imagen, hueco.centerx, hueco.centery, centrado=True)
    color_nombre = BLANCO if 260 <= transcurrido < 380 else color          # nace blanco
    texto(pantalla, nombre, CHICA, color_nombre, texto_x, caja.top + 28, alinear="izquierda")
    texto(pantalla, pista, MINI, TEXTO_SUAVE, texto_x, caja.top + 48, alinear="izquierda")


def ficha_nuevo_enemigo(pantalla, tipo, transcurrido, pancarta=None):
    ficha(pantalla, transcurrido, "izquierda", tipo.color, "NUEVO ENEMIGO", tipo.color, tipo.nombre, tipo.pista,
          tipo.cuadros()[0], pancarta)


def ficha_desafio(pantalla, desafio, transcurrido, pancarta=None):
    # La misma ficha cuenta el desafio al proponerse y despues como termino
    if desafio.estado == "cumplido":
        titulo, color_titulo, pista = "¡DESAFIO CUMPLIDO!", VERDE, "PREMIO: PUNTOS Y UN POWER-UP"
    elif desafio.estado == "fallado":
        titulo, color_titulo, pista = "DESAFIO FALLADO", ROJO, "SUERTE EN EL PROXIMO SECTOR"
    else:
        titulo, color_titulo, pista = "DESAFIO (OPCIONAL)", desafio.color, desafio.pista
    ficha(pantalla, transcurrido, "derecha", desafio.color, titulo, color_titulo, desafio.nombre, pista,
          pancarta=pancarta)


# ---------- Logro (abajo al centro) ----------

TROFEO = [
    "X.XXX.X",
    "XXXXXXX",
    "X.XXX.X",
    "..XXX..",
    "...X...",
    "..XXX..",
    ".XXXXX.",
]
Y_LOGRO = 464               # el borde de arriba del aviso de logro
ALTO_LOGRO = 56             # (la insignia del trofeo es un cuadrado de este lado)


def nave_del_logro(logro):
    # La nave que regala este logro, o None: (nombre, color)
    for nombre, color, id_logro in NAVES:
        if id_logro == logro.id:
            return nombre, color
    return None


def logro(pantalla, logro, transcurrido):
    # Primero aparece la insignia con el trofeo, despues se abre hacia los costados y al
    # final se escribe el logro. Si regala una nave, lo dice en una pestañita abajo
    restante = DURACION_FICHA - transcurrido
    insignia = apertura(transcurrido, restante, 160, 160)
    abre = suave(min((transcurrido - 160) / 320, (restante - 160) / 320))
    regalo = nave_del_logro(logro)
    contenido = max(ancho_texto(logro.nombre, CHICA), ancho_texto(logro.descripcion, MINI),
                    ancho_texto("LOGRO DESBLOQUEADO", MINI) + 40)
    if regalo is not None:
        contenido = max(contenido, ancho_texto("NAVE NUEVA: " + regalo[0], MINI) + 24)
    ancho_total = ALTO_LOGRO + 16 + contenido + 24
    ancho = dibujo.en_grilla(ALTO_LOGRO + (ancho_total - ALTO_LOGRO) * abre)
    caja = pygame.Rect(dibujo.en_grilla(CENTRO_X - ancho / 2), Y_LOGRO, ancho, ALTO_LOGRO)
    if abre > 0:
        fondo(pantalla, caja, alfa=235)
        pygame.draw.rect(pantalla, mezclar(AMARILLO, FONDO, 0.5), caja, 2)
        esquinas(pantalla, caja, AMARILLO, largo=10, grueso=2)
    # La insignia (se abre de arriba hacia abajo, desde su centro)
    alto_insignia = dibujo.en_grilla(ALTO_LOGRO * insignia)
    if alto_insignia >= 4:
        sello = pygame.Rect(caja.left, caja.centery - alto_insignia // 2, ALTO_LOGRO, alto_insignia)
        pantalla.fill(mezclar(AMARILLO, FONDO, 0.8), sello)
        pygame.draw.rect(pantalla, AMARILLO, sello, 2)
        if insignia >= 1:
            dibujo.pixel_art(pantalla, TROFEO, sello.centerx, sello.centery, AMARILLO, 4)
    if abre < 1:
        return
    desde = transcurrido - 480
    texto_x = caja.left + ALTO_LOGRO + 16
    pestana = etiqueta(pantalla, "LOGRO DESBLOQUEADO", texto_x, caja.top, AMARILLO)
    rayitas(pantalla, pestana.right + 6, caja.top, AMARILLO)
    texto(pantalla, logro.nombre, CHICA, BLANCO if desde < 120 else AMARILLO, texto_x, caja.top + 24,
          alinear="izquierda")
    texto(pantalla, logro.descripcion, MINI, TEXTO_SUAVE, texto_x, caja.top + 40, alinear="izquierda")
    if regalo is not None:
        etiqueta(pantalla, "NAVE NUEVA: " + regalo[0], caja.right - 16, caja.bottom, regalo[1], alinear="derecha")


# ---------- Momentos (franjas de lado a lado) ----------

CENTRO_MOMENTO = 300        # altura del centro de las franjas de los momentos
ALTO_MOMENTO = 120
ENTRA_MOMENTO = 260         # ms que tarda en abrirse (y en cerrarse)


def jefe_vencido(pantalla, jefe, bonus, transcurrido):
    # La franja del jefe vencido: su nombre arriba en su color, "¡JEFE VENCIDO!" entra
    # desde la izquierda y el premio desde la derecha (como la presentacion, al reves)
    color = jefe.color if jefe is not None else MAGENTA
    abierto = apertura(transcurrido, CARTEL_JEFE - transcurrido, ENTRA_MOMENTO, ENTRA_MOMENTO)
    caja = franja(pantalla, CENTRO_MOMENTO, round(ALTO_MOMENTO * abierto), color)
    if caja is None or abierto < 1:
        return
    desde = transcurrido - ENTRA_MOMENTO
    if jefe is not None:
        texto(pantalla, jefe.nombre, CHICA, color, CENTRO_X, caja.top + 18)
    x_titulo = CENTRO_X - deslizar(desde, 0, 700)
    color_titulo = BLANCO if desde < 120 else dibujo.color_arcoiris()
    dibujo.texto_3d(pantalla, "¡JEFE VENCIDO!", GRANDE, color_titulo, (30, 10, 40), caja.centery, 4, CONTORNO,
                    x_titulo)
    if bonus:
        texto(pantalla, "BONUS +" + str(bonus), CHICA, AMARILLO, CENTRO_X + deslizar(desde, 140, 700),
              caja.bottom - 18)


def sector_nuevo(pantalla, sector, numero, transcurrido):
    # La franja del sector nuevo: el numero entre dos rayas, el nombre se escribe de a una
    # letra (la computadora de a bordo lo va leyendo) y despues el lema
    color = sector["color"]
    abierto = apertura(transcurrido, CARTEL_SECTOR - transcurrido, ENTRA_MOMENTO, ENTRA_MOMENTO)
    caja = franja(pantalla, CENTRO_MOMENTO, round(ALTO_MOMENTO * abierto), color)
    if caja is None or abierto < 1:
        return
    desde = transcurrido - ENTRA_MOMENTO
    rotulo = "SECTOR " + str(numero)
    ancho_rotulo = ancho_texto(rotulo, CHICA)
    texto(pantalla, rotulo, CHICA, TEXTO_SUAVE, CENTRO_X, caja.top + 18)
    largo = dibujo.en_grilla(suave(desde / 300) * 120)
    if largo > 8:
        separador(pantalla, CENTRO_X - ancho_rotulo // 2 - 20 - largo, caja.top + 18, largo, color)
        separador(pantalla, CENTRO_X + ancho_rotulo // 2 + 20, caja.top + 18, largo, color)
    nombre = sector["nombre"]
    letras = int(desde / 35) + 1
    izquierda = CENTRO_X - ancho_texto(nombre, GRANDE) // 2
    dibujo.texto_3d(pantalla, nombre[:letras], GRANDE, color, mezclar(color, FONDO, 0.7), caja.centery, 4, CONTORNO,
                    izquierda, "izquierda")
    if letras < len(nombre):
        # El cursor de la computadora, al final de lo escrito
        cursor_x = izquierda + ancho_texto(nombre[:letras], GRANDE) + 4
        pantalla.fill(BLANCO, (dibujo.en_grilla(cursor_x), caja.centery - 16, 16, 32))
        return
    lema = sector["lema"]
    letras_lema = int((desde - len(nombre) * 35 - 120) / 25)
    if letras_lema > 0:
        izquierda_lema = CENTRO_X - ancho_texto(lema, CHICA) // 2
        texto(pantalla, lema[:letras_lema], CHICA, BLANCO, izquierda_lema, caja.bottom - 18, alinear="izquierda")


# ---------- El rango del sector ----------

COLOR_RANGO = {"S": None, "A": AMARILLO, "B": CIAN, "C": GRIS}   # None = arcoiris
RANGO = pygame.Rect(CENTRO_X - 288, 184, 576, 232)              # el panel (al centro)
MEDALLA = 104               # lado de la medalla con la letra

ESTRELLA = [
    "...X...",
    "..XXX..",
    "XXXXXXX",
    ".XXXXX.",
    "..XXX..",
    ".XX.XX.",
    "XX...XX",
]


def _estrella(pantalla, izquierda, centro_y, color):
    # Pixel art de 7x7 con pixeles de 2 (como las calaveras de la dificultad)
    dibujo.pixel_art(pantalla, ESTRELLA, izquierda + 7, centro_y, color, 2)


def rango(pantalla, rango, transcurrido):
    # El panel se abre desde su centro. Las filas salen de a una (cada estrella nace
    # blanca) y al final cae la letra en la medalla, como un sello
    from juego import interfaz          # (panel: el mismo de los menus)
    abierto = apertura(transcurrido, CARTEL_RANGO - transcurrido, ENTRA_MOMENTO, ENTRA_MOMENTO)
    alto = dibujo.en_grilla(RANGO.height * abierto)
    if alto < 4:
        return
    color = rango["color"]
    if abierto < 1:
        caja = pygame.Rect(RANGO.left, RANGO.centery - alto // 2, RANGO.width, alto)
        pantalla.fill(PANEL_FONDO, caja)
        pygame.draw.rect(pantalla, color, caja, 2)
        return
    adentro = interfaz.panel(pantalla, RANGO, color, "SECTOR " + str(rango["sector"]) + " COMPLETO")
    for i, (nombre, valor, estrellas, maximo) in enumerate(rango["filas"]):
        desde_fila = transcurrido - (300 + i * 400)
        if desde_fila < 0:
            break
        fila_y = adentro.top + 10 + i * 34
        nueva = desde_fila < 100
        texto(pantalla, nombre, CHICA, BLANCO if nueva else TEXTO_SUAVE, adentro.left + 4 - deslizar(desde_fila, 0, 16, 160),
              fila_y, alinear="izquierda")
        texto(pantalla, valor, CHICA, VERDE if estrellas else ROJO, adentro.left + 270, fila_y, alinear="derecha")
        for j in range(maximo):
            if j < estrellas:
                tono = BLANCO if desde_fila < 100 + j * 80 else AMARILLO
            else:
                tono = LINEA_APAGADA
            _estrella(pantalla, adentro.left + 290 + j * 22, fila_y, tono)
    # Abajo, el total (cuando ya salieron todas las filas)
    filas = len(rango["filas"])
    if transcurrido >= 300 + filas * 400:
        total_y = adentro.top + 10 + filas * 34
        separador(pantalla, adentro.left + 4, total_y - 6, 320)
        texto(pantalla, "ESTRELLAS", CHICA, TEXTO_SUAVE, adentro.left + 4, total_y + 14, alinear="izquierda")
        maximo = sum(fila[3] for fila in rango["filas"])
        texto(pantalla, str(rango["estrellas"]) + "/" + str(maximo), CHICA, AMARILLO, adentro.left + 270,
              total_y + 14, alinear="derecha")
    _medalla(pantalla, rango, transcurrido, adentro)


def _medalla(pantalla, rango, transcurrido, adentro):
    # A la derecha: "RANGO", la medalla (con "?" hasta que cae la letra) y el premio
    centro_x = adentro.right - 4 - MEDALLA // 2
    texto(pantalla, "RANGO", CHICA, TEXTO_SUAVE, centro_x, adentro.top + 8)
    medalla = pygame.Rect(centro_x - MEDALLA // 2, adentro.top + 24, MEDALLA, MEDALLA)
    if transcurrido < RANGO_SELLO:
        pantalla.fill(mezclar(GRIS, FONDO, 0.85), medalla)
        pygame.draw.rect(pantalla, LINEA_APAGADA, medalla, 2)
        if dibujo.parpadeo(300):
            texto(pantalla, "?", GRANDE, GRIS, medalla.centerx + 2, medalla.centery + 2)
        return
    letra = rango["letra"]
    color = COLOR_RANGO[letra] or dibujo.color_arcoiris()
    desde = transcurrido - RANGO_SELLO
    golpe = desde < 60 and not accesibilidad.destellos_reducidos()     # el destello del sello
    pantalla.fill(BLANCO if golpe else mezclar(color, FONDO, 0.78), medalla)
    pygame.draw.rect(pantalla, color, medalla, 2)
    esquinas(pantalla, medalla, color, largo=10, grueso=2)
    # Un anillo cuadrado que se abre desde la medalla
    if desde < 320:
        crece = dibujo.en_grilla(suave(desde / 320) * 40)
        pygame.draw.rect(pantalla, mezclar(color, FONDO, desde / 320), medalla.inflate(2 * crece, 2 * crece), 2)
    # Al caer, la letra es enorme y se achica de golpe (en dos etapas: estilo retro)
    tamano = TITULO * 2 if desde < 80 else TITULO
    texto(pantalla, letra, tamano, color, medalla.centerx + 4, medalla.centery + 4)
    if rango["puntos"] and desde > 300:
        texto(pantalla, "+" + str(rango["puntos"]) + " PUNTOS", CHICA, AMARILLO, centro_x, medalla.bottom + 18)


# ---------- La radio (modo historia) ----------

RADIO = pygame.Rect(CENTRO_X - 320, 418, 640, 100)     # abajo al centro, arriba de la barra del jefe
RETRATO_RADIO = 6                                       # lado de cada pixel del retrato (12 x 6 = 72 px)
ANCHO_TEXTO_RADIO = RADIO.width - 12 * RETRATO_RADIO - 52
MS_POR_LETRA_RADIO = 22                                 # el texto se escribe solo, como un teletipo
ENTRA_RADIO = 180


def lineas_radio(mensaje):
    # Los renglones de un mensaje en la caja (tiene lugar para 3)
    return dibujo.partir_lineas(mensaje, CHICA, ANCHO_TEXTO_RADIO)


def radio(pantalla, mensaje, transcurrido, restante):
    # La caja de la radio: retrato a la izquierda, el nombre en una pestañita de su color y el
    # texto que se escribe solo. Se abre y se cierra estirandose desde el centro
    nombre, color = PERSONAJES[mensaje.personaje]
    abierto = apertura(transcurrido, restante, ENTRA_RADIO, ENTRA_RADIO)
    ancho = dibujo.en_grilla(RADIO.width * abierto)
    if ancho < 16:
        return
    caja = pygame.Rect(dibujo.en_grilla(CENTRO_X - ancho // 2), RADIO.top, ancho, RADIO.height)
    fondo(pantalla, caja)
    esquinas(pantalla, caja, color)
    if abierto < 1:
        return
    dibujar_retrato(pantalla, mensaje.personaje, caja.left + 14, caja.top + 14, RETRATO_RADIO)
    texto_x = caja.left + 12 * RETRATO_RADIO + 32
    etiqueta(pantalla, nombre, texto_x, caja.top, color)
    letras = int((transcurrido - ENTRA_RADIO) / MS_POR_LETRA_RADIO)
    for i, renglon in enumerate(lineas_radio(mensaje.texto)):
        if letras <= 0:
            break
        texto(pantalla, renglon[:letras], CHICA, TEXTO, texto_x, caja.top + 34 + i * 24, alinear="izquierda")
        letras -= len(renglon) + 1
