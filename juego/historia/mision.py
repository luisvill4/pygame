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
    lugar               donde esta en la galaxia: (x, y) en el mapa de 2400 x 640 (galaxia.py)
    gravedad            años de mas que pasan en la Umbral en cada visita (dilatacion: cerca
                        de un agujero negro el tiempo de Alba va mas lento que el de afuera)
    ambiente            su peligro ambiental, ("calor", 1): para ir hace falta ese modulo (modulos.py)
    plano               el plano de modulo que Ines diseña al cumplirla (asi la historia no se traba)
    tramos              None = la ruta de su sector (rutas.py); o una lista de 4 tramos propia
                        (un tramo puede decir que anomalia trae: "anomalia": "niebla")
    jefe                False = una mision tranquila: termina con el ultimo tramo, sin jefe
    oculta, requisitos  una mision oculta no aparece en el mapa hasta encontrar sus
                        'requisitos' (ids de fragmentos)
    rama_de             (oculta) de que mision sale su camino en el mapa
    antes, despues      el dialogo de antes y de despues: [renglon, ...]
    radio               lo que se dice durante la mision: {momento: [renglon, ...]}
                        momentos: "tramo_1" ... "tramo_4" y "jefe"
    fragmentos          lo que se guarda en el Archivo: [Fragmento(...), ...]
    secretos            como se encuentra cada fragmento: [(tipo, fragmento, {opciones}), ...]
                        (los tipos estan en secretos.py; las opciones, en cada tipo)
    final               True: es el final de la historia (despues de su dialogo, la pantalla final)

Un RENGLON es (quien, texto) o (quien, texto, condicion): la condicion dice que fragmentos
tienen que estar encontrados ("F01"), cuales no ("!F02") o varios a la vez ("F01+!F06"). "T3"
pide que en la Umbral hayan pasado 3 años o mas (tiempo.py), y "!T6" que todavia no.
Asi un dialogo cambia segun lo que encontraste y segun cuanto tardaste.
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


# ---------- Los renglones con condicion ----------

def es_de_tiempo(parte):
    # "T6" (o "!T6"): habla de los años de la Umbral, no de un fragmento
    nombre = parte.lstrip("!")
    return nombre.startswith("T") and nombre[1:].isdigit()


def _vale(parte, encontrados, anios):
    # Una parte de la condicion, sin el "!"
    if es_de_tiempo(parte):
        return anios >= int(parte[1:])
    return parte in encontrados


def se_cumple(condicion, encontrados, anios=0):
    # "F01+!F06+T3": F01 encontrado, F06 no y ya pasaron 3 años. None = siempre
    if not condicion:
        return True
    for parte in condicion.split("+"):
        negada = parte.startswith("!")
        if _vale(parte.lstrip("!"), encontrados, anios) == negada:
            return False
    return True


def ids_de_la_condicion(condicion):
    # Los fragmentos que nombra una condicion (para los tests; sin las de tiempo)
    return [parte.lstrip("!") for parte in condicion.split("+") if not es_de_tiempo(parte)] if condicion else []


def filtrar(renglones, encontrados, anios=0):
    # Los renglones que corresponden a lo encontrado (y a los años), como (quien, texto)
    return [(renglon[0], renglon[1]) for renglon in renglones
            if se_cumple(renglon[2] if len(renglon) > 2 else None, encontrados, anios)]


# ---------- El registro ----------

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


def ids_de_fragmentos():
    return [fragmento.id for fragmento, _ in todos_los_fragmentos()]


def buscar_fragmento(id_):
    for fragmento, _ in todos_los_fragmentos():
        if fragmento.id == id_:
            return fragmento
    raise KeyError("No existe el fragmento " + id_)


class Mision:
    numero = None
    titulo = ""
    sector = 1
    lugar = (0, 0)
    gravedad = 0
    ambiente = None
    plano = None
    tramos = None
    jefe = True
    oculta = False
    requisitos = []
    rama_de = None
    antes = []
    despues = []
    radio = {}
    fragmentos = []
    secretos = []
    final = False

    @classmethod
    def disponible(cls, progreso):
        # La oculta, con sus requisitos encontrados. Las demas: la primera, las cumplidas y
        # la que sigue a una cumplida
        if cls.oculta:
            return all(id_ in progreso.fragmentos for id_ in cls.requisitos)
        return cls.numero == 1 or cls.numero in progreso.misiones or (cls.numero - 1) in progreso.misiones

    @classmethod
    def visible(cls, progreso):
        # ¿Aparece en el mapa? Todas menos la oculta que todavia no se encontro
        return not cls.oculta or cls.disponible(progreso) or cls.numero in progreso.misiones

    @classmethod
    def fragmentos_visibles(cls):
        # Los que el mapa cuenta ("ARCHIVO 1/3"): los ocultos no
        return [fragmento for fragmento in cls.fragmentos if not fragmento.oculto]
