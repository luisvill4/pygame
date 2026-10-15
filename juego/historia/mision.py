"""
La clase base de las misiones del modo historia y su registro.

Patron Registry (como los enemigos y los jefes): cada mision es una clase en su propio
archivo de historia/misiones/, con el decorador @registrar_mision. Para agregar una:
    1. Copiar un archivo de historia/misiones/ (por ejemplo m1_la_senal.py) y cambiar el
       numero, el titulo, el sector y los textos.
    2. Importarlo en historia/misiones/__init__.py.
    3. Escribir su parte en HISTORIA.md (que cuenta y que esconde). Los tests revisan solos
       que los textos entren en sus cajas y que los secretos sean de tipos que existen.

Una mision es casi todo DATOS (atributos de la clase):
    numero, titulo      "MISION 1", "LA SEÑAL"
    sector              el numero de sector donde se juega (1 a 5, ver SECTORES en config.py)
    tramos              None = la ruta de su sector (rutas.py); o una lista de 4 tramos propia
    antes, despues      el dialogo de antes y de despues: [(quien, texto), ...]
    radio               lo que se dice durante la mision: {momento: [(quien, texto), ...]}
                        momentos: "tramo_1" ... "tramo_4" y "jefe"
    fragmentos          lo que se guarda en el Archivo: [Fragmento(...), ...]
    secretos            como se encuentra cada fragmento: [(tipo, fragmento, {opciones}), ...]
                        (los tipos estan en secretos.py; las opciones, en cada tipo)
Los textos van en MAYUSCULAS y sin vocales con tilde (la fuente las dibuja mal).
"""


class Fragmento:
    # Una pieza del Archivo. 'glifo': escrito en el codigo de los Cantores (glifos.py).
    # 'reaccion': lo que se dice por la radio al encontrarlo. 'oculto': ni aparece como "???"
    # en el Archivo hasta encontrarlo
    def __init__(self, id_, nombre, texto, glifo=None, reaccion=(), oculto=False):
        self.id = id_
        self.nombre = nombre
        self.texto = texto          # lista de parrafos
        self.glifo = glifo
        self.reaccion = list(reaccion)
        self.oculto = oculto


TIPOS_MISION = {}           # numero -> clase


def registrar_mision(clase):
    if clase.numero in TIPOS_MISION:
        raise ValueError("Ya hay una mision " + str(clase.numero))
    TIPOS_MISION[clase.numero] = clase
    return clase


def misiones_en_orden():
    return [TIPOS_MISION[numero] for numero in sorted(TIPOS_MISION)]


def mision(numero):
    return TIPOS_MISION[numero]


def todos_los_fragmentos():
    # [(fragmento, mision), ...] en el orden de las misiones (para el Archivo)
    return [(fragmento, clase) for clase in misiones_en_orden() for fragmento in clase.fragmentos]


def buscar_fragmento(id_):
    for fragmento, _ in todos_los_fragmentos():
        if fragmento.id == id_:
            return fragmento
    raise KeyError("No existe el fragmento " + id_)


class Mision:
    numero = None
    titulo = ""
    sector = 1
    tramos = None
    antes = []
    despues = []
    radio = {}
    fragmentos = []
    secretos = []

    @classmethod
    def disponible(cls, progreso):
        # Se puede jugar la primera, las cumplidas y la que sigue a una cumplida
        return cls.numero == 1 or cls.numero in progreso.misiones or (cls.numero - 1) in progreso.misiones

    @classmethod
    def fragmentos_visibles(cls):
        # Los que el mapa cuenta ("ARCHIVO 1/3"): los ocultos no
        return [fragmento for fragmento in cls.fragmentos if not fragmento.oculto]
