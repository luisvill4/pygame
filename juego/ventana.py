"""
La ventana real del juego.

Todo se dibuja en un lienzo de ANCHO x ALTO (1066x600) y mostrar() lo
escala a la ventana sin suavizar (pixeles nitidos), centrado y con barras negras
si sobra espacio.

Las lineas CRT se ponen aqui, DESPUES de escalar: asi quedan parejas en cualquier
resolucion (en el lienzo, al agrandarlo 1.8 veces, unas salian mas gruesas que otras).
Hay UNA linea oscura al pie de cada fila de pixeles de arte (PIXEL_ARTE filas del
lienzo): cada pixel de los sprites lleva su linea, como en una pantalla de verdad. Con
una escala no entera una fila ocupa 3 o 4 pixeles de la ventana, pero igual lleva una
sola linea (se le pregunta al mismo escalador donde termina cada fila).
"""
import pygame

from juego import accesibilidad
from juego.config import RESOLUCIONES, PIXEL_ARTE


class Ventana:
    def __init__(self):
        self.alto_escritorio = pygame.display.get_desktop_sizes()[0][1]
        self.superficie = None
        self._lineas = None         # (clave, capa) de las lineas CRT para el tamaño actual
        self._zona = None           # (clave, subsuperficie) donde va el lienzo en la ventana actual
        self._grande = None         # el lienzo agrandado a un multiplo entero (escalado SUAVE)

    @property
    def resoluciones(self):
        # Las que caben en el monitor (80 px de margen para la barra de tareas y el
        # titulo de la ventana); la pantalla completa siempre esta
        return [r for r in RESOLUCIONES
                if r[0] == "COMPLETA" or r[2] + 80 <= self.alto_escritorio]

    def nombres(self):
        return [r[0] for r in self.resoluciones]

    def aplicar(self, nombre):
        # Abre la ventana con la resolucion elegida (por nombre, ej: "1280x720")
        _, ancho, alto = next(r for r in self.resoluciones if r[0] == nombre)
        if nombre == "COMPLETA":
            self.superficie = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
            pygame.mouse.set_visible(False)
        else:
            self.superficie = pygame.display.set_mode((ancho, alto))
            # Trampa: al salir de pantalla completa la ventana vuelve a su tamaño
            # anterior y no al pedido; pedirlo otra vez lo corrige
            if self.superficie.get_size() != (ancho, alto):
                self.superficie = pygame.display.set_mode((ancho, alto))
            pygame.mouse.set_visible(True)

    def mostrar(self, lienzo_dibujado):
        # Escala el lienzo a la ventana, le pone las lineas CRT y lo muestra
        # (reemplaza a display.flip())
        ancho_lienzo, alto_lienzo = lienzo_dibujado.get_size()
        ancho_ventana, alto_ventana = self.superficie.get_size()
        escala = min(ancho_ventana / ancho_lienzo, alto_ventana / alto_lienzo)
        zona = self._zona_del_juego(int(ancho_lienzo * escala), int(alto_lienzo * escala))
        if escala == 1:
            zona.blit(lienzo_dibujado, (0, 0))
        elif accesibilidad.escalado_suave() and escala != int(escala):
            self._escalar_parejo(lienzo_dibujado, zona, escala)
        else:
            try:
                # Escalar directo sobre la ventana: 3 veces mas rapido que crear una imagen
                # nueva y copiarla (~1 ms en vez de ~3.5 ms en 1920x1080)
                pygame.transform.scale(lienzo_dibujado, zona.get_size(), zona)
            except ValueError:
                # (si la ventana guarda los pixeles en otro formato, no se puede: se copia)
                zona.blit(pygame.transform.scale(lienzo_dibujado, zona.get_size()), (0, 0))
        brillo = accesibilidad.brillo_crt()
        if brillo < 255:
            # Multiplicar por una capa blanca con filas grises oscurece solo esas filas
            # (una sola operacion: ~0.3 ms en 1920x1080)
            self.superficie.blit(self._capa_crt(zona, alto_lienzo, escala, brillo), (0, 0),
                                 special_flags=pygame.BLEND_RGB_MULT)
        pygame.display.flip()

    def _escalar_parejo(self, lienzo_dibujado, zona, escala):
        # "Sharp bilinear": se agranda sin suavizar al multiplo entero de arriba (todos los
        # pixeles iguales) y despues se achica suavizando hasta el tamaño de la ventana.
        # Asi ningun pixel sale mas ancho que otro; el borde queda apenas suave
        entero = int(escala) + 1
        tamano = (lienzo_dibujado.get_width() * entero, lienzo_dibujado.get_height() * entero)
        if self._grande is None or self._grande.get_size() != tamano:
            self._grande = pygame.Surface(tamano, 0, lienzo_dibujado)
        pygame.transform.scale(lienzo_dibujado, tamano, self._grande)
        try:
            pygame.transform.smoothscale(self._grande, zona.get_size(), zona)
        except ValueError:
            zona.blit(pygame.transform.smoothscale(self._grande, zona.get_size()), (0, 0))

    def _zona_del_juego(self, ancho, alto):
        # La parte de la ventana donde va el lienzo (centrada; lo de alrededor son barras
        # negras). Se arma una vez por ventana: ahi tambien se pintan las barras
        clave = (id(self.superficie), self.superficie.get_size(), ancho, alto)
        if self._zona is None or self._zona[0] != clave:
            self.superficie.fill((0, 0, 0))
            ancho_ventana, alto_ventana = self.superficie.get_size()
            rect = pygame.Rect((ancho_ventana - ancho) // 2, (alto_ventana - alto) // 2, ancho, alto)
            self._zona = (clave, self.superficie.subsurface(rect))
        return self._zona[1]

    def _capa_crt(self, zona, alto_lienzo, escala, brillo):
        # La capa de lineas para este tamaño de ventana (se arma una vez y se guarda): una
        # linea al pie de cada fila de pixeles de arte. Mas gruesa en pantallas grandes
        # (siempre ~1/3 de la fila de arte)
        clave = (self.superficie.get_size(), zona.get_offset(), zona.get_size(), brillo)
        if self._lineas is None or self._lineas[0] != clave:
            capa = pygame.Surface(self.superficie.get_size())
            capa.fill((255, 255, 255))
            grosor = max(1, round(escala * PIXEL_ARTE * 0.3))
            arriba = zona.get_offset()[1]
            for pie in pies_de_las_filas(alto_lienzo, zona.get_height()):
                capa.fill((brillo, brillo, brillo), (0, arriba + pie - grosor + 1, capa.get_width(), grosor))
            self._lineas = (clave, capa)
        return self._lineas[1]


def pies_de_las_filas(alto_lienzo, alto_zona):
    # Para cada fila de pixeles de arte del lienzo, la ultima fila de la ventana donde se
    # ve. Se le pregunta al mismo escalador que dibuja (una tira con cada fila de otro
    # color), asi las lineas calzan siempre, con cualquier escala
    guia = pygame.Surface((1, alto_lienzo))
    for fila in range(alto_lienzo):
        guia.set_at((0, fila), (fila % 256, fila // 256, 0))
    estirada = pygame.transform.scale(guia, (1, alto_zona))
    pies = {}
    for y in range(alto_zona):
        rojo, verde = estirada.get_at((0, y))[:2]
        pies[(rojo + 256 * verde) // PIXEL_ARTE] = y
    return sorted(pies.values())
