"""
Sonido: el "mezclador" del juego (efectos, musica, ambiente y loops).

Si la computadora no tiene placa de audio (o falta un archivo), ese sonido simplemente
no suena: el juego sigue funcionando igual.

Como un mezclador profesional, cada efecto del CATALOGO (patron Registry) tiene su ficha
(un Efecto) que dice:
- categoria: INTERFAZ, EFECTOS o AMBIENTE. Cada una tiene su volumen (Opciones y MEZCLA).
- prioridad: DETALLE < ACCION < PELIGRO < MOMENTO. Si todos los canales estan ocupados,
  un sonido nuevo le "roba" el canal al menos importante; uno menos importante no suena.
- voces: cuantos del mismo pueden sonar a la vez. Si se pide uno mas, corta al mas viejo
  (asi diez monedas seguidas no se amontonan en un ruido).
- enfriamiento: ms minimos entre dos iguales (para lo que puede pasar muchas veces juntas).
- variantes: varios archivos; se turnan sin repetir el anterior (no suena "a maquina").
- paneo: si suena del lado donde paso la cosa (reproducir(nombre, x)).
Los efectos de prioridad MOMENTO ademas bajan la musica mientras suenan (ducking): la
fanfarria se oye clara sin subir el volumen de todo.

Efectos ARMONICOS (la moneda, los premios, los power-ups, la interfaz): siguen al acorde de
la musica, como en Rez o Tetris Effect. El estudio compone cada uno una vez por COLOR (la
pentatonica de cada acorde: moneda_1_fa.ogg...) y la ficha de cada tema dice el color de
cada compas. El mezclador sabe cuando empezo el tema (descontando las pausas), calcula en
que compas va y toca el archivo de ese color (color_actual). Sin musica, el de Do.

Musica y ambiente: cada uno tiene un Tocadiscos (dos canales reservados) que pasa de un
tema a otro con un fundido cruzado. Cada escena dice que musica quiere (Escena.musica) y
la App se la pide a tocar_musica() en cada paso: si ya suena esa, no pasa nada.

Canales: 0-1 musica, 2-3 ambiente, 4-5 loops (sonidos que se repiten hasta que se los
para: un laser, una sirena) y del 6 en adelante los efectos.

El limitador: pygame suma todos los canales y lo que se pasa del maximo se recorta (suena
"saturado"). Por eso el mezclador lleva la cuenta de cuanto suena cada efecto en cada
momento (la "envolvente" de su ficha, en efectos/fichas.json, que escribe el estudio) y,
si la suma con la musica se pasaria de TECHO_MEZCLA, baja los efectos: primero los poco
importantes (DETALLE y ACCION, hasta PISO_DETALLES) y, si no alcanza, todos. Cuando se
despeja, vuelven de a poco (RECUPERACION_MEZCLA). Es lo que hace un compresor en el bus de
efectos de una consola, pero sabiendo de antemano lo que va a sonar.

Para agregar un efecto: poner el archivo en efectos/ y una linea en CATALOGO. Despues,
sonidos.reproducir("nombre") (o con la x) donde pase la cosa, en la logica.
"""
import json
import math
import random

import pygame

from juego.config import (ruta, ANCHO, VOLUMEN_MAX, FUNDIDO_MUSICA, FUNDIDO_AMBIENTE, CANALES_AUDIO, MEZCLA,
                          PANEO_MINIMO, ATENUAR_MUSICA, ATENUAR_VUELTA, TECHO_MEZCLA, PISO_DETALLES,
                          RECUPERACION_MEZCLA, ADELANTO_ACORDE)

# Categorias (cada una con su volumen)
MUSICA, EFECTOS, INTERFAZ, AMBIENTE = "MUSICA", "EFECTOS", "INTERFAZ", "AMBIENTE"
# Prioridades: si no hay canal libre, el mas importante le gana el lugar al menos importante
DETALLE, ACCION, PELIGRO, MOMENTO = 1, 2, 3, 4

CANALES_MUSICA = (0, 1)
CANALES_AMBIENTE = (2, 3)
CANALES_LOOP = (4, 5)
PRIMER_CANAL_EFECTOS = 6


# Los colores de la armonia (la pentatonica de cada acorde: herramientas/estudio/armonia.py,
# que tiene los mismos) y el que suena sin musica
COLORES = ["do", "reb", "re7", "mi", "mi7", "misus", "fa", "sol", "la", "sib", "do7"]
COLOR_SIN_MUSICA = "do"


def _familia(prefijo, cuantos):
    return ["%s_%d" % (prefijo, numero) for numero in range(1, cuantos + 1)]


# Los efectos que siguen al acorde (los mismos que ARMONICOS en herramientas/estudio/obras:
# un test comprueba que coincidan). Cada uno tiene un archivo por color
ARMONICOS = set(
    _familia("moneda", 5) + _familia("combo_sube", 3) + _familia("perfecto", 5) + _familia("roce_carga", 6)
    + _familia("hielo_roto", 3) + _familia("enemigo_roto", 3) + _familia("ui_mover", 2) + _familia("carta", 6)
    + _familia("contador", 8) + _familia("dificultad", 4)
    + ["oro_brillo", "combo_max", "interceptado", "nivel", "dash_listo", "nave_dash_extra", "capsula",
       "pw_escudo", "pw_hielo", "pw_vida", "pw_iman", "pw_doble", "pw_turbo", "pw_recarga", "pw_nova",
       "mejora_elegida", "eco", "bonus", "aturdido", "vulnerable", "desafio_nuevo", "desafio_cumplido",
       "oleada_superada", "logro", "nave_nueva", "bala_rota", "aparece", "retirada", "oro_llega",
       "ui_aceptar", "ui_volver", "ui_pestana", "ui_valor_sube", "ui_valor_baja", "ui_llave_si", "ui_llave_no",
       "carta_rara", "hangar_nave", "contador_fin", "taller",
       # los que se repiten todo el tiempo (y su tension la da el ritmo, no las notas)
       "compas", "compas_acento", "combo_cortado", "mina_tic", "pw_acaba", "pw_fin", "dash_vacio",
       "enjambre_picada"] + _familia("rebote", 4))


def archivo_de_color(archivo, color):
    # "moneda_1.wav" -> "moneda_1_fa.ogg"
    return "%s_%s.ogg" % (archivo.rsplit(".", 1)[0], color)


class Efecto:
    # La ficha de un sonido del catalogo
    def __init__(self, archivos, categoria=EFECTOS, prioridad=ACCION, voces=2, enfriamiento=0, volumen=1.0,
                 paneo=True):
        variantes = [archivos] if isinstance(archivos, str) else list(archivos)    # uno por variante
        # Armonico si sus variantes son de ARMONICOS: entonces cada variante tiene un archivo
        # por color ({color: [archivo de cada variante]})
        self.armonico = all(variante.rsplit(".", 1)[0] in ARMONICOS for variante in variantes)
        if self.armonico:
            self.por_color = {color: [archivo_de_color(v, color) for v in variantes] for color in COLORES}
            self.archivos = [archivo for lista in self.por_color.values() for archivo in lista]
        else:
            self.por_color = None
            self.archivos = variantes
        self.categoria = categoria
        self.prioridad = prioridad
        self.voces = voces
        self.enfriamiento = enfriamiento    # ms
        self.volumen = volumen              # relativo a su categoria (para equilibrar uno solo)
        self.paneo = paneo                  # False: siempre al centro (la interfaz, los momentos)


# Los temas de musica (nombre -> archivo). "juego" (y sus colores), "tension", "iniciales" y
# "fin" salen del estudio (herramientas/componer.py); "menu", "jefe" (y los de cada jefe) y
# "gasolinera", del compositor viejo (herramientas/componer_musica.py). Una escena que pide SILENCIO deja todo callado (con fundido)
MUSICAS = {
    "juego": "musica_juego.ogg",
    "menu": "musica_menu.ogg",
    "jefe": "musica_jefe.ogg",
    "gasolinera": "musica_gasolinera.ogg",
    "iniciales": "musica_iniciales.ogg",
    "fin": "musica_fin.ogg",
    # "Neon en ruta" con el color de cada sector (el 1, el Cinturon, es "juego")
    "juego_2": "musica_juego_2.ogg",
    "juego_3": "musica_juego_3.ogg",
    "juego_4": "musica_juego_4.ogg",
    "juego_5": "musica_juego_5.ogg",
    "tension": "musica_tension.ogg",       # el nivel antes del jefe
    # Un tema para cada jefe, en el estilo de musica_jefe (el del Ojo); del compositor viejo
    "jefe_fortaleza": "musica_jefe_fortaleza.ogg",
    "jefe_serpiente": "musica_jefe_serpiente.ogg",
    "jefe_colmena": "musica_jefe_colmena.ogg",
    "jefe_singularidad": "musica_jefe_singularidad.ogg",
}
SILENCIO = "silencio"

# El ambiente de cada sector (el "ambiente" de config.SECTORES -> archivo): loops de 24 s,
# muy bajitos, que se cruzan con fundido al cambiar de sector
AMBIENTES = {
    "asteroides": "amb_cinturon.ogg",
    "brasas": "amb_carmesi.ogg",
    "esporas": "amb_esmeralda.ogg",
    "panal": "amb_ambar.ogg",
    "abismo": "amb_abismo.ogg",
}


def _variantes(nombre, cuantas):
    # ["nombre_1.wav", "nombre_2.wav"...]: se turnan sin repetir (ver Sonidos._elegir_variante)
    return ["%s_%d.wav" % (nombre, numero) for numero in range(1, cuantas + 1)]


def _escala(nombre, cuantas, *args, **ficha):
    # {"nombre_1": Efecto("nombre_1.wav"), ...}: una escala (la moneda, la cadena...) se pide
    # por numero, no al azar
    return {"%s_%d" % (nombre, numero): Efecto("%s_%d.wav" % (nombre, numero), *args, **ficha)
            for numero in range(1, cuantas + 1)}


def _uno(nombre, *args, **ficha):
    return {nombre: Efecto(nombre + ".wav", *args, **ficha)}


def _armar(*grupos):
    catalogo = {}
    for grupo in grupos:
        catalogo.update(grupo)
    return catalogo


# Todos los efectos (nombre -> ficha). La partitura de cada uno esta en LISTA_DE_SONIDOS.md y su
# composicion en herramientas/estudio/obras/. Los MOMENTOS bajan la musica mientras suenan
CATALOGO = _armar(
    # ---------- Interfaz (siempre al centro) ----------
    {"ui_mover": Efecto(_variantes("ui_mover", 2), INTERFAZ, ACCION, voces=2, enfriamiento=40, paneo=False)},
    *[_uno(nombre, INTERFAZ, ACCION, voces=1, enfriamiento=30, paneo=False) for nombre in (
        "ui_aceptar", "ui_volver", "ui_error", "ui_pestana", "ui_valor_sube", "ui_valor_baja", "ui_llave_si",
        "ui_llave_no", "ui_alerta", "ui_empezar", "ui_apagar", "pausa", "seguir", "pesadilla", "carta_rara",
        "taller", "tienda", "caja", "vendedor_no", "sello", "barajar", "hangar_nave", "record_guardado",
        "ficha_enemigo")],
    _escala("ui_tecla", 5, INTERFAZ, ACCION, voces=1, paneo=False),
    _escala("dificultad", 4, INTERFAZ, ACCION, voces=1, paneo=False),
    _escala("carta", 6, INTERFAZ, DETALLE, voces=3, paneo=False),
    {"teclear": Efecto(_variantes("teclear", 3), INTERFAZ, DETALLE, voces=1, enfriamiento=45, paneo=False)},

    # ---------- La nave ----------
    {"nave_dash": Efecto(_variantes("nave_dash", 3), EFECTOS, ACCION, voces=2)},
    _uno("nave_dash_extra", EFECTOS, ACCION, voces=2),
    _uno("dash_listo", EFECTOS, DETALLE, voces=1),
    _uno("escudo_roto", EFECTOS, PELIGRO, voces=1),
    _uno("nave_golpe", EFECTOS, PELIGRO, voces=2),
    _uno("ultima_vida", EFECTOS, PELIGRO, voces=1, paneo=False),
    _uno("fenix", EFECTOS, MOMENTO, voces=1, paneo=False),
    _uno("nave_muerte", EFECTOS, MOMENTO, voces=1),
    _uno("hiperespacio", EFECTOS, ACCION, voces=1, paneo=False),

    # ---------- Monedas, combo y puntos ----------
    _escala("moneda", 5, EFECTOS, ACCION, voces=2),
    _uno("oro_brillo", EFECTOS, DETALLE, voces=2),
    _escala("combo_sube", 3, EFECTOS, ACCION, voces=1, paneo=False),
    _uno("combo_max", EFECTOS, ACCION, voces=1, paneo=False),
    _uno("combo_cortado", EFECTOS, DETALLE, voces=1, paneo=False),
    _escala("perfecto", 5, EFECTOS, ACCION, voces=2),
    _uno("interceptado", EFECTOS, ACCION, voces=2),
    _uno("record", EFECTOS, MOMENTO, voces=1, paneo=False),
    _uno("nivel", EFECTOS, ACCION, voces=1, paneo=False),
    _uno("bala_rota", EFECTOS, ACCION, voces=2, enfriamiento=50),

    # ---------- Power-ups y mejoras ----------
    _uno("capsula", EFECTOS, DETALLE, voces=1),
    *[_uno(nombre, EFECTOS, ACCION, voces=1) for nombre in (
        "pw_escudo", "pw_hielo", "pw_vida", "pw_iman", "pw_doble", "pw_turbo", "pw_recarga", "pw_nova",
        "mejora_elegida", "eco")],
    _uno("nova", EFECTOS, PELIGRO, voces=1),
    _uno("pw_acaba", EFECTOS, DETALLE, voces=1, paneo=False),
    _uno("pw_fin", EFECTOS, DETALLE, voces=1, paneo=False),
    {"hielo_roto": Efecto(_variantes("hielo_roto", 3), EFECTOS, ACCION, voces=3, enfriamiento=50)},
    {"onda": Efecto(_variantes("onda", 2), EFECTOS, DETALLE, voces=1)},
    _escala("roce_carga", 6, EFECTOS, DETALLE, voces=1, paneo=False),

    # ---------- Enemigos y proyectiles ----------
    _uno("aparece", EFECTOS, DETALLE, voces=2, enfriamiento=120),
    {"enemigo_roto": Efecto(_variantes("enemigo_roto", 3), EFECTOS, ACCION, voces=3)},
    _uno("aturdido", EFECTOS, DETALLE, voces=1),
    _escala("rebote", 4, EFECTOS, DETALLE, voces=1, enfriamiento=200),
    _uno("embestidor_apunta", EFECTOS, PELIGRO, voces=2),
    _uno("mira_fija", EFECTOS, PELIGRO, voces=2),
    _uno("embestida", EFECTOS, PELIGRO, voces=2),
    _escala("divisor_parte", 3, EFECTOS, ACCION, voces=2),
    _uno("enjambre_aviso", EFECTOS, PELIGRO, voces=1),
    _uno("enjambre_picada", EFECTOS, DETALLE, voces=1),
    _uno("bonus", EFECTOS, ACCION, voces=1),
    _uno("abeja_sale", EFECTOS, DETALLE, voces=2, enfriamiento=100),
    _uno("abeja_aviso", EFECTOS, PELIGRO, voces=2, enfriamiento=150),
    _uno("retirada", EFECTOS, DETALLE, voces=1, enfriamiento=300),
    _uno("mina_tic", EFECTOS, PELIGRO, voces=2),
    _uno("mina_estalla", EFECTOS, PELIGRO, voces=2),

    # ---------- Oleadas, anomalias, desafios y carteles ----------
    _uno("oleada", EFECTOS, PELIGRO, voces=1, paneo=False),
    _uno("oleada_superada", EFECTOS, MOMENTO, voces=1, paneo=False),
    *[_uno(nombre, EFECTOS, PELIGRO, voces=1, paneo=False) for nombre in (
        "asteroides_llega", "tormenta_llega", "niebla_llega", "tormenta_aviso", "llamarada")],
    _uno("oro_llega", EFECTOS, ACCION, voces=1, paneo=False),
    _uno("meteoro_aviso", EFECTOS, PELIGRO, voces=2),
    _uno("anomalia_fin", EFECTOS, DETALLE, voces=1, paneo=False),
    _uno("desafio_nuevo", EFECTOS, ACCION, voces=1, paneo=False),
    _uno("desafio_cumplido", EFECTOS, MOMENTO, voces=1, paneo=False),
    _uno("desafio_fallado", EFECTOS, ACCION, voces=1, paneo=False),
    _uno("logro", EFECTOS, MOMENTO, voces=1, paneo=False),
    _uno("nave_nueva", EFECTOS, ACCION, voces=1, paneo=False),
    _escala("estrella", 5, EFECTOS, ACCION, voces=2, paneo=False),
    *[_uno("sello_" + letra, EFECTOS, MOMENTO, voces=1, paneo=False) for letra in "SABC"],
    _escala("sector_nuevo", 5, EFECTOS, MOMENTO, voces=1, paneo=False),
    _escala("barra_jefe", 12, EFECTOS, DETALLE, voces=2, paneo=False),
    _uno("listo_ready", EFECTOS, ACCION, voces=1, paneo=False),
    _uno("listo_go", EFECTOS, ACCION, voces=1, paneo=False),
    _uno("destruida", EFECTOS, MOMENTO, voces=1, paneo=False),
    _uno("game_over", EFECTOS, MOMENTO, voces=1, paneo=False),
    _uno("trueno", AMBIENTE, DETALLE, voces=1),

    # ---------- Jefes ----------
    *[_uno(nombre, EFECTOS, PELIGRO, voces=1, paneo=False) for nombre in (
        "alerta", "franjas", "presentacion_nombre", "presentacion_apodo")],
    _uno("vulnerable", EFECTOS, PELIGRO, voces=1),
    _uno("jefe_golpe", EFECTOS, PELIGRO, voces=2),
    _uno("jefe_parte", EFECTOS, PELIGRO, voces=2),
    _uno("parte_rota", EFECTOS, PELIGRO, voces=2),
    _uno("golpe_final", EFECTOS, MOMENTO, voces=1),
    {"agonia": Efecto(_variantes("agonia", 3), EFECTOS, ACCION, voces=2, enfriamiento=150)},
    _uno("jefe_explota", EFECTOS, MOMENTO, voces=1),
    _uno("jefe_vencido", EFECTOS, MOMENTO, voces=1, paneo=False),
    # (los ataques y avisos de cada jefe: peligro, con paneo)
    *[_uno(nombre, EFECTOS, PELIGRO, voces=2) for nombre in (
        "ojo_carga", "ojo_abanico", "ojo_anillo", "ojo_cansado", "ojo_voz",
        "carga_canon", "obus", "misil", "laser_carga", "mina_lanza", "recalentado", "coraza", "cortina_aviso",
        "escombros", "fijar", "caida", "estrellarse", "onda_suelo",
        "siseo", "cascabel", "mordida", "serpiente_choca", "mareo", "enroscar", "escupir", "corte",
        "compuerta_abre", "llamado", "furia", "temblar", "embestida_colmena", "colmena_choca",
        "nacer", "inhalar", "exhalar", "colapso", "estallido")],
    *[_uno(nombre, EFECTOS, DETALLE, voces=2, enfriamiento=80) for nombre in (
        "compas", "compas_acento", "anillo_tic", "brazos", "moneda_tragada")],
    {"laser": Efecto("laser.ogg", EFECTOS, PELIGRO, voces=1)},        # loop: tocar_loop / parar_loop
    *[_uno(nombre, EFECTOS, DETALLE, voces=1) for nombre in (
        "ojo_flota", "motor_pesado", "servo", "hidraulica", "panal", "inestable")],

    # ---------- Detalles (P3) ----------
    _uno("logo", INTERFAZ, MOMENTO, voces=1, paneo=False),
    _uno("ui_transicion", INTERFAZ, DETALLE, voces=1, enfriamiento=200, paneo=False),
    _uno("mando_dentro", INTERFAZ, DETALLE, voces=1, paneo=False),
    _uno("mando_fuera", INTERFAZ, DETALLE, voces=1, paneo=False),
    _escala("contador", 8, INTERFAZ, DETALLE, voces=2, paneo=False),
    _uno("contador_fin", INTERFAZ, ACCION, voces=1, paneo=False),
    {"fuego_artificial": Efecto(_variantes("fuego_artificial", 3), EFECTOS, DETALLE, voces=2, enfriamiento=250)},
    _uno("surtidor", INTERFAZ, DETALLE, voces=1, paneo=False),
    _uno("neon", INTERFAZ, DETALLE, voces=1, enfriamiento=150, paneo=False),
    _uno("dash_vacio", EFECTOS, DETALLE, voces=1, enfriamiento=250, paneo=False),
    _uno("latido", EFECTOS, DETALLE, voces=1, paneo=False),
)


_cache = {}     # archivo -> Sound: los temas tardan en abrirse y los tests crean muchas App


def cargar(archivo):
    # El Sound de ese archivo de efectos/ (None si no hay audio o no existe)
    if archivo not in _cache:
        try:
            _cache[archivo] = pygame.mixer.Sound(ruta("efectos/" + archivo))
        except (pygame.error, FileNotFoundError):
            return None         # sin audio o falta el archivo: ese sonido no suena
    return _cache[archivo]


BLOQUE_FICHA = 50       # ms: cada cuanto anota la envolvente de un efecto (herramientas/componer.py)


def cargar_fichas():
    # {archivo: ficha}: cuanto suena cada archivo ({} si falta: el limitador supone lo peor)
    try:
        with open(ruta("efectos/fichas.json"), encoding="utf-8") as archivo:
            return json.load(archivo)
    except (OSError, ValueError):
        return {}


class Sonando:
    # Lo que suena en un canal de efectos: su ficha dice cuanto suena en cada momento
    def __init__(self, nombre, sonido, prioridad, inicio, ganancia, paneo, envolvente, duracion):
        self.nombre = nombre
        self.sonido = sonido            # el Sound (de un armonico: el de su color)
        self.prioridad = prioridad
        self.inicio = inicio            # ms (reloj real)
        self.ganancia = ganancia        # el volumen de su Sound (categoria x opciones)
        self.paneo = paneo              # (izquierda, derecha)
        self.envolvente = envolvente    # el pico de cada bloque de 50 ms (None: sin ficha)
        self.duracion = duracion        # ms
        self.aplicado = None            # el volumen del bus que tiene puesto el canal

    def carga(self, ahora):
        # Cuanto aporta a la suma ahora: el pico de su bloque x su volumen x el lado mas fuerte
        pasado = ahora - self.inicio
        if pasado >= self.duracion:
            return 0.0
        if self.envolvente is None:
            pico = 1.0          # sin ficha: lo peor
        else:
            bloque = int(max(pasado, 0) // BLOQUE_FICHA)
            pico = self.envolvente[bloque] if bloque < len(self.envolvente) else 0.0
        return pico * self.ganancia * max(self.paneo)


def cargar_temas(archivos):
    # {nombre: Sound} con los que se pudieron cargar
    temas = {}
    for nombre, archivo in archivos.items():
        sonido = cargar(archivo)
        if sonido is not None:
            temas[nombre] = sonido
    return temas


def paneo(x, mono=False):
    # (izquierda, derecha) para un sonido que pasa en la x (0 a ANCHO). Al centro suenan
    # los dos lados enteros; hacia un costado el otro lado baja, pero nunca de PANEO_MINIMO
    # (un paneo total cansa y se pierde con auriculares de un solo lado)
    if x is None or mono:
        return 1.0, 1.0
    lugar = min(max(x / ANCHO, 0), 1)       # 0 = izquierda, 1 = derecha
    izquierda = PANEO_MINIMO + (1 - PANEO_MINIMO) * min(1, 2 * (1 - lugar))
    derecha = PANEO_MINIMO + (1 - PANEO_MINIMO) * min(1, 2 * lugar)
    return izquierda, derecha


class Tocadiscos:
    # Dos canales reservados para pasar de un tema a otro con un fundido cruzado: el tema
    # nuevo va al canal libre mientras el otro todavia apaga el viejo. Lo usan la musica y
    # el ambiente. 'actual' es el nombre pedido, aunque no haya audio (los tests lo miran)
    def __init__(self, canales, temas, fundido, reloj):
        self.canales = canales      # [] si no hay audio
        self.temas = temas          # nombre -> Sound
        self.fundido = fundido
        self.reloj = reloj          # el reloj real (ms)
        self.actual = None          # el tema que suena (None = silencio)
        self.canal = None           # el canal donde suena
        self.inicio = None          # cuando empezo el tema (sin contar las pausas): en que compas va

    def tocar(self, nombre):
        # Si ya suena ese, sigue de largo; si no, cruza al nuevo (desde el principio)
        if nombre == self.actual:
            return
        self.parar()
        self.actual = nombre
        self.inicio = self.reloj()
        tema = self.temas.get(nombre)
        if tema is not None and self.canales:
            libres = [canal for canal in self.canales if not canal.get_busy()]
            self.canal = libres[0] if libres else self.canales[0]
            self.canal.play(tema, loops=-1, fade_ms=self.fundido)

    def parar(self, fundido=None):
        # fundido = 0: corta en seco (al morir)
        fundido = self.fundido if fundido is None else fundido
        if self.canal is not None:
            if fundido:
                self.canal.fadeout(fundido)
            else:
                self.canal.stop()
        self.canal = None
        self.actual = None
        self.inicio = None

    def tema_actual(self):
        return self.temas.get(self.actual)


class Sonidos:
    def __init__(self, catalogo=CATALOGO, musicas=MUSICAS, ambientes=AMBIENTES):
        self.catalogo = catalogo
        # Los armonicos tienen ~1000 archivos (uno por color): abrirlos todos tardaba 2 s al
        # arrancar. Se abren los de Do; cada otro color, la primera vez que suena (~1.5 ms)
        self.fichas = cargar_fichas()
        self.envolventes = {}           # Sound -> envolvente (los efectos: la usa el limitador)
        self.variantes = {}             # nombre -> [Sound] (los que se pudieron cargar; de un armonico, los de Do)
        self.de_color = {}              # nombre de un armonico -> {color: [Sound de cada variante]} (los abiertos)
        for nombre, efecto in catalogo.items():
            archivos = efecto.por_color[COLOR_SIN_MUSICA] if efecto.armonico else efecto.archivos
            self.variantes[nombre] = self._abrir(archivos)
            if efecto.armonico:
                self.de_color[nombre] = {COLOR_SIN_MUSICA: self.variantes[nombre]}
        self.opciones = None            # las pone aplicar_volumen (sin opciones: todo al maximo)
        self.reloj = pygame.time.get_ticks     # reloj real en ms (la App pone el suyo)
        self.ultima_vez = {}            # nombre -> cuando sono por ultima vez (para el enfriamiento)
        self.ultima_variante = {}       # nombre -> la variante que sono (para no repetirla)
        self.atenuada_hasta = -math.inf     # hasta cuando la musica esta baja por un momento
        self.factor_aplicado = 1.0      # el ducking que tiene puesto la musica ahora
        self.pendientes = []            # [(cuando, nombre, x)]: efectos programados (reproducir_luego)
        # El limitador: cuanto suena cada archivo (las fichas) y cuanto bajo cada grupo
        fichas = self.fichas
        # nombre de un tema -> su nivel tipico (sin ficha: 1, lo peor)
        self.nivel_de_tema = {nombre: fichas.get(archivo, {}).get("nivel", 1.0)
                              for nombre, archivo in list(musicas.items()) + list(ambientes.items())}
        self.nivel_de_loop = {nombre: fichas.get(efecto.archivos[0], {}).get("nivel", 1.0)
                              for nombre, efecto in catalogo.items()}
        self.bus = {"detalles": 1.0, "importantes": 1.0}     # cuanto bajo cada grupo (1 = entero)
        self.bus_cuando = None          # cuando se ajusto por ultima vez (para volver de a poco)
        # La armonia de cada tema: nombre -> (el color de cada compas, ms de un compas)
        self.armonia = {nombre: (fichas[archivo]["colores"], fichas[archivo]["compas_ms"])
                        for nombre, archivo in musicas.items() if "colores" in fichas.get(archivo, {})}
        self.pausado_en = None          # cuando se pauso todo (la musica no avanza en la pausa)

        canales = []
        if pygame.mixer.get_init():
            pygame.mixer.set_num_channels(CANALES_AUDIO)
            pygame.mixer.set_reserved(PRIMER_CANAL_EFECTOS)    # Sound.play() no usa los reservados
            canales = [pygame.mixer.Channel(i) for i in range(CANALES_AUDIO)]

        def elegir(numeros):
            return [canales[i] for i in numeros] if canales else []

        def reloj():
            return self.reloj()     # (la App cambia self.reloj despues de crear los Sonidos)
        self.musica = Tocadiscos(elegir(CANALES_MUSICA), cargar_temas(musicas), FUNDIDO_MUSICA, reloj)
        self.ambiente = Tocadiscos(elegir(CANALES_AMBIENTE), cargar_temas(ambientes), FUNDIDO_AMBIENTE, reloj)
        self.canales_loop = elegir(CANALES_LOOP)
        self.en_loop = [None] * len(self.canales_loop)                  # el nombre que suena en cada uno
        self.canales_efectos = canales[PRIMER_CANAL_EFECTOS:]
        self.en_canal = [None] * len(self.canales_efectos)      # un Sonando (o None)

    # ---------- Efectos ----------

    def reproducir(self, nombre, x=None):
        # Toca un efecto del catalogo; 'x' es donde paso (para el paneo). Devuelve el canal,
        # o None si no sono (sin audio, en enfriamiento o sin lugar para su prioridad)
        efecto = self.catalogo.get(nombre)
        if efecto is None or not self.variantes.get(nombre):
            return None
        ahora = self.reloj()
        if ahora - self.ultima_vez.get(nombre, -math.inf) < efecto.enfriamiento:
            return None
        lugar = self._lugar_para(nombre, efecto)
        if lugar is None:
            return None
        sonido = self._elegir_variante(nombre, efecto)
        if sonido is None:
            return None
        canal = self.canales_efectos[lugar]
        canal.play(sonido)
        mono = self.opciones is not None and self.opciones.audio_mono
        self.en_canal[lugar] = Sonando(nombre, sonido, efecto.prioridad, ahora, sonido.get_volume(),
                                       paneo(x if efecto.paneo else None, mono), self.envolventes.get(sonido),
                                       sonido.get_length() * 1000)
        self.ultima_vez[nombre] = ahora
        if efecto.prioridad >= MOMENTO:
            self.atenuar_musica(sonido.get_length() * 1000)
        # El volumen del canal (el paneo x el limitador) se pone despues de play(): play lo vuelve a 1
        self.limitar()
        return canal

    # ---------- El limitador (que la suma no sature) ----------

    def carga_del_fondo(self):
        # Cuanto ocupan la musica, el ambiente y los loops (lo que no se baja con el limitador)
        carga = 0.0
        if self.musica.actual in self.nivel_de_tema:
            carga += self.nivel(MUSICA) * self.factor_aplicado * self.nivel_de_tema[self.musica.actual]
        if self.ambiente.actual in self.nivel_de_tema:
            carga += self.nivel(AMBIENTE) * self.nivel_de_tema[self.ambiente.actual]
        for nombre in self.en_loop:
            if nombre is not None:
                carga += self.nivel(EFECTOS) * self.nivel_de_loop.get(nombre, 1.0)
        return carga

    def limitar(self):
        # Ajusta el volumen de cada canal de efectos (su paneo x lo que baja su grupo) para que
        # la suma de todo no pase de TECHO_MEZCLA. Lo llaman reproducir() y actualizar()
        ahora = self.reloj()
        sonando = [(i, s) for i, s in enumerate(self.en_canal) if s is not None and s.carga(ahora) > 0]
        importantes = sum(s.carga(ahora) for i, s in sonando if s.prioridad >= PELIGRO)
        detalles = sum(s.carga(ahora) for i, s in sonando if s.prioridad < PELIGRO)
        objetivo = self._cuanto_bajar(TECHO_MEZCLA - self.carga_del_fondo(), importantes, detalles)
        # Bajar es inmediato (si no, ya sono saturado); subir, de a poco
        pasado = 0 if self.bus_cuando is None else ahora - self.bus_cuando
        for grupo, valor in objetivo.items():
            subido = self.bus[grupo] + pasado / RECUPERACION_MEZCLA
            self.bus[grupo] = min(valor, subido)
        self.bus_cuando = ahora
        for i, s in sonando:
            ganancia = self.bus["importantes" if s.prioridad >= PELIGRO else "detalles"]
            if s.aplicado != ganancia:
                self.canales_efectos[i].set_volume(s.paneo[0] * ganancia, s.paneo[1] * ganancia)
                s.aplicado = ganancia

    @staticmethod
    def _cuanto_bajar(lugar, importantes, detalles):
        # {grupo: volumen}. Si todo entra en 'lugar', nada baja. Si no, primero bajan los
        # detalles (hasta PISO_DETALLES) y, si no alcanza, los dos grupos por igual
        if importantes + detalles <= lugar:
            return {"detalles": 1.0, "importantes": 1.0}
        lugar = max(lugar, 0.05)
        bajan = max(PISO_DETALLES, (lugar - importantes) / detalles) if detalles else 1.0
        bajan = min(bajan, 1.0)
        total = importantes + detalles * bajan
        # Si bajar los detalles alcanzo, total == lugar (salvo el redondeo: 0.9999999999999999)
        todos = 1.0 if total <= lugar * (1 + 1e-9) else lugar / total
        return {"detalles": bajan * todos, "importantes": todos}

    def reproducir_luego(self, nombre, ms, x=None):
        # Lo toca dentro de 'ms' (reloj real): la fanfarria despues de la explosion, el sello
        # despues de la caja... Lo dispara actualizar()
        self.pendientes.append((self.reloj() + ms, nombre, x))

    def cancelar_pendientes(self):
        self.pendientes = []

    def sonando(self, nombre):
        # Cuantas copias de este efecto estan sonando ahora
        return len(self._lugares_de(nombre))

    def _lugares_de(self, nombre):
        return [i for i, ocupado in enumerate(self.en_canal)
                if ocupado is not None and ocupado.nombre == nombre and self.canales_efectos[i].get_busy()]

    def _lugar_para(self, nombre, efecto):
        # El canal de efectos donde va a sonar (su indice), o None si no le toca
        mismos = self._lugares_de(nombre)
        if len(mismos) >= efecto.voces:
            return min(mismos, key=lambda i: self.en_canal[i].inicio)     # corta al mas viejo de los suyos
        ocupados = []
        for i, canal in enumerate(self.canales_efectos):
            if not canal.get_busy():
                return i
            ocupados.append(i)
        if not ocupados:
            return None         # sin audio
        # Todo lleno: le roba el canal al menos importante (y entre esos, al mas viejo)
        def importancia(i):
            ocupado = self.en_canal[i]
            return (ocupado.prioridad, ocupado.inicio) if ocupado else (0, 0)
        menos_importante = min(ocupados, key=importancia)
        if importancia(menos_importante)[0] <= efecto.prioridad:
            return menos_importante
        return None

    def _elegir_variante(self, nombre, efecto):
        # Al azar entre sus variantes, pero nunca la misma dos veces seguidas. Un armonico,
        # en el color del acorde que suena (si falta ese archivo, el de Do)
        sonidos = self.variantes[nombre]
        if efecto.armonico:
            sonidos = self._de_color(nombre, efecto, self.color_actual()) or self.variantes[nombre]
            if not sonidos:
                return None
        opciones = [i for i in range(len(sonidos)) if i != self.ultima_variante.get(nombre)] or [0]
        elegida = random.choice(opciones)
        self.ultima_variante[nombre] = elegida
        return sonidos[elegida]

    def _abrir(self, archivos):
        # Los Sound de esos archivos (los que existen), con su envolvente anotada
        sonidos = []
        for archivo in archivos:
            sonido = cargar(archivo)
            if sonido is not None:
                sonidos.append(sonido)
                if "envolvente" in self.fichas.get(archivo, {}):
                    self.envolventes[sonido] = self.fichas[archivo]["envolvente"]
        return sonidos

    def _de_color(self, nombre, efecto, color):
        # Los Sound de un armonico en ese color; se abren la primera vez (con su volumen)
        colores = self.de_color[nombre]
        if color not in colores:
            colores[color] = self._abrir(efecto.por_color[color])
            for sonido in colores[color]:
                sonido.set_volume(self.nivel(efecto.categoria) * efecto.volumen)
        return colores[color]

    def color_actual(self):
        # El color del acorde que suena ahora (ver herramientas/estudio/armonia.py). Mira
        # ADELANTO_ACORDE ms adelante: si el acorde cambia justo, el efecto ya suena en el
        # nuevo (casi todo lo que se oye de un efecto viene despues de su ataque). Sin musica
        # (o con su volumen en 0), siempre el de Do: la moneda suena igual que siempre
        armonia = self.armonia.get(self.musica.actual)
        if armonia is None or self.musica.inicio is None or self.nivel(MUSICA) == 0:
            return COLOR_SIN_MUSICA
        colores, compas_ms = armonia
        ahora = self.pausado_en if self.pausado_en is not None else self.reloj()
        compas = int((ahora - self.musica.inicio + ADELANTO_ACORDE) // compas_ms)
        return colores[compas % len(colores)]

    # ---------- Loops (suenan hasta que se los para) ----------

    def tocar_loop(self, nombre):
        # Un efecto del catalogo que se repite (el laser de la Fortaleza, una sirena...).
        # Si ya suena, no hace nada; si los dos canales de loop estan ocupados, no suena
        if nombre in self.en_loop or not self.variantes.get(nombre):
            return
        for i, canal in enumerate(self.canales_loop):
            if self.en_loop[i] is None or not canal.get_busy():
                canal.play(self.variantes[nombre][0], loops=-1)
                self.en_loop[i] = nombre
                return

    def parar_loop(self, nombre, fundido=0):
        for i, canal in enumerate(self.canales_loop):
            if self.en_loop[i] == nombre:
                if fundido:
                    canal.fadeout(fundido)
                else:
                    canal.stop()
                self.en_loop[i] = None

    def parar_loops(self):
        for nombre in [n for n in self.en_loop if n is not None]:
            self.parar_loop(nombre)

    # ---------- Musica y ambiente ----------

    @property
    def actual(self):
        # El tema de musica que se pidio (None = silencio)
        return self.musica.actual

    def tocar_musica(self, nombre):
        self.musica.tocar(nombre)
        self._poner_volumen_musica()

    def parar_musica(self, fundido=FUNDIDO_MUSICA):
        self.musica.parar(fundido)

    def tocar_ambiente(self, nombre):
        self.ambiente.tocar(nombre)

    def parar_ambiente(self, fundido=FUNDIDO_AMBIENTE):
        self.ambiente.parar(fundido)

    def atenuar_musica(self, ms):
        # Baja la musica a ATENUAR_MUSICA durante 'ms' y despues vuelve de a poco (ducking)
        self.atenuada_hasta = max(self.atenuada_hasta, self.reloj() + ms)
        self._poner_volumen_musica()

    def factor_musica(self):
        # 1 = la musica entera; ATENUAR_MUSICA mientras suena un momento, y vuelve en ATENUAR_VUELTA ms
        pasado = self.reloj() - self.atenuada_hasta
        if pasado < 0:
            return ATENUAR_MUSICA
        if pasado >= ATENUAR_VUELTA:
            return 1.0
        return ATENUAR_MUSICA + (1 - ATENUAR_MUSICA) * pasado / ATENUAR_VUELTA

    def actualizar(self):
        # En cada paso (lo llama la App): los efectos programados que ya tocan y el ducking,
        # que sube de a poco
        if self.pendientes:
            ahora = self.reloj()
            for cuando, nombre, x in [p for p in self.pendientes if p[0] <= ahora]:
                self.reproducir(nombre, x)
            self.pendientes = [p for p in self.pendientes if p[0] > ahora]
        if self.factor_musica() != self.factor_aplicado:
            self._poner_volumen_musica()
        self.limitar()

    # ---------- Volumen y pausa ----------

    def nivel(self, categoria):
        # Volumen de una categoria (0 a 1): el general x el suyo x la mezcla. Silencio (M) = 0
        opciones = self.opciones
        if opciones is None:
            return MEZCLA[categoria]
        if opciones.silencio:
            return 0.0
        propio = opciones.volumen_musica if categoria == MUSICA else opciones.volumen_efectos
        return opciones.volumen / VOLUMEN_MAX * propio / VOLUMEN_MAX * MEZCLA[categoria]

    def aplicar_volumen(self, opciones):
        # Lo llaman la App al arrancar, Opciones y el atajo M. Apagado = volumen 0: sigue
        # sonando en silencio, asi la musica retoma donde iba
        self.opciones = opciones
        for nombre, efecto in self.catalogo.items():
            abiertos = self.de_color[nombre].values() if efecto.armonico else [self.variantes[nombre]]
            for sonidos in abiertos:
                for sonido in sonidos:
                    sonido.set_volume(self.nivel(efecto.categoria) * efecto.volumen)
        for tema in self.ambiente.temas.values():
            tema.set_volume(self.nivel(AMBIENTE))
        self._poner_volumen_musica()

    def _poner_volumen_musica(self):
        # El volumen del Sound (aparte del volumen del canal, que usa el fundido): asi el
        # ducking y el fundido no se pisan
        self.factor_aplicado = self.factor_musica()
        actual = self.musica.tema_actual()
        for tema in self.musica.temas.values():
            factor = self.factor_aplicado if tema is actual else 1.0
            tema.set_volume(self.nivel(MUSICA) * factor)

    def pausar_todo(self):
        # Congela todos los canales (musica incluida) y retoma donde iban. Un efecto pedido
        # despues SI suena: la pausa puede tener su sonido
        if self.pausado_en is None:
            self.pausado_en = self.reloj()
        if pygame.mixer.get_init():
            pygame.mixer.pause()

    def reanudar_todo(self):
        # La musica retoma donde iba: su "inicio" se corre lo que duro la pausa (asi sigue
        # sabiendo en que compas va)
        if self.pausado_en is not None:
            pausa = self.reloj() - self.pausado_en
            for tocadiscos in (self.musica, self.ambiente):
                if tocadiscos.inicio is not None:
                    tocadiscos.inicio += pausa
            self.pausado_en = None
        if pygame.mixer.get_init():
            pygame.mixer.unpause()
