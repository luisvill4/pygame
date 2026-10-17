"""
ARCHIVO: lo que Alba e Ines saben del camino (como las terminales de Fallout).

Cinco pestañas (LB/RB o Q/E):
    REGISTROS     los fragmentos de la historia (los secretos de cada mision). Los que faltan
                  salen como "???" con su mision (dice cuantos hay, no donde estan); los
                  'ocultos' y los de una mision oculta ni aparecen hasta encontrarlos (pero
                  la cuenta de arriba los suma: hay mas de lo que se ve)
    ECOS          las historias de los sistemas libres de la galaxia (historia/ecos.py)
    CRIATURAS     las fichas de los enemigos y los guardianes      (historia/fichas.py: se
    TECNOLOGIA    la Alondra y los power-ups                        anotan solas la primera
    FENOMENOS     la Marea, el compas, las monedas y las anomalias  vez que las ves)
A la izquierda la lista (se desplaza si no entra); a la derecha el elegido: su dibujo (las
fichas), su texto y, si tiene, el glifo de El Ultimo. Con la clave del compas
(glifos.CLAVE_DE_LOS_GLIFOS) los glifos se traducen. Todo sale de los registros: una mision,
un fragmento o una ficha nuevos aparecen solos.
"""
import pygame

from juego import dibujo, interfaz, nave, moneda
from juego.dibujo import texto, CHICA, GRANDE
from juego.config import (ANCHO, FONDO, VIOLETA, TEXTO, TEXTO_SUAVE, TEXTO_APAGADO, RESALTADO, FILA_ELEGIDA, AMARILLO,
                          LINEA_APAGADA)
from juego.entrada import VOLVER, ACEPTAR, ARRIBA, ABAJO, PESTANA_ANTERIOR, PESTANA_SIGUIENTE
from juego.escenas.base import Escena
from juego.enemigos import TIPOS_ENEMIGO
from juego.jefes import TIPOS_JEFE
from juego.powerups import TIPOS_POWERUP
from juego.historia.mision import todos_los_fragmentos
from juego.historia.glifos import CLAVE_DE_LOS_GLIFOS, traducir, dibujar_glifo
from juego.historia import fichas, galaxia
from juego.historia.ecos import ECOS as LOS_ECOS

REGISTROS, ECOS = "REGISTROS", "ECOS"
PESTANAS = [REGISTROS, ECOS] + fichas.SECCIONES
BARRA_PESTANAS = pygame.Rect(48, 96, ANCHO - 96, 28)
LISTA = pygame.Rect(48, 140, 430, 400)
DETALLE = pygame.Rect(502, 140, ANCHO - 550, 400)
COLUMNA_NOMBRE = 84         # donde empieza el nombre en cada renglon de la lista
ALTO_FILA = 34
FILAS = 10                  # cuantas entran en la lista (las demas, desplazando)
LADO_DIBUJO = 104           # el recuadro del dibujo de una ficha
FLECHA_ABAJO = ["XXXXX", ".XXX.", "..X.."]     # "hay mas" (la lista se desplaza)
FLECHA_ARRIBA = FLECHA_ABAJO[::-1]


class Entrada:
    # Un renglon del Archivo, sea un fragmento o una ficha (asi la lista y el detalle no
    # preguntan cual es): la etiqueta de la izquierda, si ya se encontro y lo que muestra
    def __init__(self, id_, nombre, texto_, glifo, etiqueta, donde, encontrada, imagen=None):
        self.id, self.nombre, self.texto, self.glifo = id_, nombre, texto_, glifo
        self.etiqueta = etiqueta        # "M1" (la mision) o "" (las fichas)
        self.donde = donde              # que se dice cuando falta ("ESTA EN LA MISION 2.")
        self.encontrada = encontrada
        self.imagen = imagen


class Archivo(Escena):
    musica = None
    ambiente = None

    def __init__(self, app, volver_a):
        super().__init__(app)
        self.volver_a = volver_a
        self.pestana = 0
        self.elegido = 0
        self.primera = 0            # la primera fila que se ve (la lista se desplaza)
        self.cursor = interfaz.Cursor(0)

    # ---------- Lo que se muestra ----------

    def entradas(self):
        if PESTANAS[self.pestana] == REGISTROS:
            return self._registros()
        if PESTANAS[self.pestana] == ECOS:
            return self._ecos()
        return self._fichas(PESTANAS[self.pestana])

    def _ecos(self):
        # Dice en que sistema esta (con el reloj corriendo, saber a donde ir importa)
        donde = {uno.eco: uno.nombre for uno in galaxia.SISTEMAS if uno.eco}
        encontrados = self.app.progreso.fragmentos
        return [Entrada(eco.id, eco.nombre, eco.texto, eco.glifo, "",
                        "ESTA EN EL SISTEMA %s. DESPEJALO." % donde[eco.id], eco.id in encontrados)
                for eco in LOS_ECOS]

    def _registros(self):
        # Los ocultos y los de una mision que todavia no aparecio en el mapa no se muestran
        # hasta encontrarlos (si no, la lista contaria el secreto)
        progreso = self.app.progreso
        encontrados = progreso.fragmentos
        return [Entrada(fragmento.id, fragmento.nombre, fragmento.texto, fragmento.glifo, "M%d" % mision.numero,
                        "ESTA EN LA MISION %d." % mision.numero, fragmento.id in encontrados)
                for fragmento, mision in todos_los_fragmentos()
                if (not fragmento.oculto and mision.visible(progreso)) or fragmento.id in encontrados]

    def _fichas(self, seccion):
        vistas = self.app.progreso.fichas
        return [Entrada(ficha.id, ficha.nombre, ficha.texto, ficha.glifo, "", "TODAVIA NO LO VISTE EN UNA MISION.",
                        ficha.id in vistas, lambda ficha=ficha: imagen_de(ficha))
                for ficha in fichas.de_la_seccion(seccion)]

    # ---------- Cada paso ----------

    def actualizar(self, entrada):
        self.mover_fondo()
        self.cursor.avanzar()
        cuantas = len(self.entradas())
        if entrada.pulso(PESTANA_ANTERIOR) or entrada.pulso(PESTANA_SIGUIENTE):
            paso = 1 if entrada.pulso(PESTANA_SIGUIENTE) else -1
            self.pestana = (self.pestana + paso) % len(PESTANAS)
            self.elegido = self.primera = 0
            self.cursor = interfaz.Cursor(0)
            self.app.sonidos.reproducir("ui_pestana")
        elif (entrada.pulso(ARRIBA) or entrada.pulso(ABAJO)) and cuantas:
            self.elegido = (self.elegido + (-1 if entrada.pulso(ARRIBA) else 1)) % cuantas
            # La lista se desplaza para que el elegido siempre se vea
            self.primera = max(min(self.primera, self.elegido), self.elegido - FILAS + 1)
            self.cursor.ir_a(self.elegido - self.primera)
            self.app.sonidos.reproducir("ui_mover")
        elif entrada.pulso(VOLVER) or entrada.pulso(ACEPTAR):
            self.app.sonidos.reproducir("ui_volver")
            self.app.cambiar_escena(self.volver_a)

    # ---------- Dibujo ----------

    def dibujar(self, pantalla):
        self.dibujar_fondo(pantalla)
        interfaz.titulo(pantalla, "ARCHIVO", 48, 60, VIOLETA, interfaz.mezclar(VIOLETA, FONDO, 0.6),
                        tamano=GRANDE)
        entradas = self.entradas()
        nombre = {REGISTROS: "FRAGMENTOS", ECOS: "ECOS"}.get(PESTANAS[self.pestana], "FICHAS")
        encontradas = len([e for e in entradas if e.encontrada])
        total = len(todos_los_fragmentos()) if PESTANAS[self.pestana] == REGISTROS else len(entradas)
        texto(pantalla, "%s %d/%d" % (nombre, encontradas, total), CHICA, TEXTO_SUAVE, ANCHO - 48, 60,
              alinear="derecha")
        interfaz.pestanas(pantalla, BARRA_PESTANAS, self.app.entrada, PESTANAS, self.pestana, VIOLETA,
                          interfaz.mezclar(VIOLETA, FONDO, 0.7))
        self._dibujar_lista(pantalla, entradas)
        if entradas:
            self._dibujar_detalle(pantalla, entradas[self.elegido])
        interfaz.ayudas(pantalla, self.app.entrada, [("pestanas", "SECCION"), ("elegir", "ELEGIR"),
                                                     ("volver", "VOLVER")])

    def _dibujar_lista(self, pantalla, entradas):
        adentro = interfaz.panel(pantalla, LISTA, VIOLETA, PESTANAS[self.pestana])
        franja_y = adentro.top + round(self.cursor.valor * ALTO_FILA)
        pantalla.fill(FILA_ELEGIDA, (adentro.left - 8, franja_y, adentro.width + 16, ALTO_FILA - 6))
        pantalla.fill(VIOLETA, (adentro.left - 8, franja_y, 4, ALTO_FILA - 6))
        columna = COLUMNA_NOMBRE if PESTANAS[self.pestana] == REGISTROS else 4
        for fila, entrada in enumerate(entradas[self.primera:self.primera + FILAS]):
            i = self.primera + fila
            y = adentro.top + fila * ALTO_FILA + (ALTO_FILA - 6) // 2
            if entrada.etiqueta:
                texto(pantalla, entrada.etiqueta, CHICA, TEXTO_SUAVE, adentro.left + 4, y, alinear="izquierda")
            if entrada.encontrada:
                color = RESALTADO if i == self.elegido else TEXTO
                texto(pantalla, entrada.nombre, CHICA, color, adentro.left + columna, y, alinear="izquierda")
            else:
                texto(pantalla, "? ? ?", CHICA, TEXTO_APAGADO, adentro.left + columna, y, alinear="izquierda")
        # Flechitas si hay mas arriba o mas abajo
        if self.primera > 0:
            dibujo.pixel_art(pantalla, FLECHA_ARRIBA, LISTA.right - 36, LISTA.top + 40, TEXTO_SUAVE, 4)
        if self.primera + FILAS < len(entradas):
            dibujo.pixel_art(pantalla, FLECHA_ABAJO, LISTA.right - 36, LISTA.bottom - 24, TEXTO_SUAVE, 4)

    def _dibujar_detalle(self, pantalla, entrada):
        if not entrada.encontrada:
            adentro = interfaz.panel(pantalla, DETALLE, interfaz.mezclar(VIOLETA, FONDO, 0.5), "SIN DATOS")
            texto(pantalla, "TODAVIA NO LO ENCONTRASTE.", CHICA, TEXTO_SUAVE, adentro.left, adentro.top + 12,
                  alinear="izquierda")
            for i, linea in enumerate(dibujo.partir_lineas(entrada.donde, CHICA, adentro.width)):
                texto(pantalla, linea, CHICA, TEXTO_SUAVE, adentro.left, adentro.top + 40 + i * 26,
                      alinear="izquierda")
            return
        adentro = interfaz.panel(pantalla, DETALLE, VIOLETA, entrada.nombre)
        imagen = entrada.imagen() if entrada.imagen else None
        if imagen is not None:
            _dibujar_imagen(pantalla, imagen, adentro.left, adentro.top + ARRIBA_TEXTO)
        lineas, alto = acomodar(entrada.texto, adentro.width, imagen is not None)
        for x, y, linea in lineas:
            texto(pantalla, linea, CHICA, TEXTO, adentro.left + x, adentro.top + y, alinear="izquierda")
        y = adentro.top + alto
        if entrada.glifo:
            y += 10
            texto(pantalla, "GLIFO", CHICA, TEXTO_SUAVE, adentro.left, y, alinear="izquierda")
            dibujar_glifo(pantalla, entrada.glifo, adentro.left + 96, y, VIOLETA)
            y += 34
            if CLAVE_DE_LOS_GLIFOS in self.app.progreso.fragmentos:
                texto(pantalla, "DICE: " + traducir(entrada.glifo), CHICA, AMARILLO, adentro.left, y,
                      alinear="izquierda")
            else:
                texto(pantalla, "SIN TRADUCIR", CHICA, TEXTO_APAGADO, adentro.left, y, alinear="izquierda")


# ---------- Donde va cada renglon ----------

ARRIBA_TEXTO = 12           # donde empieza el texto (y el dibujo) adentro del panel
ALTO_RENGLON = 26
ENTRE_PARRAFOS = 14
ALTO_GLIFO = 10 + 34 + 26   # el renglon del glifo y el de su traduccion


def acomodar(parrafos, ancho, con_dibujo):
    # Reparte los parrafos en renglones: ([(x, y, renglon), ...], alto total), relativos al
    # adentro del panel. Con dibujo, los parrafos que empiezan a su altura van a su lado (mas
    # angostos) y los demas, debajo. (El test de que todo entra usa esta misma cuenta)
    lineas = []
    y = ARRIBA_TEXTO
    fin_del_dibujo = ARRIBA_TEXTO + LADO_DIBUJO + ENTRE_PARRAFOS if con_dibujo else 0
    for parrafo in parrafos:
        x = LADO_DIBUJO + 16 if y + ALTO_RENGLON <= fin_del_dibujo else 0
        for linea in dibujo.partir_lineas(parrafo, CHICA, ancho - x):
            lineas.append((x, y, linea))
            y += ALTO_RENGLON
        y += ENTRE_PARRAFOS
    return lineas, max(y, fin_del_dibujo)


# ---------- Los dibujos de las fichas ----------

_imagenes = {}


def imagen_de(ficha):
    # El dibujo de una ficha, listo para el recuadro (o None): los sprites chicos se agrandan
    # al doble (o mas) y los jefes se recortan al centro. Asi los pixeles siguen en la grilla
    if ficha.id not in _imagenes:
        _imagenes[ficha.id] = _preparar(_original(ficha))
    return _imagenes[ficha.id]


def _original(ficha):
    categoria, tipo = ficha.categoria
    if categoria == "enemigo" and tipo in TIPOS_ENEMIGO:
        return TIPOS_ENEMIGO[tipo].cuadros()[0]
    if categoria == "jefe" and tipo in TIPOS_JEFE:
        return TIPOS_JEFE[tipo].retrato()
    if categoria == "powerup" and tipo in TIPOS_POWERUP:
        return TIPOS_POWERUP[tipo].imagen_capsula()
    if ficha.id == "tecnologia:alondra":
        return nave.imagen("nave")
    if ficha.id == "fenomeno:monedas":
        return moneda.imagen_moneda()
    return None


def _preparar(imagen):
    if imagen is None:
        return None
    ancho, alto = imagen.get_size()
    lado = LADO_DIBUJO - 8
    if ancho > lado or alto > lado:
        recorte = pygame.Rect(0, 0, min(ancho, lado), min(alto, lado))
        recorte.center = (ancho // 2 // 2 * 2, alto // 2 // 2 * 2)
        return imagen.subsurface(recorte).copy()
    veces = max(1, min(4, lado // max(ancho, alto)))
    return pygame.transform.scale(imagen, (ancho * veces, alto * veces))


def _dibujar_imagen(pantalla, imagen, x, y):
    # El recuadro con el dibujo, arriba a la izquierda del detalle (el texto empieza a su lado)
    caja = pygame.Rect(x, y, LADO_DIBUJO, LADO_DIBUJO)
    pantalla.fill(interfaz.mezclar(VIOLETA, FONDO, 0.85), caja)
    pygame.draw.rect(pantalla, LINEA_APAGADA, caja, 2)
    dibujo.pegar(pantalla, imagen, caja.centerx, caja.centery, centrado=True)
