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

# Presupuesto de amenaza: cada enemigo "cuesta" puntos y cada nivel tiene un presupuesto.
# El juego elige al azar que enemigos poner hasta gastarlo (entre los ya desbloqueados),
# asi cada partida es distinta pero la dificultad sigue controlada (ver progresion.py)
COSTO_ENEMIGO = {"rebotador": 1, "perseguidor": 2, "embestidor": 3, "divisor": 4, "enjambre": 3}
DESBLOQUEO_ENEMIGO = {"perseguidor": 1, "rebotador": 2, "embestidor": 3,   # nivel desde el que aparece
                      "divisor": 4, "enjambre": 7}
REFUERZO_ESPERA = 5000          # ms: si destruiste enemigos, cada tanto llega otro hasta llenar el presupuesto
RECARGA_POR_DESTRUIR = 400      # ms que se adelanta la recarga del dash por cada enemigo que destruye

# Divisor: masa verde que el dash parte en dos (grande -> 2 medianos -> 2 chicos cada uno)
DIVISOR_VELOCIDAD = {"divisor": 0.9, "divisor_mediano": 1.6, "divisor_chico": 2.4}
DIVISOR_PUNTOS = {"divisor": 2, "divisor_mediano": 3, "divisor_chico": 5}
DIVISOR_NACIMIENTO = 450        # ms que parpadean los hijos al nacer (sin hacer daño)

# Enjambre: drones que vuelan en formacion; el dash los destruye de a uno
ENJAMBRE_CANTIDAD = 5
ENJAMBRE_VELOCIDAD = 1.4        # velocidad del grupo
ENJAMBRE_PICADA = 3.8           # velocidad cuando se lanza en picada contra la nave
ENJAMBRE_ESPERA_PICADA = (3500, 5500)   # ms entre picadas (al azar)
ENJAMBRE_PUNTOS = 2             # por dron
ENJAMBRE_BONUS = 10             # por destruir el enjambre entero con el dash
PRESUPUESTO_INICIAL = 2
PRESUPUESTO_POR_NIVEL = 1.8
PRESUPUESTO_MAXIMO = 24
ENEMIGOS_MAX = 10               # nunca mas que esto en pantalla (sin contar las oleadas)

# Oleadas: cada tanto llegan muchos enemigos de golpe por unos segundos y despues se van
OLEADA_DESDE_NIVEL = 2
OLEADA_ESPERA = (35000, 55000)  # ms de juego entre una oleada y la siguiente (al azar)
OLEADA_DURACION = 12000         # ms que dura
OLEADA_PRESUPUESTO = 0.6        # enemigos extra: esta parte del presupuesto del nivel
OLEADA_PUNTOS = 10              # bonus por nivel si la pasas sin perder una vida

# Los que persiguen se separan entre si, para no terminar todos encimados en el mismo punto
SEPARACION_ENEMIGOS = 50        # distancia (px) a la que empiezan a alejarse de otro enemigo
FUERZA_SEPARACION = 0.3         # que tan fuerte se alejan (mas = se separan mas rapido)
# El embestidor solo te sigue (y te embiste) si estas a menos de esta distancia; si no, deambula
RANGO_EMBESTIDOR = 250

# Jefes: se les pega con el dash en el nucleo cuando quedan cansados
JEFE_CADA_NIVELES = 5           # aparece al llegar a los niveles 5, 10, 15...
ORDEN_JEFES = ["ojo", "fortaleza"]  # que jefe sale cada vez (se repite la lista)
JEFE_VIDA = 3                   # golpes que aguanta el primero (cada jefe nuevo aguanta uno mas)
JEFE_PUNTOS = 50                # bonus al vencerlo (el segundo da el doble, el tercero el triple...)
JEFE_FLOTAR = 2500              # ms que se mueve de lado a lado antes de atacar
JEFE_CANSADO = 2500             # ms que deja el nucleo al descubierto
JEFE_RAFAGAS = 3                # rafagas de balas en cada ataque
CARTEL_JEFE = 2000              # ms que se ve "¡JEFE VENCIDO!" (los enemigos vuelven despues)

# La Fortaleza: 4 cañones que se turnan para atacar. Despues de disparar, cada uno se
# recalienta y ahi se le puede pegar con el dash. Sin cañones se cae la coraza y queda el nucleo
FORTALEZA_VIDA_CANON = 2        # golpes que aguanta cada cañon
FORTALEZA_PUNTOS_CANON = 10     # puntos por romper un cañon
FORTALEZA_ESPERA = {4: 2000, 3: 1600, 2: 1200, 1: 900}  # ms entre ataques segun los cañones que quedan
FORTALEZA_CARGA = 700           # ms que se carga un cañon antes de disparar
FORTALEZA_RECALENTADO = 2200    # ms que queda recalentado (y se le puede pegar)
FORTALEZA_DISPAROS = {          # (disparos, ms entre uno y otro) de cada cañon
    "rafaga": (3, 160),         # 3 balas hacia la nave, 3 veces
    "misiles": (2, 500),        # misiles lentos que te siguen
    "laser": (1, 0),            # un rayo hacia abajo que barre la pantalla
    "minas": (3, 350),          # minas que se quedan quietas y estallan en un anillo
}
FORTALEZA_LASER = 1000          # ms que dura el rayo
FORTALEZA_MISIL_GUIADO = 2500   # ms que te sigue un misil (despues sigue derecho)
FORTALEZA_MINA_ESPERA = 1800    # ms desde que sale una mina hasta que estalla
FORTALEZA_FURIA = 3000          # sin coraza: ms que dispara en espiral...
FORTALEZA_CANSADO = 2200        # ...y ms que deja el nucleo al descubierto
FORTALEZA_BRAZOS = 3            # brazos de la espiral
FORTALEZA_ESPIRAL_CADA = 120    # ms entre una vuelta de balas y la siguiente

# ================================== #
# ===== DIFICULTAD Y SECTORES ====== #
# ================================== #

# Cada dificultad tiene su propia tabla de records.
#   vidas:          vidas al empezar (y maximas)
#   velocidad:      multiplica la velocidad de enemigos y balas
#   presupuesto:    multiplica el presupuesto de enemigos (mas o menos enemigos)
#   espera_powerup: multiplica la espera entre power-ups (mas = caen menos seguido)
ORDEN_DIFICULTADES = ["FACIL", "NORMAL", "DIFICIL", "PESADILLA"]
DIFICULTADES = {
    "FACIL": {"color": VERDE, "paleta": TREBOL, "calaveras": 1, "vidas": 5, "velocidad": 0.8,
              "presupuesto": 0.7, "espera_powerup": 0.8,
              "descripcion": ["5 VIDAS", "ENEMIGOS MAS LENTOS", "MAS POWER-UPS"]},
    "NORMAL": {"color": CIAN, "paleta": ENERGIA, "calaveras": 2, "vidas": 3, "velocidad": 1.0,
               "presupuesto": 1.0, "espera_powerup": 1.0,
               "descripcion": ["3 VIDAS", "EL DESAFIO ORIGINAL", ""]},
    "DIFICIL": {"color": AMARILLO, "paleta": ORO, "calaveras": 3, "vidas": 3, "velocidad": 1.15,
                "presupuesto": 1.3, "espera_powerup": 1.3,
                "descripcion": ["3 VIDAS", "ENEMIGOS 15% MAS RAPIDOS", "MAS ENEMIGOS, MENOS POWER-UPS"]},
    "PESADILLA": {"color": ROJO, "paleta": FUEGO, "calaveras": 4, "vidas": 1, "velocidad": 1.3,
                  "presupuesto": 1.6, "espera_powerup": 1.6,
                  "descripcion": ["1 VIDA", "ENEMIGOS 30% MAS RAPIDOS", "SIN PIEDAD"]},
}

# Sectores: cada SECTOR_CADA_NIVELES niveles cambia el ambiente (fondo teñido) y el enemigo
# que mas aparece. El primero es siempre el Cinturon; despues se sortean (nunca dos iguales
# seguidos). 'tinte' tiñe nebulosas y planetas (None = colores originales; ningun canal
# por encima de ~110, para que no se confunda con enemigos); 'fondo' es el color del espacio
SECTOR_CADA_NIVELES = 2
PESO_FAVORITO = 3               # el enemigo favorito del sector sale 3 veces mas seguido
RECAMBIO_SECTOR = 0.34          # al cambiar de sector se va esta parte de los enemigos (vienen otros)
SECTORES = [
    {"nombre": "CINTURON EXTERIOR", "color": CIAN, "tinte": None, "fondo": FONDO, "favorito": "perseguidor"},
    {"nombre": "NEBULOSA CARMESI", "color": ROJO, "tinte": (110, 35, 50), "fondo": (16, 4, 8),
     "favorito": "embestidor"},
    {"nombre": "CAMPO ESMERALDA", "color": VERDE, "tinte": (35, 105, 70), "fondo": (4, 14, 10),
     "favorito": "divisor"},
    {"nombre": "MAR DE AMBAR", "color": AMARILLO, "tinte": (110, 80, 30), "fondo": (14, 10, 4),
     "favorito": "enjambre"},
    {"nombre": "ABISMO AZUL", "color": HIELO, "tinte": (35, 65, 110), "fondo": (4, 6, 20),
     "favorito": "embestidor"},
]
TRANSICION_SECTOR = 60          # pasos (1 s) que tarda el fondo en cambiar de color, en 4 etapas

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
