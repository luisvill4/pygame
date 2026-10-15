"""
Objetivos: lo que pide cada tramo para pasar al siguiente (como las misiones de Metal Slug).

Cada tramo de la ruta (rutas.py) trae su objetivo, ligado a la idea del tramo: en
BLANCO FACIL hay que romper divisores, en CARGA frenar embestidas, en el ASEDIO aguantar.
Al cumplirlo, los enemigos que quedan se retiran y, con la zona despejada, empieza el
tramo siguiente. Los objetivos no se fallan: si algo se escapa, llega otro escuadron.

Por que objetivos y no una barra de energia: con la barra, al llenarse, el tramo se
"apuraba" y los enemigos se iban apenas llegaban. Con un objetivo, los escuadrones se
quedan su turno entero y el tramo termina cuando hiciste lo que pedia.

Patron Registry + Template Method (como desafios.py): cada tipo es una clase con
@registrar_objetivo; la Partida y el Director le pasan lo que pasa (al_recoger_moneda,
al_romper, al_interceptar...) y cada tipo escucha solo los avisos que le importan.

En el guion se escriben como una tupla: ("monedas", 10), ("romper", 3, "divisor"),
("interceptar", 2), ("perfectos", 6) o ("asedio",).
"""
from juego.config import ASEDIO_DURACION
from juego.enemigos import TIPOS_ENEMIGO

TIPOS_OBJETIVO = {}         # nombre -> clase


def registrar_objetivo(clase):
    TIPOS_OBJETIVO[clase.tipo] = clase
    return clase


def crear_objetivo(datos, factor=1):
    # datos = ("romper", 3, "divisor"): tipo, meta y (si hace falta) que enemigo. 'factor'
    # agranda la meta (en la segunda vuelta a los sectores se pide mas)
    tipo, *resto = datos
    clase = TIPOS_OBJETIVO[tipo]
    meta = max(1, round(resto[0] * factor)) if resto else 1
    enemigo = resto[1] if len(resto) > 1 else None
    return clase(meta, enemigo)


class Objetivo:
    tipo = None

    def __init__(self, meta, enemigo=None):
        self.meta = meta
        self.enemigo = enemigo      # el tipo de enemigo que pide (solo "romper")
        self.progreso = 0

    def cumplido(self):
        return self.progreso >= self.meta

    def sumar(self, cantidad=1):
        self.progreso = min(self.meta, self.progreso + cantidad)

    def fraccion(self, partida):
        # Cuanto va, de 0 a 1 (el camino de la ruta en el HUD)
        return self.progreso / self.meta

    def texto(self):
        # Lo que dice el cartel del tramo: "ROMPE 3 DIVISORES"
        raise NotImplementedError

    def etiqueta(self):
        # Corto, para el HUD: "DIVISORES 2/3"
        raise NotImplementedError

    # Avisos (por defecto no hacen nada: cada tipo escucha los suyos)
    def al_recoger_moneda(self, combo):
        pass

    def al_romper(self, enemigo):
        pass

    def al_interceptar(self):
        pass

    def al_perfecto(self):
        pass

    def al_terminar_asedio(self):
        pass


@registrar_objetivo
class JuntarMonedas(Objetivo):
    tipo = "monedas"

    def texto(self):
        return "JUNTA %d MONEDAS" % self.meta

    def etiqueta(self):
        return "MONEDAS %d/%d" % (self.progreso, self.meta)

    def al_recoger_moneda(self, combo):
        self.sumar()


@registrar_objetivo
class Romper(Objetivo):
    tipo = "romper"

    def plural(self):
        return TIPOS_ENEMIGO[self.enemigo].plural if self.enemigo else "ENEMIGOS"

    def texto(self):
        return "ROMPE %d %s" % (self.meta, self.plural())

    def etiqueta(self):
        return "%s %d/%d" % (self.plural(), self.progreso, self.meta)

    def al_romper(self, enemigo):
        # Solo cuenta el tipo exacto: romper un divisor grande es uno (sus hijos son otro tipo)
        if self.enemigo is None or enemigo.tipo == self.enemigo:
            self.sumar()


@registrar_objetivo
class Interceptar(Objetivo):
    tipo = "interceptar"

    def texto(self):
        return "FRENA %d EMBESTIDAS" % self.meta

    def etiqueta(self):
        return "EMBESTIDAS %d/%d" % (self.progreso, self.meta)

    def al_interceptar(self):
        self.sumar()


@registrar_objetivo
class Perfectos(Objetivo):
    tipo = "perfectos"

    def texto(self):
        return "LOGRA %d DASH PERFECTOS" % self.meta

    def etiqueta(self):
        return "PERFECTOS %d/%d" % (self.progreso, self.meta)

    def al_perfecto(self):
        self.sumar()


@registrar_objetivo
class AguantarElAsedio(Objetivo):
    tipo = "asedio"

    def texto(self):
        return "AGUANTA: DESPUES LLEGA EL JEFE"

    def etiqueta(self):
        return "ASEDIO"

    def fraccion(self, partida):
        # Lo que va del asedio (el tiempo es el progreso)
        director = partida.director
        if self.cumplido() or not director.en_asedio:
            return 1 if self.cumplido() else 0
        return 1 - director.restante_asedio() / ASEDIO_DURACION

    def al_terminar_asedio(self):
        self.sumar()
