"""
DIALOGO: la escena de conversacion del modo historia (antes y despues de cada mision, los
mensajes de Ines, el rescate...).

Pedido del usuario: que los dialogos se cuenten como el prologo, con animaciones. Arriba hay un
ESCENARIO de cine (apaisado) con el CUADRO que va con lo que se dice (escenas/historia/cuadros/);
abajo, la caja con el retrato grande de quien habla, su nombre y el texto que se escribe solo.

Los renglones son (quien, texto); entre ellos, ("cuadro", "nombre") dice que dibujo se ve desde
ahi (un dialogo puede empezar con el que le pasa quien lo abre: 'cuadro'). Al cambiar de dibujo
hay un corte de camara (la cortina se abre); el nombre del lugar se escribe en la esquina y, al
empezar, una franja muestra el titulo de la mision. 'datos' llega a los dibujos (el modulo nuevo,
las piezas...); la escena les suma los años de la Umbral, lo encontrado y quien esta hablando.

Pasar, volver, saltear y la velocidad del texto: la Narracion (narracion.py). Al terminar llama a
'al_terminar' (la escena que sigue la decide quien abrio el dialogo: asi esta no depende de
ninguna otra). Sin ningun cuadro, el dialogo se ve como antes: el titulo grande sobre el fondo.

El fondo es el del sector de la mision (la App lo deja en su bioma antes de abrirla).
"""
import pygame

from juego import dibujo, interfaz, recursos
from juego.dibujo import texto, CHICA, MEDIA, GRANDE
from juego.config import ANCHO, FONDO, TEXTO, TEXTO_SUAVE, BLANCO, ESCENA_TITULO, ESCENA_CORTE, LINEA_APAGADA
from juego.escenas.historia import cuadros
from juego.escenas.historia.cuadros import kit
from juego.escenas.historia.narracion import Narracion
from juego.historia.personajes import PERSONAJES, dibujar_retrato
from juego.sonido import SILENCIO

CAJA = pygame.Rect(64, 318, ANCHO - 128, 212)
ESCENARIO = pygame.Rect(64, 40, 936, 264)      # el cine de arriba (el centro cae en la grilla de 2 px)
RETRATO = 10                # lado de cada pixel del retrato (12 x 10 = 120 px)
ANCHO_TEXTO = CAJA.width - 12 * RETRATO - 96
FLECHITA = ["XXXXX", ".XXX.", "..X.."]     # "hay mas": late al terminar cada renglon
ALTO_FRANJA = 104           # la franja del titulo de apertura


def armar_paginas(renglones, cuadro=None):
    # Los renglones como paginas: ("cuadro", nombre) cambia el dibujo de las que siguen
    paginas = []
    paso = 0
    for quien, mensaje in renglones:
        if quien == "cuadro":
            cuadro, paso = mensaje, 0
            continue
        paginas.append({"cuadro": cuadro, "quien": quien, "texto": mensaje, "paso": paso})
        paso += 1
    return paginas


class Dialogo(Narracion):
    musica = SILENCIO           # (las voces y el ambiente del sector, sin musica encima)

    def __init__(self, app, renglones, al_terminar, rotulo="", titulo="", color=BLANCO, cuadro=None, datos=None):
        paginas = armar_paginas([tuple(renglon[:2]) for renglon in renglones], cuadro)
        super().__init__(app, paginas, al_terminar)
        self.renglones = [(pagina["quien"], pagina["texto"]) for pagina in paginas]
        self.rotulo, self.titulo, self.color = rotulo, titulo, color     # "MISION 1", "LA SEÑAL"
        self.datos = dict(datos or {})
        self.con_cuadros = any(pagina["cuadro"] for pagina in paginas)

    @property
    def ambiente(self):
        return self.app.fondo.sector["ambiente"]

    def renglon_completo(self):
        return self.pagina_completa()

    # ---------- Dibujo ----------

    def dibujar(self, pantalla):
        self.dibujar_fondo(pantalla)
        if self.con_cuadros:
            self._dibujar_cine(pantalla)
        elif self.titulo:
            texto(pantalla, self.rotulo, CHICA, TEXTO_SUAVE, 64, 74, alinear="izquierda")
            interfaz.titulo(pantalla, self.titulo, 64, 120, self.color, interfaz.mezclar(self.color, FONDO, 0.6),
                            tamano=GRANDE)
        self._dibujar_caja(pantalla)
        self.dibujar_ayudas(pantalla)

    def _dibujar_caja(self, pantalla):
        personaje, mensaje = self.renglones[self.indice]
        nombre, color = PERSONAJES[personaje]
        adentro = interfaz.panel(pantalla, CAJA, color, nombre)
        dibujar_retrato(pantalla, personaje, adentro.left + 4, adentro.top + 2, RETRATO)
        texto_x = adentro.left + 12 * RETRATO + 36
        letras = int(self.letras)
        for i, linea in enumerate(dibujo.partir_lineas(mensaje, CHICA, ANCHO_TEXTO)):
            if letras <= 0:
                break
            texto(pantalla, linea[:letras], CHICA, TEXTO, texto_x, adentro.top + 14 + i * 28, alinear="izquierda")
            letras -= len(linea) + 1
        if self.renglon_completo() and dibujo.parpadeo(400):
            dibujo.pixel_art(pantalla, FLECHITA, CAJA.right - 34, CAJA.bottom - 26, color, 4)
        cuenta_y = 22 if self.con_cuadros else CAJA.top - 18
        texto(pantalla, "%d/%d" % (self.indice + 1, len(self.renglones)), CHICA, TEXTO_SUAVE, CAJA.right,
              cuenta_y, alinear="derecha")

    def _dibujar_cine(self, pantalla):
        # Arriba del escenario: "MISION 1 CUMPLIDA  LA SEÑAL" (el titulo grande sale en la franja)
        izquierda = ESCENARIO.left
        if self.rotulo:
            texto(pantalla, self.rotulo, CHICA, TEXTO_SUAVE, izquierda, 22, alinear="izquierda")
            izquierda += recursos.fuente(CHICA).size(self.rotulo)[0] + 24
        if self.titulo:
            texto(pantalla, self.titulo, CHICA, self.color, izquierda, 22, alinear="izquierda")
        nombre = self.cuadro_actual()
        t = self.pasos_en_cuadro
        if nombre is None:
            pantalla.fill(cuadros.NOCHE, ESCENARIO)
        else:
            datos = dict(self.datos, anios=self.app.progreso.anios, encontrados=self.app.progreso.fragmentos,
                         quien=self.renglones[self.indice][0])
            cuadros.dibujar(pantalla, nombre, ESCENARIO, t, self.pagina()["paso"], datos)
            self._dibujar_lugar(pantalla, cuadros.rotulo(nombre), t)
        self._dibujar_corte(pantalla, t)
        self._dibujar_franja(pantalla)
        pygame.draw.rect(pantalla, LINEA_APAGADA, ESCENARIO, 2)
        interfaz.esquinas(pantalla, ESCENARIO.inflate(8, 8), TEXTO_SUAVE, largo=12, grueso=2)

    def _dibujar_lugar(self, pantalla, lugar, t):
        # El nombre del lugar se escribe en la esquina, despues del corte (como en el cine)
        letras = max(0, (t - ESCENA_CORTE) // 2)
        if not lugar or letras <= 0:
            return
        x, y = ESCENARIO.left + 20, ESCENARIO.top + 22
        pantalla.fill(self.color, (x, y - 8, 4, 16))
        kit.rotulo(pantalla, lugar[:letras], x + 14, y, TEXTO, alinear="izquierda")

    def _dibujar_corte(self, pantalla, t):
        # La cortina: dos franjas negras que se abren desde el medio, con una linea clara en el borde
        if t >= ESCENA_CORTE:
            return
        mitad = ESCENARIO.height // 2
        tapa = dibujo.en_grilla(mitad * (1 - kit.avance(t, 0, ESCENA_CORTE)))
        if tapa <= 0:
            return
        arriba = pygame.Rect(ESCENARIO.left, ESCENARIO.top, ESCENARIO.width, tapa)
        abajo = pygame.Rect(ESCENARIO.left, ESCENARIO.bottom - tapa, ESCENARIO.width, tapa)
        for franja, borde in ((arriba, arriba.bottom - 2), (abajo, abajo.top)):
            pantalla.fill(FONDO, franja)
            pantalla.fill(LINEA_APAGADA, (franja.left, borde, franja.width, 2))

    def _dibujar_franja(self, pantalla):
        # El titulo de la mision al empezar: una franja que se abre, se queda y se cierra
        if not self.titulo or self.pasos >= ESCENA_TITULO:
            return
        abre = kit.avance(self.pasos, 0, 12) * (1 - kit.avance(self.pasos, ESCENA_TITULO - 12, 12))
        alto = dibujo.en_grilla(ALTO_FRANJA * abre)
        if alto <= 0:
            return
        franja = pygame.Rect(ESCENARIO.left, dibujo.en_grilla(ESCENARIO.centery - alto / 2), ESCENARIO.width, alto)
        pantalla.fill(FONDO, franja)
        pantalla.fill(self.color, (franja.left, franja.top, franja.width, 2))
        pantalla.fill(self.color, (franja.left, franja.bottom - 2, franja.width, 2))
        if alto >= ALTO_FRANJA:
            texto(pantalla, self.rotulo, CHICA, TEXTO_SUAVE, ESCENARIO.centerx, franja.top + 24)
            dibujo.texto_3d(pantalla, self.titulo, GRANDE if len(self.titulo) < 20 else MEDIA, self.color,
                            interfaz.mezclar(self.color, FONDO, 0.6), franja.top + 64, 4)
