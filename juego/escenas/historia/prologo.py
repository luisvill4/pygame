"""
PROLOGO: la cinematica que abre el modo historia.

Pedido del usuario: "ni siquiera se que es la Marea: escribiste la historia pero no hay ningun
guion". El juego arrancaba en la mision 1 con "la Marea sigue en camino" y nadie explicaba
nada. Ahora, la primera vez que se entra a la HISTORIA, un narrador cuenta lo que sabe todo el
mundo (HISTORIA.md, seccion 1): que es la Marea, el compas, la Errante, el precio de viajar
rapido (la relatividad) y quienes son Alba e Ines. Despues viene la galaxia.

Es una lista de CUADROS. Cada uno tiene su DIBUJO (hecho con codigo y en la grilla de 2 px: el
metodo _dibujo_<nombre>) y una o mas PAGINAS de texto que se escriben solas abajo. ACEPTAR
completa la pagina o pasa a la siguiente; VOLVER saltea todo. Los dibujos se mueven con
'pasos_en_cuadro', que avanza en actualizar: funciona igual a cualquier FPS. Al terminar anota que
ya se vio (progreso.prologo) y llama a 'al_terminar' (como el Dialogo: quien lo abre decide que
sigue). Para sumar un cuadro: una linea en CUADROS y su metodo _dibujo_<nombre>.
"""
import math
import random

import pygame

from juego import dibujo, interfaz, nave
from juego.dibujo import texto, CHICA, TITULO
from juego.config import (CENTRO_X, FONDO, TEXTO, TEXTO_SUAVE, LINEA_APAGADA, ROJO, AMARILLO, CIAN, VIOLETA,
                          BLANCO, NARANJA, CONTORNO, DIALOGO_LETRAS_POR_PASO)
from juego.entrada import ACEPTAR, VOLVER
from juego.escenas.base import Escena
from juego.historia.personajes import dibujar_retrato
from juego.historia.glifos import escribir, ritmo
from juego.sonido import SILENCIO

ESCENARIO = pygame.Rect(dibujo.en_grilla(CENTRO_X - 320), 64, 640, 288)     # el dibujo de cada cuadro (en la grilla)
NOCHE = (4, 6, 16)
TEXTO_IZQUIERDA = dibujo.en_grilla(CENTRO_X - 440)
ANCHO_TEXTO = 880
TEXTO_Y = 392
RENGLONES = 4               # lo que entra abajo (un test lo comprueba)
FLECHITA = ["XXXXX", ".XXX.", "..X.."]

# Los colores de las dos galaxias: del centro (brillante) al borde (apagado)
NUESTRA = [BLANCO, (190, 225, 255), (110, 170, 255), (50, 80, 170)]
MAREA = [(255, 210, 200), ROJO, (190, 30, 90), (100, 20, 50)]

ESTACION = ["...X...", "..XXX..", "X.XXX.X", "XXXXXXX", "X.XXX.X", "..XXX..", "...X..."]
ERRANTE = ["..XX......",
           "..XXX.....",
           "XXXXXXXX..",
           "XXXXXXXXXX",
           "XXXXXXXX..",
           "..XXX.....",
           "..XX......"]

CUADROS = [         # (dibujo, [paginas del narrador])
    ("cielo", ["HACE SEIS AÑOS, LOS TELESCOPIOS DE LA ESTACION UMBRAL VIERON ALGO NUEVO EN EL CIELO."]),
    ("marea", ["UNA GALAXIA ENANA, MIL VECES MAS PEQUEÑA QUE LA NUESTRA, QUE VIENE DIRECTO HACIA AQUI. "
               "LA LLAMARON LA MAREA."]),
    ("orbitas", ["NO VA A CHOCAR CONTRA NADA: VA A PASAR CERCA. PERO SU GRAVEDAD VA A TIRAR DE LAS "
                 "ESTRELLAS Y LOS PLANETAS, COMO LA LUNA TIRA DEL MAR.",
                 "LAS ORBITAS SE VAN A DESHACER. FALTAN SEIS AÑOS. NO SE PUEDE FRENAR, Y NINGUNA NAVE "
                 "LLEGA LO BASTANTE LEJOS PARA ESCAPAR."]),
    ("compas", ["ENTONCES, EN TODAS LAS RADIOS, APARECIO UN RITMO. PULSOS CORTOS Y LARGOS, SIEMPRE LOS MISMOS.",
                "NO ES RUIDO: ALGUIEN LO ESTA MANDANDO. LO LLAMARON EL COMPAS. Y SUENA MAS FUERTE CERCA "
                "DE UNAS PIEZAS DE METAL QUE FLOTAN EN EL CINTURON EXTERIOR: LAS MONEDAS."]),
    ("errante", ["HACE TRES AÑOS, EL CAPITAN MATEO SAAVEDRA SALIO CON SU NAVE, LA ERRANTE, A BUSCAR DE "
                 "DONDE VENIA EL COMPAS.",
                 "NUNCA VOLVIO."]),
    ("relojes", ["PARA LLEGAR LEJOS HAY QUE VIAJAR CASI A LA VELOCIDAD DE LA LUZ. Y ESO TIENE UN PRECIO: "
                 "EL TIEMPO.",
                 "PARA LA PILOTO, UN VIAJE DURA HORAS. EN LA ESTACION UMBRAL PASAN MESES. CADA VIAJE "
                 "ACERCA LA MAREA."]),
    ("alba", ["A LA UMBRAL LE QUEDA UNA NAVE: LA ALONDRA. LA PILOTEA ALBA, QUE SE OFRECIO PORQUE NO TIENE "
              "A NADIE QUE LA ESPERE.",
              "LA GUIA POR RADIO INES CORIA, LA ASTROFISICA QUE DESCIFRA EL COMPAS. LA MISION: SEGUIRLO "
              "HASTA DONDE NACE, ANTES DE QUE LLEGUE LA MAREA."]),
    ("titulo", []),
]


class Prologo(Escena):
    musica = SILENCIO
    ambiente = "abismo"         # (el zumbido del espacio profundo, sin musica encima)

    def __init__(self, app, al_terminar):
        super().__init__(app)
        self.al_terminar = al_terminar
        self.cuadro = 0
        self.pagina = 0
        self.letras = 0.0
        self.pasos_en_cuadro = 0
        self.terminado = False

    def nombre_del_cuadro(self):
        return CUADROS[self.cuadro][0]

    def texto_actual(self):
        paginas = CUADROS[self.cuadro][1]
        return paginas[self.pagina] if paginas else ""

    def pagina_completa(self):
        return self.letras >= len(self.texto_actual())

    def actualizar(self, entrada):
        self.mover_fondo()
        if self.terminado:
            return
        self.pasos_en_cuadro += 1
        antes = int(self.letras)
        self.letras += DIALOGO_LETRAS_POR_PASO
        if int(self.letras) > antes and not self.pagina_completa() and int(self.letras) % 3 == 0:
            self.app.sonidos.reproducir("teclear")
        if self.pasos_en_cuadro == 1 and self.nombre_del_cuadro() == "compas":
            self.app.sonidos.reproducir("fragmento")        # el compas de verdad, el que se oye en el juego
        if entrada.pulso(VOLVER):
            self.app.sonidos.reproducir("ui_volver")
            self._terminar()
        elif entrada.pulso(ACEPTAR):
            self._seguir()

    def _seguir(self):
        # Completa la pagina; si ya estaba, la siguiente; si no hay mas, el cuadro siguiente
        if not self.pagina_completa():
            self.letras = len(self.texto_actual())
        elif self.pagina + 1 < len(CUADROS[self.cuadro][1]):
            self.pagina += 1
            self.letras = 0
            self.app.sonidos.reproducir("ui_mover")
        elif self.cuadro + 1 < len(CUADROS):
            self.cuadro += 1
            self.pagina = 0
            self.letras = 0
            self.pasos_en_cuadro = 0
            self.app.sonidos.reproducir("ui_mover")
        else:
            self.app.sonidos.reproducir("ui_aceptar")
            self._terminar()

    def _terminar(self):
        self.terminado = True
        self.app.progreso.ver_prologo()
        self.al_terminar()

    # ---------- Dibujo ----------

    def dibujar(self, pantalla):
        # Fondo liso con estrellas quietas (como en el cine: lo unico que se mueve es el cuadro)
        pantalla.fill(FONDO)
        _estrellas(pantalla, 0, 120, pantalla.get_rect())
        t = self.pasos_en_cuadro
        if self.nombre_del_cuadro() == "titulo":
            self._dibujo_titulo(pantalla, t)
            ayuda = "EMPEZAR"
        else:
            pantalla.fill(NOCHE, ESCENARIO)
            pantalla.set_clip(ESCENARIO)            # (lo que se pasa del escenario no se dibuja)
            getattr(self, "_dibujo_" + self.nombre_del_cuadro())(pantalla, t)
            pantalla.set_clip(None)
            interfaz.esquinas(pantalla, ESCENARIO, TEXTO_SUAVE, largo=12, grueso=2)
            self._dibujar_narrador(pantalla)
            ayuda = "SEGUIR"
        self._dibujar_avance(pantalla)
        interfaz.ayudas(pantalla, self.app.entrada, [("volver", "SALTEAR"), ("aceptar", ayuda)])

    def _dibujar_narrador(self, pantalla):
        letras = int(self.letras)
        lineas = dibujo.partir_lineas(self.texto_actual(), CHICA, ANCHO_TEXTO)
        for i, linea in enumerate(lineas):
            if letras <= 0:
                break
            texto(pantalla, linea[:letras], CHICA, TEXTO, TEXTO_IZQUIERDA, TEXTO_Y + i * 30, alinear="izquierda")
            letras -= len(linea) + 1
        if self.pagina_completa() and dibujo.parpadeo(400):
            dibujo.pixel_art(pantalla, FLECHITA, CENTRO_X + ANCHO_TEXTO // 2 - 10, TEXTO_Y + RENGLONES * 30 - 4,
                             TEXTO_SUAVE, 4)

    def _dibujar_avance(self, pantalla):
        # Un cuadradito por cuadro: el actual en amarillo, los vistos claros, los que faltan apagados
        izquierda = dibujo.en_grilla(CENTRO_X - len(CUADROS) * 8)
        for i in range(len(CUADROS)):
            color = AMARILLO if i == self.cuadro else TEXTO_SUAVE if i < self.cuadro else LINEA_APAGADA
            pantalla.fill(color, (izquierda + i * 16 + 4, 32, 8, 8))

    # ---------- Los dibujos de cada cuadro (t = pasos desde que empezo) ----------

    def _dibujo_cielo(self, pantalla, t):
        # Nuestra galaxia que gira despacio y, arriba a la derecha, un punto rojo que no estaba
        _estrellas(pantalla, 1, 90)
        _galaxia(pantalla, ESCENARIO.centerx - 60, ESCENARIO.centery + 10, 150, t * 0.004, NUESTRA, 1)
        if t > 50:
            x, y = ESCENARIO.right - 110, ESCENARIO.top + 64
            pantalla.fill(ROJO, (x - 2, y - 2, 4, 4))
            dibujo.halo(pantalla, x, y, 12, ROJO)
            if t > 90:      # la mira del telescopio se cierra sobre el punto
                lado = max(16, 60 - (t - 90) // 2 * 2)
                interfaz.esquinas(pantalla, pygame.Rect(x - lado // 2, y - lado // 2, lado, lado), AMARILLO,
                                  largo=6, grueso=2)

    def _dibujo_marea(self, pantalla, t):
        # La Marea (roja, sin forma) se acerca a la nuestra (la espiral azul)
        _estrellas(pantalla, 2, 70)
        _galaxia(pantalla, ESCENARIO.left + 190, ESCENARIO.centery, 120, t * 0.003, NUESTRA, 1)
        x = ESCENARIO.right - 130 - min(t, 400) * 0.15
        _nube(pantalla, x, ESCENARIO.centery - 20, 50, MAREA, 3)
        texto(pantalla, "NOSOTROS", CHICA, (110, 170, 255), ESCENARIO.left + 190, ESCENARIO.bottom - 24,
              contorno=CONTORNO)
        texto(pantalla, "LA MAREA", CHICA, ROJO, dibujo.en_grilla(x), ESCENARIO.bottom - 24, contorno=CONTORNO)

    def _dibujo_orbitas(self, pantalla, t):
        # Una estrella con sus planetas; la Marea entra por la derecha y las orbitas se estiran
        _estrellas(pantalla, 3, 60)
        tiron = min(1.0, t / 420)
        sol_x, sol_y = ESCENARIO.centerx - 60, ESCENARIO.centery
        borde = ESCENARIO.right - dibujo.en_grilla(40 + 100 * tiron)
        for y in range(ESCENARIO.top, ESCENARIO.bottom, 2):     # el frente rojo, como en el mapa
            onda = dibujo.en_grilla(math.sin(y / 19 + t / 30) * 6)
            if (y // 2) % 2 == 0:
                pantalla.fill((50, 8, 26), (borde + onda, y, ESCENARIO.right - borde - onda, 2))
            pantalla.fill(ROJO, (borde + onda, y, 4, 2))
        for i, (radio, velocidad) in enumerate(((50, 0.03), (90, 0.018), (130, 0.011))):
            estirar = 1 + tiron * 0.25 * (i + 1)                 # las de afuera se estiran mas
            centro_x = sol_x + tiron * 14 * (i + 1)
            for paso in range(0, 360, 6):
                angulo = math.radians(paso)
                pantalla.fill(LINEA_APAGADA, (dibujo.en_grilla(centro_x + math.cos(angulo) * radio * estirar),
                                              dibujo.en_grilla(sol_y + math.sin(angulo) * radio * 0.45), 2, 2))
            angulo = t * velocidad + i * 2
            x = centro_x + math.cos(angulo) * radio * estirar
            y = sol_y + math.sin(angulo) * radio * 0.45
            if i == 2 and tiron >= 1:           # el de afuera se suelta y se va hacia la Marea
                x += (t - 420) * 0.6
            pantalla.fill((140, 200, 255), (dibujo.en_grilla(x) - 4, dibujo.en_grilla(y) - 4, 8, 8))
        pantalla.fill(AMARILLO, (sol_x - 8, sol_y - 8, 16, 16))
        dibujo.halo(pantalla, sol_x, sol_y, 28, AMARILLO)
        if self.pagina >= 1:
            texto(pantalla, "FALTAN 6 AÑOS", CHICA, ROJO, ESCENARIO.left + 20, ESCENARIO.top + 24,
                  alinear="izquierda", contorno=CONTORNO)

    def _dibujo_compas(self, pantalla, t):
        # Un osciloscopio: el compas pasa de derecha a izquierda, con el ritmo de verdad
        caja = ESCENARIO.inflate(-80, -100)
        for x in range(caja.left, caja.right, 32):               # la cuadricula de la pantallita
            pantalla.fill((16, 20, 44), (x, caja.top, 2, caja.height))
        for y in range(caja.top, caja.bottom, 32):
            pantalla.fill((16, 20, 44), (caja.left, y, caja.width, 2))
        pulsos, vuelta = ritmo(escribir("ALBA"), 1)
        ancho_unidad = 14
        base, alto = caja.centery + 30, 60
        azar = random.Random(t // 3)
        for x in range(caja.left, caja.right, 2):
            unidad = ((x - caja.left + t * 2) // ancho_unidad) % vuelta
            encendido = any(inicio <= unidad < inicio + largo for inicio, largo, _ in pulsos)
            if encendido:
                pantalla.fill(VIOLETA, (x, base - alto, 2, alto + 2))
            else:
                pantalla.fill(interfaz.mezclar(VIOLETA, NOCHE, 0.5), (x, base - azar.choice((0, 2, 2, 4)), 2, 2))
        texto(pantalla, "EL COMPAS", CHICA, VIOLETA, caja.left, caja.top - 24, alinear="izquierda", contorno=CONTORNO)
        interfaz.esquinas(pantalla, caja, interfaz.mezclar(VIOLETA, NOCHE, 0.4), largo=8, grueso=2)

    def _dibujo_errante(self, pantalla, t):
        # La Errante sale de la Umbral y se pierde a lo lejos
        _estrellas(pantalla, 5, 80)
        dibujo.pixel_art(pantalla, ESTACION, ESCENARIO.left + 90, ESCENARIO.centery + 40, AMARILLO, 8)
        avance = min(t, 300)
        x = ESCENARIO.left + 150 + avance * 1.4
        y = ESCENARIO.centery + 40 - avance * 0.35
        if avance < 300:
            pixel = 4 if avance < 150 else 2                 # (se achica: se aleja)
            largo_llama = 2 + round(math.sin(t / 4) + 1) * 2
            pantalla.fill(NARANJA, (dibujo.en_grilla(x) - len(ERRANTE[0]) * pixel // 2 - largo_llama * pixel // 2,
                                    dibujo.en_grilla(y) - pixel, largo_llama * pixel // 2, pixel * 2))
            dibujo.pixel_art(pantalla, ERRANTE, dibujo.en_grilla(x), dibujo.en_grilla(y), (200, 200, 215), pixel)
        if self.pagina >= 1:
            texto(pantalla, "LA ERRANTE", CHICA, TEXTO_SUAVE, ESCENARIO.right - 24, ESCENARIO.top + 24,
                  alinear="derecha", contorno=CONTORNO)
            texto(pantalla, "SIN SEÑAL", CHICA, ROJO, ESCENARIO.right - 24, ESCENARIO.top + 52,
                  alinear="derecha", contorno=CONTORNO)

    def _dibujo_relojes(self, pantalla, t):
        # Dos relojes: el de la Alondra casi no se mueve; el de la Umbral vuela
        _estrellas(pantalla, 6, 40)
        izquierda, derecha, y = ESCENARIO.centerx - 150, ESCENARIO.centerx + 150, ESCENARIO.centery - 20
        _reloj(pantalla, izquierda, y, 70, t * 0.004, CIAN)
        _reloj(pantalla, derecha, y, 70, t * 0.25, AMARILLO)
        texto(pantalla, "LA ALONDRA", CHICA, CIAN, izquierda, y + 100, contorno=CONTORNO)
        texto(pantalla, "LA UMBRAL", CHICA, AMARILLO, derecha, y + 100, contorno=CONTORNO)
        horas = min(t // 160, 9)
        meses = min(t // 25, 99)
        texto(pantalla, _cuantos(horas, "HORA", "HORAS"), CHICA, TEXTO_SUAVE, izquierda, y + 128, contorno=CONTORNO)
        texto(pantalla, _cuantos(meses, "MES", "MESES"), CHICA, TEXTO_SUAVE, derecha, y + 128, contorno=CONTORNO)

    def _dibujo_alba(self, pantalla, t):
        # Ines y Alba, y la Alondra entre las dos
        _estrellas(pantalla, 7, 60)
        for personaje, centro, nombre, lugar, color in (("ines", ESCENARIO.left + 120, "INES CORIA", "LA UMBRAL", AMARILLO),
                                                        ("alba", ESCENARIO.right - 120, "ALBA", "LA ALONDRA", CIAN)):
            dibujar_retrato(pantalla, personaje, centro - 48, ESCENARIO.top + 72, 8)
            interfaz.esquinas(pantalla, pygame.Rect(centro - 48, ESCENARIO.top + 72, 96, 96), color, largo=8, grueso=2)
            texto(pantalla, nombre, CHICA, color, centro, ESCENARIO.top + 200, contorno=CONTORNO)
            texto(pantalla, lugar, CHICA, TEXTO_SUAVE, centro, ESCENARIO.top + 228, contorno=CONTORNO)
        imagen = nave.imagen("nave")
        grande = pygame.transform.scale(imagen, (imagen.get_width() * 2, imagen.get_height() * 2))
        flota = round(math.sin(t / 20) * 2) * 2
        y = ESCENARIO.centery - 4 + flota
        largo_llama = 6 + round(math.sin(t / 3) + 1) * 4
        pantalla.fill(NARANJA, (ESCENARIO.centerx - 6, y + 46, 12, largo_llama))
        pantalla.fill(AMARILLO, (ESCENARIO.centerx - 2, y + 46, 4, largo_llama // 2 // 2 * 2))
        dibujo.pegar(pantalla, grande, ESCENARIO.centerx, y, centrado=True)

    def _dibujo_titulo(self, pantalla, t):
        _nube(pantalla, CENTRO_X, 250, 120, [interfaz.mezclar(color, FONDO, 0.7) for color in MAREA], 9)
        dibujo.texto_3d(pantalla, "LA MAREA", TITULO, ROJO, interfaz.mezclar(ROJO, FONDO, 0.6), 220)
        if t > 40:
            texto(pantalla, "SIGUE EL COMPAS", CHICA, TEXTO_SUAVE, CENTRO_X, 320)


# ---------- Ayudas de dibujo (todo en la grilla de 2 px) ----------

def _cuantos(numero, singular, plural):
    return "%d %s" % (numero, singular if numero == 1 else plural)


def _estrellas(pantalla, semilla, cuantas, zona=ESCENARIO):
    # Estrellas fijas (la misma semilla, el mismo cielo)
    azar = random.Random(semilla)
    for _ in range(cuantas):
        x = dibujo.en_grilla(azar.randint(zona.left, zona.right))
        y = dibujo.en_grilla(azar.randint(zona.top, zona.bottom))
        gris = azar.choice((40, 60, 90, 130) if zona is not ESCENARIO else (50, 80, 120, 170))
        pantalla.fill((gris, gris, gris + 30), (x, y, 2, 2))


def _galaxia(pantalla, cx, cy, radio, giro, colores, semilla, puntos=700):
    # Una espiral de dos brazos, inclinada (se ve aplastada): del centro brillante al borde apagado.
    # Los brazos tienen ancho (cada estrella se corre un poco del centro del brazo) y entre los
    # brazos hay un polvo mas oscuro
    azar = random.Random(semilla)
    for i in range(puntos):
        fraccion = azar.random() ** 0.8
        if i % 5 == 0:          # el polvo del disco, entre los brazos
            angulo, color = azar.uniform(0, math.tau), colores[-1]
        else:
            angulo = giro + fraccion * 3.8 + (i % 2) * math.pi + azar.gauss(0, 0.22)
            color = colores[min(len(colores) - 1, int(fraccion * len(colores)))]
        distancia = radio * fraccion
        x = cx + math.cos(angulo) * distancia
        y = cy + math.sin(angulo) * distancia * 0.5
        pantalla.fill(color, (dibujo.en_grilla(x), dibujo.en_grilla(y), 2, 2))
    pantalla.fill(colores[1], (dibujo.en_grilla(cx) - 6, dibujo.en_grilla(cy) - 4, 12, 8))     # el nucleo
    pantalla.fill(colores[0], (dibujo.en_grilla(cx) - 4, dibujo.en_grilla(cy) - 2, 8, 4))
    dibujo.halo(pantalla, cx, cy, radio // 4, colores[1])


def _nube(pantalla, cx, cy, radio, colores, semilla, puntos=220):
    # Una galaxia sin forma (la Marea): una nube con una cola que se estira hacia atras
    azar = random.Random(semilla)
    for i in range(puntos):
        if i % 4 == 0:      # la cola
            distancia = azar.uniform(0, radio * 1.6)
            x, y = cx + radio * 0.4 + distancia, cy + azar.gauss(0, 4 + distancia * 0.12)
            fraccion = min(1.0, 0.5 + distancia / (radio * 3))
        else:
            distancia = abs(azar.gauss(0, radio * 0.45))
            angulo = azar.uniform(0, math.tau)
            x, y = cx + math.cos(angulo) * distancia, cy + math.sin(angulo) * distancia * 0.7
            fraccion = min(1.0, distancia / radio)
        color = colores[min(len(colores) - 1, int(fraccion * len(colores)))]
        pantalla.fill(color, (dibujo.en_grilla(x), dibujo.en_grilla(y), 2, 2))
    dibujo.halo(pantalla, cx, cy, radio // 2, colores[1])


def _reloj(pantalla, cx, cy, radio, angulo, color):
    # La esfera de puntos, las doce marcas y la aguja (cuadraditos a lo largo de la linea)
    for paso in range(0, 360, 6):
        a = math.radians(paso)
        lado = 4 if paso % 30 == 0 else 2
        pantalla.fill(interfaz.mezclar(color, NOCHE, 0.3 if lado == 4 else 0.6),
                      (dibujo.en_grilla(cx + math.cos(a) * radio), dibujo.en_grilla(cy + math.sin(a) * radio), lado, lado))
    for paso in range(0, radio - 12, 2):
        x = cx + math.sin(angulo) * paso
        y = cy - math.cos(angulo) * paso
        pantalla.fill(color, (dibujo.en_grilla(x) - 2, dibujo.en_grilla(y) - 2, 4, 4))
    pantalla.fill(BLANCO, (cx - 4, cy - 4, 8, 8))
