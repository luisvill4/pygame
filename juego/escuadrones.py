"""
Escuadrones: los enemigos llegan en GRUPOS que entran, atacan y se van.

Como en los juegos de naves (Galaga, 1942, Metal Slug): nada aparece de la nada en el
medio de la pantalla. Primero se ve una flecha en el borde (el aviso), despues el grupo
entra volando en formacion hasta su lugar y recien ahi ataca. Cuando se le termina el
turno, los que quedan se retiran volando. Si los eliminas a todos, hay bonus.

Formaciones (patron Registry, como los enemigos): cada una es una funcion con el
decorador @formacion("nombre") que recibe cuantos son y donde esta la nave, y devuelve
un par (desde, hasta) por enemigo: desde = un punto afuera de la pantalla, hasta = su
lugar adentro. Para agregar una, escribir la funcion; las rutas la usan por su nombre.

Por donde entran: siempre lejos de la nave (por el borde mas lejano), y ninguno termina
de entrar a menos de LEJOS_DE_LA_NAVE px de ella: asi nunca te aparece un enemigo encima.
"""
import math
import random

from juego.config import ANCHO, ALTO

AFUERA = 60             # px afuera del borde desde donde arrancan
ADENTRO = 130           # px adentro del borde hasta donde llegan
SEPARACION = 76         # px entre un miembro y el siguiente de la formacion
ARRIBA, ABAJO = 140, ALTO - 120     # la franja donde se ubican (sin tapar el HUD)
IZQUIERDA, DERECHA = ADENTRO, ANCHO - ADENTRO
LEJOS_DE_LA_NAVE = 170  # px como minimo entre la nave y el lugar donde termina de entrar cada uno

FORMACIONES = {}        # nombre -> funcion


def formacion(nombre):
    # Decorador: anota la funcion en el registro con su nombre
    def anotar(funcion):
        FORMACIONES[nombre] = funcion
        return funcion
    return anotar


def lugares(nombre, cantidad, nave_x, nave_y):
    # Los (desde, hasta) de cada miembro; si alguno quedaria encima de la nave, se corre
    if nombre not in FORMACIONES:
        raise ValueError("No existe la formacion '" + nombre + "'. Hay: " + ", ".join(FORMACIONES))
    return [(desde, _lejos_de_la_nave(hasta, nave_x, nave_y)) for desde, hasta in
            FORMACIONES[nombre](cantidad, nave_x, nave_y)]


def _adentro(x, y):
    return max(IZQUIERDA, min(x, DERECHA)), max(ARRIBA, min(y, ABAJO))


def _lejos_de_la_nave(hasta, nave_x, nave_y):
    # Si el lugar queda muy cerca de la nave, se aleja de ella: primero en linea recta, si
    # no alcanza (la nave esta contra un borde) solo para arriba/abajo y si no a los costados
    hasta_x, hasta_y = hasta
    if math.hypot(hasta_x - nave_x, hasta_y - nave_y) >= LEJOS_DE_LA_NAVE:
        return hasta
    lejos_x, lejos_y = hasta_x - nave_x, hasta_y - nave_y
    largo = math.hypot(lejos_x, lejos_y) or 1
    arriba_o_abajo = 1 if nave_y < (ARRIBA + ABAJO) / 2 else -1
    costado = 1 if nave_x < ANCHO / 2 else -1
    candidatos = [(lejos_x / largo, lejos_y / largo), (0, arriba_o_abajo), (costado, 0)]
    mejor = hasta
    for dir_x, dir_y in candidatos:
        lugar = _adentro(nave_x + dir_x * LEJOS_DE_LA_NAVE, nave_y + dir_y * LEJOS_DE_LA_NAVE)
        if math.hypot(lugar[0] - nave_x, lugar[1] - nave_y) >= LEJOS_DE_LA_NAVE:
            return lugar
        if math.hypot(lugar[0] - nave_x, lugar[1] - nave_y) > math.hypot(mejor[0] - nave_x, mejor[1] - nave_y):
            mejor = lugar
    return mejor


def _repartir(cantidad, centro, desde, hasta):
    # 'cantidad' posiciones separadas SEPARACION alrededor de 'centro', sin salirse de [desde, hasta]
    largo = SEPARACION * (cantidad - 1)
    inicio = max(desde, min(centro - largo / 2, hasta - largo))
    return [inicio + SEPARACION * i for i in range(cantidad)]


def _por_un_costado(cantidad, lado, nave_y):
    # En columna por la izquierda (lado = -1) o por la derecha (1), a la altura de la nave
    # mas o menos (asi la columna "apunta" hacia vos)
    centro_y = nave_y + random.randint(-90, 90)
    desde_x = -AFUERA if lado < 0 else ANCHO + AFUERA
    hasta_x = ADENTRO if lado < 0 else ANCHO - ADENTRO
    return [((desde_x, y), (hasta_x, y)) for y in _repartir(cantidad, centro_y, ARRIBA, ABAJO)]


@formacion("flanco")
def flanco(cantidad, nave_x, nave_y):
    # Todos por el costado mas lejano de la nave
    return _por_un_costado(cantidad, -1 if nave_x > ANCHO / 2 else 1, nave_y)


@formacion("pinza")
def pinza(cantidad, nave_x, nave_y):
    # La mitad por cada costado: te encierran (con uno solo, por el mas lejano)
    if cantidad == 1:
        return flanco(1, nave_x, nave_y)
    izquierda = cantidad // 2
    return _por_un_costado(izquierda, -1, nave_y) + _por_un_costado(cantidad - izquierda, 1, nave_y)


@formacion("lluvia")
def lluvia(cantidad, nave_x, nave_y):
    # En fila por arriba o por abajo (el mas lejano), repartidos a lo ancho
    por_arriba = nave_y > ALTO / 2
    desde_y = -AFUERA if por_arriba else ALTO + AFUERA
    hasta_y = ARRIBA if por_arriba else ABAJO
    centro_x = ANCHO - nave_x                   # del lado contrario a la nave
    columnas = _repartir(cantidad, centro_x, 100, ANCHO - 100)
    return [((x, desde_y), (x, hasta_y)) for x in columnas]


@formacion("esquinas")
def esquinas(cantidad, nave_x, nave_y):
    # Por las esquinas, en diagonal, empezando por la mas lejana de la nave
    todas = [(0, 0), (ANCHO, 0), (0, ALTO), (ANCHO, ALTO)]
    todas.sort(key=lambda esquina: -math.hypot(esquina[0] - nave_x, esquina[1] - nave_y))
    pares = []
    for i in range(cantidad):
        esquina_x, esquina_y = todas[i % 4]
        hacia_x = 1 if esquina_x == 0 else -1
        hacia_y = 1 if esquina_y == 0 else -1
        extra = (i // 4) * 50                   # (con mas de 4, el segundo grupo entra mas adentro)
        desde = (esquina_x - hacia_x * AFUERA, esquina_y - hacia_y * AFUERA)
        hasta = (esquina_x + hacia_x * (ADENTRO + 40 + extra), esquina_y + hacia_y * (ARRIBA if hacia_y > 0 else 120))
        pares.append((desde, hasta))
    return pares


@formacion("cerco")
def cerco(cantidad, nave_x, nave_y):
    # Repartidos alrededor, por los cuatro bordes: te rodean, con un hueco del lado de la
    # nave (por ahi no entra nadie: asi ninguno llega encima tuyo)
    pares = []
    hacia_la_nave = math.atan2(nave_y - ALTO / 2, nave_x - ANCHO / 2) + random.uniform(-0.3, 0.3)
    giro = hacia_la_nave - 2 * math.pi * cantidad / (cantidad + 1)        # el hueco es el lugar que sobra
    for i in range(cantidad):
        angulo = giro + 2 * math.pi * i / (cantidad + 1)        # (+1: queda un hueco)
        dir_x, dir_y = math.cos(angulo), math.sin(angulo)
        # El punto del borde en esa direccion desde el centro de la pantalla
        escala = min(abs((ANCHO / 2) / dir_x) if dir_x else math.inf, abs((ALTO / 2) / dir_y) if dir_y else math.inf)
        borde_x, borde_y = ANCHO / 2 + dir_x * escala, ALTO / 2 + dir_y * escala
        desde = (borde_x + dir_x * AFUERA, borde_y + dir_y * AFUERA)
        hasta = (max(ADENTRO, min(borde_x - dir_x * ADENTRO, ANCHO - ADENTRO)),
                 max(ARRIBA, min(borde_y - dir_y * ADENTRO, ABAJO)))
        pares.append((desde, hasta))
    return pares


class Escuadron:
    # Un grupo de enemigos que llego junto. Lo maneja el Director (progresion.py)

    def __init__(self, tipo, llega_en, retirada_en):
        self.tipo = tipo
        self.miembros = []              # todos los que fueron parte (tambien los hijos del divisor)
        self.llega_en = llega_en        # cuando termina de entrar (partida.tiempo)
        self.retirada_en = retirada_en  # cuando se le termina el turno
        self.se_retiro = False          # ya se dio la orden de retirada
        self.escaparon = 0              # cuantos se fueron sin que los rompas

    def sumar(self, enemigo):
        self.miembros.append(enemigo)
        enemigo.escuadron = self

    def vivos(self, partida):
        return [enemigo for enemigo in self.miembros if enemigo in partida.enemigos]

    def termino(self, partida):
        # Ya no queda ninguno en pantalla
        return not self.vivos(partida)

    def eliminado(self, partida):
        # Los rompiste a todos (ninguno se escapo): para el bonus
        return self.termino(partida) and self.escaparon == 0 and not self.se_retiro

    def retirarse(self, partida):
        # Se le termino el turno: los que quedan se van volando
        self.se_retiro = True
        for enemigo in self.vivos(partida):
            enemigo.retirarse(partida)
