"""
Configuracion: colores, paletas y todas las reglas que se pueden ajustar.

Aca van SOLO valores (numeros, colores, textos), nada de pygame ni de logica.
Asi se puede cambiar la dificultad sin miedo a romper nada.
"""
import os

# Carpeta raiz del proyecto (donde estan sprites/, efectos/ y fuentes/)
CARPETA = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def ruta(archivo):
    # Ruta de un archivo del juego, sin importar desde donde se ejecute
    return os.path.join(CARPETA, archivo)


# ================================== #
# ============ PANTALLA ============ #
# ================================== #

# El juego se dibuja en un lienzo de ALTO = 600 y un ancho que depende del formato
# (la ventana puede ser mas grande: el lienzo se escala). El ancho actual esta en lienzo.py
ALTO = 600
FORMATOS = {"4:3": 800, "16:9": 1066}      # formato -> ancho del lienzo
ANCHO_MENU = 800                # los menus se dibujan en una zona central de este ancho

# Frecuencia: la LOGICA del juego avanza siempre a 60 pasos por segundo (asi se siente igual
# a cualquier FPS) y se DIBUJA a la frecuencia elegida en Opciones (0 = sin limite).
# Todo lo que dice "por frame" en este archivo es por paso de logica (1/60 s)
PASOS_POR_SEGUNDO = 60
MS_POR_FRAME = 1000 / PASOS_POR_SEGUNDO     # cuanto avanza el reloj del juego en cada paso
FRECUENCIAS = [30, 60, 90, 120, 144, 0]     # opciones de FPS (0 = sin limite)
ATRASO_MAXIMO = 250             # ms: si la ventana se trabo mas que esto, no se intenta alcanzar

# Tamaños de ventana de cada formato (nombre, ancho, alto)
RESOLUCIONES = {
    "4:3": [("800x600", 800, 600), ("1200x900", 1200, 900),
            ("1600x1200", 1600, 1200), ("COMPLETA", 0, 0)],
    "16:9": [("1066x600", 1066, 600), ("1280x720", 1280, 720), ("1600x900", 1600, 900),
             ("1920x1080", 1920, 1080), ("COMPLETA", 0, 0)],
}
VOLUMEN_MAX = 10                # pasos de la barra de volumen (tambien es el volumen de fabrica)

# Archivos que escribe el juego (se crean solos si no existen)
NOMBRE_RECORDS = "records.json"
NOMBRE_CONFIG = "config.json"

# ================================== #
# ============ COLORES ============= #
# ================================== #

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

# ================================== #
# ======== REGLAS DEL JUEGO ======== #
# ================================== #
# (cambialas para ajustar la dificultad)

VIDAS_MAX = 3
COMBO_TIEMPO = 2000             # ms maximos entre monedas para seguir el combo
COMBO_MAXIMO = 5                # el multiplicador llega hasta x5
MONEDAS_POR_NIVEL = 10
PUNTOS_ENEMIGO_CONGELADO = 5

# Nave
NAVE_VELOCIDAD = 5              # velocidad maxima
NAVE_ACELERACION = 0.15         # que tan rapido llega a la velocidad maxima (0 a 1)
NAVE_FRICCION = 0.88            # al soltar: 1 = patina sin parar, 0 = frena en seco
NAVE_VELOCIDAD_GIRO = 15        # maximo de grados que gira en cada frame
INVULNERABLE_GOLPE = 1500       # ms sin recibir daño despues de perder una vida
INVULNERABLE_ESCUDO = 500       # ms sin recibir daño despues de que se rompe el escudo

# Dash
DASH_FUERZA = 14
DASH_DURACION = 180             # ms que dura el impulso (sin recibir daño)
DASH_RECARGA = 1500             # ms hasta poder usarlo otra vez
BUFFER_DASH = 150               # si apretas el dash hasta estos ms antes de que se recargue, sale igual

# Choques que hacen daño: circulos, asi la nave recibe el mismo golpe aunque este girada
RADIO_NAVE = 11
RADIO_ENEMIGO = 15
RADIO_BALA = 4

# Monedas: aparecen a esta distancia de la nave (asi siempre se llega antes de que se corte el combo)
MONEDA_DISTANCIA_MIN = 120
MONEDA_DISTANCIA_MAX = 450

# Power-ups
VELOCIDAD_POWERUP = 1.5         # px por frame que cae la capsula (con 1.5 cruza la pantalla en ~7 s)
PRIMER_POWERUP = 6000           # ms hasta que cae el primero
ESPERA_POWERUP = (8000, 13000)  # ms entre uno y otro (al azar entre estos dos)
TURBO_VELOCIDAD = 7             # velocidad maxima con TURBO (normal: NAVE_VELOCIDAD)
RECARGA_RAPIDA = 750            # ms de recarga del dash con RECARGA (normal: DASH_RECARGA)
DURACION = {                    # milisegundos que dura cada power-up temporal
    "escudo": 15000,
    "hielo": 5000,
    "iman": 7000,
    "doble": 8000,
}

# Enemigos
AVISO_APARICION = 800           # ms que se ve la "X" antes de que aparezca un enemigo
DISTANCIA_APARICION = 300       # los enemigos aparecen a mas de esta distancia de la nave
ENEMIGOS_INICIALES = ["perseguidor"]
ENEMIGOS_POR_NIVEL = {          # enemigo nuevo que se agrega al llegar a cada nivel
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

# Jefes: se les pega con el dash en el nucleo cuando quedan cansados
JEFE_CADA_NIVELES = 5           # aparece al llegar a los niveles 5, 10, 15...
ORDEN_JEFES = ["ojo"]           # que jefe sale cada vez (se repite la lista)
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

# Records: letras que se pueden usar en las iniciales
ALFABETO = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
FILAS_RECORDS = 5

# ================================== #
# ============= MANDO ============== #
# ================================== #

# Numeros de los botones del mando de Xbox (mapeo de SDL en Windows) y la accion de cada uno.
# Las acciones estan en entrada.py
BOTON_A = 0
BOTON_B = 1
BOTON_X = 2
BOTON_VISTA = 6                 # el de los dos cuadraditos
BOTON_MENU = 7                  # el de las tres rayitas
ZONA_MUERTA = 0.5               # en los menus: cuanto hay que inclinar el stick para que cuente (0 a 1)
ZONA_MUERTA_NAVE = 0.25         # al mover la nave (mas chica, para que responda enseguida)
