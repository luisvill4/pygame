"""
Pantalla de inicio: titulo, un panel que va cambiando y el menu JUGAR / LOGROS / OPCIONES.

El panel muestra una pagina cada PAGINA_MS: como se juega, los power-ups y (si hay)
los mejores puntajes. Unos puntitos abajo del panel dicen en que pagina esta.
"""
import math

import pygame

from juego import dibujo, nave
from juego.dibujo import texto, MINI, CHICA, MEDIA, TITULO
from juego.config import ROJO, BLANCO, AMARILLO, MAGENTA, CIAN, GRIS, MS_CUADRO_ENEMIGO
from juego.entrada import ACEPTAR, IZQUIERDA, DERECHA
from juego.escenas.base import Escena
from juego.escenas.opciones import Opciones
from juego.escenas.dificultad import Dificultad
from juego.escenas.logros import Logros
from juego.enemigos import TIPOS_ENEMIGO
from juego.moneda import imagen_moneda
from juego.powerups import TIPOS_POWERUP
from juego.logros import LOGROS
from juego import recursos

MENU = ["JUGAR", "LOGROS", "OPCIONES"]
PAGINA_MS = 5000            # cada cuanto cambia la pagina del panel


def altura_nave():
    # La nave flota en el titulo (se mueve de a 3 pixeles, estilo retro)
    return 250 + round(math.sin(pygame.time.get_ticks() / 300) * 2) * 3


class Inicio(Escena):
    def __init__(self, app):
        super().__init__(app)
        self.opcion = 0         # elegida en MENU

    def actualizar(self, entrada):
        self.mover_fondo()
        self.app.efectos.estela(400, altura_nave(), 0)
        self.app.efectos.actualizar()

        if entrada.pulso(IZQUIERDA):
            self.opcion = (self.opcion - 1) % len(MENU)
        elif entrada.pulso(DERECHA):
            self.opcion = (self.opcion + 1) % len(MENU)
        if entrada.pulso(ACEPTAR):
            self.app.sonidos.reproducir("seleccion")
            elegida = MENU[self.opcion]
            if elegida == "JUGAR":
                self.app.cambiar_escena(Dificultad(self.app, volver_a=self))
            elif elegida == "LOGROS":
                self.app.cambiar_escena(Logros(self.app, volver_a=self))
            else:
                self.app.cambiar_escena(Opciones(self.app, volver_a=self))

    # ---------- Dibujo ----------

    def paginas(self):
        # Las paginas del panel (los records solo si hay alguno)
        paginas = [self._dibujar_como_se_juega, self._dibujar_powerups]
        if self.app.records.filas(self.app.opciones.dificultad):
            paginas.append(self._dibujar_records)
        return paginas

    def dibujar(self, pantalla_completa):
        # Fondo en todo el ancho; el menu en la zona central de 800x600
        self.dibujar_fondo(pantalla_completa)
        pantalla = dibujo.zona_central(pantalla_completa)

        # Record arriba, como en las maquinas, y los logros al costado
        texto(pantalla, "RECORD", CHICA, ROJO, 400, 22)
        dificultad = self.app.opciones.dificultad
        texto(pantalla, dibujo.numero_arcade(self.app.records.maximo(dificultad)), CHICA, BLANCO, 400, 46)
        hechos = sum(1 for logro in LOGROS if logro.id in self.app.progreso.logros)
        texto(pantalla, "LOGROS " + str(hechos) + "/" + str(len(LOGROS)), MINI, GRIS, 780, 22, alinear="derecha")

        # Titulo con relieve y la nave flotando
        dibujo.texto_3d(pantalla, "CAZA", TITULO, AMARILLO, MAGENTA, 115)
        dibujo.texto_3d(pantalla, "MONEDAS", TITULO, AMARILLO, MAGENTA, 180)
        self.app.efectos.dibujar(pantalla)
        imagen_nave = nave.imagen("nave")
        pantalla.blit(imagen_nave, imagen_nave.get_rect(center=(400, altura_nave())))

        # Panel con la pagina actual y los puntitos de las paginas
        dibujo.marco(pantalla, pygame.Rect(170, 290, 460, 180), CIAN)
        paginas = self.paginas()
        actual = pygame.time.get_ticks() // PAGINA_MS % len(paginas)
        paginas[actual](pantalla)
        for i in range(len(paginas)):
            punto = pygame.Rect(400 - len(paginas) * 8 + i * 16 + 4, 450, 8, 8)
            pantalla.fill(CIAN if i == actual else (40, 60, 80), punto)

        # Menu (se elige con izquierda y derecha)
        for i, nombre in enumerate(MENU):
            dibujo.opcion(pantalla, nombre, MEDIA, 200 + i * 200, 530, i == self.opcion)
        texto(pantalla, self.app.entrada.ayuda("FLECHAS MOVER  ESPACIO DASH  P PAUSA",
                                               "STICK MOVER  X DASH  MENU PAUSA"), CHICA, GRIS, 400, 572)
        dibujo.efecto_crt(pantalla_completa)

    def _dibujar_como_se_juega(self, pantalla):
        moneda = imagen_moneda()
        pantalla.blit(moneda, moneda.get_rect(center=(220, 322)))
        texto(pantalla, "RECOGE", CHICA, BLANCO, 255, 322, alinear="izquierda")
        texto(pantalla, "+1 PUNTO", CHICA, AMARILLO, 600, 322, alinear="derecha")
        enemigo = recursos.cuadro_animado(TIPOS_ENEMIGO["perseguidor"].cuadros(), MS_CUADRO_ENEMIGO)
        pantalla.blit(enemigo, enemigo.get_rect(center=(220, 362)))
        texto(pantalla, "ESQUIVA", CHICA, BLANCO, 255, 362, alinear="izquierda")
        texto(pantalla, "-1 VIDA", CHICA, ROJO, 600, 362, alinear="derecha")
        # El dash: la nave cruzando con su estela cian
        fantasma = pygame.transform.rotate(pygame.transform.scale(nave.imagen("fantasma"), (30, 30)), -90)
        for i in range(3):
            fantasma.set_alpha(80 + i * 80)
            pantalla.blit(fantasma, fantasma.get_rect(center=(196 + i * 12, 402)))
        texto(pantalla, "ATRAVESA", CHICA, BLANCO, 255, 402, alinear="izquierda")
        texto(pantalla, "CON DASH", CHICA, CIAN, 600, 402, alinear="derecha")
        texto(pantalla, "CADA SECTOR: UN JEFE Y UNA MEJORA", MINI, GRIS, 400, 434)
        texto(pantalla, "¡PERFECTO! EL DASH SE RECARGA YA", CHICA, CIAN, 400, 492)

    def _dibujar_powerups(self, pantalla):
        # Capsulas; una a la vez se explica abajo (cambia cada segundo)
        texto(pantalla, "POWER-UPS", CHICA, CIAN, 400, 318)
        powerups = list(TIPOS_POWERUP.values())
        explicado = powerups[pygame.time.get_ticks() // 1000 % len(powerups)]
        separacion = min(60, 420 // len(powerups))      # si hay muchos, se juntan para entrar en el panel
        primera_x = 400 - separacion * (len(powerups) - 1) // 2
        for i, powerup in enumerate(powerups):
            capsula_x = primera_x + i * separacion
            powerup.dibujar_capsula(pantalla, capsula_x, 382)
            if powerup is explicado:
                pygame.draw.polygon(pantalla, powerup.color,
                                    [(capsula_x - 6, 356), (capsula_x + 6, 356), (capsula_x, 362)])
        texto(pantalla, explicado.nombre, MEDIA, explicado.color, 400, 428)
        texto(pantalla, explicado.descripcion, CHICA, explicado.color, 400, 492)

    def _dibujar_records(self, pantalla):
        dificultad = self.app.opciones.dificultad
        dibujo.tabla_records(pantalla, self.app.records.filas(dificultad), 315, titulo="MEJORES - " + dificultad)
