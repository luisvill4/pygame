"""
Secretos: COMO se encuentra cada fragmento del Archivo (el QUE cuenta esta en la mision).

Patron Registry + Template Method (como objetivos.py y desafios.py): cada tipo de secreto
es una clase con @registrar_secreto y escucha los avisos que le importan. Las misiones los
declaran como datos, asi un mismo tipo sirve en cualquier mision:

    secretos = [("moneda_grabada", "F01", {"monedas": 15, "desde_tramo": 2}),
                ("restos", "F02", {"tramo": 3}),
                ("jefe_sin_golpes", "F03")]

(tipo, el fragmento que da, y sus opciones; las que no se ponen usan las de config.py).
El ModoHistoria crea uno nuevo en cada partida (cada uno lleva su cuenta) y le pasa los
avisos. Para un tipo nuevo: una clase aca con su 'tipo', 'preparar(opciones)' y los avisos
que necesite; si deja algo en pantalla, una reliquia (reliquias.py) con self.soltar(...).

Las reglas para que un secreto este bien escrito estan en HISTORIA.md: nunca a simple
vista, todo tiene su porque, se encuentra jugando distinto.
"""
from juego.config import MONEDA_GRABADA_MONEDAS, RESTOS_ESPERA
from juego.historia.reliquias import MonedaGrabada, Restos
from juego.moneda import lugar_para_moneda

TIPOS_SECRETO = {}          # nombre -> clase


def registrar_secreto(clase):
    TIPOS_SECRETO[clase.tipo] = clase
    return clase


def crear_secreto(datos, modo):
    # datos = (tipo, fragmento) o (tipo, fragmento, {opciones})
    tipo, fragmento, *resto = datos
    if tipo not in TIPOS_SECRETO:
        raise ValueError("No existe el secreto '" + tipo + "'. Hay: " + ", ".join(TIPOS_SECRETO))
    return TIPOS_SECRETO[tipo](modo, fragmento, resto[0] if resto else {})


class Secreto:
    tipo = None

    def __init__(self, modo, fragmento, opciones):
        self.modo = modo            # el ModoHistoria de esta partida
        self.fragmento = fragmento  # el id del fragmento que da ("F01")
        self.preparar(opciones)

    def preparar(self, opciones):
        # Para los tipos: leer sus opciones y armar su cuenta
        pass

    @property
    def partida(self):
        return self.modo.partida

    def encontrado(self):
        return self.modo.ya_encontrado(self.fragmento)

    def encontrar(self):
        self.modo.encontrar(self.fragmento)

    def soltar(self, reliquia):
        # Deja algo en pantalla (cuando lo toques, el modo te da su fragmento)
        self.modo.reliquias.append(reliquia)

    # Avisos (por defecto no hacen nada: cada tipo escucha los suyos)
    def al_empezar_tramo(self, numero):
        pass

    def al_recoger_moneda(self):
        pass

    def al_llegar_jefe(self):
        pass

    def al_vencer_jefe(self, golpes):
        pass

    def actualizar(self):
        pass


@registrar_secreto
class MonedaGrabadaEscondida(Secreto):
    # Una vez por partida, despues de juntar 'monedas' y desde el tramo 'desde_tramo', aparece una
    # moneda distinta en otro lugar que la comun. Si no la agarras a tiempo, se apaga
    tipo = "moneda_grabada"

    def preparar(self, opciones):
        self.monedas_pedidas = opciones.get("monedas", MONEDA_GRABADA_MONEDAS)
        self.desde_tramo = opciones.get("desde_tramo", 2)
        self.juntadas = 0
        self.salio = False

    def al_recoger_moneda(self):
        self.juntadas += 1
        partida = self.partida
        if (self.salio or self.encontrado() or self.juntadas < self.monedas_pedidas
                or partida.director.numero_tramo < self.desde_tramo):
            return
        self.salio = True
        x, y = lugar_para_moneda(partida)
        self.soltar(MonedaGrabada(self.fragmento, x, y, partida.tiempo))


@registrar_secreto
class RestosALaDeriva(Secreto):
    # En el tramo 'tramo', 'espera' ms despues de empezar, unos restos cruzan el fondo. Solo el
    # dash los abre (ver reliquias.Restos)
    tipo = "restos"

    def preparar(self, opciones):
        self.tramo = opciones.get("tramo", 3)
        self.espera = opciones.get("espera", RESTOS_ESPERA)
        self.cruzan_en = None

    def al_empezar_tramo(self, numero):
        if numero == self.tramo and not self.encontrado():
            self.cruzan_en = self.partida.tiempo + self.espera

    def actualizar(self):
        if self.cruzan_en is not None and self.partida.tiempo >= self.cruzan_en:
            self.cruzan_en = None
            self.soltar(Restos(self.fragmento))


@registrar_secreto
class JefeSinGolpes(Secreto):
    # Vencer al jefe sin haber recibido un golpe en todo el sector
    tipo = "jefe_sin_golpes"

    def al_vencer_jefe(self, golpes):
        if golpes == 0:
            self.encontrar()
