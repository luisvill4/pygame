"""
Secretos: COMO se encuentra cada fragmento del Archivo (el QUE cuenta esta en la mision).

Patron Registry + Template Method (como objetivos.py y desafios.py): cada tipo de secreto
es una clase con @registrar_secreto y escucha los avisos que le importan. Las misiones los
declaran como datos, asi un mismo tipo sirve en cualquier mision:

    secretos = [("moneda_grabada", "F01", {"monedas": 15, "desde_tramo": 2}),
                ("restos", "F02", {"tramo": 3}),
                ("jefe_sin_golpes", "F03")]

(tipo, el fragmento que da, y sus opciones; las que no se ponen usan las de config.py).
Dos opciones sirven para cualquier tipo:
    requiere    fragmentos que tienen que estar encontrados antes (["F03"], o "todos": todos
                los demas del juego). Sin ellos el secreto ni se activa
    pista       lo que se dice por la radio cuando el secreto deja algo en pantalla
                ([(quien, texto), ...]): un "¿y eso?" que ayuda a darse cuenta
El ModoHistoria crea uno nuevo en cada partida (cada uno lleva su cuenta) y le pasa los
avisos. Para un tipo nuevo: una clase aca con su 'tipo', 'preparar(opciones)' y los avisos
que necesite; si deja algo en pantalla, una reliquia (reliquias.py) con self.soltar(...).

Las reglas para que un secreto este bien escrito estan en HISTORIA.md: nunca a simple
vista, todo tiene su porque, se encuentra jugando distinto.
"""
import math

from juego.config import (MONEDA_GRABADA_MONEDAS, RESTOS_ESPERA, BALIZA_ESPERA, COMPAS_UNIDAD, SEGUIR_DISTANCIA,
                          SEGUIR_MINIMO, GOLPE_DESDE_MARGEN, MS_POR_FRAME, VIOLETA)
from juego.historia.reliquias import MonedaGrabada, Restos, Baliza
from juego.historia.mision import ids_de_fragmentos
from juego.historia.glifos import ritmo, escribir
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
        self.requiere = opciones.get("requiere", [])
        self.pista = opciones.get("pista", [])
        self.preparar(opciones)

    def preparar(self, opciones):
        # Para los tipos: leer sus opciones y armar su cuenta
        pass

    @property
    def partida(self):
        return self.modo.partida

    def requisitos(self):
        # Los fragmentos que hacen falta antes ("todos" = todos los demas del juego)
        if self.requiere == "todos":
            return [id_ for id_ in ids_de_fragmentos() if id_ != self.fragmento]
        return self.requiere

    def en_juego(self):
        # ¿Todavia se puede encontrar? (no esta encontrado y estan sus requisitos)
        return (not self.modo.ya_encontrado(self.fragmento)
                and all(self.modo.ya_encontrado(id_) for id_ in self.requisitos()))

    def encontrar(self):
        if self.en_juego():
            self.modo.encontrar(self.fragmento)

    def soltar(self, reliquia):
        # Deja algo en pantalla (cuando lo toques, el modo te da su fragmento) y, si tiene
        # pista, la radio la dice
        self.modo.reliquias.append(reliquia)
        if self.pista:
            self.partida.radio.decir(self.pista, self.partida.tiempo)

    # Avisos (por defecto no hacen nada: cada tipo escucha los suyos)
    def al_empezar_tramo(self, numero):
        pass

    def al_recoger_moneda(self):
        pass

    def al_llegar_jefe(self):
        pass

    def al_vencer_jefe(self, golpes):
        pass

    def al_romper(self, enemigo):
        pass

    def al_romper_parte(self, jefe, parte):
        pass

    def al_golpear_jefe(self, jefe):
        pass

    def al_escapar_moneda(self, ladron):
        pass

    def actualizar(self):
        pass


# ---------- Lo que aparece en pantalla ----------

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
        partida = self.partida
        if partida.director.numero_tramo < self.desde_tramo:
            return
        self.juntadas += 1
        if self.salio or not self.en_juego() or self.juntadas < self.monedas_pedidas:
            return
        self.salio = True
        x, y = lugar_para_moneda(partida)
        self.soltar(MonedaGrabada(self.fragmento, x, y, partida.tiempo))


class AlaDeriva(Secreto):
    # Base de lo que cruza el fondo: en el tramo 'tramo', 'espera' ms despues de empezar,
    # suelta lo suyo (aparecer()). Solo el dash lo abre (ver reliquias.py)
    espera_comun = 0

    def preparar(self, opciones):
        self.tramo = opciones.get("tramo", 3)
        self.espera = opciones.get("espera", self.espera_comun)
        self.cruza_en = None

    def al_empezar_tramo(self, numero):
        if numero == self.tramo and self.en_juego():
            self.cruza_en = self.partida.tiempo + self.espera

    def actualizar(self):
        if self.cruza_en is not None and self.partida.tiempo >= self.cruza_en:
            self.cruza_en = None
            self.soltar(self.aparecer())

    def aparecer(self):
        raise NotImplementedError


@registrar_secreto
class RestosALaDeriva(AlaDeriva):
    # Los restos de una nave que cruzan el fondo
    tipo = "restos"
    espera_comun = RESTOS_ESPERA

    def aparecer(self):
        return Restos(self.fragmento)


@registrar_secreto
class BalizaALaDeriva(AlaDeriva):
    # Una baliza que titila su 'mensaje' (una palabra, en el ritmo de los Cantores)
    tipo = "baliza"
    espera_comun = BALIZA_ESPERA

    def preparar(self, opciones):
        super().preparar(opciones)
        self.mensaje = opciones.get("mensaje", "SOS")

    def aparecer(self):
        return Baliza(self.fragmento, escribir(self.mensaje))


# ---------- Lo que se encuentra jugando distinto ----------

@registrar_secreto
class JefeSinGolpes(Secreto):
    # Vencer al jefe sin haber recibido un golpe en todo el sector
    tipo = "jefe_sin_golpes"

    def al_vencer_jefe(self, golpes):
        if golpes == 0:
            self.encontrar()


@registrar_secreto
class JefeVencido(Secreto):
    # Vencer al jefe (con 'requiere', el premio de haber encontrado lo demas)
    tipo = "jefe_vencido"

    def al_vencer_jefe(self, golpes):
        self.encontrar()


@registrar_secreto
class JefeSinRomper(Secreto):
    # Vencer al jefe sin romper ningun enemigo de un 'tipo' (las abejas de la Colmena: son
    # bibliotecarias, no soldados)
    tipo = "jefe_sin_romper"

    def preparar(self, opciones):
        self.tipo_enemigo = opciones["enemigo"]
        self.rompiste = False

    def al_llegar_jefe(self):
        self.rompiste = False           # (cuenta solo la pelea)

    def al_romper(self, enemigo):
        if enemigo.tipo == self.tipo_enemigo:
            self.rompiste = True

    def al_vencer_jefe(self, golpes):
        if not self.rompiste:
            self.encontrar()


@registrar_secreto
class PartesEnOrden(Secreto):
    # Romper las piezas del jefe en orden, de izquierda a derecha (los cañones del Acorazado:
    # son relojes y un reloj se lee en orden)
    tipo = "partes_en_orden"

    def preparar(self, opciones):
        self.en_orden = True

    def al_llegar_jefe(self):
        self.en_orden = True

    def al_romper_parte(self, jefe, parte):
        # La que se rompe tiene que ser la de mas a la izquierda de las que quedaban
        if any(otra.viva() and otra.dx < parte.dx for otra in jefe.partes):
            self.en_orden = False
        elif self.en_orden and not jefe.partes_vivas():
            self.encontrar()


@registrar_secreto
class RachaDeMonedas(Secreto):
    # Juntar 'monedas' seguidas sin que se corte el combo (con tantas, las monedas "cantan"
    # tan fuerte que la radio capta un eco)
    tipo = "racha"

    def preparar(self, opciones):
        self.monedas = opciones.get("monedas", 20)

    def al_recoger_moneda(self):
        if self.partida.combo >= self.monedas:
            self.encontrar()


@registrar_secreto
class SeguirAlLadron(Secreto):
    # Seguir de cerca a un ladron que se lleva la moneda, sin alcanzarlo, hasta que salga de la
    # pantalla: "seguir las monedas" al pie de la letra. Desde que te acercas tenes que quedarte
    # a menos de 'distancia' px y seguirlo al menos SEGUIR_MINIMO ms
    tipo = "seguir_al_ladron"

    def preparar(self, opciones):
        self.distancia = opciones.get("distancia", SEGUIR_DISTANCIA)
        self.ladron = None          # el que estas siguiendo
        self.desde = None           # desde cuando lo seguis (None: todavia no te acercaste)

    def actualizar(self):
        partida = self.partida
        ladron = partida.moneda.robada_por
        if ladron is not self.ladron:           # otro robo (o ninguno): se empieza de nuevo
            self.ladron, self.desde = ladron, None
        if ladron is None or not self.en_juego():
            return
        nave_x, nave_y = partida.nave.centro()
        ladron_x, ladron_y = ladron.centro()
        cerca = math.hypot(nave_x - ladron_x, nave_y - ladron_y) <= self.distancia
        if cerca and self.desde is None:
            self.desde = partida.tiempo
        elif not cerca and self.desde is not None:
            self.desde = False                  # lo perdiste de vista: este robo ya no sirve

    def al_escapar_moneda(self, ladron):
        if ladron is self.ladron and self.desde not in (None, False):
            if self.partida.tiempo - self.desde >= SEGUIR_MINIMO:
                self.encontrar()


@registrar_secreto
class QuietoEnLaAnomalia(Secreto):
    # Quedarse quieto (sin moverse ni usar el dash) durante una 'anomalia': en el silencio se
    # oye el compas, pulso a pulso (el ritmo de 'mensaje'). Al terminar la palabra, se encuentra.
    # Si te moves, vuelve a empezar
    tipo = "quieto_en_anomalia"

    def preparar(self, opciones):
        self.anomalia = opciones.get("anomalia", "niebla")
        self.pulsos, self.duracion = ritmo(escribir(opciones.get("mensaje", "ALBA")), COMPAS_UNIDAD)
        self.quieto = 0             # ms que llevas quieto

    def actualizar(self):
        partida = self.partida
        anomalia = partida.director.anomalia
        nave = partida.nave
        # Quieta de verdad: sin apretar ninguna direccion (empujar contra un borde no vale)
        quieta = not nave.acelerando and math.hypot(nave.vx, nave.vy) < 0.3 and not nave.en_dash(partida.tiempo)
        if anomalia is None or anomalia.tipo != self.anomalia or not quieta or not self.en_juego():
            self.quieto = 0
            return
        antes = self.quieto
        self.quieto += MS_POR_FRAME
        # Cada pulso del compas suena (corto o largo) y la nave lo siente: un anillo chiquito
        for inicio, _, es_largo in self.pulsos:
            if antes < inicio + 1 <= self.quieto:
                nave_x, nave_y = nave.centro()
                partida.sonidos.reproducir("onda_larga" if es_largo else "onda_corta", nave_x)
                partida.efectos.anillo(nave_x, nave_y, [(40, 20, 70), VIOLETA], 18 if es_largo else 12, 4, 2)
        if self.quieto >= self.duracion:
            self.encontrar()


@registrar_secreto
class GolpeDesde(Secreto):
    # Pegarle al nucleo del jefe desde un lado: 'angulo' en grados, como en el mapa (0 = desde la
    # derecha, 90 = desde abajo, 180 = desde la izquierda, 270 = desde arriba)
    tipo = "golpe_desde"

    def preparar(self, opciones):
        self.angulo = opciones.get("angulo", 180)
        self.margen = opciones.get("margen", GOLPE_DESDE_MARGEN)

    def al_golpear_jefe(self, jefe):
        nave_x, nave_y = self.partida.nave.centro()
        centro_x, centro_y = jefe.centro_nucleo()
        angulo = math.degrees(math.atan2(nave_y - centro_y, nave_x - centro_x)) % 360
        diferencia = abs((angulo - self.angulo + 180) % 360 - 180)
        if diferencia <= self.margen:
            self.encontrar()
