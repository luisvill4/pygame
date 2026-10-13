"""
Efectos de sonido y musica.

Si la computadora no tiene placa de audio (o falta un archivo), ese sonido
simplemente no suena: el juego sigue funcionando igual.

Desactivar la musica o los efectos los deja en volumen 0 pero siguen sonando en
silencio, asi la musica retoma donde iba.

Musica: cada escena dice cual quiere (Escena.musica) y la App se la pide a
tocar_musica() en cada paso. Si ya suena esa, no pasa nada; si es otra, la vieja se
apaga de a poco (FUNDIDO_MUSICA) mientras la nueva sube. Hay dos "tocadiscos"
(canales reservados) para que las dos se crucen sin que un efecto les robe el canal.
Los temas menu, jefe y gasolinera los compone herramientas/componer_musica.py.
"""
import pygame

from juego.config import ruta, VOLUMEN_MAX, FUNDIDO_MUSICA

MUSICAS = {
    "juego": "musica.mp3",
    "menu": "musica_menu.ogg",
    "jefe": "musica_jefe.ogg",
    "gasolinera": "musica_gasolinera.ogg",
}
EFECTOS = {
    "game_over": "game_over.wav",
    "moneda": "moneda.wav",
    "golpe": "golpe.wav",
    "powerup": "moneda_brillante.wav",
    "seleccion": "seleccion.wav",
    "nuevo_record": "nuevo_record.wav",
}


_cache = {}     # archivo -> Sound: los temas tardan en abrirse y los tests crean muchas App


def cargar(archivos):
    # {nombre: Sound} con los que se pudieron cargar
    cargados = {}
    for nombre, archivo in archivos.items():
        if archivo not in _cache:
            try:
                _cache[archivo] = pygame.mixer.Sound(ruta("efectos/" + archivo))
            except (pygame.error, FileNotFoundError):
                continue        # sin audio o falta el archivo: ese sonido no suena
        cargados[nombre] = _cache[archivo]
    return cargados


class Sonidos:
    def __init__(self):
        self.sonidos = cargar(EFECTOS)
        self.musicas = cargar(MUSICAS)
        self.actual = None          # el nombre de la musica que suena (None = silencio)
        self.canal = None           # el tocadiscos donde suena
        self.tocadiscos = []
        if pygame.mixer.get_init():
            pygame.mixer.set_reserved(2)        # los canales 0 y 1 son solo para la musica
            self.tocadiscos = [pygame.mixer.Channel(0), pygame.mixer.Channel(1)]

    def reproducir(self, nombre):
        sonido = self.sonidos.get(nombre)
        if sonido is not None:
            sonido.play()

    def tocar_musica(self, nombre):
        # Cambia de tema con un fundido cruzado (si ya suena ese, sigue de largo)
        if nombre == self.actual:
            return
        self.parar_musica()
        self.actual = nombre
        musica = self.musicas.get(nombre)
        if musica is not None and self.tocadiscos:
            # un tocadiscos libre: el otro puede estar todavia apagando el tema viejo
            libres = [canal for canal in self.tocadiscos if not canal.get_busy()]
            self.canal = libres[0] if libres else self.tocadiscos[0]
            self.canal.play(musica, loops=-1, fade_ms=FUNDIDO_MUSICA)

    def parar_musica(self, fundido=FUNDIDO_MUSICA):
        # fundido = 0: corta en seco (al morir)
        if self.canal is not None:
            if fundido:
                self.canal.fadeout(fundido)
            else:
                self.canal.stop()
        self.canal = None
        self.actual = None

    def pausar_todo(self):
        if pygame.mixer.get_init():
            pygame.mixer.pause()

    def reanudar_todo(self):
        if pygame.mixer.get_init():
            pygame.mixer.unpause()

    def aplicar_volumen(self, opciones):
        # set_volume va de 0 a 1; desactivar la musica o los efectos es dejarlos en 0
        nivel = opciones.volumen / VOLUMEN_MAX
        for sonido in self.musicas.values():
            sonido.set_volume(nivel if opciones.musica else 0)
        for sonido in self.sonidos.values():
            sonido.set_volume(nivel if opciones.efectos else 0)
