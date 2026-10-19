"""
La radio del modo historia: mensajes cortos abajo de la pantalla que NO pausan el juego
(como en Star Fox). Alba e Ines hablan mientras juegas.

Salen de a uno, en una cola (el mismo patron que los avisos de arriba, avisos.py). Cada
mensaje se ve un rato que depende de lo largo que es. Aqui esta solo la logica (cuando
empieza y termina cada uno, con partida.tiempo); como se ve lo dibuja carteles.radio().
"""
from juego import accesibilidad
from juego.config import RADIO_MS_MINIMO, RADIO_MS_POR_LETRA


class Mensaje:
    def __init__(self, personaje, texto, no_antes_de):
        self.personaje = personaje      # clave de historia.PERSONAJES ("alba", "ines"...)
        self.texto = texto
        self.no_antes_de = no_antes_de  # no sale antes de este momento (para que no pise un cartel)
        self.desde = None
        self.hasta = None

    def duracion(self):
        # (con TEXTO LENTO dura mas: hay quien lee mas despacio)
        return max(RADIO_MS_MINIMO, len(self.texto) * RADIO_MS_POR_LETRA) * accesibilidad.factor_lectura()


class Radio:
    def __init__(self):
        self.actual = None
        self.esperando = []

    def decir(self, renglones, ahora, demora=0):
        # renglones = [(personaje, texto), ...]: salen uno detras de otro
        for personaje, texto in renglones:
            self.esperando.append(Mensaje(personaje, texto, ahora + demora))

    def actualizar(self, ahora):
        # Devuelve el mensaje que acaba de empezar (para que suene el "clic"), o None
        if self.actual is not None and ahora >= self.actual.hasta:
            self.actual = None
        if self.actual is None and self.esperando and ahora >= self.esperando[0].no_antes_de:
            self.actual = self.esperando.pop(0)
            self.actual.desde = ahora
            self.actual.hasta = ahora + self.actual.duracion()
            return self.actual
        return None

    def vaciar(self):
        self.actual = None
        self.esperando = []
