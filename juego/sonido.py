"""
Efectos de sonido y musica.

Si la computadora no tiene placa de audio (o falta un archivo), ese sonido
simplemente no suena: el juego sigue funcionando igual.

Desactivar la musica o los efectos los deja en volumen 0 pero siguen sonando en
silencio, asi la musica retoma donde iba.
"""
import pygame

from juego.config import ruta, VOLUMEN_MAX

MUSICA = "musica"
ARCHIVOS = {
    MUSICA: "musica.mp3",
    "game_over": "game_over.wav",
    "moneda": "moneda.wav",
    "golpe": "golpe.wav",
    "powerup": "moneda_brillante.wav",
    "seleccion": "seleccion.wav",
    "nuevo_record": "nuevo_record.wav",
}


class Sonidos:
    def __init__(self):
        self.sonidos = {}
        for nombre, archivo in ARCHIVOS.items():
            try:
                self.sonidos[nombre] = pygame.mixer.Sound(ruta("efectos/" + archivo))
            except (pygame.error, FileNotFoundError):
                pass        # sin audio o falta el archivo: ese sonido no suena

    def reproducir(self, nombre):
        sonido = self.sonidos.get(nombre)
        if sonido is not None:
            sonido.play()

    def empezar_musica(self):
        musica = self.sonidos.get(MUSICA)
        if musica is not None:
            musica.play(-1)

    def parar_musica(self):
        musica = self.sonidos.get(MUSICA)
        if musica is not None:
            musica.stop()

    def pausar_todo(self):
        if pygame.mixer.get_init():
            pygame.mixer.pause()

    def reanudar_todo(self):
        if pygame.mixer.get_init():
            pygame.mixer.unpause()

    def aplicar_volumen(self, opciones):
        # set_volume va de 0 a 1; desactivar la musica o los efectos es dejarlos en 0
        nivel = opciones.volumen / VOLUMEN_MAX
        for nombre, sonido in self.sonidos.items():
            if nombre == MUSICA:
                activo = opciones.musica
            else:
                activo = opciones.efectos
            sonido.set_volume(nivel if activo else 0)
