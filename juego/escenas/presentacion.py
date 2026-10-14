"""
La presentacion: lo primero que se ve al abrir el juego (como en los juegos de consola).

    1. ADVERTENCIA   la de fotosensibilidad, sobre negro (y que los destellos se pueden
                     reducir en Opciones; si ya estan reducidos, lo dice)
    2. PYGAME        "HECHO CON PYGAME": las letras se escriben de a una
    3. TITULO        salto al hiperespacio, la nave sube con su estela y el logo cae y
                     golpea (temblor, onda, chispas y el acorde del logo); entra la musica del
                     menu y "PRESIONA ENTER" (o el boton A) titila. Al apretar, el menu

Cualquier tecla o boton saltea la advertencia y la tarjeta (va al titulo, nunca se pasa de
largo); en el titulo, si el logo todavia no cayo, lo hace caer ya. Solo se ve al arrancar
(App(presentacion=True)): volver al menu desde una partida va directo al Inicio.

Mientras tanto se preparan los giros de la nave (como en el Inicio): llegan listos al juego.
"""
import pygame

from juego import dibujo, interfaz, nave, recursos, accesibilidad
from juego.dibujo import texto, MINI, CHICA, MEDIA, GRANDE, TITULO
from juego.config import (ANCHO, ALTO, CENTRO_X, BLANCO, AMARILLO, MAGENTA, CIAN, VERDE, ORO, TEXTO_SUAVE,
                          TEXTO_APAGADO, VERSION)
from juego.carteles import suave
from juego.escenas.base import Escena
from juego.sonido import SILENCIO

MS_ADVERTENCIA = 3600       # lo que se ve la advertencia (con su entrada y su salida)
MS_PYGAME = 2200            # la tarjeta "HECHO CON PYGAME"
MS_FUNDIDO = 300            # lo que tarda en aparecer y en irse cada pantalla (en escalones)
MS_POR_LETRA = 90           # "PYGAME" se escribe de a una letra
MS_SIN_SALTEAR = 250        # al empezar cada pantalla, las teclas se ignoran (no se pasa de largo)

# El titulo
NAVE_SUBE = (300, 1100)     # ms en que la nave sube desde abajo hasta su lugar
LOGO_CAE = (500, 900)       # ms en que el logo cae (y a los 900, golpea)
Y_LOGO = (200, 262)         # "CAZA" y "MONEDAS"
Y_NAVE = 420
NEGRO = (0, 0, 0)

ADVERTENCIA = ("ESTE JUEGO TIENE LUCES QUE DESTELLAN Y PATRONES QUE PUEDEN AFECTAR A PERSONAS CON "
               "EPILEPSIA FOTOSENSIBLE. SI SIENTES MAREO O MOLESTIAS, DEJA DE JUGAR.")
TRIANGULO = [             # la señal de advertencia: un triangulo con "!"
    "....X....",
    "...XXX...",
    "...X.X...",
    "..X.X.X..",
    "..X.X.X..",
    ".X..X..X.",
    ".X.....X.",
    "X...X...X",
    "XXXXXXXXX",
]


class Presentacion(Escena):
    ambiente = SILENCIO

    def __init__(self, app):
        super().__init__(app)
        self.fase = "advertencia"
        self.desde = app.ahora()
        self.letras_escritas = 0
        self.logo_cayo = False

    @property
    def musica(self):
        # En silencio hasta que golpea el logo; ahi entra la del menu (y sigue en el Inicio)
        return "menu" if self.logo_cayo else SILENCIO

    def transcurrido(self):
        return self.app.ahora() - self.desde

    def pasar_a(self, fase):
        self.fase = fase
        self.desde = self.app.ahora()
        if fase == "titulo":
            self.app.fondo.saltar_al_hiperespacio()
            self.app.sonidos.reproducir("hiperespacio")

    # ---------- Logica ----------

    def actualizar(self, entrada):
        self.mover_fondo()
        self.app.efectos.actualizar()
        nave.preparar_giros(2)
        t = self.transcurrido()
        apretado = entrada.algo_apretado and t > MS_SIN_SALTEAR
        if self.fase == "advertencia":
            if apretado:
                self.pasar_a("titulo")          # cualquier boton va directo al titulo
            elif t > MS_ADVERTENCIA:
                self.pasar_a("pygame")
        elif self.fase == "pygame":
            letras = min(len("PYGAME"), int(max(0, t - 300) // MS_POR_LETRA))
            if letras > self.letras_escritas:
                self.letras_escritas = letras
                self.app.sonidos.reproducir("teclear")
            if apretado or t > MS_PYGAME:
                self.pasar_a("titulo")
        else:
            self._actualizar_titulo(t, entrada.algo_apretado)

    def _actualizar_titulo(self, t, apretado):
        if not self.logo_cayo and (t >= LOGO_CAE[1] or (apretado and t > MS_SIN_SALTEAR)):
            self.desde = self.app.ahora() - LOGO_CAE[1]          # (si se apreto, cae ya)
            self._golpe_del_logo()
            return
        if NAVE_SUBE[0] <= t:
            self.app.efectos.estela(CENTRO_X, self.y_nave(t) + 24, 0)
        if self.logo_cayo and apretado and t > LOGO_CAE[1] + 400:
            from juego.escenas.inicio import Inicio     # (aca adentro: Inicio no importa esta escena)
            self.app.sonidos.reproducir("ui_aceptar")
            self.app.cambiar_escena(Inicio(self.app))

    def _golpe_del_logo(self):
        # El logo golpea: temblor, onda de choque, chispas doradas y el acorde del logo
        self.logo_cayo = True
        efectos = self.app.efectos
        efectos.sacudir(14, BLANCO)
        for y in Y_LOGO:
            efectos.explosion(CENTRO_X, y, ORO, 28, 7, 4)
        efectos.onda_de_choque(CENTRO_X, (Y_LOGO[0] + Y_LOGO[1]) // 2, 360, AMARILLO, 30)
        self.app.sonidos.reproducir("logo")

    def y_nave(self, t):
        # Sube desde abajo de la pantalla y frena al llegar
        avance = suave(min(1, max(0, t - NAVE_SUBE[0]) / (NAVE_SUBE[1] - NAVE_SUBE[0])))
        return round(ALTO + 80 - (ALTO + 80 - Y_NAVE) * avance) // 2 * 2

    # ---------- Dibujo ----------

    def dibujar(self, pantalla):
        t = self.transcurrido()
        if self.fase == "advertencia":
            self._dibujar_advertencia(pantalla)
            self._fundido(pantalla, t, MS_ADVERTENCIA)
        elif self.fase == "pygame":
            self._dibujar_pygame(pantalla, t)
            self._fundido(pantalla, t, MS_PYGAME)
        else:
            self._dibujar_titulo(pantalla, t)
            self.app.efectos.dibujar_temblor_y_destello(pantalla)
            self._fundido(pantalla, t, None)

    def _fundido(self, pantalla, t, total):
        # Aparecer e irse en 4 escalones de negro (sin degradado: retro)
        restante = (total - t) if total else MS_FUNDIDO
        cerca = min(t, restante)
        if cerca < MS_FUNDIDO:
            escalon = 4 - int(cerca / MS_FUNDIDO * 4)
            dibujo.oscurecer(pantalla, NEGRO, min(255, escalon * 64))

    def _dibujar_advertencia(self, pantalla):
        pantalla.fill(NEGRO)
        dibujo.pixel_art(pantalla, TRIANGULO, CENTRO_X - 27, 140, AMARILLO, 6)
        texto(pantalla, "ADVERTENCIA DE SALUD", MEDIA, AMARILLO, CENTRO_X, 226)
        interfaz.separador(pantalla, CENTRO_X - 240, 254, 480)
        for i, linea in enumerate(dibujo.partir_lineas(ADVERTENCIA, CHICA, 760)):
            texto(pantalla, linea, CHICA, BLANCO, CENTRO_X, 290 + i * 28)
        if accesibilidad.destellos_reducidos():
            texto(pantalla, "DESTELLOS REDUCIDOS: ACTIVADO", CHICA, VERDE, CENTRO_X, 420)
        else:
            for i, linea in enumerate(("PUEDES REDUCIR LOS DESTELLOS EN", "OPCIONES > ACCESIBILIDAD > DESTELLOS")):
                texto(pantalla, linea, CHICA, CIAN, CENTRO_X, 420 + i * 28)

    def _dibujar_pygame(self, pantalla, t):
        pantalla.fill(NEGRO)
        texto(pantalla, "HECHO CON", CHICA, TEXTO_SUAVE, CENTRO_X, 262)
        palabra = "PYGAME"[:self.letras_escritas]
        if palabra:
            # Se escribe desde la izquierda (en su lugar final); la letra nueva nace blanca
            ancho = recursos.fuente(GRANDE).size(palabra)[0]
            izquierda = CENTRO_X - recursos.fuente(GRANDE).size("PYGAME")[0] // 2
            texto(pantalla, palabra, GRANDE, AMARILLO, izquierda, 310, alinear="izquierda")
            nueva = t - 300 - (len(palabra) - 1) * MS_POR_LETRA < 60
            if nueva:
                ultima_x = izquierda + ancho - recursos.fuente(GRANDE).size(palabra[-1])[0]
                texto(pantalla, palabra[-1], GRANDE, BLANCO, ultima_x, 310, alinear="izquierda")
        # Una linea que crece debajo, cuando termina de escribirse
        crece = min(1, max(0, t - 300 - 6 * MS_POR_LETRA) / 300)
        if crece > 0:
            largo = int(320 * suave(crece)) // 4 * 4
            interfaz.separador(pantalla, CENTRO_X - largo // 2, 346, largo)

    def _dibujar_titulo(self, pantalla, t):
        self.dibujar_fondo(pantalla)
        self.app.efectos.dibujar(pantalla)
        # La nave (al doble, como en el Inicio)
        if t >= NAVE_SUBE[0]:
            imagen = nave.imagen("nave")
            grande = pygame.transform.scale(imagen, (imagen.get_width() * 2, imagen.get_height() * 2))
            pantalla.blit(grande, grande.get_rect(center=(CENTRO_X, self.y_nave(t))))
        # El logo: cae acelerando y queda; con un brillo que lo cruza cada tanto
        cae = min(1, max(0, t - LOGO_CAE[0]) / (LOGO_CAE[1] - LOGO_CAE[0]))
        if cae > 0:
            for palabra, y in zip(("CAZA", "MONEDAS"), Y_LOGO):
                # Las dos palabras caen juntas (sin perder su separacion), acelerando
                y_ahora = round(y - 420 * (1 - cae * cae)) // 2 * 2
                dibujo.texto_3d(pantalla, palabra, TITULO, AMARILLO, MAGENTA, y_ahora, 6, None, CENTRO_X, "centro")
        if not self.logo_cayo:
            return
        despues = t - LOGO_CAE[1]
        if despues > 250:
            texto(pantalla, "ATRAPA.  ESQUIVA.  SOBREVIVE.", CHICA, CIAN, CENTRO_X, 316)
        if despues > 700 and dibujo.parpadeo(550):
            self._presiona(pantalla, 520)
        texto(pantalla, "VERSION " + VERSION, MINI, TEXTO_APAGADO, ANCHO - 20, ALTO - 14, alinear="derecha")

    def _presiona(self, pantalla, y):
        # "PRESIONA" y el boton de aceptar del control que se uso por ultimo (ENTER o A), centrados
        teclas, botones = interfaz.GLIFOS["aceptar"]
        glifo = (botones if self.app.entrada.usando_mando() else teclas)[0]
        ancho_glifo = interfaz.boton(pygame.Surface((200, 40), pygame.SRCALPHA), glifo, 0, 20)
        ancho_texto = recursos.fuente(MEDIA).size("PRESIONA")[0]
        izquierda = CENTRO_X - (ancho_texto + 16 + ancho_glifo) // 2
        texto(pantalla, "PRESIONA", MEDIA, BLANCO, izquierda, y, alinear="izquierda")
        interfaz.boton(pantalla, glifo, izquierda + ancho_texto + 16, y)
