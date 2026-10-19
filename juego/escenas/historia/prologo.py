"""
PROLOGO: la cinematica que abre el modo historia.

Pedido del usuario: "ni siquiera se que es la Marea: escribiste la historia pero no hay ningun
guion". El juego arrancaba en la mision 1 con "la Marea sigue en camino" y nadie explicaba
nada. Ahora, la primera vez que se entra a la HISTORIA, un narrador cuenta lo que sabe todo el
mundo (HISTORIA.md, seccion 1): que es la Marea, el compas, la Errante, el precio de viajar
rapido (la relatividad) y quienes son Alba e Ines. Despues viene la galaxia.

Es una lista de CUADROS. Cada uno tiene su DIBUJO (hecho con codigo y en la grilla de 2 px: los
del prologo estan en cuadros/prologo.py) y una o mas PAGINAS de texto que se escriben solas
abajo. Lo de pasar, volver y saltear lo resuelve la Narracion (narracion.py), igual que en los
dialogos. Al terminar anota que ya se vio (progreso.prologo) y llama a 'al_terminar' (como el
Dialogo: quien lo abre decide que sigue). Para sumar un cuadro: una linea en CUADROS y su dibujo
en cuadros/prologo.py.
"""
import pygame

from juego import dibujo, interfaz
from juego.dibujo import texto, CHICA, TITULO
from juego.config import CENTRO_X, FONDO, TEXTO, TEXTO_SUAVE, LINEA_APAGADA, ROJO, AMARILLO
from juego.escenas.historia import cuadros
from juego.escenas.historia.cuadros import kit
from juego.escenas.historia.narracion import Narracion
from juego.sonido import SILENCIO

ESCENARIO = pygame.Rect(dibujo.en_grilla(CENTRO_X - 320), 64, 640, 288)     # el dibujo de cada cuadro (en la grilla)
NOCHE = cuadros.NOCHE
TEXTO_IZQUIERDA = dibujo.en_grilla(CENTRO_X - 440)
ANCHO_TEXTO = 880
TEXTO_Y = 392
RENGLONES = 4               # lo que entra abajo (un test lo comprueba)
FLECHITA = ["XXXXX", ".XXX.", "..X.."]

CUADROS = [         # (dibujo, [paginas del narrador])
    ("cielo", ["HACE SEIS AÑOS, LOS TELESCOPIOS DE LA ESTACION UMBRAL VIERON ALGO NUEVO EN EL CIELO."]),
    ("marea", ["UNA GALAXIA ENANA, MIL VECES MAS PEQUEÑA QUE LA NUESTRA, QUE VIENE DIRECTO HACIA AQUI. "
               "LA LLAMARON LA MAREA."]),
    ("orbitas", ["NO VA A CHOCAR CONTRA NADA: VA A PASAR CERCA. PERO SU GRAVEDAD VA A TIRAR DE LAS "
                 "ESTRELLAS Y LOS PLANETAS, COMO LA LUNA TIRA DEL MAR.",
                 "LAS ORBITAS SE VAN A DESHACER. FALTAN SEIS AÑOS. NO SE PUEDE FRENAR, Y NINGUNA NAVE "
                 "LLEGA LO BASTANTE LEJOS PARA ESCAPAR."]),
    ("compas", ["HACE TRES MESES, EN TODAS LAS RADIOS, APARECIO UN RITMO. PULSOS CORTOS Y LARGOS, SIEMPRE LOS MISMOS.",
                "NO ES RUIDO: ALGUIEN LO ESTA MANDANDO. LO LLAMARON EL COMPAS. Y SUENA MAS FUERTE CERCA "
                "DE UNAS PIEZAS DE METAL QUE FLOTAN EN EL CINTURON EXTERIOR: LAS MONEDAS."]),
    ("errante", ["PERO ALGUIEN LO HABIA OIDO ANTES. HACE TRES AÑOS, EL CAPITAN MATEO SAAVEDRA SALIO CON SU "
                 "NAVE, LA ERRANTE, A BUSCAR DE DONDE VENIA EL COMPAS.",
                 "NUNCA VOLVIO."]),
    ("relojes", ["PARA LLEGAR LEJOS HAY QUE VIAJAR CASI A LA VELOCIDAD DE LA LUZ. Y ESO TIENE UN PRECIO: "
                 "EL TIEMPO.",
                 "PARA LA PILOTO, UN VIAJE DURA HORAS. EN LA ESTACION UMBRAL PASAN MESES. CADA VIAJE "
                 "ACERCA LA MAREA."]),
    ("alba", ["A LA UMBRAL LE QUEDA UNA SOLA NAVE CAPAZ DE IR TAN LEJOS: LA ALONDRA. LA PILOTEA ALBA, QUE SE OFRECIO PORQUE NO TIENE "
              "A NADIE QUE LA ESPERE.",
              "LA GUIA POR RADIO INES CORIA, LA ASTROFISICA QUE DESCIFRA EL COMPAS. LA MISION: SEGUIRLO "
              "HASTA DONDE NACE, ANTES DE QUE LLEGUE LA MAREA."]),
    ("titulo", []),
]


def paginas_del_prologo():
    # Cada pagina con su dibujo; el titulo es una pagina sin texto
    paginas = []
    for orden, (nombre, textos) in enumerate(CUADROS):
        for paso, pagina in enumerate(textos or [""]):
            paginas.append({"cuadro": nombre, "texto": pagina, "paso": paso, "orden": orden})
    return paginas


class Prologo(Narracion):
    musica = SILENCIO
    ambiente = "abismo"         # (el zumbido del espacio profundo, sin musica encima)

    def __init__(self, app, al_terminar):
        super().__init__(app, paginas_del_prologo(), al_terminar)

    def nombre_del_cuadro(self):
        return self.cuadro_actual()

    def terminar(self):
        self.app.progreso.ver_prologo()
        super().terminar()

    # ---------- Dibujo ----------

    def dibujar(self, pantalla):
        # Fondo liso con estrellas quietas (como en el cine: lo unico que se mueve es el cuadro)
        pantalla.fill(FONDO)
        kit.estrellas(pantalla, pantalla.get_rect(), 0, 120)
        t = self.pasos_en_cuadro
        if self.nombre_del_cuadro() == "titulo":
            self._dibujo_titulo(pantalla, t)
            seguir = "EMPEZAR"
        else:
            cuadros.dibujar(pantalla, self.nombre_del_cuadro(), ESCENARIO, t, self.pagina()["paso"])
            interfaz.esquinas(pantalla, ESCENARIO, TEXTO_SUAVE, largo=12, grueso=2)
            self._dibujar_narrador(pantalla)
            seguir = "SEGUIR"
        self._dibujar_avance(pantalla)
        self.dibujar_ayudas(pantalla, seguir)

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
        actual = self.pagina()["orden"]
        for i in range(len(CUADROS)):
            color = AMARILLO if i == actual else TEXTO_SUAVE if i < actual else LINEA_APAGADA
            pantalla.fill(color, (izquierda + i * 16 + 4, 32, 8, 8))

    def _dibujo_titulo(self, pantalla, t):
        kit.nube(pantalla, CENTRO_X, 250, 120, [interfaz.mezclar(color, FONDO, 0.7) for color in kit.MAREA], 9)
        dibujo.texto_3d(pantalla, "LA MAREA", TITULO, ROJO, interfaz.mezclar(ROJO, FONDO, 0.6), 220)
        if t > 40:
            texto(pantalla, "SIGUE EL COMPAS", CHICA, TEXTO_SUAVE, CENTRO_X, 320)
