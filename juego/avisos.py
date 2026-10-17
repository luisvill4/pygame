"""
Avisos: los carteles de la franja de arriba ("TRAMO 2/4", "¡ASEDIO SUPERADO!", una anomalia...).

Salen de a UNO, en una cola (el patron Cola o "Queue": el primero que llega es el primero
que sale). El que llega mientras se ve otro espera su turno, asi nunca se pisan (antes
"¡OLEADA!" y "NIVEL 2" salian uno encima del otro).
Los urgentes (una amenaza: una anomalia, la ultima vida) no esperan: el que se esta viendo se
va enseguida y el urgente pasa primero.

Aqui esta solo la logica (cuando empieza y cuando termina cada uno, con partida.tiempo):
como se ve lo dibuja carteles.pancarta().
"""

SALIDA_RAPIDA = 200     # ms que tarda en irse un aviso cuando llega uno urgente


class Aviso:
    def __init__(self, etiqueta, titulo, subtitulo, color, duracion, alerta=False):
        self.etiqueta = etiqueta    # la categoria, en una pestañita arriba ("ALERTA", "ANOMALIA"...)
        self.titulo = titulo
        self.subtitulo = subtitulo
        self.color = color          # None = arcoiris (para festejar)
        self.duracion = duracion    # ms
        self.alerta = alerta        # True = lleva cinta de peligro (es una amenaza)
        self.desde = None           # cuando empezo a verse (lo pone la cola)
        self.hasta = None

    def empezar(self, ahora):
        self.desde = ahora
        self.hasta = ahora + self.duracion

    def cortar(self, ahora):
        # Que se vaya ya, con su animacion de salida (si ya se estaba yendo, no cambia)
        self.hasta = min(self.hasta, ahora + SALIDA_RAPIDA)


class ColaDeAvisos:
    def __init__(self):
        self.actual = None          # el que se esta viendo
        self.esperando = []         # los que esperan su turno, en orden

    def agregar(self, aviso, ahora, urgente=False):
        if urgente:
            self.esperando.insert(0, aviso)         # se cuela adelante de todos...
            if self.actual is not None:
                self.actual.cortar(ahora)           # ...y el que se ve se va
        else:
            self.esperando.append(aviso)            # a la fila
        self.actualizar(ahora)                      # si no se veia nada, sale ya

    def actualizar(self, ahora):
        # Cada paso: si el actual termino, pasa el siguiente
        if self.actual is not None and ahora >= self.actual.hasta:
            self.actual = None
        if self.actual is None and self.esperando:
            self.actual = self.esperando.pop(0)
            self.actual.empezar(ahora)

    def vaciar(self):
        # Llega el jefe: su presentacion ocupa la pantalla y lo pendiente ya no importa
        self.actual = None
        self.esperando.clear()
