import pygame
import random
import math
import os
import json

# Iniciar Pygame
pygame.init()

# Carpeta del juego: asi encuentra sus archivos aunque se ejecute desde otra carpeta
CARPETA = os.path.dirname(os.path.abspath(__file__))

def ruta(archivo):
    return os.path.join(CARPETA, archivo)

# Variables juego
pantalla = pygame.Surface((800, 600))  # lienzo donde se dibuja todo; mostrar() lo escala a la ventana
reloj = pygame.time.Clock()
pygame.display.set_caption("Caza Monedas")

# ================================== #
# ========= CONFIGURACION ========== #
# ================================== #

# Fuente pixelada estilo arcade (Press Start 2P, licencia en fuentes/OFL.txt)
def fuente_arcade(tamano):
    try:
        return pygame.font.Font(ruta("fuentes/PressStart2P-Regular.ttf"), tamano)
    except FileNotFoundError:
        return pygame.font.SysFont("consolas,couriernew", tamano, bold=True)

fuente_titulo = fuente_arcade(56)
fuente_grande = fuente_arcade(40)
fuente_media = fuente_arcade(24)
fuente_chica = fuente_arcade(16)

# Colores neon
BLANCO = (255, 255, 255)
GRIS = (130, 130, 160)
AMARILLO = (255, 221, 0)
ROJO = (255, 50, 70)
CIAN = (0, 230, 255)
MAGENTA = (255, 0, 170)
VERDE = (60, 255, 120)
HIELO = (140, 190, 255)
FONDO = (6, 6, 18)
ARCOIRIS = [ROJO, AMARILLO, VERDE, CIAN, MAGENTA]

# Paletas de las particulas: van del color final (apagado) al inicial (brillante).
# Cada particula nace con el ultimo color y va bajando por la lista, como en las
# consolas antiguas que cambiaban de color en vez de usar transparencias.
FUEGO = [(120, 0, 30), ROJO, (255, 140, 0), AMARILLO, BLANCO]
ORO = [(150, 90, 0), AMARILLO, (255, 250, 180), BLANCO]
ESCARCHA = [(40, 60, 140), HIELO, BLANCO]
ENERGIA = [(0, 70, 110), CIAN, BLANCO]
CORAZON = [(120, 0, 30), ROJO, (255, 160, 170), BLANCO]
EMBESTIDA = [(90, 0, 60), MAGENTA, (255, 150, 230), BLANCO]
IMANTADO = [(90, 0, 60), MAGENTA, BLANCO]
TREBOL = [(0, 90, 40), VERDE, BLANCO]

# Estrellas del fondo: [x, y, velocidad]
estrellas = []
for i in range(90):
    estrellas.append([random.randint(0, 800), random.randint(0, 600), random.choice([1, 1, 1, 2, 2, 3])])

# Lineas horizontales oscuras que imitan una pantalla de arcade (CRT)
lineas_crt = pygame.Surface((800, 600), pygame.SRCALPHA)
for linea_y in range(0, 600, 3):
    pygame.draw.line(lineas_crt, (0, 0, 0, 70), (0, linea_y), (800, linea_y))

# Reglas del juego (cambialas para ajustar la dificultad)
VIDAS_MAX = 3
COMBO_TIEMPO = 2000             # ms maximos entre monedas para seguir el combo
MONEDAS_POR_NIVEL = 10
AVISO_APARICION = 800           # ms que se ve la "X" antes de que aparezca un enemigo
DASH_FUERZA = 14
DASH_DURACION = 180             # ms que dura el impulso (sin recibir daño)
DASH_RECARGA = 1500             # ms hasta poder usarlo otra vez
BUFFER_DASH = 150               # si apretas el dash hasta estos ms antes de que se recargue, sale igual
PUNTOS_ENEMIGO_CONGELADO = 5
VELOCIDAD_POWERUP = 1.5         # px por frame que cae la capsula (con 1.5 cruza la pantalla en ~7 s)
TURBO_VELOCIDAD = 7             # velocidad maxima con TURBO (normal: 5)
RECARGA_RAPIDA = 750            # ms de recarga del dash con RECARGA (normal: DASH_RECARGA)

# Choques que hacen daño: circulos, asi la nave recibe el mismo golpe aunque este girada
RADIO_NAVE = 11
RADIO_ENEMIGO = 15
RADIO_BALA = 4

# Monedas: aparecen a esta distancia de la nave (asi siempre se llega antes de que se corte el combo)
MONEDA_DISTANCIA_MIN = 120
MONEDA_DISTANCIA_MAX = 450

# Jefe: se le pega con el dash en el nucleo cuando queda cansado
JEFE_CADA_NIVELES = 5           # aparece al llegar a los niveles 5, 10, 15...
JEFE_VIDA = 3                   # golpes que aguanta el primero (cada jefe nuevo aguanta uno mas)
JEFE_PUNTOS = 50                # bonus al vencerlo (el segundo da el doble, el tercero el triple...)
JEFE_FLOTAR = 2500              # ms que se mueve de lado a lado antes de atacar
JEFE_CANSADO = 2500             # ms que deja el nucleo al descubierto
JEFE_RAFAGAS = 3                # rafagas de balas en cada ataque
CARTEL_JEFE = 2000              # ms que se ve "¡JEFE VENCIDO!" (los enemigos vuelven despues)

# Animaciones: milisegundos que dura cada cuadro (menos = mas rapido)
MS_CUADRO_ENEMIGO = 250
MS_CUADRO_MONEDA = 100
MS_CUADRO_ESCUDO = 150
MS_CUADRO_JEFE = 200

# Fondo con paralaje: lo lejano se mueve lento y lo cercano rapido
REACCION_PARALAJE = 0.15        # cuanto se corre el fondo cuando se mueve la nave
PROFUNDIDAD = {                 # velocidad de cada capa (las estrellas van de 1 a 3)
    "nebulosa": 0.15,
    "planeta_chico": 0.3,
    "planeta_grande": 0.6,
}

# Enemigo nuevo que se agrega al llegar a cada nivel
ENEMIGOS_POR_NIVEL = {
    2: "rebotador",
    3: "embestidor",
    4: "perseguidor",
    5: "rebotador",
}
# Despues de cada jefe vencido se suma uno mas (se van turnando), hasta ENEMIGOS_MAX
ENEMIGOS_POR_JEFE = ["embestidor", "perseguidor", "rebotador"]
ENEMIGOS_MAX = 8
# Los que persiguen se separan entre si, para no terminar todos encimados en el mismo punto
SEPARACION_ENEMIGOS = 50        # distancia (px) a la que empiezan a alejarse de otro enemigo
FUERZA_SEPARACION = 0.3         # que tan fuerte se alejan (mas = se separan mas rapido)
# El embestidor solo te sigue (y te embiste) si estas a menos de esta distancia; si no, deambula
RANGO_EMBESTIDOR = 250

# Power-ups: letra, color, nombre y descripcion (capsulas como en los arcades)
POWERUPS = {
    "escudo": ("E", CIAN, "ESCUDO", "AGUANTA UN GOLPE"),
    "hielo": ("H", HIELO, "HIELO", "CONGELA ENEMIGOS"),
    "vida": ("+", ROJO, "VIDA", "RECUPERA UNA VIDA"),
    "iman": ("I", MAGENTA, "IMAN", "ATRAE LAS MONEDAS"),
    "doble": ("2", VERDE, "DOBLE", "PUNTOS DOBLES"),
    "turbo": ("T", AMARILLO, "TURBO", "RAPIDA HASTA PERDER VIDA"),
    "recarga": ("R", CIAN, "RECARGA", "DASH x2 HASTA PERDER VIDA"),
}
# turbo y recarga no estan aca: duran hasta perder una vida
DURACION = {                    # milisegundos que dura cada power-up
    "escudo": 15000,
    "hielo": 5000,
    "iman": 7000,
    "doble": 8000,
}

# Letras que se pueden usar en la tabla de records
ALFABETO = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
ARCHIVO_RECORDS = ruta("records.json")

# Tamaños de ventana (nombre, ancho, alto); el juego siempre se dibuja en 800x600
RESOLUCIONES = [("800x600", 800, 600), ("1200x900", 1200, 900),
                ("1600x1200", 1600, 1200), ("COMPLETA", 0, 0)]
ARCHIVO_CONFIG = ruta("config.json")
VOLUMEN_MAX = 10                # pasos de la barra de volumen (tambien es el volumen de fabrica)

# Mando de Xbox: cada boton "aprieta" una tecla, asi todo el juego funciona igual
BOTON_A = 0
BOTON_B = 1
BOTON_X = 2
BOTON_VISTA = 6                 # el de los dos cuadraditos
BOTON_MENU = 7                  # el de las tres rayitas
BOTONES_MANDO = {
    BOTON_A: pygame.K_RETURN,   # aceptar
    BOTON_X: pygame.K_SPACE,    # dash
    BOTON_B: pygame.K_ESCAPE,   # volver (en el juego no pausa, para no apretarlo sin querer)
    BOTON_MENU: pygame.K_p,     # pausa
    BOTON_VISTA: pygame.K_o,    # opciones desde la pausa
}
ZONA_MUERTA = 0.5               # en los menus: cuanto hay que inclinar el stick para que cuente (0 a 1)
ZONA_MUERTA_NAVE = 0.25         # al mover la nave (mas chica, para que responda enseguida)

# ================================== #
# ============ RECURSOS ============ #
# ================================== #

# Efectos de sonido
musica_fondo = pygame.mixer.Sound(ruta("efectos/musica.mp3"))
sonido_game_over = pygame.mixer.Sound(ruta("efectos/game_over.wav"))
sonido_moneda = pygame.mixer.Sound(ruta("efectos/moneda.wav"))
sonido_golpe = pygame.mixer.Sound(ruta("efectos/golpe.wav"))
sonido_powerup = pygame.mixer.Sound(ruta("efectos/moneda_brillante.wav"))
sonido_seleccion = pygame.mixer.Sound(ruta("efectos/seleccion.wav"))
sonido_nuevo_record = pygame.mixer.Sound(ruta("efectos/nuevo_record.wav"))
# Todos los efectos (sin la musica), para cambiarles el volumen juntos
efectos_sonido = [sonido_game_over, sonido_moneda, sonido_golpe, sonido_powerup,
                  sonido_seleccion, sonido_nuevo_record]

def tenir(imagen, color):
    # Copia de la imagen en tonos de un solo color (variantes sin dibujar sprites nuevos)
    copia = pygame.transform.grayscale(imagen)
    copia.fill((70, 70, 70), special_flags=pygame.BLEND_RGB_ADD)
    copia.fill(color, special_flags=pygame.BLEND_RGB_MULT)
    return copia

def cargar_sprite(archivo):
    # Devuelve la imagen, o None si el archivo todavia no existe
    # (asi el juego funciona igual mientras faltan sprites)
    try:
        return pygame.image.load(ruta("sprites/" + archivo))
    except FileNotFoundError:
        return None

def cortar_hoja(hoja, ancho_cuadro):
    # Separa una hoja de animacion (cuadros uno al lado del otro) en una lista
    cuadros = []
    for cuadro_x in range(0, hoja.get_width(), ancho_cuadro):
        cuadros.append(hoja.subsurface((cuadro_x, 0, ancho_cuadro, hoja.get_height())))
    return cuadros

def cuadro_animado(cuadros, ms_por_cuadro, desfase=0):
    # Elige el cuadro que toca segun el reloj real (es solo visual)
    return cuadros[(pygame.time.get_ticks() + desfase) // ms_por_cuadro % len(cuadros)]

# Imagenes
jugador_img = pygame.image.load(ruta("sprites/nave.png"))
nave_icono = pygame.transform.scale(jugador_img, (25, 25))
nave_icono_vacia = nave_icono.copy()
nave_icono_vacia.set_alpha(40)
nave_fantasma_img = tenir(jugador_img, CIAN)        # estela del dash

# Escudo: burbuja animada; si no hay sprite se dibuja un circulo
escudo_hoja = cargar_sprite("escudo.png")
if escudo_hoja is not None:
    ESCUDO_CUADROS = cortar_hoja(escudo_hoja, 76)
else:
    ESCUDO_CUADROS = None

# Moneda: animacion de giro; si no hay sprite se dibuja una elipse que se angosta
moneda_hoja = cargar_sprite("moneda_giro.png")
if moneda_hoja is not None:
    MONEDA_CUADROS = cortar_hoja(moneda_hoja, 20)
else:
    MONEDA_CUADROS = None

# Capsulas de power-up, en el mismo orden que POWERUPS; si no hay sprite, cuadro con letra
capsulas_hoja = cargar_sprite("powerups.png")
CAPSULAS = {}
if capsulas_hoja is not None:
    for tipo, cuadro in zip(POWERUPS, cortar_hoja(capsulas_hoja, 30)):
        CAPSULAS[tipo] = cuadro

def enemigo_respaldo(color):
    # Enemigo dibujado a mano (cuadrado con dos ojos), por si falta su sprite
    imagen = pygame.Surface((40, 40), pygame.SRCALPHA)
    pygame.draw.rect(imagen, color, (4, 4, 32, 32), 4)
    pygame.draw.rect(imagen, color, (12, 14, 6, 6))
    pygame.draw.rect(imagen, color, (22, 14, 6, 6))
    return imagen

# Enemigos: cada tipo tiene su animacion; si falta el sprite se usa el dibujo de respaldo
COLOR_ENEMIGO = {"perseguidor": ROJO, "rebotador": AMARILLO, "embestidor": MAGENTA}
ENEMIGO_CUADROS = {}
for tipo in COLOR_ENEMIGO:
    hoja = cargar_sprite(tipo + ".png")
    if hoja is not None:
        ENEMIGO_CUADROS[tipo] = cortar_hoja(hoja, 40)
    else:
        ENEMIGO_CUADROS[tipo] = [enemigo_respaldo(COLOR_ENEMIGO[tipo])]

# Variantes hechas a partir del primer cuadro de cada enemigo
ENEMIGO_CONGELADO = {}
for tipo in ENEMIGO_CUADROS:
    ENEMIGO_CONGELADO[tipo] = tenir(ENEMIGO_CUADROS[tipo][0], HIELO)

# Embestidor apuntando: su sprite de carga; si no hay, parpadea con un destello blanco
embestidor_carga_img = cargar_sprite("embestidor_carga.png")
embestidor_blanco_img = ENEMIGO_CUADROS["embestidor"][0].copy()
embestidor_blanco_img.fill(BLANCO, special_flags=pygame.BLEND_RGB_MAX)

def jefe_respaldo(color_nucleo):
    # Jefe dibujado a mano (escudo magenta con el nucleo al centro), por si falta su sprite
    imagen = pygame.Surface((120, 120), pygame.SRCALPHA)
    puntos = [(8, 14), (112, 14), (112, 62), (60, 110), (8, 62)]
    pygame.draw.polygon(imagen, MAGENTA, puntos)
    pygame.draw.polygon(imagen, (58, 0, 40), puntos, 4)
    pygame.draw.circle(imagen, (58, 0, 40), (60, 50), 22)
    pygame.draw.circle(imagen, color_nucleo, (60, 50), 18)
    return imagen

# Jefe: 6 cuadros de a pares (flotar, atacar, cansado); con 2 cuadros se usan para todo
jefe_hoja = cargar_sprite("jefe.png")
if jefe_hoja is not None:
    jefe_cuadros = cortar_hoja(jefe_hoja, 120)
else:
    jefe_cuadros = [jefe_respaldo(GRIS), jefe_respaldo(GRIS),
                    jefe_respaldo(ROJO), jefe_respaldo((255, 150, 140)),
                    jefe_respaldo(AMARILLO), jefe_respaldo(BLANCO)]
if len(jefe_cuadros) >= 6:
    JEFE_ANIMACION = {"flotar": jefe_cuadros[0:2], "atacar": jefe_cuadros[2:4], "cansado": jefe_cuadros[4:6]}
else:
    JEFE_ANIMACION = {"flotar": jefe_cuadros, "atacar": jefe_cuadros, "cansado": jefe_cuadros}

# Variantes del jefe: congelado (hielo) y blanco (destello al recibir un golpe)
JEFE_CONGELADO = {}
JEFE_BLANCO = {}
for animacion in JEFE_ANIMACION:
    JEFE_CONGELADO[animacion] = []
    JEFE_BLANCO[animacion] = []
    for cuadro in JEFE_ANIMACION[animacion]:
        JEFE_CONGELADO[animacion].append(tenir(cuadro, HIELO))
        blanco = cuadro.copy()
        blanco.fill(BLANCO, special_flags=pygame.BLEND_RGB_MAX)
        JEFE_BLANCO[animacion].append(blanco)

# Nebulosas y planetas del fondo: [imagen, x, y, profundidad]
objetos_fondo = []

def agregar_objeto_fondo(archivo, x, y, voltear=False):
    # Si falta el sprite, simplemente no se agrega
    imagen = cargar_sprite(archivo + ".png")
    if imagen is None:
        return
    if voltear:
        imagen = pygame.transform.flip(imagen, True, True)  # para que no se vean iguales
    objetos_fondo.append([imagen, x, y, PROFUNDIDAD[archivo]])

# En orden de dibujo: primero lo mas lejano
agregar_objeto_fondo("nebulosa", 40, 60)
agregar_objeto_fondo("nebulosa", 480, 360, voltear=True)
agregar_objeto_fondo("planeta_chico", 660, 140)
agregar_objeto_fondo("planeta_chico", 150, 470)
agregar_objeto_fondo("planeta_grande", 520, 250)

# ================================== #
# ============= ESTADO ============= #
# ================================== #

ejecutando = True
estado = "Inicio"       # Inicio, Opciones, Listo, Jugando, Pausa, Explosion, Iniciales, Fin
tiempo_menu = 0         # momento (reloj real) en que empezo la pantalla actual
captura_pausa = None    # imagen del juego al pausar
pausa_automatica = False    # se pausa solo si la ventana pierde el foco o se desconecta el mando

# Menus
opcion_inicio = 0       # 0 = JUGAR, 1 = OPCIONES
opcion_menu = 0         # fila elegida en Opciones (0 = RESOLUCION, la ultima = VOLVER)
volver_a = "Inicio"     # pantalla a la que se regresa al salir de Opciones

# Reloj del juego: solo avanza mientras se juega, asi la pausa, el "READY" y el
# congelado de los golpes no gastan el tiempo de los power-ups
tiempo_juego = 0
congelar_frames = 0     # frames de "hit-stop" (el juego se detiene un instante)

# Jugador
x, y = 100, 200
vx, vy = 0, 0           # velocidad actual de la nave
velocidad = 5           # velocidad maxima
aceleracion = 0.15      # que tan rapido llega a la velocidad maxima (0 a 1)
friccion = 0.88         # al soltar: 1 = patina sin parar, 0 = frena en seco
vidas = VIDAS_MAX
angulo = 0              # ángulo con el que se dibuja
angulo_objetivo = 0     # ángulo al que queremos llegar
velocidad_giro = 15     # maximo de grados que gira en cada frame
inclinacion = 0         # 0 = nave recta, 1 = totalmente ladeada al girar
invulnerable_hasta = 0  # despues de un golpe parpadea y no recibe daño
dash_hasta = 0          # el dash esta activo hasta este momento
dash_listo = 0          # desde este momento se puede volver a usar
dash_pedido_en = -10000 # ultima vez que se apreto el dash (para el buffer)
dash_avisado = True     # si ya destello la nave avisando que el dash esta listo
fantasmas = []          # copias de la nave que deja el dash: [x, y, angulo, vida]

# Puntaje
puntaje = 0
combo = 0               # monedas seguidas sin dejar pasar mucho tiempo
mejor_combo = 0
ultima_moneda = -10000
monedas_recogidas = 0
nivel = 1
tiempo_cartel_nivel = -10000
record_superado = False
tiempo_moneda = -1000   # ultima moneda (para iluminar el puntaje)
tiempo_golpe = -1000    # ultimo golpe (para hacer parpadear las vidas)

# Moneda
mx, my = 400, 300

# Power-ups
powerup_tipo = None     # power-up que hay en pantalla (None = ninguno)
px, py = 0, 0           # centro del power-up (cae desde arriba)
proximo_powerup = 0     # momento en que aparece el siguiente
escudo_hasta = 0        # cada efecto esta activo hasta ese momento
hielo_hasta = 0
iman_hasta = 0
doble_hasta = 0
turbo_activo = False    # estos dos duran hasta perder una vida
recarga_activa = False

# Enemigos (se crean en reiniciar_partida)
enemigos = []
enemigos_guardados = []     # durante la pelea con el jefe los enemigos se guardan aca

# Jefe
jefe_activo = False
jefe_x, jefe_y = 340, -130  # esquina de arriba a la izquierda del sprite (120x120)
jefe_fase = "entrar"        # entrar, flotar, atacar, cansado, morir
jefe_fase_hasta = 0         # momento en que termina la fase (en flotar, cansado y morir)
jefe_vida = 0
jefe_vida_max = 0
jefe_golpe_hasta = 0        # destello blanco despues de recibir un golpe
jefe_ataque = "anillo"      # ultimo ataque que hizo (se van turnando)
jefe_rafagas = 0            # rafagas que le quedan en el ataque actual
jefe_proximo_disparo = 0
jefes_vencidos = 0
tiempo_cartel_jefe = -10000
balas = []                  # balas del jefe: [x, y, vx, vy]

# Records
iniciales = ["A", "A", "A"]
letra_actual = 0
fila_nueva = -1         # fila de la tabla que se acaba de agregar (para resaltarla)

# Efectos visuales
particulas = []         # cada una es un diccionario (ver crear_particula)
textos_flotantes = []   # textos como "+1" que suben y desaparecen
temblor = 0             # frames que le quedan al temblor de pantalla
destello = 0            # frames que le quedan al destello de color
color_destello = BLANCO

# ================================== #
# ============ RECORDS ============= #
# ================================== #

def cargar_records():
    # Lee la tabla de records; si no existe, la crea vacia
    try:
        with open(ARCHIVO_RECORDS, encoding="utf-8") as archivo:
            datos = json.load(archivo)
        tabla = [{"nombre": str(fila["nombre"])[:3], "puntos": int(fila["puntos"])} for fila in datos]
        tabla.sort(key=lambda fila: fila["puntos"], reverse=True)
        return tabla[:5]
    except FileNotFoundError:
        with open(ARCHIVO_RECORDS, "w", encoding="utf-8") as archivo:
            json.dump([], archivo)
        return []
    except (ValueError, KeyError, TypeError):
        # Archivo dañado: se sobrescribe al guardar el proximo record
        return []

def entra_en_tabla(puntos):
    return puntos > 0 and (len(records) < 5 or puntos > records[-1]["puntos"])

def agregar_record(nombre, puntos):
    # Agrega el puntaje, deja los 5 mejores, guarda y devuelve su posicion
    global puntaje_maximo
    nueva = {"nombre": nombre, "puntos": puntos}
    records.append(nueva)
    records.sort(key=lambda fila: fila["puntos"], reverse=True)
    del records[5:]
    with open(ARCHIVO_RECORDS, "w", encoding="utf-8") as archivo:
        json.dump(records, archivo, indent=2)
    puntaje_maximo = records[0]["puntos"]
    for posicion, fila in enumerate(records):
        if fila is nueva:
            return posicion
    return -1

records = cargar_records()
if records:
    puntaje_maximo = records[0]["puntos"]
else:
    puntaje_maximo = 0

# ================================== #
# ============ OPCIONES ============ #
# ================================== #

# Solo las resoluciones que caben en el monitor (80 px de margen para la barra
# de tareas y el titulo de la ventana); la pantalla completa siempre esta
alto_escritorio = pygame.display.get_desktop_sizes()[0][1]
resoluciones = [r for r in RESOLUCIONES if r[0] == "COMPLETA" or r[2] + 80 <= alto_escritorio]

# Opciones elegidas (valores de fabrica; cargar_config los cambia por los guardados)
resolucion_actual = 0   # posicion en la lista 'resoluciones'
volumen = VOLUMEN_MAX
musica_activa = True
efectos_activos = True
aviso_jefe = True       # el jefe muestra hacia donde van a salir sus balas

def cargar_config():
    # Lee las opciones guardadas; si no hay archivo, lo crea con los valores de fabrica
    global resolucion_actual, volumen, musica_activa, efectos_activos, aviso_jefe
    try:
        with open(ARCHIVO_CONFIG, encoding="utf-8") as archivo:
            datos = json.load(archivo)
        nombres = [r[0] for r in resoluciones]
        if datos.get("resolucion") in nombres:
            resolucion_actual = nombres.index(datos["resolucion"])
        volumen = min(max(int(datos.get("volumen", VOLUMEN_MAX)), 0), VOLUMEN_MAX)
        musica_activa = bool(datos.get("musica", True))
        efectos_activos = bool(datos.get("efectos", True))
        aviso_jefe = bool(datos.get("aviso_jefe", True))
    except FileNotFoundError:
        guardar_config()
    except (ValueError, TypeError, AttributeError):
        pass    # archivo dañado: se usan los valores de fabrica

def guardar_config():
    with open(ARCHIVO_CONFIG, "w", encoding="utf-8") as archivo:
        json.dump({"resolucion": resoluciones[resolucion_actual][0], "volumen": volumen,
                   "musica": musica_activa, "efectos": efectos_activos,
                   "aviso_jefe": aviso_jefe}, archivo, indent=2)

def aplicar_volumen():
    # set_volume va de 0 a 1; desactivar la musica o los efectos es dejarlos en 0
    nivel_volumen = volumen / VOLUMEN_MAX
    if musica_activa:
        musica_fondo.set_volume(nivel_volumen)
    else:
        musica_fondo.set_volume(0)
    for sonido in efectos_sonido:
        if efectos_activos:
            sonido.set_volume(nivel_volumen)
        else:
            sonido.set_volume(0)

def cambiar_opcion(fila, direccion):
    # Cambia el valor de una fila del menu de Opciones (direccion: -1 o 1),
    # lo aplica al instante y lo guarda
    global resolucion_actual, volumen, musica_activa, efectos_activos, aviso_jefe
    if fila == "RESOLUCION":
        resolucion_actual = (resolucion_actual + direccion) % len(resoluciones)
        aplicar_resolucion()
    elif fila == "VOLUMEN":
        volumen = min(max(volumen + direccion, 0), VOLUMEN_MAX)
    elif fila == "MUSICA":
        musica_activa = not musica_activa
    elif fila == "EFECTOS":
        efectos_activos = not efectos_activos
    elif fila == "AVISO JEFE":
        aviso_jefe = not aviso_jefe
    aplicar_volumen()
    guardar_config()
    sonido_seleccion.play()

def aplicar_resolucion():
    # Abre la ventana con la resolucion elegida
    global ventana
    nombre, ancho, alto = resoluciones[resolucion_actual]
    if nombre == "COMPLETA":
        ventana = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        pygame.mouse.set_visible(False)
    else:
        ventana = pygame.display.set_mode((ancho, alto))
        # Al salir de pantalla completa la ventana vuelve a su tamaño anterior
        # y no al pedido; pedirlo otra vez lo corrige
        if ventana.get_size() != (ancho, alto):
            ventana = pygame.display.set_mode((ancho, alto))
        pygame.mouse.set_visible(True)

def mostrar():
    # Escala el lienzo de 800x600 a la ventana (sin suavizar, pixeles nitidos),
    # centrado y con barras negras si sobra espacio. Reemplaza a display.flip()
    ancho_ventana, alto_ventana = ventana.get_size()
    escala = min(ancho_ventana / 800, alto_ventana / 600)
    if escala == 1:
        ventana.blit(pantalla, (0, 0))
    else:
        ancho, alto = int(800 * escala), int(600 * escala)
        ventana.fill((0, 0, 0))
        ventana.blit(pygame.transform.scale(pantalla, (ancho, alto)),
                     ((ancho_ventana - ancho) // 2, (alto_ventana - alto) // 2))
    pygame.display.flip()

cargar_config()
aplicar_resolucion()
aplicar_volumen()

# ================================== #
# ============= MANDO ============== #
# ================================== #

# Mandos conectados, por su numero de instancia. pygame avisa con JOYDEVICEADDED
# por cada mando (tambien los que ya estaban enchufados al abrir el juego)
mandos = {}
stick_antes = [0, 0]    # direccion del stick en el frame anterior (para los menus)

def hay_mando():
    return len(mandos) > 0

def ayuda(con_teclado, con_mando):
    # Texto de ayuda segun lo que se este usando
    if hay_mando():
        return con_mando
    return con_teclado

def direccion_stick(valor):
    # -1, 0 o 1 segun hacia donde este inclinado (ignora inclinaciones chicas)
    if valor < -ZONA_MUERTA:
        return -1
    if valor > ZONA_MUERTA:
        return 1
    return 0

def direccion_mando():
    # Direccion para mover la nave: la cruceta va en 8 direcciones, como las flechas,
    # y el stick izquierdo en cualquier angulo
    for mando in mandos.values():
        if mando.get_numhats() > 0:
            cruceta_x, cruceta_y = mando.get_hat(0)
            if cruceta_x != 0 or cruceta_y != 0:
                return cruceta_x, -cruceta_y        # en la cruceta, arriba es +1
        if mando.get_numaxes() >= 2:
            stick_x = mando.get_axis(0)
            stick_y = mando.get_axis(1)
            # Se mide la inclinacion total (en circulo), asi ninguna direccion es mas sensible
            if math.hypot(stick_x, stick_y) > ZONA_MUERTA_NAVE:
                return stick_x, stick_y
    return 0, 0

def evento_mando(evento, teclas_pulsadas):
    # Convierte botones, cruceta y stick en teclas de un toque (para los menus y la pausa)
    global pausa_automatica
    if evento.type == pygame.JOYDEVICEADDED:
        mando = pygame.joystick.Joystick(evento.device_index)
        mandos[mando.get_instance_id()] = mando
    elif evento.type == pygame.JOYDEVICEREMOVED:
        # Si se desconecta en medio de la partida, el juego se pausa solo
        if evento.instance_id in mandos and estado in ("Listo", "Jugando"):
            pausa_automatica = True
        mandos.pop(evento.instance_id, None)
    elif evento.type == pygame.JOYBUTTONDOWN:
        if evento.button == BOTON_B and estado == "Jugando":
            return      # B no pausa en medio del juego
        if evento.button in BOTONES_MANDO:
            teclas_pulsadas.append(BOTONES_MANDO[evento.button])
    elif evento.type == pygame.JOYHATMOTION:
        cruceta_x, cruceta_y = evento.value
        if cruceta_x == -1:
            teclas_pulsadas.append(pygame.K_LEFT)
        elif cruceta_x == 1:
            teclas_pulsadas.append(pygame.K_RIGHT)
        if cruceta_y == 1:
            teclas_pulsadas.append(pygame.K_UP)
        elif cruceta_y == -1:
            teclas_pulsadas.append(pygame.K_DOWN)
    elif evento.type == pygame.JOYAXISMOTION and evento.axis in (0, 1):
        # El stick cuenta como una tecla solo cuando recien se inclina
        direccion = direccion_stick(evento.value)
        if direccion != stick_antes[evento.axis]:
            if evento.axis == 0 and direccion == -1:
                teclas_pulsadas.append(pygame.K_LEFT)
            elif evento.axis == 0 and direccion == 1:
                teclas_pulsadas.append(pygame.K_RIGHT)
            elif evento.axis == 1 and direccion == -1:
                teclas_pulsadas.append(pygame.K_UP)
            elif evento.axis == 1 and direccion == 1:
                teclas_pulsadas.append(pygame.K_DOWN)
        stick_antes[evento.axis] = direccion

def vibrar(suave, fuerte, ms):
    # Vibracion de todos los mandos: dos motores de 0 a 1 (suave = grave, fuerte = agudo)
    for mando in mandos.values():
        mando.rumble(suave, fuerte, ms)

# ================================== #
# ============ DIBUJO ============== #
# ================================== #

def dibujar_fondo():
    pantalla.fill(FONDO)
    # Mientras se juega, el fondo se corre al reves de la nave (en los menus solo cae)
    if estado == "Jugando":
        empuje_x = -vx * REACCION_PARALAJE
        empuje_y = -vy * REACCION_PARALAJE
    else:
        empuje_x, empuje_y = 0, 0

    # Nebulosas y planetas: cuanto mas profundos, mas lento se mueven
    for objeto in objetos_fondo:
        imagen, profundidad = objeto[0], objeto[3]
        ancho, alto = imagen.get_size()
        objeto[1] += empuje_x * profundidad
        objeto[2] += (0.6 + empuje_y) * profundidad
        # Si sale por un costado entra por el otro
        if objeto[1] < -ancho:
            objeto[1] = 800
        elif objeto[1] > 800:
            objeto[1] = -ancho
        # Si sale por arriba o por abajo vuelve por el otro lado, en otro lugar
        if objeto[2] > 600:
            objeto[1] = random.randint(-ancho // 2, 800 - ancho // 2)
            objeto[2] = -alto
        elif objeto[2] < -alto:
            objeto[1] = random.randint(-ancho // 2, 800 - ancho // 2)
            objeto[2] = 600
        pantalla.blit(imagen, (int(objeto[1]), int(objeto[2])))

    # Estrellas cuadradas (pixeles); las rapidas son mas grandes, brillantes y cercanas
    for estrella in estrellas:
        estrella[0] += empuje_x * estrella[2]
        estrella[1] += (0.6 + empuje_y) * estrella[2]
        if estrella[0] < 0:
            estrella[0] += 800
        elif estrella[0] > 800:
            estrella[0] -= 800
        if estrella[1] > 600:
            estrella[0] = random.randint(0, 800)
            estrella[1] = 0
        elif estrella[1] < 0:
            estrella[0] = random.randint(0, 800)
            estrella[1] = 600
        brillo = 60 + estrella[2] * 60
        tamano = 1 if estrella[2] < 3 else 2
        pantalla.fill((brillo, brillo, brillo), (int(estrella[0]), int(estrella[1]), tamano, tamano))

def texto(mensaje, fuente_usada, color, x, y, sombra=(0, 0, 0), alinear="centro"):
    # Dibuja texto pixelado con una sombra solida abajo a la derecha
    imagen = fuente_usada.render(mensaje, False, color)
    rect = imagen.get_rect()
    if alinear == "centro":
        rect.center = (x, y)
    elif alinear == "izquierda":
        rect.midleft = (x, y)
    else:
        rect.midright = (x, y)
    if sombra:
        desplazamiento = max(2, fuente_usada.get_height() // 10)
        pantalla.blit(fuente_usada.render(mensaje, False, sombra), rect.move(desplazamiento, desplazamiento))
    pantalla.blit(imagen, rect)

def texto_3d(mensaje, fuente_usada, color, color_relieve, y, profundidad=6):
    # Apila copias del texto hacia abajo para que parezca que tiene grosor
    for i in range(profundidad, 0, -1):
        texto(mensaje, fuente_usada, color_relieve, 400 + i, y + i, sombra=None)
    texto(mensaje, fuente_usada, color, 400, y, sombra=None)

def marco(rect, color):
    # Recuadro de doble linea, como las pantallas de arcade
    pygame.draw.rect(pantalla, FONDO, rect)
    pygame.draw.rect(pantalla, color, rect, 4)
    pygame.draw.rect(pantalla, color, rect.inflate(-14, -14), 2)

def dibujar_opcion(mensaje, fuente_usada, x, y, elegida, alinear="centro"):
    # Opcion de un menu: la elegida va en amarillo con una flecha que parpadea
    if not elegida:
        texto(mensaje, fuente_usada, GRIS, x, y, alinear=alinear)
        return
    texto(mensaje, fuente_usada, AMARILLO, x, y, alinear=alinear)
    if parpadeo(250):
        izquierda = x
        if alinear == "centro":
            izquierda = x - fuente_usada.size(mensaje)[0] // 2
        punta = izquierda - 14
        lado = fuente_usada.get_height() // 3
        pygame.draw.polygon(pantalla, AMARILLO, [(punta - lado, y - lado), (punta - lado, y + lado), (punta, y)])

def numero_arcade(numero):
    # 42 -> "000042"
    return str(numero).zfill(6)

def parpadeo(intervalo=400):
    # True y False alternados cada 'intervalo' milisegundos
    return pygame.time.get_ticks() // intervalo % 2 == 0

def color_arcoiris():
    # Cambia de color cada 100 milisegundos
    return ARCOIRIS[pygame.time.get_ticks() // 100 % len(ARCOIRIS)]

def efecto_crt():
    pantalla.blit(lineas_crt, (0, 0))

def dibujar_capsula(tipo, centro_x, centro_y):
    # Sprite de la capsula; si no hay, cuadro con borde de color y la letra adentro
    if tipo in CAPSULAS:
        pantalla.blit(CAPSULAS[tipo], CAPSULAS[tipo].get_rect(center=(centro_x, centro_y)))
        return
    letra, color = POWERUPS[tipo][0], POWERUPS[tipo][1]
    rect = pygame.Rect(0, 0, 30, 30)
    rect.center = (centro_x, centro_y)
    pygame.draw.rect(pantalla, FONDO, rect)
    pygame.draw.rect(pantalla, color, rect, 3)
    texto(letra, fuente_chica, color, centro_x + 1, centro_y + 1, sombra=None)

def imagen_moneda():
    # La moneda girando: con la animacion si existe; si no, su ancho sube y baja de a 2 pixeles
    if MONEDA_CUADROS:
        return cuadro_animado(MONEDA_CUADROS, MS_CUADRO_MONEDA)
    ancho = max(4, int(abs(math.cos(pygame.time.get_ticks() / 180)) * 10) * 2)
    imagen = pygame.Surface((20, 20), pygame.SRCALPHA)
    pygame.draw.ellipse(imagen, AMARILLO, (10 - ancho // 2, 0, ancho, 20))
    return imagen

def dibujar_moneda():
    imagen = imagen_moneda()
    pantalla.blit(imagen, imagen.get_rect(center=(int(mx) + 10, int(my) + 10)))

def dibujar_nave():
    ahora = tiempo_juego
    # Escudo: burbuja alrededor de la nave (parpadea cuando se esta acabando)
    if ahora < escudo_hasta and (escudo_hasta - ahora > 1500 or parpadeo(100)):
        if ESCUDO_CUADROS:
            burbuja = cuadro_animado(ESCUDO_CUADROS, MS_CUADRO_ESCUDO)
            pantalla.blit(burbuja, burbuja.get_rect(center=(int(x + 25), int(y + 25))))
        else:
            pygame.draw.circle(pantalla, CIAN, (int(x + 25), int(y + 25)), 36, 3)
    # Si es invulnerable, parpadea
    if ahora < invulnerable_hasta and not parpadeo(60):
        return
    # Al ladearse se ve mas angosta (hasta un 35%)
    ancho = round(50 * (1 - inclinacion * 0.35))
    nave = pygame.transform.scale(jugador_img, (ancho, 50))
    nave = pygame.transform.rotate(nave, angulo)
    # Casi quieta, flota subiendo y bajando de a 2 pixeles
    flotar = 0
    if math.hypot(vx, vy) < 1:
        flotar = round(math.sin(pygame.time.get_ticks() / 250)) * 2
    pantalla.blit(nave, nave.get_rect(center=(x + 25, y + 25 + flotar)))

def dibujar_fantasmas():
    # Copias cian de la nave que deja el dash; se apagan poco a poco
    for fantasma in fantasmas:
        imagen = pygame.transform.rotate(nave_fantasma_img, fantasma[2])
        imagen.set_alpha(fantasma[3] * 18)
        pantalla.blit(imagen, imagen.get_rect(center=(fantasma[0] + 25, fantasma[1] + 25)))

def dibujar_hud():
    ahora = tiempo_juego

    # Puntaje (izquierda): se pone amarillo un instante al recoger una moneda
    texto("PUNTOS", fuente_chica, ROJO, 20, 22, alinear="izquierda")
    if ahora - tiempo_moneda < 200:
        texto(numero_arcade(puntaje), fuente_chica, AMARILLO, 20, 46, alinear="izquierda")
    else:
        texto(numero_arcade(puntaje), fuente_chica, BLANCO, 20, 46, alinear="izquierda")

    # Combo (debajo del puntaje) con una barra del tiempo que le queda
    if combo >= 2:
        if multiplicador_combo() > 1:
            texto("COMBO x" + str(multiplicador_combo()), fuente_chica, color_arcoiris(), 20, 72, alinear="izquierda")
        else:
            texto("COMBO " + str(combo), fuente_chica, GRIS, 20, 72, alinear="izquierda")
        restante = max(0, 1 - (ahora - ultima_moneda) / COMBO_TIEMPO)
        pantalla.fill(AMARILLO, (20, 86, int(128 * restante), 4))

    # Record (centro): se actualiza en vivo si lo estas superando
    texto("RECORD", fuente_chica, ROJO, 400, 22)
    if puntaje > puntaje_maximo:
        texto(numero_arcade(puntaje), fuente_chica, AMARILLO, 400, 46)
    else:
        texto(numero_arcade(puntaje_maximo), fuente_chica, BLANCO, 400, 46)

    # Nivel y dash (abajo a la derecha)
    texto("NIVEL " + str(nivel), fuente_chica, AMARILLO, 780, 575, alinear="derecha")
    if ahora >= dash_listo:
        texto("DASH", fuente_chica, CIAN, 780, 545, alinear="derecha")
    else:
        texto("DASH", fuente_chica, GRIS, 780, 545, alinear="derecha")
        # max(0, ...) por si RECARGA cambia a mitad de una recarga
        cargado = max(0, 1 - (dash_listo - ahora) / recarga_dash())
        pantalla.fill(CIAN, (716, 557, int(64 * cargado), 3))

    # Vidas (derecha): parpadean despues de recibir un golpe
    texto("VIDAS", fuente_chica, ROJO, 780, 22, alinear="derecha")
    if ahora - tiempo_golpe < 800 and parpadeo(80):
        return
    for i in range(VIDAS_MAX):
        icono_x = 780 - VIDAS_MAX * 28 + 3 + i * 28
        if i < vidas:
            pantalla.blit(nave_icono, (icono_x, 34))
        else:
            pantalla.blit(nave_icono_vacia, (icono_x, 34))

def dibujar_efectos_activos():
    # Abajo a la izquierda: power-ups activos con los segundos que les quedan
    ahora = tiempo_juego
    activos = [
        ("ESCUDO", CIAN, escudo_hasta),
        ("HIELO", HIELO, hielo_hasta),
        ("IMAN", MAGENTA, iman_hasta),
        ("DOBLE", VERDE, doble_hasta),
    ]
    fila_y = 575
    for nombre, color, hasta in activos:
        if ahora < hasta:
            segundos = int((hasta - ahora) // 1000) + 1
            texto(nombre + " " + str(segundos), fuente_chica, color, 20, fila_y, alinear="izquierda")
            fila_y -= 26
    # Los que duran hasta perder una vida van sin segundos
    if turbo_activo:
        texto("TURBO", fuente_chica, AMARILLO, 20, fila_y, alinear="izquierda")
        fila_y -= 26
    if recarga_activa:
        texto("RECARGA", fuente_chica, CIAN, 20, fila_y, alinear="izquierda")

def dibujar_escena(con_nave=True):
    # Todo lo que se ve mientras se juega (tambien se usa en READY y en la explosion)
    dibujar_fondo()
    dibujar_moneda()
    # Power-up cayendo
    if powerup_tipo is not None:
        dibujar_capsula(powerup_tipo, px, py)
    for enemigo in enemigos:
        enemigo.dibujar()
    if jefe_activo:
        dibujar_jefe()
    dibujar_balas()
    dibujar_fantasmas()
    if con_nave:
        dibujar_nave()
    dibujar_efectos()
    dibujar_hud()
    dibujar_efectos_activos()
    if jefe_activo:
        dibujar_barra_jefe()
    # Carteles al subir de nivel y al vencer al jefe
    if tiempo_juego - tiempo_cartel_nivel < 1500:
        texto_3d("NIVEL " + str(nivel), fuente_grande, AMARILLO, MAGENTA, 250, 4)
    if tiempo_juego - tiempo_cartel_jefe < CARTEL_JEFE:
        texto_3d("¡JEFE VENCIDO!", fuente_grande, color_arcoiris(), MAGENTA, 300, 4)

def dibujar_tabla_records(y_titulo, resaltar=-1):
    texto("MEJORES PUNTAJES", fuente_chica, ROJO, 400, y_titulo)
    for i in range(5):
        fila_y = y_titulo + 32 + i * 26
        if i < len(records):
            linea = str(i + 1) + ". " + records[i]["nombre"] + "  " + numero_arcade(records[i]["puntos"])
            if i == resaltar:
                color = color_arcoiris()
            elif i == 0:
                color = AMARILLO
            else:
                color = BLANCO
        else:
            linea = str(i + 1) + ". ---  ------"
            color = GRIS
        texto(linea, fuente_chica, color, 400, fila_y)

# ================================== #
# =========== PARTICULAS =========== #
# ================================== #

def crear_particula(pos_x, pos_y, vx, vy, paleta, vida, tamano):
    particulas.append({
        "x": pos_x, "y": pos_y,     # posicion
        "vx": vx, "vy": vy,         # velocidad
        "paleta": paleta,           # colores por los que va pasando
        "vida": vida,               # frames que le quedan
        "vida_inicial": vida,
        "tamano": tamano,           # lado del cuadrado en pixeles
    })

def crear_explosion(cx, cy, paleta, cantidad, fuerza, tamano=4):
    # Lanza particulas en todas direcciones desde (cx, cy)
    for i in range(cantidad):
        direccion = random.uniform(0, 2 * math.pi)
        rapidez_p = random.uniform(fuerza * 0.3, fuerza)
        crear_particula(cx, cy, math.cos(direccion) * rapidez_p, math.sin(direccion) * rapidez_p,
                        paleta, random.randint(20, 40), tamano)

def crear_anillo(cx, cy, paleta, cantidad, fuerza, tamano=3):
    # Como la explosion, pero todas a la misma velocidad: forma un circulo que crece
    for i in range(cantidad):
        direccion = 2 * math.pi * i / cantidad
        crear_particula(cx, cy, math.cos(direccion) * fuerza, math.sin(direccion) * fuerza,
                        paleta, 22, tamano)

def crear_texto_flotante(mensaje, tx, ty, color):
    textos_flotantes.append({"texto": mensaje, "x": tx, "y": ty, "color": color, "vida": 45})

def actualizar_efectos():
    for particula in particulas[:]:
        particula["x"] += particula["vx"]
        particula["y"] += particula["vy"]
        particula["vx"] *= 0.92     # friccion: se van frenando
        particula["vy"] *= 0.92
        particula["vida"] -= 1
        if particula["vida"] <= 0:
            particulas.remove(particula)
    for flotante in textos_flotantes[:]:
        flotante["y"] -= 1
        flotante["vida"] -= 1
        if flotante["vida"] <= 0:
            textos_flotantes.remove(flotante)

def dibujar_efectos():
    for particula in particulas:
        # El color y el tamano bajan por etapas segun la vida que le queda
        fraccion = particula["vida"] / particula["vida_inicial"]
        paleta = particula["paleta"]
        color = paleta[min(int(fraccion * len(paleta)), len(paleta) - 1)]
        tamano = max(1, math.ceil(particula["tamano"] * fraccion))
        # Se alinea a una cuadricula de 2 pixeles para que se vea pixelado
        pantalla.fill(color, (int(particula["x"]) // 2 * 2, int(particula["y"]) // 2 * 2, tamano, tamano))
    for flotante in textos_flotantes:
        # Parpadea en sus ultimos frames
        if flotante["vida"] > 12 or flotante["vida"] // 3 % 2 == 0:
            texto(flotante["texto"], fuente_chica, flotante["color"], flotante["x"], flotante["y"])

def estela_nave(cx, cy, angulo_nave, cantidad=1):
    # Fuego que sale por la parte de atras de la nave
    frente_x = -math.sin(math.radians(angulo_nave))
    frente_y = -math.cos(math.radians(angulo_nave))
    for i in range(cantidad):
        salida_x = cx - frente_x * 26 + random.uniform(-4, 4)
        salida_y = cy - frente_y * 26 + random.uniform(-4, 4)
        crear_particula(salida_x, salida_y,
                        -frente_x * random.uniform(1, 2.5), -frente_y * random.uniform(1, 2.5),
                        FUEGO, random.randint(8, 16), random.choice([2, 4]))

def sacudir_pantalla(frames, color=None):
    # Temblor de pantalla y, si se da un color, un destello
    global temblor, destello, color_destello
    temblor = max(temblor, frames)
    if color:
        destello = 4
        color_destello = color

def aplicar_temblor_y_destello():
    global temblor, destello
    if destello > 0:
        velo = pygame.Surface((800, 600))
        velo.fill(color_destello)
        velo.set_alpha(70)
        pantalla.blit(velo, (0, 0))
        destello -= 1
    if temblor > 0:
        # Mueve toda la imagen unos pixeles (siempre en pasos de 2, estilo retro)
        copia = pantalla.copy()
        pantalla.fill(FONDO)
        pantalla.blit(copia, (random.randint(-3, 3) * 2, random.randint(-3, 3) * 2))
        temblor -= 1

def reiniciar_efectos():
    global temblor, destello
    particulas.clear()
    textos_flotantes.clear()
    temblor, destello = 0, 0

# ================================== #
# ============ ENEMIGOS ============ #
# ================================== #

def lugar_lejos_del_jugador():
    # Busca un lugar lejos del jugador (y fuera del marcador de arriba)
    while True:
        nuevo_x = random.randint(0, 760)
        nuevo_y = random.randint(70, 560)
        if math.hypot(nuevo_x - x, nuevo_y - y) > 300:
            return nuevo_x, nuevo_y

def factor_velocidad():
    # Desde el nivel 6 todos los enemigos se aceleran un poco por nivel
    return min(1 + max(0, nivel - 5) * 0.08, 1.5)

class Enemigo:
    # Tipos:
    #   perseguidor: va hacia ti con inercia (hace curvas y se pasa de largo)
    #   rebotador:   va en linea recta y rebota en los bordes
    #   embestidor:  se acerca lento, avisa parpadeando y embiste en linea recta
    def __init__(self, tipo):
        self.tipo = tipo
        self.desfase = random.randint(0, 1000)  # para que no se animen todos al mismo tiempo
        self.reaparecer()

    def reaparecer(self):
        self.x, self.y = lugar_lejos_del_jugador()
        self.vx, self.vy = 0, 0
        # Antes de aparecer se ve una "X" de aviso y no hace nada
        self.aparece_en = tiempo_juego + AVISO_APARICION
        self.fase = "acercarse"         # solo para el embestidor
        self.fase_hasta = self.aparece_en + random.randint(2000, 3500)
        self.rumbo = random.uniform(0, 2 * math.pi)     # hacia donde deambula el embestidor
        if self.tipo == "rebotador":
            direccion = math.radians(random.choice([45, 135, 225, 315]) + random.randint(-15, 15))
            self.vx = math.cos(direccion) * 3
            self.vy = math.sin(direccion) * 3

    def activo(self):
        return tiempo_juego >= self.aparece_en

    def caja(self):
        # Caja de daño un poco mas chica que el dibujo
        return pygame.Rect(self.x + 4, self.y + 4, 32, 32)

    def separarse(self):
        # Empuja al enemigo lejos de los otros que tiene muy cerca (mas fuerte mientras mas cerca)
        for otro in enemigos:
            if otro is self or not otro.activo():
                continue
            lejos_x = self.x - otro.x
            lejos_y = self.y - otro.y
            distancia = math.hypot(lejos_x, lejos_y)
            if distancia >= SEPARACION_ENEMIGOS:
                continue
            if distancia == 0:
                # Justo en el mismo lugar: se separan hacia un lado al azar
                angulo_azar = random.uniform(0, 2 * math.pi)
                lejos_x, lejos_y, distancia = math.cos(angulo_azar), math.sin(angulo_azar), 1
            fuerza = (1 - distancia / SEPARACION_ENEMIGOS) * FUERZA_SEPARACION
            self.vx += lejos_x / distancia * fuerza
            self.vy += lejos_y / distancia * fuerza

    def actualizar(self, congelado):
        if not self.activo() or congelado:
            return
        dir_x = (x + 25) - (self.x + 20)
        dir_y = (y + 25) - (self.y + 20)
        distancia = math.hypot(dir_x, dir_y)

        if self.tipo == "perseguidor":
            rapidez = min(2 + (nivel - 1) * 0.3, 3.5) * factor_velocidad()
            if distancia > 0:
                self.vx += (dir_x / distancia * rapidez - self.vx) * 0.05
                self.vy += (dir_y / distancia * rapidez - self.vy) * 0.05
            self.separarse()
            paso = 1
        elif self.tipo == "rebotador":
            paso = factor_velocidad()
        else:
            paso = 1
            if self.fase == "acercarse":
                if 0 < distancia < RANGO_EMBESTIDOR:
                    # Te tiene cerca: va hacia ti
                    rapidez = 1.2 * factor_velocidad()
                    self.vx += (dir_x / distancia * rapidez - self.vx) * 0.05
                    self.vy += (dir_y / distancia * rapidez - self.vy) * 0.05
                else:
                    # Estas lejos: deambula despacio y de vez en cuando cambia de rumbo
                    if random.random() < 0.01:
                        self.rumbo = random.uniform(0, 2 * math.pi)
                    if self.x <= 0 or self.x >= 760 or self.y <= 0 or self.y >= 560:
                        # Contra un borde: vuelve hacia el centro de la pantalla
                        self.rumbo = math.atan2(300 - (self.y + 20), 400 - (self.x + 20))
                    self.vx += (math.cos(self.rumbo) * 0.5 - self.vx) * 0.05
                    self.vy += (math.sin(self.rumbo) * 0.5 - self.vy) * 0.05
                self.separarse()
                # Solo embiste si estas dentro del rango (si no, espera a que te acerques)
                if tiempo_juego > self.fase_hasta and distancia < RANGO_EMBESTIDOR:
                    self.fase = "apuntar"
                    self.fase_hasta = tiempo_juego + 600
            elif self.fase == "apuntar":
                # Se queda quieto parpadeando: es el aviso de la embestida
                self.vx, self.vy = 0, 0
                if tiempo_juego > self.fase_hasta and distancia > 0:
                    self.fase = "cargar"
                    self.fase_hasta = tiempo_juego + 500
                    self.vx = dir_x / distancia * 9 * factor_velocidad()
                    self.vy = dir_y / distancia * 9 * factor_velocidad()
            else:
                crear_particula(self.x + 20, self.y + 20, 0, 0, EMBESTIDA, 14, 4)
                if tiempo_juego > self.fase_hasta:
                    self.fase = "acercarse"
                    self.fase_hasta = tiempo_juego + random.randint(2500, 3500)
                    self.vx *= 0.3
                    self.vy *= 0.3

        self.x += self.vx * paso
        self.y += self.vy * paso

        # Bordes: el rebotador rebota; los demas solo se detienen
        if self.x < 0 or self.x > 760:
            if self.tipo == "rebotador":
                self.vx = -self.vx
            else:
                self.vx = 0
        if self.y < 0 or self.y > 560:
            if self.tipo == "rebotador":
                self.vy = -self.vy
            else:
                self.vy = 0
        self.x = max(0, min(self.x, 760))
        self.y = max(0, min(self.y, 560))

    def dibujar(self):
        centro_x, centro_y = int(self.x) + 20, int(self.y) + 20
        if not self.activo():
            # Aviso de aparicion: una X parpadeante del color del enemigo
            if parpadeo(100):
                color = COLOR_ENEMIGO[self.tipo]
                pygame.draw.line(pantalla, color, (centro_x - 14, centro_y - 14), (centro_x + 14, centro_y + 14), 4)
                pygame.draw.line(pantalla, color, (centro_x - 14, centro_y + 14), (centro_x + 14, centro_y - 14), 4)
            return

        restante_hielo = hielo_hasta - tiempo_juego
        if restante_hielo > 0 and (restante_hielo > 1000 or parpadeo(100)):
            # Congelado: azul y con los puntos que da encima
            pantalla.blit(ENEMIGO_CONGELADO[self.tipo], (self.x, self.y))
            texto("+" + str(PUNTOS_ENEMIGO_CONGELADO), fuente_chica, HIELO, centro_x, self.y - 14)
        elif self.tipo == "embestidor" and self.fase == "apuntar" and restante_hielo <= 0:
            # Linea punteada hacia la nave y destellos: va a embestir
            dir_x = (x + 25) - centro_x
            dir_y = (y + 25) - centro_y
            distancia = math.hypot(dir_x, dir_y)
            if distancia > 0 and parpadeo(100):
                for paso in range(24, min(int(distancia), 220), 16):
                    punto_x = centro_x + dir_x / distancia * paso
                    punto_y = centro_y + dir_y / distancia * paso
                    pantalla.fill(ROJO, (int(punto_x) // 2 * 2, int(punto_y) // 2 * 2, 4, 4))
            if embestidor_carga_img is not None:
                pantalla.blit(embestidor_carga_img, (self.x, self.y))
            elif parpadeo(80):
                pantalla.blit(embestidor_blanco_img, (self.x, self.y))
            else:
                pantalla.blit(cuadro_animado(ENEMIGO_CUADROS[self.tipo], MS_CUADRO_ENEMIGO, self.desfase), (self.x, self.y))
        else:
            pantalla.blit(cuadro_animado(ENEMIGO_CUADROS[self.tipo], MS_CUADRO_ENEMIGO, self.desfase), (self.x, self.y))

# ================================== #
# ============== JEFE ============== #
# ================================== #

def iniciar_jefe():
    # Los enemigos explotan y se guardan hasta que venzas al jefe, que baja desde arriba
    global jefe_activo, jefe_x, jefe_y, jefe_fase, jefe_vida, jefe_vida_max, jefe_golpe_hasta
    jefe_activo = True
    jefe_x, jefe_y = 340, -130
    jefe_fase = "entrar"
    jefe_vida_max = JEFE_VIDA + jefes_vencidos
    jefe_vida = jefe_vida_max
    jefe_golpe_hasta = 0
    balas.clear()
    for enemigo in enemigos:
        crear_explosion(enemigo.x + 20, enemigo.y + 20, EMBESTIDA, 20, 4, 3)
    enemigos_guardados.extend(enemigos)
    enemigos.clear()
    sacudir_pantalla(20)

def cambiar_fase_jefe(fase, duracion=0):
    global jefe_fase, jefe_fase_hasta
    jefe_fase = fase
    jefe_fase_hasta = tiempo_juego + duracion

def jefe_congelado():
    # El hielo lo congela, salvo mientras entra o explota
    return tiempo_juego < hielo_hasta and jefe_fase in ("flotar", "atacar", "cansado")

def caja_cuerpo_jefe():
    # Un poco mas chica que el dibujo, para no ser injusta
    return pygame.Rect(jefe_x + 14, jefe_y + 16, 92, 76)

def caja_nucleo_jefe():
    return pygame.Rect(jefe_x + 40, jefe_y + 30, 40, 40)

def direcciones_ataque():
    # Angulos (en radianes) y rapidez de las balas de la proxima rafaga.
    # La usan el disparo y el aviso, asi el aviso muestra justo lo que va a salir
    ojo_x, ojo_y = jefe_x + 60, jefe_y + 92
    rapidez = min(3 + jefes_vencidos * 0.3, 4.5)
    direcciones = []
    if jefe_ataque == "abanico":
        # Hacia la nave, abierto como un abanico
        cantidad = min(5 + jefes_vencidos, 9)
        hacia_nave = math.atan2((y + 25) - ojo_y, (x + 25) - ojo_x)
        for i in range(cantidad):
            direcciones.append(hacia_nave + math.radians((i - (cantidad - 1) / 2) * 14))
    else:
        # Hacia todos lados, un poco mas lento
        cantidad = min(14 + jefes_vencidos * 2, 24)
        giro = jefe_rafagas * math.pi / cantidad    # cada rafaga sale girada: los huecos cambian
        for i in range(cantidad):
            direcciones.append(2 * math.pi * i / cantidad + giro)
        rapidez *= 0.8
    return direcciones, rapidez

def disparar_jefe():
    # Una rafaga desde el ojo: en abanico hacia la nave o en anillo hacia todos lados
    ojo_x, ojo_y = jefe_x + 60, jefe_y + 92
    direcciones, rapidez = direcciones_ataque()
    for direccion in direcciones:
        balas.append([ojo_x, ojo_y, math.cos(direccion) * rapidez, math.sin(direccion) * rapidez])
    crear_anillo(ojo_x, ojo_y, EMBESTIDA, 10, 3, 2)

def actualizar_jefe():
    global jefe_x, jefe_y, jefe_fase_hasta, jefe_ataque, jefe_rafagas, jefe_proximo_disparo
    ahora = tiempo_juego

    # Balas: siguen derecho y desaparecen al salir de la pantalla
    for bala in balas[:]:
        bala[0] += bala[2]
        bala[1] += bala[3]
        if bala[0] < -20 or bala[0] > 820 or bala[1] < -20 or bala[1] > 620:
            balas.remove(bala)
        elif random.random() < 0.3:
            crear_particula(bala[0], bala[1], 0, 0, EMBESTIDA, 8, 2)

    if jefe_congelado():
        # Congelado no se mueve ni ataca, y su fase no avanza
        jefe_fase_hasta += 1000 / 60
        jefe_proximo_disparo += 1000 / 60
        return

    if jefe_fase == "entrar":
        jefe_y += 1.2
        if jefe_y >= 70:
            jefe_y = 70
            cambiar_fase_jefe("flotar", JEFE_FLOTAR)

    elif jefe_fase == "flotar":
        # Va de lado a lado (se acerca de a poco al punto, asi no da saltos)
        objetivo_x = 340 + math.sin(ahora / 700) * 260
        jefe_x += (objetivo_x - jefe_x) * 0.05
        if ahora > jefe_fase_hasta:
            if jefe_ataque == "abanico":
                jefe_ataque = "anillo"
            else:
                jefe_ataque = "abanico"
            jefe_rafagas = JEFE_RAFAGAS
            jefe_proximo_disparo = ahora + 700      # antes de disparar se carga
            cambiar_fase_jefe("atacar")

    elif jefe_fase == "atacar":
        if jefe_rafagas == JEFE_RAFAGAS and random.random() < 0.6:
            # Cargando: chispas que se juntan en el ojo
            chispa_x = jefe_x + 60 + random.randint(-40, 40)
            chispa_y = jefe_y + 92 + random.randint(-30, 30)
            crear_particula(chispa_x, chispa_y, (jefe_x + 60 - chispa_x) * 0.1, (jefe_y + 92 - chispa_y) * 0.1,
                            EMBESTIDA, 12, 2)
        if ahora >= jefe_proximo_disparo:
            if jefe_rafagas > 0:
                disparar_jefe()
                jefe_rafagas -= 1
                jefe_proximo_disparo = ahora + 450
            else:
                # Despues de atacar queda cansado: se le abren las placas
                cambiar_fase_jefe("cansado", JEFE_CANSADO)
                crear_explosion(jefe_x + 60, jefe_y + 50, ORO, 20, 4, 3)

    elif jefe_fase == "cansado":
        if random.random() < 0.2:
            crear_particula(jefe_x + 60 + random.randint(-20, 20), jefe_y + 50 + random.randint(-20, 20),
                            random.uniform(-1, 1), random.uniform(-2, 0), ORO, 12, 2)
        if ahora > jefe_fase_hasta:
            cambiar_fase_jefe("flotar", JEFE_FLOTAR)

    elif jefe_fase == "morir":
        # Explosiones por todo el cuerpo y despues la grande
        if random.random() < 0.35:
            crear_explosion(jefe_x + random.randint(10, 110), jefe_y + random.randint(10, 100), FUEGO, 12, 4, 4)
            sacudir_pantalla(3)
        if ahora > jefe_fase_hasta:
            jefe_explota()

def golpear_jefe():
    # Dash contra el nucleo: le quita una vida y la nave rebota
    global jefe_vida, jefe_golpe_hasta, vx, vy, dash_hasta, invulnerable_hasta, congelar_frames
    nucleo_x, nucleo_y = jefe_x + 60, jefe_y + 50
    jefe_vida -= 1
    jefe_golpe_hasta = tiempo_juego + 300
    vx, vy = empujon(nucleo_x, nucleo_y, 9)
    dash_hasta = 0
    invulnerable_hasta = tiempo_juego + 800     # para alcanzar a alejarse del cuerpo
    sonido_golpe.play()
    crear_explosion(nucleo_x, nucleo_y, ORO, 40, 8, 5)
    crear_anillo(nucleo_x, nucleo_y, ENERGIA, 24, 6)
    sacudir_pantalla(12, BLANCO)
    vibrar(0.5, 0.8, 200)
    congelar_frames = 6
    if jefe_vida <= 0:
        for bala in balas:
            crear_explosion(bala[0], bala[1], EMBESTIDA, 4, 2, 2)
        balas.clear()
        cambiar_fase_jefe("morir", 2000)
    else:
        crear_texto_flotante("¡GOLPE!", nucleo_x, nucleo_y - 50, CIAN)
        cambiar_fase_jefe("flotar", JEFE_FLOTAR)

def jefe_explota():
    # Gran explosion y bonus de puntos (los enemigos vuelven cuando se va el cartel)
    global jefe_activo, jefes_vencidos, congelar_frames, tiempo_cartel_jefe
    centro_x, centro_y = jefe_x + 60, jefe_y + 60
    crear_explosion(centro_x, centro_y, FUEGO, 90, 11, 6)
    crear_explosion(centro_x, centro_y, ORO, 40, 7, 4)
    crear_anillo(centro_x, centro_y, ARCOIRIS, 40, 8, 4)
    sacudir_pantalla(35, BLANCO)
    vibrar(1, 1, 600)
    congelar_frames = 8
    sonido_golpe.play()
    sonido_powerup.play()
    jefes_vencidos += 1
    ganados = sumar_puntos(JEFE_PUNTOS * jefes_vencidos)
    crear_texto_flotante("+" + str(ganados), centro_x, centro_y - 40, AMARILLO)
    tiempo_cartel_jefe = tiempo_juego
    jefe_activo = False
    balas.clear()

def revisar_choques_jefe(caja_jugador):
    ahora = tiempo_juego
    # Dash contra el nucleo descubierto (con la caja grande, para que sea facil acertarle)
    if jefe_fase == "cansado" and ahora < dash_hasta and caja_jugador.colliderect(caja_nucleo_jefe()):
        golpear_jefe()
        return
    if jefe_fase == "morir" or ahora < dash_hasta or ahora < invulnerable_hasta:
        return      # el dash y la invulnerabilidad atraviesan al jefe y sus balas
    for bala in balas:
        if nave_toca_circulo(bala[0], bala[1], RADIO_BALA):
            balas.remove(bala)
            danar_jugador(bala[0], bala[1])
            return
    # Tocar su cuerpo hace daño (congelado no)
    if not jefe_congelado() and nave_toca_rect(caja_cuerpo_jefe()):
        danar_jugador(jefe_x + 60, jefe_y + 60)

def dibujar_jefe():
    if jefe_fase == "atacar":
        animacion = "atacar"
    elif jefe_fase in ("cansado", "morir"):
        animacion = "cansado"
    else:
        animacion = "flotar"
    indice = pygame.time.get_ticks() // MS_CUADRO_JEFE % len(JEFE_ANIMACION[animacion])

    restante_hielo = hielo_hasta - tiempo_juego
    if tiempo_juego < jefe_golpe_hasta and parpadeo(60):
        imagen = JEFE_BLANCO[animacion][indice]
    elif jefe_congelado() and (restante_hielo > 1000 or parpadeo(100)):
        imagen = JEFE_CONGELADO[animacion][indice]
    else:
        imagen = JEFE_ANIMACION[animacion][indice]

    # Flota de a 2 pixeles; al morir tiembla
    dibujo_x, dibujo_y = int(jefe_x), int(jefe_y)
    if jefe_fase == "morir":
        dibujo_x += random.randint(-2, 2) * 2
        dibujo_y += random.randint(-2, 2) * 2
    elif jefe_fase != "entrar" and not jefe_congelado():
        dibujo_y += round(math.sin(pygame.time.get_ticks() / 300)) * 2
    pantalla.blit(imagen, (dibujo_x, dibujo_y))

    # Mientras se carga para atacar, muestra por donde van a salir las balas
    if aviso_jefe and jefe_fase == "atacar" and jefe_rafagas == JEFE_RAFAGAS and not jefe_congelado():
        dibujar_aviso_ataque()

    # Avisos: al entrar y cuando se le puede pegar
    if jefe_fase == "entrar" and parpadeo(200):
        texto_3d("¡CUIDADO!", fuente_grande, ROJO, (110, 0, 30), 330, 4)
    if jefe_fase == "cansado" and parpadeo(200):
        texto("¡DASH!", fuente_chica, CIAN, int(jefe_x) + 60, int(jefe_y) + 132)

def dibujar_aviso_ataque():
    # Abanico: lineas punteadas rojas hacia la nave (como el embestidor).
    # Anillo: rayitas magenta cortas alrededor del ojo, en la direccion de cada bala
    if not parpadeo(100):
        return
    ojo_x, ojo_y = jefe_x + 60, jefe_y + 92
    direcciones = direcciones_ataque()[0]
    if jefe_ataque == "abanico":
        color, desde, hasta, separacion = ROJO, 24, 160, 16
    else:
        color, desde, hasta, separacion = MAGENTA, 20, 44, 8
    for direccion in direcciones:
        for paso in range(desde, hasta + 1, separacion):
            punto_x = ojo_x + math.cos(direccion) * paso
            punto_y = ojo_y + math.sin(direccion) * paso
            pantalla.fill(color, (int(punto_x) // 2 * 2, int(punto_y) // 2 * 2, 4, 4))

def dibujar_balas():
    # Balas pixeladas que cambian de color (en la cuadricula de 2 pixeles)
    if parpadeo(100):
        borde, centro = MAGENTA, BLANCO
    else:
        borde, centro = ROJO, (255, 150, 230)
    for bala in balas:
        bala_x = int(bala[0]) // 2 * 2
        bala_y = int(bala[1]) // 2 * 2
        pantalla.fill(borde, (bala_x - 5, bala_y - 3, 10, 6))
        pantalla.fill(borde, (bala_x - 3, bala_y - 5, 6, 10))
        pantalla.fill(centro, (bala_x - 2, bala_y - 2, 4, 4))

def dibujar_barra_jefe():
    # Abajo al centro: un bloque por cada golpe que le queda
    texto("JEFE", fuente_chica, ROJO, 318, 575, alinear="derecha")
    ancho_bloque = 200 // jefe_vida_max
    for i in range(jefe_vida_max):
        bloque = pygame.Rect(330 + i * ancho_bloque, 567, ancho_bloque - 4, 16)
        if i < jefe_vida:
            pantalla.fill(MAGENTA, bloque)
        else:
            pygame.draw.rect(pantalla, GRIS, bloque, 2)

# ================================== #
# ============= JUEGO ============== #
# ================================== #

def multiplicador_combo():
    # x1 con 1-2 monedas seguidas, x2 con 3-5, x3 con 6-8... hasta x5
    return min(1 + combo // 3, 5)

# Partes de la pantalla tapadas por el HUD: ahi no aparecen monedas
ZONAS_HUD = [
    pygame.Rect(0, 0, 800, 100),        # arriba: puntos, combo, record y vidas
    pygame.Rect(0, 530, 800, 70),       # abajo: dash, nivel y barra del jefe
    pygame.Rect(0, 430, 180, 170),      # abajo a la izquierda: power-ups activos
]

def posicion_libre(ancho, alto):
    # Esquina de arriba a la izquierda, al azar, de algo que no tape el HUD
    while True:
        nueva_x = random.randint(0, 800 - ancho)
        nueva_y = random.randint(0, 600 - alto)
        if pygame.Rect(nueva_x, nueva_y, ancho, alto).collidelist(ZONAS_HUD) == -1:
            return nueva_x, nueva_y

def lugar_moneda():
    # Lugar para la moneda nueva: fuera del HUD, a una distancia que se alcanza antes de
    # que se corte el combo, y lejos de los enemigos y del jefe
    for intento in range(200):
        nueva_x, nueva_y = posicion_libre(20, 20)
        centro_x, centro_y = nueva_x + 10, nueva_y + 10
        distancia = math.hypot(centro_x - (x + 25), centro_y - (y + 25))
        if distancia < MONEDA_DISTANCIA_MIN or distancia > MONEDA_DISTANCIA_MAX:
            continue
        cerca_de_enemigo = False
        for enemigo in enemigos:
            if math.hypot(centro_x - (enemigo.x + 20), centro_y - (enemigo.y + 20)) < 60:
                cerca_de_enemigo = True
        if cerca_de_enemigo:
            continue
        if jefe_activo and caja_cuerpo_jefe().inflate(40, 40).colliderect((nueva_x, nueva_y, 20, 20)):
            continue
        return nueva_x, nueva_y
    return nueva_x, nueva_y     # muy raro: si no encontro un lugar ideal, usa el ultimo

def nave_toca_circulo(centro_x, centro_y, radio):
    # Choque entre el circulo de daño de la nave y otro circulo
    return math.hypot((x + 25) - centro_x, (y + 25) - centro_y) < RADIO_NAVE + radio

def nave_toca_rect(rect):
    # Choque entre el circulo de daño de la nave y un rectangulo:
    # se busca el punto del rectangulo mas cercano al centro de la nave
    cerca_x = max(rect.left, min(x + 25, rect.right))
    cerca_y = max(rect.top, min(y + 25, rect.bottom))
    return math.hypot((x + 25) - cerca_x, (y + 25) - cerca_y) < RADIO_NAVE

def recarga_dash():
    # Con RECARGA el dash vuelve a estar listo mas rapido
    if recarga_activa:
        return RECARGA_RAPIDA
    return DASH_RECARGA

def sumar_puntos(base):
    # Suma puntos (dobles si esta activo el power-up) y avisa si superas el record
    global puntaje, record_superado
    puntos = base
    if tiempo_juego < doble_hasta:
        puntos *= 2
    puntaje += puntos
    if not record_superado and puntaje_maximo > 0 and puntaje > puntaje_maximo:
        record_superado = True
        sonido_nuevo_record.play()
        crear_anillo(x + 25, y + 25, ARCOIRIS, 40, 7, 4)
        crear_texto_flotante("¡NUEVO RECORD!", 400, 140, AMARILLO)
    return puntos

def subir_nivel():
    global nivel, tiempo_cartel_nivel
    nivel += 1
    tiempo_cartel_nivel = tiempo_juego
    sonido_seleccion.play()
    crear_anillo(x + 25, y + 25, ORO, 32, 6)
    if nivel in ENEMIGOS_POR_NIVEL:
        enemigos.append(Enemigo(ENEMIGOS_POR_NIVEL[nivel]))
    if nivel % JEFE_CADA_NIVELES == 0:
        iniciar_jefe()

def empujon(desde_x, desde_y, fuerza=10):
    # Velocidad que aleja a la nave del punto (desde_x, desde_y)
    empuje_x = (x + 25) - desde_x
    empuje_y = (y + 25) - desde_y
    largo = math.hypot(empuje_x, empuje_y)
    if largo == 0:
        return 0, -fuerza
    return empuje_x / largo * fuerza, empuje_y / largo * fuerza

def danar_jugador(golpe_x, golpe_y):
    # Golpe de un enemigo, del jefe o de una bala: rompe el escudo o quita una vida
    global escudo_hasta, vx, vy, vidas, combo, tiempo_golpe, invulnerable_hasta
    global congelar_frames, estado, tiempo_menu, turbo_activo, recarga_activa
    ahora = tiempo_juego
    if ahora < escudo_hasta:
        # El escudo aguanta el golpe y se rompe (medio segundo para alejarse)
        sonido_golpe.play()
        escudo_hasta = 0
        invulnerable_hasta = ahora + 500
        vx, vy = empujon(golpe_x, golpe_y, 7)
        crear_anillo(x + 25, y + 25, ENERGIA, 32, 6)
        crear_explosion(golpe_x, golpe_y, FUEGO, 20, 5)
        sacudir_pantalla(8, CIAN)
        vibrar(0.3, 0.6, 150)
        congelar_frames = 2
        return
    sonido_golpe.play()
    vidas -= 1
    combo = 0
    tiempo_golpe = ahora
    # Al perder una vida se pierden TURBO y RECARGA
    aviso_y = y - 10
    if turbo_activo:
        turbo_activo = False
        crear_texto_flotante("-TURBO", x + 25, aviso_y, AMARILLO)
        aviso_y -= 24
    if recarga_activa:
        recarga_activa = False
        crear_texto_flotante("-RECARGA", x + 25, aviso_y, CIAN)
    vx, vy = empujon(golpe_x, golpe_y)
    invulnerable_hasta = ahora + 1500
    crear_explosion(golpe_x, golpe_y, FUEGO, 35, 7, 5)
    sacudir_pantalla(15, ROJO)
    vibrar(0.7, 1, 300)
    congelar_frames = 4
    if vidas <= 0:
        # Gran explosion de la nave; el Game Over aparece despues
        musica_fondo.stop()
        crear_explosion(x + 25, y + 25, FUEGO, 90, 10, 6)
        crear_explosion(x + 25, y + 25, ORO, 30, 5, 4)
        sacudir_pantalla(35, BLANCO)
        vibrar(1, 1, 700)
        congelar_frames = 8
        estado = "Explosion"
        tiempo_menu = pygame.time.get_ticks()

def reiniciar_partida():
    # Deja todo como al principio y muestra "READY?"
    global x, y, vx, vy, vidas, angulo, angulo_objetivo, inclinacion
    global invulnerable_hasta, dash_hasta, dash_listo, dash_pedido_en, dash_avisado, pausa_automatica
    global puntaje, combo, mejor_combo, ultima_moneda, monedas_recogidas, nivel
    global tiempo_cartel_nivel, record_superado, tiempo_moneda, tiempo_golpe
    global mx, my, powerup_tipo, proximo_powerup, escudo_hasta, hielo_hasta, iman_hasta, doble_hasta
    global tiempo_juego, congelar_frames, enemigos, estado, tiempo_menu
    global jefe_activo, jefes_vencidos, tiempo_cartel_jefe, turbo_activo, recarga_activa
    tiempo_juego = 0
    congelar_frames = 0
    x, y = 100, 200
    vx, vy = 0, 0
    vidas = VIDAS_MAX
    angulo, angulo_objetivo, inclinacion = 0, 0, 0
    invulnerable_hasta, dash_hasta, dash_listo = 0, 0, 0
    dash_pedido_en, dash_avisado = -10000, True
    pausa_automatica = False
    fantasmas.clear()
    puntaje, combo, mejor_combo, monedas_recogidas = 0, 0, 0, 0
    ultima_moneda = -10000
    nivel = 1
    tiempo_cartel_nivel = -10000
    record_superado = False
    tiempo_moneda, tiempo_golpe = -1000, -1000
    mx, my = 400, 300
    powerup_tipo = None
    proximo_powerup = 6000
    escudo_hasta, hielo_hasta, iman_hasta, doble_hasta = 0, 0, 0, 0
    turbo_activo, recarga_activa = False, False
    enemigos = [Enemigo("perseguidor")]
    enemigos_guardados.clear()
    jefe_activo = False
    jefes_vencidos = 0
    tiempo_cartel_jefe = -10000
    balas.clear()
    reiniciar_efectos()
    sonido_seleccion.play()
    musica_fondo.play(-1)
    estado = "Listo"
    tiempo_menu = pygame.time.get_ticks()

# ================================== #
# ========= BUCLE PRINCIPAL ======== #
# ================================== #

while ejecutando:
    # Eventos: guardamos las teclas que se presionaron en este frame
    teclas_pulsadas = []
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            ejecutando = False
            if estado == "Iniciales":
                agregar_record("".join(iniciales), puntaje)     # no perder el record al cerrar
        elif evento.type == pygame.KEYDOWN:
            teclas_pulsadas.append(evento.key)
        elif evento.type == pygame.WINDOWFOCUSLOST:
            # Si cambias de ventana en medio de la partida, el juego se pausa solo
            if estado in ("Listo", "Jugando"):
                pausa_automatica = True
        else:
            evento_mando(evento, teclas_pulsadas)
    if not ejecutando:
        break
    enter = pygame.K_RETURN in teclas_pulsadas or pygame.K_KP_ENTER in teclas_pulsadas
    teclas = pygame.key.get_pressed()

    # ---------- Pantalla de inicio ----------
    if estado == "Inicio":
        dibujar_fondo()

        # Record arriba, como en las maquinas
        texto("RECORD", fuente_chica, ROJO, 400, 22)
        texto(numero_arcade(puntaje_maximo), fuente_chica, BLANCO, 400, 46)

        # Titulo con relieve y la nave flotando (se mueve de a 3 pixeles, estilo retro)
        texto_3d("CAZA", fuente_titulo, AMARILLO, MAGENTA, 115)
        texto_3d("MONEDAS", fuente_titulo, AMARILLO, MAGENTA, 180)
        flotar = round(math.sin(pygame.time.get_ticks() / 300) * 2) * 3
        estela_nave(400, 250 + flotar, 0)
        actualizar_efectos()
        dibujar_efectos()
        pantalla.blit(jugador_img, jugador_img.get_rect(center=(400, 250 + flotar)))

        # Panel que cambia cada 6 segundos: reglas / mejores puntajes
        marco(pygame.Rect(170, 290, 460, 180), CIAN)
        if records and pygame.time.get_ticks() // 6000 % 2 == 1:
            dibujar_tabla_records(315)
        else:
            moneda_panel = imagen_moneda()
            pantalla.blit(moneda_panel, moneda_panel.get_rect(center=(220, 327)))
            texto("RECOGE", fuente_chica, BLANCO, 255, 327, alinear="izquierda")
            texto("+1 PUNTO", fuente_chica, AMARILLO, 600, 327, alinear="derecha")
            enemigo_panel = cuadro_animado(ENEMIGO_CUADROS["perseguidor"], MS_CUADRO_ENEMIGO)
            pantalla.blit(enemigo_panel, enemigo_panel.get_rect(center=(220, 377)))
            texto("ESQUIVA", fuente_chica, BLANCO, 255, 377, alinear="izquierda")
            texto("-1 VIDA", fuente_chica, ROJO, 600, 377, alinear="derecha")
            pygame.draw.line(pantalla, CIAN, (190, 405), (610, 405), 2)

            # Capsulas; una a la vez se explica abajo (cambia cada 2.5 segundos)
            tipos = list(POWERUPS)
            explicado = tipos[pygame.time.get_ticks() // 2500 % len(tipos)]
            for i, tipo in enumerate(tipos):
                capsula_x = 220 + i * 60
                dibujar_capsula(tipo, capsula_x, 437)
                if tipo == explicado:
                    pygame.draw.polygon(pantalla, POWERUPS[tipo][1],
                                        [(capsula_x - 6, 414), (capsula_x + 6, 414), (capsula_x, 420)])
            letra, color, nombre, descripcion = POWERUPS[explicado]
            texto(nombre + ": " + descripcion, fuente_chica, color, 400, 492)

        # Menu: JUGAR / OPCIONES (se elige con izquierda y derecha)
        dibujar_opcion("JUGAR", fuente_media, 270, 530, opcion_inicio == 0)
        dibujar_opcion("OPCIONES", fuente_media, 540, 530, opcion_inicio == 1)
        texto(ayuda("FLECHAS MOVER  ESPACIO DASH  P PAUSA", "STICK MOVER  X DASH  MENU PAUSA"),
              fuente_chica, GRIS, 400, 572)
        efecto_crt()

        if pygame.K_LEFT in teclas_pulsadas or pygame.K_RIGHT in teclas_pulsadas:
            opcion_inicio = 1 - opcion_inicio
        if enter:
            if opcion_inicio == 0:
                reiniciar_partida()
            else:
                sonido_seleccion.play()
                opcion_menu = 0
                volver_a = "Inicio"
                estado = "Opciones"
        mostrar()
        reloj.tick(60)
        continue

    # ---------- READY? GO! ----------
    if estado == "Listo":
        dibujar_escena()
        transcurrido = pygame.time.get_ticks() - tiempo_menu
        if transcurrido < 1000:
            if parpadeo(150):
                texto_3d("READY?", fuente_titulo, AMARILLO, MAGENTA, 300)
        else:
            texto_3d("GO!", fuente_titulo, VERDE, (0, 90, 40), 300)
        efecto_crt()
        if transcurrido > 1600:
            estado = "Jugando"
        mostrar()
        reloj.tick(60)
        continue

    # ---------- Pausa ----------
    if estado == "Pausa":
        pantalla.blit(captura_pausa, (0, 0))
        velo = pygame.Surface((800, 600))
        velo.fill(FONDO)
        velo.set_alpha(160)
        pantalla.blit(velo, (0, 0))
        texto_3d("PAUSA", fuente_titulo, CIAN, (0, 70, 110), 270)
        if parpadeo():
            texto(ayuda("P PARA SEGUIR", "MENU PARA SEGUIR"), fuente_chica, BLANCO, 400, 350)
        texto(ayuda("O OPCIONES", "VISTA OPCIONES"), fuente_chica, GRIS, 400, 385)
        efecto_crt()
        if pygame.K_p in teclas_pulsadas or pygame.K_ESCAPE in teclas_pulsadas:
            pygame.mixer.unpause()
            estado = "Jugando"
        elif pygame.K_o in teclas_pulsadas:
            sonido_seleccion.play()
            opcion_menu = 0
            volver_a = "Pausa"
            estado = "Opciones"
        mostrar()
        reloj.tick(60)
        continue

    # ---------- Opciones ----------
    if estado == "Opciones":
        dibujar_fondo()
        texto_3d("OPCIONES", fuente_titulo, CIAN, (0, 70, 110), 130)

        # Filas del menu (para agregar una opcion nueva, sumarla a la lista)
        filas = ["RESOLUCION", "VOLUMEN", "MUSICA", "EFECTOS", "AVISO JEFE", "VOLVER"]
        marco(pygame.Rect(80, 190, 640, 290), CIAN)
        for i, fila in enumerate(filas):
            fila_y = 230 + i * 45
            dibujar_opcion(fila, fuente_media, 120, fila_y, i == opcion_menu, alinear="izquierda")
            if i == opcion_menu:
                color_valor = AMARILLO
            else:
                color_valor = BLANCO

            # Valor de la fila, a la derecha
            if fila == "RESOLUCION":
                texto("< " + resoluciones[resolucion_actual][0] + " >", fuente_media, color_valor, 700, fila_y, alinear="derecha")
            elif fila == "VOLUMEN":
                # Barra de cuadritos: llenos hasta el volumen actual, el resto solo el borde
                inicio_barra = 660 - VOLUMEN_MAX * 16
                texto("<", fuente_media, color_valor, inicio_barra - 16, fila_y, alinear="derecha")
                texto(">", fuente_media, color_valor, 700, fila_y, alinear="derecha")
                for paso in range(VOLUMEN_MAX):
                    cuadrito = pygame.Rect(inicio_barra + paso * 16, fila_y - 10, 12, 20)
                    if paso < volumen:
                        pantalla.fill(color_valor, cuadrito)
                    else:
                        pygame.draw.rect(pantalla, GRIS, cuadrito, 2)
            elif fila in ("MUSICA", "EFECTOS", "AVISO JEFE"):
                if ((fila == "MUSICA" and musica_activa) or (fila == "EFECTOS" and efectos_activos)
                        or (fila == "AVISO JEFE" and aviso_jefe)):
                    texto("< SI >", fuente_media, color_valor, 700, fila_y, alinear="derecha")
                else:
                    texto("< NO >", fuente_media, GRIS, 700, fila_y, alinear="derecha")

        texto("ARRIBA/ABAJO ELEGIR  IZQ/DER CAMBIAR", fuente_chica, GRIS, 400, 520)
        texto(ayuda("ESC VOLVER", "B VOLVER"), fuente_chica, GRIS, 400, 550)
        efecto_crt()

        # Cada tecla presionada se procesa en orden
        for tecla_pulsada in teclas_pulsadas:
            if estado != "Opciones":
                break
            fila_elegida = filas[opcion_menu]
            if tecla_pulsada == pygame.K_UP:
                opcion_menu = (opcion_menu - 1) % len(filas)
            elif tecla_pulsada == pygame.K_DOWN:
                opcion_menu = (opcion_menu + 1) % len(filas)
            elif tecla_pulsada == pygame.K_RIGHT and fila_elegida != "VOLVER":
                cambiar_opcion(fila_elegida, 1)
            elif tecla_pulsada == pygame.K_LEFT and fila_elegida != "VOLVER":
                cambiar_opcion(fila_elegida, -1)
            elif tecla_pulsada in (pygame.K_RETURN, pygame.K_KP_ENTER) and fila_elegida in ("MUSICA", "EFECTOS", "AVISO JEFE"):
                cambiar_opcion(fila_elegida, 1)     # ENTER tambien prende y apaga
            elif tecla_pulsada == pygame.K_ESCAPE or (
                    tecla_pulsada in (pygame.K_RETURN, pygame.K_KP_ENTER) and fila_elegida == "VOLVER"):
                sonido_seleccion.play()
                estado = volver_a
        mostrar()
        reloj.tick(60)
        continue

    # ---------- Escribir iniciales ----------
    if estado == "Iniciales":
        dibujar_fondo()
        if not records or puntaje > records[0]["puntos"]:
            texto_3d("NUEVO RECORD", fuente_grande, color_arcoiris(), MAGENTA, 110, 4)
        else:
            texto_3d("PUNTAJE ALTO", fuente_grande, AMARILLO, MAGENTA, 110, 4)
        texto("PUNTOS " + numero_arcade(puntaje), fuente_chica, BLANCO, 400, 180)
        texto("ESCRIBE TUS INICIALES", fuente_chica, GRIS, 400, 235)

        # Tres casillas; la actual parpadea y tiene flechas arriba y abajo
        for i in range(3):
            casilla = pygame.Rect(0, 0, 70, 84)
            casilla.center = (320 + i * 80, 330)
            if i == letra_actual:
                if parpadeo(250):
                    marco(casilla, AMARILLO)
                else:
                    marco(casilla, CIAN)
                pygame.draw.polygon(pantalla, AMARILLO, [(casilla.centerx - 10, 278), (casilla.centerx + 10, 278), (casilla.centerx, 266)])
                pygame.draw.polygon(pantalla, AMARILLO, [(casilla.centerx - 10, 382), (casilla.centerx + 10, 382), (casilla.centerx, 394)])
                texto(iniciales[i], fuente_titulo, AMARILLO, casilla.centerx + 3, casilla.centery + 3)
            else:
                marco(casilla, GRIS)
                texto(iniciales[i], fuente_titulo, BLANCO, casilla.centerx + 3, casilla.centery + 3)

        texto("ARRIBA/ABAJO: LETRA", fuente_chica, GRIS, 400, 460)
        texto(ayuda("ENTER: ACEPTAR   IZQ: VOLVER", "A: ACEPTAR   IZQ: VOLVER"), fuente_chica, GRIS, 400, 490)
        efecto_crt()

        # Cada tecla presionada se procesa en orden
        for tecla_pulsada in teclas_pulsadas:
            if estado != "Iniciales":
                break
            posicion = ALFABETO.index(iniciales[letra_actual])
            if tecla_pulsada == pygame.K_UP:
                iniciales[letra_actual] = ALFABETO[(posicion + 1) % len(ALFABETO)]
            elif tecla_pulsada == pygame.K_DOWN:
                iniciales[letra_actual] = ALFABETO[(posicion - 1) % len(ALFABETO)]
            elif tecla_pulsada == pygame.K_LEFT and letra_actual > 0:
                letra_actual -= 1
            elif tecla_pulsada in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_RIGHT):
                sonido_seleccion.play()
                letra_actual += 1
                if letra_actual == 3:
                    fila_nueva = agregar_record("".join(iniciales), puntaje)
                    estado = "Fin"
                    tiempo_menu = pygame.time.get_ticks()
        mostrar()
        reloj.tick(60)
        continue

    # ---------- Game Over ----------
    if estado == "Fin":
        dibujar_fondo()
        actualizar_efectos()
        dibujar_efectos()       # fuegos artificiales detras de todo
        texto_3d("GAME OVER", fuente_titulo, ROJO, (110, 0, 30), 75)

        # Puntaje: cuenta desde cero hasta el resultado en 1.5 segundos
        contador = min(puntaje, int(puntaje * (pygame.time.get_ticks() - tiempo_menu) / 1500))
        if fila_nueva == 0:
            marco(pygame.Rect(220, 125, 360, 125), AMARILLO)
        else:
            marco(pygame.Rect(220, 125, 360, 125), CIAN)
        texto("PUNTOS", fuente_chica, ROJO, 400, 155)
        texto(numero_arcade(contador), fuente_grande, BLANCO, 400, 195)
        texto("MEJOR COMBO " + str(mejor_combo), fuente_chica, GRIS, 400, 230)

        # Nuevo record: texto de colores y fuegos artificiales
        if fila_nueva == 0 and contador == puntaje:
            texto("¡NUEVO RECORD!", fuente_media, color_arcoiris(), 400, 288)
            if random.random() < 0.05:
                paleta = random.choice([FUEGO, ORO, ESCARCHA, ENERGIA, CORAZON])
                crear_explosion(random.randint(80, 720), random.randint(80, 560), paleta, 40, 6)

        dibujar_tabla_records(330, fila_nueva)

        # Mensaje para reintentar (ENTER se ignora el primer momento)
        if parpadeo():
            texto(ayuda("PRESIONA ENTER", "PRESIONA A"), fuente_media, CIAN, 400, 545)
        efecto_crt()

        if enter and pygame.time.get_ticks() - tiempo_menu > 800:
            reiniciar_partida()
        mostrar()
        reloj.tick(60)
        continue

    # ---------- Hit-stop: el juego se detiene unos frames tras un impacto ----------
    if congelar_frames > 0:
        congelar_frames -= 1
        mostrar()
        reloj.tick(60)
        continue

    # ---------- La nave explota ----------
    if estado == "Explosion":
        actualizar_efectos()
        dibujar_escena(con_nave=False)
        aplicar_temblor_y_destello()
        efecto_crt()
        if pygame.time.get_ticks() - tiempo_menu > 1500:
            reiniciar_efectos()
            sonido_game_over.play()
            tiempo_menu = pygame.time.get_ticks()
            if entra_en_tabla(puntaje):
                iniciales = ["A", "A", "A"]
                letra_actual = 0
                estado = "Iniciales"
            else:
                fila_nueva = -1
                estado = "Fin"
        mostrar()
        reloj.tick(60)
        continue

    # ---------- Jugando ----------
    if pausa_automatica or pygame.K_p in teclas_pulsadas or pygame.K_ESCAPE in teclas_pulsadas:
        pausa_automatica = False
        captura_pausa = pantalla.copy()
        pygame.mixer.pause()
        estado = "Pausa"
        continue

    tiempo_juego += 1000 / 60
    ahora = tiempo_juego

    # Teclas de movimiento
    dx = teclas[pygame.K_RIGHT] - teclas[pygame.K_LEFT]
    dy = teclas[pygame.K_DOWN] - teclas[pygame.K_UP]
    if dx == 0 and dy == 0:
        dx, dy = direccion_mando()      # si no hay flechas, se usa el mando
    acelerando = dx != 0 or dy != 0
    if acelerando:
        # Apunta hacia donde presionas (0 = arriba, 90 = izquierda...)
        angulo_objetivo = math.degrees(math.atan2(-dx, -dy)) % 360

    # Con TURBO la nave va mas rapido
    if turbo_activo:
        vel_max = TURBO_VELOCIDAD
    else:
        vel_max = velocidad

    # Dash: impulso hacia donde presionas (o hacia donde mira la nave).
    # Si lo apretas justo antes de que se recargue, se guarda y sale apenas este listo
    if pygame.K_SPACE in teclas_pulsadas:
        dash_pedido_en = ahora
    if ahora - dash_pedido_en <= BUFFER_DASH and ahora >= dash_listo:
        dash_pedido_en = -10000
        dash_avisado = False
        if acelerando:
            largo = math.hypot(dx, dy)
            dash_x, dash_y = dx / largo, dy / largo
        else:
            dash_x = -math.sin(math.radians(angulo))
            dash_y = -math.cos(math.radians(angulo))
        vx, vy = dash_x * DASH_FUERZA, dash_y * DASH_FUERZA
        dash_hasta = ahora + DASH_DURACION
        dash_listo = ahora + recarga_dash()
        crear_anillo(x + 25, y + 25, ENERGIA, 16, 3, 2)
    elif ahora >= dash_listo and not dash_avisado:
        # Destello chico en la nave: el dash ya esta listo
        dash_avisado = True
        crear_anillo(x + 25, y + 25, ENERGIA, 12, 3, 2)

    if ahora < dash_hasta:
        # Durante el dash no hay control: la nave sigue disparada y deja copias
        fantasmas.append([x, y, angulo, 10])
    elif acelerando:
        # Inercia: la velocidad se acerca poco a poco a la deseada
        largo = math.hypot(dx, dy)      # asi en diagonal no va mas rapido
        vx += (dx / largo * vel_max - vx) * aceleracion
        vy += (dy / largo * vel_max - vy) * aceleracion
    else:
        # Al soltar las teclas la nave se desliza un poco antes de frenar
        vx *= friccion
        vy *= friccion
    x += vx
    y += vy

    # Giro suave: rapido al empezar y mas lento al llegar al angulo
    diferencia = (angulo_objetivo - angulo + 180) % 360 - 180
    giro = max(-velocidad_giro, min(diferencia * 0.25, velocidad_giro))
    angulo = (angulo + giro) % 360

    # Inclinacion: mientras mas rapido gira, mas se ladea la nave
    inclinacion += (min(abs(giro) / velocidad_giro, 1) - inclinacion) * 0.2

    # Las copias del dash se van apagando
    for fantasma in fantasmas[:]:
        fantasma[3] -= 1
        if fantasma[3] <= 0:
            fantasmas.remove(fantasma)

    # Limites pantalla (al chocar con un borde se pierde esa velocidad)
    if x < 0 or x > 750:
        vx = 0
    if y < 0 or y > 550:
        vy = 0
    x = max(0, min(x, 750))
    y = max(0, min(y, 550))

    # El combo se corta si pasa mucho tiempo sin monedas
    if combo > 0 and ahora - ultima_moneda > COMBO_TIEMPO:
        combo = 0

    # Iman: la moneda cercana vuela hacia la nave
    if ahora < iman_hasta:
        hacia_x = (x + 25) - (mx + 10)
        hacia_y = (y + 25) - (my + 10)
        distancia = math.hypot(hacia_x, hacia_y)
        if 0 < distancia < 250:
            paso = min(distancia, 6)
            mx += hacia_x / distancia * paso
            my += hacia_y / distancia * paso
            if random.random() < 0.3:
                crear_particula(mx + 10, my + 10, 0, 0, IMANTADO, 10, 2)

    # Caja grande para recoger cosas (el daño usa circulos: nave_toca_circulo / nave_toca_rect)
    caja_jugador = pygame.Rect(x, y, 50, 50)
    caja_moneda = pygame.Rect(int(mx), int(my), 20, 20)

    # Moneda
    if caja_jugador.colliderect(caja_moneda):
        if ahora - ultima_moneda < COMBO_TIEMPO:
            combo += 1
        else:
            combo = 1
        ultima_moneda = ahora
        mejor_combo = max(mejor_combo, combo)
        ganados = sumar_puntos(multiplicador_combo())
        if multiplicador_combo() > 1:
            crear_explosion(mx + 10, my + 10, ARCOIRIS, 20, 5, 3)
        else:
            crear_explosion(mx + 10, my + 10, ORO, 14, 4, 3)
        crear_texto_flotante("+" + str(ganados), mx + 10, my - 6, AMARILLO)
        sonido_moneda.play()
        tiempo_moneda = ahora
        # La moneda nueva aparece a una distancia alcanzable, lejos de enemigos y fuera del HUD
        mx, my = lugar_moneda()
        # Durante la pelea con el jefe las monedas dan puntos pero no suben de nivel
        if not jefe_activo:
            monedas_recogidas += 1
            if monedas_recogidas % MONEDAS_POR_NIVEL == 0:
                subir_nivel()

    # Power-ups: cada 8 a 13 segundos cae uno desde arriba; si no lo recoges, se va por abajo
    if powerup_tipo is None and ahora > proximo_powerup:
        opciones = ["escudo", "hielo", "iman", "doble"]
        if vidas < VIDAS_MAX:
            opciones.append("vida")
        if not turbo_activo:
            opciones.append("turbo")
        if not recarga_activa:
            opciones.append("recarga")
        powerup_tipo = random.choice(opciones)
        px = random.randint(30, 770)
        py = -15                # empieza justo arriba de la pantalla, asi entra cayendo

    if powerup_tipo is not None:
        py += VELOCIDAD_POWERUP
        caja_powerup = pygame.Rect(px - 15, py - 15, 30, 30)
        if caja_jugador.colliderect(caja_powerup):
            sonido_powerup.play()
            nombre = POWERUPS[powerup_tipo][2]
            color = POWERUPS[powerup_tipo][1]
            if powerup_tipo == "escudo":
                escudo_hasta = ahora + DURACION["escudo"]
                crear_anillo(px, py, ENERGIA, 24, 5)
            elif powerup_tipo == "hielo":
                hielo_hasta = ahora + DURACION["hielo"]
                crear_anillo(px, py, ESCARCHA, 24, 5)
                for enemigo in enemigos:
                    crear_explosion(enemigo.x + 20, enemigo.y + 20, ESCARCHA, 20, 3, 3)
                # Las balas del jefe se rompen y el jefe se congela
                for bala in balas:
                    crear_explosion(bala[0], bala[1], ESCARCHA, 4, 2, 2)
                balas.clear()
                if jefe_activo:
                    crear_explosion(jefe_x + 60, jefe_y + 60, ESCARCHA, 40, 5, 4)
            elif powerup_tipo == "iman":
                iman_hasta = ahora + DURACION["iman"]
                crear_anillo(px, py, IMANTADO, 24, 5)
            elif powerup_tipo == "doble":
                doble_hasta = ahora + DURACION["doble"]
                crear_anillo(px, py, TREBOL, 24, 5)
            elif powerup_tipo == "turbo":
                turbo_activo = True
                crear_anillo(px, py, ORO, 24, 5)
            elif powerup_tipo == "recarga":
                recarga_activa = True
                crear_anillo(px, py, ENERGIA, 24, 5)
            else:
                vidas += 1
                nombre = "+1 VIDA"
                crear_anillo(px, py, CORAZON, 24, 5)
            crear_texto_flotante(nombre, px, py - 24, color)
            powerup_tipo = None
            proximo_powerup = ahora + random.randint(8000, 13000)
        elif py > 615:
            # Salio por abajo sin que lo recogieras
            powerup_tipo = None
            proximo_powerup = ahora + random.randint(8000, 13000)

    # Despues del jefe, los enemigos vuelven cuando se va el cartel (asi no quedan tapados)
    if not jefe_activo and enemigos_guardados and ahora - tiempo_cartel_jefe >= CARTEL_JEFE:
        for enemigo in enemigos_guardados:
            enemigo.reaparecer()
            enemigos.append(enemigo)
        enemigos_guardados.clear()
        # Y por cada jefe vencido se suma uno nuevo (hasta ENEMIGOS_MAX)
        if len(enemigos) < ENEMIGOS_MAX:
            tipo_nuevo = ENEMIGOS_POR_JEFE[(jefes_vencidos - 1) % len(ENEMIGOS_POR_JEFE)]
            enemigos.append(Enemigo(tipo_nuevo))

    # Enemigos: se mueven y luego se revisan los choques
    congelados = ahora < hielo_hasta
    for enemigo in enemigos:
        enemigo.actualizar(congelados)

    for enemigo in enemigos:
        if not enemigo.activo():
            continue
        golpe_x, golpe_y = enemigo.x + 20, enemigo.y + 20     # donde estaba al chocar
        # Congelado se "recoge" con la caja grande; si no, el daño usa los circulos
        if congelados:
            toca = caja_jugador.colliderect(enemigo.caja())
        else:
            toca = nave_toca_circulo(golpe_x, golpe_y, RADIO_ENEMIGO)
        if not toca:
            continue
        if congelados:
            # Enemigo congelado: lo destruyes y ganas puntos (el hielo sigue)
            ganados = sumar_puntos(PUNTOS_ENEMIGO_CONGELADO)
            sonido_moneda.play()
            tiempo_moneda = ahora
            crear_explosion(golpe_x, golpe_y, ESCARCHA, 40, 7, 5)
            crear_texto_flotante("+" + str(ganados), golpe_x, golpe_y - 20, HIELO)
            sacudir_pantalla(6)
            congelar_frames = 3
            enemigo.reaparecer()
        elif ahora < dash_hasta or ahora < invulnerable_hasta:
            continue    # el dash y la invulnerabilidad atraviesan enemigos
        else:
            danar_jugador(golpe_x, golpe_y)
            if estado == "Explosion":
                break
            enemigo.reaparecer()

    # Jefe: se mueve, dispara y se revisan sus choques
    if jefe_activo and estado == "Jugando":
        actualizar_jefe()
        revisar_choques_jefe(caja_jugador)

    # Efectos: fuego de la nave al moverse y brillo ocasional de la moneda
    if acelerando and ahora >= dash_hasta:
        # Mas fuego al arrancar que cuando ya va a toda velocidad
        if math.hypot(vx, vy) < vel_max * 0.8:
            estela_nave(x + 25, y + 25, angulo, 3)
        else:
            estela_nave(x + 25, y + 25, angulo, 2)
    if random.random() < 0.06:
        crear_particula(mx + random.randint(0, 20), my + random.randint(0, 20), 0, -0.3, ORO, 14, 2)
    actualizar_efectos()

    # Dibujar pantalla
    dibujar_escena(con_nave=(estado == "Jugando"))
    aplicar_temblor_y_destello()
    efecto_crt()
    mostrar()
    reloj.tick(60)

pygame.quit()
